# backend/alembic/versions/0004_create_threats_table.py

"""create threats table for DNS monitor persistence

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'threats',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('domain', sa.String(length=255), nullable=False, index=True),
        sa.Column('record_type', sa.String(length=10), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.BigInteger(), nullable=False, index=True),
    )


def downgrade():
    op.drop_table('threats')
