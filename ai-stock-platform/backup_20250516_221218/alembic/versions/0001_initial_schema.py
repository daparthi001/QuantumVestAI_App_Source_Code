"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-05-15 20:23:18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    op.create_table('stocks',
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('predictability_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('ticker')
    )
    
    op.create_table('watchlists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('watchlist_stocks',
        sa.Column('watchlist_id', sa.Integer(), nullable=False),
        sa.Column('stock_ticker', sa.String(length=20), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['watchlist_id'], ['watchlists.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stock_ticker'], ['stocks.ticker'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('watchlist_id', 'stock_ticker')
    )
    
    op.create_table('stock_forecasts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=True),
        sa.Column('forecast_date', sa.Date(), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('forecast_1d', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('forecast_1w', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('forecast_1m', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('forecast_3m', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['ticker'], ['stocks.ticker'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker', 'forecast_date', 'model_name')
    )
    
    op.create_table('user_activity_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('activity_type', sa.String(length=100), nullable=False),
        sa.Column('activity_details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('user_activity_log')
    op.drop_table('stock_forecasts')
    op.drop_table('watchlist_stocks')
    op.drop_table('watchlists')
    op.drop_table('stocks')
    op.drop_table('users')