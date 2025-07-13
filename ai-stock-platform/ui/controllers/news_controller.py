"""
News Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)
logger = logging.getLogger("quantumvestai.news_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

# Demo news data removed
DEMO_NEWS = []

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
