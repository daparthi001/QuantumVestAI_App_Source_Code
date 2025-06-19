"""
Settings Routes - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.routes.settings.
New code should import directly from routes.settings.
"""

# Import directly from the module to avoid circular imports
from routes.settings import router

__all__ = ['router']