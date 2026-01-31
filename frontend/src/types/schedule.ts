/**
 * Schedule and Alert Types
 *
 * TypeScript types for data refresh schedules and alerts.
 */

// Enums

export type ScheduleFrequency = 'once' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'custom';

export type ScheduleStatus = 'active' | 'paused' | 'disabled' | 'error';

export type RefreshType = 'full' | 'incremental' | 'partition';

export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical';

export type AlertOperator =
  | 'greater_than'
  | 'less_than'
  | 'equals'
  | 'not_equals'
  | 'between'
  | 'outside'
  | 'change_greater_than'
  | 'change_less_than'
  | 'percent_change_greater_than'
  | 'percent_change_less_than';

export type NotificationChannel = 'email' | 'slack' | 'teams' | 'webhook' | 'in_app';

// Schedule Configuration

export interface ScheduleTime {
  hour: number;
  minute: number;
  timezone: string;
}

export interface WeeklySchedule {
  days: number[];
  time: ScheduleTime;
}

export interface MonthlySchedule {
  days: number[];
  time: ScheduleTime;
}

export interface ScheduleConfig {
  frequency: ScheduleFrequency;
  startTime?: string;
  endTime?: string;
  time?: ScheduleTime;
  weekly?: WeeklySchedule;
  monthly?: MonthlySchedule;
  cronExpression?: string;
  maxRetries: number;
  retryDelayMinutes: number;
}

// Refresh Schedule

export interface RefreshSchedule {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  status: ScheduleStatus;
  targetType: string;
  targetId: string;
  refreshType: RefreshType;
  schedule: ScheduleConfig;
  incrementalColumn?: string;
  incrementalLookbackDays?: number;
  notifyOnSuccess: boolean;
  notifyOnFailure: boolean;
  notificationRecipients: string[];
  createdAt?: string;
  updatedAt?: string;
  createdBy?: string;
  lastRunAt?: string;
  lastRunStatus?: string;
  nextRunAt?: string;
}

// Alert Configuration

export interface AlertCondition {
  id: string;
  measure: string;
  operator: AlertOperator;
  threshold: number;
  threshold2?: number;
  comparisonPeriod?: string;
}

export interface AlertRule {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  severity: AlertSeverity;
  targetType: string;
  targetId: string;
  conditions: AlertCondition[];
  conditionLogic: 'AND' | 'OR';
  evaluationSchedule: ScheduleConfig;
  notificationChannels: NotificationChannel[];
  notificationRecipients: string[];
  notificationMessage?: string;
  snoozeUntil?: string;
  minIntervalMinutes: number;
  createdAt?: string;
  updatedAt?: string;
  createdBy?: string;
  lastTriggeredAt?: string;
  triggerCount: number;
}

// Notification Configuration

export interface NotificationConfig {
  channel: NotificationChannel;
  enabled: boolean;
  emailAddresses?: string[];
  slackWebhookUrl?: string;
  slackChannel?: string;
  teamsWebhookUrl?: string;
  webhookUrl?: string;
  webhookHeaders?: Record<string, string>;
}

// Execution History

export interface ScheduleExecution {
  id: string;
  scheduleId: string;
  startedAt: string;
  completedAt?: string;
  status: string;
  durationSeconds?: number;
  rowsProcessed?: number;
  errorMessage?: string;
  triggeredBy: string;
}

export interface AlertExecution {
  id: string;
  alertId: string;
  evaluatedAt: string;
  triggered: boolean;
  conditionResults: {
    conditionId: string;
    measure: string;
    triggered: boolean;
    currentValue?: number;
  }[];
  currentValue?: number;
  thresholdValue?: number;
  notificationsSent: string[];
}

// Summaries

export interface ScheduleSummary {
  totalSchedules: number;
  activeSchedules: number;
  pausedSchedules: number;
  failedSchedules: number;
  executionsToday: number;
  successfulToday: number;
  failedToday: number;
}

export interface AlertSummary {
  totalAlerts: number;
  activeAlerts: number;
  triggeredToday: number;
  criticalActive: number;
  warningActive: number;
}

// Options

export const FREQUENCY_OPTIONS = [
  { value: 'once', label: 'Once' },
  { value: 'hourly', label: 'Hourly' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'custom', label: 'Custom (Cron)' },
];

export const ALERT_OPERATOR_OPTIONS = [
  { value: 'greater_than', label: 'Greater than', description: 'Value exceeds threshold' },
  { value: 'less_than', label: 'Less than', description: 'Value falls below threshold' },
  { value: 'equals', label: 'Equals', description: 'Value equals threshold' },
  { value: 'not_equals', label: 'Not equals', description: 'Value differs from threshold' },
  { value: 'between', label: 'Between', description: 'Value is within range' },
  { value: 'outside', label: 'Outside', description: 'Value is outside range' },
  { value: 'change_greater_than', label: 'Change > than', description: 'Absolute change exceeds threshold' },
  { value: 'percent_change_greater_than', label: '% Change > than', description: 'Percentage change exceeds threshold' },
];

export const SEVERITY_OPTIONS = [
  { value: 'info', label: 'Info', color: 'blue' },
  { value: 'warning', label: 'Warning', color: 'yellow' },
  { value: 'error', label: 'Error', color: 'red' },
  { value: 'critical', label: 'Critical', color: 'purple' },
];

export const NOTIFICATION_CHANNEL_OPTIONS = [
  { value: 'email', label: 'Email' },
  { value: 'slack', label: 'Slack' },
  { value: 'teams', label: 'Microsoft Teams' },
  { value: 'webhook', label: 'Webhook' },
  { value: 'in_app', label: 'In-App' },
];

export const WEEKDAY_OPTIONS = [
  { value: 0, label: 'Monday' },
  { value: 1, label: 'Tuesday' },
  { value: 2, label: 'Wednesday' },
  { value: 3, label: 'Thursday' },
  { value: 4, label: 'Friday' },
  { value: 5, label: 'Saturday' },
  { value: 6, label: 'Sunday' },
];

// Helper Functions

export function createDefaultSchedule(
  targetType: string,
  targetId: string
): RefreshSchedule {
  return {
    id: `schedule_${Date.now()}`,
    name: `Refresh ${targetType}`,
    enabled: true,
    status: 'active',
    targetType,
    targetId,
    refreshType: 'full',
    schedule: {
      frequency: 'daily',
      time: { hour: 6, minute: 0, timezone: 'UTC' },
      maxRetries: 3,
      retryDelayMinutes: 5,
    },
    notifyOnSuccess: false,
    notifyOnFailure: true,
    notificationRecipients: [],
  };
}

export function createDefaultAlert(
  targetType: string,
  targetId: string
): AlertRule {
  return {
    id: `alert_${Date.now()}`,
    name: `Alert for ${targetType}`,
    enabled: true,
    severity: 'warning',
    targetType,
    targetId,
    conditions: [],
    conditionLogic: 'AND',
    evaluationSchedule: {
      frequency: 'hourly',
      maxRetries: 3,
      retryDelayMinutes: 5,
    },
    notificationChannels: ['in_app'],
    notificationRecipients: [],
    minIntervalMinutes: 60,
    triggerCount: 0,
  };
}

export function formatScheduleFrequency(schedule: ScheduleConfig): string {
  switch (schedule.frequency) {
    case 'once':
      return schedule.startTime ? `Once at ${schedule.startTime}` : 'Once';
    case 'hourly':
      return 'Every hour';
    case 'daily':
      return schedule.time
        ? `Daily at ${schedule.time.hour.toString().padStart(2, '0')}:${schedule.time.minute.toString().padStart(2, '0')}`
        : 'Daily';
    case 'weekly':
      if (schedule.weekly) {
        const days = schedule.weekly.days.map(d => WEEKDAY_OPTIONS[d]?.label).join(', ');
        return `Weekly on ${days}`;
      }
      return 'Weekly';
    case 'monthly':
      if (schedule.monthly) {
        const days = schedule.monthly.days.join(', ');
        return `Monthly on day ${days}`;
      }
      return 'Monthly';
    case 'custom':
      return schedule.cronExpression || 'Custom';
    default:
      return 'Unknown';
  }
}
