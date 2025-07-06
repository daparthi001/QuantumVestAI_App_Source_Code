from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from services.api_client import APIClient
from services.yahoo_finance import YahooFinanceService
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["watchlist"])

@router.get("/watchlist", response_class=HTMLResponse)
async def watchlist_page(request: Request):
    """Render watchlist page (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+requires+authentication+(demo+mode)", status_code=302)

@router.post("/watchlist/add", response_class=JSONResponse)
async def add_to_watchlist(request: Request):
    """Add to watchlist (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+features+require+authentication+(demo+mode)", status_code=302)

@router.post("/watchlist/remove", response_class=JSONResponse)
async def remove_from_watchlist(request: Request):
    """Remove from watchlist (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+features+require+authentication+(demo+mode)", status_code=302)

@router.get("/watchlist/data", response_class=JSONResponse)
async def get_watchlist_data(request: Request):
    """Get watchlist data (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+data+requires+authentication+(demo+mode)", status_code=302)

@router.post("/watchlist/reorder", response_class=JSONResponse)
async def reorder_watchlist(request: Request):
    """Reorder watchlist (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Watchlist+features+require+authentication+(demo+mode)", status_code=302)