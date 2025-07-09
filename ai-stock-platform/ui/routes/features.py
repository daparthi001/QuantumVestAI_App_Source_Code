"""
QuantumVestAI Features Routes
Last Updated: 2025-07-07 21:38:39
Author: daparthi001
"""
from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.api_client import APIClient
from pathlib import Path
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize templates
templates = Jinja2Templates(directory="templates")


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

router = APIRouter(tags=["features"])

@router.get("/features")
async def features_page(request: Request):
    """Features page (demo mode)"""
    return RedirectResponse(url="/login?msg=Features+require+authentication+(demo+mode)", status_code=302)


@router.get("/sentiment", response_class=HTMLResponse)
async def sentiment_analysis(
    request: Request,
    ticker: str = Query(None),
    period: str = Query("1m"),  # 1d, 1w, 1m, 3m, 6m, 1y
):
    """AI Market Sentiment Analysis Feature"""
    try:
        # Check if user is authenticated (adjust based on your auth system)
        user = request.session.get("user")  # or however you handle authentication
        
        # Initialize API client
        api_client = APIClient()
        
        sentiment_data = None
        if ticker:
            # Fetch sentiment analysis data
            sentiment_data = await api_client.get_sentiment_analysis(ticker, period)
        
        return get_templates(request).TemplateResponse(
            "features/sentiment.html",
            {
                "request": request,
                "user": user,
                "sentiment_data": sentiment_data,
                "selected_ticker": ticker,
                "selected_period": period,
                "available_periods": ["1d", "1w", "1m", "3m", "6m", "1y"]
            }
        )
    except Exception as e:
        logger.error(f"Error loading sentiment analysis feature: {str(e)}")
        return get_templates(request).TemplateResponse(
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
):
    """Multi-factor Analysis Feature"""
    try:
        # Check if user is authenticated
        user = request.session.get("user")
        
        # Initialize API client
        api_client = APIClient()
        
        analysis_data = None
        if ticker:
            # Fetch multi-factor analysis data
            analysis_data = await api_client.get_multi_factor_analysis(ticker)
        
        return get_templates(request).TemplateResponse(
            "features/multi_factor.html",
            {
                "request": request,
                "user": user,
                "analysis_data": analysis_data,
                "selected_ticker": ticker,
                "available_factors": ["momentum", "value", "quality", "volatility", "growth"]
            }
        )
    except Exception as e:
        logger.error(f"Error loading multi-factor analysis feature: {str(e)}")
        return get_templates(request).TemplateResponse(
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
):
    """Portfolio Optimization Feature"""
    try:
        # Check if user is authenticated
        user = request.session.get("user")
        
        # Initialize API client
        api_client = APIClient()
        
        # Fetch portfolio optimization data
        optimization_data = await api_client.get_portfolio_optimization(user_id=user.get("id") if user else None)
        
        return get_templates(request).TemplateResponse(
            "features/portfolio_optimization.html",
            {
                "request": request,
                "user": user,
                "optimization_data": optimization_data,
                "optimization_methods": ["mean_variance", "risk_parity", "black_litterman", "hierarchical_risk_parity"]
            }
        )
    except Exception as e:
        logger.error(f"Error loading portfolio optimization feature: {str(e)}")
        return get_templates(request).TemplateResponse(
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
):
    """Extended Prediction Intervals Feature"""
    try:
        # Check if user is authenticated
        user = request.session.get("user")
        
        # Initialize API client
        api_client = APIClient()
        
        prediction_data = None
        if ticker:
            # Fetch extended prediction data
            prediction_data = await api_client.get_extended_predictions(ticker, interval)
        
        return get_templates(request).TemplateResponse(
            "features/extended_predictions.html",
            {
                "request": request,
                "user": user,
                "prediction_data": prediction_data,
                "selected_ticker": ticker,
                "selected_interval": interval,
                "available_intervals": ["3m", "6m", "12m", "24m", "36m"]
            }
        )
    except Exception as e:
        logger.error(f"Error loading extended predictions feature: {str(e)}")
        return get_templates(request).TemplateResponse(
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
):
    """Custom Technical Indicators Feature"""
    try:
        # Check if user is authenticated
        user = request.session.get("user")
        
        # Initialize API client
        api_client = APIClient()
        
        # Fetch custom indicators data
        indicators_data = await api_client.get_custom_indicators(user_id=user.get("id") if user else None)
        
        return get_templates(request).TemplateResponse(
            "features/custom_indicators.html",
            {
                "request": request,
                "user": user,
                "indicators_data": indicators_data,
                "available_indicators": [
                    "RSI", "MACD", "Bollinger Bands", "Stochastic", 
                    "Williams %R", "CCI", "ADX", "Parabolic SAR"
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error loading custom indicators feature: {str(e)}")
        return get_templates(request).TemplateResponse(
            "features/custom_indicators.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to load custom indicators data"
            },
            status_code=500
        )


# Additional helper route for AJAX requests
@router.get("/api/quick-analysis/{ticker}")
async def quick_analysis_api(
    request: Request,
    ticker: str,
):
    """Quick analysis API endpoint for AJAX requests"""
    try:
        # Check authentication
        user = request.session.get("user")
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Initialize API client
        api_client = APIClient()
        
        # Get quick analysis data
        analysis = await api_client.get_quick_analysis(ticker)
        
        return {
            "success": True,
            "data": analysis,
            "ticker": ticker
        }
    except Exception as e:
        logger.error(f"Error in quick analysis API: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analysis data")