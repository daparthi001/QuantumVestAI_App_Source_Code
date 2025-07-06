from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from services.api_client import APIClient
from config.settings import settings
import os
import shutil
from pathlib import Path
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["profile"])

@router.get("/", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Render user profile page (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Profile+requires+authentication+(demo+mode)", status_code=302)

@router.post("/update", response_class=HTMLResponse)
async def update_profile(request: Request):
    """Update profile (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Profile+updates+require+authentication+(demo+mode)", status_code=302)

@router.post("/change-password", response_class=HTMLResponse)
async def change_password(request: Request):
    """Change password (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Password+changes+require+authentication+(demo+mode)", status_code=302)