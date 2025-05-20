"""
API router configuration.
"""

from fastapi import APIRouter

from app.api.endpoints import auth, users, stocks, predictions, social

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(social.router, prefix="/social", tags=["social"])