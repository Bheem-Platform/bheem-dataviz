"""Semantic layer models for business-friendly data access."""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class SemanticModel(Base):
    """A semantic model that maps business terms to database tables."""
    __tablename__ = "semantic_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(String, nullable=False, index=True)  # Reference to data connection

    name = Column(String, nullable=False)  # Business name: "Sales Analysis"
    description = Column(Text, nullable=True)

    # Primary source - either a table OR a transform
    # If transform_id is set, use transform as the primary source
    # Otherwise, use schema_name + table_name
    transform_id = Column(UUID(as_uuid=True), ForeignKey("transform_recipes.id", ondelete="SET NULL"), nullable=True, index=True)

    # Source table info (used when transform_id is NULL)
    schema_name = Column(String, nullable=True)  # Made nullable for transform-based models
    table_name = Column(String, nullable=True)  # Made nullable for transform-based models

    # Additional transforms to join with the primary source
    # Format: [{"transform_id": "uuid", "alias": "t1", "join_type": "left", "join_on": [{"left": "col1", "right": "col2"}]}]
    joined_transforms = Column(JSONB, default=list)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)  # User ID

    # Relationships
    dimensions = relationship("Dimension", back_populates="semantic_model", cascade="all, delete-orphan")
    measures = relationship("Measure", back_populates="semantic_model", cascade="all, delete-orphan")
    joins = relationship("SemanticJoin", back_populates="semantic_model", cascade="all, delete-orphan")
    transform = relationship("TransformRecipe", foreign_keys=[transform_id])


class Dimension(Base):
    """A dimension (category/grouping column) in a semantic model."""
    __tablename__ = "semantic_dimensions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    semantic_model_id = Column(UUID(as_uuid=True), ForeignKey("semantic_models.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)  # Business name: "Customer Name"
    description = Column(Text, nullable=True)

    # Column mapping
    column_name = Column(String, nullable=False)  # Actual DB column: "customer_name"
    column_expression = Column(String, nullable=True)  # Optional SQL expression

    # Display settings
    display_format = Column(String, nullable=True)  # e.g., "date", "currency"
    sort_order = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    semantic_model = relationship("SemanticModel", back_populates="dimensions")


class Measure(Base):
    """A measure (numeric/aggregatable column) in a semantic model."""
    __tablename__ = "semantic_measures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    semantic_model_id = Column(UUID(as_uuid=True), ForeignKey("semantic_models.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)  # Business name: "Total Revenue"
    description = Column(Text, nullable=True)

    # Column mapping
    column_name = Column(String, nullable=False)  # Actual DB column: "amount"
    expression = Column(String, nullable=False)  # SQL expression: "SUM(amount)"

    # Aggregation type
    aggregation = Column(String, default="sum")  # sum, avg, count, min, max, count_distinct

    # Display settings
    display_format = Column(String, nullable=True)  # e.g., "currency", "percentage", "number"
    format_pattern = Column(String, nullable=True)  # e.g., "$#,##0.00"
    sort_order = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    semantic_model = relationship("SemanticModel", back_populates="measures")


class SemanticJoin(Base):
    """A join relationship between tables in a semantic model."""
    __tablename__ = "semantic_joins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    semantic_model_id = Column(UUID(as_uuid=True), ForeignKey("semantic_models.id", ondelete="CASCADE"), nullable=False)

    # Target table
    target_schema = Column(String, nullable=False)
    target_table = Column(String, nullable=False)
    target_alias = Column(String, nullable=True)  # Optional alias for the joined table

    # Join condition
    join_type = Column(String, default="left")  # left, inner, right, full
    join_condition = Column(String, nullable=False)  # e.g., "orders.customer_id = customers.id"

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    semantic_model = relationship("SemanticModel", back_populates="joins")
