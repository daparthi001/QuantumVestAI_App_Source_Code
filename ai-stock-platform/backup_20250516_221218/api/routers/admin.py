from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from api.core.security_utils import get_current_admin_user
from api.db.session import get_db
from api.db.models.user import User
from api.services.admin_service import AdminService

router = APIRouter(prefix="/admin")

@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get system statistics."""
    admin_service = AdminService(db)
    stats = admin_service.get_system_stats()
    
    return stats

@router.get("/users/stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user statistics."""
    admin_service = AdminService(db)
    stats = admin_service.get_user_stats()
    
    return stats

@router.get("/forecasts/stats")
async def get_forecast_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get forecast statistics."""
    admin_service = AdminService(db)
    stats = admin_service.get_forecast_stats()
    
    return stats

@router.get("/stocks/sync-status")
async def get_stock_sync_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get stock data synchronization status."""
    admin_service = AdminService(db)
    status = admin_service.get_stock_sync_status()
    
    return status

@router.post("/stocks/sync")
async def trigger_stock_sync(
    tickers: List[str] = Body(None),
    full_sync: bool = Body(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Trigger stock data synchronization."""
    admin_service = AdminService(db)
    result = await admin_service.trigger_stock_sync(tickers, full_sync)
    
    return result

@router.post("/model/retrain")
async def retrain_model(
    model_name: str = Body(..., regex="^(ensemble|lstm|prophet|xgboost|arima)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Trigger model retraining."""
    admin_service = AdminService(db)
    result = await admin_service.retrain_model(model_name)
    
    return result

@router.get("/logs")
async def get_system_logs(
    level: str = Query("info", regex="^(debug|info|warning|error|critical)$"),
    limit: int = Query(100, ge=10, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get system logs."""
    admin_service = AdminService(db)
    logs = admin_service.get_system_logs(level, limit)
    
    return logs

@router.get("/cache/stats")
async def get_cache_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get cache statistics."""
    admin_service = AdminService(db)
    stats = admin_service.get_cache_stats()
    
    return stats

@router.post("/cache/clear")
async def clear_cache(
    prefix: str = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Clear cache."""
    admin_service = AdminService(db)
    result = admin_service.clear_cache(prefix)
    
    return result