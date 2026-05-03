from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import configure_root_logger, get_logger
from app.core.security import limiter
from app.routers import chat, eligibility, timeline

configure_root_logger()
logger = get_logger(__name__)

app = FastAPI(
    title="Chunav Saathi API",
    description="AI-powered bilingual Indian election assistant",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# CORS: same-origin in production, dev origins configurable via env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
)


@app.get("/healthz", tags=["ops"], include_in_schema=False)
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "ok"})


# API routers (wired here; implementations filled in Prompt 4)
app.include_router(chat.router)
app.include_router(timeline.router)
app.include_router(eligibility.router)

# Serve React build — must be last so API routes take precedence
_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")
    logger.info("Serving React build from %s", _static_dir)
else:
    logger.info("No static dir found — frontend served separately (dev mode)")
