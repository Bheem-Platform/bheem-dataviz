"""Add workspace, security, subscription, audit, and embed tables

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-01-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h8i9j0k1l2m3'
down_revision = 'g7h8i9j0k1l2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE workspace_role AS ENUM ('owner', 'admin', 'member', 'viewer')")
    op.execute("CREATE TYPE invite_status AS ENUM ('pending', 'accepted', 'declined', 'expired')")
    op.execute("CREATE TYPE rls_filter_type AS ENUM ('static', 'dynamic', 'expression')")
    op.execute("CREATE TYPE rls_operator AS ENUM ('equals', 'not_equals', 'in', 'not_in', 'contains', 'starts_with', 'ends_with', 'greater_than', 'less_than', 'between', 'is_null', 'is_not_null')")
    op.execute("CREATE TYPE schedule_frequency AS ENUM ('once', 'hourly', 'daily', 'weekly', 'monthly', 'custom')")
    op.execute("CREATE TYPE schedule_status AS ENUM ('active', 'paused', 'disabled', 'error')")
    op.execute("CREATE TYPE refresh_type AS ENUM ('full', 'incremental', 'partition')")
    op.execute("CREATE TYPE alert_severity AS ENUM ('info', 'warning', 'error', 'critical')")
    op.execute("CREATE TYPE alert_status AS ENUM ('active', 'triggered', 'acknowledged', 'resolved', 'snoozed')")
    op.execute("CREATE TYPE notification_channel AS ENUM ('email', 'slack', 'teams', 'webhook', 'in_app', 'sms')")

    # ============ WORKSPACE TABLES ============

    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_personal', sa.Boolean(), default=False),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('primary_color', sa.String(7), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('max_members', sa.Integer(), nullable=True),
        sa.Column('max_dashboards', sa.Integer(), nullable=True),
        sa.Column('max_connections', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workspaces_slug', 'workspaces', ['slug'], unique=True)
    op.create_index('ix_workspaces_owner', 'workspaces', ['owner_id'])

    # Create workspace_members table
    op.create_table(
        'workspace_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', postgresql.ENUM('owner', 'admin', 'member', 'viewer', name='workspace_role', create_type=False), nullable=False),
        sa.Column('custom_permissions', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('invited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workspace_members_workspace', 'workspace_members', ['workspace_id'])
    op.create_index('ix_workspace_members_user', 'workspace_members', ['user_id'])
    op.create_index('ix_workspace_members_unique', 'workspace_members', ['workspace_id', 'user_id'], unique=True)

    # Create workspace_invitations table
    op.create_table(
        'workspace_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('owner', 'admin', 'member', 'viewer', name='workspace_role', create_type=False), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'accepted', 'declined', 'expired', name='invite_status', create_type=False), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workspace_invitations_workspace', 'workspace_invitations', ['workspace_id'])
    op.create_index('ix_workspace_invitations_email', 'workspace_invitations', ['email'])
    op.create_index('ix_workspace_invitations_token', 'workspace_invitations', ['token'], unique=True)

    # Create object_permissions table
    op.create_table(
        'object_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('object_type', sa.String(50), nullable=False),
        sa.Column('object_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('role', postgresql.ENUM('owner', 'admin', 'member', 'viewer', name='workspace_role', create_type=False), nullable=True),
        sa.Column('can_view', sa.Boolean(), default=True),
        sa.Column('can_edit', sa.Boolean(), default=False),
        sa.Column('can_delete', sa.Boolean(), default=False),
        sa.Column('can_share', sa.Boolean(), default=False),
        sa.Column('can_export', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_object_permissions_object', 'object_permissions', ['object_type', 'object_id'])
    op.create_index('ix_object_permissions_user', 'object_permissions', ['user_id'])
    op.create_index('ix_object_permissions_workspace', 'object_permissions', ['workspace_id'])

    # ============ SECURITY/RLS TABLES ============

    # Create security_roles table
    op.create_table(
        'security_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('priority', sa.Integer(), default=0),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create user_role_assignments table
    op.create_table(
        'user_role_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('effective_from', sa.DateTime(), nullable=True),
        sa.Column('effective_to', sa.DateTime(), nullable=True),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['security_roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create rls_policies table
    op.create_table(
        'rls_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('table_name', sa.String(255), nullable=True),
        sa.Column('schema_name', sa.String(255), nullable=True),
        sa.Column('filter_logic', sa.String(10), default='AND'),
        sa.Column('conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), default=True),
        sa.Column('priority', sa.Integer(), default=0),
        sa.Column('log_access', sa.Boolean(), default=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['semantic_model_id'], ['semantic_models.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create rls_policy_roles table
    op.create_table(
        'rls_policy_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['policy_id'], ['rls_policies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['security_roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create rls_audit_logs table
    op.create_table(
        'rls_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('table_name', sa.String(255), nullable=True),
        sa.Column('schema_name', sa.String(255), nullable=True),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('access_granted', sa.Boolean(), nullable=False),
        sa.Column('filter_applied', sa.Text(), nullable=True),
        sa.Column('denial_reason', sa.Text(), nullable=True),
        sa.Column('user_attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['policy_id'], ['rls_policies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rls_audit_logs_evaluated_at', 'rls_audit_logs', ['evaluated_at'])

    # Create user_attributes table
    op.create_table(
        'user_attributes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attribute_name', sa.String(255), nullable=False),
        sa.Column('attribute_value', sa.Text(), nullable=False),
        sa.Column('source', sa.String(50), default='manual'),
        sa.Column('effective_from', sa.DateTime(), nullable=True),
        sa.Column('effective_to', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create rls_configuration table
    op.create_table(
        'rls_configuration',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('default_deny', sa.Boolean(), default=False),
        sa.Column('cache_ttl_seconds', sa.Integer(), default=300),
        sa.Column('log_all_access', sa.Boolean(), default=False),
        sa.Column('audit_mode', sa.Boolean(), default=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id')
    )

    # ============ SUBSCRIPTION/SCHEDULE TABLES ============

    # Create refresh_schedules table
    op.create_table(
        'refresh_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('frequency', postgresql.ENUM('once', 'hourly', 'daily', 'weekly', 'monthly', 'custom', name='schedule_frequency', create_type=False), nullable=False),
        sa.Column('cron_expression', sa.String(100), nullable=True),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('hour', sa.Integer(), nullable=True),
        sa.Column('minute', sa.Integer(), default=0),
        sa.Column('day_of_week', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('day_of_month', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('refresh_type', postgresql.ENUM('full', 'incremental', 'partition', name='refresh_type', create_type=False), nullable=True),
        sa.Column('incremental_column', sa.String(255), nullable=True),
        sa.Column('incremental_lookback_days', sa.Integer(), default=1),
        sa.Column('timeout_seconds', sa.Integer(), default=3600),
        sa.Column('max_retries', sa.Integer(), default=3),
        sa.Column('retry_delay_minutes', sa.Integer(), default=5),
        sa.Column('notify_on_success', sa.Boolean(), default=False),
        sa.Column('notify_on_failure', sa.Boolean(), default=True),
        sa.Column('notification_recipients', postgresql.JSONB(astext_type=sa.Text()), default=[]),
        sa.Column('status', postgresql.ENUM('active', 'paused', 'disabled', 'error', name='schedule_status', create_type=False), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), default=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_run_status', sa.String(50), nullable=True),
        sa.Column('last_run_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('last_run_error', sa.Text(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), default=0),
        sa.Column('total_runs', sa.Integer(), default=0),
        sa.Column('successful_runs', sa.Integer(), default=0),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['semantic_model_id'], ['semantic_models.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create schedule_executions table
    op.create_table(
        'schedule_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('schedule_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('rows_processed', sa.Integer(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('triggered_by', sa.String(50), default='schedule'),
        sa.Column('triggered_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('log_output', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['schedule_id'], ['refresh_schedules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create alert_rules table
    op.create_table(
        'alert_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('chart_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('kpi_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('severity', postgresql.ENUM('info', 'warning', 'error', 'critical', name='alert_severity', create_type=False), nullable=True),
        sa.Column('conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('condition_logic', sa.String(10), default='AND'),
        sa.Column('evaluation_frequency', postgresql.ENUM('once', 'hourly', 'daily', 'weekly', 'monthly', 'custom', name='schedule_frequency', create_type=False), nullable=True),
        sa.Column('evaluation_cron', sa.String(100), nullable=True),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('notification_channels', postgresql.ARRAY(sa.String()), default=[]),
        sa.Column('notification_recipients', postgresql.JSONB(astext_type=sa.Text()), default=[]),
        sa.Column('notification_message_template', sa.Text(), nullable=True),
        sa.Column('min_interval_minutes', sa.Integer(), default=60),
        sa.Column('snooze_until', sa.DateTime(), nullable=True),
        sa.Column('status', postgresql.ENUM('active', 'triggered', 'acknowledged', 'resolved', 'snoozed', name='alert_status', create_type=False), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), default=True),
        sa.Column('last_evaluated_at', sa.DateTime(), nullable=True),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('last_value', sa.Float(), nullable=True),
        sa.Column('trigger_count', sa.Integer(), default=0),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chart_id'], ['saved_charts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['kpi_id'], ['saved_kpis.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create alert_executions table
    op.create_table(
        'alert_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('alert_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluated_at', sa.DateTime(), nullable=False),
        sa.Column('triggered', sa.Boolean(), default=False),
        sa.Column('condition_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('notifications_sent', postgresql.JSONB(astext_type=sa.Text()), default=[]),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['alert_id'], ['alert_rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('chart_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('frequency', postgresql.ENUM('once', 'hourly', 'daily', 'weekly', 'monthly', 'custom', name='schedule_frequency', create_type=False), nullable=True),
        sa.Column('cron_expression', sa.String(100), nullable=True),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('hour', sa.Integer(), default=9),
        sa.Column('minute', sa.Integer(), default=0),
        sa.Column('day_of_week', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('day_of_month', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('delivery_channel', postgresql.ENUM('email', 'slack', 'teams', 'webhook', 'in_app', 'sms', name='notification_channel', create_type=False), nullable=True),
        sa.Column('recipients', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('export_format', sa.String(20), default='pdf'),
        sa.Column('include_filters', sa.Boolean(), default=True),
        sa.Column('page_size', sa.String(20), default='A4'),
        sa.Column('orientation', sa.String(20), default='landscape'),
        sa.Column('filter_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_sent_at', sa.DateTime(), nullable=True),
        sa.Column('next_send_at', sa.DateTime(), nullable=True),
        sa.Column('send_count', sa.Integer(), default=0),
        sa.Column('failure_count', sa.Integer(), default=0),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chart_id'], ['saved_charts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notification_templates table
    op.create_table(
        'notification_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('channel', postgresql.ENUM('email', 'slack', 'teams', 'webhook', 'in_app', 'sms', name='notification_channel', create_type=False), nullable=False),
        sa.Column('subject_template', sa.String(500), nullable=True),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ============ AUDIT TABLES ============

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('user_name', sa.String(255), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('geo_location', sa.String(255), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('action_category', sa.String(50), nullable=True),
        sa.Column('action_type', sa.String(50), nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resource_name', sa.String(255), nullable=True),
        sa.Column('request_method', sa.String(10), nullable=True),
        sa.Column('request_path', sa.String(500), nullable=True),
        sa.Column('request_query', sa.Text(), nullable=True),
        sa.Column('request_body', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_body_size', sa.Integer(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('success', sa.Integer(), default=1),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_action_category', 'audit_logs', ['action_category'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_resource_id', 'audit_logs', ['resource_id'])
    op.create_index('ix_audit_logs_workspace_id', 'audit_logs', ['workspace_id'])
    op.create_index('ix_audit_logs_timestamp_user', 'audit_logs', ['timestamp', 'user_id'])
    op.create_index('ix_audit_logs_action_resource', 'audit_logs', ['action', 'resource_type'])
    op.create_index('ix_audit_logs_workspace_timestamp', 'audit_logs', ['workspace_id', 'timestamp'])

    # Create audit_logs_archive table
    op.create_table(
        'audit_logs_archive',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('action_category', sa.String(50), nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resource_name', sa.String(255), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('success', sa.Integer(), default=1),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archive_reason', sa.String(50), default='retention'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_archive_timestamp', 'audit_logs_archive', ['timestamp'])
    op.create_index('ix_audit_logs_archive_user_id', 'audit_logs_archive', ['user_id'])
    op.create_index('ix_audit_logs_archive_action', 'audit_logs_archive', ['action'])
    op.create_index('ix_audit_logs_archive_workspace_id', 'audit_logs_archive', ['workspace_id'])

    # Create security_alerts table
    op.create_table(
        'security_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('alert_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('related_audit_ids', postgresql.JSONB(astext_type=sa.Text()), default=[]),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(20), default='open'),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_security_alerts_created_at', 'security_alerts', ['created_at'])
    op.create_index('ix_security_alerts_alert_type', 'security_alerts', ['alert_type'])
    op.create_index('ix_security_alerts_severity', 'security_alerts', ['severity'])
    op.create_index('ix_security_alerts_user_id', 'security_alerts', ['user_id'])

    # ============ EMBED TABLES ============

    # Create embed_tokens table
    op.create_table(
        'embed_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('allow_interactions', sa.Boolean(), default=True),
        sa.Column('allow_export', sa.Boolean(), default=False),
        sa.Column('allow_fullscreen', sa.Boolean(), default=True),
        sa.Column('allow_comments', sa.Boolean(), default=False),
        sa.Column('theme', sa.String(50), default='auto'),
        sa.Column('show_header', sa.Boolean(), default=True),
        sa.Column('show_toolbar', sa.Boolean(), default=False),
        sa.Column('custom_css', sa.Text(), nullable=True),
        sa.Column('allowed_domains', postgresql.JSONB(astext_type=sa.Text()), default=[]),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_views', sa.Integer(), nullable=True),
        sa.Column('view_count', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_embed_tokens_token_hash', 'embed_tokens', ['token_hash'], unique=True)
    op.create_index('ix_embed_tokens_created_by', 'embed_tokens', ['created_by'])
    op.create_index('ix_embed_tokens_workspace_id', 'embed_tokens', ['workspace_id'])
    op.create_index('ix_embed_tokens_resource_id', 'embed_tokens', ['resource_id'])
    op.create_index('ix_embed_tokens_resource', 'embed_tokens', ['resource_type', 'resource_id'])
    op.create_index('ix_embed_tokens_created_by_active', 'embed_tokens', ['created_by', 'is_active'])

    # Create embed_sessions table
    op.create_table(
        'embed_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.String(255), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('origin_domain', sa.String(255), nullable=True),
        sa.Column('origin_url', sa.Text(), nullable=True),
        sa.Column('referrer', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('browser', sa.String(50), nullable=True),
        sa.Column('os', sa.String(50), nullable=True),
        sa.Column('interaction_count', sa.Integer(), default=0),
        sa.Column('filter_changes', sa.Integer(), default=0),
        sa.Column('exports_count', sa.Integer(), default=0),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.ForeignKeyConstraint(['token_id'], ['embed_tokens.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_embed_sessions_token_id', 'embed_sessions', ['token_id'])
    op.create_index('ix_embed_sessions_session_id', 'embed_sessions', ['session_id'])
    op.create_index('ix_embed_sessions_started_at', 'embed_sessions', ['started_at'])
    op.create_index('ix_embed_sessions_token_started', 'embed_sessions', ['token_id', 'started_at'])

    # Create embed_analytics table
    op.create_table(
        'embed_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_views', sa.Integer(), default=0),
        sa.Column('unique_sessions', sa.Integer(), default=0),
        sa.Column('total_interactions', sa.Integer(), default=0),
        sa.Column('total_exports', sa.Integer(), default=0),
        sa.Column('avg_duration_seconds', sa.Integer(), default=0),
        sa.Column('desktop_views', sa.Integer(), default=0),
        sa.Column('mobile_views', sa.Integer(), default=0),
        sa.Column('tablet_views', sa.Integer(), default=0),
        sa.Column('top_domains', postgresql.JSONB(astext_type=sa.Text()), default=[]),
        sa.ForeignKeyConstraint(['token_id'], ['embed_tokens.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_embed_analytics_token_id', 'embed_analytics', ['token_id'])
    op.create_index('ix_embed_analytics_date', 'embed_analytics', ['date'])
    op.create_index('ix_embed_analytics_token_date', 'embed_analytics', ['token_id', 'date'], unique=True)

    # Create embed_whitelists table
    op.create_table(
        'embed_whitelists',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain', sa.String(255), nullable=False),
        sa.Column('is_wildcard', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('added_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_embed_whitelists_workspace_id', 'embed_whitelists', ['workspace_id'])
    op.create_index('ix_embed_whitelists_workspace_domain', 'embed_whitelists', ['workspace_id', 'domain'], unique=True)


def downgrade() -> None:
    # Drop embed tables
    op.drop_table('embed_whitelists')
    op.drop_table('embed_analytics')
    op.drop_table('embed_sessions')
    op.drop_table('embed_tokens')

    # Drop audit tables
    op.drop_table('security_alerts')
    op.drop_table('audit_logs_archive')
    op.drop_table('audit_logs')

    # Drop subscription tables
    op.drop_table('notification_templates')
    op.drop_table('subscriptions')
    op.drop_table('alert_executions')
    op.drop_table('alert_rules')
    op.drop_table('schedule_executions')
    op.drop_table('refresh_schedules')

    # Drop security/RLS tables
    op.drop_table('rls_configuration')
    op.drop_table('user_attributes')
    op.drop_table('rls_audit_logs')
    op.drop_table('rls_policy_roles')
    op.drop_table('rls_policies')
    op.drop_table('user_role_assignments')
    op.drop_table('security_roles')

    # Drop workspace tables
    op.drop_table('object_permissions')
    op.drop_table('workspace_invitations')
    op.drop_table('workspace_members')
    op.drop_table('workspaces')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS notification_channel")
    op.execute("DROP TYPE IF EXISTS alert_status")
    op.execute("DROP TYPE IF EXISTS alert_severity")
    op.execute("DROP TYPE IF EXISTS refresh_type")
    op.execute("DROP TYPE IF EXISTS schedule_status")
    op.execute("DROP TYPE IF EXISTS schedule_frequency")
    op.execute("DROP TYPE IF EXISTS rls_operator")
    op.execute("DROP TYPE IF EXISTS rls_filter_type")
    op.execute("DROP TYPE IF EXISTS invite_status")
    op.execute("DROP TYPE IF EXISTS workspace_role")
