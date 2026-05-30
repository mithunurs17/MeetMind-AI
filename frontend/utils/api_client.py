"""api_client.py — Backend API client with automatic auth injection."""
from __future__ import annotations

import os
from typing import Any

import requests

API_URL = os.getenv("API_URL", "http://backend:8000")


def _parse_json(resp: requests.Response) -> Any:
    """Safely parse JSON; return dict with error key on failure."""
    text = resp.text.strip()
    if not text:
        return {"error": f"Empty response (HTTP {resp.status_code})"}
    try:
        return resp.json()
    except Exception:
        return {"error": f"Invalid JSON response: {text[:200]}"}


def _detail(payload: Any, resp: requests.Response) -> str:
    if isinstance(payload, dict):
        return payload.get("detail") or payload.get("error") or resp.text
    return resp.text


class APIClient:
    """All backend calls go through here so auth headers are always injected."""

    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url

    @staticmethod
    def _headers() -> dict:
        try:
            from utils.auth import get_auth_headers
            return get_auth_headers()
        except Exception:
            return {}

    def health_check(self) -> dict:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            return _parse_json(resp)
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def get_meetings(self, skip: int = 0, limit: int = 20) -> Any:
        """Fetch meetings for the currently logged-in user only.

        The backend /meetings endpoint already filters by owner_id when a
        valid JWT is present, so regular users only ever see their own data.
        Admins see all meetings — that is intentional backend behaviour.
        """
        try:
            headers = self._headers()
            if not headers:
                # Not logged in — return empty list so pages degrade gracefully.
                return []
            resp = requests.get(
                f"{self.base_url}/meetings",
                params={"skip": skip, "limit": limit},
                headers=headers,
                timeout=15,
            )
            payload = _parse_json(resp)
            if resp.ok:
                return payload if isinstance(payload, list) else []
            return {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}

    def extract_meeting_from_text(self, title: str, raw_text: str) -> dict:
        try:
            resp = requests.post(
                f"{self.base_url}/ai/extract",
                json={"title": title, "raw_text": raw_text},
                headers=self._headers(),
                timeout=120,
            )
            payload = _parse_json(resp)
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}

    def extract_meeting_from_file(self, title: str, upload_file) -> dict:
        """Upload a file for AI extraction.

        ``title`` is sent as a multipart form field so the backend's
        ``title: str = Form(...)`` parameter receives it correctly.
        """
        try:
            files = {
                "file": (
                    upload_file.name,
                    upload_file.getvalue(),
                    upload_file.type or "application/octet-stream",
                )
            }
            # Send title as a form field (multipart), NOT as a query param.
            data = {"title": title or ""}

            resp = requests.post(
                f"{self.base_url}/ai/extract-file",
                data=data,
                files=files,
                headers=self._headers(),
                timeout=180,
            )
            payload = _parse_json(resp)
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}

    def update_action_item_status(self, action_item_id: int, status: str) -> dict:
        try:
            resp = requests.put(
                f"{self.base_url}/action-item/{action_item_id}",
                json={"status": status},
                headers=self._headers(),
                timeout=15,
            )
            payload = _parse_json(resp)
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}

    def get_users(self) -> Any:
        try:
            resp = requests.get(
                f"{self.base_url}/auth/users",
                headers=self._headers(),
                timeout=10,
            )
            payload = _parse_json(resp)
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}

    def update_user(self, user_id: int, data: dict) -> dict:
        try:
            resp = requests.put(
                f"{self.base_url}/auth/users/{user_id}",
                json=data,
                headers=self._headers(),
                timeout=10,
            )
            payload = _parse_json(resp)
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}

    def delete_user(self, user_id: int) -> dict:
        try:
            resp = requests.delete(
                f"{self.base_url}/auth/users/{user_id}",
                headers=self._headers(),
                timeout=10,
            )
            payload = _parse_json(resp)
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}

    def trial_status(self) -> dict:
        try:
            resp = requests.get(f"{self.base_url}/trial/status", timeout=10)
            if resp.ok:
                return _parse_json(resp)
            return {"trial_used": False}
        except Exception:
            return {"trial_used": False}

    def trial_extract(self, title: str, raw_text: str) -> dict:
        try:
            resp = requests.post(
                f"{self.base_url}/trial/extract",
                json={"title": title, "raw_text": raw_text},
                timeout=120,
            )
            payload = _parse_json(resp)
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}


api_client = APIClient()