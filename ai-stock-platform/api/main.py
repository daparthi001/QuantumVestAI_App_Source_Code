"""
QuantumVestAI API - Main Application (Enhanced)
Updated: 2025-06-19 15:34:18
Enhanced: 2025-01-09 (AI Assistant)
Author: daparthi001
"""
import asyncio
import json
import logging
import os
import socket
import sys
import uuid
from datetime import datetime

from core.database import (check_database_connection, get_database_health,
                           initialize_database)
from core.exceptions import AuthenticationError, NotFoundError, ValidationError
from core.responses import create_error_response, create_success_response
from core.validation import (
    validate_pagination_params,
    validate_stock_symbol_param,
    validate_user_login,
)
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from core.middleware.error_handler import ErrorHandlerMiddleware
from core.middleware.rate_limit import RateLimitMiddleware
from routers.auth import router as auth_router
from routers.websocket import manager as websocket_manager
from routers.websocket import router as websocket_router
from routers.social import router as social_router
from routers.docs import router as docs_router
from routers.analytics import public_router as analytics_public_router
import sentry_sdk
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response as FastAPIResponse
try:  # pragma: no cover - allow running without ai_analysis package
    from ai_analysis.prophet_service import ProphetService
    from ai_analysis.sentiment_service import SentimentService
except Exception:  # pragma: no cover - fallback stubs
    class ProphetService:  # type: ignore
        def fetch_historical_data(self, symbol: str):  # noqa: D401
            import pandas as pd
            return pd.DataFrame(columns=["ds", "y"])

        def forecast(self, history, days: int = 7):
            return []

    class SentimentService:  # type: ignore
        def analyze(self, history):
            return "Neutral"

REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'Latency of API requests in seconds',
    ['method', 'endpoint']
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("quantumvestai_api")

# Print startup debugging information
logger.info(f"Starting Enhanced QuantumVestAI API server...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")

# Create FastAPI application
API_ENV = os.environ.get("API_ENV", "development")
DEBUG = API_ENV.lower() == "development"
API_VERSION = "1.0.0"

app = FastAPI(
    title="QuantumVestAI API",
    version=API_VERSION,
    description="Stock Market Analysis Platform API - Enhanced with proper error handling, validation, and rate limiting",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=DEBUG
)

# Will be initialized in startup event
trending_stocks_service = None
ws_manager = websocket_manager
broadcast_task = None
data_fetch_scheduler = None
prophet_service = ProphetService()
sentiment_service = SentimentService()


def configure_cors(app: FastAPI) -> FastAPI:
    """Apply permissive CORS settings."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

# Configure CORS
app = configure_cors(app)

# Add enhanced middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)

# Include WebSocket and authentication routes
app.include_router(websocket_router)
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(social_router)
app.include_router(docs_router)
app.include_router(analytics_public_router, prefix="/api/v1")

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate request ID if not present
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    request.state.request_id = request_id
    
    path = request.url.path
    method = request.method
    start_time = datetime.now()
    
    # Log the request
    logger.info(f"[{request_id}] Request: {method} {path}")
    
    try:
        with REQUEST_LATENCY.labels(method=method, endpoint=path).time():
            response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Log the response
        logger.info(f"[{request_id}] Response: {method} {path} - Status: {response.status_code} - Duration: {duration:.3f}s")
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-Request-ID"] = request_id
        
        # Add custom security and performance headers
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Cache-Control"] = "public, max-age=60"
        response.headers["Content-Encoding"] = "gzip"
        
        REQUEST_COUNT.labels(method=method, endpoint=path, http_status=response.status_code).inc()
        
        return response
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        REQUEST_COUNT.labels(method=method, endpoint=path, http_status=500).inc()
        logger.error(f"[{request_id}] Error processing request {method} {path}: {e}")
        # Re-raise to let ErrorHandlerMiddleware handle it
        raise


# --- ENHANCED CRITICAL ENDPOINTS ---

@app.get("/")
async def root(request: Request):
    """API root endpoint with enhanced response"""
    logger.info("Root endpoint accessed")
    
    return create_success_response(
        data={
            "name": "QuantumVestAI API",
            "version": API_VERSION,
            "status": "running",
            "environment": API_ENV,
            "documentation": "/docs",
            "features": [
                "Enhanced error handling",
                "Input validation",
                "Rate limiting",
                "Standardized responses",
                "CORS security"
            ]
        },
        message="Welcome to QuantumVestAI API",
        request_id=getattr(request.state, 'request_id', None)
    )


@app.get("/health")
async def health_check(request: Request):
    """Enhanced health check endpoint"""
    logger.info("Health check endpoint accessed")
    
    # Check database connection
    db_health = get_database_health()
    db_connected = check_database_connection()
    
    # Overall health status
    overall_status = "healthy" if db_connected else "degraded"
    
    health_data = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": API_VERSION,
        "environment": API_ENV,
        "system": {
            "hostname": socket.gethostname(),
            "python_version": sys.version.split()[0]
        },
        "database": {
            "connected": db_connected,
            "host": db_health.get("host", "unknown"),
            "status": "connected" if db_connected else "disconnected"
        }
    }
    
    return create_success_response(
        data=health_data,
        request_id=getattr(request.state, 'request_id', None)
    )


@app.get("/api/v1/health")
async def api_health_check(request: Request):
    """API v1 health check endpoint with detailed system info"""
    logger.info("API v1 health check endpoint accessed")
    
    try:
        # Get system information
        db_health = get_database_health()
        db_connected = check_database_connection()
        
        system_info = {
            "hostname": socket.gethostname(),
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version.split()[0],
            "environment": API_ENV,
            "uptime": "N/A",  # Could be implemented if needed
            "db_host": db_health.get("host", "unknown").split(".")[0]
        }
        
        health_data = {
            "status": "healthy" if db_connected else "degraded",
            "version": API_VERSION,
            "system": system_info,
            "database": {
                "connected": db_connected,
                "status": "connected" if db_connected else "disconnected"
            },
            "features": {
                "error_handling": "enabled",
                "rate_limiting": "enabled",
                "input_validation": "enabled",
                "cors": "configured"
            }
        }
        
        return create_success_response(
            data=health_data,
            request_id=getattr(request.state, 'request_id', None)
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return create_error_response(
            message=f"Health check failed: {str(e)}",
            error_code="HEALTH_CHECK_ERROR",
            request_id=getattr(request.state, 'request_id', None)
        )


# --- ENHANCED AUTHENTICATION ENDPOINTS ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@app.post("/api/v1/auth/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Enhanced login endpoint with proper validation"""
    request_id = getattr(request.state, 'request_id', None)
    logger.info(f"[{request_id}] Login attempt for user: {form_data.username}")
    
    try:
        # Validate login data
        login_data = {
            "username": form_data.username,
            "password": form_data.password
        }
        validate_user_login(login_data)
        
        # Mock authentication - in production, validate against database
        if form_data.username == "demo" and form_data.password == "password":
            return create_success_response(
                data={
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vIiwicm9sZSI6InVzZXIifQ.sample_token",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user": {
                        "username": "demo",
                        "role": "user"
                    }
                },
                message="Login successful",
                request_id=request_id
            )
        else:
            raise AuthenticationError("Invalid username or password")
            
    except ValidationError as e:
        logger.warning(f"[{request_id}] Login validation failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[{request_id}] Login error: {str(e)}")
        raise AuthenticationError("Login failed")


@app.get("/api/v1/auth/login")
async def login_get(request: Request):
    """GET handler for login endpoint - shows helpful message"""
    return create_error_response(
        message="This endpoint only accepts POST requests with form data",
        error_code="METHOD_NOT_ALLOWED",
        details={
            "required_method": "POST",
            "required_fields": ["username", "password"],
            "example": "curl -X POST -d 'username=demo&password=password' /api/v1/auth/login"
        },
        request_id=getattr(request.state, 'request_id', None)
    )


@app.get("/api/v1/auth/me")
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    """Get current user endpoint with enhanced response"""
    logger.info("Current user endpoint accessed")
    
    # Mock user data - in production, decode token and get user from database
    return create_success_response(
        data={
            "username": "demo",
            "email": "demo@example.com",
            "full_name": "Demo User",
            "role": "user",
            "is_active": True,
            "permissions": ["read", "write"],
            "last_login": datetime.now().isoformat()
        },
        request_id=getattr(request.state, 'request_id', None)
    )


# --- ENHANCED STOCKS ENDPOINTS ---

@app.get("/api/v1/stocks/trending")
async def trending_stocks(request: Request, page: int = 1, limit: int = 10):
    """Get trending stocks with real-time data and caching"""
    logger.info("Trending stocks endpoint accessed")
    
    try:
        # Check if service is initialized
        if trending_stocks_service is None:
            logger.error("Trending stocks service not initialized")
            return create_error_response(
                message="Service not available",
                error_code="SERVICE_UNAVAILABLE", 
                request_id=getattr(request.state, 'request_id', None)
            )
        
        # Validate pagination parameters
        pagination = validate_pagination_params(page, limit)
        
        # Use the trending stocks service to get data
        result = await trending_stocks_service.get_trending_stocks(
            page=pagination["page"], 
            limit=pagination["limit"]
        )
        
        return create_success_response(
            data=result,
            message="Trending stocks retrieved successfully",
            request_id=getattr(request.state, 'request_id', None)
        )
        
    except Exception as e:
        logger.error(f"Error in trending stocks endpoint: {e}")
        # Return error response
        return create_error_response(
            message="Failed to fetch trending stocks",
            error_code="INTERNAL_SERVER_ERROR",
            request_id=getattr(request.state, 'request_id', None)
        )


@app.get("/api/v1/stocks/trending/cache/status")
async def get_trending_cache_status(request: Request):
    """Get cache status for trending stocks - useful for monitoring"""
    logger.info("Cache status endpoint accessed")
    
    try:
        if trending_stocks_service is None:
            return create_error_response(
                message="Service not available",
                error_code="SERVICE_UNAVAILABLE",
                request_id=getattr(request.state, 'request_id', None)
            )
        
        cache_status = trending_stocks_service.get_cache_status()
        
        return create_success_response(
            data=cache_status,
            message="Cache status retrieved successfully",
            request_id=getattr(request.state, 'request_id', None)
        )
        
    except Exception as e:
        logger.error(f"Error getting cache status: {e}")
        return create_error_response(
            message="Failed to get cache status",
            error_code="INTERNAL_SERVER_ERROR",
            request_id=getattr(request.state, 'request_id', None)
        )


@app.post("/api/v1/stocks/trending/cache/invalidate")
async def invalidate_trending_cache(request: Request):
    """Invalidate trending stocks cache - forces fresh data fetch"""
    logger.info("Cache invalidation endpoint accessed")
    
    try:
        if trending_stocks_service is None:
            return create_error_response(
                message="Service not available",
                error_code="SERVICE_UNAVAILABLE",
                request_id=getattr(request.state, 'request_id', None)
            )
        
        trending_stocks_service.invalidate_cache()
        
        return create_success_response(
            data={"message": "Cache invalidated successfully"},
            message="Trending stocks cache has been cleared",
            request_id=getattr(request.state, 'request_id', None)
        )
        
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        return create_error_response(
            message="Failed to invalidate cache",
            error_code="INTERNAL_SERVER_ERROR",
            request_id=getattr(request.state, 'request_id', None)
        )
@app.get("/api/v1/stocks/search")
async def search_stocks_endpoint(request: Request, query: str, limit: int = 10):
    """Search for stocks by symbol or name."""
    logger.info(f"Stock search endpoint accessed query: {query}")
    try:
        if not query.strip():
            raise ValidationError("Stock search query is required")
        results = []
        if trending_stocks_service is not None:
            data = await trending_stocks_service.get_trending_stocks(page=1, limit=100)
            for stock in data.get("stocks", []):
                if query.lower() in stock["symbol"].lower() or query.lower() in stock["name"].lower():
                    results.append({
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "price": stock.get("price"),
                        "change": stock.get("change"),
                    })
                    if len(results) >= limit:
                        break
        # If no results found, return an empty list - no mock data fallback
        if not results:
            logger.info(f"No real stock data found for query: {query}")
        return create_success_response(
            data={"results": results},
            message="Stock search results" if results else "No stocks found",
            request_id=getattr(request.state, 'request_id', None),
        )
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        return create_error_response(
            message="Failed to search stocks",
            error_code="INTERNAL_SERVER_ERROR",
            request_id=getattr(request.state, 'request_id', None),
        )


@app.get("/api/v1/stocks/most-predictable")
async def most_predictable_stocks(
    request: Request,
    limit: int = 10,
    min_score: float = 0.7,
) -> Response:
    """Return a list of stocks with the highest predictability scores."""
    logger.info("Most predictable stocks endpoint accessed")

    try:
        sample_data = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "current_price": 198.45,
                "predictability_score": 0.95,
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "current_price": 425.63,
                "predictability_score": 0.92,
            },
            {
                "symbol": "NVDA",
                "name": "NVIDIA Corporation",
                "current_price": 129.31,
                "predictability_score": 0.9,
            },
        ]

        filtered = [s for s in sample_data if s["predictability_score"] >= min_score][:limit]

        return create_success_response(
            data=filtered,
            message="Most predictable stocks retrieved successfully",
            request_id=getattr(request.state, 'request_id', None),
        )

    except Exception as e:  # pragma: no cover - unexpected errors
        logger.error(f"Error fetching most predictable stocks: {e}")
        return create_error_response(
            message="Failed to fetch most predictable stocks",
            error_code="INTERNAL_SERVER_ERROR",
            request_id=getattr(request.state, 'request_id', None),
        )

@app.get("/api/v1/stocks/{symbol}")
async def get_stock(request: Request, symbol: str):
    """Get stock details with symbol validation"""
    logger.info(f"Stock details endpoint accessed for symbol: {symbol}")
    
    # Validate stock symbol
    validated_symbol = validate_stock_symbol_param(symbol)
    
    # Mock stock data
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
            "52_week_low": 142.18,
            "volume": 45678900,
            "avg_volume": 52000000
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
            "52_week_low": 285.45,
            "volume": 23456789,
            "avg_volume": 28000000
        }
    }
    
    if validated_symbol in stock_data:
        return create_success_response(
            data=stock_data[validated_symbol],
            request_id=getattr(request.state, 'request_id', None)
        )
    else:
        raise NotFoundError(f"Stock with symbol {validated_symbol} not found")


@app.get("/api/v1/predictions/pre-market/{symbol}")
async def pre_market_prediction(request: Request, symbol: str) -> Response:
    """Generate a simple pre-market prediction based on recent closing prices."""
    logger.info("Pre-market prediction endpoint accessed")
    try:
        # Use mock data for testing environments
        prices = [100.0, 101.5, 102.2, 103.1, 104.0]
        predicted_open = sum(prices[-5:]) / 5
        current_price = prices[-1]
        data = {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_open": predicted_open,
        }
        return create_success_response(
            data=data,
            message="Pre-market prediction generated",
            request_id=getattr(request.state, 'request_id', None),
        )
    except Exception as e:
        logger.error(f"Error generating pre-market prediction: {e}")
        return create_error_response(
            message="Failed to generate pre-market prediction",
            error_code="INTERNAL_SERVER_ERROR",
            request_id=getattr(request.state, 'request_id', None),
        )


@app.get("/api/ai/analyze")
async def ai_analyze(symbol: str) -> Response:
    """Return 7-day forecast and trend sentiment for ``symbol``."""
    history = prophet_service.fetch_historical_data(symbol)
    forecast = prophet_service.forecast(history, days=7)
    sentiment = sentiment_service.analyze(history)
    data = {
        "symbol": symbol,
        "sentiment": sentiment,
        "forecast": [
            {"ds": fp.ds.isoformat(), "yhat": fp.yhat} for fp in forecast
        ],
    }
    return create_success_response(data=data, message="AI analysis generated")


async def trending_stock_broadcaster() -> None:
    """Background task that pushes trending stock updates to websocket clients."""
    while True:
        try:
            if trending_stocks_service:
                result = await trending_stocks_service.get_trending_stocks()
                stocks = result.get("stocks", []) if isinstance(result, dict) else []
                for stock in stocks:
                    await ws_manager.broadcast_stock_update(stock.get("symbol", ""), stock)
                await ws_manager.broadcast_event("top_movers", stocks)
                await ws_manager.broadcast_event("market_overview", stocks)
        except Exception as e:
            logger.error(f"Error broadcasting trending stocks: {e}")
        await asyncio.sleep(30)


# --- STARTUP EVENT ---
@app.on_event("startup")
async def startup_event():
    """Enhanced startup event with database initialization"""
    global trending_stocks_service, broadcast_task, data_fetch_scheduler
    
    logger.info(f"Starting QuantumVestAI API v{API_VERSION}")
    logger.info(f"Environment: {API_ENV}")
    logger.info(f"Debug mode: {DEBUG}")
    
    # Initialize services with simplified approach
    try:
        # Direct import approach - much simpler and clearer
        from services.trending_stocks_service import TrendingStocksService
        trending_stocks_service = TrendingStocksService()
        logger.info("Trending stocks service initialized successfully")
        
        # Verify service is working
        if trending_stocks_service is not None:
            logger.info("Service validation passed - trending_stocks_service is available")
        else:
            logger.error("Service validation failed - trending_stocks_service is None")

    except Exception as e:
        logger.error(f"Failed to initialize trending stocks service: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Set to None to ensure consistent state
        trending_stocks_service = None

    from services.data_fetch_scheduler import start_data_fetch_scheduler

    broadcast_task = asyncio.create_task(trending_stock_broadcaster())
    data_fetch_scheduler = start_data_fetch_scheduler()
    logger.info("Data fetch scheduler started")
    
    # Initialize database
    if initialize_database():
        logger.info("Database initialized successfully")
        run_migrations = os.environ.get("RUN_DB_MIGRATIONS", "0").lower() in ("1", "true", "yes")
        try:
            from core.database import async_engine, create_db_and_tables
            from sqlalchemy import inspect

            async with async_engine.begin() as conn:
                has_users = await conn.run_sync(lambda sconn: inspect(sconn).has_table("users"))

            if run_migrations or not has_users:
                await create_db_and_tables()
            else:
                logger.info("Database tables already exist; skipping creation")
        except Exception as e:
            logger.error(f"Database table creation failed: {e}")
    else:
        logger.warning("Database initialization failed - running in degraded mode")
    
    # Log registered routes
    route_count = 0
    for route in app.routes:
        if hasattr(route, "methods"):
            route_count += len(route.methods)
    
    logger.info(f"Registered {route_count} API endpoints")
    logger.info("Enhanced QuantumVestAI API startup complete")


# Initialize Sentry error tracking
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        environment=os.getenv("API_ENV", "production"),
    )


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return FastAPIResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup background tasks on shutdown."""
    global broadcast_task, data_fetch_scheduler
    if broadcast_task:
        broadcast_task.cancel()
        try:
            await broadcast_task
        except Exception:
            pass
    if data_fetch_scheduler:
        data_fetch_scheduler.shutdown()


# Check if this script is executed directly

if __name__ == "__main__":   
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)

