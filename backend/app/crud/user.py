from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password, hash_token, verify_password
from app.models.user import RefreshToken, User, UserRole
from app.schemas.auth import UserRegister, UserUpdate


# ── User helpers ──────────────────────────────────────────────────────────
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username.lower()).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 50) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, data: UserRegister) -> User:
    user = User(
        email=data.email.lower(),
        username=data.username.lower(),
        hashed_password=hash_password(data.password),
        role=data.role or UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Return the user if credentials are valid, else None."""
    user = get_user_by_username(db, username)
    if user is None:
        # Constant-time dummy verify to prevent user-enumeration via timing
        hash_password("dummy_prevent_timing_attack")
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, new_password: str) -> User:
    user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


# ── Refresh token helpers ─────────────────────────────────────────────────
def store_refresh_token(
    db: Session,
    user_id: int,
    raw_token: str,
    expires_at: datetime,
) -> RefreshToken:
    rt = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(raw_token),
        expires_at=expires_at,
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def get_refresh_token(db: Session, raw_token: str) -> Optional[RefreshToken]:
    return db.query(RefreshToken).filter(
        RefreshToken.token_hash == hash_token(raw_token),
        RefreshToken.revoked.is_(False),
    ).first()


def revoke_refresh_token(db: Session, raw_token: str) -> bool:
    rt = get_refresh_token(db, raw_token)
    if rt is None:
        return False
    rt.revoked = True
    db.commit()
    return True


def revoke_all_user_tokens(db: Session, user_id: int) -> int:
    """Revoke all refresh tokens for a user (e.g. on password change)."""
    count = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
        .update({"revoked": True})
    )
    db.commit()
    return count


def purge_expired_tokens(db: Session) -> int:
    """Housekeeping — call periodically."""
    now = datetime.now(tz=timezone.utc)
    count = db.query(RefreshToken).filter(RefreshToken.expires_at < now).delete()
    db.commit()
    return count