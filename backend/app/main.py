"""
AquaPura -- FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import chat, history, predict
from app.routers import auth as auth_router
from app.routers import users as users_router
from app.services.model_loader import load_model

# Import ORM models so SQLAlchemy registers them with Base.metadata
import app.models.user      # noqa: F401
import app.models.analysis  # noqa: F401
from app.database.base import Base, engine


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    FastAPI lifespan handler.

    Code before 'yield' runs once at startup.
    Code after 'yield' runs once at shutdown.
    """
    # ── Startup ────────────────────────────────────────────────────────────
    # Create database tables for any models not yet present.
    Base.metadata.create_all(bind=engine)

    # Load the ML model into memory.
    load_model()

    yield  # application runs while suspended here

    # ── Shutdown: nothing to clean up ──────────────────────────────────────


app = FastAPI(
    title="AquaPura API",
    description=(
        "AI-powered water-quality assessment and potability prediction. "
        "This API provides preliminary screening only and does not replace "
        "certified laboratory water-quality testing."
    ),
    version="0.4.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(predict.router,      prefix="/api", tags=["Prediction"])
app.include_router(chat.router,         prefix="/api", tags=["Chat"])
app.include_router(history.router,      prefix="/api", tags=["History"])
app.include_router(auth_router.router,  prefix="/api", tags=["Auth"])
app.include_router(users_router.router, prefix="/api", tags=["Users"])


@app.get("/", tags=["Health"])
def health_check():
    """Simple liveness probe. Returns 200 when the application is running."""
    return {"status": "ok", "app": "AquaPura"}
