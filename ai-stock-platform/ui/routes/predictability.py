"""
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
        )

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
        )

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