"""
<<<<<<< HEAD
Dashboard routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Query, HTTPException, status
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

# Create router
router = APIRouter()

# Setup templates - use relative path from project root
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000/api/v1")

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    auth_cookie = request.cookies.get("access_token")
    return bool(auth_cookie)

def get_user_from_request(request: Request) -> Optional[Dict]:
    """Extract user info from request"""
    if is_authenticated(request):
        # In production, decode JWT token
        return {
            "username": "demo",
            "email": "demo@quantumvestai.com",
            "role": "user",
            "is_authenticated": True
        }
    return None

def get_demo_market_data() -> Dict[str, Any]:
    """Generate demo market data for UI display"""
    return {
        "major_indices": [
            {
                "symbol": "SPY",
                "name": "S&P 500",
                "price": 458.32,
                "change": 2.45,
                "change_percent": 0.54,
                "volume": "52.3M"
            },
            {
                "symbol": "QQQ", 
                "name": "NASDAQ 100",
                "price": 391.87,
                "change": -1.23,
                "change_percent": -0.31,
                "volume": "34.7M"
            },
            {
                "symbol": "IWM",
                "name": "Russell 2000", 
                "price": 198.45,
                "change": 0.87,
                "change_percent": 0.44,
                "volume": "18.9M"
            }
        ],
        "trending_stocks": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 182.31,
                "change": 1.87,
                "change_percent": 1.04,
                "market_cap": "2.85T"
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corp",
                "price": 378.85,
                "change": -2.15,
                "change_percent": -0.56,
                "market_cap": "2.81T"
            },
            {
                "symbol": "GOOGL",
                "name": "Alphabet Inc",
                "price": 142.56,
                "change": 3.42,
                "change_percent": 2.46,
                "market_cap": "1.78T"
            },
            {
                "symbol": "AMZN",
                "name": "Amazon.com Inc",
                "price": 153.32,
                "change": 0.95,
                "change_percent": 0.62,
                "market_cap": "1.59T"
            },
            {
                "symbol": "TSLA",
                "name": "Tesla Inc",
                "price": 238.45,
                "change": -4.67,
                "change_percent": -1.92,
                "market_cap": "758.2B"
            }
        ],
        "market_news": [
            {
                "title": "Federal Reserve Signals Potential Rate Cuts in 2025",
                "summary": "Fed officials indicate a more dovish stance on monetary policy amid economic uncertainty.",
                "timestamp": "2 hours ago",
                "source": "Reuters"
            },
            {
                "title": "Tech Earnings Season Begins with Mixed Results",
                "summary": "Major technology companies report quarterly earnings with varied performance.",
                "timestamp": "4 hours ago", 
                "source": "Bloomberg"
            },
            {
                "title": "AI Revolution Drives Market Optimism",
                "summary": "Artificial intelligence advancements fuel investor confidence in technology sector.",
                "timestamp": "6 hours ago",
                "source": "CNBC"
            }
        ]
    }

def get_demo_portfolio_data() -> Dict[str, Any]:
    """Generate demo portfolio data"""
    return {
        "total_value": 142850.75,
        "total_gain_loss": 17850.75,
        "total_gain_loss_percent": 14.28,
        "cash_balance": 12500.00,
        "positions": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "shares": 50,
                "avg_cost": 165.30,
                "current_price": 182.31,
                "market_value": 9115.50,
                "gain_loss": 850.50,
                "gain_loss_percent": 10.29
            },
            {
                "symbol": "MSFT", 
                "name": "Microsoft Corp",
                "shares": 25,
                "avg_cost": 342.15,
                "current_price": 378.85,
                "market_value": 9471.25,
                "gain_loss": 917.50,
                "gain_loss_percent": 10.71
            },
            {
                "symbol": "GOOGL",
                "name": "Alphabet Inc", 
                "shares": 30,
                "avg_cost": 125.80,
                "current_price": 142.56,
                "market_value": 4276.80,
                "gain_loss": 502.80,
                "gain_loss_percent": 13.31
            },
            {
                "symbol": "AMZN",
                "name": "Amazon.com Inc",
                "shares": 40,
                "avg_cost": 145.20,
                "current_price": 153.32,
                "market_value": 6132.80,
                "gain_loss": 324.80,
                "gain_loss_percent": 5.59
            }
        ],
        "watchlist": [
            {"symbol": "NVDA", "name": "NVIDIA Corp", "price": 875.42, "change_percent": 2.34},
            {"symbol": "META", "name": "Meta Platforms", "price": 511.24, "change_percent": -0.87},
            {"symbol": "NFLX", "name": "Netflix Inc", "price": 485.67, "change_percent": 1.56}
        ]
    }

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    try:
        # Check authentication
        if not is_authenticated(request):
            return RedirectResponse(
                url="/login?msg=Please log in to access your dashboard",
                status_code=status.HTTP_302_FOUND
            )
        
        user = get_user_from_request(request)
        market_data = get_demo_market_data()
        portfolio_data = get_demo_portfolio_data()
        
        # Calculate dashboard statistics
        dashboard_stats = {
            "total_accounts": 1,
            "total_positions": len(portfolio_data["positions"]),
            "watchlist_items": len(portfolio_data["watchlist"]),
            "alerts_count": 3,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        context = {
            "request": request,
            "user": user,
            "market_data": market_data,
            "portfolio": portfolio_data,
            "stats": dashboard_stats,
            "page_title": "Dashboard - QuantumVestAI",
            "active_page": "dashboard"
        }
        
        return templates.TemplateResponse("dashboard/index.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard Error - QuantumVestAI</title>
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
                                    <h2 class="card-title text-danger">Dashboard Unavailable</h2>
                                    <p class="card-text">We're experiencing technical difficulties loading your dashboard.</p>
                                    <div class="mt-3">
                                        <a href="/login" class="btn btn-primary">Return to Login</a>
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

@router.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request: Request):
    """Portfolio overview page"""
    try:
        # Check authentication
        if not is_authenticated(request):
            return RedirectResponse(
                url="/login?msg=Please log in to view your portfolio",
                status_code=status.HTTP_302_FOUND
            )
        
        user = get_user_from_request(request)
        portfolio_data = get_demo_portfolio_data()
        
        # Enhanced portfolio analytics
        portfolio_analytics = {
            "performance_1d": 0.85,
            "performance_1w": 2.34,
            "performance_1m": 5.67,
            "performance_3m": 12.45,
            "performance_ytd": 14.28,
            "beta": 1.12,
            "sharpe_ratio": 1.65,
            "volatility": 18.3,
            "max_drawdown": -8.7
        }
        
        # Sector allocation
        sector_allocation = [
            {"name": "Technology", "value": 65.4, "color": "#007bff"},
            {"name": "Consumer Discretionary", "value": 21.3, "color": "#28a745"},
            {"name": "Communication Services", "value": 13.3, "color": "#ffc107"}
        ]
        
        context = {
            "request": request,
            "user": user,
            "portfolio": portfolio_data,
            "analytics": portfolio_analytics,
            "sectors": sector_allocation,
            "page_title": "Portfolio - QuantumVestAI",
            "active_page": "portfolio"
        }
        
        return templates.TemplateResponse("dashboard/portfolio.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering portfolio page: {str(e)}")
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics and insights page"""
    try:
        # Check authentication
        if not is_authenticated(request):
            return RedirectResponse(
                url="/login?msg=Please log in to view analytics",
                status_code=status.HTTP_302_FOUND
            )
        
        user = get_user_from_request(request)
        
        # Demo analytics data
        analytics_data = {
            "ai_insights": [
                {
                    "type": "opportunity",
                    "title": "Technology Sector Momentum",
                    "description": "AI analysis suggests continued growth in tech stocks based on earnings patterns.",
                    "confidence": 87,
                    "timeframe": "3-6 months"
                },
                {
                    "type": "warning",
                    "title": "Market Volatility Alert",
                    "description": "Increased volatility expected due to upcoming Federal Reserve decisions.",
                    "confidence": 73,
                    "timeframe": "2-4 weeks"
                },
                {
                    "type": "recommendation",
                    "title": "Portfolio Rebalancing",
                    "description": "Consider reducing exposure to overweight positions in AAPL and MSFT.",
                    "confidence": 91,
                    "timeframe": "Immediate"
                }
            ],
            "risk_metrics": {
                "portfolio_risk_score": 6.8,
                "diversification_score": 7.2,
                "volatility_score": 6.5,
                "correlation_risk": 5.9
            },
            "performance_attribution": [
                {"factor": "Stock Selection", "contribution": 8.7},
                {"factor": "Sector Allocation", "contribution": 3.2},
                {"factor": "Market Timing", "contribution": 1.9},
                {"factor": "Other", "contribution": 0.5}
            ]
        }
        
        context = {
            "request": request,
            "user": user,
            "analytics": analytics_data,
            "page_title": "Analytics - QuantumVestAI",
            "active_page": "analytics"
        }
        
        return templates.TemplateResponse("dashboard/analytics.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering analytics page: {str(e)}")
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@router.get("/api/market-data")
async def get_market_data_api(request: Request):
    """API endpoint for real-time market data"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        market_data = get_demo_market_data()
        
        return JSONResponse(content={
            "success": True,
            "data": market_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market data"
=======
QuantumVestAI Dashboard Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import logging
from datetime import datetime
from pathlib import Path

# Setup router
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Demo data for market summary
DEMO_MARKET_DATA = {
    "indices": {
        "S&P 500": {"value": 4567.89, "change": 23.45, "change_pct": 0.52},
        "NASDAQ": {"value": 14234.56, "change": -45.67, "change_pct": -0.32},
        "DOW": {"value": 34567.12, "change": 156.78, "change_pct": 0.46}
    },
    "sectors": {
        "Technology": {"change_pct": 1.2, "leader": "AAPL"},
        "Healthcare": {"change_pct": -0.3, "leader": "JNJ"},
        "Finance": {"change_pct": 0.8, "leader": "JPM"},
        "Energy": {"change_pct": 2.1, "leader": "XOM"}
    },
    "top_movers": {
        "gainers": [
            {"symbol": "NVDA", "price": 245.67, "change_pct": 5.2},
            {"symbol": "TSLA", "price": 189.34, "change_pct": 3.8},
            {"symbol": "AMZN", "price": 145.23, "change_pct": 2.9}
        ],
        "losers": [
            {"symbol": "META", "price": 298.45, "change_pct": -2.1},
            {"symbol": "NFLX", "price": 423.67, "change_pct": -1.8},
            {"symbol": "GOOGL", "price": 134.56, "change_pct": -1.2}
        ]
    }
}

DEMO_STOCKS = [
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "price": 185.50,
        "change": 2.25,
        "change_pct": 1.23,
        "volume": "45.2M",
        "market_cap": "2.89T"
    },
    {
        "symbol": "MSFT", 
        "name": "Microsoft Corporation",
        "price": 365.25,
        "change": -1.75,
        "change_pct": -0.48,
        "volume": "28.7M",
        "market_cap": "2.71T"
    },
    {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "price": 134.56,
        "change": 3.42,
        "change_pct": 2.61,
        "volume": "32.1M", 
        "market_cap": "1.68T"
    },
    {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "price": 145.23,
        "change": 4.18,
        "change_pct": 2.96,
        "volume": "41.5M",
        "market_cap": "1.51T"
    },
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "price": 189.34,
        "change": 6.92,
        "change_pct": 3.79,
        "volume": "87.3M",
        "market_cap": "601.2B"
    }
]

DEMO_NEWS = [
    {
        "title": "Tech Stocks Rally as AI Optimism Grows",
        "summary": "Major technology companies see significant gains as artificial intelligence adoption accelerates across industries.",
        "source": "MarketWatch",
        "published_at": "2025-07-07T20:30:00Z",
        "url": "#",
        "sentiment": "positive"
    },
    {
        "title": "Federal Reserve Maintains Interest Rates",
        "summary": "The Fed keeps rates steady at 5.25-5.50% as inflation shows signs of cooling while employment remains strong.",
        "source": "Reuters",
        "published_at": "2025-07-07T18:15:00Z", 
        "url": "#",
        "sentiment": "neutral"
    },
    {
        "title": "EV Market Shows Strong Q2 Performance",
        "summary": "Electric vehicle sales surge 45% year-over-year as infrastructure improvements support adoption.",
        "source": "Bloomberg",
        "published_at": "2025-07-07T16:45:00Z",
        "url": "#",
        "sentiment": "positive"
    },
    {
        "title": "Energy Sector Leads Market Gains",
        "summary": "Oil and gas companies post strong earnings as crude prices stabilize above $75 per barrel.",
        "source": "CNBC",
        "published_at": "2025-07-07T14:20:00Z",
        "url": "#",
        "sentiment": "positive"
    }
]

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Render main dashboard page (demo mode)"""
    try:
        logger.info("Loading dashboard page in demo mode")
        
        # Get user info from request (demo mode)
        user = {
            "username": "demo",
            "email": "demo@quantumvestai.com", 
            "is_authenticated": True,
            "account_type": "Premium Demo",
            "features_enabled": {
                "advanced_analytics": True,
                "real_time_data": True,
                "portfolio_management": True,
                "ai_predictions": True
            }
        }
        
        # Demo watchlist
        watchlist_items = [
            {"symbol": "AAPL", "price": 185.50, "change_pct": 1.23, "alert_price": 180.00},
            {"symbol": "MSFT", "price": 365.25, "change_pct": -0.48, "alert_price": 370.00},
            {"symbol": "GOOGL", "price": 134.56, "change_pct": 2.61, "alert_price": 140.00}
        ]
        
        # Demo portfolio performance
        portfolio_data = {
            "total_value": 125750.45,
            "daily_change": 1234.56,
            "daily_change_pct": 0.99,
            "positions": 12,
            "cash_available": 15250.00
        }
        
        return templates.TemplateResponse(
            "dashboard/index.html",
            {
                "request": request,
                "user": user,
                "demo_mode": True,
                "market_summary": DEMO_MARKET_DATA,
                "popular_stocks": DEMO_STOCKS,
                "news": DEMO_NEWS,
                "watchlist": watchlist_items,
                "portfolio": portfolio_data,
                "page_title": "Dashboard - QuantumVestAI"
            }
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
        )

@router.get("/api/portfolio-data")
async def get_portfolio_data_api(request: Request):
    """API endpoint for portfolio data"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        portfolio_data = get_demo_portfolio_data()
        
        return JSONResponse(content={
            "success": True,
            "data": portfolio_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
<<<<<<< HEAD
        logger.error(f"Error fetching portfolio data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch portfolio data"
        )

@router.post("/api/add-to-watchlist")
async def add_to_watchlist(request: Request):
    """Add stock to user watchlist"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Parse request body
        body = await request.json()
        symbol = body.get("symbol", "").upper()
        
        if not symbol:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Stock symbol is required"
            )
        
        # In a real app, add to database
        logger.info(f"Adding {symbol} to watchlist (demo mode)")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Added {symbol} to your watchlist",
            "symbol": symbol
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add to watchlist"
        )

@router.delete("/api/remove-from-watchlist/{symbol}")
async def remove_from_watchlist(request: Request, symbol: str):
    """Remove stock from user watchlist"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        symbol = symbol.upper()
        
        # In a real app, remove from database
        logger.info(f"Removing {symbol} from watchlist (demo mode)")
        
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
=======
        logger.error(f"Error loading dashboard: {str(e)}")
        return templates.TemplateResponse(
            "dashboard/index.html",
            {
                "request": request,
                "user": None,
                "demo_mode": True,
                "market_summary": {"indices": {}, "sectors": {}, "top_movers": {}},
                "popular_stocks": [],
                "news": [],
                "watchlist": [],
                "portfolio": {},
                "error": f"Error loading dashboard: {str(e)}",
                "page_title": "Dashboard Error"
            },
            status_code=500
        )

@router.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request: Request):
    """Portfolio overview page"""
    try:
        # Demo portfolio data
        portfolio_data = {
            "total_value": 125750.45,
            "daily_change": 1234.56,
            "daily_change_pct": 0.99,
            "total_gain_loss": 8750.45,
            "total_gain_loss_pct": 7.48,
            "positions": [
                {
                    "symbol": "AAPL",
                    "shares": 50,
                    "avg_cost": 165.00,
                    "current_price": 185.50,
                    "market_value": 9275.00,
                    "gain_loss": 1025.00,
                    "gain_loss_pct": 12.42
                },
                {
                    "symbol": "MSFT", 
                    "shares": 25,
                    "avg_cost": 350.00,
                    "current_price": 365.25,
                    "market_value": 9131.25,
                    "gain_loss": 381.25,
                    "gain_loss_pct": 4.36
                },
                {
                    "symbol": "GOOGL",
                    "shares": 75,
                    "avg_cost": 125.00,
                    "current_price": 134.56,
                    "market_value": 10092.00,
                    "gain_loss": 717.00,
                    "gain_loss_pct": 7.65
                }
            ]
        }
        
        return templates.TemplateResponse(
            "dashboard/portfolio.html",
            {
                "request": request,
                "portfolio": portfolio_data,
                "demo_mode": True,
                "page_title": "Portfolio - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading portfolio page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load portfolio data",
                "page_title": "Portfolio Error"
            },
            status_code=500
        )

@router.get("/analytics", response_class=HTMLResponse) 
async def analytics_page(request: Request):
    """Advanced analytics page"""
    try:
        # Demo analytics data
        analytics_data = {
            "performance_metrics": {
                "sharpe_ratio": 1.45,
                "alpha": 0.08,
                "beta": 1.12,
                "max_drawdown": -5.2,
                "volatility": 12.8
            },
            "sector_allocation": {
                "Technology": 35.2,
                "Healthcare": 18.5,
                "Finance": 15.3,
                "Consumer": 12.7,
                "Energy": 8.9,
                "Other": 9.4
            },
            "risk_metrics": {
                "var_95": -2.3,
                "var_99": -4.1,
                "correlation_sp500": 0.85
            }
        }
        
        return templates.TemplateResponse(
            "dashboard/analytics.html",
            {
                "request": request,
                "analytics": analytics_data,
                "demo_mode": True,
                "page_title": "Analytics - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading analytics page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load analytics data",
                "page_title": "Analytics Error"
            },
            status_code=500
        )

@router.get("/api/summary")
async def dashboard_api_summary(request: Request):
    """API endpoint for dashboard summary data"""
    try:
        return {
            "status": "success",
            "data": {
                "market_summary": DEMO_MARKET_DATA,
                "portfolio": {
                    "total_value": 125750.45,
                    "daily_change": 1234.56,
                    "daily_change_pct": 0.99
                },
                "alerts": [
                    {"type": "price", "symbol": "AAPL", "message": "AAPL reached target price of $185"},
                    {"type": "news", "symbol": "TSLA", "message": "Positive earnings report released"}
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
