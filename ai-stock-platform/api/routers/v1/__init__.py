"""
API v1 Router Module
Created: 2025-06-19 07:48:11
Author: daparthi001
"""
import socket
import os
import sys
from datetime import datetime
from fastapi import APIRouter

# Create the router
router = APIRouter(prefix="/api/v1")

@router.get("/health")
async def health_check():
    """API v1 health check endpoint"""
    try:
        # Get environment variables
        API_ENV = os.environ.get("API_ENV", "development")

        # Basic system information
        system_info = {
            "hostname": socket.gethostname(),
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "environment": API_ENV,
            "db_host": os.environ.get("DB_HOST", "unknown").split(".")[0] if os.environ.get("DB_HOST") else "unknown"
        }
        
        return {
            "status": "healthy",
            "version": "1.0.1",
            "system": system_info
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }