"""Simplified order models for tests.

The real project exposes these models from ``api.models.orders`` but
importing that package pulls in database initialisation.  These copies
provide the small subset of functionality required by the tests without
any external dependencies.
"""

from datetime import datetime
from enum import Enum
from typing import Optional


class Base:
    """Lightweight base class used in tests."""

    pass


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PARTIAL_FILLED = "PARTIAL_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class TimeInForce(str, Enum):
    DAY = "DAY"
    GTC = "GTC"  # Good Till Cancelled
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill


class Order(Base):
    """Simple Order model used for tests without requiring SQLAlchemy."""

    def __init__(
        self,
        id: str,
        user_id: str,
        symbol: str,
        side: str,
        quantity: float,
        order_type: OrderType,
        time_in_force: TimeInForce,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        status: OrderStatus = OrderStatus.PENDING,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.order_type = order_type
        self.time_in_force = time_in_force
        self.price = price
        self.stop_price = stop_price
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = self.created_at
        self.executed_price: Optional[float] = None
        self.executed_quantity: Optional[float] = None


__all__ = [
    "Order",
    "OrderStatus",
    "OrderType",
    "TimeInForce",
]

