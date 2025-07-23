"""Lightweight APIClient wrapper used for tests."""
from __future__ import annotations

from pathlib import Path
import json
import requests

from core.config import settings

class APIClient:
    """Simplified API client for unit tests."""
    def __init__(self, token: str | None = None):
        self.base_url = settings.API_BASE_URL
        self.token = token
        self.timeout = 10

    @property
    def headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _normalize_endpoint(self, endpoint: str) -> str:
        if endpoint.startswith("/api/v1"):
            return endpoint
        if endpoint.startswith("/"):
            return f"/api/v1{endpoint}"
        return f"/api/v1/{endpoint}"

    def build_url(self, endpoint: str) -> str:
        return self.base_url.rstrip("/") + self._normalize_endpoint(endpoint)

    def get(self, endpoint: str, params: dict | None = None) -> dict | None:
        try:
            resp = requests.get(self.build_url(endpoint), headers=self.headers, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def post(self, endpoint: str, data: dict | None = None) -> dict | None:
        try:
            resp = requests.post(self.build_url(endpoint), headers=self.headers, data=json.dumps(data or {}), timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def put(self, endpoint: str, data: dict | None = None) -> dict | None:
        try:
            resp = requests.put(self.build_url(endpoint), headers=self.headers, data=json.dumps(data or {}), timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def delete(self, endpoint: str) -> dict | None:
        try:
            resp = requests.delete(self.build_url(endpoint), headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def post_form(self, endpoint: str, data: dict | None = None) -> dict | None:
        try:
            resp = requests.post(self.build_url(endpoint), headers=self.headers, data=data, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

__all__ = ["APIClient"]
