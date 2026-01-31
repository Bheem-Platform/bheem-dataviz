"""
Scheduled Reports Schemas

Pydantic schemas for scheduled report management including
schedules, recurrence patterns, delivery options, and execution history.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
from datetime import datetime


# Enums

class ScheduleFrequency(str, Enum):
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class DeliveryMethod(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    S3 = "s3"
    FTP = "ftp"
    SFTP = "sftp"
    DOWNLOAD_LINK = "download_link"


class DayOfWeek(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class TimeZone(str, Enum):
    UTC = "UTC"
    US_EASTERN = "America/New_York"
    US_CENTRAL = "America/Chicago"
    US_PACIFIC = "America/Los_Angeles"
    EUROPE_LONDON = "Europe/London"
    EUROPE_PARIS = "Europe/Paris"
    ASIA_TOKYO = "Asia/Tokyo"
    ASIA_SHANGHAI = "Asia/Shanghai"
    AUSTRALIA_SYDNEY = "Australia/Sydney"


# Schedule Configuration Schemas

class TimeOfDay(BaseModel):
    hour: int = Field(ge=0, le=23, default=9)
    minute: int = Field(ge=0, le=59, default=0)


class RecurrencePattern(BaseModel):
    frequency: ScheduleFrequency
    interval: int = Field(ge=1, default=1)  # Every N intervals
    days_of_week: list[DayOfWeek] = []  # For weekly schedules
    day_of_month: Optional[int] = Field(None, ge=1, le=31)  # For monthly schedules
    month_of_year: Optional[int] = Field(None, ge=1, le=12)  # For yearly schedules
    cron_expression: Optional[str] = None  # For custom schedules
    time_of_day: TimeOfDay = Field(default_factory=TimeOfDay)
    timezone: str = "UTC"


class DateRange(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = None


# Delivery Configuration Schemas

class EmailDeliveryConfig(BaseModel):
    recipients: list[str]
    cc: list[str] = []
    bcc: list[str] = []
    subject_template: str = "Scheduled Report: {report_name}"
    body_template: str = "Please find attached the scheduled report generated on {date}."
    include_inline_preview: bool = False
    attachment_format: str = "pdf"
    max_attachment_size_mb: int = 25


class SlackDeliveryConfig(BaseModel):
    webhook_url: str
    channel: str
    mention_users: list[str] = []
    include_preview_image: bool = True
    message_template: str = "Scheduled report *{report_name}* is ready!"


class TeamsDeliveryConfig(BaseModel):
    webhook_url: str
    include_preview_image: bool = True
    message_template: str = "Scheduled report {report_name} is ready!"


class WebhookDeliveryConfig(BaseModel):
    url: str
    method: str = "POST"
    headers: dict[str, str] = {}
    include_report_data: bool = True
    include_file_url: bool = True
    auth_type: Optional[str] = None
    auth_credentials: Optional[dict[str, str]] = None


class S3DeliveryConfig(BaseModel):
    bucket: str
    path_template: str = "reports/{year}/{month}/{report_name}_{timestamp}"
    region: str = "us-east-1"
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    use_iam_role: bool = False
    encryption: str = "AES256"


class FTPDeliveryConfig(BaseModel):
    host: str
    port: int = 21
    username: str
    password: Optional[str] = None
    path: str = "/"
    passive_mode: bool = True
    use_sftp: bool = False


class DeliveryConfig(BaseModel):
    method: DeliveryMethod
    email_config: Optional[EmailDeliveryConfig] = None
    slack_config: Optional[SlackDeliveryConfig] = None
    teams_config: Optional[TeamsDeliveryConfig] = None
    webhook_config: Optional[WebhookDeliveryConfig] = None
    s3_config: Optional[S3DeliveryConfig] = None
    ftp_config: Optional[FTPDeliveryConfig] = None
    retry_on_failure: bool = True
    max_retries: int = 3
    retry_delay_minutes: int = 5


# Report Configuration Schemas

class ReportSourceConfig(BaseModel):
    source_type: str  # "dashboard", "chart", "template", "query"
    source_id: str
    source_name: Optional[str] = None
    export_format: str = "pdf"
    filters: dict[str, Any] = {}
    parameters: dict[str, Any] = {}
    template_id: Optional[str] = None
    date_range_type: str = "last_7_days"  # "custom", "last_7_days", "last_30_days", etc.
    custom_date_range: Optional[DateRange] = None


# Scheduled Report Schemas

class ScheduledReportBase(BaseModel):
    name: str
    description: Optional[str] = None
    source_config: ReportSourceConfig
    recurrence: RecurrencePattern
    delivery_configs: list[DeliveryConfig]
    date_range: DateRange


class ScheduledReportCreate(ScheduledReportBase):
    is_active: bool = True
    notify_on_failure: bool = True
    failure_notification_emails: list[str] = []
    tags: list[str] = []


class ScheduledReportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_config: Optional[ReportSourceConfig] = None
    recurrence: Optional[RecurrencePattern] = None
    delivery_configs: Optional[list[DeliveryConfig]] = None
    date_range: Optional[DateRange] = None
    is_active: Optional[bool] = None
    status: Optional[ScheduleStatus] = None
    notify_on_failure: Optional[bool] = None
    failure_notification_emails: Optional[list[str]] = None
    tags: Optional[list[str]] = None


class ScheduledReport(ScheduledReportBase):
    id: str
    user_id: str
    organization_id: Optional[str] = None
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    is_active: bool = True
    notify_on_failure: bool = True
    failure_notification_emails: list[str] = []
    tags: list[str] = []
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[ExecutionStatus] = None
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduledReportListResponse(BaseModel):
    schedules: list[ScheduledReport]
    total: int


# Execution History Schemas

class ExecutionLog(BaseModel):
    timestamp: datetime
    level: str  # "info", "warning", "error"
    message: str
    details: Optional[dict[str, Any]] = None


class DeliveryResult(BaseModel):
    method: DeliveryMethod
    success: bool
    message: Optional[str] = None
    delivered_at: Optional[datetime] = None
    recipient_count: int = 0
    file_url: Optional[str] = None
    error: Optional[str] = None


class ReportExecution(BaseModel):
    id: str
    schedule_id: str
    schedule_name: str
    user_id: str
    organization_id: Optional[str] = None
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    source_config: ReportSourceConfig
    export_format: str
    file_size_bytes: Optional[int] = None
    file_url: Optional[str] = None
    delivery_results: list[DeliveryResult] = []
    logs: list[ExecutionLog] = []
    error_message: Optional[str] = None
    retry_count: int = 0
    triggered_by: str = "schedule"  # "schedule", "manual", "retry"

    class Config:
        from_attributes = True


class ReportExecutionListResponse(BaseModel):
    executions: list[ReportExecution]
    total: int


# Schedule Statistics

class ScheduleStats(BaseModel):
    organization_id: str
    total_schedules: int
    active_schedules: int
    paused_schedules: int
    total_executions: int
    executions_today: int
    executions_this_week: int
    executions_this_month: int
    success_rate: float
    average_duration_seconds: float
    by_frequency: dict[str, int]
    by_format: dict[str, int]
    by_delivery_method: dict[str, int]
    upcoming_executions: int


# Constants

SCHEDULE_FREQUENCY_LABELS: dict[ScheduleFrequency, str] = {
    ScheduleFrequency.ONCE: "One Time",
    ScheduleFrequency.HOURLY: "Hourly",
    ScheduleFrequency.DAILY: "Daily",
    ScheduleFrequency.WEEKLY: "Weekly",
    ScheduleFrequency.BIWEEKLY: "Bi-Weekly",
    ScheduleFrequency.MONTHLY: "Monthly",
    ScheduleFrequency.QUARTERLY: "Quarterly",
    ScheduleFrequency.YEARLY: "Yearly",
    ScheduleFrequency.CUSTOM: "Custom",
}

SCHEDULE_STATUS_LABELS: dict[ScheduleStatus, str] = {
    ScheduleStatus.ACTIVE: "Active",
    ScheduleStatus.PAUSED: "Paused",
    ScheduleStatus.COMPLETED: "Completed",
    ScheduleStatus.EXPIRED: "Expired",
    ScheduleStatus.FAILED: "Failed",
    ScheduleStatus.CANCELLED: "Cancelled",
}

EXECUTION_STATUS_LABELS: dict[ExecutionStatus, str] = {
    ExecutionStatus.PENDING: "Pending",
    ExecutionStatus.RUNNING: "Running",
    ExecutionStatus.COMPLETED: "Completed",
    ExecutionStatus.FAILED: "Failed",
    ExecutionStatus.CANCELLED: "Cancelled",
    ExecutionStatus.SKIPPED: "Skipped",
}

DELIVERY_METHOD_LABELS: dict[DeliveryMethod, str] = {
    DeliveryMethod.EMAIL: "Email",
    DeliveryMethod.SLACK: "Slack",
    DeliveryMethod.TEAMS: "Microsoft Teams",
    DeliveryMethod.WEBHOOK: "Webhook",
    DeliveryMethod.S3: "Amazon S3",
    DeliveryMethod.FTP: "FTP",
    DeliveryMethod.SFTP: "SFTP",
    DeliveryMethod.DOWNLOAD_LINK: "Download Link",
}

DAY_OF_WEEK_LABELS: dict[DayOfWeek, str] = {
    DayOfWeek.MONDAY: "Monday",
    DayOfWeek.TUESDAY: "Tuesday",
    DayOfWeek.WEDNESDAY: "Wednesday",
    DayOfWeek.THURSDAY: "Thursday",
    DayOfWeek.FRIDAY: "Friday",
    DayOfWeek.SATURDAY: "Saturday",
    DayOfWeek.SUNDAY: "Sunday",
}


# Helper Functions

def get_next_run_time(recurrence: RecurrencePattern, from_time: Optional[datetime] = None) -> datetime:
    """Calculate next run time based on recurrence pattern."""
    from datetime import timedelta
    import calendar

    now = from_time or datetime.utcnow()

    # Set base time to configured time of day
    base_time = now.replace(
        hour=recurrence.time_of_day.hour,
        minute=recurrence.time_of_day.minute,
        second=0,
        microsecond=0
    )

    if recurrence.frequency == ScheduleFrequency.HOURLY:
        next_run = now.replace(minute=recurrence.time_of_day.minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(hours=recurrence.interval)
        return next_run

    elif recurrence.frequency == ScheduleFrequency.DAILY:
        if base_time <= now:
            base_time += timedelta(days=recurrence.interval)
        return base_time

    elif recurrence.frequency == ScheduleFrequency.WEEKLY:
        # Find next matching day of week
        current_day = now.weekday()
        target_days = [DayOfWeek(d).value for d in recurrence.days_of_week] if recurrence.days_of_week else [0]
        days_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
        target_day_nums = sorted([days_map.get(d, 0) for d in target_days])

        for day_num in target_day_nums:
            days_ahead = day_num - current_day
            if days_ahead < 0:
                days_ahead += 7
            candidate = base_time + timedelta(days=days_ahead)
            if candidate > now:
                return candidate

        # Next week
        days_ahead = target_day_nums[0] - current_day + 7
        return base_time + timedelta(days=days_ahead)

    elif recurrence.frequency == ScheduleFrequency.MONTHLY:
        day = recurrence.day_of_month or 1
        next_month = now.month + recurrence.interval
        year = now.year + (next_month - 1) // 12
        month = ((next_month - 1) % 12) + 1

        # Handle months with fewer days
        max_day = calendar.monthrange(year, month)[1]
        day = min(day, max_day)

        next_run = base_time.replace(year=year, month=month, day=day)
        if next_run <= now:
            next_month += recurrence.interval
            year = now.year + (next_month - 1) // 12
            month = ((next_month - 1) % 12) + 1
            max_day = calendar.monthrange(year, month)[1]
            day = min(recurrence.day_of_month or 1, max_day)
            next_run = base_time.replace(year=year, month=month, day=day)

        return next_run

    else:
        # Default: add one day
        return base_time + timedelta(days=1)


def is_schedule_due(schedule: ScheduledReport) -> bool:
    """Check if a schedule is due to run."""
    if schedule.status != ScheduleStatus.ACTIVE or not schedule.is_active:
        return False

    if not schedule.next_run_at:
        return False

    return datetime.utcnow() >= schedule.next_run_at


def format_schedule_description(recurrence: RecurrencePattern) -> str:
    """Generate human-readable schedule description."""
    freq = recurrence.frequency
    time_str = f"{recurrence.time_of_day.hour:02d}:{recurrence.time_of_day.minute:02d}"

    if freq == ScheduleFrequency.ONCE:
        return f"One time at {time_str}"
    elif freq == ScheduleFrequency.HOURLY:
        if recurrence.interval == 1:
            return f"Every hour at minute {recurrence.time_of_day.minute}"
        return f"Every {recurrence.interval} hours at minute {recurrence.time_of_day.minute}"
    elif freq == ScheduleFrequency.DAILY:
        if recurrence.interval == 1:
            return f"Daily at {time_str}"
        return f"Every {recurrence.interval} days at {time_str}"
    elif freq == ScheduleFrequency.WEEKLY:
        days = ", ".join([DAY_OF_WEEK_LABELS.get(d, d) for d in recurrence.days_of_week])
        return f"Weekly on {days} at {time_str}"
    elif freq == ScheduleFrequency.MONTHLY:
        day = recurrence.day_of_month or 1
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        if 11 <= day <= 13:
            suffix = "th"
        return f"Monthly on the {day}{suffix} at {time_str}"
    elif freq == ScheduleFrequency.QUARTERLY:
        return f"Quarterly at {time_str}"
    elif freq == ScheduleFrequency.YEARLY:
        return f"Yearly at {time_str}"
    elif freq == ScheduleFrequency.CUSTOM and recurrence.cron_expression:
        return f"Custom: {recurrence.cron_expression}"

    return "Unknown schedule"
