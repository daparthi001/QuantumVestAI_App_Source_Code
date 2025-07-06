from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from routes.auth import get_current_user
from services.api_client import APIClient
from services.yahoo_finance import YahooFinanceService
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["watchlist"])

@router.get("/watchlist", response_class=HTMLResponse)
async def watchlist_page(
    request: Request, 
    current_user: dict = Depends(get_current_user),
    view: str = Query("grid", regex="^(grid|list)$")
):
    """Render watchlist page"""
    if not current_user:
        return RedirectResponse(url="/login?next=/watchlist", status_code=302)
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Get user's watchlist
        watchlist = api_client.get("/api/watchlist")
        
        # Fetch current data for stocks in watchlist
        stocks_data = []
        if watchlist:
            for item in watchlist:
                ticker = item["ticker"]
                try:
                    # Get stock info from Yahoo Finance
                    stock_info = YahooFinanceService.get_stock_info(ticker)
                    
                    # Add stock info to watchlist item
                    stocks_data.append({
                        **item,
                        "info": stock_info
                    })
                except Exception:
                    # If stock info fetch fails, still include the ticker
                    stocks_data.append(item)
        
        # Get watchlist summary if available
        summary = None
        try:
            summary = api_client.get("/api/watchlist/summary")
        except:
            # If summary fails, continue without it
            pass
            
        # Get alerts for the watchlist
        alerts = None
        try:
            alerts = api_client.get("/api/watchlist/alerts")
        except:
            # If alerts fetch fails, continue without them
            pass
            
        return templates.TemplateResponse(
            "watchlist.html", 
            {
                "request": request, 
                "user": current_user, 
                "watchlist": stocks_data, 
                "summary": summary,
                "alerts": alerts,
                "view": view
            }
        )
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return templates.TemplateResponse(
            "watchlist.html", 
            {
                "request": request, 
                "user": current_user, 
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
    current_user: dict = Depends(get_current_user)
):
    """Add a stock to the watchlist"""
    if not current_user:
        return JSONResponse(
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Add stock to watchlist
        data = {"ticker": ticker}
        if notes:
            data["notes"] = notes
            
        api_client.post("/api/watchlist/add", data=data)
            
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        error_message = "Failed to add stock to watchlist"
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.post("/watchlist/remove")
async def remove_from_watchlist(
    request: Request,
    ticker: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Remove a stock from the watchlist"""
    if not current_user:
        return JSONResponse(
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Remove stock from watchlist
        api_client.post("/api/watchlist/remove", data={"ticker": ticker})
            
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        error_message = "Failed to remove stock from watchlist"
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
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
    current_user: dict = Depends(get_current_user)
):
    """Set a price alert for a stock"""
    if not current_user:
        return JSONResponse(
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Set price alert
        api_client.post(
            "/api/watchlist/alert", 
            data={"ticker": ticker, "price": price, "direction": direction}
        )
            
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        error_message = "Failed to set price alert"
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.post("/watchlist/remove-alert")
async def remove_price_alert(
    request: Request,
    alert_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Remove a price alert"""
    if not current_user:
        return JSONResponse(
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Remove price alert
        api_client.post("/api/watchlist/alert/remove", data={"alert_id": alert_id})
            
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        error_message = "Failed to remove price alert"
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
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
    current_user: dict = Depends(get_current_user)
):
    """Update notes for a stock in the watchlist"""
    if not current_user:
        return JSONResponse(
            content={"success": False, "message": "Authentication required"},
            status_code=401
        )
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Update stock notes
        api_client.post(
            "/api/watchlist/update-notes",
            data={"ticker": ticker, "notes": notes}
        )
            
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        error_message = "Failed to update notes"
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )