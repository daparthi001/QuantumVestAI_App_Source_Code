"""
UI Middleware Module - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.middleware.
New code should import directly from middleware.
"""

# Import all middleware components directly
from middleware.auth_middleware import *
from middleware.error_handlers import *

__all__ = []