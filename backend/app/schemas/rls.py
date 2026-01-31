"""
Row-Level Security (RLS) Schemas

Provides schemas for row-level security including:
- Security roles and permissions
- RLS policies and rules
- Dynamic filters based on user context
- Object-level permissions
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class RLSFilterType(str, Enum):
    """Type of RLS filter"""
    STATIC = "static"           # Fixed filter values
    DYNAMIC = "dynamic"         # Based on user attributes
    EXPRESSION = "expression"   # Custom expression/formula


class RLSOperator(str, Enum):
    """Operators for RLS conditions"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class UserAttributeType(str, Enum):
    """Types of user attributes for dynamic filtering"""
    USER_ID = "user_id"
    USERNAME = "username"
    EMAIL = "email"
    DEPARTMENT = "department"
    REGION = "region"
    ROLE = "role"
    TEAM = "team"
    CUSTOM = "custom"


class PermissionLevel(str, Enum):
    """Permission levels"""
    NONE = "none"
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin"


# Security Role

class SecurityRole(BaseModel):
    """A security role that can have RLS policies"""
    id: str = Field(..., description="Unique role ID")
    name: str = Field(..., description="Role display name")
    description: Optional[str] = Field(None, description="Role description")
    is_default: bool = Field(False, description="Default role for new users")
    priority: int = Field(0, description="Role priority (higher = more restrictive)")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


# RLS Filter Condition

class RLSCondition(BaseModel):
    """A single condition in an RLS filter"""
    id: str = Field(..., description="Condition ID")
    column: str = Field(..., description="Column to filter")
    operator: RLSOperator = Field(..., description="Comparison operator")
    filter_type: RLSFilterType = Field(RLSFilterType.STATIC, description="Type of filter")

    # Static value
    value: Optional[Any] = Field(None, description="Static value(s) to compare")

    # Dynamic attribute
    user_attribute: Optional[UserAttributeType] = Field(None, description="User attribute for dynamic filter")
    custom_attribute: Optional[str] = Field(None, description="Custom attribute name")

    # Expression
    expression: Optional[str] = Field(None, description="Custom expression for complex conditions")


class RLSConditionGroup(BaseModel):
    """Group of conditions with AND/OR logic"""
    id: str = Field(..., description="Group ID")
    logic: str = Field("AND", description="AND or OR")
    conditions: list[RLSCondition] = Field(default_factory=list)
    groups: list["RLSConditionGroup"] = Field(default_factory=list, description="Nested groups")


# Update forward reference
RLSConditionGroup.model_rebuild()


# RLS Policy

class RLSPolicy(BaseModel):
    """A row-level security policy"""
    id: str = Field(..., description="Policy ID")
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    enabled: bool = Field(True, description="Whether policy is active")
    priority: int = Field(0, description="Policy priority")

    # Scope
    table_name: Optional[str] = Field(None, description="Specific table (None = all)")
    schema_name: Optional[str] = Field(None, description="Specific schema")
    connection_id: Optional[str] = Field(None, description="Specific connection")

    # Filter conditions
    filter_group: RLSConditionGroup = Field(..., description="Filter conditions")

    # Role assignment
    role_ids: list[str] = Field(default_factory=list, description="Roles this policy applies to")

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None


# Role-User Mapping

class UserRoleMapping(BaseModel):
    """Mapping of users to roles"""
    user_id: str = Field(..., description="User ID")
    role_ids: list[str] = Field(..., description="Assigned role IDs")
    effective_from: Optional[str] = Field(None, description="Start date")
    effective_to: Optional[str] = Field(None, description="End date")


# User Attributes

class UserSecurityContext(BaseModel):
    """Security context for a user"""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="Email")
    roles: list[str] = Field(default_factory=list, description="User's role IDs")
    attributes: dict[str, Any] = Field(default_factory=dict, description="User attributes")


# Object-Level Permissions

class ObjectPermission(BaseModel):
    """Permission for a specific object (dashboard, chart, etc.)"""
    object_type: str = Field(..., description="Type: dashboard, chart, dataset")
    object_id: str = Field(..., description="Object ID")
    role_id: Optional[str] = Field(None, description="Role ID (if role-based)")
    user_id: Optional[str] = Field(None, description="User ID (if user-based)")
    permission_level: PermissionLevel = Field(PermissionLevel.VIEW)
    inherited: bool = Field(False, description="Inherited from parent object")


class ObjectPermissions(BaseModel):
    """All permissions for an object"""
    object_type: str
    object_id: str
    permissions: list[ObjectPermission] = Field(default_factory=list)
    effective_permission: PermissionLevel = Field(PermissionLevel.NONE)


# RLS Request/Response

class RLSFilterRequest(BaseModel):
    """Request to get RLS filters for a query"""
    connection_id: str = Field(..., description="Connection ID")
    schema_name: str = Field(..., description="Schema name")
    table_name: str = Field(..., description="Table name")
    user_context: UserSecurityContext = Field(..., description="User's security context")


class RLSFilterResponse(BaseModel):
    """Response with RLS filters to apply"""
    has_filters: bool = Field(False, description="Whether any filters apply")
    where_clause: Optional[str] = Field(None, description="WHERE clause to add")
    policies_applied: list[str] = Field(default_factory=list, description="Policy IDs applied")
    access_denied: bool = Field(False, description="Whether access is denied entirely")
    denial_reason: Optional[str] = Field(None, description="Reason for denial")


# Configuration

class RLSConfiguration(BaseModel):
    """Global RLS configuration"""
    enabled: bool = Field(True, description="Global RLS enabled")
    default_deny: bool = Field(False, description="Deny access when no policy matches")
    cache_ttl_seconds: int = Field(300, description="Cache TTL for RLS evaluations")
    log_access: bool = Field(True, description="Log access decisions")
    audit_mode: bool = Field(False, description="Audit mode (log but don't enforce)")


# Audit Log

class RLSAuditEntry(BaseModel):
    """Audit log entry for RLS decisions"""
    timestamp: str = Field(..., description="Timestamp")
    user_id: str = Field(..., description="User ID")
    action: str = Field(..., description="Action type")
    object_type: str = Field(..., description="Object type")
    object_id: str = Field(..., description="Object ID")
    policies_evaluated: list[str] = Field(default_factory=list)
    policies_applied: list[str] = Field(default_factory=list)
    decision: str = Field(..., description="allow or deny")
    reason: Optional[str] = None
    filters_applied: Optional[str] = None


# Policy Templates

RLS_POLICY_TEMPLATES = [
    {
        "id": "department_filter",
        "name": "Department Filter",
        "description": "Users can only see data for their department",
        "filter_group": {
            "id": "dept_group",
            "logic": "AND",
            "conditions": [
                {
                    "id": "dept_cond",
                    "column": "department",
                    "operator": "equals",
                    "filter_type": "dynamic",
                    "user_attribute": "department",
                }
            ],
        },
    },
    {
        "id": "region_filter",
        "name": "Region Filter",
        "description": "Users can only see data for their region(s)",
        "filter_group": {
            "id": "region_group",
            "logic": "AND",
            "conditions": [
                {
                    "id": "region_cond",
                    "column": "region",
                    "operator": "in",
                    "filter_type": "dynamic",
                    "user_attribute": "region",
                }
            ],
        },
    },
    {
        "id": "owner_filter",
        "name": "Owner Filter",
        "description": "Users can only see records they own",
        "filter_group": {
            "id": "owner_group",
            "logic": "AND",
            "conditions": [
                {
                    "id": "owner_cond",
                    "column": "owner_id",
                    "operator": "equals",
                    "filter_type": "dynamic",
                    "user_attribute": "user_id",
                }
            ],
        },
    },
    {
        "id": "team_hierarchy",
        "name": "Team Hierarchy",
        "description": "Users can see their team's data and subordinates",
        "filter_group": {
            "id": "team_group",
            "logic": "OR",
            "conditions": [
                {
                    "id": "team_cond",
                    "column": "team_id",
                    "operator": "equals",
                    "filter_type": "dynamic",
                    "user_attribute": "team",
                },
                {
                    "id": "owner_cond",
                    "column": "created_by",
                    "operator": "equals",
                    "filter_type": "dynamic",
                    "user_attribute": "user_id",
                },
            ],
        },
    },
]
