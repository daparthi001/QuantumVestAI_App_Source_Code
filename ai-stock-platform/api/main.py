"""
Main API Module - Updated with Authentication Fixes
Created: 2025-05-21 14:26:28
Updated: 2025-06-17 17:55:08
Author: daparthi001
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from datetime import datetime

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import settings and logger first
from core.config import settings
from core.logger import logger
from core.middleware.cors import configure_cors
from core.middleware.exception_handlers import configure_exception_handlers
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

# Setup middleware including basic middleware
setup_middleware(app)

# Configure CORS with our standardized configuration
app = configure_cors(app)

# Configure exception handlers for consistent error responses
app = configure_exception_handlers(app)

logger.info(
    "Starting API %s version %s",
    settings.PROJECT_NAME,
    settings.VERSION
)

# Register auth router WITHOUT the API prefix
# This ensures /auth/* endpoints are accessible directly
app.include_router(auth.router)
logger.debug(f"Registered auth router without API prefix")

# Register remaining routers with API prefix
API_ROUTERS = [
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
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "version": settings.VERSION
    }

# Add startup event to verify database connection
@app.on_event("startup")
async def startup_event():
    """Verify database connection on startup"""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection verified")
        
        # Log authentication routes
        logger.info("Authentication routes registered:")
        auth_paths = [route.path for route in auth.router.routes]
        for path in auth_paths:
            logger.info(f" - {path}")
            
    except Exception as e:
        logger.error("Database connection failed: %s", str(e))
        raise

# Log application startup complete
logger.info(
    "API startup complete - %s v%s",
    settings.PROJECT_NAME,
    settings.VERSION
)

# Special handling for OPTIONS requests to support CORS preflight
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """Handle OPTIONS requests for CORS preflight"""
    response = JSONResponse(content={})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PUT, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)