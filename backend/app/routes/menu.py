from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from PIL import Image
import io

from app.auth import require_admin
from app.config import settings
from app.database import get_db
from app.models import (
    MenuItemCreate,
    MenuItemImageResponse,
    MenuItemPublic,
    MenuItemUpdate,
    SuccessResponse,
)

router = APIRouter(prefix="/api")

# ── Admin: POST /api/admin/upload-image ───────────────────────────────────────
# Convert any image format to WebP and save to disk

@router.post(
    "/admin/upload-image",
    dependencies=[Depends(require_admin)],
)
async def admin_upload_image(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload an image (JPEG, PNG, etc) and convert to WebP"""
    # Allowed types
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, WebP, and GIF images are allowed"
        )
    
    # Read file into memory
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image too large (max 5MB)"
        )
    
    try:
        # Open image and convert to WebP
        img = Image.open(io.BytesIO(contents))
        
        # Convert RGBA to RGB if needed (WebP quality)
        if img.mode in ("RGBA", "LA", "P"):
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = rgb_img
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.webp"
        filepath = Path(settings.upload_dir) / filename

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as WebP
        img.save(str(filepath), "WEBP", quality=85, method=6)
        
        # Return the URL path
        return {
            "success": True,
            "url": f"/uploads/{filename}",
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image processing failed: {str(e)}"
        )


# ── Public: GET /api/menu ─────────────────────────────────────────────────────

@router.get("/menu", response_model=list[MenuItemPublic])
async def get_public_menu(
    db: asyncpg.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = await db.fetch(
        "SELECT id, section, name, description, price, image, hidden, sort_order, insert_after, badge "
        "FROM menu_items WHERE hidden = 0 ORDER BY section, sort_order"
    )
    return [dict(r) for r in rows]


# ── Public: GET /api/menu/images ──────────────────────────────────────────────

@router.get("/menu/images")
async def get_menu_images(
    db: asyncpg.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = await db.fetch(
        "SELECT id, image FROM menu_items "
        "WHERE hidden = 0 AND image IS NOT NULL AND image != ''"
    )
    return [dict(r) for r in rows]


# ── Admin: GET /api/admin/menu ────────────────────────────────────────────────

@router.get("/admin/menu", dependencies=[Depends(require_admin)])
async def admin_get_menu(
    db: asyncpg.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = await db.fetch(
        "SELECT id, section, name, description, price, hidden, sort_order, insert_after, badge "
        "FROM menu_items ORDER BY section, sort_order"
    )
    return [dict(r) for r in rows]


# ── Admin: GET /api/admin/menu/:id/image ──────────────────────────────────────

@router.get(
    "/admin/menu/{item_id}/image",
    response_model=MenuItemImageResponse,
    dependencies=[Depends(require_admin)],
)
async def admin_get_item_image(
    item_id: str,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    row = await db.fetchrow("SELECT image FROM menu_items WHERE id = $1", item_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"image": row["image"]}


# ── Admin: POST /api/admin/menu ───────────────────────────────────────────────

@router.post(
    "/admin/menu",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def admin_create_item(
    body: MenuItemCreate,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    item_id = str(uuid.uuid4())
    async with db.transaction():
        await db.execute(
            "INSERT INTO menu_items "
            "(id, section, name, description, price, image, hidden, sort_order, insert_after, badge) "
            "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)",
            item_id, body.section, body.name, body.description,
            body.price, body.image, body.hidden, body.sort_order,
            body.insert_after, body.badge or "",
        )
    return {"success": True, "id": item_id}


# ── Admin: PUT /api/admin/menu/:id ────────────────────────────────────────────

@router.put(
    "/admin/menu/{item_id}",
    response_model=SuccessResponse,
    dependencies=[Depends(require_admin)],
)
async def admin_update_item(
    item_id: str,
    body: MenuItemUpdate,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    row = await db.fetchrow("SELECT id FROM menu_items WHERE id = $1", item_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    fields = body.model_dump(exclude_none=True)
    if not fields:
        return {"success": True}

    set_clause = ", ".join(f"{k} = ${i + 1}" for i, k in enumerate(fields))
    values = list(fields.values()) + [item_id]
    async with db.transaction():
        await db.execute(
            f"UPDATE menu_items SET {set_clause} WHERE id = ${len(values)}",
            *values,
        )
    return {"success": True}


# ── Admin: DELETE /api/admin/menu/:id ─────────────────────────────────────────

@router.delete(
    "/admin/menu/{item_id}",
    response_model=SuccessResponse,
    dependencies=[Depends(require_admin)],
)
async def admin_delete_item(
    item_id: str,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    async with db.transaction():
        await db.execute("DELETE FROM menu_items WHERE id = $1", item_id)
    return {"success": True}
