"""
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


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

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
        
        return get_templates(request).TemplateResponse(
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
        )
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return get_templates(request).TemplateResponse(
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
        
        return get_templates(request).TemplateResponse(
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
        return get_templates(request).TemplateResponse(
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
        
        return get_templates(request).TemplateResponse(
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
        return get_templates(request).TemplateResponse(
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
