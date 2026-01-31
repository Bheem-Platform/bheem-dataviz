/**
 * Administration Dashboard Types
 *
 * TypeScript types for the admin dashboard, system health,
 * statistics, alerts, and administrative controls.
 */

// Enums

export enum SystemHealthStatus {
  HEALTHY = 'healthy',
  DEGRADED = 'degraded',
  UNHEALTHY = 'unhealthy',
  MAINTENANCE = 'maintenance',
}

export enum AlertLevel {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

export enum TrendDirection {
  UP = 'up',
  DOWN = 'down',
  STABLE = 'stable',
}

export enum TimeRange {
  TODAY = 'today',
  LAST_7_DAYS = 'last_7_days',
  LAST_30_DAYS = 'last_30_days',
  LAST_90_DAYS = 'last_90_days',
  THIS_MONTH = 'this_month',
  THIS_YEAR = 'this_year',
}

// Metric Interfaces

export interface MetricValue {
  name: string;
  value: number;
  previous_value?: number;
  unit?: string;
  trend: TrendDirection;
  change_percent: number;
}

export interface MetricTimeSeries {
  name: string;
  data_points: Array<{ timestamp: string; value: number }>;
  aggregation: string;
}

// System Health Interfaces

export interface ServiceHealth {
  name: string;
  status: SystemHealthStatus;
  latency_ms?: number;
  last_check_at: string;
  error_message?: string;
  details: Record<string, unknown>;
}

export interface SystemHealth {
  status: SystemHealthStatus;
  services: ServiceHealth[];
  uptime_percent: number;
  last_incident_at?: string;
  active_incidents: number;
}

export interface ResourceUsage {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  network_in_mbps: number;
  network_out_mbps: number;
  active_connections: number;
}

// Statistics Interfaces

export interface UserStats {
  total_users: number;
  active_users: number;
  new_users_today: number;
  new_users_this_week: number;
  new_users_this_month: number;
  mfa_enabled_percent: number;
  users_by_status: Record<string, number>;
  users_by_type: Record<string, number>;
  users_by_auth_provider: Record<string, number>;
  user_growth: Array<{ date: string; count: number }>;
}

export interface SessionStats {
  active_sessions: number;
  sessions_today: number;
  avg_session_duration_minutes: number;
  sessions_by_device: Record<string, number>;
  sessions_by_location: Record<string, number>;
  peak_concurrent_today: number;
}

export interface WorkspaceStats {
  total_workspaces: number;
  active_workspaces: number;
  new_workspaces_this_month: number;
  workspaces_by_plan: Record<string, number>;
  workspaces_by_status: Record<string, number>;
  avg_members_per_workspace: number;
  workspace_growth: Array<{ date: string; count: number }>;
}

export interface RevenueStats {
  mrr: number;
  arr: number;
  revenue_this_month: number;
  revenue_this_year: number;
  avg_revenue_per_user: number;
  churn_rate: number;
  revenue_by_plan: Record<string, number>;
  revenue_growth: Array<{ date: string; amount: number }>;
  currency: string;
}

export interface SubscriptionStats {
  total_subscriptions: number;
  active_subscriptions: number;
  trial_subscriptions: number;
  canceled_this_month: number;
  subscriptions_by_plan: Record<string, number>;
  subscriptions_by_interval: Record<string, number>;
  conversion_rate: number;
}

export interface PlatformUsageStats {
  total_dashboards: number;
  total_charts: number;
  total_connections: number;
  total_queries_today: number;
  total_api_calls_today: number;
  storage_used_gb: number;
  storage_total_gb: number;
  query_minutes_today: number;
  most_active_workspaces: Array<{
    workspace_id: string;
    name: string;
    activity_score: number;
  }>;
  popular_features: Array<{
    feature: string;
    usage_count: number;
  }>;
}

// Alert Interfaces

export interface SystemAlert {
  id: string;
  level: AlertLevel;
  title: string;
  message: string;
  source: string;
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  created_at: string;
  resolved_at?: string;
}

export interface AlertSummary {
  total_alerts: number;
  unacknowledged: number;
  by_level: Record<string, number>;
  recent_alerts: SystemAlert[];
}

export interface SystemAlertListResponse {
  alerts: SystemAlert[];
  total: number;
}

// Activity Interfaces

export interface AdminActivity {
  id: string;
  admin_id: string;
  admin_name: string;
  action: string;
  target_type: string;
  target_id?: string;
  target_name?: string;
  details: Record<string, unknown>;
  ip_address?: string;
  created_at: string;
}

export interface RecentActivity {
  user_activities: Array<{
    user: string;
    action: string;
    target: string;
    time: string;
  }>;
  admin_activities: AdminActivity[];
  system_events: Array<{
    event: string;
    message: string;
    time: string;
  }>;
}

export interface AdminActivityListResponse {
  activities: AdminActivity[];
  total: number;
}

// Configuration Interfaces

export interface SystemConfig {
  maintenance_mode: boolean;
  maintenance_message?: string;
  registration_enabled: boolean;
  public_signup_enabled: boolean;
  default_plan_id: string;
  max_workspaces_per_user: number;
  trial_days: number;
  session_timeout_hours: number;
  password_policy: Record<string, unknown>;
  email_verification_required: boolean;
  mfa_required_for_admins: boolean;
  allowed_email_domains: string[];
  blocked_email_domains: string[];
  rate_limits: Record<string, number>;
  feature_flags: Record<string, boolean>;
}

export interface SystemConfigUpdate {
  maintenance_mode?: boolean;
  maintenance_message?: string;
  registration_enabled?: boolean;
  public_signup_enabled?: boolean;
  default_plan_id?: string;
  max_workspaces_per_user?: number;
  trial_days?: number;
  session_timeout_hours?: number;
  password_policy?: Record<string, unknown>;
  email_verification_required?: boolean;
  mfa_required_for_admins?: boolean;
  allowed_email_domains?: string[];
  blocked_email_domains?: string[];
  rate_limits?: Record<string, number>;
  feature_flags?: Record<string, boolean>;
}

// Dashboard Interfaces

export interface DashboardWidget {
  id: string;
  type: string;
  title: string;
  size: string;
  position: number;
  config: Record<string, unknown>;
  refresh_interval_seconds: number;
}

export interface AdminDashboardConfig {
  widgets: DashboardWidget[];
  refresh_interval_seconds: number;
  theme: string;
}

export interface AdminDashboardSummary {
  system_health: SystemHealth;
  resource_usage: ResourceUsage;
  key_metrics: MetricValue[];
  user_stats: UserStats;
  workspace_stats: WorkspaceStats;
  revenue_stats?: RevenueStats;
  subscription_stats: SubscriptionStats;
  usage_stats: PlatformUsageStats;
  alert_summary: AlertSummary;
  recent_activity: RecentActivity;
}

// Report Interfaces

export interface AdminReport {
  id: string;
  name: string;
  type: string;
  format: string;
  time_range: TimeRange;
  generated_at: string;
  generated_by: string;
  download_url?: string;
  expires_at?: string;
  parameters: Record<string, unknown>;
}

export interface ReportSchedule {
  id: string;
  report_type: string;
  name: string;
  schedule: string;
  recipients: string[];
  format: string;
  time_range: TimeRange;
  enabled: boolean;
  last_run_at?: string;
  next_run_at?: string;
  created_at: string;
}

export interface AdminReportListResponse {
  reports: AdminReport[];
  total: number;
}

// Quick Action Interfaces

export interface QuickAction {
  id: string;
  name: string;
  description: string;
  icon: string;
  action_type: string;
  parameters: Record<string, unknown>;
  requires_confirmation: boolean;
  permission_required: string;
}

export interface QuickActionResult {
  success: boolean;
  message: string;
  details: Record<string, unknown>;
}

// Constants

export const HEALTH_STATUS_LABELS: Record<SystemHealthStatus, string> = {
  [SystemHealthStatus.HEALTHY]: 'Healthy',
  [SystemHealthStatus.DEGRADED]: 'Degraded',
  [SystemHealthStatus.UNHEALTHY]: 'Unhealthy',
  [SystemHealthStatus.MAINTENANCE]: 'Maintenance',
};

export const ALERT_LEVEL_LABELS: Record<AlertLevel, string> = {
  [AlertLevel.INFO]: 'Info',
  [AlertLevel.WARNING]: 'Warning',
  [AlertLevel.ERROR]: 'Error',
  [AlertLevel.CRITICAL]: 'Critical',
};

export const TIME_RANGE_LABELS: Record<TimeRange, string> = {
  [TimeRange.TODAY]: 'Today',
  [TimeRange.LAST_7_DAYS]: 'Last 7 Days',
  [TimeRange.LAST_30_DAYS]: 'Last 30 Days',
  [TimeRange.LAST_90_DAYS]: 'Last 90 Days',
  [TimeRange.THIS_MONTH]: 'This Month',
  [TimeRange.THIS_YEAR]: 'This Year',
};

export const TREND_ICONS: Record<TrendDirection, string> = {
  [TrendDirection.UP]: '↑',
  [TrendDirection.DOWN]: '↓',
  [TrendDirection.STABLE]: '→',
};

// Helper Functions

export function getHealthStatusColor(status: SystemHealthStatus): string {
  const colors: Record<SystemHealthStatus, string> = {
    [SystemHealthStatus.HEALTHY]: 'green',
    [SystemHealthStatus.DEGRADED]: 'yellow',
    [SystemHealthStatus.UNHEALTHY]: 'red',
    [SystemHealthStatus.MAINTENANCE]: 'blue',
  };
  return colors[status] || 'gray';
}

export function getAlertLevelColor(level: AlertLevel): string {
  const colors: Record<AlertLevel, string> = {
    [AlertLevel.INFO]: 'blue',
    [AlertLevel.WARNING]: 'yellow',
    [AlertLevel.ERROR]: 'orange',
    [AlertLevel.CRITICAL]: 'red',
  };
  return colors[level] || 'gray';
}

export function getAlertLevelIcon(level: AlertLevel): string {
  const icons: Record<AlertLevel, string> = {
    [AlertLevel.INFO]: 'ℹ️',
    [AlertLevel.WARNING]: '⚠️',
    [AlertLevel.ERROR]: '❌',
    [AlertLevel.CRITICAL]: '🚨',
  };
  return icons[level] || '📝';
}

export function getTrendColor(trend: TrendDirection, isPositiveGood: boolean = true): string {
  if (trend === TrendDirection.STABLE) return 'gray';
  const isUp = trend === TrendDirection.UP;
  if (isPositiveGood) {
    return isUp ? 'green' : 'red';
  }
  return isUp ? 'red' : 'green';
}

export function formatMetricValue(value: number, unit?: string): string {
  if (unit === 'USD' || unit === '$') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  }
  if (unit === '%') {
    return `${value.toFixed(1)}%`;
  }
  if (unit === 'ms') {
    return `${value.toFixed(0)}ms`;
  }
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  return value.toLocaleString();
}

export function formatChangePercent(percent: number): string {
  const sign = percent >= 0 ? '+' : '';
  return `${sign}${percent.toFixed(1)}%`;
}

export function getResourceUsageStatus(percent: number): 'ok' | 'warning' | 'critical' {
  if (percent >= 90) return 'critical';
  if (percent >= 75) return 'warning';
  return 'ok';
}

export function getResourceUsageColor(percent: number): string {
  const status = getResourceUsageStatus(percent);
  const colors = {
    ok: 'green',
    warning: 'yellow',
    critical: 'red',
  };
  return colors[status];
}

export function formatUptime(percent: number): string {
  return `${percent.toFixed(2)}%`;
}

export function calculateSLA(uptime: number): string {
  if (uptime >= 99.99) return 'Four 9s';
  if (uptime >= 99.9) return 'Three 9s';
  if (uptime >= 99) return 'Two 9s';
  return 'Below SLA';
}

export function getServiceIcon(serviceName: string): string {
  const icons: Record<string, string> = {
    database: '🗄️',
    cache: '⚡',
    api: '🌐',
    background_jobs: '⚙️',
    storage: '💾',
    auth: '🔐',
  };
  return icons[serviceName] || '📦';
}

export function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;

  return date.toLocaleDateString();
}
