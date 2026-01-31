/**
 * Workspace Management Types
 *
 * TypeScript types for multi-tenant workspace management, member management,
 * invitations, and workspace settings.
 */

// Enums

export enum WorkspaceStatus {
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  TRIAL = 'trial',
  EXPIRED = 'expired',
  DELETED = 'deleted',
}

export enum WorkspacePlan {
  FREE = 'free',
  STARTER = 'starter',
  PRO = 'pro',
  BUSINESS = 'business',
  ENTERPRISE = 'enterprise',
}

export enum MemberRole {
  OWNER = 'owner',
  ADMIN = 'admin',
  EDITOR = 'editor',
  VIEWER = 'viewer',
  GUEST = 'guest',
}

export enum MemberStatus {
  ACTIVE = 'active',
  INVITED = 'invited',
  SUSPENDED = 'suspended',
  DEACTIVATED = 'deactivated',
}

export enum InvitationStatus {
  PENDING = 'pending',
  ACCEPTED = 'accepted',
  DECLINED = 'declined',
  EXPIRED = 'expired',
  CANCELLED = 'cancelled',
}

export enum ResourceType {
  DASHBOARD = 'dashboard',
  CHART = 'chart',
  CONNECTION = 'connection',
  DATASET = 'dataset',
  TRANSFORM = 'transform',
  SEMANTIC_MODEL = 'semantic_model',
  QUERY = 'query',
  KPI = 'kpi',
  REPORT = 'report',
}

// Workspace Interfaces

export interface WorkspaceCreate {
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  plan?: WorkspacePlan;
  settings?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  status: WorkspaceStatus;
  plan: WorkspacePlan;
  owner_id: string;
  member_count: number;
  dashboard_count: number;
  connection_count: number;
  storage_used_mb: number;
  settings: Record<string, unknown>;
  metadata: Record<string, unknown>;
  trial_ends_at?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceUpdate {
  name?: string;
  description?: string;
  logo_url?: string;
  settings?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface WorkspaceSettings {
  workspace_id: string;
  allow_public_dashboards: boolean;
  allow_public_links: boolean;
  require_2fa: boolean;
  default_member_role: MemberRole;
  allowed_email_domains: string[];
  ip_whitelist: string[];
  session_timeout_minutes: number;
  password_policy: Record<string, unknown>;
  branding: Record<string, unknown>;
  notification_settings: Record<string, unknown>;
  data_retention_days: number;
  max_connections: number;
  max_dashboards: number;
  max_members: number;
  features_enabled: string[];
}

export interface WorkspaceSettingsUpdate {
  allow_public_dashboards?: boolean;
  allow_public_links?: boolean;
  require_2fa?: boolean;
  default_member_role?: MemberRole;
  allowed_email_domains?: string[];
  ip_whitelist?: string[];
  session_timeout_minutes?: number;
  password_policy?: Record<string, unknown>;
  branding?: Record<string, unknown>;
  notification_settings?: Record<string, unknown>;
  data_retention_days?: number;
}

// Member Interfaces

export interface WorkspaceMemberCreate {
  user_id: string;
  role?: MemberRole;
  permissions?: Record<string, boolean>;
}

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  email: string;
  name: string;
  avatar_url?: string;
  role: MemberRole;
  status: MemberStatus;
  permissions: Record<string, boolean>;
  last_active_at?: string;
  joined_at: string;
  invited_by?: string;
}

export interface WorkspaceMemberUpdate {
  role?: MemberRole;
  permissions?: Record<string, boolean>;
  status?: MemberStatus;
}

// Invitation Interfaces

export interface InvitationCreate {
  email: string;
  role?: MemberRole;
  message?: string;
  expires_in_days?: number;
}

export interface Invitation {
  id: string;
  workspace_id: string;
  workspace_name: string;
  email: string;
  role: MemberRole;
  status: InvitationStatus;
  message?: string;
  token: string;
  invited_by_id: string;
  invited_by_name: string;
  expires_at: string;
  accepted_at?: string;
  declined_at?: string;
  created_at: string;
}

export interface BulkInvitationCreate {
  emails: string[];
  role?: MemberRole;
  message?: string;
  expires_in_days?: number;
}

export interface InvitationResponse {
  accept: boolean;
  user_id?: string;
}

// Quota Interfaces

export interface WorkspaceQuota {
  workspace_id: string;
  plan: WorkspacePlan;
  max_members: number;
  current_members: number;
  max_guests: number;
  current_guests: number;
  max_connections: number;
  current_connections: number;
  max_dashboards: number;
  current_dashboards: number;
  max_charts: number;
  current_charts: number;
  max_datasets: number;
  current_datasets: number;
  max_storage_mb: number;
  current_storage_mb: number;
  max_api_calls_per_day: number;
  current_api_calls_today: number;
  max_query_execution_minutes: number;
  current_query_minutes_today: number;
  max_scheduled_reports: number;
  current_scheduled_reports: number;
  max_alerts: number;
  current_alerts: number;
}

export interface QuotaUsage {
  workspace_id: string;
  resource_type: string;
  limit: number;
  used: number;
  remaining: number;
  percent_used: number;
}

// Access Control Interfaces

export interface ResourcePermission {
  resource_type: ResourceType;
  resource_id: string;
  member_id: string;
  can_view: boolean;
  can_edit: boolean;
  can_delete: boolean;
  can_share: boolean;
  can_export: boolean;
}

export interface RolePermissions {
  role: MemberRole;
  can_manage_workspace: boolean;
  can_manage_members: boolean;
  can_manage_billing: boolean;
  can_manage_settings: boolean;
  can_create_connections: boolean;
  can_create_dashboards: boolean;
  can_create_charts: boolean;
  can_create_datasets: boolean;
  can_execute_queries: boolean;
  can_export_data: boolean;
  can_share_resources: boolean;
  can_create_public_links: boolean;
  can_use_ai_features: boolean;
  can_create_alerts: boolean;
  can_schedule_reports: boolean;
  can_use_api: boolean;
}

// Team Interfaces

export interface Team {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  color?: string;
  member_ids: string[];
  permissions: Record<string, boolean>;
  created_at: string;
}

export interface TeamCreate {
  name: string;
  description?: string;
  color?: string;
  member_ids?: string[];
}

export interface TeamUpdate {
  name?: string;
  description?: string;
  color?: string;
  member_ids?: string[];
  permissions?: Record<string, boolean>;
}

// Activity Interfaces

export interface WorkspaceActivity {
  id: string;
  workspace_id: string;
  user_id: string;
  user_name: string;
  action: string;
  resource_type?: ResourceType;
  resource_id?: string;
  resource_name?: string;
  details: Record<string, unknown>;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

// Response Interfaces

export interface WorkspaceListResponse {
  workspaces: Workspace[];
  total: number;
}

export interface WorkspaceMemberListResponse {
  members: WorkspaceMember[];
  total: number;
}

export interface InvitationListResponse {
  invitations: Invitation[];
  total: number;
}

export interface TeamListResponse {
  teams: Team[];
  total: number;
}

export interface WorkspaceActivityListResponse {
  activities: WorkspaceActivity[];
  total: number;
}

export interface QuotaUsageListResponse {
  quotas: QuotaUsage[];
}

// Summary Interfaces

export interface WorkspaceSummary {
  workspace_id: string;
  name: string;
  plan: WorkspacePlan;
  status: WorkspaceStatus;
  member_count: number;
  dashboard_count: number;
  connection_count: number;
  chart_count: number;
  storage_used_mb: number;
  storage_limit_mb: number;
  api_calls_today: number;
  active_users_today: number;
  recent_activities: WorkspaceActivity[];
}

export interface UserWorkspaces {
  owned: Workspace[];
  member_of: Workspace[];
  pending_invitations: Invitation[];
}

// Permission Check Interface

export interface PermissionCheck {
  workspace_id: string;
  member_id: string;
  permission: string;
  allowed: boolean;
  reason?: string;
}

// Constants

export const PLAN_LIMITS: Record<WorkspacePlan, Record<string, number>> = {
  [WorkspacePlan.FREE]: {
    max_members: 3,
    max_guests: 0,
    max_connections: 2,
    max_dashboards: 5,
    max_charts: 20,
    max_datasets: 5,
    max_storage_mb: 100,
    max_api_calls_per_day: 100,
    max_query_execution_minutes: 10,
    max_scheduled_reports: 0,
    max_alerts: 0,
  },
  [WorkspacePlan.STARTER]: {
    max_members: 5,
    max_guests: 5,
    max_connections: 5,
    max_dashboards: 20,
    max_charts: 100,
    max_datasets: 20,
    max_storage_mb: 500,
    max_api_calls_per_day: 1000,
    max_query_execution_minutes: 60,
    max_scheduled_reports: 5,
    max_alerts: 10,
  },
  [WorkspacePlan.PRO]: {
    max_members: 25,
    max_guests: 25,
    max_connections: 20,
    max_dashboards: 100,
    max_charts: 500,
    max_datasets: 100,
    max_storage_mb: 5000,
    max_api_calls_per_day: 10000,
    max_query_execution_minutes: 300,
    max_scheduled_reports: 25,
    max_alerts: 50,
  },
  [WorkspacePlan.BUSINESS]: {
    max_members: 100,
    max_guests: 100,
    max_connections: 50,
    max_dashboards: 500,
    max_charts: 2500,
    max_datasets: 500,
    max_storage_mb: 25000,
    max_api_calls_per_day: 100000,
    max_query_execution_minutes: 1000,
    max_scheduled_reports: 100,
    max_alerts: 200,
  },
  [WorkspacePlan.ENTERPRISE]: {
    max_members: -1,
    max_guests: -1,
    max_connections: -1,
    max_dashboards: -1,
    max_charts: -1,
    max_datasets: -1,
    max_storage_mb: -1,
    max_api_calls_per_day: -1,
    max_query_execution_minutes: -1,
    max_scheduled_reports: -1,
    max_alerts: -1,
  },
};

export const ROLE_HIERARCHY: MemberRole[] = [
  MemberRole.OWNER,
  MemberRole.ADMIN,
  MemberRole.EDITOR,
  MemberRole.VIEWER,
  MemberRole.GUEST,
];

export const ROLE_LABELS: Record<MemberRole, string> = {
  [MemberRole.OWNER]: 'Owner',
  [MemberRole.ADMIN]: 'Admin',
  [MemberRole.EDITOR]: 'Editor',
  [MemberRole.VIEWER]: 'Viewer',
  [MemberRole.GUEST]: 'Guest',
};

export const PLAN_LABELS: Record<WorkspacePlan, string> = {
  [WorkspacePlan.FREE]: 'Free',
  [WorkspacePlan.STARTER]: 'Starter',
  [WorkspacePlan.PRO]: 'Pro',
  [WorkspacePlan.BUSINESS]: 'Business',
  [WorkspacePlan.ENTERPRISE]: 'Enterprise',
};

export const STATUS_LABELS: Record<WorkspaceStatus, string> = {
  [WorkspaceStatus.ACTIVE]: 'Active',
  [WorkspaceStatus.SUSPENDED]: 'Suspended',
  [WorkspaceStatus.TRIAL]: 'Trial',
  [WorkspaceStatus.EXPIRED]: 'Expired',
  [WorkspaceStatus.DELETED]: 'Deleted',
};

export const INVITATION_STATUS_LABELS: Record<InvitationStatus, string> = {
  [InvitationStatus.PENDING]: 'Pending',
  [InvitationStatus.ACCEPTED]: 'Accepted',
  [InvitationStatus.DECLINED]: 'Declined',
  [InvitationStatus.EXPIRED]: 'Expired',
  [InvitationStatus.CANCELLED]: 'Cancelled',
};

export const MEMBER_STATUS_LABELS: Record<MemberStatus, string> = {
  [MemberStatus.ACTIVE]: 'Active',
  [MemberStatus.INVITED]: 'Invited',
  [MemberStatus.SUSPENDED]: 'Suspended',
  [MemberStatus.DEACTIVATED]: 'Deactivated',
};

export const RESOURCE_TYPE_LABELS: Record<ResourceType, string> = {
  [ResourceType.DASHBOARD]: 'Dashboard',
  [ResourceType.CHART]: 'Chart',
  [ResourceType.CONNECTION]: 'Connection',
  [ResourceType.DATASET]: 'Dataset',
  [ResourceType.TRANSFORM]: 'Transform',
  [ResourceType.SEMANTIC_MODEL]: 'Semantic Model',
  [ResourceType.QUERY]: 'Query',
  [ResourceType.KPI]: 'KPI',
  [ResourceType.REPORT]: 'Report',
};

// Helper Functions

export function getPlanLimits(plan: WorkspacePlan): Record<string, number> {
  return PLAN_LIMITS[plan] || PLAN_LIMITS[WorkspacePlan.FREE];
}

export function isUnlimited(limit: number): boolean {
  return limit === -1;
}

export function formatQuotaValue(value: number, limit: number): string {
  if (isUnlimited(limit)) {
    return `${value} / Unlimited`;
  }
  return `${value} / ${limit}`;
}

export function calculateQuotaPercentage(used: number, limit: number): number {
  if (isUnlimited(limit)) return 0;
  if (limit === 0) return 100;
  return Math.min(100, Math.round((used / limit) * 100));
}

export function getQuotaStatus(
  used: number,
  limit: number
): 'ok' | 'warning' | 'critical' {
  if (isUnlimited(limit)) return 'ok';
  const percentage = calculateQuotaPercentage(used, limit);
  if (percentage >= 100) return 'critical';
  if (percentage >= 80) return 'warning';
  return 'ok';
}

export function canRoleManage(managerRole: MemberRole, targetRole: MemberRole): boolean {
  const managerIndex = ROLE_HIERARCHY.indexOf(managerRole);
  const targetIndex = ROLE_HIERARCHY.indexOf(targetRole);
  return managerIndex < targetIndex;
}

export function isRoleAtLeast(role: MemberRole, minimumRole: MemberRole): boolean {
  const roleIndex = ROLE_HIERARCHY.indexOf(role);
  const minimumIndex = ROLE_HIERARCHY.indexOf(minimumRole);
  return roleIndex <= minimumIndex;
}

export function formatStorageSize(megabytes: number): string {
  if (megabytes < 1024) {
    return `${megabytes} MB`;
  }
  return `${(megabytes / 1024).toFixed(1)} GB`;
}

export function isInvitationExpired(invitation: Invitation): boolean {
  return new Date(invitation.expires_at) < new Date();
}

export function isPendingInvitation(invitation: Invitation): boolean {
  return invitation.status === InvitationStatus.PENDING && !isInvitationExpired(invitation);
}

export function getActivityIcon(action: string): string {
  const icons: Record<string, string> = {
    created: '➕',
    updated: '✏️',
    deleted: '🗑️',
    invited: '✉️',
    joined: '👋',
    left: '👋',
    shared: '🔗',
    exported: '📤',
    imported: '📥',
  };
  return icons[action] || '📝';
}

export function formatActivityMessage(activity: WorkspaceActivity): string {
  const { user_name, action, resource_type, resource_name } = activity;

  if (resource_type && resource_name) {
    return `${user_name} ${action} ${RESOURCE_TYPE_LABELS[resource_type].toLowerCase()} "${resource_name}"`;
  }

  return `${user_name} ${action}`;
}
