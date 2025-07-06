"""
Stock Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Query, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.stock_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000/api/v1")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/stock/{ticker}", response_class=HTMLResponse)
async def stock_detail(
    request: Request,
    ticker: str,
    timeframe: str = Query("1d", regex="^(1d|1w|1m|3m|6m|1y|5y)$"),
    forecast_days: int = Query(7, ge=1, le=30)
):
    """Display stock detail page (demo mode)"""
    try:
        stock_data = {
            "ticker": ticker.upper(),
            "timeframe": timeframe,
            "forecast_days": forecast_days
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
                f"{API_V1_URL}/forecast/{ticker}?days={forecast_days}",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    stock_data["forecast"] = await response.json()
                else:
                    stock_data["forecast"] = {"status": "unavailable"}
            
            # Get stock sentiment
            if user.get("role") in ["premium", "admin"]:
                async with session.get(
                    f"{API_V1_URL}/sentiment/stock/{ticker}",
                    headers=headers,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        stock_data["sentiment"] = await response.json()
                    else:
                        stock_data["sentiment"] = {"status": "unavailable"}
            
            # Check if stock is in user's watchlist
            async with session.get(
                f"{API_V1_URL}/watchlist/{user['username']}/contains?ticker={ticker}",
                headers=headers,
                timeout=5
            ) as response:
                stock_data["in_watchlist"] = response.status == 200
        
        return templates.TemplateResponse(
            "stocks/detail.html",
            {
                "request": request, 
                "stock": stock_data,
                "user": None,
                "demo_mode": True
            }
        )
    except HTTPException as e:

    forecast_days: int = Query(7, ge=1, le=30),
    
):
    """Display stock detail page"""
        raise e
    except Exception as e:
        logger.error(f"Stock detail error for {ticker}: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e), "user": None, "demo_mode": True},
            status_code=500
        )

@router.get("/stock/search", response_class=HTMLResponse)
async def stock_search(
    request: Request,
    q: str = Query(None)
):
    """Search for stocks (demo mode)"""
    try:
        search_results = []
        
        if q:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_V1_URL}/stocks/search?query={q}&limit=10",
                    timeout=5
                ) as response:
                    if response.status == 200:
                        search_results = await response.json()
        
        return templates.TemplateResponse(
            "stocks/search.html",
            {
                "request": request,
                "query": q,
                "results": search_results,
                "user": None,
                "demo_mode": True
            }
        )
    except Exception as e:

    q: str = Query(None),
    
):
    """Search for stocks"""
        logger.error(f"Stock search error: {str(e)}")
        return templates.TemplateResponse(
            "stocks/search.html",
            {
                "request": request,
                "query": q,
                "error": str(e),
                "results": [],
                "user": None,
                "demo_mode": True
            }
        )

@router.post("/stock/{ticker}/add-to-watchlist")
async def add_to_watchlist(
    request: Request,
    ticker: str
):
    """Add stock to watchlist (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+features+require+authentication+(demo+mode)", status_code=302)

    ticker: str,
    
):
    """Add stock to watchlist"""
        raise e
    except Exception as e:
        logger.error(f"Add to watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
