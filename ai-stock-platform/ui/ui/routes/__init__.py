"""
UI Routes Module - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.routes.
New code should import directly from routes.
"""

# Import all routes directly to make them available through ui.routes
from routes.auth import *
from routes.admin import *
from routes.forecast import *
from routes.predictability import *
from routes.watchlist import *
from routes.utils import *

__all__ = []