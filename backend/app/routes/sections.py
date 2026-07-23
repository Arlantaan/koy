from __future__ import annotations

import asyncpg
from fastapi import APIRouter, Depends, HTTPException 

from app.auth import require_admin
from app.database import get_db
from app.models import Section, SectionLabelUpdate

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
async def update_section_label(
    key: str,
    payload: SectionLabelUpdate,
    db: asyncpg.Connection = Depends(get_db),
) -> Section:
    row = await db.fetchrow(
        "UPDATE sections SET label = $1 WHERE key = $2 "
        "RETURNING key, label, icon, ornament, sort_order",
        payload.label.strip(), key,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return Section(**dict(row))



