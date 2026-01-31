"""
Report Templates Schemas

Pydantic schemas for report template management including
layouts, placeholders, styles, and template versioning.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
from datetime import datetime


# Enums

class TemplateType(str, Enum):
    DASHBOARD = "dashboard"
    CHART = "chart"
    DATA_TABLE = "data_table"
    KPI = "kpi"
    MIXED = "mixed"
    CUSTOM = "custom"


class TemplateStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class PlaceholderType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    CHART = "chart"
    TABLE = "table"
    KPI = "kpi"
    DATE = "date"
    PAGE_NUMBER = "page_number"
    FILTER = "filter"
    LOGO = "logo"
    CUSTOM = "custom"


class LayoutType(str, Enum):
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "two_column"
    THREE_COLUMN = "three_column"
    GRID = "grid"
    FREEFORM = "freeform"
    MASTER_DETAIL = "master_detail"


class PageBreakBehavior(str, Enum):
    AUTO = "auto"
    BEFORE = "before"
    AFTER = "after"
    AVOID = "avoid"


# Style Schemas

class FontStyle(BaseModel):
    family: str = "Arial"
    size: int = 12
    weight: str = "normal"
    style: str = "normal"
    color: str = "#000000"
    line_height: float = 1.5


class BorderStyle(BaseModel):
    width: int = 1
    style: str = "solid"
    color: str = "#cccccc"
    radius: int = 0


class SpacingStyle(BaseModel):
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0


class BackgroundStyle(BaseModel):
    color: Optional[str] = None
    image_url: Optional[str] = None
    repeat: str = "no-repeat"
    position: str = "center"
    size: str = "cover"


class ElementStyle(BaseModel):
    font: Optional[FontStyle] = None
    border: Optional[BorderStyle] = None
    padding: Optional[SpacingStyle] = None
    margin: Optional[SpacingStyle] = None
    background: Optional[BackgroundStyle] = None
    width: Optional[str] = None
    height: Optional[str] = None
    min_width: Optional[str] = None
    min_height: Optional[str] = None
    max_width: Optional[str] = None
    max_height: Optional[str] = None
    alignment: str = "left"
    vertical_alignment: str = "top"


# Placeholder Schemas

class PlaceholderPosition(BaseModel):
    x: float = 0
    y: float = 0
    width: float = 100
    height: float = 100
    z_index: int = 0
    rotation: float = 0


class PlaceholderConfig(BaseModel):
    placeholder_type: PlaceholderType
    source_id: Optional[str] = None
    default_value: Optional[str] = None
    format_string: Optional[str] = None
    filters: Optional[dict[str, Any]] = None
    parameters: Optional[dict[str, Any]] = None


class TemplatePlaceholder(BaseModel):
    id: str
    name: str
    placeholder_type: PlaceholderType
    position: PlaceholderPosition
    config: PlaceholderConfig
    style: Optional[ElementStyle] = None
    required: bool = False
    editable: bool = True
    page_break: PageBreakBehavior = PageBreakBehavior.AUTO


# Section Schemas

class TemplateSection(BaseModel):
    id: str
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    layout: LayoutType = LayoutType.SINGLE_COLUMN
    placeholders: list[TemplatePlaceholder] = []
    style: Optional[ElementStyle] = None
    page_break: PageBreakBehavior = PageBreakBehavior.AUTO
    repeat_for_data: bool = False
    data_source: Optional[str] = None
    visible: bool = True
    order: int = 0


# Page Schemas

class PageMargins(BaseModel):
    top: float = 20
    right: float = 20
    bottom: float = 20
    left: float = 20


class PageConfig(BaseModel):
    size: str = "A4"
    orientation: str = "portrait"
    margins: PageMargins = Field(default_factory=PageMargins)
    background: Optional[BackgroundStyle] = None


class TemplatePage(BaseModel):
    id: str
    name: str
    page_number: int
    config: PageConfig = Field(default_factory=PageConfig)
    header: Optional[TemplateSection] = None
    footer: Optional[TemplateSection] = None
    sections: list[TemplateSection] = []


# Theme Schemas

class TemplateColorPalette(BaseModel):
    primary: str = "#3B82F6"
    secondary: str = "#6B7280"
    accent: str = "#10B981"
    background: str = "#FFFFFF"
    surface: str = "#F9FAFB"
    text_primary: str = "#111827"
    text_secondary: str = "#6B7280"
    border: str = "#E5E7EB"
    success: str = "#10B981"
    warning: str = "#F59E0B"
    error: str = "#EF4444"
    info: str = "#3B82F6"


class TemplateTypography(BaseModel):
    title: FontStyle = Field(default_factory=lambda: FontStyle(size=24, weight="bold"))
    subtitle: FontStyle = Field(default_factory=lambda: FontStyle(size=18, weight="semibold"))
    heading: FontStyle = Field(default_factory=lambda: FontStyle(size=16, weight="semibold"))
    body: FontStyle = Field(default_factory=lambda: FontStyle(size=12))
    caption: FontStyle = Field(default_factory=lambda: FontStyle(size=10, color="#6B7280"))
    label: FontStyle = Field(default_factory=lambda: FontStyle(size=11, weight="medium"))


class TemplateTheme(BaseModel):
    name: str = "default"
    colors: TemplateColorPalette = Field(default_factory=TemplateColorPalette)
    typography: TemplateTypography = Field(default_factory=TemplateTypography)
    chart_colors: list[str] = Field(default_factory=lambda: [
        "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
        "#EC4899", "#06B6D4", "#84CC16", "#F97316", "#6366F1"
    ])
    border_radius: int = 4
    shadow: str = "0 1px 3px rgba(0,0,0,0.1)"


# Template Schemas

class ReportTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: TemplateType
    category: Optional[str] = None
    tags: list[str] = []


class ReportTemplateCreate(ReportTemplateBase):
    pages: list[TemplatePage] = []
    theme: Optional[TemplateTheme] = None
    default_filters: Optional[dict[str, Any]] = None
    default_parameters: Optional[dict[str, Any]] = None
    is_public: bool = False


class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    pages: Optional[list[TemplatePage]] = None
    theme: Optional[TemplateTheme] = None
    default_filters: Optional[dict[str, Any]] = None
    default_parameters: Optional[dict[str, Any]] = None
    status: Optional[TemplateStatus] = None
    is_public: Optional[bool] = None


class ReportTemplate(ReportTemplateBase):
    id: str
    user_id: str
    organization_id: Optional[str] = None
    status: TemplateStatus = TemplateStatus.DRAFT
    version: int = 1
    pages: list[TemplatePage] = []
    theme: TemplateTheme = Field(default_factory=TemplateTheme)
    default_filters: dict[str, Any] = {}
    default_parameters: dict[str, Any] = {}
    is_public: bool = False
    is_system: bool = False
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportTemplateListResponse(BaseModel):
    templates: list[ReportTemplate]
    total: int


# Template Version Schemas

class TemplateVersion(BaseModel):
    id: str
    template_id: str
    version: int
    name: str
    description: Optional[str] = None
    pages: list[TemplatePage]
    theme: TemplateTheme
    change_summary: Optional[str] = None
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateVersionListResponse(BaseModel):
    versions: list[TemplateVersion]
    total: int


# Template Category Schemas

class TemplateCategory(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[str] = None
    order: int = 0
    template_count: int = 0

    class Config:
        from_attributes = True


class TemplateCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[str] = None
    order: int = 0


class TemplateCategoryListResponse(BaseModel):
    categories: list[TemplateCategory]
    total: int


# Template Instance Schemas (for generated reports)

class TemplateInstance(BaseModel):
    id: str
    template_id: str
    template_version: int
    name: str
    user_id: str
    organization_id: Optional[str] = None
    placeholder_values: dict[str, Any] = {}
    filters: dict[str, Any] = {}
    parameters: dict[str, Any] = {}
    generated_at: Optional[datetime] = None
    file_url: Optional[str] = None
    file_format: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateInstanceCreate(BaseModel):
    template_id: str
    name: str
    placeholder_values: dict[str, Any] = {}
    filters: dict[str, Any] = {}
    parameters: dict[str, Any] = {}


class TemplateInstanceListResponse(BaseModel):
    instances: list[TemplateInstance]
    total: int


# Constants

TEMPLATE_TYPE_LABELS: dict[TemplateType, str] = {
    TemplateType.DASHBOARD: "Dashboard Report",
    TemplateType.CHART: "Chart Report",
    TemplateType.DATA_TABLE: "Data Table Report",
    TemplateType.KPI: "KPI Report",
    TemplateType.MIXED: "Mixed Report",
    TemplateType.CUSTOM: "Custom Report",
}

TEMPLATE_STATUS_LABELS: dict[TemplateStatus, str] = {
    TemplateStatus.DRAFT: "Draft",
    TemplateStatus.PUBLISHED: "Published",
    TemplateStatus.ARCHIVED: "Archived",
    TemplateStatus.DEPRECATED: "Deprecated",
}

PLACEHOLDER_TYPE_LABELS: dict[PlaceholderType, str] = {
    PlaceholderType.TEXT: "Text",
    PlaceholderType.IMAGE: "Image",
    PlaceholderType.CHART: "Chart",
    PlaceholderType.TABLE: "Data Table",
    PlaceholderType.KPI: "KPI Card",
    PlaceholderType.DATE: "Date",
    PlaceholderType.PAGE_NUMBER: "Page Number",
    PlaceholderType.FILTER: "Filter Value",
    PlaceholderType.LOGO: "Logo",
    PlaceholderType.CUSTOM: "Custom",
}

LAYOUT_TYPE_LABELS: dict[LayoutType, str] = {
    LayoutType.SINGLE_COLUMN: "Single Column",
    LayoutType.TWO_COLUMN: "Two Columns",
    LayoutType.THREE_COLUMN: "Three Columns",
    LayoutType.GRID: "Grid",
    LayoutType.FREEFORM: "Freeform",
    LayoutType.MASTER_DETAIL: "Master-Detail",
}


# Helper Functions

def get_default_theme() -> TemplateTheme:
    """Get default template theme."""
    return TemplateTheme()


def get_default_page() -> TemplatePage:
    """Get default template page."""
    return TemplatePage(
        id="page-1",
        name="Page 1",
        page_number=1,
    )


def create_text_placeholder(
    id: str,
    name: str,
    x: float = 0,
    y: float = 0,
    width: float = 100,
    height: float = 30,
    default_value: str = "",
) -> TemplatePlaceholder:
    """Create a text placeholder."""
    return TemplatePlaceholder(
        id=id,
        name=name,
        placeholder_type=PlaceholderType.TEXT,
        position=PlaceholderPosition(x=x, y=y, width=width, height=height),
        config=PlaceholderConfig(
            placeholder_type=PlaceholderType.TEXT,
            default_value=default_value,
        ),
    )


def create_chart_placeholder(
    id: str,
    name: str,
    chart_id: str,
    x: float = 0,
    y: float = 0,
    width: float = 400,
    height: float = 300,
) -> TemplatePlaceholder:
    """Create a chart placeholder."""
    return TemplatePlaceholder(
        id=id,
        name=name,
        placeholder_type=PlaceholderType.CHART,
        position=PlaceholderPosition(x=x, y=y, width=width, height=height),
        config=PlaceholderConfig(
            placeholder_type=PlaceholderType.CHART,
            source_id=chart_id,
        ),
    )


def create_table_placeholder(
    id: str,
    name: str,
    data_source: str,
    x: float = 0,
    y: float = 0,
    width: float = 500,
    height: float = 400,
) -> TemplatePlaceholder:
    """Create a table placeholder."""
    return TemplatePlaceholder(
        id=id,
        name=name,
        placeholder_type=PlaceholderType.TABLE,
        position=PlaceholderPosition(x=x, y=y, width=width, height=height),
        config=PlaceholderConfig(
            placeholder_type=PlaceholderType.TABLE,
            source_id=data_source,
        ),
    )
