from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

import asyncpg
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.database import get_db

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

bearer_scheme = HTTPBearer(auto_error=False)

# Roles: "admin" | "receptionist" | "waiter"
StaffRole = Literal["admin", "receptionist", "waiter"]


def make_staff_token(staff_id: str, role: StaffRole) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": staff_id, "role": role, "exp": exp},
        settings.jwt_secret, algorithm=ALGORITHM,
    )


def _decode_staff_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def _resolve_admin_password(db: asyncpg.Connection) -> str:
    row = await db.fetchrow("SELECT value FROM site_settings WHERE key = 'admin_password'")
    return row["value"] if row else settings.admin_password


async def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: asyncpg.Connection = Depends(get_db),
) -> None:
    """Accept only admin-role tokens (or legacy plaintext admin password)."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    # Legacy: plaintext admin password
    expected = await _resolve_admin_password(db)
    if token == expected:
        return
    # JWT admin token
    try:
        payload = _decode_staff_token(token)
        if payload.get("role") == "admin":
            return
    except HTTPException:
        pass
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(*allowed_roles: StaffRole) -> Any:
    """Return a FastAPI dependency that accepts any of the given roles (or admin)."""
    async def _dep(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        db: asyncpg.Connection = Depends(get_db),
    ) -> None:
        if credentials is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        token = credentials.credentials
        # Legacy plaintext admin password → treat as admin (accepted for all roles)
        expected = await _resolve_admin_password(db)
        if token == expected:
            return
        payload = _decode_staff_token(token)
        role = payload.get("role", "")
        if role == "admin" or role in allowed_roles:
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return _dep


def make_token(user_id: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": user_id, "exp": exp}, settings.jwt_secret, algorithm=ALGORITHM)


def _decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return str(payload["sub"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = _decode_token(credentials.credentials)
    row = await db.fetchrow(
        "SELECT id, name, email, phone, avatar, created_at FROM users WHERE id = $1", user_id
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return dict(row)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: asyncpg.Connection = Depends(get_db),
) -> Optional[dict[str, Any]]:
    if credentials is None:
        return None
    token = credentials.credentials
    if token == settings.admin_password:
        return None  # admin token, not a user JWT
    try:
        user_id = _decode_token(credentials.credentials)
        row = await db.fetchrow("SELECT id, name, email, phone FROM users WHERE id = $1", user_id)
        return dict(row) if row else None
    except HTTPException:
        return None
