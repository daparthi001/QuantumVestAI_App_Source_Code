"""
QuantumVestAI API - Main Application (Enhanced)
Updated: 2025-06-19 15:34:18
Enhanced: 2025-01-09 (AI Assistant)
Author: daparthi001
"""
import os
import sys
import socket
import logging
from datetime import datetime
import json
import uuid
import asyncio

from fastapi import FastAPI, Request, HTTPException, status, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# Import enhanced core modules
from core.middleware.error_handler import ErrorHandlerMiddleware
from core.middleware.rate_limit import RateLimitMiddleware
from core.middleware.cors import configure_cors
from core.responses import create_success_response, create_error_response
from core.validation import validate_user_login, validate_stock_symbol_param, validate_pagination_params
from core.database import initialize_database, get_database_health, check_database_connection
from core.exceptions import ValidationError, AuthenticationError, NotFoundError
from routers.websocket import router as websocket_router, manager as websocket_manager

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

# Configure CORS
app = configure_cors(app)

# Add enhanced middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include WebSocket routes
app.include_router(websocket_router)

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
        # Process the request
        response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Log the response
        logger.info(f"[{request_id}] Response: {method} {path} - Status: {response.status_code} - Duration: {duration:.3f}s")
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
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
    global trending_stocks_service, broadcast_task
    
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

    broadcast_task = asyncio.create_task(trending_stock_broadcaster())
    
    # Initialize database
    if initialize_database():
        logger.info("Database initialized successfully")
    else:
        logger.warning("Database initialization failed - running in degraded mode")
    
    # Log registered routes
    route_count = 0
    for route in app.routes:
        if hasattr(route, "methods"):
            route_count += len(route.methods)
    
    logger.info(f"Registered {route_count} API endpoints")
    logger.info("Enhanced QuantumVestAI API startup complete")


# Check if this script is executed directly
if __name__ == "__main__":
    import uvicorn    uvicorn.run(app, host="0.0.0.0", port=8000)