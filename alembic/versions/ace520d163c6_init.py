"""init

Revision ID: ace520d163c6
Revises: 
Create Date: 2022-06-10 19:59:27.229669

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey

revision = 'ace520d163c6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('timetable')
    op.drop_table('skills')
    op.drop_table('admin')
    op.create_table(
        'admin',
        sa.Column("id", sa.BIGINT(), primary_key=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True)
    )

    op.drop_table('student')
    op.create_table(
        'student',
        sa.Column("id", sa.BIGINT(), primary_key=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True)
    )

    op.drop_table('teacher')
    op.create_table(
        'teacher',
        sa.Column("id", sa.BIGINT(), primary_key=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("skills", sa.BIGINT(), nullable=True),
    )


    op.create_table(
        'timetable',
        sa.Column("id", sa.BIGINT(), primary_key=True),
        sa.Column("student", sa.BIGINT(), ForeignKey("student.id"), nullable=True),
        sa.Column("teacher", sa.BIGINT(),  ForeignKey("teacher.id"), nullable=True),
        sa.Column("day", sa.Date, nullable=True)
    )

    op.drop_table('language')
    op.create_table(
        'language',
        sa.Column("id", sa.BIGINT(), primary_key=True),
        sa.Column("language", sa.String(), nullable=True),
    )


    op.create_table(
        'skills',
        sa.Column("id", sa.BIGINT(), primary_key=True),
        sa.Column("teacher", sa.BIGINT, ForeignKey("teacher.id"), nullable=True),
        sa.Column("language", sa.BIGINT, ForeignKey("language.id"), nullable=True),
    )


def downgrade():
    op.drop_table('users')
