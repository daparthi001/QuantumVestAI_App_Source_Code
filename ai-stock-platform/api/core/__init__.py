"""
Core Module Initialization
Created: 2025-06-14 23:01:21
Author: daparthi001
"""
# Import and re-export settings to make it accessible via core.settings
from .config.settings import Settings, settings
# Only import logger after settings are set up
from .logger import logger, setup_logger

__all__ = ['Settings', 'settings', 'logger', 'setup_logger']
