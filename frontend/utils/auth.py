"""
auth.py — Frontend authentication helpers.

Stores tokens in st.session_state (cleared on browser close).
Handles token refresh transparently.
"""
from __future__ import annotations

import time
from typing import Optional

import requests
import streamlit as st

from utils.api_client import API_URL


# ── Session-state keys ────────────────────────────────────────────────────
_KEY_ACCESS   = "_mm_access_token"
_KEY_REFRESH  = "_mm_refresh_token"
_KEY_EXPIRES  = "_mm_token_expires"   # unix timestamp
_KEY_USER     = "_mm_user"


# ── Token helpers ─────────────────────────────────────────────────────────
def _save_tokens(access: str, refresh: str, expires_in: int) -> None:
    st.session_state[_KEY_ACCESS]  = access
    st.session_state[_KEY_REFRESH] = refresh
    st.session_state[_KEY_EXPIRES] = time.time() + expires_in - 30   # 30-s buffer


def _refresh_if_needed() -> bool:
    """Return True if we still have a valid access token (refresh if needed)."""
    expires = st.session_state.get(_KEY_EXPIRES, 0)
    if time.time() < expires:
        return True                          # still fresh

    raw_refresh = st.session_state.get(_KEY_REFRESH)
    if not raw_refresh:
        return False

    try:
        resp = requests.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": raw_refresh},
            timeout=10,
        )
        if resp.ok:
            data = resp.json()
            st.session_state[_KEY_ACCESS]  = data["access_token"]
            st.session_state[_KEY_EXPIRES] = time.time() + data["expires_in"] - 30
            return True
    except Exception:
        pass
    return False


def get_auth_headers() -> dict:
    """Return Authorization header dict; auto-refreshes if needed."""
    if not _refresh_if_needed():
        return {}
    token = st.session_state.get(_KEY_ACCESS, "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def is_logged_in() -> bool:
    """Check if user is logged in without triggering a rerun."""
    access = st.session_state.get(_KEY_ACCESS, "")
    if not access:
        return False
    expires = st.session_state.get(_KEY_EXPIRES, 0)
    if time.time() < expires:
        return True
    # Try to refresh
    return _refresh_if_needed()


def current_user() -> Optional[dict]:
    return st.session_state.get(_KEY_USER)


def current_role() -> str:
    user = current_user()
    return user.get("role", "user") if user else ""


def is_admin() -> bool:
    return current_role() == "admin"


# ── Auth actions ──────────────────────────────────────────────────────────
def login(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, error_message)."""
    try:
        resp = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=15,
        )
        if resp.ok:
            data = resp.json()
            _save_tokens(data["access_token"], data["refresh_token"], data["expires_in"])
            _load_profile()
            return True, ""
        try:
            detail = resp.json().get("detail", "Login failed")
        except Exception:
            detail = "Login failed"
        return False, detail
    except Exception as exc:
        return False, str(exc)


def register(email: str, username: str, password: str) -> tuple[bool, str]:
    """Returns (success, error_message)."""
    try:
        resp = requests.post(
            f"{API_URL}/auth/register",
            json={"email": email, "username": username, "password": password},
            timeout=15,
        )
        if resp.ok:
            return True, ""
        try:
            detail = resp.json().get("detail", "Registration failed")
        except Exception:
            detail = "Registration failed"
        return False, detail
    except Exception as exc:
        return False, str(exc)


def logout() -> None:
    raw_refresh = st.session_state.get(_KEY_REFRESH, "")
    if raw_refresh:
        try:
            requests.post(
                f"{API_URL}/auth/logout",
                json={"refresh_token": raw_refresh},
                headers=get_auth_headers(),
                timeout=10,
            )
        except Exception:
            pass
    for key in [_KEY_ACCESS, _KEY_REFRESH, _KEY_EXPIRES, _KEY_USER]:
        st.session_state.pop(key, None)


def _load_profile() -> None:
    headers = get_auth_headers()
    if not headers:
        return
    try:
        resp = requests.get(f"{API_URL}/auth/me", headers=headers, timeout=10)
        if resp.ok:
            st.session_state[_KEY_USER] = resp.json()
    except Exception:
        pass