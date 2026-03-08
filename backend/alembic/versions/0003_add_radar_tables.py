"""add radar tables: observed_endpoints, documented_endpoints

Revision ID: 0003
Revises: 317e2274e8c4
Create Date: 2026-03-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '317e2274e8c4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'observed_endpoints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('endpoint', sa.String(length=512), nullable=False),
        sa.Column('count', sa.Integer(), nullable=True),
        sa.Column('is_shadow', sa.Boolean(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_observed_endpoints_id'), 'observed_endpoints', ['id'], unique=False)

    op.create_table(
        'documented_endpoints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('endpoint', sa.String(length=512), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_documented_endpoints_id'), 'documented_endpoints', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_documented_endpoints_id'), table_name='documented_endpoints')
    op.drop_table('documented_endpoints')
    op.drop_index(op.f('ix_observed_endpoints_id'), table_name='observed_endpoints')
    op.drop_table('observed_endpoints')
