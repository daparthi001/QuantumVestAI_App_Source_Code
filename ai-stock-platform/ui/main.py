import os
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from ui.config.settings import settings
from ui.middleware.error_handlers import register_exception_handlers

# Create FastAPI application
app = FastAPI(
    title="QuantumVestAI UI",
    description="Advanced AI-powered stock prediction and analysis platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Configure templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import UI-specific routes
from ui.routes.auth import router as auth_router
from ui.routes.forecast import router as forecast_router
from ui.routes.admin import router as admin_router
from ui.routes.watchlist import router as watchlist_router
from ui.routes.predictability import router as predictability_router

app.include_router(auth_router)
app.include_router(forecast_router)
app.include_router(admin_router)
app.include_router(watchlist_router)
app.include_router(predictability_router)

# Root endpoint for home page
@app.get("/")
async def home(request: Request):
    """Render the home page"""
    # Get market summary for homepage display
    try:
        from ui.services.yahoo_finance import YahooFinanceService
        market_data = YahooFinanceService.get_market_summary()
    except Exception:
        market_data = None
        
    return templates.TemplateResponse(
        "home.html", 
        {"request": request, "market_data": market_data}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """UI health check endpoint"""
    # Check if API is reachable
    api_status = "unknown"
    try:
        import requests
        api_health = requests.get(f"{settings.API_BASE_URL}/health", timeout=2)
        api_status = "connected" if api_health.status_code == 200 else "disconnected"
    except Exception:
        api_status = "unreachable"
        
    return JSONResponse(content={
        "status": "healthy", 
        "version": "1.0.0",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "api_connection": api_status
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ui.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 3000)), reload=True)