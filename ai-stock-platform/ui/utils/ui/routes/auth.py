"""
Auth Routes - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.routes.auth.
New code should import directly from routes.auth.
"""

# Import directly from the module to avoid circular imports
from routes.auth import get_current_user, router

__all__ = ['get_current_user', 'router']