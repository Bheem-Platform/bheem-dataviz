"""
Governance Schemas - Pydantic models for API request/response
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class DataOwnerType(str, Enum):
    primary = "primary"
    steward = "steward"
    custodian = "custodian"
    consumer = "consumer"


class EnvironmentType(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


class PromotionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    deployed = "deployed"
    rolled_back = "rolled_back"


class LineageNodeType(str, Enum):
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


class VersionableType(str, Enum):
    dashboard = "dashboard"
    chart = "chart"
    semantic_model = "semantic_model"
    transform = "transform"
    report = "report"
    kpi = "kpi"
    rls_policy = "rls_policy"


class QualityRuleType(str, Enum):
    not_null = "not_null"
    unique = "unique"
    range_check = "range_check"
    regex = "regex"
    enum_check = "enum_check"
    foreign_key = "foreign_key"
    custom_sql = "custom_sql"
    freshness = "freshness"
    row_count = "row_count"


class QualitySeverity(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class QualityCheckStatus(str, Enum):
    pending = "pending"
    running = "running"
    passed = "passed"
    failed = "failed"
    error = "error"


class SchemaChangeType(str, Enum):
    column_added = "column_added"
    column_removed = "column_removed"
    column_type_changed = "column_type_changed"
    table_added = "table_added"
    table_removed = "table_removed"


class AppStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


# ============================================================================
# DATA STEWARD SCHEMAS
# ============================================================================

class DataStewardBase(BaseModel):
    user_id: UUID
    user_email: str
    user_name: str
    owner_type: DataOwnerType = DataOwnerType.steward
    department: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class DataStewardCreate(DataStewardBase):
    workspace_id: Optional[UUID] = None


class DataStewardUpdate(BaseModel):
    owner_type: Optional[DataOwnerType] = None
    department: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DataStewardResponse(DataStewardBase):
    id: UUID
    workspace_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DATA OWNERSHIP SCHEMAS
# ============================================================================

class DataOwnershipBase(BaseModel):
    asset_type: str
    asset_id: UUID
    asset_name: str
    connection_id: Optional[UUID] = None
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    steward_id: UUID
    owner_type: DataOwnerType = DataOwnerType.primary
    sla_freshness_hours: Optional[int] = None
    sla_availability_percent: Optional[float] = None
    quality_threshold: float = 95.0
    description: Optional[str] = None
    business_glossary: Optional[str] = None
    pii_flag: bool = False


class DataOwnershipCreate(DataOwnershipBase):
    workspace_id: Optional[UUID] = None


class DataOwnershipUpdate(BaseModel):
    steward_id: Optional[UUID] = None
    owner_type: Optional[DataOwnerType] = None
    sla_freshness_hours: Optional[int] = None
    sla_availability_percent: Optional[float] = None
    quality_threshold: Optional[float] = None
    description: Optional[str] = None
    business_glossary: Optional[str] = None
    pii_flag: Optional[bool] = None


class DataOwnershipResponse(DataOwnershipBase):
    id: UUID
    workspace_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DEPLOYMENT ENVIRONMENT SCHEMAS
# ============================================================================

class DeploymentEnvironmentBase(BaseModel):
    name: str
    environment_type: EnvironmentType
    description: Optional[str] = None
    is_default: bool = False
    is_protected: bool = False
    connection_overrides: Dict[str, Any] = {}
    allowed_deployers: List[UUID] = []
    required_approvers: List[UUID] = []
    min_approvals: int = 1


class DeploymentEnvironmentCreate(DeploymentEnvironmentBase):
    workspace_id: UUID


class DeploymentEnvironmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_protected: Optional[bool] = None
    connection_overrides: Optional[Dict[str, Any]] = None
    allowed_deployers: Optional[List[UUID]] = None
    required_approvers: Optional[List[UUID]] = None
    min_approvals: Optional[int] = None


class DeploymentEnvironmentResponse(DeploymentEnvironmentBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DEPLOYMENT PROMOTION SCHEMAS
# ============================================================================

class DeploymentPromotionBase(BaseModel):
    asset_type: str
    asset_id: UUID
    asset_name: str
    source_environment_id: UUID
    target_environment_id: UUID
    promotion_notes: Optional[str] = None


class DeploymentPromotionCreate(DeploymentPromotionBase):
    workspace_id: UUID
    version_id: Optional[UUID] = None


class DeploymentPromotionApproval(BaseModel):
    approved: bool
    comment: Optional[str] = None


class DeploymentPromotionResponse(DeploymentPromotionBase):
    id: UUID
    workspace_id: UUID
    version_id: Optional[UUID] = None
    status: PromotionStatus
    requested_by: UUID
    requested_at: datetime
    approvals: List[Dict[str, Any]] = []
    rejections: List[Dict[str, Any]] = []
    deployed_by: Optional[UUID] = None
    deployed_at: Optional[datetime] = None
    change_summary: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# LINEAGE SCHEMAS
# ============================================================================

class LineageNodeBase(BaseModel):
    node_type: LineageNodeType
    asset_id: UUID
    asset_name: str
    connection_id: Optional[UUID] = None
    schema_name: Optional[str] = None
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    description: Optional[str] = None
    node_metadata: Dict[str, Any] = {}


class LineageNodeCreate(LineageNodeBase):
    workspace_id: UUID


class LineageNodeResponse(LineageNodeBase):
    id: UUID
    workspace_id: UUID
    quality_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LineageEdgeBase(BaseModel):
    source_node_id: UUID
    target_node_id: UUID
    edge_type: str = "derived_from"
    transformation_type: Optional[str] = None
    transformation_sql: Optional[str] = None
    confidence: float = 1.0


class LineageEdgeCreate(LineageEdgeBase):
    workspace_id: UUID


class LineageEdgeResponse(LineageEdgeBase):
    id: UUID
    workspace_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LineageGraphResponse(BaseModel):
    nodes: List[LineageNodeResponse]
    edges: List[LineageEdgeResponse]


class ImpactAnalysisRequest(BaseModel):
    source_node_id: UUID
    change_type: str


class ImpactAnalysisResponse(BaseModel):
    source_node_id: UUID
    change_type: str
    affected_nodes: List[Dict[str, Any]]
    affected_dashboards: List[Dict[str, Any]]
    affected_charts: List[Dict[str, Any]]
    total_affected: int
    critical_impacts: int


# ============================================================================
# VERSION CONTROL SCHEMAS
# ============================================================================

class AssetVersionBase(BaseModel):
    asset_type: VersionableType
    asset_id: UUID
    asset_name: str
    version_label: Optional[str] = None
    changes_summary: Optional[str] = None


class AssetVersionCreate(AssetVersionBase):
    workspace_id: UUID
    snapshot: Dict[str, Any]


class AssetVersionResponse(AssetVersionBase):
    id: UUID
    workspace_id: UUID
    version_number: int
    snapshot: Dict[str, Any]
    changes_diff: Dict[str, Any] = {}
    created_by: UUID
    created_at: datetime
    environment_id: Optional[UUID] = None
    is_current: bool
    is_published: bool

    class Config:
        from_attributes = True


class VersionComparisonRequest(BaseModel):
    version_a_id: UUID
    version_b_id: UUID


class VersionComparisonResponse(BaseModel):
    version_a_id: UUID
    version_b_id: UUID
    additions: List[Dict[str, Any]]
    removals: List[Dict[str, Any]]
    modifications: List[Dict[str, Any]]
    total_changes: int
    breaking_changes: bool


class RollbackRequest(BaseModel):
    version_id: UUID
    reason: Optional[str] = None


# ============================================================================
# DATA QUALITY SCHEMAS
# ============================================================================

class DataQualityRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: QualityRuleType
    severity: QualitySeverity = QualitySeverity.warning
    connection_id: UUID
    table_name: str
    column_name: Optional[str] = None
    rule_config: Dict[str, Any]
    error_threshold: float = 0
    warning_threshold: float = 5
    is_active: bool = True
    check_frequency: str = "daily"


class DataQualityRuleCreate(DataQualityRuleBase):
    workspace_id: UUID


class DataQualityRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[QualitySeverity] = None
    rule_config: Optional[Dict[str, Any]] = None
    error_threshold: Optional[float] = None
    warning_threshold: Optional[float] = None
    is_active: Optional[bool] = None
    check_frequency: Optional[str] = None


class DataQualityRuleResponse(DataQualityRuleBase):
    id: UUID
    workspace_id: UUID
    last_check_at: Optional[datetime] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataQualityCheckResponse(BaseModel):
    id: UUID
    rule_id: UUID
    workspace_id: UUID
    status: QualityCheckStatus
    total_rows: int
    passed_rows: int
    failed_rows: int
    pass_rate: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    failed_samples: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True


class DataQualityScoreResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    asset_type: str
    connection_id: UUID
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    overall_score: float
    completeness_score: Optional[float] = None
    validity_score: Optional[float] = None
    freshness_score: Optional[float] = None
    rules_passed: int
    rules_failed: int
    calculated_at: datetime

    class Config:
        from_attributes = True


class RunQualityCheckRequest(BaseModel):
    rule_ids: Optional[List[UUID]] = None  # If None, run all active rules
    connection_id: Optional[UUID] = None
    table_name: Optional[str] = None


# ============================================================================
# SCHEMA CHANGE SCHEMAS
# ============================================================================

class SchemaSnapshotResponse(BaseModel):
    id: UUID
    connection_id: UUID
    workspace_id: UUID
    tables: List[Dict[str, Any]]
    snapshot_hash: str
    tables_count: int
    columns_count: int
    captured_at: datetime

    class Config:
        from_attributes = True


class SchemaChangeResponse(BaseModel):
    id: UUID
    connection_id: UUID
    workspace_id: UUID
    change_type: SchemaChangeType
    table_name: str
    column_name: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    is_breaking: bool
    affected_assets: List[Dict[str, Any]]
    acknowledged: bool
    detected_at: datetime

    class Config:
        from_attributes = True


class AcknowledgeSchemaChangeRequest(BaseModel):
    change_ids: List[UUID]


class CaptureSchemaRequest(BaseModel):
    connection_id: UUID


# ============================================================================
# APP BUNDLING SCHEMAS
# ============================================================================

class AppBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    dashboards: List[UUID] = []
    charts: List[UUID] = []
    reports: List[UUID] = []
    navigation: List[Dict[str, Any]] = []
    landing_dashboard_id: Optional[UUID] = None
    is_public: bool = False


class AppCreate(AppBase):
    workspace_id: UUID


class AppUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    dashboards: Optional[List[UUID]] = None
    charts: Optional[List[UUID]] = None
    reports: Optional[List[UUID]] = None
    navigation: Optional[List[Dict[str, Any]]] = None
    landing_dashboard_id: Optional[UUID] = None
    is_public: Optional[bool] = None


class AppResponse(AppBase):
    id: UUID
    workspace_id: UUID
    status: AppStatus
    published_at: Optional[datetime] = None
    published_by: Optional[UUID] = None
    version: str
    install_count: int
    view_count: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppPublishRequest(BaseModel):
    version: Optional[str] = None


class AppInstallationResponse(BaseModel):
    id: UUID
    app_id: UUID
    installed_by: UUID
    target_workspace_id: UUID
    preferences: Dict[str, Any]
    is_active: bool
    installed_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# USER ANALYTICS SCHEMAS
# ============================================================================

class UserAnalyticsResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    user_id: UUID
    period_start: datetime
    period_end: datetime
    period_type: str
    sessions_count: int
    total_duration_seconds: int
    dashboards_viewed: int
    charts_viewed: int
    reports_generated: int
    queries_executed: int
    exports_count: int
    filters_applied: int
    drill_downs: int
    dashboards_created: int
    charts_created: int
    top_dashboards: List[Dict[str, Any]]
    calculated_at: datetime

    class Config:
        from_attributes = True


class FeatureAdoptionResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    period_start: datetime
    period_end: datetime
    feature_name: str
    total_users: int
    active_users: int
    usage_count: int
    adoption_rate: float
    calculated_at: datetime

    class Config:
        from_attributes = True


class ContentPopularityResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    content_type: str
    content_id: UUID
    content_name: str
    period_start: datetime
    period_end: datetime
    unique_viewers: int
    total_views: int
    shares_count: int
    exports_count: int
    popularity_score: float
    calculated_at: datetime

    class Config:
        from_attributes = True


class AnalyticsDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    total_dashboards: int
    total_charts: int
    total_queries: int
    avg_session_duration: int
    top_features: List[FeatureAdoptionResponse]
    top_content: List[ContentPopularityResponse]
    user_activity: List[UserAnalyticsResponse]


class AnalyticsQueryParams(BaseModel):
    period_type: str = "daily"  # daily, weekly, monthly
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[UUID] = None
