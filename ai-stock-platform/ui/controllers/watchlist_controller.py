"""
Watchlist Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.watchlist_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000/api/v1")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/watchlist", response_class=HTMLResponse)
async def watchlist(request: Request):
    """Display user's watchlist (demo mode)"""
    
    # Demo mode - redirect to login with a message that watchlist requires authentication
    return RedirectResponse(url="/login?msg=Watchlist+requires+authentication+(demo+mode)", status_code=302)

@router.post("/watchlist/add")
async def add_to_watchlist(request: Request):
    """Add stock to watchlist (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+features+require+authentication+(demo+mode)", status_code=302)

@router.post("/watchlist/remove")
async def remove_from_watchlist(request: Request):
    """Remove stock from watchlist (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+features+require+authentication+(demo+mode)", status_code=302)
=======
    """Display user's watchlist"""
        logger.error(f"Watchlist error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.post("/watchlist/add")
async def add_to_watchlist(
    request: Request,
    ticker: str = Form(...),
    
):
    """Add stock to watchlist"""
        raise e
    except Exception as e:
        logger.error(f"Add to watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/watchlist/remove")
async def remove_from_watchlist(
    request: Request,
    ticker: str = Form(...),
    
):
    """Remove stock from watchlist"""
        raise e
    except Exception as e:
        logger.error(f"Remove from watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
