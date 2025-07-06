"""
Forecast routes for QuantumVestAI UI
Last updated: 2025-06-20 04:18:52
Updated by: daparthi001
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Query, Path
from fastapi.responses import HTMLResponse, JSONResponse
import logging
import httpx
import os
from datetime import datetime, timedelta
import json

# Configure logging
logger = logging.getLogger(__name__)
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Create router
router = APIRouter(
    prefix="/forecast",
    tags=["forecast"]
)

# Try to import dependencies
    logger.error(f"Error importing dependencies: {str(e)}")
    # Create mock settings
    settings = {
        "API_URL": os.getenv("API_URL", "http://api:8000"),
        "DEBUG": os.getenv("DEBUG", "false").lower() == "true",
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development")
    }
    logger.warning(f"Using fallback settings in forecast routes: {settings}")
except NameError as e:
    logger.error(f"Error setting up templates: {str(e)}")
    # Create mock settings
    settings = {
        "API_URL": os.getenv("API_URL", "http://api:8000"),
        "DEBUG": os.getenv("DEBUG", "false").lower() == "true",
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development")
    }
    logger.warning(f"Using fallback settings in forecast routes: {settings}")

# Try to import auth dependencies
    logger.warning("Auth dependencies not found. Using mock functions.")
    
    
    async def (request: Request, response=None):
        """Mock function that optionally returns a default user"""
        return {"username": "defaultuser", "token": "mock_token"}

# Helper function to get templates
def get_templates(request):
    """Helper function to get templates from app state or create a new instance."""
    templates = getattr(request.app.state, 'templates', None)
    if templates is None:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="templates")
    return templates

@router.get("", response_class=HTMLResponse)
async def forecast_home(
    request: Request,
    
):
    """
    Render the forecast home page.
    """
        logger.exception(f"Error rendering forecast home: {str(e)}")
        
        # Get templates
        templates = get_templates(request)
        
        # Render error template
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "user": None,
                "message": "An error occurred loading the forecast page.",
                "error_code": "FORECAST_ERR"
            },
            status_code=500
        )

@router.get("/stock/{symbol}", response_class=HTMLResponse)
async def stock_forecast(
    request: Request,
    symbol: str = Path(..., description="Stock symbol"),
    period: str = Query("month", description="Forecast period (day, week, month, quarter, year)"),
    
):
    """
    Render the stock forecast page for a specific stock.
    """
        logger.exception(f"Error rendering stock forecast: {str(e)}")
        
        # Get templates
        templates = get_templates(request)
        
        # Render error template
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "user": None,
                "message": f"An error occurred loading the forecast for {symbol}.",
                "error_code": "STOCK_FORECAST_ERR"
            },
            status_code=500
        )

@router.get("/api/forecast/{symbol}", response_model=dict)
async def api_stock_forecast(
    request: Request,
    symbol: str = Path(..., description="Stock symbol"),
    period: str = Query("month", description="Forecast period"),
    
):
    """
    API endpoint to get forecast data for a stock.
    """
        logger.exception(f"API forecast error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error generating forecast"
        )