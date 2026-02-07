"""
Governance Models - Data Ownership, Lineage, Versioning, Quality, Apps, Schema Tracking
Implements enterprise BI workflow requirements
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime
import uuid
import enum

from app.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class DataOwnerType(str, enum.Enum):
    primary = "primary"
    steward = "steward"
    custodian = "custodian"
    consumer = "consumer"


class EnvironmentType(str, enum.Enum):
    development = "development"
    staging = "staging"
    production = "production"


class PromotionStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    deployed = "deployed"
    rolled_back = "rolled_back"


class LineageNodeType(str, enum.Enum):
    connection = "connection"
    table = "table"
    column = "column"
    transform = "transform"
    semantic_model = "semantic_model"
    measure = "measure"
    dimension = "dimension"
    chart = "chart"
    dashboard = "dashboard"
    kpi = "kpi"


class VersionableType(str, enum.Enum):
    dashboard = "dashboard"
    chart = "chart"
    semantic_model = "semantic_model"
    transform = "transform"
    report = "report"
    kpi = "kpi"
    rls_policy = "rls_policy"


class QualityRuleType(str, enum.Enum):
    not_null = "not_null"
    unique = "unique"
    range_check = "range_check"
    regex = "regex"
    enum_check = "enum_check"
    foreign_key = "foreign_key"
    custom_sql = "custom_sql"
    freshness = "freshness"
    row_count = "row_count"


class QualitySeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class QualityCheckStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    passed = "passed"
    failed = "failed"
    error = "error"


class SchemaChangeType(str, enum.Enum):
    column_added = "column_added"
    column_removed = "column_removed"
    column_type_changed = "column_type_changed"
    table_added = "table_added"
    table_removed = "table_removed"


class AppStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


# ============================================================================
# DATA OWNERSHIP & STEWARDSHIP
# ============================================================================

class DataSteward(Base):
    __tablename__ = "data_stewards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_name = Column(String(255), nullable=False)
    owner_type = Column(SQLEnum(DataOwnerType, name='data_owner_type', create_type=False), default=DataOwnerType.steward)
    department = Column(String(100), nullable=True)
    domain = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class DataOwnership(Base):
    __tablename__ = "data_ownership"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_type = Column(String(50), nullable=False)
    asset_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    asset_name = Column(String(255), nullable=False)
    connection_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    table_name = Column(String(255), nullable=True)
    column_name = Column(String(255), nullable=True)
    steward_id = Column(UUID(as_uuid=True), ForeignKey("data_stewards.id"), nullable=False)
    owner_type = Column(SQLEnum(DataOwnerType, name='data_owner_type', create_type=False), default=DataOwnerType.primary)
    sla_freshness_hours = Column(Integer, nullable=True)
    sla_availability_percent = Column(Float, nullable=True)
    quality_threshold = Column(Float, default=95.0)
    description = Column(Text, nullable=True)
    business_glossary = Column(Text, nullable=True)
    pii_flag = Column(Boolean, default=False)
    workspace_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# DEPLOYMENT PIPELINES
# ============================================================================

class DeploymentEnvironment(Base):
    __tablename__ = "deployment_environments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    environment_type = Column(SQLEnum(EnvironmentType, name='environment_type', create_type=False), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    is_protected = Column(Boolean, default=False)
    connection_overrides = Column(JSONB, default={})
    allowed_deployers = Column(JSONB, default=[])
    required_approvers = Column(JSONB, default=[])
    min_approvals = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class DeploymentPromotion(Base):
    __tablename__ = "deployment_promotions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)
    asset_id = Column(UUID(as_uuid=True), nullable=False)
    asset_name = Column(String(255), nullable=False)
    version_id = Column(UUID(as_uuid=True), nullable=True)
    source_environment_id = Column(UUID(as_uuid=True), ForeignKey("deployment_environments.id"), nullable=False)
    target_environment_id = Column(UUID(as_uuid=True), ForeignKey("deployment_environments.id"), nullable=False)
    status = Column(SQLEnum(PromotionStatus, name='promotion_status', create_type=False), default=PromotionStatus.pending)
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    requested_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    approvals = Column(JSONB, default=[])
    rejections = Column(JSONB, default=[])
    deployed_by = Column(UUID(as_uuid=True), nullable=True)
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    promotion_notes = Column(Text, nullable=True)
    change_summary = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# DATA LINEAGE
# ============================================================================

class LineageNode(Base):
    __tablename__ = "lineage_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    node_type = Column(SQLEnum(LineageNodeType, name='lineage_node_type', create_type=False), nullable=False)
    asset_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    asset_name = Column(String(255), nullable=False)
    connection_id = Column(UUID(as_uuid=True), nullable=True)
    schema_name = Column(String(255), nullable=True)
    table_name = Column(String(255), nullable=True)
    column_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    node_metadata = Column(JSONB, default={})
    quality_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class LineageEdge(Base):
    __tablename__ = "lineage_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    source_node_id = Column(UUID(as_uuid=True), ForeignKey("lineage_nodes.id"), nullable=False)
    target_node_id = Column(UUID(as_uuid=True), ForeignKey("lineage_nodes.id"), nullable=False)
    edge_type = Column(String(50), default="derived_from")
    transformation_type = Column(String(100), nullable=True)
    transformation_sql = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# VERSION CONTROL
# ============================================================================

class AssetVersion(Base):
    __tablename__ = "asset_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    asset_type = Column(SQLEnum(VersionableType, name='versionable_type', create_type=False), nullable=False)
    asset_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    asset_name = Column(String(255), nullable=False)
    version_number = Column(Integer, nullable=False)
    version_label = Column(String(100), nullable=True)
    snapshot = Column(JSONB, nullable=False)
    changes_summary = Column(Text, nullable=True)
    changes_diff = Column(JSONB, default={})
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    environment_id = Column(UUID(as_uuid=True), nullable=True)
    is_current = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)


# ============================================================================
# DATA QUALITY RULES
# ============================================================================

class DataQualityRule(Base):
    __tablename__ = "data_quality_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    rule_type = Column(SQLEnum(QualityRuleType, name='quality_rule_type', create_type=False), nullable=False)
    severity = Column(SQLEnum(QualitySeverity, name='quality_severity', create_type=False), default=QualitySeverity.warning)
    connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    table_name = Column(String(255), nullable=False)
    column_name = Column(String(255), nullable=True)
    rule_config = Column(JSONB, nullable=False)
    error_threshold = Column(Float, default=0)
    warning_threshold = Column(Float, default=5)
    is_active = Column(Boolean, default=True)
    check_frequency = Column(String(50), default="daily")
    last_check_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class DataQualityCheck(Base):
    __tablename__ = "data_quality_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("data_quality_rules.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(SQLEnum(QualityCheckStatus, name='quality_check_status', create_type=False), nullable=False)
    total_rows = Column(Integer, default=0)
    passed_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    pass_rate = Column(Float, default=0)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    failed_samples = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class DataQualityScore(Base):
    __tablename__ = "data_quality_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)
    connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    table_name = Column(String(255), nullable=True)
    column_name = Column(String(255), nullable=True)
    overall_score = Column(Float, nullable=False)
    completeness_score = Column(Float, nullable=True)
    validity_score = Column(Float, nullable=True)
    freshness_score = Column(Float, nullable=True)
    rules_passed = Column(Integer, default=0)
    rules_failed = Column(Integer, default=0)
    calculated_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# SCHEMA CHANGE DETECTION
# ============================================================================

class SchemaSnapshot(Base):
    __tablename__ = "schema_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tables = Column(JSONB, nullable=False)
    snapshot_hash = Column(String(64), nullable=False)
    tables_count = Column(Integer, default=0)
    columns_count = Column(Integer, default=0)
    captured_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class SchemaChange(Base):
    __tablename__ = "schema_changes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    old_snapshot_id = Column(UUID(as_uuid=True), ForeignKey("schema_snapshots.id"), nullable=False)
    new_snapshot_id = Column(UUID(as_uuid=True), ForeignKey("schema_snapshots.id"), nullable=False)
    change_type = Column(SQLEnum(SchemaChangeType, name='schema_change_type', create_type=False), nullable=False)
    table_name = Column(String(255), nullable=False)
    column_name = Column(String(255), nullable=True)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    is_breaking = Column(Boolean, default=False)
    affected_assets = Column(JSONB, default=[])
    acknowledged = Column(Boolean, default=False)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# APP BUNDLING
# ============================================================================

class App(Base):
    __tablename__ = "apps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(255), nullable=True)
    color = Column(String(7), nullable=True)
    dashboards = Column(JSONB, default=[])
    charts = Column(JSONB, default=[])
    reports = Column(JSONB, default=[])
    navigation = Column(JSONB, default=[])
    landing_dashboard_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(SQLEnum(AppStatus, name='app_status', create_type=False), default=AppStatus.draft)
    published_at = Column(DateTime(timezone=True), nullable=True)
    published_by = Column(UUID(as_uuid=True), nullable=True)
    version = Column(String(20), default="1.0.0")
    is_public = Column(Boolean, default=False)
    install_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AppInstallation(Base):
    __tablename__ = "app_installations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    app_id = Column(UUID(as_uuid=True), ForeignKey("apps.id"), nullable=False)
    installed_by = Column(UUID(as_uuid=True), nullable=False)
    target_workspace_id = Column(UUID(as_uuid=True), nullable=False)
    preferences = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    installed_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# USER ANALYTICS
# ============================================================================

class UserAnalytics(Base):
    __tablename__ = "user_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), nullable=False)
    sessions_count = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    dashboards_viewed = Column(Integer, default=0)
    charts_viewed = Column(Integer, default=0)
    reports_generated = Column(Integer, default=0)
    queries_executed = Column(Integer, default=0)
    exports_count = Column(Integer, default=0)
    filters_applied = Column(Integer, default=0)
    drill_downs = Column(Integer, default=0)
    dashboards_created = Column(Integer, default=0)
    charts_created = Column(Integer, default=0)
    top_dashboards = Column(JSONB, default=[])
    calculated_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class FeatureAdoption(Base):
    __tablename__ = "feature_adoption"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    feature_name = Column(String(100), nullable=False)
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    adoption_rate = Column(Float, default=0)
    calculated_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ContentPopularity(Base):
    __tablename__ = "content_popularity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_name = Column(String(255), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    unique_viewers = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    exports_count = Column(Integer, default=0)
    popularity_score = Column(Float, default=0)
    calculated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
