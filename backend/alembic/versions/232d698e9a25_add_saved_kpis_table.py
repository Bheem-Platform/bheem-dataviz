"""add_saved_kpis_table

Revision ID: 232d698e9a25
Revises: f6g7h8i9j0k1
Create Date: 2026-01-27 05:29:18.081717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '232d698e9a25'
down_revision: Union[str, None] = 'f6g7h8i9j0k1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create saved_kpis table
    op.create_table(
        'saved_kpis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('connection_id', sa.String(), nullable=True),
        sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('transform_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('config', postgresql.JSON(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('saved_kpis')
