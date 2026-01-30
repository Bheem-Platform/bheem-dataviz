"""Pydantic schemas for dashboards and saved charts."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Saved Chart schemas
class SavedChartBase(BaseModel):
    name: str
    description: Optional[str] = None
    connection_id: str
    semantic_model_id: Optional[UUID] = None
    transform_recipe_id: Optional[UUID] = None  # Reference to transform recipe if chart uses transformed data
    chart_type: str
    chart_config: Dict[str, Any]
    query_config: Optional[Dict[str, Any]] = None
    width: int = 6
    height: int = 4
    position_x: int = 0
    position_y: int = 0
    is_favorite: bool = False


class SavedChartCreate(SavedChartBase):
    dashboard_id: Optional[UUID] = None


class SavedChartUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chart_type: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = None
    query_config: Optional[Dict[str, Any]] = None
    transform_recipe_id: Optional[UUID] = None
    width: Optional[int] = None
    height: Optional[int] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    is_favorite: Optional[bool] = None
    dashboard_id: Optional[UUID] = None


class SavedChart(SavedChartBase):
    id: UUID
    dashboard_id: Optional[UUID] = None
    transform_recipe_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    last_viewed_at: Optional[datetime] = None
    view_count: int = 0

    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    is_public: bool = False
    is_featured: bool = False
    layout: Optional[Dict[str, Any]] = None


class DashboardCreate(DashboardBase):
    pass


class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    layout: Optional[Dict[str, Any]] = None


class Dashboard(DashboardBase):
    id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    charts: List[SavedChart] = []

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    """Summary view without nested charts."""
    id: UUID
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    is_public: bool
    is_featured: bool
    chart_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Saved KPI schemas
class SavedKPIBase(BaseModel):
    name: str
    description: Optional[str] = None
    connection_id: Optional[str] = None
    semantic_model_id: Optional[UUID] = None
    transform_id: Optional[UUID] = None
    config: Dict[str, Any]  # Full KPI config


class SavedKPICreate(SavedKPIBase):
    pass


class SavedKPIUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    connection_id: Optional[str] = None
    semantic_model_id: Optional[UUID] = None
    transform_id: Optional[UUID] = None
    config: Optional[Dict[str, Any]] = None
    is_favorite: Optional[bool] = None


class SavedKPI(SavedKPIBase):
    id: UUID
    created_by: Optional[UUID] = None
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Suggested Question schemas
class SuggestedQuestionBase(BaseModel):
    question: str
    description: Optional[str] = None
    icon: Optional[str] = None
    connection_id: str
    query_config: Dict[str, Any]
    chart_type: str = "bar"
    category: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class SuggestedQuestionCreate(SuggestedQuestionBase):
    pass


class SuggestedQuestion(SuggestedQuestionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Transform Recipe Summary for home page
class TransformRecipeSummary(BaseModel):
    """Summary of a transform recipe for home page."""
    id: UUID
    name: str
    description: Optional[str] = None
    connection_id: UUID
    source_table: str
    source_schema: str
    steps_count: int = 0
    row_count: Optional[int] = None
    last_executed: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Home page response
class HomePageData(BaseModel):
    """Data for the home page dashboard grid."""
    featured_dashboards: List[DashboardSummary] = []
    recent_charts: List[SavedChart] = []
    favorite_charts: List[SavedChart] = []
    suggested_questions: List[SuggestedQuestion] = []
    recent_transforms: List[TransformRecipeSummary] = []
