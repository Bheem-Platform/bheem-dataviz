"""Filter API endpoints for advanced slicers and filter management."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.dashboard import (
    Dashboard, SavedChart, SavedFilterPreset, DashboardFilterState
)
from app.models.connection import Connection as ConnectionModel, ConnectionType
from app.models.semantic import SemanticModel
from app.models.transform import TransformRecipe
from app.models.user import User
from app.schemas.filter import (
    FilterCondition, FilterOptionsResponse, MultiColumnFilterOptionsResponse,
    SlicerConfig, GlobalFilterConfig, ApplyFiltersRequest,
    SaveFiltersRequest, SavedFilterPreset as SavedFilterPresetSchema,
    DashboardFilterState as DashboardFilterStateSchema,
    FilterType, RelativeDateFilter, DateRangeFilter
)
from app.services.filter_service import get_filter_service
from app.services.postgres_service import postgres_service
from app.services.mysql_service import MySQLService
from app.services.encryption_service import encryption_service
from app.services.transform_service import get_transform_service
from app.core.security import get_current_user
from pydantic import BaseModel
import uuid as uuid_module

router = APIRouter()


# ============== Helper Functions ==============

async def get_connection_and_service(connection_id: str, db: AsyncSession):
    """Get connection and appropriate filter service."""
    try:
        conn_uuid = uuid_module.UUID(connection_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid connection ID format")

    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == conn_uuid)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    conn_type = conn.type.value if hasattr(conn.type, 'value') else str(conn.type)
    filter_service = get_filter_service(conn_type)

    return conn, filter_service, conn_type


async def execute_query_on_connection(conn: ConnectionModel, sql: str, limit: int = 100) -> Dict[str, Any]:
    """Execute a query on a connection and return results."""
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    if conn.type == ConnectionType.postgresql:
        conn_str = postgres_service.build_connection_string(
            host=conn.host or "localhost",
            port=conn.port or 5432,
            database=conn.database_name or "",
            username=conn.username,
            password=password,
            extra=conn.additional_config
        )
        return await postgres_service.execute_query(conn_str, sql, limit)

    elif conn.type == ConnectionType.mysql:
        return await MySQLService.execute_query(
            host=conn.host or "localhost",
            port=conn.port or 3306,
            database=conn.database_name or "",
            sql=sql,
            username=conn.username,
            password=password,
            limit=limit
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Filter options not supported for connection type: {conn.type.value}"
        )


# ============== Filter Options Endpoints ==============

@router.get("/options/{connection_id}/{schema_name}/{table_name}/{column_name}", response_model=FilterOptionsResponse)
async def get_filter_options_for_column(
    connection_id: str,
    schema_name: str,
    table_name: str,
    column_name: str,
    search: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get distinct values for a column to populate filter options.

    Returns counts for each value to show distribution.
    Supports search to filter values in large datasets.
    """
    conn, filter_service, conn_type = await get_connection_and_service(connection_id, db)

    async def execute_fn(sql: str, lim: int):
        return await execute_query_on_connection(conn, sql, lim)

    return await filter_service.get_filter_options(
        execute_query_fn=execute_fn,
        table=table_name,
        schema=schema_name,
        column=column_name,
        search=search,
        limit=limit
    )


@router.post("/options/{connection_id}/{schema_name}/{table_name}", response_model=MultiColumnFilterOptionsResponse)
async def get_filter_options_for_multiple_columns(
    connection_id: str,
    schema_name: str,
    table_name: str,
    columns: List[str],
    existing_filters: Optional[List[FilterCondition]] = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get filter options for multiple columns at once.

    Useful for initializing a filter panel with multiple slicers.
    Existing filters are applied to show contextual options.
    """
    conn, filter_service, conn_type = await get_connection_and_service(connection_id, db)

    async def execute_fn(sql: str, lim: int):
        return await execute_query_on_connection(conn, sql, lim)

    results = {}
    for column in columns[:10]:  # Limit to 10 columns
        try:
            options = await filter_service.get_filter_options(
                execute_query_fn=execute_fn,
                table=table_name,
                schema=schema_name,
                column=column,
                limit=limit,
                existing_filters=existing_filters
            )
            results[column] = options
        except Exception:
            # Skip columns that fail
            pass

    return MultiColumnFilterOptionsResponse(columns=results)


@router.get("/options/chart/{chart_id}", response_model=MultiColumnFilterOptionsResponse)
async def get_filter_options_for_chart(
    chart_id: UUID,
    columns: Optional[List[str]] = Query(default=None),
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get filter options for a chart based on its data source.

    Automatically determines the columns from semantic model dimensions
    or transform columns if columns are not specified.
    """
    # Get the chart
    result = await db.execute(
        select(SavedChart).where(SavedChart.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    conn, filter_service, conn_type = await get_connection_and_service(chart.connection_id, db)

    async def execute_fn(sql: str, lim: int):
        return await execute_query_on_connection(conn, sql, lim)

    # Determine schema, table, and columns
    schema_name = "public"
    table_name = None
    filter_columns = columns or []

    if chart.semantic_model_id:
        # Get columns from semantic model dimensions
        model_result = await db.execute(
            select(SemanticModel)
            .options(selectinload(SemanticModel.dimensions))
            .where(SemanticModel.id == chart.semantic_model_id)
        )
        model = model_result.scalar_one_or_none()

        if model:
            schema_name = model.schema_name or "public"
            table_name = model.table_name

            if not filter_columns:
                filter_columns = [d.column_name for d in model.dimensions[:10]]

    elif chart.transform_recipe_id:
        # Get columns from transform result
        transform_result = await db.execute(
            select(TransformRecipe).where(TransformRecipe.id == chart.transform_recipe_id)
        )
        transform = transform_result.scalar_one_or_none()

        if transform:
            schema_name = transform.source_schema or "public"
            table_name = transform.source_table

            if transform.result_columns and not filter_columns:
                filter_columns = [c.get("name") for c in transform.result_columns[:10] if c.get("name")]

    elif chart.query_config:
        schema_name = chart.query_config.get("schema", "public")
        table_name = chart.query_config.get("table")

        if not filter_columns:
            dims = chart.query_config.get("dimensions", [])
            filter_columns = [
                d.get("column", d) if isinstance(d, dict) else d
                for d in dims[:10]
            ]

    if not table_name:
        raise HTTPException(status_code=400, detail="Could not determine table for chart")

    # Get options for each column
    results = {}
    for column in filter_columns[:10]:
        try:
            options = await filter_service.get_filter_options(
                execute_query_fn=execute_fn,
                table=table_name,
                schema=schema_name,
                column=column,
                limit=limit
            )
            results[column] = options
        except Exception:
            pass

    return MultiColumnFilterOptionsResponse(columns=results)


# ============== Filter Preset Endpoints ==============

@router.get("/presets", response_model=List[SavedFilterPresetSchema])
async def list_filter_presets(
    dashboard_id: Optional[UUID] = None,
    chart_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List saved filter presets."""
    query = select(SavedFilterPreset)

    if dashboard_id:
        query = query.where(SavedFilterPreset.dashboard_id == dashboard_id)
    if chart_id:
        query = query.where(SavedFilterPreset.chart_id == chart_id)

    result = await db.execute(query.order_by(SavedFilterPreset.name))
    return result.scalars().all()


@router.post("/presets", response_model=SavedFilterPresetSchema)
async def create_filter_preset(
    request: SaveFiltersRequest,
    dashboard_id: Optional[UUID] = None,
    chart_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new filter preset."""
    # If this is set as default, unset other defaults
    if request.is_default:
        query = select(SavedFilterPreset).where(SavedFilterPreset.is_default == True)
        if dashboard_id:
            query = query.where(SavedFilterPreset.dashboard_id == dashboard_id)
        if chart_id:
            query = query.where(SavedFilterPreset.chart_id == chart_id)

        result = await db.execute(query)
        for preset in result.scalars().all():
            preset.is_default = False

    preset = SavedFilterPreset(
        name=request.name,
        description=request.description,
        dashboard_id=dashboard_id,
        chart_id=chart_id,
        filters=[f.model_dump() for f in request.filters],
        slicers=[s.model_dump() for s in request.slicers] if request.slicers else None,
        is_default=request.is_default,
        created_by=current_user.id if current_user else None
    )

    db.add(preset)
    await db.commit()
    await db.refresh(preset)

    return preset


@router.get("/presets/{preset_id}", response_model=SavedFilterPresetSchema)
async def get_filter_preset(
    preset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a filter preset by ID."""
    result = await db.execute(
        select(SavedFilterPreset).where(SavedFilterPreset.id == preset_id)
    )
    preset = result.scalar_one_or_none()

    if not preset:
        raise HTTPException(status_code=404, detail="Filter preset not found")

    return preset


@router.put("/presets/{preset_id}", response_model=SavedFilterPresetSchema)
async def update_filter_preset(
    preset_id: UUID,
    request: SaveFiltersRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a filter preset."""
    result = await db.execute(
        select(SavedFilterPreset).where(SavedFilterPreset.id == preset_id)
    )
    preset = result.scalar_one_or_none()

    if not preset:
        raise HTTPException(status_code=404, detail="Filter preset not found")

    preset.name = request.name
    preset.description = request.description
    preset.filters = [f.model_dump() for f in request.filters]
    preset.slicers = [s.model_dump() for s in request.slicers] if request.slicers else None
    preset.is_default = request.is_default
    preset.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(preset)

    return preset


@router.delete("/presets/{preset_id}")
async def delete_filter_preset(
    preset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a filter preset."""
    result = await db.execute(
        select(SavedFilterPreset).where(SavedFilterPreset.id == preset_id)
    )
    preset = result.scalar_one_or_none()

    if not preset:
        raise HTTPException(status_code=404, detail="Filter preset not found")

    await db.delete(preset)
    await db.commit()

    return {"status": "deleted"}


# ============== Dashboard Filter State Endpoints ==============

@router.get("/state/{dashboard_id}", response_model=DashboardFilterStateSchema)
async def get_dashboard_filter_state(
    dashboard_id: UUID,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current filter state for a dashboard."""
    query = select(DashboardFilterState).where(
        DashboardFilterState.dashboard_id == dashboard_id
    )

    if current_user:
        query = query.where(DashboardFilterState.user_id == current_user.id)
    elif session_id:
        query = query.where(DashboardFilterState.session_id == session_id)

    result = await db.execute(query.order_by(DashboardFilterState.updated_at.desc()).limit(1))
    state = result.scalar_one_or_none()

    if not state:
        # Return empty state
        return DashboardFilterStateSchema(
            dashboard_id=dashboard_id,
            filters={},
            updated_at=datetime.utcnow()
        )

    return DashboardFilterStateSchema(
        dashboard_id=state.dashboard_id,
        filters=state.filter_state or {},
        date_filters=state.date_filter_state or {},
        updated_at=state.updated_at
    )


class UpdateFilterStateRequest(BaseModel):
    """Request to update filter state."""
    filters: Dict[str, Any]
    date_filters: Optional[Dict[str, Any]] = None
    cross_filter_state: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


@router.put("/state/{dashboard_id}", response_model=DashboardFilterStateSchema)
async def update_dashboard_filter_state(
    dashboard_id: UUID,
    request: UpdateFilterStateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the filter state for a dashboard."""
    # Find existing state or create new
    query = select(DashboardFilterState).where(
        DashboardFilterState.dashboard_id == dashboard_id
    )

    if current_user:
        query = query.where(DashboardFilterState.user_id == current_user.id)
    elif request.session_id:
        query = query.where(DashboardFilterState.session_id == request.session_id)

    result = await db.execute(query.limit(1))
    state = result.scalar_one_or_none()

    if state:
        state.filter_state = request.filters
        state.date_filter_state = request.date_filters
        state.cross_filter_state = request.cross_filter_state
        state.updated_at = datetime.utcnow()
    else:
        state = DashboardFilterState(
            dashboard_id=dashboard_id,
            user_id=current_user.id if current_user else None,
            filter_state=request.filters,
            date_filter_state=request.date_filters,
            cross_filter_state=request.cross_filter_state,
            session_id=request.session_id
        )
        db.add(state)

    await db.commit()
    await db.refresh(state)

    return DashboardFilterStateSchema(
        dashboard_id=state.dashboard_id,
        filters=state.filter_state or {},
        date_filters=state.date_filter_state or {},
        updated_at=state.updated_at
    )


@router.delete("/state/{dashboard_id}")
async def clear_dashboard_filter_state(
    dashboard_id: UUID,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear the filter state for a dashboard."""
    query = select(DashboardFilterState).where(
        DashboardFilterState.dashboard_id == dashboard_id
    )

    if current_user:
        query = query.where(DashboardFilterState.user_id == current_user.id)
    elif session_id:
        query = query.where(DashboardFilterState.session_id == session_id)

    result = await db.execute(query)
    for state in result.scalars().all():
        await db.delete(state)

    await db.commit()

    return {"status": "cleared"}


# ============== Slicer Configuration Endpoints ==============

class SlicerConfigRequest(BaseModel):
    """Request to update slicer configuration."""
    slicers: List[SlicerConfig]


@router.put("/dashboard/{dashboard_id}/slicers")
async def update_dashboard_slicers(
    dashboard_id: UUID,
    request: SlicerConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the slicer configuration for a dashboard."""
    result = await db.execute(
        select(Dashboard).where(Dashboard.id == dashboard_id)
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Update global filter config
    config = dashboard.global_filter_config or {}
    config["slicers"] = [s.model_dump() for s in request.slicers]
    dashboard.global_filter_config = config
    dashboard.updated_at = datetime.utcnow()

    await db.commit()

    return {"status": "updated", "slicer_count": len(request.slicers)}


@router.get("/dashboard/{dashboard_id}/slicers", response_model=List[SlicerConfig])
async def get_dashboard_slicers(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the slicer configuration for a dashboard."""
    result = await db.execute(
        select(Dashboard).where(Dashboard.id == dashboard_id)
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    config = dashboard.global_filter_config or {}
    slicers_data = config.get("slicers", [])

    return [SlicerConfig(**s) for s in slicers_data]
