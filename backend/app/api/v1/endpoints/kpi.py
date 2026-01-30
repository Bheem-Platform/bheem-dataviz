"""KPI calculation endpoints with period comparisons and trends."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import time

from app.database import get_db
from app.models.connection import Connection as ConnectionModel, ConnectionType
from app.models.semantic import SemanticModel, Measure
from app.models.transform import TransformRecipe
from app.models.dashboard import SavedKPI as SavedKPIModel
from app.schemas.dashboard import SavedKPI, SavedKPICreate, SavedKPIUpdate
from app.services.postgres_service import postgres_service
from app.services.mysql_service import MySQLService
from app.services.encryption_service import encryption_service
from app.services.transform_service import get_transform_service
from pydantic import BaseModel, Field


router = APIRouter()


# ============== Enums and Schemas ==============

class ComparisonPeriod(str, Enum):
    """Period for comparison calculations."""
    previous_day = "previous_day"
    previous_week = "previous_week"
    previous_month = "previous_month"
    previous_quarter = "previous_quarter"
    previous_year = "previous_year"
    custom = "custom"


class KPIRequest(BaseModel):
    """Request to calculate a KPI."""
    connection_id: str

    # Data source (one of these required)
    semantic_model_id: Optional[str] = None
    transform_id: Optional[str] = None
    table_name: Optional[str] = None
    schema_name: str = "public"

    # Measure configuration
    measure_column: str  # Column to aggregate
    aggregation: str = "sum"  # sum, avg, count, min, max

    # Time configuration for comparison
    date_column: Optional[str] = None  # Required for period comparison
    comparison_period: ComparisonPeriod = ComparisonPeriod.previous_month
    custom_days: Optional[int] = None  # For custom period

    # Optional filters
    filters: List[Dict[str, Any]] = []

    # Goal/target (optional)
    goal_value: Optional[float] = None
    goal_label: Optional[str] = None

    # Trend configuration
    include_trend: bool = True
    trend_points: int = 7  # Number of data points for sparkline


class KPIResponse(BaseModel):
    """Response with calculated KPI data."""
    # Core values
    current_value: float
    formatted_value: str

    # Comparison
    previous_value: Optional[float] = None
    change_value: Optional[float] = None
    change_percent: Optional[float] = None
    change_direction: Optional[str] = None  # "up", "down", "flat"
    comparison_label: Optional[str] = None  # "vs last month"

    # Goal
    goal_value: Optional[float] = None
    goal_percent: Optional[float] = None
    goal_status: Optional[str] = None  # "above", "below", "at"
    goal_label: Optional[str] = None

    # Trend (for sparkline)
    trend_data: List[Dict[str, Any]] = []

    # Metadata
    aggregation: str
    measure_column: str
    execution_time_ms: float

    # Smart date detection info
    reference_date: Optional[str] = None  # The detected "current" date from data
    current_period: Optional[str] = None  # e.g., "Jun 2022"
    previous_period: Optional[str] = None  # e.g., "May 2022"


# ============== Helper Functions ==============

def format_number(value: float) -> str:
    """Format a number for display."""
    if value is None:
        return "N/A"

    abs_value = abs(value)

    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B" if value >= 0 else f"-${abs_value / 1_000_000_000:.1f}B"
    elif abs_value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M" if value >= 0 else f"-${abs_value / 1_000_000:.1f}M"
    elif abs_value >= 1_000:
        return f"${value / 1_000:.1f}K" if value >= 0 else f"-${abs_value / 1_000:.1f}K"
    elif abs_value >= 1:
        return f"${value:,.0f}" if value >= 0 else f"-${abs_value:,.0f}"
    else:
        return f"${value:.2f}" if value >= 0 else f"-${abs_value:.2f}"


def get_period_dates(period: ComparisonPeriod, custom_days: Optional[int] = None, reference_date=None):
    """Get date ranges for current and previous periods.

    Args:
        period: The comparison period type
        custom_days: Number of days for custom period
        reference_date: The date to use as "today" (for smart date detection).
                       If None, uses current UTC date.
    """
    if reference_date:
        today = reference_date if hasattr(reference_date, 'year') else reference_date.date()
    else:
        today = datetime.utcnow().date()

    if period == ComparisonPeriod.previous_day:
        current_start = today
        current_end = today
        prev_start = today - timedelta(days=1)
        prev_end = prev_start
        label = "vs yesterday"

    elif period == ComparisonPeriod.previous_week:
        # Current week (Mon-Sun)
        current_start = today - timedelta(days=today.weekday())
        current_end = today
        # Previous week
        prev_start = current_start - timedelta(days=7)
        prev_end = current_start - timedelta(days=1)
        label = "vs last week"

    elif period == ComparisonPeriod.previous_month:
        # Current month
        current_start = today.replace(day=1)
        current_end = today
        # Previous month
        prev_end = current_start - timedelta(days=1)
        prev_start = prev_end.replace(day=1)
        label = "vs last month"

    elif period == ComparisonPeriod.previous_quarter:
        # Current quarter
        quarter = (today.month - 1) // 3
        current_start = today.replace(month=quarter * 3 + 1, day=1)
        current_end = today
        # Previous quarter
        if quarter == 0:
            prev_start = today.replace(year=today.year - 1, month=10, day=1)
            prev_end = today.replace(year=today.year - 1, month=12, day=31)
        else:
            prev_start = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            prev_end = current_start - timedelta(days=1)
        label = "vs last quarter"

    elif period == ComparisonPeriod.previous_year:
        # Current year
        current_start = today.replace(month=1, day=1)
        current_end = today
        # Previous year
        prev_start = today.replace(year=today.year - 1, month=1, day=1)
        prev_end = today.replace(year=today.year - 1, month=12, day=31)
        label = "vs last year"

    elif period == ComparisonPeriod.custom and custom_days:
        current_start = today - timedelta(days=custom_days - 1)
        current_end = today
        prev_start = current_start - timedelta(days=custom_days)
        prev_end = current_start - timedelta(days=1)
        label = f"vs previous {custom_days} days"

    else:
        # Default to last 30 days
        current_start = today - timedelta(days=29)
        current_end = today
        prev_start = current_start - timedelta(days=30)
        prev_end = current_start - timedelta(days=1)
        label = "vs previous period"

    return current_start, current_end, prev_start, prev_end, label


async def execute_query(conn: ConnectionModel, sql: str) -> Dict[str, Any]:
    """Execute SQL query on connection."""
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
        return await postgres_service.execute_query(conn_str, sql, 1000)

    elif conn.type == ConnectionType.mysql:
        return await MySQLService.execute_query(
            host=conn.host or "localhost",
            port=conn.port or 3306,
            database=conn.database_name or "",
            sql=sql,
            username=conn.username,
            password=password,
            limit=1000
        )

    raise HTTPException(status_code=400, detail=f"Unsupported connection type: {conn.type}")


def build_agg_sql(
    agg: str,
    column: str,
    quote: str
) -> str:
    """Build aggregation SQL."""
    agg_upper = agg.upper()
    col = f'{quote}{column}{quote}'

    if agg_upper == "COUNT_DISTINCT":
        return f"COUNT(DISTINCT {col})"
    elif agg_upper in ("SUM", "AVG", "MIN", "MAX", "COUNT"):
        return f"{agg_upper}({col})"
    else:
        return f"SUM({col})"


# ============== Main KPI Endpoint ==============

@router.post("/calculate", response_model=KPIResponse)
async def calculate_kpi(
    request: KPIRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate a KPI with period comparison, trend data, and goal progress.

    This endpoint:
    1. Calculates the current period value
    2. Calculates the previous period value for comparison
    3. Generates trend data for sparkline visualization
    4. Calculates goal progress if a target is specified
    """
    start_time = time.time()

    # Get connection
    conn_result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == request.connection_id)
    )
    conn = conn_result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    conn_type = conn.type.value if hasattr(conn.type, 'value') else str(conn.type)
    quote = '`' if conn_type == "mysql" else '"'

    # Determine the base SQL/source
    base_sql = None
    use_cte = False

    if request.transform_id:
        # Use transform as source
        transform_result = await db.execute(
            select(TransformRecipe).where(TransformRecipe.id == request.transform_id)
        )
        transform = transform_result.scalar_one_or_none()

        if not transform:
            raise HTTPException(status_code=404, detail="Transform not found")

        transform_service = get_transform_service(conn_type)
        base_sql = transform_service.generate_sql(
            source_table=transform.source_table,
            source_schema=transform.source_schema,
            steps=transform.steps or []
        )
        use_cte = True

    elif request.semantic_model_id:
        # Use semantic model's source
        model_result = await db.execute(
            select(SemanticModel)
            .options(selectinload(SemanticModel.transform))
            .where(SemanticModel.id == request.semantic_model_id)
        )
        model = model_result.scalar_one_or_none()

        if not model:
            raise HTTPException(status_code=404, detail="Semantic model not found")

        if model.transform_id and model.transform:
            transform_service = get_transform_service(conn_type)
            base_sql = transform_service.generate_sql(
                source_table=model.transform.source_table,
                source_schema=model.transform.source_schema,
                steps=model.transform.steps or []
            )
            use_cte = True
        else:
            # MySQL doesn't use schema prefix the same way
            if conn_type == "mysql":
                base_sql = f'{quote}{model.table_name}{quote}'
            else:
                base_sql = f'{quote}{model.schema_name}{quote}.{quote}{model.table_name}{quote}'

    elif request.table_name:
        # Use raw table - MySQL doesn't use schema prefix the same way
        if conn_type == "mysql":
            base_sql = f'{quote}{request.table_name}{quote}'
        else:
            base_sql = f'{quote}{request.schema_name}{quote}.{quote}{request.table_name}{quote}'

    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide semantic_model_id, transform_id, or table_name"
        )

    # Build aggregation
    agg_sql = build_agg_sql(request.aggregation, request.measure_column, quote)

    # Build filter clause
    filter_parts = []
    for f in request.filters:
        col = f.get("column")
        op = f.get("operator", "=")
        val = f.get("value")
        if col and val is not None:
            if isinstance(val, str):
                filter_parts.append(f'{quote}{col}{quote} {op} \'{val}\'')
            else:
                filter_parts.append(f'{quote}{col}{quote} {op} {val}')

    filter_clause = f" AND {' AND '.join(filter_parts)}" if filter_parts else ""

    # Build the source clause
    source_clause = f"kpi_source" if use_cte else base_sql
    cte_prefix = f"WITH kpi_source AS ({base_sql}) " if use_cte else ""

    # Smart Date Detection: Find the max date in the data
    reference_date = None
    if request.date_column:
        date_col = f'{quote}{request.date_column}{quote}'

        # Build date conversion for max date query
        if conn_type == "postgresql":
            date_expr_for_max = f"""
                CASE
                    WHEN {date_col} ~ '^[0-9]{{2}}-[0-9]{{2}}-[0-9]{{2}}$' THEN TO_DATE({date_col}, 'MM-DD-YY')
                    WHEN {date_col} ~ '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}' THEN {date_col}::DATE
                    ELSE {date_col}::DATE
                END
            """
        else:
            date_expr_for_max = f"STR_TO_DATE({date_col}, '%m-%d-%y')"

        max_date_sql = f"""
            {cte_prefix}
            SELECT MAX({date_expr_for_max}) as max_date
            FROM {source_clause}
        """
        try:
            max_date_result = await execute_query(conn, max_date_sql)
            if max_date_result.get("rows") and len(max_date_result["rows"]) > 0:
                max_date_val = max_date_result["rows"][0].get("max_date")
                if max_date_val:
                    # Parse the date - handle various formats
                    if isinstance(max_date_val, datetime):
                        reference_date = max_date_val.date()
                    elif isinstance(max_date_val, str):
                        # Try common date formats
                        for fmt in ("%Y-%m-%d", "%m-%d-%y", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
                            try:
                                reference_date = datetime.strptime(max_date_val.split()[0], fmt).date()
                                break
                            except ValueError:
                                continue
                    else:
                        # Assume it's already a date object
                        reference_date = max_date_val
        except Exception as e:
            # If we can't detect date, fall back to current date
            pass

    # Get period dates using detected reference date (or current date if not detected)
    current_start, current_end, prev_start, prev_end, comparison_label = get_period_dates(
        request.comparison_period,
        request.custom_days,
        reference_date
    )

    # Query 1: Current period value
    if request.date_column:
        date_col = f'{quote}{request.date_column}{quote}'

        # Build date conversion SQL based on database type
        # Handle common date formats: MM-DD-YY, YYYY-MM-DD, etc.
        if conn_type == "postgresql":
            # Try to cast to date, handling MM-DD-YY format
            date_cast = f"TO_DATE({date_col}, 'MM-DD-YY')"
            # Use a CASE to handle multiple formats
            date_expr = f"""
                CASE
                    WHEN {date_col} ~ '^[0-9]{{2}}-[0-9]{{2}}-[0-9]{{2}}$' THEN TO_DATE({date_col}, 'MM-DD-YY')
                    WHEN {date_col} ~ '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}' THEN {date_col}::DATE
                    ELSE {date_col}::DATE
                END
            """
        else:
            # MySQL
            date_expr = f"STR_TO_DATE({date_col}, '%m-%d-%y')"

        current_sql = f"""
            {cte_prefix}
            SELECT {agg_sql} as value
            FROM {source_clause}
            WHERE ({date_expr}) >= '{current_start}'
            AND ({date_expr}) <= '{current_end}'
            {filter_clause}
        """
    else:
        # No date column - just calculate total
        current_sql = f"""
            {cte_prefix}
            SELECT {agg_sql} as value
            FROM {source_clause}
            WHERE 1=1 {filter_clause}
        """

    try:
        current_result = await execute_query(conn, current_sql)
        current_value = 0.0
        if current_result.get("rows") and len(current_result["rows"]) > 0:
            val = current_result["rows"][0].get("value")
            current_value = float(val) if val is not None else 0.0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate current value: {str(e)}")

    # Query 2: Previous period value (if date column provided)
    previous_value = None
    change_value = None
    change_percent = None
    change_direction = None

    if request.date_column:
        date_col = f'{quote}{request.date_column}{quote}'

        # Use same date conversion as current period
        if conn_type == "postgresql":
            date_expr = f"""
                CASE
                    WHEN {date_col} ~ '^[0-9]{{2}}-[0-9]{{2}}-[0-9]{{2}}$' THEN TO_DATE({date_col}, 'MM-DD-YY')
                    WHEN {date_col} ~ '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}' THEN {date_col}::DATE
                    ELSE {date_col}::DATE
                END
            """
        else:
            date_expr = f"STR_TO_DATE({date_col}, '%m-%d-%y')"

        prev_sql = f"""
            {cte_prefix}
            SELECT {agg_sql} as value
            FROM {source_clause}
            WHERE ({date_expr}) >= '{prev_start}'
            AND ({date_expr}) <= '{prev_end}'
            {filter_clause}
        """

        try:
            prev_result = await execute_query(conn, prev_sql)
            if prev_result.get("rows") and len(prev_result["rows"]) > 0:
                val = prev_result["rows"][0].get("value")
                previous_value = float(val) if val is not None else 0.0

                # Calculate change
                change_value = current_value - previous_value
                if previous_value != 0:
                    change_percent = (change_value / previous_value) * 100
                else:
                    change_percent = 100.0 if current_value > 0 else 0.0

                if change_value > 0:
                    change_direction = "up"
                elif change_value < 0:
                    change_direction = "down"
                else:
                    change_direction = "flat"
        except Exception as e:
            # Non-fatal - continue without comparison
            pass

    # Query 3: Trend data (if requested and date column provided)
    trend_data = []

    if request.include_trend and request.date_column:
        date_col = f'{quote}{request.date_column}{quote}'

        # Use same date conversion
        if conn_type == "postgresql":
            date_expr = f"""
                CASE
                    WHEN {date_col} ~ '^[0-9]{{2}}-[0-9]{{2}}-[0-9]{{2}}$' THEN TO_DATE({date_col}, 'MM-DD-YY')
                    WHEN {date_col} ~ '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}' THEN {date_col}::DATE
                    ELSE {date_col}::DATE
                END
            """
        else:
            date_expr = f"STR_TO_DATE({date_col}, '%m-%d-%y')"

        # Determine grouping based on period
        if request.comparison_period in (ComparisonPeriod.previous_day, ComparisonPeriod.previous_week):
            # Group by day
            if conn_type == "mysql":
                date_trunc = f"DATE({date_expr})"
            else:
                date_trunc = f"DATE_TRUNC('day', ({date_expr}))"
        else:
            # Group by week or month depending on range
            if conn_type == "mysql":
                date_trunc = f"DATE_FORMAT({date_expr}, '%Y-%m-01')"
            else:
                date_trunc = f"DATE_TRUNC('week', ({date_expr}))"

        # Get trend for current period + some history
        trend_start = current_start - timedelta(days=request.trend_points * 7)  # Extend back

        trend_sql = f"""
            {cte_prefix}
            SELECT
                {date_trunc} as period,
                {agg_sql} as value
            FROM {source_clause}
            WHERE ({date_expr}) >= '{trend_start}'
            AND ({date_expr}) <= '{current_end}'
            {filter_clause}
            GROUP BY {date_trunc}
            ORDER BY period
            LIMIT {request.trend_points}
        """

        try:
            trend_result = await execute_query(conn, trend_sql)
            if trend_result.get("rows"):
                trend_data = [
                    {
                        "period": str(row.get("period")),
                        "value": float(row.get("value") or 0)
                    }
                    for row in trend_result["rows"]
                ]
        except Exception:
            # Non-fatal - continue without trend
            pass

    # Calculate goal progress
    goal_percent = None
    goal_status = None

    if request.goal_value is not None and request.goal_value > 0:
        goal_percent = (current_value / request.goal_value) * 100

        if current_value >= request.goal_value:
            goal_status = "above"
        elif current_value >= request.goal_value * 0.9:
            goal_status = "at"
        else:
            goal_status = "below"

    execution_time = (time.time() - start_time) * 1000

    # Format period labels for display
    current_period_label = None
    previous_period_label = None
    if reference_date and request.date_column:
        current_period_label = f"{current_start.strftime('%b %d')} - {current_end.strftime('%b %d, %Y')}"
        previous_period_label = f"{prev_start.strftime('%b %d')} - {prev_end.strftime('%b %d, %Y')}"

    return KPIResponse(
        current_value=current_value,
        formatted_value=format_number(current_value),
        previous_value=previous_value,
        change_value=change_value,
        change_percent=round(change_percent, 1) if change_percent is not None else None,
        change_direction=change_direction,
        comparison_label=comparison_label if request.date_column else None,
        goal_value=request.goal_value,
        goal_percent=round(goal_percent, 1) if goal_percent is not None else None,
        goal_status=goal_status,
        goal_label=request.goal_label,
        trend_data=trend_data,
        aggregation=request.aggregation,
        measure_column=request.measure_column,
        execution_time_ms=round(execution_time, 2),
        reference_date=str(reference_date) if reference_date else None,
        current_period=current_period_label,
        previous_period=previous_period_label
    )


@router.post("/batch", response_model=List[KPIResponse])
async def calculate_kpis_batch(
    requests: List[KPIRequest],
    db: AsyncSession = Depends(get_db)
):
    """Calculate multiple KPIs in a single request."""
    results = []
    for req in requests:
        try:
            result = await calculate_kpi(req, db)
            results.append(result)
        except HTTPException as e:
            # Return error as a response
            results.append(KPIResponse(
                current_value=0,
                formatted_value="Error",
                aggregation=req.aggregation,
                measure_column=req.measure_column,
                execution_time_ms=0
            ))
    return results


# ============== Saved KPI CRUD Endpoints ==============

@router.get("/saved", response_model=List[SavedKPI])
async def list_saved_kpis(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all saved KPIs."""
    result = await db.execute(
        select(SavedKPIModel)
        .order_by(SavedKPIModel.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/saved", response_model=SavedKPI)
async def create_saved_kpi(
    kpi: SavedKPICreate,
    db: AsyncSession = Depends(get_db)
):
    """Save a new KPI configuration."""
    db_kpi = SavedKPIModel(**kpi.model_dump())
    db.add(db_kpi)
    await db.commit()
    await db.refresh(db_kpi)
    return db_kpi


@router.get("/saved/{kpi_id}", response_model=SavedKPI)
async def get_saved_kpi(
    kpi_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a saved KPI by ID."""
    result = await db.execute(
        select(SavedKPIModel).where(SavedKPIModel.id == kpi_id)
    )
    kpi = result.scalar_one_or_none()

    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")

    return kpi


@router.patch("/saved/{kpi_id}", response_model=SavedKPI)
async def update_saved_kpi(
    kpi_id: str,
    kpi_update: SavedKPIUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a saved KPI."""
    result = await db.execute(
        select(SavedKPIModel).where(SavedKPIModel.id == kpi_id)
    )
    kpi = result.scalar_one_or_none()

    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")

    update_data = kpi_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(kpi, field, value)

    await db.commit()
    await db.refresh(kpi)
    return kpi


@router.delete("/saved/{kpi_id}")
async def delete_saved_kpi(
    kpi_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a saved KPI."""
    result = await db.execute(
        select(SavedKPIModel).where(SavedKPIModel.id == kpi_id)
    )
    kpi = result.scalar_one_or_none()

    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")

    await db.delete(kpi)
    await db.commit()
    return {"status": "deleted"}


@router.post("/saved/{kpi_id}/favorite", response_model=SavedKPI)
async def toggle_kpi_favorite(
    kpi_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Toggle favorite status of a KPI."""
    result = await db.execute(
        select(SavedKPIModel).where(SavedKPIModel.id == kpi_id)
    )
    kpi = result.scalar_one_or_none()

    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")

    kpi.is_favorite = not kpi.is_favorite
    await db.commit()
    await db.refresh(kpi)
    return kpi
