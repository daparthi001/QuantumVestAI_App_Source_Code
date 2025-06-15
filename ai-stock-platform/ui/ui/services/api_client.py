"""
API Client - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.services.api_client.
New code should import directly from services.api_client.
"""

# Import directly from the module to avoid circular imports
from services.api_client import APIClient

__all__ = ['APIClient']