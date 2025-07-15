"""Add full_name column to users table if missing"""

from alembic import op
import sqlalchemy as sa

revision = 'add_full_name_20250715'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = [c['name'] for c in insp.get_columns('users')]
    if 'full_name' not in columns:
        op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
        if 'first_name' in columns and 'last_name' in columns:
            op.execute("UPDATE users SET full_name = CONCAT(first_name, ' ', last_name) WHERE full_name IS NULL")


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = [c['name'] for c in insp.get_columns('users')]
    if 'full_name' in columns:
        op.drop_column('users', 'full_name')
