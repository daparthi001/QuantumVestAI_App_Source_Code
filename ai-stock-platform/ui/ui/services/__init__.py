"""
UI Services Module - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.services.
New code should import directly from services.
"""

# Import all services directly to make them available through ui.services
from services.api_client import *
from services.yahoo_finance import *

__all__ = []
