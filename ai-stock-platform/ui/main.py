"""
QuantumVestAI UI - Main Application
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-16 22:11:00 by daparthi001
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from pathlib import Path
import logging
import os
import importlib

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

# Add global exception handlers - IMPORTANT: Add these before any middleware
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.info(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Add middleware in the correct order - IMPORTANT: Server error middleware must be first
app.add_middleware(ServerErrorMiddleware, debug=safe_settings.DEBUG)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Always allow all origins for stability
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safely import middleware
try:
    from middleware.auth_middleware import AuthMiddleware
    from middleware.metrics_middleware import MetricsMiddleware
    from middleware.error_handlers import setup_error_handlers
    
    # Add custom middleware - ORDER MATTERS! AuthMiddleware should be last
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(AuthMiddleware)
    logger.info("Successfully added middleware")

    # Safely set up error handlers from imported module
    setup_error_handlers(app)
    logger.info("Successfully set up error handlers")
except Exception as e:
    logger.error(f"Error adding middleware or error handlers: {e}")

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

# Function to safely import a router
def safe_import_router(module_path, router_name="router"):
    try:
        module = importlib.import_module(module_path)
        return getattr(module, router_name)
    except ImportError as e:
        logger.error(f"Error importing {module_path}: {e}")
        return None
    except AttributeError as e:
        logger.error(f"Error getting router from {module_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error importing {module_path}: {e}")
        return None

# Safely include routers - IMPORT THEM INDEPENDENTLY to avoid circular imports
routers_config = [
    {"module": "routes.dashboard", "prefix": "", "tags": ["Dashboard"]},
    {"module": "routes.auth", "prefix": "/auth", "tags": ["Authentication"]},
    {"module": "routes.admin", "prefix": "/admin", "tags": ["Admin"]},
    {"module": "routes.forecast", "prefix": "/forecast", "tags": ["Forecasting"]},
    {"module": "routes.watchlist", "prefix": "/watchlist", "tags": ["Watchlist"]},
    {"module": "routes.predictability", "prefix": "/predictability", "tags": ["Predictability"]},
    {"module": "routes.settings", "prefix": "/settings", "tags": ["Settings"]},
    {"module": "routes.profile", "prefix": "/profile", "tags": ["Profile"]}
]

for router_config in routers_config:
    router = safe_import_router(router_config["module"])
    if router:
        app.include_router(
            router,
            prefix=router_config["prefix"],
            tags=router_config["tags"]
        )
        logger.info(f"Successfully included router from {router_config['module']}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": safe_settings.VERSION,
        "timestamp": "2025-06-16 22:11:00",
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