"""Initial schema

Revision ID: bf9021d2617b
Revises: 
Create Date: 2025-05-15 10:25:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSON

# revision identifiers, used by Alembic.
revision = 'bf9021d2617b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('role', sa.String(), nullable=False, default='free'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('api_key', sa.String(), nullable=True),
        sa.Column('password_reset_token', sa.String(), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Stocks table
    op.create_table(
        'stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('exchange', sa.String(), nullable=True),
        sa.Column('sector', sa.String(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('last_price', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker')
    )
    
    # Stock prices table
    op.create_table(
        'stock_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('adjusted_close', sa.Float(), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('stock_id', 'date')
    )
    
    # Create index on stock prices date
    op.create_index(op.f('ix_stock_prices_date'), 'stock_prices', ['date'], unique=False)
    
    # User watchlist association table
    op.create_table(
        'user_watchlist',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('added_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'stock_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE')
    )
    
    # Forecasts table
    op.create_table(
        'forecasts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('days', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('forecast_data', JSON(), nullable=False),
        sa.Column('accuracy_metrics', JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE')
    )
    
    # Forecast models table
    op.create_table(
        'forecast_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parameters', JSON(), nullable=True),
        sa.Column('last_trained', sa.DateTime(), nullable=True),
        sa.Column('performance_metrics', JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Whitepapers table
    op.create_table(
        'whitepapers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', ARRAY(sa.String()), nullable=True),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('analyzed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Whitepaper analyses table
    op.create_table(
        'whitepaper_analyses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('whitepaper_id', sa.String(), nullable=False),
        sa.Column('analysis_data', JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['whitepaper_id'], ['whitepapers.id'], ondelete='CASCADE')
    )


def downgrade():
    # Drop tables in reverse order to avoid foreign key constraints
    op.drop_table('whitepaper_analyses')
    op.drop_table('whitepapers')
    op.drop_table('forecast_models')
    op.drop_table('forecasts')
    op.drop_table('user_watchlist')
    op.drop_index(op.f('ix_stock_prices_date'), table_name='stock_prices')
    op.drop_table('stock_prices')
    op.drop_table('stocks')
    op.drop_table('users')
