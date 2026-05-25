import os
import requests

API_URL = os.getenv("API_URL", "http://backend:8000")


class APIClient:
    """Client for interacting with MeetMind AI Backend API."""

    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url

    def health_check(self) -> dict:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_meetings(self, skip: int = 0, limit: int = 20) -> dict:
        try:
            response = requests.get(
                f"{self.base_url}/meetings",
                params={"skip": skip, "limit": limit},
                timeout=15,
            )
            payload = response.json()
            if response.ok:
                return payload
            return {"error": payload.get("detail") or payload.get("error") or response.text}
        except Exception as e:
            return {"error": str(e)}

    def extract_meeting_from_text(self, title: str, raw_text: str) -> dict:
        try:
            payload = {"title": title, "raw_text": raw_text}
            response = requests.post(
                f"{self.base_url}/ai/extract",
                json=payload,
                timeout=120,
            )
            payload = response.json()
            if response.ok:
                return payload
            return {"error": payload.get("detail") or payload.get("error") or response.text}
        except Exception as e:
            return {"error": str(e)}

    def extract_meeting_from_file(self, title: str, upload_file) -> dict:
        try:
            files = {
                "file": (
                    upload_file.name,
                    upload_file.getvalue(),
                    upload_file.type or "application/octet-stream",
                )
            }
            data = {"title": title}
            response = requests.post(
                f"{self.base_url}/ai/extract-file",
                data=data,
                files=files,
                timeout=180,
            )
            payload = response.json()
            if response.ok:
                return payload
            return {"error": payload.get("detail") or payload.get("error") or response.text}
        except Exception as e:
            return {"error": str(e)}

    def update_action_item_status(self, action_item_id: int, status: str) -> dict:
        try:
            response = requests.put(
                f"{self.base_url}/action-item/{action_item_id}",
                json={"status": status},
                timeout=15,
            )
            payload = response.json()
            if response.ok:
                return payload
            return {"error": payload.get("detail") or payload.get("error") or response.text}
        except Exception as e:
            return {"error": str(e)}


api_client = APIClient()
