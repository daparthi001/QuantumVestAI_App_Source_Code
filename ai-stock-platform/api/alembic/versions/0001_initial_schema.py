"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-05-17 14:12:31

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100)),
        sa.Column('last_name', sa.String(length=100)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('role', sa.String(length=50), default='free'),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('api_key', sa.String(length=64), unique=True),
        sa.Column('avatar_url', sa.String(length=255)),
        sa.Column('bio', sa.Text()),
        sa.Column('phone', sa.String(length=20)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # Stocks table
    op.create_table(
        'stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('sector', sa.String(length=100)),
        sa.Column('industry', sa.String(length=100)),
        sa.Column('exchange', sa.String(length=20)),
        sa.Column('market_cap', sa.BigInteger()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol')
    )

    # WhitePapers table
    op.create_table(
        'whitepapers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('tags', postgresql.ARRAY(sa.String())),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('analyzed_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    # Add other tables...

def downgrade():
    op.drop_table('whitepapers')
    op.drop_table('stocks')
    op.drop_table('users')
