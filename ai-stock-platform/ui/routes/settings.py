from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from services.api_client import APIClient
from config.settings import settings

API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["settings"])

@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Render user settings page (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Settings+require+authentication+(demo+mode)", status_code=302)

@router.post("/update", response_class=HTMLResponse)
async def update_settings(request: Request):
    """Update settings (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Settings+updates+require+authentication+(demo+mode)", status_code=302)