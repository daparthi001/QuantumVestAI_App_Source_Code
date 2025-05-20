from fastapi import Depends, HTTPException, status, Query
from typing import Optional, List, Dict, Any, Generator, Annotated
from sqlalchemy.orm import Session

from api.db.session import get_db
from core.security import (
    get_current_user, get_current_active_user, get_current_admin_user, oauth2_scheme
)
from api.db.models.user import User
from api.services.stock_service import StockService
from core.exceptions import ResourceNotFoundError, PermissionDeniedError

def get_stock_service(db: Session = Depends(get_db)) -> StockService:
    """Dependency for StockService."""
    return StockService(db)

def verify_premium_access(current_user: User = Depends(get_current_active_user)) -> User:
    """Verify user has premium access."""
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
    stock_info = stock_service.get_stock_info(ticker)
    if not stock_info:
        raise ResourceNotFoundError(f"Stock with ticker {ticker} not found")
    return stock_info

def verify_api_key(
    api_key: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    """Verify API key and return associated user."""
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