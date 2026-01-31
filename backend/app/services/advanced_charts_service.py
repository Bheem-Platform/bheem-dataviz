"""
Advanced Charts Service

Service for generating advanced visualization configurations.
"""

import statistics
from typing import Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.advanced_charts import (
    AdvancedChartType,
    WaterfallDataPoint,
    WaterfallBarType,
    WaterfallChartConfig,
    WaterfallChartRequest,
    FunnelStage,
    FunnelChartConfig,
    FunnelChartRequest,
    GanttTask,
    GanttChartConfig,
    GanttChartRequest,
    TreemapNode,
    TreemapChartConfig,
    TreemapChartRequest,
    SankeyNode,
    SankeyLink,
    SankeyChartConfig,
    SankeyChartRequest,
    RadarAxis,
    RadarSeries,
    RadarChartConfig,
    RadarChartRequest,
    BulletChartData,
    BulletRange,
    BulletChartConfig,
    BulletChartRequest,
    HeatmapCell,
    HeatmapChartConfig,
    HeatmapChartRequest,
    GaugeChartConfig,
    GaugeChartRequest,
    BoxplotData,
    BoxplotChartConfig,
    BoxplotChartRequest,
    AdvancedChartResponse,
    ChartColorConfig,
    CHART_TYPE_CATALOG,
)


logger = logging.getLogger(__name__)


class AdvancedChartsService:
    """Service for creating advanced chart configurations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Waterfall Chart

    async def create_waterfall_chart(
        self,
        data: list[dict[str, Any]],
        request: WaterfallChartRequest,
    ) -> AdvancedChartResponse:
        """Create a waterfall chart configuration from data."""
        data_points = []
        running_total = request.starting_value

        for i, row in enumerate(data):
            category = str(row.get(request.category_column, f"Item {i+1}"))
            value = float(row.get(request.value_column, 0))

            # Determine bar type
            if request.type_column and request.type_column in row:
                type_str = str(row[request.type_column]).lower()
                if type_str in ["total", "subtotal"]:
                    bar_type = WaterfallBarType.TOTAL if type_str == "total" else WaterfallBarType.SUBTOTAL
                elif value >= 0:
                    bar_type = WaterfallBarType.INCREASE
                else:
                    bar_type = WaterfallBarType.DECREASE
            else:
                bar_type = WaterfallBarType.INCREASE if value >= 0 else WaterfallBarType.DECREASE

            # Calculate running total for non-total bars
            if bar_type not in [WaterfallBarType.TOTAL, WaterfallBarType.SUBTOTAL]:
                running_total += value

            data_points.append(WaterfallDataPoint(
                category=category,
                value=value if bar_type not in [WaterfallBarType.TOTAL, WaterfallBarType.SUBTOTAL] else running_total,
                bar_type=bar_type,
            ))

        # Add auto total if requested
        if request.auto_total and data_points:
            if data_points[-1].bar_type != WaterfallBarType.TOTAL:
                data_points.append(WaterfallDataPoint(
                    category="Total",
                    value=running_total,
                    bar_type=WaterfallBarType.TOTAL,
                ))

        config = request.config or WaterfallChartConfig(data=data_points)
        config.data = data_points

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.WATERFALL,
            config=config.model_dump(),
            data={"points": [p.model_dump() for p in data_points]},
        )

    # Funnel Chart

    async def create_funnel_chart(
        self,
        data: list[dict[str, Any]],
        request: FunnelChartRequest,
    ) -> AdvancedChartResponse:
        """Create a funnel chart configuration from data."""
        # Extract stages
        stage_data = {}
        for row in data:
            stage = str(row.get(request.stage_column, ""))
            value = float(row.get(request.value_column, 0))
            if stage:
                stage_data[stage] = stage_data.get(stage, 0) + value

        # Order stages
        if request.stage_order:
            ordered_stages = request.stage_order
        else:
            # Order by value descending
            ordered_stages = sorted(stage_data.keys(), key=lambda s: stage_data.get(s, 0), reverse=True)

        # Calculate percentages and conversion rates
        stages = []
        first_value = None
        prev_value = None

        for stage_name in ordered_stages:
            if stage_name not in stage_data:
                continue

            value = stage_data[stage_name]
            if first_value is None:
                first_value = value

            percentage = (value / first_value * 100) if first_value > 0 else 0
            conversion_rate = (value / prev_value * 100) if prev_value and prev_value > 0 else 100

            stages.append(FunnelStage(
                name=stage_name,
                value=value,
                percentage=round(percentage, 1),
                conversion_rate=round(conversion_rate, 1),
            ))

            prev_value = value

        config = request.config or FunnelChartConfig(stages=stages)
        config.stages = stages

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.FUNNEL,
            config=config.model_dump(),
            data={"stages": [s.model_dump() for s in stages]},
        )

    # Gantt Chart

    async def create_gantt_chart(
        self,
        data: list[dict[str, Any]],
        request: GanttChartRequest,
    ) -> AdvancedChartResponse:
        """Create a Gantt chart configuration from data."""
        tasks = []

        for row in data:
            task_id = str(row.get(request.id_column, ""))
            name = str(row.get(request.name_column, ""))

            # Parse dates
            start = row.get(request.start_column)
            end = row.get(request.end_column)

            if isinstance(start, str):
                start = datetime.fromisoformat(start.replace("Z", "+00:00"))
            if isinstance(end, str):
                end = datetime.fromisoformat(end.replace("Z", "+00:00"))

            if not task_id or not start or not end:
                continue

            # Optional fields
            progress = float(row.get(request.progress_column, 0)) if request.progress_column else 0
            parent_id = str(row.get(request.parent_column)) if request.parent_column and row.get(request.parent_column) else None

            dependencies = []
            if request.dependencies_column and row.get(request.dependencies_column):
                deps = row[request.dependencies_column]
                if isinstance(deps, str):
                    dependencies = [d.strip() for d in deps.split(",")]
                elif isinstance(deps, list):
                    dependencies = deps

            tasks.append(GanttTask(
                id=task_id,
                name=name,
                start=start,
                end=end,
                progress=progress,
                parent_id=parent_id,
                dependencies=dependencies,
            ))

        config = request.config or GanttChartConfig(tasks=tasks)
        config.tasks = tasks

        # Calculate date range
        if tasks:
            min_start = min(t.start for t in tasks)
            max_end = max(t.end for t in tasks)
            config.start_date = min_start
            config.end_date = max_end

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.GANTT,
            config=config.model_dump(),
            data={"tasks": [t.model_dump() for t in tasks]},
        )

    # Treemap

    async def create_treemap_chart(
        self,
        data: list[dict[str, Any]],
        request: TreemapChartRequest,
    ) -> AdvancedChartResponse:
        """Create a treemap configuration from data."""
        nodes = {}
        root_children = []

        # Build node dictionary
        for row in data:
            node_id = str(row.get(request.id_column, ""))
            name = str(row.get(request.name_column, ""))
            value = float(row.get(request.value_column, 0))
            parent_id = str(row.get(request.parent_column)) if request.parent_column and row.get(request.parent_column) else None
            color = row.get(request.color_column) if request.color_column else None

            if not node_id:
                continue

            nodes[node_id] = TreemapNode(
                id=node_id,
                name=name,
                value=value,
                parent_id=parent_id,
                color=color,
            )

        # Build tree structure
        for node_id, node in nodes.items():
            if node.parent_id and node.parent_id in nodes:
                parent = nodes[node.parent_id]
                parent.children.append(node)
            else:
                root_children.append(node)

        # Create root node
        root = TreemapNode(
            id="root",
            name="Root",
            value=sum(n.value for n in root_children),
            children=root_children,
        )

        config = request.config or TreemapChartConfig(root=root)
        config.root = root

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.TREEMAP,
            config=config.model_dump(),
            data={"root": root.model_dump()},
        )

    # Sankey Diagram

    async def create_sankey_chart(
        self,
        data: list[dict[str, Any]],
        request: SankeyChartRequest,
    ) -> AdvancedChartResponse:
        """Create a Sankey diagram configuration from data."""
        nodes_set = set()
        links = []

        for row in data:
            source = str(row.get(request.source_column, ""))
            target = str(row.get(request.target_column, ""))
            value = float(row.get(request.value_column, 0))

            if source and target and value > 0:
                nodes_set.add(source)
                nodes_set.add(target)
                links.append(SankeyLink(
                    source=source,
                    target=target,
                    value=value,
                ))

        nodes = [SankeyNode(id=n, name=n) for n in sorted(nodes_set)]

        config = request.config or SankeyChartConfig(nodes=nodes, links=links)
        config.nodes = nodes
        config.links = links

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.SANKEY,
            config=config.model_dump(),
            data={
                "nodes": [n.model_dump() for n in nodes],
                "links": [l.model_dump() for l in links],
            },
        )

    # Radar Chart

    async def create_radar_chart(
        self,
        data: list[dict[str, Any]],
        request: RadarChartRequest,
    ) -> AdvancedChartResponse:
        """Create a radar chart configuration from data."""
        # Extract axes (unique values from axis column)
        axes_values = {}
        for row in data:
            axis_name = str(row.get(request.axis_column, ""))
            if axis_name:
                for col in request.value_columns:
                    if axis_name not in axes_values:
                        axes_values[axis_name] = {}
                    axes_values[axis_name][col] = float(row.get(col, 0))

        axes = [RadarAxis(name=name) for name in axes_values.keys()]

        # Create series
        series = []
        for col in request.value_columns:
            values = [axes_values[axis.name].get(col, 0) for axis in axes]
            series.append(RadarSeries(
                name=col,
                values=values,
            ))

        # Calculate max values for each axis
        for i, axis in enumerate(axes):
            max_val = max(s.values[i] for s in series) if series else 0
            axis.max_value = max_val * 1.1  # Add 10% padding

        config = request.config or RadarChartConfig(axes=axes, series=series)
        config.axes = axes
        config.series = series

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.RADAR,
            config=config.model_dump(),
            data={
                "axes": [a.model_dump() for a in axes],
                "series": [s.model_dump() for s in series],
            },
        )

    # Bullet Chart

    async def create_bullet_chart(
        self,
        data: list[dict[str, Any]],
        request: BulletChartRequest,
    ) -> AdvancedChartResponse:
        """Create a bullet chart configuration from data."""
        bullets = []

        for row in data:
            title = str(row.get(request.title_column, ""))
            actual = float(row.get(request.actual_column, 0))
            target = float(row.get(request.target_column, 0)) if request.target_column else None

            # Build ranges
            ranges = []
            if request.range_columns:
                range_colors = ["#e5e7eb", "#d1d5db", "#9ca3af"]
                prev_value = 0
                for i, col in enumerate(request.range_columns):
                    range_value = float(row.get(col, 0))
                    ranges.append(BulletRange(
                        name=col,
                        start=prev_value,
                        end=range_value,
                        color=range_colors[i % len(range_colors)],
                    ))
                    prev_value = range_value

            bullets.append(BulletChartData(
                title=title,
                actual=actual,
                target=target,
                ranges=ranges,
            ))

        config = request.config or BulletChartConfig(data=bullets)
        config.data = bullets

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.BULLET,
            config=config.model_dump(),
            data={"bullets": [b.model_dump() for b in bullets]},
        )

    # Heatmap

    async def create_heatmap_chart(
        self,
        data: list[dict[str, Any]],
        request: HeatmapChartRequest,
    ) -> AdvancedChartResponse:
        """Create a heatmap configuration from data."""
        # Aggregate data
        cell_values = {}
        x_categories = set()
        y_categories = set()

        for row in data:
            x = str(row.get(request.x_column, ""))
            y = str(row.get(request.y_column, ""))
            value = float(row.get(request.value_column, 0))

            if x and y:
                x_categories.add(x)
                y_categories.add(y)
                key = (x, y)
                if key not in cell_values:
                    cell_values[key] = []
                cell_values[key].append(value)

        # Aggregate
        cells = []
        for (x, y), values in cell_values.items():
            if request.aggregation == "sum":
                agg_value = sum(values)
            elif request.aggregation == "avg":
                agg_value = statistics.mean(values)
            elif request.aggregation == "count":
                agg_value = len(values)
            elif request.aggregation == "min":
                agg_value = min(values)
            elif request.aggregation == "max":
                agg_value = max(values)
            else:
                agg_value = sum(values)

            cells.append(HeatmapCell(x=x, y=y, value=agg_value))

        x_list = sorted(x_categories)
        y_list = sorted(y_categories)

        config = request.config or HeatmapChartConfig(
            cells=cells,
            x_categories=x_list,
            y_categories=y_list,
        )
        config.cells = cells
        config.x_categories = x_list
        config.y_categories = y_list

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.HEATMAP,
            config=config.model_dump(),
            data={
                "cells": [c.model_dump() for c in cells],
                "x_categories": x_list,
                "y_categories": y_list,
            },
        )

    # Gauge Chart

    async def create_gauge_chart(
        self,
        data: list[dict[str, Any]],
        request: GaugeChartRequest,
    ) -> AdvancedChartResponse:
        """Create a gauge chart configuration from data."""
        # Get the value (use first row or aggregate)
        value = 0
        if data:
            values = [float(row.get(request.value_column, 0)) for row in data]
            value = values[0] if len(values) == 1 else statistics.mean(values)

        config = request.config or GaugeChartConfig(
            value=value,
            min_value=request.min_value,
            max_value=request.max_value,
        )
        config.value = value
        config.min_value = request.min_value
        config.max_value = request.max_value

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.GAUGE,
            config=config.model_dump(),
            data={"value": value},
        )

    # Box Plot

    async def create_boxplot_chart(
        self,
        data: list[dict[str, Any]],
        request: BoxplotChartRequest,
    ) -> AdvancedChartResponse:
        """Create a boxplot configuration from data."""
        # Group by category
        category_values = {}
        for row in data:
            category = str(row.get(request.category_column, ""))
            value = float(row.get(request.value_column, 0))
            if category:
                if category not in category_values:
                    category_values[category] = []
                category_values[category].append(value)

        # Calculate boxplot statistics
        boxplots = []
        for category, values in category_values.items():
            if len(values) < 5:
                continue

            sorted_values = sorted(values)
            n = len(sorted_values)

            q1_idx = int(n * 0.25)
            q3_idx = int(n * 0.75)

            q1 = sorted_values[q1_idx]
            q3 = sorted_values[q3_idx]
            median = statistics.median(sorted_values)
            mean = statistics.mean(sorted_values)

            iqr = q3 - q1
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr

            # Find min/max within fences
            whisker_min = min(v for v in sorted_values if v >= lower_fence)
            whisker_max = max(v for v in sorted_values if v <= upper_fence)

            # Find outliers
            outliers = [v for v in sorted_values if v < lower_fence or v > upper_fence]

            boxplots.append(BoxplotData(
                category=category,
                min=whisker_min,
                q1=q1,
                median=median,
                q3=q3,
                max=whisker_max,
                outliers=outliers,
                mean=mean,
            ))

        config = request.config or BoxplotChartConfig(data=boxplots)
        config.data = boxplots

        return AdvancedChartResponse(
            chart_type=AdvancedChartType.BOXPLOT,
            config=config.model_dump(),
            data={"boxplots": [b.model_dump() for b in boxplots]},
        )

    # Utility Methods

    async def get_chart_types(self) -> list[dict[str, Any]]:
        """Get all available advanced chart types."""
        return [info.model_dump() for info in CHART_TYPE_CATALOG]

    async def get_chart_type_info(self, chart_type: AdvancedChartType) -> Optional[dict[str, Any]]:
        """Get information about a specific chart type."""
        for info in CHART_TYPE_CATALOG:
            if info.type == chart_type:
                return info.model_dump()
        return None

    async def suggest_chart_type(
        self,
        data: list[dict[str, Any]],
        columns: list[str],
        data_characteristics: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Suggest appropriate advanced chart types based on data."""
        suggestions = []

        # Analyze data characteristics
        has_time = data_characteristics.get("has_time_column", False)
        has_hierarchy = data_characteristics.get("has_hierarchy", False)
        has_flow = data_characteristics.get("has_flow_data", False)
        num_categories = data_characteristics.get("num_categories", 0)
        num_measures = data_characteristics.get("num_measures", 0)

        # Suggest based on characteristics
        if has_flow:
            suggestions.append({
                "type": AdvancedChartType.SANKEY,
                "reason": "Data has flow/connection patterns",
                "confidence": 0.9,
            })
            suggestions.append({
                "type": AdvancedChartType.FUNNEL,
                "reason": "Data may represent process stages",
                "confidence": 0.7,
            })

        if has_time and num_categories > 1:
            suggestions.append({
                "type": AdvancedChartType.GANTT,
                "reason": "Time-based data with multiple items",
                "confidence": 0.8,
            })

        if has_hierarchy:
            suggestions.append({
                "type": AdvancedChartType.TREEMAP,
                "reason": "Hierarchical data structure detected",
                "confidence": 0.9,
            })

        if num_measures > 3:
            suggestions.append({
                "type": AdvancedChartType.RADAR,
                "reason": "Multiple measures for comparison",
                "confidence": 0.8,
            })

        if num_categories <= 10 and num_measures >= 1:
            suggestions.append({
                "type": AdvancedChartType.WATERFALL,
                "reason": "Sequential data suitable for breakdown",
                "confidence": 0.6,
            })

        if num_measures == 1 and num_categories == 1:
            suggestions.append({
                "type": AdvancedChartType.GAUGE,
                "reason": "Single KPI value",
                "confidence": 0.9,
            })
            suggestions.append({
                "type": AdvancedChartType.BULLET,
                "reason": "Single metric with potential target",
                "confidence": 0.7,
            })

        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)

        return suggestions[:5]
