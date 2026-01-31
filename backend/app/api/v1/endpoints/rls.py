"""
Row-Level Security API Endpoints

Provides endpoints for managing RLS policies and evaluating access.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.rls import (
    SecurityRole,
    RLSPolicy,
    RLSConditionGroup,
    RLSCondition,
    UserRoleMapping,
    UserSecurityContext,
    ObjectPermission,
    ObjectPermissions,
    RLSFilterRequest,
    RLSFilterResponse,
    RLSConfiguration,
    PermissionLevel,
    RLS_POLICY_TEMPLATES,
)
from app.services.rls_service import get_rls_service

router = APIRouter()

# In-memory storage for demo (in production, use database)
_roles: dict[str, SecurityRole] = {}
_policies: dict[str, RLSPolicy] = {}
_user_role_mappings: dict[str, UserRoleMapping] = {}
_object_permissions: dict[str, list[ObjectPermission]] = {}
_config = RLSConfiguration()


# Security Roles

@router.get("/roles", response_model=list[SecurityRole])
async def list_roles(
    current_user: dict = Depends(get_current_user),
):
    """List all security roles"""
    return list(_roles.values())


@router.post("/roles", response_model=SecurityRole)
async def create_role(
    role: SecurityRole,
    current_user: dict = Depends(get_current_user),
):
    """Create a new security role"""
    if not role.id:
        role.id = str(uuid.uuid4())

    role.created_at = datetime.utcnow().isoformat()
    role.updated_at = role.created_at

    _roles[role.id] = role
    return role


@router.get("/roles/{role_id}", response_model=SecurityRole)
async def get_role(
    role_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific role"""
    if role_id not in _roles:
        raise HTTPException(status_code=404, detail="Role not found")
    return _roles[role_id]


@router.put("/roles/{role_id}", response_model=SecurityRole)
async def update_role(
    role_id: str,
    role: SecurityRole,
    current_user: dict = Depends(get_current_user),
):
    """Update a role"""
    if role_id not in _roles:
        raise HTTPException(status_code=404, detail="Role not found")

    role.id = role_id
    role.updated_at = datetime.utcnow().isoformat()
    role.created_at = _roles[role_id].created_at

    _roles[role_id] = role
    return role


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a role"""
    if role_id not in _roles:
        raise HTTPException(status_code=404, detail="Role not found")

    del _roles[role_id]
    return {"success": True, "message": "Role deleted"}


# RLS Policies

@router.get("/policies", response_model=list[RLSPolicy])
async def list_policies(
    table_name: str = None,
    schema_name: str = None,
    connection_id: str = None,
    current_user: dict = Depends(get_current_user),
):
    """List RLS policies with optional filtering"""
    policies = list(_policies.values())

    if table_name:
        policies = [p for p in policies if p.table_name == table_name or p.table_name is None]
    if schema_name:
        policies = [p for p in policies if p.schema_name == schema_name or p.schema_name is None]
    if connection_id:
        policies = [p for p in policies if p.connection_id == connection_id or p.connection_id is None]

    return policies


@router.post("/policies", response_model=RLSPolicy)
async def create_policy(
    policy: RLSPolicy,
    current_user: dict = Depends(get_current_user),
):
    """Create a new RLS policy"""
    if not policy.id:
        policy.id = str(uuid.uuid4())

    policy.created_at = datetime.utcnow().isoformat()
    policy.updated_at = policy.created_at
    policy.created_by = current_user.get("user_id")

    _policies[policy.id] = policy
    return policy


@router.get("/policies/{policy_id}", response_model=RLSPolicy)
async def get_policy(
    policy_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific policy"""
    if policy_id not in _policies:
        raise HTTPException(status_code=404, detail="Policy not found")
    return _policies[policy_id]


@router.put("/policies/{policy_id}", response_model=RLSPolicy)
async def update_policy(
    policy_id: str,
    policy: RLSPolicy,
    current_user: dict = Depends(get_current_user),
):
    """Update a policy"""
    if policy_id not in _policies:
        raise HTTPException(status_code=404, detail="Policy not found")

    policy.id = policy_id
    policy.updated_at = datetime.utcnow().isoformat()
    policy.created_at = _policies[policy_id].created_at
    policy.created_by = _policies[policy_id].created_by

    _policies[policy_id] = policy
    return policy


@router.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a policy"""
    if policy_id not in _policies:
        raise HTTPException(status_code=404, detail="Policy not found")

    del _policies[policy_id]
    return {"success": True, "message": "Policy deleted"}


@router.put("/policies/{policy_id}/toggle")
async def toggle_policy(
    policy_id: str,
    enabled: bool,
    current_user: dict = Depends(get_current_user),
):
    """Enable or disable a policy"""
    if policy_id not in _policies:
        raise HTTPException(status_code=404, detail="Policy not found")

    _policies[policy_id].enabled = enabled
    _policies[policy_id].updated_at = datetime.utcnow().isoformat()

    return {"success": True, "enabled": enabled}


# User Role Mappings

@router.get("/user-roles/{user_id}", response_model=UserRoleMapping)
async def get_user_roles(
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get role assignments for a user"""
    if user_id not in _user_role_mappings:
        return UserRoleMapping(user_id=user_id, role_ids=[])
    return _user_role_mappings[user_id]


@router.put("/user-roles/{user_id}")
async def set_user_roles(
    user_id: str,
    mapping: UserRoleMapping,
    current_user: dict = Depends(get_current_user),
):
    """Set role assignments for a user"""
    mapping.user_id = user_id
    _user_role_mappings[user_id] = mapping
    return {"success": True, "message": "Roles assigned"}


# Object Permissions

@router.get("/permissions/{object_type}/{object_id}", response_model=ObjectPermissions)
async def get_object_permissions(
    object_type: str,
    object_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get permissions for an object"""
    key = f"{object_type}:{object_id}"
    permissions = _object_permissions.get(key, [])

    # Determine effective permission for current user
    user_id = current_user.get("user_id")
    user_roles = current_user.get("roles", [])

    effective = PermissionLevel.NONE
    permission_hierarchy = {
        PermissionLevel.NONE: 0,
        PermissionLevel.VIEW: 1,
        PermissionLevel.EDIT: 2,
        PermissionLevel.ADMIN: 3,
    }

    for perm in permissions:
        if perm.user_id == user_id or perm.role_id in user_roles:
            if permission_hierarchy.get(perm.permission_level, 0) > permission_hierarchy.get(effective, 0):
                effective = perm.permission_level

    return ObjectPermissions(
        object_type=object_type,
        object_id=object_id,
        permissions=permissions,
        effective_permission=effective,
    )


@router.put("/permissions/{object_type}/{object_id}")
async def set_object_permissions(
    object_type: str,
    object_id: str,
    permissions: list[ObjectPermission],
    current_user: dict = Depends(get_current_user),
):
    """Set permissions for an object"""
    key = f"{object_type}:{object_id}"
    _object_permissions[key] = permissions
    return {"success": True, "message": "Permissions updated"}


# RLS Evaluation

@router.post("/evaluate", response_model=RLSFilterResponse)
async def evaluate_rls(
    request: RLSFilterRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Evaluate RLS policies and return filters to apply.

    Used internally when executing queries.
    """
    service = get_rls_service(_config)
    policies = list(_policies.values())

    return service.evaluate_access(request, policies)


@router.post("/test")
async def test_rls_policy(
    policy: RLSPolicy,
    test_user: UserSecurityContext,
    table_name: str,
    schema_name: str = "public",
    connection_id: str = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Test an RLS policy with a simulated user context.

    Returns the WHERE clause that would be generated.
    """
    service = get_rls_service(_config)

    request = RLSFilterRequest(
        connection_id=connection_id or "test",
        schema_name=schema_name,
        table_name=table_name,
        user_context=test_user,
    )

    result = service.evaluate_access(request, [policy])

    return {
        "policy_would_apply": policy.id in result.policies_applied,
        "where_clause": result.where_clause,
        "access_denied": result.access_denied,
        "denial_reason": result.denial_reason,
    }


# Configuration

@router.get("/config", response_model=RLSConfiguration)
async def get_rls_config(
    current_user: dict = Depends(get_current_user),
):
    """Get RLS configuration"""
    return _config


@router.put("/config", response_model=RLSConfiguration)
async def update_rls_config(
    config: RLSConfiguration,
    current_user: dict = Depends(get_current_user),
):
    """Update RLS configuration"""
    global _config
    _config = config
    return _config


# Templates

@router.get("/templates")
async def get_policy_templates(
    current_user: dict = Depends(get_current_user),
):
    """Get pre-built policy templates"""
    return RLS_POLICY_TEMPLATES


@router.post("/templates/{template_id}/apply")
async def apply_template(
    template_id: str,
    table_name: str,
    schema_name: str = "public",
    connection_id: str = None,
    role_ids: list[str] = [],
    current_user: dict = Depends(get_current_user),
):
    """Apply a policy template to create a new policy"""
    template = next((t for t in RLS_POLICY_TEMPLATES if t["id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Create policy from template
    policy = RLSPolicy(
        id=str(uuid.uuid4()),
        name=f"{template['name']} - {table_name}",
        description=template.get("description"),
        enabled=True,
        table_name=table_name,
        schema_name=schema_name,
        connection_id=connection_id,
        filter_group=RLSConditionGroup(**template["filter_group"]),
        role_ids=role_ids,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        created_by=current_user.get("user_id"),
    )

    _policies[policy.id] = policy
    return policy
