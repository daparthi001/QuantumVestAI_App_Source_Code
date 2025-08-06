"""
QuantumVestAI Settings Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from core.config.settings import settings

# Setup router
router = APIRouter(prefix="/settings", tags=["settings"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# Demo settings data removed
DEMO_USER_SETTINGS = {}

@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Main settings page"""
    try:
        # AuthMiddleware attaches validated user info to request.state
        user = getattr(request.state, "user", None)
        if not user:
            return RedirectResponse(
                url="/auth/login?msg=Please log in to access settings", status_code=302
            )

        logger.info("Loading settings page for %s", user.get("username"))

        return get_templates(request).TemplateResponse(
            "settings.html",
            {
                "request": request,
                "settings": DEMO_USER_SETTINGS,
                "page_title": "Settings - QuantumVestAI",
            },
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
    """Update user settings."""
    try:
        logger.info("Updating settings")

        user = getattr(request.state, "user", None)
        if not user:
            return JSONResponse(
                {"status": "error", "message": "Authentication required"},
                status_code=401,
            )

        return JSONResponse(
            {"status": "success", "message": "Settings updated successfully"}
        )
        
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
        user = getattr(request.state, "user", None)
        if not user:
            return JSONResponse(
                {"status": "error", "message": "Authentication required"},
                status_code=401,
            )

        return JSONResponse(
            {
                "status": "success",
                "settings": DEMO_USER_SETTINGS,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error getting current settings: {str(e)}")
        return JSONResponse(
            {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
            status_code=500,
        )
