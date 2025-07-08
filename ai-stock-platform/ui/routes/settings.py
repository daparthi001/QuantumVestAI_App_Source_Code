"""
QuantumVestAI Settings Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging
from datetime import datetime
from pathlib import Path

# Setup router
router = APIRouter(prefix="/settings", tags=["settings"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# Demo settings data (in-memory for demo)
DEMO_USER_SETTINGS = {
    "general": {
        "email_notifications": True,
        "push_notifications": False,
        "sms_notifications": False,
        "newsletter": True,
        "market_updates": True,
        "price_alerts": True,
        "portfolio_updates": True,
        "news_digest": True
    },
    "preferences": {
        "theme": "light",  # light, dark, auto
        "language": "en",
        "timezone": "America/New_York",
        "currency": "USD",
        "date_format": "MM/DD/YYYY",
        "number_format": "US",
        "chart_type": "candlestick"  # candlestick, line, area
    },
    "privacy": {
        "profile_visibility": "private",  # public, private, friends
        "data_sharing": False,
        "analytics_tracking": True,
        "marketing_emails": False,
        "third_party_data": False
    },
    "trading": {
        "default_quantity": 100,
        "order_confirmation": True,
        "risk_warnings": True,
        "auto_diversification": False,
        "stop_loss_default": 5.0,  # percentage
        "take_profit_default": 10.0  # percentage
    },
    "api": {
        "api_key": "demo_api_key_12345",
        "rate_limit": 1000,  # requests per hour
        "webhook_url": "",
        "api_enabled": True
    }
}

@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Main settings page"""
    try:
        # Check authentication
        auth_cookie = request.cookies.get("access_token")
        if not auth_cookie:
            return RedirectResponse(url="/auth/login?msg=Please log in to access settings", status_code=302)
        
        logger.info("Loading settings page in demo mode")
        
        return get_templates(request).TemplateResponse(
            "settings.html",
            {
                "request": request,
                "demo_mode": True,
                "settings": DEMO_USER_SETTINGS,
                "page_title": "Settings - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load settings",
                "page_title": "Settings Error"
            },
            status_code=500
        )

@router.post("/update")
async def update_settings(request: Request):
    """Update user settings (demo mode)"""
    try:
        logger.info("Updating settings in demo mode")
        
        # Check authentication
        auth_cookie = request.cookies.get("access_token")
        if not auth_cookie:
            return JSONResponse({
                "status": "error",
                "message": "Authentication required"
            }, status_code=401)
        
        return JSONResponse({
            "status": "success",
            "message": "Settings updated successfully (demo mode)"
        })
        
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@router.get("/api/current")
async def get_current_settings(request: Request):
    """Get current user settings via API"""
    try:
        # Check authentication
        auth_cookie = request.cookies.get("access_token")
        if not auth_cookie:
            return JSONResponse({
                "status": "error",
                "message": "Authentication required"
            }, status_code=401)
        
        return JSONResponse({
            "status": "success",
            "settings": DEMO_USER_SETTINGS,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting current settings: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)