"""
Workspace Schemas

Pydantic schemas for workspace API requests and responses.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import datetime


# Enums

class WorkspaceRole(str, Enum):
    """Roles within a workspace"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class InviteStatus(str, Enum):
    """Status of workspace invitations"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


# Workspace Schemas

class WorkspaceBase(BaseModel):
    """Base workspace schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a workspace"""
    slug: Optional[str] = None  # Auto-generated if not provided
    logo_url: Optional[str] = None
    primary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    settings: dict[str, Any] = Field(default_factory=dict)


class WorkspaceUpdate(BaseModel):
    """Schema for updating a workspace"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    settings: Optional[dict[str, Any]] = None
    is_default: Optional[bool] = None


class WorkspaceResponse(WorkspaceBase):
    """Schema for workspace response"""
    id: str
    slug: str
    owner_id: str
    is_personal: bool
    is_default: bool
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    settings: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    member_count: int = 0
    dashboard_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkspaceSummary(BaseModel):
    """Lightweight workspace summary"""
    id: str
    name: str
    slug: str
    is_personal: bool
    is_default: bool
    role: WorkspaceRole
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None


# Member Schemas

class MemberBase(BaseModel):
    """Base member schema"""
    role: WorkspaceRole = WorkspaceRole.MEMBER


class MemberCreate(MemberBase):
    """Schema for adding a member directly (if user exists)"""
    user_id: str


class MemberUpdate(BaseModel):
    """Schema for updating a member"""
    role: Optional[WorkspaceRole] = None
    custom_permissions: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class MemberResponse(BaseModel):
    """Schema for member response"""
    id: str
    workspace_id: str
    user_id: str
    role: WorkspaceRole
    custom_permissions: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    joined_at: datetime
    last_accessed_at: Optional[datetime] = None

    # User info (populated from relationship)
    user_email: Optional[str] = None
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


# Invitation Schemas

class InvitationCreate(BaseModel):
    """Schema for creating an invitation"""
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.MEMBER
    message: Optional[str] = None
    expires_in_days: int = Field(default=7, ge=1, le=30)


class InvitationResponse(BaseModel):
    """Schema for invitation response"""
    id: str
    workspace_id: str
    email: str
    role: WorkspaceRole
    status: InviteStatus
    message: Optional[str] = None
    invited_by: str
    inviter_name: Optional[str] = None
    expires_at: datetime
    created_at: datetime
    accepted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvitationAccept(BaseModel):
    """Schema for accepting an invitation"""
    token: str


class BulkInvite(BaseModel):
    """Schema for bulk invitations"""
    emails: list[EmailStr] = Field(..., min_length=1, max_length=50)
    role: WorkspaceRole = WorkspaceRole.MEMBER
    message: Optional[str] = None


class BulkInviteResponse(BaseModel):
    """Response for bulk invitations"""
    sent: list[str]
    failed: list[dict[str, str]]  # {"email": "...", "reason": "..."}
    total_sent: int
    total_failed: int


# Permission Schemas

class ObjectPermissionBase(BaseModel):
    """Base object permission schema"""
    object_type: str
    object_id: str
    can_view: bool = True
    can_edit: bool = False
    can_delete: bool = False
    can_share: bool = False
    can_export: bool = False


class ObjectPermissionCreate(ObjectPermissionBase):
    """Schema for creating object permission"""
    user_id: Optional[str] = None  # Either user_id or role must be set
    role: Optional[WorkspaceRole] = None


class ObjectPermissionResponse(ObjectPermissionBase):
    """Schema for object permission response"""
    id: str
    workspace_id: str
    user_id: Optional[str] = None
    role: Optional[WorkspaceRole] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionCheck(BaseModel):
    """Schema for checking permissions"""
    object_type: str
    object_id: str
    action: str  # view, edit, delete, share, export


class PermissionCheckResponse(BaseModel):
    """Response for permission check"""
    allowed: bool
    reason: Optional[str] = None


# Transfer Ownership Schema

class TransferOwnership(BaseModel):
    """Schema for transferring workspace ownership"""
    new_owner_id: str


# Workspace Settings

class WorkspaceSettings(BaseModel):
    """Workspace settings schema"""
    allow_member_invite: bool = True
    allow_viewer_export: bool = False
    require_approval_for_publish: bool = False
    default_dashboard_visibility: str = "workspace"  # workspace, private
    default_connection_visibility: str = "workspace"
    enable_audit_logging: bool = True
    data_retention_days: Optional[int] = None


# Role Permissions (default permissions per role)

ROLE_PERMISSIONS = {
    WorkspaceRole.OWNER: {
        "can_manage_workspace": True,
        "can_manage_members": True,
        "can_manage_billing": True,
        "can_create_content": True,
        "can_edit_all_content": True,
        "can_delete_all_content": True,
        "can_share_content": True,
        "can_export_data": True,
        "can_manage_connections": True,
        "can_view_audit_logs": True,
    },
    WorkspaceRole.ADMIN: {
        "can_manage_workspace": False,
        "can_manage_members": True,
        "can_manage_billing": False,
        "can_create_content": True,
        "can_edit_all_content": True,
        "can_delete_all_content": True,
        "can_share_content": True,
        "can_export_data": True,
        "can_manage_connections": True,
        "can_view_audit_logs": True,
    },
    WorkspaceRole.MEMBER: {
        "can_manage_workspace": False,
        "can_manage_members": False,
        "can_manage_billing": False,
        "can_create_content": True,
        "can_edit_all_content": False,  # Only own content
        "can_delete_all_content": False,  # Only own content
        "can_share_content": True,
        "can_export_data": True,
        "can_manage_connections": False,
        "can_view_audit_logs": False,
    },
    WorkspaceRole.VIEWER: {
        "can_manage_workspace": False,
        "can_manage_members": False,
        "can_manage_billing": False,
        "can_create_content": False,
        "can_edit_all_content": False,
        "can_delete_all_content": False,
        "can_share_content": False,
        "can_export_data": False,  # Configurable via workspace settings
        "can_manage_connections": False,
        "can_view_audit_logs": False,
    },
}


def get_role_permissions(role: WorkspaceRole) -> dict[str, bool]:
    """Get default permissions for a role"""
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[WorkspaceRole.VIEWER])


def can_perform_action(role: WorkspaceRole, action: str, custom_permissions: dict = None) -> bool:
    """Check if a role can perform a specific action"""
    # Check custom permissions first
    if custom_permissions and action in custom_permissions:
        return custom_permissions[action]

    # Fall back to role defaults
    permissions = get_role_permissions(role)
    return permissions.get(action, False)
