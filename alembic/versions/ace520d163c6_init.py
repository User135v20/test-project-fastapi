"""init

Revision ID: ace520d163c6
Revises: 
Create Date: 2022-06-10 19:59:27.229669

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ace520d163c6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=True)
    )


def downgrade():
    op.drop_table('users')
