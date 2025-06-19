"""
API v1 Router Module
Created: 2025-06-19 15:30:25
Author: daparthi001
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v1/health")
async def api_health_check():
    """API v1 health check endpoint"""
    import os
    import sys
    import socket
    from datetime import datetime
    
    try:
        # Get environment variables
        API_ENV = os.environ.get("API_ENV", "development")
        API_VERSION = "1.0.0"

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
            "version": API_VERSION,
            "system": system_info
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }