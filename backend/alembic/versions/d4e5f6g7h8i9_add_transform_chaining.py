"""Add transform chaining support

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2024-01-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4e5f6g7h8i9'
down_revision = 'c3d4e5f6g7h8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add source_transform_id column for transform chaining
    op.add_column('transform_recipes', sa.Column('source_transform_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Create index on source_transform_id
    op.create_index('ix_transform_recipes_source_transform_id', 'transform_recipes', ['source_transform_id'])

    # Add foreign key constraint (self-referential)
    op.create_foreign_key(
        'fk_transform_recipes_source_transform_id',
        'transform_recipes',
        'transform_recipes',
        ['source_transform_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Make source_table nullable (for transform-based sources)
    op.alter_column('transform_recipes', 'source_table', nullable=True)


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_transform_recipes_source_transform_id', 'transform_recipes', type_='foreignkey')

    # Drop index
    op.drop_index('ix_transform_recipes_source_transform_id', table_name='transform_recipes')

    # Drop column
    op.drop_column('transform_recipes', 'source_transform_id')

    # Revert source_table to non-nullable
    op.alter_column('transform_recipes', 'source_table', nullable=False)
