"""
Health Check Router
Updated: 2025-06-19 04:23:15
Author: daparthi001
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import socket
import platform
import psutil
import os
from datetime import datetime
import logging

from core.database import get_db_session
from core.models.response import StandardResponse

# Create router WITHOUT a prefix (prefix will be added in main.py)
router = APIRouter(tags=["Health"])

logger = logging.getLogger("quantumvestai_api.health")

@router.get(
    "/detailed",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed Health Check",
    description="Get detailed health status of the API and its dependencies"
)
async def detailed_health_check(db: AsyncSession = Depends(get_db_session)):
    """Detailed API health check"""
    logger.info("Detailed health check requested")
    
    try:
        # Check database connection
        db_healthy = True
        db_error = None
        
        try:
            await db.execute("SELECT 1")
        except Exception as e:
            db_healthy = False
            db_error = str(e)
        
        # System information
        system_info = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "memory_percent": psutil.virtual_memory().percent,
            "cpu_percent": psutil.cpu_percent(interval=0.1)
        }
        
        # Process information
        process = psutil.Process(os.getpid())
        process_info = {
            "pid": process.pid,
            "memory_usage_mb": round(process.memory_info().rss / (1024 * 1024), 2),
            "threads": process.num_threads(),
            "open_files": len(process.open_files()),
            "connections": len(process.connections()),
            "start_time": datetime.fromtimestamp(process.create_time()).isoformat()
        }
        
        # Environment information
        env_info = {
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "debug": os.environ.get("DEBUG", "false") == "true",
            "pod_name": os.environ.get("POD_NAME", "unknown"),
            "node_name": os.environ.get("NODE_NAME", "unknown")
        }
        
        health_data = {
            "status": "healthy" if db_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "error": db_error
            },
            "system": system_info,
            "process": process_info,
            "environment": env_info
        }
        
        return StandardResponse(
            status="success",
            message="Health check completed",
            data=health_data
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return StandardResponse(
            status="error",
            message=f"Health check failed: {str(e)}",
            data={"status": "error"}
        )