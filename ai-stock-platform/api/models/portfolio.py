"""
Portfolio Models
Created: 2025-05-19 04:28:10
Author: daparthi001
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db.base import Base, TimestampMixin
import enum

class TransactionType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class Position(Base, TimestampMixin):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    shares = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    cost_basis = Column(Float, nullable=False)
    
    # Virtual fields (not stored in database)
    current_price: float = None
    market_value: float = None
    gain_loss: float = None
    gain_loss_percent: float = None
    day_change: float = None
    day_change_percent: float = None

    # Relationships
    user = relationship("User", back_populates="positions")
    transactions = relationship("Transaction", back_populates="position")

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    symbol = Column(String, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")
    position = relationship("Position", back_populates="transactions")

class PortfolioSummary:
    def __init__(
        self,
        total_value: float,
        cash_balance: float,
        total_market_value: float,
        total_cost_basis: float,
        total_gain_loss: float,
        total_gain_loss_percent: float,
        day_change: float,
        day_change_percent: float,
        last_updated: datetime
    ):
        self.total_value = total_value
        self.cash_balance = cash_balance
        self.total_market_value = total_market_value
        self.total_cost_basis = total_cost_basis
        self.total_gain_loss = total_gain_loss
        self.total_gain_loss_percent = total_gain_loss_percent
        self.day_change = day_change
        self.day_change_percent = day_change_percent
        self.last_updated = last_updated