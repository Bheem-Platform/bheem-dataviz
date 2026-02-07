"""Pydantic schemas for advanced filters and slicers."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime, date
from uuid import UUID
from enum import Enum


class FilterType(str, Enum):
    """Types of filters/slicers available."""
    DROPDOWN = "dropdown"
    LIST = "list"
    TILE = "tile"
    BETWEEN = "between"
    RELATIVE_DATE = "relative_date"
    DATE_RANGE = "date_range"
    HIERARCHY = "hierarchy"
    SEARCH = "search"


class FilterOperator(str, Enum):
    """Filter operators for conditions."""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUALS = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUALS = "<="
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    LIKE = "like"
    NOT_LIKE = "not_like"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    CONTAINS = "contains"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class DateGranularity(str, Enum):
    """Date granularity for date filters."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class RelativeDateUnit(str, Enum):
    """Units for relative date calculations."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


# ============== Filter Value Models ==============

class RelativeDateOption(BaseModel):
    """Option for relative date slicer."""
    label: str
    value: int
    unit: RelativeDateUnit

    class Config:
        json_schema_extra = {
            "example": {"label": "Last 7 Days", "value": 7, "unit": "day"}
        }


class DateConfig(BaseModel):
    """Configuration for date-type slicers."""
    granularity: DateGranularity = DateGranularity.DAY
    relative_options: List[RelativeDateOption] = Field(default_factory=list)
    min_date: Optional[date] = None
    max_date: Optional[date] = None
    default_range_days: int = 30
    include_time: bool = False


class NumericConfig(BaseModel):
    """Configuration for numeric range slicers."""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: float = 1.0
    format: str = "{value}"
    show_histogram: bool = False


class HierarchyLevel(BaseModel):
    """A level in a hierarchy slicer."""
    column: str
    label: str
    parent_column: Optional[str] = None


class HierarchyConfig(BaseModel):
    """Configuration for hierarchy slicers."""
    levels: List[HierarchyLevel]
    expand_all: bool = False
    single_select_per_level: bool = False


# ============== Slicer Configuration ==============

class SlicerConfig(BaseModel):
    """Configuration for a slicer/filter UI component."""
    type: FilterType
    column: str
    label: Optional[str] = None

    # Common options
    multi_select: bool = True
    select_all_enabled: bool = True
    search_enabled: bool = True
    show_count: bool = False
    default_values: Optional[List[Any]] = None

    # Type-specific configs
    date_config: Optional[DateConfig] = None
    numeric_config: Optional[NumericConfig] = None
    hierarchy_config: Optional[HierarchyConfig] = None

    # Display options
    width: int = 200
    collapsed: bool = False
    visible: bool = True
    sort_order: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "type": "dropdown",
                "column": "category",
                "label": "Category",
                "multi_select": True,
                "search_enabled": True
            }
        }


# ============== Filter Condition Models ==============

class FilterCondition(BaseModel):
    """A single filter condition."""
    column: str
    operator: FilterOperator = FilterOperator.EQUALS
    value: Optional[Any] = None
    value2: Optional[Any] = None  # For BETWEEN operator
    data_type: Optional[str] = None  # string, number, date, boolean

    class Config:
        json_schema_extra = {
            "example": {
                "column": "status",
                "operator": "in",
                "value": ["active", "pending"]
            }
        }


class RelativeDateFilter(BaseModel):
    """A relative date filter (e.g., last 7 days)."""
    column: str
    value: int
    unit: RelativeDateUnit
    include_current: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "column": "created_at",
                "value": 7,
                "unit": "day",
                "include_current": True
            }
        }


class DateRangeFilter(BaseModel):
    """A date range filter with start and end dates."""
    column: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_start: bool = True
    include_end: bool = True


class FilterGroup(BaseModel):
    """A group of filters combined with AND/OR logic."""
    logic: Literal["and", "or"] = "and"
    conditions: List[Union[FilterCondition, "FilterGroup"]] = Field(default_factory=list)


# ============== Dashboard Filter State ==============

class DashboardFilterState(BaseModel):
    """Current state of all filters on a dashboard."""
    dashboard_id: UUID
    filters: Dict[str, Any] = Field(default_factory=dict)  # column -> selected values
    date_filters: Dict[str, Union[RelativeDateFilter, DateRangeFilter]] = Field(default_factory=dict)
    cross_filter_source: Optional[str] = None  # chart_id that triggered cross-filter
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChartFilterState(BaseModel):
    """Filter state for a specific chart."""
    chart_id: UUID
    applied_filters: List[FilterCondition] = Field(default_factory=list)
    inherited_from_dashboard: bool = True
    local_overrides: Dict[str, Any] = Field(default_factory=dict)


# ============== Filter Options Response ==============

class FilterOptionValue(BaseModel):
    """A single filter option value with count."""
    value: Any
    label: Optional[str] = None
    count: Optional[int] = None
    children: Optional[List["FilterOptionValue"]] = None  # For hierarchy


class FilterOptionsResponse(BaseModel):
    """Response containing available filter options."""
    column: str
    data_type: str = "string"
    total_count: int = 0
    distinct_count: int = 0
    null_count: int = 0
    values: List[FilterOptionValue] = Field(default_factory=list)
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None

    # For date columns
    min_date: Optional[date] = None
    max_date: Optional[date] = None


class MultiColumnFilterOptionsResponse(BaseModel):
    """Response containing filter options for multiple columns."""
    columns: Dict[str, FilterOptionsResponse] = Field(default_factory=dict)


# ============== Global Filter Configuration ==============

class GlobalFilterConfig(BaseModel):
    """Configuration for dashboard-level global filters."""
    slicers: List[SlicerConfig] = Field(default_factory=list)
    cross_filter_enabled: bool = True
    sync_slicers: bool = True  # Sync slicer selections across pages
    filter_pane_visible: bool = True
    filter_pane_position: Literal["left", "right", "top"] = "right"


# ============== Filter Request/Response Models ==============

class ApplyFiltersRequest(BaseModel):
    """Request to apply filters to a chart or dashboard."""
    filters: List[FilterCondition] = Field(default_factory=list)
    date_filters: List[Union[RelativeDateFilter, DateRangeFilter]] = Field(default_factory=list)
    limit: int = 1000

    class Config:
        json_schema_extra = {
            "example": {
                "filters": [
                    {"column": "category", "operator": "in", "value": ["Electronics", "Books"]},
                    {"column": "price", "operator": ">=", "value": 100}
                ],
                "date_filters": [
                    {"column": "order_date", "value": 30, "unit": "day"}
                ],
                "limit": 1000
            }
        }


class SaveFiltersRequest(BaseModel):
    """Request to save filter configuration."""
    name: str
    description: Optional[str] = None
    filters: List[FilterCondition] = Field(default_factory=list)
    slicers: List[SlicerConfig] = Field(default_factory=list)
    is_default: bool = False


class SavedFilterPreset(BaseModel):
    """A saved filter preset."""
    id: UUID
    name: str
    description: Optional[str] = None
    dashboard_id: Optional[UUID] = None
    chart_id: Optional[UUID] = None
    filters: Optional[List[FilterCondition]] = Field(default_factory=list)
    slicers: Optional[List[SlicerConfig]] = Field(default_factory=list)
    is_default: bool = False
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    @validator('filters', 'slicers', pre=True, always=True)
    def ensure_list(cls, v):
        return v if v is not None else []

    class Config:
        from_attributes = True


# ============== Cross-Filter Models ==============

class CrossFilterEvent(BaseModel):
    """Event when a user clicks on a chart element for cross-filtering."""
    source_chart_id: UUID
    selected_data: Dict[str, Any]  # column -> value mappings
    action: Literal["add", "remove", "replace"] = "replace"


class CrossFilterConfig(BaseModel):
    """Configuration for cross-filtering between charts."""
    enabled: bool = True
    source_charts: List[UUID] = Field(default_factory=list)  # Charts that can trigger cross-filter
    target_charts: List[UUID] = Field(default_factory=list)  # Charts that respond to cross-filter
    column_mappings: Dict[str, str] = Field(default_factory=dict)  # source_col -> target_col


# Enable forward references for recursive models
FilterGroup.model_rebuild()
FilterOptionValue.model_rebuild()
