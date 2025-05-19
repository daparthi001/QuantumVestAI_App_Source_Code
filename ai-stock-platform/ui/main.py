"""
QuantumVestAI UI - Main Application
Created: 2025-05-19 03:44:39
Author: daparthi001
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

# Import routes
from routes.admin import router as admin_router
from routes.auth import router as auth_router
from routes.forecast import router as forecast_router
from routes.watchlist import router as watchlist_router
from routes.predictability import router as predictability_router
from routes.settings import router as settings_router
from routes.dashboard import router as dashboard_router
from routes.profile import router as profile_router

# Import middleware
from middleware.auth_middleware import AuthMiddleware
from middleware.error_handlers import setup_error_handlers
from middleware.metrics_middleware import MetricsMiddleware
from core.config import settings
from core.logging import setup_logging

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="QuantumVestAI Web Interface",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
app.add_middleware(AuthMiddleware)
app.add_middleware(MetricsMiddleware)

# Setup error handlers
setup_error_handlers(app)

# Ensure static and template directories exist
Path(settings.STATIC_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.TEMPLATES_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Configure templates
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

# Include routers with proper prefixes
app.include_router(dashboard_router, prefix="", tags=["Dashboard"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(forecast_router, prefix="/forecast", tags=["Forecasting"])
app.include_router(watchlist_router, prefix="/watchlist", tags=["Watchlist"])
app.include_router(predictability_router, prefix="/predictability", tags=["Predictability"])
app.include_router(settings_router, prefix="/settings", tags=["Settings"])
app.include_router(profile_router, prefix="/profile", tags=["Profile"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": "2025-05-19 03:44:39",
        "author": "daparthi001",
        "environment": settings.ENVIRONMENT
    }

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info(f"Starting {settings.PROJECT_NAME} UI v{settings.VERSION}")
    # Initialize services here

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks"""
    logger.info(f"Shutting down {settings.PROJECT_NAME} UI")
    # Cleanup services here

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )