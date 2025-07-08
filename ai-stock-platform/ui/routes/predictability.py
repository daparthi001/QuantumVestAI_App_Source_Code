"""
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


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

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
        
        return get_templates(request).TemplateResponse(
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
        )
        
    except Exception as e:
        logger.error(f"Error loading predictability analysis: {str(e)}")
        return get_templates(request).TemplateResponse(
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
        
        return get_templates(request).TemplateResponse(
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
        )
        
    except Exception as e:
        logger.error(f"Error loading predictability ranking: {str(e)}")
        return get_templates(request).TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load predictability ranking",
                "page_title": "Ranking Error"
            },
            status_code=500
        )

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
        
        return get_templates(request).TemplateResponse(
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
        return get_templates(request).TemplateResponse(
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