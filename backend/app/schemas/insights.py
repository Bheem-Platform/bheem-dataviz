"""
Quick Insights Schemas

Defines data models for automated data insights including
trend detection, outlier detection, correlation analysis, and more.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class InsightType(str, Enum):
    """Type of insight detected"""
    TREND = "trend"
    OUTLIER = "outlier"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    COMPARISON = "comparison"
    ANOMALY = "anomaly"
    SEASONALITY = "seasonality"
    GROWTH = "growth"
    TOP_PERFORMER = "top_performer"
    BOTTOM_PERFORMER = "bottom_performer"
    SIGNIFICANT_CHANGE = "significant_change"


class TrendDirection(str, Enum):
    """Direction of a trend"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class InsightSeverity(str, Enum):
    """Severity/importance of an insight"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CorrelationType(str, Enum):
    """Type of correlation"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NONE = "none"


class OutlierType(str, Enum):
    """Type of outlier"""
    ABOVE = "above"
    BELOW = "below"
    BOTH = "both"


# Request Models

class InsightsRequest(BaseModel):
    """Request for insights analysis"""
    connection_id: str
    model_id: Optional[str] = None
    table_name: Optional[str] = None
    schema_name: str = "public"
    columns: list[str] = Field(default_factory=list)  # Specific columns to analyze
    date_column: Optional[str] = None  # For time-based analysis
    measure_columns: list[str] = Field(default_factory=list)  # Numeric columns for analysis
    dimension_columns: list[str] = Field(default_factory=list)  # Categorical columns
    limit_rows: int = Field(default=10000, le=100000)
    insight_types: list[InsightType] = Field(default_factory=list)  # Filter specific types


class DatasetInsightsRequest(BaseModel):
    """Request for insights on a specific dataset/chart"""
    chart_id: Optional[str] = None
    dataset_id: Optional[str] = None
    data: Optional[list[dict[str, Any]]] = None  # Pre-loaded data
    columns: list[str] = Field(default_factory=list)
    date_column: Optional[str] = None


# Insight Models

class TrendInsight(BaseModel):
    """A trend insight"""
    column: str
    direction: TrendDirection
    slope: float
    r_squared: float  # How well the trend fits
    period: str  # e.g., "last 30 days", "Q1 2024"
    change_percent: float
    start_value: float
    end_value: float
    data_points: int


class OutlierInsight(BaseModel):
    """An outlier insight"""
    column: str
    outlier_type: OutlierType
    values: list[dict[str, Any]]  # The outlier records
    count: int
    threshold_low: Optional[float] = None
    threshold_high: Optional[float] = None
    mean: float
    std_dev: float
    method: str = "iqr"  # iqr, zscore, isolation_forest


class CorrelationInsight(BaseModel):
    """A correlation insight"""
    column_1: str
    column_2: str
    correlation_type: CorrelationType
    coefficient: float  # -1 to 1
    p_value: Optional[float] = None
    sample_size: int
    interpretation: str


class DistributionInsight(BaseModel):
    """A distribution insight"""
    column: str
    distribution_type: str  # normal, skewed_left, skewed_right, uniform, bimodal
    mean: float
    median: float
    mode: Optional[float] = None
    std_dev: float
    skewness: float
    kurtosis: float
    min_value: float
    max_value: float
    quartiles: list[float]  # Q1, Q2, Q3


class ComparisonInsight(BaseModel):
    """A comparison insight"""
    measure: str
    dimension: str
    top_values: list[dict[str, Any]]
    bottom_values: list[dict[str, Any]]
    total: float
    average: float
    variance_coefficient: float


class SeasonalityInsight(BaseModel):
    """A seasonality insight"""
    column: str
    has_seasonality: bool
    period: Optional[str] = None  # daily, weekly, monthly, quarterly, yearly
    peak_periods: list[str] = Field(default_factory=list)
    trough_periods: list[str] = Field(default_factory=list)
    amplitude: Optional[float] = None


class GrowthInsight(BaseModel):
    """A growth/change insight"""
    column: str
    dimension_value: Optional[str] = None
    period_1: str
    period_2: str
    value_1: float
    value_2: float
    absolute_change: float
    percent_change: float
    is_significant: bool


class Insight(BaseModel):
    """A single insight"""
    id: str
    type: InsightType
    severity: InsightSeverity
    title: str
    description: str
    details: dict[str, Any] = Field(default_factory=dict)  # Type-specific details
    affected_columns: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0, le=1)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Visualization suggestion
    suggested_chart_type: Optional[str] = None
    suggested_query: Optional[str] = None


class InsightsResponse(BaseModel):
    """Response with all insights"""
    insights: list[Insight]
    summary: dict[str, Any] = Field(default_factory=dict)
    data_profile: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float
    rows_analyzed: int
    columns_analyzed: int


# Data Profile Models

class ColumnProfile(BaseModel):
    """Profile of a single column"""
    name: str
    data_type: str
    null_count: int
    null_percent: float
    unique_count: int
    unique_percent: float

    # For numeric columns
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    std_dev: Optional[float] = None

    # For string columns
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None

    # Top values
    top_values: list[dict[str, Any]] = Field(default_factory=list)


class DataProfile(BaseModel):
    """Complete data profile"""
    row_count: int
    column_count: int
    columns: list[ColumnProfile]
    memory_usage_bytes: Optional[int] = None
    duplicate_rows: int = 0
    complete_rows: int = 0  # Rows with no nulls


# Trend Analysis Models

class TrendAnalysisRequest(BaseModel):
    """Request for trend analysis"""
    connection_id: str
    table_name: str
    schema_name: str = "public"
    date_column: str
    value_column: str
    group_by: Optional[str] = None
    granularity: str = "day"  # day, week, month, quarter, year
    lookback_periods: int = 30


class TrendAnalysisResponse(BaseModel):
    """Response with trend analysis"""
    trend: TrendInsight
    forecast: list[dict[str, Any]] = Field(default_factory=list)
    seasonality: Optional[SeasonalityInsight] = None
    data_points: list[dict[str, Any]]


# Outlier Detection Models

class OutlierDetectionRequest(BaseModel):
    """Request for outlier detection"""
    connection_id: str
    table_name: str
    schema_name: str = "public"
    columns: list[str]
    method: str = "iqr"  # iqr, zscore, isolation_forest
    threshold: float = 1.5  # For IQR method
    zscore_threshold: float = 3.0  # For z-score method


class OutlierDetectionResponse(BaseModel):
    """Response with outlier detection"""
    outliers: list[OutlierInsight]
    total_outliers: int
    outlier_percent: float


# Correlation Analysis Models

class CorrelationAnalysisRequest(BaseModel):
    """Request for correlation analysis"""
    connection_id: str
    table_name: str
    schema_name: str = "public"
    columns: list[str]  # At least 2 columns
    method: str = "pearson"  # pearson, spearman, kendall
    min_correlation: float = 0.5  # Minimum correlation to report


class CorrelationMatrix(BaseModel):
    """Correlation matrix result"""
    columns: list[str]
    matrix: list[list[float]]
    significant_correlations: list[CorrelationInsight]


# Constants

INSIGHT_TEMPLATES = {
    InsightType.TREND: {
        "increasing": "{column} shows an increasing trend of {change_percent:.1f}% over {period}",
        "decreasing": "{column} shows a decreasing trend of {change_percent:.1f}% over {period}",
        "stable": "{column} has remained stable over {period} with minimal variation",
        "volatile": "{column} shows high volatility over {period}",
    },
    InsightType.OUTLIER: {
        "above": "Found {count} values in {column} significantly above the normal range",
        "below": "Found {count} values in {column} significantly below the normal range",
        "both": "Found {count} outliers in {column} both above and below normal range",
    },
    InsightType.CORRELATION: {
        "positive": "{column_1} and {column_2} are strongly positively correlated (r={coefficient:.2f})",
        "negative": "{column_1} and {column_2} are strongly negatively correlated (r={coefficient:.2f})",
    },
    InsightType.TOP_PERFORMER: {
        "default": "Top performing {dimension}: {top_value} with {measure}={value:.2f}",
    },
    InsightType.SIGNIFICANT_CHANGE: {
        "increase": "{column} increased by {change_percent:.1f}% from {period_1} to {period_2}",
        "decrease": "{column} decreased by {change_percent:.1f}% from {period_1} to {period_2}",
    },
}

CHART_SUGGESTIONS = {
    InsightType.TREND: "line",
    InsightType.OUTLIER: "scatter",
    InsightType.CORRELATION: "scatter",
    InsightType.DISTRIBUTION: "histogram",
    InsightType.COMPARISON: "bar",
    InsightType.TOP_PERFORMER: "bar",
    InsightType.SEASONALITY: "line",
    InsightType.GROWTH: "bar",
}

SEVERITY_THRESHOLDS = {
    "trend_change_percent": {"high": 25, "medium": 10},
    "outlier_percent": {"high": 5, "medium": 2},
    "correlation_coefficient": {"high": 0.8, "medium": 0.6},
    "growth_percent": {"high": 50, "medium": 20},
}
