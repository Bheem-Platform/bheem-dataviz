"""Add transform_id to semantic_models

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2024-01-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add transform_id column to semantic_models
    op.add_column('semantic_models', sa.Column('transform_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Create index on transform_id
    op.create_index('ix_semantic_models_transform_id', 'semantic_models', ['transform_id'])

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_semantic_models_transform_id',
        'semantic_models',
        'transform_recipes',
        ['transform_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Make schema_name and table_name nullable (for transform-based models)
    op.alter_column('semantic_models', 'schema_name', nullable=True)
    op.alter_column('semantic_models', 'table_name', nullable=True)


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_semantic_models_transform_id', 'semantic_models', type_='foreignkey')

    # Drop index
    op.drop_index('ix_semantic_models_transform_id', table_name='semantic_models')

    # Drop column
    op.drop_column('semantic_models', 'transform_id')

    # Revert schema_name and table_name to non-nullable
    op.alter_column('semantic_models', 'schema_name', nullable=False)
    op.alter_column('semantic_models', 'table_name', nullable=False)
