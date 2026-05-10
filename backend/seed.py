from __future__ import annotations

"""Seed the PostgreSQL database from public/mock-menu.json."""

import asyncio
import json
import sys
from pathlib import Path

import asyncpg

from app.config import settings
from app.database import create_pool, init_db

MOCK_MENU = Path(__file__).parent.parent / "public" / "mock-menu.json"


async def seed() -> None:
    pool = await create_pool()
    async with pool.acquire() as conn:
        await init_db(conn)  # type: ignore[arg-type]

        with MOCK_MENU.open() as f:
            items: list[dict[str, object]] = json.load(f)

        count: int = await conn.fetchval("SELECT COUNT(*) FROM menu_items") or 0

        if count and "--force" not in sys.argv:
            print(f"Database already has {count} items. Use --force to re-seed.")
            await pool.close()
            return

        if count:
            await conn.execute("DELETE FROM menu_items")

        async with conn.transaction():
            for i, item in enumerate(items):
                await conn.execute(
                    "INSERT INTO menu_items "
                    "(id, section, name, description, price, image, hidden, sort_order, insert_after, badge) "
                    "VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)",
                    item["id"],
                    item["section"],
                    item["name"],
                    item.get("description"),
                    item.get("price"),
                    item.get("image"),
                    int(item.get("hidden", 0)),  # type: ignore[arg-type]
                    i + 1,
                    item.get("insert_after"),
                    item.get("badge") or "",
                )

        print(f"Seeded {len(items)} menu items into {settings.database_url.split('@')[-1]}")
    await pool.close()


if __name__ == "__main__":
    asyncio.run(seed())
