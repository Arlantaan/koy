# Local preview server: serves the FastAPI API AND the static frontend
# (public/) on one origin so admin.html / index.html talk to the API locally.
# Run from the backend/ dir:  uvicorn dev_server:app --reload --port 8000
# Not used in production (nginx serves the static files there).
from pathlib import Path

from fastapi.staticfiles import StaticFiles

from app.main import app

_public = Path(__file__).resolve().parent.parent / "public"
# Mounted AFTER the API routers, so /api/* still matches first.
app.mount("/", StaticFiles(directory=str(_public), html=True), name="frontend")
