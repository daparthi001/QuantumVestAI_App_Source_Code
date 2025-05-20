"""
Core Middleware Implementation
Created: 2025-05-20 20:04:12
Author: daparthi001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from core.config import settings

def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the FastAPI application.
    
    Args:
        app (FastAPI): The FastAPI application instance
    """
    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Enable GZip compression
    app.add_middleware(
        GZipMiddleware,
        minimum_size=settings.GZIP_MIN_SIZE
    )
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS
    )

    # Add custom timing middleware
    @app.middleware("http")
    async def add_timing_header(request, call_next):
        import time
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response