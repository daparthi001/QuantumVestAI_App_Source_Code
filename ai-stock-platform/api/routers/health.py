"""
Health Check Router
Created: 2025-05-19 05:43:23
Author: daparthi001
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import psutil
import os

from api.db.session import get_db
from api.core.config import settings

router = APIRouter()

@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for Kubernetes probes
    Checks:
    - Database connection
    - Memory usage
    - Disk space
    - Environment variables
    """
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/app')
        
        # Check required environment variables
        required_vars = [
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_SERVER",
            "JWT_SECRET",
            "ALPHA_VANTAGE_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars 
                       if not getattr(settings, var, None)]
        
        if missing_vars:
            raise HTTPException(
                status_code=503,
                detail=f"Missing required environment variables: {missing_vars}"
            )
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "pod": {
                "name": settings.POD_NAME,
                "namespace": settings.POD_NAMESPACE
            },
            "database": "connected",
            "system": {
                "memory_usage": f"{memory.percent}%",
                "disk_usage": f"{disk.percent}%"
            },
            "version": settings.VERSION
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )