// Connection Types
export type ConnectionType =
  | 'postgresql'
  | 'mysql'
  | 'bigquery'
  | 'snowflake'
  | 'redshift'
  | 'clickhouse'
  | 'mongodb'
  | 'elasticsearch'
  | 'csv'
  | 'excel'
  | 'api'
  | 'cube'

export type ConnectionStatus = 'connected' | 'disconnected' | 'error' | 'syncing'

export interface Connection {
  id: string
  name: string
  type: ConnectionType
  host?: string
  port?: number
  database?: string
  status: ConnectionStatus
  tables_count: number
  last_sync?: string
  created_at: string
  updated_at: string
}

// Dataset Types
export type DataType = 'string' | 'number' | 'boolean' | 'date' | 'datetime' | 'json'

export type AggregationType = 'sum' | 'avg' | 'count' | 'min' | 'max' | 'count_distinct'

export interface Column {
  name: string
  type: DataType
  description?: string
  is_dimension: boolean
  is_measure: boolean
}

export interface Measure {
  id: string
  name: string
  expression: string
  aggregation: AggregationType
  format?: string
  description?: string
}

export interface Relationship {
  id: string
  from_table: string
  from_column: string
  to_table: string
  to_column: string
  type: 'one_to_one' | 'one_to_many' | 'many_to_many'
}

export interface Dataset {
  id: string
  name: string
  connection_id: string
  tables: string[]
  columns: Column[]
  measures: Measure[]
  relationships: Relationship[]
  created_at: string
  updated_at: string
}

// Chart Types
export type ChartType =
  | 'bar'
  | 'line'
  | 'area'
  | 'pie'
  | 'donut'
  | 'scatter'
  | 'bubble'
  | 'heatmap'
  | 'treemap'
  | 'sunburst'
  | 'radar'
  | 'funnel'
  | 'gauge'
  | 'sankey'
  | 'map'
  | 'table'
  | 'kpi'
  | 'candlestick'
  | 'boxplot'
  | 'waterfall'

export interface ChartConfig {
  type: ChartType
  dataset_id?: string
  dimensions: string[]
  measures: string[]
  filters?: Filter[]
  sort?: SortConfig[]
  limit?: number
}

export interface ChartStyle {
  title?: string
  subtitle?: string
  colors?: string[]
  show_legend?: boolean
  legend_position?: 'top' | 'bottom' | 'left' | 'right'
  show_labels?: boolean
  label_position?: string
  axis_config?: AxisConfig
}

export interface AxisConfig {
  x_axis_title?: string
  y_axis_title?: string
  x_axis_format?: string
  y_axis_format?: string
  y_axis_min?: number
  y_axis_max?: number
}

export interface Chart {
  id: string
  name: string
  type: ChartType
  config: ChartConfig
  style: ChartStyle
  echarts_option?: Record<string, unknown>
  created_at: string
  updated_at: string
}

// Dashboard Types
export type WidgetType = 'chart' | 'kpi' | 'table' | 'text' | 'filter' | 'image'

export type DashboardVisibility = 'private' | 'team' | 'organization' | 'public'

export interface WidgetPosition {
  x: number
  y: number
  w: number
  h: number
}

export interface Widget {
  id: string
  type: WidgetType
  title: string
  position: WidgetPosition
  config: Record<string, unknown>
  chart_id?: string
}

export interface Dashboard {
  id: string
  name: string
  description?: string
  visibility: DashboardVisibility
  widgets: Widget[]
  filters?: Filter[]
  refresh_interval?: number
  thumbnail_url?: string
  created_at: string
  updated_at: string
  created_by: string
}

// Query Types
export type QueryType = 'sql' | 'visual'

export interface Filter {
  column: string
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'not_in' | 'like' | 'between'
  value: unknown
}

export interface SortConfig {
  column: string
  direction: 'asc' | 'desc'
}

export interface QueryRequest {
  type: QueryType
  connection_id: string
  dataset_id?: string
  sql?: string
  visual_config?: {
    dimensions: string[]
    measures: string[]
    filters?: Filter[]
    sort?: SortConfig[]
    limit?: number
  }
}

export interface QueryResult {
  columns: Array<{ name: string; type: string }>
  rows: unknown[][]
  row_count: number
  execution_time_ms: number
}

// AI Types
export type InsightType = 'trend' | 'anomaly' | 'correlation' | 'distribution' | 'summary'

export interface Insight {
  type: InsightType
  title: string
  description: string
  confidence: number
  data?: Record<string, unknown>
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  chart?: Chart
  timestamp: Date
}
