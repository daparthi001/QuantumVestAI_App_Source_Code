"""Compatibility module exposing UI core utilities."""

from ui.core.http_client import (
    HTTPClient,
    HTTPClientConfig,
    get_http_client,
    safe_get_json,
    safe_post_json,
    cleanup_http_clients,
)
from ui.core.config.settings import settings, Settings, get_settings

__all__ = [
    "HTTPClient",
    "HTTPClientConfig",
    "get_http_client",
    "safe_get_json",
    "safe_post_json",
    "cleanup_http_clients",
    "settings",
    "Settings",
    "get_settings",
]
