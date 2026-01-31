/**
 * External Integrations Types
 *
 * TypeScript types for webhooks, notification channels, Git integration,
 * dbt projects, and other external integrations.
 */

// Enums

export enum IntegrationType {
  ZAPIER = 'zapier',
  MAKE = 'make',
  WEBHOOK = 'webhook',
  SLACK = 'slack',
  TEAMS = 'teams',
  DISCORD = 'discord',
  DBT = 'dbt',
  GIT = 'git',
  GITHUB = 'github',
  GITLAB = 'gitlab',
  BITBUCKET = 'bitbucket',
  JIRA = 'jira',
  NOTION = 'notion',
  AIRTABLE = 'airtable',
}

export enum IntegrationStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ERROR = 'error',
  PENDING = 'pending',
  EXPIRED = 'expired',
}

export enum WebhookEventType {
  DASHBOARD_CREATED = 'dashboard.created',
  DASHBOARD_UPDATED = 'dashboard.updated',
  DASHBOARD_DELETED = 'dashboard.deleted',
  DASHBOARD_PUBLISHED = 'dashboard.published',
  CHART_CREATED = 'chart.created',
  CHART_UPDATED = 'chart.updated',
  CHART_DELETED = 'chart.deleted',
  QUERY_EXECUTED = 'query.executed',
  DATA_REFRESHED = 'data.refreshed',
  ALERT_TRIGGERED = 'alert.triggered',
  REPORT_GENERATED = 'report.generated',
  USER_INVITED = 'user.invited',
  USER_JOINED = 'user.joined',
  COMMENT_ADDED = 'comment.added',
  SHARE_LINK_CREATED = 'share_link.created',
}

export enum WebhookMethod {
  POST = 'POST',
  PUT = 'PUT',
  PATCH = 'PATCH',
}

export enum GitProvider {
  GITHUB = 'github',
  GITLAB = 'gitlab',
  BITBUCKET = 'bitbucket',
  AZURE_DEVOPS = 'azure_devops',
}

export enum GitSyncDirection {
  PUSH = 'push',
  PULL = 'pull',
  BIDIRECTIONAL = 'bidirectional',
}

export enum DbtResourceType {
  MODEL = 'model',
  SOURCE = 'source',
  SEED = 'seed',
  SNAPSHOT = 'snapshot',
  TEST = 'test',
  MACRO = 'macro',
}

export enum DbtRunCommand {
  RUN = 'run',
  TEST = 'test',
  BUILD = 'build',
  COMPILE = 'compile',
  SEED = 'seed',
  SNAPSHOT = 'snapshot',
  SOURCE_FRESHNESS = 'source freshness',
  DOCS_GENERATE = 'docs generate',
}

// Webhook Types

export interface WebhookConfig {
  url: string;
  method: WebhookMethod;
  headers: Record<string, string>;
  secret?: string | null;
  timeout_seconds: number;
  retry_count: number;
  retry_delay_seconds: number;
}

export interface Webhook {
  id: string;
  name: string;
  description?: string | null;
  integration_type: IntegrationType;
  events: WebhookEventType[];
  config: WebhookConfig;
  status: IntegrationStatus;
  workspace_id?: string | null;
  created_by: string;
  created_at: string;
  updated_at?: string | null;
  last_triggered_at?: string | null;
  trigger_count: number;
  failure_count: number;
  last_error?: string | null;
}

export interface WebhookCreate {
  name: string;
  description?: string;
  integration_type?: IntegrationType;
  events: WebhookEventType[];
  config: WebhookConfig;
  workspace_id?: string;
}

export interface WebhookUpdate {
  name?: string;
  description?: string;
  events?: WebhookEventType[];
  config?: WebhookConfig;
  status?: IntegrationStatus;
}

export interface WebhookDelivery {
  id: string;
  webhook_id: string;
  event_type: WebhookEventType;
  payload: Record<string, unknown>;
  response_status?: number | null;
  response_body?: string | null;
  duration_ms: number;
  success: boolean;
  error?: string | null;
  attempt_number: number;
  delivered_at: string;
}

export interface WebhookTest {
  event_type?: WebhookEventType;
  sample_data?: Record<string, unknown>;
}

// Notification Channel Types

export interface SlackConfig {
  webhook_url: string;
  channel?: string | null;
  username: string;
  icon_emoji: string;
  include_preview: boolean;
}

export interface TeamsConfig {
  webhook_url: string;
  include_preview: boolean;
  theme_color: string;
}

export interface DiscordConfig {
  webhook_url: string;
  username: string;
  avatar_url?: string | null;
  include_preview: boolean;
}

export interface NotificationChannelConfig {
  slack?: SlackConfig | null;
  teams?: TeamsConfig | null;
  discord?: DiscordConfig | null;
}

export interface NotificationChannel {
  id: string;
  name: string;
  integration_type: IntegrationType;
  config: NotificationChannelConfig;
  status: IntegrationStatus;
  workspace_id?: string | null;
  created_by: string;
  created_at: string;
  updated_at?: string | null;
  last_used_at?: string | null;
  message_count: number;
}

export interface NotificationChannelCreate {
  name: string;
  integration_type: IntegrationType;
  config: NotificationChannelConfig;
  workspace_id?: string;
}

export interface NotificationMessage {
  title: string;
  message: string;
  url?: string;
  color?: string;
  fields: Array<{ title: string; value: string }>;
  image_url?: string;
}

// Git Integration Types

export interface GitRepository {
  id: string;
  name: string;
  description?: string | null;
  provider: GitProvider;
  url: string;
  branch: string;
  path_prefix: string;
  access_token?: string | null;
  ssh_key_id?: string | null;
  sync_direction: GitSyncDirection;
  auto_sync: boolean;
  sync_interval_minutes: number;
  status: IntegrationStatus;
  workspace_id?: string | null;
  created_by: string;
  created_at: string;
  updated_at?: string | null;
  last_sync_at?: string | null;
  last_sync_commit?: string | null;
  last_sync_error?: string | null;
}

export interface GitRepositoryCreate {
  name: string;
  description?: string;
  provider: GitProvider;
  url: string;
  branch?: string;
  path_prefix?: string;
  access_token?: string;
  ssh_key_id?: string;
  sync_direction?: GitSyncDirection;
  auto_sync?: boolean;
  sync_interval_minutes?: number;
  workspace_id?: string;
}

export interface GitRepositoryUpdate {
  name?: string;
  description?: string;
  branch?: string;
  path_prefix?: string;
  access_token?: string;
  ssh_key_id?: string;
  sync_direction?: GitSyncDirection;
  auto_sync?: boolean;
  sync_interval_minutes?: number;
  status?: IntegrationStatus;
}

export interface GitCommit {
  sha: string;
  message: string;
  author_name: string;
  author_email: string;
  timestamp: string;
  files_changed: number;
  additions: number;
  deletions: number;
}

export interface GitSyncResult {
  repository_id: string;
  direction: GitSyncDirection;
  success: boolean;
  commits: GitCommit[];
  files_synced: number;
  conflicts: string[];
  error?: string | null;
  started_at: string;
  completed_at: string;
}

export interface GitExportConfig {
  resource_type: string;
  resource_id: string;
  file_path: string;
  format?: string;
  include_data?: boolean;
  commit_message?: string;
}

export interface GitImportConfig {
  file_path: string;
  resource_type: string;
  overwrite_existing?: boolean;
  target_workspace_id?: string;
}

// dbt Integration Types

export interface DbtProject {
  id: string;
  name: string;
  description?: string | null;
  project_path: string;
  profile_name: string;
  target_name: string;
  version: string;
  connection_id?: string | null;
  git_repository_id?: string | null;
  status: IntegrationStatus;
  workspace_id?: string | null;
  created_by: string;
  created_at: string;
  updated_at?: string | null;
  last_run_at?: string | null;
  last_run_status?: string | null;
}

export interface DbtProjectCreate {
  name: string;
  description?: string;
  project_path: string;
  profile_name: string;
  target_name?: string;
  connection_id?: string;
  git_repository_id?: string;
  workspace_id?: string;
}

export interface DbtModel {
  name: string;
  description?: string | null;
  resource_type: DbtResourceType;
  schema_name: string;
  database?: string | null;
  columns: Array<Record<string, unknown>>;
  depends_on: string[];
  tags: string[];
  config: Record<string, unknown>;
}

export interface DbtRunRequest {
  command: DbtRunCommand;
  select?: string;
  exclude?: string;
  full_refresh?: boolean;
  vars?: Record<string, unknown>;
}

export interface DbtRunResult {
  id: string;
  project_id: string;
  command: DbtRunCommand;
  status: string;
  started_at: string;
  completed_at?: string | null;
  duration_seconds?: number | null;
  models_run: number;
  models_success: number;
  models_error: number;
  models_skipped: number;
  tests_run: number;
  tests_passed: number;
  tests_failed: number;
  tests_warned: number;
  logs: string[];
  artifacts: Record<string, unknown>;
}

// Integration Hub Types

export interface IntegrationInfo {
  type: IntegrationType;
  name: string;
  description: string;
  icon: string;
  category: string;
  available: boolean;
  connected: boolean;
  requires_oauth: boolean;
  config_schema: Array<Record<string, unknown>>;
}

export interface IntegrationHub {
  integrations: IntegrationInfo[];
  categories: string[];
  total: number;
}

// Response Types

export interface WebhookListResponse {
  webhooks: Webhook[];
  total: number;
}

export interface WebhookDeliveryListResponse {
  deliveries: WebhookDelivery[];
  total: number;
}

export interface NotificationChannelListResponse {
  channels: NotificationChannel[];
  total: number;
}

export interface GitRepositoryListResponse {
  repositories: GitRepository[];
  total: number;
}

export interface DbtProjectListResponse {
  projects: DbtProject[];
  total: number;
}

// Constants

export const INTEGRATION_TYPE_LABELS: Record<IntegrationType, string> = {
  [IntegrationType.ZAPIER]: 'Zapier',
  [IntegrationType.MAKE]: 'Make (Integromat)',
  [IntegrationType.WEBHOOK]: 'Webhook',
  [IntegrationType.SLACK]: 'Slack',
  [IntegrationType.TEAMS]: 'Microsoft Teams',
  [IntegrationType.DISCORD]: 'Discord',
  [IntegrationType.DBT]: 'dbt',
  [IntegrationType.GIT]: 'Git',
  [IntegrationType.GITHUB]: 'GitHub',
  [IntegrationType.GITLAB]: 'GitLab',
  [IntegrationType.BITBUCKET]: 'Bitbucket',
  [IntegrationType.JIRA]: 'Jira',
  [IntegrationType.NOTION]: 'Notion',
  [IntegrationType.AIRTABLE]: 'Airtable',
};

export const INTEGRATION_TYPE_ICONS: Record<IntegrationType, string> = {
  [IntegrationType.ZAPIER]: 'zap',
  [IntegrationType.MAKE]: 'layers',
  [IntegrationType.WEBHOOK]: 'link',
  [IntegrationType.SLACK]: 'slack',
  [IntegrationType.TEAMS]: 'users',
  [IntegrationType.DISCORD]: 'message-circle',
  [IntegrationType.DBT]: 'database',
  [IntegrationType.GIT]: 'git-branch',
  [IntegrationType.GITHUB]: 'github',
  [IntegrationType.GITLAB]: 'gitlab',
  [IntegrationType.BITBUCKET]: 'bitbucket',
  [IntegrationType.JIRA]: 'trello',
  [IntegrationType.NOTION]: 'book-open',
  [IntegrationType.AIRTABLE]: 'grid',
};

export const INTEGRATION_STATUS_LABELS: Record<IntegrationStatus, string> = {
  [IntegrationStatus.ACTIVE]: 'Active',
  [IntegrationStatus.INACTIVE]: 'Inactive',
  [IntegrationStatus.ERROR]: 'Error',
  [IntegrationStatus.PENDING]: 'Pending',
  [IntegrationStatus.EXPIRED]: 'Expired',
};

export const INTEGRATION_STATUS_COLORS: Record<IntegrationStatus, string> = {
  [IntegrationStatus.ACTIVE]: 'green',
  [IntegrationStatus.INACTIVE]: 'gray',
  [IntegrationStatus.ERROR]: 'red',
  [IntegrationStatus.PENDING]: 'yellow',
  [IntegrationStatus.EXPIRED]: 'orange',
};

export const WEBHOOK_EVENT_TYPE_LABELS: Record<WebhookEventType, string> = {
  [WebhookEventType.DASHBOARD_CREATED]: 'Dashboard Created',
  [WebhookEventType.DASHBOARD_UPDATED]: 'Dashboard Updated',
  [WebhookEventType.DASHBOARD_DELETED]: 'Dashboard Deleted',
  [WebhookEventType.DASHBOARD_PUBLISHED]: 'Dashboard Published',
  [WebhookEventType.CHART_CREATED]: 'Chart Created',
  [WebhookEventType.CHART_UPDATED]: 'Chart Updated',
  [WebhookEventType.CHART_DELETED]: 'Chart Deleted',
  [WebhookEventType.QUERY_EXECUTED]: 'Query Executed',
  [WebhookEventType.DATA_REFRESHED]: 'Data Refreshed',
  [WebhookEventType.ALERT_TRIGGERED]: 'Alert Triggered',
  [WebhookEventType.REPORT_GENERATED]: 'Report Generated',
  [WebhookEventType.USER_INVITED]: 'User Invited',
  [WebhookEventType.USER_JOINED]: 'User Joined',
  [WebhookEventType.COMMENT_ADDED]: 'Comment Added',
  [WebhookEventType.SHARE_LINK_CREATED]: 'Share Link Created',
};

export const GIT_PROVIDER_LABELS: Record<GitProvider, string> = {
  [GitProvider.GITHUB]: 'GitHub',
  [GitProvider.GITLAB]: 'GitLab',
  [GitProvider.BITBUCKET]: 'Bitbucket',
  [GitProvider.AZURE_DEVOPS]: 'Azure DevOps',
};

export const DBT_COMMAND_LABELS: Record<DbtRunCommand, string> = {
  [DbtRunCommand.RUN]: 'Run Models',
  [DbtRunCommand.TEST]: 'Run Tests',
  [DbtRunCommand.BUILD]: 'Build (Run + Test)',
  [DbtRunCommand.COMPILE]: 'Compile',
  [DbtRunCommand.SEED]: 'Seed Data',
  [DbtRunCommand.SNAPSHOT]: 'Run Snapshots',
  [DbtRunCommand.SOURCE_FRESHNESS]: 'Check Source Freshness',
  [DbtRunCommand.DOCS_GENERATE]: 'Generate Documentation',
};

export const INTEGRATION_CATEGORIES: Record<string, string> = {
  automation: 'Automation',
  notification: 'Notifications',
  version_control: 'Version Control',
  data: 'Data Tools',
};

// Helper Functions

export function isWebhookActive(webhook: Webhook): boolean {
  return webhook.status === IntegrationStatus.ACTIVE;
}

export function getWebhookSuccessRate(webhook: Webhook): number {
  if (webhook.trigger_count === 0) return 100;
  return ((webhook.trigger_count - webhook.failure_count) / webhook.trigger_count) * 100;
}

export function formatWebhookEventType(eventType: WebhookEventType): string {
  return WEBHOOK_EVENT_TYPE_LABELS[eventType] || eventType;
}

export function getIntegrationIcon(type: IntegrationType): string {
  return INTEGRATION_TYPE_ICONS[type] || 'link';
}

export function getIntegrationStatusColor(status: IntegrationStatus): string {
  return INTEGRATION_STATUS_COLORS[status] || 'gray';
}

export function formatGitCommitSha(sha: string): string {
  return sha.substring(0, 7);
}

export function getDbtRunStatusColor(status: string): string {
  switch (status) {
    case 'success':
      return 'green';
    case 'error':
      return 'red';
    case 'running':
      return 'blue';
    default:
      return 'gray';
  }
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
}

// State Management

export interface IntegrationsState {
  webhooks: Webhook[];
  notificationChannels: NotificationChannel[];
  gitRepositories: GitRepository[];
  dbtProjects: DbtProject[];
  integrationHub: IntegrationHub | null;
  selectedWebhook: Webhook | null;
  selectedChannel: NotificationChannel | null;
  selectedRepository: GitRepository | null;
  selectedProject: DbtProject | null;
  isLoading: boolean;
  error: string | null;
}

export function createInitialIntegrationsState(): IntegrationsState {
  return {
    webhooks: [],
    notificationChannels: [],
    gitRepositories: [],
    dbtProjects: [],
    integrationHub: null,
    selectedWebhook: null,
    selectedChannel: null,
    selectedRepository: null,
    selectedProject: null,
    isLoading: false,
    error: null,
  };
}

// Webhook Builder Helpers

export function createDefaultWebhookConfig(): WebhookConfig {
  return {
    url: '',
    method: WebhookMethod.POST,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout_seconds: 30,
    retry_count: 3,
    retry_delay_seconds: 5,
  };
}

export function createDefaultSlackConfig(): SlackConfig {
  return {
    webhook_url: '',
    channel: null,
    username: 'Bheem DataViz',
    icon_emoji: ':chart_with_upwards_trend:',
    include_preview: true,
  };
}

export function createDefaultTeamsConfig(): TeamsConfig {
  return {
    webhook_url: '',
    include_preview: true,
    theme_color: '#3B82F6',
  };
}

export function createDefaultDiscordConfig(): DiscordConfig {
  return {
    webhook_url: '',
    username: 'Bheem DataViz',
    avatar_url: null,
    include_preview: true,
  };
}

// Validation

export function validateWebhookUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

export function validateGitRepositoryUrl(url: string, provider: GitProvider): boolean {
  const patterns: Record<GitProvider, RegExp> = {
    [GitProvider.GITHUB]: /^https?:\/\/(www\.)?github\.com\/.+\/.+$/,
    [GitProvider.GITLAB]: /^https?:\/\/(www\.)?gitlab\.com\/.+\/.+$/,
    [GitProvider.BITBUCKET]: /^https?:\/\/(www\.)?bitbucket\.org\/.+\/.+$/,
    [GitProvider.AZURE_DEVOPS]: /^https?:\/\/dev\.azure\.com\/.+\/.+\/_git\/.+$/,
  };

  return patterns[provider]?.test(url) ?? false;
}
