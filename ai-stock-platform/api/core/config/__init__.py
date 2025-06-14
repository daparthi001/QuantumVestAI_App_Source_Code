"""
Config Module Initialization
Created: 2025-06-14 23:01:21
Author: daparthi001
"""
# Re-export settings from settings.py to make it accessible via core.config.settings
from .settings import Settings, settings

# This line ensures that when someone imports from core.config, they get the settings
__all__ = ['Settings', 'settings']