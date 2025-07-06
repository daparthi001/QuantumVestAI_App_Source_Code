"""
QuantumVestAI Feature Controller
Updated: 2025-06-19 02:20:19
Author: daparthi001
"""
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import requests
import logging
import os
import json
from pathlib import Path

# Setup router
router = APIRouter(prefix="/features", tags=["features"])
logger = logging.getLogger("quantumvestai.feature_controller")

# Get templates from app state
def get_templates():
    from main import app
    return app.state.templates

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000/api/v1")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/advanced", response_class=HTMLResponse)
async def advanced_features(request: Request):
    """Advanced features page (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Advanced+features+require+authentication+(demo+mode)", status_code=302)

@router.post("/activate")
async def activate_features(request: Request):
    """Activate features (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Feature+activation+requires+authentication+(demo+mode)", status_code=302)

@router.get("/status")
async def feature_status(request: Request):
    """Feature status (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Feature+status+requires+authentication+(demo+mode)", status_code=302)

@router.get("/debug", response_class=HTMLResponse)
async def debug_features(request: Request):
    """Debug features page (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Debug+features+require+authentication+(demo+mode)", status_code=302)