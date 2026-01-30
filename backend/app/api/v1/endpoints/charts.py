"""Chart API endpoints with data rendering."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
import time

from app.database import get_db
from app.models.dashboard import SavedChart as SavedChartModel
from app.models.connection import Connection as ConnectionModel, ConnectionType
from app.models.semantic import SemanticModel, Dimension, Measure
from app.models.transform import TransformRecipe
from app.models.user import User
from app.schemas.dashboard import SavedChart, SavedChartCreate, SavedChartUpdate
from app.services.postgres_service import postgres_service
from app.services.mysql_service import MySQLService
from app.services.mongodb_service import mongodb_service
from app.services.encryption_service import encryption_service
from app.services.transform_service import get_transform_service
from app.core.config import settings
from app.core.security import get_current_user
from pydantic import BaseModel
import uuid as uuid_module


router = APIRouter()


# ============== Response Schemas ==============

class ChartDataResponse(BaseModel):
    """Response containing chart data."""
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    sql_generated: Optional[str] = None
    execution_time_ms: float
    chart_config: Dict[str, Any]
    chart_type: str


class ChartRenderRequest(BaseModel):
    """Optional filters/parameters for chart rendering."""
    filters: Optional[Dict[str, Any]] = None
    limit: int = 1000


# ============== Helper Functions ==============

async def execute_query_on_connection(
    conn: ConnectionModel,
    sql: str,
    limit: int = 1000,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Execute SQL on a connection and return results."""
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

    elif conn.type == ConnectionType.mongodb:
        # MongoDB doesn't use SQL, this function shouldn't be called for MongoDB
        # MongoDB charts should use execute_mongodb_aggregation instead
        raise HTTPException(
            status_code=400,
            detail="Use execute_mongodb_aggregation for MongoDB connections"
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Query execution not supported for connection type: {conn.type.value}"
        )


async def execute_mongodb_aggregation(
    conn: ConnectionModel,
    query_config: Dict[str, Any],
    limit: int = 1000
) -> Dict[str, Any]:
    """Execute MongoDB aggregation and return results."""
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    additional = conn.additional_config or {}

    # Build aggregation pipeline from query_config
    collection = query_config.get("table")
    dimensions = query_config.get("dimensions", [])
    measures = query_config.get("measures", [])

    if not collection:
        raise HTTPException(status_code=400, detail="query_config must include 'table' (collection name)")

    # Build MongoDB aggregation pipeline
    pipeline = []

    # Group stage
    group_id = {}
    group_accumulators = {}

    for dim in dimensions:
        if isinstance(dim, dict):
            col = dim.get("column", dim.get("name", ""))
            alias = dim.get("alias", col)
        else:
            col = dim
            alias = dim
        group_id[alias] = f"${col}"

    for measure in measures:
        if isinstance(measure, dict):
            col = measure.get("column", measure.get("name", ""))
            agg = measure.get("aggregation", "sum").lower()
            alias = measure.get("alias", f"{agg}_{col}")
        else:
            col = measure
            agg = "sum"
            alias = f"sum_{col}"

        if agg == "sum":
            group_accumulators[alias] = {"$sum": f"${col}"}
        elif agg == "avg":
            group_accumulators[alias] = {"$avg": f"${col}"}
        elif agg == "count":
            group_accumulators[alias] = {"$sum": 1}
        elif agg == "count_distinct":
            group_accumulators[alias] = {"$addToSet": f"${col}"}
        elif agg == "min":
            group_accumulators[alias] = {"$min": f"${col}"}
        elif agg == "max":
            group_accumulators[alias] = {"$max": f"${col}"}

    if group_id or group_accumulators:
        pipeline.append({"$group": {"_id": group_id if group_id else None, **group_accumulators}})

    # Project stage to flatten results
    if group_id:
        project = {}
        for alias in group_id.keys():
            project[alias] = f"$_id.{alias}"
        for alias in group_accumulators.keys():
            if "addToSet" in str(group_accumulators.get(alias, {})):
                project[alias] = {"$size": f"${alias}"}
            else:
                project[alias] = 1
        project["_id"] = 0
        pipeline.append({"$project": project})

    # Limit stage
    pipeline.append({"$limit": limit})

    # Execute aggregation
    result = await mongodb_service.execute_aggregation(
        host=conn.host or "localhost",
        port=conn.port or 27017,
        database=conn.database_name or "",
        collection=collection,
        pipeline=pipeline,
        username=conn.username,
        password=password,
        auth_source=additional.get("auth_source"),
        is_srv=additional.get("is_srv", False),
        ssl=additional.get("ssl", False)
    )

    return result


def build_query_from_config(
    query_config: Dict[str, Any],
    conn_type: str = "postgresql"
) -> str:
    """Build SQL query from query_config."""
    quote = '`' if conn_type == "mysql" else '"'

    schema = query_config.get("schema", "public")
    table = query_config.get("table")
    dimensions = query_config.get("dimensions", [])
    measures = query_config.get("measures", [])
    filters = query_config.get("filters", [])
    order_by = query_config.get("order_by", [])
    limit = query_config.get("limit", 1000)

    if not table:
        raise HTTPException(status_code=400, detail="query_config must include 'table'")

    # Build SELECT clause
    select_parts = []

    for dim in dimensions:
        if isinstance(dim, dict):
            col = dim.get("column", dim.get("name", ""))
            alias = dim.get("alias", col)
            select_parts.append(f'{quote}{col}{quote} AS {quote}{alias}{quote}')
        else:
            select_parts.append(f'{quote}{dim}{quote}')

    for measure in measures:
        if isinstance(measure, dict):
            col = measure.get("column", measure.get("name", ""))
            agg = measure.get("aggregation", "sum").upper()
            alias = measure.get("alias", f"{agg.lower()}_{col}")
            if agg == "COUNT_DISTINCT":
                select_parts.append(f'COUNT(DISTINCT {quote}{col}{quote}) AS {quote}{alias}{quote}')
            else:
                select_parts.append(f'{agg}({quote}{col}{quote}) AS {quote}{alias}{quote}')
        else:
            select_parts.append(f'SUM({quote}{measure}{quote})')

    if not select_parts:
        select_parts = ["*"]

    # Build FROM clause
    from_clause = f'{quote}{schema}{quote}.{quote}{table}{quote}'

    # Build WHERE clause
    where_parts = []
    for f in filters:
        if isinstance(f, dict):
            col = f.get("column")
            op = f.get("operator", "=")
            val = f.get("value")
            if col and val is not None:
                if op.lower() in ("is_null", "is null"):
                    where_parts.append(f'{quote}{col}{quote} IS NULL')
                elif op.lower() in ("is_not_null", "is not null"):
                    where_parts.append(f'{quote}{col}{quote} IS NOT NULL')
                elif op.lower() == "like":
                    where_parts.append(f'{quote}{col}{quote} LIKE \'%{val}%\'')
                elif op.lower() == "in":
                    if isinstance(val, list):
                        vals = ", ".join([f"'{v}'" for v in val])
                        where_parts.append(f'{quote}{col}{quote} IN ({vals})')
                else:
                    if isinstance(val, str):
                        where_parts.append(f'{quote}{col}{quote} {op} \'{val}\'')
                    else:
                        where_parts.append(f'{quote}{col}{quote} {op} {val}')

    # Build GROUP BY (if we have both dimensions and measures)
    group_by = ""
    if dimensions and measures:
        group_cols = []
        for dim in dimensions:
            if isinstance(dim, dict):
                group_cols.append(f'{quote}{dim.get("column", dim.get("name", ""))}{quote}')
            else:
                group_cols.append(f'{quote}{dim}{quote}')
        group_by = f'GROUP BY {", ".join(group_cols)}'

    # Build ORDER BY
    order_parts = []
    for o in order_by:
        if isinstance(o, dict):
            col = o.get("column")
            direction = o.get("direction", "ASC").upper()
            order_parts.append(f'{quote}{col}{quote} {direction}')
        else:
            order_parts.append(f'{quote}{o}{quote}')

    # Assemble query
    sql = f'SELECT {", ".join(select_parts)} FROM {from_clause}'
    if where_parts:
        sql += f' WHERE {" AND ".join(where_parts)}'
    if group_by:
        sql += f' {group_by}'
    if order_parts:
        sql += f' ORDER BY {", ".join(order_parts)}'
    sql += f' LIMIT {limit}'

    return sql


async def build_semantic_model_query(
    model: SemanticModel,
    dimension_ids: List[str],
    measure_ids: List[str],
    conn_type: str,
    db: AsyncSession,
    filters: Optional[List[Dict[str, Any]]] = None
) -> str:
    """Build SQL query from semantic model."""
    quote = '`' if conn_type == "mysql" else '"'

    # Get selected dimensions and measures
    selected_dims = [d for d in model.dimensions if str(d.id) in dimension_ids]
    selected_measures = [m for m in model.measures if str(m.id) in measure_ids]

    # Build SELECT
    select_parts = []
    for dim in selected_dims:
        select_parts.append(f'{quote}{dim.column_name}{quote}')
    for measure in selected_measures:
        agg = measure.aggregation.upper()
        col = f'{quote}{measure.column_name}{quote}'
        alias = f'{quote}{measure.name}{quote}'
        if agg == "COUNT_DISTINCT":
            select_parts.append(f'COUNT(DISTINCT {col}) AS {alias}')
        else:
            select_parts.append(f'{agg}({col}) AS {alias}')

    if not select_parts:
        select_parts = ["*"]

    # Build FROM - use transform or table
    cte_parts = []
    if model.transform_id and model.transform:
        transform_service = get_transform_service(conn_type)
        transform_sql = transform_service.generate_sql(
            source_table=model.transform.source_table,
            source_schema=model.transform.source_schema,
            steps=model.transform.steps or []
        )
        cte_parts.append(f'source_data AS ({transform_sql})')
        from_clause = 'source_data'

        # Handle joined transforms
        if model.joined_transforms:
            for jt in model.joined_transforms:
                jt_result = await db.execute(
                    select(TransformRecipe).where(TransformRecipe.id == jt['transform_id'])
                )
                joined_transform = jt_result.scalar_one_or_none()
                if joined_transform:
                    jt_sql = transform_service.generate_sql(
                        source_table=joined_transform.source_table,
                        source_schema=joined_transform.source_schema,
                        steps=joined_transform.steps or []
                    )
                    alias = jt.get('alias', f'jt_{jt["transform_id"][:8]}')
                    cte_parts.append(f'{alias} AS ({jt_sql})')

                    # Add JOIN
                    join_type = jt.get('join_type', 'left').upper()
                    join_conditions = []
                    for join_on in jt.get('join_on', []):
                        left_col = f'source_data.{quote}{join_on["left"]}{quote}'
                        right_col = f'{alias}.{quote}{join_on["right"]}{quote}'
                        join_conditions.append(f'{left_col} = {right_col}')
                    if join_conditions:
                        from_clause += f' {join_type} JOIN {alias} ON {" AND ".join(join_conditions)}'
    else:
        from_clause = f'{quote}{model.schema_name}{quote}.{quote}{model.table_name}{quote}'

    # GROUP BY
    group_by = ""
    if selected_dims and selected_measures:
        group_cols = [f'{quote}{d.column_name}{quote}' for d in selected_dims]
        group_by = f'GROUP BY {", ".join(group_cols)}'

    # Build WHERE clause from filters
    where_parts = []
    if filters:
        for f in filters:
            col = f.get("column")
            op = f.get("operator", "=")
            val = f.get("value")
            if col and val is not None:
                if op.lower() in ("is_null", "is null"):
                    where_parts.append(f'{quote}{col}{quote} IS NULL')
                elif op.lower() in ("is_not_null", "is not null"):
                    where_parts.append(f'{quote}{col}{quote} IS NOT NULL')
                elif op.lower() == "like":
                    where_parts.append(f'{quote}{col}{quote} LIKE \'%{val}%\'')
                elif op.lower() == "in":
                    if isinstance(val, list):
                        vals = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in val])
                        where_parts.append(f'{quote}{col}{quote} IN ({vals})')
                else:
                    if isinstance(val, str):
                        where_parts.append(f'{quote}{col}{quote} {op} \'{val}\'')
                    else:
                        where_parts.append(f'{quote}{col}{quote} {op} {val}')

    # Assemble
    if cte_parts:
        sql = f'WITH {", ".join(cte_parts)} SELECT {", ".join(select_parts)} FROM {from_clause}'
    else:
        sql = f'SELECT {", ".join(select_parts)} FROM {from_clause}'
    if where_parts:
        sql += f' WHERE {" AND ".join(where_parts)}'
    if group_by:
        sql += f' {group_by}'
    sql += ' LIMIT 1000'

    return sql


# ============== Chart CRUD Endpoints ==============

@router.get("/", response_model=List[SavedChart])
async def list_charts(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all saved charts."""
    result = await db.execute(
        select(SavedChartModel)
        .order_by(SavedChartModel.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/", response_model=SavedChart)
async def create_chart(
    chart: SavedChartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chart."""
    db_chart = SavedChartModel(**chart.model_dump())
    db.add(db_chart)
    await db.commit()
    await db.refresh(db_chart)
    return db_chart


@router.get("/{chart_id}", response_model=SavedChart)
async def get_chart(
    chart_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a chart by ID."""
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    # Update view count
    chart.view_count += 1
    chart.last_viewed_at = datetime.utcnow()
    await db.commit()

    return chart


@router.patch("/{chart_id}", response_model=SavedChart)
async def update_chart(
    chart_id: UUID,
    chart_update: SavedChartUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a chart."""
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    update_data = chart_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chart, field, value)

    await db.commit()
    await db.refresh(chart)
    return chart


@router.delete("/{chart_id}")
async def delete_chart(
    chart_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a chart."""
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    await db.delete(chart)
    await db.commit()
    return {"status": "deleted"}


# ============== Chart Rendering ==============

@router.get("/{chart_id}/render", response_model=ChartDataResponse)
async def render_chart(
    chart_id: UUID,
    limit: int = 1000,
    db: AsyncSession = Depends(get_db),
    filters: Optional[List[Dict[str, Any]]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Render a chart by executing its query and returning data.

    This endpoint:
    1. Fetches the chart configuration
    2. Determines the data source (semantic model, transform, or query_config)
    3. Executes the appropriate query
    4. Returns the data formatted for the chart

    Optional filters can be passed to filter the data dynamically.
    """
    start_time = time.time()

    # Get the chart
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    # Get the connection - convert string to UUID
    try:
        conn_uuid = uuid_module.UUID(chart.connection_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid connection ID format in chart")

    conn_result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == conn_uuid)
    )
    conn = conn_result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    conn_type = conn.type.value if hasattr(conn.type, 'value') else str(conn.type)

    # For CSV/Excel connections, use app database
    use_app_db = conn.type in (ConnectionType.csv, ConnectionType.excel)
    sql = None
    query_result = None

    try:
        # Priority 1: Use semantic model if specified
        if chart.semantic_model_id:
            model_result = await db.execute(
                select(SemanticModel)
                .options(
                    selectinload(SemanticModel.dimensions),
                    selectinload(SemanticModel.measures),
                    selectinload(SemanticModel.transform)
                )
                .where(SemanticModel.id == chart.semantic_model_id)
            )
            semantic_model = model_result.scalar_one_or_none()

            if semantic_model:
                # Get dimension and measure IDs from chart_config or use all
                chart_config = chart.chart_config or {}
                dimension_ids = chart_config.get("dimension_ids", [str(d.id) for d in semantic_model.dimensions])
                measure_ids = chart_config.get("measure_ids", [str(m.id) for m in semantic_model.measures])

                sql = await build_semantic_model_query(
                    semantic_model,
                    dimension_ids,
                    measure_ids,
                    conn_type,
                    db,
                    filters=filters
                )

        # Priority 2: Use transform recipe if specified
        elif chart.transform_recipe_id:
            transform_result = await db.execute(
                select(TransformRecipe).where(TransformRecipe.id == chart.transform_recipe_id)
            )
            transform = transform_result.scalar_one_or_none()

            if transform:
                transform_service = get_transform_service(conn_type)
                base_sql = transform_service.generate_sql(
                    source_table=transform.source_table,
                    source_schema=transform.source_schema,
                    steps=transform.steps or []
                )
                # Wrap transform query and apply filters
                quote = '`' if conn_type == "mysql" else '"'
                where_parts = []
                if filters:
                    for f in filters:
                        col = f.get("column")
                        op = f.get("operator", "=")
                        val = f.get("value")
                        if col and val is not None:
                            if op.lower() == "in" and isinstance(val, list):
                                vals = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in val])
                                where_parts.append(f'{quote}{col}{quote} IN ({vals})')
                            elif isinstance(val, str):
                                where_parts.append(f'{quote}{col}{quote} {op} \'{val}\'')
                            else:
                                where_parts.append(f'{quote}{col}{quote} {op} {val}')

                if where_parts:
                    sql = f'SELECT * FROM ({base_sql}) AS transform_data WHERE {" AND ".join(where_parts)} LIMIT {limit}'
                else:
                    sql = f'{base_sql} LIMIT {limit}'

        # Priority 3: Use query_config
        elif chart.query_config:
            # Merge filters into query_config
            config = chart.query_config.copy()
            if filters:
                existing_filters = config.get("filters", [])
                config["filters"] = existing_filters + filters
            sql = build_query_from_config(config, conn_type)

        # Fallback: No data source configured
        else:
            raise HTTPException(
                status_code=400,
                detail="Chart has no data source configured (semantic_model_id, transform_recipe_id, or query_config)"
            )

        # Execute the query
        if use_app_db:
            # For CSV/Excel, data is stored in app database
            query_result = await postgres_service.execute_query(settings.DATABASE_URL, sql, limit)
        elif conn.type == ConnectionType.mongodb:
            # MongoDB uses aggregation instead of SQL
            if chart.query_config:
                config = chart.query_config.copy()
                if filters:
                    existing_filters = config.get("filters", [])
                    config["filters"] = existing_filters + filters
                query_result = await execute_mongodb_aggregation(conn, config, limit)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="MongoDB charts require query_config with dimensions and measures"
                )
        else:
            query_result = await execute_query_on_connection(conn, sql, limit, db)

        execution_time = (time.time() - start_time) * 1000

        # Update chart view stats
        chart.view_count += 1
        chart.last_viewed_at = datetime.utcnow()
        await db.commit()

        return ChartDataResponse(
            columns=query_result.get("columns", []),
            rows=query_result.get("rows", []),
            total_rows=query_result.get("total", len(query_result.get("rows", []))),
            sql_generated=sql,
            execution_time_ms=round(execution_time, 2),
            chart_config=chart.chart_config or {},
            chart_type=chart.chart_type
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render chart: {str(e)}"
        )


@router.post("/{chart_id}/render", response_model=ChartDataResponse)
async def render_chart_with_filters(
    chart_id: UUID,
    request: ChartRenderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Render a chart with additional filters applied.

    This allows for interactive filtering without modifying the saved chart.
    Filters should be in format: [{"column": "state", "operator": "=", "value": "CA"}]
    Supported operators: =, !=, >, <, >=, <=, in, like, is_null, is_not_null
    """
    # Convert filters dict to list format if needed
    filters_list = None
    if request.filters:
        if isinstance(request.filters, dict):
            # Convert {column: value} to [{column, operator, value}]
            filters_list = [
                {"column": k, "operator": "in" if isinstance(v, list) else "=", "value": v}
                for k, v in request.filters.items()
                if v is not None and v != "" and v != []
            ]
        elif isinstance(request.filters, list):
            filters_list = request.filters

    return await render_chart(chart_id, request.limit, db, filters=filters_list, current_user=current_user)


class FilterColumn(BaseModel):
    """A column that can be used as a filter."""
    column: str
    label: str
    data_type: str = "string"
    distinct_count: Optional[int] = None


class FilterValuesResponse(BaseModel):
    """Response containing filter columns and their values."""
    columns: List[FilterColumn]
    values: Dict[str, List[Any]]


@router.get("/{chart_id}/filter-options", response_model=FilterValuesResponse)
async def get_chart_filter_options(
    chart_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get available filter columns and their distinct values for a chart.
    Returns columns from the chart's data source (semantic model dimensions or transform columns).
    """
    # Get the chart
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    # Get the connection - convert string to UUID
    try:
        conn_uuid = uuid_module.UUID(chart.connection_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid connection ID format in chart")

    conn_result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == conn_uuid)
    )
    conn = conn_result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    conn_type = conn.type.value if hasattr(conn.type, 'value') else str(conn.type)
    quote = '`' if conn_type == "mysql" else '"'

    filter_columns = []
    filter_values = {}

    try:
        # Get columns from semantic model dimensions
        if chart.semantic_model_id:
            model_result = await db.execute(
                select(SemanticModel)
                .options(selectinload(SemanticModel.dimensions))
                .where(SemanticModel.id == chart.semantic_model_id)
            )
            semantic_model = model_result.scalar_one_or_none()

            if semantic_model:
                for dim in semantic_model.dimensions:
                    filter_columns.append(FilterColumn(
                        column=dim.column_name,
                        label=dim.name or dim.column_name,
                        data_type=dim.data_type or "string"
                    ))

                # Get distinct values for each dimension (limit to 100)
                for dim in semantic_model.dimensions[:5]:  # Limit to first 5 dimensions
                    if semantic_model.transform_id and semantic_model.transform:
                        transform_service = get_transform_service(conn_type)
                        base_sql = transform_service.generate_sql(
                            source_table=semantic_model.transform.source_table,
                            source_schema=semantic_model.transform.source_schema,
                            steps=semantic_model.transform.steps or []
                        )
                        sql = f'SELECT DISTINCT {quote}{dim.column_name}{quote} FROM ({base_sql}) AS t ORDER BY 1 LIMIT 100'
                    else:
                        sql = f'SELECT DISTINCT {quote}{dim.column_name}{quote} FROM {quote}{semantic_model.schema_name}{quote}.{quote}{semantic_model.table_name}{quote} ORDER BY 1 LIMIT 100'

                    try:
                        result = await execute_query_on_connection(conn, sql, 100, db)
                        values = [row.get(dim.column_name) for row in result.get("rows", []) if row.get(dim.column_name) is not None]
                        filter_values[dim.column_name] = values
                    except:
                        filter_values[dim.column_name] = []

        # Get columns from transform recipe
        elif chart.transform_recipe_id:
            transform_result = await db.execute(
                select(TransformRecipe).where(TransformRecipe.id == chart.transform_recipe_id)
            )
            transform = transform_result.scalar_one_or_none()

            if transform:
                transform_service = get_transform_service(conn_type)
                base_sql = transform_service.generate_sql(
                    source_table=transform.source_table,
                    source_schema=transform.source_schema,
                    steps=transform.steps or []
                )
                # Get column names from the transform
                columns_sql = f'SELECT * FROM ({base_sql}) AS t LIMIT 1'
                try:
                    result = await execute_query_on_connection(conn, columns_sql, 1, db)
                    columns = result.get("columns", [])

                    for col in columns[:10]:  # Limit to first 10 columns
                        filter_columns.append(FilterColumn(
                            column=col,
                            label=col.replace("_", " ").title(),
                            data_type="string"
                        ))

                    # Get distinct values for first 5 columns
                    for col in columns[:5]:
                        values_sql = f'SELECT DISTINCT {quote}{col}{quote} FROM ({base_sql}) AS t ORDER BY 1 LIMIT 100'
                        try:
                            vals_result = await execute_query_on_connection(conn, values_sql, 100, db)
                            values = [row.get(col) for row in vals_result.get("rows", []) if row.get(col) is not None]
                            filter_values[col] = values
                        except:
                            filter_values[col] = []
                except:
                    pass

        return FilterValuesResponse(columns=filter_columns, values=filter_values)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get filter options: {str(e)}")


@router.post("/{chart_id}/favorite", response_model=SavedChart)
async def toggle_favorite(
    chart_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle favorite status of a chart."""
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    chart.is_favorite = not chart.is_favorite
    await db.commit()
    await db.refresh(chart)
    return chart
