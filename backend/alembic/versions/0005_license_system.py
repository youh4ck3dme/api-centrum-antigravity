"""Add license system tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-09 02:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None

def upgrade():
    # User table update
    op.add_column('users', sa.Column('is_unlimited', sa.Boolean(), nullable=True))
    op.execute("UPDATE users SET is_unlimited = false")
    
    # Licenses table
    op.create_table('licenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key_id', sa.String(length=100), nullable=False),
        sa.Column('hash', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('activated_at', sa.DateTime(), nullable=True),
        sa.Column('revoked', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hash')
    )
    op.create_index(op.f('ix_licenses_id'), 'licenses', ['id'], unique=False)
    op.create_index(op.f('ix_licenses_key_id'), 'licenses', ['key_id'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_licenses_key_id'), table_name='licenses')
    op.drop_index(op.f('ix_licenses_id'), table_name='licenses')
    op.drop_table('licenses')
    op.drop_column('users', 'is_unlimited')
