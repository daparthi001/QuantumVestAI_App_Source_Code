"""
QuantumVestAI Watchlist Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from core.config import settings

# Setup router
router = APIRouter(prefix="/watchlist", tags=["watchlist"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# Demo watchlist data removed
DEMO_WATCHLIST = []

# Demo portfolio data removed
DEMO_PORTFOLIO = {}

@router.get("/", response_class=HTMLResponse)
async def watchlist_page(request: Request, view: str = "grid"):
    """Render watchlist page (demo mode)"""
    try:
        logger.info("Loading watchlist page in demo mode")
        
        # Calculate watchlist summary
        watchlist_summary = {
            "total_stocks": len(DEMO_WATCHLIST),
            "total_value": sum([item["price"] * 10 for item in DEMO_WATCHLIST]),  # Assume 10 shares each
            "gainers": len([item for item in DEMO_WATCHLIST if item["change_pct"] > 0]),
            "losers": len([item for item in DEMO_WATCHLIST if item["change_pct"] < 0]),
            "alerts_triggered": 2
        }
        
        return get_templates(request).TemplateResponse(
            "watchlist.html",
            {
                "request": request,
                "demo_mode": settings.DEMO_MODE,
                "watchlist": DEMO_WATCHLIST,
                "portfolio": DEMO_PORTFOLIO,
                "summary": watchlist_summary,
                "view": view,
                "page_title": "Watchlist - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading watchlist: {str(e)}")
        return get_templates(request).TemplateResponse(
            "watchlist.html",
            {
                "request": request,
                "demo_mode": settings.DEMO_MODE,
                "watchlist": [],
                "portfolio": {},
                "summary": {},
                "view": view,
                "error": f"Error loading watchlist: {str(e)}",
                "page_title": "Watchlist Error"
            },
            status_code=500
        )

@router.post("/add")
async def add_to_watchlist(
    request: Request,
    ticker: str = Form(...),
    notes: Optional[str] = Form(None),
    alert_price: Optional[float] = Form(None),
    alert_type: str = Form("above")
):
    """Add stock to watchlist (demo mode)"""
    try:
        ticker = ticker.upper()
        logger.info(f"Adding {ticker} to watchlist in demo mode")
        
        # Check if already in watchlist
        existing = next((item for item in DEMO_WATCHLIST if item["symbol"] == ticker), None)
        if existing:
            return JSONResponse({
                "status": "error",
                "message": f"{ticker} is already in your watchlist"
            }, status_code=400)
        
        # Create new watchlist item
        new_item = {
            "id": max([item["id"] for item in DEMO_WATCHLIST], default=0) + 1,
            "symbol": ticker,
            "name": f"{ticker} Corporation",  # Would normally fetch from API
            "price": 100.00,  # Demo price
            "change": 1.50,
            "change_pct": 1.52,
            "volume": "10.5M",
            "market_cap": "500.0B",
            "added_date": datetime.now().strftime("%Y-%m-%d"),
            "notes": notes or "",
            "alert_price": alert_price,
            "alert_type": alert_type
        }
        
        # Add to demo watchlist (in production, this would save to database)
        DEMO_WATCHLIST.append(new_item)
        
        return JSONResponse({
            "status": "success",
            "message": f"{ticker} added to watchlist successfully",
            "item": new_item
        })
        
    except Exception as e:
        logger.error(f"Error adding to watchlist: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@router.post("/remove")
async def remove_from_watchlist(
    request: Request,
    ticker: str = Form(...)
):
    """Remove stock from watchlist (demo mode)"""
    try:
        ticker = ticker.upper()
        logger.info(f"Removing {ticker} from watchlist in demo mode")
        
        # Find and remove item
        original_length = len(DEMO_WATCHLIST)
        
        # Filter out the item to remove
        updated_watchlist = [item for item in DEMO_WATCHLIST if item["symbol"] != ticker]
        
        if len(updated_watchlist) == original_length:
            return JSONResponse({
                "status": "error",
                "message": f"{ticker} not found in watchlist"
            }, status_code=404)
        
        # Update the global list
        DEMO_WATCHLIST.clear()
        DEMO_WATCHLIST.extend(updated_watchlist)
        
        return JSONResponse({
            "status": "success",
            "message": f"{ticker} removed from watchlist successfully"
        })
        
    except Exception as e:
        logger.error(f"Error removing from watchlist: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@router.post("/set-alert")
async def set_price_alert(
    request: Request,
    ticker: str = Form(...),
    alert_price: float = Form(...),
    alert_type: str = Form("above")
):
    """Set price alert for watchlist item (demo mode)"""
    try:
        ticker = ticker.upper()
        logger.info(f"Setting alert for {ticker} at ${alert_price} ({alert_type}) in demo mode")
        
        # Find and update item
        item = next((item for item in DEMO_WATCHLIST if item["symbol"] == ticker), None)
        if not item:
            return JSONResponse({
                "status": "error",
                "message": f"{ticker} not found in watchlist"
            }, status_code=404)
        
        # Update alert settings
        item["alert_price"] = alert_price
        item["alert_type"] = alert_type
        
        return JSONResponse({
            "status": "success",
            "message": f"Alert set for {ticker} at ${alert_price} ({alert_type})"
        })
        
    except Exception as e:
        logger.error(f"Error setting alert: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@router.post("/update-notes")
async def update_notes(
    request: Request,
    ticker: str = Form(...),
    notes: str = Form(...)
):
    """Update notes for watchlist item (demo mode)"""
    try:
        ticker = ticker.upper()
        logger.info(f"Updating notes for {ticker} in demo mode")
        
        # Find and update item
        item = next((item for item in DEMO_WATCHLIST if item["symbol"] == ticker), None)
        if not item:
            return JSONResponse({
                "status": "error",
                "message": f"{ticker} not found in watchlist"
            }, status_code=404)
        
        # Update notes
        item["notes"] = notes
        
        return JSONResponse({
            "status": "success",
            "message": f"Notes updated for {ticker}"
        })
        
    except Exception as e:
        logger.error(f"Error updating notes: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@router.get("/data", response_class=JSONResponse)
async def get_watchlist_data(request: Request):
    """Get watchlist data (demo mode)"""
    try:
        return JSONResponse({
            "status": "success",
            "watchlist": DEMO_WATCHLIST,
            "portfolio": DEMO_PORTFOLIO,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting watchlist data: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)

@router.post("/reorder")
async def reorder_watchlist(request: Request):
    """Reorder watchlist items (demo mode)"""
    try:
        # In a real implementation, this would update the order in the database
        # For demo, we'll just return success
        return JSONResponse({
            "status": "success",
            "message": "Watchlist order updated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error reordering watchlist: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@router.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request: Request):
    """Portfolio management page"""
    try:
        # Calculate portfolio metrics
        portfolio_metrics = {
            "total_return": (DEMO_PORTFOLIO["total_gain_loss"] / (DEMO_PORTFOLIO["total_value"] - DEMO_PORTFOLIO["total_gain_loss"])) * 100,
            "best_performer": max(DEMO_PORTFOLIO["positions"], key=lambda x: x["gain_loss_pct"]),
            "worst_performer": min(DEMO_PORTFOLIO["positions"], key=lambda x: x["gain_loss_pct"]),
            "sector_allocation": {
                "Technology": 60.2,
                "Healthcare": 15.8,
                "Finance": 12.5,
                "Energy": 8.1,
                "Other": 3.4
            }
        }
        
        return get_templates(request).TemplateResponse(
            "portfolio.html",
            {
                "request": request,
                "demo_mode": settings.DEMO_MODE,
                "portfolio": DEMO_PORTFOLIO,
                "metrics": portfolio_metrics,
                "page_title": "Portfolio - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading portfolio page: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load portfolio data",
                "page_title": "Portfolio Error"
            },
            status_code=500
        )

@router.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    """Price alerts page"""
    try:
        # Demo alerts
        active_alerts = [
            {
                "symbol": "AAPL",
                "alert_price": 180.00,
                "current_price": 185.50,
                "alert_type": "above",
                "status": "triggered",
                "created_date": "2025-07-01"
            },
            {
                "symbol": "MSFT",
                "alert_price": 370.00,
                "current_price": 365.25,
                "alert_type": "above",
                "status": "active",
                "created_date": "2025-06-28"
            }
        ]
        
        return get_templates(request).TemplateResponse(
            "alerts.html",
            {
                "request": request,
                "demo_mode": settings.DEMO_MODE,
                "alerts": active_alerts,
                "page_title": "Price Alerts - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading alerts page: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load alerts data",
                "page_title": "Alerts Error"
            },
            status_code=500        )
