"""
Conditional Format Service

Handles evaluation and application of conditional formatting rules.
"""

import logging
import colorsys
from typing import Any, Optional
import statistics

from app.schemas.conditional_format import (
    FormatType,
    ComparisonOperator,
    Color,
    ColorScaleConfig,
    DataBarConfig,
    IconSetConfig,
    RulesConfig,
    TopBottomConfig,
    AboveBelowAvgConfig,
    ConditionalFormat,
    FormatStyle,
    ICON_SETS,
)

logger = logging.getLogger(__name__)


class ConditionalFormatService:
    """Service for evaluating and applying conditional formats"""

    def evaluate_formats(
        self,
        data: list[dict[str, Any]],
        formats: list[ConditionalFormat],
    ) -> list[dict[str, Any]]:
        """
        Evaluate conditional formats for a dataset.

        Returns the data with formatting information attached.

        Args:
            data: List of data rows
            formats: List of conditional formats to apply

        Returns:
            Data with _formats key containing format results
        """
        if not data or not formats:
            return data

        # Sort formats by priority
        sorted_formats = sorted(
            [f for f in formats if f.enabled],
            key=lambda x: x.priority,
        )

        # Pre-calculate statistics for formats that need them
        stats = self._calculate_statistics(data, sorted_formats)

        # Apply formats to each row
        result = []
        for row_idx, row in enumerate(data):
            row_formats = {}

            for fmt in sorted_formats:
                column = fmt.column
                if column not in row:
                    continue

                value = row[column]
                format_result = self._evaluate_format(
                    fmt, value, row, row_idx, data, stats
                )

                if format_result:
                    if column not in row_formats:
                        row_formats[column] = []
                    row_formats[column].append(format_result)

            result.append({**row, "_formats": row_formats})

        return result

    def _calculate_statistics(
        self,
        data: list[dict[str, Any]],
        formats: list[ConditionalFormat],
    ) -> dict[str, dict[str, Any]]:
        """Calculate statistics needed for formatting"""
        stats = {}

        columns_needed = set()
        for fmt in formats:
            if fmt.type in [
                FormatType.COLOR_SCALE,
                FormatType.DATA_BAR,
                FormatType.TOP_BOTTOM,
                FormatType.ABOVE_BELOW_AVG,
            ]:
                columns_needed.add(fmt.column)

        for column in columns_needed:
            values = []
            for row in data:
                val = row.get(column)
                if val is not None and isinstance(val, (int, float)):
                    values.append(val)

            if values:
                stats[column] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                    "values": sorted(values),
                    "count": len(values),
                }

        return stats

    def _evaluate_format(
        self,
        fmt: ConditionalFormat,
        value: Any,
        row: dict[str, Any],
        row_idx: int,
        all_data: list[dict[str, Any]],
        stats: dict[str, dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """Evaluate a single format for a value"""
        try:
            if fmt.type == FormatType.COLOR_SCALE:
                return self._evaluate_color_scale(fmt.color_scale, value, stats.get(fmt.column))

            elif fmt.type == FormatType.DATA_BAR:
                return self._evaluate_data_bar(fmt.data_bar, value, stats.get(fmt.column))

            elif fmt.type == FormatType.ICON_SET:
                return self._evaluate_icon_set(fmt.icon_set, value, stats.get(fmt.column))

            elif fmt.type == FormatType.RULES:
                return self._evaluate_rules(fmt.rules, value, row)

            elif fmt.type == FormatType.TOP_BOTTOM:
                return self._evaluate_top_bottom(fmt.top_bottom, value, row_idx, stats.get(fmt.column))

            elif fmt.type == FormatType.ABOVE_BELOW_AVG:
                return self._evaluate_above_below_avg(fmt.above_below_avg, value, stats.get(fmt.column))

        except Exception as e:
            logger.warning(f"Error evaluating format {fmt.id}: {e}")

        return None

    def _evaluate_color_scale(
        self,
        config: ColorScaleConfig,
        value: Any,
        stats: Optional[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """Evaluate color scale format"""
        if not isinstance(value, (int, float)) or stats is None:
            return None

        # Determine min/max/mid values
        min_val = self._get_threshold_value(config.min_type, config.min_value, stats)
        max_val = self._get_threshold_value(config.max_type, config.max_value, stats)

        if min_val >= max_val:
            return None

        # Calculate position (0 to 1)
        position = (value - min_val) / (max_val - min_val)
        position = max(0, min(1, position))

        # Calculate color
        if config.mid_color:
            mid_val = self._get_threshold_value(config.mid_type or "percent", config.mid_value or 50, stats)
            mid_position = (mid_val - min_val) / (max_val - min_val)

            if position <= mid_position:
                # Interpolate between min and mid
                sub_position = position / mid_position if mid_position > 0 else 0
                color = self._interpolate_color(config.min_color, config.mid_color, sub_position)
            else:
                # Interpolate between mid and max
                sub_position = (position - mid_position) / (1 - mid_position) if mid_position < 1 else 1
                color = self._interpolate_color(config.mid_color, config.max_color, sub_position)
        else:
            # 2-color scale
            color = self._interpolate_color(config.min_color, config.max_color, position)

        return {
            "type": "color_scale",
            "background_color": color,
        }

    def _evaluate_data_bar(
        self,
        config: DataBarConfig,
        value: Any,
        stats: Optional[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """Evaluate data bar format"""
        if not isinstance(value, (int, float)) or stats is None:
            return None

        min_val = stats["min"]
        max_val = stats["max"]

        if min_val >= max_val:
            return None

        # Calculate bar width as percentage
        range_val = max_val - min_val
        if min_val < 0 and max_val > 0:
            # Handle negative values
            if value >= 0:
                width = (value / max_val) * 50
                is_negative = False
            else:
                width = (abs(value) / abs(min_val)) * 50
                is_negative = True
        else:
            width = ((value - min_val) / range_val) * 100
            is_negative = value < 0

        # Apply min/max length constraints
        width = max(config.min_length, min(config.max_length, width))

        return {
            "type": "data_bar",
            "width": width,
            "is_negative": is_negative,
            "fill_color": (config.negative_fill_color.to_hex() if is_negative and config.negative_fill_color
                          else config.fill_color.to_hex()),
            "show_value": config.show_value,
            "direction": config.bar_direction,
        }

    def _evaluate_icon_set(
        self,
        config: IconSetConfig,
        value: Any,
        stats: Optional[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """Evaluate icon set format"""
        if not isinstance(value, (int, float)) or stats is None:
            return None

        icons = ICON_SETS.get(config.icon_set, ICON_SETS["traffic_light"])
        if config.reverse_order:
            icons = list(reversed(icons))

        # Determine which icon to show based on thresholds
        icon_index = len(icons) - 1  # Default to last icon

        for threshold in config.thresholds:
            threshold_value = self._get_threshold_value(
                threshold.get("type", "percent"),
                threshold.get("value", 0),
                stats,
            )

            if value >= threshold_value:
                icon_index = threshold.get("icon_index", 0)
                break

        return {
            "type": "icon_set",
            "icon": icons[min(icon_index, len(icons) - 1)],
            "show_value": not config.show_icon_only,
        }

    def _evaluate_rules(
        self,
        config: RulesConfig,
        value: Any,
        row: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """Evaluate rule-based format"""
        for rule in sorted(config.rules, key=lambda r: r.priority):
            if not rule.enabled:
                continue

            if self._check_rule_condition(rule.operator, value, rule.value, rule.value2):
                return {
                    "type": "rules",
                    "rule_id": rule.id,
                    "style": rule.style.model_dump() if rule.style else None,
                }

                if rule.stop_if_true or config.apply_first_match_only:
                    break

        return None

    def _evaluate_top_bottom(
        self,
        config: TopBottomConfig,
        value: Any,
        row_idx: int,
        stats: Optional[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """Evaluate top/bottom format"""
        if not isinstance(value, (int, float)) or stats is None:
            return None

        values = stats["values"]
        count = config.count

        if config.is_percent:
            count = int(len(values) * (count / 100))

        count = max(1, count)

        if config.type == "top":
            threshold = values[-count] if count <= len(values) else values[0]
            matches = value >= threshold
        else:  # bottom
            threshold = values[count - 1] if count <= len(values) else values[-1]
            matches = value <= threshold

        if matches:
            return {
                "type": "top_bottom",
                "style": config.style.model_dump() if config.style else None,
            }

        return None

    def _evaluate_above_below_avg(
        self,
        config: AboveBelowAvgConfig,
        value: Any,
        stats: Optional[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """Evaluate above/below average format"""
        if not isinstance(value, (int, float)) or stats is None:
            return None

        mean = stats["mean"]
        stdev = stats["stdev"]

        if config.std_dev:
            threshold_above = mean + (config.std_dev * stdev)
            threshold_below = mean - (config.std_dev * stdev)
        else:
            threshold_above = mean
            threshold_below = mean

        is_above = False
        is_below = False

        if config.type == "above":
            is_above = value > threshold_above
        elif config.type == "above_or_equal":
            is_above = value >= threshold_above
        elif config.type == "below":
            is_below = value < threshold_below
        elif config.type == "below_or_equal":
            is_below = value <= threshold_below

        if is_above:
            return {
                "type": "above_below_avg",
                "position": "above",
                "style": config.above_style.model_dump() if config.above_style else None,
            }
        elif is_below and config.below_style:
            return {
                "type": "above_below_avg",
                "position": "below",
                "style": config.below_style.model_dump() if config.below_style else None,
            }

        return None

    def _get_threshold_value(
        self,
        threshold_type: str,
        threshold_value: Optional[float],
        stats: dict[str, Any],
    ) -> float:
        """Get actual value from threshold definition"""
        if threshold_type == "min":
            return stats["min"]
        elif threshold_type == "max":
            return stats["max"]
        elif threshold_type == "number":
            return threshold_value or 0
        elif threshold_type == "percent":
            range_val = stats["max"] - stats["min"]
            return stats["min"] + (range_val * (threshold_value or 0) / 100)
        elif threshold_type == "percentile":
            values = stats["values"]
            idx = int(len(values) * (threshold_value or 0) / 100)
            return values[min(idx, len(values) - 1)]
        return threshold_value or 0

    def _interpolate_color(self, color1: Color, color2: Color, position: float) -> str:
        """Interpolate between two colors"""
        hex1 = color1.to_hex()
        hex2 = color2.to_hex()

        # Parse hex colors
        r1 = int(hex1[1:3], 16)
        g1 = int(hex1[3:5], 16)
        b1 = int(hex1[5:7], 16)

        r2 = int(hex2[1:3], 16)
        g2 = int(hex2[3:5], 16)
        b2 = int(hex2[5:7], 16)

        # Interpolate
        r = int(r1 + (r2 - r1) * position)
        g = int(g1 + (g2 - g1) * position)
        b = int(b1 + (b2 - b1) * position)

        return f"#{r:02x}{g:02x}{b:02x}"

    def _check_rule_condition(
        self,
        operator: ComparisonOperator,
        value: Any,
        compare_value: Any,
        compare_value2: Any = None,
    ) -> bool:
        """Check if a rule condition is satisfied"""
        try:
            if operator == ComparisonOperator.EQUALS:
                return value == compare_value
            elif operator == ComparisonOperator.NOT_EQUALS:
                return value != compare_value
            elif operator == ComparisonOperator.GREATER_THAN:
                return value > compare_value
            elif operator == ComparisonOperator.GREATER_THAN_OR_EQUAL:
                return value >= compare_value
            elif operator == ComparisonOperator.LESS_THAN:
                return value < compare_value
            elif operator == ComparisonOperator.LESS_THAN_OR_EQUAL:
                return value <= compare_value
            elif operator == ComparisonOperator.BETWEEN:
                return compare_value <= value <= compare_value2
            elif operator == ComparisonOperator.NOT_BETWEEN:
                return not (compare_value <= value <= compare_value2)
            elif operator == ComparisonOperator.CONTAINS:
                return str(compare_value) in str(value)
            elif operator == ComparisonOperator.NOT_CONTAINS:
                return str(compare_value) not in str(value)
            elif operator == ComparisonOperator.STARTS_WITH:
                return str(value).startswith(str(compare_value))
            elif operator == ComparisonOperator.ENDS_WITH:
                return str(value).endswith(str(compare_value))
            elif operator == ComparisonOperator.IS_BLANK:
                return value is None or value == ""
            elif operator == ComparisonOperator.IS_NOT_BLANK:
                return value is not None and value != ""
        except (TypeError, ValueError):
            return False

        return False


def get_conditional_format_service() -> ConditionalFormatService:
    """Factory function to get service instance"""
    return ConditionalFormatService()
