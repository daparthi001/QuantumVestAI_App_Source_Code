"""
Portfolio Router
Created: 2025-05-20 04:48:48
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError, ValidationError
from db.session import get_db
from db.models.user import User
from services.portfolio_service import PortfolioService
from schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioDetailResponse,
    TransactionCreate,
    TransactionResponse,
    PortfolioAnalyticsResponse,
    PortfolioAllocationResponse,
    PortfolioDiversificationResponse
)

router = APIRouter(
    prefix="/portfolios",
    tags=["portfolio"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=PortfolioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create portfolio",
    description="Create a new investment portfolio"
)
async def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioResponse:
    """Create new portfolio."""
    service = PortfolioService(db)
    return await service.create_portfolio(portfolio, current_user.id)

@router.get(
    "/",
    response_model=List[PortfolioResponse],
    summary="List portfolios",
    description="Get all portfolios for current user"
)
async def list_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[PortfolioResponse]:
    """List all portfolios."""
    service = PortfolioService(db)
    return await service.get_user_portfolios(current_user.id)

@router.get(
    "/{portfolio_id}",
    response_model=PortfolioDetailResponse,
    summary="Get portfolio",
    description="Get detailed portfolio information"
)
async def get_portfolio(
    portfolio_id: int,
    include_transactions: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioDetailResponse:
    """Get portfolio details."""
    service = PortfolioService(db)
    portfolio = await service.get_portfolio_details(
        portfolio_id,
        current_user.id,
        include_transactions
    )
    
    if not portfolio:
        raise ResourceNotFoundError(f"Portfolio {portfolio_id} not found")
    
    return portfolio

@router.post(
    "/{portfolio_id}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add transaction",
    description="Add new transaction to portfolio"
)
async def add_transaction(
    portfolio_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TransactionResponse:
    """Add portfolio transaction."""
    service = PortfolioService(db)
    result = await service.add_transaction(
        portfolio_id,
        transaction,
        current_user.id
    )
    
    if not result:
        raise ResourceNotFoundError(f"Portfolio {portfolio_id} not found")
    
    return result

@router.get(
    "/{portfolio_id}/analytics",
    response_model=PortfolioAnalyticsResponse,
    summary="Get analytics",
    description="Get portfolio performance analytics"
)
async def get_portfolio_analytics(
    portfolio_id: int,
    period: str = Query(
        "1mo",
        regex="^(1d|1wk|1mo|3mo|6mo|1y|ytd|all)$"
    ),
    benchmark: Optional[str] = Query(
        "SPY",
        description="Benchmark symbol"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioAnalyticsResponse:
    """Get portfolio analytics."""
    service = PortfolioService(db)
    analytics = await service.get_analytics(
        portfolio_id,
        current_user.id,
        period,
        benchmark
    )
    
    if not analytics:
        raise ResourceNotFoundError(f"Portfolio {portfolio_id} not found")
    
    return analytics

@router.get(
    "/{portfolio_id}/allocation",
    response_model=PortfolioAllocationResponse,
    summary="Get allocation",
    description="Get portfolio allocation breakdown"
)
async def get_portfolio_allocation(
    portfolio_id: int,
    group_by: str = Query(
        "sector",
        regex="^(sector|industry|asset_class|geography)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioAllocationResponse:
    """Get portfolio allocation."""
    service = PortfolioService(db)
    allocation = await service.get_allocation(
        portfolio_id,
        current_user.id,
        group_by
    )
    
    if not allocation:
        raise ResourceNotFoundError(f"Portfolio {portfolio_id} not found")
    
    return allocation

@router.get(
    "/{portfolio_id}/diversification",
    response_model=PortfolioDiversificationResponse,
    summary="Get diversification",
    description="Get portfolio diversification metrics"
)
async def get_portfolio_diversification(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PortfolioDiversificationResponse:
    """Get portfolio diversification metrics."""
    service = PortfolioService(db)
    metrics = await service.get_diversification_metrics(
        portfolio_id,
        current_user.id
    )
    
    if not metrics:
        raise ResourceNotFoundError(f"Portfolio {portfolio_id} not found")
    
    return metrics