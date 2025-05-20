"""
API Routers Initialization
Created: 2025-05-20 05:58:02
Author: daparthi001
"""

from fastapi import APIRouter
from routers.v1 import router as v1_router

# Create main router
router = APIRouter()

# Include versioned routers
router.include_router(v1_router, prefix="/v1")

__all__ = ['router']