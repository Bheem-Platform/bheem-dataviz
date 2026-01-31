/**
 * Report Subscriptions Types
 *
 * TypeScript types for report subscription management including
 * subscriptions, notifications, digests, and user preferences.
 */

// Enums

export enum SubscriptionType {
  INSTANT = 'instant',
  DAILY_DIGEST = 'daily_digest',
  WEEKLY_DIGEST = 'weekly_digest',
  MONTHLY_DIGEST = 'monthly_digest',
  SCHEDULED = 'scheduled',
  ON_REFRESH = 'on_refresh',
  ON_THRESHOLD = 'on_threshold',
}

export enum SubscriptionStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  EXPIRED = 'expired',
  CANCELLED = 'cancelled',
}

export enum ResourceType {
  DASHBOARD = 'dashboard',
  CHART = 'chart',
  REPORT = 'report',
  KPI = 'kpi',
  QUERY = 'query',
  ALERT = 'alert',
}

export enum NotificationChannel {
  EMAIL = 'email',
  SLACK = 'slack',
  TEAMS = 'teams',
  PUSH = 'push',
  IN_APP = 'in_app',
  SMS = 'sms',
  WEBHOOK = 'webhook',
}

export enum DigestFrequency {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  BIWEEKLY = 'biweekly',
  MONTHLY = 'monthly',
}

export enum ThresholdOperator {
  GREATER_THAN = 'gt',
  GREATER_THAN_OR_EQUAL = 'gte',
  LESS_THAN = 'lt',
  LESS_THAN_OR_EQUAL = 'lte',
  EQUAL = 'eq',
  NOT_EQUAL = 'neq',
  CHANGE_BY = 'change_by',
  CHANGE_BY_PERCENT = 'change_by_percent',
}

// Notification Configuration Interfaces

export interface EmailNotificationConfig {
  email_address?: string;
  include_preview: boolean;
  include_attachment: boolean;
  attachment_format: string;
  subject_prefix: string;
}

export interface SlackNotificationConfig {
  channel_id?: string;
  dm_user: boolean;
  include_preview_image: boolean;
  mention_on_threshold: boolean;
}

export interface TeamsNotificationConfig {
  channel_webhook?: string;
  include_preview_image: boolean;
}

export interface PushNotificationConfig {
  send_to_mobile: boolean;
  send_to_desktop: boolean;
  sound_enabled: boolean;
}

export interface WebhookNotificationConfig {
  url: string;
  method: string;
  headers: Record<string, string>;
  include_data: boolean;
}

export interface NotificationConfig {
  channel: NotificationChannel;
  email_config?: EmailNotificationConfig;
  slack_config?: SlackNotificationConfig;
  teams_config?: TeamsNotificationConfig;
  push_config?: PushNotificationConfig;
  webhook_config?: WebhookNotificationConfig;
  enabled: boolean;
}

// Threshold Configuration

export interface ThresholdCondition {
  metric_name: string;
  operator: ThresholdOperator;
  value: number;
  secondary_value?: number;
  comparison_period?: string;
}

// Schedule Configuration

export interface SubscriptionSchedule {
  days_of_week: string[];
  time_of_day: string;
  timezone: string;
}

// Digest Configuration

export interface DigestConfig {
  frequency: DigestFrequency;
  day_of_week?: string;
  day_of_month?: number;
  time_of_day: string;
  timezone: string;
  include_summary: boolean;
  include_highlights: boolean;
  max_items: number;
  group_by_resource: boolean;
}

// Subscription Interfaces

export interface Subscription {
  id: string;
  user_id: string;
  organization_id?: string;
  resource_type: ResourceType;
  resource_id: string;
  resource_name?: string;
  subscription_type: SubscriptionType;
  notification_channels: NotificationConfig[];
  status: SubscriptionStatus;
  is_active: boolean;
  schedule?: SubscriptionSchedule;
  digest_config?: DigestConfig;
  threshold_conditions: ThresholdCondition[];
  filters: Record<string, unknown>;
  last_notified_at?: string;
  notification_count: number;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionCreate {
  resource_type: ResourceType;
  resource_id: string;
  resource_name?: string;
  subscription_type: SubscriptionType;
  notification_channels: NotificationConfig[];
  schedule?: SubscriptionSchedule;
  digest_config?: DigestConfig;
  threshold_conditions?: ThresholdCondition[];
  filters?: Record<string, unknown>;
  is_active?: boolean;
  expires_at?: string;
}

export interface SubscriptionUpdate {
  resource_name?: string;
  subscription_type?: SubscriptionType;
  notification_channels?: NotificationConfig[];
  schedule?: SubscriptionSchedule;
  digest_config?: DigestConfig;
  threshold_conditions?: ThresholdCondition[];
  filters?: Record<string, unknown>;
  is_active?: boolean;
  status?: SubscriptionStatus;
  expires_at?: string;
}

export interface SubscriptionListResponse {
  subscriptions: Subscription[];
  total: number;
}

// Notification Interfaces

export interface NotificationDelivery {
  channel: NotificationChannel;
  success: boolean;
  delivered_at?: string;
  error?: string;
}

export interface SubscriptionNotification {
  id: string;
  subscription_id: string;
  user_id: string;
  resource_type: ResourceType;
  resource_id: string;
  resource_name?: string;
  notification_type: string;
  title: string;
  message: string;
  data: Record<string, unknown>;
  deliveries: NotificationDelivery[];
  read: boolean;
  read_at?: string;
  clicked: boolean;
  clicked_at?: string;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: SubscriptionNotification[];
  total: number;
  unread_count: number;
}

// Digest Interfaces

export interface DigestItem {
  resource_type: ResourceType;
  resource_id: string;
  resource_name: string;
  summary: string;
  changes: string[];
  metrics: Record<string, unknown>;
  timestamp: string;
}

export interface Digest {
  id: string;
  user_id: string;
  digest_type: DigestFrequency;
  period_start: string;
  period_end: string;
  items: DigestItem[];
  total_items: number;
  highlights: string[];
  sent_at?: string;
  created_at: string;
}

export interface DigestListResponse {
  digests: Digest[];
  total: number;
}

// User Preferences Interfaces

export interface GlobalNotificationPreferences {
  email_enabled: boolean;
  push_enabled: boolean;
  in_app_enabled: boolean;
  slack_enabled: boolean;
  teams_enabled: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
  timezone: string;
  digest_enabled: boolean;
  digest_frequency: DigestFrequency;
  digest_time: string;
  unsubscribe_from_marketing: boolean;
}

export interface UserSubscriptionPreferences {
  user_id: string;
  global_preferences: GlobalNotificationPreferences;
  channel_preferences: Record<string, boolean>;
  resource_preferences: Record<string, boolean>;
  muted_resources: string[];
  updated_at: string;
}

// Statistics Interfaces

export interface SubscriptionStats {
  organization_id: string;
  total_subscriptions: number;
  active_subscriptions: number;
  subscriptions_by_type: Record<string, number>;
  subscriptions_by_resource: Record<string, number>;
  subscriptions_by_channel: Record<string, number>;
  notifications_sent_today: number;
  notifications_sent_this_week: number;
  notifications_sent_this_month: number;
  open_rate: number;
  click_rate: number;
  unsubscribe_rate: number;
}

// Constants

export const SUBSCRIPTION_TYPE_LABELS: Record<SubscriptionType, string> = {
  [SubscriptionType.INSTANT]: 'Instant Notifications',
  [SubscriptionType.DAILY_DIGEST]: 'Daily Digest',
  [SubscriptionType.WEEKLY_DIGEST]: 'Weekly Digest',
  [SubscriptionType.MONTHLY_DIGEST]: 'Monthly Digest',
  [SubscriptionType.SCHEDULED]: 'Scheduled',
  [SubscriptionType.ON_REFRESH]: 'On Data Refresh',
  [SubscriptionType.ON_THRESHOLD]: 'On Threshold',
};

export const SUBSCRIPTION_STATUS_LABELS: Record<SubscriptionStatus, string> = {
  [SubscriptionStatus.ACTIVE]: 'Active',
  [SubscriptionStatus.PAUSED]: 'Paused',
  [SubscriptionStatus.EXPIRED]: 'Expired',
  [SubscriptionStatus.CANCELLED]: 'Cancelled',
};

export const RESOURCE_TYPE_LABELS: Record<ResourceType, string> = {
  [ResourceType.DASHBOARD]: 'Dashboard',
  [ResourceType.CHART]: 'Chart',
  [ResourceType.REPORT]: 'Report',
  [ResourceType.KPI]: 'KPI',
  [ResourceType.QUERY]: 'Query',
  [ResourceType.ALERT]: 'Alert',
};

export const NOTIFICATION_CHANNEL_LABELS: Record<NotificationChannel, string> = {
  [NotificationChannel.EMAIL]: 'Email',
  [NotificationChannel.SLACK]: 'Slack',
  [NotificationChannel.TEAMS]: 'Microsoft Teams',
  [NotificationChannel.PUSH]: 'Push Notification',
  [NotificationChannel.IN_APP]: 'In-App',
  [NotificationChannel.SMS]: 'SMS',
  [NotificationChannel.WEBHOOK]: 'Webhook',
};

export const THRESHOLD_OPERATOR_LABELS: Record<ThresholdOperator, string> = {
  [ThresholdOperator.GREATER_THAN]: 'Greater than',
  [ThresholdOperator.GREATER_THAN_OR_EQUAL]: 'Greater than or equal to',
  [ThresholdOperator.LESS_THAN]: 'Less than',
  [ThresholdOperator.LESS_THAN_OR_EQUAL]: 'Less than or equal to',
  [ThresholdOperator.EQUAL]: 'Equal to',
  [ThresholdOperator.NOT_EQUAL]: 'Not equal to',
  [ThresholdOperator.CHANGE_BY]: 'Changes by',
  [ThresholdOperator.CHANGE_BY_PERCENT]: 'Changes by %',
};

export const DIGEST_FREQUENCY_LABELS: Record<DigestFrequency, string> = {
  [DigestFrequency.DAILY]: 'Daily',
  [DigestFrequency.WEEKLY]: 'Weekly',
  [DigestFrequency.BIWEEKLY]: 'Bi-Weekly',
  [DigestFrequency.MONTHLY]: 'Monthly',
};

export const SUBSCRIPTION_STATUS_COLORS: Record<SubscriptionStatus, string> = {
  [SubscriptionStatus.ACTIVE]: 'green',
  [SubscriptionStatus.PAUSED]: 'yellow',
  [SubscriptionStatus.EXPIRED]: 'gray',
  [SubscriptionStatus.CANCELLED]: 'red',
};

// Helper Functions

export function getDefaultGlobalPreferences(): GlobalNotificationPreferences {
  return {
    email_enabled: true,
    push_enabled: true,
    in_app_enabled: true,
    slack_enabled: false,
    teams_enabled: false,
    quiet_hours_enabled: false,
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
    timezone: 'UTC',
    digest_enabled: true,
    digest_frequency: DigestFrequency.DAILY,
    digest_time: '09:00',
    unsubscribe_from_marketing: false,
  };
}

export function getDefaultEmailNotificationConfig(): NotificationConfig {
  return {
    channel: NotificationChannel.EMAIL,
    email_config: {
      include_preview: true,
      include_attachment: false,
      attachment_format: 'pdf',
      subject_prefix: '[DataViz]',
    },
    enabled: true,
  };
}

export function getDefaultDigestConfig(): DigestConfig {
  return {
    frequency: DigestFrequency.DAILY,
    time_of_day: '09:00',
    timezone: 'UTC',
    include_summary: true,
    include_highlights: true,
    max_items: 10,
    group_by_resource: true,
  };
}

export function isSubscriptionActive(subscription: Subscription): boolean {
  return subscription.status === SubscriptionStatus.ACTIVE && subscription.is_active;
}

export function hasUnreadNotifications(response: NotificationListResponse): boolean {
  return response.unread_count > 0;
}

export function getChannelIcon(channel: NotificationChannel): string {
  const icons: Record<NotificationChannel, string> = {
    [NotificationChannel.EMAIL]: 'mail',
    [NotificationChannel.SLACK]: 'message-square',
    [NotificationChannel.TEAMS]: 'users',
    [NotificationChannel.PUSH]: 'bell',
    [NotificationChannel.IN_APP]: 'inbox',
    [NotificationChannel.SMS]: 'smartphone',
    [NotificationChannel.WEBHOOK]: 'globe',
  };
  return icons[channel] || 'bell';
}

export function getResourceTypeIcon(resourceType: ResourceType): string {
  const icons: Record<ResourceType, string> = {
    [ResourceType.DASHBOARD]: 'layout-dashboard',
    [ResourceType.CHART]: 'bar-chart',
    [ResourceType.REPORT]: 'file-text',
    [ResourceType.KPI]: 'trending-up',
    [ResourceType.QUERY]: 'database',
    [ResourceType.ALERT]: 'alert-circle',
  };
  return icons[resourceType] || 'file';
}

export function getSubscriptionTypeIcon(type: SubscriptionType): string {
  const icons: Record<SubscriptionType, string> = {
    [SubscriptionType.INSTANT]: 'zap',
    [SubscriptionType.DAILY_DIGEST]: 'calendar',
    [SubscriptionType.WEEKLY_DIGEST]: 'calendar-days',
    [SubscriptionType.MONTHLY_DIGEST]: 'calendar-range',
    [SubscriptionType.SCHEDULED]: 'clock',
    [SubscriptionType.ON_REFRESH]: 'refresh-cw',
    [SubscriptionType.ON_THRESHOLD]: 'alert-triangle',
  };
  return icons[type] || 'bell';
}

export function formatThresholdDescription(condition: ThresholdCondition): string {
  const opLabel = THRESHOLD_OPERATOR_LABELS[condition.operator] || condition.operator;

  if (
    condition.operator === ThresholdOperator.CHANGE_BY ||
    condition.operator === ThresholdOperator.CHANGE_BY_PERCENT
  ) {
    const unit = condition.operator === ThresholdOperator.CHANGE_BY_PERCENT ? '%' : '';
    return `${condition.metric_name} ${opLabel.toLowerCase()} ${condition.value}${unit}`;
  }

  return `${condition.metric_name} is ${opLabel.toLowerCase()} ${condition.value}`;
}

export function getSubscriptionDescription(subscription: Subscription): string {
  const type = SUBSCRIPTION_TYPE_LABELS[subscription.subscription_type];
  const resource = RESOURCE_TYPE_LABELS[subscription.resource_type];
  const channels = subscription.notification_channels
    .filter(c => c.enabled)
    .map(c => NOTIFICATION_CHANNEL_LABELS[c.channel])
    .join(', ');

  return `${type} for ${resource} via ${channels || 'no channels'}`;
}

export function canPauseSubscription(subscription: Subscription): boolean {
  return subscription.status === SubscriptionStatus.ACTIVE;
}

export function canResumeSubscription(subscription: Subscription): boolean {
  return subscription.status === SubscriptionStatus.PAUSED;
}

export function getEnabledChannels(subscription: Subscription): NotificationChannel[] {
  return subscription.notification_channels
    .filter(c => c.enabled)
    .map(c => c.channel);
}
