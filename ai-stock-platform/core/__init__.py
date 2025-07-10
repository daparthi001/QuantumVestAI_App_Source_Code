"""Compatibility layer aliasing to api.core."""
import importlib, sys

# Import the API configuration modules we rely on. Avoid importing optional
# subpackages that would trigger database connections or other heavy side
# effects during test collection.
from api.core import config, logger
from api.core.config.settings import settings, Settings, get_settings

# Lightweight HTTP client utilities are provided by the UI core package.
from ui.core import http_client as ui_http_client

# Expose api.core submodules under the ``core`` namespace so imports like
# ``core.logger`` resolve correctly even when this lightweight compatibility
# package is imported first.
import sys

sys.modules.setdefault(__name__ + ".config", config)
sys.modules.setdefault(__name__ + ".logger", logger)

# Re-export commonly used components from api.core
HTTPClient = ui_http_client.HTTPClient
HTTPClientConfig = ui_http_client.HTTPClientConfig
get_http_client = ui_http_client.get_http_client
safe_get_json = ui_http_client.safe_get_json
safe_post_json = ui_http_client.safe_post_json
cleanup_http_clients = ui_http_client.cleanup_http_clients

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
