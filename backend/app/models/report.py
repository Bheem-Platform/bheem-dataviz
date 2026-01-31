"""
Report Models

Database models for reports, templates, and scheduled reports.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Report(Base):
    """
    Report model for saved reports.
    """
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # dashboard, chart, query, custom

    # Content
    content_config = Column(JSONB, default={})
    layout_config = Column(JSONB, default={})

    # Source
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="SET NULL"), nullable=True)
    chart_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])
    query_id = Column(UUID(as_uuid=True), nullable=True)

    # Filters
    applied_filters = Column(JSONB, default={})
    date_range = Column(JSONB, nullable=True)

    # Export settings
    export_format = Column(String(20), default="pdf")  # pdf, xlsx, csv, png
    page_size = Column(String(20), default="A4")
    orientation = Column(String(20), default="portrait")

    # Ownership
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Status
    is_template = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_generated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    scheduled_reports = relationship("ScheduledReport", back_populates="report", cascade="all, delete-orphan")


class ReportTemplate(Base):
    """
    Report template model for reusable report layouts.
    """
    __tablename__ = "report_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    # Template configuration
    template_config = Column(JSONB, nullable=False, default={})
    layout = Column(JSONB, default={})
    styles = Column(JSONB, default={})

    # Header/Footer
    header_config = Column(JSONB, nullable=True)
    footer_config = Column(JSONB, nullable=True)

    # Placeholders
    placeholders = Column(JSONB, default=[])

    # Preview
    thumbnail_url = Column(String(500), nullable=True)

    # Status
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ScheduledReport(Base):
    """
    Scheduled report model for automated report generation and delivery.
    """
    __tablename__ = "scheduled_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Report reference
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)

    # Schedule
    schedule_name = Column(String(255), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    timezone = Column(String(50), default="UTC")

    # Delivery
    delivery_method = Column(String(50), nullable=False)  # email, slack, webhook, s3
    recipients = Column(JSONB, default=[])
    delivery_config = Column(JSONB, default={})

    # Export settings
    export_format = Column(String(20), default="pdf")
    include_data = Column(Boolean, default=True)

    # Status
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_status = Column(String(50), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)

    # Error tracking
    consecutive_failures = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    report = relationship("Report", back_populates="scheduled_reports")
    executions = relationship("ScheduledReportExecution", back_populates="scheduled_report", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_scheduled_reports_next_run', next_run_at, is_active),
    )


class ScheduledReportExecution(Base):
    """
    Execution history for scheduled reports.
    """
    __tablename__ = "scheduled_report_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    scheduled_report_id = Column(UUID(as_uuid=True), ForeignKey("scheduled_reports.id", ondelete="CASCADE"), nullable=False)

    # Execution details
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False)  # pending, running, completed, failed

    # Result
    output_url = Column(String(500), nullable=True)
    output_size_bytes = Column(Integer, nullable=True)
    recipients_count = Column(Integer, default=0)
    delivery_status = Column(JSONB, default={})

    # Error
    error_message = Column(Text, nullable=True)

    # Relationships
    scheduled_report = relationship("ScheduledReport", back_populates="executions")

    __table_args__ = (
        Index('ix_scheduled_report_executions_report_started', scheduled_report_id, started_at),
    )
