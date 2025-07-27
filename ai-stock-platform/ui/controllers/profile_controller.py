"""
QuantumVestAI Profile Controller
Last Updated: 2025-06-18 21:25:28
Author: daparthi001
"""
import logging
from pathlib import Path
from typing import Optional

# Import settings from the API package directly.  Importing via the
# ``core`` compatibility package may load the module instead of the
# ``settings`` instance when multiple ``core`` packages are on the path.
from core.config.settings import settings
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.api_client import APIClient

API_URL = "http://quantumvestai-dev-api.dev.svc.cluster.local:8000"

# Setup router and templates
router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)
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

@router.get("/profile/settings", response_class=HTMLResponse)
async def profile_settings(request: Request):
    """Display user profile settings page"""
    return RedirectResponse(url="/login?next=/profile/settings", status_code=302)

@router.post("/profile/update")
async def update_profile(
    request: Request,
    full_name: str = Form(...),
    bio: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None)
):
    """Update user profile information"""
    return RedirectResponse(url="/login", status_code=302)

@router.post("/profile/update-preferences")
async def update_preferences(
    request: Request,
    theme: str = Form(...),
    language: str = Form(...),
    timezone: str = Form(...),
    dashboard_view: str = Form(...)
):
    """Update user preferences"""
    return RedirectResponse(url="/login", status_code=302)

@router.post("/profile/update-notifications")
async def update_notifications(
    request: Request
):
    """Update user notification settings"""
    return RedirectResponse(url="/login", status_code=302)

@router.post("/profile/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Change user password"""
    return RedirectResponse(url="/login", status_code=302)

@router.post("/profile/features/activate")
async def activate_advanced_features(
    request: Request
):
    """Activate advanced features for user"""
    return RedirectResponse(url="/login", status_code=302)

@router.post("/profile/features/deactivate")
async def deactivate_advanced_features(
    request: Request
):
    """Deactivate advanced features for user"""
    return RedirectResponse(url="/login", status_code=302)
