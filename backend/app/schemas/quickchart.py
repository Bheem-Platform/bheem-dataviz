"""Schemas for Quick Charts feature - intelligent auto-chart generation."""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum


class ColumnDataType(str, Enum):
    """Categorized data types for chart selection."""
    CATEGORICAL = "categorical"
    NUMERIC = "numeric"
    TEMPORAL = "temporal"
    TEXT = "text"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"


class Cardinality(str, Enum):
    """Column cardinality classification."""
    LOW = "low"        # < 10 distinct values
    MEDIUM = "medium"  # 10-100 distinct values
    HIGH = "high"      # > 100 distinct values


class TopValue(BaseModel):
    """Represents a frequent value in a column."""
    value: Any
    count: int
    percent: float


class ColumnProfile(BaseModel):
    """Profile of a single column with statistics."""
    name: str
    sql_type: str
    data_type: ColumnDataType

    # Row statistics
    row_count: int
    null_count: int
    null_percent: float
    distinct_count: int
    cardinality: Cardinality

    # For numeric columns
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean: Optional[float] = None

    # For categorical columns
    top_values: Optional[List[TopValue]] = None


class TableProfile(BaseModel):
    """Complete profile of a database table."""
    connection_id: str
    schema_name: str
    table_name: str
    row_count: int
    columns: List[ColumnProfile]

    # Derived insights
    has_temporal: bool = False
    has_numeric: bool = False
    has_categorical: bool = False
    suggested_dimensions: List[str] = []
    suggested_measures: List[str] = []


class DimensionConfig(BaseModel):
    """Configuration for a chart dimension."""
    column: str
    alias: str


class MeasureConfig(BaseModel):
    """Configuration for a chart measure."""
    column: str
    aggregation: str  # sum, count, avg, min, max
    alias: str


class ChartRecommendation(BaseModel):
    """A recommended chart configuration."""
    id: str
    chart_type: str
    confidence: float
    reason: str
    title: str
    description: str

    # Data configuration
    dimensions: List[DimensionConfig]
    measures: List[MeasureConfig]

    # Pre-built configs
    chart_config: Dict[str, Any]
    query_config: Dict[str, Any]


class QuickChartResponse(BaseModel):
    """Response for quick chart suggestions."""
    connection_id: str
    schema_name: str
    table_name: str
    profile: TableProfile
    recommendations: List[ChartRecommendation]


class TableSummary(BaseModel):
    """Summary of a table for quick chart selection."""
    schema_name: str
    table_name: str
    row_count: Optional[int] = None
    column_count: int
    has_numeric: bool = False
    has_temporal: bool = False


class QuickChartCreateRequest(BaseModel):
    """Request to create a chart from a quick chart suggestion."""
    recommendation_id: Optional[str] = None
    title: Optional[str] = None
    dashboard_id: Optional[str] = None
    connection_id: str
    chart_type: str
    chart_config: Dict[str, Any]
    query_config: Dict[str, Any]


class HomeQuickSuggestion(BaseModel):
    """Quick chart suggestion for home page."""
    id: str
    title: str
    chart_type: str
    confidence: float
    table_name: str
    connection_id: str
    connection_name: str
    chart_config: Dict[str, Any]
    query_config: Dict[str, Any]
