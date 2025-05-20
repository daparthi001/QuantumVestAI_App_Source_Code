"""
Main FastAPI Application
Created: 2025-05-20 17:36:23
Author: daparthi001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Update imports to use absolute paths
import core.config as config_module
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

settings = config_module.settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
        "version": settings.VERSION,
        "timestamp": "2025-05-20 17:36:23",
        "user": "daparthi001"
    }