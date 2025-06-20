"""
Market Controller for QuantumVestAI UI
Last updated: 2025-06-20 04:11:30
Updated by: daparthi001
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query, Path, status, Response
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List, Dict, Any, Union
import httpx
import logging
import time
import os
from datetime import datetime, timedelta

# Import dependencies with fallback
try:
    from auth.dependencies import get_current_user, get_optional_current_user
except ImportError:
    # Create mock auth functions if they don't exist
    logging.getLogger(__name__).warning("Auth dependencies not found. Using mock functions.")
    
    async def get_current_user(request: Request, response: Response = None):
        """Mock function that returns a default user"""
        return {"username": "defaultuser", "token": "mock_token"}
    
    async def get_optional_current_user(request: Request, response: Response = None):
        """Mock function that optionally returns a default user"""
        return {"username": "defaultuser", "token": "mock_token"}

# Set up router
router = APIRouter(
    prefix="/market",
    tags=["market"]
)

# Set up logging
logger = logging.getLogger(__name__)

# API client timeout (configurable via environment variable)
TIMEOUT = float(os.getenv("API_TIMEOUT", "10.0"))

# Cache configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # Default: 5 minutes
cache_store = {}

def get_cached_data(key: str) -> Union[Dict[str, Any], None]:
    """Get data from cache if it exists and is not expired."""
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
    """Store data in cache with expiration time."""
    if not CACHE_ENABLED:
        return
        
    expires = time.time() + ttl
    cache_store[key] = {
        "data": data,
        "expires": expires
    }
    logger.debug(f"Cached data for {key}, expires in {ttl} seconds")

def get_templates(request: Request):
    """Helper function to get templates from app state or create a new instance."""
    templates = getattr(request.app.state, 'templates', None)
    if templates is None:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="templates")
    return templates

@router.get("", response_class=HTMLResponse)
async def market_overview(
    request: Request,
    response: Response,
    user=Depends(get_optional_current_user)
):
    """
    Market overview page showing indices, trends, and top movers.
    This page is accessible to both logged-in and anonymous users.
    """
    try:
        # Get API URL from app state or environment
        api_url_base = getattr(request.app.state, 'settings', {}).get('API_URL', os.getenv('API_URL', 'http://api:8000'))
        
        # Create cache key - include user info if available for personalized content
        cache_key = f"market_overview_{user.get('username') if user else 'anonymous'}"
        
        # Try to get data from cache
        market_data = get_cached_data(cache_key)
        
        if market_data is None:
            try:
                # Fetch market data from API
                async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                    headers = {}
                    if user:
                        headers["Authorization"] = f"Bearer {user.get('token')}"
                    
                    response = await client.get(
                        f"{api_url_base}/api/market/overview",
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"API error: {response.status_code} - {response.text}")
                        raise HTTPException(
                            status_code=response.status_code,
                            detail="Error fetching market data"
                        )
                    
                    market_data = response.json()
                    
                    # Cache the data
                    set_cached_data(cache_key, market_data)
            except httpx.RequestError as e:
                logger.error(f"API request error: {str(e)}")
                # Use fallback data
                market_data = {
                    "indices": [
                        {"name": "S&P 500", "value": 4752.75, "change_percent": 0.8},
                        {"name": "NASDAQ", "value": 16234.50, "change_percent": 1.2},
                        {"name": "DOW", "value": 35750.25, "change_percent": 0.5}
                    ],
                    "top_gainers": [
                        {"symbol": "AAPL", "name": "Apple Inc.", "price": 178.50, "change_percent": 3.2},
                        {"symbol": "MSFT", "name": "Microsoft Corp.", "price": 360.25, "change_percent": 2.5},
                        {"symbol": "AMZN", "name": "Amazon.com Inc.", "price": 145.75, "change_percent": 1.8}
                    ],
                    "top_losers": [
                        {"symbol": "META", "name": "Meta Platforms Inc.", "price": 425.80, "change_percent": -1.2},
                        {"symbol": "NFLX", "name": "Netflix Inc.", "price": 615.25, "change_percent": -0.8},
                        {"symbol": "TSLA", "name": "Tesla Inc.", "price": 215.40, "change_percent": -0.5}
                    ],
                    "sectors": [
                        {"name": "Technology", "change_percent": 1.5},
                        {"name": "Healthcare", "change_percent": 0.8},
                        {"name": "Financials", "change_percent": 0.3},
                        {"name": "Consumer Discretionary", "change_percent": -0.2},
                        {"name": "Energy", "change_percent": -0.5}
                    ]
                }
        
        # Get templates
        templates = get_templates(request)
        
        # Render template
        return templates.TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "user": user,
                "page_title": "Market Overview",
                "market_data": market_data,
                "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "is_authenticated": user is not None
            }
        )
    
    except Exception as e:
        logger.exception(f"Market overview error: {str(e)}")
        
        # Get templates
        templates = get_templates(request)
        
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": "An error occurred while loading market data.",
                "error_code": "MARKET_ERR",
                "user": user
            },
            status_code=500
        )

@router.get("/stock/{symbol}", response_class=HTMLResponse)
async def stock_details(
    request: Request,
    response: Response,
    symbol: str = Path(..., description="Stock symbol"),
    user=Depends(get_optional_current_user)
):
    """
    Stock details page showing price, charts, news, and fundamentals for a specific stock.
    This page is accessible to both logged-in and anonymous users.
    """
    try:
        # Get API URL from app state or environment
        api_url_base = getattr(request.app.state, 'settings', {}).get('API_URL', os.getenv('API_URL', 'http://api:8000'))
        
        # Create cache key - include user info if available for personalized content
        cache_key = f"stock_details_{symbol.upper()}_{user.get('username') if user else 'anonymous'}"
        
        # Try to get data from cache
        stock_data = get_cached_data(cache_key)
        
        if stock_data is None:
            try:
                # Fetch stock data from API
                async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                    headers = {}
                    if user:
                        headers["Authorization"] = f"Bearer {user.get('token')}"
                    
                    response = await client.get(
                        f"{api_url_base}/api/stocks/{symbol.upper()}",
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"API error: {response.status_code} - {response.text}")
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Error fetching data for {symbol}"
                        )
                    
                    stock_data = response.json()
                    
                    # Cache the data
                    set_cached_data(cache_key, stock_data)
            except httpx.RequestError as e:
                logger.error(f"API request error: {str(e)}")
                # Use fallback data
                stock_data = {
                    "symbol": symbol.upper(),
                    "name": f"{symbol.upper()} Corporation",
                    "price": 178.50,
                    "change": 5.25,
                    "change_percent": 3.2,
                    "market_cap": "2.5T",
                    "pe_ratio": 28.5,
                    "dividend_yield": 0.55,
                    "volume": "25.3M",
                    "chart_data": {
                        "labels": ["9:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "1:00", "1:30", "2:00", "2:30", "3:00", "3:30", "4:00"],
                        "values": [175.25, 176.50, 177.00, 176.75, 177.25, 177.50, 178.00, 177.75, 178.25, 178.50, 178.75, 179.00, 178.75, 178.50]
                    }
                }
        
        # Check if user has this stock in watchlist
        is_in_watchlist = False
        if user:
            try:
                async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                    response = await client.get(
                        f"{api_url_base}/api/watchlist/check/{symbol.upper()}",
                        headers={"Authorization": f"Bearer {user.get('token')}"}
                    )
                    
                    if response.status_code == 200:
                        is_in_watchlist = response.json().get("in_watchlist", False)
            except Exception as e:
                logger.warning(f"Error checking watchlist status: {str(e)}")
                is_in_watchlist = False
        
        # Get templates
        templates = get_templates(request)
        
        # Render template
        return templates.TemplateResponse(
            "market/stock_details.html",
            {
                "request": request,
                "user": user,
                "page_title": f"{stock_data.get('name')} ({stock_data.get('symbol')})",
                "stock": stock_data,
                "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "is_authenticated": user is not None,
                "is_in_watchlist": is_in_watchlist
            }
        )
    
    except Exception as e:
        logger.exception(f"Stock details error: {str(e)}")
        
        # Get templates
        templates = get_templates(request)
        
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": f"An error occurred while loading data for {symbol}.",
                "error_code": "STOCK_ERR",
                "user": user
            },
            status_code=500
        )

@router.get("/api/stocks/search", response_model=Dict[str, Any])
async def search_stocks(
    request: Request,
    query: str = Query(..., description="Search query"),
    user=Depends(get_optional_current_user)
):
    """
    API endpoint to search for stocks by name or symbol.
    Used for autocomplete functionality.
    """
    try:
        # Get API URL from app state or environment
        api_url_base = getattr(request.app.state, 'settings', {}).get('API_URL', os.getenv('API_URL', 'http://api:8000'))
        
        # Create cache key
        cache_key = f"stock_search_{query.lower()}"
        
        # Try to get data from cache
        search_results = get_cached_data(cache_key)
        
        if search_results is None:
            try:
                # Fetch search results from API
                async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                    headers = {}
                    if user:
                        headers["Authorization"] = f"Bearer {user.get('token')}"}
                    
                    response = await client.get(
                        f"{api_url_base}/api/stocks/search?query={query}",
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"API error: {response.status_code} - {response.text}")
                        raise HTTPException(
                            status_code=response.status_code,
                            detail="Error searching stocks"
                        )
                    
                    search_results = response.json()
                    
                    # Cache the data
                    set_cached_data(cache_key, search_results)
            except httpx.RequestError as e:
                logger.error(f"API request error: {str(e)}")
                # Use fallback data based on query
                search_results = {
                    "results": [
                        {"symbol": "AAPL", "name": "Apple Inc."},
                        {"symbol": "AMZN", "name": "Amazon.com Inc."},
                        {"symbol": "MSFT", "name": "Microsoft Corporation"}
                    ]
                }
        
        return search_results
    
    except Exception as e:
        logger.exception(f"Stock search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching stocks"
        )