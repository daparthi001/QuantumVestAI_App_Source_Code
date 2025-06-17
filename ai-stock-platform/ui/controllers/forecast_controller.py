"""
Forecast Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Depends, Query, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List, Optional
from auth.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.forecast_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/forecast", response_class=HTMLResponse)
async def forecast_dashboard(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """Display forecast dashboard"""
    try:
        forecast_data = {
            "user": user
        }
        
        headers = {"Authorization": f"Bearer {user.get('token', '')}"}
        
        async with aiohttp.ClientSession() as session:
            # Get recommendations
            async with session.get(
                f"{API_V1_URL}/forecast/recommendations",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    forecast_data["recommendations"] = await response.json()
                else:
                    forecast_data["recommendations"] = []
            
            # Get user's watchlist for quick forecasting
            async with session.get(
                f"{API_V1_URL}/watchlist/{user['username']}",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    watchlist = await response.json()
                    forecast_data["watchlist"] = watchlist
                else:
                    forecast_data["watchlist"] = []
        
        return templates.TemplateResponse(
            "forecast/dashboard.html",
            {"request": request, "data": forecast_data}
        )
    except Exception as e:
        logger.error(f"Forecast dashboard error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.get("/forecast/{ticker}", response_class=HTMLResponse)
async def stock_forecast(
    request: Request,
    ticker: str,
    days: int = Query(7, ge=1, le=30),
    model: str = Query("ensemble", regex="^(ensemble|lstm|prophet|xgboost|arima)$"),
    include_sentiment: bool = Query(False),
    user: dict = Depends(get_current_user)
):
    """Display forecast for a specific stock"""
    try:
        forecast_data = {
            "ticker": ticker.upper(),
            "days": days,
            "model": model,
            "include_sentiment": include_sentiment
        }
        
        headers = {"Authorization": f"Bearer {user.get('token', '')}"}
        
        async with aiohttp.ClientSession() as session:
            # Get stock details
            async with session.get(f"{API_V1_URL}/stocks/{ticker}", timeout=5) as response:
                if response.status == 200:
                    forecast_data["stock"] = await response.json()
                elif response.status == 404:
                    raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")
                else:
                    forecast_data["stock"] = {"symbol": ticker.upper()}
            
            # Get forecast
            sentiment_param = "&include_sentiment=true" if include_sentiment else ""
            async with session.get(
                f"{API_V1_URL}/forecast/{ticker}?days={days}&model={model}{sentiment_param}",
                headers=headers,
                timeout=10
            ) as response:
                if response.status == 200:
                    forecast_data["forecast"] = await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Forecast API error: {error_text}")
                    forecast_data["forecast"] = {"status": "error", "error": error_text}
            
            # Get predictability if premium user
            if user.get("role") in ["premium", "admin"]:
                async with session.get(
                    f"{API_V1_URL}/forecast/{ticker}/predictability",
                    headers=headers,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        forecast_data["predictability"] = await response.json()
                    else:
                        forecast_data["predictability"] = {"status": "unavailable"}
        
        # Determine available models based on user role
        available_models = ["ensemble"]
        if user.get("role") in ["premium", "admin"]:
            available_models = ["ensemble", "lstm", "prophet", "xgboost", "arima"]
        
        forecast_data["available_models"] = available_models
        
        return templates.TemplateResponse(
            "forecast/stock.html",
            {"request": request, "data": forecast_data, "user": user}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Stock forecast error for {ticker}: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.get("/forecast/compare/{ticker}", response_class=HTMLResponse)
async def compare_models(
    request: Request,
    ticker: str,
    days: int = Query(7, ge=1, le=30),
    user: dict = Depends(get_current_user)
):
    """Compare different forecast models for a stock"""
    # Check premium access
    if user.get("role") not in ["premium", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Model comparison requires a premium subscription"
        )
    
    try:
        compare_data = {
            "ticker": ticker.upper(),
            "days": days
        }
        
        headers = {"Authorization": f"Bearer {user.get('token', '')}"}
        
        async with aiohttp.ClientSession() as session:
            # Get stock details
            async with session.get(f"{API_V1_URL}/stocks/{ticker}", timeout=5) as response:
                if response.status == 200:
                    compare_data["stock"] = await response.json()
                elif response.status == 404:
                    raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")
                else:
                    compare_data["stock"] = {"symbol": ticker.upper()}
            
            # Get model comparison
            async with session.get(
                f"{API_V1_URL}/forecast/{ticker}/compare-models?days={days}",
                headers=headers,
                timeout=15
            ) as response:
                if response.status == 200:
                    compare_data["comparison"] = await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Model comparison API error: {error_text}")
                    compare_data["comparison"] = {"status": "error", "error": error_text}
        
        return templates.TemplateResponse(
            "forecast/compare.html",
            {"request": request, "data": compare_data, "user": user}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Model comparison error for {ticker}: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )