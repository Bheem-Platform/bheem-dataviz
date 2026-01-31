"""
Workspace Management Schemas

Pydantic schemas for multi-tenant workspace management, member management,
invitations, and workspace settings.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import datetime


# Enums

class WorkspaceStatus(str, Enum):
    """Workspace status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"
    DELETED = "deleted"


class WorkspacePlan(str, Enum):
    """Workspace subscription plan"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class MemberRole(str, Enum):
    """Member role within workspace"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"


class MemberStatus(str, Enum):
    """Member status"""
    ACTIVE = "active"
    INVITED = "invited"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class InvitationStatus(str, Enum):
    """Invitation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ResourceType(str, Enum):
    """Types of workspace resources"""
    DASHBOARD = "dashboard"
    CHART = "chart"
    CONNECTION = "connection"
    DATASET = "dataset"
    TRANSFORM = "transform"
    SEMANTIC_MODEL = "semantic_model"
    QUERY = "query"
    KPI = "kpi"
    REPORT = "report"


# Workspace Models

class WorkspaceCreate(BaseModel):
    """Create a new workspace"""
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    plan: WorkspacePlan = WorkspacePlan.FREE
    settings: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Workspace(BaseModel):
    """Workspace model"""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    status: WorkspaceStatus
    plan: WorkspacePlan
    owner_id: str
    member_count: int = 0
    dashboard_count: int = 0
    connection_count: int = 0
    storage_used_mb: float = 0
    settings: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    trial_ends_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkspaceUpdate(BaseModel):
    """Update workspace fields"""
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None


class WorkspaceSettings(BaseModel):
    """Workspace settings"""
    workspace_id: str
    allow_public_dashboards: bool = True
    allow_public_links: bool = True
    require_2fa: bool = False
    default_member_role: MemberRole = MemberRole.VIEWER
    allowed_email_domains: list[str] = Field(default_factory=list)
    ip_whitelist: list[str] = Field(default_factory=list)
    session_timeout_minutes: int = 480  # 8 hours
    password_policy: dict[str, Any] = Field(default_factory=dict)
    branding: dict[str, Any] = Field(default_factory=dict)
    notification_settings: dict[str, Any] = Field(default_factory=dict)
    data_retention_days: int = 365
    max_connections: int = 10
    max_dashboards: int = 50
    max_members: int = 10
    features_enabled: list[str] = Field(default_factory=list)


class WorkspaceSettingsUpdate(BaseModel):
    """Update workspace settings"""
    allow_public_dashboards: Optional[bool] = None
    allow_public_links: Optional[bool] = None
    require_2fa: Optional[bool] = None
    default_member_role: Optional[MemberRole] = None
    allowed_email_domains: Optional[list[str]] = None
    ip_whitelist: Optional[list[str]] = None
    session_timeout_minutes: Optional[int] = None
    password_policy: Optional[dict[str, Any]] = None
    branding: Optional[dict[str, Any]] = None
    notification_settings: Optional[dict[str, Any]] = None
    data_retention_days: Optional[int] = None


# Member Models

class WorkspaceMemberCreate(BaseModel):
    """Add member to workspace"""
    user_id: str
    role: MemberRole = MemberRole.VIEWER
    permissions: dict[str, bool] = Field(default_factory=dict)


class WorkspaceMember(BaseModel):
    """Workspace member"""
    id: str
    workspace_id: str
    user_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    role: MemberRole
    status: MemberStatus
    permissions: dict[str, bool] = Field(default_factory=dict)
    last_active_at: Optional[datetime] = None
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[str] = None


class WorkspaceMemberUpdate(BaseModel):
    """Update member fields"""
    role: Optional[MemberRole] = None
    permissions: Optional[dict[str, bool]] = None
    status: Optional[MemberStatus] = None


# Invitation Models

class InvitationCreate(BaseModel):
    """Create invitation"""
    email: EmailStr
    role: MemberRole = MemberRole.VIEWER
    message: Optional[str] = None
    expires_in_days: int = 7


class Invitation(BaseModel):
    """Workspace invitation"""
    id: str
    workspace_id: str
    workspace_name: str
    email: str
    role: MemberRole
    status: InvitationStatus
    message: Optional[str] = None
    token: str
    invited_by_id: str
    invited_by_name: str
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    declined_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BulkInvitationCreate(BaseModel):
    """Bulk invitation creation"""
    emails: list[EmailStr]
    role: MemberRole = MemberRole.VIEWER
    message: Optional[str] = None
    expires_in_days: int = 7


class InvitationResponse(BaseModel):
    """Response for invitation action"""
    accept: bool
    user_id: Optional[str] = None  # For existing users


# Workspace Quota Models

class WorkspaceQuota(BaseModel):
    """Workspace resource quotas"""
    workspace_id: str
    plan: WorkspacePlan
    # Member limits
    max_members: int
    current_members: int
    max_guests: int
    current_guests: int
    # Resource limits
    max_connections: int
    current_connections: int
    max_dashboards: int
    current_dashboards: int
    max_charts: int
    current_charts: int
    max_datasets: int
    current_datasets: int
    # Storage limits
    max_storage_mb: int
    current_storage_mb: float
    # API limits
    max_api_calls_per_day: int
    current_api_calls_today: int
    max_query_execution_minutes: int
    current_query_minutes_today: float
    # Feature limits
    max_scheduled_reports: int
    current_scheduled_reports: int
    max_alerts: int
    current_alerts: int


class QuotaUsage(BaseModel):
    """Real-time quota usage"""
    workspace_id: str
    resource_type: str
    limit: int
    used: int
    remaining: int
    percent_used: float


# Access Control Models

class ResourcePermission(BaseModel):
    """Resource-level permission"""
    resource_type: ResourceType
    resource_id: str
    member_id: str
    can_view: bool = True
    can_edit: bool = False
    can_delete: bool = False
    can_share: bool = False
    can_export: bool = True


class RolePermissions(BaseModel):
    """Permissions for a role"""
    role: MemberRole
    # Workspace permissions
    can_manage_workspace: bool = False
    can_manage_members: bool = False
    can_manage_billing: bool = False
    can_manage_settings: bool = False
    # Resource permissions
    can_create_connections: bool = False
    can_create_dashboards: bool = True
    can_create_charts: bool = True
    can_create_datasets: bool = False
    can_execute_queries: bool = True
    can_export_data: bool = True
    can_share_resources: bool = True
    can_create_public_links: bool = False
    # Feature permissions
    can_use_ai_features: bool = True
    can_create_alerts: bool = False
    can_schedule_reports: bool = False
    can_use_api: bool = False


# Team Models

class Team(BaseModel):
    """Team within workspace"""
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    member_ids: list[str] = Field(default_factory=list)
    permissions: dict[str, bool] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TeamCreate(BaseModel):
    """Create team"""
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    member_ids: list[str] = Field(default_factory=list)


class TeamUpdate(BaseModel):
    """Update team"""
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    member_ids: Optional[list[str]] = None
    permissions: Optional[dict[str, bool]] = None


# Activity Models

class WorkspaceActivity(BaseModel):
    """Workspace activity log"""
    id: str
    workspace_id: str
    user_id: str
    user_name: str
    action: str
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Response Models

class WorkspaceListResponse(BaseModel):
    """List workspaces response"""
    workspaces: list[Workspace]
    total: int


class WorkspaceMemberListResponse(BaseModel):
    """List members response"""
    members: list[WorkspaceMember]
    total: int


class InvitationListResponse(BaseModel):
    """List invitations response"""
    invitations: list[Invitation]
    total: int


class TeamListResponse(BaseModel):
    """List teams response"""
    teams: list[Team]
    total: int


class WorkspaceActivityListResponse(BaseModel):
    """List activity response"""
    activities: list[WorkspaceActivity]
    total: int


class QuotaUsageListResponse(BaseModel):
    """List quota usage response"""
    quotas: list[QuotaUsage]


# Summary Models

class WorkspaceSummary(BaseModel):
    """Workspace summary for dashboard"""
    workspace_id: str
    name: str
    plan: WorkspacePlan
    status: WorkspaceStatus
    member_count: int
    dashboard_count: int
    connection_count: int
    chart_count: int
    storage_used_mb: float
    storage_limit_mb: int
    api_calls_today: int
    active_users_today: int
    recent_activities: list[WorkspaceActivity]


class UserWorkspaces(BaseModel):
    """User's workspaces"""
    owned: list[Workspace]
    member_of: list[Workspace]
    pending_invitations: list[Invitation]


# Constants

PLAN_LIMITS = {
    WorkspacePlan.FREE: {
        "max_members": 3,
        "max_guests": 0,
        "max_connections": 2,
        "max_dashboards": 5,
        "max_charts": 20,
        "max_datasets": 5,
        "max_storage_mb": 100,
        "max_api_calls_per_day": 100,
        "max_query_execution_minutes": 10,
        "max_scheduled_reports": 0,
        "max_alerts": 0,
    },
    WorkspacePlan.STARTER: {
        "max_members": 5,
        "max_guests": 5,
        "max_connections": 5,
        "max_dashboards": 20,
        "max_charts": 100,
        "max_datasets": 20,
        "max_storage_mb": 500,
        "max_api_calls_per_day": 1000,
        "max_query_execution_minutes": 60,
        "max_scheduled_reports": 5,
        "max_alerts": 10,
    },
    WorkspacePlan.PRO: {
        "max_members": 25,
        "max_guests": 25,
        "max_connections": 20,
        "max_dashboards": 100,
        "max_charts": 500,
        "max_datasets": 100,
        "max_storage_mb": 5000,
        "max_api_calls_per_day": 10000,
        "max_query_execution_minutes": 300,
        "max_scheduled_reports": 25,
        "max_alerts": 50,
    },
    WorkspacePlan.BUSINESS: {
        "max_members": 100,
        "max_guests": 100,
        "max_connections": 50,
        "max_dashboards": 500,
        "max_charts": 2500,
        "max_datasets": 500,
        "max_storage_mb": 25000,
        "max_api_calls_per_day": 100000,
        "max_query_execution_minutes": 1000,
        "max_scheduled_reports": 100,
        "max_alerts": 200,
    },
    WorkspacePlan.ENTERPRISE: {
        "max_members": -1,  # Unlimited
        "max_guests": -1,
        "max_connections": -1,
        "max_dashboards": -1,
        "max_charts": -1,
        "max_datasets": -1,
        "max_storage_mb": -1,
        "max_api_calls_per_day": -1,
        "max_query_execution_minutes": -1,
        "max_scheduled_reports": -1,
        "max_alerts": -1,
    },
}

ROLE_PERMISSIONS = {
    MemberRole.OWNER: RolePermissions(
        role=MemberRole.OWNER,
        can_manage_workspace=True,
        can_manage_members=True,
        can_manage_billing=True,
        can_manage_settings=True,
        can_create_connections=True,
        can_create_dashboards=True,
        can_create_charts=True,
        can_create_datasets=True,
        can_execute_queries=True,
        can_export_data=True,
        can_share_resources=True,
        can_create_public_links=True,
        can_use_ai_features=True,
        can_create_alerts=True,
        can_schedule_reports=True,
        can_use_api=True,
    ),
    MemberRole.ADMIN: RolePermissions(
        role=MemberRole.ADMIN,
        can_manage_workspace=False,
        can_manage_members=True,
        can_manage_billing=False,
        can_manage_settings=True,
        can_create_connections=True,
        can_create_dashboards=True,
        can_create_charts=True,
        can_create_datasets=True,
        can_execute_queries=True,
        can_export_data=True,
        can_share_resources=True,
        can_create_public_links=True,
        can_use_ai_features=True,
        can_create_alerts=True,
        can_schedule_reports=True,
        can_use_api=True,
    ),
    MemberRole.EDITOR: RolePermissions(
        role=MemberRole.EDITOR,
        can_manage_workspace=False,
        can_manage_members=False,
        can_manage_billing=False,
        can_manage_settings=False,
        can_create_connections=False,
        can_create_dashboards=True,
        can_create_charts=True,
        can_create_datasets=True,
        can_execute_queries=True,
        can_export_data=True,
        can_share_resources=True,
        can_create_public_links=False,
        can_use_ai_features=True,
        can_create_alerts=True,
        can_schedule_reports=True,
        can_use_api=False,
    ),
    MemberRole.VIEWER: RolePermissions(
        role=MemberRole.VIEWER,
        can_manage_workspace=False,
        can_manage_members=False,
        can_manage_billing=False,
        can_manage_settings=False,
        can_create_connections=False,
        can_create_dashboards=False,
        can_create_charts=False,
        can_create_datasets=False,
        can_execute_queries=True,
        can_export_data=True,
        can_share_resources=False,
        can_create_public_links=False,
        can_use_ai_features=True,
        can_create_alerts=False,
        can_schedule_reports=False,
        can_use_api=False,
    ),
    MemberRole.GUEST: RolePermissions(
        role=MemberRole.GUEST,
        can_manage_workspace=False,
        can_manage_members=False,
        can_manage_billing=False,
        can_manage_settings=False,
        can_create_connections=False,
        can_create_dashboards=False,
        can_create_charts=False,
        can_create_datasets=False,
        can_execute_queries=False,
        can_export_data=False,
        can_share_resources=False,
        can_create_public_links=False,
        can_use_ai_features=False,
        can_create_alerts=False,
        can_schedule_reports=False,
        can_use_api=False,
    ),
}


# Helper Functions

def get_plan_limits(plan: WorkspacePlan) -> dict[str, int]:
    """Get limits for a plan."""
    return PLAN_LIMITS.get(plan, PLAN_LIMITS[WorkspacePlan.FREE])


def get_role_permissions(role: MemberRole) -> RolePermissions:
    """Get permissions for a role."""
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[MemberRole.VIEWER])


def check_quota(quota: WorkspaceQuota, resource_type: str) -> bool:
    """Check if quota allows adding resource."""
    limits = {
        "members": (quota.max_members, quota.current_members),
        "guests": (quota.max_guests, quota.current_guests),
        "connections": (quota.max_connections, quota.current_connections),
        "dashboards": (quota.max_dashboards, quota.current_dashboards),
        "charts": (quota.max_charts, quota.current_charts),
        "datasets": (quota.max_datasets, quota.current_datasets),
        "storage": (quota.max_storage_mb, quota.current_storage_mb),
    }

    if resource_type not in limits:
        return True

    max_val, current = limits[resource_type]
    if max_val == -1:  # Unlimited
        return True

    return current < max_val


def calculate_quota_usage(max_val: int, current: float) -> QuotaUsage:
    """Calculate quota usage percentage."""
    if max_val == -1:
        return QuotaUsage(
            workspace_id="",
            resource_type="",
            limit=-1,
            used=int(current),
            remaining=-1,
            percent_used=0,
        )

    remaining = max_val - int(current)
    percent = (current / max_val * 100) if max_val > 0 else 0

    return QuotaUsage(
        workspace_id="",
        resource_type="",
        limit=max_val,
        used=int(current),
        remaining=remaining,
        percent_used=round(percent, 2),
    )
