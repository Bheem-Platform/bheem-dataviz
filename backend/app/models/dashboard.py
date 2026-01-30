"""Dashboard and saved chart models."""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Dashboard(Base):
    """A dashboard containing multiple saved charts."""
    __tablename__ = "dashboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)  # Icon name or emoji

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)  # User ID
    is_public = Column(Boolean, default=False)  # Shared with everyone
    is_featured = Column(Boolean, default=False)  # Show on home page

    # Layout
    layout = Column(JSON, nullable=True)  # Grid layout configuration

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    charts = relationship("SavedChart", back_populates="dashboard", cascade="all, delete-orphan")


class SavedChart(Base):
    """A saved chart configuration."""
    __tablename__ = "saved_charts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=True)

    name = Column(String, nullable=False)  # "Monthly Revenue Trend"
    description = Column(Text, nullable=True)

    # Data source
    connection_id = Column(String, nullable=False)
    semantic_model_id = Column(UUID(as_uuid=True), nullable=True)  # Optional semantic model reference
    transform_recipe_id = Column(UUID(as_uuid=True), ForeignKey("transform_recipes.id", ondelete="SET NULL"), nullable=True)  # Optional transform recipe reference

    # Chart configuration
    chart_type = Column(String, nullable=False)  # bar, line, pie, area, donut, etc.
    chart_config = Column(JSON, nullable=False)  # Full ECharts option or config

    # Query configuration (if not using semantic model)
    query_config = Column(JSON, nullable=True)  # { schema, table, dimensions, measures, filters }

    # Display settings
    width = Column(Integer, default=6)  # Grid width (1-12)
    height = Column(Integer, default=4)  # Grid height
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    is_favorite = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_viewed_at = Column(DateTime, nullable=True)
    view_count = Column(Integer, default=0)

    # Relationships
    dashboard = relationship("Dashboard", back_populates="charts")


class SavedKPI(Base):
    """A saved KPI configuration."""
    __tablename__ = "saved_kpis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)  # "Monthly Revenue"
    description = Column(Text, nullable=True)

    # Data source
    connection_id = Column(String, nullable=True)
    semantic_model_id = Column(UUID(as_uuid=True), nullable=True)
    transform_id = Column(UUID(as_uuid=True), nullable=True)

    # KPI configuration
    config = Column(JSON, nullable=False)  # Full KPI config (title, measure, aggregation, etc.)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    is_favorite = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SuggestedQuestion(Base):
    """Pre-defined questions that appear on the home page."""
    __tablename__ = "suggested_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    question = Column(String, nullable=False)  # "What were the top products last month?"
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)

    # Query that answers this question
    connection_id = Column(String, nullable=False)
    query_config = Column(JSON, nullable=False)  # Pre-built query config
    chart_type = Column(String, default="bar")

    # Display
    category = Column(String, nullable=True)  # "Sales", "Marketing", "Finance"
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
