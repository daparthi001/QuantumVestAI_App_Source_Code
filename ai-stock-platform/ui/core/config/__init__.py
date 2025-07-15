"""
Config Module Initialization
Created: 2025-05-19 03:44:39
Updated: 2025-06-15 03:42:15
Author: daparthi001
"""
# Re-export settings from settings module
# Re-export settings directly from the API package to avoid accidentally
# importing the compatibility module which may expose the ``settings``
# submodule rather than the instance.
from api.core.config.settings import Settings, get_settings, settings

__all__ = ["settings", "Settings", "get_settings"]
