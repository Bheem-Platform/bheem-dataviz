"""
Drill API Endpoints

Provides endpoints for drill-down and drillthrough operations.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.dashboard import Dashboard, SavedChart
from app.schemas.drill import (
    DrillDirection,
    DrillHierarchy,
    DrillHierarchyLevel,
    DrillPath,
    DrillRequest,
    DrillResponse,
    DrillthroughRequest,
    DrillthroughResponse,
    ChartDrillConfig,
    ChartDrillState,
    DashboardDrillState,
)
from app.services.drill_service import get_drill_service

router = APIRouter()


@router.post("/execute", response_model=DrillResponse)
async def execute_drill(
    request: DrillRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Execute a drill operation on a chart.

    - **chart_id**: ID of the chart to drill
    - **hierarchy_id**: ID of the hierarchy to use
    - **direction**: up or down
    - **clicked_value**: Value that was clicked (for drill-down)
    - **current_path**: Current drill path state
    """
    # Get the chart
    chart = db.query(SavedChart).filter(SavedChart.id == request.chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    # Get drill configuration
    drill_config = chart.drill_config or {}
    if not drill_config.get("drill_enabled", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drill is not enabled for this chart",
        )

    # Find the hierarchy
    hierarchies = drill_config.get("hierarchies", [])
    hierarchy_dict = next(
        (h for h in hierarchies if h.get("id") == request.hierarchy_id),
        None,
    )

    if not hierarchy_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hierarchy '{request.hierarchy_id}' not found",
        )

    # Convert to DrillHierarchy model
    hierarchy = DrillHierarchy(
        id=hierarchy_dict["id"],
        name=hierarchy_dict["name"],
        levels=[
            DrillHierarchyLevel(**level)
            for level in hierarchy_dict.get("levels", [])
        ],
        default_level=hierarchy_dict.get("default_level", 0),
    )

    # Get the base query from chart config
    chart_config = chart.config or {}
    base_query = chart_config.get("query", "")

    if not base_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart has no query configured",
        )

    # Execute drill operation
    drill_service = get_drill_service()
    response = drill_service.execute_drill(
        request=request,
        hierarchy=hierarchy,
        base_query=base_query,
        connection_params={},  # Would come from connection
    )

    return response


@router.post("/drillthrough", response_model=DrillthroughResponse)
async def execute_drillthrough(
    request: DrillthroughRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Execute a drillthrough operation.

    - **source_chart_id**: ID of the source chart
    - **target_id**: ID of the drillthrough target
    - **clicked_data**: Data from the clicked element
    - **current_filters**: Current dashboard filters to pass through
    """
    # Get the source chart
    chart = db.query(SavedChart).filter(SavedChart.id == request.source_chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    # Get drillthrough configuration
    drill_config = chart.drill_config or {}
    drillthrough_config = drill_config.get("drillthrough", {})

    if not drillthrough_config.get("enabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drillthrough is not enabled for this chart",
        )

    # Find the target
    targets = drillthrough_config.get("targets", [])
    target = next(
        (t for t in targets if t.get("id") == request.target_id),
        None,
    )

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drillthrough target '{request.target_id}' not found",
        )

    # Execute drillthrough
    drill_service = get_drill_service()
    response = drill_service.execute_drillthrough(
        request=request,
        target_config=target,
    )

    return response


@router.get("/config/{chart_id}", response_model=ChartDrillConfig)
async def get_chart_drill_config(
    chart_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get drill configuration for a chart.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    drill_config = chart.drill_config or {}

    return ChartDrillConfig(
        drill_enabled=drill_config.get("drill_enabled", True),
        hierarchies=[
            DrillHierarchy(
                id=h["id"],
                name=h["name"],
                levels=[DrillHierarchyLevel(**l) for l in h.get("levels", [])],
                default_level=h.get("default_level", 0),
            )
            for h in drill_config.get("hierarchies", [])
        ],
        default_hierarchy_id=drill_config.get("default_hierarchy_id"),
        drillthrough=drill_config.get("drillthrough"),
        show_drill_buttons=drill_config.get("show_drill_buttons", True),
        show_breadcrumbs=drill_config.get("show_breadcrumbs", True),
        allow_multi_level_expand=drill_config.get("allow_multi_level_expand", False),
    )


@router.put("/config/{chart_id}")
async def update_chart_drill_config(
    chart_id: str,
    config: ChartDrillConfig,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update drill configuration for a chart.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    # Convert config to dict for storage
    chart.drill_config = config.model_dump()
    db.commit()

    return {"success": True, "message": "Drill configuration updated"}


@router.get("/hierarchies/templates")
async def get_hierarchy_templates(
    current_user: dict = Depends(get_current_user),
):
    """
    Get pre-built hierarchy templates for common use cases.
    """
    drill_service = get_drill_service()
    return drill_service.get_common_hierarchies()


@router.post("/hierarchies/create")
async def create_hierarchy_from_columns(
    hierarchy_id: str,
    hierarchy_name: str,
    columns: list[dict[str, Any]],
    current_user: dict = Depends(get_current_user),
):
    """
    Create a custom hierarchy from column definitions.

    - **hierarchy_id**: Unique ID for the hierarchy
    - **hierarchy_name**: Display name
    - **columns**: List of column configs with name, label, sort_order, format
    """
    drill_service = get_drill_service()
    hierarchy = drill_service.create_hierarchy_from_columns(
        columns=columns,
        hierarchy_id=hierarchy_id,
        hierarchy_name=hierarchy_name,
    )

    return hierarchy.model_dump()


@router.get("/breadcrumbs/{chart_id}")
async def get_drill_breadcrumbs(
    chart_id: str,
    hierarchy_id: str,
    drill_path: str = None,  # JSON-encoded drill path
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get formatted breadcrumbs for a chart's current drill state.
    """
    import json

    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    drill_config = chart.drill_config or {}
    hierarchies = drill_config.get("hierarchies", [])

    hierarchy_dict = next(
        (h for h in hierarchies if h.get("id") == hierarchy_id),
        None,
    )

    if not hierarchy_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hierarchy not found",
        )

    hierarchy = DrillHierarchy(
        id=hierarchy_dict["id"],
        name=hierarchy_dict["name"],
        levels=[DrillHierarchyLevel(**l) for l in hierarchy_dict.get("levels", [])],
        default_level=hierarchy_dict.get("default_level", 0),
    )

    # Parse drill path
    if drill_path:
        try:
            path_dict = json.loads(drill_path)
            path = DrillPath(**path_dict)
        except Exception:
            path = DrillPath(
                hierarchy_id=hierarchy_id,
                current_level=0,
                filters={},
                breadcrumbs=[],
            )
    else:
        path = DrillPath(
            hierarchy_id=hierarchy_id,
            current_level=0,
            filters={},
            breadcrumbs=[],
        )

    drill_service = get_drill_service()
    breadcrumbs = drill_service.get_drill_breadcrumbs(path, hierarchy)

    return {"breadcrumbs": breadcrumbs}


@router.get("/state/dashboard/{dashboard_id}", response_model=DashboardDrillState)
async def get_dashboard_drill_state(
    dashboard_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get drill state for all charts in a dashboard.
    """
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    # Get stored drill state or return empty state
    drill_state = dashboard.default_filters or {}
    drill_states = drill_state.get("drill_states", {})

    return DashboardDrillState(
        dashboard_id=dashboard_id,
        chart_states={
            chart_id: ChartDrillState(**state)
            for chart_id, state in drill_states.items()
        },
        global_drill_path=drill_state.get("global_drill_path"),
        sync_drill=drill_state.get("sync_drill", False),
    )


@router.put("/state/dashboard/{dashboard_id}")
async def save_dashboard_drill_state(
    dashboard_id: str,
    state: DashboardDrillState,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Save drill state for a dashboard.
    """
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    # Update the drill states in default_filters
    filters = dashboard.default_filters or {}
    filters["drill_states"] = {
        chart_id: cs.model_dump()
        for chart_id, cs in state.chart_states.items()
    }
    filters["global_drill_path"] = state.global_drill_path.model_dump() if state.global_drill_path else None
    filters["sync_drill"] = state.sync_drill

    dashboard.default_filters = filters
    db.commit()

    return {"success": True, "message": "Drill state saved"}


@router.delete("/state/dashboard/{dashboard_id}")
async def clear_dashboard_drill_state(
    dashboard_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Clear drill state for a dashboard.
    """
    dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    # Clear drill states
    filters = dashboard.default_filters or {}
    filters.pop("drill_states", None)
    filters.pop("global_drill_path", None)
    filters.pop("sync_drill", None)

    dashboard.default_filters = filters
    db.commit()

    return {"success": True, "message": "Drill state cleared"}
