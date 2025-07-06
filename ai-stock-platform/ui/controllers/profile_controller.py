"""
QuantumVestAI Profile Controller
Last Updated: 2025-06-18 21:25:28
Author: daparthi001
"""
import logging
from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional
from services.api_client import APIClient
from core.config.settings import settings
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Setup router and templates
router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger(__name__)

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Display user profile page (demo mode)"""
    
    # Demo mode - redirect to login with a message that profile requires authentication
    return RedirectResponse(url="/login?msg=Profile+requires+authentication+(demo+mode)", status_code=302)

@router.get("/profile/settings", response_class=HTMLResponse)
async def profile_settings(request: Request):
    """Display profile settings page (demo mode)"""
    
    # Demo mode - redirect to login with a message that profile requires authentication
    return RedirectResponse(url="/login?msg=Profile+settings+require+authentication+(demo+mode)", status_code=302)

@router.post("/profile/update")
async def update_profile(request: Request):
    """Update user profile (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Profile+updates+require+authentication+(demo+mode)", status_code=302)

@router.post("/profile/update-preferences")
async def update_preferences(request: Request):
    """Update user preferences (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Preference+updates+require+authentication+(demo+mode)", status_code=302)

@router.post("/profile/update-notifications")
async def update_notifications(request: Request):
    """Update notification settings (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Notification+settings+require+authentication+(demo+mode)", status_code=302)

@router.post("/profile/change-password")
async def change_password(request: Request):
    """Change user password (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Password+changes+require+authentication+(demo+mode)", status_code=302)

@router.post("/activate-advanced-features")
async def activate_advanced_features(request: Request):
    """Activate advanced features (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Advanced+features+require+authentication+(demo+mode)", status_code=302)

@router.get("/advanced-features", response_class=HTMLResponse)
async def advanced_features_page(request: Request):
    """Display advanced features page (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Advanced+features+require+authentication+(demo+mode)", status_code=302)