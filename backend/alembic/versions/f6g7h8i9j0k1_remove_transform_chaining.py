"""Remove transform chaining - source_transform_id

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-01-24 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f6g7h8i9j0k1'
down_revision = 'e5f6g7h8i9j0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, update any NULL source_table values from chained transforms
    # Set them to the source transform's source_table
    op.execute("""
        UPDATE transform_recipes t
        SET source_table = st.source_table,
            source_schema = st.source_schema
        FROM transform_recipes st
        WHERE t.source_transform_id = st.id
        AND t.source_table IS NULL
    """)

    # For any remaining NULLs, set a placeholder (should not happen)
    op.execute("""
        UPDATE transform_recipes
        SET source_table = 'unknown'
        WHERE source_table IS NULL
    """)

    # Drop foreign key constraint first
    op.drop_constraint('fk_transform_recipes_source_transform_id', 'transform_recipes', type_='foreignkey')

    # Drop index
    op.drop_index('ix_transform_recipes_source_transform_id', table_name='transform_recipes')

    # Drop source_transform_id column
    op.drop_column('transform_recipes', 'source_transform_id')

    # Make source_table non-nullable again
    op.alter_column('transform_recipes', 'source_table', nullable=False)


def downgrade() -> None:
    # Make source_table nullable
    op.alter_column('transform_recipes', 'source_table', nullable=True)

    # Add source_transform_id column back
    op.add_column('transform_recipes', sa.Column('source_transform_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Create index
    op.create_index('ix_transform_recipes_source_transform_id', 'transform_recipes', ['source_transform_id'])

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_transform_recipes_source_transform_id',
        'transform_recipes',
        'transform_recipes',
        ['source_transform_id'],
        ['id'],
        ondelete='SET NULL'
    )
