"""
Main UI Module - Updated with Authentication Fixes
Created: 2025-05-21 14:30:14
Updated: 2025-06-17 17:55:08
Author: daparthi001
"""
import sys
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import settings and routes
from core.config import settings
from core.middleware.cors import configure_cors
from routes import (
    auth,
    dashboard,
    landing,
    stocks,
    profile,
    watchlist,
    analytics
)

# Create FastAPI application
app = FastAPI(
    title=f"{settings.PROJECT_NAME} UI",
    version=settings.VERSION,
    description="QuantumVestAI Stock Market Analysis Platform UI",
)

# Configure CORS
app = configure_cors(app)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=settings.SESSION_MAX_AGE
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Register routes
ROUTES = [
    auth.router,
    dashboard.router,
    landing.router,
    stocks.router,
    profile.router,
    watchlist.router,
    analytics.router
]

for router in ROUTES:
    app.include_router(router)

# Default route - redirect to landing page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to landing page"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/landing")

# Error handling
@app.exception_handler(404)
async def not_found_error(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request}
    )

@app.exception_handler(500)
async def server_error(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-06-17 17:55:08",
        "version": settings.VERSION
    }

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
    uvicorn.run(app, host="0.0.0.0", port=3000)