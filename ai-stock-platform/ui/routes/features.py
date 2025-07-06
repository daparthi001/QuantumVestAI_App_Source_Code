"""
QuantumVestAI Features Routes
Last Updated: 2025-06-18 21:25:28
Author: daparthi001
"""
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.api_client import APIClient
from pathlib import Path
import logging

# Setup router and templates
router = APIRouter(prefix="/features", tags=["features"])
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger(__name__)

API_URL = "http://quantumvestai-dev-api:8000/api/v1"

@router.get("/sentiment", response_class=HTMLResponse)
async def sentiment_analysis(
    request: Request,
    ticker: str = Query(None),
    period: str = Query("1m"),  # 1d, 1w, 1m, 3m, 6m, 1y
    current_
):
    """AI Market Sentiment Analysis Feature"""

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Check if user has access to advanced features
        features = api_client.get_available_features()
        if not features.get("features", {}).get("advanced", {}).get("ai_sentiment", False):
            # If no access, redirect to upgrade page
            return RedirectResponse(url="/profile/upgrade?required=sentiment", status_code=302)
            
        # Get overall market sentiment data
        market_sentiment = api_client.get(
            "/features/sentiment/market",
            params={"period": period}
        )
        
        ticker_sentiment = None
        if ticker:
            # Get ticker-specific sentiment data
            ticker_sentiment = api_client.get(
                "/features/sentiment/ticker",
                params={"ticker": ticker, "period": period}
            )
        
        # Get trending topics related to market sentiment
        trending_topics = api_client.get(
            "/features/sentiment/trends",
            params={"limit": 5}
        )
        
        return templates.TemplateResponse(
            "features/sentiment.html",
            {
                "request": request,
                "user": None,
                "market_sentiment": market_sentiment,
                "ticker_sentiment": ticker_sentiment,
                "trending_topics": trending_topics,
                "selected_ticker": ticker,
                "selected_period": period
            }
        )
    except Exception as e:
        logger.error(f"Error loading sentiment analysis feature: {str(e)}")
        return templates.TemplateResponse(
            "features/sentiment.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to load sentiment analysis data",
                "selected_ticker": ticker,
                "selected_period": period
            },
            status_code=500
        )

@router.get("/multi-factor", response_class=HTMLResponse)
async def multi_factor_analysis(
    request: Request,
    ticker: str = Query(None),
    current_
):
    """Multi-factor Analysis Feature"""

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Check if user has access to advanced features
        features = api_client.get_available_features()
        if not features.get("features", {}).get("advanced", {}).get("multi_factor_analysis", False):
            # If no access, redirect to upgrade page
            return RedirectResponse(url="/profile/upgrade?required=multi-factor", status_code=302)
        
        # Get available factors
        factors = api_client.get("/features/multi-factor/factors")
        
        # Get user's saved factor models
        user_models = api_client.get("/features/multi-factor/user-models")
        
        # Get ticker analysis if specified
        ticker_analysis = None
        if ticker:
            ticker_analysis = api_client.get(
                "/features/multi-factor/analyze",
                params={"ticker": ticker}
            )
        
        return templates.TemplateResponse(
            "features/multi_factor.html",
            {
                "request": request,
                "user": None,
                "factors": factors,
                "user_models": user_models,
                "ticker_analysis": ticker_analysis,
                "selected_ticker": ticker
            }
        )
    except Exception as e:
        logger.error(f"Error loading multi-factor analysis feature: {str(e)}")
        return templates.TemplateResponse(
            "features/multi_factor.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to load multi-factor analysis data",
                "selected_ticker": ticker
            },
            status_code=500
        )

@router.get("/portfolio-optimization", response_class=HTMLResponse)
async def portfolio_optimization(
    request: Request,
    current_
):
    """Portfolio Optimization Feature"""

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Check if user has access to advanced features
        features = api_client.get_available_features()
        if not features.get("features", {}).get("advanced", {}).get("portfolio_optimization", False):
            # If no access, redirect to upgrade page
            return RedirectResponse(url="/profile/upgrade?required=portfolio-optimization", status_code=302)
        
        # Get user portfolios
        portfolios = api_client.get("/users/me/portfolios")
        
        # Get optimization models
        optimization_models = api_client.get("/features/portfolio-optimization/models")
        
        return templates.TemplateResponse(
            "features/portfolio_optimization.html",
            {
                "request": request,
                "user": None,
                "portfolios": portfolios,
                "optimization_models": optimization_models
            }
        )
    except Exception as e:
        logger.error(f"Error loading portfolio optimization feature: {str(e)}")
        return templates.TemplateResponse(
            "features/portfolio_optimization.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to load portfolio optimization data"
            },
            status_code=500
        )

@router.get("/extended-predictions", response_class=HTMLResponse)
async def extended_predictions(
    request: Request,
    ticker: str = Query(None),
    interval: str = Query("12m"),
    current_
):
    """Extended Prediction Intervals Feature"""

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Check if user has access to advanced features
        features = api_client.get_available_features()
        if not features.get("features", {}).get("advanced", {}).get("prediction_interval", False):
            # If no access, redirect to upgrade page
            return RedirectResponse(url="/profile/upgrade?required=extended-predictions", status_code=302)
            
        # Get ticker prediction if specified
        prediction_data = None
        if ticker:
            prediction_data = api_client.get(
                "/features/predictions/extended",
                params={"ticker": ticker, "interval": interval}
            )
        
        # Get recent predictions
        recent_predictions = api_client.get(
            "/features/predictions/recent",
            params={"limit": 5}
        )
        
        return templates.TemplateResponse(
            "features/extended_predictions.html",
            {
                "request": request,
                "user": None,
                "prediction_data": prediction_data,
                "recent_predictions": recent_predictions,
                "selected_ticker": ticker,
                "selected_interval": interval
            }
        )
    except Exception as e:
        logger.error(f"Error loading extended predictions feature: {str(e)}")
        return templates.TemplateResponse(
            "features/extended_predictions.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to load extended prediction data",
                "selected_ticker": ticker,
                "selected_interval": interval
            },
            status_code=500
        )

@router.get("/custom-indicators", response_class=HTMLResponse)
async def custom_indicators(
    request: Request,
    current_
):
    """Custom Technical Indicators Feature"""

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Check if user has access to advanced features
        features = api_client.get_available_features()
        if not features.get("features", {}).get("advanced", {}).get("custom_indicators", False):
            # If no access, redirect to upgrade page
            return RedirectResponse(url="/profile/upgrade?required=custom-indicators", status_code=302)
            
        # Get user's custom indicators
        user_indicators = api_client.get("/features/indicators/custom")
        
        # Get available indicator components
        components = api_client.get("/features/indicators/components")
        
        return templates.TemplateResponse(
            "features/custom_indicators.html",
            {
                "request": request,
                "user": None,
                "user_indicators": user_indicators,
                "components": components
            }
        )
    except Exception as e:
        logger.error(f"Error loading custom indicators feature: {str(e)}")
        return templates.TemplateResponse(
            "features/custom_indicators.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to load custom indicators data"
            },
            status_code=500
        )