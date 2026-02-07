"""
Governance API Endpoints
Data Ownership, Lineage, Versioning, Quality, Apps, Schema Tracking, Analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import hashlib
import json

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.governance import (
    # Data Stewards
    DataStewardCreate, DataStewardUpdate, DataStewardResponse,
    # Data Ownership
    DataOwnershipCreate, DataOwnershipUpdate, DataOwnershipResponse,
    # Deployment
    DeploymentEnvironmentCreate, DeploymentEnvironmentUpdate, DeploymentEnvironmentResponse,
    DeploymentPromotionCreate, DeploymentPromotionApproval, DeploymentPromotionResponse,
    # Lineage
    LineageNodeCreate, LineageNodeResponse, LineageEdgeCreate, LineageEdgeResponse,
    LineageGraphResponse, ImpactAnalysisRequest, ImpactAnalysisResponse,
    # Versioning
    AssetVersionCreate, AssetVersionResponse, VersionComparisonRequest,
    VersionComparisonResponse, RollbackRequest,
    # Quality
    DataQualityRuleCreate, DataQualityRuleUpdate, DataQualityRuleResponse,
    DataQualityCheckResponse, DataQualityScoreResponse, RunQualityCheckRequest,
    # Schema
    SchemaSnapshotResponse, SchemaChangeResponse, AcknowledgeSchemaChangeRequest,
    CaptureSchemaRequest,
    # Apps
    AppCreate, AppUpdate, AppResponse, AppPublishRequest, AppInstallationResponse,
    # Analytics
    UserAnalyticsResponse, FeatureAdoptionResponse, ContentPopularityResponse,
    AnalyticsDashboardResponse,
    # Enums
    PromotionStatus, QualityCheckStatus, AppStatus
)
from app.models.governance import (
    DataSteward, DataOwnership, DeploymentEnvironment, DeploymentPromotion,
    LineageNode, LineageEdge, AssetVersion, DataQualityRule, DataQualityCheck,
    DataQualityScore, SchemaSnapshot, SchemaChange, App, AppInstallation,
    UserAnalytics, FeatureAdoption, ContentPopularity
)

router = APIRouter()


# =============================================================================
# DATA STEWARDS ENDPOINTS
# =============================================================================

@router.post("/stewards", response_model=DataStewardResponse, tags=["Data Governance"])
async def create_data_steward(
    steward: DataStewardCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new data steward"""
    db_steward = DataSteward(**steward.model_dump())
    db.add(db_steward)
    await db.commit()
    await db.refresh(db_steward)
    return db_steward


@router.get("/stewards", response_model=List[DataStewardResponse], tags=["Data Governance"])
async def list_data_stewards(
    workspace_id: Optional[UUID] = None,
    domain: Optional[str] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all data stewards"""
    query = select(DataSteward).where(DataSteward.is_active == is_active)
    if workspace_id:
        query = query.where(DataSteward.workspace_id == workspace_id)
    if domain:
        query = query.where(DataSteward.domain == domain)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stewards/{steward_id}", response_model=DataStewardResponse, tags=["Data Governance"])
async def get_data_steward(
    steward_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific data steward"""
    result = await db.execute(select(DataSteward).where(DataSteward.id == steward_id))
    steward = result.scalar_one_or_none()
    if not steward:
        raise HTTPException(status_code=404, detail="Data steward not found")
    return steward


@router.put("/stewards/{steward_id}", response_model=DataStewardResponse, tags=["Data Governance"])
async def update_data_steward(
    steward_id: UUID,
    updates: DataStewardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a data steward"""
    result = await db.execute(select(DataSteward).where(DataSteward.id == steward_id))
    steward = result.scalar_one_or_none()
    if not steward:
        raise HTTPException(status_code=404, detail="Data steward not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(steward, key, value)

    await db.commit()
    await db.refresh(steward)
    return steward


# =============================================================================
# DATA OWNERSHIP ENDPOINTS
# =============================================================================

@router.post("/ownership", response_model=DataOwnershipResponse, tags=["Data Governance"])
async def create_data_ownership(
    ownership: DataOwnershipCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign ownership to a data asset"""
    db_ownership = DataOwnership(**ownership.model_dump())
    db.add(db_ownership)
    await db.commit()
    await db.refresh(db_ownership)
    return db_ownership


@router.get("/ownership", response_model=List[DataOwnershipResponse], tags=["Data Governance"])
async def list_data_ownership(
    workspace_id: Optional[UUID] = None,
    asset_type: Optional[str] = None,
    connection_id: Optional[UUID] = None,
    steward_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List data ownership records"""
    query = select(DataOwnership)
    if workspace_id:
        query = query.where(DataOwnership.workspace_id == workspace_id)
    if asset_type:
        query = query.where(DataOwnership.asset_type == asset_type)
    if connection_id:
        query = query.where(DataOwnership.connection_id == connection_id)
    if steward_id:
        query = query.where(DataOwnership.steward_id == steward_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/ownership/{asset_id}", response_model=DataOwnershipResponse, tags=["Data Governance"])
async def get_asset_ownership(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get ownership for a specific asset"""
    result = await db.execute(select(DataOwnership).where(DataOwnership.asset_id == asset_id))
    ownership = result.scalar_one_or_none()
    if not ownership:
        raise HTTPException(status_code=404, detail="Ownership not found")
    return ownership


# =============================================================================
# DEPLOYMENT ENVIRONMENTS ENDPOINTS
# =============================================================================

@router.post("/environments", response_model=DeploymentEnvironmentResponse, tags=["Deployment"])
async def create_environment(
    env: DeploymentEnvironmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a deployment environment"""
    db_env = DeploymentEnvironment(**env.model_dump())
    db.add(db_env)
    await db.commit()
    await db.refresh(db_env)
    return db_env


@router.get("/environments", response_model=List[DeploymentEnvironmentResponse], tags=["Deployment"])
async def list_environments(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List deployment environments for a workspace"""
    result = await db.execute(
        select(DeploymentEnvironment).where(DeploymentEnvironment.workspace_id == workspace_id)
    )
    return result.scalars().all()


@router.put("/environments/{env_id}", response_model=DeploymentEnvironmentResponse, tags=["Deployment"])
async def update_environment(
    env_id: UUID,
    updates: DeploymentEnvironmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a deployment environment"""
    result = await db.execute(select(DeploymentEnvironment).where(DeploymentEnvironment.id == env_id))
    env = result.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(env, key, value)

    await db.commit()
    await db.refresh(env)
    return env


# =============================================================================
# DEPLOYMENT PROMOTIONS ENDPOINTS
# =============================================================================

@router.post("/promotions", response_model=DeploymentPromotionResponse, tags=["Deployment"])
async def create_promotion(
    promotion: DeploymentPromotionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Request a deployment promotion"""
    db_promotion = DeploymentPromotion(
        **promotion.model_dump(),
        requested_by=current_user.id
    )
    db.add(db_promotion)
    await db.commit()
    await db.refresh(db_promotion)
    return db_promotion


@router.get("/promotions", response_model=List[DeploymentPromotionResponse], tags=["Deployment"])
async def list_promotions(
    workspace_id: UUID,
    status: Optional[PromotionStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List deployment promotions"""
    query = select(DeploymentPromotion).where(DeploymentPromotion.workspace_id == workspace_id)
    if status:
        query = query.where(DeploymentPromotion.status == status)
    result = await db.execute(query.order_by(DeploymentPromotion.requested_at.desc()))
    return result.scalars().all()


@router.post("/promotions/{promotion_id}/approve", response_model=DeploymentPromotionResponse, tags=["Deployment"])
async def approve_promotion(
    promotion_id: UUID,
    approval: DeploymentPromotionApproval,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve or reject a promotion"""
    result = await db.execute(select(DeploymentPromotion).where(DeploymentPromotion.id == promotion_id))
    promotion = result.scalar_one_or_none()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")

    approval_record = {
        "user_id": str(current_user.id),
        "approved_at": datetime.utcnow().isoformat(),
        "comment": approval.comment
    }

    if approval.approved:
        promotion.approvals = promotion.approvals + [approval_record]
        # Check if enough approvals
        env_result = await db.execute(
            select(DeploymentEnvironment).where(DeploymentEnvironment.id == promotion.target_environment_id)
        )
        target_env = env_result.scalar_one_or_none()
        if target_env and len(promotion.approvals) >= target_env.min_approvals:
            promotion.status = PromotionStatus.approved
    else:
        promotion.rejections = promotion.rejections + [approval_record]
        promotion.status = PromotionStatus.rejected

    await db.commit()
    await db.refresh(promotion)
    return promotion


@router.post("/promotions/{promotion_id}/deploy", response_model=DeploymentPromotionResponse, tags=["Deployment"])
async def deploy_promotion(
    promotion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Deploy an approved promotion"""
    result = await db.execute(select(DeploymentPromotion).where(DeploymentPromotion.id == promotion_id))
    promotion = result.scalar_one_or_none()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")

    if promotion.status != PromotionStatus.approved:
        raise HTTPException(status_code=400, detail="Promotion must be approved before deployment")

    promotion.status = PromotionStatus.deployed
    promotion.deployed_by = current_user.id
    promotion.deployed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(promotion)
    return promotion


# =============================================================================
# LINEAGE ENDPOINTS
# =============================================================================

@router.post("/lineage/nodes", response_model=LineageNodeResponse, tags=["Data Lineage"])
async def create_lineage_node(
    node: LineageNodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a lineage node"""
    db_node = LineageNode(**node.model_dump())
    db.add(db_node)
    await db.commit()
    await db.refresh(db_node)
    return db_node


@router.post("/lineage/edges", response_model=LineageEdgeResponse, tags=["Data Lineage"])
async def create_lineage_edge(
    edge: LineageEdgeCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a lineage edge"""
    db_edge = LineageEdge(**edge.model_dump())
    db.add(db_edge)
    await db.commit()
    await db.refresh(db_edge)
    return db_edge


@router.get("/lineage/graph", response_model=LineageGraphResponse, tags=["Data Lineage"])
async def get_lineage_graph(
    workspace_id: UUID,
    asset_id: Optional[UUID] = None,
    depth: int = 3,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get lineage graph for a workspace or specific asset"""
    nodes_query = select(LineageNode).where(LineageNode.workspace_id == workspace_id)
    if asset_id:
        nodes_query = nodes_query.where(LineageNode.asset_id == asset_id)

    nodes_result = await db.execute(nodes_query)
    nodes = nodes_result.scalars().all()

    edges_query = select(LineageEdge).where(
        LineageEdge.workspace_id == workspace_id,
        LineageEdge.is_active == True
    )
    edges_result = await db.execute(edges_query)
    edges = edges_result.scalars().all()

    return LineageGraphResponse(nodes=nodes, edges=edges)


@router.post("/lineage/impact-analysis", response_model=ImpactAnalysisResponse, tags=["Data Lineage"])
async def analyze_impact(
    request: ImpactAnalysisRequest,
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Analyze impact of changes to a data asset"""
    # Get all downstream edges
    edges_result = await db.execute(
        select(LineageEdge).where(
            LineageEdge.workspace_id == workspace_id,
            LineageEdge.source_node_id == request.source_node_id,
            LineageEdge.is_active == True
        )
    )
    edges = edges_result.scalars().all()

    affected_node_ids = [e.target_node_id for e in edges]

    # Get affected nodes
    affected_nodes = []
    affected_dashboards = []
    affected_charts = []

    if affected_node_ids:
        nodes_result = await db.execute(
            select(LineageNode).where(LineageNode.id.in_(affected_node_ids))
        )
        for node in nodes_result.scalars().all():
            affected_nodes.append({"id": str(node.id), "name": node.asset_name, "type": node.node_type.value})
            if node.node_type.value == "dashboard":
                affected_dashboards.append({"id": str(node.asset_id), "name": node.asset_name})
            elif node.node_type.value == "chart":
                affected_charts.append({"id": str(node.asset_id), "name": node.asset_name})

    return ImpactAnalysisResponse(
        source_node_id=request.source_node_id,
        change_type=request.change_type,
        affected_nodes=affected_nodes,
        affected_dashboards=affected_dashboards,
        affected_charts=affected_charts,
        total_affected=len(affected_nodes),
        critical_impacts=len(affected_dashboards)
    )


# =============================================================================
# VERSION CONTROL ENDPOINTS
# =============================================================================

@router.post("/versions", response_model=AssetVersionResponse, tags=["Version Control"])
async def create_version(
    version: AssetVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new version of an asset"""
    # Get current max version number
    result = await db.execute(
        select(func.max(AssetVersion.version_number)).where(
            AssetVersion.asset_type == version.asset_type,
            AssetVersion.asset_id == version.asset_id
        )
    )
    max_version = result.scalar() or 0

    # Mark previous versions as not current
    await db.execute(
        select(AssetVersion).where(
            AssetVersion.asset_type == version.asset_type,
            AssetVersion.asset_id == version.asset_id,
            AssetVersion.is_current == True
        )
    )

    db_version = AssetVersion(
        **version.model_dump(),
        version_number=max_version + 1,
        created_by=current_user.id
    )
    db.add(db_version)
    await db.commit()
    await db.refresh(db_version)
    return db_version


@router.get("/versions", response_model=List[AssetVersionResponse], tags=["Version Control"])
async def list_versions(
    asset_type: str,
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all versions of an asset"""
    result = await db.execute(
        select(AssetVersion).where(
            AssetVersion.asset_type == asset_type,
            AssetVersion.asset_id == asset_id
        ).order_by(AssetVersion.version_number.desc())
    )
    return result.scalars().all()


@router.get("/versions/{version_id}", response_model=AssetVersionResponse, tags=["Version Control"])
async def get_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific version"""
    result = await db.execute(select(AssetVersion).where(AssetVersion.id == version_id))
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.post("/versions/compare", response_model=VersionComparisonResponse, tags=["Version Control"])
async def compare_versions(
    request: VersionComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Compare two versions"""
    result_a = await db.execute(select(AssetVersion).where(AssetVersion.id == request.version_a_id))
    result_b = await db.execute(select(AssetVersion).where(AssetVersion.id == request.version_b_id))

    version_a = result_a.scalar_one_or_none()
    version_b = result_b.scalar_one_or_none()

    if not version_a or not version_b:
        raise HTTPException(status_code=404, detail="Version not found")

    # Simple comparison logic
    snapshot_a = version_a.snapshot or {}
    snapshot_b = version_b.snapshot or {}

    additions = []
    removals = []
    modifications = []

    all_keys = set(snapshot_a.keys()) | set(snapshot_b.keys())
    for key in all_keys:
        if key not in snapshot_a:
            additions.append({"key": key, "value": snapshot_b[key]})
        elif key not in snapshot_b:
            removals.append({"key": key, "value": snapshot_a[key]})
        elif snapshot_a[key] != snapshot_b[key]:
            modifications.append({"key": key, "old": snapshot_a[key], "new": snapshot_b[key]})

    return VersionComparisonResponse(
        version_a_id=request.version_a_id,
        version_b_id=request.version_b_id,
        additions=additions,
        removals=removals,
        modifications=modifications,
        total_changes=len(additions) + len(removals) + len(modifications),
        breaking_changes=len(removals) > 0
    )


@router.post("/versions/{version_id}/rollback", response_model=AssetVersionResponse, tags=["Version Control"])
async def rollback_to_version(
    version_id: UUID,
    request: RollbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Rollback to a specific version"""
    result = await db.execute(select(AssetVersion).where(AssetVersion.id == version_id))
    target_version = result.scalar_one_or_none()
    if not target_version:
        raise HTTPException(status_code=404, detail="Version not found")

    # Create new version from rollback target
    result = await db.execute(
        select(func.max(AssetVersion.version_number)).where(
            AssetVersion.asset_type == target_version.asset_type,
            AssetVersion.asset_id == target_version.asset_id
        )
    )
    max_version = result.scalar() or 0

    new_version = AssetVersion(
        workspace_id=target_version.workspace_id,
        asset_type=target_version.asset_type,
        asset_id=target_version.asset_id,
        asset_name=target_version.asset_name,
        version_number=max_version + 1,
        version_label=f"Rollback to v{target_version.version_number}",
        snapshot=target_version.snapshot,
        changes_summary=f"Rolled back to version {target_version.version_number}. Reason: {request.reason or 'Not specified'}",
        created_by=current_user.id,
        is_current=True
    )
    db.add(new_version)
    await db.commit()
    await db.refresh(new_version)
    return new_version


# =============================================================================
# DATA QUALITY ENDPOINTS
# =============================================================================

@router.post("/quality/rules", response_model=DataQualityRuleResponse, tags=["Data Quality"])
async def create_quality_rule(
    rule: DataQualityRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a data quality rule"""
    db_rule = DataQualityRule(**rule.model_dump(), created_by=current_user.id)
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.get("/quality/rules", response_model=List[DataQualityRuleResponse], tags=["Data Quality"])
async def list_quality_rules(
    workspace_id: UUID,
    connection_id: Optional[UUID] = None,
    table_name: Optional[str] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List data quality rules"""
    query = select(DataQualityRule).where(
        DataQualityRule.workspace_id == workspace_id,
        DataQualityRule.is_active == is_active
    )
    if connection_id:
        query = query.where(DataQualityRule.connection_id == connection_id)
    if table_name:
        query = query.where(DataQualityRule.table_name == table_name)
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/quality/rules/{rule_id}", response_model=DataQualityRuleResponse, tags=["Data Quality"])
async def update_quality_rule(
    rule_id: UUID,
    updates: DataQualityRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a data quality rule"""
    result = await db.execute(select(DataQualityRule).where(DataQualityRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)

    await db.commit()
    await db.refresh(rule)
    return rule


@router.post("/quality/rules/{rule_id}/run", response_model=DataQualityCheckResponse, tags=["Data Quality"])
async def run_quality_check(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Run a quality check for a specific rule"""
    result = await db.execute(select(DataQualityRule).where(DataQualityRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Create check record
    check = DataQualityCheck(
        rule_id=rule_id,
        workspace_id=rule.workspace_id,
        status=QualityCheckStatus.running,
        started_at=datetime.utcnow()
    )
    db.add(check)
    await db.commit()

    # TODO: Implement actual quality check logic based on rule_type
    # For now, simulate a passed check
    check.status = QualityCheckStatus.passed
    check.completed_at = datetime.utcnow()
    check.total_rows = 1000
    check.passed_rows = 950
    check.failed_rows = 50
    check.pass_rate = 95.0
    check.duration_ms = 1500

    rule.last_check_at = datetime.utcnow()

    await db.commit()
    await db.refresh(check)
    return check


@router.get("/quality/scores", response_model=List[DataQualityScoreResponse], tags=["Data Quality"])
async def get_quality_scores(
    workspace_id: UUID,
    connection_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get quality scores"""
    query = select(DataQualityScore).where(DataQualityScore.workspace_id == workspace_id)
    if connection_id:
        query = query.where(DataQualityScore.connection_id == connection_id)
    result = await db.execute(query.order_by(DataQualityScore.calculated_at.desc()))
    return result.scalars().all()


# =============================================================================
# SCHEMA TRACKING ENDPOINTS
# =============================================================================

@router.post("/schema/capture", response_model=SchemaSnapshotResponse, tags=["Schema Tracking"])
async def capture_schema(
    request: CaptureSchemaRequest,
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Capture current schema snapshot"""
    # TODO: Implement actual schema introspection
    # For now, create a placeholder snapshot
    tables_data = []  # Would be populated by schema introspection

    snapshot_hash = hashlib.sha256(json.dumps(tables_data, sort_keys=True).encode()).hexdigest()

    snapshot = SchemaSnapshot(
        connection_id=request.connection_id,
        workspace_id=workspace_id,
        tables=tables_data,
        snapshot_hash=snapshot_hash,
        tables_count=len(tables_data),
        columns_count=sum(len(t.get("columns", [])) for t in tables_data)
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot


@router.get("/schema/snapshots", response_model=List[SchemaSnapshotResponse], tags=["Schema Tracking"])
async def list_schema_snapshots(
    connection_id: UUID,
    workspace_id: UUID,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List schema snapshots for a connection"""
    result = await db.execute(
        select(SchemaSnapshot).where(
            SchemaSnapshot.connection_id == connection_id,
            SchemaSnapshot.workspace_id == workspace_id
        ).order_by(SchemaSnapshot.captured_at.desc()).limit(limit)
    )
    return result.scalars().all()


@router.get("/schema/changes", response_model=List[SchemaChangeResponse], tags=["Schema Tracking"])
async def list_schema_changes(
    workspace_id: UUID,
    connection_id: Optional[UUID] = None,
    acknowledged: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List detected schema changes"""
    query = select(SchemaChange).where(SchemaChange.workspace_id == workspace_id)
    if connection_id:
        query = query.where(SchemaChange.connection_id == connection_id)
    if acknowledged is not None:
        query = query.where(SchemaChange.acknowledged == acknowledged)
    result = await db.execute(query.order_by(SchemaChange.detected_at.desc()))
    return result.scalars().all()


@router.post("/schema/changes/acknowledge", tags=["Schema Tracking"])
async def acknowledge_schema_changes(
    request: AcknowledgeSchemaChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Acknowledge schema changes"""
    for change_id in request.change_ids:
        result = await db.execute(select(SchemaChange).where(SchemaChange.id == change_id))
        change = result.scalar_one_or_none()
        if change:
            change.acknowledged = True

    await db.commit()
    return {"acknowledged": len(request.change_ids)}


# =============================================================================
# APPS ENDPOINTS
# =============================================================================

@router.post("/apps", response_model=AppResponse, tags=["Apps"])
async def create_app(
    app: AppCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new app bundle"""
    db_app = App(**app.model_dump(), created_by=current_user.id)
    db.add(db_app)
    await db.commit()
    await db.refresh(db_app)
    return db_app


@router.get("/apps", response_model=List[AppResponse], tags=["Apps"])
async def list_apps(
    workspace_id: UUID,
    status: Optional[AppStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List apps in a workspace"""
    query = select(App).where(App.workspace_id == workspace_id)
    if status:
        query = query.where(App.status == status)
    result = await db.execute(query.order_by(App.created_at.desc()))
    return result.scalars().all()


@router.get("/apps/{app_id}", response_model=AppResponse, tags=["Apps"])
async def get_app(
    app_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get an app by ID"""
    result = await db.execute(select(App).where(App.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    # Increment view count
    app.view_count += 1
    await db.commit()
    await db.refresh(app)
    return app


@router.put("/apps/{app_id}", response_model=AppResponse, tags=["Apps"])
async def update_app(
    app_id: UUID,
    updates: AppUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an app"""
    result = await db.execute(select(App).where(App.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(app, key, value)

    await db.commit()
    await db.refresh(app)
    return app


@router.post("/apps/{app_id}/publish", response_model=AppResponse, tags=["Apps"])
async def publish_app(
    app_id: UUID,
    request: AppPublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Publish an app"""
    result = await db.execute(select(App).where(App.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    app.status = AppStatus.published
    app.published_at = datetime.utcnow()
    app.published_by = current_user.id
    if request.version:
        app.version = request.version

    await db.commit()
    await db.refresh(app)
    return app


@router.post("/apps/{app_id}/install", response_model=AppInstallationResponse, tags=["Apps"])
async def install_app(
    app_id: UUID,
    target_workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Install an app to a workspace"""
    result = await db.execute(select(App).where(App.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")

    installation = AppInstallation(
        app_id=app_id,
        installed_by=current_user.id,
        target_workspace_id=target_workspace_id
    )
    db.add(installation)

    app.install_count += 1

    await db.commit()
    await db.refresh(installation)
    return installation


# =============================================================================
# USER ANALYTICS ENDPOINTS
# =============================================================================

@router.get("/analytics/users", response_model=List[UserAnalyticsResponse], tags=["Analytics"])
async def get_user_analytics(
    workspace_id: UUID,
    period_type: str = "daily",
    user_id: Optional[UUID] = None,
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user analytics"""
    query = select(UserAnalytics).where(
        UserAnalytics.workspace_id == workspace_id,
        UserAnalytics.period_type == period_type
    )
    if user_id:
        query = query.where(UserAnalytics.user_id == user_id)
    result = await db.execute(query.order_by(UserAnalytics.period_start.desc()).limit(limit))
    return result.scalars().all()


@router.get("/analytics/features", response_model=List[FeatureAdoptionResponse], tags=["Analytics"])
async def get_feature_adoption(
    workspace_id: UUID,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get feature adoption metrics"""
    result = await db.execute(
        select(FeatureAdoption).where(
            FeatureAdoption.workspace_id == workspace_id
        ).order_by(FeatureAdoption.adoption_rate.desc()).limit(limit)
    )
    return result.scalars().all()


@router.get("/analytics/content", response_model=List[ContentPopularityResponse], tags=["Analytics"])
async def get_content_popularity(
    workspace_id: UUID,
    content_type: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get content popularity metrics"""
    query = select(ContentPopularity).where(ContentPopularity.workspace_id == workspace_id)
    if content_type:
        query = query.where(ContentPopularity.content_type == content_type)
    result = await db.execute(query.order_by(ContentPopularity.popularity_score.desc()).limit(limit))
    return result.scalars().all()


@router.get("/analytics/dashboard", response_model=AnalyticsDashboardResponse, tags=["Analytics"])
async def get_analytics_dashboard(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get comprehensive analytics dashboard data"""
    # Get user counts
    user_analytics = await db.execute(
        select(UserAnalytics).where(
            UserAnalytics.workspace_id == workspace_id,
            UserAnalytics.period_type == "daily"
        ).order_by(UserAnalytics.period_start.desc()).limit(30)
    )
    user_data = user_analytics.scalars().all()

    # Get feature adoption
    features = await db.execute(
        select(FeatureAdoption).where(
            FeatureAdoption.workspace_id == workspace_id
        ).order_by(FeatureAdoption.adoption_rate.desc()).limit(10)
    )
    feature_data = features.scalars().all()

    # Get content popularity
    content = await db.execute(
        select(ContentPopularity).where(
            ContentPopularity.workspace_id == workspace_id
        ).order_by(ContentPopularity.popularity_score.desc()).limit(10)
    )
    content_data = content.scalars().all()

    # Calculate totals
    total_users = len(set(u.user_id for u in user_data))
    active_users = sum(1 for u in user_data if u.sessions_count > 0)
    total_dashboards = sum(u.dashboards_viewed for u in user_data)
    total_charts = sum(u.charts_viewed for u in user_data)
    total_queries = sum(u.queries_executed for u in user_data)
    avg_duration = sum(u.total_duration_seconds for u in user_data) // max(len(user_data), 1)

    return AnalyticsDashboardResponse(
        total_users=total_users,
        active_users=active_users,
        total_dashboards=total_dashboards,
        total_charts=total_charts,
        total_queries=total_queries,
        avg_session_duration=avg_duration,
        top_features=feature_data,
        top_content=content_data,
        user_activity=user_data
    )
