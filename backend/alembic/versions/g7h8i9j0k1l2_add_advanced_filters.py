"""Add advanced filters and drill configuration

Revision ID: g7h8i9j0k1l2
Revises: 232d698e9a25
Create Date: 2026-01-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'g7h8i9j0k1l2'
down_revision = '232d698e9a25'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    """Check if column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(index_name):
    """Check if index exists in any table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    for table_name in inspector.get_table_names():
        indexes = inspector.get_indexes(table_name)
        for idx in indexes:
            if idx['name'] == index_name:
                return True
    return False


def upgrade() -> None:
    # Add new columns to dashboards table
    if not column_exists('dashboards', 'global_filter_config'):
        op.add_column('dashboards', sa.Column('global_filter_config', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    if not column_exists('dashboards', 'default_filters'):
        op.add_column('dashboards', sa.Column('default_filters', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Add new columns to saved_charts table
    if not column_exists('saved_charts', 'filter_config'):
        op.add_column('saved_charts', sa.Column('filter_config', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    if not column_exists('saved_charts', 'default_filters'):
        op.add_column('saved_charts', sa.Column('default_filters', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    if not column_exists('saved_charts', 'drill_config'):
        op.add_column('saved_charts', sa.Column('drill_config', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    if not column_exists('saved_charts', 'conditional_formats'):
        op.add_column('saved_charts', sa.Column('conditional_formats', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Create saved_filter_presets table
    if not table_exists('saved_filter_presets'):
        op.create_table(
            'saved_filter_presets',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('chart_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('filters', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
            sa.Column('slicers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('global_filter_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('is_default', sa.Boolean(), nullable=True, server_default='false'),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['chart_id'], ['saved_charts.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create dashboard_filter_states table
    if not table_exists('dashboard_filter_states'):
        op.create_table(
            'dashboard_filter_states',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('filter_state', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
            sa.Column('date_filter_state', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('cross_filter_state', postgresql.JSON(astext_type=sa.Text()), nullable=True),
            sa.Column('session_id', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # Create indexes (only if they don't exist)
    if not index_exists('ix_saved_filter_presets_dashboard_id'):
        op.create_index('ix_saved_filter_presets_dashboard_id', 'saved_filter_presets', ['dashboard_id'])
    if not index_exists('ix_saved_filter_presets_chart_id'):
        op.create_index('ix_saved_filter_presets_chart_id', 'saved_filter_presets', ['chart_id'])
    if not index_exists('ix_dashboard_filter_states_dashboard_id'):
        op.create_index('ix_dashboard_filter_states_dashboard_id', 'dashboard_filter_states', ['dashboard_id'])
    if not index_exists('ix_dashboard_filter_states_user_id'):
        op.create_index('ix_dashboard_filter_states_user_id', 'dashboard_filter_states', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    if index_exists('ix_dashboard_filter_states_user_id'):
        op.drop_index('ix_dashboard_filter_states_user_id', table_name='dashboard_filter_states')
    if index_exists('ix_dashboard_filter_states_dashboard_id'):
        op.drop_index('ix_dashboard_filter_states_dashboard_id', table_name='dashboard_filter_states')
    if index_exists('ix_saved_filter_presets_chart_id'):
        op.drop_index('ix_saved_filter_presets_chart_id', table_name='saved_filter_presets')
    if index_exists('ix_saved_filter_presets_dashboard_id'):
        op.drop_index('ix_saved_filter_presets_dashboard_id', table_name='saved_filter_presets')

    # Drop tables
    if table_exists('dashboard_filter_states'):
        op.drop_table('dashboard_filter_states')
    if table_exists('saved_filter_presets'):
        op.drop_table('saved_filter_presets')

    # Remove columns from saved_charts
    if column_exists('saved_charts', 'conditional_formats'):
        op.drop_column('saved_charts', 'conditional_formats')
    if column_exists('saved_charts', 'drill_config'):
        op.drop_column('saved_charts', 'drill_config')
    if column_exists('saved_charts', 'default_filters'):
        op.drop_column('saved_charts', 'default_filters')
    if column_exists('saved_charts', 'filter_config'):
        op.drop_column('saved_charts', 'filter_config')

    # Remove columns from dashboards
    if column_exists('dashboards', 'default_filters'):
        op.drop_column('dashboards', 'default_filters')
    if column_exists('dashboards', 'global_filter_config'):
        op.drop_column('dashboards', 'global_filter_config')
