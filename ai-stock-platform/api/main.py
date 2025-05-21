"""
Main API Module
Created: 2025-05-21 05:17:43
Author: daparthi001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.config.settings import settings
from core.logger import logger
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

# Include routers with tags
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}", tags=["users"])
app.include_router(stocks.router, prefix=f"{settings.API_V1_STR}", tags=["stocks"])
app.include_router(forecast.router, prefix=f"{settings.API_V1_STR}", tags=["forecast"])
app.include_router(watchlist.router, prefix=f"{settings.API_V1_STR}", tags=["watchlist"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}", tags=["admin"])
app.include_router(sentiment.router, prefix=f"{settings.API_V1_STR}", tags=["sentiment"])
app.include_router(data.router, prefix=f"{settings.API_V1_STR}", tags=["data"])
app.include_router(whitepaper.router, prefix=f"{settings.API_V1_STR}", tags=["whitepaper"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-05-21 05:17:43",
        "version": settings.VERSION
    }