"""
Main application entry point
Created: 2025-05-19 02:59:42 UTC
Author: daparthi001
"""
from fastapi import FastAPI
from api.core.config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the QuantumVestAI trading platform",
    version=settings.VERSION
)

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