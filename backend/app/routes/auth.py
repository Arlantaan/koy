from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

import asyncpg
import bcrypt as _bcrypt
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user, get_optional_user, make_token, require_admin
from app.config import settings
from app.database import get_db
from app.models import (
    AdminCustomer,
    GoogleAuthRequest,
    TokenResponse,
    UserLogin,
    UserPublic,
    UserRegister,
)

router = APIRouter(prefix="/api")


def _hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return _bcrypt.checkpw(password.encode(), hashed.encode())


# ── POST /api/auth/register ───────────────────────────────────────────────────

@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserRegister,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    if not body.email and not body.phone:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email or phone is required")
    # Normalise
    email = body.email.lower().strip() if body.email else None
    phone = body.phone.strip() if body.phone else None
    # Duplicate check
    if email:
        existing = await db.fetchrow("SELECT id FROM users WHERE email = $1", email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if phone:
        existing = await db.fetchrow("SELECT id FROM users WHERE phone = $1", phone)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number already registered")
    user_id = str(uuid.uuid4())
    hashed = _hash_password(body.pin)
    now = datetime.now(timezone.utc)
    async with db.transaction():
        await db.execute(
            "INSERT INTO users (id, name, email, phone, hashed_password, created_at, last_login) VALUES ($1,$2,$3,$4,$5,$6,$6)",
            user_id, body.name.strip(), email, phone, hashed, now,
        )
    return {
        "access_token": make_token(user_id),
        "user": {"id": user_id, "name": body.name.strip(), "email": email, "phone": phone, "avatar": None, "created_at": now.isoformat()},
    }


# ── POST /api/auth/login ──────────────────────────────────────────────────────

@router.post("/auth/login", response_model=TokenResponse)
async def login(
    body: UserLogin,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    identifier = body.identifier.strip()
    # Try email match first, then phone
    row = await db.fetchrow(
        "SELECT id, name, email, phone, hashed_password, avatar, created_at FROM users "
        "WHERE email = $1 OR phone = $1",
        identifier.lower() if "@" in identifier else identifier,
    )
    # If email search with lowercase didn't find by phone, try direct
    if row is None and "@" not in identifier:
        row = await db.fetchrow(
            "SELECT id, name, email, phone, hashed_password, avatar, created_at FROM users WHERE phone = $1",
            identifier,
        )
    if row is None or not row["hashed_password"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not _verify_password(body.pin, row["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    await db.execute("UPDATE users SET last_login = NOW() WHERE id = $1", row["id"])
    return {
        "access_token": make_token(row["id"]),
        "user": {
            "id": row["id"], "name": row["name"], "email": row["email"], "phone": row["phone"],
            "avatar": row["avatar"],
            "created_at": row["created_at"].isoformat(),
        },
    }


# ── POST /api/auth/google ─────────────────────────────────────────────────────

@router.post("/auth/google", response_model=TokenResponse)
async def google_auth(
    body: GoogleAuthRequest,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    if not settings.google_client_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Google auth not configured")
    try:
        from google.auth.transport import requests as g_requests
        from google.oauth2 import id_token as g_id_token
        id_info = g_id_token.verify_oauth2_token(body.credential, g_requests.Request(), settings.google_client_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google credential")

    google_id = id_info["sub"]
    email = id_info.get("email", "").lower()
    name = id_info.get("name", "")
    avatar = id_info.get("picture")

    row = await db.fetchrow(
        "SELECT id, name, email, phone, avatar, created_at FROM users WHERE google_id = $1 OR email = $2",
        google_id, email,
    )
    now = datetime.now(timezone.utc)
    if row:
        await db.execute(
            "UPDATE users SET last_login = $1, google_id = $2, avatar = $3 WHERE id = $4",
            now, google_id, avatar, row["id"],
        )
        user_id, user_name, user_email = row["id"], row["name"], row["email"]
        user_phone = row["phone"]
        user_created = row["created_at"].isoformat()
    else:
        user_id = str(uuid.uuid4())
        async with db.transaction():
            await db.execute(
                "INSERT INTO users (id, name, email, google_id, avatar, created_at, last_login) VALUES ($1,$2,$3,$4,$5,$6,$6)",
                user_id, name, email, google_id, avatar, now,
            )
        user_name, user_email, user_phone, user_created = name, email, None, now.isoformat()

    return {
        "access_token": make_token(user_id),
        "user": {"id": user_id, "name": user_name, "email": user_email, "phone": user_phone, "avatar": avatar, "created_at": user_created},
    }


# ── GET /api/auth/me ──────────────────────────────────────────────────────────

@router.get("/auth/me", response_model=UserPublic)
async def get_me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user.get("email"),
        "phone": user.get("phone"),
        "avatar": user.get("avatar"),
        "created_at": user["created_at"].isoformat() if hasattr(user.get("created_at"), "isoformat") else str(user.get("created_at", "")),
    }


# ── GET /api/user/reservations ────────────────────────────────────────────────

@router.get("/user/reservations")
async def my_reservations(
    user: dict[str, Any] = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    rows = await db.fetch(
        "SELECT id, date, time, party_size, status, notes, created_at FROM reservations "
        "WHERE user_id = $1 ORDER BY date DESC, time ASC",
        user["id"],
    )
    return {
        "reservations": [
            {**dict(r), "created_at": r["created_at"].isoformat() if r.get("created_at") else None}
            for r in rows
        ]
    }


# ── Admin: GET /api/admin/customers ──────────────────────────────────────────

def _parse_dalasi(s: str) -> float:
    """Parse 'D1,200' or '1200' into float."""
    cleaned = re.sub(r'[^\d.]', '', s or '')
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


@router.get("/admin/customers", response_model=list[AdminCustomer], dependencies=[Depends(require_admin)])
async def admin_list_customers(
    db: asyncpg.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = await db.fetch("""
        SELECT u.id, u.name, u.email, u.phone, u.avatar,
               u.created_at, u.last_login,
               (u.google_id IS NOT NULL) AS has_google,
               (u.hashed_password IS NOT NULL) AS has_password,
               COUNT(DISTINCT r.id)::int AS reservation_count,
               COUNT(DISTINCT o.id)::int AS order_count,
               COALESCE(
                 array_agg(o.total) FILTER (WHERE o.total IS NOT NULL AND o.total <> ''),
                 ARRAY[]::text[]
               ) AS order_totals
        FROM users u
        LEFT JOIN reservations r ON r.user_id = u.id
        LEFT JOIN orders o ON o.customer_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    result = []
    for r in rows:
        d = dict(r)
        d["created_at"] = d["created_at"].isoformat() if d.get("created_at") else ""
        d["last_login"] = d["last_login"].isoformat() if d.get("last_login") else None
        totals = list(d.pop("order_totals", None) or [])
        d["total_spend"] = round(sum(_parse_dalasi(t) for t in totals if t), 2)
        result.append(d)
    return result
