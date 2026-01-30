"""add transform_recipes table

Revision ID: a1b2c3d4e5f6
Revises: 59ff6bfee78a
Create Date: 2026-01-22 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '59ff6bfee78a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create transform_recipes table
    op.create_table(
        'transform_recipes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('connections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_table', sa.String(255), nullable=False),
        sa.Column('source_schema', sa.String(255), server_default='public'),
        sa.Column('steps', postgresql.JSONB(), server_default='[]'),
        sa.Column('result_columns', postgresql.JSONB(), server_default='[]'),
        sa.Column('is_cached', sa.String(50), server_default='false'),
        sa.Column('cache_ttl', sa.Integer(), server_default='3600'),
        sa.Column('last_executed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create indexes
    op.create_index('idx_transform_recipes_connection', 'transform_recipes', ['connection_id'])
    op.create_index('idx_transform_recipes_tenant', 'transform_recipes', ['tenant_id'])


def downgrade() -> None:
    op.drop_index('idx_transform_recipes_tenant', table_name='transform_recipes')
    op.drop_index('idx_transform_recipes_connection', table_name='transform_recipes')
    op.drop_table('transform_recipes')
