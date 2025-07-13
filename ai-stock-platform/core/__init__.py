"""Compatibility layer aliasing to api.core."""
import importlib
# Expose api.core submodules under the ``core`` namespace so imports like
# ``core.logger`` resolve correctly even when this lightweight compatibility
# package is imported first.
import sys

# Import the API configuration modules we rely on. Avoid importing optional
# subpackages that would trigger database connections or other heavy side
# effects during test collection.
from api.core import config
from api.core import database as api_database
from api.core import exceptions as api_exceptions
from api.core import logger
from api.core import models as api_models
from api.core import responses as api_responses
from api.core import security as api_security
from api.core import validation as api_validation
from api.core.config.settings import Settings, get_settings, settings

# Lightweight HTTP client utilities are provided by the UI core package.
from ui.core import http_client as ui_http_client

from . import http_client

sys.modules.setdefault(__name__ + ".config", config)
sys.modules.setdefault(__name__ + ".logger", logger)
sys.modules.setdefault(__name__ + ".exceptions", api_exceptions)
sys.modules.setdefault(__name__ + ".responses", api_responses)
sys.modules.setdefault(__name__ + ".validation", api_validation)
sys.modules.setdefault(__name__ + ".database", api_database)
sys.modules.setdefault(__name__ + ".security", api_security)
sys.modules.setdefault(__name__ + ".models", api_models)

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
