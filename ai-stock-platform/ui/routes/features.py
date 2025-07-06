=======
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

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["features"])

@router.get("/features")
async def features_page(request: Request):
    """Features page (demo mode)"""
    return RedirectResponse(url="/login?msg=Features+require+authentication+(demo+mode)", status_code=302)

=======
@router.get("/sentiment", response_class=HTMLResponse)
async def sentiment_analysis(
    request: Request,
    ticker: str = Query(None),
    period: str = Query("1m"),  # 1d, 1w, 1m, 3m, 6m, 1y
    request: Request
):
    """AI Market Sentiment Analysis Feature"""

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
    request: Request
):
    """Multi-factor Analysis Feature"""

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
    request: Request
):
    """Portfolio Optimization Feature"""

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
    request: Request
):
    """Extended Prediction Intervals Feature"""

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
    request: Request
):
    """Custom Technical Indicators Feature"""

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
