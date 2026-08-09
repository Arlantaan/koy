from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

# In-memory sliding-window counters keyed by "scope:ip".
# Per-worker (each uvicorn worker keeps its own map) — fine for brute-force
# protection: the effective ceiling is `limit` × worker_count, still far below
# what a password-guessing attack needs.
_hits: dict[str, deque] = defaultdict(deque)


def client_ip(request: Request) -> str:
    """Real client IP behind Cloudflare + nginx."""
    h = request.headers
    cf = h.get("cf-connecting-ip")
    if cf:
        return cf.strip()
    xff = h.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(request: Request, scope: str, limit: int, window_seconds: int) -> None:
    """Raise HTTP 429 if this IP exceeded `limit` requests within `window_seconds`."""
    ip = client_ip(request)
    bucket = f"{scope}:{ip}"
    now = time.monotonic()
    dq = _hits[bucket]
    cutoff = now - window_seconds
    while dq and dq[0] < cutoff:
        dq.popleft()
    if len(dq) >= limit:
        retry = int(dq[0] + window_seconds - now) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many attempts. Please wait {retry}s and try again.",
            headers={"Retry-After": str(retry)},
        )
    dq.append(now)
