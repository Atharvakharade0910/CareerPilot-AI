from contextlib import asynccontextmanager
import asyncio
from collections import defaultdict, deque
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.api.routes import router
from app.api.opportunities import router as opportunities_router
from app.api.intelligence import router as intelligence_router
from app.api.interviews import router as interviews_router
from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    task = asyncio.create_task(_reminder_loop())
    try:
        yield
    finally:
        task.cancel()

async def _reminder_loop():
    # Best-effort local reminder loop; durable deployments should run a worker.
    while True:
        await asyncio.sleep(60)


app = FastAPI(title="CareerPilot AI", version="0.1.0", lifespan=lifespan)
if settings.sentry_dsn:
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1, send_default_pii=False)
    except ImportError:
        pass
_attempts = defaultdict(deque)


@app.middleware("http")
async def protection(request: Request, call_next):
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("origin")
        if origin and origin != settings.frontend_origin:
            return JSONResponse({"detail": "Origin not allowed."}, 403)
        if request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse({"detail": "Cross-site request denied."}, 403)
    if request.url.path.startswith("/api/auth/") and request.method == "POST":
        key = request.client.host
        bucket = _attempts[key]
        now = time.monotonic()
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= settings.auth_rate_limit_per_minute:
            return JSONResponse(
                {"detail": "Too many requests. Try again in one minute."}, 429
            )
        bucket.append(now)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(router)
app.include_router(opportunities_router)
app.include_router(intelligence_router)
app.include_router(interviews_router)


@app.get("/api/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "postgresql",
        "phase": 1,
        "parser": "evidence-rules-v1",
        "ai_provider": "gemini" if settings.gemini_api_key else "local-fallback",
        "gemini_model": settings.gemini_model,
    }
