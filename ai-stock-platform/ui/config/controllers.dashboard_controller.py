# Dashboard controller
# Last updated: 2025-06-20 02:51:31
# Updated by: daparthi001

from fastapi import APIRouter, HTTPException, Request, Query, status
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

API_URL = "http://quantumvestai-dev-api:8000"
# Set up logging
logger = logging.getLogger(__name__)

# Set up router
router = APIRouter()

# Set up templates
templates = Jinja2Templates(directory="templates")

def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

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
    Dashboard main view showing portfolio performance and analytics (demo mode).
    
    Args:
        request: FastAPI request object
        period: Time period for analysis (day, week, month, year, all)
        refresh: Whether to force refresh data from API
        
    Returns:
        HTMLResponse: Rendered dashboard template
    """
    try:
        # Start timing for metrics
        start_time = time.time()
        
        # Record metric
        http_requests_total.labels(
            method="GET", 
            endpoint="/dashboard", 
            status=200
        ).inc()
        
        # Create cache key for demo mode
        cache_key = f"dashboard_demo_{period}"
        
        # Try to get data from cache unless refresh is requested
        dashboard_data = None if refresh else get_cached_data(cache_key)
        
        if dashboard_data is None:
            # Use demo data instead of API calls
            portfolio_data = {
                "total_value": 125350.75,
                "daily_change": 2845.50,
                "daily_change_percent": 2.34,
                "holdings": [
                    {"symbol": "AAPL", "name": "Apple Inc.", "shares": 50, "value": 8925.00, "change_percent": 1.2},
                    {"symbol": "MSFT", "name": "Microsoft Corp.", "shares": 30, "value": 10807.50, "change_percent": 0.8},
                    {"symbol": "GOOGL", "name": "Alphabet Inc.", "shares": 25, "value": 6725.25, "change_percent": -0.5}
                ]
            }
            
            # Demo market overview
            market_data = {
                "indices": [
                    {"name": "S&P 500", "value": 4752.75, "change_percent": 0.8},
                    {"name": "NASDAQ", "value": 16234.50, "change_percent": 1.2}
                ],
                "status": "available"
            }
            
            # Demo recent transactions
            transactions = [
                {"date": "2025-06-20", "type": "BUY", "symbol": "AAPL", "shares": 10, "price": 178.50},
                {"date": "2025-06-19", "type": "SELL", "symbol": "TSLA", "shares": 5, "price": 215.40},
                {"date": "2025-06-18", "type": "BUY", "symbol": "MSFT", "shares": 15, "price": 360.25}
            ]
            
            # Combine all data
            dashboard_data = {
                "portfolio": portfolio_data,
                "market": market_data,
                "transactions": transactions
            }
            
            # Cache the dashboard data
            set_cached_data(cache_key, dashboard_data)
        else:
            logger.info(f"Using cached dashboard data for demo mode")
            portfolio_data = dashboard_data["portfolio"]
            market_data = dashboard_data["market"]
            transactions = dashboard_data["transactions"]
        
        # Combine data for template
        context = {
            "request": request,
            "user": None,
            "demo_mode": True,
            "page_title": "Dashboard",
            "portfolio": portfolio_data,
            "market": market_data,
            "transactions": transactions,
            "selected_period": period,
            "periods": [
                {"value": "day", "label": "Today"},
                {"value": "week", "label": "This Week"},
                {"value": "month", "label": "This Month"},
                {"value": "year", "label": "This Year"},
                {"value": "all", "label": "All Time"}
            ],
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "is_cached": not refresh and dashboard_data is not None
        }
        
        # Record timing for metrics
        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method="GET", 
            endpoint="/dashboard"
        ).observe(duration)
        
        return get_templates(request).TemplateResponse("dashboard/index.html", context)
    
    except httpx.RequestError as e:

        logger.error(f"Request error: {str(e)}")
        return get_templates(request).TemplateResponse(
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
        return get_templates(request).TemplateResponse(
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
    API endpoint to get dashboard data for the frontend (demo mode).
    Used for AJAX requests to update the dashboard dynamically.
    
    Args:
        request: FastAPI request object
        period: Time period for analysis
        refresh: Whether to force refresh data from API
        
    Returns:
        Dict[str, Any]: Dashboard data in JSON format
    """
    try:
        # Start timing for metrics
        start_time = time.time()
        
        # Record metric
        http_requests_total.labels(
            method="GET", 
            endpoint="/api/dashboard/data", 
            status=200
        ).inc()
        
        # Create cache key for demo mode
        cache_key = f"dashboard_api_demo_{period}"
        
        # Try to get data from cache unless refresh is requested
        data = None if refresh else get_cached_data(cache_key)
        
        if data is None:
            # In a real implementation, this would fetch data from a service or database
            # For this example, we'll generate some sample data
            
            # Current portfolio value
            portfolio_value = 125350.75
            daily_change_percent = 2.34
            
            # Sample performance data
            performance_data = [
                {"date": "2025-05-21", "value": 122000.50},
                {"date": "2025-05-28", "value": 123100.25},
                {"date": "2025-06-04", "value": 121500.75},
                {"date": "2025-06-11", "value": 124200.00},
                {"date": "2025-06-18", "value": 125350.75}
            ]
            
            # Sample asset allocation
            asset_allocation = [
                {"name": "Stocks", "value": 70, "color": "#4f81bd"},
                {"name": "Bonds", "value": 20, "color": "#c0504d"},
                {"name": "Cash", "value": 5, "color": "#9bbb59"},
                {"name": "Crypto", "value": 5, "color": "#8064a2"}
            ]
            
            # Risk assessment
            risk_score = 68
            risk_level = "Moderate-High"
            
            # Compile all data
            data = {
                "portfolio_value": portfolio_value,
                "daily_change_percent": daily_change_percent,
                "performance_data": performance_data,
                "asset_allocation": asset_allocation,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "timestamp": datetime.utcnow().isoformat(),
                "is_cached": False
            }
            
            # Cache the data
            set_cached_data(cache_key, data)
        else:
            # Update cached flag
            data["is_cached"] = True
        
        # Record timing for metrics
        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method="GET", 
            endpoint="/api/dashboard/data"
        ).observe(duration)
        
        return data
    
    except Exception as e:

        logger.exception(f"Dashboard data error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving dashboard data"
        )

@router.get("/api/dashboard/insights", response_model=Dict[str, Any])
async def dashboard_insights():
async def dashboard_insights(
    
):
    """
    API endpoint to get AI-generated insights for the dashboard (demo mode).
    
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
