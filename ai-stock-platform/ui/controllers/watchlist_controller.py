"""
Watchlist Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import logging
import os
from pathlib import Path

import aiohttp
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))

def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)
logger = logging.getLogger("quantumvestai.watchlist_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/watchlist", response_class=HTMLResponse)
async def watchlist(request: Request):
    """Display user's watchlist."""
    
    # Demo mode - redirect to login with a message that watchlist requires authentication
    return RedirectResponse(url="/login?msg=Watchlist+requires+authentication", status_code=302)

@router.post("/watchlist/add")
async def add_to_watchlist(request: Request):
    """Add stock to watchlist."""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+features+require+authentication", status_code=302)

@router.post("/watchlist")
async def view_watchlist(request: Request):
    """Display user's watchlist"""
    try:
        # Demo mode - redirect to login with a message
        return RedirectResponse(
            url="/login?msg=Watchlist+features+require+authentication+(demo+mode)", 
            status_code=302
        )
    except Exception as e:
        logger.error(f"Watchlist error: {str(e)}")
        return get_templates(request).TemplateResponse(
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
    try:
        # Get user from session or authentication
        user_id = request.session.get("user_id")  # Adjust based on your auth system
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Validate ticker format (basic validation)
        ticker = ticker.upper().strip()
        if not ticker or len(ticker) > 10:
            raise HTTPException(status_code=400, detail="Invalid ticker symbol")
        
        # Add to watchlist (adjust based on your database/storage system)
        # Example with database:
        # await db.add_to_watchlist(user_id, ticker)
        
        # Example response
        return {"message": f"Successfully added {ticker} to watchlist", "ticker": ticker}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Add to watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add stock to watchlist")


@router.post("/watchlist/remove")
async def remove_from_watchlist(
    request: Request,
    ticker: str = Form(...),
):
    """Remove stock from watchlist"""
    try:
        # Get user from session or authentication
        user_id = request.session.get("user_id")  # Adjust based on your auth system
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Validate ticker format
        ticker = ticker.upper().strip()
        if not ticker:
            raise HTTPException(status_code=400, detail="Invalid ticker symbol")
        
        # Remove from watchlist (adjust based on your database/storage system)
        # Example with database:
        # removed = await db.remove_from_watchlist(user_id, ticker)
        # if not removed:
        #     raise HTTPException(status_code=404, detail="Stock not found in watchlist")
        
        # Example response
        return {"message": f"Successfully removed {ticker} from watchlist", "ticker": ticker}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Remove from watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove stock from watchlist")
