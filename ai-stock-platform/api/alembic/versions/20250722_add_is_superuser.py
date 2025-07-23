"""Add is_superuser column to users table if missing"""

from alembic import op
import sqlalchemy as sa

revision = 'add_is_superuser_20250722'
down_revision = 'add_full_name_20250715'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = [c['name'] for c in insp.get_columns('users')]
    if 'is_superuser' not in columns:
        op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        op.execute("UPDATE users SET is_superuser = FALSE WHERE is_superuser IS NULL")
        op.alter_column('users', 'is_superuser', server_default=None)


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = [c['name'] for c in insp.get_columns('users')]
    if 'is_superuser' in columns:
        op.drop_column('users', 'is_superuser')
