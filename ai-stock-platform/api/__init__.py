"""
QuantumVestAI API Package
Created: 2025-05-20 04:36:10
Author: daparthi001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings

__version__ = "1.0.0"

def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=__version__,
        description="AI-powered stock analysis platform",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    return app