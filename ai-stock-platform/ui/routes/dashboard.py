"""
QuantumVestAI Dashboard Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import logging
from datetime import datetime
from pathlib import Path

# Setup router
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# Demo data removed
DEMO_MARKET_DATA = {}
DEMO_STOCKS = []
DEMO_NEWS = []

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Render main dashboard page (demo mode)"""
    try:
        logger.info("Loading dashboard page in demo mode")
        
        # Get user info from request (demo mode)
        user = {
            "username": "demo",
            "email": "demo@quantumvestai.com", 
            "is_authenticated": True,
            "account_type": "Premium Demo",
            "features_enabled": {
                "advanced_analytics": True,
                "real_time_data": True,
                "portfolio_management": True,
                "ai_predictions": True
            }
        }
        
        # Demo watchlist removed
        watchlist_items = []

        # Demo portfolio performance removed
        portfolio_data = {}
        
        return get_templates(request).TemplateResponse(
            "dashboard/index.html",
            {
                "request": request,
                "user": user,
                "demo_mode": True,
                "market_summary": DEMO_MARKET_DATA,
                "popular_stocks": DEMO_STOCKS,
                "news": DEMO_NEWS,
                "watchlist": watchlist_items,
                "portfolio": portfolio_data,
                "page_title": "Dashboard - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return get_templates(request).TemplateResponse(
            "dashboard/index.html",
            {
                "request": request,
                "user": None,
                "demo_mode": True,
                "market_summary": {"indices": {}, "sectors": {}, "top_movers": {}},
                "popular_stocks": [],
                "news": [],
                "watchlist": [],
                "portfolio": {},
                "error": f"Error loading dashboard: {str(e)}",
                "page_title": "Dashboard Error"
            },
            status_code=500
        )

@router.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request: Request):
    """Portfolio overview page"""
    try:
        # Demo portfolio data removed
        portfolio_data = {}
        
        return get_templates(request).TemplateResponse(
            "dashboard/portfolio.html",
            {
                "request": request,
                "portfolio": portfolio_data,
                "demo_mode": True,
                "page_title": "Portfolio - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading portfolio page: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load portfolio data",
                "page_title": "Portfolio Error"
            },
            status_code=500
        )

@router.get("/analytics", response_class=HTMLResponse) 
async def analytics_page(request: Request):
    """Advanced analytics page"""
    try:
        # Demo analytics data removed
        analytics_data = {}
        
        return get_templates(request).TemplateResponse(
            "dashboard/analytics.html",
            {
                "request": request,
                "analytics": analytics_data,
                "demo_mode": True,
                "page_title": "Analytics - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading analytics page: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load analytics data",
                "page_title": "Analytics Error"
            },
            status_code=500
        )

@router.get("/api/summary")
async def dashboard_api_summary(request: Request):
    """API endpoint for dashboard summary data"""
    try:
        return {
            "status": "success",
            "data": {},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
