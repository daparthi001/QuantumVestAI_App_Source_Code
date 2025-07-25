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
from ui.config.constants import AVAILABLE_MODELS, MODEL_ENSEMBLE

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
                # API not available, fall back to Yahoo Finance search
                logger.info(
                    f"API not available, fetching live data from Yahoo Finance: {q}"
                )
                search_results = await _get_live_search_results(q, limit)
        
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

async def _get_live_search_results(query: str, limit: int = 10) -> list:
    """Fetch search results from Yahoo Finance."""
    url = "https://query1.finance.yahoo.com/v1/finance/search"
    params = {"q": query, "quotesCount": limit}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = []
                    for quote in data.get("quotes", [])[:limit]:
                        results.append({
                            "symbol": quote.get("symbol"),
                            "name": quote.get("shortname") or quote.get("longname"),
                            "sector": quote.get("sector"),
                            "price": quote.get("regularMarketPrice"),
                            "change": quote.get("regularMarketChange"),
                            "change_percent": quote.get("regularMarketChangePercent"),
                        })
                    return results
    except Exception as exc:
        logger.error(f"Yahoo Finance search failed: {exc}")
    return []

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


@router.get("/stocks/flow", response_class=HTMLResponse)
async def stock_flow_page(request: Request):
    """Display interactive stock flow visualization page."""
    try:
        return get_templates(request).TemplateResponse(
            "stocks/flow.html",
            {
                "request": request,
                "user": None,
                "demo_mode": True,
            },
        )
    except Exception as e:  # pragma: no cover - template errors
        logger.error(f"Error loading stock flow page: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {"request": request, "error": "Unable to load stock flow page"},
            status_code=500,
        )

@router.post("/stock/{ticker}/add-to-watchlist")
async def add_to_watchlist(
    request: Request,
    ticker: str
):
    """Add stock to watchlist (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+features+require+authentication+(demo+mode)", status_code=302)
