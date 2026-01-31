"""
Export & Document Generation Schemas

Pydantic schemas for PDF, Excel, PowerPoint, and image exports,
including export jobs, formats, and configurations.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class ExportFormat(str, Enum):
    """Export file formats"""
    PDF = "pdf"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    PNG = "png"
    SVG = "svg"
    JPEG = "jpeg"
    CSV = "csv"
    JSON = "json"


class ExportStatus(str, Enum):
    """Export job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ExportType(str, Enum):
    """Type of content being exported"""
    DASHBOARD = "dashboard"
    CHART = "chart"
    REPORT = "report"
    QUERY_RESULT = "query_result"
    DATA_TABLE = "data_table"


class PageSize(str, Enum):
    """PDF page sizes"""
    A4 = "a4"
    A3 = "a3"
    LETTER = "letter"
    LEGAL = "legal"
    TABLOID = "tabloid"
    CUSTOM = "custom"


class PageOrientation(str, Enum):
    """Page orientation"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class ImageQuality(str, Enum):
    """Image export quality"""
    LOW = "low"  # 72 DPI
    MEDIUM = "medium"  # 150 DPI
    HIGH = "high"  # 300 DPI
    PRINT = "print"  # 600 DPI


class ExcelSheetType(str, Enum):
    """Excel sheet content type"""
    DATA = "data"
    CHART = "chart"
    SUMMARY = "summary"
    PIVOT = "pivot"


# PDF Export Models

class PDFMargins(BaseModel):
    """PDF page margins in millimeters"""
    top: float = 20
    bottom: float = 20
    left: float = 20
    right: float = 20


class PDFHeader(BaseModel):
    """PDF header configuration"""
    enabled: bool = True
    text: Optional[str] = None
    logo_url: Optional[str] = None
    include_date: bool = True
    include_page_number: bool = False
    height: float = 15  # mm


class PDFFooter(BaseModel):
    """PDF footer configuration"""
    enabled: bool = True
    text: Optional[str] = None
    include_date: bool = False
    include_page_number: bool = True
    include_total_pages: bool = True
    height: float = 10  # mm


class PDFWatermark(BaseModel):
    """PDF watermark configuration"""
    enabled: bool = False
    text: Optional[str] = None
    image_url: Optional[str] = None
    opacity: float = 0.1
    rotation: float = -45
    position: str = "center"  # center, tile


class PDFExportConfig(BaseModel):
    """PDF export configuration"""
    page_size: PageSize = PageSize.A4
    orientation: PageOrientation = PageOrientation.LANDSCAPE
    custom_width: Optional[float] = None  # mm, for CUSTOM size
    custom_height: Optional[float] = None  # mm, for CUSTOM size
    margins: PDFMargins = Field(default_factory=PDFMargins)
    header: PDFHeader = Field(default_factory=PDFHeader)
    footer: PDFFooter = Field(default_factory=PDFFooter)
    watermark: PDFWatermark = Field(default_factory=PDFWatermark)
    include_toc: bool = False  # Table of contents
    include_filters: bool = True  # Show active filters
    include_timestamp: bool = True
    scale: float = 1.0
    print_background: bool = True
    compress: bool = True
    password: Optional[str] = None  # PDF password protection


# Excel Export Models

class ExcelColumnFormat(BaseModel):
    """Excel column formatting"""
    column: str
    width: Optional[float] = None
    number_format: Optional[str] = None  # e.g., "#,##0.00", "0%"
    alignment: str = "left"  # left, center, right
    wrap_text: bool = False
    bold: bool = False
    font_color: Optional[str] = None
    bg_color: Optional[str] = None


class ExcelConditionalFormat(BaseModel):
    """Excel conditional formatting rule"""
    column: str
    rule_type: str  # "greater_than", "less_than", "between", "text_contains", "duplicate"
    value: Any
    value2: Optional[Any] = None  # For "between" rule
    format: dict[str, Any] = Field(default_factory=dict)  # bg_color, font_color, bold, etc.


class ExcelChartConfig(BaseModel):
    """Excel embedded chart configuration"""
    chart_type: str  # bar, line, pie, column, area
    data_range: str
    title: Optional[str] = None
    position: str  # Cell reference like "F1"
    width: int = 500
    height: int = 300


class ExcelSheetConfig(BaseModel):
    """Excel sheet configuration"""
    name: str
    sheet_type: ExcelSheetType = ExcelSheetType.DATA
    data_source: Optional[str] = None  # Query ID, dataset ID, etc.
    include_headers: bool = True
    freeze_panes: Optional[str] = None  # Cell reference like "A2"
    auto_filter: bool = True
    column_formats: list[ExcelColumnFormat] = Field(default_factory=list)
    conditional_formats: list[ExcelConditionalFormat] = Field(default_factory=list)
    charts: list[ExcelChartConfig] = Field(default_factory=list)
    hidden: bool = False


class ExcelExportConfig(BaseModel):
    """Excel export configuration"""
    sheets: list[ExcelSheetConfig] = Field(default_factory=list)
    include_metadata_sheet: bool = False
    include_summary_sheet: bool = False
    default_column_width: float = 15
    date_format: str = "YYYY-MM-DD"
    datetime_format: str = "YYYY-MM-DD HH:mm:ss"
    number_format: str = "#,##0.00"
    currency_format: str = "$#,##0.00"
    percentage_format: str = "0.00%"
    password: Optional[str] = None
    protect_structure: bool = False


# PowerPoint Export Models

class SlideLayout(str, Enum):
    """PowerPoint slide layouts"""
    TITLE = "title"
    TITLE_CONTENT = "title_content"
    TWO_COLUMN = "two_column"
    COMPARISON = "comparison"
    BLANK = "blank"
    SECTION_HEADER = "section_header"


class SlideContent(BaseModel):
    """PowerPoint slide content"""
    type: str  # "chart", "table", "text", "image", "shape"
    source_id: Optional[str] = None  # Chart ID, image URL, etc.
    content: Optional[str] = None  # Text content
    position: dict[str, float] = Field(default_factory=dict)  # x, y, width, height (inches)
    style: dict[str, Any] = Field(default_factory=dict)


class SlideConfig(BaseModel):
    """PowerPoint slide configuration"""
    layout: SlideLayout = SlideLayout.TITLE_CONTENT
    title: Optional[str] = None
    subtitle: Optional[str] = None
    notes: Optional[str] = None
    contents: list[SlideContent] = Field(default_factory=list)
    background_color: Optional[str] = None
    background_image: Optional[str] = None
    transition: Optional[str] = None


class PowerPointTheme(BaseModel):
    """PowerPoint theme configuration"""
    primary_color: str = "#4F46E5"
    secondary_color: str = "#7C3AED"
    background_color: str = "#FFFFFF"
    text_color: str = "#1F2937"
    font_family: str = "Arial"
    title_font_size: int = 36
    body_font_size: int = 18


class PowerPointExportConfig(BaseModel):
    """PowerPoint export configuration"""
    slides: list[SlideConfig] = Field(default_factory=list)
    theme: PowerPointTheme = Field(default_factory=PowerPointTheme)
    include_title_slide: bool = True
    title: Optional[str] = None
    subtitle: Optional[str] = None
    author: Optional[str] = None
    include_notes: bool = True
    slide_width: float = 13.333  # inches (16:9)
    slide_height: float = 7.5  # inches (16:9)


# Image Export Models

class ImageExportConfig(BaseModel):
    """Image export configuration"""
    format: ExportFormat = ExportFormat.PNG
    quality: ImageQuality = ImageQuality.HIGH
    width: Optional[int] = None  # pixels, None = auto
    height: Optional[int] = None  # pixels, None = auto
    scale: float = 2.0  # For retina displays
    background_color: Optional[str] = "#FFFFFF"
    transparent_background: bool = False
    include_title: bool = True
    include_legend: bool = True
    padding: int = 20  # pixels


# CSV/JSON Export Models

class CSVExportConfig(BaseModel):
    """CSV export configuration"""
    delimiter: str = ","
    quote_char: str = '"'
    include_headers: bool = True
    encoding: str = "utf-8"
    line_terminator: str = "\n"
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    null_value: str = ""
    escape_char: Optional[str] = None


class JSONExportConfig(BaseModel):
    """JSON export configuration"""
    pretty_print: bool = True
    indent: int = 2
    date_format: str = "iso"  # iso, timestamp, custom
    include_metadata: bool = True
    array_format: bool = True  # True = array of objects, False = object with arrays


# Export Job Models

class ExportRequest(BaseModel):
    """Request to create an export"""
    export_type: ExportType
    format: ExportFormat
    source_id: str  # Dashboard ID, chart ID, query ID, etc.
    filename: Optional[str] = None
    pdf_config: Optional[PDFExportConfig] = None
    excel_config: Optional[ExcelExportConfig] = None
    powerpoint_config: Optional[PowerPointExportConfig] = None
    image_config: Optional[ImageExportConfig] = None
    csv_config: Optional[CSVExportConfig] = None
    json_config: Optional[JSONExportConfig] = None
    filters: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    notify_on_completion: bool = False
    notification_email: Optional[str] = None


class ExportJob(BaseModel):
    """Export job"""
    id: str
    user_id: str
    organization_id: Optional[str] = None
    export_type: ExportType
    format: ExportFormat
    source_id: str
    source_name: Optional[str] = None
    filename: str
    status: ExportStatus
    progress: int = 0  # 0-100
    file_size: Optional[int] = None  # bytes
    file_url: Optional[str] = None
    download_count: int = 0
    error_message: Optional[str] = None
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExportJobUpdate(BaseModel):
    """Update export job"""
    status: Optional[ExportStatus] = None
    progress: Optional[int] = None
    file_size: Optional[int] = None
    file_url: Optional[str] = None
    error_message: Optional[str] = None


class ExportJobListResponse(BaseModel):
    """List export jobs response"""
    jobs: list[ExportJob]
    total: int


# Export Preset Models

class ExportPreset(BaseModel):
    """Saved export configuration preset"""
    id: str
    name: str
    description: Optional[str] = None
    export_type: ExportType
    format: ExportFormat
    config: dict[str, Any]  # Format-specific config
    user_id: str
    organization_id: Optional[str] = None
    is_default: bool = False
    is_shared: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ExportPresetCreate(BaseModel):
    """Create export preset"""
    name: str
    description: Optional[str] = None
    export_type: ExportType
    format: ExportFormat
    config: dict[str, Any]
    is_default: bool = False
    is_shared: bool = False


class ExportPresetListResponse(BaseModel):
    """List export presets response"""
    presets: list[ExportPreset]
    total: int


# Export History Models

class ExportHistoryEntry(BaseModel):
    """Export history entry"""
    id: str
    job_id: str
    user_id: str
    export_type: ExportType
    format: ExportFormat
    source_id: str
    source_name: Optional[str] = None
    filename: str
    file_size: Optional[int] = None
    status: ExportStatus
    duration_seconds: Optional[float] = None
    downloaded: bool = False
    downloaded_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExportHistoryListResponse(BaseModel):
    """List export history response"""
    entries: list[ExportHistoryEntry]
    total: int


# Export Statistics Models

class ExportStats(BaseModel):
    """Export statistics"""
    organization_id: str
    total_exports: int
    exports_today: int
    exports_this_week: int
    exports_this_month: int
    exports_by_format: dict[str, int]
    exports_by_type: dict[str, int]
    total_file_size_bytes: int
    average_duration_seconds: float
    success_rate: float


# Constants

EXPORT_FILE_EXTENSIONS = {
    ExportFormat.PDF: ".pdf",
    ExportFormat.EXCEL: ".xlsx",
    ExportFormat.POWERPOINT: ".pptx",
    ExportFormat.PNG: ".png",
    ExportFormat.SVG: ".svg",
    ExportFormat.JPEG: ".jpg",
    ExportFormat.CSV: ".csv",
    ExportFormat.JSON: ".json",
}

EXPORT_MIME_TYPES = {
    ExportFormat.PDF: "application/pdf",
    ExportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ExportFormat.POWERPOINT: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ExportFormat.PNG: "image/png",
    ExportFormat.SVG: "image/svg+xml",
    ExportFormat.JPEG: "image/jpeg",
    ExportFormat.CSV: "text/csv",
    ExportFormat.JSON: "application/json",
}

DEFAULT_EXPORT_EXPIRY_HOURS = 24
MAX_EXPORT_FILE_SIZE_MB = 100
EXPORT_RETENTION_DAYS = 30


# Helper Functions

def get_file_extension(format: ExportFormat) -> str:
    """Get file extension for export format."""
    return EXPORT_FILE_EXTENSIONS.get(format, ".bin")


def get_mime_type(format: ExportFormat) -> str:
    """Get MIME type for export format."""
    return EXPORT_MIME_TYPES.get(format, "application/octet-stream")


def generate_export_filename(
    source_name: str,
    format: ExportFormat,
    timestamp: bool = True,
) -> str:
    """Generate export filename."""
    import re
    from datetime import datetime

    # Sanitize source name
    safe_name = re.sub(r'[^\w\s-]', '', source_name).strip()
    safe_name = re.sub(r'[-\s]+', '_', safe_name)

    if timestamp:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{safe_name}_{ts}{get_file_extension(format)}"

    return f"{safe_name}{get_file_extension(format)}"


def calculate_dpi(quality: ImageQuality) -> int:
    """Calculate DPI from quality setting."""
    dpi_map = {
        ImageQuality.LOW: 72,
        ImageQuality.MEDIUM: 150,
        ImageQuality.HIGH: 300,
        ImageQuality.PRINT: 600,
    }
    return dpi_map.get(quality, 150)


def format_file_size(size_bytes: int) -> str:
    """Format file size for display."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
