"""api_client.py — Backend API client with automatic auth injection."""
from __future__ import annotations

import os
from typing import Any

import requests

API_URL = os.getenv("API_URL", "http://backend:8000")


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
            return resp.json()
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def get_meetings(self, skip: int = 0, limit: int = 20) -> Any:
        try:
            resp = requests.get(
                f"{self.base_url}/meetings",
                params={"skip": skip, "limit": limit},
                headers=self._headers(),
                timeout=15,
            )
            payload = resp.json()
            return payload if resp.ok else {"error": _detail(payload, resp)}
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
            payload = resp.json()
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}

    def extract_meeting_from_file(self, title: str, upload_file) -> dict:
        try:
            files = {
                "file": (
                    upload_file.name,
                    upload_file.getvalue(),
                    upload_file.type or "application/octet-stream",
                )
            }
            resp = requests.post(
                f"{self.base_url}/ai/extract-file",
                data={"title": title},
                files=files,
                headers=self._headers(),
                timeout=180,
            )
            payload = resp.json()
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
            payload = resp.json()
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
            payload = resp.json()
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
            payload = resp.json()
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
            payload = resp.json()
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}

    def trial_status(self) -> dict:
        try:
            resp = requests.get(f"{self.base_url}/trial/status", timeout=10)
            return resp.json() if resp.ok else {"error": resp.text}
        except Exception as exc:
            return {"error": str(exc)}

    def trial_extract(self, title: str, raw_text: str) -> dict:
        try:
            resp = requests.post(
                f"{self.base_url}/trial/extract",
                json={"title": title, "raw_text": raw_text},
                timeout=120,
            )
            payload = resp.json()
            return payload if resp.ok else {"error": _detail(payload, resp)}
        except Exception as exc:
            return {"error": str(exc)}


def _detail(payload: Any, resp) -> str:
    if isinstance(payload, dict):
        return payload.get("detail") or payload.get("error") or resp.text
    return resp.text


api_client = APIClient()