"""
QuantumVestAI Forecast Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json

# Setup router
router = APIRouter(prefix="/forecast", tags=["forecast"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# Demo forecast data
DEMO_PREDICTIONS = {
    "AAPL": {
        "current_price": 185.50,
        "predictions": {
            "7d": {"price": 192.75, "confidence": 0.78, "trend": "bullish", "probability": 0.73},
            "30d": {"price": 198.25, "confidence": 0.72, "trend": "bullish", "probability": 0.68},
            "90d": {"price": 205.50, "confidence": 0.65, "trend": "bullish", "probability": 0.61}
        },
        "models": {
            "LSTM": {"price": 194.20, "confidence": 0.75, "accuracy": 0.82},
            "Prophet": {"price": 191.30, "confidence": 0.80, "accuracy": 0.78},
            "XGBoost": {"price": 196.15, "confidence": 0.73, "accuracy": 0.79},
            "Ensemble": {"price": 193.88, "confidence": 0.76, "accuracy": 0.80}
        },
        "factors": {
            "technical": {"score": 7.2, "signals": ["MA_BULLISH", "RSI_OVERSOLD"]},
            "fundamental": {"score": 8.1, "factors": ["STRONG_EARNINGS", "GROWTH_OUTLOOK"]},
            "sentiment": {"score": 6.8, "sentiment": "positive", "news_count": 45}
        }
    },
    "MSFT": {
        "current_price": 365.25,
        "predictions": {
            "7d": {"price": 371.80, "confidence": 0.81, "trend": "bullish", "probability": 0.76},
            "30d": {"price": 378.50, "confidence": 0.74, "trend": "bullish", "probability": 0.71},
            "90d": {"price": 385.75, "confidence": 0.68, "trend": "bullish", "probability": 0.64}
        },
        "models": {
            "LSTM": {"price": 372.45, "confidence": 0.78, "accuracy": 0.84},
            "Prophet": {"price": 370.25, "confidence": 0.82, "accuracy": 0.81},
            "XGBoost": {"price": 375.90, "confidence": 0.76, "accuracy": 0.83},
            "Ensemble": {"price": 372.87, "confidence": 0.79, "accuracy": 0.83}
        },
        "factors": {
            "technical": {"score": 7.8, "signals": ["MOMENTUM_STRONG", "VOLUME_INCREASE"]},
            "fundamental": {"score": 8.5, "factors": ["CLOUD_GROWTH", "AI_LEADERSHIP"]},
            "sentiment": {"score": 7.5, "sentiment": "positive", "news_count": 38}
        }
    },
    "GOOGL": {
        "current_price": 134.56,
        "predictions": {
            "7d": {"price": 138.20, "confidence": 0.72, "trend": "bullish", "probability": 0.67},
            "30d": {"price": 142.15, "confidence": 0.69, "trend": "bullish", "probability": 0.63},
            "90d": {"price": 148.30, "confidence": 0.62, "trend": "bullish", "probability": 0.58}
        },
        "models": {
            "LSTM": {"price": 139.85, "confidence": 0.71, "accuracy": 0.77},
            "Prophet": {"price": 136.90, "confidence": 0.75, "accuracy": 0.74},
            "XGBoost": {"price": 140.65, "confidence": 0.68, "accuracy": 0.76},
            "Ensemble": {"price": 139.13, "confidence": 0.71, "accuracy": 0.76}
        },
        "factors": {
            "technical": {"score": 6.9, "signals": ["SUPPORT_LEVEL", "BULLISH_PATTERN"]},
            "fundamental": {"score": 7.8, "factors": ["AD_REVENUE_GROWTH", "SEARCH_DOMINANCE"]},
            "sentiment": {"score": 6.5, "sentiment": "neutral", "news_count": 32}
        }
    }
}

MARKET_SENTIMENT = {
    "overall": {
        "score": 72,
        "trend": "bullish",
        "confidence": 0.74,
        "factors": ["Fed_Policy_Stable", "Earnings_Strong", "Economic_Data_Positive"]
    },
    "sectors": {
        "Technology": {"score": 78, "trend": "bullish"},
        "Healthcare": {"score": 65, "trend": "neutral"},
        "Finance": {"score": 70, "trend": "bullish"}, 
        "Energy": {"score": 82, "trend": "very_bullish"},
        "Consumer": {"score": 68, "trend": "neutral"}
    },
    "risk_factors": [
        {"factor": "Inflation", "impact": "medium", "probability": 0.35},
        {"factor": "Geopolitical", "impact": "low", "probability": 0.20},
        {"factor": "Interest_Rates", "impact": "medium", "probability": 0.40}
    ]
}

@router.get("/", response_class=HTMLResponse)
async def forecast_home(request: Request):
    """Main forecast dashboard page"""
    try:
        logger.info("Loading forecast dashboard in demo mode")
        
        # Get top predictions
        top_predictions = []
        for symbol, data in DEMO_PREDICTIONS.items():
            pred_30d = data["predictions"]["30d"]
            top_predictions.append({
                "symbol": symbol,
                "current_price": data["current_price"],
                "predicted_price": pred_30d["price"],
                "confidence": pred_30d["confidence"],
                "trend": pred_30d["trend"],
                "change_pct": ((pred_30d["price"] - data["current_price"]) / data["current_price"]) * 100
            })
        
        # Sort by confidence
        top_predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return get_templates(request).TemplateResponse(
            "forecast.html",
            {
                "request": request,
                "demo_mode": True,
                "predictions": top_predictions,
                "market_sentiment": MARKET_SENTIMENT,
                "featured_stocks": ["AAPL", "MSFT", "GOOGL"],
                "page_title": "AI Forecast - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading forecast dashboard: {str(e)}")
        return get_templates(request).TemplateResponse(
            "forecast.html",
            {
                "request": request,
                "demo_mode": True,
                "predictions": [],
                "market_sentiment": {},
                "featured_stocks": [],
                "error": f"Error loading forecast dashboard: {str(e)}",
                "page_title": "Forecast Error"
            },
            status_code=500
        )

@router.get("/stock/{symbol}", response_class=HTMLResponse)
async def stock_forecast(
    request: Request, 
    symbol: str,
    timeframe: str = Query("30d", description="Forecast timeframe: 7d, 30d, 90d")
):
    """Individual stock forecast page"""
    try:
        symbol = symbol.upper()
        logger.info(f"Loading forecast for {symbol} with timeframe {timeframe}")
        
        if symbol not in DEMO_PREDICTIONS:
            # Generate demo data for any symbol
            base_price = 100.0
            demo_data = {
                "current_price": base_price,
                "predictions": {
                    "7d": {"price": base_price * 1.02, "confidence": 0.70, "trend": "bullish", "probability": 0.65},
                    "30d": {"price": base_price * 1.05, "confidence": 0.65, "trend": "bullish", "probability": 0.60},
                    "90d": {"price": base_price * 1.08, "confidence": 0.60, "trend": "bullish", "probability": 0.55}
                },
                "models": {
                    "LSTM": {"price": base_price * 1.04, "confidence": 0.68, "accuracy": 0.75},
                    "Prophet": {"price": base_price * 1.03, "confidence": 0.72, "accuracy": 0.73},
                    "XGBoost": {"price": base_price * 1.06, "confidence": 0.65, "accuracy": 0.77},
                    "Ensemble": {"price": base_price * 1.04, "confidence": 0.68, "accuracy": 0.75}
                },
                "factors": {
                    "technical": {"score": 6.5, "signals": ["NEUTRAL"]},
                    "fundamental": {"score": 7.0, "factors": ["STABLE"]},
                    "sentiment": {"score": 6.0, "sentiment": "neutral", "news_count": 15}
                }
            }
        else:
            demo_data = DEMO_PREDICTIONS[symbol]
        
        # Get prediction for requested timeframe
        if timeframe in demo_data["predictions"]:
            prediction = demo_data["predictions"][timeframe]
        else:
            prediction = demo_data["predictions"]["30d"]
        
        # Generate historical chart data
        historical_data = []
        current_price = demo_data["current_price"]
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
            price = current_price * (0.95 + (i * 0.003) + (0.02 * (i % 7 - 3) / 10))
            historical_data.append({"date": date, "price": round(price, 2)})
        
        return get_templates(request).TemplateResponse(
            "forecast_detail.html",
            {
                "request": request,
                "symbol": symbol,
                "timeframe": timeframe,
                "demo_mode": True,
                "stock_data": demo_data,
                "prediction": prediction,
                "historical_data": historical_data,
                "page_title": f"{symbol} Forecast - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading stock forecast for {symbol}: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Unable to load forecast for {symbol}",
                "page_title": "Forecast Error"
            },
            status_code=500
        )

@router.get("/models", response_class=HTMLResponse)
async def model_comparison(request: Request):
    """Model comparison page"""
    try:
        # Demo model performance data
        model_performance = {
            "LSTM": {
                "accuracy": 0.82,
                "precision": 0.79,
                "recall": 0.84,
                "f1_score": 0.81,
                "description": "Long Short-Term Memory neural network optimized for time series prediction"
            },
            "Prophet": {
                "accuracy": 0.78,
                "precision": 0.81,
                "recall": 0.76,
                "f1_score": 0.78,
                "description": "Facebook's time series forecasting model with trend and seasonality components"
            },
            "XGBoost": {
                "accuracy": 0.79,
                "precision": 0.77,
                "recall": 0.82,
                "f1_score": 0.79,
                "description": "Gradient boosting framework optimized for structured data"
            },
            "Ensemble": {
                "accuracy": 0.83,
                "precision": 0.82,
                "recall": 0.85,
                "f1_score": 0.83,
                "description": "Combined model using weighted predictions from all individual models"
            }
        }
        
        return get_templates(request).TemplateResponse(
            "model_comparison.html",
            {
                "request": request,
                "demo_mode": True,
                "models": model_performance,
                "page_title": "Model Comparison - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading model comparison: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load model comparison data",
                "page_title": "Model Comparison Error"
            },
            status_code=500
        )

@router.get("/api/predictions", response_class=dict)
async def get_predictions_api(
    request: Request,
    symbols: Optional[str] = Query(None, description="Comma-separated stock symbols"),
    timeframe: str = Query("30d", description="Forecast timeframe")
):
    """API endpoint for getting forecast predictions"""
    try:
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
        else:
            symbol_list = list(DEMO_PREDICTIONS.keys())
        
        predictions = {}
        for symbol in symbol_list[:10]:  # Limit to 10 symbols
            if symbol in DEMO_PREDICTIONS:
                data = DEMO_PREDICTIONS[symbol]
                if timeframe in data["predictions"]:
                    predictions[symbol] = {
                        "current_price": data["current_price"],
                        "prediction": data["predictions"][timeframe],
                        "models": data["models"]
                    }
        
        return {
            "status": "success",
            "predictions": predictions,
            "timeframe": timeframe,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting predictions API: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/api/market-sentiment", response_class=dict)
async def get_market_sentiment_api(request: Request):
    """API endpoint for current market sentiment"""
    try:
        return {
            "status": "success",
            "sentiment": MARKET_SENTIMENT,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market sentiment: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/health")
async def forecast_health_check():
    """Health check endpoint for forecast service"""
    return {
        "status": "healthy",
        "service": "forecast",
        "timestamp": datetime.utcnow().isoformat(),
        "demo_mode": True,
        "models_available": ["LSTM", "Prophet", "XGBoost", "Ensemble"],
        "predictions_count": len(DEMO_PREDICTIONS)
    }