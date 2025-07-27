"""
QuantumVestAI Utility Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from core.config.settings import settings

# Setup router
router = APIRouter(prefix="/utils", tags=["utils"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

@router.get("/health")
async def health_check():
    """Health check endpoint for utility service"""
    return {
        "status": "healthy",
        "service": "utils",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "author": "hemanth9398"
    }

@router.get("/api/version")
async def get_version_info():
    """Get version and build information"""
    try:
        return JSONResponse({
            "status": "success",
            "version": "2.0.0",
            "author": "hemanth9398",
            "updated": "2025-07-07 21:54:42",
                "build": {
                "environment": "production",
                "features": ["auth", "dashboard", "forecast", "market", "watchlist", "predictability", "settings"]
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting version info: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)

@router.get("/api/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    try:
        metrics = {
            "performance": {
                "cpu_usage": 23.5,
                "memory_usage": 67.2,
                "disk_usage": 45.8,
                "network_io": 125.6
            },
            "application": {
                "active_sessions": 156,
                "requests_per_minute": 450,
                "avg_response_time": 145.6,
                "error_rate": 0.02
            },
            "features": {
                "predictions_generated": 12450,
                "stocks_tracked": 5000,
                "alerts_active": 2340,
                "users_online": 89
            }
        }
        
        return JSONResponse({
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)
