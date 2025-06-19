"""
QuantumVestAI Dashboard Controller
Last Updated: 2025-06-18 23:08:04
Author: daparthi001
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import logging
from datetime import datetime
import os
from pathlib import Path
from controllers.auth_controller import get_current_user

# Setup router
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory=str(Path("templates")))
logger = logging.getLogger(__name__)

# Get API URL from environment
API_URL = os.environ.get("API_URL", "http://api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, user: dict = Depends(get_current_user)):
    """Main dashboard page"""
    if not user:
        return RedirectResponse(url="/login?next=/dashboard", status_code=302)
    
    # Prepare dashboard data structure
    dashboard_data = {
        "user": user,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    
    try:
        # Get auth token from cookies
        token = request.cookies.get("access_token", "")
        if token:
            headers = {"Authorization": token}
            
            # Fetch market data
            try:
                market_response = requests.get(
                    f"{API_V1_URL}/market/overview", 
                    headers=headers,
                    timeout=5
                )
                if market_response.status_code == 200:
                    dashboard_data["market"] = market_response.json()
                else:
                    dashboard_data["market"] = {"status": "error", "message": f"API returned status {market_response.status_code}"}
            except Exception as e:
                logger.warning(f"Error fetching market data: {str(e)}")
                dashboard_data["market"] = {"status": "unavailable", "message": str(e)}
            
            # Fetch portfolio data
            try:
                portfolio_response = requests.get(
                    f"{API_V1_URL}/portfolio/summary", 
                    headers=headers,
                    timeout=5
                )
                if portfolio_response.status_code == 200:
                    dashboard_data["portfolio"] = portfolio_response.json()
                else:
                    dashboard_data["portfolio"] = {"status": "error", "message": f"API returned status {portfolio_response.status_code}"}
            except Exception as e:
                logger.warning(f"Error fetching portfolio data: {str(e)}")
                dashboard_data["portfolio"] = {"status": "unavailable", "message": str(e)}
            
            # Fetch watchlist
            try:
                watchlist_response = requests.get(
                    f"{API_V1_URL}/watchlist/highlights", 
                    headers=headers,
                    timeout=5
                )
                if watchlist_response.status_code == 200:
                    dashboard_data["watchlist"] = watchlist_response.json()
                else:
                    dashboard_data["watchlist"] = {"status": "error", "message": f"API returned status {watchlist_response.status_code}"}
            except Exception as e:
                logger.warning(f"Error fetching watchlist: {str(e)}")
                dashboard_data["watchlist"] = {"status": "unavailable", "message": str(e)}
            
            # Fetch news
            try:
                news_response = requests.get(
                    f"{API_V1_URL}/news/highlights", 
                    headers=headers,
                    timeout=5
                )
                if news_response.status_code == 200:
                    dashboard_data["news"] = news_response.json()
                else:
                    dashboard_data["news"] = {"status": "error", "message": f"API returned status {news_response.status_code}"}
            except Exception as e:
                logger.warning(f"Error fetching news: {str(e)}")
                dashboard_data["news"] = {"status": "unavailable", "message": str(e)}
            
            # Fetch recommendations
            try:
                recommendations_response = requests.get(
                    f"{API_V1_URL}/recommendations/personal", 
                    headers=headers,
                    timeout=5
                )
                if recommendations_response.status_code == 200:
                    dashboard_data["recommendations"] = recommendations_response.json()
                else:
                    dashboard_data["recommendations"] = {"status": "error", "message": f"API returned status {recommendations_response.status_code}"}
            except Exception as e:
                logger.warning(f"Error fetching recommendations: {str(e)}")
                dashboard_data["recommendations"] = {"status": "unavailable", "message": str(e)}
            
            # Check feature access - specifically for advanced features
            try:
                features_response = requests.get(
                    f"{API_V1_URL}/users/features",
                    headers=headers,
                    timeout=3
                )
                if features_response.status_code == 200:
                    dashboard_data["features"] = features_response.json()
                    # Log feature status for debugging
                    logger.info(f"User {user.get('username')} features: {dashboard_data['features']}")
                else:
                    dashboard_data["features"] = {"advanced": False}
            except Exception as e:
                logger.warning(f"Error fetching feature access: {str(e)}")
                dashboard_data["features"] = {"advanced": False}
        
        # Render the dashboard with data
        return templates.TemplateResponse(
            "dashboard/index.html",  # Changed from dashboard.html to dashboard/index.html
            {
                "request": request, 
                "user": user,
                "data": dashboard_data
            }
        )
    
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request, 
                "user": user,
                "error": f"Error loading dashboard: {str(e)}"
            },
            status_code=500
        )