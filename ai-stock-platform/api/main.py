"""
Main API Module
Created: 2025-05-21 14:26:28
Updated: 2025-06-16 23:40:22
Author: daparthi001
"""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import settings and logger first
from core.config import settings
from core.logger import logger

# Then import database
from db.session import engine, SessionLocal

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
    description="QuantumVestAI Stock Market Analysis Platform",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Setup middleware
setup_middleware(app)

logger.info(
    "Starting %s version %s",
    settings.PROJECT_NAME,
    settings.VERSION
)

# Register all routers
for router in [
    auth.router,
    users.router,
    stocks.router,
    forecast.router,
    watchlist.router,
    admin.router,
    sentiment.router,
    data.router,
    whitepaper.router
]:
    app.include_router(
        router,
        prefix=f"{settings.API_V1_STR}"
    )
    logger.debug(f"Registered router: {router.prefix}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-06-16 23:40:22",
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
    except Exception as e:
        logger.error("Database connection failed: %s", str(e))
        raise

# Log application startup complete
logger.info(
    "Application startup complete - %s v%s",
    settings.PROJECT_NAME,
    settings.VERSION
)