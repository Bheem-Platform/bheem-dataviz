"""
Drill-Down & Drillthrough Schemas

Provides schemas for drill operations including:
- Drill hierarchy configuration
- Drill-down state management
- Drillthrough page configuration
- Cross-report drillthrough
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class DrillDirection(str, Enum):
    """Direction of drill operation"""
    UP = "up"
    DOWN = "down"


class DrillType(str, Enum):
    """Type of drill operation"""
    DRILL_DOWN = "drill_down"  # Navigate down hierarchy
    DRILL_UP = "drill_up"      # Navigate up hierarchy
    DRILLTHROUGH = "drillthrough"  # Navigate to detail page/report
    EXPAND = "expand"          # Expand to show next level (keep current)
    COLLAPSE = "collapse"      # Collapse to hide level


class DrillHierarchyLevel(BaseModel):
    """Configuration for a single level in a drill hierarchy"""
    column: str = Field(..., description="Column name for this level")
    label: str = Field(..., description="Display label for this level")
    sort_order: Optional[str] = Field("asc", description="Sort order: asc or desc")
    format: Optional[str] = Field(None, description="Format string for values")


class DrillHierarchy(BaseModel):
    """Configuration for a drill hierarchy"""
    id: str = Field(..., description="Unique identifier for the hierarchy")
    name: str = Field(..., description="Display name for the hierarchy")
    levels: list[DrillHierarchyLevel] = Field(..., description="Ordered list of hierarchy levels")
    default_level: int = Field(0, description="Default level to display (0-indexed)")


class DrillPath(BaseModel):
    """Represents the current drill path/breadcrumb"""
    hierarchy_id: str = Field(..., description="ID of the hierarchy being drilled")
    current_level: int = Field(0, description="Current level in the hierarchy")
    filters: dict[str, Any] = Field(default_factory=dict, description="Filter values at each level")
    breadcrumbs: list[dict[str, Any]] = Field(default_factory=list, description="Breadcrumb trail")


class DrillRequest(BaseModel):
    """Request for a drill operation"""
    chart_id: str = Field(..., description="ID of the chart to drill")
    hierarchy_id: str = Field(..., description="ID of the hierarchy to use")
    direction: DrillDirection = Field(..., description="Direction of drill")
    clicked_value: Optional[Any] = Field(None, description="Value that was clicked")
    current_path: Optional[DrillPath] = Field(None, description="Current drill path")


class DrillResponse(BaseModel):
    """Response from a drill operation"""
    success: bool = Field(True, description="Whether the drill operation succeeded")
    new_path: DrillPath = Field(..., description="Updated drill path")
    data: Optional[list[dict[str, Any]]] = Field(None, description="New data for the chart")
    query: Optional[str] = Field(None, description="Query used to fetch data")
    can_drill_down: bool = Field(True, description="Whether further drill-down is possible")
    can_drill_up: bool = Field(False, description="Whether drill-up is possible")


# Drillthrough Configuration

class DrillthroughField(BaseModel):
    """Field mapping for drillthrough"""
    source_column: str = Field(..., description="Column from source chart")
    target_parameter: str = Field(..., description="Parameter name in target")
    pass_all_filters: bool = Field(False, description="Pass all current filters")


class DrillthroughTarget(BaseModel):
    """Configuration for a drillthrough target"""
    id: str = Field(..., description="Unique identifier for this target")
    name: str = Field(..., description="Display name for the target")
    target_type: str = Field("page", description="Type: page, report, or url")
    target_id: Optional[str] = Field(None, description="ID of target page/report")
    target_url: Optional[str] = Field(None, description="URL for external target")
    field_mappings: list[DrillthroughField] = Field(default_factory=list, description="Field mappings")
    open_in_new_tab: bool = Field(False, description="Open target in new tab")
    icon: Optional[str] = Field(None, description="Icon to display")


class DrillthroughConfig(BaseModel):
    """Drillthrough configuration for a chart"""
    enabled: bool = Field(True, description="Whether drillthrough is enabled")
    targets: list[DrillthroughTarget] = Field(default_factory=list, description="Available drillthrough targets")
    default_target_id: Optional[str] = Field(None, description="Default target when clicking")


class DrillthroughRequest(BaseModel):
    """Request to execute a drillthrough"""
    source_chart_id: str = Field(..., description="ID of the source chart")
    target_id: str = Field(..., description="ID of the drillthrough target")
    clicked_data: dict[str, Any] = Field(..., description="Data from clicked element")
    current_filters: Optional[dict[str, Any]] = Field(None, description="Current dashboard filters")


class DrillthroughResponse(BaseModel):
    """Response from drillthrough execution"""
    success: bool = Field(True, description="Whether drillthrough succeeded")
    target_type: str = Field(..., description="Type of target")
    target_url: Optional[str] = Field(None, description="URL to navigate to")
    target_filters: dict[str, Any] = Field(default_factory=dict, description="Filters to apply at target")
    error: Optional[str] = Field(None, description="Error message if failed")


# Chart Drill Configuration

class ChartDrillConfig(BaseModel):
    """Complete drill configuration for a chart"""
    drill_enabled: bool = Field(True, description="Enable drill functionality")
    hierarchies: list[DrillHierarchy] = Field(default_factory=list, description="Available hierarchies")
    default_hierarchy_id: Optional[str] = Field(None, description="Default hierarchy to use")
    drillthrough: Optional[DrillthroughConfig] = Field(None, description="Drillthrough configuration")
    show_drill_buttons: bool = Field(True, description="Show drill up/down buttons")
    show_breadcrumbs: bool = Field(True, description="Show drill breadcrumbs")
    allow_multi_level_expand: bool = Field(False, description="Allow expanding multiple levels")


# Drill State

class ChartDrillState(BaseModel):
    """Current drill state for a chart"""
    chart_id: str = Field(..., description="ID of the chart")
    active_hierarchy_id: Optional[str] = Field(None, description="Currently active hierarchy")
    current_path: Optional[DrillPath] = Field(None, description="Current drill path")
    expanded_items: list[str] = Field(default_factory=list, description="List of expanded item keys")
    last_drillthrough: Optional[dict[str, Any]] = Field(None, description="Last drillthrough context")


class DashboardDrillState(BaseModel):
    """Drill state for all charts in a dashboard"""
    dashboard_id: str = Field(..., description="ID of the dashboard")
    chart_states: dict[str, ChartDrillState] = Field(default_factory=dict, description="Drill state per chart")
    global_drill_path: Optional[DrillPath] = Field(None, description="Shared drill path for linked charts")
    sync_drill: bool = Field(False, description="Sync drill across linked charts")


# Drill History

class DrillHistoryEntry(BaseModel):
    """Entry in drill history"""
    timestamp: str = Field(..., description="When the drill occurred")
    chart_id: str = Field(..., description="Chart that was drilled")
    operation: DrillType = Field(..., description="Type of drill operation")
    from_level: int = Field(..., description="Level before drill")
    to_level: int = Field(..., description="Level after drill")
    clicked_value: Optional[Any] = Field(None, description="Value that triggered drill")


class DrillHistory(BaseModel):
    """Drill history for undo/redo functionality"""
    dashboard_id: str = Field(..., description="ID of the dashboard")
    entries: list[DrillHistoryEntry] = Field(default_factory=list, description="History entries")
    current_index: int = Field(-1, description="Current position in history")
    max_entries: int = Field(50, description="Maximum history entries to keep")
