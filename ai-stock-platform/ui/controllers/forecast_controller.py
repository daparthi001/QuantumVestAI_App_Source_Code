"""
QuantumVestAI Forecast Controller
Last Updated: 2025-06-18 22:36:43
Author: daparthi001
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import logging
from pathlib import Path
import os
from controllers.auth_controller import get_current_user

# Setup router
router = APIRouter(prefix="/forecast", tags=["forecast"])
templates = Jinja2Templates(directory=str(Path("templates")))
logger = logging.getLogger(__name__)

# Get API URL from environment
API_URL = os.environ.get("API_URL", "http://api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/", response_class=HTMLResponse)
async def forecast_home(request: Request, user: dict = Depends(get_current_user)):
    """Forecast dashboard page"""
    if not user:
        return RedirectResponse(url="/login?next=/forecast", status_code=302)
    
    try:
        # Get auth token from cookies
        token = request.cookies.get("access_token", "")
        headers = {"Authorization": token} if token else {}
        
        # Fetch forecast overview data
        try:
            response = requests.get(
                f"{API_V1_URL}/forecast/overview", 
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                forecast_data = response.json()
            else:
                forecast_data = {"error": f"API returned status {response.status_code}"}
        except Exception as e:
            logger.warning(f"Error fetching forecast overview: {str(e)}")
            forecast_data = {"error": str(e)}
        
        # Render the forecast dashboard
        return templates.TemplateResponse(
            "forecast/index.html",  # UPDATED: Make sure this path is correct
            {
                "request": request,
                "user": user,
                "data": forecast_data
            }
        )
    except Exception as e:
        logger.error(f"Error rendering forecast dashboard: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "user": user,
                "error": f"Error loading forecast dashboard: {str(e)}"
            },
            status_code=500
        )

@router.get("/dashboard", response_class=HTMLResponse)  # THIS ROUTE NEEDS UPDATING
async def forecast_dashboard(request: Request, user: dict = Depends(get_current_user)):
    """Forecast dashboard (alias route)"""
    # Redirect to main forecast page for consistency
    return RedirectResponse(url="/forecast", status_code=302)