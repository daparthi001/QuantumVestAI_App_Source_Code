"""
API Dependencies
Created: 2025-05-19 03:40:27
Author: daparthi001
"""
from fastapi import Depends, HTTPException, status, Query
from typing import Optional, List, Dict, Any, Generator, Annotated
from sqlalchemy.orm import Session
import logging

from api.db.session import get_db
from api.core.security import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    oauth2_scheme
)
from api.db.models.user import User
from api.services.stock_service import StockService
from api.core.exceptions import ResourceNotFoundError, PermissionDeniedError

logger = logging.getLogger(__name__)

def get_stock_service(db: Session = Depends(get_db)) -> StockService:
    """Dependency for StockService."""
    try:
        return StockService(db)
    except Exception as e:
        logger.error(f"Failed to create StockService: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service initialization failed"
        )

def verify_premium_access(current_user: User = Depends(get_current_active_user)) -> User:
    """Verify user has premium access."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    if current_user.role not in ["premium", "admin"]:
        raise PermissionDeniedError("Premium subscription required")
    return current_user

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
) -> Dict[str, int]:
    """Get pagination parameters."""
    return {"page": page, "limit": limit, "offset": (page - 1) * limit}

def get_ticker_param(
    ticker: str = Query(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    stock_service: StockService = Depends(get_stock_service),
) -> Dict[str, Any]:
    """Verify ticker exists and return stock info."""
    try:
        stock_info = stock_service.get_stock_info(ticker)
        if not stock_info:
            raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
        return stock_info
    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving stock info for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stock information"
        )

def verify_api_key(
    api_key: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    """Verify API key and return associated user."""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key associated with inactive user"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )