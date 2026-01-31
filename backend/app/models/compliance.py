"""
Compliance Models

Database models for compliance, governance, and data policies.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class CompliancePolicy(Base):
    """
    Compliance policy model for data governance rules.
    """
    __tablename__ = "compliance_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Policy info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    policy_type = Column(String(50), nullable=False)  # data_retention, access_control, pii, export

    # Scope
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)
    applies_to = Column(String(50), default="all")  # all, specific

    # Rules
    rules = Column(JSONB, nullable=False, default=[])
    conditions = Column(JSONB, default={})

    # Actions
    enforcement_action = Column(String(50), default="warn")  # warn, block, notify, log
    notification_config = Column(JSONB, default={})

    # Status
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    violations = relationship("ComplianceViolation", back_populates="policy", cascade="all, delete-orphan")


class ComplianceViolation(Base):
    """
    Compliance violation record.
    """
    __tablename__ = "compliance_violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    policy_id = Column(UUID(as_uuid=True), ForeignKey("compliance_policies.id", ondelete="CASCADE"), nullable=False)

    # Violation details
    violation_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    description = Column(Text, nullable=True)

    # Context
    user_id = Column(UUID(as_uuid=True), nullable=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Evidence
    evidence = Column(JSONB, default={})
    request_data = Column(JSONB, nullable=True)

    # Status
    status = Column(String(50), default="open")  # open, acknowledged, resolved, dismissed
    resolution = Column(Text, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    policy = relationship("CompliancePolicy", back_populates="violations")

    __table_args__ = (
        Index('ix_compliance_violations_policy_status', policy_id, status),
        Index('ix_compliance_violations_severity_date', severity, detected_at),
    )


class DataClassification(Base):
    """
    Data classification for sensitive data handling.
    """
    __tablename__ = "data_classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Classification info
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=False)  # 1=public, 2=internal, 3=confidential, 4=restricted

    # Visual
    color = Column(String(20), default="#6B7280")
    icon = Column(String(50), nullable=True)

    # Handling requirements
    encryption_required = Column(Boolean, default=False)
    audit_required = Column(Boolean, default=True)
    export_allowed = Column(Boolean, default=True)
    sharing_allowed = Column(Boolean, default=True)

    # Retention
    retention_days = Column(Integer, nullable=True)

    # Status
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class DataRetentionPolicy(Base):
    """
    Data retention policy for automatic data cleanup.
    """
    __tablename__ = "data_retention_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Policy info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Target
    target_type = Column(String(50), nullable=False)  # audit_logs, query_results, exports, cache
    target_classification = Column(String(100), nullable=True)

    # Retention
    retention_days = Column(Integer, nullable=False)
    archive_before_delete = Column(Boolean, default=True)
    archive_location = Column(String(255), nullable=True)

    # Schedule
    run_schedule = Column(String(100), default="0 2 * * *")  # Daily at 2 AM

    # Status
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)

    # Stats
    total_deleted = Column(Integer, default=0)
    total_archived = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ConsentRecord(Base):
    """
    User consent tracking for privacy compliance.
    """
    __tablename__ = "consent_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Consent type
    consent_type = Column(String(100), nullable=False)  # terms, privacy, marketing, analytics
    version = Column(String(50), nullable=True)

    # Status
    granted = Column(Boolean, nullable=False)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index('ix_consent_records_user_type', user_id, consent_type),
    )
