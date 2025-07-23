"""
Models package initialization for QuantumVestAI
Created: 2025-07-23
Author: daparthi001
"""

# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .role import Role
from .user_role import UserRole
from .user_setting import UserSetting
from .audit_log import AuditLog
from .user_session import UserSession
from .stock import Stock, WatchList
from .portfolio import (
    Position,
    Transaction,
    PortfolioSummary,
    TransactionType,
)
from .watchlist import Watchlist
from .watchlist_stock import WatchlistStock

# Import utility functions
from .user import (
    get_user_by_email,
    get_user_by_username, 
    get_user_by_uuid,
    create_user
)

# Export all models and utilities
__all__ = [
    # Models
    "User",
    "Role", 
    "UserRole",
    "UserSetting",
    "AuditLog",
    "UserSession",
    
    # Utility functions
    "get_user_by_email",
    "get_user_by_username",
    "get_user_by_uuid", 
    "create_user",
    "Stock",
    "WatchList",
    "Watchlist",
    "WatchlistStock",
    "Position",
    "Transaction",
    "PortfolioSummary",
    "TransactionType"
]