"""
Sharing Models

Database models for sharing dashboards, charts, and reports.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.database import Base


class SharedLink(Base):
    """
    Shared link model for public/private sharing.
    """
    __tablename__ = "shared_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Link token
    token = Column(String(64), unique=True, nullable=False, index=True)

    # Resource
    resource_type = Column(String(50), nullable=False)  # dashboard, chart, report
    resource_id = Column(UUID(as_uuid=True), nullable=False)

    # Access control
    access_type = Column(String(50), default="view")  # view, interact, edit
    password_hash = Column(String(255), nullable=True)
    require_login = Column(Boolean, default=False)

    # Permissions
    allow_export = Column(Boolean, default=False)
    allow_filter = Column(Boolean, default=True)
    allow_drill = Column(Boolean, default=True)

    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)
    max_views = Column(Integer, nullable=True)
    view_count = Column(Integer, default=0)

    # Domain restrictions
    allowed_domains = Column(JSONB, default=[])
    allowed_emails = Column(JSONB, default=[])

    # Status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_by = Column(UUID(as_uuid=True), nullable=True)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_shared_links_resource', resource_type, resource_id),
    )


class SharePermission(Base):
    """
    User-specific share permissions.
    """
    __tablename__ = "share_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Resource
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=False)

    # Grantee
    grantee_type = Column(String(50), nullable=False)  # user, group, role
    grantee_id = Column(UUID(as_uuid=True), nullable=False)
    grantee_email = Column(String(255), nullable=True)

    # Permission
    permission_level = Column(String(50), nullable=False)  # view, edit, admin

    # Status
    is_active = Column(Boolean, default=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    # Ownership
    granted_by = Column(UUID(as_uuid=True), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_share_permissions_resource', resource_type, resource_id),
        Index('ix_share_permissions_grantee', grantee_type, grantee_id),
    )


class ShareInvitation(Base):
    """
    Share invitation for external users.
    """
    __tablename__ = "share_invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Invitation token
    token = Column(String(64), unique=True, nullable=False, index=True)

    # Resource
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=False)

    # Invitee
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)

    # Permission
    permission_level = Column(String(50), default="view")

    # Message
    message = Column(Text, nullable=True)

    # Status
    status = Column(String(50), default="pending")  # pending, accepted, declined, expired
    expires_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    accepted_by = Column(UUID(as_uuid=True), nullable=True)

    # Ownership
    invited_by = Column(UUID(as_uuid=True), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index('ix_share_invitations_email_status', email, status),
    )


class ShareActivity(Base):
    """
    Activity log for shared resources.
    """
    __tablename__ = "share_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Resource
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=False)

    # Activity
    activity_type = Column(String(100), nullable=False)  # viewed, filtered, exported, commented

    # User
    user_id = Column(UUID(as_uuid=True), nullable=True)
    user_email = Column(String(255), nullable=True)
    is_anonymous = Column(Boolean, default=False)

    # Context
    shared_link_id = Column(UUID(as_uuid=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Details
    activity_data = Column(JSONB, default={})

    # Timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('ix_share_activities_resource_date', resource_type, resource_id, created_at),
    )


class Comment(Base):
    """
    Comments on shared dashboards/charts.
    """
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Resource
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=False)

    # Parent (for replies)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    # Content
    content = Column(Text, nullable=False)

    # Position (for annotations)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    chart_id = Column(UUID(as_uuid=True), nullable=True)

    # Author
    author_id = Column(UUID(as_uuid=True), nullable=False)
    author_name = Column(String(255), nullable=True)

    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_comments_resource', resource_type, resource_id),
    )
