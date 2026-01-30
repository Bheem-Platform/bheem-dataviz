"""Add joined_transforms to semantic_models

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-01-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add joined_transforms column for multi-transform support
    op.add_column('semantic_models', sa.Column('joined_transforms', postgresql.JSONB(), nullable=True, server_default='[]'))


def downgrade() -> None:
    # Drop joined_transforms column
    op.drop_column('semantic_models', 'joined_transforms')
