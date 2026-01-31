/**
 * Scheduled Reports Types
 *
 * TypeScript types for scheduled report automation including
 * schedules, recurrence patterns, delivery options, and execution history.
 */

// Enums

export enum ScheduleFrequency {
  ONCE = 'once',
  HOURLY = 'hourly',
  DAILY = 'daily',
  WEEKLY = 'weekly',
  BIWEEKLY = 'biweekly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  YEARLY = 'yearly',
  CUSTOM = 'custom',
}

export enum ScheduleStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  EXPIRED = 'expired',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum ExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  SKIPPED = 'skipped',
}

export enum DeliveryMethod {
  EMAIL = 'email',
  SLACK = 'slack',
  TEAMS = 'teams',
  WEBHOOK = 'webhook',
  S3 = 's3',
  FTP = 'ftp',
  SFTP = 'sftp',
  DOWNLOAD_LINK = 'download_link',
}

export enum DayOfWeek {
  MONDAY = 'monday',
  TUESDAY = 'tuesday',
  WEDNESDAY = 'wednesday',
  THURSDAY = 'thursday',
  FRIDAY = 'friday',
  SATURDAY = 'saturday',
  SUNDAY = 'sunday',
}

// Schedule Configuration Interfaces

export interface TimeOfDay {
  hour: number;
  minute: number;
}

export interface RecurrencePattern {
  frequency: ScheduleFrequency;
  interval: number;
  days_of_week: DayOfWeek[];
  day_of_month?: number;
  month_of_year?: number;
  cron_expression?: string;
  time_of_day: TimeOfDay;
  timezone: string;
}

export interface DateRange {
  start_date: string;
  end_date?: string;
  max_occurrences?: number;
}

// Delivery Configuration Interfaces

export interface EmailDeliveryConfig {
  recipients: string[];
  cc: string[];
  bcc: string[];
  subject_template: string;
  body_template: string;
  include_inline_preview: boolean;
  attachment_format: string;
  max_attachment_size_mb: number;
}

export interface SlackDeliveryConfig {
  webhook_url: string;
  channel: string;
  mention_users: string[];
  include_preview_image: boolean;
  message_template: string;
}

export interface TeamsDeliveryConfig {
  webhook_url: string;
  include_preview_image: boolean;
  message_template: string;
}

export interface WebhookDeliveryConfig {
  url: string;
  method: string;
  headers: Record<string, string>;
  include_report_data: boolean;
  include_file_url: boolean;
  auth_type?: string;
  auth_credentials?: Record<string, string>;
}

export interface S3DeliveryConfig {
  bucket: string;
  path_template: string;
  region: string;
  access_key_id?: string;
  secret_access_key?: string;
  use_iam_role: boolean;
  encryption: string;
}

export interface FTPDeliveryConfig {
  host: string;
  port: number;
  username: string;
  password?: string;
  path: string;
  passive_mode: boolean;
  use_sftp: boolean;
}

export interface DeliveryConfig {
  method: DeliveryMethod;
  email_config?: EmailDeliveryConfig;
  slack_config?: SlackDeliveryConfig;
  teams_config?: TeamsDeliveryConfig;
  webhook_config?: WebhookDeliveryConfig;
  s3_config?: S3DeliveryConfig;
  ftp_config?: FTPDeliveryConfig;
  retry_on_failure: boolean;
  max_retries: number;
  retry_delay_minutes: number;
}

// Report Source Configuration

export interface ReportSourceConfig {
  source_type: string;
  source_id: string;
  source_name?: string;
  export_format: string;
  filters: Record<string, unknown>;
  parameters: Record<string, unknown>;
  template_id?: string;
  date_range_type: string;
  custom_date_range?: DateRange;
}

// Scheduled Report Interfaces

export interface ScheduledReport {
  id: string;
  user_id: string;
  organization_id?: string;
  name: string;
  description?: string;
  source_config: ReportSourceConfig;
  recurrence: RecurrencePattern;
  delivery_configs: DeliveryConfig[];
  date_range: DateRange;
  status: ScheduleStatus;
  is_active: boolean;
  notify_on_failure: boolean;
  failure_notification_emails: string[];
  tags: string[];
  next_run_at?: string;
  last_run_at?: string;
  last_run_status?: ExecutionStatus;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  created_at: string;
  updated_at: string;
}

export interface ScheduledReportCreate {
  name: string;
  description?: string;
  source_config: ReportSourceConfig;
  recurrence: RecurrencePattern;
  delivery_configs: DeliveryConfig[];
  date_range: DateRange;
  is_active?: boolean;
  notify_on_failure?: boolean;
  failure_notification_emails?: string[];
  tags?: string[];
}

export interface ScheduledReportUpdate {
  name?: string;
  description?: string;
  source_config?: ReportSourceConfig;
  recurrence?: RecurrencePattern;
  delivery_configs?: DeliveryConfig[];
  date_range?: DateRange;
  is_active?: boolean;
  status?: ScheduleStatus;
  notify_on_failure?: boolean;
  failure_notification_emails?: string[];
  tags?: string[];
}

export interface ScheduledReportListResponse {
  schedules: ScheduledReport[];
  total: number;
}

// Execution Interfaces

export interface ExecutionLog {
  timestamp: string;
  level: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface DeliveryResult {
  method: DeliveryMethod;
  success: boolean;
  message?: string;
  delivered_at?: string;
  recipient_count: number;
  file_url?: string;
  error?: string;
}

export interface ReportExecution {
  id: string;
  schedule_id: string;
  schedule_name: string;
  user_id: string;
  organization_id?: string;
  status: ExecutionStatus;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  source_config: ReportSourceConfig;
  export_format: string;
  file_size_bytes?: number;
  file_url?: string;
  delivery_results: DeliveryResult[];
  logs: ExecutionLog[];
  error_message?: string;
  retry_count: number;
  triggered_by: string;
}

export interface ReportExecutionListResponse {
  executions: ReportExecution[];
  total: number;
}

// Statistics Interfaces

export interface ScheduleStats {
  organization_id: string;
  total_schedules: number;
  active_schedules: number;
  paused_schedules: number;
  total_executions: number;
  executions_today: number;
  executions_this_week: number;
  executions_this_month: number;
  success_rate: number;
  average_duration_seconds: number;
  by_frequency: Record<string, number>;
  by_format: Record<string, number>;
  by_delivery_method: Record<string, number>;
  upcoming_executions: number;
}

// Constants

export const SCHEDULE_FREQUENCY_LABELS: Record<ScheduleFrequency, string> = {
  [ScheduleFrequency.ONCE]: 'One Time',
  [ScheduleFrequency.HOURLY]: 'Hourly',
  [ScheduleFrequency.DAILY]: 'Daily',
  [ScheduleFrequency.WEEKLY]: 'Weekly',
  [ScheduleFrequency.BIWEEKLY]: 'Bi-Weekly',
  [ScheduleFrequency.MONTHLY]: 'Monthly',
  [ScheduleFrequency.QUARTERLY]: 'Quarterly',
  [ScheduleFrequency.YEARLY]: 'Yearly',
  [ScheduleFrequency.CUSTOM]: 'Custom',
};

export const SCHEDULE_STATUS_LABELS: Record<ScheduleStatus, string> = {
  [ScheduleStatus.ACTIVE]: 'Active',
  [ScheduleStatus.PAUSED]: 'Paused',
  [ScheduleStatus.COMPLETED]: 'Completed',
  [ScheduleStatus.EXPIRED]: 'Expired',
  [ScheduleStatus.FAILED]: 'Failed',
  [ScheduleStatus.CANCELLED]: 'Cancelled',
};

export const EXECUTION_STATUS_LABELS: Record<ExecutionStatus, string> = {
  [ExecutionStatus.PENDING]: 'Pending',
  [ExecutionStatus.RUNNING]: 'Running',
  [ExecutionStatus.COMPLETED]: 'Completed',
  [ExecutionStatus.FAILED]: 'Failed',
  [ExecutionStatus.CANCELLED]: 'Cancelled',
  [ExecutionStatus.SKIPPED]: 'Skipped',
};

export const DELIVERY_METHOD_LABELS: Record<DeliveryMethod, string> = {
  [DeliveryMethod.EMAIL]: 'Email',
  [DeliveryMethod.SLACK]: 'Slack',
  [DeliveryMethod.TEAMS]: 'Microsoft Teams',
  [DeliveryMethod.WEBHOOK]: 'Webhook',
  [DeliveryMethod.S3]: 'Amazon S3',
  [DeliveryMethod.FTP]: 'FTP',
  [DeliveryMethod.SFTP]: 'SFTP',
  [DeliveryMethod.DOWNLOAD_LINK]: 'Download Link',
};

export const DAY_OF_WEEK_LABELS: Record<DayOfWeek, string> = {
  [DayOfWeek.MONDAY]: 'Monday',
  [DayOfWeek.TUESDAY]: 'Tuesday',
  [DayOfWeek.WEDNESDAY]: 'Wednesday',
  [DayOfWeek.THURSDAY]: 'Thursday',
  [DayOfWeek.FRIDAY]: 'Friday',
  [DayOfWeek.SATURDAY]: 'Saturday',
  [DayOfWeek.SUNDAY]: 'Sunday',
};

export const SCHEDULE_STATUS_COLORS: Record<ScheduleStatus, string> = {
  [ScheduleStatus.ACTIVE]: 'green',
  [ScheduleStatus.PAUSED]: 'yellow',
  [ScheduleStatus.COMPLETED]: 'blue',
  [ScheduleStatus.EXPIRED]: 'gray',
  [ScheduleStatus.FAILED]: 'red',
  [ScheduleStatus.CANCELLED]: 'gray',
};

export const EXECUTION_STATUS_COLORS: Record<ExecutionStatus, string> = {
  [ExecutionStatus.PENDING]: 'yellow',
  [ExecutionStatus.RUNNING]: 'blue',
  [ExecutionStatus.COMPLETED]: 'green',
  [ExecutionStatus.FAILED]: 'red',
  [ExecutionStatus.CANCELLED]: 'gray',
  [ExecutionStatus.SKIPPED]: 'orange',
};

// Helper Functions

export function getDefaultTimeOfDay(): TimeOfDay {
  return { hour: 9, minute: 0 };
}

export function getDefaultRecurrence(): RecurrencePattern {
  return {
    frequency: ScheduleFrequency.DAILY,
    interval: 1,
    days_of_week: [],
    time_of_day: getDefaultTimeOfDay(),
    timezone: 'UTC',
  };
}

export function getDefaultDateRange(): DateRange {
  const now = new Date();
  return {
    start_date: now.toISOString(),
  };
}

export function getDefaultEmailDelivery(): DeliveryConfig {
  return {
    method: DeliveryMethod.EMAIL,
    email_config: {
      recipients: [],
      cc: [],
      bcc: [],
      subject_template: 'Scheduled Report: {report_name}',
      body_template: 'Please find attached the scheduled report generated on {date}.',
      include_inline_preview: false,
      attachment_format: 'pdf',
      max_attachment_size_mb: 25,
    },
    retry_on_failure: true,
    max_retries: 3,
    retry_delay_minutes: 5,
  };
}

export function isScheduleActive(schedule: ScheduledReport): boolean {
  return schedule.status === ScheduleStatus.ACTIVE && schedule.is_active;
}

export function isSchedulePaused(schedule: ScheduledReport): boolean {
  return schedule.status === ScheduleStatus.PAUSED || !schedule.is_active;
}

export function canTriggerSchedule(schedule: ScheduledReport): boolean {
  return schedule.status !== ScheduleStatus.EXPIRED && schedule.status !== ScheduleStatus.CANCELLED;
}

export function isExecutionInProgress(execution: ReportExecution): boolean {
  return execution.status === ExecutionStatus.PENDING || execution.status === ExecutionStatus.RUNNING;
}

export function isExecutionComplete(execution: ReportExecution): boolean {
  return execution.status === ExecutionStatus.COMPLETED;
}

export function canRetryExecution(execution: ReportExecution): boolean {
  return execution.status === ExecutionStatus.FAILED;
}

export function canCancelExecution(execution: ReportExecution): boolean {
  return execution.status === ExecutionStatus.PENDING || execution.status === ExecutionStatus.RUNNING;
}

export function formatScheduleDescription(recurrence: RecurrencePattern): string {
  const freq = recurrence.frequency;
  const time = `${recurrence.time_of_day.hour.toString().padStart(2, '0')}:${recurrence.time_of_day.minute.toString().padStart(2, '0')}`;

  switch (freq) {
    case ScheduleFrequency.ONCE:
      return `One time at ${time}`;
    case ScheduleFrequency.HOURLY:
      return recurrence.interval === 1
        ? `Every hour at minute ${recurrence.time_of_day.minute}`
        : `Every ${recurrence.interval} hours at minute ${recurrence.time_of_day.minute}`;
    case ScheduleFrequency.DAILY:
      return recurrence.interval === 1
        ? `Daily at ${time}`
        : `Every ${recurrence.interval} days at ${time}`;
    case ScheduleFrequency.WEEKLY:
      const days = recurrence.days_of_week.map(d => DAY_OF_WEEK_LABELS[d]).join(', ');
      return `Weekly on ${days || 'weekdays'} at ${time}`;
    case ScheduleFrequency.MONTHLY:
      const day = recurrence.day_of_month || 1;
      const suffix = day === 1 ? 'st' : day === 2 ? 'nd' : day === 3 ? 'rd' : 'th';
      return `Monthly on the ${day}${suffix} at ${time}`;
    case ScheduleFrequency.QUARTERLY:
      return `Quarterly at ${time}`;
    case ScheduleFrequency.YEARLY:
      return `Yearly at ${time}`;
    case ScheduleFrequency.CUSTOM:
      return recurrence.cron_expression
        ? `Custom: ${recurrence.cron_expression}`
        : 'Custom schedule';
    default:
      return 'Unknown schedule';
  }
}

export function getScheduleSuccessRate(schedule: ScheduledReport): number {
  if (schedule.total_runs === 0) return 0;
  return (schedule.successful_runs / schedule.total_runs) * 100;
}

export function formatDuration(seconds?: number): string {
  if (!seconds) return '-';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
}

export function getScheduleStatusIcon(status: ScheduleStatus): string {
  const icons: Record<ScheduleStatus, string> = {
    [ScheduleStatus.ACTIVE]: 'play-circle',
    [ScheduleStatus.PAUSED]: 'pause-circle',
    [ScheduleStatus.COMPLETED]: 'check-circle',
    [ScheduleStatus.EXPIRED]: 'clock',
    [ScheduleStatus.FAILED]: 'x-circle',
    [ScheduleStatus.CANCELLED]: 'slash',
  };
  return icons[status] || 'help-circle';
}

export function getExecutionStatusIcon(status: ExecutionStatus): string {
  const icons: Record<ExecutionStatus, string> = {
    [ExecutionStatus.PENDING]: 'clock',
    [ExecutionStatus.RUNNING]: 'loader',
    [ExecutionStatus.COMPLETED]: 'check-circle',
    [ExecutionStatus.FAILED]: 'x-circle',
    [ExecutionStatus.CANCELLED]: 'slash',
    [ExecutionStatus.SKIPPED]: 'skip-forward',
  };
  return icons[status] || 'help-circle';
}

export function getDeliveryMethodIcon(method: DeliveryMethod): string {
  const icons: Record<DeliveryMethod, string> = {
    [DeliveryMethod.EMAIL]: 'mail',
    [DeliveryMethod.SLACK]: 'message-square',
    [DeliveryMethod.TEAMS]: 'users',
    [DeliveryMethod.WEBHOOK]: 'globe',
    [DeliveryMethod.S3]: 'cloud',
    [DeliveryMethod.FTP]: 'upload-cloud',
    [DeliveryMethod.SFTP]: 'lock',
    [DeliveryMethod.DOWNLOAD_LINK]: 'download',
  };
  return icons[method] || 'send';
}
