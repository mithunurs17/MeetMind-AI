"""main.py — MeetMind AI FastAPI application entry-point."""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.routes import (
    action_items_router,
    ai_router,
    auth_router,
    generate_router,
    health_router,
    meetings_router,
    trial_router,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("meetmind")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Meeting Minutes & Action Item Extractor",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Middleware (outermost = last added)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_MAX_REQUESTS,
    window_secs=settings.RATE_LIMIT_WINDOW_SECS,
    burst_paths=["/auth/login", "/auth/register"],
    burst_max=settings.AUTH_RATE_LIMIT_MAX,
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    logger.info("MeetMind AI started — debug=%s", settings.DEBUG)


def _seed_admin():
    from sqlalchemy.orm import Session
    from app.crud.user import create_user, get_user_by_username
    from app.schemas.auth import UserRegister
    from app.models.user import UserRole

    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_email    = os.environ.get("ADMIN_EMAIL",    "admin@meetmind.local")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@12345!")

    with Session(engine) as db:
        if get_user_by_username(db, admin_username) is None:
            create_user(db, UserRegister(
                email=admin_email,
                username=admin_username,
                password=admin_password,
                role=UserRole.ADMIN,
            ))
            logger.info("Default admin created: username=%s", admin_username)


# Routes
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(trial_router)       # <-- free trial (no auth)
app.include_router(generate_router)
app.include_router(meetings_router)
app.include_router(action_items_router)
app.include_router(ai_router)


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)