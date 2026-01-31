"""
Time Intelligence API Endpoints

Provides endpoints for time-based calculations.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.time_intelligence import (
    TimeIntelligenceRequest,
    TimeIntelligenceResponse,
    TimeIntelligenceResult,
    TimeIntelligenceFunction,
    DateTableConfig,
    COMMON_TIME_INTELLIGENCE_TEMPLATES,
    DATE_TABLE_COLUMNS,
    FISCAL_DATE_TABLE_COLUMNS,
)
from app.services.time_intelligence_service import get_time_intelligence_service
from app.services.postgres_service import postgres_service
from app.services.mysql_service import mysql_service
from app.services.encryption_service import encryption_service
from app.models.connection import Connection as ConnectionModel, ConnectionType

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/calculate", response_model=TimeIntelligenceResponse)
async def calculate_time_intelligence(
    request: TimeIntelligenceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Calculate time intelligence functions.

    Supports various time-based calculations like YTD, MTD, SPLY, rolling periods, etc.
    """
    # Get connection details
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == request.connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Generate SQL and period info from service
    service = get_time_intelligence_service()
    response = service.calculate(request)

    print(f"DEBUG: Request functions count: {len(request.functions)}")
    print(f"DEBUG: Connection type: {conn.type}")
    print(f"DEBUG: Response success: {response.success}")

    if not response.success:
        return response

    # Build connection string
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    # Execute queries and get actual values
    updated_results = []
    for i, func in enumerate(request.functions):
        result_info = response.results[i] if i < len(response.results) else None

        # Generate individual function SQL
        sql = service._generate_function_sql(
            func=func,
            schema_name=request.schema_name,
            table_name=request.table_name,
            reference_date=service._parse_date(request.reference_date) or __import__('datetime').date.today(),
            filters=request.filters,
            group_by=request.group_by,
        )

        try:
            print(f"DEBUG: Executing for func {func.id}, conn type: {conn.type}")
            print(f"DEBUG: SQL: {sql[:300]}")

            # Execute query based on connection type
            if conn.type == ConnectionType.postgresql:
                conn_str = postgres_service.build_connection_string(
                    host=conn.host or "localhost",
                    port=conn.port or 5432,
                    database=conn.database_name or "",
                    username=conn.username,
                    password=password,
                    extra=conn.additional_config
                )
                query_result = await postgres_service.execute_query(conn_str, sql, limit=10)
            elif conn.type == ConnectionType.mysql:
                query_result = await mysql_service.execute_query(
                    host=conn.host or "localhost",
                    port=conn.port or 3306,
                    database=conn.database_name or "",
                    sql=sql,
                    username=conn.username,
                    password=password,
                    limit=10
                )
            else:
                # Unsupported connection type - return without values
                updated_results.append(result_info)
                continue

            print(f"DEBUG: Query result: {query_result}")

            # Parse query results
            if query_result and query_result.get("rows"):
                row = query_result["rows"][0]

                # Extract values from result
                value = None
                comparison_value = None
                pct_change = None

                # Look for value columns in result
                from decimal import Decimal
                for key, val in row.items():
                    key_lower = key.lower()
                    measure_col_lower = func.measure_column.lower()

                    # Check for current_value or measure column name (including in compound names like ytd_base_salary)
                    if 'current_value' in key_lower or key_lower == measure_col_lower or measure_col_lower in key_lower:
                        if val is not None:
                            value = float(val) if isinstance(val, (int, float, Decimal)) else None
                    elif 'comparison' in key_lower:
                        if val is not None:
                            comparison_value = float(val) if isinstance(val, (int, float, Decimal)) else None
                    elif 'pct_change' in key_lower or key_lower == 'change':
                        if val is not None:
                            pct_change = float(val) if isinstance(val, (int, float, Decimal)) else None
                    elif value is None and isinstance(val, (int, float, Decimal)):
                        # First numeric column as value (fallback)
                        value = float(val)

                print(f"DEBUG: Extracted value={value}, comparison={comparison_value}, pct={pct_change}")

                updated_results.append(TimeIntelligenceResult(
                    function_id=func.id,
                    value=value,
                    comparison_value=comparison_value,
                    pct_change=pct_change,
                    period_start=result_info.period_start if result_info else None,
                    period_end=result_info.period_end if result_info else None,
                    comparison_period_start=result_info.comparison_period_start if result_info else None,
                    comparison_period_end=result_info.comparison_period_end if result_info else None,
                ))
            else:
                # No results - return with null values
                updated_results.append(TimeIntelligenceResult(
                    function_id=func.id,
                    value=None,
                    comparison_value=None,
                    pct_change=None,
                    period_start=result_info.period_start if result_info else None,
                    period_end=result_info.period_end if result_info else None,
                    comparison_period_start=result_info.comparison_period_start if result_info else None,
                    comparison_period_end=result_info.comparison_period_end if result_info else None,
                ))

        except Exception as e:
            logger.error(f"Failed to execute time intelligence query: {e}")
            # Return result with null values on error
            updated_results.append(TimeIntelligenceResult(
                function_id=func.id,
                value=None,
                comparison_value=None,
                pct_change=None,
                period_start=result_info.period_start if result_info else None,
                period_end=result_info.period_end if result_info else None,
                comparison_period_start=result_info.comparison_period_start if result_info else None,
                comparison_period_end=result_info.comparison_period_end if result_info else None,
            ))

    final_response = TimeIntelligenceResponse(
        success=True,
        results=updated_results,
        query=response.query,
    )
    print(f"DEBUG: Final response: {final_response.model_dump()}")
    return final_response


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
