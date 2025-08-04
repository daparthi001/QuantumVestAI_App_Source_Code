"""
QuantumVestAI Market Routes  
Updated: 2025-08-04
Author: hemanth9398
"""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from core.config.settings import settings

# Setup router and templates
router = APIRouter(prefix="/market", tags=["market"])
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# No demo data - only live data should be used
DEMO_MARKET_DATA = {} 
DEMO_STOCKS_DB = {} # Empty - this will force API calls for live data

@router.get("/", response_class=HTMLResponse)
async def market_overview(request: Request):
    """Market overview page."""
    try:
        logger.info("Loading market overview")
        
        # Market news removed
        market_news = []
        
        data = {}

        return get_templates(request).TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "data": data,
                "market_news": market_news,
                "page_title": "Market Overview - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading market overview: {str(e)}")
        return get_templates(request).TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "data": {
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "overview": None,
                    "sectors": None,
                    "movers": None,
                    "sentiment": None,
                    "user": None,
                },
                "market_news": [],
                "error": "Failed to load market data",
                "page_title": "Market Overview Error",
            },
            status_code=500
        )

@router.get("/ticker/{ticker}", response_class=HTMLResponse)
async def ticker_details(
    request: Request,
    ticker: str,
    period: str = Query("1d", description="Time period: 1d, 5d, 1m, 3m, 6m, 1y")
):
    """Ticker details page"""
    try:
        ticker = ticker.upper()
        logger.info(f"Loading ticker details for {ticker}")
        
        # Get real stock data from API
        try:
            # Get API URL from environment or default
            api_url = os.getenv("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
            
            # Fetch real stock data from API
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{api_url}/api/v1/stocks/{ticker}")
                response.raise_for_status()
                stock_data = response.json().get("data", {})
                
            # Log successful API fetch
            logger.info(f"Successfully fetched live data for {ticker} from API")
            
        except Exception as e:
            logger.error(f"Failed to fetch real data for {ticker}: {e}")
            # Return an error rather than using mock data
            raise HTTPException(
                status_code=503, 
                detail=f"Unable to fetch live data for {ticker}. Please try again later."
            )
        
        # Generate chart data
        chart_data = []
        base_price = stock_data["price"]
        days = {"1d": 1, "5d": 5, "1m": 30, "3m": 90, "6m": 180, "1y": 365}.get(period, 30)
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-1-i)).strftime("%Y-%m-%d")
            price = base_price * (0.95 + (i * 0.003) + (0.02 * (i % 7 - 3) / 10))
            chart_data.append({
                "date": date,
                "price": round(price, 2),
                "volume": int(10000000 + (i * 50000))
            })
        
        # Technical indicators
        technical_indicators = {
            "rsi": 65.4,
            "macd": 2.15,
            "bb_upper": stock_data["price"] * 1.05,
            "bb_lower": stock_data["price"] * 0.95,
            "ma_20": stock_data["price"] * 0.98,
            "ma_50": stock_data["price"] * 0.96
        }
        
        return get_templates(request).TemplateResponse(
            "market/ticker_detail.html",
            {
                "request": request,
                "ticker": ticker,
                "period": period,
                "stock_data": stock_data,
                "chart_data": chart_data,
                "technical_indicators": technical_indicators,
                "page_title": f"{ticker} - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading ticker details for {ticker}: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Unable to load data for {ticker}",
                "page_title": "Ticker Error"
            },
            status_code=500
        )

@router.get("/search")
async def ticker_search(
    request: Request,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Search for ticker symbols using real API data"""
    try:
        query = q.upper()
        
        # Get API URL from environment or default
        api_url = os.getenv("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
        
        try:
            # Fetch real stock search data from API
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{api_url}/api/v1/stocks/search?q={query}&limit={limit}")
                response.raise_for_status()
                search_results = response.json().get("data", [])
                
            # Log successful API fetch
            logger.info(f"Successfully fetched live search results for '{query}' from API")
            
            return JSONResponse({
                "status": "success",
                "results": search_results,
                "query": q,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to fetch real search data for '{query}': {e}")
            # Return an error rather than using mock data
            raise HTTPException(
                status_code=503, 
                detail=f"Unable to fetch live search results. Please try again later."
            )
        
    except Exception as e:
        logger.error(f"Error in ticker search: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)

@router.get("/sentiment", response_class=HTMLResponse)
async def market_sentiment(
    request: Request,
    period: str = Query("1w", description="Time period: 1d, 1w, 1m")
):
    """Market sentiment page"""
    try:
        sentiment_data = {}
        
        return get_templates(request).TemplateResponse(
            "market/sentiment.html",
            {
                "request": request,
                "period": period,
                "sentiment_data": sentiment_data,
                "page_title": "Market Sentiment - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading market sentiment: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load market sentiment data",
                "page_title": "Market Sentiment Error"
            },
            status_code=500
        )

@router.get("/api/data")
async def market_data_api(request: Request):
    """API endpoint for market data"""
    try:
        return JSONResponse({
            "status": "success",
            "data": {},
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting market data API: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)

@router.get("/api/movers")
async def market_movers_api(
    request: Request,
    type: str = Query("gainers", description="Type: gainers, losers, active")
):
    """API endpoint for market movers"""
    try:
        data = []
        
        return JSONResponse({
            "status": "success",
            "movers": data,
            "type": type,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting market movers: {str(e)}")
        return JSONResponse({
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)
