from __future__ import annotations

import json
import uuid
from typing import Any, Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user, get_optional_user, require_admin, require_role
from app.database import get_db
from app.models import MyOrder, Order, OrderCreate, OrderItemsAppend, OrderUpdate, SuccessResponse

router = APIRouter(prefix="/api")


# ── Public: POST /api/orders ──────────────────────────────────────────────────

@router.post(
    "/orders",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    body: OrderCreate,
    db: asyncpg.Connection = Depends(get_db),
    customer: Optional[dict[str, Any]] = Depends(get_optional_user),
) -> dict[str, Any]:
    order_id = str(uuid.uuid4())
    items_json = json.dumps([item.model_dump() for item in body.items])
    customer_id = customer["id"] if customer else None
    async with db.transaction():
        await db.execute(
            "INSERT INTO orders (id, table_number, items, total, notes, status, customer_id) "
            "VALUES ($1,$2,$3,$4,$5,$6,$7)",
            order_id,
            body.table_number,
            items_json,
            body.total or "",
            body.notes or "",
            "new",
            customer_id,
        )
    return {"success": True, "id": order_id}


# ── Admin: GET /api/admin/orders ──────────────────────────────────────────────

@router.get(
    "/admin/orders",
    response_model=list[Order],
    dependencies=[Depends(require_role("waiter"))],
)
async def admin_list_orders(
    status_filter: str | None = None,
    db: asyncpg.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    if status_filter:
        rows = await db.fetch(
            "SELECT * FROM orders WHERE status = $1 ORDER BY created_at DESC", status_filter
        )
    else:
        rows = await db.fetch(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT 200"
        )
    result = []
    for r in rows:
        row = dict(r)
        if "created_at" in row and row["created_at"] is not None:
            row["created_at"] = row["created_at"].isoformat()
        result.append(row)
    return result


# ── Admin: PATCH /api/admin/orders/:id ───────────────────────────────────────

@router.patch(
    "/admin/orders/{order_id}",
    response_model=SuccessResponse,
    dependencies=[Depends(require_role("waiter"))],
)
async def admin_update_order(
    order_id: str,
    body: OrderUpdate,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        "UPDATE orders SET status = $1 WHERE id = $2",
        body.status, order_id,
    )
    if result == "UPDATE 0":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return {"success": True}


# ── Admin: PATCH /api/admin/orders/:id/items ─────────────────────────────────

@router.patch(
    "/admin/orders/{order_id}/items",
    response_model=SuccessResponse,
    dependencies=[Depends(require_role("waiter"))],
)
async def admin_append_order_items(
    order_id: str,
    body: OrderItemsAppend,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    row = await db.fetchrow("SELECT items, total FROM orders WHERE id = $1", order_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    existing: list[dict] = json.loads(row["items"] or "[]")
    for new_item in body.items:
        merged = False
        for ex in existing:
            if ex.get("name") == new_item.name:
                ex["qty"] = ex.get("qty", 1) + new_item.qty
                merged = True
                break
        if not merged:
            existing.append(new_item.model_dump())
    updated_total = body.total if body.total is not None else row["total"]
    await db.execute(
        "UPDATE orders SET items = $1, total = $2 WHERE id = $3",
        json.dumps(existing), updated_total, order_id,
    )
    return {"success": True}


# ── Customer: GET /api/user/orders ────────────────────────────────────────────

@router.get("/user/orders", response_model=list[MyOrder])
async def my_orders(
    user: dict[str, Any] = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = await db.fetch(
        "SELECT id, table_number, items, total, notes, status, created_at "
        "FROM orders WHERE customer_id = $1 ORDER BY created_at DESC LIMIT 50",
        user["id"],
    )
    result = []
    for r in rows:
        row = dict(r)
        if row.get("created_at") is not None:
            row["created_at"] = row["created_at"].isoformat()
        result.append(row)
    return result
