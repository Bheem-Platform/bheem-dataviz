"""
Subscriptions and Data Alerts Schemas

Pydantic schemas for dashboard subscriptions and data-driven alerts.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime, time


# Enums

class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SMS = "sms"
    TEAMS = "teams"


class SubscriptionFrequency(str, Enum):
    """Subscription delivery frequency"""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class AlertCondition(str, Enum):
    """Alert trigger conditions"""
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_OR_EQUAL = "gte"
    LESS_OR_EQUAL = "lte"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"
    INCREASES_BY = "increases_by"
    DECREASES_BY = "decreases_by"
    CHANGES_BY = "changes_by"
    PERCENT_CHANGE = "percent_change"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "active"
    PAUSED = "paused"
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


# Notification Channel Configuration

class EmailConfig(BaseModel):
    """Email notification configuration"""
    recipients: list[str]
    subject_template: str = "Alert: {alert_name}"
    include_chart_image: bool = True
    include_data_table: bool = False


class SlackConfig(BaseModel):
    """Slack notification configuration"""
    webhook_url: str
    channel: Optional[str] = None
    username: str = "Bheem DataViz"
    icon_emoji: str = ":chart_with_upwards_trend:"
    include_chart_image: bool = True


class WebhookConfig(BaseModel):
    """Webhook notification configuration"""
    url: str
    method: str = "POST"
    headers: dict[str, str] = Field(default_factory=dict)
    include_full_data: bool = False
    secret: Optional[str] = None  # For HMAC signing


class TeamsConfig(BaseModel):
    """Microsoft Teams notification configuration"""
    webhook_url: str
    include_chart_image: bool = True


class NotificationConfig(BaseModel):
    """Unified notification configuration"""
    channel: NotificationChannel
    email: Optional[EmailConfig] = None
    slack: Optional[SlackConfig] = None
    webhook: Optional[WebhookConfig] = None
    teams: Optional[TeamsConfig] = None


# Alert Schemas

class AlertThreshold(BaseModel):
    """Alert threshold configuration"""
    condition: AlertCondition
    value: float
    secondary_value: Optional[float] = None  # For between conditions
    severity: AlertSeverity = AlertSeverity.WARNING


class DataAlertBase(BaseModel):
    """Base data alert schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: bool = True


class DataAlertCreate(DataAlertBase):
    """Schema for creating a data alert"""
    # Target
    target_type: str  # chart, kpi, query, dataset
    target_id: str
    metric_column: Optional[str] = None  # Specific column to monitor

    # Thresholds
    thresholds: list[AlertThreshold]

    # Evaluation
    evaluation_frequency: str = "hourly"  # cron expression or preset
    cooldown_minutes: int = 60  # Min time between alerts

    # Notifications
    notifications: list[NotificationConfig]

    # Additional options
    workspace_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DataAlertUpdate(BaseModel):
    """Schema for updating a data alert"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    thresholds: Optional[list[AlertThreshold]] = None
    evaluation_frequency: Optional[str] = None
    cooldown_minutes: Optional[int] = None
    notifications: Optional[list[NotificationConfig]] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class DataAlertResponse(DataAlertBase):
    """Schema for data alert response"""
    id: str
    target_type: str
    target_id: str
    metric_column: Optional[str] = None
    thresholds: list[AlertThreshold]
    evaluation_frequency: str
    cooldown_minutes: int
    notifications: list[NotificationConfig]
    workspace_id: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_evaluated_at: Optional[datetime] = None
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    status: AlertStatus
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


# Alert Trigger

class AlertTriggerEvent(BaseModel):
    """Alert trigger event"""
    alert_id: str
    alert_name: str
    triggered_at: datetime
    threshold: AlertThreshold
    current_value: float
    previous_value: Optional[float] = None
    target_type: str
    target_id: str
    target_name: Optional[str] = None
    severity: AlertSeverity
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlertHistory(BaseModel):
    """Alert history entry"""
    id: str
    alert_id: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    threshold_triggered: AlertThreshold
    value_at_trigger: float
    severity: AlertSeverity
    notification_sent: bool
    notification_channels: list[str]
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


# Subscription Schemas

class SubscriptionSchedule(BaseModel):
    """Subscription delivery schedule"""
    frequency: SubscriptionFrequency
    time_of_day: Optional[time] = None  # For daily/weekly/monthly
    day_of_week: Optional[int] = None  # 0-6 for weekly
    day_of_month: Optional[int] = None  # 1-31 for monthly
    timezone: str = "UTC"
    cron_expression: Optional[str] = None  # For custom


class SubscriptionContent(BaseModel):
    """Subscription content configuration"""
    include_dashboard_snapshot: bool = True
    include_charts: list[str] = Field(default_factory=list)  # Chart IDs, empty = all
    include_data_tables: bool = False
    include_insights: bool = False
    include_kpis: bool = True
    format: str = "pdf"  # pdf, html, excel


class SubscriptionBase(BaseModel):
    """Base subscription schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: bool = True


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a subscription"""
    # Target
    dashboard_id: str

    # Schedule
    schedule: SubscriptionSchedule

    # Content
    content: SubscriptionContent

    # Recipients
    recipients: list[str]  # Email addresses or user IDs
    notification_channel: NotificationChannel = NotificationChannel.EMAIL

    # Filters
    filter_state: Optional[dict[str, Any]] = None  # Dashboard filters to apply

    # Options
    workspace_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    schedule: Optional[SubscriptionSchedule] = None
    content: Optional[SubscriptionContent] = None
    recipients: Optional[list[str]] = None
    notification_channel: Optional[NotificationChannel] = None
    filter_state: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None


class SubscriptionResponse(SubscriptionBase):
    """Schema for subscription response"""
    id: str
    dashboard_id: str
    dashboard_name: Optional[str] = None
    schedule: SubscriptionSchedule
    content: SubscriptionContent
    recipients: list[str]
    notification_channel: NotificationChannel
    filter_state: Optional[dict[str, Any]] = None
    workspace_id: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_sent_at: Optional[datetime] = None
    next_send_at: Optional[datetime] = None
    send_count: int = 0
    status: SubscriptionStatus
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class SubscriptionDelivery(BaseModel):
    """Subscription delivery record"""
    id: str
    subscription_id: str
    sent_at: datetime
    recipients: list[str]
    success: bool
    error_message: Optional[str] = None
    file_urls: list[str] = Field(default_factory=list)


# Digest Schemas

class DigestConfig(BaseModel):
    """Digest email configuration"""
    include_alerts: bool = True
    include_insights: bool = True
    include_top_dashboards: bool = True
    include_usage_stats: bool = False
    max_alerts: int = 10
    max_insights: int = 5


class DigestSubscription(BaseModel):
    """User digest subscription"""
    user_id: str
    enabled: bool = True
    frequency: SubscriptionFrequency = SubscriptionFrequency.DAILY
    time_of_day: time = time(8, 0)
    timezone: str = "UTC"
    config: DigestConfig = Field(default_factory=DigestConfig)


# Summary Schemas

class AlertSummary(BaseModel):
    """Summary of alerts"""
    total_alerts: int
    active_alerts: int
    triggered_today: int
    critical_alerts: int
    alerts_by_severity: dict[str, int]
    recent_triggers: list[AlertTriggerEvent]


class SubscriptionSummary(BaseModel):
    """Summary of subscriptions"""
    total_subscriptions: int
    active_subscriptions: int
    sent_today: int
    sent_this_week: int
    subscriptions_by_frequency: dict[str, int]
    recent_deliveries: list[SubscriptionDelivery]


# Helper Functions

def build_alert_message(
    alert_name: str,
    threshold: AlertThreshold,
    current_value: float,
    target_name: Optional[str] = None,
) -> str:
    """Build human-readable alert message"""
    condition_text = {
        AlertCondition.GREATER_THAN: "exceeded",
        AlertCondition.LESS_THAN: "dropped below",
        AlertCondition.EQUALS: "equals",
        AlertCondition.NOT_EQUALS: "changed from",
        AlertCondition.GREATER_OR_EQUAL: "reached or exceeded",
        AlertCondition.LESS_OR_EQUAL: "reached or dropped below",
        AlertCondition.BETWEEN: "is between",
        AlertCondition.NOT_BETWEEN: "is outside range",
        AlertCondition.INCREASES_BY: "increased by",
        AlertCondition.DECREASES_BY: "decreased by",
        AlertCondition.CHANGES_BY: "changed by",
        AlertCondition.PERCENT_CHANGE: "changed by percentage",
    }

    condition = condition_text.get(threshold.condition, str(threshold.condition))
    target = f" for {target_name}" if target_name else ""

    if threshold.condition == AlertCondition.BETWEEN:
        return f"{alert_name}: Value ({current_value}) is between {threshold.value} and {threshold.secondary_value}{target}"
    elif threshold.condition == AlertCondition.NOT_BETWEEN:
        return f"{alert_name}: Value ({current_value}) is outside {threshold.value} to {threshold.secondary_value}{target}"
    else:
        return f"{alert_name}: Value ({current_value}) {condition} threshold ({threshold.value}){target}"


def evaluate_threshold(
    threshold: AlertThreshold,
    current_value: float,
    previous_value: Optional[float] = None,
) -> bool:
    """Evaluate if threshold condition is met"""
    if threshold.condition == AlertCondition.GREATER_THAN:
        return current_value > threshold.value
    elif threshold.condition == AlertCondition.LESS_THAN:
        return current_value < threshold.value
    elif threshold.condition == AlertCondition.EQUALS:
        return current_value == threshold.value
    elif threshold.condition == AlertCondition.NOT_EQUALS:
        return current_value != threshold.value
    elif threshold.condition == AlertCondition.GREATER_OR_EQUAL:
        return current_value >= threshold.value
    elif threshold.condition == AlertCondition.LESS_OR_EQUAL:
        return current_value <= threshold.value
    elif threshold.condition == AlertCondition.BETWEEN:
        if threshold.secondary_value is None:
            return False
        return threshold.value <= current_value <= threshold.secondary_value
    elif threshold.condition == AlertCondition.NOT_BETWEEN:
        if threshold.secondary_value is None:
            return False
        return current_value < threshold.value or current_value > threshold.secondary_value
    elif threshold.condition == AlertCondition.INCREASES_BY:
        if previous_value is None:
            return False
        return current_value - previous_value >= threshold.value
    elif threshold.condition == AlertCondition.DECREASES_BY:
        if previous_value is None:
            return False
        return previous_value - current_value >= threshold.value
    elif threshold.condition == AlertCondition.CHANGES_BY:
        if previous_value is None:
            return False
        return abs(current_value - previous_value) >= threshold.value
    elif threshold.condition == AlertCondition.PERCENT_CHANGE:
        if previous_value is None or previous_value == 0:
            return False
        percent_change = abs((current_value - previous_value) / previous_value * 100)
        return percent_change >= threshold.value

    return False


# Constants

CONDITION_LABELS = {
    AlertCondition.GREATER_THAN: "Greater than",
    AlertCondition.LESS_THAN: "Less than",
    AlertCondition.EQUALS: "Equals",
    AlertCondition.NOT_EQUALS: "Not equals",
    AlertCondition.GREATER_OR_EQUAL: "Greater or equal",
    AlertCondition.LESS_OR_EQUAL: "Less or equal",
    AlertCondition.BETWEEN: "Between",
    AlertCondition.NOT_BETWEEN: "Not between",
    AlertCondition.INCREASES_BY: "Increases by",
    AlertCondition.DECREASES_BY: "Decreases by",
    AlertCondition.CHANGES_BY: "Changes by",
    AlertCondition.PERCENT_CHANGE: "Percent change",
}

SEVERITY_COLORS = {
    AlertSeverity.INFO: "#3b82f6",
    AlertSeverity.WARNING: "#f59e0b",
    AlertSeverity.CRITICAL: "#ef4444",
}

FREQUENCY_LABELS = {
    SubscriptionFrequency.IMMEDIATE: "Immediately",
    SubscriptionFrequency.HOURLY: "Every hour",
    SubscriptionFrequency.DAILY: "Daily",
    SubscriptionFrequency.WEEKLY: "Weekly",
    SubscriptionFrequency.MONTHLY: "Monthly",
    SubscriptionFrequency.CUSTOM: "Custom schedule",
}
