"""
Main FastAPI Application
Created: 2025-05-19 04:05:44
Author: daparthi001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.routes import auth, stocks

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(stocks.router, prefix=settings.API_V1_STR)
app.include_router(forecast_router, prefix="/api", tags=["forecast"])
app.include_router(watchlist_router, prefix="/api", tags=["watchlist"])
app.include_router(admin_router, prefix="/api", tags=["admin"])
app.include_router(sentiment_router, prefix="/api", tags=["sentiment"])
app.include_router(data_router, prefix="/api", tags=["data"])
app.include_router(whitepaper_router, prefix="/api", tags=["whitepaper"])

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": "2025-05-19 04:05:44"
    }