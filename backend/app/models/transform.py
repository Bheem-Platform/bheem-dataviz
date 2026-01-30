"""Transform Recipe model for storing data transformation pipelines."""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import uuid

from app.database import Base


class TransformRecipe(Base):
    """
    Stores a reusable data transformation recipe.

    A recipe consists of:
    - A source (connection + table)
    - A series of transform steps (stored as JSON)
    - Metadata for management
    """
    __tablename__ = "transform_recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Source configuration - always a table
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.id", ondelete="CASCADE"), nullable=False)
    source_table = Column(String(255), nullable=False)  # Source table name
    source_schema = Column(String(255), default="public")  # Schema name

    # Transform steps - array of step objects
    # Each step: {"type": "filter", "config": {...}}
    steps = Column(JSONB, default=list)

    # Result configuration
    result_columns = Column(JSONB, default=list)  # Final column list after transforms

    # Caching/Performance
    is_cached = Column(String(50), default="false")  # Whether to cache results
    cache_ttl = Column(Integer, default=3600)  # Cache TTL in seconds
    last_executed = Column(DateTime(timezone=True), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)  # Last execution time

    # Row count from last execution
    row_count = Column(Integer, nullable=True)

    # Ownership
    tenant_id = Column(UUID(as_uuid=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to connection - passive_deletes lets DB handle CASCADE
    connection = relationship("Connection", backref=backref("transform_recipes", passive_deletes=True))


class TransformStep:
    """
    Reference for transform step types (not a DB model, just documentation).

    Step Types:
    -----------

    COLUMN OPERATIONS:
    - select: {"type": "select", "columns": ["col1", "col2"]}
    - rename: {"type": "rename", "mapping": {"old_name": "new_name"}}
    - reorder: {"type": "reorder", "columns": ["col2", "col1", "col3"]}
    - cast: {"type": "cast", "column": "col1", "to_type": "integer"}
    - add_column: {"type": "add_column", "name": "total", "expression": "qty * price"}
    - drop_column: {"type": "drop_column", "columns": ["col1", "col2"]}

    ROW OPERATIONS:
    - filter: {"type": "filter", "conditions": [{"column": "status", "op": "=", "value": "active"}]}
    - sort: {"type": "sort", "columns": [{"column": "date", "direction": "desc"}]}
    - deduplicate: {"type": "deduplicate", "columns": ["col1", "col2"]}  # or null for all
    - limit: {"type": "limit", "count": 100, "offset": 0}

    DATA CLEANING:
    - replace: {"type": "replace", "column": "status", "find": "NULL", "replace_with": "Unknown"}
    - trim: {"type": "trim", "columns": ["name", "email"]}
    - case: {"type": "case", "column": "name", "to": "upper"}  # upper, lower, title
    - fill_null: {"type": "fill_null", "column": "amount", "value": 0}

    TABLE OPERATIONS:
    - join: {"type": "join", "table": "customers", "join_type": "left",
             "on": [{"left": "customer_id", "right": "id"}]}
    - union: {"type": "union", "table": "archived_orders", "all": true}

    AGGREGATIONS:
    - group_by: {"type": "group_by",
                 "columns": ["category", "month"],
                 "aggregations": [
                     {"column": "amount", "function": "sum", "alias": "total_amount"},
                     {"column": "id", "function": "count", "alias": "order_count"}
                 ]}
    """
    pass
