/**
 * Performance Monitoring Types
 *
 * TypeScript types for system metrics, application metrics, database metrics,
 * real-time monitoring, and alerting.
 */

// Enums

export enum MetricType {
  COUNTER = 'counter',
  GAUGE = 'gauge',
  HISTOGRAM = 'histogram',
  SUMMARY = 'summary',
}

export enum MetricCategory {
  SYSTEM = 'system',
  APPLICATION = 'application',
  DATABASE = 'database',
  CACHE = 'cache',
  API = 'api',
  QUERY = 'query',
  JOB = 'job',
  CUSTOM = 'custom',
}

export enum AlertSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

export enum AlertStatus {
  ACTIVE = 'active',
  ACKNOWLEDGED = 'acknowledged',
  RESOLVED = 'resolved',
  SILENCED = 'silenced',
}

export enum ComparisonOperator {
  GREATER_THAN = 'gt',
  GREATER_THAN_OR_EQUAL = 'gte',
  LESS_THAN = 'lt',
  LESS_THAN_OR_EQUAL = 'lte',
  EQUAL = 'eq',
  NOT_EQUAL = 'ne',
}

export enum AggregationType {
  AVG = 'avg',
  SUM = 'sum',
  MIN = 'min',
  MAX = 'max',
  COUNT = 'count',
  P50 = 'p50',
  P90 = 'p90',
  P95 = 'p95',
  P99 = 'p99',
}

export enum TimeWindow {
  LAST_MINUTE = '1m',
  LAST_5_MINUTES = '5m',
  LAST_15_MINUTES = '15m',
  LAST_HOUR = '1h',
  LAST_6_HOURS = '6h',
  LAST_24_HOURS = '24h',
  LAST_7_DAYS = '7d',
  LAST_30_DAYS = '30d',
}

// Metric Types

export interface MetricPoint {
  timestamp: string;
  value: number;
  labels: Record<string, string>;
}

export interface MetricSeries {
  name: string;
  category: MetricCategory;
  type: MetricType;
  unit?: string | null;
  description?: string | null;
  labels: Record<string, string>;
  points: MetricPoint[];
}

export interface MetricDefinition {
  id: string;
  name: string;
  category: MetricCategory;
  type: MetricType;
  unit?: string | null;
  description?: string | null;
  labels: string[];
  enabled: boolean;
  retention_days: number;
}

export interface MetricValue {
  name: string;
  value: number;
  timestamp: string;
  labels: Record<string, string>;
}

export interface MetricQuery {
  metric_name: string;
  labels?: Record<string, string>;
  aggregation?: AggregationType;
  time_window?: TimeWindow;
  start_time?: string;
  end_time?: string;
  step_seconds?: number;
}

export interface MetricStatistics {
  metric_name: string;
  min: number;
  max: number;
  avg: number;
  sum: number;
  count: number;
  p50: number;
  p90: number;
  p95: number;
  p99: number;
  stddev: number;
  time_window: TimeWindow;
}

// System Metrics

export interface SystemMetrics {
  timestamp: string;
  cpu_percent: number;
  cpu_count: number;
  memory_total_mb: number;
  memory_used_mb: number;
  memory_percent: number;
  disk_total_gb: number;
  disk_used_gb: number;
  disk_percent: number;
  network_bytes_sent: number;
  network_bytes_recv: number;
  load_average_1m?: number | null;
  load_average_5m?: number | null;
  load_average_15m?: number | null;
  uptime_seconds: number;
}

export interface ProcessMetrics {
  timestamp: string;
  pid: number;
  cpu_percent: number;
  memory_mb: number;
  memory_percent: number;
  threads: number;
  open_files: number;
  connections: number;
}

// Request Metrics

export interface RequestMetrics {
  timestamp: string;
  total_requests: number;
  requests_per_second: number;
  avg_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
  error_count: number;
  error_rate: number;
  by_endpoint: Record<string, Record<string, unknown>>;
  by_status_code: Record<number, number>;
}

export interface EndpointMetrics {
  endpoint: string;
  method: string;
  request_count: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  error_count: number;
  error_rate: number;
  last_request_at?: string | null;
}

// Database Metrics

export interface DatabaseMetrics {
  timestamp: string;
  connection_id: string;
  connection_name: string;
  active_connections: number;
  max_connections: number;
  connection_utilization: number;
  queries_per_second: number;
  avg_query_time_ms: number;
  slow_queries: number;
  deadlocks: number;
  cache_hit_ratio: number;
  table_scans: number;
  index_scans: number;
  rows_read: number;
  rows_written: number;
}

export interface ConnectionPoolMetrics {
  connection_id: string;
  pool_size: number;
  active_connections: number;
  idle_connections: number;
  waiting_requests: number;
  checkout_timeout_count: number;
  avg_checkout_time_ms: number;
}

// Cache Metrics

export interface CacheMetrics {
  timestamp: string;
  total_keys: number;
  memory_used_mb: number;
  memory_limit_mb: number;
  hit_count: number;
  miss_count: number;
  hit_rate: number;
  evictions: number;
  expired_keys: number;
  operations_per_second: number;
  avg_key_size_bytes: number;
  avg_value_size_bytes: number;
}

// Alert Types

export interface AlertThreshold {
  metric_name: string;
  operator: ComparisonOperator;
  value: number;
  duration_seconds?: number;
  aggregation?: AggregationType;
  labels?: Record<string, string>;
}

export interface AlertRule {
  id: string;
  name: string;
  description?: string | null;
  severity: AlertSeverity;
  category: MetricCategory;
  thresholds: AlertThreshold[];
  notification_channels: string[];
  cooldown_seconds: number;
  enabled: boolean;
  last_triggered_at?: string | null;
  trigger_count: number;
  workspace_id?: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface AlertRuleCreate {
  name: string;
  description?: string;
  severity: AlertSeverity;
  category: MetricCategory;
  thresholds: AlertThreshold[];
  notification_channels?: string[];
  cooldown_seconds?: number;
  enabled?: boolean;
  workspace_id?: string;
  tags?: string[];
}

export interface AlertRuleUpdate {
  name?: string;
  description?: string;
  severity?: AlertSeverity;
  thresholds?: AlertThreshold[];
  notification_channels?: string[];
  cooldown_seconds?: number;
  enabled?: boolean;
  tags?: string[];
}

export interface Alert {
  id: string;
  rule_id: string;
  rule_name: string;
  severity: AlertSeverity;
  status: AlertStatus;
  message: string;
  metric_name: string;
  metric_value: number;
  threshold_value: number;
  labels: Record<string, string>;
  triggered_at: string;
  acknowledged_at?: string | null;
  acknowledged_by?: string | null;
  resolved_at?: string | null;
  silenced_until?: string | null;
  notification_sent: boolean;
  metadata: Record<string, unknown>;
}

export interface AlertAcknowledge {
  user_id: string;
  comment?: string;
}

export interface AlertSilence {
  duration_minutes: number;
  reason?: string;
}

export interface AlertStatistics {
  total_alerts: number;
  active_alerts: number;
  acknowledged_alerts: number;
  resolved_alerts: number;
  by_severity: Record<string, number>;
  by_category: Record<string, number>;
  avg_resolution_time_minutes: number;
  alert_rate_per_hour: number;
}

// Dashboard Types

export interface MonitoringDashboard {
  timestamp: string;
  system: SystemMetrics;
  process: ProcessMetrics;
  requests: RequestMetrics;
  cache: CacheMetrics;
  databases: DatabaseMetrics[];
  active_alerts: Alert[];
  health_status: string;
}

export interface HealthCheck {
  component: string;
  status: string;
  latency_ms?: number | null;
  message?: string | null;
  last_check: string;
  details: Record<string, unknown>;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  checks: HealthCheck[];
  uptime_seconds: number;
  version: string;
}

// Configuration Types

export interface MonitoringConfig {
  enabled: boolean;
  collection_interval_seconds: number;
  retention_days: number;
  enable_system_metrics: boolean;
  enable_application_metrics: boolean;
  enable_database_metrics: boolean;
  enable_cache_metrics: boolean;
  slow_request_threshold_ms: number;
  alert_cooldown_seconds: number;
}

export interface MonitoringConfigUpdate {
  enabled?: boolean;
  collection_interval_seconds?: number;
  retention_days?: number;
  enable_system_metrics?: boolean;
  enable_application_metrics?: boolean;
  enable_database_metrics?: boolean;
  enable_cache_metrics?: boolean;
  slow_request_threshold_ms?: number;
  alert_cooldown_seconds?: number;
}

// Response Types

export interface MetricSeriesListResponse {
  series: MetricSeries[];
  total: number;
}

export interface AlertRuleListResponse {
  rules: AlertRule[];
  total: number;
}

export interface AlertListResponse {
  alerts: Alert[];
  total: number;
}

export interface EndpointMetricsListResponse {
  endpoints: EndpointMetrics[];
  total: number;
}

export interface DatabaseMetricsListResponse {
  databases: DatabaseMetrics[];
  total: number;
}

// Constants

export const METRIC_CATEGORY_LABELS: Record<MetricCategory, string> = {
  [MetricCategory.SYSTEM]: 'System',
  [MetricCategory.APPLICATION]: 'Application',
  [MetricCategory.DATABASE]: 'Database',
  [MetricCategory.CACHE]: 'Cache',
  [MetricCategory.API]: 'API',
  [MetricCategory.QUERY]: 'Query',
  [MetricCategory.JOB]: 'Job',
  [MetricCategory.CUSTOM]: 'Custom',
};

export const ALERT_SEVERITY_LABELS: Record<AlertSeverity, string> = {
  [AlertSeverity.INFO]: 'Info',
  [AlertSeverity.WARNING]: 'Warning',
  [AlertSeverity.ERROR]: 'Error',
  [AlertSeverity.CRITICAL]: 'Critical',
};

export const ALERT_SEVERITY_COLORS: Record<AlertSeverity, string> = {
  [AlertSeverity.INFO]: 'blue',
  [AlertSeverity.WARNING]: 'yellow',
  [AlertSeverity.ERROR]: 'orange',
  [AlertSeverity.CRITICAL]: 'red',
};

export const ALERT_STATUS_LABELS: Record<AlertStatus, string> = {
  [AlertStatus.ACTIVE]: 'Active',
  [AlertStatus.ACKNOWLEDGED]: 'Acknowledged',
  [AlertStatus.RESOLVED]: 'Resolved',
  [AlertStatus.SILENCED]: 'Silenced',
};

export const ALERT_STATUS_COLORS: Record<AlertStatus, string> = {
  [AlertStatus.ACTIVE]: 'red',
  [AlertStatus.ACKNOWLEDGED]: 'yellow',
  [AlertStatus.RESOLVED]: 'green',
  [AlertStatus.SILENCED]: 'gray',
};

export const TIME_WINDOW_LABELS: Record<TimeWindow, string> = {
  [TimeWindow.LAST_MINUTE]: 'Last minute',
  [TimeWindow.LAST_5_MINUTES]: 'Last 5 minutes',
  [TimeWindow.LAST_15_MINUTES]: 'Last 15 minutes',
  [TimeWindow.LAST_HOUR]: 'Last hour',
  [TimeWindow.LAST_6_HOURS]: 'Last 6 hours',
  [TimeWindow.LAST_24_HOURS]: 'Last 24 hours',
  [TimeWindow.LAST_7_DAYS]: 'Last 7 days',
  [TimeWindow.LAST_30_DAYS]: 'Last 30 days',
};

export const COMPARISON_OPERATOR_LABELS: Record<ComparisonOperator, string> = {
  [ComparisonOperator.GREATER_THAN]: '>',
  [ComparisonOperator.GREATER_THAN_OR_EQUAL]: '>=',
  [ComparisonOperator.LESS_THAN]: '<',
  [ComparisonOperator.LESS_THAN_OR_EQUAL]: '<=',
  [ComparisonOperator.EQUAL]: '=',
  [ComparisonOperator.NOT_EQUAL]: '!=',
};

// Helper Functions

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatLatency(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(0)}us`;
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

export function getAlertSeverityColor(severity: AlertSeverity): string {
  return ALERT_SEVERITY_COLORS[severity] || 'gray';
}

export function getAlertStatusColor(status: AlertStatus): string {
  return ALERT_STATUS_COLORS[status] || 'gray';
}

export function getHealthStatusColor(status: string): string {
  switch (status) {
    case 'healthy':
      return 'green';
    case 'degraded':
      return 'yellow';
    case 'unhealthy':
      return 'red';
    default:
      return 'gray';
  }
}

export function isAlertActive(alert: Alert): boolean {
  return alert.status === AlertStatus.ACTIVE;
}

export function isAlertSilenced(alert: Alert): boolean {
  if (alert.status !== AlertStatus.SILENCED) return false;
  if (!alert.silenced_until) return false;
  return new Date(alert.silenced_until) > new Date();
}

export function getMetricTrend(
  current: number,
  previous: number
): 'up' | 'down' | 'stable' {
  const change = ((current - previous) / previous) * 100;
  if (Math.abs(change) < 1) return 'stable';
  return change > 0 ? 'up' : 'down';
}

export function calculatePercentile(values: number[], percentile: number): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const index = (percentile / 100) * (sorted.length - 1);
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) return sorted[lower];
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (index - lower);
}

// State Management

export interface PerformanceMonitoringState {
  dashboard: MonitoringDashboard | null;
  systemMetrics: SystemMetrics | null;
  requestMetrics: RequestMetrics | null;
  cacheMetrics: CacheMetrics | null;
  databaseMetrics: DatabaseMetrics[];
  alertRules: AlertRule[];
  alerts: Alert[];
  alertStats: AlertStatistics | null;
  healthStatus: HealthStatus | null;
  config: MonitoringConfig | null;
  selectedMetric: string | null;
  selectedTimeWindow: TimeWindow;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export function createInitialPerformanceMonitoringState(): PerformanceMonitoringState {
  return {
    dashboard: null,
    systemMetrics: null,
    requestMetrics: null,
    cacheMetrics: null,
    databaseMetrics: [],
    alertRules: [],
    alerts: [],
    alertStats: null,
    healthStatus: null,
    config: null,
    selectedMetric: null,
    selectedTimeWindow: TimeWindow.LAST_HOUR,
    isLoading: false,
    error: null,
    lastUpdated: null,
  };
}
