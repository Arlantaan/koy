from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ── Menu ──────────────────────────────────────────────────────────────────────

class MenuItem(BaseModel):
    id: str
    section: str
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    image: Optional[str] = None
    hidden: int = 0
    sort_order: int = 999
    insert_after: Optional[str] = None
    badge: Optional[str] = None


class MenuItemPublic(BaseModel):
    id: str
    section: str
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    image: Optional[str] = None
    hidden: int
    sort_order: int
    insert_after: Optional[str] = None
    badge: Optional[str] = None


class MenuItemCreate(BaseModel):
    section: str
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    image: Optional[str] = None
    hidden: int = 0
    sort_order: int = 999
    insert_after: Optional[str] = None
    badge: Optional[str] = None


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    image: Optional[str] = None
    hidden: Optional[int] = None
    sort_order: Optional[int] = None
    badge: Optional[str] = None


class MenuItemImageResponse(BaseModel):
    image: Optional[str] = None


# ── Reservations ──────────────────────────────────────────────────────────────

class ReservationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    phone: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=120)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    party_size: int = Field(..., ge=1, le=50)
    notes: Optional[str] = Field(None, max_length=500)


class ReservationUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(pending|confirmed|seated|cancelled)$")
    notes: Optional[str] = Field(None, max_length=500)


class Reservation(BaseModel):
    model_config = {"extra": "ignore"}

    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    date: str
    time: str
    party_size: int
    notes: Optional[str] = None
    status: str
    created_at: str
    user_id: Optional[str] = None


class SuccessResponse(BaseModel):
    success: bool = True
    id: Optional[str] = None


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderItemInput(BaseModel):
    id: str
    name: str = Field(..., min_length=1, max_length=200)
    price: Optional[str] = Field(None, max_length=50)
    qty: int = Field(..., ge=1, le=100)


class OrderCreate(BaseModel):
    table_number: str = Field(..., min_length=1, max_length=20)
    items: list[OrderItemInput] = Field(..., min_length=1)
    total: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)


class OrderUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(new|done)$")


class OrderItemsAppend(BaseModel):
    items: list[OrderItemInput] = Field(..., min_length=1)
    total: Optional[str] = Field(None, max_length=50)


class Order(BaseModel):
    model_config = {"extra": "ignore"}
    id: str
    table_number: str
    items: str
    total: str
    notes: str
    status: str
    created_at: str


# ── Auth / Users ──────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: Optional[str] = Field(None, min_length=3, max_length=120)
    phone: Optional[str] = Field(None, min_length=6, max_length=30)
    pin: str = Field(..., pattern=r"^\d{4}$")


class UserLogin(BaseModel):
    identifier: str = Field(..., max_length=120)  # email or phone
    pin: str = Field(..., pattern=r"^\d{4}$")


class GoogleAuthRequest(BaseModel):
    credential: str


class ForgotPinRequest(BaseModel):
    identifier: str = Field(..., min_length=1, max_length=200)


class ResetPinRequest(BaseModel):
    identifier: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=6, max_length=6)
    new_pin: str = Field(..., min_length=4, max_length=4)


class UserPublic(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    user: UserPublic


class AdminCustomer(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None
    has_google: bool
    has_password: bool
    reservation_count: int
    order_count: int
    total_spend: float = 0.0


class MyOrder(BaseModel):
    model_config = {"extra": "ignore"}

    id: str
    table_number: str
    items: str
    total: str
    notes: str
    status: str
    created_at: str
