"""
Advanced Charts API Endpoints

REST API for advanced visualization types.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.advanced_charts_service import AdvancedChartsService
from app.schemas.advanced_charts import (
    AdvancedChartType,
    WaterfallChartRequest,
    FunnelChartRequest,
    GanttChartRequest,
    TreemapChartRequest,
    SankeyChartRequest,
    RadarChartRequest,
    BulletChartRequest,
    HeatmapChartRequest,
    GaugeChartRequest,
    BoxplotChartRequest,
    AdvancedChartResponse,
    CHART_TYPE_CATALOG,
)

router = APIRouter()


# Chart Type Information

@router.get("/types")
async def list_chart_types():
    """
    List all available advanced chart types.

    Returns information about each chart type including:
    - Name and description
    - Required and optional data fields
    - Best use cases
    - Example configuration
    """
    return [info.model_dump() for info in CHART_TYPE_CATALOG]


@router.get("/types/{chart_type}")
async def get_chart_type_info(
    chart_type: AdvancedChartType,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific chart type."""
    service = AdvancedChartsService(db)
    info = await service.get_chart_type_info(chart_type)

    if not info:
        raise HTTPException(status_code=404, detail="Chart type not found")

    return info


# Chart Suggestions

@router.post("/suggest")
async def suggest_chart_types(
    data: list[dict],
    columns: list[str] = Query(..., description="Available columns"),
    has_time_column: bool = Query(False, description="Data has time/date column"),
    has_hierarchy: bool = Query(False, description="Data has hierarchical structure"),
    has_flow_data: bool = Query(False, description="Data represents flows/connections"),
    num_categories: int = Query(0, description="Number of categorical columns"),
    num_measures: int = Query(0, description="Number of measure columns"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get chart type suggestions based on data characteristics.

    Analyzes the data and suggests appropriate advanced chart types.
    """
    service = AdvancedChartsService(db)

    characteristics = {
        "has_time_column": has_time_column,
        "has_hierarchy": has_hierarchy,
        "has_flow_data": has_flow_data,
        "num_categories": num_categories,
        "num_measures": num_measures,
    }

    suggestions = await service.suggest_chart_type(data, columns, characteristics)
    return {"suggestions": suggestions}


# Waterfall Chart

@router.post("/waterfall", response_model=AdvancedChartResponse)
async def create_waterfall_chart(
    request: WaterfallChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a waterfall chart configuration.

    Waterfall charts show how an initial value is affected by
    a series of positive or negative values.

    **Use cases:**
    - Financial analysis (profit/loss breakdown)
    - Inventory changes
    - Sequential value changes
    """
    service = AdvancedChartsService(db)
    return await service.create_waterfall_chart(data, request)


# Funnel Chart

@router.post("/funnel", response_model=AdvancedChartResponse)
async def create_funnel_chart(
    request: FunnelChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a funnel chart configuration.

    Funnel charts visualize stages in a process,
    showing how values decrease at each stage.

    **Use cases:**
    - Sales pipelines
    - Conversion funnels
    - Process stage analysis
    """
    service = AdvancedChartsService(db)
    return await service.create_funnel_chart(data, request)


# Gantt Chart

@router.post("/gantt", response_model=AdvancedChartResponse)
async def create_gantt_chart(
    request: GanttChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Gantt chart configuration.

    Gantt charts display project timelines with tasks,
    durations, dependencies, and progress.

    **Use cases:**
    - Project management
    - Resource planning
    - Schedule visualization
    """
    service = AdvancedChartsService(db)
    return await service.create_gantt_chart(data, request)


# Treemap

@router.post("/treemap", response_model=AdvancedChartResponse)
async def create_treemap_chart(
    request: TreemapChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a treemap configuration.

    Treemaps display hierarchical data as nested rectangles,
    with size proportional to value.

    **Use cases:**
    - Disk usage visualization
    - Budget allocation
    - Hierarchical category comparison
    """
    service = AdvancedChartsService(db)
    return await service.create_treemap_chart(data, request)


# Sankey Diagram

@router.post("/sankey", response_model=AdvancedChartResponse)
async def create_sankey_chart(
    request: SankeyChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a Sankey diagram configuration.

    Sankey diagrams visualize flow quantities between nodes,
    with link width proportional to flow magnitude.

    **Use cases:**
    - Energy flow analysis
    - Budget allocation flows
    - User journey mapping
    """
    service = AdvancedChartsService(db)
    return await service.create_sankey_chart(data, request)


# Radar Chart

@router.post("/radar", response_model=AdvancedChartResponse)
async def create_radar_chart(
    request: RadarChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a radar (spider) chart configuration.

    Radar charts display multivariate data on axes radiating
    from a center point.

    **Use cases:**
    - Performance comparison
    - Skill assessment
    - Product feature comparison
    """
    service = AdvancedChartsService(db)
    return await service.create_radar_chart(data, request)


# Bullet Chart

@router.post("/bullet", response_model=AdvancedChartResponse)
async def create_bullet_chart(
    request: BulletChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a bullet chart configuration.

    Bullet charts are linear gauges showing actual value
    against a target with qualitative ranges.

    **Use cases:**
    - KPI dashboards
    - Goal tracking
    - Performance metrics
    """
    service = AdvancedChartsService(db)
    return await service.create_bullet_chart(data, request)


# Heatmap

@router.post("/heatmap", response_model=AdvancedChartResponse)
async def create_heatmap_chart(
    request: HeatmapChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a heatmap configuration.

    Heatmaps display matrix data with color-coded cells
    representing values.

    **Use cases:**
    - Correlation matrices
    - Time-based patterns (hour x day)
    - Geographic density
    """
    service = AdvancedChartsService(db)
    return await service.create_heatmap_chart(data, request)


# Gauge Chart

@router.post("/gauge", response_model=AdvancedChartResponse)
async def create_gauge_chart(
    request: GaugeChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a gauge chart configuration.

    Gauge charts display a single value on a circular scale
    with optional threshold indicators.

    **Use cases:**
    - KPI display
    - Progress tracking
    - Status indicators
    """
    service = AdvancedChartsService(db)
    return await service.create_gauge_chart(data, request)


# Box Plot

@router.post("/boxplot", response_model=AdvancedChartResponse)
async def create_boxplot_chart(
    request: BoxplotChartRequest,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a box plot configuration.

    Box plots display statistical distribution including
    quartiles, median, and outliers.

    **Use cases:**
    - Distribution comparison
    - Outlier detection
    - Statistical analysis
    """
    service = AdvancedChartsService(db)
    return await service.create_boxplot_chart(data, request)


# Generic Creation Endpoint

@router.post("/create/{chart_type}", response_model=AdvancedChartResponse)
async def create_advanced_chart(
    chart_type: AdvancedChartType,
    config: dict,
    data: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Generic endpoint to create any advanced chart type.

    Accepts chart type as path parameter and configuration
    in request body.
    """
    service = AdvancedChartsService(db)

    # Map chart type to handler
    handlers = {
        AdvancedChartType.WATERFALL: lambda: service.create_waterfall_chart(
            data, WaterfallChartRequest(**config)
        ),
        AdvancedChartType.FUNNEL: lambda: service.create_funnel_chart(
            data, FunnelChartRequest(**config)
        ),
        AdvancedChartType.GANTT: lambda: service.create_gantt_chart(
            data, GanttChartRequest(**config)
        ),
        AdvancedChartType.TREEMAP: lambda: service.create_treemap_chart(
            data, TreemapChartRequest(**config)
        ),
        AdvancedChartType.SANKEY: lambda: service.create_sankey_chart(
            data, SankeyChartRequest(**config)
        ),
        AdvancedChartType.RADAR: lambda: service.create_radar_chart(
            data, RadarChartRequest(**config)
        ),
        AdvancedChartType.BULLET: lambda: service.create_bullet_chart(
            data, BulletChartRequest(**config)
        ),
        AdvancedChartType.HEATMAP: lambda: service.create_heatmap_chart(
            data, HeatmapChartRequest(**config)
        ),
        AdvancedChartType.GAUGE: lambda: service.create_gauge_chart(
            data, GaugeChartRequest(**config)
        ),
        AdvancedChartType.BOXPLOT: lambda: service.create_boxplot_chart(
            data, BoxplotChartRequest(**config)
        ),
    }

    handler = handlers.get(chart_type)
    if not handler:
        raise HTTPException(
            status_code=400,
            detail=f"Chart type '{chart_type}' not supported"
        )

    try:
        return await handler()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Template Endpoints

@router.get("/templates/{chart_type}")
async def get_chart_template(
    chart_type: AdvancedChartType,
):
    """
    Get a configuration template for a chart type.

    Returns a sample configuration that can be customized.
    """
    templates = {
        AdvancedChartType.WATERFALL: {
            "connection_id": "your-connection-id",
            "category_column": "category",
            "value_column": "amount",
            "auto_total": True,
            "starting_value": 0,
            "config": {
                "show_connectors": True,
                "show_labels": True,
            },
        },
        AdvancedChartType.FUNNEL: {
            "connection_id": "your-connection-id",
            "stage_column": "stage",
            "value_column": "count",
            "config": {
                "orientation": "vertical",
                "show_percentages": True,
                "show_conversion_rates": True,
            },
        },
        AdvancedChartType.GANTT: {
            "connection_id": "your-connection-id",
            "id_column": "task_id",
            "name_column": "task_name",
            "start_column": "start_date",
            "end_column": "end_date",
            "progress_column": "progress",
            "config": {
                "show_dependencies": True,
                "show_progress": True,
                "time_unit": "day",
            },
        },
        AdvancedChartType.TREEMAP: {
            "connection_id": "your-connection-id",
            "id_column": "id",
            "name_column": "name",
            "value_column": "size",
            "parent_column": "parent_id",
            "config": {
                "algorithm": "squarify",
                "drilldown_enabled": True,
            },
        },
        AdvancedChartType.SANKEY: {
            "connection_id": "your-connection-id",
            "source_column": "source",
            "target_column": "target",
            "value_column": "value",
            "config": {
                "color_by": "source",
                "show_values": True,
            },
        },
        AdvancedChartType.RADAR: {
            "connection_id": "your-connection-id",
            "axis_column": "metric",
            "value_columns": ["product_a", "product_b"],
            "config": {
                "shape": "polygon",
                "fill_area": True,
                "levels": 5,
            },
        },
        AdvancedChartType.BULLET: {
            "connection_id": "your-connection-id",
            "title_column": "metric_name",
            "actual_column": "actual_value",
            "target_column": "target_value",
            "range_columns": ["poor", "satisfactory", "good"],
            "config": {
                "orientation": "horizontal",
                "show_target": True,
            },
        },
        AdvancedChartType.HEATMAP: {
            "connection_id": "your-connection-id",
            "x_column": "hour",
            "y_column": "day_of_week",
            "value_column": "count",
            "aggregation": "sum",
            "config": {
                "color_scale": "sequential",
                "show_labels": True,
            },
        },
        AdvancedChartType.GAUGE: {
            "connection_id": "your-connection-id",
            "value_column": "current_value",
            "min_value": 0,
            "max_value": 100,
            "config": {
                "show_pointer": True,
                "thresholds": [
                    {"value": 33, "color": "#ef4444"},
                    {"value": 66, "color": "#f59e0b"},
                    {"value": 100, "color": "#22c55e"},
                ],
            },
        },
        AdvancedChartType.BOXPLOT: {
            "connection_id": "your-connection-id",
            "category_column": "group",
            "value_column": "measurement",
            "config": {
                "orientation": "vertical",
                "show_outliers": True,
                "show_mean": True,
            },
        },
    }

    template = templates.get(chart_type)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template
