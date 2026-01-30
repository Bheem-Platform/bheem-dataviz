"""Pydantic schemas for Transform Recipe API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class FilterOperator(str, Enum):
    eq = "="
    ne = "!="
    gt = ">"
    gte = ">="
    lt = "<"
    lte = "<="
    like = "like"
    not_like = "not_like"
    in_ = "in"
    not_in = "not_in"
    is_null = "is_null"
    is_not_null = "is_not_null"


class JoinType(str, Enum):
    inner = "inner"
    left = "left"
    right = "right"
    full = "full"


class AggregateFunction(str, Enum):
    sum = "sum"
    count = "count"
    avg = "avg"
    min = "min"
    max = "max"
    count_distinct = "count_distinct"


class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"


class CaseType(str, Enum):
    upper = "upper"
    lower = "lower"
    title = "title"


class DataType(str, Enum):
    text = "text"
    integer = "integer"
    bigint = "bigint"
    decimal = "decimal"
    boolean = "boolean"
    date = "date"
    timestamp = "timestamp"


# ============================================================================
# STEP CONFIGURATION SCHEMAS
# ============================================================================

class SelectStep(BaseModel):
    """Select specific columns."""
    type: Literal["select"] = "select"
    columns: List[str]


class RenameStep(BaseModel):
    """Rename columns."""
    type: Literal["rename"] = "rename"
    mapping: Dict[str, str]  # {old_name: new_name}


class ReorderStep(BaseModel):
    """Reorder columns."""
    type: Literal["reorder"] = "reorder"
    columns: List[str]  # New column order


class CastStep(BaseModel):
    """Change column data type."""
    type: Literal["cast"] = "cast"
    column: str
    to_type: DataType


class AddColumnStep(BaseModel):
    """Add a calculated column."""
    type: Literal["add_column"] = "add_column"
    name: str
    expression: str  # SQL expression like "qty * price"


class DropColumnStep(BaseModel):
    """Drop columns."""
    type: Literal["drop_column"] = "drop_column"
    columns: List[str]


class FilterCondition(BaseModel):
    """A single filter condition."""
    column: str
    operator: FilterOperator
    value: Optional[Any] = None  # Not needed for is_null/is_not_null


class FilterStep(BaseModel):
    """Filter rows based on conditions."""
    type: Literal["filter"] = "filter"
    conditions: List[FilterCondition]
    logic: Literal["and", "or"] = "and"  # How to combine conditions


class SortColumn(BaseModel):
    """Sort specification for a column."""
    column: str
    direction: SortDirection = SortDirection.asc


class SortStep(BaseModel):
    """Sort rows."""
    type: Literal["sort"] = "sort"
    columns: List[SortColumn]


class DeduplicateStep(BaseModel):
    """Remove duplicate rows."""
    type: Literal["deduplicate"] = "deduplicate"
    columns: Optional[List[str]] = None  # None = all columns


class LimitStep(BaseModel):
    """Limit number of rows."""
    type: Literal["limit"] = "limit"
    count: int
    offset: int = 0


class ReplaceStep(BaseModel):
    """Replace values in a column."""
    type: Literal["replace"] = "replace"
    column: str
    find: Any
    replace_with: Any


class TrimStep(BaseModel):
    """Trim whitespace from columns."""
    type: Literal["trim"] = "trim"
    columns: List[str]


class CaseStep(BaseModel):
    """Change case of string columns."""
    type: Literal["case"] = "case"
    column: str
    to: CaseType


class FillNullStep(BaseModel):
    """Replace NULL values."""
    type: Literal["fill_null"] = "fill_null"
    column: str
    value: Any


class JoinCondition(BaseModel):
    """Join condition between two columns."""
    left: str   # Column from current table
    right: str  # Column from joined table


class JoinStep(BaseModel):
    """Join with another table."""
    type: Literal["join"] = "join"
    table: str  # Table to join
    schema_name: str = "public"
    join_type: JoinType = JoinType.left
    on: List[JoinCondition]
    select_columns: Optional[List[str]] = None  # Columns to include from joined table


class UnionStep(BaseModel):
    """Union with another table."""
    type: Literal["union"] = "union"
    table: str
    schema_name: str = "public"
    all: bool = True  # UNION ALL vs UNION DISTINCT


class Aggregation(BaseModel):
    """Aggregation specification."""
    column: str
    function: AggregateFunction
    alias: str


class GroupByStep(BaseModel):
    """Group by with aggregations."""
    type: Literal["group_by"] = "group_by"
    columns: List[str]  # Group by columns
    aggregations: List[Aggregation]


# Union type for all step types
TransformStepType = Union[
    SelectStep,
    RenameStep,
    ReorderStep,
    CastStep,
    AddColumnStep,
    DropColumnStep,
    FilterStep,
    SortStep,
    DeduplicateStep,
    LimitStep,
    ReplaceStep,
    TrimStep,
    CaseStep,
    FillNullStep,
    JoinStep,
    UnionStep,
    GroupByStep
]


# ============================================================================
# RECIPE SCHEMAS
# ============================================================================

class TransformRecipeBase(BaseModel):
    """Base schema for transform recipe."""
    name: str
    description: Optional[str] = None
    source_table: str  # Source table name (required)
    source_schema: str = "public"
    steps: List[Dict[str, Any]] = []  # List of step configs


class TransformRecipeCreate(BaseModel):
    """Schema for creating a transform recipe."""
    name: str
    description: Optional[str] = None
    connection_id: str
    source_table: str  # Source table name (required)
    source_schema: str = "public"
    steps: List[Dict[str, Any]] = []


class TransformRecipeUpdate(BaseModel):
    """Schema for updating a transform recipe."""
    name: Optional[str] = None
    description: Optional[str] = None
    source_table: Optional[str] = None
    source_schema: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None


class TransformRecipeResponse(BaseModel):
    """Schema for transform recipe response."""
    name: str
    description: Optional[str] = None
    source_table: str
    source_schema: str = "public"
    steps: List[Dict[str, Any]] = []
    id: str
    connection_id: str
    result_columns: List[Dict[str, Any]] = []
    row_count: Optional[int] = None
    last_executed: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# EXECUTION SCHEMAS
# ============================================================================

class TransformExecuteRequest(BaseModel):
    """Request to execute a transform (ad-hoc or saved)."""
    connection_id: str
    source_table: str  # Source table name (required)
    source_schema: str = "public"
    steps: List[Dict[str, Any]] = []
    preview: bool = True  # If true, limit results
    limit: int = 100
    offset: int = 0  # For pagination


class TransformPreviewResponse(BaseModel):
    """Response from transform execution."""
    columns: List[Dict[str, Any]]  # [{name, type}]
    rows: List[Dict[str, Any]]
    total_rows: int
    preview_rows: int
    execution_time_ms: int
    sql_generated: Optional[str] = None  # For debugging


class TransformValidateRequest(BaseModel):
    """Request to validate a transform step."""
    connection_id: str
    source_table: str
    source_schema: str = "public"
    step: Dict[str, Any]


class TransformValidateResponse(BaseModel):
    """Response from transform validation."""
    valid: bool
    error: Optional[str] = None
    sql_preview: Optional[str] = None
