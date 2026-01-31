"""
Security Models

SQLAlchemy models for Row-Level Security (RLS) policies and roles.
"""

from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Enum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class RLSFilterType(str, enum.Enum):
    """RLS filter type"""
    STATIC = "static"           # Fixed values
    DYNAMIC = "dynamic"         # Based on user attributes
    EXPRESSION = "expression"   # SQL expression


class RLSOperator(str, enum.Enum):
    """RLS comparison operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class SecurityRole(Base):
    """
    Security role for RLS.

    Groups users for applying RLS policies.
    """
    __tablename__ = "security_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Configuration
    is_default = Column(Boolean, default=False)  # Assign to new users automatically
    priority = Column(Integer, default=0)  # Higher priority = evaluated first

    # Ownership
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_assignments = relationship("UserRoleAssignment", back_populates="role", cascade="all, delete-orphan")
    policies = relationship("RLSPolicyRole", back_populates="role", cascade="all, delete-orphan")


class UserRoleAssignment(Base):
    """
    Assignment of users to security roles.
    """
    __tablename__ = "user_role_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("security_roles.id", ondelete="CASCADE"), nullable=False)

    # Time-bound assignments
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)

    # Metadata
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship("SecurityRole", back_populates="user_assignments")


class RLSPolicy(Base):
    """
    Row-Level Security policy.

    Defines data access rules based on user identity/attributes.
    """
    __tablename__ = "rls_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Target
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.id", ondelete="CASCADE"), nullable=True)
    semantic_model_id = Column(UUID(as_uuid=True), ForeignKey("semantic_models.id", ondelete="CASCADE"), nullable=True)
    table_name = Column(String(255), nullable=True)  # Specific table or NULL for all
    schema_name = Column(String(255), nullable=True)

    # Filter configuration
    filter_logic = Column(String(10), default="AND")  # AND, OR for multiple conditions
    conditions = Column(JSONB, nullable=False)
    # conditions format: [
    #   {
    #     "id": "cond_1",
    #     "column": "region",
    #     "operator": "equals",
    #     "filter_type": "dynamic",
    #     "user_attribute": "department",  # For dynamic
    #     "value": "East",  # For static
    #     "expression": "CURRENT_USER()"  # For expression
    #   }
    # ]

    # Status
    is_enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Lower number = higher priority

    # Audit
    log_access = Column(Boolean, default=False)  # Log when policy is applied

    # Ownership
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = relationship("RLSPolicyRole", back_populates="policy", cascade="all, delete-orphan")
    audit_logs = relationship("RLSAuditLog", back_populates="policy", cascade="all, delete-orphan")


class RLSPolicyRole(Base):
    """
    Many-to-many relationship between policies and roles.
    """
    __tablename__ = "rls_policy_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("rls_policies.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("security_roles.id", ondelete="CASCADE"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    policy = relationship("RLSPolicy", back_populates="roles")
    role = relationship("SecurityRole", back_populates="policies")


class RLSAuditLog(Base):
    """
    Audit log for RLS policy evaluations.
    """
    __tablename__ = "rls_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("rls_policies.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Access details
    table_name = Column(String(255), nullable=True)
    schema_name = Column(String(255), nullable=True)
    connection_id = Column(UUID(as_uuid=True), nullable=True)

    # Evaluation result
    access_granted = Column(Boolean, nullable=False)
    filter_applied = Column(Text, nullable=True)  # The WHERE clause generated
    denial_reason = Column(Text, nullable=True)

    # Context
    user_attributes = Column(JSONB, nullable=True)  # Snapshot of user attributes at time of access
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamps
    evaluated_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    policy = relationship("RLSPolicy", back_populates="audit_logs")


class UserAttribute(Base):
    """
    Custom user attributes for dynamic RLS.

    Stores additional attributes about users for RLS evaluation.
    """
    __tablename__ = "user_attributes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Attribute
    attribute_name = Column(String(255), nullable=False)
    attribute_value = Column(Text, nullable=False)

    # Source
    source = Column(String(50), default="manual")  # manual, ldap, oauth, api

    # Validity
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint on user_id + attribute_name
    __table_args__ = (
        {'extend_existing': True}
    )


class RLSConfiguration(Base):
    """
    Global RLS configuration.
    """
    __tablename__ = "rls_configuration"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, unique=True)

    # Settings
    enabled = Column(Boolean, default=True)
    default_deny = Column(Boolean, default=False)  # Deny access if no policy matches
    cache_ttl_seconds = Column(Integer, default=300)
    log_all_access = Column(Boolean, default=False)
    audit_mode = Column(Boolean, default=False)  # Log but don't enforce

    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
