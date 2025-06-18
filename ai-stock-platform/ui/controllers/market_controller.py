"""
Market Controller for QuantumVestAI
Created: 2025-06-17 22:30:15
Updated: 2025-06-18 00:46:35
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pathlib import Path
from auth.dependencies import get_current_user, get_optional_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.market_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/market", response_class=HTMLResponse)
async def market_overview(request: Request, user: dict = Depends(get_optional_current_user)):
    """
    Market overview page displaying indices, sector performance, and top movers
    Public endpoint that shows more details for logged in users
    """
    try:
        market_data = {
            "user": user,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        async with aiohttp.ClientSession() as session:
            # Get market overview data
            try:
                async with session.get(f"{API_V1_URL}/market/overview", timeout=5) as response:
                    if response.status == 200:
                        market_data["overview"] = await response.json()
                    else:
                        logger.error(f"Market overview API returned status {response.status}")
                        market_data["overview"] = {"status": "unavailable"}
            except Exception as e:
                logger.error(f"Error fetching market overview: {str(e)}")
                market_data["overview"] = {"status": "error", "message": str(e)}
            
            # Get sector performance
            try:
                async with session.get(f"{API_V1_URL}/market/sectors", timeout=5) as response:
                    if response.status == 200:
                        market_data["sectors"] = await response.json()
                    else:
                        market_data["sectors"] = {"status": "unavailable"}
            except Exception as e:
                logger.error(f"Error fetching sector data: {str(e)}")
                market_data["sectors"] = {"status": "error", "message": str(e)}
            
            # Get top movers
            try:
                async with session.get(f"{API_V1_URL}/market/movers", timeout=5) as response:
                    if response.status == 200:
                        market_data["movers"] = await response.json()
                    else:
                        market_data["movers"] = {"status": "unavailable"}
            except Exception as e:
                logger.error(f"Error fetching top movers: {str(e)}")
                market_data["movers"] = {"status": "error", "message": str(e)}
            
            # Get market sentiment (premium feature)
            if user and user.get("role") in ("premium", "admin"):
                try:
                    headers = {"Authorization": f"Bearer {user.get('token', '')}"}
                    async with session.get(
                        f"{API_V1_URL}/market/sentiment", 
                        headers=headers,
                        timeout=5
                    ) as response:
                        if response.status == 200:
                            market_data["sentiment"] = await response.json()
                        else:
                            market_data["sentiment"] = {"status": "unavailable"}
                except Exception as e:
                    logger.error(f"Error fetching market sentiment: {str(e)}")
                    market_data["sentiment"] = {"status": "error", "message": str(e)}

        return templates.TemplateResponse(
            "market/overview.html",
            {"request": request, "data": market_data}
        )
    except Exception as e:
        logger.error(f"Market page error: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.get("/market/sentiment", response_class=HTMLResponse)
async def market_sentiment(request: Request, user: dict = Depends(get_current_user)):
    """
    Detailed market sentiment analysis (premium feature)
    """
    # Check if user has premium access
    if user.get("role") not in ("premium", "admin"):
        return templates.TemplateResponse(
            "premium_required.html",
            {"request": request, "feature": "Market Sentiment Analysis"}
        )
    
    try:
        sentiment_data = {
            "user": user,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        async with aiohttp.ClientSession() as session:
            # Set authorization header for API requests
            headers = {"Authorization": f"Bearer {user.get('token', '')}"}
            
            # Get market sentiment data
            try:
                async with session.get(
                    f"{API_V1_URL}/market/sentiment/detailed", 
                    headers=headers,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        sentiment_data["sentiment"] = await response.json()
                    else:
                        sentiment_data["sentiment"] = {"status": "unavailable"}
            except Exception as e:
                logger.error(f"Error fetching detailed sentiment: {str(e)}")
                sentiment_data["sentiment"] = {"status": "error", "message": str(e)}
                
        return templates.TemplateResponse(
            "market/sentiment.html",
            {"request": request, "data": sentiment_data}
        )
    except Exception as e:
        logger.error(f"Market sentiment page error: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "error": str(e)},
            status_code=500
        )