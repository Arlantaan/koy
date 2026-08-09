from __future__ import annotations

import uuid

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_admin
from app.database import get_db
from app.models import GalleryAdd, GalleryImage

router = APIRouter(prefix="/api")


# ── Public: GET /api/gallery ──────────────────────────────────────────────────

@router.get("/gallery", response_model=list[GalleryImage])
async def get_gallery(
    db: asyncpg.Connection = Depends(get_db),
) -> list[GalleryImage]:
    rows = await db.fetch(
        "SELECT id, image, sort_order FROM gallery ORDER BY sort_order, created_at"
    )
    return [GalleryImage(**dict(row)) for row in rows]


# ── Admin: POST /api/admin/gallery ────────────────────────────────────────────

@router.post("/admin/gallery", response_model=GalleryImage, dependencies=[Depends(require_admin)])
async def add_gallery_image(
    payload: GalleryAdd,
    db: asyncpg.Connection = Depends(get_db),
) -> GalleryImage:
    next_order = await db.fetchval("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM gallery")
    gid = str(uuid.uuid4())
    row = await db.fetchrow(
        "INSERT INTO gallery (id, image, sort_order) VALUES ($1, $2, $3) "
        "RETURNING id, image, sort_order",
        gid, payload.image.strip(), next_order,
    )
    return GalleryImage(**dict(row))


# ── Admin: DELETE /api/admin/gallery/{image_id} ───────────────────────────────

@router.delete("/admin/gallery/{image_id}", dependencies=[Depends(require_admin)])
async def delete_gallery_image(
    image_id: str,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, bool]:
    result = await db.execute("DELETE FROM gallery WHERE id = $1", image_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Image not found")
    return {"success": True}
