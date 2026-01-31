/**
 * Quick Insights Types
 *
 * TypeScript types for automated data insights including
 * trend detection, outlier detection, and correlation analysis.
 */

// Enums

export type InsightType =
  | 'trend'
  | 'outlier'
  | 'correlation'
  | 'distribution'
  | 'comparison'
  | 'anomaly'
  | 'seasonality'
  | 'growth'
  | 'top_performer'
  | 'bottom_performer'
  | 'significant_change';

export type TrendDirection = 'increasing' | 'decreasing' | 'stable' | 'volatile';

export type InsightSeverity = 'high' | 'medium' | 'low';

export type CorrelationType = 'positive' | 'negative' | 'none';

export type OutlierType = 'above' | 'below' | 'both';

// Request Types

export interface InsightsRequest {
  connection_id: string;
  model_id?: string;
  table_name?: string;
  schema_name?: string;
  columns?: string[];
  date_column?: string;
  measure_columns?: string[];
  dimension_columns?: string[];
  limit_rows?: number;
  insight_types?: InsightType[];
}

export interface DatasetInsightsRequest {
  chart_id?: string;
  dataset_id?: string;
  data?: Record<string, unknown>[];
  columns?: string[];
  date_column?: string;
}

// Insight Detail Types

export interface TrendInsight {
  column: string;
  direction: TrendDirection;
  slope: number;
  r_squared: number;
  period: string;
  change_percent: number;
  start_value: number;
  end_value: number;
  data_points: number;
}

export interface OutlierInsight {
  column: string;
  outlier_type: OutlierType;
  values: Record<string, unknown>[];
  count: number;
  threshold_low?: number;
  threshold_high?: number;
  mean: number;
  std_dev: number;
  method: string;
}

export interface CorrelationInsight {
  column_1: string;
  column_2: string;
  correlation_type: CorrelationType;
  coefficient: number;
  p_value?: number;
  sample_size: number;
  interpretation: string;
}

export interface DistributionInsight {
  column: string;
  distribution_type: string;
  mean: number;
  median: number;
  mode?: number;
  std_dev: number;
  skewness: number;
  kurtosis: number;
  min_value: number;
  max_value: number;
  quartiles: number[];
}

export interface ComparisonInsight {
  measure: string;
  dimension: string;
  top_values: Record<string, unknown>[];
  bottom_values: Record<string, unknown>[];
  total: number;
  average: number;
  variance_coefficient: number;
}

export interface SeasonalityInsight {
  column: string;
  has_seasonality: boolean;
  period?: string;
  peak_periods: string[];
  trough_periods: string[];
  amplitude?: number;
}

export interface GrowthInsight {
  column: string;
  dimension_value?: string;
  period_1: string;
  period_2: string;
  value_1: number;
  value_2: number;
  absolute_change: number;
  percent_change: number;
  is_significant: boolean;
}

// Main Insight Type

export interface Insight {
  id: string;
  type: InsightType;
  severity: InsightSeverity;
  title: string;
  description: string;
  details: Record<string, unknown>;
  affected_columns: string[];
  confidence: number;
  generated_at: string;
  suggested_chart_type?: string;
  suggested_query?: string;
}

export interface InsightsResponse {
  insights: Insight[];
  summary: Record<string, unknown>;
  data_profile: Record<string, unknown>;
  execution_time_ms: number;
  rows_analyzed: number;
  columns_analyzed: number;
}

// Data Profile Types

export interface ColumnProfile {
  name: string;
  data_type: string;
  null_count: number;
  null_percent: number;
  unique_count: number;
  unique_percent: number;
  min_value?: number;
  max_value?: number;
  mean?: number;
  median?: number;
  std_dev?: number;
  min_length?: number;
  max_length?: number;
  avg_length?: number;
  top_values: Array<{
    value: string;
    count: number;
    percent: number;
  }>;
}

export interface DataProfile {
  row_count: number;
  column_count: number;
  columns: ColumnProfile[];
  memory_usage_bytes?: number;
  duplicate_rows: number;
  complete_rows: number;
}

// Trend Analysis Types

export interface TrendAnalysisRequest {
  connection_id: string;
  table_name: string;
  schema_name?: string;
  date_column: string;
  value_column: string;
  group_by?: string;
  granularity?: string;
  lookback_periods?: number;
}

export interface TrendAnalysisResponse {
  trend: TrendInsight;
  forecast: Record<string, unknown>[];
  seasonality?: SeasonalityInsight;
  data_points: Record<string, unknown>[];
}

// Outlier Detection Types

export interface OutlierDetectionRequest {
  connection_id: string;
  table_name: string;
  schema_name?: string;
  columns: string[];
  method?: 'iqr' | 'zscore' | 'isolation_forest';
  threshold?: number;
  zscore_threshold?: number;
}

export interface OutlierDetectionResponse {
  outliers: OutlierInsight[];
  total_outliers: number;
  outlier_percent: number;
}

// Correlation Analysis Types

export interface CorrelationAnalysisRequest {
  connection_id: string;
  table_name: string;
  schema_name?: string;
  columns: string[];
  method?: 'pearson' | 'spearman' | 'kendall';
  min_correlation?: number;
}

export interface CorrelationMatrix {
  columns: string[];
  matrix: number[][];
  significant_correlations: CorrelationInsight[];
}

// Constants

export const INSIGHT_TYPE_LABELS: Record<InsightType, string> = {
  trend: 'Trend',
  outlier: 'Outlier',
  correlation: 'Correlation',
  distribution: 'Distribution',
  comparison: 'Comparison',
  anomaly: 'Anomaly',
  seasonality: 'Seasonality',
  growth: 'Growth',
  top_performer: 'Top Performer',
  bottom_performer: 'Bottom Performer',
  significant_change: 'Significant Change',
};

export const INSIGHT_TYPE_ICONS: Record<InsightType, string> = {
  trend: 'trending-up',
  outlier: 'alert-triangle',
  correlation: 'link',
  distribution: 'bar-chart-2',
  comparison: 'git-compare',
  anomaly: 'zap',
  seasonality: 'calendar',
  growth: 'arrow-up-right',
  top_performer: 'award',
  bottom_performer: 'arrow-down',
  significant_change: 'activity',
};

export const SEVERITY_COLORS: Record<InsightSeverity, string> = {
  high: 'red',
  medium: 'yellow',
  low: 'blue',
};

export const TREND_DIRECTION_COLORS: Record<TrendDirection, string> = {
  increasing: 'green',
  decreasing: 'red',
  stable: 'gray',
  volatile: 'yellow',
};

export const CORRELATION_TYPE_COLORS: Record<CorrelationType, string> = {
  positive: 'green',
  negative: 'red',
  none: 'gray',
};

// Helper Functions

export function formatInsightSeverity(severity: InsightSeverity): string {
  return severity.charAt(0).toUpperCase() + severity.slice(1);
}

export function getInsightIcon(type: InsightType): string {
  return INSIGHT_TYPE_ICONS[type] || 'info';
}

export function getSeverityColor(severity: InsightSeverity): string {
  return SEVERITY_COLORS[severity];
}

export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

export function formatPercentChange(change: number): string {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(1)}%`;
}

export function sortInsightsBySeverity(insights: Insight[]): Insight[] {
  const severityOrder: Record<InsightSeverity, number> = {
    high: 0,
    medium: 1,
    low: 2,
  };

  return [...insights].sort((a, b) => {
    const severityDiff = severityOrder[a.severity] - severityOrder[b.severity];
    if (severityDiff !== 0) return severityDiff;
    return b.confidence - a.confidence;
  });
}

export function filterInsightsByType(
  insights: Insight[],
  types: InsightType[]
): Insight[] {
  return insights.filter((insight) => types.includes(insight.type));
}

export function groupInsightsByType(
  insights: Insight[]
): Record<InsightType, Insight[]> {
  const grouped: Record<string, Insight[]> = {};

  for (const insight of insights) {
    if (!grouped[insight.type]) {
      grouped[insight.type] = [];
    }
    grouped[insight.type].push(insight);
  }

  return grouped as Record<InsightType, Insight[]>;
}

export function getHighPriorityInsights(insights: Insight[]): Insight[] {
  return insights.filter((insight) => insight.severity === 'high');
}

export function createAnalysisRequest(
  data: Record<string, unknown>[],
  options?: {
    columns?: string[];
    dateColumn?: string;
    measureColumns?: string[];
    dimensionColumns?: string[];
    insightTypes?: InsightType[];
  }
): Record<string, unknown> {
  return {
    data,
    columns: options?.columns,
    date_column: options?.dateColumn,
    measure_columns: options?.measureColumns,
    dimension_columns: options?.dimensionColumns,
    insight_types: options?.insightTypes,
  };
}
