"""
QuantumVestAI UI - Main Application
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-15 03:50:31 by daparthi001
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import os

# Configure basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create safe settings wrapper to handle missing attributes
class SafeSettings:
    def __init__(self, original_settings=None):
        self._original = original_settings
        self._defaults = {
            'PROJECT_NAME': 'QuantumVestAI',
            'VERSION': '1.0.0',
            'DEBUG': False,
            'CORS_ORIGINS': ['*'],
            'STATIC_DIR': 'static',
            'TEMPLATES_DIR': 'templates',
            'UPLOAD_DIR': 'uploads',
            'HOST': '0.0.0.0',
            'PORT': 3000,
            'LOG_LEVEL': 'INFO',
            'ENVIRONMENT': 'production'
        }
        
    def __getattr__(self, name):
        if self._original is not None:
            try:
                return getattr(self._original, name)
            except (AttributeError, Exception) as e:
                logger.warning(f"Setting {name} not found in original settings: {e}")
        
        # Return default value if exists
        if name in self._defaults:
            logger.info(f"Using default value for {name}: {self._defaults[name]}")
            return self._defaults[name]
        
        # For any other attribute, return a safe default
        logger.warning(f"No default found for {name}, returning empty string")
        return ""

# Safely import routes and middleware
try:
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
    
    logger.info("Successfully imported all routes and middleware")
except ImportError as e:
    logger.error(f"Error importing routes or middleware: {e}")
    raise

# Safely import settings and logging
try:
    from core.config import settings
    from core.logging import setup_logging
    logger = setup_logging()
    logger.info("Successfully imported settings and logging")
except ImportError as e:
    logger.error(f"Error importing settings or logging: {e}")
    logger.warning("Using fallback settings")
    
    # Create fallback settings
    class FallbackSettings:
        PROJECT_NAME = "QuantumVestAI"
        VERSION = "1.0.0"
        DEBUG = False
        CORS_ORIGINS = ["*"]
        STATIC_DIR = "static"
        TEMPLATES_DIR = "templates"
        UPLOAD_DIR = "uploads"
        HOST = "0.0.0.0"
        PORT = 3000
        LOG_LEVEL = "INFO"
        ENVIRONMENT = "production"
    
    settings = FallbackSettings()
    
    # Create fallback setup_logging
    def setup_logging():
        return logging.getLogger(__name__)

# Wrap settings with SafeSettings to handle missing attributes
safe_settings = SafeSettings(settings)

# Create FastAPI app
app = FastAPI(
    title=safe_settings.PROJECT_NAME,
    description="QuantumVestAI Web Interface",
    version=safe_settings.VERSION,
    docs_url="/docs" if safe_settings.DEBUG else None,
    redoc_url="/redoc" if safe_settings.DEBUG else None
)

# Configure CORS with safe values
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Always allow all origins for stability
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safely add middleware
try:
    app.add_middleware(AuthMiddleware)
    app.add_middleware(MetricsMiddleware)
    logger.info("Successfully added middleware")
except Exception as e:
    logger.error(f"Error adding middleware: {e}")

# Safely set up error handlers
try:
    setup_error_handlers(app)
    logger.info("Successfully set up error handlers")
except Exception as e:
    logger.error(f"Error setting up error handlers: {e}")

# Ensure static and template directories exist
for directory in [safe_settings.STATIC_DIR, safe_settings.TEMPLATES_DIR, safe_settings.UPLOAD_DIR]:
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory created or verified: {directory}")
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")

# Mount static files safely
try:
    app.mount("/static", StaticFiles(directory=safe_settings.STATIC_DIR), name="static")
    logger.info(f"Successfully mounted static files from {safe_settings.STATIC_DIR}")
except Exception as e:
    logger.error(f"Error mounting static files: {e}")

# Configure templates safely
try:
    templates = Jinja2Templates(directory=safe_settings.TEMPLATES_DIR)
    logger.info(f"Successfully configured templates from {safe_settings.TEMPLATES_DIR}")
except Exception as e:
    logger.error(f"Error configuring templates: {e}")

# Include routers with proper prefixes safely
try:
    app.include_router(dashboard_router, prefix="", tags=["Dashboard"])
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    app.include_router(forecast_router, prefix="/forecast", tags=["Forecasting"])
    app.include_router(watchlist_router, prefix="/watchlist", tags=["Watchlist"])
    app.include_router(predictability_router, prefix="/predictability", tags=["Predictability"])
    app.include_router(settings_router, prefix="/settings", tags=["Settings"])
    app.include_router(profile_router, prefix="/profile", tags=["Profile"])
    logger.info("Successfully included all routers")
except Exception as e:
    logger.error(f"Error including routers: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": safe_settings.VERSION,
        "timestamp": "2025-06-15 03:50:31",
        "author": "daparthi001",
        "environment": safe_settings.ENVIRONMENT
    }

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info(f"Starting {safe_settings.PROJECT_NAME} UI v{safe_settings.VERSION}")
    # Initialize services here

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks"""
    logger.info(f"Shutting down {safe_settings.PROJECT_NAME} UI")
    # Cleanup services here

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=safe_settings.HOST,
        port=safe_settings.PORT,
        reload=safe_settings.DEBUG,
        log_level=safe_settings.LOG_LEVEL.lower()
    )