"""
Stock Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Depends, Query, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from auth.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.stock_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/stock/{ticker}", response_class=HTMLResponse)
async def stock_detail(
    request: Request,
    ticker: str,
    timeframe: str = Query("1d", regex="^(1d|1w|1m|3m|6m|1y|5y)$"),
    forecast_days: int = Query(7, ge=1, le=30),
    user: dict = Depends(get_current_user)
):
    """Display stock detail page"""
    try:
        stock_data = {
            "ticker": ticker.upper(),
            "timeframe": timeframe,
            "forecast_days": forecast_days
        }
        
        headers = {"Authorization": f"Bearer {user.get('token', '')}"}
        
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
                "user": user
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Stock detail error for {ticker}: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.get("/stock/search", response_class=HTMLResponse)
async def stock_search(
    request: Request,
    q: str = Query(None),
    user: dict = Depends(get_current_user)
):
    """Search for stocks"""
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
                "user": user
            }
        )
    except Exception as e:
        logger.error(f"Stock search error: {str(e)}")
        return templates.TemplateResponse(
            "stocks/search.html",
            {
                "request": request,
                "query": q,
                "error": str(e),
                "results": [],
                "user": user
            }
        )

@router.post("/stock/{ticker}/add-to-watchlist")
async def add_to_watchlist(
    request: Request,
    ticker: str,
    user: dict = Depends(get_current_user)
):
    """Add stock to watchlist"""
    try:
        headers = {"Authorization": f"Bearer {user.get('token', '')}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_V1_URL}/watchlist/{user['username']}/add",
                json={"symbol": ticker},
                headers=headers,
                timeout=5
            ) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to add to watchlist: {error_text}"
                    )
        
        # Redirect back to stock detail page
        return RedirectResponse(
            url=f"/stock/{ticker}?added=1",
            status_code=303
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Add to watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))