"""
CORS Configuration Middleware
Updated: 2025-06-19 03:33:28
Enhanced: 2025-01-09 (AI Assistant)
Author: daparthi001
"""
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Try to import settings safely
try:
    from core.config import settings
    FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
except ImportError:
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')


def get_cors_origins() -> List[str]:
    """Get CORS origins from environment or use defaults"""
    # Check for environment variable first
    cors_origins_env = os.environ.get("CORS_ORIGINS")
    if cors_origins_env:
        return [origin.strip() for origin in cors_origins_env.split(",")]
    
    # Default origins for development and production
    default_origins = [
        FRONTEND_URL,
        # Local development
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8001",
        # Development and production domains
        "https://dev.quantumvestai.com",
        "https://quantumvestai.com",
        "https://www.quantumvestai.com",
        "https://app.quantumvestai.com",
        "https://api.quantumvestai.com"
    ]
    
    # Only allow wildcard in development
    if os.environ.get("ENVIRONMENT", "development").lower() == "development":
        default_origins.append("*")
    
    return default_origins


def configure_cors(app: FastAPI) -> FastAPI:
    """Configure CORS for the FastAPI application with enhanced security"""
    
    origins = get_cors_origins()
    
    # Log CORS configuration
    import logging
    logger = logging.getLogger("api")
    logger.info(f"Configuring CORS with origins: {origins}")
    
    # Determine if we should allow credentials
    allow_credentials = True
    
    # If wildcard is in origins, we cannot allow credentials
    if "*" in origins:
        allow_credentials = False
        logger.warning("Wildcard (*) in CORS origins detected. Credentials will be disabled.")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=[
            "GET",
            "POST", 
            "PUT",
            "DELETE",
            "OPTIONS",
            "PATCH"
        ],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-API-Key",
            "X-Request-ID",
            "Accept",
            "Accept-Language",
            "Cache-Control",
            "User-Agent"
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Process-Time",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Used",
            "X-RateLimit-Window"
        ],
        max_age=86400,  # Cache preflight requests for 24 hours
    )
    
    return app


def configure_cors_strict(app: FastAPI) -> FastAPI:
    """Configure CORS with strict settings for production"""
    
    # Production-only origins (no wildcards)
    origins = [
        "https://quantumvestai.com",
        "https://www.quantumvestai.com",
        "https://app.quantumvestai.com"
    ]
    
    # Add custom origins from environment
    custom_origins = os.environ.get("CORS_ORIGINS_STRICT")
    if custom_origins:
        origins.extend([origin.strip() for origin in custom_origins.split(",")])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
        max_age=86400,
    )
    
    return app
