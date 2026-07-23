from __future__ import annotations

from typing import AsyncGenerator

import asyncpg

from app.config import settings

# Module-level pool; set in lifespan.
pool: asyncpg.Pool | None = None

CREATE_MENU_ITEMS = """
CREATE TABLE IF NOT EXISTS menu_items (
    id           TEXT PRIMARY KEY,
    section      TEXT NOT NULL,
    name         TEXT NOT NULL,
    description  TEXT,
    price        TEXT,
    image        TEXT,
    hidden       INTEGER NOT NULL DEFAULT 0,
    sort_order   INTEGER NOT NULL DEFAULT 999,
    insert_after TEXT,
    badge        TEXT NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

CREATE_RESERVATIONS = """
CREATE TABLE IF NOT EXISTS reservations (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    phone      TEXT NOT NULL DEFAULT '',
    email      TEXT NOT NULL DEFAULT '',
    date       TEXT NOT NULL,
    time       TEXT NOT NULL,
    party_size INTEGER NOT NULL,
    notes      TEXT NOT NULL DEFAULT '',
    status     TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

CREATE_SITE_SETTINGS = """
CREATE TABLE IF NOT EXISTS site_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL DEFAULT ''
)
"""

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    hashed_password TEXT,
    google_id       TEXT UNIQUE,
    avatar          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ
)
"""

ALTER_RESERVATIONS_ADD_USER_ID = """
ALTER TABLE reservations ADD COLUMN IF NOT EXISTS user_id TEXT REFERENCES users(id) ON DELETE SET NULL
"""

ALTER_USERS_ADD_PHONE = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT
"""

ALTER_USERS_EMAIL_NULLABLE = """
DO $$ BEGIN
  ALTER TABLE users ALTER COLUMN email DROP NOT NULL;
EXCEPTION WHEN others THEN NULL;
END $$
"""

CREATE_USERS_PHONE_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS users_phone_unique ON users(phone) WHERE phone IS NOT NULL
"""

CREATE_ORDERS = """
CREATE TABLE IF NOT EXISTS orders (
    id           TEXT PRIMARY KEY,
    table_number TEXT NOT NULL,
    items        TEXT NOT NULL,
    total        TEXT NOT NULL DEFAULT '',
    notes        TEXT NOT NULL DEFAULT '',
    status       TEXT NOT NULL DEFAULT 'new',
    customer_id  TEXT REFERENCES users(id) ON DELETE SET NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

ALTER_ORDERS_ADD_CUSTOMER_ID = """
ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_id TEXT REFERENCES users(id) ON DELETE SET NULL
"""

CREATE_PIN_RESET_TOKENS = """
CREATE TABLE IF NOT EXISTS pin_reset_tokens (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""
CREATE_SECTIONS = """
CREATE TABLE IF NOT EXISTS sections (
    key      TEXT PRIMARY KEY,
    label    TEXT NOT NULL,
    icon     TEXT NOT NULL DEFAULT 'fa-utensils',
    ornament BOOLEAN NOT NULL DEFAULT 'false'
    sort_order INTEGER NOT NULL DEFAULT 999
)
"""

CREATE_STAFF = """
CREATE TABLE IF NOT EXISTS staff (
    id              TEXT PRIMARY KEY,
    username        TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'waiter',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

DEFAULT_SETTINGS = [
    ("phone", "+220 2222208"),
    ("whatsapp", "2202222208"),
    ("hours_open", "18:00"),
    ("hours_close", "01:30"),
    ("about_description", "Koya is a fine dining restaurant nestled in the heart of Senegambia, The Gambia. We blend West African tradition with contemporary cuisine in an atmosphere that feels both intimate and alive."),
    ("cover_tagline", "Fine Dining · The Gambia"),
    ("instagram", "casaafriqa"),
    ("facebook", "casaafriqa"),
    ("tiktok", "@casaafriqa"),
    ("email", "comedine@koya.living"),
    ("maps_url", "https://maps.app.goo.gl/fcSsMLpHL6t6gf6G6"),
]

DEFAULT_SECTIONS = [
    ("starters",    "Starters",         "fa-leaf",                  True,  1),
    ("salads",      "Salads & Bowls",   "fa-seedling",              False, 2),
    ("fish",        "Fish & Seafood",   "fa-fish",                  True,  3),
    ("meat",        "Meat",             "fa-drumstick-bite",        True,  4),
    ("pizza",       "Pizza",            "fa-pizza-slice",           True,  5),
    ("pasta",       "Pasta",            "fa-wheat-awn",             False, 6),
    ("calzone",     "Calzone",          "fa-bread-slice",           False, 7),
    ("sharing",     "Sharing Mix",      "fa-people-group",          True,  8),
    ("sides",       "Sides",            "fa-bowl-food",             False, 9),
    ("sauces",      "Sauces",           "fa-mortar-pestle",         False, 10),
    ("desserts",    "Desserts",         "fa-ice-cream",             True,  11),
    ("softdrinks",  "Soft Drinks",      "fa-glass-water",           False, 12),
    ("freshjuices", "Fresh Juices",     "fa-lemon",                 False, 13),
    ("localjuices", "Local Juices",     "fa-leaf",                  False, 14),
    ("milkshakes",  "Milkshakes",       "fa-blender",               False, 15),
    ("coffee",      "Coffee",           "fa-mug-hot",               False, 16),
    ("hottea",      "Hot Tea",          "fa-mug-saucer",            False, 17),
    ("matchas",     "Matchas",          "fa-spa",                   False, 18),
    ("mocktails",   "Mocktails",        "fa-martini-glass-citrus",  True,  19),
    ("icedtea",     "Iced Tea",         "fa-snowflake",             False, 20),
]



async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(settings.database_url)  # type: ignore[return-value]


async def init_db(conn: asyncpg.Connection) -> None:
    await conn.execute(CREATE_MENU_ITEMS)
    await conn.execute(CREATE_RESERVATIONS)
    await conn.execute(CREATE_SITE_SETTINGS)
    await conn.execute(CREATE_USERS)
    await conn.execute(ALTER_RESERVATIONS_ADD_USER_ID)
    await conn.execute(ALTER_USERS_ADD_PHONE)
    await conn.execute(ALTER_USERS_EMAIL_NULLABLE)
    await conn.execute(CREATE_USERS_PHONE_INDEX)
    await conn.execute(CREATE_ORDERS)
    await conn.execute(ALTER_ORDERS_ADD_CUSTOMER_ID)
    await conn.execute(CREATE_STAFF)
    await conn.execute(CREATE_PIN_RESET_TOKENS)
    await conn.execute(CREATE_SECTIONS)
    for key, label, icon, ornament, sort_order in DEFAULT_SECTIONS:
        await conn.execute(
            "INSERT INTO sections (key, label, icon, ornament, sort_order) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (key) DO NOTHING",
            key, label, icon, ornament, sort_order,
        )


    # Seed defaults only if the table is empty
    for key, value in DEFAULT_SETTINGS:
        await conn.execute(
            "INSERT INTO site_settings (key, value) VALUES ($1, $2) ON CONFLICT (key) DO NOTHING",
            key, value,
        )


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    assert pool is not None, "Database pool not initialised"
    async with pool.acquire() as conn:
        yield conn  # type: ignore[misc]
