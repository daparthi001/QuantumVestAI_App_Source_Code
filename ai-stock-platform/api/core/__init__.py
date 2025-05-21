"""
Core Package
Created: 2025-05-21 14:16:44
Author: daparthi001
"""
# Import settings first to avoid circular imports
from core.config.settings import settings

# Then import logger
from core.logger import logger, setup_logger

__all__ = ['settings', 'logger', 'setup_logger']