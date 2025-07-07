"""
<<<<<<< HEAD
Stock predictability analysis routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Query, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import requests
import os
from datetime import datetime, timedelta
import json
import math

# Setup logging
logger = logging.getLogger(__name__)

# Setup templates - use relative path from project root
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000/api/v1")

# Create router
router = APIRouter(tags=["predictability"])

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

def calculate_predictability_score(symbol: str) -> Dict[str, Any]:
    """Calculate demo predictability metrics for a stock"""
    # Base calculations on symbol characteristics for consistency
    base_score = 50 + (len(symbol) * 5) % 40
    
    # Generate various predictability metrics
    metrics = {
        "overall_score": base_score,
        "technical_score": base_score + 5,
        "fundamental_score": base_score - 3,
        "sentiment_score": base_score + 2,
        "volatility_score": 100 - base_score,
        "trend_strength": base_score - 10,
        "momentum_score": base_score + 8,
        "correlation_score": base_score - 5
    }
    
    # Ensure scores are within 0-100 range
    for key in metrics:
        metrics[key] = max(0, min(100, metrics[key]))
    
    return {
        "symbol": symbol,
        "scores": metrics,
        "risk_level": "Low" if metrics["overall_score"] > 70 else "Medium" if metrics["overall_score"] > 40 else "High",
        "confidence_level": metrics["overall_score"],
        "prediction_horizon": "30 days",
        "last_updated": datetime.now().isoformat()
    }

def get_demo_predictability_factors(symbol: str) -> List[Dict[str, Any]]:
    """Generate demo predictability factors analysis"""
    return [
        {
            "factor": "Price Momentum",
            "impact": 23.5,
            "description": "Strong upward price momentum over the last 20 days",
            "confidence": 82,
            "direction": "positive"
        },
        {
            "factor": "Volume Patterns",
            "impact": 18.7,
            "description": "Consistent volume patterns indicate institutional interest",
            "confidence": 75,
            "direction": "positive"
        },
        {
            "factor": "Technical Indicators",
            "impact": 16.2,
            "description": "RSI and MACD showing bullish convergence",
            "confidence": 79,
            "direction": "positive"
        },
        {
            "factor": "Market Correlation",
            "impact": 14.8,
            "description": "Low correlation with market indices suggests independence",
            "confidence": 68,
            "direction": "neutral"
        },
        {
            "factor": "Earnings Quality",
            "impact": 12.3,
            "description": "Consistent earnings growth over past 4 quarters",
            "confidence": 84,
            "direction": "positive"
        },
        {
            "factor": "Sector Performance",
            "impact": 10.1,
            "description": "Technology sector showing outperformance",
            "confidence": 71,
            "direction": "positive"
        },
        {
            "factor": "Options Activity",
            "impact": 4.4,
            "description": "Unusual options activity suggesting volatility",
            "confidence": 63,
            "direction": "negative"
        }
    ]

def get_demo_historical_accuracy(symbol: str) -> Dict[str, Any]:
    """Generate demo historical prediction accuracy data"""
    # Generate time series data for accuracy tracking
    dates = []
    accuracy_scores = []
    prediction_counts = []
    
    for i in range(12):  # 12 months of data
        date = (datetime.now() - timedelta(days=30*i)).strftime("%Y-%m")
        accuracy = 65 + (len(symbol) + i) % 25
        predictions = 15 + (i % 10)
        
        dates.insert(0, date)
        accuracy_scores.insert(0, accuracy)
        prediction_counts.insert(0, predictions)
    
    return {
        "timeframe": "12 months",
        "dates": dates,
        "accuracy_scores": accuracy_scores,
        "prediction_counts": prediction_counts,
        "average_accuracy": sum(accuracy_scores) / len(accuracy_scores),
        "total_predictions": sum(prediction_counts),
        "accuracy_trend": "improving" if accuracy_scores[-1] > accuracy_scores[0] else "declining"
    }

def get_demo_model_comparison(symbol: str) -> List[Dict[str, Any]]:
    """Generate demo model comparison data"""
    models = [
        {
            "name": "LSTM Neural Network",
            "accuracy": 78.5,
            "precision": 82.1,
            "recall": 75.9,
            "f1_score": 78.9,
            "last_trained": "2025-01-05",
            "prediction_horizon": "1-7 days",
            "strengths": ["Short-term trends", "Pattern recognition"],
            "weaknesses": ["Black swan events", "Market regime changes"]
        },
        {
            "name": "Random Forest",
            "accuracy": 73.2,
            "precision": 76.8,
            "recall": 71.4,
            "f1_score": 74.0,
            "last_trained": "2025-01-06",
            "prediction_horizon": "1-14 days",
            "strengths": ["Feature importance", "Robust to outliers"],
            "weaknesses": ["Limited extrapolation", "Complex interactions"]
        },
        {
            "name": "XGBoost",
            "accuracy": 75.8,
            "precision": 79.3,
            "recall": 73.6,
            "f1_score": 76.4,
            "last_trained": "2025-01-07",
            "prediction_horizon": "1-21 days",
            "strengths": ["Non-linear patterns", "High performance"],
            "weaknesses": ["Overfitting risk", "Parameter tuning"]
        },
        {
            "name": "Ensemble Model",
            "accuracy": 81.7,
            "precision": 84.2,
            "recall": 79.8,
            "f1_score": 81.9,
            "last_trained": "2025-01-07",
            "prediction_horizon": "1-30 days",
            "strengths": ["Combines multiple approaches", "Reduced variance"],
            "weaknesses": ["Computational complexity", "Interpretability"]
        }
    ]
    
    # Sort by accuracy descending
    return sorted(models, key=lambda x: x["accuracy"], reverse=True)

@router.get("/", response_class=HTMLResponse)
async def predictability_home(
    request: Request,
    symbol: str = Query("AAPL", description="Stock symbol to analyze"),
    timeframe: str = Query("30d", description="Analysis timeframe"),
    model: str = Query("ensemble", description="Prediction model to use")
):
    """Main predictability analysis page"""
    try:
        user = get_user_from_request(request)
        
        # Validate and clean symbol
        symbol = symbol.upper().strip()
        if not symbol or len(symbol) > 10:
            symbol = "AAPL"  # Default fallback
        
        # Validate timeframe
        valid_timeframes = ["7d", "30d", "90d", "1y"]
        if timeframe not in valid_timeframes:
            timeframe = "30d"
        
        # Validate model
        valid_models = ["lstm", "random_forest", "xgboost", "ensemble"]
        if model not in valid_models:
            model = "ensemble"
        
        # Generate analysis data
        predictability_data = calculate_predictability_score(symbol)
        factors = get_demo_predictability_factors(symbol)
        historical_accuracy = get_demo_historical_accuracy(symbol)
        model_comparison = get_demo_model_comparison(symbol)
        
        # Popular stocks for quick analysis
        popular_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]
        
        context = {
            "request": request,
            "user": user,
            "symbol": symbol,
            "timeframe": timeframe,
            "model": model,
            "predictability": predictability_data,
            "factors": factors,
            "historical": historical_accuracy,
            "models": model_comparison,
            "popular_stocks": popular_stocks,
            "valid_timeframes": valid_timeframes,
            "valid_models": valid_models,
            "page_title": f"{symbol} Predictability Analysis - QuantumVestAI",
            "active_page": "predictability"
        }
        
        return templates.TemplateResponse("predictability/index.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering predictability page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Predictability Analysis Error - QuantumVestAI</title>
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
                                    <h2 class="card-title text-danger">Analysis Unavailable</h2>
                                    <p class="card-text">We're experiencing technical difficulties with predictability analysis.</p>
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
=======
QuantumVestAI Predictability Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup router
router = APIRouter(prefix="/predictability", tags=["predictability"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Demo predictability data
DEMO_PREDICTABILITY_SCORES = {
    "AAPL": {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "current_price": 185.50,
        "predictability_score": 85.2,
        "volatility": 0.25,
        "trend_strength": 0.78,
        "pattern_recognition": 0.82,
        "market_correlation": 0.73,
        "volume_predictability": 0.79,
        "sector": "Technology",
        "rank": 1,
        "confidence": 0.89,
        "risk_level": "Medium",
        "patterns": {
            "bullish_patterns": ["Cup and Handle", "Ascending Triangle"],
            "bearish_patterns": [],
            "neutral_patterns": ["Consolidation"]
        },
        "support_resistance": {
            "support_levels": [175.00, 170.00, 165.00],
            "resistance_levels": [190.00, 195.00, 200.00]
        },
        "momentum_indicators": {
            "rsi": 65.4,
            "macd": 2.15,
            "stochastic": 68.2,
            "williams_r": -25.8
        }
    },
    "MSFT": {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "current_price": 365.25,
        "predictability_score": 82.7,
        "volatility": 0.22,
        "trend_strength": 0.75,
        "pattern_recognition": 0.88,
        "market_correlation": 0.71,
        "volume_predictability": 0.76,
        "sector": "Technology",
        "rank": 2,
        "confidence": 0.85,
        "risk_level": "Medium",
        "patterns": {
            "bullish_patterns": ["Flag Pattern", "Rising Channel"],
            "bearish_patterns": [],
            "neutral_patterns": ["Sideways Trend"]
        },
        "support_resistance": {
            "support_levels": [350.00, 345.00, 340.00],
            "resistance_levels": [370.00, 375.00, 380.00]
        },
        "momentum_indicators": {
            "rsi": 58.9,
            "macd": 1.85,
            "stochastic": 62.1,
            "williams_r": -35.2
        }
    },
    "GOOGL": {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "current_price": 134.56,
        "predictability_score": 78.9,
        "volatility": 0.28,
        "trend_strength": 0.68,
        "pattern_recognition": 0.79,
        "market_correlation": 0.69,
        "volume_predictability": 0.73,
        "sector": "Communication Services",
        "rank": 3,
        "confidence": 0.81,
        "risk_level": "Medium-High",
        "patterns": {
            "bullish_patterns": ["Breakout", "Bullish Divergence"],
            "bearish_patterns": [],
            "neutral_patterns": ["Range Bound"]
        },
        "support_resistance": {
            "support_levels": [130.00, 125.00, 120.00],
            "resistance_levels": [140.00, 145.00, 150.00]
        },
        "momentum_indicators": {
            "rsi": 71.3,
            "macd": 3.22,
            "stochastic": 75.8,
            "williams_r": -18.4
        }
    },
    "TSLA": {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "current_price": 189.34,
        "predictability_score": 65.4,
        "volatility": 0.45,
        "trend_strength": 0.58,
        "pattern_recognition": 0.62,
        "market_correlation": 0.55,
        "volume_predictability": 0.68,
        "sector": "Consumer Cyclical",
        "rank": 8,
        "confidence": 0.67,
        "risk_level": "High",
        "patterns": {
            "bullish_patterns": ["Momentum Breakout"],
            "bearish_patterns": ["Head and Shoulders"],
            "neutral_patterns": ["Volatile Range"]
        },
        "support_resistance": {
            "support_levels": [180.00, 175.00, 170.00],
            "resistance_levels": [195.00, 200.00, 210.00]
        },
        "momentum_indicators": {
            "rsi": 82.1,
            "macd": 5.67,
            "stochastic": 88.9,
            "williams_r": -8.2
        }
    },
    "NVDA": {
        "symbol": "NVDA",
        "name": "NVIDIA Corp",
        "current_price": 245.67,
        "predictability_score": 81.3,
        "volatility": 0.35,
        "trend_strength": 0.85,
        "pattern_recognition": 0.78,
        "market_correlation": 0.67,
        "volume_predictability": 0.82,
        "sector": "Technology",
        "rank": 4,
        "confidence": 0.84,
        "risk_level": "Medium-High",
        "patterns": {
            "bullish_patterns": ["Strong Uptrend", "Bullish Flag"],
            "bearish_patterns": [],
            "neutral_patterns": []
        },
        "support_resistance": {
            "support_levels": [230.00, 220.00, 210.00],
            "resistance_levels": [250.00, 260.00, 270.00]
        },
        "momentum_indicators": {
            "rsi": 76.5,
            "macd": 4.33,
            "stochastic": 81.7,
            "williams_r": -15.6
        }
    }
}

SECTOR_PREDICTABILITY = {
    "Technology": {
        "avg_score": 82.4,
        "volatility": 0.27,
        "trend_consistency": 0.79,
        "top_stocks": ["AAPL", "MSFT", "NVDA"],
        "risk_level": "Medium"
    },
    "Healthcare": {
        "avg_score": 76.8,
        "volatility": 0.21,
        "trend_consistency": 0.73,
        "top_stocks": ["JNJ", "PFE", "UNH"],
        "risk_level": "Low-Medium"
    },
    "Finance": {
        "avg_score": 74.2,
        "volatility": 0.29,
        "trend_consistency": 0.71,
        "top_stocks": ["JPM", "BAC", "WFC"],
        "risk_level": "Medium"
    },
    "Energy": {
        "avg_score": 68.9,
        "volatility": 0.38,
        "trend_consistency": 0.64,
        "top_stocks": ["XOM", "CVX", "COP"],
        "risk_level": "High"
    }
}

@router.get("/", response_class=HTMLResponse)
async def predictability_page(
    request: Request, 
    ticker: str = Query(default="AAPL"), 
    timeframe: str = Query(default="1y"),
    model: str = Query(default="all")
):
    """Stock predictability analysis page"""
    try:
        ticker = ticker.upper()
        logger.info(f"Loading predictability analysis for {ticker}")
        
        # Get stock data
        if ticker in DEMO_PREDICTABILITY_SCORES:
            stock_data = DEMO_PREDICTABILITY_SCORES[ticker]
        else:
            # Generate demo data for any ticker
            stock_data = {
                "symbol": ticker,
                "name": f"{ticker} Corporation",
                "current_price": 100.00,
                "predictability_score": 70.5,
                "volatility": 0.30,
                "trend_strength": 0.65,
                "pattern_recognition": 0.70,
                "market_correlation": 0.60,
                "volume_predictability": 0.68,
                "sector": "Technology",
                "rank": 10,
                "confidence": 0.72,
                "risk_level": "Medium",
                "patterns": {
                    "bullish_patterns": ["Neutral"],
                    "bearish_patterns": [],
                    "neutral_patterns": ["Consolidation"]
                },
                "support_resistance": {
                    "support_levels": [95.00, 90.00, 85.00],
                    "resistance_levels": [105.00, 110.00, 115.00]
                },
                "momentum_indicators": {
                    "rsi": 55.0,
                    "macd": 0.50,
                    "stochastic": 60.0,
                    "williams_r": -40.0
                }
            }
        
        # Generate historical predictability scores
        historical_scores = []
        base_score = stock_data["predictability_score"]
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
            score = base_score + (5 * (i % 7 - 3) / 10) + (2 * (i % 3 - 1))
            historical_scores.append({
                "date": date,
                "score": max(0, min(100, score))
            })
        
        # Top ranked stocks for comparison
        top_stocks = sorted(
            DEMO_PREDICTABILITY_SCORES.values(),
            key=lambda x: x["predictability_score"],
            reverse=True
        )[:10]
        
        return templates.TemplateResponse(
            "predictability.html",
            {
                "request": request,
                "ticker": ticker,
                "timeframe": timeframe,
                "model": model,
                "demo_mode": True,
                "stock_data": stock_data,
                "historical_scores": historical_scores,
                "top_stocks": top_stocks,
                "sector_data": SECTOR_PREDICTABILITY,
                "page_title": f"{ticker} Predictability - QuantumVestAI"
            }
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
        )
        
    except Exception as e:
        logger.error(f"Error loading predictability analysis: {str(e)}")
        return templates.TemplateResponse(
            "predictability.html",
            {
                "request": request,
                "ticker": ticker,
                "timeframe": timeframe,
                "model": model,
                "demo_mode": True,
                "stock_data": {},
                "historical_scores": [],
                "top_stocks": [],
                "sector_data": {},
                "error": f"Error loading predictability analysis: {str(e)}",
                "page_title": "Predictability Error"
            },
            status_code=500
        )

<<<<<<< HEAD
@router.get("/compare", response_class=HTMLResponse)
async def predictability_compare(
    request: Request,
    symbols: str = Query("AAPL,MSFT,GOOGL", description="Comma-separated list of symbols")
):
    """Compare predictability across multiple stocks"""
    try:
        user = get_user_from_request(request)
        
        # Parse and validate symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        symbol_list = symbol_list[:5]  # Limit to 5 symbols
        
        if not symbol_list:
            symbol_list = ["AAPL", "MSFT", "GOOGL"]  # Default comparison
        
        # Generate comparison data
        comparison_data = []
        for symbol in symbol_list:
            predictability = calculate_predictability_score(symbol)
            comparison_data.append({
                "symbol": symbol,
                "overall_score": predictability["scores"]["overall_score"],
                "technical_score": predictability["scores"]["technical_score"],
                "fundamental_score": predictability["scores"]["fundamental_score"],
                "volatility_score": predictability["scores"]["volatility_score"],
                "risk_level": predictability["risk_level"],
                "confidence": predictability["confidence_level"]
            })
        
        # Sort by overall score
        comparison_data.sort(key=lambda x: x["overall_score"], reverse=True)
        
        context = {
            "request": request,
            "user": user,
            "symbols": symbol_list,
            "comparison_data": comparison_data,
            "page_title": "Predictability Comparison - QuantumVestAI",
            "active_page": "predictability"
        }
        
        return templates.TemplateResponse("predictability/compare.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering predictability comparison: {str(e)}")
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
                                    <p class="card-text">Unable to load predictability comparison at this time.</p>
                                    <div class="mt-3">
                                        <a href="/predictability" class="btn btn-primary">Back to Analysis</a>
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
=======
@router.get("/ranking", response_class=HTMLResponse)
async def predictability_ranking_page(
    request: Request,
    sector: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=5, le=50)
):
    """Predictability ranking page"""
    try:
        logger.info(f"Loading predictability ranking (sector: {sector}, limit: {limit})")
        
        # Get all stocks and sort by predictability score
        all_stocks = list(DEMO_PREDICTABILITY_SCORES.values())
        
        # Filter by sector if specified
        if sector:
            all_stocks = [stock for stock in all_stocks if stock["sector"] == sector]
        
        # Sort by predictability score
        ranked_stocks = sorted(all_stocks, key=lambda x: x["predictability_score"], reverse=True)[:limit]
        
        # Add ranking
        for i, stock in enumerate(ranked_stocks):
            stock["rank"] = i + 1
        
        return templates.TemplateResponse(
            "predictability_ranking.html",
            {
                "request": request,
                "sector": sector,
                "limit": limit,
                "demo_mode": True,
                "ranked_stocks": ranked_stocks,
                "sector_data": SECTOR_PREDICTABILITY,
                "available_sectors": list(SECTOR_PREDICTABILITY.keys()),
                "page_title": "Predictability Ranking - QuantumVestAI"
            }
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
        )
        
    except Exception as e:
        logger.error(f"Error loading predictability ranking: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load predictability ranking",
                "page_title": "Ranking Error"
            },
            status_code=500
        )

<<<<<<< HEAD
@router.get("/api/score/{symbol}")
async def get_predictability_score(
    request: Request,
    symbol: str,
    timeframe: str = Query("30d"),
    model: str = Query("ensemble")
):
    """API endpoint for predictability score"""
    try:
        symbol = symbol.upper().strip()
        if not symbol:
            raise HTTPException(
                status_code=422,
                detail="Invalid stock symbol"
            )
        
        predictability_data = calculate_predictability_score(symbol)
        factors = get_demo_predictability_factors(symbol)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "model": model,
                "predictability": predictability_data,
                "factors": factors
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in predictability API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate predictability score"
        )

@router.get("/api/models/{symbol}")
async def get_model_performance(request: Request, symbol: str):
    """Get model performance comparison for a symbol"""
    try:
        symbol = symbol.upper().strip()
        if not symbol:
            raise HTTPException(
                status_code=422,
                detail="Invalid stock symbol"
            )
        
        models = get_demo_model_comparison(symbol)
        historical = get_demo_historical_accuracy(symbol)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "symbol": symbol,
                "models": models,
                "historical_accuracy": historical
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching model performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch model performance data"
        )

@router.post("/api/analyze")
async def analyze_predictability(request: Request):
    """Analyze predictability for custom parameters"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        
        # Parse request body
        body = await request.json()
        symbol = body.get("symbol", "").upper().strip()
        timeframe = body.get("timeframe", "30d")
        features = body.get("features", ["price", "volume", "sentiment"])
        
        if not symbol:
            raise HTTPException(
                status_code=422,
                detail="Symbol is required"
            )
        
        # Generate custom analysis
        analysis_result = {
            "symbol": symbol,
            "timeframe": timeframe,
            "features_analyzed": features,
            "analysis_id": f"analysis_{symbol}_{int(datetime.now().timestamp())}",
            "results": calculate_predictability_score(symbol),
            "factors": get_demo_predictability_factors(symbol),
            "recommendations": [
                f"Monitor {symbol} for short-term trading opportunities",
                "Consider position sizing based on volatility metrics",
                "Set stop-loss levels at key technical support levels"
            ]
        }
        
        logger.info(f"Generated custom predictability analysis for {symbol}")
        
        return JSONResponse(content={
            "success": True,
            "data": analysis_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in predictability analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze predictability"
        )

@router.get("/api/batch-analysis")
async def batch_predictability_analysis(
    request: Request,
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    limit: int = Query(10, ge=1, le=20)
):
    """Batch analysis for multiple symbols"""
    try:
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        symbol_list = symbol_list[:limit]
        
        if not symbol_list:
            raise HTTPException(
                status_code=422,
                detail="No valid symbols provided"
            )
        
        # Generate analysis for each symbol
        batch_results = []
        for symbol in symbol_list:
            try:
                result = calculate_predictability_score(symbol)
                batch_results.append(result)
            except Exception as e:
                logger.warning(f"Failed to analyze {symbol}: {str(e)}")
                continue
        
        # Sort by overall score
        batch_results.sort(key=lambda x: x["scores"]["overall_score"], reverse=True)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "symbols_analyzed": len(batch_results),
                "results": batch_results
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to perform batch analysis"
        )
=======
@router.get("/compare", response_class=HTMLResponse)
async def predictability_comparison_page(
    request: Request,
    tickers: str = Query(...),  # Comma-separated list of tickers
    timeframe: str = Query(default="1y")
):
    """Predictability comparison page"""
    try:
        ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
        logger.info(f"Loading predictability comparison for: {ticker_list}")
        
        comparison_data = []
        for ticker in ticker_list[:5]:  # Limit to 5 stocks
            if ticker in DEMO_PREDICTABILITY_SCORES:
                stock_data = DEMO_PREDICTABILITY_SCORES[ticker]
            else:
                # Generate demo data
                stock_data = {
                    "symbol": ticker,
                    "name": f"{ticker} Corporation",
                    "predictability_score": 65.0 + (len(ticker) * 2),
                    "volatility": 0.25 + (len(ticker) * 0.02),
                    "trend_strength": 0.60 + (len(ticker) * 0.03),
                    "pattern_recognition": 0.65 + (len(ticker) * 0.02),
                    "market_correlation": 0.55 + (len(ticker) * 0.03),
                    "volume_predictability": 0.60 + (len(ticker) * 0.02),
                    "risk_level": "Medium",
                    "confidence": 0.70 + (len(ticker) * 0.02)
                }
            comparison_data.append(stock_data)
        
        # Calculate relative rankings
        comparison_data.sort(key=lambda x: x["predictability_score"], reverse=True)
        for i, stock in enumerate(comparison_data):
            stock["comparison_rank"] = i + 1
        
        return templates.TemplateResponse(
            "predictability_comparison.html",
            {
                "request": request,
                "tickers": ticker_list,
                "timeframe": timeframe,
                "demo_mode": True,
                "comparison_data": comparison_data,
                "page_title": "Predictability Comparison - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading predictability comparison: {str(e)}")
        return templates.TemplateResponse(
            "predictability_comparison.html",
            {
                "request": request,
                "tickers": tickers.split(","),
                "timeframe": timeframe,
                "demo_mode": True,
                "comparison_data": [],
                "error": f"Error loading comparison: {str(e)}",
                "page_title": "Comparison Error"
            },
            status_code=500
        )

@router.get("/api/score/{symbol}")
async def get_predictability_score_api(request: Request, symbol: str):
    """API endpoint for getting predictability score"""
    try:
        symbol = symbol.upper()
        
        if symbol in DEMO_PREDICTABILITY_SCORES:
            data = DEMO_PREDICTABILITY_SCORES[symbol]
        else:
            # Generate demo data
            data = {
                "symbol": symbol,
                "predictability_score": 70.0,
                "volatility": 0.30,
                "trend_strength": 0.65,
                "confidence": 0.72,
                "risk_level": "Medium"
            }
        
        return JSONResponse({
            "status": "success",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting predictability score API: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)

@router.get("/api/ranking")
async def get_ranking_api(
    request: Request,
    sector: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=5, le=50)
):
    """API endpoint for predictability ranking"""
    try:
        all_stocks = list(DEMO_PREDICTABILITY_SCORES.values())
        
        if sector:
            all_stocks = [stock for stock in all_stocks if stock["sector"] == sector]
        
        ranked_stocks = sorted(all_stocks, key=lambda x: x["predictability_score"], reverse=True)[:limit]
        
        return JSONResponse({
            "status": "success",
            "ranking": ranked_stocks,
            "sector": sector,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting ranking API: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)

@router.get("/health")
async def predictability_health_check():
    """Health check endpoint for predictability service"""
    return {
        "status": "healthy",
        "service": "predictability",
        "timestamp": datetime.utcnow().isoformat(),
        "demo_mode": True,
        "stocks_analyzed": len(DEMO_PREDICTABILITY_SCORES),
        "sectors_available": len(SECTOR_PREDICTABILITY)
    }
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
