from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_pool, init_db
import app.database as db_module
from app.routes.menu import router as menu_router
from app.routes.reservations import router as reservations_router
from app.routes.settings import router as settings_router
from app.routes.auth import router as auth_router
from app.routes.orders import router as orders_router
from app.routes.staff import router as staff_router
from app.routes.sections import router as sections_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    db_module.pool = await create_pool()
    async with db_module.pool.acquire() as conn:
        await init_db(conn)  # type: ignore[arg-type]
    yield
    await db_module.pool.close()


app = FastAPI(
    title="Koya API",
    version="1.0.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(menu_router)
app.include_router(reservations_router)
app.include_router(settings_router)
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(staff_router)
app.include_router(sections_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
