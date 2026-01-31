/**
 * Subscriptions and Alerts Types
 *
 * TypeScript types for data alerts and dashboard subscriptions.
 */

// Enums

export type NotificationChannel = 'email' | 'slack' | 'webhook' | 'in_app' | 'sms' | 'teams';

export type SubscriptionFrequency = 'immediate' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'custom';

export type AlertCondition =
  | 'gt'
  | 'lt'
  | 'eq'
  | 'ne'
  | 'gte'
  | 'lte'
  | 'between'
  | 'not_between'
  | 'increases_by'
  | 'decreases_by'
  | 'changes_by'
  | 'percent_change';

export type AlertSeverity = 'info' | 'warning' | 'critical';

export type AlertStatus = 'active' | 'paused' | 'triggered' | 'acknowledged' | 'resolved';

export type SubscriptionStatus = 'active' | 'paused' | 'cancelled';

// Notification Configuration

export interface EmailConfig {
  recipients: string[];
  subject_template?: string;
  include_chart_image?: boolean;
  include_data_table?: boolean;
}

export interface SlackConfig {
  webhook_url: string;
  channel?: string;
  username?: string;
  icon_emoji?: string;
  include_chart_image?: boolean;
}

export interface WebhookConfig {
  url: string;
  method?: string;
  headers?: Record<string, string>;
  include_full_data?: boolean;
  secret?: string;
}

export interface TeamsConfig {
  webhook_url: string;
  include_chart_image?: boolean;
}

export interface NotificationConfig {
  channel: NotificationChannel;
  email?: EmailConfig;
  slack?: SlackConfig;
  webhook?: WebhookConfig;
  teams?: TeamsConfig;
}

// Alert Types

export interface AlertThreshold {
  condition: AlertCondition;
  value: number;
  secondary_value?: number;
  severity: AlertSeverity;
}

export interface DataAlert {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  target_type: string;
  target_id: string;
  metric_column?: string;
  thresholds: AlertThreshold[];
  evaluation_frequency: string;
  cooldown_minutes: number;
  notifications: NotificationConfig[];
  workspace_id?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  last_evaluated_at?: string;
  last_triggered_at?: string;
  trigger_count: number;
  status: AlertStatus;
  tags: string[];
  metadata: Record<string, unknown>;
}

export interface DataAlertCreate {
  name: string;
  description?: string;
  enabled?: boolean;
  target_type: string;
  target_id: string;
  metric_column?: string;
  thresholds: AlertThreshold[];
  evaluation_frequency?: string;
  cooldown_minutes?: number;
  notifications: NotificationConfig[];
  workspace_id?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface DataAlertUpdate {
  name?: string;
  description?: string;
  enabled?: boolean;
  thresholds?: AlertThreshold[];
  evaluation_frequency?: string;
  cooldown_minutes?: number;
  notifications?: NotificationConfig[];
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface AlertTriggerEvent {
  alert_id: string;
  alert_name: string;
  triggered_at: string;
  threshold: AlertThreshold;
  current_value: number;
  previous_value?: number;
  target_type: string;
  target_id: string;
  target_name?: string;
  severity: AlertSeverity;
  message: string;
  metadata: Record<string, unknown>;
}

export interface AlertHistory {
  id: string;
  alert_id: string;
  triggered_at: string;
  resolved_at?: string;
  threshold_triggered: AlertThreshold;
  value_at_trigger: number;
  severity: AlertSeverity;
  notification_sent: boolean;
  notification_channels: string[];
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolution_notes?: string;
}

// Subscription Types

export interface SubscriptionSchedule {
  frequency: SubscriptionFrequency;
  time_of_day?: string;
  day_of_week?: number;
  day_of_month?: number;
  timezone?: string;
  cron_expression?: string;
}

export interface SubscriptionContent {
  include_dashboard_snapshot?: boolean;
  include_charts?: string[];
  include_data_tables?: boolean;
  include_insights?: boolean;
  include_kpis?: boolean;
  format?: string;
}

export interface Subscription {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  dashboard_id: string;
  dashboard_name?: string;
  schedule: SubscriptionSchedule;
  content: SubscriptionContent;
  recipients: string[];
  notification_channel: NotificationChannel;
  filter_state?: Record<string, unknown>;
  workspace_id?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  last_sent_at?: string;
  next_send_at?: string;
  send_count: number;
  status: SubscriptionStatus;
  metadata: Record<string, unknown>;
}

export interface SubscriptionCreate {
  name: string;
  description?: string;
  enabled?: boolean;
  dashboard_id: string;
  schedule: SubscriptionSchedule;
  content: SubscriptionContent;
  recipients: string[];
  notification_channel?: NotificationChannel;
  filter_state?: Record<string, unknown>;
  workspace_id?: string;
  metadata?: Record<string, unknown>;
}

export interface SubscriptionUpdate {
  name?: string;
  description?: string;
  enabled?: boolean;
  schedule?: SubscriptionSchedule;
  content?: SubscriptionContent;
  recipients?: string[];
  notification_channel?: NotificationChannel;
  filter_state?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface SubscriptionDelivery {
  id: string;
  subscription_id: string;
  sent_at: string;
  recipients: string[];
  success: boolean;
  error_message?: string;
  file_urls: string[];
}

// Summary Types

export interface AlertSummary {
  total_alerts: number;
  active_alerts: number;
  triggered_today: number;
  critical_alerts: number;
  alerts_by_severity: Record<string, number>;
  recent_triggers: AlertTriggerEvent[];
}

export interface SubscriptionSummary {
  total_subscriptions: number;
  active_subscriptions: number;
  sent_today: number;
  sent_this_week: number;
  subscriptions_by_frequency: Record<string, number>;
  recent_deliveries: SubscriptionDelivery[];
}

// Channel Info

export interface NotificationChannelInfo {
  channel: NotificationChannel;
  name: string;
  description: string;
  config_fields: string[];
}

// Constants

export const CONDITION_LABELS: Record<AlertCondition, string> = {
  gt: 'Greater than',
  lt: 'Less than',
  eq: 'Equals',
  ne: 'Not equals',
  gte: 'Greater or equal',
  lte: 'Less or equal',
  between: 'Between',
  not_between: 'Not between',
  increases_by: 'Increases by',
  decreases_by: 'Decreases by',
  changes_by: 'Changes by',
  percent_change: 'Percent change',
};

export const SEVERITY_LABELS: Record<AlertSeverity, string> = {
  info: 'Info',
  warning: 'Warning',
  critical: 'Critical',
};

export const SEVERITY_COLORS: Record<AlertSeverity, string> = {
  info: 'blue',
  warning: 'yellow',
  critical: 'red',
};

export const STATUS_LABELS: Record<AlertStatus, string> = {
  active: 'Active',
  paused: 'Paused',
  triggered: 'Triggered',
  acknowledged: 'Acknowledged',
  resolved: 'Resolved',
};

export const STATUS_COLORS: Record<AlertStatus, string> = {
  active: 'green',
  paused: 'gray',
  triggered: 'red',
  acknowledged: 'yellow',
  resolved: 'blue',
};

export const FREQUENCY_LABELS: Record<SubscriptionFrequency, string> = {
  immediate: 'Immediately',
  hourly: 'Every hour',
  daily: 'Daily',
  weekly: 'Weekly',
  monthly: 'Monthly',
  custom: 'Custom schedule',
};

export const CHANNEL_LABELS: Record<NotificationChannel, string> = {
  email: 'Email',
  slack: 'Slack',
  webhook: 'Webhook',
  in_app: 'In-App',
  sms: 'SMS',
  teams: 'Microsoft Teams',
};

export const CHANNEL_ICONS: Record<NotificationChannel, string> = {
  email: 'mail',
  slack: 'slack',
  webhook: 'globe',
  in_app: 'bell',
  sms: 'smartphone',
  teams: 'users',
};

// Helper Functions

export function getConditionLabel(condition: AlertCondition): string {
  return CONDITION_LABELS[condition] || condition;
}

export function getSeverityLabel(severity: AlertSeverity): string {
  return SEVERITY_LABELS[severity];
}

export function getSeverityColor(severity: AlertSeverity): string {
  return SEVERITY_COLORS[severity];
}

export function getStatusLabel(status: AlertStatus): string {
  return STATUS_LABELS[status];
}

export function getStatusColor(status: AlertStatus): string {
  return STATUS_COLORS[status];
}

export function getFrequencyLabel(frequency: SubscriptionFrequency): string {
  return FREQUENCY_LABELS[frequency];
}

export function getChannelLabel(channel: NotificationChannel): string {
  return CHANNEL_LABELS[channel];
}

export function getChannelIcon(channel: NotificationChannel): string {
  return CHANNEL_ICONS[channel];
}

export function formatNextSend(nextSendAt?: string): string {
  if (!nextSendAt) return 'Not scheduled';

  const date = new Date(nextSendAt);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffMs < 0) return 'Overdue';
  if (diffHours < 1) return 'Less than an hour';
  if (diffHours < 24) return `In ${diffHours} hours`;
  if (diffDays < 7) return `In ${diffDays} days`;

  return date.toLocaleDateString();
}

export function buildConditionDescription(threshold: AlertThreshold): string {
  const label = getConditionLabel(threshold.condition);

  if (threshold.condition === 'between' || threshold.condition === 'not_between') {
    return `${label} ${threshold.value} and ${threshold.secondary_value}`;
  }

  return `${label} ${threshold.value}`;
}

export function isAlertTriggered(alert: DataAlert): boolean {
  return alert.status === 'triggered';
}

export function isAlertActive(alert: DataAlert): boolean {
  return alert.enabled && alert.status === 'active';
}

export function getAlertHealthStatus(alert: DataAlert): 'healthy' | 'warning' | 'critical' {
  if (!alert.enabled) return 'healthy';
  if (alert.status === 'triggered') {
    const hasCritical = alert.thresholds.some((t) => t.severity === 'critical');
    return hasCritical ? 'critical' : 'warning';
  }
  return 'healthy';
}
