from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Import routes
from routes.admin import router as admin_router
from routes.auth import router as auth_router
from routes.forecast import router as forecast_router
from routes.watchlist import router as watchlist_router
from routes.predictability import router as predictability_router

# Import middleware
from middleware.auth_middleware import AuthMiddleware
# or
from middleware.auth_middleware import AuthenticationMiddleware
from middleware.error_handlers import setup_error_handlers
# Create FastAPI app
app = FastAPI(title="QuantumVestAI UI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
app.add_middleware(AuthMiddleware)

# Setup error handlers
setup_error_handlers(app)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(forecast_router)
app.include_router(watchlist_router)
app.include_router(predictability_router)

# Import other configurations as needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)