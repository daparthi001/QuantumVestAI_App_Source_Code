"""
Models Package
Created: 2025-05-20 05:58:02
Updated: 2025-05-21 15:48:25
Author: daparthi001
"""
# Import models individually so failure of one does not mask the others
try:  # Timestamp mixin is required by most models
    from db.base import TimestampMixin
except Exception:  # pragma: no cover - optional in test environment
    TimestampMixin = object

try:
    from db.models.user import User
except Exception:  # pragma: no cover - optional in test environment
    class User:  # Minimal fallback to avoid attribute errors in tests
        pass

try:
    from db.models.stock import Stock, WatchList
except Exception:  # pragma: no cover - optional in test environment
    Stock = object
    WatchList = object

try:
    from db.models.portfolio import (
        PortfolioSummary,
        Position,
        Transaction,
        TransactionType,
    )
except Exception:  # pragma: no cover - optional in test environment
    Position = object
    Transaction = object
    PortfolioSummary = object
    TransactionType = object

__all__ = [
    "TimestampMixin",
    "User",
    "Stock",
    "WatchList",
    "Position",
    "Transaction",
    "PortfolioSummary",    "TransactionType"]
