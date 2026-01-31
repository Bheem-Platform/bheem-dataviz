"""
Schedule and Alert Schemas

Provides schemas for:
- Data refresh schedules
- Alert rules and conditions
- Notification configuration
- Schedule history and status
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ScheduleFrequency(str, Enum):
    """Frequency of scheduled tasks"""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"  # Cron expression


class ScheduleStatus(str, Enum):
    """Status of a schedule"""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    ERROR = "error"


class RefreshType(str, Enum):
    """Type of data refresh"""
    FULL = "full"           # Full refresh
    INCREMENTAL = "incremental"  # Incremental refresh
    PARTITION = "partition"  # Partition-based refresh


class AlertSeverity(str, Enum):
    """Severity level of alerts"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertOperator(str, Enum):
    """Operators for alert conditions"""
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    BETWEEN = "between"
    OUTSIDE = "outside"
    CHANGE_GREATER_THAN = "change_greater_than"
    CHANGE_LESS_THAN = "change_less_than"
    PERCENT_CHANGE_GREATER_THAN = "percent_change_greater_than"
    PERCENT_CHANGE_LESS_THAN = "percent_change_less_than"


class NotificationChannel(str, Enum):
    """Notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


# Schedule Configuration

class ScheduleTime(BaseModel):
    """Time specification for schedules"""
    hour: int = Field(0, ge=0, le=23, description="Hour (0-23)")
    minute: int = Field(0, ge=0, le=59, description="Minute (0-59)")
    timezone: str = Field("UTC", description="Timezone")


class WeeklySchedule(BaseModel):
    """Weekly schedule configuration"""
    days: list[int] = Field(..., description="Days of week (0=Monday, 6=Sunday)")
    time: ScheduleTime = Field(...)


class MonthlySchedule(BaseModel):
    """Monthly schedule configuration"""
    days: list[int] = Field(..., description="Days of month (1-31)")
    time: ScheduleTime = Field(...)


class ScheduleConfig(BaseModel):
    """Complete schedule configuration"""
    frequency: ScheduleFrequency = Field(..., description="Schedule frequency")
    start_time: Optional[str] = Field(None, description="Start datetime (ISO format)")
    end_time: Optional[str] = Field(None, description="End datetime (optional)")
    time: Optional[ScheduleTime] = Field(None, description="Time for daily schedules")
    weekly: Optional[WeeklySchedule] = Field(None, description="Weekly configuration")
    monthly: Optional[MonthlySchedule] = Field(None, description="Monthly configuration")
    cron_expression: Optional[str] = Field(None, description="Cron expression for custom schedules")
    max_retries: int = Field(3, description="Max retries on failure")
    retry_delay_minutes: int = Field(5, description="Delay between retries")


# Data Refresh Schedule

class RefreshSchedule(BaseModel):
    """Schedule for data refresh"""
    id: str = Field(..., description="Schedule ID")
    name: str = Field(..., description="Schedule name")
    description: Optional[str] = Field(None)
    enabled: bool = Field(True, description="Whether schedule is active")
    status: ScheduleStatus = Field(ScheduleStatus.ACTIVE)

    # Target
    target_type: str = Field(..., description="dashboard, dataset, connection")
    target_id: str = Field(..., description="ID of target object")

    # Refresh configuration
    refresh_type: RefreshType = Field(RefreshType.FULL)
    schedule: ScheduleConfig = Field(...)

    # Incremental refresh options
    incremental_column: Optional[str] = Field(None, description="Column for incremental refresh")
    incremental_lookback_days: Optional[int] = Field(None, description="Days to look back")

    # Notification on completion
    notify_on_success: bool = Field(False)
    notify_on_failure: bool = Field(True)
    notification_recipients: list[str] = Field(default_factory=list)

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    last_run_at: Optional[str] = None
    last_run_status: Optional[str] = None
    next_run_at: Optional[str] = None


# Alert Configuration

class AlertCondition(BaseModel):
    """Condition that triggers an alert"""
    id: str = Field(..., description="Condition ID")
    measure: str = Field(..., description="Measure/column to evaluate")
    operator: AlertOperator = Field(...)
    threshold: float = Field(..., description="Threshold value")
    threshold2: Optional[float] = Field(None, description="Second threshold for between/outside")
    comparison_period: Optional[str] = Field(None, description="Period for change comparisons")


class AlertRule(BaseModel):
    """Alert rule configuration"""
    id: str = Field(..., description="Alert rule ID")
    name: str = Field(..., description="Alert name")
    description: Optional[str] = Field(None)
    enabled: bool = Field(True)
    severity: AlertSeverity = Field(AlertSeverity.WARNING)

    # Target
    target_type: str = Field(..., description="dashboard, chart, kpi")
    target_id: str = Field(..., description="ID of target object")

    # Conditions
    conditions: list[AlertCondition] = Field(..., description="Alert conditions")
    condition_logic: str = Field("AND", description="AND or OR for multiple conditions")

    # Evaluation schedule
    evaluation_schedule: ScheduleConfig = Field(...)

    # Notification
    notification_channels: list[NotificationChannel] = Field(default_factory=list)
    notification_recipients: list[str] = Field(default_factory=list)
    notification_message: Optional[str] = Field(None, description="Custom message template")

    # Snooze/suppression
    snooze_until: Optional[str] = Field(None, description="Suppress alerts until this time")
    min_interval_minutes: int = Field(60, description="Minimum time between alerts")

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    last_triggered_at: Optional[str] = None
    trigger_count: int = Field(0)


# Notification Configuration

class NotificationConfig(BaseModel):
    """Configuration for notification channels"""
    channel: NotificationChannel = Field(...)
    enabled: bool = Field(True)

    # Email config
    email_addresses: Optional[list[str]] = Field(None)

    # Slack config
    slack_webhook_url: Optional[str] = Field(None)
    slack_channel: Optional[str] = Field(None)

    # Teams config
    teams_webhook_url: Optional[str] = Field(None)

    # Webhook config
    webhook_url: Optional[str] = Field(None)
    webhook_headers: Optional[dict[str, str]] = Field(None)


# Execution History

class ScheduleExecution(BaseModel):
    """Record of a schedule execution"""
    id: str = Field(..., description="Execution ID")
    schedule_id: str = Field(..., description="Schedule ID")
    started_at: str = Field(..., description="Start time")
    completed_at: Optional[str] = Field(None, description="Completion time")
    status: str = Field(..., description="pending, running, success, failed")
    duration_seconds: Optional[float] = Field(None)
    rows_processed: Optional[int] = Field(None)
    error_message: Optional[str] = Field(None)
    triggered_by: str = Field("schedule", description="schedule, manual, api")


class AlertExecution(BaseModel):
    """Record of an alert evaluation"""
    id: str = Field(..., description="Execution ID")
    alert_id: str = Field(..., description="Alert ID")
    evaluated_at: str = Field(..., description="Evaluation time")
    triggered: bool = Field(False, description="Whether alert was triggered")
    condition_results: list[dict[str, Any]] = Field(default_factory=list)
    current_value: Optional[float] = Field(None)
    threshold_value: Optional[float] = Field(None)
    notifications_sent: list[str] = Field(default_factory=list)


# Summary Statistics

class ScheduleSummary(BaseModel):
    """Summary of schedule activity"""
    total_schedules: int = Field(0)
    active_schedules: int = Field(0)
    paused_schedules: int = Field(0)
    failed_schedules: int = Field(0)
    executions_today: int = Field(0)
    successful_today: int = Field(0)
    failed_today: int = Field(0)


class AlertSummary(BaseModel):
    """Summary of alert activity"""
    total_alerts: int = Field(0)
    active_alerts: int = Field(0)
    triggered_today: int = Field(0)
    critical_active: int = Field(0)
    warning_active: int = Field(0)


# Common schedule templates

SCHEDULE_TEMPLATES = [
    {
        "id": "daily_morning",
        "name": "Daily Morning Refresh",
        "description": "Refresh data every morning at 6 AM",
        "config": {
            "frequency": "daily",
            "time": {"hour": 6, "minute": 0, "timezone": "UTC"},
        },
    },
    {
        "id": "hourly",
        "name": "Hourly Refresh",
        "description": "Refresh data every hour",
        "config": {
            "frequency": "hourly",
        },
    },
    {
        "id": "weekly_monday",
        "name": "Weekly Monday Morning",
        "description": "Refresh data every Monday at 7 AM",
        "config": {
            "frequency": "weekly",
            "weekly": {"days": [0], "time": {"hour": 7, "minute": 0, "timezone": "UTC"}},
        },
    },
    {
        "id": "monthly_first",
        "name": "Monthly First Day",
        "description": "Refresh data on the first of each month",
        "config": {
            "frequency": "monthly",
            "monthly": {"days": [1], "time": {"hour": 6, "minute": 0, "timezone": "UTC"}},
        },
    },
]

# Common alert templates

ALERT_TEMPLATES = [
    {
        "id": "threshold_exceeded",
        "name": "Threshold Exceeded",
        "description": "Alert when a value exceeds a threshold",
        "conditions": [
            {"operator": "greater_than", "measure": "{measure}", "threshold": "{threshold}"},
        ],
    },
    {
        "id": "threshold_below",
        "name": "Below Threshold",
        "description": "Alert when a value falls below a threshold",
        "conditions": [
            {"operator": "less_than", "measure": "{measure}", "threshold": "{threshold}"},
        ],
    },
    {
        "id": "significant_change",
        "name": "Significant Change",
        "description": "Alert when value changes by more than a percentage",
        "conditions": [
            {"operator": "percent_change_greater_than", "measure": "{measure}", "threshold": 20},
        ],
    },
    {
        "id": "out_of_range",
        "name": "Out of Range",
        "description": "Alert when value is outside expected range",
        "conditions": [
            {"operator": "outside", "measure": "{measure}", "threshold": "{min}", "threshold2": "{max}"},
        ],
    },
]
