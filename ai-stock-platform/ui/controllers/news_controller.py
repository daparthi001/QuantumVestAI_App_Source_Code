"""
News Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import logging
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional
from datetime import datetime

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)
logger = logging.getLogger("quantumvestai.news_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000/api/v1")
API_V1_URL = f"{API_URL}/api/v1"

# Demo news data
DEMO_NEWS = [
    {
        "id": 1,
        "title": "Tech Stocks Rally as AI Optimism Grows",
        "summary": "Major technology companies see significant gains as artificial intelligence adoption accelerates across industries.",
        "source": "MarketWatch",
        "published_at": "2025-07-07T20:30:00Z",
        "url": "#",
        "sentiment": "positive",
        "category": "market"
    },
    {
        "id": 2,
        "title": "Federal Reserve Maintains Interest Rates",
        "summary": "The Fed keeps rates steady at 5.25-5.50% as inflation shows signs of cooling while employment remains strong.",
        "source": "Reuters",
        "published_at": "2025-07-07T18:15:00Z", 
        "url": "#",
        "sentiment": "neutral",
        "category": "economy"
    },
    {
        "id": 3,
        "title": "EV Market Shows Strong Q2 Performance",
        "summary": "Electric vehicle sales surge 45% year-over-year as infrastructure improvements support adoption.",
        "source": "Bloomberg",
        "published_at": "2025-07-07T16:45:00Z",
        "url": "#",
        "sentiment": "positive",
        "category": "stocks"
    },
    {
        "id": 4,
        "title": "Cryptocurrency Market Volatility Continues",
        "summary": "Bitcoin and major altcoins experience significant price swings amid regulatory uncertainty.",
        "source": "CoinDesk",
        "published_at": "2025-07-07T14:20:00Z",
        "url": "#",
        "sentiment": "neutral",
        "category": "crypto"
    }
]

@router.get("/news", response_class=HTMLResponse)
async def news_page(
    request: Request,
    category: str = Query("market", regex="^(market|stocks|crypto|economy)$"),
    page: int = Query(1, ge=1)
):
    """Display news page (demo mode)"""
    try:
        # Filter news by category
        filtered_news = [article for article in DEMO_NEWS if article["category"] == category]
        
        # Pagination
        items_per_page = 10
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        paginated_news = filtered_news[start_index:end_index]
        
        # Calculate pagination info
        total_articles = len(filtered_news)
        total_pages = (total_articles + items_per_page - 1) // items_per_page
        
        news_data = {
            "articles": paginated_news,
            "category": category,
            "page": page,
            "total_pages": total_pages,
            "total_articles": total_articles,
            "trending": ["AI", "Federal Reserve", "EV Market", "Cryptocurrency"]
        }
        
        return get_templates(request).TemplateResponse(
            "news/index.html",
            {
                "request": request, 
                "data": news_data, 
                "user": None, 
                "demo_mode": True,
                "page_title": f"News - {category.title()} - QuantumVestAI"
            }
        )
    except Exception as e:
        logger.error(f"News page error: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request, 
                "error": str(e), 
                "user": None, 
                "demo_mode": True,
                "page_title": "News Error"
            },
            status_code=500
        )

@router.get("/news/article/{article_id}", response_class=HTMLResponse)
async def news_article(
    request: Request,
    article_id: str
):
    """Display specific news article (demo mode)"""
    try:
        # Find article by ID
        article = None
        for item in DEMO_NEWS:
            if str(item["id"]) == article_id:
                article = item
                break
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get related articles (same category)
        related_articles = [
            item for item in DEMO_NEWS 
            if item["category"] == article["category"] and item["id"] != article["id"]
        ][:3]  # Limit to 3 related articles
        
        article_data = {
            "article": article,
            "related": related_articles,
            "sentiment": {"status": "available", "score": 0.7, "label": "positive"}
        }
        
        return get_templates(request).TemplateResponse(
            "news/article.html",
            {
                "request": request, 
                "data": article_data, 
                "user": None, 
                "demo_mode": True,
                "page_title": f"{article['title']} - QuantumVestAI"
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"News article error for {article_id}: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request, 
                "error": str(e), 
                "user": None, 
                "demo_mode": True,
                "page_title": "Article Error"
            },
            status_code=500        )