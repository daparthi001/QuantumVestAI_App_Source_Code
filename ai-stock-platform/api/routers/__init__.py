"""
Routers Package
Updated: 2025-06-19 16:40:55
Author: daparthi001
"""
from routers.v1 import router as v1_router
from routers.social import router as social_router
from routers.docs import router as docs_router

__all__ = ["v1_router", "social_router", "docs_router"]
