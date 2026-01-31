"""
User & Role Management API Endpoints

REST API for user profiles, roles, permissions, sessions,
and administrative user management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.user_management import (
    User, UserCreate, UserUpdate, UserAdminUpdate, UserProfile,
    UserStatus, UserType, AuthProvider,
    UserPreferences, UserPreferencesUpdate,
    Role, RoleCreate, RoleUpdate, RoleAssignment, RoleAssignmentCreate,
    PermissionScope, UserPermissions,
    Session, SessionCreate, SessionInfo,
    MFASetup, MFAVerify, MFABackupCodes,
    PasswordChange, PasswordPolicy,
    AuditLogEntry, AuditAction, AuditLogQuery,
    UserListResponse, RoleListResponse, SessionListResponse, AuditLogResponse,
    PermissionListResponse, UserStatistics,
)
from app.services.user_management_service import user_management_service

router = APIRouter()


# User Management Endpoints

@router.post("/users", response_model=User, tags=["users"])
async def create_user(
    data: UserCreate,
    created_by: Optional[str] = Query(None, description="ID of user creating this account"),
):
    """Create a new user account."""
    try:
        return user_management_service.create_user(data, created_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users", response_model=UserListResponse, tags=["users"])
async def list_users(
    status: Optional[UserStatus] = None,
    user_type: Optional[UserType] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List users with optional filters."""
    return user_management_service.list_users(status, user_type, search, skip, limit)


@router.get("/users/{user_id}", response_model=User, tags=["users"])
async def get_user(user_id: str):
    """Get user by ID."""
    user = user_management_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/email/{email}", response_model=User, tags=["users"])
async def get_user_by_email(email: str):
    """Get user by email."""
    user = user_management_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=User, tags=["users"])
async def update_user(user_id: str, data: UserUpdate):
    """Update user profile."""
    user = user_management_service.update_user(user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}/admin", response_model=User, tags=["users"])
async def admin_update_user(
    user_id: str,
    data: UserAdminUpdate,
    admin_id: str = Query(..., description="Admin user ID"),
):
    """Admin update user (can change status, type, etc.)."""
    user = user_management_service.admin_update_user(user_id, data, admin_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{user_id}", tags=["users"])
async def delete_user(
    user_id: str,
    deleted_by: str = Query(..., description="User performing deletion"),
):
    """Soft delete user account."""
    if not user_management_service.delete_user(user_id, deleted_by):
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted", "user_id": user_id}


@router.get("/users/{user_id}/profile", response_model=UserProfile, tags=["users"])
async def get_user_profile(user_id: str):
    """Get public user profile."""
    profile = user_management_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


# User Preferences

@router.get("/users/{user_id}/preferences", response_model=UserPreferences, tags=["preferences"])
async def get_user_preferences(user_id: str):
    """Get user preferences."""
    prefs = user_management_service.get_preferences(user_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="User not found")
    return prefs


@router.put("/users/{user_id}/preferences", response_model=UserPreferences, tags=["preferences"])
async def update_user_preferences(user_id: str, data: UserPreferencesUpdate):
    """Update user preferences."""
    prefs = user_management_service.update_preferences(user_id, data)
    if not prefs:
        raise HTTPException(status_code=404, detail="User not found")
    return prefs


# Password Management

@router.post("/users/{user_id}/password/change", tags=["password"])
async def change_password(
    user_id: str,
    data: PasswordChange,
    ip_address: Optional[str] = Query(None),
):
    """Change user password."""
    try:
        if user_management_service.change_password(user_id, data, ip_address):
            return {"status": "success", "message": "Password changed successfully"}
        raise HTTPException(status_code=400, detail="Failed to change password")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/password/policy", response_model=PasswordPolicy, tags=["password"])
async def get_password_policy():
    """Get current password policy."""
    return user_management_service.password_policy


# MFA Management

@router.post("/users/{user_id}/mfa/setup", response_model=MFASetup, tags=["mfa"])
async def setup_mfa(user_id: str):
    """Setup MFA for user (generates secret and QR code)."""
    setup = user_management_service.setup_mfa(user_id)
    if not setup:
        raise HTTPException(status_code=404, detail="User not found")
    return setup


@router.post("/users/{user_id}/mfa/enable", tags=["mfa"])
async def enable_mfa(user_id: str, data: MFAVerify):
    """Enable MFA after verification."""
    if user_management_service.enable_mfa(user_id, data.code):
        return {"status": "enabled", "message": "MFA enabled successfully"}
    raise HTTPException(status_code=400, detail="Invalid verification code")


@router.post("/users/{user_id}/mfa/disable", tags=["mfa"])
async def disable_mfa(user_id: str, data: MFAVerify):
    """Disable MFA."""
    if user_management_service.disable_mfa(user_id, data.code):
        return {"status": "disabled", "message": "MFA disabled successfully"}
    raise HTTPException(status_code=400, detail="Invalid verification code")


@router.post("/users/{user_id}/mfa/verify", tags=["mfa"])
async def verify_mfa(user_id: str, data: MFAVerify):
    """Verify MFA code."""
    if user_management_service.verify_mfa(user_id, data.code):
        return {"valid": True}
    return {"valid": False}


@router.post("/users/{user_id}/mfa/backup-codes", response_model=MFABackupCodes, tags=["mfa"])
async def regenerate_backup_codes(user_id: str):
    """Regenerate MFA backup codes."""
    codes = user_management_service.regenerate_backup_codes(user_id)
    if not codes:
        raise HTTPException(status_code=400, detail="MFA not enabled for user")
    return codes


# Role Management

@router.post("/roles", response_model=Role, tags=["roles"])
async def create_role(
    data: RoleCreate,
    created_by: str = Query(..., description="User creating the role"),
):
    """Create a custom role."""
    return user_management_service.create_role(data, created_by)


@router.get("/roles", response_model=RoleListResponse, tags=["roles"])
async def list_roles(
    scope: Optional[PermissionScope] = None,
    workspace_id: Optional[str] = None,
    include_system: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List roles."""
    return user_management_service.list_roles(scope, workspace_id, include_system, skip, limit)


@router.get("/roles/{role_id}", response_model=Role, tags=["roles"])
async def get_role(role_id: str):
    """Get role by ID."""
    role = user_management_service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch("/roles/{role_id}", response_model=Role, tags=["roles"])
async def update_role(role_id: str, data: RoleUpdate):
    """Update role (cannot update system roles)."""
    role = user_management_service.update_role(role_id, data)
    if not role:
        raise HTTPException(status_code=400, detail="Role not found or is a system role")
    return role


@router.delete("/roles/{role_id}", tags=["roles"])
async def delete_role(role_id: str):
    """Delete role (cannot delete system roles)."""
    if not user_management_service.delete_role(role_id):
        raise HTTPException(status_code=400, detail="Role not found or is a system role")
    return {"status": "deleted", "role_id": role_id}


# Role Assignment

@router.post("/roles/assign", response_model=RoleAssignment, tags=["roles"])
async def assign_role(
    data: RoleAssignmentCreate,
    assigned_by: str = Query(..., description="User assigning the role"),
):
    """Assign role to user."""
    assignment = user_management_service.assign_role(data, assigned_by)
    if not assignment:
        raise HTTPException(status_code=400, detail="User or role not found")
    return assignment


@router.delete("/roles/assignments/{assignment_id}", tags=["roles"])
async def revoke_role(
    assignment_id: str,
    revoked_by: str = Query(..., description="User revoking the role"),
):
    """Revoke role assignment."""
    if not user_management_service.revoke_role(assignment_id, revoked_by):
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"status": "revoked", "assignment_id": assignment_id}


@router.get("/users/{user_id}/roles", response_model=list[RoleAssignment], tags=["roles"])
async def get_user_roles(
    user_id: str,
    workspace_id: Optional[str] = None,
):
    """Get roles assigned to user."""
    return user_management_service.get_user_roles(user_id, workspace_id)


# Permissions

@router.get("/permissions", response_model=PermissionListResponse, tags=["permissions"])
async def get_all_permissions():
    """Get all available permissions."""
    return user_management_service.get_all_permissions()


@router.get("/users/{user_id}/permissions", response_model=UserPermissions, tags=["permissions"])
async def get_user_permissions(
    user_id: str,
    workspace_id: Optional[str] = None,
):
    """Get all permissions for a user."""
    return user_management_service.get_user_permissions(user_id, workspace_id)


@router.get("/users/{user_id}/permissions/check", tags=["permissions"])
async def check_user_permission(
    user_id: str,
    permission: str = Query(..., description="Permission to check"),
    workspace_id: Optional[str] = None,
):
    """Check if user has specific permission."""
    has_perm = user_management_service.check_permission(user_id, permission, workspace_id)
    return {"user_id": user_id, "permission": permission, "allowed": has_perm}


# Session Management

@router.post("/sessions", response_model=Session, tags=["sessions"])
async def create_session(
    data: SessionCreate,
    expires_in_hours: int = Query(24, ge=1, le=720),
):
    """Create user session."""
    return user_management_service.create_session(data, expires_in_hours)


@router.get("/sessions/{session_id}", response_model=Session, tags=["sessions"])
async def get_session(session_id: str):
    """Get session by ID."""
    session = user_management_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return session


@router.post("/sessions/{session_id}/activity", tags=["sessions"])
async def update_session_activity(session_id: str):
    """Update session last activity timestamp."""
    if not user_management_service.update_session_activity(session_id):
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    return {"status": "updated"}


@router.post("/sessions/{session_id}/revoke", tags=["sessions"])
async def revoke_session(
    session_id: str,
    reason: Optional[str] = Query(None),
):
    """Revoke session."""
    if not user_management_service.revoke_session(session_id, reason):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "revoked"}


@router.get("/users/{user_id}/sessions", response_model=SessionListResponse, tags=["sessions"])
async def get_user_sessions(
    user_id: str,
    current_session_id: Optional[str] = Query(None),
):
    """Get all sessions for a user."""
    return user_management_service.get_user_sessions(user_id, current_session_id)


@router.post("/users/{user_id}/sessions/revoke-all", tags=["sessions"])
async def revoke_all_user_sessions(
    user_id: str,
    except_session_id: Optional[str] = Query(None, description="Session to keep active"),
):
    """Revoke all sessions for a user."""
    count = user_management_service.revoke_all_sessions(user_id, except_session_id)
    return {"status": "revoked", "count": count}


# Audit Logs

@router.get("/audit", response_model=AuditLogResponse, tags=["audit"])
async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    success: Optional[bool] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Query audit logs."""
    from datetime import datetime

    query = AuditLogQuery(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        success=success,
        start_date=datetime.fromisoformat(start_date) if start_date else None,
        end_date=datetime.fromisoformat(end_date) if end_date else None,
        skip=skip,
        limit=limit,
    )
    return user_management_service.query_audit_logs(query)


@router.get("/users/{user_id}/audit", response_model=AuditLogResponse, tags=["audit"])
async def get_user_audit_logs(
    user_id: str,
    action: Optional[AuditAction] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get audit logs for a specific user."""
    query = AuditLogQuery(user_id=user_id, action=action, skip=skip, limit=limit)
    return user_management_service.query_audit_logs(query)


# Statistics

@router.get("/statistics", response_model=UserStatistics, tags=["statistics"])
async def get_user_statistics():
    """Get user statistics."""
    return user_management_service.get_statistics()


# Login Tracking

@router.post("/auth/login-attempt", tags=["auth"])
async def log_login_attempt(
    email: str = Query(...),
    success: bool = Query(...),
    ip_address: Optional[str] = Query(None),
    user_agent: Optional[str] = Query(None),
    error_message: Optional[str] = Query(None),
):
    """Log a login attempt (for external auth systems)."""
    user_management_service.log_login_attempt(email, success, ip_address, user_agent, error_message)
    return {"logged": True}
