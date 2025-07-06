# Dashboard controller
# Last updated: 2025-06-20 02:53:45
# Updated by: daparthi001

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any, Union
import httpx
import logging
import time
import json
import os
from datetime import datetime, timedelta
from metrics import http_requests_total, http_request_duration_seconds
API_URL = "http://quantumvestai-dev-api:8000/api/v1"
# Set up logging
logger = logging.getLogger(__name__)

# Set up router
router = APIRouter()

# Set up templates
templates = Jinja2Templates(directory="templates")

# API client timeout (configurable via environment variable)
TIMEOUT = float(os.getenv("API_TIMEOUT", "10.0"))

# Cache configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # Default: 5 minutes
cache_store = {}

def get_cached_data(key: str) -> Union[Dict[str, Any], None]:
    """Get data from cache if it exists and is not expired.
    
    Args:
        key: Cache key
        
    Returns:
        Cached data or None if not found or expired
    """
    if not CACHE_ENABLED:
        return None
        
    if key in cache_store:
        entry = cache_store[key]
        if entry["expires"] > time.time():
            logger.debug(f"Cache hit for {key}")
            return entry["data"]
        else:
            logger.debug(f"Cache expired for {key}")
            del cache_store[key]
    
    logger.debug(f"Cache miss for {key}")
    return None

def set_cached_data(key: str, data: Dict[str, Any], ttl: int = CACHE_TTL) -> None:
    """Store data in cache with expiration time.
    
    Args:
        key: Cache key
        data: Data to cache
        ttl: Time to live in seconds
    """
    if not CACHE_ENABLED:
        return
        
    expires = time.time() + ttl
    cache_store[key] = {
        "data": data,
        "expires": expires
    }
    logger.debug(f"Cached data for {key}, expires in {ttl} seconds")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    request: Request,
    period: Optional[str] = Query("month", description="Time period for data analysis"),
    refresh: Optional[bool] = Query(False, description="Force refresh data from API")
):
    """
    Dashboard main view showing portfolio performance and analytics.
    
    Args:
        request: FastAPI request object
        user: Current authenticated user
        period: Time period for analysis (day, week, month, year, all)
        refresh: Whether to force refresh data from API
        
    Returns:
        HTMLResponse: Rendered dashboard template
    """
        logger.error(f"Request error: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request,
                "message": "Service temporarily unavailable. Please try again later.",
                "error_code": "API_CONN_ERR"
            }
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request,
                "message": "An unexpected error occurred while loading the dashboard.",
                "error_code": "DASHBOARD_ERR"
            }
        )

@router.get("/api/dashboard/data", response_model=Dict[str, Any])
async def dashboard_data(
    request: Request,
    request: Request,
    period: Optional[str] = Query("month"),
    refresh: Optional[bool] = Query(False)
):
    """
    API endpoint to get dashboard data for the frontend.
    Used for AJAX requests to update the dashboard dynamically.
    
    Args:
        request: FastAPI request object
        user: Current authenticated user
        period: Time period for analysis
        refresh: Whether to force refresh data from API
        
    Returns:
        Dict[str, Any]: Dashboard data in JSON format
    """
        logger.exception(f"Dashboard data error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving dashboard data"
        )

@router.get("/api/dashboard/insights", response_model=Dict[str, Any])
async def dashboard_insights(
    
):
    """
    API endpoint to get AI-generated insights for the dashboard.
    
    Args:
        user: Current authenticated user
        
    Returns:
        Dict[str, Any]: AI insights in JSON format
    """
        logger.exception(f"Insights error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving AI insights"
        )

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    
):
    """
    Admin dashboard view showing system metrics and user statistics.
    
    Args:
        request: FastAPI request object
        user: Current authenticated admin user
        
    Returns:
        HTMLResponse: Rendered admin dashboard template
    """
        # Re-raise HTTP exceptions (like 403 from validate_admin_access)
        raise
    except Exception as e:
        logger.exception(f"Admin dashboard error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading admin dashboard"
        )