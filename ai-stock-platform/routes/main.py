from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from routes.admin import router as admin_router
from routes.webapi import router as web_router
from routes.auth import router as auth_router
from routes.sentiment import router as sentiment_router
from routes.whitepaper_analysis import router as whitepaper_router

# Create FastAPI application
app = FastAPI(
    title="QuantumVestAI",
    description="Stock prediction and analysis API using machine learning",
    version="1.0.0"
)

# Configure templates
templates = Jinja2Templates(directory="templates")

# Include all routers
app.include_router(web_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(sentiment_router)
app.include_router(whitepaper_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for home page
@app.get("/")
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("home.html", {"request": request})

# Health check endpoint
@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {"status": "healthy", "message": "QuantumVestAI API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)