"""
test_auth.py — Integration tests for the auth system.

Run:  pytest backend/tests/test_auth.py -v
"""
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────
def _register(client, username="testuser", email="test@example.com", password="TestPass1!"):
    return client.post("/auth/register", json={
        "email": email, "username": username, "password": password
    })


def _login(client, username="testuser", password="TestPass1!"):
    return client.post("/auth/login", json={"username": username, "password": password})


def _auth_header(client, username="testuser", password="TestPass1!"):
    r = _login(client, username, password)
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


# ── Registration ──────────────────────────────────────────────────────────
def test_register_success(client):
    r = _register(client)
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "testuser"
    assert data["role"] == "user"
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    _register(client, username="u1", email="dup@example.com")
    r = _register(client, username="u2", email="dup@example.com")
    assert r.status_code == 409


def test_register_duplicate_username(client):
    _register(client, username="same")
    r = _register(client, username="same", email="other@example.com")
    assert r.status_code == 409


def test_register_weak_password(client):
    r = _register(client, username="weakpw", email="w@example.com", password="abc")
    assert r.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────
def test_login_success(client):
    _register(client)
    r = _login(client)
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    _register(client, username="wrongpw")
    r = _login(client, username="wrongpw", password="WrongPass1!")
    assert r.status_code == 401


def test_login_nonexistent_user(client):
    r = _login(client, username="nobody", password="TestPass1!")
    assert r.status_code == 401


# ── Protected endpoints ───────────────────────────────────────────────────
def test_get_me_authenticated(client):
    _register(client, username="meuser", email="me@example.com")
    headers = _auth_header(client, username="meuser")
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["username"] == "meuser"


def test_get_me_unauthenticated(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


# ── Token refresh ─────────────────────────────────────────────────────────
def test_refresh_access_token(client):
    _register(client, username="refresher", email="rf@example.com")
    login_data = _login(client, username="refresher").json()

    r = client.post("/auth/refresh", json={"refresh_token": login_data["refresh_token"]})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_refresh_with_invalid_token(client):
    r = client.post("/auth/refresh", json={"refresh_token": "not.a.valid.token"})
    assert r.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────
def test_logout_revokes_refresh_token(client):
    _register(client, username="logoutuser", email="lo@example.com")
    login_data = _login(client, username="logoutuser").json()
    headers = {"Authorization": f"Bearer {login_data['access_token']}"}

    # Logout
    r = client.post("/auth/logout", json={"refresh_token": login_data["refresh_token"]}, headers=headers)
    assert r.status_code == 200

    # Refresh token should now be rejected
    r2 = client.post("/auth/refresh", json={"refresh_token": login_data["refresh_token"]})
    assert r2.status_code == 401


# ── Role-based access ─────────────────────────────────────────────────────
def test_admin_route_forbidden_for_user(client):
    _register(client, username="normaluser", email="nu@example.com")
    headers = _auth_header(client, username="normaluser")
    r = client.get("/auth/users", headers=headers)
    assert r.status_code == 403


def test_admin_route_allowed_for_admin(client):
    # The default admin is seeded at startup
    headers = _auth_header(client, username="admin", password="Admin@12345!")
    r = client.get("/auth/users", headers=headers)
    assert r.status_code == 200


# ── Meeting ownership ─────────────────────────────────────────────────────
def test_user_cannot_access_others_meeting(client):
    _register(client, username="owner1", email="o1@example.com")
    _register(client, username="owner2", email="o2@example.com")

    h1 = _auth_header(client, username="owner1")
    h2 = _auth_header(client, username="owner2")

    # Owner1 creates a meeting
    r = client.post("/generate", json={
        "title": "Owner1 Meeting",
        "raw_text": "private content",
    }, headers=h1)
    assert r.status_code == 201
    meeting_id = r.json()["id"]

    # Owner2 should be denied
    r2 = client.get(f"/meeting/{meeting_id}", headers=h2)
    assert r2.status_code == 403


def test_admin_can_access_all_meetings(client):
    _register(client, username="regularuser", email="ru@example.com")
    h_user  = _auth_header(client, username="regularuser")
    h_admin = _auth_header(client, username="admin", password="Admin@12345!")

    r = client.post("/generate", json={
        "title": "User Meeting",
        "raw_text": "some content here",
    }, headers=h_user)
    assert r.status_code == 201
    meeting_id = r.json()["id"]

    r2 = client.get(f"/meeting/{meeting_id}", headers=h_admin)
    assert r2.status_code == 200


# ── Password change ───────────────────────────────────────────────────────
def test_password_change(client):
    _register(client, username="pwchanger", email="pwc@example.com")
    headers = _auth_header(client, username="pwchanger")

    r = client.put("/auth/me/password", json={
        "current_password": "TestPass1!",
        "new_password": "NewPass2@"
    }, headers=headers)
    assert r.status_code == 200

    # Old password should no longer work
    r2 = _login(client, username="pwchanger", password="TestPass1!")
    assert r2.status_code == 401

    # New password should work
    r3 = _login(client, username="pwchanger", password="NewPass2@")
    assert r3.status_code == 200