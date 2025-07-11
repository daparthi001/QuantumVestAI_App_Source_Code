"""
Watchlist Router
Created: 2025-05-20 04:44:57
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import List

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError, ValidationError
from db.session import get_db
from db.models.user import User
from services.watchlist_service import WatchlistService
from schemas.watchlist import (
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistResponse,
    WatchlistDetailResponse,
    WatchlistStockAdd,
    WatchlistPerformanceResponse
)

router = APIRouter(
    prefix="/watchlists",
    tags=["watchlists"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create watchlist",
    description="Create a new watchlist"
)
async def create_watchlist(
    watchlist: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WatchlistResponse:
    """Create a new watchlist."""
    service = WatchlistService(db)
    return await service.create_watchlist(watchlist, current_user.id)

@router.get(
    "/",
    response_model=List[WatchlistResponse],
    summary="Get watchlists",
    description="Get all watchlists for current user"
)
async def get_watchlists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[WatchlistResponse]:
    """Get all watchlists."""
    service = WatchlistService(db)
    return await service.get_user_watchlists(current_user.id)

@router.get(
    "/{watchlist_id}",
    response_model=WatchlistDetailResponse,
    summary="Get watchlist",
    description="Get detailed watchlist information"
)
async def get_watchlist(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WatchlistDetailResponse:
    """Get watchlist details."""
    service = WatchlistService(db)
    watchlist = await service.get_watchlist(watchlist_id, current_user.id)
    
    if not watchlist:
        raise ResourceNotFoundError(f"Watchlist {watchlist_id} not found")
    
    return watchlist

@router.put(
    "/{watchlist_id}",
    response_model=WatchlistResponse,
    summary="Update watchlist",
    description="Update watchlist information"
)
async def update_watchlist(
    watchlist_id: int,
    watchlist: WatchlistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WatchlistResponse:
    """Update watchlist."""
    service = WatchlistService(db)
    updated = await service.update_watchlist(
        watchlist_id,
        watchlist,
        current_user.id
    )
    
    if not updated:
        raise ResourceNotFoundError(f"Watchlist {watchlist_id} not found")
    
    return updated

@router.delete(
    "/{watchlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete watchlist",
    description="Delete a watchlist"
)
async def delete_watchlist(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete watchlist."""
    service = WatchlistService(db)
    success = await service.delete_watchlist(watchlist_id, current_user.id)
    
    if not success:
        raise ResourceNotFoundError(f"Watchlist {watchlist_id} not found")

@router.post(
    "/{watchlist_id}/stocks",
    response_model=WatchlistDetailResponse,
    summary="Add stock",
    description="Add stock to watchlist"
)
async def add_stock_to_watchlist(
    watchlist_id: int,
    stock: WatchlistStockAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WatchlistDetailResponse:
    """Add stock to watchlist."""
    service = WatchlistService(db)
    updated = await service.add_stock(watchlist_id, stock.ticker, current_user.id)
    
    if not updated:
        raise ResourceNotFoundError(f"Watchlist {watchlist_id} not found")
    
    return updated

@router.delete(
    "/{watchlist_id}/stocks/{ticker}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove stock",
    description="Remove stock from watchlist"
)
async def remove_stock_from_watchlist(
    watchlist_id: int,
    ticker: str = Path(..., min_length=1, max_length=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove stock from watchlist."""
    service = WatchlistService(db)
    success = await service.remove_stock(watchlist_id, ticker, current_user.id)
    
    if not success:
        raise ResourceNotFoundError(
            f"Stock {ticker} not found in watchlist {watchlist_id}"
        )

@router.get(
    "/{watchlist_id}/performance",
    response_model=WatchlistPerformanceResponse,
    summary="Get performance",
    description="Get watchlist performance metrics"
)
async def get_watchlist_performance(
    watchlist_id: int,
    period: str = Query(
        "1d",
        regex="^(1d|1w|1m|3m|6m|1y|ytd|all)$",
        description="Performance period"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WatchlistPerformanceResponse:
    """Get watchlist performance."""
    service = WatchlistService(db)
    performance = await service.get_performance(
        watchlist_id,
        period,
        current_user.id
    )
    
    if not performance:
        raise ResourceNotFoundError(f"Watchlist {watchlist_id} not found")

    return performance

