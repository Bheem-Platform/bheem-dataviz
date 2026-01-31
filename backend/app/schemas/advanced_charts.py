"""
Advanced Charts Schemas

Pydantic schemas for advanced visualization types.
"""

from typing import Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class AdvancedChartType(str, Enum):
    """Advanced chart types"""
    WATERFALL = "waterfall"
    FUNNEL = "funnel"
    GANTT = "gantt"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    RADAR = "radar"
    BULLET = "bullet"
    HEATMAP = "heatmap"
    BOXPLOT = "boxplot"
    CANDLESTICK = "candlestick"
    GAUGE = "gauge"
    SUNBURST = "sunburst"
    PARALLEL = "parallel"
    WORDCLOUD = "wordcloud"


class WaterfallBarType(str, Enum):
    """Waterfall bar types"""
    INCREASE = "increase"
    DECREASE = "decrease"
    TOTAL = "total"
    SUBTOTAL = "subtotal"


class FunnelOrientation(str, Enum):
    """Funnel chart orientation"""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class GanttTimeUnit(str, Enum):
    """Gantt chart time units"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


# Base Configuration

class ChartColorConfig(BaseModel):
    """Color configuration for charts"""
    primary: str = "#3b82f6"
    secondary: str = "#10b981"
    increase: str = "#22c55e"
    decrease: str = "#ef4444"
    total: str = "#6366f1"
    neutral: str = "#94a3b8"
    palette: list[str] = Field(default_factory=lambda: [
        "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
        "#ec4899", "#06b6d4", "#84cc16", "#f97316", "#6366f1"
    ])


class ChartAxisConfig(BaseModel):
    """Axis configuration"""
    show: bool = True
    title: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    format: Optional[str] = None  # number format string
    tick_count: Optional[int] = None


class ChartLegendConfig(BaseModel):
    """Legend configuration"""
    show: bool = True
    position: str = "bottom"  # top, bottom, left, right
    orientation: str = "horizontal"  # horizontal, vertical


class ChartTooltipConfig(BaseModel):
    """Tooltip configuration"""
    show: bool = True
    format: Optional[str] = None
    include_percentage: bool = False


# Waterfall Chart

class WaterfallDataPoint(BaseModel):
    """Single waterfall data point"""
    category: str
    value: float
    bar_type: WaterfallBarType = WaterfallBarType.INCREASE
    label: Optional[str] = None
    color: Optional[str] = None


class WaterfallChartConfig(BaseModel):
    """Waterfall chart configuration"""
    chart_type: str = "waterfall"
    data: list[WaterfallDataPoint]

    # Display options
    show_connectors: bool = True
    connector_color: str = "#94a3b8"
    show_labels: bool = True
    label_position: str = "outside"  # inside, outside

    # Axis
    category_axis: ChartAxisConfig = Field(default_factory=ChartAxisConfig)
    value_axis: ChartAxisConfig = Field(default_factory=ChartAxisConfig)

    # Colors
    colors: ChartColorConfig = Field(default_factory=ChartColorConfig)

    # Legend/Tooltip
    legend: ChartLegendConfig = Field(default_factory=ChartLegendConfig)
    tooltip: ChartTooltipConfig = Field(default_factory=ChartTooltipConfig)


class WaterfallChartRequest(BaseModel):
    """Request to create waterfall chart from data"""
    connection_id: str
    query: Optional[str] = None

    # Column mappings
    category_column: str
    value_column: str
    type_column: Optional[str] = None  # Column indicating increase/decrease/total

    # Auto-calculate
    auto_total: bool = True  # Add running total
    starting_value: float = 0

    # Config
    config: Optional[WaterfallChartConfig] = None


# Funnel Chart

class FunnelStage(BaseModel):
    """Single funnel stage"""
    name: str
    value: float
    percentage: Optional[float] = None
    conversion_rate: Optional[float] = None
    color: Optional[str] = None


class FunnelChartConfig(BaseModel):
    """Funnel chart configuration"""
    chart_type: str = "funnel"
    stages: list[FunnelStage]

    # Display
    orientation: FunnelOrientation = FunnelOrientation.VERTICAL
    show_labels: bool = True
    show_percentages: bool = True
    show_conversion_rates: bool = True

    # Shape
    neck_width: float = 0.3  # 0-1, width of funnel neck
    neck_height: float = 0.25  # 0-1, height of neck section
    gap: float = 0.02  # Gap between stages

    # Colors
    colors: ChartColorConfig = Field(default_factory=ChartColorConfig)

    # Legend/Tooltip
    legend: ChartLegendConfig = Field(default_factory=ChartLegendConfig)
    tooltip: ChartTooltipConfig = Field(default_factory=ChartTooltipConfig)


class FunnelChartRequest(BaseModel):
    """Request to create funnel chart"""
    connection_id: str
    query: Optional[str] = None

    # Column mappings
    stage_column: str
    value_column: str

    # Order
    stage_order: Optional[list[str]] = None  # Custom stage ordering

    # Config
    config: Optional[FunnelChartConfig] = None


# Gantt Chart

class GanttTask(BaseModel):
    """Single Gantt task"""
    id: str
    name: str
    start: datetime
    end: datetime
    progress: float = 0  # 0-100
    parent_id: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)
    color: Optional[str] = None
    assignee: Optional[str] = None
    milestone: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class GanttChartConfig(BaseModel):
    """Gantt chart configuration"""
    chart_type: str = "gantt"
    tasks: list[GanttTask]

    # Time scale
    time_unit: GanttTimeUnit = GanttTimeUnit.DAY
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Display
    show_grid: bool = True
    show_today_line: bool = True
    show_dependencies: bool = True
    show_progress: bool = True
    row_height: int = 40

    # Grouping
    group_by: Optional[str] = None  # Column to group tasks by
    collapse_groups: bool = False

    # Colors
    colors: ChartColorConfig = Field(default_factory=ChartColorConfig)

    # Legend/Tooltip
    legend: ChartLegendConfig = Field(default_factory=ChartLegendConfig)
    tooltip: ChartTooltipConfig = Field(default_factory=ChartTooltipConfig)


class GanttChartRequest(BaseModel):
    """Request to create Gantt chart"""
    connection_id: str
    query: Optional[str] = None

    # Column mappings
    id_column: str
    name_column: str
    start_column: str
    end_column: str
    progress_column: Optional[str] = None
    parent_column: Optional[str] = None
    dependencies_column: Optional[str] = None

    # Config
    config: Optional[GanttChartConfig] = None


# Treemap

class TreemapNode(BaseModel):
    """Treemap node"""
    id: str
    name: str
    value: float
    parent_id: Optional[str] = None
    color: Optional[str] = None
    children: list["TreemapNode"] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TreemapChartConfig(BaseModel):
    """Treemap chart configuration"""
    chart_type: str = "treemap"
    root: TreemapNode

    # Layout
    algorithm: str = "squarify"  # squarify, binary, slice, dice
    padding: int = 2

    # Display
    show_labels: bool = True
    label_min_size: int = 20  # Min size to show label
    show_values: bool = True
    show_breadcrumb: bool = True

    # Interaction
    drilldown_enabled: bool = True

    # Colors
    color_by: str = "value"  # value, depth, category
    colors: ChartColorConfig = Field(default_factory=ChartColorConfig)

    # Legend/Tooltip
    legend: ChartLegendConfig = Field(default_factory=ChartLegendConfig)
    tooltip: ChartTooltipConfig = Field(default_factory=ChartTooltipConfig)


class TreemapChartRequest(BaseModel):
    """Request to create treemap"""
    connection_id: str
    query: Optional[str] = None

    # Column mappings
    id_column: str
    name_column: str
    value_column: str
    parent_column: Optional[str] = None
    color_column: Optional[str] = None

    # Hierarchy
    hierarchy_columns: Optional[list[str]] = None  # Alternative: define hierarchy via columns

    # Config
    config: Optional[TreemapChartConfig] = None


# Sankey Diagram

class SankeyNode(BaseModel):
    """Sankey node"""
    id: str
    name: str
    color: Optional[str] = None
    column: Optional[int] = None  # Fixed column position


class SankeyLink(BaseModel):
    """Sankey link"""
    source: str  # Node ID
    target: str  # Node ID
    value: float
    color: Optional[str] = None
    label: Optional[str] = None


class SankeyChartConfig(BaseModel):
    """Sankey chart configuration"""
    chart_type: str = "sankey"
    nodes: list[SankeyNode]
    links: list[SankeyLink]

    # Layout
    node_width: int = 20
    node_padding: int = 10
    iterations: int = 32  # Layout iterations

    # Display
    show_labels: bool = True
    label_position: str = "outside"  # inside, outside
    show_values: bool = True

    # Colors
    color_by: str = "source"  # source, target, gradient
    colors: ChartColorConfig = Field(default_factory=ChartColorConfig)

    # Legend/Tooltip
    legend: ChartLegendConfig = Field(default_factory=ChartLegendConfig)
    tooltip: ChartTooltipConfig = Field(default_factory=ChartTooltipConfig)


class SankeyChartRequest(BaseModel):
    """Request to create Sankey diagram"""
    connection_id: str
    query: Optional[str] = None

    # Column mappings
    source_column: str
    target_column: str
    value_column: str

    # Config
    config: Optional[SankeyChartConfig] = None


# Radar/Spider Chart

class RadarAxis(BaseModel):
    """Radar chart axis"""
    name: str
    max_value: Optional[float] = None
    min_value: float = 0


class RadarSeries(BaseModel):
    """Radar chart series"""
    name: str
    values: list[float]
    color: Optional[str] = None
    fill_opacity: float = 0.3


class RadarChartConfig(BaseModel):
    """Radar chart configuration"""
    chart_type: str = "radar"
    axes: list[RadarAxis]
    series: list[RadarSeries]

    # Shape
    shape: str = "polygon"  # polygon, circle
    levels: int = 5  # Number of grid levels

    # Display
    show_grid: bool = True
    show_labels: bool = True
    show_values: bool = False
    fill_area: bool = True

    # Colors
    colors: ChartColorConfig = Field(default_factory=ChartColorConfig)

    # Legend/Tooltip
    legend: ChartLegendConfig = Field(default_factory=ChartLegendConfig)
    tooltip: ChartTooltipConfig = Field(default_factory=ChartTooltipConfig)


class RadarChartRequest(BaseModel):
    """Request to create radar chart"""
    connection_id: str
    query: Optional[str] = None

    # Column mappings
    axis_column: str  # Column containing axis names
    value_columns: list[str]  # Columns for each series

    # Config
    config: Optional[RadarChartConfig] = None


# Bullet Chart

class BulletRange(BaseModel):
    """Bullet chart range"""
    name: str
    start: float
    end: float
    color: str


class BulletChartData(BaseModel):
    """Single bullet chart"""
    title: str
    subtitle: Optional[str] = None
    actual: float
    target: Optional[float] = None
    ranges: list[BulletRange] = Field(default_factory=list)
    format: Optional[str] = None


class BulletChartConfig(BaseModel):
    """Bullet chart configuration"""
    chart_type: str = "bullet"
    data: list[BulletChartData]

    # Layout
    orientation: str = "horizontal"  # horizontal, vertical

    # Display
    show_target: bool = True
    target_marker: str = "line"  # line, diamond
    show_labels: bool = True

    # Colors
    actual_color: str = "#1f2937"
    target_color: str = "#ef4444"
    range_colors: list[str] = Field(default_factory=lambda: ["#e5e7eb", "#d1d5db", "#9ca3af"])

    # Legend/Tooltip
    legend: ChartLegendConfig = Field(default_factory=ChartLegendConfig)
    tooltip: ChartTooltipConfig = Field(default_factory=ChartTooltipConfig)


class BulletChartRequest(BaseModel):
    """Request to create bullet chart"""
    connection_id: str
    query: Optional[str] = None

    # Column mappings
    title_column: str
    actual_column: str
    target_column: Optional[str] = None
    range_columns: Optional[list[str]] = None  # Columns defining ranges

    # Config
    config: Optional[BulletChartConfig] = None


# Heatmap

class HeatmapCell(BaseModel):
    """Heatmap cell"""
    x: str
    y: str
    value: float
    label: Optional[str] = None


class HeatmapChartConfig(BaseModel):
    """Heatmap configuration"""
    chart_type: str = "heatmap"
    cells: list[HeatmapCell]
    x_categories: list[str]
    y_categories: list[str]

    # Display
    show_labels: bool = True
    show_grid: bool = True
    cell_padding: int = 2

    # Color scale
    color_scale: str = "sequential"  # sequential, diverging
    min_color: str = "#eff6ff"
    max_color: str = "#1d4ed8"
    mid_color: Optional[str] = None  # For diverging

    # Axis
    x_axis: ChartAxisConfig = Field(default_factory=ChartAxisConfig)
    y_axis: ChartAxisConfig = Field(default_factory=ChartAxisConfig)

    # Legend/Tooltip
    legend: ChartLegendConfig = Field(default_factory=ChartLegendConfig)
    tooltip: ChartTooltipConfig = Field(default_factory=ChartTooltipConfig)


class HeatmapChartRequest(BaseModel):
    """Request to create heatmap"""
    connection_id: str
    query: Optional[str] = None

    # Column mappings
    x_column: str
    y_column: str
    value_column: str

    # Aggregation
    aggregation: str = "sum"  # sum, avg, count, min, max

    # Config
    config: Optional[HeatmapChartConfig] = None


# Gauge Chart

class GaugeChartConfig(BaseModel):
    """Gauge chart configuration"""
    chart_type: str = "gauge"
    value: float
    min_value: float = 0
    max_value: float = 100

    # Display
    title: Optional[str] = None
    subtitle: Optional[str] = None
    show_value: bool = True
    value_format: Optional[str] = None

    # Arc
    start_angle: float = -120
    end_angle: float = 120
    arc_width: float = 0.2  # Proportion of radius

    # Thresholds
    thresholds: list[dict[str, Any]] = Field(default_factory=lambda: [
        {"value": 33, "color": "#ef4444"},
        {"value": 66, "color": "#f59e0b"},
        {"value": 100, "color": "#22c55e"}
    ])

    # Pointer
    show_pointer: bool = True
    pointer_color: str = "#1f2937"


class GaugeChartRequest(BaseModel):
    """Request to create gauge chart"""
    connection_id: str
    query: Optional[str] = None

    # Column mapping
    value_column: str

    # Bounds
    min_value: float = 0
    max_value: float = 100

    # Config
    config: Optional[GaugeChartConfig] = None


# Boxplot

class BoxplotData(BaseModel):
    """Boxplot data for one category"""
    category: str
    min: float
    q1: float
    median: float
    q3: float
    max: float
    outliers: list[float] = Field(default_factory=list)
    mean: Optional[float] = None


class BoxplotChartConfig(BaseModel):
    """Boxplot configuration"""
    chart_type: str = "boxplot"
    data: list[BoxplotData]

    # Display
    orientation: str = "vertical"  # vertical, horizontal
    show_outliers: bool = True
    show_mean: bool = False
    box_width: float = 0.5

    # Colors
    box_color: str = "#3b82f6"
    median_color: str = "#1f2937"
    outlier_color: str = "#ef4444"

    # Axis
    category_axis: ChartAxisConfig = Field(default_factory=ChartAxisConfig)
    value_axis: ChartAxisConfig = Field(default_factory=ChartAxisConfig)

    # Legend/Tooltip
    legend: ChartLegendConfig = Field(default_factory=ChartLegendConfig)
    tooltip: ChartTooltipConfig = Field(default_factory=ChartTooltipConfig)


class BoxplotChartRequest(BaseModel):
    """Request to create boxplot"""
    connection_id: str
    query: Optional[str] = None

    # Column mappings
    category_column: str
    value_column: str

    # Config
    config: Optional[BoxplotChartConfig] = None


# Response Types

class AdvancedChartResponse(BaseModel):
    """Response for advanced chart creation"""
    chart_type: AdvancedChartType
    config: dict[str, Any]
    data: dict[str, Any]
    render_options: dict[str, Any] = Field(default_factory=dict)


class ChartTypeInfo(BaseModel):
    """Information about a chart type"""
    type: AdvancedChartType
    name: str
    description: str
    category: str
    required_data: list[str]
    optional_data: list[str]
    best_for: list[str]
    example_config: dict[str, Any]


# Chart Type Catalog

CHART_TYPE_CATALOG: list[ChartTypeInfo] = [
    ChartTypeInfo(
        type=AdvancedChartType.WATERFALL,
        name="Waterfall Chart",
        description="Shows how an initial value is affected by positive and negative changes",
        category="comparison",
        required_data=["category", "value"],
        optional_data=["type"],
        best_for=["Financial analysis", "Profit/loss breakdown", "Sequential changes"],
        example_config={"show_connectors": True, "auto_total": True}
    ),
    ChartTypeInfo(
        type=AdvancedChartType.FUNNEL,
        name="Funnel Chart",
        description="Visualizes stages in a process, showing conversion rates",
        category="flow",
        required_data=["stage", "value"],
        optional_data=[],
        best_for=["Sales pipelines", "Conversion funnels", "Process stages"],
        example_config={"show_conversion_rates": True, "orientation": "vertical"}
    ),
    ChartTypeInfo(
        type=AdvancedChartType.GANTT,
        name="Gantt Chart",
        description="Project timeline showing tasks, durations, and dependencies",
        category="timeline",
        required_data=["task", "start_date", "end_date"],
        optional_data=["progress", "dependencies", "assignee"],
        best_for=["Project management", "Resource planning", "Timeline visualization"],
        example_config={"show_dependencies": True, "show_progress": True}
    ),
    ChartTypeInfo(
        type=AdvancedChartType.TREEMAP,
        name="Treemap",
        description="Hierarchical data as nested rectangles proportional to value",
        category="hierarchy",
        required_data=["name", "value"],
        optional_data=["parent", "color"],
        best_for=["Disk usage", "Budget allocation", "Hierarchical comparisons"],
        example_config={"drilldown_enabled": True, "algorithm": "squarify"}
    ),
    ChartTypeInfo(
        type=AdvancedChartType.SANKEY,
        name="Sankey Diagram",
        description="Flow diagram showing quantities between nodes",
        category="flow",
        required_data=["source", "target", "value"],
        optional_data=[],
        best_for=["Energy flows", "Budget flows", "User journeys"],
        example_config={"color_by": "source", "show_values": True}
    ),
    ChartTypeInfo(
        type=AdvancedChartType.RADAR,
        name="Radar Chart",
        description="Multivariate data on axes starting from the same point",
        category="comparison",
        required_data=["axis", "values"],
        optional_data=[],
        best_for=["Performance comparison", "Skill assessment", "Product comparison"],
        example_config={"shape": "polygon", "fill_area": True}
    ),
    ChartTypeInfo(
        type=AdvancedChartType.BULLET,
        name="Bullet Chart",
        description="Linear gauge showing actual vs target with qualitative ranges",
        category="kpi",
        required_data=["title", "actual"],
        optional_data=["target", "ranges"],
        best_for=["KPI dashboards", "Goal tracking", "Performance metrics"],
        example_config={"show_target": True, "orientation": "horizontal"}
    ),
    ChartTypeInfo(
        type=AdvancedChartType.HEATMAP,
        name="Heatmap",
        description="Matrix with color-coded cells representing values",
        category="distribution",
        required_data=["x", "y", "value"],
        optional_data=[],
        best_for=["Correlation matrices", "Time patterns", "Geographic density"],
        example_config={"color_scale": "sequential", "show_labels": True}
    ),
    ChartTypeInfo(
        type=AdvancedChartType.GAUGE,
        name="Gauge Chart",
        description="Circular chart showing a single value against a scale",
        category="kpi",
        required_data=["value"],
        optional_data=["min", "max", "thresholds"],
        best_for=["KPI display", "Progress tracking", "Status indicators"],
        example_config={"show_pointer": True, "arc_width": 0.2}
    ),
    ChartTypeInfo(
        type=AdvancedChartType.BOXPLOT,
        name="Box Plot",
        description="Statistical distribution showing quartiles and outliers",
        category="distribution",
        required_data=["category", "value"],
        optional_data=[],
        best_for=["Distribution comparison", "Outlier detection", "Statistical analysis"],
        example_config={"show_outliers": True, "show_mean": True}
    ),
]


def get_chart_type_info(chart_type: AdvancedChartType) -> Optional[ChartTypeInfo]:
    """Get info for a specific chart type"""
    for info in CHART_TYPE_CATALOG:
        if info.type == chart_type:
            return info
    return None
