"""
config.py — centralised, validated configuration via pydantic-settings.
"""
from __future__ import annotations

import json
import os
import warnings
from functools import lru_cache
from typing import Any, List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "MeetMind AI"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = False

    DATABASE_URL: str = (
        "postgresql://meetmind_user:meetmind_password@db:5432/meetmind_db"
    )

    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Accepts JSON array, comma-separated string, or a list.
    # On Render set: CORS_ORIGINS=https://your-frontend.onrender.com
    CORS_ORIGINS: Any = [
        "http://localhost:8501",
        "http://frontend:8501",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    RATE_LIMIT_MAX_REQUESTS: int = 200
    RATE_LIMIT_WINDOW_SECS: int = 60
    AUTH_RATE_LIMIT_MAX: int = 10

    AI_API_KEY: str = ""
    AI_API_BASE: str = "https://api.groq.com/openai/v1"
    AI_MODEL: str = "openai/gpt-oss-120b"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("["):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(i).strip() for i in parsed]
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return [str(v)]

    @field_validator("CORS_ALLOW_METHODS", "CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def parse_list_fields(cls, v: Any) -> List[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("["):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(i).strip() for i in parsed]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return [str(v)]

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def warn_weak_secret(cls, v: str) -> str:
        if v in ("CHANGE_ME_IN_PRODUCTION", "secret", "password"):
            warnings.warn(
                "JWT_SECRET_KEY is set to a default/weak value. "
                "Set a strong random key in production.",
                stacklevel=2,
            )
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite://")):
            raise ValueError("DATABASE_URL must be a postgresql or sqlite URL")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


_s = get_settings()

DATABASE_URL          = _s.DATABASE_URL
AI_API_KEY            = _s.AI_API_KEY
AI_API_BASE           = _s.AI_API_BASE
AI_MODEL              = _s.AI_MODEL
APP_NAME              = _s.APP_NAME
APP_VERSION           = _s.APP_VERSION
DEBUG                 = _s.DEBUG
CORS_ORIGINS          = _s.CORS_ORIGINS
API_HOST              = _s.API_HOST
API_PORT              = _s.API_PORT
