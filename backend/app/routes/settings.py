from __future__ import annotations

from typing import Any

import asyncpg
import bcrypt
from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_admin
from app.database import get_db

router = APIRouter(prefix="/api")

# Keys that must never be returned by the public settings endpoint, nor be
# writable through the generic settings PUT. The admin password (hash) and
# internal migration flags live in site_settings but are not "site settings".
PRIVATE_KEYS = {"admin_password", "admin_password_hash", "section_icons_v2"}


def _public_settings(rows: list[asyncpg.Record]) -> dict[str, str]:
    return {r["key"]: r["value"] for r in rows if r["key"] not in PRIVATE_KEYS}


# ── Public: GET /api/settings ─────────────────────────────────────────────────

@router.get("/settings")
async def get_settings(
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, str]:
    rows = await db.fetch("SELECT key, value FROM site_settings ORDER BY key")
    return _public_settings(rows)


# ── Admin: PUT /api/admin/settings ────────────────────────────────────────────

@router.put("/admin/settings", dependencies=[Depends(require_admin)])
async def update_settings(
    payload: dict[str, Any],
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, str]:
    async with db.transaction():
        for key, value in payload.items():
            if key in PRIVATE_KEYS:
                continue  # never writable here — use /admin/change-password
            await db.execute(
                "INSERT INTO site_settings (key, value) VALUES ($1, $2) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                key, str(value),
            )
    rows = await db.fetch("SELECT key, value FROM site_settings ORDER BY key")
    return _public_settings(rows)


# ── Admin: POST /api/admin/change-password ────────────────────────────────────

@router.post("/admin/change-password", dependencies=[Depends(require_admin)])
async def change_password(
    payload: dict[str, str],
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, str]:
    new_password = payload.get("new_password", "").strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    async with db.transaction():
        await db.execute(
            "INSERT INTO site_settings (key, value) VALUES ('admin_password_hash', $1) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            hashed,
        )
        # Remove any legacy plaintext password row now that a hash exists.
        await db.execute("DELETE FROM site_settings WHERE key = 'admin_password'")
    return {"status": "ok"}
