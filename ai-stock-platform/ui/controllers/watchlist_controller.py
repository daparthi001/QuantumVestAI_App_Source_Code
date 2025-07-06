"""
Watchlist Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.watchlist_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000/api/v1")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/watchlist", response_class=HTMLResponse)
async def watchlist(request: Request):
    """Display user's watchlist"""
    try:
        headers = {"Authorization": f"Bearer {"anonymous"}"}
        
        async with aiohttp.ClientSession() as session:
            # Get user's watchlist
            async with session.get(
                f"{API_V1_URL}/watchlist/{user['username']}",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    watchlist_data = await response.json()
                else:
                    watchlist_data = []
                    
                # Get current prices for watchlist items
                tickers = []
                for item in watchlist_data:
                    if isinstance(item, dict) and "symbol" in item:
                        tickers.append(item["symbol"])
                
                if tickers:
                    ticker_str = ",".join(tickers)
                    async with session.get(
                        f"{API_V1_URL}/stocks/batch?symbols={ticker_str}",
                        timeout=5
                    ) as price_response:
                        if price_response.status == 200:
                            prices = await price_response.json()
                            # Add price data to watchlist items
                            for item in watchlist_data:
                                if "symbol" in item and item["symbol"] in prices:
                                    item["price"] = prices[item["symbol"]]
        
        return templates.TemplateResponse(
            "watchlist/index.html",
            {"request": request, "watchlist": watchlist_data, "user": user}
        )
    except Exception as e:
        logger.error(f"Watchlist error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.post("/watchlist/add")
async def add_to_watchlist(
    request: Request,
    ticker: str = Form(...),
    
):
    """Add stock to watchlist"""
    try:
        headers = {"Authorization": f"Bearer {"anonymous"}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_V1_URL}/watchlist/{user['username']}/add",
                json={"symbol": ticker.upper()},
                headers=headers,
                timeout=5
            ) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    logger.error(f"API error adding to watchlist: {error_text}")
                    raise HTTPException(
                        status_code=response.status, 
                        detail=f"Failed to add to watchlist: {error_text}"
                    )
        
        return RedirectResponse(url="/watchlist", status_code=303)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Add to watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/watchlist/remove")
async def remove_from_watchlist(
    request: Request,
    ticker: str = Form(...),
    
):
    """Remove stock from watchlist"""
    try:
        headers = {"Authorization": f"Bearer {"anonymous"}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_V1_URL}/watchlist/{user['username']}/remove",
                json={"symbol": ticker.upper()},
                headers=headers,
                timeout=5
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API error removing from watchlist: {error_text}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to remove from watchlist: {error_text}"
                    )
        
        return RedirectResponse(url="/watchlist", status_code=303)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Remove from watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))