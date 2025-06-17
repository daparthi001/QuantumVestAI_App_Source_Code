"""
Dashboard Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
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
from auth.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.dashboard_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    """Main dashboard integrating with API endpoints"""
    try:
        dashboard_data = {
            "user": user,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        async with aiohttp.ClientSession() as session:
            # Set authorization header for API requests
            headers = {"Authorization": f"Bearer {user.get('token', '')}"}
            
            # 1. Get market overview data
            try:
                async with session.get(f"{API_V1_URL}/market/overview", timeout=5) as response:
                    if response.status == 200:
                        dashboard_data["market"] = await response.json()
                    else:
                        dashboard_data["market"] = {
                            "status": "unavailable", 
                            "error": f"Status code: {response.status}"
                        }
            except Exception as e:
                logger.error(f"Error fetching market overview: {str(e)}")
                dashboard_data["market"] = {"status": "error", "message": str(e)}
            
            # 2. Get user portfolio summary if available
            try:
                async with session.get(
                    f"{API_V1_URL}/portfolio/{user['username']}/summary", 
                    headers=headers,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        dashboard_data["portfolio"] = await response.json()
                    else:
                        dashboard_data["portfolio"] = {"status": "unavailable"}
            except Exception as e:
                logger.error(f"Error fetching portfolio: {str(e)}")
                dashboard_data["portfolio"] = {"status": "error", "message": str(e)}
            
            # 3. Get forecast recommendations
            try:
                async with session.get(
                    f"{API_V1_URL}/forecast/recommendations",
                    headers=headers,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        dashboard_data["recommendations"] = await response.json()
                    else:
                        dashboard_data["recommendations"] = {"status": "unavailable"}
            except Exception as e:
                logger.error(f"Error fetching recommendations: {str(e)}")
                dashboard_data["recommendations"] = {"status": "error", "message": str(e)}
            
            # 4. Get watchlist summary
            try:
                async with session.get(
                    f"{API_V1_URL}/watchlist/{user['username']}/highlights",
                    headers=headers,
                    timeout=5
                ) as response:
                    if response.status == 200:
                        dashboard_data["watchlist"] = await response.json()
                    else:
                        dashboard_data["watchlist"] = {"status": "unavailable"}
            except Exception as e:
                logger.error(f"Error fetching watchlist: {str(e)}")
                dashboard_data["watchlist"] = {"status": "error", "message": str(e)}
            
            # 5. Get recent news
            try:
                async with session.get(f"{API_V1_URL}/news/recent", timeout=5) as response:
                    if response.status == 200:
                        dashboard_data["news"] = await response.json()
                    else:
                        dashboard_data["news"] = {"status": "unavailable"}
            except Exception as e:
                logger.error(f"Error fetching news: {str(e)}")
                dashboard_data["news"] = {"status": "error", "message": str(e)}

        return templates.TemplateResponse(
            "dashboard/index.html",
            {"request": request, "data": dashboard_data}
        )
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "error": str(e)},
            status_code=500
        )