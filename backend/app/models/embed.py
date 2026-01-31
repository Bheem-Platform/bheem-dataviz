"""
Embed Models

Database models for embed tokens and configurations.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class EmbedToken(Base):
    """
    Embed token model for secure dashboard/chart embedding.

    Tokens are used to authenticate embedded content without exposing
    user credentials. Each token has configurable permissions and expiry.
    """
    __tablename__ = "embed_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Token value (hashed for security)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)

    # Human-readable name
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Target content
    resource_type = Column(String(50), nullable=False)  # dashboard, chart
    resource_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Permissions
    allow_interactions = Column(Boolean, default=True)  # filters, drill-down
    allow_export = Column(Boolean, default=False)
    allow_fullscreen = Column(Boolean, default=True)
    allow_comments = Column(Boolean, default=False)

    # Appearance
    theme = Column(String(50), default="auto")  # light, dark, auto
    show_header = Column(Boolean, default=True)
    show_toolbar = Column(Boolean, default=False)
    custom_css = Column(Text, nullable=True)

    # Domain restrictions
    allowed_domains = Column(JSONB, default=[])  # Empty = allow all

    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)
    max_views = Column(Integer, nullable=True)  # Null = unlimited
    view_count = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_by = Column(UUID(as_uuid=True), nullable=True)

    # Settings and extra data
    settings = Column(JSONB, default={})
    extra_data = Column(JSONB, default={})

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_embed_tokens_resource', resource_type, resource_id),
        Index('ix_embed_tokens_created_by_active', created_by, is_active),
    )


class EmbedSession(Base):
    """
    Embed session tracking for analytics and security.

    Records each viewing session for embedded content.
    """
    __tablename__ = "embed_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Associated token
    token_id = Column(UUID(as_uuid=True), ForeignKey("embed_tokens.id"), nullable=False, index=True)

    # Session info
    session_id = Column(String(255), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Origin
    origin_domain = Column(String(255), nullable=True)
    origin_url = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)

    # Client info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)

    # Engagement
    interaction_count = Column(Integer, default=0)
    filter_changes = Column(Integer, default=0)
    exports_count = Column(Integer, default=0)
    duration_seconds = Column(Integer, nullable=True)

    # Context
    extra_data = Column(JSONB, default={})

    __table_args__ = (
        Index('ix_embed_sessions_token_started', token_id, started_at),
    )


class EmbedAnalytics(Base):
    """
    Aggregated embed analytics.

    Daily aggregation of embed metrics for reporting.
    """
    __tablename__ = "embed_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Token reference
    token_id = Column(UUID(as_uuid=True), ForeignKey("embed_tokens.id"), nullable=False, index=True)

    # Date (day-level aggregation)
    date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Metrics
    total_views = Column(Integer, default=0)
    unique_sessions = Column(Integer, default=0)
    total_interactions = Column(Integer, default=0)
    total_exports = Column(Integer, default=0)
    avg_duration_seconds = Column(Integer, default=0)

    # Device breakdown
    desktop_views = Column(Integer, default=0)
    mobile_views = Column(Integer, default=0)
    tablet_views = Column(Integer, default=0)

    # Top domains
    top_domains = Column(JSONB, default=[])

    __table_args__ = (
        Index('ix_embed_analytics_token_date', token_id, date, unique=True),
    )


class EmbedWhitelist(Base):
    """
    Global domain whitelist for embedded content.

    Workspace-level configuration for allowed embedding domains.
    """
    __tablename__ = "embed_whitelists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    domain = Column(String(255), nullable=False)
    is_wildcard = Column(Boolean, default=False)  # *.example.com

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    added_by = Column(UUID(as_uuid=True), nullable=False)
    added_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index('ix_embed_whitelists_workspace_domain', workspace_id, domain, unique=True),
    )


# Constants

class EmbedResourceType:
    """Valid embed resource types"""
    DASHBOARD = "dashboard"
    CHART = "chart"
    REPORT = "report"


class EmbedTheme:
    """Available embed themes"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    CUSTOM = "custom"


class DeviceType:
    """Device type classifications"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    UNKNOWN = "unknown"
