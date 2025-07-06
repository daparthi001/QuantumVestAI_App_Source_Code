from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from routes.auth import get_current_user
from services.api_client import APIClient
from services.yahoo_finance import YahooFinanceService
from config.settings import settings

API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["dashboard"])

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Render dashboard page"""
    try:
        # Create API client with auth token if available
        token = request.cookies.get("token") if current_user else None
        api_client = APIClient(token=token)
        
        # Get market summary
        market_summary = YahooFinanceService.get_market_summary()
        
        # Get popular stocks
        popular_stocks = [
            YahooFinanceService.get_stock_info(ticker) 
            for ticker in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        ]
        
        # Get news
        news_items = []
        for ticker in ["AAPL", "MSFT", "GOOGL"]:
            try:
                news = YahooFinanceService.get_stock_news(ticker, limit=2)
                news_items.extend(news)
            except:
                continue
                
        # Sort news by published date (newest first)
        news_items = sorted(
            news_items, 
            key=lambda x: x.get("published_at", ""), 
            reverse=True
        )[:6]
        
        # Get personalized data if user is logged in
        personalized_data = {}
        watchlist_items = []
        if current_user:
            try:
                # Get personalized analytics
                personalized_data = api_client.get("/api/users/analytics")
                
                # Get watchlist items
                watchlist = api_client.get("/api/watchlist")
                if watchlist:
                    for item in watchlist[:5]:  # Get first 5 items
                        ticker = item["ticker"]
                        try:
                            stock_info = YahooFinanceService.get_stock_info(ticker)
                            watchlist_items.append({
                                **item,
                                "info": stock_info
                            })
                        except:
                            continue
            except:
                pass
        
        return templates.TemplateResponse(
            "dashboard/index.html", 
            {
                "request": request,
                "user": current_user,
                "market_summary": market_summary,
                "popular_stocks": popular_stocks,
                "news": news_items,
                "personalized_data": personalized_data,
                "watchlist": watchlist_items
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
            "dashboard/index.html", 
            {
                "request": request,
                "user": current_user,
                "market_summary": {"indices": {}, "sectors": {}, "top_movers": {}},
                "popular_stocks": [],
                "news": [],
                "personalized_data": {},
                "watchlist": [],
                "error": error_message
            }
        )