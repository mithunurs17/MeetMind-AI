"""
dependencies.py — FastAPI DI for authentication and authorisation.

Usage in routes:
    current_user: User = Depends(get_current_user)
    _admin: User       = Depends(require_admin)
    maybe_user         = Depends(get_optional_user)
"""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import verify_access_token
from app.database import get_db
from app.models.user import User, UserRole

_bearer = HTTPBearer(auto_error=False)


def _extract_user(
    credentials: Optional[HTTPAuthorizationCredentials],
    db: Session,
) -> Optional[User]:
    if credentials is None:
        return None
    try:
        payload = verify_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None

    user: Optional[User] = db.query(User).filter(
        User.id == user_id,
        User.is_active.is_(True),
    ).first()
    return user


# ── Public dependency — raises 401 if no valid token ─────────────────────
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    user = _extract_user(credentials, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ── Admin-only dependency ─────────────────────────────────────────────────
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# ── Optional auth (public routes that can also accept a user) ─────────────
def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    return _extract_user(credentials, db)