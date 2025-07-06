"""
Services Module

This module provides service interfaces for external API communications,
authentication, caching, and other service-level functionalities.
"""
# The order of imports is important to avoid circular dependencies

# Import api_client first (without importing from itself)
# Use a relative import to avoid circular references
from .api_client import APIClient

# Then import other services
from .auth_service import AuthService
from .cache_service import CacheService

# Only import these if they exist
    # Create a stub if the service doesn't exist
    class ForecastService:
        """Stub for forecast service"""
        pass

    # Create a stub if the service doesn't exist
    class YahooFinanceService:
        """Stub for Yahoo Finance service"""
        pass

__all__ = [
    'APIClient',
    'AuthService', 
    'CacheService',
    'ForecastService',
    'YahooFinanceService'
]