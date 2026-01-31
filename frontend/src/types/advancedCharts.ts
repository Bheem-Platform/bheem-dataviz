/**
 * Advanced Charts Types
 *
 * TypeScript types for advanced visualization types.
 */

// Enums

export type AdvancedChartType =
  | 'waterfall'
  | 'funnel'
  | 'gantt'
  | 'treemap'
  | 'sankey'
  | 'radar'
  | 'bullet'
  | 'heatmap'
  | 'boxplot'
  | 'candlestick'
  | 'gauge'
  | 'sunburst'
  | 'parallel'
  | 'wordcloud';

export type WaterfallBarType = 'increase' | 'decrease' | 'total' | 'subtotal';

export type FunnelOrientation = 'vertical' | 'horizontal';

export type GanttTimeUnit = 'hour' | 'day' | 'week' | 'month' | 'quarter' | 'year';

// Base Configuration Types

export interface ChartColorConfig {
  primary: string;
  secondary: string;
  increase: string;
  decrease: string;
  total: string;
  neutral: string;
  palette: string[];
}

export interface ChartAxisConfig {
  show: boolean;
  title?: string;
  min?: number;
  max?: number;
  format?: string;
  tick_count?: number;
}

export interface ChartLegendConfig {
  show: boolean;
  position: 'top' | 'bottom' | 'left' | 'right';
  orientation: 'horizontal' | 'vertical';
}

export interface ChartTooltipConfig {
  show: boolean;
  format?: string;
  include_percentage: boolean;
}

// Waterfall Chart

export interface WaterfallDataPoint {
  category: string;
  value: number;
  bar_type: WaterfallBarType;
  label?: string;
  color?: string;
}

export interface WaterfallChartConfig {
  chart_type: 'waterfall';
  data: WaterfallDataPoint[];
  show_connectors: boolean;
  connector_color: string;
  show_labels: boolean;
  label_position: 'inside' | 'outside';
  category_axis: ChartAxisConfig;
  value_axis: ChartAxisConfig;
  colors: ChartColorConfig;
  legend: ChartLegendConfig;
  tooltip: ChartTooltipConfig;
}

export interface WaterfallChartRequest {
  connection_id: string;
  query?: string;
  category_column: string;
  value_column: string;
  type_column?: string;
  auto_total?: boolean;
  starting_value?: number;
  config?: Partial<WaterfallChartConfig>;
}

// Funnel Chart

export interface FunnelStage {
  name: string;
  value: number;
  percentage?: number;
  conversion_rate?: number;
  color?: string;
}

export interface FunnelChartConfig {
  chart_type: 'funnel';
  stages: FunnelStage[];
  orientation: FunnelOrientation;
  show_labels: boolean;
  show_percentages: boolean;
  show_conversion_rates: boolean;
  neck_width: number;
  neck_height: number;
  gap: number;
  colors: ChartColorConfig;
  legend: ChartLegendConfig;
  tooltip: ChartTooltipConfig;
}

export interface FunnelChartRequest {
  connection_id: string;
  query?: string;
  stage_column: string;
  value_column: string;
  stage_order?: string[];
  config?: Partial<FunnelChartConfig>;
}

// Gantt Chart

export interface GanttTask {
  id: string;
  name: string;
  start: string;
  end: string;
  progress: number;
  parent_id?: string;
  dependencies: string[];
  color?: string;
  assignee?: string;
  milestone: boolean;
  metadata: Record<string, unknown>;
}

export interface GanttChartConfig {
  chart_type: 'gantt';
  tasks: GanttTask[];
  time_unit: GanttTimeUnit;
  start_date?: string;
  end_date?: string;
  show_grid: boolean;
  show_today_line: boolean;
  show_dependencies: boolean;
  show_progress: boolean;
  row_height: number;
  group_by?: string;
  collapse_groups: boolean;
  colors: ChartColorConfig;
  legend: ChartLegendConfig;
  tooltip: ChartTooltipConfig;
}

export interface GanttChartRequest {
  connection_id: string;
  query?: string;
  id_column: string;
  name_column: string;
  start_column: string;
  end_column: string;
  progress_column?: string;
  parent_column?: string;
  dependencies_column?: string;
  config?: Partial<GanttChartConfig>;
}

// Treemap

export interface TreemapNode {
  id: string;
  name: string;
  value: number;
  parent_id?: string;
  color?: string;
  children: TreemapNode[];
  metadata: Record<string, unknown>;
}

export interface TreemapChartConfig {
  chart_type: 'treemap';
  root: TreemapNode;
  algorithm: 'squarify' | 'binary' | 'slice' | 'dice';
  padding: number;
  show_labels: boolean;
  label_min_size: number;
  show_values: boolean;
  show_breadcrumb: boolean;
  drilldown_enabled: boolean;
  color_by: 'value' | 'depth' | 'category';
  colors: ChartColorConfig;
  legend: ChartLegendConfig;
  tooltip: ChartTooltipConfig;
}

export interface TreemapChartRequest {
  connection_id: string;
  query?: string;
  id_column: string;
  name_column: string;
  value_column: string;
  parent_column?: string;
  color_column?: string;
  hierarchy_columns?: string[];
  config?: Partial<TreemapChartConfig>;
}

// Sankey Diagram

export interface SankeyNode {
  id: string;
  name: string;
  color?: string;
  column?: number;
}

export interface SankeyLink {
  source: string;
  target: string;
  value: number;
  color?: string;
  label?: string;
}

export interface SankeyChartConfig {
  chart_type: 'sankey';
  nodes: SankeyNode[];
  links: SankeyLink[];
  node_width: number;
  node_padding: number;
  iterations: number;
  show_labels: boolean;
  label_position: 'inside' | 'outside';
  show_values: boolean;
  color_by: 'source' | 'target' | 'gradient';
  colors: ChartColorConfig;
  legend: ChartLegendConfig;
  tooltip: ChartTooltipConfig;
}

export interface SankeyChartRequest {
  connection_id: string;
  query?: string;
  source_column: string;
  target_column: string;
  value_column: string;
  config?: Partial<SankeyChartConfig>;
}

// Radar Chart

export interface RadarAxis {
  name: string;
  max_value?: number;
  min_value: number;
}

export interface RadarSeries {
  name: string;
  values: number[];
  color?: string;
  fill_opacity: number;
}

export interface RadarChartConfig {
  chart_type: 'radar';
  axes: RadarAxis[];
  series: RadarSeries[];
  shape: 'polygon' | 'circle';
  levels: number;
  show_grid: boolean;
  show_labels: boolean;
  show_values: boolean;
  fill_area: boolean;
  colors: ChartColorConfig;
  legend: ChartLegendConfig;
  tooltip: ChartTooltipConfig;
}

export interface RadarChartRequest {
  connection_id: string;
  query?: string;
  axis_column: string;
  value_columns: string[];
  config?: Partial<RadarChartConfig>;
}

// Bullet Chart

export interface BulletRange {
  name: string;
  start: number;
  end: number;
  color: string;
}

export interface BulletChartData {
  title: string;
  subtitle?: string;
  actual: number;
  target?: number;
  ranges: BulletRange[];
  format?: string;
}

export interface BulletChartConfig {
  chart_type: 'bullet';
  data: BulletChartData[];
  orientation: 'horizontal' | 'vertical';
  show_target: boolean;
  target_marker: 'line' | 'diamond';
  show_labels: boolean;
  actual_color: string;
  target_color: string;
  range_colors: string[];
  legend: ChartLegendConfig;
  tooltip: ChartTooltipConfig;
}

export interface BulletChartRequest {
  connection_id: string;
  query?: string;
  title_column: string;
  actual_column: string;
  target_column?: string;
  range_columns?: string[];
  config?: Partial<BulletChartConfig>;
}

// Heatmap

export interface HeatmapCell {
  x: string;
  y: string;
  value: number;
  label?: string;
}

export interface HeatmapChartConfig {
  chart_type: 'heatmap';
  cells: HeatmapCell[];
  x_categories: string[];
  y_categories: string[];
  show_labels: boolean;
  show_grid: boolean;
  cell_padding: number;
  color_scale: 'sequential' | 'diverging';
  min_color: string;
  max_color: string;
  mid_color?: string;
  x_axis: ChartAxisConfig;
  y_axis: ChartAxisConfig;
  legend: ChartLegendConfig;
  tooltip: ChartTooltipConfig;
}

export interface HeatmapChartRequest {
  connection_id: string;
  query?: string;
  x_column: string;
  y_column: string;
  value_column: string;
  aggregation?: 'sum' | 'avg' | 'count' | 'min' | 'max';
  config?: Partial<HeatmapChartConfig>;
}

// Gauge Chart

export interface GaugeThreshold {
  value: number;
  color: string;
}

export interface GaugeChartConfig {
  chart_type: 'gauge';
  value: number;
  min_value: number;
  max_value: number;
  title?: string;
  subtitle?: string;
  show_value: boolean;
  value_format?: string;
  start_angle: number;
  end_angle: number;
  arc_width: number;
  thresholds: GaugeThreshold[];
  show_pointer: boolean;
  pointer_color: string;
}

export interface GaugeChartRequest {
  connection_id: string;
  query?: string;
  value_column: string;
  min_value?: number;
  max_value?: number;
  config?: Partial<GaugeChartConfig>;
}

// Box Plot

export interface BoxplotData {
  category: string;
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
  outliers: number[];
  mean?: number;
}

export interface BoxplotChartConfig {
  chart_type: 'boxplot';
  data: BoxplotData[];
  orientation: 'vertical' | 'horizontal';
  show_outliers: boolean;
  show_mean: boolean;
  box_width: number;
  box_color: string;
  median_color: string;
  outlier_color: string;
  category_axis: ChartAxisConfig;
  value_axis: ChartAxisConfig;
  legend: ChartLegendConfig;
  tooltip: ChartTooltipConfig;
}

export interface BoxplotChartRequest {
  connection_id: string;
  query?: string;
  category_column: string;
  value_column: string;
  config?: Partial<BoxplotChartConfig>;
}

// Response Types

export interface AdvancedChartResponse {
  chart_type: AdvancedChartType;
  config: Record<string, unknown>;
  data: Record<string, unknown>;
  render_options: Record<string, unknown>;
}

export interface ChartTypeInfo {
  type: AdvancedChartType;
  name: string;
  description: string;
  category: string;
  required_data: string[];
  optional_data: string[];
  best_for: string[];
  example_config: Record<string, unknown>;
}

export interface ChartSuggestion {
  type: AdvancedChartType;
  reason: string;
  confidence: number;
}

// Constants

export const CHART_TYPE_NAMES: Record<AdvancedChartType, string> = {
  waterfall: 'Waterfall Chart',
  funnel: 'Funnel Chart',
  gantt: 'Gantt Chart',
  treemap: 'Treemap',
  sankey: 'Sankey Diagram',
  radar: 'Radar Chart',
  bullet: 'Bullet Chart',
  heatmap: 'Heatmap',
  boxplot: 'Box Plot',
  candlestick: 'Candlestick Chart',
  gauge: 'Gauge Chart',
  sunburst: 'Sunburst Chart',
  parallel: 'Parallel Coordinates',
  wordcloud: 'Word Cloud',
};

export const CHART_TYPE_CATEGORIES: Record<string, AdvancedChartType[]> = {
  comparison: ['waterfall', 'radar', 'bullet'],
  flow: ['funnel', 'sankey'],
  hierarchy: ['treemap', 'sunburst'],
  timeline: ['gantt'],
  distribution: ['heatmap', 'boxplot'],
  kpi: ['gauge', 'bullet'],
  financial: ['candlestick', 'waterfall'],
};

export const CHART_TYPE_ICONS: Record<AdvancedChartType, string> = {
  waterfall: 'bar-chart-2',
  funnel: 'filter',
  gantt: 'calendar',
  treemap: 'grid',
  sankey: 'git-branch',
  radar: 'target',
  bullet: 'minus',
  heatmap: 'grid',
  boxplot: 'box',
  candlestick: 'trending-up',
  gauge: 'activity',
  sunburst: 'sun',
  parallel: 'align-justify',
  wordcloud: 'type',
};

// Helper Functions

export function getChartTypeName(type: AdvancedChartType): string {
  return CHART_TYPE_NAMES[type] || type;
}

export function getChartTypeIcon(type: AdvancedChartType): string {
  return CHART_TYPE_ICONS[type] || 'bar-chart';
}

export function getChartsByCategory(category: string): AdvancedChartType[] {
  return CHART_TYPE_CATEGORIES[category] || [];
}

export function formatChartValue(value: number, format?: string): string {
  if (!format) return value.toLocaleString();

  if (format.includes('%')) {
    return `${(value * 100).toFixed(1)}%`;
  }
  if (format.includes('$')) {
    return `$${value.toLocaleString()}`;
  }
  if (format.includes('K')) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  if (format.includes('M')) {
    return `${(value / 1000000).toFixed(1)}M`;
  }

  return value.toLocaleString();
}

export function getDefaultColorPalette(): string[] {
  return [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#ec4899', // pink
    '#06b6d4', // cyan
    '#84cc16', // lime
    '#f97316', // orange
    '#6366f1', // indigo
  ];
}

export function getSequentialColors(count: number, startColor = '#eff6ff', endColor = '#1d4ed8'): string[] {
  const colors: string[] = [];
  for (let i = 0; i < count; i++) {
    const ratio = i / (count - 1);
    colors.push(interpolateColor(startColor, endColor, ratio));
  }
  return colors;
}

function interpolateColor(color1: string, color2: string, ratio: number): string {
  const hex = (c: string) => parseInt(c.slice(1), 16);
  const r = (h: number) => (h >> 16) & 255;
  const g = (h: number) => (h >> 8) & 255;
  const b = (h: number) => h & 255;

  const h1 = hex(color1);
  const h2 = hex(color2);

  const rr = Math.round(r(h1) + (r(h2) - r(h1)) * ratio);
  const rg = Math.round(g(h1) + (g(h2) - g(h1)) * ratio);
  const rb = Math.round(b(h1) + (b(h2) - b(h1)) * ratio);

  return `#${((1 << 24) + (rr << 16) + (rg << 8) + rb).toString(16).slice(1)}`;
}
