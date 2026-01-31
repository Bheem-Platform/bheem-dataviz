/**
 * Audit Log Types
 *
 * TypeScript types for audit logging and security alerts.
 */

// Enums

export type ActionCategory =
  | 'auth'
  | 'dashboard'
  | 'chart'
  | 'connection'
  | 'query'
  | 'data'
  | 'workspace'
  | 'admin'
  | 'system';

export type ActionType =
  | 'view'
  | 'create'
  | 'update'
  | 'delete'
  | 'export'
  | 'share'
  | 'execute'
  | 'login'
  | 'logout';

export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';

export type AlertStatus = 'open' | 'investigating' | 'resolved' | 'dismissed';

// Audit Log Types

export interface AuditLog {
  id: string;
  timestamp: string;
  user_id?: string;
  user_email?: string;
  user_name?: string;
  action: string;
  action_category?: ActionCategory;
  action_type?: ActionType;
  resource_type?: string;
  resource_id?: string;
  resource_name?: string;
  ip_address?: string;
  user_agent?: string;
  request_method?: string;
  request_path?: string;
  response_status?: number;
  duration_ms?: number;
  workspace_id?: string;
  success: number;
  error_message?: string;
  metadata: Record<string, unknown>;
}

export interface AuditLogFilter {
  user_id?: string;
  user_email?: string;
  action?: string;
  action_category?: ActionCategory;
  action_type?: ActionType;
  resource_type?: string;
  resource_id?: string;
  workspace_id?: string;
  ip_address?: string;
  success_only?: boolean;
  start_date?: string;
  end_date?: string;
}

export interface AuditLogSummary {
  total_events: number;
  successful_events: number;
  failed_events: number;
  unique_users: number;
  top_actions: Array<{ action: string; count: number }>;
  activity_by_hour: Array<{ hour: number; count: number }>;
  activity_by_category: Record<string, number>;
}

export interface AuditLogExport {
  format: 'csv' | 'json' | 'xlsx';
  filters?: AuditLogFilter;
  include_metadata?: boolean;
  max_records?: number;
}

// Security Alert Types

export interface SecurityAlert {
  id: string;
  created_at: string;
  resolved_at?: string;
  alert_type: string;
  severity: AlertSeverity;
  title: string;
  description?: string;
  user_id?: string;
  user_email?: string;
  ip_address?: string;
  related_audit_ids: string[];
  workspace_id?: string;
  status: AlertStatus;
  resolved_by?: string;
  resolution_notes?: string;
  metadata: Record<string, unknown>;
}

export interface SecurityAlertCreate {
  alert_type: string;
  severity: AlertSeverity;
  title: string;
  description?: string;
  user_id?: string;
  user_email?: string;
  ip_address?: string;
  related_audit_ids?: string[];
  workspace_id?: string;
  metadata?: Record<string, unknown>;
}

export interface SecurityAlertUpdate {
  status?: AlertStatus;
  resolution_notes?: string;
}

export interface SecurityAlertFilter {
  alert_type?: string;
  severity?: AlertSeverity;
  status?: AlertStatus;
  user_id?: string;
  workspace_id?: string;
  start_date?: string;
  end_date?: string;
}

// Activity Types

export interface ActivityTimelineEntry {
  timestamp: string;
  action: string;
  description: string;
  user_name?: string;
  user_email?: string;
  resource_type?: string;
  resource_name?: string;
  success: boolean;
  icon?: string;
  color?: string;
}

export interface UserActivitySummary {
  user_id: string;
  user_email?: string;
  user_name?: string;
  total_actions: number;
  last_active?: string;
  most_used_features: Array<{ feature: string; count: number }>;
  login_count: number;
  failed_login_count: number;
}

// Dashboard Stats

export interface AuditDashboardStats {
  total_events_today: number;
  total_events_week: number;
  active_users_today: number;
  failed_logins_today: number;
  open_alerts: number;
  critical_alerts: number;
  top_users: Array<{ user_email: string; action_count: number }>;
  recent_alerts: SecurityAlert[];
}

// Anomaly Detection

export interface AnomalyCheckResult {
  checked_at: string;
  anomalies_found: number;
  alerts_created: string[];
}

// Archive

export interface ArchiveResult {
  archived_count: number;
  days_kept: number;
  archived_at: string;
}

// Constants

export const ACTION_CATEGORY_LABELS: Record<ActionCategory, string> = {
  auth: 'Authentication',
  dashboard: 'Dashboard',
  chart: 'Chart',
  connection: 'Connection',
  query: 'Query',
  data: 'Data',
  workspace: 'Workspace',
  admin: 'Admin',
  system: 'System',
};

export const ACTION_TYPE_LABELS: Record<ActionType, string> = {
  view: 'View',
  create: 'Create',
  update: 'Update',
  delete: 'Delete',
  export: 'Export',
  share: 'Share',
  execute: 'Execute',
  login: 'Login',
  logout: 'Logout',
};

export const ALERT_SEVERITY_LABELS: Record<AlertSeverity, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
};

export const ALERT_SEVERITY_COLORS: Record<AlertSeverity, string> = {
  low: 'blue',
  medium: 'yellow',
  high: 'orange',
  critical: 'red',
};

export const ALERT_STATUS_LABELS: Record<AlertStatus, string> = {
  open: 'Open',
  investigating: 'Investigating',
  resolved: 'Resolved',
  dismissed: 'Dismissed',
};

export const ALERT_STATUS_COLORS: Record<AlertStatus, string> = {
  open: 'red',
  investigating: 'yellow',
  resolved: 'green',
  dismissed: 'gray',
};

export const ACTION_ICONS: Record<string, string> = {
  'auth.login': 'log-in',
  'auth.logout': 'log-out',
  'auth.login_failed': 'x-circle',
  'dashboard.view': 'eye',
  'dashboard.create': 'plus',
  'dashboard.update': 'edit',
  'dashboard.delete': 'trash',
  'dashboard.share': 'share',
  'chart.view': 'eye',
  'chart.create': 'plus',
  'chart.update': 'edit',
  'chart.delete': 'trash',
  'chart.export': 'download',
  'connection.create': 'database',
  'connection.test': 'refresh-cw',
  'query.execute': 'play',
  'data.export': 'download',
  'workspace.create': 'folder-plus',
  'workspace.member_add': 'user-plus',
  'workspace.member_remove': 'user-minus',
};

export const ACTION_COLORS: Record<string, string> = {
  'auth.login': 'green',
  'auth.logout': 'gray',
  'auth.login_failed': 'red',
  'dashboard.create': 'blue',
  'dashboard.update': 'yellow',
  'dashboard.delete': 'red',
  'chart.create': 'blue',
  'chart.delete': 'red',
  'chart.export': 'purple',
  'data.export': 'purple',
};

// Helper Functions

export function getActionIcon(action: string): string {
  return ACTION_ICONS[action] || 'activity';
}

export function getActionColor(action: string): string {
  return ACTION_COLORS[action] || 'gray';
}

export function getSeverityColor(severity: AlertSeverity): string {
  return ALERT_SEVERITY_COLORS[severity];
}

export function getStatusColor(status: AlertStatus): string {
  return ALERT_STATUS_COLORS[status];
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
}

export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

export function formatRelativeTime(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function isHighSeverity(severity: AlertSeverity): boolean {
  return severity === 'high' || severity === 'critical';
}

export function isOpenAlert(status: AlertStatus): boolean {
  return status === 'open' || status === 'investigating';
}
