"""
Time Intelligence Service

Provides time-based calculations similar to DAX time intelligence functions.
Generates SQL for various time period calculations.
"""

import logging
from typing import Any, Optional
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from app.schemas.time_intelligence import (
    TimeGranularity,
    TimePeriodType,
    AggregationType,
    FiscalCalendarConfig,
    TimeIntelligenceFunction,
    TimeIntelligenceRequest,
    TimeIntelligenceResult,
    TimeIntelligenceResponse,
    DateTableConfig,
    DATE_TABLE_COLUMNS,
    FISCAL_DATE_TABLE_COLUMNS,
)

logger = logging.getLogger(__name__)


class TimeIntelligenceService:
    """Service for time intelligence calculations"""

    def __init__(self, db_type: str = "postgresql"):
        self.db_type = db_type

    def calculate(
        self,
        request: TimeIntelligenceRequest,
    ) -> TimeIntelligenceResponse:
        """
        Calculate time intelligence functions.

        Returns results and the generated query.
        """
        try:
            # Parse reference date
            ref_date = self._parse_date(request.reference_date) or date.today()

            results = []
            queries = []

            for func in request.functions:
                # Generate SQL for this function
                query = self._generate_function_sql(
                    func=func,
                    schema_name=request.schema_name,
                    table_name=request.table_name,
                    reference_date=ref_date,
                    filters=request.filters,
                    group_by=request.group_by,
                )
                queries.append(query)

                # Calculate period dates
                period_start, period_end = self._get_period_dates(
                    func.period_type,
                    ref_date,
                    func.periods,
                    func.granularity,
                    func.fiscal_config if func.use_fiscal_calendar else None,
                )

                # Get comparison period if needed
                comp_start, comp_end = None, None
                if func.include_comparison:
                    comp_start, comp_end = self._get_comparison_period(
                        func.period_type,
                        period_start,
                        period_end,
                        func.fiscal_config if func.use_fiscal_calendar else None,
                    )

                result = TimeIntelligenceResult(
                    function_id=func.id,
                    period_start=period_start.isoformat() if period_start else None,
                    period_end=period_end.isoformat() if period_end else None,
                    comparison_period_start=comp_start.isoformat() if comp_start else None,
                    comparison_period_end=comp_end.isoformat() if comp_end else None,
                )
                results.append(result)

            return TimeIntelligenceResponse(
                success=True,
                results=results,
                query="\n\n".join(queries) if queries else None,
            )

        except Exception as e:
            logger.error(f"Time intelligence calculation failed: {e}")
            return TimeIntelligenceResponse(
                success=False,
                error=str(e),
            )

    def _generate_function_sql(
        self,
        func: TimeIntelligenceFunction,
        schema_name: str,
        table_name: str,
        reference_date: date,
        filters: Optional[dict[str, Any]] = None,
        group_by: Optional[list[str]] = None,
    ) -> str:
        """Generate SQL for a time intelligence function"""
        # Get period dates
        period_start, period_end = self._get_period_dates(
            func.period_type,
            reference_date,
            func.periods,
            func.granularity,
            func.fiscal_config if func.use_fiscal_calendar else None,
        )

        # Build aggregation expression
        agg_expr = self._get_aggregation_expr(func.aggregation, func.measure_column)

        # Build date filter
        date_filter = self._build_date_filter(
            func.date_column,
            period_start,
            period_end,
        )

        # Build additional filters
        filter_clauses = [date_filter]
        if filters:
            for col, val in filters.items():
                if isinstance(val, str):
                    filter_clauses.append(f"{col} = '{val}'")
                elif val is None:
                    filter_clauses.append(f"{col} IS NULL")
                else:
                    filter_clauses.append(f"{col} = {val}")

        where_clause = " AND ".join(filter_clauses)

        # Build GROUP BY
        group_clause = ""
        select_cols = ""
        if group_by:
            group_clause = f"GROUP BY {', '.join(group_by)}"
            select_cols = f"{', '.join(group_by)}, "

        # Build output column name
        output_col = func.output_column or f"{func.period_type.value}_{func.measure_column}"

        # Build main query
        sql = f"""
SELECT
    {select_cols}{agg_expr} AS {output_col}
FROM {schema_name}.{table_name}
WHERE {where_clause}
{group_clause}
""".strip()

        # Add comparison query if needed
        if func.include_comparison:
            comp_start, comp_end = self._get_comparison_period(
                func.period_type,
                period_start,
                period_end,
                func.fiscal_config if func.use_fiscal_calendar else None,
            )

            if comp_start and comp_end:
                comp_date_filter = self._build_date_filter(
                    func.date_column,
                    comp_start,
                    comp_end,
                )
                comp_filter_clauses = [comp_date_filter]
                if filters:
                    for col, val in filters.items():
                        if isinstance(val, str):
                            comp_filter_clauses.append(f"{col} = '{val}'")
                        elif val is None:
                            comp_filter_clauses.append(f"{col} IS NULL")
                        else:
                            comp_filter_clauses.append(f"{col} = {val}")

                comp_where = " AND ".join(comp_filter_clauses)

                sql = f"""
-- Current Period
WITH current_period AS (
    SELECT
        {select_cols}{agg_expr} AS current_value
    FROM {schema_name}.{table_name}
    WHERE {where_clause}
    {group_clause}
),
-- Comparison Period
comparison_period AS (
    SELECT
        {select_cols}{agg_expr} AS comparison_value
    FROM {schema_name}.{table_name}
    WHERE {comp_where}
    {group_clause}
)
SELECT
    c.*,
    p.comparison_value,
    CASE
        WHEN p.comparison_value != 0 AND p.comparison_value IS NOT NULL
        THEN ((c.current_value - p.comparison_value) / p.comparison_value * 100)
        ELSE NULL
    END AS pct_change
FROM current_period c
LEFT JOIN comparison_period p ON 1=1
""".strip()

        return sql

    def _get_period_dates(
        self,
        period_type: TimePeriodType,
        reference_date: date,
        periods: Optional[int] = None,
        granularity: Optional[TimeGranularity] = None,
        fiscal_config: Optional[FiscalCalendarConfig] = None,
    ) -> tuple[Optional[date], Optional[date]]:
        """Get start and end dates for a period type"""
        if period_type == TimePeriodType.YTD:
            start = date(reference_date.year, 1, 1)
            end = reference_date
        elif period_type == TimePeriodType.FISCAL_YTD and fiscal_config:
            start = self._get_fiscal_year_start(reference_date, fiscal_config)
            end = reference_date
        elif period_type == TimePeriodType.QTD:
            quarter = (reference_date.month - 1) // 3 + 1
            start = date(reference_date.year, (quarter - 1) * 3 + 1, 1)
            end = reference_date
        elif period_type == TimePeriodType.MTD:
            start = date(reference_date.year, reference_date.month, 1)
            end = reference_date
        elif period_type == TimePeriodType.WTD:
            # Week starts on Monday by default
            start = reference_date - timedelta(days=reference_date.weekday())
            end = reference_date
        elif period_type == TimePeriodType.ROLLING and periods and granularity:
            end = reference_date
            start = self._subtract_periods(reference_date, periods, granularity)
        elif period_type == TimePeriodType.TRAILING and periods and granularity:
            # Trailing excludes current period
            period_end = self._get_period_end(reference_date, granularity)
            end = period_end - timedelta(days=1)
            start = self._subtract_periods(end, periods - 1, granularity)
        elif period_type in [TimePeriodType.SPLY, TimePeriodType.PPY]:
            # Same dates, previous year
            start = date(reference_date.year - 1, 1, 1)
            end = date(reference_date.year - 1, reference_date.month, reference_date.day)
        elif period_type in [TimePeriodType.SPLM, TimePeriodType.PPM]:
            prev_month = reference_date - relativedelta(months=1)
            start = date(prev_month.year, prev_month.month, 1)
            last_day = calendar.monthrange(prev_month.year, prev_month.month)[1]
            end = date(prev_month.year, prev_month.month, last_day)
        elif period_type in [TimePeriodType.SPLQ, TimePeriodType.PPQ]:
            prev_quarter_end = reference_date - relativedelta(months=3)
            quarter = (prev_quarter_end.month - 1) // 3 + 1
            start = date(prev_quarter_end.year, (quarter - 1) * 3 + 1, 1)
            end_month = quarter * 3
            last_day = calendar.monthrange(prev_quarter_end.year, end_month)[1]
            end = date(prev_quarter_end.year, end_month, last_day)
        elif period_type == TimePeriodType.PP:
            # Previous complete period (month)
            prev_month = reference_date - relativedelta(months=1)
            start = date(prev_month.year, prev_month.month, 1)
            last_day = calendar.monthrange(prev_month.year, prev_month.month)[1]
            end = date(prev_month.year, prev_month.month, last_day)
        else:
            # Default to full current period
            start = date(reference_date.year, 1, 1)
            end = reference_date

        return start, end

    def _get_comparison_period(
        self,
        period_type: TimePeriodType,
        period_start: date,
        period_end: date,
        fiscal_config: Optional[FiscalCalendarConfig] = None,
    ) -> tuple[Optional[date], Optional[date]]:
        """Get comparison period dates"""
        if period_type in [TimePeriodType.YTD, TimePeriodType.SPLY, TimePeriodType.PPY]:
            # Compare to previous year
            return (
                date(period_start.year - 1, period_start.month, period_start.day),
                date(period_end.year - 1, period_end.month, period_end.day),
            )
        elif period_type in [TimePeriodType.QTD, TimePeriodType.SPLQ, TimePeriodType.PPQ]:
            # Compare to previous quarter
            comp_end = period_end - relativedelta(months=3)
            comp_start = period_start - relativedelta(months=3)
            return (comp_start, comp_end)
        elif period_type in [TimePeriodType.MTD, TimePeriodType.SPLM, TimePeriodType.PPM]:
            # Compare to previous month
            comp_end = period_end - relativedelta(months=1)
            comp_start = period_start - relativedelta(months=1)
            return (comp_start, comp_end)
        elif period_type == TimePeriodType.ROLLING:
            # Compare to previous rolling period
            period_length = (period_end - period_start).days
            comp_end = period_start - timedelta(days=1)
            comp_start = comp_end - timedelta(days=period_length)
            return (comp_start, comp_end)
        else:
            # Default: compare to previous year
            return (
                date(period_start.year - 1, period_start.month, period_start.day),
                date(period_end.year - 1, period_end.month, period_end.day),
            )

    def _get_aggregation_expr(
        self,
        aggregation: AggregationType,
        column: str,
    ) -> str:
        """Get SQL aggregation expression"""
        if aggregation == AggregationType.SUM:
            return f"SUM({column})"
        elif aggregation == AggregationType.AVG:
            return f"AVG({column})"
        elif aggregation == AggregationType.MIN:
            return f"MIN({column})"
        elif aggregation == AggregationType.MAX:
            return f"MAX({column})"
        elif aggregation == AggregationType.COUNT:
            return f"COUNT({column})"
        elif aggregation == AggregationType.FIRST:
            if self.db_type == "postgresql":
                return f"(ARRAY_AGG({column} ORDER BY {column}))[1]"
            return f"MIN({column})"  # Fallback
        elif aggregation == AggregationType.LAST:
            if self.db_type == "postgresql":
                return f"(ARRAY_AGG({column} ORDER BY {column} DESC))[1]"
            return f"MAX({column})"  # Fallback
        return f"SUM({column})"

    def _build_date_filter(
        self,
        date_column: str,
        start_date: date,
        end_date: date,
    ) -> str:
        """Build SQL date filter"""
        return f"{date_column} >= '{start_date}' AND {date_column} <= '{end_date}'"

    def _subtract_periods(
        self,
        ref_date: date,
        periods: int,
        granularity: TimeGranularity,
    ) -> date:
        """Subtract periods from a date"""
        if granularity == TimeGranularity.YEAR:
            return ref_date - relativedelta(years=periods)
        elif granularity == TimeGranularity.QUARTER:
            return ref_date - relativedelta(months=periods * 3)
        elif granularity == TimeGranularity.MONTH:
            return ref_date - relativedelta(months=periods)
        elif granularity == TimeGranularity.WEEK:
            return ref_date - timedelta(weeks=periods)
        elif granularity == TimeGranularity.DAY:
            return ref_date - timedelta(days=periods)
        elif granularity == TimeGranularity.HOUR:
            return ref_date  # Hours handled differently
        return ref_date

    def _get_period_end(
        self,
        ref_date: date,
        granularity: TimeGranularity,
    ) -> date:
        """Get end of current period"""
        if granularity == TimeGranularity.YEAR:
            return date(ref_date.year, 12, 31)
        elif granularity == TimeGranularity.QUARTER:
            quarter = (ref_date.month - 1) // 3 + 1
            end_month = quarter * 3
            last_day = calendar.monthrange(ref_date.year, end_month)[1]
            return date(ref_date.year, end_month, last_day)
        elif granularity == TimeGranularity.MONTH:
            last_day = calendar.monthrange(ref_date.year, ref_date.month)[1]
            return date(ref_date.year, ref_date.month, last_day)
        elif granularity == TimeGranularity.WEEK:
            # End of week (Sunday)
            days_until_sunday = 6 - ref_date.weekday()
            return ref_date + timedelta(days=days_until_sunday)
        return ref_date

    def _get_fiscal_year_start(
        self,
        ref_date: date,
        config: FiscalCalendarConfig,
    ) -> date:
        """Get start of fiscal year"""
        fiscal_start = date(ref_date.year, config.fiscal_year_start_month, config.fiscal_year_start_day)
        if ref_date < fiscal_start:
            fiscal_start = date(ref_date.year - 1, config.fiscal_year_start_month, config.fiscal_year_start_day)
        return fiscal_start

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def generate_date_table_sql(
        self,
        config: DateTableConfig,
    ) -> str:
        """Generate SQL to create a date dimension table"""
        columns = DATE_TABLE_COLUMNS.copy()
        if config.include_fiscal and config.fiscal_config:
            columns.extend(FISCAL_DATE_TABLE_COLUMNS)

        # Build column definitions
        col_defs = ",\n    ".join([f"{c.name} {c.sql_type}" for c in columns])

        # Generate recursive CTE for date generation
        sql = f"""
-- Create date dimension table
CREATE TABLE IF NOT EXISTS {config.table_name} (
    {col_defs}
);

-- Populate date table
WITH RECURSIVE date_series AS (
    SELECT DATE '{config.start_date}' AS dt
    UNION ALL
    SELECT dt + INTERVAL '1 day'
    FROM date_series
    WHERE dt < DATE '{config.end_date}'
)
INSERT INTO {config.table_name}
SELECT
    CAST(TO_CHAR(dt, 'YYYYMMDD') AS INTEGER) AS date_key,
    dt AS full_date,
    EXTRACT(DOW FROM dt)::INTEGER + 1 AS day_of_week,
    TO_CHAR(dt, 'Day') AS day_of_week_name,
    EXTRACT(DAY FROM dt)::INTEGER AS day_of_month,
    EXTRACT(DOY FROM dt)::INTEGER AS day_of_year,
    EXTRACT(WEEK FROM dt)::INTEGER AS week_of_year,
    EXTRACT(MONTH FROM dt)::INTEGER AS month_number,
    TO_CHAR(dt, 'Month') AS month_name,
    TO_CHAR(dt, 'Mon') AS month_short_name,
    EXTRACT(QUARTER FROM dt)::INTEGER AS quarter_number,
    'Q' || EXTRACT(QUARTER FROM dt)::INTEGER AS quarter_name,
    EXTRACT(YEAR FROM dt)::INTEGER AS year_number,
    TO_CHAR(dt, 'YYYY-MM') AS year_month,
    TO_CHAR(dt, 'YYYY') || '-Q' || EXTRACT(QUARTER FROM dt)::INTEGER AS year_quarter,
    EXTRACT(DOW FROM dt) IN (0, 6) AS is_weekend,
    EXTRACT(DOW FROM dt) NOT IN (0, 6) AS is_weekday,
    EXTRACT(DAY FROM dt) = 1 AS is_month_start,
    dt = (DATE_TRUNC('month', dt) + INTERVAL '1 month' - INTERVAL '1 day')::DATE AS is_month_end,
    EXTRACT(MONTH FROM dt) IN (1, 4, 7, 10) AND EXTRACT(DAY FROM dt) = 1 AS is_quarter_start,
    EXTRACT(MONTH FROM dt) IN (3, 6, 9, 12) AND dt = (DATE_TRUNC('month', dt) + INTERVAL '1 month' - INTERVAL '1 day')::DATE AS is_quarter_end,
    EXTRACT(MONTH FROM dt) = 1 AND EXTRACT(DAY FROM dt) = 1 AS is_year_start,
    EXTRACT(MONTH FROM dt) = 12 AND EXTRACT(DAY FROM dt) = 31 AS is_year_end
FROM date_series;
"""

        return sql


def get_time_intelligence_service(db_type: str = "postgresql") -> TimeIntelligenceService:
    """Factory function to get service instance"""
    return TimeIntelligenceService(db_type=db_type)
