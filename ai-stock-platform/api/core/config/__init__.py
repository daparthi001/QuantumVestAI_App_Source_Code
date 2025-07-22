"""Application configuration wrapper.

This module used to contain the application's configuration but the
implementation was moved to :mod:`core.config.settings`.  It now
re-exports the new settings objects so that older imports of
``api.core.config`` keep working.
"""

from .settings import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
