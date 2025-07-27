"""Lightweight API client used in tests."""
from __future__ import annotations

import os
import json
import requests

try:  # Prefer project settings when available
    from core.config.settings import settings  # type: ignore
except Exception:  # Fallback for isolated usage
    class _Settings:
        """Minimal settings object for tests."""

        API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost")

    settings = _Settings()


class APIClient:
    """Simplified HTTP client for unit tests."""

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
            resp = requests.get(
                self.build_url(endpoint), headers=self.headers, params=params, timeout=self.timeout
            )
            if resp.status_code >= 400:
                return None
            return resp.json()
        except Exception:
            return None

    def post(self, endpoint: str, data: dict | None = None) -> dict | None:
        try:
            resp = requests.post(
                self.build_url(endpoint),
                headers=self.headers,
                data=json.dumps(data or {}),
                timeout=self.timeout,
            )
            if resp.status_code >= 400:
                return None
            return resp.json()
        except Exception:
            return None

    def put(self, endpoint: str, data: dict | None = None) -> dict | None:
        try:
            resp = requests.put(
                self.build_url(endpoint),
                headers=self.headers,
                data=json.dumps(data or {}),
                timeout=self.timeout,
            )
            if resp.status_code >= 400:
                return None
            return resp.json()
        except Exception:
            return None

    def delete(self, endpoint: str) -> dict | None:
        try:
            resp = requests.delete(
                self.build_url(endpoint), headers=self.headers, timeout=self.timeout
            )
            if resp.status_code >= 400:
                return None
            # DELETE endpoints often return no content
            return resp.json() if resp.content else None
        except Exception:
            return None

    def post_form(self, endpoint: str, data: dict | None = None) -> dict | None:
        try:
            resp = requests.post(
                self.build_url(endpoint), headers=self.headers, data=data, timeout=self.timeout
            )
            if resp.status_code >= 400:
                return None
            return resp.json()
        except Exception:
            return None

__all__ = ["APIClient"]
