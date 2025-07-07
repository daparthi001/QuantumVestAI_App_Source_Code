"""
User settings routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import requests
import os
from datetime import datetime
import json

# Setup logging
logger = logging.getLogger(__name__)

# Setup templates - use relative path from project root
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000/api/v1")

# Create router
router = APIRouter(tags=["settings"])

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    auth_cookie = request.cookies.get("access_token")
    return bool(auth_cookie)

def get_user_from_request(request: Request) -> Optional[Dict]:
    """Extract user info from request"""
    if is_authenticated(request):
        return {
            "username": "demo",
            "email": "demo@quantumvestai.com",
            "role": "user",
            "is_authenticated": True
        }
    return None

def get_demo_user_settings() -> Dict[str, Any]:
    """Generate demo user settings"""
    return {
        "profile": {
            "username": "demo",
            "email": "demo@quantumvestai.com",
            "full_name": "Demo User",
            "phone": "+1-555-0123",
            "timezone": "America/New_York",
            "language": "en-US",
            "country": "United States"
        },
        "preferences": {
            "theme": "dark",
            "currency": "USD",
            "date_format": "MM/DD/YYYY",
            "time_format": "12h",
            "dashboard_layout": "default",
            "default_timeframe": "1y",
            "auto_refresh": True,
            "refresh_interval": 30
        },
        "notifications": {
            "email_enabled": True,
            "push_enabled": True,
            "sms_enabled": False,
            "price_alerts": True,
            "portfolio_updates": True,
            "market_news": True,
            "research_reports": False,
            "system_notifications": True
        },
        "privacy": {
            "profile_visibility": "private",
            "portfolio_visibility": "private",
            "analytics_tracking": True,
            "data_sharing": False,
            "marketing_emails": False
        },
        "trading": {
            "risk_tolerance": "moderate",
            "investment_style": "growth",
            "auto_rebalancing": False,
            "stop_loss_enabled": True,
            "stop_loss_percentage": 10.0,
            "take_profit_enabled": False,
            "take_profit_percentage": 20.0
        },
        "api": {
            "api_key_enabled": False,
            "rate_limit": 1000,
            "webhooks_enabled": False,
            "data_export_enabled": True
        }
    }

@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Main settings page"""
    try:
        # Check authentication
        if not is_authenticated(request):
            return RedirectResponse(
                url="/login?msg=Please log in to access your settings",
                status_code=status.HTTP_302_FOUND
            )
        
        user = get_user_from_request(request)
        user_settings = get_demo_user_settings()
        
        # Available options for dropdowns
        options = {
            "themes": ["light", "dark", "auto"],
            "currencies": ["USD", "EUR", "GBP", "JPY", "CAD"],
            "timezones": [
                "America/New_York", "America/Chicago", "America/Denver", 
                "America/Los_Angeles", "Europe/London", "Europe/Paris",
                "Asia/Tokyo", "Asia/Singapore", "Australia/Sydney"
            ],
            "languages": ["en-US", "es-ES", "fr-FR", "de-DE", "ja-JP"],
            "risk_tolerance": ["conservative", "moderate", "aggressive"],
            "investment_styles": ["value", "growth", "dividend", "momentum"]
        }
        
        context = {
            "request": request,
            "user": user,
            "settings": user_settings,
            "options": options,
            "page_title": "Settings - QuantumVestAI",
            "active_page": "settings"
        }
        
        return templates.TemplateResponse("settings/index.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering settings page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Settings Error - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h2 class="card-title text-danger">Settings Unavailable</h2>
                                    <p class="card-text">We're experiencing technical difficulties loading your settings.</p>
                                    <div class="mt-3">
                                        <a href="/dashboard" class="btn btn-primary">Return to Dashboard</a>
                                        <a href="/" class="btn btn-secondary">Go Home</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )

@router.post("/profile")
async def update_profile(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    timezone: str = Form("America/New_York"),
    language: str = Form("en-US")
):
    """Update user profile settings"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Validate inputs
        if not full_name or len(full_name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Full name must be at least 2 characters"
            )
        
        if not email or "@" not in email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Please enter a valid email address"
            )
        
        # Simulate API call to update profile
        updated_data = {
            "full_name": full_name.strip(),
            "email": email.strip().lower(),
            "phone": phone.strip(),
            "timezone": timezone,
            "language": language
        }
        
        logger.info(f"Updated profile settings (demo mode): {updated_data}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Profile updated successfully",
            "data": updated_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.post("/preferences")
async def update_preferences(
    request: Request,
    theme: str = Form("dark"),
    currency: str = Form("USD"),
    date_format: str = Form("MM/DD/YYYY"),
    time_format: str = Form("12h"),
    auto_refresh: bool = Form(False),
    refresh_interval: int = Form(30)
):
    """Update user preferences"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Validate inputs
        if theme not in ["light", "dark", "auto"]:
            theme = "dark"
        
        if currency not in ["USD", "EUR", "GBP", "JPY", "CAD"]:
            currency = "USD"
        
        if refresh_interval < 5 or refresh_interval > 300:
            refresh_interval = 30
        
        updated_data = {
            "theme": theme,
            "currency": currency,
            "date_format": date_format,
            "time_format": time_format,
            "auto_refresh": auto_refresh,
            "refresh_interval": refresh_interval
        }
        
        logger.info(f"Updated preferences (demo mode): {updated_data}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Preferences updated successfully",
            "data": updated_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

@router.post("/notifications")
async def update_notifications(
    request: Request,
    email_enabled: bool = Form(False),
    push_enabled: bool = Form(False),
    sms_enabled: bool = Form(False),
    price_alerts: bool = Form(False),
    portfolio_updates: bool = Form(False),
    market_news: bool = Form(False)
):
    """Update notification settings"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        updated_data = {
            "email_enabled": email_enabled,
            "push_enabled": push_enabled,
            "sms_enabled": sms_enabled,
            "price_alerts": price_alerts,
            "portfolio_updates": portfolio_updates,
            "market_news": market_news
        }
        
        logger.info(f"Updated notification settings (demo mode): {updated_data}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Notification settings updated successfully",
            "data": updated_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification settings"
        )

@router.post("/trading")
async def update_trading_settings(
    request: Request,
    risk_tolerance: str = Form("moderate"),
    investment_style: str = Form("growth"),
    auto_rebalancing: bool = Form(False),
    stop_loss_enabled: bool = Form(False),
    stop_loss_percentage: float = Form(10.0),
    take_profit_enabled: bool = Form(False),
    take_profit_percentage: float = Form(20.0)
):
    """Update trading settings"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Validate inputs
        if risk_tolerance not in ["conservative", "moderate", "aggressive"]:
            risk_tolerance = "moderate"
        
        if investment_style not in ["value", "growth", "dividend", "momentum"]:
            investment_style = "growth"
        
        if stop_loss_percentage < 1 or stop_loss_percentage > 50:
            stop_loss_percentage = 10.0
        
        if take_profit_percentage < 5 or take_profit_percentage > 100:
            take_profit_percentage = 20.0
        
        updated_data = {
            "risk_tolerance": risk_tolerance,
            "investment_style": investment_style,
            "auto_rebalancing": auto_rebalancing,
            "stop_loss_enabled": stop_loss_enabled,
            "stop_loss_percentage": stop_loss_percentage,
            "take_profit_enabled": take_profit_enabled,
            "take_profit_percentage": take_profit_percentage
        }
        
        logger.info(f"Updated trading settings (demo mode): {updated_data}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Trading settings updated successfully",
            "data": updated_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trading settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update trading settings"
        )

@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Change user password"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Validate passwords
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New password must be at least 8 characters long"
            )
        
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New passwords do not match"
            )
        
        # For demo purposes, always succeed
        logger.info("Password changed successfully (demo mode)")
        
        return JSONResponse(content={
            "success": True,
            "message": "Password changed successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@router.get("/api/data")
async def get_settings_data(request: Request):
    """API endpoint to get user settings"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        settings_data = get_demo_user_settings()
        
        return JSONResponse(content={
            "success": True,
            "data": settings_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching settings data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch settings data"
        )

@router.post("/export-data")
async def export_user_data(request: Request):
    """Export user data"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Generate export data
        export_data = {
            "user_profile": get_demo_user_settings()["profile"],
            "settings": get_demo_user_settings(),
            "exported_at": datetime.now().isoformat(),
            "export_format": "json",
            "data_version": "1.0"
        }
        
        logger.info("User data export requested (demo mode)")
        
        return JSONResponse(content={
            "success": True,
            "message": "Data export prepared successfully",
            "data": export_data,
            "download_url": "/api/download/user-data.json"  # Mock URL
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export data"
        )

@router.delete("/delete-account")
async def delete_account(
    request: Request,
    password: str = Form(...),
    confirmation: str = Form(...)
):
    """Delete user account"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Validate confirmation
        if confirmation.lower() != "delete my account":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Please type 'delete my account' to confirm"
            )
        
        # For demo purposes, just log the request
        logger.info("Account deletion requested (demo mode - not actually deleting)")
        
        return JSONResponse(content={
            "success": True,
            "message": "Account deletion request received (demo mode - account not actually deleted)",
            "redirect_url": "/login?msg=Demo account deletion completed"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing account deletion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process account deletion"
        )