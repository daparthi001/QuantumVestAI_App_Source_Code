"""
QuantumVestAI Dashboard Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from core.config.settings import settings
from services.yahoo_finance import YahooFinanceService
from services.trending_stocks_service import TrendingStocksService
from services.api_client import APIClient

# Setup router
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)


# No demo/mock data - only live data from Alpha Vantage and RapidAPI


@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Render main dashboard page"""
    try:
        token = request.cookies.get("access_token")
        api = APIClient(token=token) if token else None
        user = api.get("/users/me") if api else None
        subscribed = bool(user and user.get("role") != "free")
        watchlist_items: List[str] = []
        portfolio_data: dict = {}

        # Always use live data from Alpha Vantage and RapidAPI
        market_summary = YahooFinanceService.get_market_summary()
        popular_stocks = []
        news = []

        try:
            trending = await TrendingStocksService().get_trending_stocks(limit=5)
            popular_stocks = trending.get("stocks", [])
            for stock in popular_stocks:
                try:
                    symbol = stock.get("symbol") or stock.get("ticker")
                    if symbol and api:
                        pred = api.get(f"/predictions/{symbol}")
                        price = (
                            pred.get("data", {})
                            .get("predictions", [{}])[0]
                            .get("predicted_price")
                        )
                        if price is not None:
                            stock["prediction"] = price
                except Exception as exc:  # pragma: no cover
                    logger.warning(f"Prediction fetch failed for {symbol}: {exc}")
        except Exception as ex:  # pragma: no cover - network errors
            logger.warning(f"Trending stocks fetch failed: {ex}")
            # Don't fallback to demo data, just log the error

        return get_templates(request).TemplateResponse(
            "dashboard/index.html",
            {
                "request": request,
                "user": user,
                "market_summary": market_summary,
                "popular_stocks": popular_stocks,
                "news": news,
                "watchlist": watchlist_items,
                "portfolio": portfolio_data,
                "page_title": "Dashboard - QuantumVestAI",
            },
        )

    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return get_templates(request).TemplateResponse(
            "dashboard/index.html",
            {
                "request": request,
                "user": None,
                "market_summary": {"indices": {}, "sectors": {}, "top_movers": {}},
                "popular_stocks": [],
                "news": [],
                "watchlist": [],
                "portfolio": {},
                "error": f"Error loading dashboard: {str(e)}",
                "page_title": "Dashboard Error",
            },
            status_code=500,
        )


@router.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request: Request):
    """Portfolio overview page"""
    try:
        # Provide default empty portfolio structure to avoid template errors
        portfolio_data = {
            "total_value": 0,
            "daily_change": 0,
            "total_gain_loss": 0,
            "total_gain_loss_pct": 0,

            "positions": [],
        }

        templates_obj = get_templates(request)
        # Ensure template filters are registered so function calls don't fail
        try:  # pragma: no cover - defensive
            from ui.utils import template_filters

            template_filters.register_filters(request.app)
        except Exception:  # pragma: no cover
            pass

        return templates_obj.TemplateResponse(
            "dashboard/portfolio.html",
            {
                "request": request,
                "portfolio": portfolio_data,
                "page_title": "Portfolio - QuantumVestAI",
            },
        )

    except Exception as e:
        logger.error(f"Error loading portfolio page: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load portfolio data",
                "page_title": "Portfolio Error",
            },
            status_code=500,
        )


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Advanced analytics page"""
    try:
        # Demo analytics data removed
        analytics_data = {}

        return get_templates(request).TemplateResponse(
            "dashboard/analytics.html",
            {
                "request": request,
                "analytics": analytics_data,
                "page_title": "Analytics - QuantumVestAI",
            },
        )

    except Exception as e:
        logger.error(f"Error loading analytics page: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load analytics data",
                "page_title": "Analytics Error",
            },
            status_code=500,
        )


@router.get("/api/summary")
async def dashboard_api_summary(request: Request):
    """API endpoint for dashboard summary data"""
    try:
        token = request.cookies.get("access_token")
        api = APIClient(token=token) if token else None
        if not api:
            data = {}
        else:
            data = YahooFinanceService.get_market_summary()
            trending = await TrendingStocksService().get_trending_stocks(limit=5)
            stocks = trending.get("stocks", [])
            for stock in stocks:
                symbol = stock.get("symbol") or stock.get("ticker")
                if symbol:
                    pred = api.get(f"/predictions/{symbol}")
                    price = (
                        pred.get("data", {})
                        .get("predictions", [{}])[0]
                        .get("predicted_price")
                        if pred
                        else None
                    )
                    if price is not None:
                        stock["prediction"] = price
            data["trending"] = stocks
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
