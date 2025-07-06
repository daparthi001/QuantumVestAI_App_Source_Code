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
    forecast_days: int = Query(7, ge=1, le=30),
    
):
    """Display stock detail page"""
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
                "user": user
            }
        )

@router.post("/stock/{ticker}/add-to-watchlist")
async def add_to_watchlist(
    request: Request,
    ticker: str,
    
):
    """Add stock to watchlist"""
        raise e
    except Exception as e:
        logger.error(f"Add to watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))