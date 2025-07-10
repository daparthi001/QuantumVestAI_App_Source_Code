"""Compatibility module redirecting to API core utilities."""

from api.core import (
    config,
    middleware,
    security,
    utils,
)
from api.core.config.settings import settings, Settings, get_settings
from api.core.logger import logger, setup_logger
from .http_client import (
    HTTPClient,
    HTTPClientConfig,
    get_http_client,
    safe_get_json,
    safe_post_json,
    cleanup_http_clients,
)



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
    "logger",
    "setup_logger",
]
