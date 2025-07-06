"""
Dashboard Controller for QuantumVestAI UI
Last updated: 2025-06-20 05:25:00
Author: daparthi001
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any, Union
import httpx
import logging
import time
import json
import os
from datetime import datetime, timedelta

API_URL = "http://quantumvestai-dev-api:8000/api/v1"
# Auth dependencies removed as per requirements

# Define mock metrics classes that do nothing
class NoOpMetric:
    """A no-operation metric that implements the basic prometheus interface"""
    
    def __init__(self, name=None, documentation=None, labelnames=None):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames or []
    
    def labels(self, **kwargs):
        return self
    
    def inc(self, amount=1):
        pass
    
    def observe(self, amount):
        pass
    
    def set(self, value):
        pass

# Create mock metrics
http_requests_total = NoOpMetric(
    name="http_requests_total",
    documentation="Total number of HTTP requests",
    labelnames=["method", "endpoint", "status"]
)

http_request_duration_seconds = NoOpMetric(
    name="http_request_duration_seconds",
    documentation="HTTP request duration in seconds",
    labelnames=["method", "endpoint"]
)

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
    response: Response,
    period: Optional[str] = Query("month", description="Time period for data analysis"),
    refresh: Optional[bool] = Query(False, description="Force refresh data from API")
):
    """
    Dashboard main view showing portfolio performance and analytics.
    
    Args:
        request: FastAPI request object
        period: Time period for analysis (day, week, month, year, all)
        refresh: Whether to force refresh data from API
        
    Returns:
        HTMLResponse: Rendered dashboard template
    """
    # Check if user is authenticated
    if user is None:
        # Redirect to login page with return URL
        return RedirectResponse(
            url=f"/login?next=/dashboard?period={period}",
            status_code=302
        )
    
    try:
        # Start timing for metrics
        start_time = time.time()
        
        # Record metric
        http_requests_total.labels(
            method="GET", 
            endpoint="/dashboard", 
            status=200
        ).inc()
        
        # Create cache key based on user and period
        # Use safe username access with default value
        username = user.get('username', 'anonymous')
        cache_key = f"dashboard_{username}_{period}"
        
        # Try to get data from cache unless refresh is requested
        dashboard_data = None if refresh else get_cached_data(cache_key)
        
        if dashboard_data is None:
            # Check if app.state has settings attribute
            api_url_base = getattr(request.app.state, 'settings', {}).get('API_URL', os.getenv('API_URL', 'http://api:8000'))
            
            try:
                # Get portfolio data from API using centralized HTTP client
                from core.http_client import safe_get_json
                
                auth_token = user.get('token')
                portfolio_data = await safe_get_json(
                    url=f"{api_url_base}/api/portfolio/summary",
                    params={"period": period},
                    auth_token=auth_token
                )
                
                if portfolio_data is None:
                    logger.error("Failed to fetch portfolio data from API")
                    raise HTTPException(
                        status_code=503,
                        detail="Error fetching portfolio data"
                    )
                
                # Get market overview
                market_data = await safe_get_json(
                    url=f"{api_url_base}/api/market/overview",
                    auth_token=auth_token
                )
                
                if market_data is None:
                    logger.warning("Market data unavailable")
                    market_data = {"status": "unavailable"}
                
                # Get recent transactions
                transactions_data = await safe_get_json(
                    url=f"{api_url_base}/api/transactions/recent",
                    params={"limit": 5},
                    auth_token=auth_token
                )
                
                if transactions_data is None:
                    logger.warning("Transactions data unavailable")
                    transactions = []
                else:
                    transactions = transactions_data.get("transactions", [])
                
            except Exception as e:
                logger.error(f"API request error: {str(e)}")
                # Use fallback data
                portfolio_data = {
                    "value": 125350.75,
                    "daily_change": 2850.25,
                    "daily_change_percent": 2.34,
                    "total_return": 25350.75,
                    "total_return_percent": 25.35,
                    "holdings": [
                        {"symbol": "AAPL", "name": "Apple Inc.", "value": 45350.25, "change_percent": 1.5},
                        {"symbol": "MSFT", "name": "Microsoft Corp.", "value": 38250.50, "change_percent": 0.8},
                        {"symbol": "GOOG", "name": "Alphabet Inc.", "value": 41750.00, "change_percent": -0.3}
                    ]
                }
                
                market_data = {
                    "status": "fallback",
                    "indices": [
                        {"name": "S&P 500", "value": 4752.75, "change_percent": 0.8},
                        {"name": "NASDAQ", "value": 16234.50, "change_percent": 1.2},
                        {"name": "DOW", "value": 35750.25, "change_percent": 0.5}
                    ]
                }
                
                transactions = [
                    {"date": "2025-06-20", "type": "BUY", "symbol": "AAPL", "shares": 10, "price": 178.50, "total": 1785.00},
                    {"date": "2025-06-19", "type": "SELL", "symbol": "MSFT", "shares": 5, "price": 360.25, "total": 1801.25}
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
            logger.info(f"Using cached dashboard data for user {username}")
            portfolio_data = dashboard_data["portfolio"]
            market_data = dashboard_data["market"]
            transactions = dashboard_data["transactions"]
        
        # Combine data for template
        context = {
            "request": request,
            "user": None,
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
            "is_cached": not refresh and dashboard_data is not None,
            # Ensure template filters are available directly in context
            "get_asset_url": lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}&t={datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }
        
        # Record timing for metrics
        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method="GET", 
            endpoint="/dashboard"
        ).observe(duration)
        
        # Get correct templates object - check if app.state.templates exists
        templates_obj = getattr(request.app.state, 'templates', templates)
        
        # Ensure template filters are registered
            logger.warning("Could not import template_filters in dashboard")
        
        return templates_obj.TemplateResponse("dashboard/index.html", context)
    
    except httpx.RequestError as e:
        logger.error(f"Request error: {str(e)}")
        
        # Get correct templates object
        templates_obj = getattr(request.app.state, 'templates', templates)
        
        # Add get_asset_url to context directly
        def get_asset_url(path, version=None):
            if not version:
                version = os.environ.get('APP_VERSION', 'v1.5.2')
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            return f"/static/{path}?v={version}&t={timestamp}"
        
        return templates_obj.TemplateResponse(
            "error.html", 
            {
                "request": request,
                "user": None,
                "message": "Service temporarily unavailable. Please try again later.",
                "error_code": "API_CONN_ERR",
                "get_asset_url": get_asset_url  # Add function directly to context
            },
            status_code=503  # Changed from default to indicate service unavailable
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        
        # Get correct templates object
        templates_obj = getattr(request.app.state, 'templates', templates)
        
        # Add get_asset_url to context directly
        def get_asset_url(path, version=None):
            if not version:
                version = os.environ.get('APP_VERSION', 'v1.5.2')
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            return f"/static/{path}?v={version}&t={timestamp}"
        
        return templates_obj.TemplateResponse(
            "error.html", 
            {
                "request": request,
                "user": None,
                "message": "An unexpected error occurred while loading the dashboard.",
                "error_code": "DASHBOARD_ERR",
                "get_asset_url": get_asset_url  # Add function directly to context
            }
        )

@router.get("/api/dashboard/data", response_model=Dict[str, Any])
async def dashboard_data(
    request: Request,
    period: Optional[str] = Query("month"),
    refresh: Optional[bool] = Query(False)
):
    """
    API endpoint to get dashboard data for the frontend.
    Used for AJAX requests to update the dashboard dynamically.
    
    Args:
        request: FastAPI request object
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
async def dashboard_insights():
    """
    API endpoint to get AI-generated insights for the dashboard.
    
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
    request: Request
):
    """
    Admin dashboard view showing system metrics and user statistics.
    
    Args:
        request: FastAPI request object
        
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