"""
Market Controller for QuantumVestAI UI
Last updated: 2025-06-20 04:32:00
Updated by: daparthi001
"""

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import httpx
from core.http_client import safe_get_json
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import HTMLResponse, JSONResponse

API_URL = "http://quantumvestai-dev-api.dev.svc.cluster.local:8000"
# Import dependencies with fallback
try:
    from auth.dependencies import get_current_user, get_optional_current_user
except ImportError:
    # Create mock auth functions if they don't exist
    logging.getLogger(__name__).warning(
        "Auth dependencies not found. Using mock functions."
    )

    async def get_current_user(request: Request, response: Response = None):
        """Mock function that returns None."""
        return None

    async def get_optional_current_user(request: Request, response: Response = None):
        """Mock function that returns None."""
        return None


# Set up router
router = APIRouter(prefix="/market", tags=["market"])

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
    cache_store[key] = {"data": data, "expires": expires}
    logger.debug(f"Cached data for {key}, expires in {ttl} seconds")


def get_templates(request: Request):
    """Helper function to get templates from app state or create a new instance."""
    templates = getattr(request.app.state, "templates", None)
    if templates is None:
        from fastapi.templating import Jinja2Templates

        templates = Jinja2Templates(directory="templates")
    return templates


@router.get("", response_class=HTMLResponse)
async def market_overview(request: Request, response: Response):
    """Market overview page showing indices, trends, and top movers."""
    try:
        # Get API URL from app state or environment
        api_url_base = getattr(request.app.state, "settings", {}).get(
            "API_URL", os.getenv("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
        )

        cache_key = "market_overview"

        # Try to get data from cache
        market_data = get_cached_data(cache_key)

        if market_data is None:
            try:
                # Get current user for authentication
                user = await get_optional_current_user(request, response)
                auth_token = user.get("token") if user else None

                # Fetch market data from API using centralized HTTP client
                market_data = await safe_get_json(
                    url=f"{api_url_base}/api/market/overview", auth_token=auth_token
                )

                if market_data is None:
                    logger.error("Failed to fetch market data from API")
                    raise HTTPException(
                        status_code=503, detail="Error fetching market data"
                    )

                # Cache the data
                set_cached_data(cache_key, market_data)
            except Exception as e:
                logger.error(f"Market data fetch error: {str(e)}")
                logger.error(f"API request error: {str(e)}")
                raise HTTPException(
                    status_code=503, detail="Unable to fetch market data"
                )

        # Get templates
        templates = get_templates(request)

        # Render template
        return get_templates(request).TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "user": None,
                "page_title": "Market Overview",
                "market_data": market_data,
                "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "is_authenticated": False,
            },
        )

    except Exception as e:
        logger.exception(f"Market overview error: {str(e)}")

        # Get templates
        templates = get_templates(request)

        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": "An error occurred while loading market data.",
                "error_code": "MARKET_ERR",
                "user": None,
            },
            status_code=500,
        )


@router.get("/stock/{symbol}", response_class=HTMLResponse)
async def stock_details(
    request: Request,
    response: Response,
    symbol: str = Path(..., description="Stock symbol"),
):
    """Stock details page showing price, charts, news, and fundamentals for a specific stock."""
    try:
        # Get API URL from app state or environment
        api_url_base = getattr(request.app.state, "settings", {}).get(
            "API_URL", os.getenv("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
        )

        # Create cache key
        cache_key = f"stock_details_{symbol.upper()}"

        # Try to get data from cache
        stock_data = get_cached_data(cache_key)

        if stock_data is None:
            try:
                # Get current user for authentication
                user = await get_optional_current_user(request, response)
                auth_token = user.get("token") if user else None

                # Fetch stock data from API using centralized HTTP client
                stock_data = await safe_get_json(
                    url=f"{api_url_base}/api/stocks/{symbol.upper()}",
                    auth_token=auth_token,
                )

                if stock_data is None:
                    logger.error(f"Failed to fetch stock data for {symbol}")
                    raise HTTPException(
                        status_code=503, detail=f"Error fetching data for {symbol}"
                    )

                # Cache the data
                set_cached_data(cache_key, stock_data)
            except Exception as e:
                logger.error(f"Stock data fetch error: {str(e)}")
                logger.error(f"API request error: {str(e)}")
                raise HTTPException(
                    status_code=503, detail="Unable to fetch stock data"
                )

        # Get current user for checking watchlist
        user = await get_optional_current_user(request, response)

        # Check if user has this stock in watchlist
        is_in_watchlist = False
        if user:
            try:
                watchlist_data = await safe_get_json(
                    url=f"{api_url_base}/api/watchlist/check/{symbol.upper()}",
                    auth_token=user.get("token"),
                )

                if watchlist_data:
                    is_in_watchlist = watchlist_data.get("in_watchlist", False)
            except Exception as e:
                logger.warning(f"Error checking watchlist status: {str(e)}")
                is_in_watchlist = False

        # Get templates
        templates = get_templates(request)

        # Render template
        return get_templates(request).TemplateResponse(
            "market/stock_details.html",
            {
                "request": request,
                "user": None,
                "page_title": f"{stock_data.get('name')} ({stock_data.get('symbol')})",
                "stock": stock_data,
                "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "is_authenticated": False,
                "is_in_watchlist": False,
            },
        )

    except Exception as e:
        logger.exception(f"Stock details error: {str(e)}")

        # Get templates
        templates = get_templates(request)

        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": f"An error occurred while loading data for {symbol}.",
                "error_code": "STOCK_ERR",
                "user": None,
            },
            status_code=500,
        )


@router.get("/api/stocks/search", response_model=Dict[str, Any])
async def search_stocks(
    request: Request, query: str = Query(..., description="Search query")
):
    """API endpoint to search for stocks by name or symbol."""
    try:
        # Get API URL from app state or environment
        api_url_base = getattr(request.app.state, "settings", {}).get(
            "API_URL", os.getenv("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
        )

        cache_key = f"stock_search_{query.lower()}"

        # Try to get data from cache
        search_results = get_cached_data(cache_key)

        if search_results is None:
            try:
                # Get current user for authentication
                user = await get_optional_current_user(request)
                auth_token = user.get("token") if user else None

                # Fetch search results from API using centralized HTTP client
                search_results = await safe_get_json(
                    url=f"{api_url_base}/api/stocks/search",
                    params={"query": query},
                    auth_token=auth_token,
                )

                if search_results is None:
                    logger.error("Failed to fetch search results from API")
                    raise HTTPException(
                        status_code=503, detail="Error searching stocks"
                    )

                # Cache the data
                set_cached_data(cache_key, search_results)
            except Exception as e:
                logger.error(f"Stock search error: {str(e)}")
                logger.error(f"API request error: {str(e)}")
                raise HTTPException(status_code=503, detail="Unable to search stocks")

        return search_results

    except Exception as e:
        logger.exception(f"Stock search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching stocks",
        )
