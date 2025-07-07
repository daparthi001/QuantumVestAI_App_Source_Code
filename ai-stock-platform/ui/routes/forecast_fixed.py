"""
Forecast routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Query, Path, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path as PathLib
import logging
import requests
import os
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, Any, List

# Configure logging
logger = logging.getLogger(__name__)

# Setup templates - use relative path from project root
BASE_DIR = PathLib(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000/api/v1")

# Create router
router = APIRouter(
    prefix="/forecast",
    tags=["forecast"]
)

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    auth_cookie = request.cookies.get("access_token")
    return bool(auth_cookie)

def get_user_from_request(request: Request) -> Optional[Dict]:
    """Extract user info from request"""
    if is_authenticated(request):
        return {
            "username": "demo",
            "email": "demo@quantumvestai.com",
            "role": "user",
            "is_authenticated": True
        }
    return None

def get_demo_forecast_data(symbol: str) -> Dict[str, Any]:
    """Generate demo forecast data for a given symbol"""
    base_price = {
        "AAPL": 182.31,
        "MSFT": 378.85,
        "GOOGL": 142.56,
        "AMZN": 153.32,
        "TSLA": 238.45,
        "NVDA": 875.42,
        "META": 511.24
    }.get(symbol, 150.00)
    
    # Generate forecast points
    forecast_dates = []
    forecast_prices = []
    current_date = datetime.now()
    
    for i in range(30):  # 30-day forecast
        date = current_date + timedelta(days=i+1)
        forecast_dates.append(date.strftime("%Y-%m-%d"))
        
        # Simulate some price movement with trend
        trend_factor = 1.002 if i < 20 else 0.998  # Uptrend then slight downtrend
        volatility = base_price * 0.02 * (0.5 - (i % 7) / 14)  # Weekly volatility pattern
        price = base_price * (trend_factor ** i) + volatility
        forecast_prices.append(round(price, 2))
    
    # Generate confidence intervals
    upper_bound = [p * 1.15 for p in forecast_prices]
    lower_bound = [p * 0.85 for p in forecast_prices]
    
    return {
        "symbol": symbol,
        "current_price": base_price,
        "forecast_horizon": "30 days",
        "confidence_level": 85,
        "dates": forecast_dates,
        "prices": forecast_prices,
        "upper_bound": upper_bound,
        "lower_bound": lower_bound,
        "key_metrics": {
            "expected_return": 5.4,
            "volatility": 18.7,
            "sharpe_ratio": 1.23,
            "max_drawdown": -12.3,
            "win_probability": 67.8
        },
        "ai_insights": [
            {
                "category": "Technical Analysis",
                "insight": f"{symbol} shows strong momentum with bullish indicators across multiple timeframes.",
                "confidence": 78
            },
            {
                "category": "Fundamental Analysis", 
                "insight": "Company fundamentals remain strong with solid earnings growth prospects.",
                "confidence": 82
            },
            {
                "category": "Market Sentiment",
                "insight": "Positive market sentiment driven by sector rotation and institutional buying.",
                "confidence": 71
            }
        ],
        "risk_factors": [
            "Market volatility due to economic uncertainty",
            "Sector-specific risks in technology industry",
            "Regulatory changes affecting business operations"
        ]
    }

@router.get("/", response_class=HTMLResponse)
async def forecast_home(request: Request):
    """Main forecast page"""
    try:
        # Check authentication for full features
        user = get_user_from_request(request)
        
        # Popular stocks for demo
        popular_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]
        
        # Recent forecasts (demo data)
        recent_forecasts = []
        for i, symbol in enumerate(popular_stocks[:5]):
            forecast_data = get_demo_forecast_data(symbol)
            recent_forecasts.append({
                "symbol": symbol,
                "current_price": forecast_data["current_price"],
                "forecast_price": forecast_data["prices"][29],  # 30-day forecast
                "expected_return": forecast_data["key_metrics"]["expected_return"],
                "confidence": forecast_data["confidence_level"],
                "created_at": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            })
        
        context = {
            "request": request,
            "user": user,
            "popular_stocks": popular_stocks,
            "recent_forecasts": recent_forecasts,
            "page_title": "AI Forecasting - QuantumVestAI",
            "active_page": "forecast"
        }
        
        return templates.TemplateResponse("forecast/index.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering forecast home page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Forecast Error - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h2 class="card-title text-danger">Forecast Service Unavailable</h2>
                                    <p class="card-text">We're experiencing technical difficulties with our forecasting service.</p>
                                    <div class="mt-3">
                                        <a href="/dashboard" class="btn btn-primary">Return to Dashboard</a>
                                        <a href="/" class="btn btn-secondary">Go Home</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )

@router.get("/stock/{symbol}", response_class=HTMLResponse)
async def forecast_stock(request: Request, symbol: str):
    """Individual stock forecast page"""
    try:
        # Validate and clean symbol
        symbol = symbol.upper().strip()
        if not symbol or len(symbol) > 10:
            raise HTTPException(
                status_code=400,
                detail="Invalid stock symbol"
            )
        
        user = get_user_from_request(request)
        forecast_data = get_demo_forecast_data(symbol)
        
        # Historical data for comparison (demo)
        historical_data = {
            "dates": [(datetime.now() - timedelta(days=30-i)).strftime("%Y-%m-%d") for i in range(30)],
            "prices": [forecast_data["current_price"] * (0.95 + 0.1 * (i/30)) for i in range(30)]
        }
        
        context = {
            "request": request,
            "user": user,
            "symbol": symbol,
            "forecast": forecast_data,
            "historical": historical_data,
            "page_title": f"{symbol} Forecast - QuantumVestAI",
            "active_page": "forecast"
        }
        
        return templates.TemplateResponse("forecast/stock.html", context)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering stock forecast for {symbol}: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Forecast Error - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h2 class="card-title text-danger">Unable to Load Forecast</h2>
                                    <p class="card-text">We couldn't generate a forecast for symbol: {symbol}</p>
                                    <div class="mt-3">
                                        <a href="/forecast" class="btn btn-primary">Back to Forecasts</a>
                                        <a href="/dashboard" class="btn btn-secondary">Dashboard</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )

@router.post("/generate")
async def generate_forecast(
    request: Request,
    symbol: str = Form(...),
    forecast_days: int = Form(30),
    model_type: str = Form("advanced")
):
    """Generate new forecast for a stock"""
    try:
        # Validate inputs
        symbol = symbol.upper().strip()
        if not symbol or len(symbol) > 10:
            raise HTTPException(
                status_code=422,
                detail="Invalid stock symbol"
            )
        
        if forecast_days < 1 or forecast_days > 365:
            raise HTTPException(
                status_code=422,
                detail="Forecast days must be between 1 and 365"
            )
        
        if model_type not in ["basic", "advanced", "premium"]:
            model_type = "advanced"
        
        logger.info(f"Generating {model_type} forecast for {symbol} for {forecast_days} days")
        
        # Simulate API call to generate forecast
        forecast_data = get_demo_forecast_data(symbol)
        
        # Adjust forecast length
        if forecast_days != 30:
            # Recalculate for different timeframe
            forecast_dates = []
            forecast_prices = []
            current_date = datetime.now()
            base_price = forecast_data["current_price"]
            
            for i in range(forecast_days):
                date = current_date + timedelta(days=i+1)
                forecast_dates.append(date.strftime("%Y-%m-%d"))
                
                # Adjust trend for longer/shorter periods
                trend_factor = 1.001 if forecast_days > 30 else 1.003
                volatility = base_price * 0.02 * (0.5 - (i % 7) / 14)
                price = base_price * (trend_factor ** i) + volatility
                forecast_prices.append(round(price, 2))
            
            forecast_data["dates"] = forecast_dates
            forecast_data["prices"] = forecast_prices
            forecast_data["forecast_horizon"] = f"{forecast_days} days"
        
        # Enhanced features for advanced/premium models
        if model_type in ["advanced", "premium"]:
            forecast_data["enhanced_features"] = {
                "sentiment_analysis": True,
                "options_flow": True,
                "insider_activity": True,
                "institutional_holdings": True
            }
            
            if model_type == "premium":
                forecast_data["premium_features"] = {
                    "real_time_updates": True,
                    "alert_system": True,
                    "custom_risk_models": True,
                    "portfolio_optimization": True
                }
        
        return JSONResponse(content={
            "success": True,
            "message": f"Forecast generated successfully for {symbol}",
            "data": forecast_data,
            "model_type": model_type,
            "generated_at": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate forecast"
        )

@router.get("/api/forecast/{symbol}")
async def get_forecast_api(
    request: Request,
    symbol: str,
    days: int = Query(30, ge=1, le=365),
    model: str = Query("advanced")
):
    """API endpoint to get forecast data"""
    try:
        symbol = symbol.upper().strip()
        if not symbol:
            raise HTTPException(
                status_code=422,
                detail="Invalid stock symbol"
            )
        
        logger.info(f"API request for {symbol} forecast ({days} days, {model} model)")
        
        forecast_data = get_demo_forecast_data(symbol)
        
        # Adjust for requested timeframe
        if days != 30:
            # Recalculate forecast for different period
            forecast_dates = []
            forecast_prices = []
            current_date = datetime.now()
            base_price = forecast_data["current_price"]
            
            for i in range(days):
                date = current_date + timedelta(days=i+1)
                forecast_dates.append(date.strftime("%Y-%m-%d"))
                
                trend_factor = 1.001 if days > 30 else 1.003
                volatility = base_price * 0.02 * (0.5 - (i % 7) / 14)
                price = base_price * (trend_factor ** i) + volatility
                forecast_prices.append(round(price, 2))
            
            forecast_data["dates"] = forecast_dates
            forecast_data["prices"] = forecast_prices
            forecast_data["forecast_horizon"] = f"{days} days"
        
        return JSONResponse(content={
            "success": True,
            "data": forecast_data,
            "requested_days": days,
            "model_type": model,
            "generated_at": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in forecast API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve forecast data"
        )

@router.get("/compare", response_class=HTMLResponse)
async def forecast_compare(
    request: Request,
    symbols: str = Query("AAPL,MSFT,GOOGL", description="Comma-separated list of symbols")
):
    """Compare forecasts for multiple stocks"""
    try:
        user = get_user_from_request(request)
        
        # Parse and validate symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        symbol_list = symbol_list[:5]  # Limit to 5 symbols
        
        if not symbol_list:
            symbol_list = ["AAPL", "MSFT", "GOOGL"]  # Default comparison
        
        # Generate forecast data for each symbol
        comparison_data = []
        for symbol in symbol_list:
            forecast = get_demo_forecast_data(symbol)
            comparison_data.append({
                "symbol": symbol,
                "current_price": forecast["current_price"],
                "forecast_price": forecast["prices"][29],  # 30-day
                "expected_return": forecast["key_metrics"]["expected_return"],
                "volatility": forecast["key_metrics"]["volatility"],
                "sharpe_ratio": forecast["key_metrics"]["sharpe_ratio"],
                "win_probability": forecast["key_metrics"]["win_probability"]
            })
        
        context = {
            "request": request,
            "user": user,
            "symbols": symbol_list,
            "comparison_data": comparison_data,
            "page_title": "Forecast Comparison - QuantumVestAI",
            "active_page": "forecast"
        }
        
        return templates.TemplateResponse("forecast/compare.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering forecast comparison: {str(e)}")
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Comparison Error - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h2 class="card-title text-danger">Comparison Unavailable</h2>
                                    <p class="card-text">Unable to load forecast comparison at this time.</p>
                                    <div class="mt-3">
                                        <a href="/forecast" class="btn btn-primary">Back to Forecasts</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )

@router.post("/save-forecast")
async def save_forecast(request: Request):
    """Save forecast to user's saved forecasts"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        
        # Parse request body
        body = await request.json()
        symbol = body.get("symbol", "").upper()
        forecast_type = body.get("type", "advanced")
        
        if not symbol:
            raise HTTPException(
                status_code=422,
                detail="Symbol is required"
            )
        
        logger.info(f"Saving forecast for {symbol} (demo mode)")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Forecast for {symbol} saved successfully",
            "saved_at": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving forecast: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save forecast"
        )