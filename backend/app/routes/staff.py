from __future__ import annotations

import uuid
from typing import Any

import asyncpg
import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import make_staff_token, require_admin
from app.database import get_db

router = APIRouter(prefix="/api")

ALLOWED_ROLES = {"receptionist", "waiter"}


# ── Models ────────────────────────────────────────────────────────────────────

class StaffLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=60)
    password: str = Field(..., min_length=1)


class StaffCreateRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=60, pattern=r"^[a-zA-Z0-9_\-]+$")
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern=r"^(receptionist|waiter)$")


class StaffUpdateRequest(BaseModel):
    password: str | None = Field(None, min_length=6)
    role: str | None = Field(None, pattern=r"^(receptionist|waiter)$")


# ── Public: POST /api/staff/login ─────────────────────────────────────────────

@router.post("/staff/login")
async def staff_login(
    body: StaffLoginRequest,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    row = await db.fetchrow(
        "SELECT id, hashed_password, role FROM staff WHERE username = $1",
        body.username,
    )
    if row is None or not bcrypt.checkpw(body.password.encode(), row["hashed_password"].encode()):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = make_staff_token(row["id"], row["role"])  # type: ignore[arg-type]
    return {"token": token, "role": row["role"], "username": body.username}


# ── Admin: list staff ─────────────────────────────────────────────────────────

@router.get("/admin/staff", dependencies=[Depends(require_admin)])
async def list_staff(
    db: asyncpg.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = await db.fetch(
        "SELECT id, username, role, created_at FROM staff ORDER BY created_at"
    )
    return [dict(r) for r in rows]


# ── Admin: create staff ───────────────────────────────────────────────────────

@router.post("/admin/staff", dependencies=[Depends(require_admin)])
async def create_staff(
    body: StaffCreateRequest,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    existing = await db.fetchrow("SELECT id FROM staff WHERE username = $1", body.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    staff_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO staff (id, username, hashed_password, role) VALUES ($1, $2, $3, $4)",
        staff_id, body.username, hashed, body.role,
    )
    return {"id": staff_id, "username": body.username, "role": body.role}


# ── Admin: update staff (password / role) ────────────────────────────────────

@router.patch("/admin/staff/{staff_id}", dependencies=[Depends(require_admin)])
async def update_staff(
    staff_id: str,
    body: StaffUpdateRequest,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, str]:
    row = await db.fetchrow("SELECT id FROM staff WHERE id = $1", staff_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Staff member not found")
    if body.password:
        hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
        await db.execute("UPDATE staff SET hashed_password = $1 WHERE id = $2", hashed, staff_id)
    if body.role:
        await db.execute("UPDATE staff SET role = $1 WHERE id = $2", body.role, staff_id)
    return {"ok": "updated"}


# ── Admin: delete staff ───────────────────────────────────────────────────────

@router.delete("/admin/staff/{staff_id}", dependencies=[Depends(require_admin)])
async def delete_staff(
    staff_id: str,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, str]:
    await db.execute("DELETE FROM staff WHERE id = $1", staff_id)
    return {"ok": "deleted"}
