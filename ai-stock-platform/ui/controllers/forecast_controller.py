"""
QuantumVestAI Forecast Controller
Last Updated: 2025-06-18 22:36:43
Author: daparthi001
"""
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import logging
from pathlib import Path
import os

# Setup router
router = APIRouter(prefix="/forecast", tags=["forecast"])
templates = Jinja2Templates(directory=str(Path("templates")))
logger = logging.getLogger(__name__)

# Get API URL from environment
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000/api/v1")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/", response_class=HTMLResponse)
async def forecast_home(request: Request):
    """Forecast dashboard page (demo mode)"""
    
    try:
        # Demo mode - no authentication required
        
        # Use demo forecast data
        forecast_data = {
            "status": "success",
            "predictions": [
                {"symbol": "AAPL", "prediction": "bullish", "confidence": 0.85, "target_price": 195.25},
                {"symbol": "MSFT", "prediction": "bullish", "confidence": 0.78, "target_price": 375.50},
                {"symbol": "GOOGL", "prediction": "neutral", "confidence": 0.65, "target_price": 142.75}
            ],
            "market_sentiment": "positive",
            "ai_accuracy": 0.82
        }
        
        # Render the forecast dashboard
        return templates.TemplateResponse(
            "forecast/index.html",  # UPDATED: Make sure this path is correct
            {
                "request": request,
                "user": None,
                "demo_mode": True,
                "data": forecast_data
            }
        )
    except Exception as e:
        logger.error(f"Error rendering forecast dashboard: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "user": None,
                "demo_mode": True,
                "error": f"Error loading forecast dashboard: {str(e)}"
            },
            status_code=500
        )

@router.get("/dashboard", response_class=HTMLResponse)  # THIS ROUTE NEEDS UPDATING
async def forecast_dashboard(request: Request):
    """Forecast dashboard (alias route - demo mode)"""
    # Redirect to main forecast page for consistency
    return RedirectResponse(url="/forecast", status_code=302)