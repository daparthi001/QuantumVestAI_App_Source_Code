"""
News Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.news_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000/api/v1")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/news", response_class=HTMLResponse)
async def news_page(
    request: Request,
    category: str = Query("market", regex="^(market|stocks|crypto|economy)$"),
    page: int = Query(1, ge=1)
):
    """Display news page (demo mode)"""
    try:
        news_data = {
            "category": category,
            "page": page
        }
        
        # Demo mode - no authentication headers
        
        async with aiohttp.ClientSession() as session:
            # Get news articles
            async with session.get(
                f"{API_V1_URL}/news?category={category}&page={page}&limit=20",
                timeout=5
            ) as response:
                if response.status == 200:
                    news_data["articles"] = await response.json()
                else:
                    news_data["articles"] = []
            
            # Get trending topics
            async with session.get(
                f"{API_V1_URL}/news/trending",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    news_data["trending"] = await response.json()
                else:
                    news_data["trending"] = []
        
        return templates.TemplateResponse(
            "news/index.html",
            {"request": request, "data": news_data, "user": None, "demo_mode": True}
        )
    except Exception as e:
        logger.error(f"News page error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e), "user": None, "demo_mode": True},
            status_code=500
        )

@router.get("/news/article/{article_id}", response_class=HTMLResponse)
async def news_article(
    request: Request,
    article_id: str
):
    """Display specific news article (demo mode)"""
    try:
        article_data = {}
        
        # Demo mode - no authentication headers
        
        async with aiohttp.ClientSession() as session:
            # Get article details
            async with session.get(
                f"{API_V1_URL}/news/article/{article_id}",
                timeout=5
            ) as response:
                if response.status == 200:
                    article_data["article"] = await response.json()
                elif response.status == 404:
                    raise HTTPException(status_code=404, detail="Article not found")
                else:
                    raise HTTPException(status_code=response.status, detail="Failed to retrieve article")
            
            # Get related articles
            async with session.get(
                f"{API_V1_URL}/news/related/{article_id}",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    article_data["related"] = await response.json()
                else:
                    article_data["related"] = []
            
            # Get sentiment analysis if premium user
            if user and user.get("role") in ["premium", "admin"]:
                async with session.get(
                    f"{API_V1_URL}/news/sentiment/{article_id}",
                    headers=headers,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        article_data["sentiment"] = await response.json()
                    else:
                        article_data["sentiment"] = {"status": "unavailable"}
        
        return templates.TemplateResponse(
            "news/article.html",
            {"request": request, "data": article_data, "user": None, "demo_mode": True}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"News article error for {article_id}: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e), "user": None, "demo_mode": True},
            status_code=500
        )