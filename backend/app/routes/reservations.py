from __future__ import annotations

import uuid
from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import require_admin, require_role, get_optional_user
from app.database import get_db
from app.models import Reservation, ReservationCreate, ReservationUpdate, SuccessResponse

router = APIRouter(prefix="/api")


# ── Public: POST /api/reservations ───────────────────────────────────────────

@router.post(
    "/reservations",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reservation(
    body: ReservationCreate,
    db: asyncpg.Connection = Depends(get_db),
    user: dict | None = Depends(get_optional_user),
) -> dict[str, Any]:
    res_id = str(uuid.uuid4())
    user_id = user["id"] if user else None
    async with db.transaction():
        await db.execute(
            "INSERT INTO reservations "
            "(id, name, phone, email, date, time, party_size, notes, status, user_id) "
            "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)",
            res_id, body.name, body.phone or "", body.email or "",
            body.date, body.time, body.party_size, body.notes or "", "pending", user_id,
        )
    return {"success": True, "id": res_id}


# ── Admin: GET /api/admin/reservations ───────────────────────────────────────

@router.get(
    "/admin/reservations",
    response_model=list[Reservation],
    dependencies=[Depends(require_role("receptionist"))],
)
async def admin_list_reservations(
    date: str | None = None,
    db: asyncpg.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    if date:
        rows = await db.fetch(
            "SELECT * FROM reservations WHERE date = $1 ORDER BY time ASC", date
        )
    else:
        rows = await db.fetch(
            "SELECT * FROM reservations ORDER BY date DESC, time ASC"
        )
    result = []
    for r in rows:
        row = dict(r)
        for key in ("date", "time", "created_at"):
            if key in row and row[key] is not None:
                row[key] = str(row[key])
        result.append(row)
    return result


# ── Admin: PUT /api/admin/reservations/:id ────────────────────────────────────

@router.put(
    "/admin/reservations/{res_id}",
    response_model=SuccessResponse,
    dependencies=[Depends(require_role("receptionist"))],
)
async def admin_update_reservation(
    res_id: str,
    body: ReservationUpdate,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    row = await db.fetchrow("SELECT id FROM reservations WHERE id = $1", res_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    async with db.transaction():
        await db.execute(
            "UPDATE reservations SET status = $1, notes = $2 WHERE id = $3",
            body.status, body.notes or "", res_id,
        )
    return {"success": True}


# ── Admin: DELETE /api/admin/reservations/:id ─────────────────────────────────

@router.delete(
    "/admin/reservations/{res_id}",
    response_model=SuccessResponse,
    dependencies=[Depends(require_admin)],
)
async def admin_delete_reservation(
    res_id: str,
    db: asyncpg.Connection = Depends(get_db),
) -> dict[str, Any]:
    async with db.transaction():
        await db.execute("DELETE FROM reservations WHERE id = $1", res_id)
    return {"success": True}
