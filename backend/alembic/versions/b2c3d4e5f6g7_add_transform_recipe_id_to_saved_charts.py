"""add transform_recipe_id to saved_charts

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add transform_recipe_id column to saved_charts table
    op.add_column(
        'saved_charts',
        sa.Column(
            'transform_recipe_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('transform_recipes.id', ondelete='SET NULL'),
            nullable=True
        )
    )

    # Create index for transform_recipe_id
    op.create_index(
        'idx_saved_charts_transform_recipe',
        'saved_charts',
        ['transform_recipe_id']
    )


def downgrade() -> None:
    op.drop_index('idx_saved_charts_transform_recipe', table_name='saved_charts')
    op.drop_column('saved_charts', 'transform_recipe_id')
