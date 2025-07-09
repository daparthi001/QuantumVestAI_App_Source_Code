"""
Auth Routes - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.routes.auth.
New code should import directly from routes.auth.
"""

# Import directly from the real routes package
API_URL = "http://quantumvestai-dev-api:8000"
from ...routes.auth import router__all__ = ['router']