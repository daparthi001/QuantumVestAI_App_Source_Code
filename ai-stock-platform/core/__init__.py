"""Compatibility module redirecting to API core utilities."""

from api.core import (
    config,
    logger,
    middleware,
    security,
    utils,
)
from api.core.config.settings import settings, Settings, get_settings

# Re-export commonly used components from api.core
HTTPClient = utils.http_client.HTTPClient
HTTPClientConfig = utils.http_client.HTTPClientConfig
get_http_client = utils.http_client.get_http_client
safe_get_json = utils.http_client.safe_get_json
safe_post_json = utils.http_client.safe_post_json
cleanup_http_clients = utils.http_client.cleanup_http_clients

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
