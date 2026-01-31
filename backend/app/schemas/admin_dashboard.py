"""
Administration Dashboard Schemas

Pydantic schemas for the administration dashboard, system overview,
health monitoring, and administrative controls.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class SystemHealthStatus(str, Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


class AlertLevel(str, Enum):
    """Alert severity level"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    """Trend direction"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class TimeRange(str, Enum):
    """Time range for statistics"""
    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    THIS_MONTH = "this_month"
    THIS_YEAR = "this_year"


# Metric Models

class MetricValue(BaseModel):
    """A metric with current value and trend"""
    name: str
    value: float
    previous_value: Optional[float] = None
    unit: Optional[str] = None
    trend: TrendDirection = TrendDirection.STABLE
    change_percent: float = 0


class MetricTimeSeries(BaseModel):
    """Time series data for a metric"""
    name: str
    data_points: list[dict[str, Any]]  # [{timestamp, value}, ...]
    aggregation: str = "sum"  # sum, avg, max, min


# System Health Models

class ServiceHealth(BaseModel):
    """Health status of a service"""
    name: str
    status: SystemHealthStatus
    latency_ms: Optional[float] = None
    last_check_at: datetime
    error_message: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)


class SystemHealth(BaseModel):
    """Overall system health"""
    status: SystemHealthStatus
    services: list[ServiceHealth]
    uptime_percent: float = 100.0
    last_incident_at: Optional[datetime] = None
    active_incidents: int = 0


class ResourceUsage(BaseModel):
    """Resource usage metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_in_mbps: float = 0
    network_out_mbps: float = 0
    active_connections: int = 0


# User Statistics Models

class UserStats(BaseModel):
    """User statistics"""
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    mfa_enabled_percent: float
    users_by_status: dict[str, int]
    users_by_type: dict[str, int]
    users_by_auth_provider: dict[str, int]
    user_growth: list[dict[str, Any]]  # [{date, count}, ...]


class SessionStats(BaseModel):
    """Session statistics"""
    active_sessions: int
    sessions_today: int
    avg_session_duration_minutes: float
    sessions_by_device: dict[str, int]
    sessions_by_location: dict[str, int]
    peak_concurrent_today: int


# Workspace Statistics Models

class WorkspaceStats(BaseModel):
    """Workspace statistics"""
    total_workspaces: int
    active_workspaces: int
    new_workspaces_this_month: int
    workspaces_by_plan: dict[str, int]
    workspaces_by_status: dict[str, int]
    avg_members_per_workspace: float
    workspace_growth: list[dict[str, Any]]


# Revenue Statistics Models

class RevenueStats(BaseModel):
    """Revenue statistics"""
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    revenue_this_month: float
    revenue_this_year: float
    avg_revenue_per_user: float
    churn_rate: float
    revenue_by_plan: dict[str, float]
    revenue_growth: list[dict[str, Any]]
    currency: str = "USD"


class SubscriptionStats(BaseModel):
    """Subscription statistics"""
    total_subscriptions: int
    active_subscriptions: int
    trial_subscriptions: int
    canceled_this_month: int
    subscriptions_by_plan: dict[str, int]
    subscriptions_by_interval: dict[str, int]
    conversion_rate: float  # Trial to paid


# Usage Statistics Models

class PlatformUsageStats(BaseModel):
    """Platform usage statistics"""
    total_dashboards: int
    total_charts: int
    total_connections: int
    total_queries_today: int
    total_api_calls_today: int
    storage_used_gb: float
    storage_total_gb: float
    query_minutes_today: float
    most_active_workspaces: list[dict[str, Any]]
    popular_features: list[dict[str, Any]]


# Alert Models

class SystemAlert(BaseModel):
    """System alert"""
    id: str
    level: AlertLevel
    title: str
    message: str
    source: str
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class AlertSummary(BaseModel):
    """Alert summary"""
    total_alerts: int
    unacknowledged: int
    by_level: dict[str, int]
    recent_alerts: list[SystemAlert]


# Activity Models

class AdminActivity(BaseModel):
    """Admin activity log"""
    id: str
    admin_id: str
    admin_name: str
    action: str
    target_type: str
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RecentActivity(BaseModel):
    """Recent activities summary"""
    user_activities: list[dict[str, Any]]
    admin_activities: list[AdminActivity]
    system_events: list[dict[str, Any]]


# Configuration Models

class SystemConfig(BaseModel):
    """System configuration"""
    maintenance_mode: bool = False
    maintenance_message: Optional[str] = None
    registration_enabled: bool = True
    public_signup_enabled: bool = True
    default_plan_id: str = "plan_free"
    max_workspaces_per_user: int = 5
    trial_days: int = 14
    session_timeout_hours: int = 24
    password_policy: dict[str, Any] = Field(default_factory=dict)
    email_verification_required: bool = True
    mfa_required_for_admins: bool = True
    allowed_email_domains: list[str] = Field(default_factory=list)
    blocked_email_domains: list[str] = Field(default_factory=list)
    rate_limits: dict[str, int] = Field(default_factory=dict)
    feature_flags: dict[str, bool] = Field(default_factory=dict)


class SystemConfigUpdate(BaseModel):
    """Update system configuration"""
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    registration_enabled: Optional[bool] = None
    public_signup_enabled: Optional[bool] = None
    default_plan_id: Optional[str] = None
    max_workspaces_per_user: Optional[int] = None
    trial_days: Optional[int] = None
    session_timeout_hours: Optional[int] = None
    password_policy: Optional[dict[str, Any]] = None
    email_verification_required: Optional[bool] = None
    mfa_required_for_admins: Optional[bool] = None
    allowed_email_domains: Optional[list[str]] = None
    blocked_email_domains: Optional[list[str]] = None
    rate_limits: Optional[dict[str, int]] = None
    feature_flags: Optional[dict[str, bool]] = None


# Dashboard Models

class AdminDashboardSummary(BaseModel):
    """Main admin dashboard summary"""
    system_health: SystemHealth
    resource_usage: ResourceUsage
    key_metrics: list[MetricValue]
    user_stats: UserStats
    workspace_stats: WorkspaceStats
    revenue_stats: Optional[RevenueStats] = None
    subscription_stats: SubscriptionStats
    usage_stats: PlatformUsageStats
    alert_summary: AlertSummary
    recent_activity: RecentActivity


class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""
    id: str
    type: str
    title: str
    size: str  # small, medium, large
    position: int
    config: dict[str, Any] = Field(default_factory=dict)
    refresh_interval_seconds: int = 60


class AdminDashboardConfig(BaseModel):
    """Admin dashboard configuration"""
    widgets: list[DashboardWidget]
    refresh_interval_seconds: int = 30
    theme: str = "light"


# Report Models

class AdminReport(BaseModel):
    """Generated admin report"""
    id: str
    name: str
    type: str  # usage, revenue, growth, audit
    format: str  # pdf, csv, excel
    time_range: TimeRange
    generated_at: datetime
    generated_by: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    parameters: dict[str, Any] = Field(default_factory=dict)


class ReportSchedule(BaseModel):
    """Scheduled report"""
    id: str
    report_type: str
    name: str
    schedule: str  # cron expression
    recipients: list[str]
    format: str
    time_range: TimeRange
    enabled: bool = True
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Response Models

class SystemAlertListResponse(BaseModel):
    """List alerts response"""
    alerts: list[SystemAlert]
    total: int


class AdminActivityListResponse(BaseModel):
    """List admin activities response"""
    activities: list[AdminActivity]
    total: int


class AdminReportListResponse(BaseModel):
    """List reports response"""
    reports: list[AdminReport]
    total: int


# Quick Actions

class QuickAction(BaseModel):
    """Admin quick action"""
    id: str
    name: str
    description: str
    icon: str
    action_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = False
    permission_required: str


class QuickActionResult(BaseModel):
    """Result of quick action"""
    success: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


# Constants

DEFAULT_DASHBOARD_WIDGETS = [
    DashboardWidget(
        id="system_health",
        type="health_status",
        title="System Health",
        size="small",
        position=1,
    ),
    DashboardWidget(
        id="active_users",
        type="metric",
        title="Active Users",
        size="small",
        position=2,
        config={"metric": "active_users"},
    ),
    DashboardWidget(
        id="revenue",
        type="metric",
        title="Monthly Revenue",
        size="small",
        position=3,
        config={"metric": "mrr"},
    ),
    DashboardWidget(
        id="user_growth",
        type="chart",
        title="User Growth",
        size="medium",
        position=4,
        config={"chart_type": "line"},
    ),
    DashboardWidget(
        id="recent_alerts",
        type="alert_list",
        title="Recent Alerts",
        size="medium",
        position=5,
    ),
    DashboardWidget(
        id="recent_activity",
        type="activity_feed",
        title="Recent Activity",
        size="medium",
        position=6,
    ),
]

QUICK_ACTIONS = [
    QuickAction(
        id="clear_cache",
        name="Clear Cache",
        description="Clear all system caches",
        icon="refresh",
        action_type="system",
        requires_confirmation=True,
        permission_required="admin:settings",
    ),
    QuickAction(
        id="enable_maintenance",
        name="Enable Maintenance Mode",
        description="Put the system in maintenance mode",
        icon="tool",
        action_type="config",
        requires_confirmation=True,
        permission_required="admin:settings",
    ),
    QuickAction(
        id="export_users",
        name="Export Users",
        description="Export all users to CSV",
        icon="download",
        action_type="export",
        permission_required="users:read",
    ),
    QuickAction(
        id="send_announcement",
        name="Send Announcement",
        description="Send announcement to all users",
        icon="megaphone",
        action_type="notification",
        requires_confirmation=True,
        permission_required="admin:settings",
    ),
]


# Helper Functions

def calculate_trend(current: float, previous: float) -> tuple[TrendDirection, float]:
    """Calculate trend direction and change percent."""
    if previous == 0:
        if current > 0:
            return TrendDirection.UP, 100.0
        return TrendDirection.STABLE, 0.0

    change = ((current - previous) / previous) * 100

    if change > 5:
        return TrendDirection.UP, round(change, 1)
    elif change < -5:
        return TrendDirection.DOWN, round(change, 1)
    return TrendDirection.STABLE, round(change, 1)


def get_health_status_from_checks(services: list[ServiceHealth]) -> SystemHealthStatus:
    """Determine overall health from service checks."""
    if not services:
        return SystemHealthStatus.UNHEALTHY

    unhealthy_count = sum(1 for s in services if s.status == SystemHealthStatus.UNHEALTHY)
    degraded_count = sum(1 for s in services if s.status == SystemHealthStatus.DEGRADED)

    if unhealthy_count > 0:
        return SystemHealthStatus.UNHEALTHY
    if degraded_count > 0:
        return SystemHealthStatus.DEGRADED
    return SystemHealthStatus.HEALTHY
