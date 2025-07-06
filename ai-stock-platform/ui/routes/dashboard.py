from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
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
    
):
    """Render dashboard page"""
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
                            continue
            except:
                pass
        
        return templates.TemplateResponse(
            "dashboard/index.html", 
            {
                "request": request,
                "user": None,
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
                pass
                
        return templates.TemplateResponse(
            "dashboard/index.html", 
            {
                "request": request,
                "user": None,
                "market_summary": {"indices": {}, "sectors": {}, "top_movers": {}},
                "popular_stocks": [],
                "news": [],
                "personalized_data": {},
                "watchlist": [],
                "error": error_message
            }
        )