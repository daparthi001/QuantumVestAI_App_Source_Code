"""
Auth Routes - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.routes.auth.
New code should import directly from routes.auth.
"""

# Import directly from the module to avoid circular imports
API_URL = "http://quantumvestai-dev-api:8000/api/v1"
from routes.auth import router

__all__ = ['router']