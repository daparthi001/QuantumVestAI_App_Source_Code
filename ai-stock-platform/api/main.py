"""
QuantumVestAI API - Main Application
Updated: 2025-06-19 04:35:11
Author: daparthi001
"""
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime
import logging
import os
import socket
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("quantumvestai_api")

# Create FastAPI application with debug option
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
    "http://localhost:3000",
    "https://dev.quantumvestai.com",
    "https://quantumvestai.com",
    "*"  # Remove in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip middleware for compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

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

# --- CRITICAL ENDPOINTS: DIRECT DEFINITIONS ---

@app.get("/")
async def root():
    """API root endpoint"""
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

# Fix for forecast endpoint
@app.get("/api/v1/forecast")
async def forecast():
    """Temporary endpoint for forecast data"""
    logger.info("Forecast endpoint accessed")
    return {
        "status": "success",
        "data": {
            "forecast_date": datetime.now().isoformat(),
            "market_outlook": "bullish",
            "top_picks": ["AAPL", "MSFT", "GOOGL"]
        }
    }

# --- ROUTERS IMPORT AND REGISTRATION ---
# Import routers here to avoid circular imports
from api.routers import auth, stocks, predictions, users, watchlists, analytics, sentiment, backtest

# Include routers with explicit prefixes
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(stocks.router, prefix="/api/v1/stocks")
app.include_router(predictions.router, prefix="/api/v1/predictions")
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(watchlists.router, prefix="/api/v1/watchlists")
app.include_router(analytics.router, prefix="/api/v1/analytics")
app.include_router(sentiment.router, prefix="/api/v1/sentiment")
app.include_router(backtest.router, prefix="/api/v1/backtest")

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

# --- STARTUP AND SHUTDOWN EVENTS ---
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

# No need for if __name__ == "__main__" block since this is run by uvicorn directly