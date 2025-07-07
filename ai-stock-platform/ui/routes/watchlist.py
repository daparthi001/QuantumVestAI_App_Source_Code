"""
Watchlist management routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Form, Query, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import requests
import os
from datetime import datetime, timedelta
import json

# Setup logging
logger = logging.getLogger(__name__)

# Setup templates - use relative path from project root
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000/api/v1")

# Create router
router = APIRouter(tags=["watchlist"])

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    auth_cookie = request.cookies.get("access_token")
    return bool(auth_cookie)

def get_user_from_request(request: Request) -> Optional[Dict]:
    """Extract user info from request"""
    if is_authenticated(request):
        return {
            "username": "demo",
            "email": "demo@quantumvestai.com",
            "role": "user",
            "is_authenticated": True
        }
    return None

def get_demo_watchlist_data() -> List[Dict[str, Any]]:
    """Generate demo watchlist data"""
    return [
        {
            "id": 1,
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "current_price": 182.31,
            "change": 1.87,
            "change_percent": 1.04,
            "target_price": 195.00,
            "target_reached": False,
            "alert_enabled": True,
            "added_date": "2025-01-01",
            "added_price": 175.20,
            "gain_loss_percent": 4.06,
            "market_cap": "2.85T",
            "pe_ratio": 28.45,
            "dividend_yield": 0.46,
            "volume": "45.2M",
            "avg_volume": "52.3M",
            "notes": "Strong Q4 earnings expected"
        },
        {
            "id": 2,
            "symbol": "MSFT",
            "name": "Microsoft Corp",
            "current_price": 378.85,
            "change": -2.15,
            "change_percent": -0.56,
            "target_price": 400.00,
            "target_reached": False,
            "alert_enabled": True,
            "added_date": "2024-12-15",
            "added_price": 365.40,
            "gain_loss_percent": 3.68,
            "market_cap": "2.81T",
            "pe_ratio": 32.12,
            "dividend_yield": 0.73,
            "volume": "28.7M",
            "avg_volume": "31.5M",
            "notes": "Cloud growth driving revenue"
        },
        {
            "id": 3,
            "symbol": "GOOGL",
            "name": "Alphabet Inc",
            "current_price": 142.56,
            "change": 3.42,
            "change_percent": 2.46,
            "target_price": 160.00,
            "target_reached": False,
            "alert_enabled": False,
            "added_date": "2024-11-20",
            "added_price": 135.80,
            "gain_loss_percent": 4.98,
            "market_cap": "1.78T",
            "pe_ratio": 24.67,
            "dividend_yield": 0.00,
            "volume": "32.1M",
            "avg_volume": "28.9M",
            "notes": "AI initiatives showing promise"
        },
        {
            "id": 4,
            "symbol": "NVDA",
            "name": "NVIDIA Corp",
            "current_price": 875.42,
            "change": 42.87,
            "change_percent": 5.15,
            "target_price": 1000.00,
            "target_reached": False,
            "alert_enabled": True,
            "added_date": "2024-10-10",
            "added_price": 720.50,
            "gain_loss_percent": 21.51,
            "market_cap": "2.16T",
            "pe_ratio": 74.23,
            "dividend_yield": 0.03,
            "volume": "67.8M",
            "avg_volume": "45.2M",
            "notes": "AI chip demand remains strong"
        },
        {
            "id": 5,
            "symbol": "TSLA",
            "name": "Tesla Inc",
            "current_price": 238.45,
            "change": -4.67,
            "change_percent": -1.92,
            "target_price": 280.00,
            "target_reached": False,
            "alert_enabled": True,
            "added_date": "2024-09-05",
            "added_price": 245.30,
            "gain_loss_percent": -2.79,
            "market_cap": "758.2B",
            "pe_ratio": 65.18,
            "dividend_yield": 0.00,
            "volume": "89.4M",
            "avg_volume": "72.1M",
            "notes": "Robotaxi launch approaching"
        }
    ]

def get_demo_watchlist_analytics() -> Dict[str, Any]:
    """Generate demo watchlist analytics"""
    watchlist = get_demo_watchlist_data()
    
    total_value = sum(item["current_price"] * 10 for item in watchlist)  # Assume 10 shares each
    total_gain_loss = sum((item["current_price"] - item["added_price"]) * 10 for item in watchlist)
    avg_gain_loss_percent = sum(item["gain_loss_percent"] for item in watchlist) / len(watchlist)
    
    winners = [item for item in watchlist if item["gain_loss_percent"] > 0]
    losers = [item for item in watchlist if item["gain_loss_percent"] < 0]
    
    return {
        "total_symbols": len(watchlist),
        "total_value": total_value,
        "total_gain_loss": total_gain_loss,
        "avg_gain_loss_percent": avg_gain_loss_percent,
        "winners_count": len(winners),
        "losers_count": len(losers),
        "alerts_enabled": len([item for item in watchlist if item["alert_enabled"]]),
        "targets_reached": len([item for item in watchlist if item["target_reached"]]),
        "best_performer": max(watchlist, key=lambda x: x["gain_loss_percent"]),
        "worst_performer": min(watchlist, key=lambda x: x["gain_loss_percent"])
    }

@router.get("/", response_class=HTMLResponse)
async def watchlist_page(request: Request):
    """Main watchlist page"""
    try:
        # Check authentication
        if not is_authenticated(request):
            return RedirectResponse(
                url="/login?msg=Please log in to view your watchlist",
                status_code=status.HTTP_302_FOUND
            )
        
        user = get_user_from_request(request)
        watchlist_data = get_demo_watchlist_data()
        analytics = get_demo_watchlist_analytics()
        
        # Recent alerts (demo data)
        recent_alerts = [
            {
                "symbol": "NVDA",
                "type": "price_target",
                "message": "NVDA approaching target price of $1000.00",
                "timestamp": "2 hours ago",
                "status": "active"
            },
            {
                "symbol": "AAPL", 
                "type": "price_change",
                "message": "AAPL up 1.87 (+1.04%) today",
                "timestamp": "4 hours ago",
                "status": "triggered"
            },
            {
                "symbol": "TSLA",
                "type": "volume_spike",
                "message": "TSLA volume 24% above average",
                "timestamp": "1 day ago",
                "status": "triggered"
            }
        ]
        
        context = {
            "request": request,
            "user": user,
            "watchlist": watchlist_data,
            "analytics": analytics,
            "alerts": recent_alerts,
            "page_title": "Watchlist - QuantumVestAI",
            "active_page": "watchlist"
        }
        
        return templates.TemplateResponse("watchlist/index.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering watchlist page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Watchlist Error - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h2 class="card-title text-danger">Watchlist Unavailable</h2>
                                    <p class="card-text">We're experiencing technical difficulties loading your watchlist.</p>
                                    <div class="mt-3">
                                        <a href="/dashboard" class="btn btn-primary">Return to Dashboard</a>
                                        <a href="/" class="btn btn-secondary">Go Home</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )

@router.post("/add")
async def add_to_watchlist(
    request: Request,
    symbol: str = Form(...),
    target_price: Optional[float] = Form(None),
    notes: Optional[str] = Form("")
):
    """Add stock to watchlist"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Validate input
        symbol = symbol.upper().strip()
        if not symbol or len(symbol) > 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid stock symbol"
            )
        
        # Check if already in watchlist
        watchlist = get_demo_watchlist_data()
        if any(item["symbol"] == symbol for item in watchlist):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{symbol} is already in your watchlist"
            )
        
        # Simulate adding to database
        new_item = {
            "id": len(watchlist) + 1,
            "symbol": symbol,
            "name": f"{symbol} Corp",  # In real app, fetch from API
            "current_price": 150.00 + len(symbol),  # Mock price
            "target_price": target_price,
            "alert_enabled": bool(target_price),
            "added_date": datetime.now().strftime("%Y-%m-%d"),
            "added_price": 150.00 + len(symbol),
            "notes": notes.strip() if notes else ""
        }
        
        logger.info(f"Added {symbol} to watchlist (demo mode)")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Added {symbol} to your watchlist",
            "data": new_item
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add to watchlist"
        )

@router.delete("/remove/{symbol}")
async def remove_from_watchlist(request: Request, symbol: str):
    """Remove stock from watchlist"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        symbol = symbol.upper().strip()
        
        # Check if in watchlist
        watchlist = get_demo_watchlist_data()
        if not any(item["symbol"] == symbol for item in watchlist):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{symbol} not found in watchlist"
            )
        
        logger.info(f"Removed {symbol} from watchlist (demo mode)")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Removed {symbol} from your watchlist",
            "symbol": symbol
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove from watchlist"
        )

@router.put("/update/{symbol}")
async def update_watchlist_item(
    request: Request,
    symbol: str,
    target_price: Optional[float] = Form(None),
    alert_enabled: bool = Form(False),
    notes: Optional[str] = Form("")
):
    """Update watchlist item settings"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        symbol = symbol.upper().strip()
        
        # Validate target price
        if target_price is not None and target_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Target price must be positive"
            )
        
        # Simulate update
        logger.info(f"Updated watchlist settings for {symbol} (demo mode)")
        
        updated_data = {
            "symbol": symbol,
            "target_price": target_price,
            "alert_enabled": alert_enabled,
            "notes": notes.strip() if notes else "",
            "updated_at": datetime.now().isoformat()
        }
        
        return JSONResponse(content={
            "success": True,
            "message": f"Updated settings for {symbol}",
            "data": updated_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating watchlist item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update watchlist item"
        )

@router.get("/api/data")
async def get_watchlist_data(request: Request):
    """API endpoint for watchlist data"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        watchlist_data = get_demo_watchlist_data()
        analytics = get_demo_watchlist_analytics()
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "watchlist": watchlist_data,
                "analytics": analytics
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching watchlist data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch watchlist data"
        )

@router.post("/reorder")
async def reorder_watchlist(request: Request):
    """Reorder watchlist items"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Parse request body
        body = await request.json()
        order = body.get("order", [])
        
        if not isinstance(order, list):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Order must be an array of symbol IDs"
            )
        
        logger.info(f"Reordered watchlist: {order} (demo mode)")
        
        return JSONResponse(content={
            "success": True,
            "message": "Watchlist reordered successfully",
            "order": order
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering watchlist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder watchlist"
        )

@router.get("/api/alerts")
async def get_watchlist_alerts(request: Request):
    """Get watchlist alerts"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Demo alerts
        alerts = [
            {
                "id": 1,
                "symbol": "NVDA",
                "type": "price_target",
                "condition": "price >= 1000.00",
                "current_value": 875.42,
                "target_value": 1000.00,
                "triggered": False,
                "created_at": "2025-01-01T10:00:00Z"
            },
            {
                "id": 2,
                "symbol": "AAPL",
                "type": "price_change",
                "condition": "daily_change > 2%",
                "current_value": 1.04,
                "target_value": 2.0,
                "triggered": False,
                "created_at": "2025-01-01T10:00:00Z"
            },
            {
                "id": 3,
                "symbol": "TSLA",
                "type": "volume_spike",
                "condition": "volume > 1.5x average",
                "current_value": 1.24,
                "target_value": 1.5,
                "triggered": False,
                "created_at": "2025-01-01T10:00:00Z"
            }
        ]
        
        return JSONResponse(content={
            "success": True,
            "data": alerts,
            "count": len(alerts),
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alerts"
        )

@router.post("/import")
async def import_watchlist(request: Request):
    """Import watchlist from CSV or other formats"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Parse request body
        body = await request.json()
        symbols = body.get("symbols", [])
        
        if not isinstance(symbols, list) or len(symbols) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Symbols array is required"
            )
        
        # Validate symbols
        valid_symbols = []
        for symbol in symbols:
            if isinstance(symbol, str) and len(symbol.strip()) <= 10:
                valid_symbols.append(symbol.upper().strip())
        
        if not valid_symbols:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No valid symbols provided"
            )
        
        logger.info(f"Imported {len(valid_symbols)} symbols to watchlist (demo mode)")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Imported {len(valid_symbols)} symbols to watchlist",
            "imported_symbols": valid_symbols,
            "count": len(valid_symbols)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing watchlist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to import watchlist"
        )