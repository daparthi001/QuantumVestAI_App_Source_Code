"""
Profile Routes - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.routes.profile.
New code should import directly from routes.profile.
"""

# Import directly from the module to avoid circular imports
from routes.profile import router

__all__ = ['router']
