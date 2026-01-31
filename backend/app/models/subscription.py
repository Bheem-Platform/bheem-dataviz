"""
Subscription and Schedule Models

SQLAlchemy models for scheduled refresh, alerts, and subscriptions.
"""

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class ScheduleFrequency(str, enum.Enum):
    """Schedule frequency options"""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ScheduleStatus(str, enum.Enum):
    """Schedule status"""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    ERROR = "error"


class RefreshType(str, enum.Enum):
    """Data refresh type"""
    FULL = "full"
    INCREMENTAL = "incremental"
    PARTITION = "partition"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    """Alert status"""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SNOOZED = "snoozed"


class NotificationChannel(str, enum.Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SMS = "sms"


class RefreshSchedule(Base):
    """
    Data refresh schedule configuration.

    Stores schedules for automatic data refresh of connections/datasets.
    """
    __tablename__ = "refresh_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Target
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.id", ondelete="CASCADE"), nullable=True)
    dataset_id = Column(UUID(as_uuid=True), nullable=True)
    semantic_model_id = Column(UUID(as_uuid=True), ForeignKey("semantic_models.id", ondelete="CASCADE"), nullable=True)

    # Schedule configuration
    frequency = Column(Enum(ScheduleFrequency), nullable=False, default=ScheduleFrequency.DAILY)
    cron_expression = Column(String(100), nullable=True)  # For custom schedules
    timezone = Column(String(50), default="UTC")

    # Schedule time (for non-custom)
    hour = Column(Integer, nullable=True)  # 0-23
    minute = Column(Integer, default=0)  # 0-59
    day_of_week = Column(ARRAY(Integer), nullable=True)  # 0=Monday, 6=Sunday
    day_of_month = Column(ARRAY(Integer), nullable=True)  # 1-31

    # Refresh options
    refresh_type = Column(Enum(RefreshType), default=RefreshType.FULL)
    incremental_column = Column(String(255), nullable=True)
    incremental_lookback_days = Column(Integer, default=1)
    timeout_seconds = Column(Integer, default=3600)  # 1 hour default

    # Retry configuration
    max_retries = Column(Integer, default=3)
    retry_delay_minutes = Column(Integer, default=5)

    # Notifications
    notify_on_success = Column(Boolean, default=False)
    notify_on_failure = Column(Boolean, default=True)
    notification_recipients = Column(JSONB, default=list)  # [{"type": "email", "value": "..."}]

    # Status
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.ACTIVE)
    is_enabled = Column(Boolean, default=True)

    # Execution tracking
    last_run_at = Column(DateTime, nullable=True)
    last_run_status = Column(String(50), nullable=True)
    last_run_duration_seconds = Column(Integer, nullable=True)
    last_run_error = Column(Text, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    consecutive_failures = Column(Integer, default=0)
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)

    # Ownership
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship("ScheduleExecution", back_populates="schedule", cascade="all, delete-orphan")


class ScheduleExecution(Base):
    """
    Record of a schedule execution.

    Tracks each run of a refresh schedule.
    """
    __tablename__ = "schedule_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("refresh_schedules.id", ondelete="CASCADE"), nullable=False)

    # Execution details
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="running")  # running, success, failed, cancelled

    # Results
    rows_processed = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)

    # Trigger info
    triggered_by = Column(String(50), default="schedule")  # schedule, manual, api
    triggered_by_user_id = Column(UUID(as_uuid=True), nullable=True)

    # Logs
    log_output = Column(Text, nullable=True)

    # Relationships
    schedule = relationship("RefreshSchedule", back_populates="executions")


class AlertRule(Base):
    """
    Alert rule configuration.

    Defines conditions that trigger notifications.
    """
    __tablename__ = "alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Target
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=True)
    chart_id = Column(UUID(as_uuid=True), ForeignKey("saved_charts.id", ondelete="CASCADE"), nullable=True)
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("saved_kpis.id", ondelete="CASCADE"), nullable=True)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.id", ondelete="CASCADE"), nullable=True)

    # Alert configuration
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.WARNING)
    conditions = Column(JSONB, nullable=False)  # [{measure, operator, threshold, threshold2}]
    condition_logic = Column(String(10), default="AND")  # AND, OR

    # Evaluation schedule
    evaluation_frequency = Column(Enum(ScheduleFrequency), default=ScheduleFrequency.HOURLY)
    evaluation_cron = Column(String(100), nullable=True)
    timezone = Column(String(50), default="UTC")

    # Notification
    notification_channels = Column(ARRAY(String), default=list)  # ['email', 'slack', ...]
    notification_recipients = Column(JSONB, default=list)
    notification_message_template = Column(Text, nullable=True)

    # Throttling
    min_interval_minutes = Column(Integer, default=60)  # Don't alert more than once per interval
    snooze_until = Column(DateTime, nullable=True)

    # Status
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    is_enabled = Column(Boolean, default=True)

    # Tracking
    last_evaluated_at = Column(DateTime, nullable=True)
    last_triggered_at = Column(DateTime, nullable=True)
    last_value = Column(Float, nullable=True)
    trigger_count = Column(Integer, default=0)

    # Ownership
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship("AlertExecution", back_populates="alert", cascade="all, delete-orphan")


class AlertExecution(Base):
    """
    Record of an alert evaluation.

    Tracks each evaluation of an alert rule.
    """
    __tablename__ = "alert_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False)

    # Evaluation
    evaluated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    triggered = Column(Boolean, default=False)

    # Results
    condition_results = Column(JSONB, nullable=True)  # [{condition_id, triggered, current_value}]
    current_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)

    # Notifications
    notifications_sent = Column(JSONB, default=list)  # [{channel, recipient, sent_at, status}]

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Relationships
    alert = relationship("AlertRule", back_populates="executions")


class Subscription(Base):
    """
    User subscription to reports/dashboards.

    Scheduled delivery of reports to users.
    """
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Target
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=True)
    chart_id = Column(UUID(as_uuid=True), ForeignKey("saved_charts.id", ondelete="CASCADE"), nullable=True)
    report_id = Column(UUID(as_uuid=True), nullable=True)

    # Schedule
    frequency = Column(Enum(ScheduleFrequency), default=ScheduleFrequency.DAILY)
    cron_expression = Column(String(100), nullable=True)
    timezone = Column(String(50), default="UTC")
    hour = Column(Integer, default=9)  # 9 AM default
    minute = Column(Integer, default=0)
    day_of_week = Column(ARRAY(Integer), nullable=True)
    day_of_month = Column(ARRAY(Integer), nullable=True)

    # Delivery
    delivery_channel = Column(Enum(NotificationChannel), default=NotificationChannel.EMAIL)
    recipients = Column(JSONB, nullable=False)  # [{"type": "email", "value": "..."}]

    # Format options
    export_format = Column(String(20), default="pdf")  # pdf, xlsx, png
    include_filters = Column(Boolean, default=True)
    page_size = Column(String(20), default="A4")
    orientation = Column(String(20), default="landscape")

    # Filter state (optional - apply filters before export)
    filter_state = Column(JSONB, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Tracking
    last_sent_at = Column(DateTime, nullable=True)
    next_send_at = Column(DateTime, nullable=True)
    send_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)

    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationTemplate(Base):
    """
    Notification message templates.

    Reusable templates for alert/subscription notifications.
    """
    __tablename__ = "notification_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Template
    channel = Column(Enum(NotificationChannel), nullable=False)
    subject_template = Column(String(500), nullable=True)  # For email
    body_template = Column(Text, nullable=False)

    # Variables available: {{alert_name}}, {{value}}, {{threshold}}, {{dashboard_name}}, etc.

    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Ownership
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
