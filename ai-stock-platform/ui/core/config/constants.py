"""
Application Constants

This module defines constants used throughout the application.
"""

# User roles
USER_ROLE_ADMIN = "admin"
USER_ROLE_PREMIUM = "premium"
USER_ROLE_BASIC = "basic"

# Authentication
AUTH_TOKEN_EXPIRY = 24  # hours
REFRESH_TOKEN_EXPIRY = 7  # days
PASSWORD_MIN_LENGTH = 8

# UI Constants
MAX_WATCHLIST_ITEMS = 50
MAX_PORTFOLIO_ITEMS = 100
DEFAULT_CHART_TIMEFRAME = "1y"
DEFAULT_PAGINATION_LIMIT = 20

# API Rate Limits
API_RATE_LIMIT_PER_MINUTE = 60
API_RATE_LIMIT_PER_DAY = 1000

# Cache settings
CACHE_TTL_DEFAULT = 300  # seconds
CACHE_TTL_STOCK_DATA = 900  # 15 minutes