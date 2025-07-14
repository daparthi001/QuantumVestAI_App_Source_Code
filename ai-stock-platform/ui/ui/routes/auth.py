"""
Auth Routes - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.routes.auth.
New code should import directly from routes.auth.
"""

# Import directly from the real routes package
from routes.auth import router

__all__ = ["router"]
