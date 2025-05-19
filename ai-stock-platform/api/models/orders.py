"""
Order Models
Created: 2025-05-19 04:48:12
Author: daparthi001
"""
from enum import Enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from api.db.base import Base

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
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY or SELL
    quantity = Column(Float, nullable=False)
    order_type = Column(SQLEnum(OrderType), nullable=False)
    time_in_force = Column(SQLEnum(TimeInForce), nullable=False)
    price = Column(Float, nullable=True)  # Required for LIMIT orders
    stop_price = Column(Float, nullable=True)  # Required for STOP orders
    status = Column(SQLEnum(OrderStatus), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.utcnow)
    executed_price = Column(Float, nullable=True)
    executed_quantity = Column(Float, nullable=True)
    execution_time = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    expiration_time = Column(DateTime, nullable=True)
    
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
        created_at: Optional[datetime] = None
    ):
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