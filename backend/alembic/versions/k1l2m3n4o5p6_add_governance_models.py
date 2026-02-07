"""Add governance models - data ownership, lineage, versioning, quality, apps, schema tracking, analytics

Revision ID: k1l2m3n4o5p6
Revises: j0k1l2m3n4o5
Create Date: 2026-02-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'k1l2m3n4o5p6'
down_revision = 'j0k1l2m3n4o5'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def enum_exists(enum_name):
    """Check if an enum type exists."""
    bind = op.get_bind()
    result = bind.execute(sa.text(
        "SELECT 1 FROM pg_type WHERE typname = :name"
    ), {"name": enum_name})
    return result.fetchone() is not None


def upgrade() -> None:
    # Create enum types
    if not enum_exists('data_owner_type'):
        op.execute("CREATE TYPE data_owner_type AS ENUM ('primary', 'steward', 'custodian', 'consumer')")

    if not enum_exists('environment_type'):
        op.execute("CREATE TYPE environment_type AS ENUM ('development', 'staging', 'production')")

    if not enum_exists('promotion_status'):
        op.execute("CREATE TYPE promotion_status AS ENUM ('pending', 'approved', 'rejected', 'deployed', 'rolled_back')")

    if not enum_exists('lineage_node_type'):
        op.execute("CREATE TYPE lineage_node_type AS ENUM ('connection', 'table', 'column', 'transform', 'semantic_model', 'measure', 'dimension', 'chart', 'dashboard', 'kpi')")

    if not enum_exists('versionable_type'):
        op.execute("CREATE TYPE versionable_type AS ENUM ('dashboard', 'chart', 'semantic_model', 'transform', 'report', 'kpi', 'rls_policy')")

    if not enum_exists('quality_rule_type'):
        op.execute("CREATE TYPE quality_rule_type AS ENUM ('not_null', 'unique', 'range_check', 'regex', 'enum_check', 'foreign_key', 'custom_sql', 'freshness', 'row_count')")

    if not enum_exists('quality_severity'):
        op.execute("CREATE TYPE quality_severity AS ENUM ('info', 'warning', 'error', 'critical')")

    if not enum_exists('quality_check_status'):
        op.execute("CREATE TYPE quality_check_status AS ENUM ('pending', 'running', 'passed', 'failed', 'error')")

    if not enum_exists('schema_change_type'):
        op.execute("CREATE TYPE schema_change_type AS ENUM ('column_added', 'column_removed', 'column_type_changed', 'table_added', 'table_removed')")

    if not enum_exists('app_status'):
        op.execute("CREATE TYPE app_status AS ENUM ('draft', 'published', 'archived')")

    # =========================================================================
    # DATA STEWARDS TABLE
    # =========================================================================
    if not table_exists('data_stewards'):
        op.create_table(
            'data_stewards',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('user_email', sa.String(255), nullable=False),
            sa.Column('user_name', sa.String(255), nullable=False),
            sa.Column('owner_type', postgresql.ENUM('primary', 'steward', 'custodian', 'consumer', name='data_owner_type', create_type=False), default='steward'),
            sa.Column('department', sa.String(100), nullable=True),
            sa.Column('domain', sa.String(100), nullable=True),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )

    # =========================================================================
    # DATA OWNERSHIP TABLE
    # =========================================================================
    if not table_exists('data_ownership'):
        op.create_table(
            'data_ownership',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('asset_type', sa.String(50), nullable=False),
            sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('asset_name', sa.String(255), nullable=False),
            sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
            sa.Column('table_name', sa.String(255), nullable=True),
            sa.Column('column_name', sa.String(255), nullable=True),
            sa.Column('steward_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('data_stewards.id'), nullable=False),
            sa.Column('owner_type', postgresql.ENUM('primary', 'steward', 'custodian', 'consumer', name='data_owner_type', create_type=False), default='primary'),
            sa.Column('sla_freshness_hours', sa.Integer, nullable=True),
            sa.Column('sla_availability_percent', sa.Float, nullable=True),
            sa.Column('quality_threshold', sa.Float, default=95.0),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('business_glossary', sa.Text, nullable=True),
            sa.Column('pii_flag', sa.Boolean, default=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )

    # =========================================================================
    # DEPLOYMENT ENVIRONMENTS TABLE
    # =========================================================================
    if not table_exists('deployment_environments'):
        op.create_table(
            'deployment_environments',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('environment_type', postgresql.ENUM('development', 'staging', 'production', name='environment_type', create_type=False), nullable=False),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('is_default', sa.Boolean, default=False),
            sa.Column('is_protected', sa.Boolean, default=False),
            sa.Column('connection_overrides', postgresql.JSONB, default={}),
            sa.Column('allowed_deployers', postgresql.JSONB, default=[]),
            sa.Column('required_approvers', postgresql.JSONB, default=[]),
            sa.Column('min_approvals', sa.Integer, default=1),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )

    # =========================================================================
    # DEPLOYMENT PROMOTIONS TABLE
    # =========================================================================
    if not table_exists('deployment_promotions'):
        op.create_table(
            'deployment_promotions',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('asset_type', sa.String(50), nullable=False),
            sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('asset_name', sa.String(255), nullable=False),
            sa.Column('version_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('source_environment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('deployment_environments.id'), nullable=False),
            sa.Column('target_environment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('deployment_environments.id'), nullable=False),
            sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', 'deployed', 'rolled_back', name='promotion_status', create_type=False), default='pending'),
            sa.Column('requested_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('approvals', postgresql.JSONB, default=[]),
            sa.Column('rejections', postgresql.JSONB, default=[]),
            sa.Column('deployed_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('promotion_notes', sa.Text, nullable=True),
            sa.Column('change_summary', postgresql.JSONB, default={}),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )

    # =========================================================================
    # LINEAGE NODES TABLE
    # =========================================================================
    if not table_exists('lineage_nodes'):
        op.create_table(
            'lineage_nodes',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('node_type', postgresql.ENUM('connection', 'table', 'column', 'transform', 'semantic_model', 'measure', 'dimension', 'chart', 'dashboard', 'kpi', name='lineage_node_type', create_type=False), nullable=False),
            sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('asset_name', sa.String(255), nullable=False),
            sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('schema_name', sa.String(255), nullable=True),
            sa.Column('table_name', sa.String(255), nullable=True),
            sa.Column('column_name', sa.String(255), nullable=True),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('node_metadata', postgresql.JSONB, default={}),
            sa.Column('quality_score', sa.Float, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )

    # =========================================================================
    # LINEAGE EDGES TABLE
    # =========================================================================
    if not table_exists('lineage_edges'):
        op.create_table(
            'lineage_edges',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('source_node_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lineage_nodes.id'), nullable=False),
            sa.Column('target_node_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lineage_nodes.id'), nullable=False),
            sa.Column('edge_type', sa.String(50), default='derived_from'),
            sa.Column('transformation_type', sa.String(100), nullable=True),
            sa.Column('transformation_sql', sa.Text, nullable=True),
            sa.Column('confidence', sa.Float, default=1.0),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # =========================================================================
    # ASSET VERSIONS TABLE
    # =========================================================================
    if not table_exists('asset_versions'):
        op.create_table(
            'asset_versions',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('asset_type', postgresql.ENUM('dashboard', 'chart', 'semantic_model', 'transform', 'report', 'kpi', 'rls_policy', name='versionable_type', create_type=False), nullable=False),
            sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('asset_name', sa.String(255), nullable=False),
            sa.Column('version_number', sa.Integer, nullable=False),
            sa.Column('version_label', sa.String(100), nullable=True),
            sa.Column('snapshot', postgresql.JSONB, nullable=False),
            sa.Column('changes_summary', sa.Text, nullable=True),
            sa.Column('changes_diff', postgresql.JSONB, default={}),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('environment_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('is_current', sa.Boolean, default=True),
            sa.Column('is_published', sa.Boolean, default=False),
        )
        op.create_index('ix_asset_versions_asset', 'asset_versions', ['asset_type', 'asset_id'])

    # =========================================================================
    # DATA QUALITY RULES TABLE
    # =========================================================================
    if not table_exists('data_quality_rules'):
        op.create_table(
            'data_quality_rules',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('rule_type', postgresql.ENUM('not_null', 'unique', 'range_check', 'regex', 'enum_check', 'foreign_key', 'custom_sql', 'freshness', 'row_count', name='quality_rule_type', create_type=False), nullable=False),
            sa.Column('severity', postgresql.ENUM('info', 'warning', 'error', 'critical', name='quality_severity', create_type=False), default='warning'),
            sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('table_name', sa.String(255), nullable=False),
            sa.Column('column_name', sa.String(255), nullable=True),
            sa.Column('rule_config', postgresql.JSONB, nullable=False),
            sa.Column('error_threshold', sa.Float, default=0),
            sa.Column('warning_threshold', sa.Float, default=5),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('check_frequency', sa.String(50), default='daily'),
            sa.Column('last_check_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )

    # =========================================================================
    # DATA QUALITY CHECKS TABLE
    # =========================================================================
    if not table_exists('data_quality_checks'):
        op.create_table(
            'data_quality_checks',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('data_quality_rules.id'), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('status', postgresql.ENUM('pending', 'running', 'passed', 'failed', 'error', name='quality_check_status', create_type=False), nullable=False),
            sa.Column('total_rows', sa.Integer, default=0),
            sa.Column('passed_rows', sa.Integer, default=0),
            sa.Column('failed_rows', sa.Integer, default=0),
            sa.Column('pass_rate', sa.Float, default=0),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('duration_ms', sa.Integer, nullable=True),
            sa.Column('error_message', sa.Text, nullable=True),
            sa.Column('failed_samples', postgresql.JSONB, default=[]),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # =========================================================================
    # DATA QUALITY SCORES TABLE
    # =========================================================================
    if not table_exists('data_quality_scores'):
        op.create_table(
            'data_quality_scores',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('asset_type', sa.String(50), nullable=False),
            sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('table_name', sa.String(255), nullable=True),
            sa.Column('column_name', sa.String(255), nullable=True),
            sa.Column('overall_score', sa.Float, nullable=False),
            sa.Column('completeness_score', sa.Float, nullable=True),
            sa.Column('validity_score', sa.Float, nullable=True),
            sa.Column('freshness_score', sa.Float, nullable=True),
            sa.Column('rules_passed', sa.Integer, default=0),
            sa.Column('rules_failed', sa.Integer, default=0),
            sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # =========================================================================
    # SCHEMA SNAPSHOTS TABLE
    # =========================================================================
    if not table_exists('schema_snapshots'):
        op.create_table(
            'schema_snapshots',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('tables', postgresql.JSONB, nullable=False),
            sa.Column('snapshot_hash', sa.String(64), nullable=False),
            sa.Column('tables_count', sa.Integer, default=0),
            sa.Column('columns_count', sa.Integer, default=0),
            sa.Column('captured_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # =========================================================================
    # SCHEMA CHANGES TABLE
    # =========================================================================
    if not table_exists('schema_changes'):
        op.create_table(
            'schema_changes',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('old_snapshot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('schema_snapshots.id'), nullable=False),
            sa.Column('new_snapshot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('schema_snapshots.id'), nullable=False),
            sa.Column('change_type', postgresql.ENUM('column_added', 'column_removed', 'column_type_changed', 'table_added', 'table_removed', name='schema_change_type', create_type=False), nullable=False),
            sa.Column('table_name', sa.String(255), nullable=False),
            sa.Column('column_name', sa.String(255), nullable=True),
            sa.Column('old_value', postgresql.JSONB, nullable=True),
            sa.Column('new_value', postgresql.JSONB, nullable=True),
            sa.Column('is_breaking', sa.Boolean, default=False),
            sa.Column('affected_assets', postgresql.JSONB, default=[]),
            sa.Column('acknowledged', sa.Boolean, default=False),
            sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # =========================================================================
    # APPS TABLE
    # =========================================================================
    if not table_exists('apps'):
        op.create_table(
            'apps',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('slug', sa.String(100), nullable=False, index=True),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('icon', sa.String(255), nullable=True),
            sa.Column('color', sa.String(7), nullable=True),
            sa.Column('dashboards', postgresql.JSONB, default=[]),
            sa.Column('charts', postgresql.JSONB, default=[]),
            sa.Column('reports', postgresql.JSONB, default=[]),
            sa.Column('navigation', postgresql.JSONB, default=[]),
            sa.Column('landing_dashboard_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('status', postgresql.ENUM('draft', 'published', 'archived', name='app_status', create_type=False), default='draft'),
            sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('published_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('version', sa.String(20), default='1.0.0'),
            sa.Column('is_public', sa.Boolean, default=False),
            sa.Column('install_count', sa.Integer, default=0),
            sa.Column('view_count', sa.Integer, default=0),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )
        op.create_unique_constraint('uq_apps_workspace_slug', 'apps', ['workspace_id', 'slug'])

    # =========================================================================
    # APP INSTALLATIONS TABLE
    # =========================================================================
    if not table_exists('app_installations'):
        op.create_table(
            'app_installations',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('app_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('apps.id'), nullable=False),
            sa.Column('installed_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('target_workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('preferences', postgresql.JSONB, default={}),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('installed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    # =========================================================================
    # USER ANALYTICS TABLE
    # =========================================================================
    if not table_exists('user_analytics'):
        op.create_table(
            'user_analytics',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
            sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
            sa.Column('period_type', sa.String(20), nullable=False),
            sa.Column('sessions_count', sa.Integer, default=0),
            sa.Column('total_duration_seconds', sa.Integer, default=0),
            sa.Column('dashboards_viewed', sa.Integer, default=0),
            sa.Column('charts_viewed', sa.Integer, default=0),
            sa.Column('reports_generated', sa.Integer, default=0),
            sa.Column('queries_executed', sa.Integer, default=0),
            sa.Column('exports_count', sa.Integer, default=0),
            sa.Column('filters_applied', sa.Integer, default=0),
            sa.Column('drill_downs', sa.Integer, default=0),
            sa.Column('dashboards_created', sa.Integer, default=0),
            sa.Column('charts_created', sa.Integer, default=0),
            sa.Column('top_dashboards', postgresql.JSONB, default=[]),
            sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index('ix_user_analytics_period', 'user_analytics', ['workspace_id', 'user_id', 'period_type', 'period_start'])

    # =========================================================================
    # FEATURE ADOPTION TABLE
    # =========================================================================
    if not table_exists('feature_adoption'):
        op.create_table(
            'feature_adoption',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
            sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
            sa.Column('feature_name', sa.String(100), nullable=False),
            sa.Column('total_users', sa.Integer, default=0),
            sa.Column('active_users', sa.Integer, default=0),
            sa.Column('usage_count', sa.Integer, default=0),
            sa.Column('adoption_rate', sa.Float, default=0),
            sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index('ix_feature_adoption_period', 'feature_adoption', ['workspace_id', 'feature_name', 'period_start'])

    # =========================================================================
    # CONTENT POPULARITY TABLE
    # =========================================================================
    if not table_exists('content_popularity'):
        op.create_table(
            'content_popularity',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('content_type', sa.String(50), nullable=False),
            sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('content_name', sa.String(255), nullable=False),
            sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
            sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
            sa.Column('unique_viewers', sa.Integer, default=0),
            sa.Column('total_views', sa.Integer, default=0),
            sa.Column('shares_count', sa.Integer, default=0),
            sa.Column('exports_count', sa.Integer, default=0),
            sa.Column('popularity_score', sa.Float, default=0),
            sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index('ix_content_popularity_period', 'content_popularity', ['workspace_id', 'content_type', 'period_start'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('content_popularity') if table_exists('content_popularity') else None
    op.drop_table('feature_adoption') if table_exists('feature_adoption') else None
    op.drop_table('user_analytics') if table_exists('user_analytics') else None
    op.drop_table('app_installations') if table_exists('app_installations') else None
    op.drop_table('apps') if table_exists('apps') else None
    op.drop_table('schema_changes') if table_exists('schema_changes') else None
    op.drop_table('schema_snapshots') if table_exists('schema_snapshots') else None
    op.drop_table('data_quality_scores') if table_exists('data_quality_scores') else None
    op.drop_table('data_quality_checks') if table_exists('data_quality_checks') else None
    op.drop_table('data_quality_rules') if table_exists('data_quality_rules') else None
    op.drop_table('asset_versions') if table_exists('asset_versions') else None
    op.drop_table('lineage_edges') if table_exists('lineage_edges') else None
    op.drop_table('lineage_nodes') if table_exists('lineage_nodes') else None
    op.drop_table('deployment_promotions') if table_exists('deployment_promotions') else None
    op.drop_table('deployment_environments') if table_exists('deployment_environments') else None
    op.drop_table('data_ownership') if table_exists('data_ownership') else None
    op.drop_table('data_stewards') if table_exists('data_stewards') else None

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS app_status")
    op.execute("DROP TYPE IF EXISTS schema_change_type")
    op.execute("DROP TYPE IF EXISTS quality_check_status")
    op.execute("DROP TYPE IF EXISTS quality_severity")
    op.execute("DROP TYPE IF EXISTS quality_rule_type")
    op.execute("DROP TYPE IF EXISTS versionable_type")
    op.execute("DROP TYPE IF EXISTS lineage_node_type")
    op.execute("DROP TYPE IF EXISTS promotion_status")
    op.execute("DROP TYPE IF EXISTS environment_type")
    op.execute("DROP TYPE IF EXISTS data_owner_type")
