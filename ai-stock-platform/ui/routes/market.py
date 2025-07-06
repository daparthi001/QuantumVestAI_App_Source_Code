"""
QuantumVestAI Market Routes
Last Updated: 2025-06-18 22:03:16
Author: daparthi001
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from services.api_client import APIClient
from pathlib import Path
import logging

# Setup router and templates
router = APIRouter(tags=["market"])
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger(__name__)
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

@router.get("/market", response_class=HTMLResponse)
async def market_overview(request: Request):
    """Market overview page (demo mode)"""
    try:
        # Demo mode - no authentication required
        api_client = APIClient(token=None)
        
        # Get market data from API
        market_data = api_client.get("/market/data")
        
        # Get market news
        market_news = api_client.get("/news", params={"limit": 5})
        
        return templates.TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "user": None, "demo_mode": True,
                "market_data": market_data,
                "market_news": market_news
            }
        )
    except Exception as e:

async def market_overview(
    request: Request,
    request: Request
):
    """Market overview page"""
        logger.error(f"Error loading market overview: {str(e)}")
        return templates.TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "user": None, "demo_mode": True,
                "user": None,
                "error": "Failed to load market data"
            },
            status_code=500
        )

@router.get("/market/ticker/{ticker}", response_class=HTMLResponse)
async def ticker_details(
    request: Request,
    ticker: str,
    period: str = Query("1m"),
    request: Request
):
    """Ticker details page"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get ticker details from API
        ticker_data = api_client.get(f"/market/ticker/{ticker}", params={"period": period})
        
        # Get ticker news
        ticker_news = api_client.get("/news/ticker", params={"ticker": ticker, "limit": 5})
        
        # Get ticker predictions
        ticker_predictions = api_client.get(f"/forecast/ticker/{ticker}", params={"period": period})
        
        return templates.TemplateResponse(
            "market/ticker_details.html",
            {
                "request": request,
                "user": None, "demo_mode": True,
                "ticker_data": ticker_data,
                "ticker_news": ticker_news,
                "ticker_predictions": ticker_predictions,
                "selected_period": period
            }
        )
    except Exception as e:

        logger.error(f"Error loading ticker details for {ticker}: {str(e)}")
        return templates.TemplateResponse(
            "market/ticker_details.html",
            {
                "request": request,
                "user": None, "demo_mode": True,

                "user": None,
                "ticker": ticker,
                "error": f"Failed to load data for {ticker}"
            },
            status_code=500
        )

@router.get("/ticker-search")
async def ticker_search(
    request: Request,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Search for ticker symbols"""
        logger.error(f"Error searching tickers with query '{q}': {str(e)}")
        return JSONResponse(
            content={"error": "Failed to search tickers", "detail": str(e)},
            status_code=500
        )

@router.get("/market/sentiment", response_class=HTMLResponse)
async def market_sentiment(
    request: Request,
    period: str = Query("1w"),
    request: Request
):
    """Market sentiment page"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get market sentiment data from API
        sentiment_data = api_client.get("/market/sentiment", params={"period": period})
        
        # Get sentiment trends
        sentiment_trends = api_client.get("/market/sentiment/trends", params={"period": period})
        
        # Get top positive/negative tickers
        sentiment_tickers = api_client.get("/market/sentiment/tickers", params={"limit": 5})
        
        return templates.TemplateResponse(
            "market/sentiment.html",
            {
                "request": request,
                "user": None, "demo_mode": True,
                "sentiment_data": sentiment_data,
                "sentiment_trends": sentiment_trends,
                "sentiment_tickers": sentiment_tickers,
                "selected_period": period
            }
        )
    except Exception as e:

        logger.error(f"Error loading market sentiment: {str(e)}")
        return templates.TemplateResponse(
            "market/sentiment.html",
            {
                "request": request,
                "user": None, "demo_mode": True,
                "user": None,
                "error": "Failed to load market sentiment data"
            },
            status_code=500
        )