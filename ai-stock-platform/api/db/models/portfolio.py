"""
Portfolio Models Module
Created: 2025-05-21 17:23:43
Author: daparthi001
"""
import enum
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from db.base import Base, TimestampMixin
from db.models.associations import user_portfolio
from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Integer,
                        Numeric, String)
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func


class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    BUY = "BUY"
    SELL = "SELL"

class Position(Base, TimestampMixin):
    """Portfolio position model"""
    __tablename__ = "positions"
    __table_args__ = {"extend_existing": True}

    # Primary fields
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    stock_id: Mapped[int] = Column(
        Integer,
        ForeignKey("stocks.id", ondelete="CASCADE"),
        nullable=False
    )
    shares: Mapped[Decimal] = Column(
        Numeric(precision=10, scale=4),
        nullable=False,
        default=Decimal('0')
    )
    average_cost: Mapped[Decimal] = Column(
        Numeric(precision=10, scale=2),
        nullable=False,
        default=Decimal('0')
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="positions")
    stock: Mapped["Stock"] = relationship("Stock", back_populates="positions")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="position",
        cascade="all, delete-orphan"
    )

    @property
    def market_value(self) -> Optional[Decimal]:
        """Calculate current market value of position"""
        if self.stock and self.stock.last_price:
            return Decimal(str(self.stock.last_price)) * self.shares
        return None

    @property
    def cost_basis(self) -> Decimal:
        """Calculate total cost basis of position"""
        return self.average_cost * self.shares

    @property
    def unrealized_gain_loss(self) -> Optional[Decimal]:
        """Calculate unrealized gain/loss"""
        market_value = self.market_value
        if market_value is not None:
            return market_value - self.cost_basis
        return None

    @property
    def unrealized_gain_loss_percent(self) -> Optional[Decimal]:
        """Calculate unrealized gain/loss percentage"""
        if self.cost_basis and self.unrealized_gain_loss is not None:
            if self.cost_basis != 0:
                return (self.unrealized_gain_loss / self.cost_basis) * Decimal('100')
        return None

    def __repr__(self) -> str:
        return f"<Position {self.user.username} {self.stock.ticker} {self.shares}>"

class Transaction(Base, TimestampMixin):
    """Portfolio transaction model"""
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}

    # Primary fields
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    position_id: Mapped[int] = Column(
        Integer,
        ForeignKey("positions.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[int] = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    stock_id: Mapped[int] = Column(
        Integer,
        ForeignKey("stocks.id", ondelete="CASCADE"),
        nullable=False
    )
    transaction_type: Mapped[TransactionType] = Column(
        Enum(TransactionType),
        nullable=False
    )
    shares: Mapped[Decimal] = Column(
        Numeric(precision=10, scale=4),
        nullable=False
    )
    price: Mapped[Decimal] = Column(
        Numeric(precision=10, scale=2),
        nullable=False
    )
    timestamp: Mapped[datetime] = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    position: Mapped["Position"] = relationship("Position", back_populates="transactions")
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    stock: Mapped["Stock"] = relationship("Stock", back_populates="transactions")

    @property
    def total_amount(self) -> Decimal:
        """Calculate total transaction amount"""
        return self.shares * self.price

    def update_position(self) -> None:
        """Update the associated position after transaction"""
        if self.transaction_type == TransactionType.BUY:
            new_shares = self.position.shares + self.shares
            new_cost = (self.position.cost_basis + self.total_amount)
            self.position.shares = new_shares
            if new_shares > 0:
                self.position.average_cost = new_cost / new_shares
        else:  # SELL
            self.position.shares -= self.shares
            if self.position.shares > 0:
                # Recalculate average cost only if shares remain
                realized_cost = self.shares * self.position.average_cost
                self.position.cost_basis -= realized_cost

    def __repr__(self) -> str:
        return (
            f"<Transaction {self.transaction_type.value} "
            f"{self.stock.ticker} {self.shares} @ {self.price}>"
        )

class PortfolioSummary:
    """Portfolio summary value object"""
    def __init__(
        self,
        total_value: Decimal,
        cash_balance: Decimal,
        total_cost: Decimal,
        unrealized_gain_loss: Decimal,
        day_change: Decimal,
        day_change_percent: Decimal,
        total_positions: int,
        last_updated: datetime
    ):
        self.total_value = total_value
        self.cash_balance = cash_balance
        self.total_cost = total_cost
        self.unrealized_gain_loss = unrealized_gain_loss
        self.day_change = day_change
        self.day_change_percent = day_change_percent
        self.total_positions = total_positions
        self.last_updated = last_updated

    @property
    def invested_value(self) -> Decimal:
        """Calculate total invested value"""
        return self.total_value - self.cash_balance

    @property
    def gain_loss_percent(self) -> Optional[Decimal]:
        """Calculate total gain/loss percentage"""
        if self.total_cost and self.total_cost != 0:
            return (self.unrealized_gain_loss / self.total_cost) * Decimal('100')
        return None

    def to_dict(self) -> dict:
        """Convert summary to dictionary"""
        return {
            'total_value': str(self.total_value),
            'cash_balance': str(self.cash_balance),
            'invested_value': str(self.invested_value),
            'total_cost': str(self.total_cost),
            'unrealized_gain_loss': str(self.unrealized_gain_loss),
            'gain_loss_percent': str(self.gain_loss_percent) if self.gain_loss_percent else None,
            'day_change': str(self.day_change),
            'day_change_percent': str(self.day_change_percent),
            'total_positions': self.total_positions,
            'last_updated': self.last_updated.isoformat()
        }
