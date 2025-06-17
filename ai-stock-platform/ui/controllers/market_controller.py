"""
Market Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional
from auth.dependencies import get_current_user, get_optional_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.market_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/market", response_class=HTMLResponse)
async def market_overview(request: Request, user: Optional[dict] = Depends(get_optional_current_user)):
    """Display market overview page"""
    try:
        market_data = {}
        
        async with aiohttp.ClientSession() as session:
            headers = {}
            if user and "token" in user:
                headers["Authorization"] = f"Bearer {user['token']}"
            
            # Get market overview
            async with session.get(f"{API_V1_URL}/market/overview", headers=headers, timeout=5) as response:
                if response.status == 200:
                    market_data["overview"] = await response.json()
                else:
                    market_data["overview"] = {"status": "unavailable"}
            
            # Get top gainers
            async with session.get(f"{API_V1_URL}/market/gainers", headers=headers, timeout=5) as response:
                if response.status == 200:
                    market_data["gainers"] = await response.json()
                else:
                    market_data["gainers"] = []
            
            # Get top losers
            async with session.get(f"{API_V1_URL}/market/losers", headers=headers, timeout=5) as response:
                if response.status == 200:
                    market_data["losers"] = await response.json()
                else:
                    market_data["losers"] = []
            
            # Get sector performance
            async with session.get(f"{API_V1_URL}/market/sectors", headers=headers, timeout=5) as response:
                if response.status == 200:
                    market_data["sectors"] = await response.json()
                else:
                    market_data["sectors"] = []
            
            # Get market indices
            async with session.get(f"{API_V1_URL}/market/indices", headers=headers, timeout=5) as response:
                if response.status == 200:
                    market_data["indices"] = await response.json()
                else:
                    market_data["indices"] = []

        return templates.TemplateResponse(
            "market/overview.html",
            {"request": request, "data": market_data, "user": user}
        )
    except Exception as e:
        logger.error(f"Market overview error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.get("/market/sentiment", response_class=HTMLResponse)
async def market_sentiment(request: Request, user: dict = Depends(get_current_user)):
    """Display market sentiment page"""
    try:
        sentiment_data = {}
        
        # This requires premium access
        headers = {"Authorization": f"Bearer {user.get('token', '')}"}
        
        async with aiohttp.ClientSession() as session:
            # Get market sentiment
            async with session.get(f"{API_V1_URL}/sentiment/market", headers=headers, timeout=5) as response:
                if response.status == 200:
                    sentiment_data["market"] = await response.json()
                else:
                    sentiment_data["market"] = {"status": "unavailable"}
                    
            # Get sentiment for sectors
            async with session.get(f"{API_V1_URL}/sentiment/sectors", headers=headers, timeout=5) as response:
                if response.status == 200:
                    sentiment_data["sectors"] = await response.json()
                else:
                    sentiment_data["sectors"] = []
            
            # Get positive sentiment stocks
            async with session.get(f"{API_V1_URL}/sentiment/positive", headers=headers, timeout=5) as response:
                if response.status == 200:
                    sentiment_data["positive"] = await response.json()
                else:
                    sentiment_data["positive"] = []
            
            # Get negative sentiment stocks
            async with session.get(f"{API_V1_URL}/sentiment/negative", headers=headers, timeout=5) as response:
                if response.status == 200:
                    sentiment_data["negative"] = await response.json()
                else:
                    sentiment_data["negative"] = []
            
            # Get sentiment trend
            async with session.get(f"{API_V1_URL}/sentiment/trend", headers=headers, timeout=5) as response:
                if response.status == 200:
                    sentiment_data["trend"] = await response.json()
                else:
                    sentiment_data["trend"] = {"status": "unavailable"}

        return templates.TemplateResponse(
            "market/sentiment.html",
            {"request": request, "data": sentiment_data, "user": user}
        )
    except Exception as e:
        logger.error(f"Market sentiment error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )