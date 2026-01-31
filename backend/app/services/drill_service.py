"""
Drill Service

Handles drill-down and drillthrough operations for charts.
Provides query modification and data fetching for drill navigation.
"""

import logging
from typing import Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.drill import (
    DrillDirection,
    DrillType,
    DrillHierarchy,
    DrillPath,
    DrillRequest,
    DrillResponse,
    DrillthroughRequest,
    DrillthroughResponse,
    ChartDrillConfig,
    ChartDrillState,
    DrillHistoryEntry,
)

logger = logging.getLogger(__name__)


class DrillService:
    """Service for handling drill operations"""

    def __init__(self, db_type: str = "postgresql"):
        self.db_type = db_type

    def execute_drill(
        self,
        request: DrillRequest,
        hierarchy: DrillHierarchy,
        base_query: str,
        connection_params: dict[str, Any],
    ) -> DrillResponse:
        """
        Execute a drill operation and return updated data.

        Args:
            request: The drill request
            hierarchy: The hierarchy configuration
            base_query: The base query for the chart
            connection_params: Database connection parameters

        Returns:
            DrillResponse with updated path and data
        """
        current_path = request.current_path or DrillPath(
            hierarchy_id=hierarchy.id,
            current_level=0,
            filters={},
            breadcrumbs=[],
        )

        if request.direction == DrillDirection.DOWN:
            return self._drill_down(request, hierarchy, current_path, base_query, connection_params)
        else:
            return self._drill_up(request, hierarchy, current_path, base_query, connection_params)

    def _drill_down(
        self,
        request: DrillRequest,
        hierarchy: DrillHierarchy,
        current_path: DrillPath,
        base_query: str,
        connection_params: dict[str, Any],
    ) -> DrillResponse:
        """Execute drill-down operation"""
        current_level = current_path.current_level
        max_level = len(hierarchy.levels) - 1

        # Check if we can drill down further
        if current_level >= max_level:
            return DrillResponse(
                success=False,
                new_path=current_path,
                can_drill_down=False,
                can_drill_up=current_level > 0,
            )

        # Get current and next level info
        current_level_config = hierarchy.levels[current_level]
        next_level_config = hierarchy.levels[current_level + 1]

        # Update filters with clicked value
        new_filters = current_path.filters.copy()
        if request.clicked_value is not None:
            new_filters[current_level_config.column] = request.clicked_value

        # Update breadcrumbs
        new_breadcrumbs = current_path.breadcrumbs.copy()
        new_breadcrumbs.append({
            "level": current_level,
            "column": current_level_config.column,
            "label": current_level_config.label,
            "value": request.clicked_value,
        })

        # Build new path
        new_path = DrillPath(
            hierarchy_id=hierarchy.id,
            current_level=current_level + 1,
            filters=new_filters,
            breadcrumbs=new_breadcrumbs,
        )

        # Build drill query
        drill_query = self._build_drill_query(
            base_query=base_query,
            hierarchy=hierarchy,
            drill_path=new_path,
        )

        return DrillResponse(
            success=True,
            new_path=new_path,
            query=drill_query,
            can_drill_down=(current_level + 1) < max_level,
            can_drill_up=True,
        )

    def _drill_up(
        self,
        request: DrillRequest,
        hierarchy: DrillHierarchy,
        current_path: DrillPath,
        base_query: str,
        connection_params: dict[str, Any],
    ) -> DrillResponse:
        """Execute drill-up operation"""
        current_level = current_path.current_level

        # Check if we can drill up
        if current_level <= 0:
            return DrillResponse(
                success=False,
                new_path=current_path,
                can_drill_down=True,
                can_drill_up=False,
            )

        # Go up one level
        new_level = current_level - 1

        # Remove the last filter and breadcrumb
        new_filters = current_path.filters.copy()
        new_breadcrumbs = current_path.breadcrumbs.copy()

        if new_breadcrumbs:
            removed = new_breadcrumbs.pop()
            if removed["column"] in new_filters:
                del new_filters[removed["column"]]

        # Build new path
        new_path = DrillPath(
            hierarchy_id=hierarchy.id,
            current_level=new_level,
            filters=new_filters,
            breadcrumbs=new_breadcrumbs,
        )

        # Build drill query
        drill_query = self._build_drill_query(
            base_query=base_query,
            hierarchy=hierarchy,
            drill_path=new_path,
        )

        return DrillResponse(
            success=True,
            new_path=new_path,
            query=drill_query,
            can_drill_down=True,
            can_drill_up=new_level > 0,
        )

    def _build_drill_query(
        self,
        base_query: str,
        hierarchy: DrillHierarchy,
        drill_path: DrillPath,
    ) -> str:
        """
        Build a query for the current drill level.

        Modifies the base query to:
        1. Group by the current level column
        2. Apply filters from previous levels
        """
        current_level = drill_path.current_level
        level_config = hierarchy.levels[current_level]

        # Build WHERE clause from drill filters
        where_conditions = []
        for column, value in drill_path.filters.items():
            if isinstance(value, str):
                where_conditions.append(f"{column} = '{value}'")
            elif value is None:
                where_conditions.append(f"{column} IS NULL")
            else:
                where_conditions.append(f"{column} = {value}")

        where_clause = " AND ".join(where_conditions) if where_conditions else ""

        # Wrap base query and add drill modifications
        drill_query = f"""
        WITH base_data AS (
            {base_query}
        )
        SELECT
            {level_config.column},
            COUNT(*) as _count,
            SUM(CASE WHEN _measure IS NOT NULL THEN _measure ELSE 0 END) as _sum
        FROM base_data
        """

        if where_clause:
            drill_query += f"\nWHERE {where_clause}"

        drill_query += f"""
        GROUP BY {level_config.column}
        ORDER BY {level_config.column} {level_config.sort_order or 'ASC'}
        """

        return drill_query

    def execute_drillthrough(
        self,
        request: DrillthroughRequest,
        target_config: dict[str, Any],
    ) -> DrillthroughResponse:
        """
        Execute a drillthrough operation.

        Args:
            request: The drillthrough request
            target_config: Configuration for the drillthrough target

        Returns:
            DrillthroughResponse with navigation info
        """
        target_type = target_config.get("target_type", "page")
        field_mappings = target_config.get("field_mappings", [])

        # Build target filters from clicked data
        target_filters = {}

        for mapping in field_mappings:
            source_col = mapping.get("source_column")
            target_param = mapping.get("target_parameter")

            if source_col in request.clicked_data:
                target_filters[target_param] = request.clicked_data[source_col]

        # Include current dashboard filters if configured
        if target_config.get("pass_all_filters") and request.current_filters:
            for key, value in request.current_filters.items():
                if key not in target_filters:
                    target_filters[key] = value

        # Build target URL
        target_url = None
        if target_type == "url":
            base_url = target_config.get("target_url", "")
            # Append filters as query params
            if target_filters:
                params = "&".join([f"{k}={v}" for k, v in target_filters.items()])
                separator = "&" if "?" in base_url else "?"
                target_url = f"{base_url}{separator}{params}"
            else:
                target_url = base_url
        elif target_type == "page":
            target_id = target_config.get("target_id")
            target_url = f"/dashboard/{request.source_chart_id.split('-')[0]}?page={target_id}"
            if target_filters:
                params = "&".join([f"filter_{k}={v}" for k, v in target_filters.items()])
                target_url += f"&{params}"
        elif target_type == "report":
            target_id = target_config.get("target_id")
            target_url = f"/dashboard/{target_id}"
            if target_filters:
                params = "&".join([f"filter_{k}={v}" for k, v in target_filters.items()])
                target_url += f"?{params}"

        return DrillthroughResponse(
            success=True,
            target_type=target_type,
            target_url=target_url,
            target_filters=target_filters,
        )

    def get_drill_breadcrumbs(
        self,
        drill_path: DrillPath,
        hierarchy: DrillHierarchy,
    ) -> list[dict[str, Any]]:
        """
        Generate breadcrumb display data from drill path.

        Returns formatted breadcrumbs for UI display.
        """
        breadcrumbs = [
            {
                "level": 0,
                "label": "All",
                "value": None,
                "is_current": drill_path.current_level == 0 and not drill_path.breadcrumbs,
            }
        ]

        for i, crumb in enumerate(drill_path.breadcrumbs):
            level_config = hierarchy.levels[crumb["level"]]
            value_display = crumb["value"]

            # Apply format if specified
            if level_config.format and value_display is not None:
                try:
                    value_display = level_config.format.format(value=value_display)
                except Exception:
                    pass

            breadcrumbs.append({
                "level": crumb["level"] + 1,
                "label": f"{level_config.label}: {value_display}",
                "value": crumb["value"],
                "is_current": i == len(drill_path.breadcrumbs) - 1,
            })

        return breadcrumbs

    def create_hierarchy_from_columns(
        self,
        columns: list[dict[str, Any]],
        hierarchy_id: str,
        hierarchy_name: str,
    ) -> DrillHierarchy:
        """
        Create a drill hierarchy from a list of column definitions.

        Args:
            columns: List of column configs with name, label, etc.
            hierarchy_id: ID for the new hierarchy
            hierarchy_name: Display name for the hierarchy

        Returns:
            DrillHierarchy configuration
        """
        from app.schemas.drill import DrillHierarchyLevel

        levels = []
        for col in columns:
            level = DrillHierarchyLevel(
                column=col.get("name") or col.get("column"),
                label=col.get("label") or col.get("name") or col.get("column"),
                sort_order=col.get("sort_order", "asc"),
                format=col.get("format"),
            )
            levels.append(level)

        return DrillHierarchy(
            id=hierarchy_id,
            name=hierarchy_name,
            levels=levels,
            default_level=0,
        )

    def get_common_hierarchies(self) -> list[dict[str, Any]]:
        """
        Return common pre-built hierarchies for typical use cases.

        Returns list of hierarchy templates.
        """
        return [
            {
                "id": "time_hierarchy",
                "name": "Time",
                "levels": [
                    {"column": "year", "label": "Year"},
                    {"column": "quarter", "label": "Quarter"},
                    {"column": "month", "label": "Month"},
                    {"column": "week", "label": "Week"},
                    {"column": "day", "label": "Day"},
                ],
            },
            {
                "id": "geography_hierarchy",
                "name": "Geography",
                "levels": [
                    {"column": "country", "label": "Country"},
                    {"column": "region", "label": "Region"},
                    {"column": "state", "label": "State"},
                    {"column": "city", "label": "City"},
                ],
            },
            {
                "id": "product_hierarchy",
                "name": "Product",
                "levels": [
                    {"column": "category", "label": "Category"},
                    {"column": "subcategory", "label": "Subcategory"},
                    {"column": "product", "label": "Product"},
                ],
            },
            {
                "id": "org_hierarchy",
                "name": "Organization",
                "levels": [
                    {"column": "division", "label": "Division"},
                    {"column": "department", "label": "Department"},
                    {"column": "team", "label": "Team"},
                    {"column": "employee", "label": "Employee"},
                ],
            },
        ]


def get_drill_service(db_type: str = "postgresql") -> DrillService:
    """Factory function to get a drill service instance"""
    return DrillService(db_type=db_type)
