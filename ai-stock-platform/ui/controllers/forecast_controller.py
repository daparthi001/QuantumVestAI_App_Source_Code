"""
QuantumVestAI Forecast Controller
Last Updated: 2025-07-07 21:39:48
Author: hemanth9398
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests
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
    """Forecast dashboard page (demo mode)"""
    
    try:
        # Demo mode - no authentication required
        logger.info("Loading forecast dashboard in demo mode")
        
        # Use demo forecast data
        forecast_data = {
            "status": "success",
            "predictions": [
                {
                    "symbol": "AAPL", 
                    "prediction": "bullish", 
                    "confidence": 0.85, 
                    "target_price": 195.25,
                    "current_price": 185.50,
                    "change_percent": 5.26,
                    "timeframe": "30d"
                },
                {
                    "symbol": "MSFT", 
                    "prediction": "bullish", 
                    "confidence": 0.78, 
                    "target_price": 375.50,
                    "current_price": 365.25,
                    "change_percent": 2.81,
                    "timeframe": "30d"
                },
                {
                    "symbol": "GOOGL", 
                    "prediction": "neutral", 
                    "confidence": 0.65, 
                    "target_price": 142.75,
                    "current_price": 141.80,
                    "change_percent": 0.67,
                    "timeframe": "30d"
                },
                {
                    "symbol": "TSLA", 
                    "prediction": "bearish", 
                    "confidence": 0.72, 
                    "target_price": 195.00,
                    "current_price": 215.30,
                    "change_percent": -9.43,
                    "timeframe": "30d"
                }
            ],
            "market_sentiment": "positive",
            "ai_accuracy": 0.82,
            "last_updated": "2025-07-07T21:39:48Z",
            "total_predictions": 4,
            "bullish_count": 2,
            "bearish_count": 1,
            "neutral_count": 1
        }
        
        # Additional market overview data
        market_overview = {
            "sp500_trend": "bullish",
            "nasdaq_trend": "neutral", 
            "dow_trend": "bullish",
            "vix_level": "low",
            "fear_greed_index": 68
        }
        
        # Render the forecast dashboard
        return get_templates(request).TemplateResponse(
            "forecast/index.html",
            {
                "request": request,
                "user": None,
                "demo_mode": True,
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
                "demo_mode": True,
                "error": f"Error loading forecast dashboard: {str(e)}",
                "page_title": "Forecast Error"
            },
            status_code=500
        )


@router.get("/dashboard", response_class=HTMLResponse)
async def forecast_dashboard(request: Request):
    """Forecast dashboard (alias route - demo mode)"""
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
        
        # Demo forecast data for individual stock
        stock_forecast_data = {
            "symbol": symbol,
            "company_name": f"{symbol} Corporation",  # In real app, fetch from API
            "current_price": 185.50,
            "prediction": "bullish",
            "confidence": 0.85,
            "target_price": 195.25,
            "timeframe": timeframe,
            "price_history": [
                {"date": "2025-07-01", "price": 180.25},
                {"date": "2025-07-02", "price": 182.50},
                {"date": "2025-07-03", "price": 181.75},
                {"date": "2025-07-04", "price": 184.30},
                {"date": "2025-07-05", "price": 185.50}
            ],
            "technical_indicators": {
                "rsi": 65.2,
                "macd": "bullish",
                "moving_avg_20": 183.45,
                "moving_avg_50": 179.20,
                "support_level": 175.00,
                "resistance_level": 190.00
            },
            "ai_insights": [
                "Strong momentum indicators suggest continued upward movement",
                "Earnings expectations are positive for next quarter",
                "Technical analysis shows bullish pattern formation"
            ]
        }
        
        return get_templates(request).TemplateResponse(
            "forecast/stock_detail.html",
            {
                "request": request,
                "user": None,
                "demo_mode": True,
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
                "demo_mode": True,
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
        # Parse symbols
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
        else:
            symbol_list = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        
        # Demo API response
        predictions = []
        for symbol in symbol_list:
            predictions.append({
                "symbol": symbol,
                "prediction": "bullish" if symbol in ["AAPL", "MSFT"] else "neutral",
                "confidence": 0.75 + (hash(symbol) % 20) / 100,  # Mock confidence
                "target_price": 150 + (hash(symbol) % 100),  # Mock target price
                "timeframe": timeframe,
                "timestamp": "2025-07-07T21:39:48Z"
            })
        
        return {
            "status": "success",
            "predictions": predictions,
            "timeframe": timeframe,
            "total_count": len(predictions),
            "demo_mode": True
        }
        
    except Exception as e:
        logger.error(f"Error in predictions API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching predictions: {str(e)}")


@router.get("/api/market-sentiment", response_class=dict)
async def get_market_sentiment_api(request: Request):
    """API endpoint for current market sentiment"""
    
    try:
        # Demo market sentiment data
        sentiment_data = {
            "overall_sentiment": "positive",
            "sentiment_score": 0.68,
            "fear_greed_index": 68,
            "volatility_index": 18.5,
            "market_trends": {
                "sp500": {"trend": "bullish", "confidence": 0.75},
                "nasdaq": {"trend": "neutral", "confidence": 0.65},
                "dow": {"trend": "bullish", "confidence": 0.80}
            },
            "sector_sentiment": {
                "technology": "bullish",
                "healthcare": "neutral",
                "finance": "bullish",
                "energy": "bearish",
                "consumer": "neutral"
            },
            "timestamp": "2025-07-07T21:39:48Z",
            "demo_mode": True
        }
        
        return {
            "status": "success",
            "data": sentiment_data
        }
        
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
        "timestamp": "2025-07-07T21:39:48Z",
        "demo_mode": True
    }
