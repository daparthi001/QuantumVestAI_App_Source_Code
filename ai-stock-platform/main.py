"""
QuantumVestAI API - Main Application Entry Point
Created: 2025-05-19 03:43:23
Author: daparthi001
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from config.settings_wrapper import wrapped_settings as settings
from api.core.config import settings
from api.core.logging import setup_logging
from api.core.middleware import (
    rate_limit_middleware,
    metrics_middleware,
    request_id_middleware
)
from api.routers import (
    auth,
    users,
    stocks,
    forecast,
    watchlist,
    admin,
    sentiment,
    data,
    whitepaper,
    websocket
)

# Setup logging
logger = setup_logging()
logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the QuantumVestAI trading platform",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    debug=settings.DEBUG
)

# Configure CORS
if settings.BACKEND_CORS_ORIGINS:
    logger.info("Configuring CORS middleware")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add custom middleware
app.middleware("http")(request_id_middleware)
app.middleware("http")(metrics_middleware)
app.middleware("http")(rate_limit_middleware)

# Include API routers
logger.info("Registering API routers")
api_routers = [
    (auth.router, "Authentication"),
    (users.router, "User Management"),
    (stocks.router, "Stock Data"),
    (forecast.router, "Forecasting"),
    (watchlist.router, "Watchlists"),
    (admin.router, "Administration"),
    (sentiment.router, "Sentiment Analysis"),
    (data.router, "Data Management"),
    (whitepaper.router, "Whitepapers"),
    (websocket.router, "WebSocket")
]

for router, description in api_routers:
    logger.debug(f"Registering router: {description}")
    app.include_router(
        router,
        prefix=settings.API_V1_STR,
        tags=[description]
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": "2025-05-19 03:43:23",
        "author": "daparthi001",
        "environment": settings.ENVIRONMENT,
        "uptime": "System uptime will be added here"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "headers": dict(request.headers),
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    logger.info(f"Starting {settings.PROJECT_NAME} on http://0.0.0.0:8000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )