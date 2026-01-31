"""Add report, billing, plugin, integration, theming, compliance, performance, sharing models

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-01-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'j0k1l2m3n4o5'
down_revision = 'i9j0k1l2m3n4'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    # =====================
    # REPORT MODELS
    # =====================

    if not table_exists('reports'):
        op.create_table(
            'reports',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('report_type', sa.String(50), nullable=False),
            sa.Column('content_config', postgresql.JSONB(), server_default='{}'),
            sa.Column('layout_config', postgresql.JSONB(), server_default='{}'),
            sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('chart_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
            sa.Column('query_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('applied_filters', postgresql.JSONB(), server_default='{}'),
            sa.Column('date_range', postgresql.JSONB(), nullable=True),
            sa.Column('export_format', sa.String(20), server_default='pdf'),
            sa.Column('page_size', sa.String(20), server_default='A4'),
            sa.Column('orientation', sa.String(20), server_default='portrait'),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('is_template', sa.Boolean(), server_default='false'),
            sa.Column('is_public', sa.Boolean(), server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('last_generated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE')
        )

    if not table_exists('report_templates'):
        op.create_table(
            'report_templates',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('category', sa.String(100), nullable=True),
            sa.Column('template_config', postgresql.JSONB(), nullable=False, server_default='{}'),
            sa.Column('layout', postgresql.JSONB(), server_default='{}'),
            sa.Column('styles', postgresql.JSONB(), server_default='{}'),
            sa.Column('header_config', postgresql.JSONB(), nullable=True),
            sa.Column('footer_config', postgresql.JSONB(), nullable=True),
            sa.Column('placeholders', postgresql.JSONB(), server_default='[]'),
            sa.Column('thumbnail_url', sa.String(500), nullable=True),
            sa.Column('is_system', sa.Boolean(), server_default='false'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )

    if not table_exists('scheduled_reports'):
        op.create_table(
            'scheduled_reports',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('schedule_name', sa.String(255), nullable=False),
            sa.Column('cron_expression', sa.String(100), nullable=False),
            sa.Column('timezone', sa.String(50), server_default='UTC'),
            sa.Column('delivery_method', sa.String(50), nullable=False),
            sa.Column('recipients', postgresql.JSONB(), server_default='[]'),
            sa.Column('delivery_config', postgresql.JSONB(), server_default='{}'),
            sa.Column('export_format', sa.String(20), server_default='pdf'),
            sa.Column('include_data', sa.Boolean(), server_default='true'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('last_run_status', sa.String(50), nullable=True),
            sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('consecutive_failures', sa.Integer(), server_default='0'),
            sa.Column('last_error', sa.Text(), nullable=True),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE')
        )
        op.create_index('ix_scheduled_reports_next_run', 'scheduled_reports', ['next_run_at', 'is_active'])

    if not table_exists('scheduled_report_executions'):
        op.create_table(
            'scheduled_report_executions',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('scheduled_report_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('status', sa.String(50), nullable=False),
            sa.Column('output_url', sa.String(500), nullable=True),
            sa.Column('output_size_bytes', sa.Integer(), nullable=True),
            sa.Column('recipients_count', sa.Integer(), server_default='0'),
            sa.Column('delivery_status', postgresql.JSONB(), server_default='{}'),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['scheduled_report_id'], ['scheduled_reports.id'], ondelete='CASCADE')
        )
        op.create_index('ix_scheduled_report_executions_report_started', 'scheduled_report_executions', ['scheduled_report_id', 'started_at'])

    # =====================
    # BILLING MODELS
    # =====================

    if not table_exists('billing_plans'):
        op.create_table(
            'billing_plans',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(100), nullable=False, unique=True),
            sa.Column('display_name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('price_monthly', sa.Float(), server_default='0'),
            sa.Column('price_yearly', sa.Float(), server_default='0'),
            sa.Column('currency', sa.String(3), server_default='USD'),
            sa.Column('max_users', sa.Integer(), nullable=True),
            sa.Column('max_dashboards', sa.Integer(), nullable=True),
            sa.Column('max_connections', sa.Integer(), nullable=True),
            sa.Column('max_queries_per_day', sa.Integer(), nullable=True),
            sa.Column('max_storage_gb', sa.Float(), nullable=True),
            sa.Column('max_api_calls_per_month', sa.Integer(), nullable=True),
            sa.Column('features', postgresql.JSONB(), server_default='[]'),
            sa.Column('feature_flags', postgresql.JSONB(), server_default='{}'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('is_public', sa.Boolean(), server_default='true'),
            sa.Column('sort_order', sa.Integer(), server_default='0'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )

    if not table_exists('workspace_subscriptions'):
        op.create_table(
            'workspace_subscriptions',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
            sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('billing_cycle', sa.String(20), server_default='monthly'),
            sa.Column('status', sa.String(50), server_default='active'),
            sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('is_trial', sa.Boolean(), server_default='false'),
            sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
            sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
            sa.Column('payment_method_id', sa.String(255), nullable=True),
            sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
            sa.Column('stripe_customer_id', sa.String(255), nullable=True),
            sa.Column('quantity', sa.Integer(), server_default='1'),
            sa.Column('discount_percent', sa.Float(), server_default='0'),
            sa.Column('discount_ends_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['plan_id'], ['billing_plans.id'], ondelete='RESTRICT')
        )

    if not table_exists('invoices'):
        op.create_table(
            'invoices',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('invoice_number', sa.String(50), nullable=False, unique=True),
            sa.Column('status', sa.String(50), server_default='draft'),
            sa.Column('subtotal', sa.Float(), nullable=False),
            sa.Column('tax', sa.Float(), server_default='0'),
            sa.Column('discount', sa.Float(), server_default='0'),
            sa.Column('total', sa.Float(), nullable=False),
            sa.Column('currency', sa.String(3), server_default='USD'),
            sa.Column('invoice_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
            sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
            sa.Column('line_items', postgresql.JSONB(), server_default='[]'),
            sa.Column('payment_intent_id', sa.String(255), nullable=True),
            sa.Column('stripe_invoice_id', sa.String(255), nullable=True),
            sa.Column('pdf_url', sa.String(500), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['subscription_id'], ['workspace_subscriptions.id'], ondelete='CASCADE')
        )
        op.create_index('ix_invoices_subscription_date', 'invoices', ['subscription_id', 'invoice_date'])

    if not table_exists('usage_records'):
        op.create_table(
            'usage_records',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('usage_type', sa.String(50), nullable=False),
            sa.Column('quantity', sa.Float(), nullable=False),
            sa.Column('unit', sa.String(20), nullable=True),
            sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
            sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('resource_type', sa.String(50), nullable=True),
            sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('extra_data', postgresql.JSONB(), server_default='{}'),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE')
        )
        op.create_index('ix_usage_records_workspace_type_date', 'usage_records', ['workspace_id', 'usage_type', 'recorded_at'])

    if not table_exists('usage_summaries'):
        op.create_table(
            'usage_summaries',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('total_queries', sa.Integer(), server_default='0'),
            sa.Column('total_api_calls', sa.Integer(), server_default='0'),
            sa.Column('total_exports', sa.Integer(), server_default='0'),
            sa.Column('storage_used_bytes', sa.Float(), server_default='0'),
            sa.Column('active_users', sa.Integer(), server_default='0'),
            sa.Column('queries_by_type', postgresql.JSONB(), server_default='{}'),
            sa.Column('top_users', postgresql.JSONB(), server_default='[]'),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE')
        )
        op.create_index('ix_usage_summaries_workspace_date', 'usage_summaries', ['workspace_id', 'date'], unique=True)

    # =====================
    # PLUGIN MODELS
    # =====================

    if not table_exists('plugins'):
        op.create_table(
            'plugins',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(255), nullable=False, unique=True),
            sa.Column('display_name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('version', sa.String(50), nullable=False),
            sa.Column('source', sa.String(50), server_default='marketplace'),
            sa.Column('package_url', sa.String(500), nullable=True),
            sa.Column('repository_url', sa.String(500), nullable=True),
            sa.Column('plugin_type', sa.String(50), nullable=False),
            sa.Column('author', sa.String(255), nullable=True),
            sa.Column('author_email', sa.String(255), nullable=True),
            sa.Column('icon_url', sa.String(500), nullable=True),
            sa.Column('banner_url', sa.String(500), nullable=True),
            sa.Column('config_schema', postgresql.JSONB(), server_default='{}'),
            sa.Column('default_config', postgresql.JSONB(), server_default='{}'),
            sa.Column('required_permissions', postgresql.JSONB(), server_default='[]'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('is_system', sa.Boolean(), server_default='false'),
            sa.Column('installed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('installed_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )

    if not table_exists('plugin_workspace_configs'):
        op.create_table(
            'plugin_workspace_configs',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('plugin_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('config', postgresql.JSONB(), server_default='{}'),
            sa.Column('secrets', postgresql.JSONB(), server_default='{}'),
            sa.Column('is_enabled', sa.Boolean(), server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('enabled_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE')
        )
        op.create_index('ix_plugin_workspace_configs_unique', 'plugin_workspace_configs', ['plugin_id', 'workspace_id'], unique=True)

    if not table_exists('plugin_marketplace'):
        op.create_table(
            'plugin_marketplace',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(255), nullable=False, unique=True),
            sa.Column('display_name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('long_description', sa.Text(), nullable=True),
            sa.Column('latest_version', sa.String(50), nullable=False),
            sa.Column('versions', postgresql.JSONB(), server_default='[]'),
            sa.Column('plugin_type', sa.String(50), nullable=False),
            sa.Column('categories', postgresql.JSONB(), server_default='[]'),
            sa.Column('tags', postgresql.JSONB(), server_default='[]'),
            sa.Column('author', sa.String(255), nullable=True),
            sa.Column('author_url', sa.String(500), nullable=True),
            sa.Column('icon_url', sa.String(500), nullable=True),
            sa.Column('banner_url', sa.String(500), nullable=True),
            sa.Column('screenshots', postgresql.JSONB(), server_default='[]'),
            sa.Column('downloads', sa.Integer(), server_default='0'),
            sa.Column('rating', sa.Float(), server_default='0'),
            sa.Column('reviews_count', sa.Integer(), server_default='0'),
            sa.Column('is_verified', sa.Boolean(), server_default='false'),
            sa.Column('is_featured', sa.Boolean(), server_default='false'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )

    # =====================
    # INTEGRATION MODELS
    # =====================

    if not table_exists('integrations'):
        op.create_table(
            'integrations',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('integration_type', sa.String(50), nullable=False),
            sa.Column('config', postgresql.JSONB(), server_default='{}'),
            sa.Column('auth_type', sa.String(50), nullable=True),
            sa.Column('credentials', postgresql.JSONB(), server_default='{}'),
            sa.Column('oauth_tokens', postgresql.JSONB(), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('connection_status', sa.String(50), server_default='pending'),
            sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('last_error', sa.Text(), nullable=True),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE')
        )
        op.create_index('ix_integrations_workspace_type', 'integrations', ['workspace_id', 'integration_type'])

    if not table_exists('integration_webhooks'):
        op.create_table(
            'integration_webhooks',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('integration_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('webhook_url', sa.String(500), nullable=False),
            sa.Column('secret', sa.String(255), nullable=True),
            sa.Column('events', postgresql.JSONB(), server_default='[]'),
            sa.Column('payload_format', sa.String(20), server_default='json'),
            sa.Column('headers', postgresql.JSONB(), server_default='{}'),
            sa.Column('retry_config', postgresql.JSONB(), server_default='{"max_retries": 3, "retry_delay": 60}'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('last_triggered_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('last_status', sa.String(50), nullable=True),
            sa.Column('failure_count', sa.Integer(), server_default='0'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE')
        )

    if not table_exists('integration_logs'):
        op.create_table(
            'integration_logs',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('integration_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('event_type', sa.String(100), nullable=False),
            sa.Column('direction', sa.String(20), nullable=False),
            sa.Column('request_data', postgresql.JSONB(), nullable=True),
            sa.Column('response_data', postgresql.JSONB(), nullable=True),
            sa.Column('status_code', sa.Integer(), nullable=True),
            sa.Column('success', sa.Boolean(), server_default='true'),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('duration_ms', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE')
        )
        op.create_index('ix_integration_logs_integration_created', 'integration_logs', ['integration_id', 'created_at'])

    if not table_exists('slack_channels'):
        op.create_table(
            'slack_channels',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('integration_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('channel_id', sa.String(100), nullable=False),
            sa.Column('channel_name', sa.String(255), nullable=False),
            sa.Column('channel_type', sa.String(50), server_default='channel'),
            sa.Column('notify_alerts', sa.Boolean(), server_default='true'),
            sa.Column('notify_reports', sa.Boolean(), server_default='false'),
            sa.Column('notify_comments', sa.Boolean(), server_default='false'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE')
        )
        op.create_index('ix_slack_channels_integration_channel', 'slack_channels', ['integration_id', 'channel_id'], unique=True)

    # =====================
    # THEMING MODELS
    # =====================

    if not table_exists('themes'):
        op.create_table(
            'themes',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('display_name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('theme_type', sa.String(50), server_default='custom'),
            sa.Column('primary_color', sa.String(20), server_default='#3B82F6'),
            sa.Column('secondary_color', sa.String(20), server_default='#6366F1'),
            sa.Column('accent_color', sa.String(20), server_default='#8B5CF6'),
            sa.Column('background_color', sa.String(20), server_default='#FFFFFF'),
            sa.Column('surface_color', sa.String(20), server_default='#F3F4F6'),
            sa.Column('text_color', sa.String(20), server_default='#1F2937'),
            sa.Column('dark_primary_color', sa.String(20), server_default='#60A5FA'),
            sa.Column('dark_background_color', sa.String(20), server_default='#111827'),
            sa.Column('dark_surface_color', sa.String(20), server_default='#1F2937'),
            sa.Column('dark_text_color', sa.String(20), server_default='#F9FAFB'),
            sa.Column('chart_colors', postgresql.JSONB(), server_default='[]'),
            sa.Column('font_family', sa.String(100), server_default='Inter'),
            sa.Column('heading_font', sa.String(100), nullable=True),
            sa.Column('font_size_base', sa.Integer(), server_default='14'),
            sa.Column('border_radius', sa.Integer(), server_default='8'),
            sa.Column('shadow_style', sa.String(50), server_default='soft'),
            sa.Column('custom_css', sa.Text(), nullable=True),
            sa.Column('logo_light_url', sa.String(500), nullable=True),
            sa.Column('logo_dark_url', sa.String(500), nullable=True),
            sa.Column('favicon_url', sa.String(500), nullable=True),
            sa.Column('is_system', sa.Boolean(), server_default='false'),
            sa.Column('is_default', sa.Boolean(), server_default='false'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )

    if not table_exists('workspace_themes'):
        op.create_table(
            'workspace_themes',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
            sa.Column('theme_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('color_mode', sa.String(20), server_default='auto'),
            sa.Column('custom_overrides', postgresql.JSONB(), server_default='{}'),
            sa.Column('company_name', sa.String(255), nullable=True),
            sa.Column('logo_url', sa.String(500), nullable=True),
            sa.Column('favicon_url', sa.String(500), nullable=True),
            sa.Column('hide_powered_by', sa.Boolean(), server_default='false'),
            sa.Column('custom_domain', sa.String(255), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], ondelete='SET NULL')
        )

    if not table_exists('user_theme_preferences'):
        op.create_table(
            'user_theme_preferences',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
            sa.Column('color_mode', sa.String(20), server_default='auto'),
            sa.Column('theme_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('compact_mode', sa.Boolean(), server_default='false'),
            sa.Column('high_contrast', sa.Boolean(), server_default='false'),
            sa.Column('reduced_motion', sa.Boolean(), server_default='false'),
            sa.Column('preferred_chart_theme', sa.String(50), server_default='default'),
            sa.Column('chart_animation', sa.Boolean(), server_default='true'),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
        )

    # =====================
    # COMPLIANCE MODELS
    # =====================

    if not table_exists('compliance_policies'):
        op.create_table(
            'compliance_policies',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('policy_type', sa.String(50), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('applies_to', sa.String(50), server_default='all'),
            sa.Column('rules', postgresql.JSONB(), nullable=False, server_default='[]'),
            sa.Column('conditions', postgresql.JSONB(), server_default='{}'),
            sa.Column('enforcement_action', sa.String(50), server_default='warn'),
            sa.Column('notification_config', postgresql.JSONB(), server_default='{}'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('priority', sa.Integer(), server_default='0'),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE')
        )

    if not table_exists('compliance_violations'):
        op.create_table(
            'compliance_violations',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('violation_type', sa.String(100), nullable=False),
            sa.Column('severity', sa.String(20), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('resource_type', sa.String(50), nullable=True),
            sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('evidence', postgresql.JSONB(), server_default='{}'),
            sa.Column('request_data', postgresql.JSONB(), nullable=True),
            sa.Column('status', sa.String(50), server_default='open'),
            sa.Column('resolution', sa.Text(), nullable=True),
            sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['policy_id'], ['compliance_policies.id'], ondelete='CASCADE')
        )
        op.create_index('ix_compliance_violations_policy_status', 'compliance_violations', ['policy_id', 'status'])
        op.create_index('ix_compliance_violations_severity_date', 'compliance_violations', ['severity', 'detected_at'])

    if not table_exists('data_classifications'):
        op.create_table(
            'data_classifications',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(100), nullable=False, unique=True),
            sa.Column('display_name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('level', sa.Integer(), nullable=False),
            sa.Column('color', sa.String(20), server_default='#6B7280'),
            sa.Column('icon', sa.String(50), nullable=True),
            sa.Column('encryption_required', sa.Boolean(), server_default='false'),
            sa.Column('audit_required', sa.Boolean(), server_default='true'),
            sa.Column('export_allowed', sa.Boolean(), server_default='true'),
            sa.Column('sharing_allowed', sa.Boolean(), server_default='true'),
            sa.Column('retention_days', sa.Integer(), nullable=True),
            sa.Column('is_system', sa.Boolean(), server_default='false'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )

    if not table_exists('data_retention_policies'):
        op.create_table(
            'data_retention_policies',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('target_type', sa.String(50), nullable=False),
            sa.Column('target_classification', sa.String(100), nullable=True),
            sa.Column('retention_days', sa.Integer(), nullable=False),
            sa.Column('archive_before_delete', sa.Boolean(), server_default='true'),
            sa.Column('archive_location', sa.String(255), nullable=True),
            sa.Column('run_schedule', sa.String(100), server_default='0 2 * * *'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('total_deleted', sa.Integer(), server_default='0'),
            sa.Column('total_archived', sa.Integer(), server_default='0'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE')
        )

    if not table_exists('consent_records'):
        op.create_table(
            'consent_records',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('consent_type', sa.String(100), nullable=False),
            sa.Column('version', sa.String(50), nullable=True),
            sa.Column('granted', sa.Boolean(), nullable=False),
            sa.Column('granted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('user_agent', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
        )
        op.create_index('ix_consent_records_user_type', 'consent_records', ['user_id', 'consent_type'])

    # =====================
    # PERFORMANCE MODELS
    # =====================

    if not table_exists('query_performance'):
        op.create_table(
            'query_performance',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('query_hash', sa.String(64), nullable=False),
            sa.Column('query_text', sa.Text(), nullable=True),
            sa.Column('query_type', sa.String(50), nullable=True),
            sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('chart_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('execution_time_ms', sa.Integer(), nullable=False),
            sa.Column('rows_returned', sa.Integer(), nullable=True),
            sa.Column('bytes_processed', sa.Float(), nullable=True),
            sa.Column('cpu_time_ms', sa.Integer(), nullable=True),
            sa.Column('memory_bytes', sa.Float(), nullable=True),
            sa.Column('io_reads', sa.Integer(), nullable=True),
            sa.Column('cache_hit', sa.Boolean(), server_default='false'),
            sa.Column('cache_key', sa.String(255), nullable=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='SET NULL')
        )
        op.create_index('ix_query_performance_hash_date', 'query_performance', ['query_hash', 'executed_at'])
        op.create_index('ix_query_performance_connection_date', 'query_performance', ['connection_id', 'executed_at'])

    if not table_exists('slow_query_logs'):
        op.create_table(
            'slow_query_logs',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('query_hash', sa.String(64), nullable=False),
            sa.Column('query_text', sa.Text(), nullable=False),
            sa.Column('execution_time_ms', sa.Integer(), nullable=False),
            sa.Column('threshold_ms', sa.Integer(), nullable=False),
            sa.Column('times_over_threshold', sa.Float(), nullable=True),
            sa.Column('explain_plan', postgresql.JSONB(), nullable=True),
            sa.Column('optimization_suggestions', postgresql.JSONB(), server_default='[]'),
            sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('connection_type', sa.String(50), nullable=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('status', sa.String(50), server_default='new'),
            sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_slow_query_logs_status_date', 'slow_query_logs', ['status', 'detected_at'])

    if not table_exists('dashboard_performance'):
        op.create_table(
            'dashboard_performance',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('total_load_time_ms', sa.Integer(), nullable=False),
            sa.Column('query_time_ms', sa.Integer(), nullable=True),
            sa.Column('render_time_ms', sa.Integer(), nullable=True),
            sa.Column('chart_timings', postgresql.JSONB(), server_default='{}'),
            sa.Column('slowest_chart_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('slowest_chart_time_ms', sa.Integer(), nullable=True),
            sa.Column('total_rows_loaded', sa.Integer(), nullable=True),
            sa.Column('total_queries', sa.Integer(), nullable=True),
            sa.Column('cache_hits', sa.Integer(), server_default='0'),
            sa.Column('cache_misses', sa.Integer(), server_default='0'),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('device_type', sa.String(50), nullable=True),
            sa.Column('browser', sa.String(50), nullable=True),
            sa.Column('viewport_width', sa.Integer(), nullable=True),
            sa.Column('loaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE')
        )
        op.create_index('ix_dashboard_performance_dashboard_date', 'dashboard_performance', ['dashboard_id', 'loaded_at'])

    if not table_exists('system_metrics'):
        op.create_table(
            'system_metrics',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('metric_name', sa.String(100), nullable=False),
            sa.Column('metric_type', sa.String(50), nullable=False),
            sa.Column('value', sa.Float(), nullable=False),
            sa.Column('unit', sa.String(20), nullable=True),
            sa.Column('dimensions', postgresql.JSONB(), server_default='{}'),
            sa.Column('aggregation_type', sa.String(20), server_default='instant'),
            sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_system_metrics_name_date', 'system_metrics', ['metric_name', 'recorded_at'])

    if not table_exists('performance_alerts'):
        op.create_table(
            'performance_alerts',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('alert_type', sa.String(100), nullable=False),
            sa.Column('severity', sa.String(20), nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('metric_name', sa.String(100), nullable=True),
            sa.Column('threshold_value', sa.Float(), nullable=True),
            sa.Column('actual_value', sa.Float(), nullable=True),
            sa.Column('resource_type', sa.String(50), nullable=True),
            sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('status', sa.String(50), server_default='open'),
            sa.Column('acknowledged_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('triggered_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_performance_alerts_status_date', 'performance_alerts', ['status', 'triggered_at'])

    if not table_exists('cache_stats'):
        op.create_table(
            'cache_stats',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
            sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
            sa.Column('granularity', sa.String(20), server_default='hour'),
            sa.Column('cache_type', sa.String(50), nullable=False),
            sa.Column('total_requests', sa.Integer(), server_default='0'),
            sa.Column('cache_hits', sa.Integer(), server_default='0'),
            sa.Column('cache_misses', sa.Integer(), server_default='0'),
            sa.Column('hit_rate', sa.Float(), server_default='0'),
            sa.Column('entries_count', sa.Integer(), server_default='0'),
            sa.Column('total_size_bytes', sa.Float(), server_default='0'),
            sa.Column('evictions', sa.Integer(), server_default='0'),
            sa.Column('expirations', sa.Integer(), server_default='0'),
            sa.Column('avg_hit_latency_ms', sa.Float(), server_default='0'),
            sa.Column('avg_miss_latency_ms', sa.Float(), server_default='0'),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_cache_stats_type_period', 'cache_stats', ['cache_type', 'period_start'])

    # =====================
    # SHARING MODELS
    # =====================

    if not table_exists('shared_links'):
        op.create_table(
            'shared_links',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('token', sa.String(64), nullable=False, unique=True),
            sa.Column('resource_type', sa.String(50), nullable=False),
            sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('access_type', sa.String(50), server_default='view'),
            sa.Column('password_hash', sa.String(255), nullable=True),
            sa.Column('require_login', sa.Boolean(), server_default='false'),
            sa.Column('allow_export', sa.Boolean(), server_default='false'),
            sa.Column('allow_filter', sa.Boolean(), server_default='true'),
            sa.Column('allow_drill', sa.Boolean(), server_default='true'),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('max_views', sa.Integer(), nullable=True),
            sa.Column('view_count', sa.Integer(), server_default='0'),
            sa.Column('allowed_domains', postgresql.JSONB(), server_default='[]'),
            sa.Column('allowed_emails', postgresql.JSONB(), server_default='[]'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('revoked_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_shared_links_resource', 'shared_links', ['resource_type', 'resource_id'])

    if not table_exists('share_permissions'):
        op.create_table(
            'share_permissions',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('resource_type', sa.String(50), nullable=False),
            sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('grantee_type', sa.String(50), nullable=False),
            sa.Column('grantee_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('grantee_email', sa.String(255), nullable=True),
            sa.Column('permission_level', sa.String(50), nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('granted_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_share_permissions_resource', 'share_permissions', ['resource_type', 'resource_id'])
        op.create_index('ix_share_permissions_grantee', 'share_permissions', ['grantee_type', 'grantee_id'])

    if not table_exists('share_invitations'):
        op.create_table(
            'share_invitations',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('token', sa.String(64), nullable=False, unique=True),
            sa.Column('resource_type', sa.String(50), nullable=False),
            sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('email', sa.String(255), nullable=False),
            sa.Column('name', sa.String(255), nullable=True),
            sa.Column('permission_level', sa.String(50), server_default='view'),
            sa.Column('message', sa.Text(), nullable=True),
            sa.Column('status', sa.String(50), server_default='pending'),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('accepted_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('invited_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_share_invitations_email_status', 'share_invitations', ['email', 'status'])

    if not table_exists('share_activities'):
        op.create_table(
            'share_activities',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('resource_type', sa.String(50), nullable=False),
            sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('activity_type', sa.String(100), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('user_email', sa.String(255), nullable=True),
            sa.Column('is_anonymous', sa.Boolean(), server_default='false'),
            sa.Column('shared_link_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('user_agent', sa.Text(), nullable=True),
            sa.Column('activity_data', postgresql.JSONB(), server_default='{}'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_share_activities_resource_date', 'share_activities', ['resource_type', 'resource_id', 'created_at'])

    if not table_exists('comments'):
        op.create_table(
            'comments',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('resource_type', sa.String(50), nullable=False),
            sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('position_x', sa.Float(), nullable=True),
            sa.Column('position_y', sa.Float(), nullable=True),
            sa.Column('chart_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('author_name', sa.String(255), nullable=True),
            sa.Column('is_resolved', sa.Boolean(), server_default='false'),
            sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], ondelete='CASCADE')
        )
        op.create_index('ix_comments_resource', 'comments', ['resource_type', 'resource_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    tables = [
        'comments', 'share_activities', 'share_invitations', 'share_permissions', 'shared_links',
        'cache_stats', 'performance_alerts', 'system_metrics', 'dashboard_performance',
        'slow_query_logs', 'query_performance',
        'consent_records', 'data_retention_policies', 'data_classifications',
        'compliance_violations', 'compliance_policies',
        'user_theme_preferences', 'workspace_themes', 'themes',
        'slack_channels', 'integration_logs', 'integration_webhooks', 'integrations',
        'plugin_marketplace', 'plugin_workspace_configs', 'plugins',
        'usage_summaries', 'usage_records', 'invoices', 'workspace_subscriptions', 'billing_plans',
        'scheduled_report_executions', 'scheduled_reports', 'report_templates', 'reports'
    ]

    for table in tables:
        if table_exists(table):
            op.drop_table(table)
