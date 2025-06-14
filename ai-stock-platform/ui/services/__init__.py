# This file makes the services directory a proper Python package.
# It allows for easier imports of service modules throughout the application.

"""
Services Module

This module provides service interfaces for external API communications,
authentication, caching, and other service-level functionalities.
"""
# Import services directly
from services.api_client import APIClient
from services.auth_service import AuthService
from services.cache_service import CacheService
from services.forecast_service import ForecastService
from services.yahoo_finance import YahooFinanceService

__all__ = [
    'APIClient',
    'AuthService', 
    'CacheService',
    'ForecastService',
    'YahooFinanceService'
]

# This allows importing these classes directly from the services package
# For example: from ui.services import APIClient, YahooFinanceService