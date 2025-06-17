"""
Main API Module
Created: 2025-05-21 14:26:28
Updated: 2025-06-17 00:30:50
Author: daparthi001
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import settings and logger first
from core.config import settings
from core.logger import logger

# Then import database
from db.session import engine, SessionLocal, get_db

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
from schemas.auth import RegisterRequest

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

# Attempt to mount static files if directory exists
try:
    app.mount("/static", StaticFiles(directory="ui/static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {str(e)}")

# Setup templates if directory exists
templates_path = Path("ui/templates")
if templates_path.exists() and templates_path.is_dir():
    templates = Jinja2Templates(directory="ui/templates")
else:
    templates = None
    logger.warning("Templates directory not found")

logger.info(
    "Starting %s version %s",
    settings.PROJECT_NAME,
    settings.VERSION
)

# Register all routers with API prefix
API_ROUTERS = [
    auth.router,
    users.router,
    stocks.router,
    forecast.router,
    watchlist.router,
    admin.router,
    sentiment.router,
    data.router,
    whitepaper.router
]

for router in API_ROUTERS:
    app.include_router(
        router,
        prefix=f"{settings.API_V1_STR}"
    )
    logger.debug(f"Registered router: {router.prefix} at {settings.API_V1_STR}{router.prefix}")

# Register specific non-prefixed routes for web app integration
@app.get("/register")
async def register_page(request: Request, msg: str = None):
    """Serve registration page"""
    if templates:
        try:
            return templates.TemplateResponse(
                "register.html", 
                {"request": request, "msg": msg}
            )
        except Exception as e:
            logger.error(f"Could not render template: {str(e)}")
    
    # If templates not available, redirect to API endpoint
    return RedirectResponse(url=f"{settings.API_V1_STR}/auth/register" + 
                          (f"?next={request.query_params.get('next', '/')}" 
                           if "next" in request.query_params else ""))

@app.post("/register")
async def process_registration(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    terms: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Process registration form submission"""
    # Validate inputs
    if password != confirm_password:
        if templates:
            return templates.TemplateResponse(
                "register.html", 
                {
                    "request": request, 
                    "msg": "Passwords do not match"
                },
                status_code=400
            )
    
    if not terms:
        if templates:
            return templates.TemplateResponse(
                "register.html", 
                {
                    "request": request, 
                    "msg": "You must accept the Terms of Service"
                },
                status_code=400
            )
    
    try:
        # Create registration data
        user_data = RegisterRequest(
            username=username,
            email=email,
            password=password,
            full_name=username  # Default to username as full name
        )
        
        # Call API register function
        result = await auth.register(request, user_data, db)
        
        # Redirect to login with success message
        next_url = request.query_params.get("next", "/login")
        return RedirectResponse(
            url=f"{next_url}?msg=Registration+successful!+Please+log+in.",
            status_code=303
        )
    
    except Exception as e:
        # Handle errors
        logger.error(f"Registration error: {str(e)}")
        
        if templates:
            return templates.TemplateResponse(
                "register.html", 
                {
                    "request": request, 
                    "msg": str(e)
                },
                status_code=400
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": str(e)}
            )

@app.get("/signup")
async def signup_page(request: Request):
    """Serve signup page or redirect to registration page"""
    return RedirectResponse(url="/register" + 
                           (f"?next={request.query_params.get('next')}" 
                            if "next" in request.query_params else ""))

# Add root route handler
@app.get("/")
async def root():
    """
    Root endpoint - redirects to API documentation
    """
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-06-17 00:30:50",
        "version": settings.VERSION
    }

# Error handling
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    if templates:
        try:
            return templates.TemplateResponse(
                "404.html", 
                {"request": request, "path": request.url.path},
                status_code=404
            )
        except Exception as e:
            logger.error(f"Could not render template: {str(e)}")
    
    return JSONResponse(
        status_code=404,
        content={
            "message": "The requested resource was not found",
            "path": request.url.path,
            "timestamp": "2025-06-17 00:30:50"
        }
    )

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