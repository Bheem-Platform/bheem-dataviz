"""
Chart Recommendation Service for Quick Charts feature.

Uses rule-based heuristics to suggest optimal chart types
based on data profiles.
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from app.schemas.quickchart import (
    ColumnDataType,
    Cardinality,
    ColumnProfile,
    TableProfile,
    ChartRecommendation,
    DimensionConfig,
    MeasureConfig,
)

logger = logging.getLogger(__name__)


class ChartRecommender:
    """
    Recommends optimal chart types based on data profile.
    Uses rule-based heuristics for fast, deterministic results.
    """

    # Chart type rules - order matters (first match wins for similar patterns)
    CHART_RULES = [
        {
            "type": "kpi",
            "name": "KPI Card",
            "requires": {"numeric": 1},
            "max_dimensions": 0,
            "confidence": 0.90,
            "reason": "Single metric display for key performance indicators"
        },
        {
            "type": "pie",
            "name": "Pie Chart",
            "requires": {"categorical_low": 1, "numeric": 1},
            "max_distinct": 6,
            "confidence": 0.88,
            "reason": "Pie chart shows proportion breakdown for small categories"
        },
        {
            "type": "donut",
            "name": "Donut Chart",
            "requires": {"categorical_low": 1, "numeric": 1},
            "max_distinct": 10,
            "confidence": 0.85,
            "reason": "Donut chart provides proportion view with center space"
        },
        {
            "type": "line",
            "name": "Line Chart",
            "requires": {"temporal": 1, "numeric": 1},
            "confidence": 0.95,
            "reason": "Line chart is ideal for showing trends over time"
        },
        {
            "type": "area",
            "name": "Area Chart",
            "requires": {"temporal": 1, "numeric": 1},
            "confidence": 0.82,
            "reason": "Area chart emphasizes magnitude of change over time"
        },
        {
            "type": "bar",
            "name": "Bar Chart",
            "requires": {"categorical": 1, "numeric": 1},
            "max_distinct": 20,
            "confidence": 0.95,
            "reason": "Bar chart is ideal for comparing categories"
        },
        {
            "type": "horizontal-bar",
            "name": "Horizontal Bar Chart",
            "requires": {"categorical": 1, "numeric": 1},
            "min_distinct": 8,
            "confidence": 0.85,
            "reason": "Horizontal bars work better for many categories"
        },
        {
            "type": "scatter",
            "name": "Scatter Plot",
            "requires": {"numeric": 2},
            "confidence": 0.85,
            "reason": "Scatter plot reveals correlation between variables"
        },
        {
            "type": "table",
            "name": "Data Table",
            "requires": {},
            "min_columns": 3,
            "confidence": 0.70,
            "reason": "Table view for detailed multi-column data exploration"
        }
    ]

    # Color palette for charts
    COLORS = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
        '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#48b8d0'
    ]

    def recommend(
        self,
        profile: TableProfile,
        max_recommendations: int = 5
    ) -> List[ChartRecommendation]:
        """
        Generate chart recommendations based on table profile.

        Args:
            profile: TableProfile with column statistics
            max_recommendations: Maximum number of suggestions to return

        Returns:
            List of ChartRecommendation sorted by confidence
        """
        recommendations = []

        # Categorize available columns
        categorized = self._categorize_columns(profile.columns)

        # Track used chart types to avoid duplicates
        used_types = set()

        # Try each chart rule
        for rule in self.CHART_RULES:
            if rule["type"] in used_types:
                continue

            if self._matches_rule(categorized, rule, profile):
                recommendation = self._build_recommendation(
                    rule, categorized, profile
                )
                if recommendation:
                    recommendations.append(recommendation)
                    used_types.add(rule["type"])

        # Sort by confidence, take top N
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        return recommendations[:max_recommendations]

    def _categorize_columns(
        self,
        columns: List[ColumnProfile]
    ) -> Dict[str, List[ColumnProfile]]:
        """Group columns by their data type and cardinality."""
        return {
            "numeric": [c for c in columns if c.data_type == ColumnDataType.NUMERIC],
            "temporal": [c for c in columns if c.data_type == ColumnDataType.TEMPORAL],
            "categorical": [c for c in columns if c.data_type == ColumnDataType.CATEGORICAL],
            "categorical_low": [
                c for c in columns
                if c.data_type == ColumnDataType.CATEGORICAL
                and c.cardinality == Cardinality.LOW
            ],
            "categorical_medium": [
                c for c in columns
                if c.data_type == ColumnDataType.CATEGORICAL
                and c.cardinality == Cardinality.MEDIUM
            ],
            "boolean": [c for c in columns if c.data_type == ColumnDataType.BOOLEAN],
            "all": columns
        }

    def _matches_rule(
        self,
        categorized: Dict[str, List[ColumnProfile]],
        rule: Dict,
        profile: TableProfile
    ) -> bool:
        """Check if available columns match a chart rule."""
        requires = rule.get("requires", {})

        # Check required column types
        for col_type, min_count in requires.items():
            available = categorized.get(col_type, [])
            if len(available) < min_count:
                return False

        # Check max dimensions
        if "max_dimensions" in rule:
            dim_count = len(categorized.get("categorical", [])) + len(categorized.get("temporal", []))
            if rule["max_dimensions"] == 0 and dim_count > 0:
                # KPI rule: only match if we have no good dimensions
                # But actually, we want KPI to match if we have numeric
                pass  # Allow KPI even with dimensions

        # Check max_distinct constraint
        if "max_distinct" in rule:
            cat_cols = (
                categorized.get("categorical_low", []) or
                categorized.get("categorical_medium", []) or
                categorized.get("categorical", [])
            )
            if cat_cols:
                # Use first categorical column, handle None
                distinct = cat_cols[0].distinct_count if cat_cols[0].distinct_count is not None else 50
                if distinct > rule["max_distinct"]:
                    return False

        # Check min_distinct constraint
        if "min_distinct" in rule:
            cat_cols = categorized.get("categorical", [])
            if cat_cols:
                distinct = cat_cols[0].distinct_count if cat_cols[0].distinct_count is not None else 50
                if distinct < rule["min_distinct"]:
                    return False

        # Check min_columns constraint
        if "min_columns" in rule:
            if len(profile.columns) < rule["min_columns"]:
                return False

        return True

    def _build_recommendation(
        self,
        rule: Dict,
        categorized: Dict[str, List[ColumnProfile]],
        profile: TableProfile
    ) -> Optional[ChartRecommendation]:
        """Build a complete chart recommendation with config."""
        chart_type = rule["type"]

        # Select columns for this chart
        dimension_col: Optional[ColumnProfile] = None
        measure_col: Optional[ColumnProfile] = None
        measure_col_2: Optional[ColumnProfile] = None

        if chart_type in ["bar", "horizontal-bar", "pie", "donut"]:
            # Need categorical + numeric
            dimension_col = self._select_best_dimension(categorized)
            measure_col = self._select_best_measure(categorized)

        elif chart_type in ["line", "area"]:
            # Need temporal + numeric
            dimension_col = self._select_temporal(categorized)
            measure_col = self._select_best_measure(categorized)

        elif chart_type == "scatter":
            # Need 2 numeric columns
            numerics = categorized.get("numeric", [])
            if len(numerics) >= 2:
                measure_col = numerics[0]
                measure_col_2 = numerics[1]

        elif chart_type == "kpi":
            # Need 1 numeric column
            measure_col = self._select_best_measure(categorized)

        elif chart_type == "table":
            # Use all columns
            pass

        # Validate we have required columns
        if chart_type not in ["table", "kpi"] and not dimension_col:
            return None
        if chart_type not in ["table"] and not measure_col:
            return None

        # Build configurations
        dimensions = []
        measures = []

        if dimension_col:
            dimensions.append(DimensionConfig(
                column=dimension_col.name,
                alias=self._humanize(dimension_col.name)
            ))

        if measure_col:
            aggregation = self._suggest_aggregation(measure_col)
            measures.append(MeasureConfig(
                column=measure_col.name,
                aggregation=aggregation,
                alias=f"{aggregation.title()} of {self._humanize(measure_col.name)}"
            ))

        if measure_col_2:
            measures.append(MeasureConfig(
                column=measure_col_2.name,
                aggregation="sum",
                alias=self._humanize(measure_col_2.name)
            ))

        # Generate title
        title = self._generate_title(chart_type, dimension_col, measure_col, profile)

        # Build ECharts config
        chart_config = self._build_echarts_config(
            chart_type, dimensions, measures, title, profile
        )

        # Build query config
        query_config = self._build_query_config(
            profile, dimensions, measures, chart_type
        )

        return ChartRecommendation(
            id=str(uuid.uuid4()),
            chart_type=chart_type,
            confidence=rule["confidence"],
            reason=rule["reason"],
            title=title,
            description=f"Automatically generated {rule['name'].lower()}",
            dimensions=dimensions,
            measures=measures,
            chart_config=chart_config,
            query_config=query_config
        )

    def _select_best_dimension(
        self,
        categorized: Dict[str, List[ColumnProfile]]
    ) -> Optional[ColumnProfile]:
        """Select the best categorical column for dimension."""
        # Prefer low cardinality, then medium
        candidates = (
            categorized.get("categorical_low", []) +
            categorized.get("categorical_medium", []) +
            categorized.get("boolean", [])
        )
        if candidates:
            # Sort by cardinality (prefer lower), handle None values
            return sorted(candidates, key=lambda c: c.distinct_count if c.distinct_count is not None else 999999)[0]
        return None

    def _select_temporal(
        self,
        categorized: Dict[str, List[ColumnProfile]]
    ) -> Optional[ColumnProfile]:
        """Select the best temporal column."""
        temporals = categorized.get("temporal", [])
        if temporals:
            # Prefer columns with 'date' or 'created' in name
            for col in temporals:
                if 'date' in col.name.lower() or 'created' in col.name.lower():
                    return col
            return temporals[0]
        return None

    def _select_best_measure(
        self,
        categorized: Dict[str, List[ColumnProfile]]
    ) -> Optional[ColumnProfile]:
        """Select the best numeric column for measure."""
        numerics = categorized.get("numeric", [])
        if numerics:
            # Prefer columns with value-like names
            value_keywords = ['amount', 'total', 'price', 'revenue', 'sales', 'cost', 'value', 'quantity', 'count']
            for col in numerics:
                if any(kw in col.name.lower() for kw in value_keywords):
                    return col
            return numerics[0]
        return None

    def _suggest_aggregation(self, column: ColumnProfile) -> str:
        """Suggest aggregation function based on column name."""
        name_lower = column.name.lower()

        # Count-like columns
        if any(kw in name_lower for kw in ['count', 'quantity', 'qty', 'num']):
            return 'sum'

        # Average-like columns
        if any(kw in name_lower for kw in ['avg', 'average', 'rate', 'percent', 'ratio']):
            return 'avg'

        # Sum for value columns
        if any(kw in name_lower for kw in ['amount', 'total', 'price', 'revenue', 'sales', 'cost', 'value']):
            return 'sum'

        # Default to sum
        return 'sum'

    def _generate_title(
        self,
        chart_type: str,
        dimension: Optional[ColumnProfile],
        measure: Optional[ColumnProfile],
        profile: TableProfile
    ) -> str:
        """Generate a human-readable chart title."""
        if chart_type == "kpi" and measure:
            return f"Total {self._humanize(measure.name)}"

        if chart_type == "table":
            return f"{self._humanize(profile.table_name)} Data"

        if dimension and measure:
            return f"{self._humanize(measure.name)} by {self._humanize(dimension.name)}"

        if chart_type == "scatter" and measure:
            return f"{self._humanize(profile.table_name)} Correlation"

        return f"{self._humanize(profile.table_name)} Overview"

    def _humanize(self, name: str) -> str:
        """Convert column_name to Human Name."""
        # Replace underscores and hyphens with spaces
        result = name.replace("_", " ").replace("-", " ")
        # Title case
        result = result.title()
        # Handle common abbreviations
        result = result.replace(" Id", " ID").replace(" Url", " URL")
        return result

    def _build_echarts_config(
        self,
        chart_type: str,
        dimensions: List[DimensionConfig],
        measures: List[MeasureConfig],
        title: str,
        profile: TableProfile
    ) -> Dict[str, Any]:
        """Build ECharts option configuration."""

        # Base config
        config: Dict[str, Any] = {
            "title": {"text": title, "left": "center", "textStyle": {"fontSize": 14}},
            "tooltip": {},
            "color": self.COLORS
        }

        if chart_type == "bar":
            config.update({
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                "xAxis": {"type": "category", "data": []},
                "yAxis": {"type": "value"},
                "series": [{
                    "type": "bar",
                    "name": measures[0].alias if measures else "Value",
                    "data": [],
                    "itemStyle": {"borderRadius": [4, 4, 0, 0]}
                }]
            })

        elif chart_type == "horizontal-bar":
            config.update({
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                "xAxis": {"type": "value"},
                "yAxis": {"type": "category", "data": []},
                "series": [{
                    "type": "bar",
                    "name": measures[0].alias if measures else "Value",
                    "data": [],
                    "itemStyle": {"borderRadius": [0, 4, 4, 0]}
                }]
            })

        elif chart_type == "line":
            config.update({
                "tooltip": {"trigger": "axis"},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                "xAxis": {"type": "category", "data": [], "boundaryGap": False},
                "yAxis": {"type": "value"},
                "series": [{
                    "type": "line",
                    "name": measures[0].alias if measures else "Value",
                    "data": [],
                    "smooth": True,
                    "areaStyle": {"opacity": 0.1}
                }]
            })

        elif chart_type == "area":
            config.update({
                "tooltip": {"trigger": "axis"},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                "xAxis": {"type": "category", "data": [], "boundaryGap": False},
                "yAxis": {"type": "value"},
                "series": [{
                    "type": "line",
                    "name": measures[0].alias if measures else "Value",
                    "data": [],
                    "smooth": True,
                    "areaStyle": {"opacity": 0.7}
                }]
            })

        elif chart_type == "pie":
            config.update({
                "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
                "legend": {"orient": "vertical", "left": "left", "top": "middle"},
                "series": [{
                    "type": "pie",
                    "radius": "65%",
                    "center": ["60%", "50%"],
                    "data": [],
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)"
                        }
                    },
                    "label": {"formatter": "{b}: {d}%"}
                }]
            })

        elif chart_type == "donut":
            config.update({
                "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
                "legend": {"orient": "vertical", "left": "left", "top": "middle"},
                "series": [{
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "center": ["60%", "50%"],
                    "data": [],
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)"
                        }
                    },
                    "label": {"formatter": "{b}: {d}%"}
                }]
            })

        elif chart_type == "scatter":
            config.update({
                "tooltip": {"trigger": "item"},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                "xAxis": {
                    "type": "value",
                    "name": measures[0].alias if measures else "X",
                    "nameLocation": "middle",
                    "nameGap": 30
                },
                "yAxis": {
                    "type": "value",
                    "name": measures[1].alias if len(measures) > 1 else "Y",
                    "nameLocation": "middle",
                    "nameGap": 40
                },
                "series": [{
                    "type": "scatter",
                    "data": [],
                    "symbolSize": 10
                }]
            })

        elif chart_type == "kpi":
            # KPI is handled differently - not ECharts
            config = {
                "type": "kpi",
                "title": title,
                "value": 0,
                "format": "number",
                "prefix": "",
                "suffix": "",
                "trend": None,
                "trendLabel": "vs previous period"
            }

        elif chart_type == "table":
            # Table config
            config = {
                "type": "table",
                "title": title,
                "columns": [{"key": c.name, "label": self._humanize(c.name)} for c in profile.columns[:10]],
                "pageSize": 10
            }

        return config

    def _build_query_config(
        self,
        profile: TableProfile,
        dimensions: List[DimensionConfig],
        measures: List[MeasureConfig],
        chart_type: str
    ) -> Dict[str, Any]:
        """Build query configuration for data fetching."""
        config: Dict[str, Any] = {
            "schema": profile.schema_name,
            "table": profile.table_name,
            "dimensions": [d.model_dump() for d in dimensions],
            "measures": [m.model_dump() for m in measures],
            "filters": [],
            "order_by": [],
            "limit": 100 if chart_type != "table" else 1000
        }

        # Add sorting based on chart type - use alias names for aggregated queries
        if chart_type in ["line", "area"] and dimensions:
            config["order_by"] = [{"column": dimensions[0].alias, "direction": "asc"}]
        elif chart_type in ["bar", "horizontal-bar"] and measures:
            config["order_by"] = [{"column": measures[0].alias, "direction": "desc"}]

        return config


# Singleton instance
chart_recommender = ChartRecommender()
