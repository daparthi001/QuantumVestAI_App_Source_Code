"""
Health Check Router
Updated: 2025-06-19 03:54:33
Author: daparthi001
"""
from fastapi import APIRouter, status
import socket
from datetime import datetime
import logging
import os

from core.models.response import StandardResponse

router = APIRouter(tags=["Health"])
logger = logging.getLogger("quantumvestai_api.health")

# Note: No prefix here - it will be added by the main app

@router.get(
    "/health/details",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed API Health Check",
    description="Get detailed health status of the API and its dependencies"
)
async def detailed_health_check():
    """Detailed API health check"""
    logger.info("Detailed health check requested")
    
    try:
        # System information
        system_info = {
            "hostname": socket.gethostname(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "python_version": os.sys.version,
            "environment": os.environ.get("ENVIRONMENT", "development"),
        }
        
        # Health data
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": "unknown",  # Would need process start time
            "system": system_info
        }
        
        return StandardResponse(
            status="success",
            message="API is healthy",
            data=health_data
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return StandardResponse(
            status="error",
            message=f"Health check failed: {str(e)}",
            data={"status": "unhealthy"}
        )