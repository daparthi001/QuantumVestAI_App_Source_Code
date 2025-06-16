"""
QuantumVestAI - FastAPI Application
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-16 03:37:20 by daparthi001
"""
import logging
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import traceback
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Import settings
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    class Settings:
        API_PREFIX = ""
        DEBUG = True
        PROJECT_NAME = "QuantumVestAI"
        VERSION = "1.0.0"
    
    settings = Settings()

# Setup middleware and routes
try:
    # Import middleware - only import AuthMiddleware, not get_current_user
    from middleware import AuthMiddleware, MetricsMiddleware, setup_error_handlers
    
    # Import routes
    from routes.auth import router as auth_router
    from routes.auth import get_current_user  # Import from routes.auth, not middleware
    
    # Import other routes as needed
    from routes.dashboard import router as dashboard_router
    from routes.api import router as api_router
    from routes.health import router as health_router
except ImportError as e:
    logger.error(f"Error importing routes or middleware: {e}")
    traceback.print_exc()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: add any async startup code here
    logger.info("Starting QuantumVestAI application")
    yield
    # Shutdown: add any async shutdown code here
    logger.info("Shutting down QuantumVestAI application")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
# Note: Order matters - middleware executes in reverse order (last added, first executed)
app.add_middleware(MetricsMiddleware)  # Add first, executed last
app.add_middleware(AuthMiddleware)     # Add second, executed first

# Set up error handlers
setup_error_handlers(app)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
app.include_router(api_router, prefix="/api", tags=["api"])

# Root endpoint
@app.get("/")
async def root(current_user = Depends(get_current_user)):
    return {"message": f"Welcome to QuantumVestAI, {current_user['username']}!"}

# Health check endpoint (publicly accessible)
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

# Version endpoint
@app.get("/version", tags=["system"])
async def version():
    return {"version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)