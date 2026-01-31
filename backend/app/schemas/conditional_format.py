"""
Conditional Formatting Schemas

Provides schemas for conditional formatting rules including:
- Color scales (gradient)
- Data bars
- Icon sets
- Rule-based formatting
- Top/Bottom N formatting
"""

from typing import Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class FormatType(str, Enum):
    """Type of conditional format"""
    COLOR_SCALE = "color_scale"       # Gradient based on value
    DATA_BAR = "data_bar"             # Bar visualization in cell
    ICON_SET = "icon_set"             # Icons based on thresholds
    RULES = "rules"                   # Custom rule-based
    TOP_BOTTOM = "top_bottom"         # Top/Bottom N values
    ABOVE_BELOW_AVG = "above_below_avg"  # Above/Below average
    DUPLICATE_UNIQUE = "duplicate_unique"  # Highlight duplicates


class ComparisonOperator(str, Enum):
    """Comparison operators for rules"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_BLANK = "is_blank"
    IS_NOT_BLANK = "is_not_blank"


class FormatTarget(str, Enum):
    """What to format"""
    CELL = "cell"                     # Format entire cell
    TEXT = "text"                     # Format text only
    BACKGROUND = "background"         # Format background only
    BORDER = "border"                 # Format border only


# Color definitions

class Color(BaseModel):
    """Color specification"""
    hex: Optional[str] = Field(None, description="Hex color code (e.g., #FF0000)")
    rgb: Optional[tuple[int, int, int]] = Field(None, description="RGB values")
    rgba: Optional[tuple[int, int, int, float]] = Field(None, description="RGBA with alpha")
    name: Optional[str] = Field(None, description="Named color (e.g., 'red')")

    def to_hex(self) -> str:
        """Convert to hex format"""
        if self.hex:
            return self.hex
        if self.rgb:
            return f"#{self.rgb[0]:02x}{self.rgb[1]:02x}{self.rgb[2]:02x}"
        if self.rgba:
            return f"#{int(self.rgba[0]):02x}{int(self.rgba[1]):02x}{int(self.rgba[2]):02x}"
        return "#000000"


class ColorStop(BaseModel):
    """A stop in a color gradient"""
    position: float = Field(..., ge=0, le=1, description="Position from 0 to 1")
    color: Color = Field(..., description="Color at this position")


# Format Styles

class TextStyle(BaseModel):
    """Text formatting style"""
    color: Optional[Color] = None
    font_weight: Optional[str] = Field(None, description="normal, bold")
    font_style: Optional[str] = Field(None, description="normal, italic")
    text_decoration: Optional[str] = Field(None, description="none, underline, line-through")
    font_size: Optional[str] = Field(None, description="Font size (e.g., '14px', '1.2em')")


class BackgroundStyle(BaseModel):
    """Background formatting style"""
    color: Optional[Color] = None
    gradient: Optional[list[ColorStop]] = None
    opacity: float = Field(1.0, ge=0, le=1)


class BorderStyle(BaseModel):
    """Border formatting style"""
    color: Optional[Color] = None
    width: str = Field("1px", description="Border width")
    style: str = Field("solid", description="solid, dashed, dotted")
    sides: list[str] = Field(["all"], description="all, top, right, bottom, left")


class FormatStyle(BaseModel):
    """Combined format style"""
    text: Optional[TextStyle] = None
    background: Optional[BackgroundStyle] = None
    border: Optional[BorderStyle] = None


# Color Scale Configuration

class ColorScaleConfig(BaseModel):
    """Configuration for color scale formatting"""
    min_color: Color = Field(..., description="Color for minimum value")
    mid_color: Optional[Color] = Field(None, description="Color for midpoint (3-color scale)")
    max_color: Color = Field(..., description="Color for maximum value")
    min_type: str = Field("min", description="min, number, percent, percentile")
    min_value: Optional[float] = Field(None, description="Value for min if type is number")
    mid_type: Optional[str] = Field(None, description="number, percent, percentile")
    mid_value: Optional[float] = Field(None, description="Value for mid")
    max_type: str = Field("max", description="max, number, percent, percentile")
    max_value: Optional[float] = Field(None, description="Value for max if type is number")


# Data Bar Configuration

class DataBarConfig(BaseModel):
    """Configuration for data bar formatting"""
    fill_color: Color = Field(default_factory=lambda: Color(hex="#638EC6"))
    border_color: Optional[Color] = None
    negative_fill_color: Optional[Color] = Field(default_factory=lambda: Color(hex="#FF0000"))
    negative_border_color: Optional[Color] = None
    bar_direction: str = Field("context", description="context, left_to_right, right_to_left")
    show_value: bool = Field(True, description="Show value alongside bar")
    min_length: float = Field(0, ge=0, le=100, description="Minimum bar length %")
    max_length: float = Field(100, ge=0, le=100, description="Maximum bar length %")
    axis_position: str = Field("auto", description="auto, midpoint, none")
    axis_color: Optional[Color] = None


# Icon Set Configuration

class IconSetConfig(BaseModel):
    """Configuration for icon set formatting"""
    icon_set: str = Field("traffic_light", description="Icon set name")
    reverse_order: bool = Field(False, description="Reverse icon order")
    show_icon_only: bool = Field(False, description="Hide value, show only icon")
    thresholds: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {"type": "percent", "value": 67, "icon_index": 0},
            {"type": "percent", "value": 33, "icon_index": 1},
        ],
        description="Threshold definitions"
    )


# Available icon sets
ICON_SETS = {
    "traffic_light": ["green_circle", "yellow_circle", "red_circle"],
    "traffic_light_rim": ["green_circle_rim", "yellow_circle_rim", "red_circle_rim"],
    "arrows_3": ["arrow_up", "arrow_right", "arrow_down"],
    "arrows_4": ["arrow_up", "arrow_up_right", "arrow_down_right", "arrow_down"],
    "arrows_5": ["arrow_up", "arrow_up_right", "arrow_right", "arrow_down_right", "arrow_down"],
    "triangles": ["triangle_up", "dash", "triangle_down"],
    "stars": ["star_full", "star_half", "star_empty"],
    "ratings": ["rating_5", "rating_4", "rating_3", "rating_2", "rating_1"],
    "flags": ["flag_green", "flag_yellow", "flag_red"],
    "checkmarks": ["check", "exclamation", "x"],
}


# Rule Configuration

class FormatRule(BaseModel):
    """A single conditional formatting rule"""
    id: str = Field(..., description="Unique rule ID")
    name: Optional[str] = Field(None, description="Rule name for display")
    priority: int = Field(0, description="Rule priority (lower = higher priority)")
    enabled: bool = Field(True, description="Whether rule is active")
    stop_if_true: bool = Field(False, description="Stop evaluating if this rule matches")

    # Condition
    operator: ComparisonOperator = Field(..., description="Comparison operator")
    value: Optional[Any] = Field(None, description="Value to compare against")
    value2: Optional[Any] = Field(None, description="Second value for between operators")
    formula: Optional[str] = Field(None, description="Custom formula for complex conditions")

    # Formatting
    style: FormatStyle = Field(..., description="Style to apply when rule matches")


class RulesConfig(BaseModel):
    """Configuration for rule-based formatting"""
    rules: list[FormatRule] = Field(default_factory=list, description="List of rules")
    apply_first_match_only: bool = Field(True, description="Stop after first matching rule")


# Top/Bottom Configuration

class TopBottomConfig(BaseModel):
    """Configuration for top/bottom formatting"""
    type: str = Field("top", description="top or bottom")
    count: int = Field(10, description="Number of items")
    is_percent: bool = Field(False, description="Count is percentage")
    style: FormatStyle = Field(..., description="Style to apply")


# Above/Below Average Configuration

class AboveBelowAvgConfig(BaseModel):
    """Configuration for above/below average formatting"""
    type: str = Field("above", description="above, below, above_or_equal, below_or_equal")
    std_dev: Optional[int] = Field(None, description="Number of standard deviations")
    above_style: FormatStyle = Field(..., description="Style for above average")
    below_style: Optional[FormatStyle] = Field(None, description="Style for below average")


# Main Conditional Format Configuration

class ConditionalFormat(BaseModel):
    """Complete conditional format configuration for a column/measure"""
    id: str = Field(..., description="Unique format ID")
    name: Optional[str] = Field(None, description="Format name for display")
    column: str = Field(..., description="Column to apply formatting to")
    type: FormatType = Field(..., description="Type of conditional format")
    enabled: bool = Field(True, description="Whether format is active")
    priority: int = Field(0, description="Priority among formats on same column")
    target: FormatTarget = Field(FormatTarget.CELL, description="What to format")

    # Type-specific configurations (only one should be set)
    color_scale: Optional[ColorScaleConfig] = None
    data_bar: Optional[DataBarConfig] = None
    icon_set: Optional[IconSetConfig] = None
    rules: Optional[RulesConfig] = None
    top_bottom: Optional[TopBottomConfig] = None
    above_below_avg: Optional[AboveBelowAvgConfig] = None


class ChartConditionalFormats(BaseModel):
    """All conditional formats for a chart"""
    chart_id: str = Field(..., description="Chart ID")
    formats: list[ConditionalFormat] = Field(default_factory=list, description="List of formats")


# Predefined format templates

class FormatTemplate(BaseModel):
    """Predefined format template"""
    id: str
    name: str
    description: str
    type: FormatType
    config: dict[str, Any]


DEFAULT_FORMAT_TEMPLATES = [
    FormatTemplate(
        id="green_yellow_red",
        name="Green-Yellow-Red Scale",
        description="Color gradient from green (high) to red (low)",
        type=FormatType.COLOR_SCALE,
        config={
            "min_color": {"hex": "#F8696B"},
            "mid_color": {"hex": "#FFEB84"},
            "max_color": {"hex": "#63BE7B"},
        },
    ),
    FormatTemplate(
        id="red_white_green",
        name="Red-White-Green Scale",
        description="Color gradient from red through white to green",
        type=FormatType.COLOR_SCALE,
        config={
            "min_color": {"hex": "#FF0000"},
            "mid_color": {"hex": "#FFFFFF"},
            "max_color": {"hex": "#00FF00"},
        },
    ),
    FormatTemplate(
        id="blue_data_bar",
        name="Blue Data Bar",
        description="Blue data bars showing relative values",
        type=FormatType.DATA_BAR,
        config={
            "fill_color": {"hex": "#638EC6"},
            "show_value": True,
        },
    ),
    FormatTemplate(
        id="traffic_lights",
        name="Traffic Light Icons",
        description="Green/Yellow/Red circles based on thresholds",
        type=FormatType.ICON_SET,
        config={
            "icon_set": "traffic_light",
            "thresholds": [
                {"type": "percent", "value": 67},
                {"type": "percent", "value": 33},
            ],
        },
    ),
    FormatTemplate(
        id="highlight_negative",
        name="Highlight Negative",
        description="Red background for negative values",
        type=FormatType.RULES,
        config={
            "rules": [
                {
                    "id": "neg",
                    "operator": "less_than",
                    "value": 0,
                    "style": {"background": {"color": {"hex": "#FFCCCC"}}},
                }
            ]
        },
    ),
]
