"""Pydantic schemas for Semantic Model API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class RelationshipType(str, Enum):
    one_to_one = "one_to_one"
    one_to_many = "one_to_many"
    many_to_one = "many_to_one"


class JoinType(str, Enum):
    inner = "inner"
    left = "left"
    right = "right"
    full = "full"


class AggregateType(str, Enum):
    sum = "sum"
    count = "count"
    count_distinct = "count_distinct"
    avg = "avg"
    min = "min"
    max = "max"


class FormatType(str, Enum):
    number = "number"
    currency = "currency"
    percent = "percent"
    date = "date"
    text = "text"


# ============================================================================
# TABLE SCHEMAS
# ============================================================================

class ModelTable(BaseModel):
    """A table included in the semantic model."""
    name: str
    schema_name: str = "public"
    alias: Optional[str] = None  # Friendly display name
    description: Optional[str] = None
    # Position on canvas for UI
    x: float = 0
    y: float = 0


class ModelTableCreate(BaseModel):
    """Schema for adding a table to a model."""
    name: str
    schema_name: str = "public"
    alias: Optional[str] = None
    x: float = 0
    y: float = 0


# ============================================================================
# RELATIONSHIP SCHEMAS
# ============================================================================

class Relationship(BaseModel):
    """A relationship between two tables."""
    id: str
    name: Optional[str] = None
    from_table: str  # Table name
    from_column: str
    to_table: str  # Table name
    to_column: str
    relationship_type: RelationshipType = RelationshipType.many_to_one
    join_type: JoinType = JoinType.left


class RelationshipCreate(BaseModel):
    """Schema for creating a relationship."""
    name: Optional[str] = None
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: RelationshipType = RelationshipType.many_to_one
    join_type: JoinType = JoinType.left


class RelationshipUpdate(BaseModel):
    """Schema for updating a relationship."""
    name: Optional[str] = None
    relationship_type: Optional[RelationshipType] = None
    join_type: Optional[JoinType] = None


# ============================================================================
# MEASURE SCHEMAS
# ============================================================================

class Measure(BaseModel):
    """A pre-defined measure (aggregation)."""
    id: str
    name: str
    description: Optional[str] = None
    table: str  # Source table
    column: str  # Source column
    aggregate: AggregateType
    format: FormatType = FormatType.number
    format_config: Optional[Dict[str, Any]] = None  # e.g., {"currency": "INR", "decimals": 2}


class MeasureCreate(BaseModel):
    """Schema for creating a measure."""
    name: str
    description: Optional[str] = None
    table: str
    column: str
    aggregate: AggregateType
    format: FormatType = FormatType.number
    format_config: Optional[Dict[str, Any]] = None


class MeasureUpdate(BaseModel):
    """Schema for updating a measure."""
    name: Optional[str] = None
    description: Optional[str] = None
    aggregate: Optional[AggregateType] = None
    format: Optional[FormatType] = None
    format_config: Optional[Dict[str, Any]] = None


# ============================================================================
# DIMENSION SCHEMAS
# ============================================================================

class Dimension(BaseModel):
    """A dimension (grouping/filtering field)."""
    id: str
    name: str
    description: Optional[str] = None
    table: str
    column: str
    hierarchy: Optional[List[str]] = None  # For drill-down: ["year", "quarter", "month"]
    format: FormatType = FormatType.text


class DimensionCreate(BaseModel):
    """Schema for creating a dimension."""
    name: str
    description: Optional[str] = None
    table: str
    column: str
    hierarchy: Optional[List[str]] = None
    format: FormatType = FormatType.text


# ============================================================================
# COLUMN ALIAS SCHEMAS
# ============================================================================

class ColumnAlias(BaseModel):
    """A friendly name for a column."""
    table: str
    column: str
    alias: str
    description: Optional[str] = None
    format: Optional[FormatType] = None


# ============================================================================
# SEMANTIC MODEL SCHEMAS
# ============================================================================

class SemanticModelBase(BaseModel):
    """Base schema for semantic model."""
    name: str
    description: Optional[str] = None


class SemanticModelCreate(SemanticModelBase):
    """Schema for creating a semantic model."""
    connection_id: str
    tables: List[ModelTableCreate] = []


class SemanticModelUpdate(BaseModel):
    """Schema for updating a semantic model."""
    name: Optional[str] = None
    description: Optional[str] = None


class SemanticModelResponse(SemanticModelBase):
    """Schema for semantic model response."""
    id: str
    connection_id: str
    tables: List[ModelTable] = []
    relationships: List[Relationship] = []
    measures: List[Measure] = []
    dimensions: List[Dimension] = []
    column_aliases: List[ColumnAlias] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SemanticModelSummary(BaseModel):
    """Summary view of a semantic model for list display."""
    id: str
    name: str
    description: Optional[str] = None
    connection_id: str
    connection_name: Optional[str] = None
    tables_count: int = 0
    relationships_count: int = 0
    measures_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================================
# MODEL FIELD SCHEMAS (for chart builder)
# ============================================================================

class ModelField(BaseModel):
    """A field available in the model (for chart builder)."""
    table: str
    table_alias: Optional[str] = None
    column: str
    column_alias: Optional[str] = None
    data_type: str
    is_measure: bool = False
    is_dimension: bool = False
    format: Optional[FormatType] = None


class ModelFieldsResponse(BaseModel):
    """Response containing all available fields from a model."""
    model_id: str
    model_name: str
    fields: List[ModelField]
    measures: List[Measure]
    dimensions: List[Dimension]


# ============================================================================
# QUERY GENERATION SCHEMAS
# ============================================================================

class ModelQueryRequest(BaseModel):
    """Request to generate a query from a semantic model."""
    model_id: str
    select_fields: List[Dict[str, str]]  # [{"table": "orders", "column": "amount"}]
    measures: List[str] = []  # Measure IDs to include
    dimensions: List[str] = []  # Dimension IDs to group by
    filters: List[Dict[str, Any]] = []
    limit: int = 100
    offset: int = 0


class ModelQueryResponse(BaseModel):
    """Response from model query execution."""
    columns: List[Dict[str, Any]]
    rows: List[Dict[str, Any]]
    total_rows: int
    sql_generated: Optional[str] = None
    execution_time_ms: int
