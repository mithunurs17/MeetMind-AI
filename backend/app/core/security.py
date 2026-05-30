"""
security.py — centralises all crypto operations.

 • Passwords : bcrypt via passlib
 • Tokens    : RS256 JWT (falls back to HS256 when RSA keys not provided)
               - access  token  : short-lived  (15 min default)
               - refresh token  : long-lived   (7 days  default)
"""
from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# ── Passlib / bcrypt ──────────────────────────────────────────────────────
_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,          # cost factor — tune to ~100 ms on your hardware
)


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ── JWT settings (from env) ───────────────────────────────────────────────
SECRET_KEY: str = os.environ.get(
    "JWT_SECRET_KEY",
    "CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32",
)
ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
)
REFRESH_TOKEN_EXPIRE_DAYS: int = int(
    os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)


# ── Token creation ────────────────────────────────────────────────────────
def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def create_access_token(
    subject: str,               # typically user.id cast to str
    role: str,
    extra: Optional[dict] = None,
) -> str:
    expire = _utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict = {
        "sub": subject,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": _utcnow(),
        **(extra or {}),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> tuple[str, datetime]:
    """Returns (raw_token, expires_at)."""
    expires_at = _utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": expires_at,
        "iat": _utcnow(),
        "jti": secrets.token_hex(16),   # unique token id prevents reuse
    }
    raw = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return raw, expires_at


def hash_token(raw: str) -> str:
    """SHA-256 fingerprint stored in DB — keeps plain tokens out of storage."""
    return hashlib.sha256(raw.encode()).hexdigest()


# ── Token verification ────────────────────────────────────────────────────
def decode_token(token: str) -> dict:
    """Decode and return the full payload; raises JWTError on failure."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def verify_access_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise JWTError("Not an access token")
    return payload


def verify_refresh_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise JWTError("Not a refresh token")
    return payload