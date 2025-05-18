"""
QuantumVestAI API - Main Application Entry Point
Created: 2025-05-18 16:11:55
Author: daparthi001
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from api.core.config import settings
from api.core.logging import setup_logging
from api.routers import (
    auth,
    users,
    stocks,
    forecast,
    watchlist,
    admin,
    sentiment,
    data,
    whitepaper
)

# Setup logging
logger = setup_logging()
logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the QuantumVestAI trading platform",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    debug=settings.DEBUG
)

# Configure CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    logger.info("Configuring CORS middleware")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
logger.info("Registering API routers")
api_routers = [
    (auth.router, "Authentication"),
    (users.router, "User Management"),
    (stocks.router, "Stock Data"),
    (forecast.router, "Forecasting"),
    (watchlist.router, "Watchlists"),
    (admin.router, "Administration"),
    (sentiment.router, "Sentiment Analysis"),
    (data.router, "Data Management"),
    (whitepaper.router, "Whitepapers")
]

for router, description in api_routers:
    logger.debug(f"Registering router: {description}")
    app.include_router(
        router,
        prefix=settings.API_V1_STR,
        tags=[description]
    )

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns basic application status and version information.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": "2025-05-18 16:11:55",
        "author": "daparthi001",
        "environment": "development" if settings.DEBUG else "production"
    }

if __name__ == "__main__":
    logger.info(f"Starting {settings.PROJECT_NAME} on http://0.0.0.0:8000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )