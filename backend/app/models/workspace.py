"""
Workspace Models

Database models for team workspaces and collaboration.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class WorkspaceRole(str, enum.Enum):
    """Roles within a workspace"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class InviteStatus(str, enum.Enum):
    """Status of workspace invitations"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class Workspace(Base):
    """
    Workspace model for team collaboration.

    Workspaces provide isolated environments for teams to collaborate
    on dashboards, charts, and data connections.
    """
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Settings
    is_personal = Column(Boolean, default=False)  # Personal workspace (one per user)
    is_default = Column(Boolean, default=False)   # Default workspace for new resources

    # Branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), nullable=True)  # Hex color

    # Configuration
    settings = Column(JSONB, default={})

    # Limits
    max_members = Column(Integer, nullable=True)  # None = unlimited
    max_dashboards = Column(Integer, nullable=True)
    max_connections = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], backref="owned_workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    invitations = relationship("WorkspaceInvitation", back_populates="workspace", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_workspaces_owner', owner_id),
    )


class WorkspaceMember(Base):
    """
    Workspace membership model.

    Links users to workspaces with specific roles.
    """
    __tablename__ = "workspace_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Role - use String with PostgreSQL enum through type cast
    role = Column(String(20), nullable=False, default='member')

    # Permissions overrides (if different from role defaults)
    custom_permissions = Column(JSONB, default={})

    # Invitation tracking
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    invited_at = Column(DateTime(timezone=True), nullable=True)
    joined_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Status
    is_active = Column(Boolean, default=True)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], backref="workspace_memberships")
    inviter = relationship("User", foreign_keys=[invited_by])

    __table_args__ = (
        Index('ix_workspace_members_workspace', workspace_id),
        Index('ix_workspace_members_user', user_id),
        Index('ix_workspace_members_unique', workspace_id, user_id, unique=True),
    )


class WorkspaceInvitation(Base):
    """
    Workspace invitation model.

    Tracks pending invitations to join workspaces.
    """
    __tablename__ = "workspace_invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)

    # Invitation details
    email = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='member')

    # Token for accepting invitation
    token = Column(String(255), unique=True, nullable=False, index=True)

    # Sender
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Status
    status = Column(String(20), default='pending')

    # Message
    message = Column(Text, nullable=True)

    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by])

    __table_args__ = (
        Index('ix_workspace_invitations_workspace', workspace_id),
        Index('ix_workspace_invitations_email', email),
    )


class ObjectPermission(Base):
    """
    Object-level permission overrides.

    Allows fine-grained access control for specific resources
    within a workspace.
    """
    __tablename__ = "object_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)

    # Object reference
    object_type = Column(String(50), nullable=False)  # dashboard, chart, connection, dataset
    object_id = Column(UUID(as_uuid=True), nullable=False)

    # Permission target (user or role)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    role = Column(String(20), nullable=True)

    # Permissions
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index('ix_object_permissions_object', object_type, object_id),
        Index('ix_object_permissions_user', user_id),
        Index('ix_object_permissions_workspace', workspace_id),
    )
