"""
Database Association Tables
Created: 2025-05-20 20:31:25
Author: daparthi001
"""
from sqlalchemy import Table, Column, Integer, ForeignKey
from db.base import Base

# Association table for user watchlists
user_watchlist = Table(
    'user_watchlist',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('stock_id', Integer, ForeignKey('stocks.id', ondelete='CASCADE')),
)

# Association table for user portfolios
user_portfolio = Table(
    'user_portfolio',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('stock_id', Integer, ForeignKey('stocks.id', ondelete='CASCADE')),
)
