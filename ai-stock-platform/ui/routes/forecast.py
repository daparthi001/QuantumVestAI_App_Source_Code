"""
Forecasting routes for QuantumVestAI
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-16 22:11:00 by daparthi001
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Try to import settings and auth dependencies
try:
    from core.config import settings
    
    # Direct dependency function to avoid importing from routes.auth
    async def get_user_from_token(token: str):
        from routes.auth import get_current_user
        return await get_current_user(token)
    
    # Define custom dependency
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
    
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        return await get_user_from_token(token)
    
except ImportError as e:
    logger.error(f"Error importing dependencies: {e}")
    
    # Fallback dependencies
    async def get_current_user(token = None):
        return {"username": "unknown", "role": "guest"}

# Set up templates
try:
    from pathlib import Path
    templates_dir = Path(settings.TEMPLATES_DIR)
    templates = Jinja2Templates(directory=templates_dir)
except Exception as e:
    logger.error(f"Error setting up templates: {e}")
    # Fallback to a basic path
    from pathlib import Path
    templates = Jinja2Templates(directory="templates")

# Forecast routes
@router.get("/", response_class=HTMLResponse)
async def forecast_home(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse(
        "forecast/index.html", 
        {"request": request, "user": current_user}
    )