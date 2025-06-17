"""
Main API Module
Created: 2025-05-21 14:26:28
Updated: 2025-06-17 01:50:11
Author: daparthi001
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import settings and logger first
from core.config import settings
from core.logger import logger

# Then import database
from db.session import engine, SessionLocal, get_db

# Import middleware and routers
from core.middleware import setup_middleware
from routers import (
    auth,
    stocks,
    users,
    forecast,
    watchlist,
    admin,
    sentiment,
    data,
    whitepaper
)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="QuantumVestAI Stock Market Analysis Platform API",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Setup middleware including CORS for cross-container communication
setup_middleware(app)

# Add explicit CORS middleware with more permissive settings for UI container
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual UI domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(
    "Starting API %s version %s",
    settings.PROJECT_NAME,
    settings.VERSION
)

# Register all routers with API prefix
API_ROUTERS = [
    auth.router,
    users.router,
    stocks.router,
    forecast.router,
    watchlist.router,
    admin.router,
    sentiment.router,
    data.router,
    whitepaper.router
]

for router in API_ROUTERS:
    app.include_router(
        router,
        prefix=f"{settings.API_V1_STR}"
    )
    logger.debug(f"Registered router: {router.prefix} at {settings.API_V1_STR}{router.prefix}")

@app.get("/")
async def api_root():
    """API Root endpoint - provides basic information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "QuantumVestAI Stock Market Analysis Platform API",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-06-17 01:50:11",
        "version": settings.VERSION
    }

# Error handling
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "message": "The requested API resource was not found",
            "path": request.url.path,
            "timestamp": "2025-06-17 01:50:11"
        }
    )

# Add startup event to verify database connection
@app.on_event("startup")
async def startup_event():
    """Verify database connection on startup"""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection verified")
    except Exception as e:
        logger.error("Database connection failed: %s", str(e))
        raise

# Log application startup complete
logger.info(
    "API startup complete - %s v%s",
    settings.PROJECT_NAME,
    settings.VERSION
)