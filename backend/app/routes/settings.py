from __future__ import annotations

from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_admin
from app.database import get_db

router = APIRouter(prefix="/api")


# ── Public: GET /api/settings ─────────────────────────────────────────────────

@router.get("/settings")
async def get_settings(
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, str]:
    rows = await db.fetch("SELECT key, value FROM site_settings ORDER BY key")
    return {row["key"]: row["value"] for row in rows}


# ── Admin: PUT /api/admin/settings ────────────────────────────────────────────

@router.put("/admin/settings", dependencies=[Depends(require_admin)])
async def update_settings(
    payload: dict[str, Any],
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, str]:
    async with db.transaction():
        for key, value in payload.items():
            await db.execute(
                "INSERT INTO site_settings (key, value) VALUES ($1, $2) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                key, str(value),
            )
    rows = await db.fetch("SELECT key, value FROM site_settings ORDER BY key")
    return {row["key"]: row["value"] for row in rows}


# ── Admin: POST /api/admin/change-password ────────────────────────────────────

@router.post("/admin/change-password", dependencies=[Depends(require_admin)])
async def change_password(
    payload: dict[str, str],
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, str]:
    new_password = payload.get("new_password", "").strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    await db.execute(
        "INSERT INTO site_settings (key, value) VALUES ('admin_password', $1) "
        "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
        new_password,
    )
    return {"status": "ok"}
