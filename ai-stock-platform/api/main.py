"""
QuantumVestAI API - Main Application
Updated: 2025-06-19 15:34:18
Author: daparthi001
"""
import os
import sys
import socket
import logging
from datetime import datetime
import json

from fastapi import FastAPI, Request, HTTPException, status, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("quantumvestai_api")

# Print startup debugging information
logger.info(f"Starting API server (FIXED VERSION)...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"System path: {sys.path}")

# Create FastAPI application
API_ENV = os.environ.get("API_ENV", "development")
DEBUG = API_ENV.lower() == "development"
API_VERSION = "1.0.0"

app = FastAPI(
    title="QuantumVestAI API",
    version=API_VERSION,
    description="Stock Market Analysis Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=DEBUG
)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",  # React development server
    "http://localhost:5173",  # Vite development server
    "https://quantumvestai.com",
    "https://www.quantumvestai.com",
    "https://dev.quantumvestai.com", 
    "http://dev.quantumvestai.com",   # Include HTTP version
    "*"  # Remove in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "Accept"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Log requests middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    path = request.url.path
    method = request.method
    start_time = datetime.now()
    
    # Log the request
    logger.info(f"Request: {method} {path}")
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Log the response
        logger.info(f"Response: {method} {path} - Status: {response.status_code} - Duration: {duration:.3f}s")
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        return response
    except Exception as e:
        logger.error(f"Error processing request {method} {path}: {e}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Response: {method} {path} - Status: 500 - Duration: {duration:.3f}s")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={"detail": str(e)}
        )

# --- CRITICAL ENDPOINTS ---

@app.get("/")
async def root():
    """API root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "name": "QuantumVestAI API",
        "version": API_VERSION,
        "status": "running",
        "environment": API_ENV,
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint for Kubernetes probes"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def api_health_check():
    """API v1 health check endpoint"""
    logger.info("API v1 health check endpoint accessed")
    try:
        # Basic system information
        system_info = {
            "hostname": socket.gethostname(),
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "environment": API_ENV,
            "db_host": os.environ.get("DB_HOST", "unknown").split(".")[0]  # Only include first part of hostname for security
        }
        
        return {
            "status": "healthy",
            "version": API_VERSION,
            "system": system_info
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Import routers
try:
    from routers.v1 import router as v1_router
    app.include_router(v1_router)
    logger.info("Included v1 router")
except ImportError as e:
    logger.error(f"Could not import v1 router: {e}")

# Try to import routes if they exist, with graceful fallback
try:
    from routes.sentiment import router as sentiment_router
    app.include_router(sentiment_router)
    logger.info("Included sentiment router")
except ImportError as e:
    logger.warning(f"Could not import sentiment router: {e}")

try:
    from routes.admin import router as admin_router
    app.include_router(admin_router)
    logger.info("Included admin router")
except ImportError as e:
    logger.warning(f"Could not import admin router: {e}")

try:
    from routes.whitepaper_analysis import router as whitepaper_router
    app.include_router(whitepaper_router)
    logger.info("Included whitepaper router")
except ImportError as e:
    logger.warning(f"Could not import whitepaper router: {e}")

# --- BUILT-IN ENDPOINTS ---

@app.get("/api/v1/forecast")
async def forecast():
    """Forecast endpoint"""
    logger.info("Forecast endpoint accessed")
    return {
        "status": "success",
        "data": {
            "forecast_date": datetime.now().isoformat(),
            "market_outlook": "bullish",
            "top_picks": ["AAPL", "MSFT", "GOOGL"],
            "market_trends": [
                {"sector": "Technology", "trend": "positive", "change_percent": 2.3},
                {"sector": "Healthcare", "trend": "neutral", "change_percent": 0.5},
                {"sector": "Finance", "trend": "positive", "change_percent": 1.7}
            ]
        }
    }

# --- AUTHENTICATION ENDPOINTS ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

@app.post("/api/v1/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    logger.info(f"Login attempt for user: {form_data.username}")
    
    # This is a mock implementation - in production, you'd validate against your database
    if form_data.username == "demo" and form_data.password == "password":
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vIiwicm9sZSI6InVzZXIifQ.sample_token",
                "token_type": "bearer"
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Add OPTIONS handler for login endpoint
@app.options("/api/v1/auth/login")
async def login_options():
    """Handle CORS preflight requests for login endpoint"""
    return Response(status_code=200)

@app.get("/api/v1/auth/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user endpoint"""
    logger.info("Current user endpoint accessed")
    return {
        "status": "success",
        "data": {
            "username": "demo",
            "email": "demo@example.com",
            "full_name": "Demo User",
            "role": "user",
            "is_active": True
        }
    }

# --- STOCKS ENDPOINTS ---

@app.get("/api/v1/stocks/trending")
async def trending_stocks():
    """Get trending stocks"""
    logger.info("Trending stocks endpoint accessed")
    return {
        "status": "success",
        "data": [
            {"symbol": "AAPL", "name": "Apple Inc.", "change_percent": 2.1, "price": 198.45},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "change_percent": 1.8, "price": 425.63},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "change_percent": 1.5, "price": 187.12},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "change_percent": 1.2, "price": 176.89},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "change_percent": 3.2, "price": 1024.78}
        ]
    }

@app.get("/api/v1/stocks/{symbol}")
async def get_stock(symbol: str):
    """Get stock details"""
    logger.info(f"Stock details endpoint accessed for symbol: {symbol}")
    
    # Mock data for demo purposes
    stock_data = {
        "AAPL": {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 198.45,
            "change": 4.12,
            "change_percent": 2.1,
            "market_cap": "3.12T",
            "pe_ratio": 32.5,
            "dividend_yield": 0.53,
            "52_week_high": 205.87,
            "52_week_low": 142.18
        },
        "MSFT": {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "price": 425.63,
            "change": 7.56,
            "change_percent": 1.8,
            "market_cap": "3.16T",
            "pe_ratio": 37.1,
            "dividend_yield": 0.72,
            "52_week_high": 430.82,
            "52_week_low": 285.45
        }
    }
    
    if symbol.upper() in stock_data:
        return {
            "status": "success",
            "data": stock_data[symbol.upper()]
        }
    else:
        return {
            "status": "error",
            "message": f"Stock with symbol {symbol} not found",
            "data": None
        }

# --- PREDICTIONS ENDPOINTS ---

@app.get("/api/v1/predictions/{symbol}")
async def get_prediction(symbol: str):
    """Get stock price prediction"""
    logger.info(f"Prediction endpoint accessed for symbol: {symbol}")
    return {
        "status": "success",
        "data": {
            "symbol": symbol.upper(),
            "current_price": 198.45 if symbol.upper() == "AAPL" else 425.63,
            "prediction_date": datetime.now().isoformat(),
            "predictions": [
                {"date": "2025-06-20", "price": 201.23, "confidence": 0.85},
                {"date": "2025-06-21", "price": 203.45, "confidence": 0.82},
                {"date": "2025-06-22", "price": 205.12, "confidence": 0.78},
                {"date": "2025-06-23", "price": 204.87, "confidence": 0.75},
                {"date": "2025-06-24", "price": 206.54, "confidence": 0.72}
            ],
            "recommendation": "buy",
            "confidence_score": 0.85,
            "analysis": "Strong upward trend based on technical indicators and positive market sentiment."
        }
    }

# --- WATCHLISTS ENDPOINTS ---

@app.get("/api/v1/watchlists")
async def get_watchlists(token: str = Depends(oauth2_scheme)):
    """Get user watchlists"""
    logger.info("Watchlists endpoint accessed")
    return {
        "status": "success",
        "data": [
            {
                "id": 1,
                "name": "Tech Stocks",
                "stocks": [
                    {"symbol": "AAPL", "name": "Apple Inc.", "price": 198.45, "change_percent": 2.1},
                    {"symbol": "MSFT", "name": "Microsoft Corporation", "price": 425.63, "change_percent": 1.8},
                    {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": 176.89, "change_percent": 1.2}
                ]
            },
            {
                "id": 2,
                "name": "Green Energy",
                "stocks": [
                    {"symbol": "TSLA", "name": "Tesla, Inc.", "price": 248.12, "change_percent": -0.8},
                    {"symbol": "ENPH", "name": "Enphase Energy, Inc.", "price": 113.56, "change_percent": 1.5}
                ]
            }
        ]
    }

# --- SENTIMENT ENDPOINTS ---

@app.get("/api/v1/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    """Get market sentiment for a stock"""
    logger.info(f"Sentiment endpoint accessed for symbol: {symbol}")
    return {
        "status": "success",
        "data": {
            "symbol": symbol.upper(),
            "overall_sentiment": "positive",
            "sentiment_score": 0.78,
            "date": datetime.now().isoformat(),
            "sources": {
                "news": 0.82,
                "social_media": 0.76,
                "analyst_ratings": 0.74
            },
            "recent_changes": {
                "1_day": 0.03,
                "1_week": 0.07,
                "1_month": 0.12
            }
        }
    }

# --- ANALYTICS ENDPOINTS ---

@app.get("/api/v1/analytics/market-overview")
async def market_overview():
    """Get market overview analytics"""
    logger.info("Market overview endpoint accessed")
    return {
        "status": "success",
        "data": {
            "date": datetime.now().isoformat(),
            "indices": [
                {"name": "S&P 500", "value": 5421.53, "change_percent": 0.8},
                {"name": "Nasdaq", "value": 17658.23, "change_percent": 1.2},
                {"name": "Dow Jones", "value": 39875.12, "change_percent": 0.5}
            ],
            "sectors": [
                {"name": "Technology", "change_percent": 1.4},
                {"name": "Healthcare", "change_percent": 0.3},
                {"name": "Finance", "change_percent": 0.7},
                {"name": "Energy", "change_percent": -0.2},
                {"name": "Consumer Staples", "change_percent": 0.1}
            ],
            "market_sentiment": "bullish",
            "volatility_index": 15.3
        }
    }

# --- BACKTEST ENDPOINTS ---

@app.post("/api/v1/backtest")
async def run_backtest(token: str = Depends(oauth2_scheme)):
    """Run a backtest on a trading strategy"""
    logger.info("Backtest endpoint accessed")
    return {
        "status": "success",
        "data": {
            "strategy_id": "momentum_strategy_v1",
            "start_date": "2024-01-01",
            "end_date": "2025-06-01",
            "initial_capital": 100000,
            "final_capital": 124567.89,
            "total_return": 24.57,
            "annualized_return": 16.8,
            "sharpe_ratio": 1.45,
            "max_drawdown": -8.2,
            "trades": 78,
            "winning_trades": 52,
            "losing_trades": 26,
            "win_rate": 66.7
        }
    }

# --- ERROR HANDLING ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

# --- STARTUP EVENT ---
@app.on_event("startup")
async def startup_event():
    """Log app startup and registered routes"""
    logger.info(f"Starting QuantumVestAI API v{API_VERSION}")
    logger.info(f"Environment: {API_ENV}")
    logger.info(f"Debug mode: {DEBUG}")
    
    # Log all registered routes
    route_paths = []
    for route in app.routes:
        methods = getattr(route, "methods", {"GET"})
        for method in methods:
            route_paths.append(f"{method} {route.path}")
    
    logger.info(f"Registered routes: {route_paths}")

# Check if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)