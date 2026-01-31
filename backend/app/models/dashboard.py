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

    # Global filter configuration
    global_filter_config = Column(JSON, nullable=True)  # GlobalFilterConfig with slicers
    default_filters = Column(JSON, nullable=True)  # Default filter values

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    charts = relationship("SavedChart", back_populates="dashboard", cascade="all, delete-orphan")
    filter_presets = relationship("SavedFilterPreset", backref="dashboard", cascade="all, delete-orphan", foreign_keys="SavedFilterPreset.dashboard_id")


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

    # Advanced filter configuration
    filter_config = Column(JSON, nullable=True)  # Slicer configurations for this chart
    default_filters = Column(JSON, nullable=True)  # Default filter values

    # Drill-down/through configuration
    drill_config = Column(JSON, nullable=True)  # DrillConfig with hierarchy and targets

    # Conditional formatting
    conditional_formats = Column(JSON, nullable=True)  # List of ConditionalFormat

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


class SavedFilterPreset(Base):
    """A saved filter preset for reusable filter configurations."""
    __tablename__ = "saved_filter_presets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Scope - can be global, dashboard-level, or chart-level
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=True)
    chart_id = Column(UUID(as_uuid=True), ForeignKey("saved_charts.id", ondelete="CASCADE"), nullable=True)

    # Filter configuration
    filters = Column(JSON, nullable=False, default=list)  # List of FilterCondition
    slicers = Column(JSON, nullable=True)  # List of SlicerConfig
    global_filter_config = Column(JSON, nullable=True)  # GlobalFilterConfig

    # Default preset
    is_default = Column(Boolean, default=False)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DashboardFilterState(Base):
    """Persisted filter state for a dashboard session."""
    __tablename__ = "dashboard_filter_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)

    # Current filter state
    filter_state = Column(JSON, nullable=False, default=dict)  # column -> selected values
    date_filter_state = Column(JSON, nullable=True)  # date filter configurations
    cross_filter_state = Column(JSON, nullable=True)  # cross-filter selections

    # Session info
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
