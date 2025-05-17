"""
QuantumVestAI API - Main Application Entry Point
Created: 2025-05-17 14:56:36 UTC
Author: daparthi001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from typing import Optional

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
from api.core.config import settings
#from api.core.security 
from api.core.security_pkg.rds import validate_rds_connection
from api.core.db_init import initialize_database
from api.services.twitter_sentiment_scheduler import TwitterSentimentScheduler  # Correct import

# Setup logging
logger = setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the QuantumVestAI trading platform",
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(stocks.router, prefix=settings.API_V1_STR)
app.include_router(forecast.router, prefix=settings.API_V1_STR)
app.include_router(watchlist.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(sentiment.router, prefix=settings.API_V1_STR)
app.include_router(data.router, prefix=settings.API_V1_STR)
app.include_router(whitepaper.router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns basic application information and status.
    """
    return {
        "status": "healthy",
        "timestamp": "2025-05-17 14:56:36",
        "version": settings.VERSION,
        "environment": "development" if settings.DEBUG else "production"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )