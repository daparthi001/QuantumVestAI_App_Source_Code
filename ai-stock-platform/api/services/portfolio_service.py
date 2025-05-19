"""
Portfolio Service
Created: 2025-05-19 04:28:10
Author: daparthi001
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.models.portfolio import Position, Transaction, PortfolioSummary
from api.schemas.portfolio import TransactionCreate, PositionUpdate
from api.services.market_data_service import MarketDataService

class PortfolioService:
    def __init__(self, db: Session, market_data: MarketDataService):
        self.db = db
        self.market_data = market_data

    async def get_portfolio_summary(self, user_id: int) -> PortfolioSummary:
        """Get portfolio summary with real-time market values"""
        try:
            positions = self.db.query(Position).filter(Position.user_id == user_id).all()
            
            total_market_value = 0
            total_cost_basis = 0
            day_change = 0
            
            for position in positions:
                current_price = await self.market_data.get_current_price(position.symbol)
                previous_close = await self.market_data.get_previous_close(position.symbol)
                
                market_value = position.shares * current_price
                day_change += (current_price - previous_close) * position.shares
                
                total_market_value += market_value
                total_cost_basis += position.cost_basis

            cash_balance = self._get_cash_balance(user_id)
            total_value = total_market_value + cash_balance
            total_gain_loss = total_market_value - total_cost_basis
            
            return PortfolioSummary(
                total_value=total_value,
                cash_balance=cash_balance,
                total_market_value=total_market_value,
                total_cost_basis=total_cost_basis,
                total_gain_loss=total_gain_loss,
                total_gain_loss_percent=(total_gain_loss / total_cost_basis * 100) if total_cost_basis else 0,
                day_change=day_change,
                day_change_percent=(day_change / (total_value - day_change) * 100) if total_value != day_change else 0,
                last_updated=datetime.utcnow()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get portfolio summary: {str(e)}")

    async def get_positions(self, user_id: int) -> List[Position]:
        """Get all positions with real-time market data"""
        try:
            positions = self.db.query(Position).filter(Position.user_id == user_id).all()
            
            for position in positions:
                current_price = await self.market_data.get_current_price(position.symbol)
                previous_close = await self.market_data.get_previous_close(position.symbol)
                
                position.current_price = current_price
                position.market_value = position.shares * current_price
                position.gain_loss = position.market_value - position.cost_basis
                position.gain_loss_percent = (position.gain_loss / position.cost_basis * 100) if position.cost_basis else 0
                position.day_change = (current_price - previous_close) * position.shares
                position.day_change_percent = ((current_price - previous_close) / previous_close * 100) if previous_close else 0

            return positions
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get positions: {str(e)}")

    async def add_transaction(self, user_id: int, transaction: TransactionCreate) -> Transaction:
        """Add a new transaction and update positions"""
        try:
            # Start transaction
            db_transaction = Transaction(
                user_id=user_id,
                symbol=transaction.symbol,
                transaction_type=transaction.type,
                shares=transaction.shares,
                price=transaction.price,
                total_amount=transaction.shares * transaction.price,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(db_transaction)
            
            # Update position
            position = self.db.query(Position).filter(
                Position.user_id == user_id,
                Position.symbol == transaction.symbol
            ).first()
            
            if position:
                if transaction.type == "BUY":
                    new_shares = position.shares + transaction.shares
                    new_cost_basis = position.cost_basis + (transaction.shares * transaction.price)
                    position.average_cost = new_cost_basis / new_shares
                    position.shares = new_shares
                    position.cost_basis = new_cost_basis
                else:  # SELL
                    if position.shares < transaction.shares:
                        raise HTTPException(status_code=400, detail="Insufficient shares for sale")
                    
                    new_shares = position.shares - transaction.shares
                    position.shares = new_shares
                    if new_shares == 0:
                        self.db.delete(position)
                    else:
                        position.cost_basis = position.average_cost * new_shares
            else:
                if transaction.type == "SELL":
                    raise HTTPException(status_code=400, detail="No position exists for sale")
                
                position = Position(
                    user_id=user_id,
                    symbol=transaction.symbol,
                    shares=transaction.shares,
                    average_cost=transaction.price,
                    cost_basis=transaction.shares * transaction.price
                )
                self.db.add(position)
            
            # Update cash balance
            self._update_cash_balance(
                user_id,
                -transaction.total_amount if transaction.type == "BUY" else transaction.total_amount
            )
            
            self.db.commit()
            return db_transaction
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to process transaction: {str(e)}")

    def get_transaction_history(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get transaction history with optional filters"""
        try:
            query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
            
            if symbol:
                query = query.filter(Transaction.symbol == symbol)
            if start_date:
                query = query.filter(Transaction.timestamp >= start_date)
            if end_date:
                query = query.filter(Transaction.timestamp <= end_date)
                
            return query.order_by(Transaction.timestamp.desc()).all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get transaction history: {str(e)}")

    def _get_cash_balance(self, user_id: int) -> float:
        """Get user's cash balance"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.cash_balance

    def _update_cash_balance(self, user_id: int, amount: float):
        """Update user's cash balance"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        new_balance = user.cash_balance + amount
        if new_balance < 0:
            raise HTTPException(status_code=400, detail="Insufficient funds")
            
        user.cash_balance = new_balance