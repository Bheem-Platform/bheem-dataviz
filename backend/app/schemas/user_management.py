"""
User & Role Management Schemas

Pydantic schemas for user profiles, roles, permissions, sessions,
and administrative user management.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import datetime


# Enums

class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    LOCKED = "locked"
    DELETED = "deleted"


class UserType(str, Enum):
    """Type of user account"""
    REGULAR = "regular"
    ADMIN = "admin"
    SERVICE = "service"
    API = "api"
    SYSTEM = "system"


class AuthProvider(str, Enum):
    """Authentication provider"""
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    OKTA = "okta"
    SAML = "saml"
    LDAP = "ldap"


class SessionStatus(str, Enum):
    """Session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    LOGGED_OUT = "logged_out"


class PermissionScope(str, Enum):
    """Permission scope"""
    GLOBAL = "global"
    WORKSPACE = "workspace"
    RESOURCE = "resource"


class AuditAction(str, Enum):
    """Audit action types"""
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    PROFILE_UPDATE = "profile_update"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    SESSION_CREATED = "session_created"
    SESSION_REVOKED = "session_revoked"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    PERMISSION_CHANGED = "permission_changed"


# User Models

class UserCreate(BaseModel):
    """Create a new user"""
    email: EmailStr
    password: Optional[str] = None  # Optional if using OAuth
    name: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    user_type: UserType = UserType.REGULAR
    auth_provider: AuthProvider = AuthProvider.LOCAL
    auth_provider_id: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "UTC"
    locale: str = "en"
    metadata: dict[str, Any] = Field(default_factory=dict)


class User(BaseModel):
    """User model"""
    id: str
    email: str
    name: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    user_type: UserType
    status: UserStatus
    auth_provider: AuthProvider
    auth_provider_id: Optional[str] = None
    phone: Optional[str] = None
    timezone: str
    locale: str
    email_verified: bool = False
    phone_verified: bool = False
    mfa_enabled: bool = False
    mfa_method: Optional[str] = None
    last_login_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    login_count: int = 0
    failed_login_count: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserUpdate(BaseModel):
    """Update user fields"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class UserAdminUpdate(BaseModel):
    """Admin user update"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    user_type: Optional[UserType] = None
    status: Optional[UserStatus] = None
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None
    mfa_enabled: Optional[bool] = None
    metadata: Optional[dict[str, Any]] = None


class UserProfile(BaseModel):
    """User public profile"""
    id: str
    email: str
    name: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str
    locale: str
    created_at: datetime


class UserPreferences(BaseModel):
    """User preferences"""
    user_id: str
    theme: str = "system"  # light, dark, system
    language: str = "en"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "HH:mm"
    number_format: str = "1,234.56"
    first_day_of_week: int = 0  # 0 = Sunday, 1 = Monday
    default_workspace_id: Optional[str] = None
    notifications: dict[str, bool] = Field(default_factory=dict)
    email_notifications: dict[str, bool] = Field(default_factory=dict)
    dashboard_settings: dict[str, Any] = Field(default_factory=dict)
    chart_defaults: dict[str, Any] = Field(default_factory=dict)


class UserPreferencesUpdate(BaseModel):
    """Update user preferences"""
    theme: Optional[str] = None
    language: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    number_format: Optional[str] = None
    first_day_of_week: Optional[int] = None
    default_workspace_id: Optional[str] = None
    notifications: Optional[dict[str, bool]] = None
    email_notifications: Optional[dict[str, bool]] = None
    dashboard_settings: Optional[dict[str, Any]] = None
    chart_defaults: Optional[dict[str, Any]] = None


# Role Models

class RoleCreate(BaseModel):
    """Create a custom role"""
    name: str
    description: Optional[str] = None
    scope: PermissionScope = PermissionScope.WORKSPACE
    permissions: list[str] = Field(default_factory=list)
    is_system: bool = False
    workspace_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Role(BaseModel):
    """Role model"""
    id: str
    name: str
    description: Optional[str] = None
    scope: PermissionScope
    permissions: list[str]
    is_system: bool
    is_default: bool = False
    workspace_id: Optional[str] = None
    user_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RoleUpdate(BaseModel):
    """Update role"""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class RoleAssignment(BaseModel):
    """Role assignment to user"""
    id: str
    user_id: str
    role_id: str
    role_name: str
    workspace_id: Optional[str] = None  # None = global
    assigned_by: str
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class RoleAssignmentCreate(BaseModel):
    """Assign role to user"""
    user_id: str
    role_id: str
    workspace_id: Optional[str] = None
    expires_at: Optional[datetime] = None


# Permission Models

class Permission(BaseModel):
    """Permission definition"""
    id: str
    name: str
    code: str  # e.g., "dashboard:create", "connection:delete"
    description: Optional[str] = None
    category: str  # e.g., "dashboards", "connections", "admin"
    scope: PermissionScope
    is_sensitive: bool = False  # Requires additional confirmation


class PermissionGroup(BaseModel):
    """Group of related permissions"""
    id: str
    name: str
    description: Optional[str] = None
    category: str
    permissions: list[Permission]


class UserPermissions(BaseModel):
    """All permissions for a user"""
    user_id: str
    global_permissions: list[str]
    workspace_permissions: dict[str, list[str]]  # workspace_id -> permissions
    effective_permissions: list[str]  # Combined/resolved permissions


# Session Models

class SessionCreate(BaseModel):
    """Create session"""
    user_id: str
    device_info: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class Session(BaseModel):
    """User session"""
    id: str
    user_id: str
    status: SessionStatus
    device_info: dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None
    is_current: bool = False
    last_activity_at: datetime
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None


class SessionInfo(BaseModel):
    """Session info for display"""
    id: str
    device_type: str  # desktop, mobile, tablet
    browser: Optional[str] = None
    os: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    is_current: bool
    last_activity_at: datetime
    created_at: datetime


# MFA Models

class MFASetup(BaseModel):
    """MFA setup response"""
    secret: str
    qr_code_url: str
    backup_codes: list[str]


class MFAVerify(BaseModel):
    """Verify MFA code"""
    code: str


class MFABackupCodes(BaseModel):
    """Backup codes"""
    codes: list[str]
    generated_at: datetime


# Password Models

class PasswordChange(BaseModel):
    """Change password"""
    current_password: str
    new_password: str


class PasswordReset(BaseModel):
    """Reset password"""
    token: str
    new_password: str


class PasswordResetRequest(BaseModel):
    """Request password reset"""
    email: EmailStr


class PasswordPolicy(BaseModel):
    """Password policy"""
    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    disallow_common: bool = True
    disallow_username: bool = True
    max_age_days: int = 90  # 0 = never expires
    history_count: int = 5  # Can't reuse last N passwords
    lockout_threshold: int = 5  # Lock after N failed attempts
    lockout_duration_minutes: int = 30


# Audit Models

class AuditLogEntry(BaseModel):
    """Audit log entry"""
    id: str
    user_id: str
    user_email: str
    action: AuditAction
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLogQuery(BaseModel):
    """Query audit logs"""
    user_id: Optional[str] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[str] = None
    success: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 50


# Response Models

class UserListResponse(BaseModel):
    """List users response"""
    users: list[User]
    total: int


class RoleListResponse(BaseModel):
    """List roles response"""
    roles: list[Role]
    total: int


class SessionListResponse(BaseModel):
    """List sessions response"""
    sessions: list[SessionInfo]
    total: int


class AuditLogResponse(BaseModel):
    """Audit log response"""
    entries: list[AuditLogEntry]
    total: int


class PermissionListResponse(BaseModel):
    """List permissions response"""
    permissions: list[Permission]
    groups: list[PermissionGroup]


# Auth Response Models

class AuthTokens(BaseModel):
    """Authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    """Authentication response"""
    user: User
    tokens: AuthTokens
    mfa_required: bool = False
    mfa_token: Optional[str] = None  # Temporary token for MFA flow


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    expires_in: int


# Statistics Models

class UserStatistics(BaseModel):
    """User statistics"""
    total_users: int
    active_users: int
    inactive_users: int
    locked_users: int
    pending_verification: int
    users_by_type: dict[str, int]
    users_by_provider: dict[str, int]
    mfa_enabled_count: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    active_sessions: int


# Constants

SYSTEM_ROLES = {
    "super_admin": {
        "name": "Super Admin",
        "description": "Full system access",
        "permissions": ["*"],  # All permissions
    },
    "admin": {
        "name": "Admin",
        "description": "Administrative access",
        "permissions": [
            "users:read", "users:create", "users:update",
            "roles:read", "roles:assign",
            "workspaces:manage",
            "audit:read",
        ],
    },
    "user": {
        "name": "User",
        "description": "Standard user access",
        "permissions": [
            "profile:read", "profile:update",
            "dashboards:create", "dashboards:read", "dashboards:update", "dashboards:delete",
            "charts:create", "charts:read", "charts:update", "charts:delete",
            "queries:execute",
        ],
    },
    "viewer": {
        "name": "Viewer",
        "description": "Read-only access",
        "permissions": [
            "profile:read",
            "dashboards:read",
            "charts:read",
        ],
    },
}

PERMISSION_CATEGORIES = {
    "profile": ["profile:read", "profile:update"],
    "users": ["users:read", "users:create", "users:update", "users:delete", "users:impersonate"],
    "roles": ["roles:read", "roles:create", "roles:update", "roles:delete", "roles:assign"],
    "workspaces": ["workspaces:read", "workspaces:create", "workspaces:update", "workspaces:delete", "workspaces:manage"],
    "dashboards": ["dashboards:read", "dashboards:create", "dashboards:update", "dashboards:delete", "dashboards:share"],
    "charts": ["charts:read", "charts:create", "charts:update", "charts:delete"],
    "connections": ["connections:read", "connections:create", "connections:update", "connections:delete", "connections:test"],
    "datasets": ["datasets:read", "datasets:create", "datasets:update", "datasets:delete"],
    "queries": ["queries:execute", "queries:read", "queries:create", "queries:update", "queries:delete"],
    "reports": ["reports:read", "reports:create", "reports:schedule", "reports:export"],
    "admin": ["admin:access", "admin:settings", "audit:read", "system:manage"],
}

ALL_PERMISSIONS = [perm for perms in PERMISSION_CATEGORIES.values() for perm in perms]


# Helper Functions

def has_permission(user_permissions: list[str], required: str) -> bool:
    """Check if user has required permission."""
    if "*" in user_permissions:
        return True
    if required in user_permissions:
        return True
    # Check wildcard permissions (e.g., "dashboards:*")
    category = required.split(":")[0]
    if f"{category}:*" in user_permissions:
        return True
    return False


def validate_password(password: str, policy: PasswordPolicy) -> tuple[bool, list[str]]:
    """Validate password against policy. Returns (valid, errors)."""
    errors = []

    if len(password) < policy.min_length:
        errors.append(f"Password must be at least {policy.min_length} characters")
    if len(password) > policy.max_length:
        errors.append(f"Password must be at most {policy.max_length} characters")
    if policy.require_uppercase and not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    if policy.require_lowercase and not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    if policy.require_numbers and not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    if policy.require_special_chars and not any(c in policy.special_chars for c in password):
        errors.append(f"Password must contain at least one special character ({policy.special_chars})")

    return len(errors) == 0, errors


def get_role_permissions(role_name: str) -> list[str]:
    """Get permissions for a system role."""
    role = SYSTEM_ROLES.get(role_name)
    if role:
        return role["permissions"]
    return []


def merge_permissions(*permission_lists: list[str]) -> list[str]:
    """Merge multiple permission lists, removing duplicates."""
    all_perms = set()
    for perms in permission_lists:
        all_perms.update(perms)
    return list(all_perms)
