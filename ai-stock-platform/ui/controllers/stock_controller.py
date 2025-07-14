"""
Stock Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import logging
import os
from pathlib import Path

import aiohttp
from fastapi import APIRouter, Form, HTTPException, Query, Request
from config.constants import MODEL_ENSEMBLE

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)
logger = logging.getLogger("quantumvestai.stock_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/stock/search", response_class=HTMLResponse)
async def stock_search(
    request: Request,
    q: str = Query(None),
    sector: str = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    """Search for stocks with enhanced filtering"""
    try:
        search_results = []
        error_message = None
        
        if q:
            # Get authentication token if available
            auth_token = request.cookies.get("access_token")
            headers = {}
            if auth_token:
                headers["Authorization"] = auth_token
            
            # Build query parameters
            params = {
                "query": q,
                "limit": limit
            }
            
            # Note: sector parameter is included but API may not support it yet
            # This is prepared for future API enhancement
            if sector:
                params["sector"] = sector
            
            # Try to connect to the real API first
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{API_V1_URL}/stocks/search",
                        params=params,
                        headers=headers,
                        timeout=5  # Reduced timeout for quick fallback
                    ) as response:
                        if response.status == 200:
                            search_results = await response.json()
                            logger.info(f"Stock search successful: {len(search_results)} results for query '{q}'")
                        elif response.status == 401:
                            error_message = "Authentication required. Please log in to search for stocks."
                            logger.warning(f"Authentication required for stock search: {q}")
                        elif response.status == 404:
                            error_message = "Stock search service is currently unavailable."
                            logger.error(f"Stock search API not found: {response.status}")
                        else:
                            error_message = f"Search failed with status {response.status}. Please try again."
                            logger.error(f"Stock search API error: Status {response.status}")
                            
            except Exception as e:
                # API not available, fall back to demo mode
                logger.info(f"API not available, using demo mode for search: {q}")
                search_results = _get_demo_search_results(q, sector, limit)
        
        # Process results to ensure proper data structure
        if search_results and isinstance(search_results, list):
            for result in search_results:
                # Ensure required fields exist with defaults
                if not isinstance(result, dict):
                    continue
                result.setdefault('symbol', 'N/A')
                result.setdefault('name', 'N/A')
                result.setdefault('sector', None)
                result.setdefault('price', None)
                result.setdefault('change', None)
                result.setdefault('change_percent', None)
        
        return get_templates(request).TemplateResponse(
            "stocks/search.html",
            {
                "request": request,
                "query": q,
                "sector": sector,
                "limit": limit,
                "results": search_results,
                "error": error_message,
                "user": None,
                "demo_mode": True
            }
        )
    except Exception as e:
        logger.error(f"Stock search error: {str(e)}")
        return get_templates(request).TemplateResponse(
            "stocks/search.html",
            {
                "request": request,
                "query": q,
                "sector": sector,
                "limit": limit,
                "error": f"An unexpected error occurred: {str(e)}",
                "results": [],
                "user": None,
                "demo_mode": True
            }
        )

def _get_demo_search_results(query: str, sector: str = None, limit: int = 10):
    """Generate demo search results when API is not available"""
    # Demo stock data
    demo_stocks = [
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "price": 175.43, "change": 2.15, "change_percent": 1.24},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "price": 338.11, "change": -1.23, "change_percent": -0.36},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "price": 129.40, "change": 0.85, "change_percent": 0.66},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer", "price": 131.93, "change": -0.47, "change_percent": -0.36},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer", "price": 248.50, "change": 5.23, "change_percent": 2.15},
        {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology", "price": 308.56, "change": 1.34, "change_percent": 0.44},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "price": 875.28, "change": 12.45, "change_percent": 1.44},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial", "price": 161.52, "change": -0.78, "change_percent": -0.48},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "price": 155.99, "change": 0.23, "change_percent": 0.15},
        {"symbol": "V", "name": "Visa Inc.", "sector": "Financial", "price": 237.08, "change": 1.87, "change_percent": 0.79},
        {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare", "price": 493.22, "change": -2.15, "change_percent": -0.43},
        {"symbol": "HD", "name": "The Home Depot Inc.", "sector": "Consumer", "price": 327.44, "change": 0.92, "change_percent": 0.28},
        {"symbol": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer", "price": 143.18, "change": -0.34, "change_percent": -0.24},
        {"symbol": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "price": 108.87, "change": 1.42, "change_percent": 1.32},
        {"symbol": "CVX", "name": "Chevron Corporation", "sector": "Energy", "price": 162.34, "change": 0.67, "change_percent": 0.41},
    ]
    
    # Filter by query (symbol or name)
    query_lower = query.lower()
    filtered_stocks = []
    
    for stock in demo_stocks:
        if (query_lower in stock["symbol"].lower() or 
            query_lower in stock["name"].lower()):
            filtered_stocks.append(stock)
    
    # Filter by sector if specified
    if sector:
        filtered_stocks = [s for s in filtered_stocks if s["sector"] == sector]
    
    # Limit results
    return filtered_stocks[:limit]

@router.get("/stock/{ticker}", response_class=HTMLResponse)
async def stock_detail(
    request: Request,
    ticker: str,
    timeframe: str = Query("1d", regex="^(1d|1w|1m|3m|6m|1y|5y)$"),
    forecast_days: int = Query(7, ge=1, le=30),
    model: str = Query(MODEL_ENSEMBLE)
):
    """Display stock detail page (demo mode)"""
    try:
        stock_data = {
            "ticker": ticker.upper(),
            "timeframe": timeframe,
            "forecast_days": forecast_days,
            "model": model
        }
        
        # Demo mode - no authentication headers
        
        async with aiohttp.ClientSession() as session:
            # Get stock details
            async with session.get(f"{API_V1_URL}/stocks/{ticker}", timeout=5) as response:
                if response.status == 200:
                    stock_data["details"] = await response.json()
                elif response.status == 404:
                    raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")
                else:
                    logger.error(f"Error fetching stock details: Status {response.status}")
                    stock_data["details"] = {"status": "error", "error": f"API returned status {response.status}"}
            
            # Get stock price
            async with session.get(
                f"{API_V1_URL}/stocks/{ticker}/price?interval={timeframe}", 
                timeout=5
            ) as response:
                if response.status == 200:
                    stock_data["price"] = await response.json()
                else:
                    stock_data["price"] = {"status": "unavailable"}
            
            # Get stock forecast
            async with session.get(
                f"{API_V1_URL}/forecast/{ticker}?days={forecast_days}&model={model}",
                timeout=5
            ) as response:
                if response.status == 200:
                    stock_data["forecast"] = await response.json()
                else:
                    stock_data["forecast"] = {"status": "unavailable"}
            
            # Demo mode - skip premium features like sentiment and watchlist
            stock_data["sentiment"] = {"status": "unavailable", "reason": "demo_mode"}
            stock_data["in_watchlist"] = False
        
        return get_templates(request).TemplateResponse(
            "stocks/detail.html",
            {
                "request": request,
                "stock": stock_data,
                "user": None,
                "demo_mode": True,
                "available_models": AVAILABLE_MODELS
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Stock detail error for {ticker}: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {"request": request, "error": str(e), "user": None, "demo_mode": True},
            status_code=500
        )

@router.post("/stock/{ticker}/add-to-watchlist")
async def add_to_watchlist(
    request: Request,
    ticker: str
):
    """Add stock to watchlist (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+features+require+authentication+(demo+mode)", status_code=302)
