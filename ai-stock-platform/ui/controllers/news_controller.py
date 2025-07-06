"""
News Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Depends, Query, HTTPException
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
    page: int = Query(1, ge=1),
    request: Request
):
    """Display news page"""
        logger.error(f"News page error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.get("/news/article/{article_id}", response_class=HTMLResponse)
async def news_article(
    request: Request,
    article_id: str,
    request: Request
):
    """Display specific news article"""
        raise e
    except Exception as e:
        logger.error(f"News article error for {article_id}: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )