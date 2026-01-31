"""
Report Builder Schemas

Pydantic schemas for report generation and export.
"""

from typing import Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class ReportFormat(str, Enum):
    """Report export formats"""
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"
    POWERPOINT = "pptx"
    IMAGE = "image"


class PageSize(str, Enum):
    """Page sizes for PDF"""
    A4 = "a4"
    LETTER = "letter"
    LEGAL = "legal"
    A3 = "a3"
    TABLOID = "tabloid"


class PageOrientation(str, Enum):
    """Page orientation"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class ElementType(str, Enum):
    """Report element types"""
    CHART = "chart"
    TABLE = "table"
    TEXT = "text"
    IMAGE = "image"
    KPI = "kpi"
    HEADING = "heading"
    DIVIDER = "divider"
    SPACER = "spacer"
    PAGE_BREAK = "page_break"
    TOC = "table_of_contents"


class TextAlignment(str, Enum):
    """Text alignment"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


# Branding Configuration

class BrandingConfig(BaseModel):
    """Report branding configuration"""
    logo_url: Optional[str] = None
    logo_width: int = 150
    logo_position: str = "left"  # left, center, right
    primary_color: str = "#1f2937"
    secondary_color: str = "#3b82f6"
    accent_color: str = "#10b981"
    font_family: str = "Inter, sans-serif"
    header_font_family: Optional[str] = None
    company_name: Optional[str] = None
    footer_text: Optional[str] = None


# Page Configuration

class PageMargins(BaseModel):
    """Page margins in mm"""
    top: int = 20
    bottom: int = 20
    left: int = 15
    right: int = 15


class HeaderFooterConfig(BaseModel):
    """Header/footer configuration"""
    show_header: bool = True
    show_footer: bool = True
    header_height: int = 30
    footer_height: int = 20
    include_logo: bool = True
    include_title: bool = True
    include_date: bool = True
    include_page_numbers: bool = True
    custom_header_html: Optional[str] = None
    custom_footer_html: Optional[str] = None


class PageConfig(BaseModel):
    """Page configuration"""
    size: PageSize = PageSize.A4
    orientation: PageOrientation = PageOrientation.PORTRAIT
    margins: PageMargins = Field(default_factory=PageMargins)
    header_footer: HeaderFooterConfig = Field(default_factory=HeaderFooterConfig)


# Report Elements

class TextStyle(BaseModel):
    """Text styling"""
    font_size: int = 12
    font_weight: str = "normal"  # normal, bold
    font_style: str = "normal"  # normal, italic
    color: str = "#1f2937"
    alignment: TextAlignment = TextAlignment.LEFT
    line_height: float = 1.5


class ChartElement(BaseModel):
    """Chart element configuration"""
    element_type: str = "chart"
    chart_id: str
    title: Optional[str] = None
    show_title: bool = True
    width: str = "100%"
    height: int = 400
    filters: Optional[dict[str, Any]] = None


class TableElement(BaseModel):
    """Table element configuration"""
    element_type: str = "table"
    data_source: str  # query_id, dataset_id, or inline data
    query: Optional[str] = None
    columns: Optional[list[str]] = None
    title: Optional[str] = None
    show_title: bool = True
    max_rows: int = 100
    show_row_numbers: bool = False
    striped: bool = True
    bordered: bool = True
    compact: bool = False


class TextElement(BaseModel):
    """Text element configuration"""
    element_type: str = "text"
    content: str
    style: TextStyle = Field(default_factory=TextStyle)
    markdown: bool = False


class HeadingElement(BaseModel):
    """Heading element configuration"""
    element_type: str = "heading"
    text: str
    level: int = 1  # 1-6
    style: Optional[TextStyle] = None
    include_in_toc: bool = True


class ImageElement(BaseModel):
    """Image element configuration"""
    element_type: str = "image"
    url: str
    alt_text: str = ""
    width: Optional[str] = None
    height: Optional[str] = None
    alignment: TextAlignment = TextAlignment.CENTER


class KPIElement(BaseModel):
    """KPI card element"""
    element_type: str = "kpi"
    kpi_id: Optional[str] = None
    label: str
    value: Optional[Union[str, float]] = None
    query: Optional[str] = None  # Query to fetch value
    format: Optional[str] = None
    comparison_value: Optional[float] = None
    comparison_label: Optional[str] = None
    trend_direction: Optional[str] = None  # up, down, neutral
    color: Optional[str] = None


class DividerElement(BaseModel):
    """Divider element"""
    element_type: str = "divider"
    style: str = "solid"  # solid, dashed, dotted
    color: str = "#e5e7eb"
    thickness: int = 1
    margin_top: int = 10
    margin_bottom: int = 10


class SpacerElement(BaseModel):
    """Spacer element"""
    element_type: str = "spacer"
    height: int = 20


class PageBreakElement(BaseModel):
    """Page break element"""
    element_type: str = "page_break"


class TOCElement(BaseModel):
    """Table of contents element"""
    element_type: str = "table_of_contents"
    title: str = "Table of Contents"
    max_depth: int = 3
    show_page_numbers: bool = True


ReportElement = Union[
    ChartElement,
    TableElement,
    TextElement,
    HeadingElement,
    ImageElement,
    KPIElement,
    DividerElement,
    SpacerElement,
    PageBreakElement,
    TOCElement,
]


# Report Section

class ReportSection(BaseModel):
    """Report section"""
    id: str
    title: Optional[str] = None
    elements: list[ReportElement]
    columns: int = 1  # 1, 2, or 3 column layout
    background_color: Optional[str] = None
    padding: int = 10


# Report Template

class ReportTemplateBase(BaseModel):
    """Base report template schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ReportTemplateCreate(ReportTemplateBase):
    """Schema for creating a report template"""
    page_config: PageConfig = Field(default_factory=PageConfig)
    branding: BrandingConfig = Field(default_factory=BrandingConfig)
    sections: list[ReportSection]
    workspace_id: Optional[str] = None
    is_public: bool = False
    tags: list[str] = Field(default_factory=list)


class ReportTemplateUpdate(BaseModel):
    """Schema for updating a report template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    page_config: Optional[PageConfig] = None
    branding: Optional[BrandingConfig] = None
    sections: Optional[list[ReportSection]] = None
    is_public: Optional[bool] = None
    tags: Optional[list[str]] = None


class ReportTemplateResponse(ReportTemplateBase):
    """Schema for report template response"""
    id: str
    page_config: PageConfig
    branding: BrandingConfig
    sections: list[ReportSection]
    workspace_id: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_public: bool
    usage_count: int = 0
    tags: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Report Generation

class ReportGenerateRequest(BaseModel):
    """Request to generate a report"""
    template_id: Optional[str] = None
    dashboard_id: Optional[str] = None  # Generate from dashboard
    title: str = "Report"
    subtitle: Optional[str] = None
    format: ReportFormat = ReportFormat.PDF
    page_config: Optional[PageConfig] = None
    branding: Optional[BrandingConfig] = None
    sections: Optional[list[ReportSection]] = None
    filters: Optional[dict[str, Any]] = None  # Apply filters to data
    parameters: Optional[dict[str, Any]] = None  # Template parameters
    include_cover_page: bool = True
    include_toc: bool = False
    generated_date: Optional[datetime] = None


class ReportGenerateResponse(BaseModel):
    """Response for report generation"""
    job_id: str
    status: str  # pending, processing, completed, failed
    format: ReportFormat
    message: Optional[str] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class ReportJob(BaseModel):
    """Report generation job"""
    id: str
    template_id: Optional[str] = None
    dashboard_id: Optional[str] = None
    title: str
    format: ReportFormat
    status: str
    progress: int = 0
    created_by: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    expires_at: Optional[datetime] = None


# Scheduled Reports

class ScheduledReportConfig(BaseModel):
    """Scheduled report configuration"""
    template_id: str
    title: str
    format: ReportFormat = ReportFormat.PDF
    filters: Optional[dict[str, Any]] = None
    parameters: Optional[dict[str, Any]] = None


class ScheduledReport(BaseModel):
    """Scheduled report"""
    id: str
    name: str
    config: ScheduledReportConfig
    schedule: str  # Cron expression
    recipients: list[str]
    enabled: bool = True
    workspace_id: Optional[str] = None
    created_by: str
    created_at: datetime
    last_generated_at: Optional[datetime] = None
    next_generation_at: Optional[datetime] = None


# Export Options

class PDFExportOptions(BaseModel):
    """PDF-specific export options"""
    page_size: PageSize = PageSize.A4
    orientation: PageOrientation = PageOrientation.PORTRAIT
    margins: PageMargins = Field(default_factory=PageMargins)
    print_background: bool = True
    display_header_footer: bool = True
    scale: float = 1.0


class ExcelExportOptions(BaseModel):
    """Excel-specific export options"""
    include_charts_as_images: bool = True
    include_formulas: bool = False
    freeze_headers: bool = True
    auto_filter: bool = True
    sheet_per_section: bool = False


class ImageExportOptions(BaseModel):
    """Image export options"""
    format: str = "png"  # png, jpeg, webp
    width: int = 1200
    height: Optional[int] = None  # Auto-calculate
    scale: float = 2.0  # For retina
    quality: int = 90  # For jpeg


# Dashboard Export

class DashboardExportRequest(BaseModel):
    """Request to export a dashboard"""
    dashboard_id: str
    format: ReportFormat = ReportFormat.PDF
    title: Optional[str] = None
    include_filters: bool = True
    filter_state: Optional[dict[str, Any]] = None
    pdf_options: Optional[PDFExportOptions] = None
    excel_options: Optional[ExcelExportOptions] = None
    image_options: Optional[ImageExportOptions] = None


class ChartExportRequest(BaseModel):
    """Request to export a single chart"""
    chart_id: str
    format: str = "png"  # png, jpeg, svg, pdf
    width: int = 800
    height: int = 600
    scale: float = 2.0
    include_title: bool = True
    include_legend: bool = True
    background_color: str = "white"


# Template Library

class TemplateCategory(BaseModel):
    """Template category"""
    id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    template_count: int = 0


class TemplatePreview(BaseModel):
    """Template preview info"""
    id: str
    name: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    usage_count: int = 0
    is_public: bool = False


# Constants

BUILT_IN_TEMPLATES = [
    {
        "id": "executive-summary",
        "name": "Executive Summary",
        "description": "High-level overview with KPIs and key charts",
        "category": "business",
        "tags": ["executive", "summary", "kpi"],
    },
    {
        "id": "financial-report",
        "name": "Financial Report",
        "description": "Detailed financial analysis with tables and trends",
        "category": "finance",
        "tags": ["finance", "accounting", "budget"],
    },
    {
        "id": "sales-performance",
        "name": "Sales Performance",
        "description": "Sales metrics, pipeline, and team performance",
        "category": "sales",
        "tags": ["sales", "revenue", "pipeline"],
    },
    {
        "id": "marketing-analytics",
        "name": "Marketing Analytics",
        "description": "Campaign performance and marketing metrics",
        "category": "marketing",
        "tags": ["marketing", "campaigns", "roi"],
    },
    {
        "id": "operational-dashboard",
        "name": "Operational Dashboard",
        "description": "Real-time operational metrics and KPIs",
        "category": "operations",
        "tags": ["operations", "metrics", "monitoring"],
    },
]

FORMAT_EXTENSIONS = {
    ReportFormat.PDF: ".pdf",
    ReportFormat.HTML: ".html",
    ReportFormat.EXCEL: ".xlsx",
    ReportFormat.POWERPOINT: ".pptx",
    ReportFormat.IMAGE: ".png",
}

FORMAT_MIME_TYPES = {
    ReportFormat.PDF: "application/pdf",
    ReportFormat.HTML: "text/html",
    ReportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ReportFormat.POWERPOINT: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ReportFormat.IMAGE: "image/png",
}
