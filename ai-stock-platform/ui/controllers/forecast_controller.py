"""
QuantumVestAI Forecast Controller
Last Updated: 2025-07-07 21:39:48
Author: hemanth9398
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from core.config.settings import settings

import requests
import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Setup router
router = APIRouter(prefix="/forecast", tags=["forecast"])
templates = Jinja2Templates(directory=str(Path("templates")))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)
logger = logging.getLogger(__name__)

# Get API URL from environment
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/", response_class=HTMLResponse)
async def forecast_home(request: Request):
    """Forecast dashboard page."""
    
    try:
        logger.info("Loading forecast dashboard")
        
        # Fetch live forecast data from API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_V1_URL}/predictions")
                response.raise_for_status()
                forecast_data = response.json()
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch forecast data from API: {e}")
            raise HTTPException(
                status_code=503, 
                detail="Forecast service temporarily unavailable - please check API connectivity"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"API returned error status {e.response.status_code}: {e}")
            raise HTTPException(
                status_code=502,
                detail="Forecast service returned an error - please try again later"
            )
        
        # Additional market overview data from API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_V1_URL}/market/overview")
                response.raise_for_status()
                market_overview = response.json()
        except httpx.RequestError as e:
            logger.warning(f"Failed to fetch market overview: {e}")
            # Use minimal fallback data if API fails
            market_overview = {
                "sp500_trend": "unknown",
                "nasdaq_trend": "unknown", 
                "dow_trend": "unknown",
                "vix_level": "unknown",
                "fear_greed_index": None
            }
        
        # Render the forecast dashboard
        return get_templates(request).TemplateResponse(
            "forecast/index.html",
            {
                "request": request,
                "user": None,
                "forecast_data": forecast_data,
                "market_overview": market_overview,
                "page_title": "AI Forecast Dashboard",
                "active_nav": "forecast"
            }
        )
        
    except Exception as e:
        logger.error(f"Error rendering forecast dashboard: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "user": None,
                "error": f"Error loading forecast dashboard: {str(e)}",
                "page_title": "Forecast Error"
            },
            status_code=500
        )


@router.get("/dashboard", response_class=HTMLResponse)
async def forecast_dashboard(request: Request):
    """Forecast dashboard (alias route)."""
    # Redirect to main forecast page for consistency
    return RedirectResponse(url="/forecast/", status_code=302)


@router.get("/stock/{symbol}", response_class=HTMLResponse)
async def stock_forecast(
    request: Request, 
    symbol: str,
    timeframe: str = Query("30d", description="Forecast timeframe: 7d, 30d, 90d, 1y")
):
    """Individual stock forecast page"""
    
    try:
        symbol = symbol.upper()
        logger.info(f"Loading forecast for {symbol} with timeframe {timeframe}")
        
        # Fetch live forecast data for individual stock from API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_V1_URL}/predictions/{symbol}")
                response.raise_for_status()
                stock_forecast_data = response.json()
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch forecast data for {symbol}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Forecast service temporarily unavailable for {symbol} - please check API connectivity"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"API returned error status {e.response.status_code} for {symbol}: {e}")
            raise HTTPException(
                status_code=502,
                detail=f"Forecast service returned an error for {symbol} - please try again later"
            )
        
        return get_templates(request).TemplateResponse(
            "forecast/stock_detail.html",
            {
                "request": request,
                "user": None,
                "stock_data": stock_forecast_data,
                "available_timeframes": ["7d", "30d", "90d", "1y"],
                "page_title": f"{symbol} Forecast",
                "active_nav": "forecast"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading stock forecast for {symbol}: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "user": None,
                "error": f"Error loading forecast for {symbol}: {str(e)}",
                "page_title": "Stock Forecast Error"
            },
            status_code=500
        )


@router.get("/api/predictions", response_class=dict)
async def get_predictions_api(
    request: Request,
    symbols: Optional[str] = Query(None, description="Comma-separated stock symbols"),
    timeframe: str = Query("30d", description="Forecast timeframe")
):
    """API endpoint for getting forecast predictions"""
    
    try:
        # Fetch live predictions from API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {}
                if symbols:
                    params['symbols'] = symbols
                params['timeframe'] = timeframe
                
                response = await client.get(f"{API_V1_URL}/predictions", params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch predictions from API: {e}")
            raise HTTPException(
                status_code=503,
                detail="Predictions service temporarily unavailable - please check API connectivity"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"API returned error status {e.response.status_code}: {e}")
            raise HTTPException(
                status_code=502,
                detail="Predictions service returned an error - please try again later"
            )
        
    except Exception as e:
        logger.error(f"Error in predictions API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching predictions: {str(e)}")


@router.get("/api/market-sentiment", response_class=dict)
async def get_market_sentiment_api(request: Request):
    """API endpoint for current market sentiment"""
    
    try:
        # Fetch live market sentiment from API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_V1_URL}/market/sentiment")
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Failed to fetch market sentiment from API: {e}")
            raise HTTPException(
                status_code=503,
                detail="Market sentiment service temporarily unavailable - please check API connectivity"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"API returned error status {e.response.status_code}: {e}")
            raise HTTPException(
                status_code=502,
                detail="Market sentiment service returned an error - please try again later"
            )
        
    except Exception as e:
        logger.error(f"Error in market sentiment API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching market sentiment: {str(e)}")


# Health check endpoint for the forecast service
@router.get("/health")
async def forecast_health_check():
    """Health check endpoint for forecast service"""
    return {
        "status": "healthy",
        "service": "forecast",
        "timestamp": "2025-07-07T21:39:48Z"
    }
