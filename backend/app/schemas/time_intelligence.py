"""
Time Intelligence Schemas

Provides schemas for time-based calculations similar to DAX time intelligence:
- Year-to-Date (YTD)
- Quarter-to-Date (QTD)
- Month-to-Date (MTD)
- Same Period Last Year (SPLY)
- Rolling Periods
- Period-over-Period comparisons
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import date


class TimeGranularity(str, Enum):
    """Time granularity levels"""
    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    HOUR = "hour"


class TimePeriodType(str, Enum):
    """Type of time period calculation"""
    # To-Date functions
    YTD = "ytd"            # Year-to-Date
    QTD = "qtd"            # Quarter-to-Date
    MTD = "mtd"            # Month-to-Date
    WTD = "wtd"            # Week-to-Date

    # Same Period comparisons
    SPLY = "sply"          # Same Period Last Year
    SPLM = "splm"          # Same Period Last Month
    SPLQ = "splq"          # Same Period Last Quarter

    # Previous Period
    PP = "pp"              # Previous Period
    PPY = "ppy"            # Previous Period Year
    PPQ = "ppq"            # Previous Period Quarter
    PPM = "ppm"            # Previous Period Month

    # Rolling Periods
    ROLLING = "rolling"    # Rolling N periods
    TRAILING = "trailing"  # Trailing N periods

    # Parallel Period
    PARALLEL = "parallel"  # Parallel period offset

    # Date Range
    DATE_RANGE = "date_range"  # Custom date range

    # Fiscal Calendar
    FISCAL_YTD = "fiscal_ytd"
    FISCAL_QTD = "fiscal_qtd"


class AggregationType(str, Enum):
    """Aggregation types for time intelligence"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    FIRST = "first"
    LAST = "last"


class FiscalCalendarConfig(BaseModel):
    """Configuration for fiscal calendar"""
    fiscal_year_start_month: int = Field(1, ge=1, le=12, description="Month fiscal year starts (1-12)")
    fiscal_year_start_day: int = Field(1, ge=1, le=31, description="Day fiscal year starts")
    week_starts_on: int = Field(0, ge=0, le=6, description="Day week starts (0=Monday, 6=Sunday)")


class TimeIntelligenceFunction(BaseModel):
    """Definition of a time intelligence function"""
    id: str = Field(..., description="Unique function ID")
    name: str = Field(..., description="Function display name")
    period_type: TimePeriodType = Field(..., description="Type of time period calculation")
    date_column: str = Field(..., description="Column containing dates")
    measure_column: str = Field(..., description="Column to aggregate")
    aggregation: AggregationType = Field(AggregationType.SUM, description="Aggregation function")

    # Period-specific parameters
    periods: Optional[int] = Field(None, description="Number of periods for rolling/trailing")
    offset: Optional[int] = Field(None, description="Period offset for parallel period")
    granularity: Optional[TimeGranularity] = Field(None, description="Granularity for rolling periods")

    # Fiscal calendar
    use_fiscal_calendar: bool = Field(False, description="Use fiscal calendar instead of standard")
    fiscal_config: Optional[FiscalCalendarConfig] = None

    # Date range (for custom)
    start_date: Optional[str] = Field(None, description="Start date for custom range")
    end_date: Optional[str] = Field(None, description="End date for custom range")

    # Output
    output_column: Optional[str] = Field(None, description="Name for result column")
    include_comparison: bool = Field(False, description="Include comparison value")
    include_pct_change: bool = Field(False, description="Include percentage change")


class TimeIntelligenceRequest(BaseModel):
    """Request to calculate time intelligence"""
    connection_id: str = Field(..., description="Database connection ID")
    schema_name: str = Field(..., description="Schema name")
    table_name: str = Field(..., description="Table name")
    functions: list[TimeIntelligenceFunction] = Field(..., description="Functions to calculate")
    filters: Optional[dict[str, Any]] = Field(None, description="Additional filters")
    group_by: Optional[list[str]] = Field(None, description="Columns to group by")
    reference_date: Optional[str] = Field(None, description="Reference date (defaults to today)")


class TimeIntelligenceResult(BaseModel):
    """Result of a time intelligence calculation"""
    function_id: str = Field(..., description="ID of the function")
    value: Optional[float] = Field(None, description="Calculated value")
    comparison_value: Optional[float] = Field(None, description="Comparison value")
    pct_change: Optional[float] = Field(None, description="Percentage change")
    period_start: Optional[str] = Field(None, description="Start of the period")
    period_end: Optional[str] = Field(None, description="End of the period")
    comparison_period_start: Optional[str] = Field(None, description="Start of comparison period")
    comparison_period_end: Optional[str] = Field(None, description="End of comparison period")


class TimeIntelligenceResponse(BaseModel):
    """Response from time intelligence calculation"""
    success: bool = Field(True)
    results: list[TimeIntelligenceResult] = Field(default_factory=list)
    query: Optional[str] = Field(None, description="Generated query")
    error: Optional[str] = Field(None)


# Pre-built time intelligence measures

class TimeIntelligenceMeasure(BaseModel):
    """A pre-built time intelligence measure"""
    id: str
    name: str
    description: str
    function: TimeIntelligenceFunction


# Date Table Configuration

class DateTableConfig(BaseModel):
    """Configuration for generating a date dimension table"""
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    table_name: str = Field("dim_date", description="Name for the date table")
    include_fiscal: bool = Field(False, description="Include fiscal calendar columns")
    fiscal_config: Optional[FiscalCalendarConfig] = None
    include_holidays: bool = Field(False, description="Include holiday flags")
    holiday_country: Optional[str] = Field(None, description="Country code for holidays")


class DateTableColumn(BaseModel):
    """Column definition for date table"""
    name: str
    sql_type: str
    description: str


# Standard date table columns
DATE_TABLE_COLUMNS = [
    DateTableColumn(name="date_key", sql_type="INTEGER", description="Date key (YYYYMMDD)"),
    DateTableColumn(name="full_date", sql_type="DATE", description="Full date"),
    DateTableColumn(name="day_of_week", sql_type="INTEGER", description="Day of week (1-7)"),
    DateTableColumn(name="day_of_week_name", sql_type="VARCHAR(20)", description="Day name"),
    DateTableColumn(name="day_of_month", sql_type="INTEGER", description="Day of month (1-31)"),
    DateTableColumn(name="day_of_year", sql_type="INTEGER", description="Day of year (1-366)"),
    DateTableColumn(name="week_of_year", sql_type="INTEGER", description="Week of year (1-53)"),
    DateTableColumn(name="month_number", sql_type="INTEGER", description="Month number (1-12)"),
    DateTableColumn(name="month_name", sql_type="VARCHAR(20)", description="Month name"),
    DateTableColumn(name="month_short_name", sql_type="VARCHAR(3)", description="Month short name"),
    DateTableColumn(name="quarter_number", sql_type="INTEGER", description="Quarter (1-4)"),
    DateTableColumn(name="quarter_name", sql_type="VARCHAR(10)", description="Quarter name (Q1-Q4)"),
    DateTableColumn(name="year_number", sql_type="INTEGER", description="Year"),
    DateTableColumn(name="year_month", sql_type="VARCHAR(7)", description="Year-Month (YYYY-MM)"),
    DateTableColumn(name="year_quarter", sql_type="VARCHAR(7)", description="Year-Quarter (YYYY-Q#)"),
    DateTableColumn(name="is_weekend", sql_type="BOOLEAN", description="Is weekend"),
    DateTableColumn(name="is_weekday", sql_type="BOOLEAN", description="Is weekday"),
    DateTableColumn(name="is_month_start", sql_type="BOOLEAN", description="Is first day of month"),
    DateTableColumn(name="is_month_end", sql_type="BOOLEAN", description="Is last day of month"),
    DateTableColumn(name="is_quarter_start", sql_type="BOOLEAN", description="Is first day of quarter"),
    DateTableColumn(name="is_quarter_end", sql_type="BOOLEAN", description="Is last day of quarter"),
    DateTableColumn(name="is_year_start", sql_type="BOOLEAN", description="Is first day of year"),
    DateTableColumn(name="is_year_end", sql_type="BOOLEAN", description="Is last day of year"),
]

FISCAL_DATE_TABLE_COLUMNS = [
    DateTableColumn(name="fiscal_year", sql_type="INTEGER", description="Fiscal year"),
    DateTableColumn(name="fiscal_quarter", sql_type="INTEGER", description="Fiscal quarter (1-4)"),
    DateTableColumn(name="fiscal_month", sql_type="INTEGER", description="Fiscal month (1-12)"),
    DateTableColumn(name="fiscal_week", sql_type="INTEGER", description="Fiscal week"),
    DateTableColumn(name="fiscal_year_quarter", sql_type="VARCHAR(10)", description="Fiscal Year-Quarter"),
]


# Common time intelligence templates

COMMON_TIME_INTELLIGENCE_TEMPLATES = [
    {
        "id": "ytd_sales",
        "name": "Year-to-Date Sales",
        "description": "Total sales from start of year to current date",
        "period_type": "ytd",
        "aggregation": "sum",
    },
    {
        "id": "mtd_sales",
        "name": "Month-to-Date Sales",
        "description": "Total sales from start of month to current date",
        "period_type": "mtd",
        "aggregation": "sum",
    },
    {
        "id": "sply_comparison",
        "name": "Same Period Last Year",
        "description": "Value from the same period last year",
        "period_type": "sply",
        "aggregation": "sum",
        "include_comparison": True,
        "include_pct_change": True,
    },
    {
        "id": "rolling_12_months",
        "name": "Rolling 12 Months",
        "description": "Sum of last 12 months",
        "period_type": "rolling",
        "periods": 12,
        "granularity": "month",
        "aggregation": "sum",
    },
    {
        "id": "mom_change",
        "name": "Month-over-Month Change",
        "description": "Change from previous month",
        "period_type": "ppm",
        "aggregation": "sum",
        "include_comparison": True,
        "include_pct_change": True,
    },
    {
        "id": "yoy_change",
        "name": "Year-over-Year Change",
        "description": "Change from previous year",
        "period_type": "ppy",
        "aggregation": "sum",
        "include_comparison": True,
        "include_pct_change": True,
    },
]
