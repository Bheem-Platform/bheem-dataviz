"""
Audit Log Schemas

Pydantic schemas for audit logging API.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class ActionCategory(str, Enum):
    """Categories of audit actions"""
    AUTH = "auth"
    DASHBOARD = "dashboard"
    CHART = "chart"
    CONNECTION = "connection"
    QUERY = "query"
    DATA = "data"
    WORKSPACE = "workspace"
    ADMIN = "admin"
    SYSTEM = "system"


class ActionType(str, Enum):
    """Types of actions"""
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    SHARE = "share"
    EXECUTE = "execute"
    LOGIN = "login"
    LOGOUT = "logout"


class AlertSeverity(str, Enum):
    """Security alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Security alert status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


# Audit Log Schemas

class AuditLogBase(BaseModel):
    """Base audit log schema"""
    action: str
    action_category: Optional[ActionCategory] = None
    action_type: Optional[ActionType] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log entry"""
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_body: Optional[dict[str, Any]] = None
    response_status: Optional[int] = None
    duration_ms: Optional[int] = None
    workspace_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    """Schema for audit log response"""
    id: str
    timestamp: datetime
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    response_status: Optional[int] = None
    duration_ms: Optional[int] = None
    workspace_id: Optional[str] = None
    success: int = 1
    error_message: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs"""
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: Optional[str] = None
    action_category: Optional[ActionCategory] = None
    action_type: Optional[ActionType] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    workspace_id: Optional[str] = None
    ip_address: Optional[str] = None
    success_only: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AuditLogSummary(BaseModel):
    """Summary of audit logs"""
    total_events: int
    successful_events: int
    failed_events: int
    unique_users: int
    top_actions: list[dict[str, Any]]
    activity_by_hour: list[dict[str, Any]]
    activity_by_category: dict[str, int]


class AuditLogExport(BaseModel):
    """Schema for audit log export"""
    format: str = "csv"  # csv, json, xlsx
    filters: Optional[AuditLogFilter] = None
    include_metadata: bool = False
    max_records: int = Field(default=10000, le=100000)


# Security Alert Schemas

class SecurityAlertBase(BaseModel):
    """Base security alert schema"""
    alert_type: str
    severity: AlertSeverity
    title: str
    description: Optional[str] = None


class SecurityAlertCreate(SecurityAlertBase):
    """Schema for creating a security alert"""
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    related_audit_ids: list[str] = Field(default_factory=list)
    workspace_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SecurityAlertResponse(SecurityAlertBase):
    """Schema for security alert response"""
    id: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    related_audit_ids: list[str] = Field(default_factory=list)
    workspace_id: Optional[str] = None
    status: AlertStatus
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class SecurityAlertUpdate(BaseModel):
    """Schema for updating a security alert"""
    status: Optional[AlertStatus] = None
    resolution_notes: Optional[str] = None


class SecurityAlertFilter(BaseModel):
    """Schema for filtering security alerts"""
    alert_type: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Activity Timeline

class ActivityTimelineEntry(BaseModel):
    """A single entry in the activity timeline"""
    timestamp: datetime
    action: str
    description: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    resource_type: Optional[str] = None
    resource_name: Optional[str] = None
    success: bool = True
    icon: Optional[str] = None
    color: Optional[str] = None


class UserActivitySummary(BaseModel):
    """Summary of user activity"""
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    total_actions: int
    last_active: Optional[datetime] = None
    most_used_features: list[dict[str, Any]]
    login_count: int
    failed_login_count: int


# Admin Dashboard

class AuditDashboardStats(BaseModel):
    """Statistics for audit dashboard"""
    total_events_today: int
    total_events_week: int
    active_users_today: int
    failed_logins_today: int
    open_alerts: int
    critical_alerts: int
    top_users: list[dict[str, Any]]
    recent_alerts: list[SecurityAlertResponse]


# Constants

ACTION_ICONS = {
    "auth.login": "log-in",
    "auth.logout": "log-out",
    "auth.login_failed": "x-circle",
    "dashboard.view": "eye",
    "dashboard.create": "plus",
    "dashboard.update": "edit",
    "dashboard.delete": "trash",
    "dashboard.share": "share",
    "chart.view": "eye",
    "chart.create": "plus",
    "chart.update": "edit",
    "chart.delete": "trash",
    "chart.export": "download",
    "connection.create": "database",
    "connection.test": "refresh",
    "query.execute": "play",
    "data.export": "download",
    "workspace.create": "folder-plus",
    "workspace.member_add": "user-plus",
    "workspace.member_remove": "user-minus",
}

ACTION_COLORS = {
    "auth.login": "green",
    "auth.logout": "gray",
    "auth.login_failed": "red",
    "dashboard.create": "blue",
    "dashboard.update": "yellow",
    "dashboard.delete": "red",
    "chart.create": "blue",
    "chart.delete": "red",
    "chart.export": "purple",
    "data.export": "purple",
}

SENSITIVE_FIELDS = [
    "password",
    "secret",
    "token",
    "api_key",
    "credentials",
    "private_key",
    "access_token",
    "refresh_token",
]


def sanitize_request_body(body: dict) -> dict:
    """Remove sensitive fields from request body"""
    if not body:
        return {}

    sanitized = {}
    for key, value in body.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_request_body(value)
        else:
            sanitized[key] = value

    return sanitized


def format_action_description(action: str, resource_type: str = None, resource_name: str = None) -> str:
    """Generate human-readable description for an action"""
    action_parts = action.split(".")
    if len(action_parts) != 2:
        return action

    category, action_type = action_parts

    descriptions = {
        ("auth", "login"): "logged in",
        ("auth", "logout"): "logged out",
        ("auth", "login_failed"): "failed to log in",
        ("dashboard", "view"): f"viewed dashboard{f' {resource_name}' if resource_name else ''}",
        ("dashboard", "create"): f"created dashboard{f' {resource_name}' if resource_name else ''}",
        ("dashboard", "update"): f"updated dashboard{f' {resource_name}' if resource_name else ''}",
        ("dashboard", "delete"): f"deleted dashboard{f' {resource_name}' if resource_name else ''}",
        ("dashboard", "share"): f"shared dashboard{f' {resource_name}' if resource_name else ''}",
        ("chart", "view"): f"viewed chart{f' {resource_name}' if resource_name else ''}",
        ("chart", "create"): f"created chart{f' {resource_name}' if resource_name else ''}",
        ("chart", "update"): f"updated chart{f' {resource_name}' if resource_name else ''}",
        ("chart", "delete"): f"deleted chart{f' {resource_name}' if resource_name else ''}",
        ("chart", "export"): f"exported chart{f' {resource_name}' if resource_name else ''}",
        ("connection", "create"): f"created connection{f' {resource_name}' if resource_name else ''}",
        ("connection", "test"): f"tested connection{f' {resource_name}' if resource_name else ''}",
        ("query", "execute"): "executed a query",
        ("data", "export"): "exported data",
        ("workspace", "create"): f"created workspace{f' {resource_name}' if resource_name else ''}",
        ("workspace", "member_add"): "added a member to workspace",
        ("workspace", "member_remove"): "removed a member from workspace",
    }

    return descriptions.get((category, action_type), action)
