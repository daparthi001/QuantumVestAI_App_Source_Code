"""
Main application entry point
Created: 2025-05-19 02:59:42 UTC
Author: daparthi001
"""
from fastapi import FastAPI
from api.core.config import settings
import logging
from api.routers import auth_router, users_router, stocks_router, forecast_router, watchlist_router, admin_router, sentiment_router, data_router, whitepaper_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the QuantumVestAI trading platform",
    version=settings.VERSION
)

# Include routers
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(stocks_router, prefix="/api", tags=["stocks"])
app.include_router(forecast_router, prefix="/api", tags=["forecast"])
app.include_router(watchlist_router, prefix="/api", tags=["watchlist"])
app.include_router(admin_router, prefix="/api", tags=["admin"])
app.include_router(sentiment_router, prefix="/api", tags=["sentiment"])
app.include_router(data_router, prefix="/api", tags=["data"])
app.include_router(whitepaper_router, prefix="/api", tags=["whitepaper"])

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes
    Created: 2025-05-19 02:59:42 UTC
    Author: daparthi001
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "pod": settings.POD_NAME,
        "namespace": settings.POD_NAMESPACE,
        "environment": settings.ENVIRONMENT
    }