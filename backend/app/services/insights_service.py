"""
Quick Insights Service

Provides automated data insights including trend detection,
outlier detection, correlation analysis, and distribution analysis.
"""

import logging
import uuid
from typing import Any, Optional
from datetime import datetime
import time
import statistics
from collections import Counter

import numpy as np
from scipy import stats as scipy_stats

from app.schemas.insights import (
    InsightType,
    TrendDirection,
    InsightSeverity,
    CorrelationType,
    OutlierType,
    InsightsRequest,
    DatasetInsightsRequest,
    TrendInsight,
    OutlierInsight,
    CorrelationInsight,
    DistributionInsight,
    ComparisonInsight,
    SeasonalityInsight,
    GrowthInsight,
    Insight,
    InsightsResponse,
    ColumnProfile,
    DataProfile,
    TrendAnalysisRequest,
    TrendAnalysisResponse,
    OutlierDetectionRequest,
    OutlierDetectionResponse,
    CorrelationAnalysisRequest,
    CorrelationMatrix,
    INSIGHT_TEMPLATES,
    CHART_SUGGESTIONS,
    SEVERITY_THRESHOLDS,
)

logger = logging.getLogger(__name__)


class InsightsService:
    """Service for generating automated data insights"""

    def __init__(self):
        pass

    # ========================================================================
    # MAIN INSIGHTS GENERATION
    # ========================================================================

    async def generate_insights(
        self,
        data: list[dict[str, Any]],
        columns: list[str] = None,
        date_column: Optional[str] = None,
        measure_columns: list[str] = None,
        dimension_columns: list[str] = None,
        insight_types: list[InsightType] = None,
    ) -> InsightsResponse:
        """
        Generate insights from data.

        Args:
            data: List of records as dictionaries
            columns: Columns to analyze (if None, analyze all)
            date_column: Date column for time-based analysis
            measure_columns: Numeric columns for analysis
            dimension_columns: Categorical columns for grouping

        Returns:
            InsightsResponse with all detected insights
        """
        start_time = time.time()
        insights = []

        if not data:
            return InsightsResponse(
                insights=[],
                summary={},
                data_profile={},
                execution_time_ms=0,
                rows_analyzed=0,
                columns_analyzed=0,
            )

        # Auto-detect column types if not specified
        if not columns:
            columns = list(data[0].keys())

        if not measure_columns:
            measure_columns = self._detect_numeric_columns(data, columns)

        if not dimension_columns:
            dimension_columns = self._detect_categorical_columns(data, columns)

        # Generate data profile
        profile = self._generate_data_profile(data, columns)

        # Default insight types
        if not insight_types:
            insight_types = list(InsightType)

        # Generate various insights
        if InsightType.TREND in insight_types and date_column:
            for col in measure_columns:
                trend_insights = self._detect_trends(data, date_column, col)
                insights.extend(trend_insights)

        if InsightType.OUTLIER in insight_types:
            for col in measure_columns:
                outlier_insights = self._detect_outliers(data, col)
                insights.extend(outlier_insights)

        if InsightType.CORRELATION in insight_types and len(measure_columns) >= 2:
            correlation_insights = self._analyze_correlations(data, measure_columns)
            insights.extend(correlation_insights)

        if InsightType.DISTRIBUTION in insight_types:
            for col in measure_columns:
                dist_insights = self._analyze_distribution(data, col)
                insights.extend(dist_insights)

        if InsightType.COMPARISON in insight_types:
            for measure in measure_columns[:3]:  # Limit to top 3 measures
                for dim in dimension_columns[:2]:  # Limit to top 2 dimensions
                    comp_insights = self._compare_by_dimension(data, measure, dim)
                    insights.extend(comp_insights)

        if InsightType.TOP_PERFORMER in insight_types or InsightType.BOTTOM_PERFORMER in insight_types:
            for measure in measure_columns[:3]:
                for dim in dimension_columns[:2]:
                    perf_insights = self._identify_performers(data, measure, dim)
                    insights.extend(perf_insights)

        # Sort by severity and confidence
        insights.sort(key=lambda x: (
            {"high": 0, "medium": 1, "low": 2}[x.severity.value],
            -x.confidence
        ))

        # Limit to top insights
        insights = insights[:20]

        execution_time = (time.time() - start_time) * 1000

        # Build summary
        summary = self._build_summary(insights, profile)

        return InsightsResponse(
            insights=insights,
            summary=summary,
            data_profile=profile.model_dump() if profile else {},
            execution_time_ms=execution_time,
            rows_analyzed=len(data),
            columns_analyzed=len(columns),
        )

    # ========================================================================
    # DATA PROFILING
    # ========================================================================

    def _generate_data_profile(
        self,
        data: list[dict[str, Any]],
        columns: list[str],
    ) -> DataProfile:
        """Generate a profile of the data"""
        column_profiles = []

        for col in columns:
            values = [row.get(col) for row in data]
            non_null_values = [v for v in values if v is not None]

            profile = ColumnProfile(
                name=col,
                data_type=self._infer_column_type(non_null_values),
                null_count=len(values) - len(non_null_values),
                null_percent=((len(values) - len(non_null_values)) / len(values) * 100) if values else 0,
                unique_count=len(set(str(v) for v in non_null_values)),
                unique_percent=(len(set(str(v) for v in non_null_values)) / len(non_null_values) * 100) if non_null_values else 0,
            )

            # Add numeric stats if applicable
            numeric_values = self._extract_numeric_values(non_null_values)
            if numeric_values:
                profile.min_value = min(numeric_values)
                profile.max_value = max(numeric_values)
                profile.mean = statistics.mean(numeric_values)
                profile.median = statistics.median(numeric_values)
                if len(numeric_values) > 1:
                    profile.std_dev = statistics.stdev(numeric_values)

            # Top values
            counter = Counter(str(v) for v in non_null_values)
            profile.top_values = [
                {"value": val, "count": cnt, "percent": cnt / len(non_null_values) * 100}
                for val, cnt in counter.most_common(5)
            ]

            column_profiles.append(profile)

        # Count complete rows (no nulls)
        complete_rows = sum(
            1 for row in data
            if all(row.get(col) is not None for col in columns)
        )

        return DataProfile(
            row_count=len(data),
            column_count=len(columns),
            columns=column_profiles,
            complete_rows=complete_rows,
        )

    # ========================================================================
    # TREND DETECTION
    # ========================================================================

    def _detect_trends(
        self,
        data: list[dict[str, Any]],
        date_column: str,
        value_column: str,
    ) -> list[Insight]:
        """Detect trends in time series data"""
        insights = []

        # Sort by date
        try:
            sorted_data = sorted(
                [d for d in data if d.get(date_column) and d.get(value_column) is not None],
                key=lambda x: x[date_column]
            )
        except (TypeError, ValueError):
            return insights

        if len(sorted_data) < 5:
            return insights

        # Extract values
        values = [float(d[value_column]) for d in sorted_data]
        x = list(range(len(values)))

        # Linear regression
        try:
            slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x, values)
            r_squared = r_value ** 2

            # Determine trend direction
            if r_squared < 0.3:
                direction = TrendDirection.VOLATILE
            elif abs(slope) < 0.01 * statistics.mean(values):
                direction = TrendDirection.STABLE
            elif slope > 0:
                direction = TrendDirection.INCREASING
            else:
                direction = TrendDirection.DECREASING

            # Calculate change
            start_value = values[0]
            end_value = values[-1]
            change_percent = ((end_value - start_value) / start_value * 100) if start_value != 0 else 0

            trend = TrendInsight(
                column=value_column,
                direction=direction,
                slope=slope,
                r_squared=r_squared,
                period=f"last {len(values)} data points",
                change_percent=change_percent,
                start_value=start_value,
                end_value=end_value,
                data_points=len(values),
            )

            # Determine severity
            abs_change = abs(change_percent)
            if abs_change >= SEVERITY_THRESHOLDS["trend_change_percent"]["high"]:
                severity = InsightSeverity.HIGH
            elif abs_change >= SEVERITY_THRESHOLDS["trend_change_percent"]["medium"]:
                severity = InsightSeverity.MEDIUM
            else:
                severity = InsightSeverity.LOW

            # Create insight
            template_key = direction.value
            title = INSIGHT_TEMPLATES[InsightType.TREND][template_key].format(
                column=value_column,
                change_percent=abs(change_percent),
                period=trend.period,
            )

            insight = Insight(
                id=str(uuid.uuid4()),
                type=InsightType.TREND,
                severity=severity,
                title=title,
                description=f"{value_column} changed from {start_value:.2f} to {end_value:.2f} ({change_percent:+.1f}%)",
                details=trend.model_dump(),
                affected_columns=[value_column, date_column],
                confidence=min(r_squared + 0.2, 1.0),
                suggested_chart_type=CHART_SUGGESTIONS[InsightType.TREND],
            )
            insights.append(insight)

        except Exception as e:
            logger.error(f"Error detecting trends: {e}")

        return insights

    # ========================================================================
    # OUTLIER DETECTION
    # ========================================================================

    def _detect_outliers(
        self,
        data: list[dict[str, Any]],
        column: str,
        method: str = "iqr",
        threshold: float = 1.5,
    ) -> list[Insight]:
        """Detect outliers in a column"""
        insights = []

        # Extract numeric values
        values_with_idx = [
            (i, float(d[column]))
            for i, d in enumerate(data)
            if d.get(column) is not None and self._is_numeric(d[column])
        ]

        if len(values_with_idx) < 10:
            return insights

        values = [v for _, v in values_with_idx]
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        outlier_indices = []

        if method == "iqr":
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            for idx, val in values_with_idx:
                if val < lower_bound or val > upper_bound:
                    outlier_indices.append((idx, val, "below" if val < lower_bound else "above"))

        elif method == "zscore":
            if std_dev == 0:
                return insights

            for idx, val in values_with_idx:
                z = abs((val - mean) / std_dev)
                if z > threshold:
                    outlier_indices.append((idx, val, "below" if val < mean else "above"))

        if not outlier_indices:
            return insights

        # Categorize outliers
        above_outliers = [(idx, val) for idx, val, t in outlier_indices if t == "above"]
        below_outliers = [(idx, val) for idx, val, t in outlier_indices if t == "below"]

        if above_outliers and below_outliers:
            outlier_type = OutlierType.BOTH
        elif above_outliers:
            outlier_type = OutlierType.ABOVE
        else:
            outlier_type = OutlierType.BELOW

        outlier_values = [
            {**data[idx], "_outlier_value": val}
            for idx, val, _ in outlier_indices[:10]
        ]

        outlier = OutlierInsight(
            column=column,
            outlier_type=outlier_type,
            values=outlier_values,
            count=len(outlier_indices),
            threshold_low=lower_bound if method == "iqr" else mean - threshold * std_dev,
            threshold_high=upper_bound if method == "iqr" else mean + threshold * std_dev,
            mean=mean,
            std_dev=std_dev,
            method=method,
        )

        # Determine severity
        outlier_percent = len(outlier_indices) / len(values) * 100
        if outlier_percent >= SEVERITY_THRESHOLDS["outlier_percent"]["high"]:
            severity = InsightSeverity.HIGH
        elif outlier_percent >= SEVERITY_THRESHOLDS["outlier_percent"]["medium"]:
            severity = InsightSeverity.MEDIUM
        else:
            severity = InsightSeverity.LOW

        title = INSIGHT_TEMPLATES[InsightType.OUTLIER][outlier_type.value].format(
            count=len(outlier_indices),
            column=column,
        )

        insight = Insight(
            id=str(uuid.uuid4()),
            type=InsightType.OUTLIER,
            severity=severity,
            title=title,
            description=f"Detected {len(outlier_indices)} outliers ({outlier_percent:.1f}% of data) in {column}",
            details=outlier.model_dump(),
            affected_columns=[column],
            confidence=0.85,
            suggested_chart_type=CHART_SUGGESTIONS[InsightType.OUTLIER],
        )
        insights.append(insight)

        return insights

    # ========================================================================
    # CORRELATION ANALYSIS
    # ========================================================================

    def _analyze_correlations(
        self,
        data: list[dict[str, Any]],
        columns: list[str],
        min_correlation: float = 0.5,
    ) -> list[Insight]:
        """Analyze correlations between numeric columns"""
        insights = []

        # Build arrays for each column
        column_arrays = {}
        for col in columns:
            values = []
            for d in data:
                val = d.get(col)
                if self._is_numeric(val):
                    values.append(float(val))
                else:
                    values.append(None)
            column_arrays[col] = values

        # Calculate correlations for each pair
        for i, col1 in enumerate(columns):
            for col2 in columns[i + 1:]:
                # Get paired values (both non-null)
                pairs = [
                    (column_arrays[col1][j], column_arrays[col2][j])
                    for j in range(len(data))
                    if column_arrays[col1][j] is not None and column_arrays[col2][j] is not None
                ]

                if len(pairs) < 10:
                    continue

                vals1, vals2 = zip(*pairs)

                try:
                    corr, p_value = scipy_stats.pearsonr(vals1, vals2)

                    if abs(corr) >= min_correlation:
                        if corr > 0:
                            corr_type = CorrelationType.POSITIVE
                        else:
                            corr_type = CorrelationType.NEGATIVE

                        correlation = CorrelationInsight(
                            column_1=col1,
                            column_2=col2,
                            correlation_type=corr_type,
                            coefficient=corr,
                            p_value=p_value,
                            sample_size=len(pairs),
                            interpretation=f"{'Strong' if abs(corr) > 0.7 else 'Moderate'} {corr_type.value} correlation",
                        )

                        # Determine severity
                        if abs(corr) >= SEVERITY_THRESHOLDS["correlation_coefficient"]["high"]:
                            severity = InsightSeverity.HIGH
                        elif abs(corr) >= SEVERITY_THRESHOLDS["correlation_coefficient"]["medium"]:
                            severity = InsightSeverity.MEDIUM
                        else:
                            severity = InsightSeverity.LOW

                        title = INSIGHT_TEMPLATES[InsightType.CORRELATION][corr_type.value].format(
                            column_1=col1,
                            column_2=col2,
                            coefficient=corr,
                        )

                        insight = Insight(
                            id=str(uuid.uuid4()),
                            type=InsightType.CORRELATION,
                            severity=severity,
                            title=title,
                            description=correlation.interpretation,
                            details=correlation.model_dump(),
                            affected_columns=[col1, col2],
                            confidence=1 - (p_value if p_value else 0.1),
                            suggested_chart_type=CHART_SUGGESTIONS[InsightType.CORRELATION],
                        )
                        insights.append(insight)

                except Exception as e:
                    logger.error(f"Error calculating correlation: {e}")

        return insights

    # ========================================================================
    # DISTRIBUTION ANALYSIS
    # ========================================================================

    def _analyze_distribution(
        self,
        data: list[dict[str, Any]],
        column: str,
    ) -> list[Insight]:
        """Analyze the distribution of a numeric column"""
        insights = []

        values = [
            float(d[column])
            for d in data
            if d.get(column) is not None and self._is_numeric(d[column])
        ]

        if len(values) < 20:
            return insights

        try:
            mean = statistics.mean(values)
            median = statistics.median(values)
            std_dev = statistics.stdev(values)
            skewness = scipy_stats.skew(values)
            kurtosis = scipy_stats.kurtosis(values)

            # Determine distribution type
            if abs(skewness) < 0.5:
                dist_type = "normal"
            elif skewness < -0.5:
                dist_type = "skewed_left"
            else:
                dist_type = "skewed_right"

            # Check for bimodality
            _, p_value = scipy_stats.normaltest(values)
            if p_value < 0.05 and kurtosis < -1:
                dist_type = "bimodal"

            distribution = DistributionInsight(
                column=column,
                distribution_type=dist_type,
                mean=mean,
                median=median,
                std_dev=std_dev,
                skewness=skewness,
                kurtosis=kurtosis,
                min_value=min(values),
                max_value=max(values),
                quartiles=[
                    np.percentile(values, 25),
                    np.percentile(values, 50),
                    np.percentile(values, 75),
                ],
            )

            # Only create insight if distribution is interesting
            if dist_type != "normal":
                severity = InsightSeverity.MEDIUM if abs(skewness) > 1 else InsightSeverity.LOW

                insight = Insight(
                    id=str(uuid.uuid4()),
                    type=InsightType.DISTRIBUTION,
                    severity=severity,
                    title=f"{column} has a {dist_type.replace('_', ' ')} distribution",
                    description=f"Mean: {mean:.2f}, Median: {median:.2f}, Skewness: {skewness:.2f}",
                    details=distribution.model_dump(),
                    affected_columns=[column],
                    confidence=0.8,
                    suggested_chart_type=CHART_SUGGESTIONS[InsightType.DISTRIBUTION],
                )
                insights.append(insight)

        except Exception as e:
            logger.error(f"Error analyzing distribution: {e}")

        return insights

    # ========================================================================
    # COMPARISON ANALYSIS
    # ========================================================================

    def _compare_by_dimension(
        self,
        data: list[dict[str, Any]],
        measure: str,
        dimension: str,
    ) -> list[Insight]:
        """Compare a measure across dimension values"""
        insights = []

        # Group by dimension
        groups = {}
        for d in data:
            dim_val = d.get(dimension)
            meas_val = d.get(measure)

            if dim_val is None or meas_val is None:
                continue

            if not self._is_numeric(meas_val):
                continue

            dim_key = str(dim_val)
            if dim_key not in groups:
                groups[dim_key] = []
            groups[dim_key].append(float(meas_val))

        if len(groups) < 2:
            return insights

        # Calculate aggregates
        group_totals = {k: sum(v) for k, v in groups.items()}
        total = sum(group_totals.values())
        average = total / len(group_totals)

        # Sort by total
        sorted_groups = sorted(group_totals.items(), key=lambda x: x[1], reverse=True)

        # Calculate variance
        values = list(group_totals.values())
        variance_coefficient = (statistics.stdev(values) / statistics.mean(values)) if len(values) > 1 and statistics.mean(values) != 0 else 0

        comparison = ComparisonInsight(
            measure=measure,
            dimension=dimension,
            top_values=[{"value": k, measure: v} for k, v in sorted_groups[:5]],
            bottom_values=[{"value": k, measure: v} for k, v in sorted_groups[-5:]],
            total=total,
            average=average,
            variance_coefficient=variance_coefficient,
        )

        # Only create insight if there's significant variance
        if variance_coefficient > 0.5:
            severity = InsightSeverity.HIGH if variance_coefficient > 1 else InsightSeverity.MEDIUM

            insight = Insight(
                id=str(uuid.uuid4()),
                type=InsightType.COMPARISON,
                severity=severity,
                title=f"High variance in {measure} across {dimension}",
                description=f"Top: {sorted_groups[0][0]} ({sorted_groups[0][1]:.2f}), Bottom: {sorted_groups[-1][0]} ({sorted_groups[-1][1]:.2f})",
                details=comparison.model_dump(),
                affected_columns=[measure, dimension],
                confidence=0.85,
                suggested_chart_type=CHART_SUGGESTIONS[InsightType.COMPARISON],
            )
            insights.append(insight)

        return insights

    # ========================================================================
    # PERFORMER IDENTIFICATION
    # ========================================================================

    def _identify_performers(
        self,
        data: list[dict[str, Any]],
        measure: str,
        dimension: str,
    ) -> list[Insight]:
        """Identify top and bottom performers"""
        insights = []

        # Group by dimension
        groups = {}
        for d in data:
            dim_val = d.get(dimension)
            meas_val = d.get(measure)

            if dim_val is None or meas_val is None:
                continue

            if not self._is_numeric(meas_val):
                continue

            dim_key = str(dim_val)
            if dim_key not in groups:
                groups[dim_key] = 0
            groups[dim_key] += float(meas_val)

        if len(groups) < 3:
            return insights

        sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
        total = sum(groups.values())

        # Top performer
        top_name, top_value = sorted_groups[0]
        top_percent = (top_value / total * 100) if total else 0

        if top_percent > 20:  # Only if significant
            insight = Insight(
                id=str(uuid.uuid4()),
                type=InsightType.TOP_PERFORMER,
                severity=InsightSeverity.MEDIUM,
                title=f"{top_name} leads in {measure}",
                description=f"{top_name} accounts for {top_percent:.1f}% of total {measure}",
                details={
                    "dimension": dimension,
                    "measure": measure,
                    "top_value": top_name,
                    "value": top_value,
                    "percent_of_total": top_percent,
                },
                affected_columns=[measure, dimension],
                confidence=0.9,
                suggested_chart_type="bar",
            )
            insights.append(insight)

        # Bottom performer
        bottom_name, bottom_value = sorted_groups[-1]
        bottom_percent = (bottom_value / total * 100) if total else 0

        if len(sorted_groups) >= 5 and bottom_percent < 5:
            insight = Insight(
                id=str(uuid.uuid4()),
                type=InsightType.BOTTOM_PERFORMER,
                severity=InsightSeverity.LOW,
                title=f"{bottom_name} underperforms in {measure}",
                description=f"{bottom_name} accounts for only {bottom_percent:.1f}% of total {measure}",
                details={
                    "dimension": dimension,
                    "measure": measure,
                    "bottom_value": bottom_name,
                    "value": bottom_value,
                    "percent_of_total": bottom_percent,
                },
                affected_columns=[measure, dimension],
                confidence=0.85,
                suggested_chart_type="bar",
            )
            insights.append(insight)

        return insights

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _detect_numeric_columns(
        self,
        data: list[dict[str, Any]],
        columns: list[str],
    ) -> list[str]:
        """Detect numeric columns"""
        numeric_cols = []
        for col in columns:
            sample_values = [d.get(col) for d in data[:100] if d.get(col) is not None]
            if sample_values and all(self._is_numeric(v) for v in sample_values):
                numeric_cols.append(col)
        return numeric_cols

    def _detect_categorical_columns(
        self,
        data: list[dict[str, Any]],
        columns: list[str],
    ) -> list[str]:
        """Detect categorical columns"""
        categorical_cols = []
        for col in columns:
            sample_values = [d.get(col) for d in data[:100] if d.get(col) is not None]
            if sample_values:
                # Check if mostly strings and has limited unique values
                unique_ratio = len(set(str(v) for v in sample_values)) / len(sample_values)
                if unique_ratio < 0.5 and not all(self._is_numeric(v) for v in sample_values):
                    categorical_cols.append(col)
        return categorical_cols

    def _is_numeric(self, value: Any) -> bool:
        """Check if a value is numeric"""
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False
        return False

    def _extract_numeric_values(self, values: list[Any]) -> list[float]:
        """Extract numeric values from a list"""
        numeric = []
        for v in values:
            if self._is_numeric(v):
                numeric.append(float(v))
        return numeric

    def _infer_column_type(self, values: list[Any]) -> str:
        """Infer the data type of a column"""
        if not values:
            return "unknown"

        sample = values[:100]

        # Check for boolean
        if all(isinstance(v, bool) for v in sample):
            return "boolean"

        # Check for integer
        if all(isinstance(v, int) for v in sample):
            return "integer"

        # Check for float
        if all(self._is_numeric(v) for v in sample):
            return "numeric"

        # Check for datetime
        if all(isinstance(v, (datetime,)) for v in sample):
            return "datetime"

        return "string"

    def _build_summary(
        self,
        insights: list[Insight],
        profile: DataProfile,
    ) -> dict[str, Any]:
        """Build a summary of the insights"""
        type_counts = {}
        severity_counts = {"high": 0, "medium": 0, "low": 0}

        for insight in insights:
            type_counts[insight.type.value] = type_counts.get(insight.type.value, 0) + 1
            severity_counts[insight.severity.value] += 1

        return {
            "total_insights": len(insights),
            "by_type": type_counts,
            "by_severity": severity_counts,
            "high_priority_count": severity_counts["high"],
            "data_quality_score": self._calculate_quality_score(profile),
        }

    def _calculate_quality_score(self, profile: DataProfile) -> float:
        """Calculate a data quality score (0-100)"""
        if not profile or not profile.columns:
            return 0

        scores = []

        for col in profile.columns:
            # Completeness score
            completeness = 100 - col.null_percent
            scores.append(completeness)

        return round(statistics.mean(scores) if scores else 0, 1)


def get_insights_service() -> InsightsService:
    """Factory function to get insights service instance"""
    return InsightsService()
