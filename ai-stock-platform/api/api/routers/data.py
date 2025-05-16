from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from typing import Optional

from api.core.security_utils import get_current_user, get_optional_current_user
from api.core.exceptions import ResourceNotFoundError, PermissionDeniedError
from api.db.session import get_db
from api.db.models.user import User
from api.services.data_service import DataService

router = APIRouter(prefix="/data")

@router.get("/{ticker}")
async def get_processed_stock_data(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    period: str = Query("1y", regex=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Time period"),
    with_sentiment: bool = Query(False, description="Include sentiment analysis"),
    full_data: bool = Query(False, description="Include full processed data"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get processed stock data for a ticker."""
    # Check if user has permission for full data
    if full_data and (not current_user or current_user.role not in ["premium", "admin"]):
        full_data = False
    
    # Check if user has permission for sentiment
    if with_sentiment and (not current_user or current_user.role == "free"):
        with_sentiment = False
    
    # Get data service
    data_service = DataService(db)
    
    # Get data
    result = await data_service.get_stock_data(
        ticker=ticker,
        period=period,
        include_sentiment=with_sentiment
    )
    
    # Check if there was an error
    if "error" in result:
        raise ResourceNotFoundError(result["error"])
    
    # Remove full data if not requested
    if not full_data and "data" in result:
        # Include just summary data
        df = result["data"]
        if df is not None and not df.empty:
            result["summary_data"] = {
                "start_date": df.date.min().isoformat(),
                "end_date": df.date.max().isoformat(),
                "days": len(df),
                "start_price": float(df.iloc[0].close) if "close" in df.columns else None,
                "end_price": float(df.iloc[-1].close) if "close" in df.columns else None,
                "min_price": float(df.close.min()) if "close" in df.columns else None,
                "max_price": float(df.close.max()) if "close" in df.columns else None,
                "price_change_pct": float((df.iloc[-1].close / df.iloc[0].close - 1) * 100) 
                    if "close" in df.columns else None,
                "avg_volume": int(df.volume.mean()) if "volume" in df.columns else None
            }
        del result["data"]
    
    return result

@router.get("/{ticker}/predictability")
async def get_stock_predictability(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get predictability analysis for a stock."""
    data_service = DataService(db)
    predictability = await data_service.get_predictability_analysis(ticker)
    
    if not predictability.get("success", False):
        raise ResourceNotFoundError(predictability.get("error", "Failed to retrieve predictability data"))
    
    return predictability

@router.get("/{ticker}/technical-indicators")
async def get_technical_indicators(
    ticker: str = Path(..., min_length=1, max_length=10, description="Stock ticker symbol"),
    period: str = Query("1mo", regex=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Time period"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get technical indicators for a stock."""
    # Check user permissions for detailed indicators
    detailed = current_user.role in ["basic", "premium", "admin"]
    
    data_service = DataService(db)
    indicators = await data_service.get_technical_indicators(ticker, period, detailed)
    
    if "error" in indicators:
        raise ResourceNotFoundError(indicators["error"])
    
    return indicators

@router.get("/sectors/performance")
async def get_sectors_performance(
    period: str = Query("1mo", regex=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Time period"),
    db: Session = Depends(get_db)
):
    """Get performance of market sectors."""
    data_service = DataService(db)
    performance = await data_service.get_sectors_performance(period)
    
    return performance

@router.get("/industries/performance")
async def get_industries_performance(
    period: str = Query("1mo", regex=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$", description="Time period"),
    sector: str = Query(None, description="Filter by sector name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get performance of industries."""
    data_service = DataService(db)
    performance = await data_service.get_industries_performance(period, sector)
    
    return performance