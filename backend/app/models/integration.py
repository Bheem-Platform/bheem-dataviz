"""
Integration Models

Database models for third-party integrations.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Integration(Base):
    """
    Integration model for third-party service connections.
    """
    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)

    # Integration info
    name = Column(String(255), nullable=False)
    integration_type = Column(String(50), nullable=False)  # slack, teams, email, webhook, jira, github

    # Configuration
    config = Column(JSONB, default={})

    # Authentication
    auth_type = Column(String(50), nullable=True)  # oauth2, api_key, webhook
    credentials = Column(JSONB, default={})  # Encrypted
    oauth_tokens = Column(JSONB, nullable=True)  # Encrypted

    # Status
    is_active = Column(Boolean, default=True)
    connection_status = Column(String(50), default="pending")  # pending, connected, error, expired

    # Last sync
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    webhooks = relationship("IntegrationWebhook", back_populates="integration", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_integrations_workspace_type', workspace_id, integration_type),
    )


class IntegrationWebhook(Base):
    """
    Webhook configuration for integrations.
    """
    __tablename__ = "integration_webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False)

    # Webhook info
    name = Column(String(255), nullable=False)
    webhook_url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=True)

    # Events
    events = Column(JSONB, default=[])  # dashboard.created, alert.triggered, etc.

    # Configuration
    payload_format = Column(String(20), default="json")
    headers = Column(JSONB, default={})
    retry_config = Column(JSONB, default={"max_retries": 3, "retry_delay": 60})

    # Status
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    last_status = Column(String(50), nullable=True)
    failure_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    integration = relationship("Integration", back_populates="webhooks")


class IntegrationLog(Base):
    """
    Log of integration events and API calls.
    """
    __tablename__ = "integration_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False)

    # Event info
    event_type = Column(String(100), nullable=False)
    direction = Column(String(20), nullable=False)  # inbound, outbound

    # Request/Response
    request_data = Column(JSONB, nullable=True)
    response_data = Column(JSONB, nullable=True)
    status_code = Column(Integer, nullable=True)

    # Result
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Timing
    duration_ms = Column(Integer, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('ix_integration_logs_integration_created', integration_id, created_at),
    )


class SlackChannel(Base):
    """
    Slack channel mapping for notifications.
    """
    __tablename__ = "slack_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False)

    # Channel info
    channel_id = Column(String(100), nullable=False)
    channel_name = Column(String(255), nullable=False)
    channel_type = Column(String(50), default="channel")  # channel, dm, group

    # Notification settings
    notify_alerts = Column(Boolean, default=True)
    notify_reports = Column(Boolean, default=False)
    notify_comments = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index('ix_slack_channels_integration_channel', integration_id, channel_id, unique=True),
    )
