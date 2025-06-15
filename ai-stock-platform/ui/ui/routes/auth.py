"""
Auth Routes - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.routes.auth.
New code should import directly from routes.auth.
"""

# Import all auth routes directly
from routes.auth import *

__all__ = []