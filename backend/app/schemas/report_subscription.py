"""
Report Subscriptions Schemas

Pydantic schemas for report subscription management including
subscriptions, notification preferences, and digest configurations.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
from datetime import datetime


# Enums

class SubscriptionType(str, Enum):
    INSTANT = "instant"  # Notify immediately on changes
    DAILY_DIGEST = "daily_digest"
    WEEKLY_DIGEST = "weekly_digest"
    MONTHLY_DIGEST = "monthly_digest"
    SCHEDULED = "scheduled"  # At specific times
    ON_REFRESH = "on_refresh"  # When data refreshes
    ON_THRESHOLD = "on_threshold"  # When metrics cross thresholds


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ResourceType(str, Enum):
    DASHBOARD = "dashboard"
    CHART = "chart"
    REPORT = "report"
    KPI = "kpi"
    QUERY = "query"
    ALERT = "alert"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    PUSH = "push"
    IN_APP = "in_app"
    SMS = "sms"
    WEBHOOK = "webhook"


class DigestFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class ThresholdOperator(str, Enum):
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    EQUAL = "eq"
    NOT_EQUAL = "neq"
    CHANGE_BY = "change_by"
    CHANGE_BY_PERCENT = "change_by_percent"


# Notification Configuration Schemas

class EmailNotificationConfig(BaseModel):
    email_address: Optional[str] = None  # If different from user's email
    include_preview: bool = True
    include_attachment: bool = False
    attachment_format: str = "pdf"
    subject_prefix: str = "[DataViz]"


class SlackNotificationConfig(BaseModel):
    channel_id: Optional[str] = None
    dm_user: bool = True
    include_preview_image: bool = True
    mention_on_threshold: bool = False


class TeamsNotificationConfig(BaseModel):
    channel_webhook: Optional[str] = None
    include_preview_image: bool = True


class PushNotificationConfig(BaseModel):
    send_to_mobile: bool = True
    send_to_desktop: bool = True
    sound_enabled: bool = True


class WebhookNotificationConfig(BaseModel):
    url: str
    method: str = "POST"
    headers: dict[str, str] = {}
    include_data: bool = True


class NotificationConfig(BaseModel):
    channel: NotificationChannel
    email_config: Optional[EmailNotificationConfig] = None
    slack_config: Optional[SlackNotificationConfig] = None
    teams_config: Optional[TeamsNotificationConfig] = None
    push_config: Optional[PushNotificationConfig] = None
    webhook_config: Optional[WebhookNotificationConfig] = None
    enabled: bool = True


# Threshold Configuration

class ThresholdCondition(BaseModel):
    metric_name: str
    operator: ThresholdOperator
    value: float
    secondary_value: Optional[float] = None  # For range conditions
    comparison_period: Optional[str] = None  # "previous_day", "previous_week", etc.


# Schedule Configuration

class SubscriptionSchedule(BaseModel):
    days_of_week: list[str] = []  # ["monday", "wednesday", "friday"]
    time_of_day: str = "09:00"  # HH:MM format
    timezone: str = "UTC"


# Digest Configuration

class DigestConfig(BaseModel):
    frequency: DigestFrequency
    day_of_week: Optional[str] = None  # For weekly digests
    day_of_month: Optional[int] = None  # For monthly digests
    time_of_day: str = "09:00"
    timezone: str = "UTC"
    include_summary: bool = True
    include_highlights: bool = True
    max_items: int = 10
    group_by_resource: bool = True


# Subscription Schemas

class SubscriptionBase(BaseModel):
    resource_type: ResourceType
    resource_id: str
    resource_name: Optional[str] = None
    subscription_type: SubscriptionType
    notification_channels: list[NotificationConfig]


class SubscriptionCreate(SubscriptionBase):
    schedule: Optional[SubscriptionSchedule] = None
    digest_config: Optional[DigestConfig] = None
    threshold_conditions: list[ThresholdCondition] = []
    filters: dict[str, Any] = {}
    is_active: bool = True
    expires_at: Optional[datetime] = None


class SubscriptionUpdate(BaseModel):
    resource_name: Optional[str] = None
    subscription_type: Optional[SubscriptionType] = None
    notification_channels: Optional[list[NotificationConfig]] = None
    schedule: Optional[SubscriptionSchedule] = None
    digest_config: Optional[DigestConfig] = None
    threshold_conditions: Optional[list[ThresholdCondition]] = None
    filters: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None
    status: Optional[SubscriptionStatus] = None
    expires_at: Optional[datetime] = None


class Subscription(SubscriptionBase):
    id: str
    user_id: str
    organization_id: Optional[str] = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    is_active: bool = True
    schedule: Optional[SubscriptionSchedule] = None
    digest_config: Optional[DigestConfig] = None
    threshold_conditions: list[ThresholdCondition] = []
    filters: dict[str, Any] = {}
    last_notified_at: Optional[datetime] = None
    notification_count: int = 0
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    subscriptions: list[Subscription]
    total: int


# Notification History Schemas

class NotificationDelivery(BaseModel):
    channel: NotificationChannel
    success: bool
    delivered_at: Optional[datetime] = None
    error: Optional[str] = None


class SubscriptionNotification(BaseModel):
    id: str
    subscription_id: str
    user_id: str
    resource_type: ResourceType
    resource_id: str
    resource_name: Optional[str] = None
    notification_type: str  # "instant", "digest", "threshold", etc.
    title: str
    message: str
    data: dict[str, Any] = {}
    deliveries: list[NotificationDelivery] = []
    read: bool = False
    read_at: Optional[datetime] = None
    clicked: bool = False
    clicked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: list[SubscriptionNotification]
    total: int
    unread_count: int


# Digest Schemas

class DigestItem(BaseModel):
    resource_type: ResourceType
    resource_id: str
    resource_name: str
    summary: str
    changes: list[str] = []
    metrics: dict[str, Any] = {}
    timestamp: datetime


class Digest(BaseModel):
    id: str
    user_id: str
    digest_type: DigestFrequency
    period_start: datetime
    period_end: datetime
    items: list[DigestItem]
    total_items: int
    highlights: list[str] = []
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DigestListResponse(BaseModel):
    digests: list[Digest]
    total: int


# User Preferences Schemas

class GlobalNotificationPreferences(BaseModel):
    email_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    slack_enabled: bool = False
    teams_enabled: bool = False
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    timezone: str = "UTC"
    digest_enabled: bool = True
    digest_frequency: DigestFrequency = DigestFrequency.DAILY
    digest_time: str = "09:00"
    unsubscribe_from_marketing: bool = False


class UserSubscriptionPreferences(BaseModel):
    user_id: str
    global_preferences: GlobalNotificationPreferences
    channel_preferences: dict[str, bool] = {}  # Per-channel overrides
    resource_preferences: dict[str, bool] = {}  # Per-resource-type overrides
    muted_resources: list[str] = []  # Resource IDs to never notify about
    updated_at: datetime

    class Config:
        from_attributes = True


# Statistics Schemas

class SubscriptionStats(BaseModel):
    organization_id: str
    total_subscriptions: int
    active_subscriptions: int
    subscriptions_by_type: dict[str, int]
    subscriptions_by_resource: dict[str, int]
    subscriptions_by_channel: dict[str, int]
    notifications_sent_today: int
    notifications_sent_this_week: int
    notifications_sent_this_month: int
    open_rate: float
    click_rate: float
    unsubscribe_rate: float


# Constants

SUBSCRIPTION_TYPE_LABELS: dict[SubscriptionType, str] = {
    SubscriptionType.INSTANT: "Instant Notifications",
    SubscriptionType.DAILY_DIGEST: "Daily Digest",
    SubscriptionType.WEEKLY_DIGEST: "Weekly Digest",
    SubscriptionType.MONTHLY_DIGEST: "Monthly Digest",
    SubscriptionType.SCHEDULED: "Scheduled",
    SubscriptionType.ON_REFRESH: "On Data Refresh",
    SubscriptionType.ON_THRESHOLD: "On Threshold",
}

SUBSCRIPTION_STATUS_LABELS: dict[SubscriptionStatus, str] = {
    SubscriptionStatus.ACTIVE: "Active",
    SubscriptionStatus.PAUSED: "Paused",
    SubscriptionStatus.EXPIRED: "Expired",
    SubscriptionStatus.CANCELLED: "Cancelled",
}

RESOURCE_TYPE_LABELS: dict[ResourceType, str] = {
    ResourceType.DASHBOARD: "Dashboard",
    ResourceType.CHART: "Chart",
    ResourceType.REPORT: "Report",
    ResourceType.KPI: "KPI",
    ResourceType.QUERY: "Query",
    ResourceType.ALERT: "Alert",
}

NOTIFICATION_CHANNEL_LABELS: dict[NotificationChannel, str] = {
    NotificationChannel.EMAIL: "Email",
    NotificationChannel.SLACK: "Slack",
    NotificationChannel.TEAMS: "Microsoft Teams",
    NotificationChannel.PUSH: "Push Notification",
    NotificationChannel.IN_APP: "In-App",
    NotificationChannel.SMS: "SMS",
    NotificationChannel.WEBHOOK: "Webhook",
}

THRESHOLD_OPERATOR_LABELS: dict[ThresholdOperator, str] = {
    ThresholdOperator.GREATER_THAN: "Greater than",
    ThresholdOperator.GREATER_THAN_OR_EQUAL: "Greater than or equal to",
    ThresholdOperator.LESS_THAN: "Less than",
    ThresholdOperator.LESS_THAN_OR_EQUAL: "Less than or equal to",
    ThresholdOperator.EQUAL: "Equal to",
    ThresholdOperator.NOT_EQUAL: "Not equal to",
    ThresholdOperator.CHANGE_BY: "Changes by",
    ThresholdOperator.CHANGE_BY_PERCENT: "Changes by %",
}


# Helper Functions

def evaluate_threshold(
    current_value: float,
    condition: ThresholdCondition,
    previous_value: Optional[float] = None,
) -> bool:
    """Evaluate if a threshold condition is met."""
    op = condition.operator
    threshold = condition.value

    if op == ThresholdOperator.GREATER_THAN:
        return current_value > threshold
    elif op == ThresholdOperator.GREATER_THAN_OR_EQUAL:
        return current_value >= threshold
    elif op == ThresholdOperator.LESS_THAN:
        return current_value < threshold
    elif op == ThresholdOperator.LESS_THAN_OR_EQUAL:
        return current_value <= threshold
    elif op == ThresholdOperator.EQUAL:
        return current_value == threshold
    elif op == ThresholdOperator.NOT_EQUAL:
        return current_value != threshold
    elif op == ThresholdOperator.CHANGE_BY:
        if previous_value is None:
            return False
        return abs(current_value - previous_value) >= threshold
    elif op == ThresholdOperator.CHANGE_BY_PERCENT:
        if previous_value is None or previous_value == 0:
            return False
        change_percent = abs((current_value - previous_value) / previous_value) * 100
        return change_percent >= threshold

    return False


def format_threshold_description(condition: ThresholdCondition) -> str:
    """Format threshold condition as human-readable string."""
    op_label = THRESHOLD_OPERATOR_LABELS.get(condition.operator, str(condition.operator))

    if condition.operator in [ThresholdOperator.CHANGE_BY, ThresholdOperator.CHANGE_BY_PERCENT]:
        unit = "%" if condition.operator == ThresholdOperator.CHANGE_BY_PERCENT else ""
        return f"{condition.metric_name} {op_label.lower()} {condition.value}{unit}"

    return f"{condition.metric_name} is {op_label.lower()} {condition.value}"


def should_send_digest(
    preferences: GlobalNotificationPreferences,
    last_digest_time: Optional[datetime] = None,
) -> bool:
    """Check if it's time to send a digest based on preferences."""
    if not preferences.digest_enabled:
        return False

    if last_digest_time is None:
        return True

    from datetime import timedelta

    now = datetime.utcnow()
    freq = preferences.digest_frequency

    if freq == DigestFrequency.DAILY:
        return (now - last_digest_time) >= timedelta(days=1)
    elif freq == DigestFrequency.WEEKLY:
        return (now - last_digest_time) >= timedelta(weeks=1)
    elif freq == DigestFrequency.BIWEEKLY:
        return (now - last_digest_time) >= timedelta(weeks=2)
    elif freq == DigestFrequency.MONTHLY:
        return (now - last_digest_time) >= timedelta(days=30)

    return False


def is_in_quiet_hours(preferences: GlobalNotificationPreferences) -> bool:
    """Check if current time is within quiet hours."""
    if not preferences.quiet_hours_enabled:
        return False

    from datetime import datetime as dt

    now = dt.utcnow()
    # In production, convert to user's timezone
    current_time = now.strftime("%H:%M")

    start = preferences.quiet_hours_start
    end = preferences.quiet_hours_end

    # Handle overnight quiet hours (e.g., 22:00 to 08:00)
    if start > end:
        return current_time >= start or current_time < end
    else:
        return start <= current_time < end
