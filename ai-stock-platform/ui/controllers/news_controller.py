"""
News Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from core.config import get_settings

import httpx

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
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
API_V1_URL = f"{API_URL}/api/v1"

# External news API configuration
NEWS_API_URL = os.environ.get("NEWS_API_URL", "https://newsapi.org/v2/top-headlines")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

settings = get_settings()

# Simple in-memory cache for fetched news
_NEWS_CACHE: Dict[str, Dict[str, Any]] = {}


async def fetch_news(category: str, page: int = 1, ttl: int = 600) -> Dict[str, Any]:
    """Fetch news articles from the external API with basic caching.

    Falls back to demo news when the external API isn't configured so that the
    `/news` page can still render without errors.
    """
    cache_key = f"{category}_{page}"
    cached = _NEWS_CACHE.get(cache_key)
    now = datetime.utcnow()
    if cached and cached["expires"] > now:
        return cached["data"]

    # Require NEWS_API_KEY to be configured - no demo fallback
    if not NEWS_API_KEY:
        logger.error("NEWS_API_KEY not configured - news service unavailable")
        raise httpx.HTTPStatusError(
            "News API key not configured",
            request=None,
            response=httpx.Response(503)
        )

    params = {"apiKey": NEWS_API_KEY, "page": page, "pageSize": 10}
    if category != "market":
        params["category"] = category

    async with httpx.AsyncClient() as client:
        resp = await client.get(NEWS_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    _NEWS_CACHE[cache_key] = {"data": data, "expires": now + timedelta(seconds=ttl)}
    return data


@router.get("/news", response_class=HTMLResponse)
async def news_page(
    request: Request,
    category: str = Query("market", regex="^(market|stocks|crypto|economy)$"),
    page: int = Query(1, ge=1),
):
    """Display news page using live data."""
    try:
        data = await fetch_news(category, page)

        articles = []
        for idx, art in enumerate(data.get("articles", [])):
            source = art.get("source")
            if isinstance(source, dict):
                source = source.get("name")
            summary = art.get("description") or art.get("summary")
            published = art.get("publishedAt") or art.get("timestamp")

            articles.append(
                {
                    "id": idx,
                    "title": art.get("title"),
                    "summary": summary,
                    "source": source,
                    "published_at": published,
                    "category": category,
                    "sentiment": "neutral",
                }
            )

        news_data = {
            "articles": articles,
            "category": category,
            "page": page,
            "total_pages": 1,
            "total_articles": data.get("totalResults", 0),
            "trending": [],
        }

        return get_templates(request).TemplateResponse(
            "news/index.html",
            {
                "request": request,
                "data": news_data,
                "user": None,
                "page_title": f"News - {category.title()} - QuantumVestAI",
            },
        )
    except Exception as e:
        detail = getattr(e, "detail", str(e))
        logger.error(f"News page error: {detail}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": str(e),
                "user": None,
                "page_title": "News Error",
            },
            status_code=500,
        )


@router.get("/news/article/{article_id}", response_class=HTMLResponse)
async def news_article(
    request: Request,
    article_id: int,
    category: str = Query("market", regex="^(market|stocks|crypto|economy)$"),
    page: int = Query(1, ge=1),
):
    """Display a single news article retrieved from the external API."""
    try:
        data = await fetch_news(category, page)
        articles = data.get("articles", [])
        if article_id < 0 or article_id >= len(articles):
            raise HTTPException(status_code=404, detail="Article not found")

        article = articles[article_id]
        article_data = {
            "article": {
                "id": article_id,
                "title": article.get("title"),
                "summary": article.get("description"),
                "source": article.get("source", {}).get("name"),
                "published_at": article.get("publishedAt"),
                "category": category,
                "sentiment": "neutral",
            },
            "related": [],
            "sentiment": {"status": "unavailable"},
        }

        return get_templates(request).TemplateResponse(
            "news/article.html",
            {
                "request": request,
                "data": article_data,
                "user": None,
                "page_title": f"{article.get('title')} - QuantumVestAI",
            },
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        detail = getattr(e, "detail", str(e))
        logger.error(f"News article error for {article_id}: {detail}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": str(e),
                "user": None,
                "page_title": "Article Error",
            },
            status_code=500,
        )
