"""
Audit Log Models

Database models for comprehensive audit logging.
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.database import Base


class AuditLog(Base):
    """
    Audit log model for tracking all user actions.

    Captures detailed information about every significant action
    performed in the system for security and compliance purposes.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Timestamp
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True, nullable=False)

    # User information
    user_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    user_email = Column(String(255), nullable=True)
    user_name = Column(String(255), nullable=True)

    # Session information
    session_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    geo_location = Column(String(255), nullable=True)

    # Action details
    action = Column(String(100), index=True, nullable=False)  # e.g., 'dashboard.view', 'chart.create'
    action_category = Column(String(50), index=True, nullable=True)  # auth, dashboard, chart, data, admin
    action_type = Column(String(50), nullable=True)  # view, create, update, delete, export, share

    # Resource information
    resource_type = Column(String(50), index=True, nullable=True)  # dashboard, chart, connection, etc.
    resource_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    resource_name = Column(String(255), nullable=True)

    # Request details
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_query = Column(Text, nullable=True)
    request_body = Column(JSONB, nullable=True)  # Sanitized, no passwords

    # Response details
    response_status = Column(Integer, nullable=True)
    response_body_size = Column(Integer, nullable=True)

    # Execution metrics
    duration_ms = Column(Integer, nullable=True)

    # Context
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    tenant_id = Column(UUID(as_uuid=True), index=True, nullable=True)

    # Additional data
    extra_data = Column(JSONB, default={})

    # Error information
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)

    # Success flag
    success = Column(Integer, default=1)  # 1 = success, 0 = failure

    __table_args__ = (
        Index('ix_audit_logs_timestamp_user', timestamp, user_id),
        Index('ix_audit_logs_action_resource', action, resource_type),
        Index('ix_audit_logs_workspace_timestamp', workspace_id, timestamp),
    )


class AuditLogArchive(Base):
    """
    Archive table for older audit logs.

    Used for data retention and performance optimization.
    """
    __tablename__ = "audit_logs_archive"

    id = Column(UUID(as_uuid=True), primary_key=True)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), index=True, nullable=False)
    action_category = Column(String(50), nullable=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    resource_name = Column(String(255), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    success = Column(Integer, default=1)
    extra_data = Column(JSONB, default={})

    # Archive data
    archived_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    archive_reason = Column(String(50), default="retention")


class SecurityAlert(Base):
    """
    Security alert model for suspicious activities.

    Generated automatically when suspicious patterns are detected.
    """
    __tablename__ = "security_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Alert details
    alert_type = Column(String(100), index=True, nullable=False)
    severity = Column(String(20), index=True, nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # User involved
    user_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    user_email = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Related audit logs
    related_audit_ids = Column(JSONB, default=[])

    # Context
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Status
    status = Column(String(20), default="open")  # open, investigating, resolved, dismissed

    # Resolution
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Extra data
    extra_data = Column(JSONB, default={})


# Action Constants

class AuditAction:
    """Constants for audit actions"""

    # Authentication
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_LOGIN_FAILED = "auth.login_failed"
    AUTH_PASSWORD_RESET = "auth.password_reset"
    AUTH_TOKEN_REFRESH = "auth.token_refresh"

    # Dashboard
    DASHBOARD_VIEW = "dashboard.view"
    DASHBOARD_CREATE = "dashboard.create"
    DASHBOARD_UPDATE = "dashboard.update"
    DASHBOARD_DELETE = "dashboard.delete"
    DASHBOARD_SHARE = "dashboard.share"
    DASHBOARD_PUBLISH = "dashboard.publish"
    DASHBOARD_EXPORT = "dashboard.export"

    # Chart
    CHART_VIEW = "chart.view"
    CHART_CREATE = "chart.create"
    CHART_UPDATE = "chart.update"
    CHART_DELETE = "chart.delete"
    CHART_EXPORT = "chart.export"

    # Connection
    CONNECTION_CREATE = "connection.create"
    CONNECTION_UPDATE = "connection.update"
    CONNECTION_DELETE = "connection.delete"
    CONNECTION_TEST = "connection.test"

    # Query
    QUERY_EXECUTE = "query.execute"
    QUERY_SAVE = "query.save"

    # Data
    DATA_EXPORT = "data.export"
    DATA_IMPORT = "data.import"

    # Workspace
    WORKSPACE_CREATE = "workspace.create"
    WORKSPACE_UPDATE = "workspace.update"
    WORKSPACE_DELETE = "workspace.delete"
    WORKSPACE_MEMBER_ADD = "workspace.member_add"
    WORKSPACE_MEMBER_REMOVE = "workspace.member_remove"
    WORKSPACE_INVITE = "workspace.invite"

    # Admin
    ADMIN_USER_CREATE = "admin.user_create"
    ADMIN_USER_UPDATE = "admin.user_update"
    ADMIN_USER_DELETE = "admin.user_delete"
    ADMIN_ROLE_CHANGE = "admin.role_change"
    ADMIN_SETTINGS_UPDATE = "admin.settings_update"


class AlertType:
    """Constants for security alert types"""

    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    SUSPICIOUS_LOGIN = "suspicious_login"
    UNUSUAL_DATA_ACCESS = "unusual_data_access"
    PERMISSION_ESCALATION = "permission_escalation"
    MASS_DATA_EXPORT = "mass_data_export"
    API_RATE_LIMIT = "api_rate_limit"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
