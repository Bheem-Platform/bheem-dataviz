"""
Time Intelligence API Endpoints

Provides endpoints for time-based calculations.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.time_intelligence import (
    TimeIntelligenceRequest,
    TimeIntelligenceResponse,
    TimeIntelligenceFunction,
    DateTableConfig,
    COMMON_TIME_INTELLIGENCE_TEMPLATES,
    DATE_TABLE_COLUMNS,
    FISCAL_DATE_TABLE_COLUMNS,
)
from app.services.time_intelligence_service import get_time_intelligence_service

router = APIRouter()


@router.post("/calculate", response_model=TimeIntelligenceResponse)
async def calculate_time_intelligence(
    request: TimeIntelligenceRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Calculate time intelligence functions.

    Supports various time-based calculations like YTD, MTD, SPLY, rolling periods, etc.

    - **connection_id**: Database connection to use
    - **schema_name**: Schema containing the table
    - **table_name**: Table to query
    - **functions**: List of time intelligence functions to calculate
    - **filters**: Additional filters to apply
    - **group_by**: Columns to group by
    - **reference_date**: Reference date (defaults to today)
    """
    service = get_time_intelligence_service()
    return service.calculate(request)


@router.post("/generate-sql")
async def generate_time_intelligence_sql(
    request: TimeIntelligenceRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate SQL for time intelligence calculations without executing.

    Useful for previewing the query that would be executed.
    """
    service = get_time_intelligence_service()
    response = service.calculate(request)

    return {
        "sql": response.query,
        "functions": [r.function_id for r in response.results],
    }


@router.get("/templates")
async def get_time_intelligence_templates(
    current_user: dict = Depends(get_current_user),
):
    """
    Get common time intelligence function templates.

    Returns pre-built templates for common calculations.
    """
    return COMMON_TIME_INTELLIGENCE_TEMPLATES


@router.post("/date-table/generate")
async def generate_date_table(
    config: DateTableConfig,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate SQL to create a date dimension table.

    - **start_date**: Start date for the table
    - **end_date**: End date for the table
    - **table_name**: Name for the date table
    - **include_fiscal**: Include fiscal calendar columns
    - **fiscal_config**: Fiscal calendar configuration
    """
    service = get_time_intelligence_service()
    sql = service.generate_date_table_sql(config)

    return {
        "sql": sql,
        "table_name": config.table_name,
        "columns": DATE_TABLE_COLUMNS + (FISCAL_DATE_TABLE_COLUMNS if config.include_fiscal else []),
    }


@router.get("/date-table/columns")
async def get_date_table_columns(
    include_fiscal: bool = False,
    current_user: dict = Depends(get_current_user),
):
    """
    Get the column definitions for a date dimension table.
    """
    columns = DATE_TABLE_COLUMNS.copy()
    if include_fiscal:
        columns.extend(FISCAL_DATE_TABLE_COLUMNS)

    return [
        {
            "name": c.name,
            "type": c.sql_type,
            "description": c.description,
        }
        for c in columns
    ]


@router.post("/preview")
async def preview_time_function(
    function: TimeIntelligenceFunction,
    schema_name: str,
    table_name: str,
    reference_date: str = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Preview a single time intelligence function.

    Returns the SQL and period dates without executing.
    """
    from datetime import date, datetime

    service = get_time_intelligence_service()

    # Parse reference date
    ref_date = date.today()
    if reference_date:
        try:
            ref_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reference_date format. Use YYYY-MM-DD.",
            )

    # Get period dates
    period_start, period_end = service._get_period_dates(
        function.period_type,
        ref_date,
        function.periods,
        function.granularity,
        function.fiscal_config if function.use_fiscal_calendar else None,
    )

    # Get comparison period if needed
    comp_start, comp_end = None, None
    if function.include_comparison:
        comp_start, comp_end = service._get_comparison_period(
            function.period_type,
            period_start,
            period_end,
            function.fiscal_config if function.use_fiscal_calendar else None,
        )

    # Generate SQL
    sql = service._generate_function_sql(
        func=function,
        schema_name=schema_name,
        table_name=table_name,
        reference_date=ref_date,
    )

    return {
        "function_id": function.id,
        "period_type": function.period_type.value,
        "reference_date": ref_date.isoformat(),
        "period_start": period_start.isoformat() if period_start else None,
        "period_end": period_end.isoformat() if period_end else None,
        "comparison_period_start": comp_start.isoformat() if comp_start else None,
        "comparison_period_end": comp_end.isoformat() if comp_end else None,
        "sql": sql,
    }


@router.get("/period-types")
async def get_period_types(
    current_user: dict = Depends(get_current_user),
):
    """
    Get available time period types with descriptions.
    """
    return [
        {"value": "ytd", "label": "Year-to-Date", "description": "From start of year to current date"},
        {"value": "qtd", "label": "Quarter-to-Date", "description": "From start of quarter to current date"},
        {"value": "mtd", "label": "Month-to-Date", "description": "From start of month to current date"},
        {"value": "wtd", "label": "Week-to-Date", "description": "From start of week to current date"},
        {"value": "sply", "label": "Same Period Last Year", "description": "Same dates in the previous year"},
        {"value": "splm", "label": "Same Period Last Month", "description": "Same dates in the previous month"},
        {"value": "splq", "label": "Same Period Last Quarter", "description": "Same dates in the previous quarter"},
        {"value": "ppy", "label": "Previous Year", "description": "Full previous year"},
        {"value": "ppq", "label": "Previous Quarter", "description": "Full previous quarter"},
        {"value": "ppm", "label": "Previous Month", "description": "Full previous month"},
        {"value": "rolling", "label": "Rolling Periods", "description": "Rolling N periods from current date"},
        {"value": "trailing", "label": "Trailing Periods", "description": "N complete periods before current"},
        {"value": "fiscal_ytd", "label": "Fiscal Year-to-Date", "description": "From fiscal year start to current date"},
        {"value": "fiscal_qtd", "label": "Fiscal Quarter-to-Date", "description": "From fiscal quarter start to current date"},
    ]


@router.get("/aggregation-types")
async def get_aggregation_types(
    current_user: dict = Depends(get_current_user),
):
    """
    Get available aggregation types.
    """
    return [
        {"value": "sum", "label": "Sum", "description": "Total of all values"},
        {"value": "avg", "label": "Average", "description": "Mean of all values"},
        {"value": "min", "label": "Minimum", "description": "Smallest value"},
        {"value": "max", "label": "Maximum", "description": "Largest value"},
        {"value": "count", "label": "Count", "description": "Number of values"},
        {"value": "first", "label": "First", "description": "First value in period"},
        {"value": "last", "label": "Last", "description": "Last value in period"},
    ]


@router.get("/granularities")
async def get_time_granularities(
    current_user: dict = Depends(get_current_user),
):
    """
    Get available time granularities.
    """
    return [
        {"value": "year", "label": "Year"},
        {"value": "quarter", "label": "Quarter"},
        {"value": "month", "label": "Month"},
        {"value": "week", "label": "Week"},
        {"value": "day", "label": "Day"},
        {"value": "hour", "label": "Hour"},
    ]
