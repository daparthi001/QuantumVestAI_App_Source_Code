"""
Core Package
Created: 2025-05-21 05:17:43
Author: daparthi001
"""
# First import settings as other modules depend on it
from core.config.settings import settings

# Then import other core modules
from core.logger import logger, setup_logger
from core.middleware import setup_middleware

__all__ = ['settings', 'logger', 'setup_logger', 'setup_middleware']