/**
 * Background Jobs Types
 *
 * TypeScript types for job queue management, task scheduling, retry policies,
 * progress tracking, and job history.
 */

// Enums

export enum JobStatus {
  PENDING = 'pending',
  QUEUED = 'queued',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  RETRY = 'retry',
  TIMEOUT = 'timeout',
}

export enum JobPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum JobType {
  QUERY_EXECUTION = 'query_execution',
  DATA_EXPORT = 'data_export',
  DATA_IMPORT = 'data_import',
  REPORT_GENERATION = 'report_generation',
  DASHBOARD_REFRESH = 'dashboard_refresh',
  CACHE_WARMING = 'cache_warming',
  SCHEMA_SYNC = 'schema_sync',
  TRANSFORM_EXECUTION = 'transform_execution',
  ALERT_CHECK = 'alert_check',
  NOTIFICATION_SEND = 'notification_send',
  CLEANUP = 'cleanup',
  ANALYTICS = 'analytics',
  CUSTOM = 'custom',
}

export enum ScheduleType {
  ONCE = 'once',
  INTERVAL = 'interval',
  CRON = 'cron',
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
}

export enum RetryStrategy {
  NONE = 'none',
  FIXED = 'fixed',
  EXPONENTIAL = 'exponential',
  LINEAR = 'linear',
}

export enum WorkerStatus {
  IDLE = 'idle',
  BUSY = 'busy',
  PAUSED = 'paused',
  OFFLINE = 'offline',
}

// Job Types

export interface Job {
  id: string;
  name: string;
  job_type: JobType;
  status: JobStatus;
  priority: JobPriority;
  payload: Record<string, unknown>;
  result?: Record<string, unknown> | null;
  error_message?: string | null;
  error_details?: Record<string, unknown> | null;
  progress: number;
  progress_message?: string | null;
  scheduled_at?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  timeout_seconds: number;
  retry_count: number;
  max_retries: number;
  retry_policy_id?: string | null;
  worker_id?: string | null;
  workspace_id?: string | null;
  user_id?: string | null;
  tags: string[];
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface JobCreate {
  name: string;
  job_type: JobType;
  priority?: JobPriority;
  payload?: Record<string, unknown>;
  scheduled_at?: string;
  timeout_seconds?: number;
  retry_policy_id?: string;
  workspace_id?: string;
  user_id?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface JobUpdate {
  status?: JobStatus;
  priority?: JobPriority;
  progress?: number;
  progress_message?: string;
  result?: Record<string, unknown>;
  error_message?: string;
  tags?: string[];
}

export interface JobProgress {
  job_id: string;
  progress: number;
  message?: string;
  metadata?: Record<string, unknown>;
}

export interface JobResult {
  job_id: string;
  status: JobStatus;
  result?: Record<string, unknown>;
  error_message?: string;
  error_details?: Record<string, unknown>;
  execution_time_ms: number;
  completed_at: string;
}

// Schedule Types

export interface Schedule {
  id: string;
  name: string;
  description?: string | null;
  job_type: JobType;
  schedule_type: ScheduleType;
  schedule_config: Record<string, unknown>;
  payload: Record<string, unknown>;
  priority: JobPriority;
  timeout_seconds: number;
  retry_policy_id?: string | null;
  enabled: boolean;
  last_run_at?: string | null;
  next_run_at?: string | null;
  last_run_status?: JobStatus | null;
  run_count: number;
  failure_count: number;
  workspace_id?: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface ScheduleCreate {
  name: string;
  description?: string;
  job_type: JobType;
  schedule_type: ScheduleType;
  schedule_config: Record<string, unknown>;
  payload?: Record<string, unknown>;
  priority?: JobPriority;
  timeout_seconds?: number;
  retry_policy_id?: string;
  enabled?: boolean;
  workspace_id?: string;
  tags?: string[];
}

export interface ScheduleUpdate {
  name?: string;
  description?: string;
  schedule_type?: ScheduleType;
  schedule_config?: Record<string, unknown>;
  payload?: Record<string, unknown>;
  priority?: JobPriority;
  timeout_seconds?: number;
  retry_policy_id?: string;
  enabled?: boolean;
  tags?: string[];
}

export interface ScheduleRun {
  id: string;
  schedule_id: string;
  job_id: string;
  status: JobStatus;
  scheduled_time: string;
  started_at?: string | null;
  completed_at?: string | null;
  execution_time_ms?: number | null;
  error_message?: string | null;
}

// Retry Policy Types

export interface RetryPolicy {
  id: string;
  name: string;
  description?: string | null;
  strategy: RetryStrategy;
  max_retries: number;
  initial_delay_seconds: number;
  max_delay_seconds: number;
  multiplier: number;
  retry_on_statuses: string[];
  retry_on_errors: string[];
  created_at: string;
}

export interface RetryPolicyCreate {
  name: string;
  description?: string;
  strategy: RetryStrategy;
  max_retries?: number;
  initial_delay_seconds?: number;
  max_delay_seconds?: number;
  multiplier?: number;
  retry_on_statuses?: string[];
  retry_on_errors?: string[];
}

export interface RetryPolicyUpdate {
  name?: string;
  description?: string;
  strategy?: RetryStrategy;
  max_retries?: number;
  initial_delay_seconds?: number;
  max_delay_seconds?: number;
  multiplier?: number;
  retry_on_statuses?: string[];
  retry_on_errors?: string[];
}

// Worker Types

export interface Worker {
  id: string;
  name: string;
  hostname: string;
  status: WorkerStatus;
  current_job_id?: string | null;
  job_types: JobType[];
  max_concurrent_jobs: number;
  jobs_processed: number;
  jobs_failed: number;
  last_heartbeat: string;
  started_at: string;
  metadata: Record<string, unknown>;
}

export interface WorkerHeartbeat {
  worker_id: string;
  status: WorkerStatus;
  current_job_id?: string;
  memory_usage_mb?: number;
  cpu_usage_percent?: number;
}

// Queue Types

export interface QueueStats {
  name: string;
  pending_count: number;
  running_count: number;
  completed_count: number;
  failed_count: number;
  avg_wait_time_ms: number;
  avg_execution_time_ms: number;
  throughput_per_minute: number;
  oldest_pending_age_seconds: number;
}

export interface QueueConfig {
  name: string;
  job_types: JobType[];
  max_workers: number;
  max_queue_size: number;
  default_timeout_seconds: number;
  default_priority: JobPriority;
  rate_limit_per_minute?: number;
}

// History Types

export interface JobHistoryEntry {
  id: string;
  job_id: string;
  job_name: string;
  job_type: JobType;
  status: JobStatus;
  priority: JobPriority;
  workspace_id?: string | null;
  user_id?: string | null;
  execution_time_ms?: number | null;
  retry_count: number;
  error_message?: string | null;
  scheduled_at?: string | null;
  started_at?: string | null;
  completed_at: string;
  tags: string[];
}

export interface JobHistoryStats {
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  cancelled_jobs: number;
  avg_execution_time_ms: number;
  total_execution_time_ms: number;
  success_rate: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  by_hour: Array<Record<string, unknown>>;
  slowest_jobs: JobHistoryEntry[];
}

// Dashboard Types

export interface JobsDashboard {
  active_jobs: number;
  pending_jobs: number;
  completed_today: number;
  failed_today: number;
  success_rate: number;
  avg_wait_time_ms: number;
  avg_execution_time_ms: number;
  active_workers: number;
  total_workers: number;
  queues: QueueStats[];
  recent_failures: Job[];
}

// Configuration Types

export interface JobsConfig {
  enabled: boolean;
  max_workers: number;
  default_timeout_seconds: number;
  max_retry_attempts: number;
  cleanup_completed_after_hours: number;
  cleanup_failed_after_hours: number;
  rate_limit_enabled: boolean;
  rate_limit_per_minute: number;
}

export interface JobsConfigUpdate {
  enabled?: boolean;
  max_workers?: number;
  default_timeout_seconds?: number;
  max_retry_attempts?: number;
  cleanup_completed_after_hours?: number;
  cleanup_failed_after_hours?: number;
  rate_limit_enabled?: boolean;
  rate_limit_per_minute?: number;
}

// Response Types

export interface JobListResponse {
  jobs: Job[];
  total: number;
}

export interface ScheduleListResponse {
  schedules: Schedule[];
  total: number;
}

export interface RetryPolicyListResponse {
  policies: RetryPolicy[];
  total: number;
}

export interface WorkerListResponse {
  workers: Worker[];
  total: number;
}

export interface JobHistoryListResponse {
  entries: JobHistoryEntry[];
  total: number;
}

export interface ScheduleRunListResponse {
  runs: ScheduleRun[];
  total: number;
}

// Constants

export const JOB_TYPE_LABELS: Record<JobType, string> = {
  [JobType.QUERY_EXECUTION]: 'Query Execution',
  [JobType.DATA_EXPORT]: 'Data Export',
  [JobType.DATA_IMPORT]: 'Data Import',
  [JobType.REPORT_GENERATION]: 'Report Generation',
  [JobType.DASHBOARD_REFRESH]: 'Dashboard Refresh',
  [JobType.CACHE_WARMING]: 'Cache Warming',
  [JobType.SCHEMA_SYNC]: 'Schema Sync',
  [JobType.TRANSFORM_EXECUTION]: 'Transform Execution',
  [JobType.ALERT_CHECK]: 'Alert Check',
  [JobType.NOTIFICATION_SEND]: 'Notification Send',
  [JobType.CLEANUP]: 'Cleanup',
  [JobType.ANALYTICS]: 'Analytics',
  [JobType.CUSTOM]: 'Custom',
};

export const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  [JobStatus.PENDING]: 'Pending',
  [JobStatus.QUEUED]: 'Queued',
  [JobStatus.RUNNING]: 'Running',
  [JobStatus.COMPLETED]: 'Completed',
  [JobStatus.FAILED]: 'Failed',
  [JobStatus.CANCELLED]: 'Cancelled',
  [JobStatus.RETRY]: 'Retry',
  [JobStatus.TIMEOUT]: 'Timeout',
};

export const JOB_STATUS_COLORS: Record<JobStatus, string> = {
  [JobStatus.PENDING]: 'gray',
  [JobStatus.QUEUED]: 'blue',
  [JobStatus.RUNNING]: 'indigo',
  [JobStatus.COMPLETED]: 'green',
  [JobStatus.FAILED]: 'red',
  [JobStatus.CANCELLED]: 'gray',
  [JobStatus.RETRY]: 'yellow',
  [JobStatus.TIMEOUT]: 'orange',
};

export const JOB_PRIORITY_LABELS: Record<JobPriority, string> = {
  [JobPriority.LOW]: 'Low',
  [JobPriority.NORMAL]: 'Normal',
  [JobPriority.HIGH]: 'High',
  [JobPriority.CRITICAL]: 'Critical',
};

export const JOB_PRIORITY_COLORS: Record<JobPriority, string> = {
  [JobPriority.LOW]: 'gray',
  [JobPriority.NORMAL]: 'blue',
  [JobPriority.HIGH]: 'yellow',
  [JobPriority.CRITICAL]: 'red',
};

export const SCHEDULE_TYPE_LABELS: Record<ScheduleType, string> = {
  [ScheduleType.ONCE]: 'Once',
  [ScheduleType.INTERVAL]: 'Interval',
  [ScheduleType.CRON]: 'Cron',
  [ScheduleType.DAILY]: 'Daily',
  [ScheduleType.WEEKLY]: 'Weekly',
  [ScheduleType.MONTHLY]: 'Monthly',
};

export const RETRY_STRATEGY_LABELS: Record<RetryStrategy, string> = {
  [RetryStrategy.NONE]: 'None',
  [RetryStrategy.FIXED]: 'Fixed Delay',
  [RetryStrategy.EXPONENTIAL]: 'Exponential Backoff',
  [RetryStrategy.LINEAR]: 'Linear Backoff',
};

export const WORKER_STATUS_LABELS: Record<WorkerStatus, string> = {
  [WorkerStatus.IDLE]: 'Idle',
  [WorkerStatus.BUSY]: 'Busy',
  [WorkerStatus.PAUSED]: 'Paused',
  [WorkerStatus.OFFLINE]: 'Offline',
};

export const WORKER_STATUS_COLORS: Record<WorkerStatus, string> = {
  [WorkerStatus.IDLE]: 'green',
  [WorkerStatus.BUSY]: 'blue',
  [WorkerStatus.PAUSED]: 'yellow',
  [WorkerStatus.OFFLINE]: 'gray',
};

// Helper Functions

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
  return `${(ms / 3600000).toFixed(1)}h`;
}

export function formatSchedule(schedule: Schedule): string {
  const { schedule_type, schedule_config } = schedule;

  switch (schedule_type) {
    case ScheduleType.ONCE:
      return `Once at ${schedule_config.run_at}`;
    case ScheduleType.INTERVAL:
      const seconds = schedule_config.interval_seconds as number;
      if (seconds < 60) return `Every ${seconds}s`;
      if (seconds < 3600) return `Every ${seconds / 60}m`;
      return `Every ${seconds / 3600}h`;
    case ScheduleType.DAILY:
      return `Daily at ${String(schedule_config.hour).padStart(2, '0')}:${String(schedule_config.minute || 0).padStart(2, '0')}`;
    case ScheduleType.WEEKLY:
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      return `Weekly on ${days[schedule_config.day_of_week as number]}`;
    case ScheduleType.MONTHLY:
      return `Monthly on day ${schedule_config.day}`;
    case ScheduleType.CRON:
      return `Cron: ${schedule_config.expression}`;
    default:
      return 'Unknown';
  }
}

export function getJobStatusColor(status: JobStatus): string {
  return JOB_STATUS_COLORS[status] || 'gray';
}

export function getJobPriorityColor(priority: JobPriority): string {
  return JOB_PRIORITY_COLORS[priority] || 'gray';
}

export function getWorkerStatusColor(status: WorkerStatus): string {
  return WORKER_STATUS_COLORS[status] || 'gray';
}

export function isJobRunning(job: Job): boolean {
  return job.status === JobStatus.RUNNING;
}

export function isJobComplete(job: Job): boolean {
  return [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED].includes(job.status);
}

export function canRetryJob(job: Job): boolean {
  return [JobStatus.FAILED, JobStatus.TIMEOUT].includes(job.status);
}

export function canCancelJob(job: Job): boolean {
  return [JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RUNNING].includes(job.status);
}

export function calculateRetryDelay(
  retryCount: number,
  strategy: RetryStrategy,
  initialDelay: number,
  multiplier: number,
  maxDelay: number
): number {
  let delay: number;

  switch (strategy) {
    case RetryStrategy.NONE:
      return 0;
    case RetryStrategy.FIXED:
      delay = initialDelay;
      break;
    case RetryStrategy.LINEAR:
      delay = initialDelay * (retryCount + 1);
      break;
    case RetryStrategy.EXPONENTIAL:
      delay = initialDelay * Math.pow(multiplier, retryCount);
      break;
    default:
      delay = initialDelay;
  }

  return Math.min(delay, maxDelay);
}

// State Management

export interface BackgroundJobsState {
  jobs: Job[];
  schedules: Schedule[];
  retryPolicies: RetryPolicy[];
  workers: Worker[];
  history: JobHistoryEntry[];
  historyStats: JobHistoryStats | null;
  dashboard: JobsDashboard | null;
  config: JobsConfig | null;
  selectedJob: Job | null;
  selectedSchedule: Schedule | null;
  isLoading: boolean;
  error: string | null;
}

export function createInitialBackgroundJobsState(): BackgroundJobsState {
  return {
    jobs: [],
    schedules: [],
    retryPolicies: [],
    workers: [],
    history: [],
    historyStats: null,
    dashboard: null,
    config: null,
    selectedJob: null,
    selectedSchedule: null,
    isLoading: false,
    error: null,
  };
}
