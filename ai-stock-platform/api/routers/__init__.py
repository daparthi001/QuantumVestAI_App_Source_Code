"""
Routers Package
Created: 2025-06-19 07:48:11
Author: daparthi001
"""
import os

# Import existing routers if available
try:
    from routes.sentiment import router as sentiment_router
except ImportError:
    pass

try:
    from routes.admin import router as admin_router
except ImportError:
    pass

try:
    from routes.whitepaper_analysis import router as whitepaper_analysis_router
except ImportError:
    pass

# Import our new v1 router
from routers.v1 import router as v1_router

__all__ = ["v1_router"]

# Add other routers to __all__ if they exist
if "sentiment_router" in locals():
    __all__.append("sentiment_router")
if "admin_router" in locals():
    __all__.append("admin_router")
if "whitepaper_analysis_router" in locals():
    __all__.append("whitepaper_analysis_router")