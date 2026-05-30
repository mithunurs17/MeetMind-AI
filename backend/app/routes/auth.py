"""
auth.py — Authentication & user-management routes.

Public  :  POST /auth/register   POST /auth/login   POST /auth/refresh
Protected: POST /auth/logout     GET  /auth/me       PUT  /auth/me/password
Admin   :  GET  /auth/users      GET  /auth/users/{id}  PUT  /auth/users/{id}
           DELETE /auth/users/{id}
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.crud.user import (
    authenticate_user,
    change_password,
    create_user,
    delete_user,
    get_all_users,
    get_refresh_token,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    revoke_all_user_tokens,
    revoke_refresh_token,
    store_refresh_token,
    update_user,
)
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    PasswordChange,
    RefreshRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Register ──────────────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    if get_user_by_username(db, data.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    return create_user(db, data)


# ── Login ─────────────────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtain JWT access + refresh tokens",
)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access = create_access_token(str(user.id), user.role.value)
    raw_refresh, expires_at = create_refresh_token(str(user.id))
    store_refresh_token(db, user.id, raw_refresh, expires_at)

    return TokenResponse(
        access_token=access,
        refresh_token=raw_refresh,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ── Refresh ───────────────────────────────────────────────────────────────
@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Get a new access token using a refresh token",
)
def refresh_access(body: RefreshRequest, db: Session = Depends(get_db)):
    from jose import JWTError
    try:
        payload = verify_refresh_token(body.refresh_token)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

    # Check the token exists in DB and hasn't been revoked
    stored = get_refresh_token(db, body.refresh_token)
    if stored is None or stored.revoked:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token revoked or not found")
    if stored.expires_at < datetime.now(tz=timezone.utc):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token expired")

    user = get_user_by_id(db, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")

    access = create_access_token(str(user.id), user.role.value)
    return AccessTokenResponse(
        access_token=access,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ── Logout ────────────────────────────────────────────────────────────────
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke the current refresh token",
)
def logout(
    body: RefreshRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    revoke_refresh_token(db, body.refresh_token)
    return {"detail": "Logged out successfully"}


# ── Logout all devices ────────────────────────────────────────────────────
@router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    summary="Revoke all refresh tokens (all devices)",
)
def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = revoke_all_user_tokens(db, current_user.id)
    return {"detail": f"Revoked {count} session(s)"}


# ── Current user profile ──────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ── Change password ───────────────────────────────────────────────────────
@router.put(
    "/me/password",
    status_code=status.HTTP_200_OK,
    summary="Change your password and revoke all refresh tokens",
)
def change_my_password(
    body: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.core.security import verify_password
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    change_password(db, current_user, body.new_password)
    revoke_all_user_tokens(db, current_user.id)
    return {"detail": "Password updated. All sessions have been revoked."}


# ═══════════════════════════════════════════════════════════════════════════
# Admin routes
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="[Admin] List all users",
)
def list_users(
    skip: int = 0,
    limit: int = 50,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_all_users(db, skip=skip, limit=limit)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="[Admin] Get a user by ID",
)
def get_user(
    user_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="[Admin] Update a user's profile or role",
)
def admin_update_user(
    user_id: int,
    data: UserUpdate,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return update_user(db, user, data)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="[Admin] Delete a user",
)
def admin_delete_user(
    user_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    delete_user(db, user)
    return {"detail": f"User {user_id} deleted"}