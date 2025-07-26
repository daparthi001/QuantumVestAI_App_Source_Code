"""
QuantumVestAI Feature Controller
Updated: 2025-06-19 02:20:19
Author: daparthi001
"""
import json
import logging
import os
from pathlib import Path

import requests
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Setup router
router = APIRouter(prefix="/features", tags=["features"])
logger = logging.getLogger("quantumvestai.feature_controller")

# Get templates from app state
templates = Jinja2Templates(directory=str(Path("templates")))

def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
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

