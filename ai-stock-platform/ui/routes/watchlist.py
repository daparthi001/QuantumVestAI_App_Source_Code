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
async def watchlist_page(
    request: Request, 
    current_request: Request,
    view: str = Query("grid", regex="^(grid|list)$")
):
    """Render watchlist page"""
    
                    # If stock info fetch fails, still include the ticker
                    stocks_data.append(item)
        
        # Get watchlist summary if available
        summary = None
            # If summary fails, continue without it
            pass
            
        # Get alerts for the watchlist
        alerts = None
            # If alerts fetch fails, continue without them
            pass
            
        return templates.TemplateResponse(
            "watchlist.html", 
            {
                "request": request, 
                "user": None, 
                "watchlist": stocks_data, 
                "summary": summary,
                "alerts": alerts,
                "view": view
            }
        )
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        return templates.TemplateResponse(
            "watchlist.html", 
            {
                "request": request, 
                "user": None, 
                "watchlist": [], 
                "error": error_message,
                "view": view
            }
        )

@router.post("/watchlist/add")
async def add_to_watchlist(
    request: Request,
    ticker: str = Form(...),
    notes: Optional[str] = Form(None),
    request: Request
):
    """Add a stock to the watchlist"""
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
        error_message = "Failed to add stock to watchlist"
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.post("/watchlist/remove")
async def remove_from_watchlist(
    request: Request,
    ticker: str = Form(...),
    request: Request
):
    """Remove a stock from the watchlist"""
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
        error_message = "Failed to remove stock from watchlist"
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.post("/watchlist/set-alert")
async def set_price_alert(
    request: Request,
    ticker: str = Form(...),
    price: float = Form(...),
    direction: str = Form(...),  # "above" or "below"
    request: Request
):
    """Set a price alert for a stock"""
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
        error_message = "Failed to set price alert"
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.post("/watchlist/remove-alert")
async def remove_price_alert(
    request: Request,
    alert_id: str = Form(...),
    request: Request
):
    """Remove a price alert"""
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
        error_message = "Failed to remove price alert"
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.post("/watchlist/update-notes")
async def update_stock_notes(
    request: Request,
    ticker: str = Form(...),
    notes: str = Form(...),
    request: Request
):
    """Update notes for a stock in the watchlist"""
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
        error_message = "Failed to update notes"
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )
