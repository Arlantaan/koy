from __future__ import annotations

import re

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_admin
from app.database import get_db
from app.models import Section, SectionCreate, SectionEdit, SectionReorder

router = APIRouter(prefix="/api")

@router.get("/sections", response_model=list[Section])
async def get_sections(
    db: asyncpg.Connection = Depends(get_db),
) -> list[Section]:
    rows = await db.fetch(
        "SELECT key, label, icon, ornament, sort_order FROM sections ORDER BY sort_order"
    )
    return [Section(**dict(row)) for row in rows]


# ── Admin: PATCH /api/admin/sections/{key} ────────────────────────────────────

@router.patch("/admin/sections/{key}", dependencies=[Depends(require_admin)])
async def update_section(
    key: str,
    payload: SectionEdit,
    db: asyncpg.Connection = Depends(get_db),
) -> Section:
    fields: dict[str, str] = {}
    if payload.label is not None:
        fields["label"] = payload.label.strip()
    if payload.icon is not None:
        fields["icon"] = payload.icon.strip()
    if not fields:
        row = await db.fetchrow(
            "SELECT key, label, icon, ornament, sort_order FROM sections WHERE key = $1", key
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Section not found")
        return Section(**dict(row))
    set_clause = ", ".join(f"{col} = ${i + 1}" for i, col in enumerate(fields))
    values = list(fields.values()) + [key]
    row = await db.fetchrow(
        f"UPDATE sections SET {set_clause} WHERE key = ${len(values)} "
        "RETURNING key, label, icon, ornament, sort_order",
        *values,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return Section(**dict(row))


# ── Admin: PUT /api/admin/sections/reorder ────────────────────────────────────

@router.put("/admin/sections/reorder", dependencies=[Depends(require_admin)])
async def reorder_sections(
    payload: SectionReorder,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, bool]:
    async with db.transaction():
        for index, key in enumerate(payload.keys):
            await db.execute(
                "UPDATE sections SET sort_order = $1 WHERE key = $2", index + 1, key
            )
    return {"success": True}


# ── Admin: POST /api/admin/sections ───────────────────────────────────────────

@router.post("/admin/sections", response_model=Section, dependencies=[Depends(require_admin)])
async def create_section(
    payload: SectionCreate,
    db: asyncpg.Connection = Depends(get_db),
) -> Section:
    # Derive a stable internal key from the label; ensure it's unique
    base = re.sub(r"[^a-z0-9]", "", payload.label.strip().lower()) or "section"
    key = base
    n = 2
    while await db.fetchval("SELECT 1 FROM sections WHERE key = $1", key):
        key = f"{base}{n}"
        n += 1
    next_order = await db.fetchval("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM sections")
    row = await db.fetchrow(
        "INSERT INTO sections (key, label, icon, ornament, sort_order) VALUES ($1, $2, $3, false, $4) "
        "RETURNING key, label, icon, ornament, sort_order",
        key, payload.label.strip(), payload.icon.strip(), next_order,
    )
    return Section(**dict(row))


# ── Admin: DELETE /api/admin/sections/{key} ───────────────────────────────────

@router.delete("/admin/sections/{key}", dependencies=[Depends(require_admin)])
async def delete_section(
    key: str,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, bool]:
    count = await db.fetchval("SELECT COUNT(*) FROM menu_items WHERE section = $1", key)
    if count:
        raise HTTPException(
            status_code=409,
            detail=f"This section still has {count} item(s). Move or delete them first.",
        )
    await db.execute("DELETE FROM sections WHERE key = $1", key)
    return {"success": True}



