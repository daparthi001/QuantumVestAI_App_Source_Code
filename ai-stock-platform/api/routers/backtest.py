"""
Backtest Router
Created: 2025-05-20 04:53:22
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Query, Path, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.security import get_current_user
from core.exceptions import ResourceNotFoundError, PermissionDeniedError
from db.session import get_db
from db.models.user import User
from services.backtest_service import BacktestService
from schemas.backtest import (
    BacktestCreate,
    BacktestResponse,
    BacktestResultResponse,
    BacktestPerformanceResponse,
    StrategyResponse,
    OptimizationResponse,
    RiskMetricsResponse,
    BacktestComparisonResponse
)

router = APIRouter(
    prefix="/backtest",
    tags=["backtest"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=BacktestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create backtest",
    description="Create a new backtest simulation"
)
async def create_backtest(
    backtest: BacktestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> BacktestResponse:
    """Create new backtest."""
    if current_user.role == "free":
        raise PermissionDeniedError("Backtesting requires premium subscription")
    
    service = BacktestService(db)
    result = await service.create_backtest(
        backtest=backtest,
        user_id=current_user.id
    )
    
    background_tasks.add_task(
        service.run_backtest,
        backtest_id=result.id
    )
    
    return result

@router.get(
    "/{backtest_id}/results",
    response_model=BacktestResultResponse,
    summary="Get results",
    description="Get backtest simulation results"
)
async def get_backtest_results(
    backtest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> BacktestResultResponse:
    """Get backtest results."""
    service = BacktestService(db)
    results = await service.get_results(
        backtest_id=backtest_id,
        user_id=current_user.id
    )
    
    if not results:
        raise ResourceNotFoundError(f"Backtest {backtest_id} not found")
    
    return results

@router.get(
    "/{backtest_id}/performance",
    response_model=BacktestPerformanceResponse,
    summary="Get performance",
    description="Get backtest performance metrics"
)
async def get_backtest_performance(
    backtest_id: int,
    metrics: List[str] = Query(
        ["returns", "sharpe", "drawdown", "win_rate"],
        description="Performance metrics to calculate"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> BacktestPerformanceResponse:
    """Get backtest performance."""
    service = BacktestService(db)
    performance = await service.get_performance(
        backtest_id=backtest_id,
        metrics=metrics,
        user_id=current_user.id
    )
    
    if not performance:
        raise ResourceNotFoundError(f"Backtest {backtest_id} not found")
    
    return performance

@router.get(
    "/strategies",
    response_model=List[StrategyResponse],
    summary="List strategies",
    description="Get available trading strategies"
)
async def list_strategies(
    category: Optional[str] = Query(
        None,
        regex="^(momentum|mean_reversion|ml|options|multi)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[StrategyResponse]:
    """List trading strategies."""
    service = BacktestService(db)
    return await service.list_strategies(category)

@router.post(
    "/{backtest_id}/optimize",
    response_model=OptimizationResponse,
    summary="Optimize strategy",
    description="Optimize strategy parameters"
)
async def optimize_strategy(
    backtest_id: int,
    optimization_config: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> OptimizationResponse:
    """Optimize strategy parameters."""
    if current_user.role != "premium":
        raise PermissionDeniedError(
            "Strategy optimization requires premium subscription"
        )
    
    service = BacktestService(db)
    optimization = await service.optimize_strategy(
        backtest_id=backtest_id,
        config=optimization_config,
        user_id=current_user.id
    )
    
    background_tasks.add_task(
        service.run_optimization,
        optimization_id=optimization.id
    )
    
    return optimization

@router.get(
    "/{backtest_id}/risk",
    response_model=RiskMetricsResponse,
    summary="Get risk metrics",
    description="Get backtest risk analysis"
)
async def get_risk_metrics(
    backtest_id: int,
    risk_metrics: List[str] = Query(
        ["var", "sortino", "beta", "correlation"],
        description="Risk metrics to calculate"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RiskMetricsResponse:
    """Get risk metrics."""
    service = BacktestService(db)
    metrics = await service.get_risk_metrics(
        backtest_id=backtest_id,
        metrics=risk_metrics,
        user_id=current_user.id
    )
    
    if not metrics:
        raise ResourceNotFoundError(f"Backtest {backtest_id} not found")
    
    return metrics

@router.get(
    "/compare",
    response_model=BacktestComparisonResponse,
    summary="Compare backtests",
    description="Compare multiple backtest results"
)
async def compare_backtests(
    backtest_ids: List[int],
    metrics: List[str] = Query(
        ["returns", "sharpe", "drawdown"],
        description="Metrics to compare"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> BacktestComparisonResponse:
    """Compare backtests."""
    service = BacktestService(db)
    comparison = await service.compare_backtests(
        backtest_ids=backtest_ids,
        metrics=metrics,
        user_id=current_user.id
    )
    
    return comparison