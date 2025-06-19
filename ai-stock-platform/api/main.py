"""
Main API Module - Health Endpoint Fix
Updated: 2025-06-19 03:54:33
Author: daparthi001
"""
import logging
import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import socket
from datetime import datetime

from core.config import settings
from core.middleware.cors import configure_cors
from core.middleware.error_handler import ErrorHandlerMiddleware

# Import routers
from routers import (
    auth,
    stocks,
    predictions,
    users,
    watchlists,
    analytics,
    health,
    sentiment,
    backtest
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("quantumvestai_api")

# Create FastAPI application
app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    version=settings.VERSION,
    description="QuantumVestAI Stock Market Analysis Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.3f}s")
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    return await call_next(request)

# Configure middleware
app = configure_cors(app)
app.add_middleware(ErrorHandlerMiddleware)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

# CRITICAL FIX: Add explicit health check endpoint directly in main.py
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for ALB
    This is specifically added at the root level to ensure it's always available
    regardless of router configuration
    """
    logger.info("Health check endpoint accessed")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION,
        "hostname": socket.gethostname()
    }

# ALB specific health check endpoint
@app.get("/health", tags=["Health"], include_in_schema=False)
async def alb_health_check():
    """Simple health check endpoint for ALB"""
    logger.info("ALB health check endpoint accessed")
    return {"status": "healthy"}

# Include routers with proper prefixes
# Note: Avoid nested prefixes that could cause routing issues
app.include_router(auth.router, prefix="/api/v1")
app.include_router(stocks.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(watchlists.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(sentiment.router, prefix="/api/v1")
app.include_router(backtest.router, prefix="/api/v1")

# Log all routes on startup
@app.on_event("startup")
async def log_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": getattr(route, "methods", None)
        })
    logger.info(f"Registered routes: {routes}")
    logger.info(f"Starting {settings.PROJECT_NAME} API v{settings.VERSION}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )