/**
 * Workspace Types
 *
 * TypeScript types for team workspaces and collaboration.
 */

// Enums

export type WorkspaceRole = 'owner' | 'admin' | 'member' | 'viewer';

export type InviteStatus = 'pending' | 'accepted' | 'declined' | 'expired';

// Workspace Types

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description?: string;
  owner_id: string;
  is_personal: boolean;
  is_default: boolean;
  logo_url?: string;
  primary_color?: string;
  settings: Record<string, unknown>;
  is_active: boolean;
  member_count: number;
  dashboard_count: number;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceSummary {
  id: string;
  name: string;
  slug: string;
  is_personal: boolean;
  is_default: boolean;
  role: WorkspaceRole;
  logo_url?: string;
  primary_color?: string;
}

export interface WorkspaceCreate {
  name: string;
  description?: string;
  slug?: string;
  logo_url?: string;
  primary_color?: string;
  settings?: Record<string, unknown>;
}

export interface WorkspaceUpdate {
  name?: string;
  description?: string;
  logo_url?: string;
  primary_color?: string;
  settings?: Record<string, unknown>;
  is_default?: boolean;
}

// Member Types

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  role: WorkspaceRole;
  custom_permissions: Record<string, boolean>;
  is_active: boolean;
  joined_at: string;
  last_accessed_at?: string;
  user_email?: string;
  user_name?: string;
}

export interface MemberCreate {
  user_id: string;
  role?: WorkspaceRole;
}

export interface MemberUpdate {
  role?: WorkspaceRole;
  custom_permissions?: Record<string, boolean>;
  is_active?: boolean;
}

// Invitation Types

export interface WorkspaceInvitation {
  id: string;
  workspace_id: string;
  email: string;
  role: WorkspaceRole;
  status: InviteStatus;
  message?: string;
  invited_by: string;
  inviter_name?: string;
  expires_at: string;
  created_at: string;
  accepted_at?: string;
}

export interface InvitationCreate {
  email: string;
  role?: WorkspaceRole;
  message?: string;
  expires_in_days?: number;
}

export interface BulkInvite {
  emails: string[];
  role?: WorkspaceRole;
  message?: string;
}

export interface BulkInviteResponse {
  sent: string[];
  failed: Array<{ email: string; reason: string }>;
  total_sent: number;
  total_failed: number;
}

// Permission Types

export interface ObjectPermission {
  id: string;
  workspace_id: string;
  object_type: string;
  object_id: string;
  user_id?: string;
  role?: WorkspaceRole;
  can_view: boolean;
  can_edit: boolean;
  can_delete: boolean;
  can_share: boolean;
  can_export: boolean;
  created_at: string;
}

export interface ObjectPermissionCreate {
  object_type: string;
  object_id: string;
  user_id?: string;
  role?: WorkspaceRole;
  can_view?: boolean;
  can_edit?: boolean;
  can_delete?: boolean;
  can_share?: boolean;
  can_export?: boolean;
}

export interface PermissionCheck {
  object_type: string;
  object_id: string;
  action: string;
}

export interface PermissionCheckResponse {
  allowed: boolean;
  reason?: string;
}

// Settings Types

export interface WorkspaceSettings {
  allow_member_invite: boolean;
  allow_viewer_export: boolean;
  require_approval_for_publish: boolean;
  default_dashboard_visibility: 'workspace' | 'private';
  default_connection_visibility: 'workspace' | 'private';
  enable_audit_logging: boolean;
  data_retention_days?: number;
}

// Role Permissions

export interface RolePermissions {
  can_manage_workspace: boolean;
  can_manage_members: boolean;
  can_manage_billing: boolean;
  can_create_content: boolean;
  can_edit_all_content: boolean;
  can_delete_all_content: boolean;
  can_share_content: boolean;
  can_export_data: boolean;
  can_manage_connections: boolean;
  can_view_audit_logs: boolean;
}

// Constants

export const ROLE_LABELS: Record<WorkspaceRole, string> = {
  owner: 'Owner',
  admin: 'Admin',
  member: 'Member',
  viewer: 'Viewer',
};

export const ROLE_DESCRIPTIONS: Record<WorkspaceRole, string> = {
  owner: 'Full control over the workspace including deletion and ownership transfer',
  admin: 'Can manage members and all content, but cannot delete the workspace',
  member: 'Can create and manage their own content',
  viewer: 'Can only view content shared with the workspace',
};

export const ROLE_COLORS: Record<WorkspaceRole, string> = {
  owner: 'purple',
  admin: 'blue',
  member: 'green',
  viewer: 'gray',
};

export const INVITE_STATUS_LABELS: Record<InviteStatus, string> = {
  pending: 'Pending',
  accepted: 'Accepted',
  declined: 'Declined',
  expired: 'Expired',
};

export const INVITE_STATUS_COLORS: Record<InviteStatus, string> = {
  pending: 'yellow',
  accepted: 'green',
  declined: 'red',
  expired: 'gray',
};

export const DEFAULT_ROLE_PERMISSIONS: Record<WorkspaceRole, RolePermissions> = {
  owner: {
    can_manage_workspace: true,
    can_manage_members: true,
    can_manage_billing: true,
    can_create_content: true,
    can_edit_all_content: true,
    can_delete_all_content: true,
    can_share_content: true,
    can_export_data: true,
    can_manage_connections: true,
    can_view_audit_logs: true,
  },
  admin: {
    can_manage_workspace: false,
    can_manage_members: true,
    can_manage_billing: false,
    can_create_content: true,
    can_edit_all_content: true,
    can_delete_all_content: true,
    can_share_content: true,
    can_export_data: true,
    can_manage_connections: true,
    can_view_audit_logs: true,
  },
  member: {
    can_manage_workspace: false,
    can_manage_members: false,
    can_manage_billing: false,
    can_create_content: true,
    can_edit_all_content: false,
    can_delete_all_content: false,
    can_share_content: true,
    can_export_data: true,
    can_manage_connections: false,
    can_view_audit_logs: false,
  },
  viewer: {
    can_manage_workspace: false,
    can_manage_members: false,
    can_manage_billing: false,
    can_create_content: false,
    can_edit_all_content: false,
    can_delete_all_content: false,
    can_share_content: false,
    can_export_data: false,
    can_manage_connections: false,
    can_view_audit_logs: false,
  },
};

// Helper Functions

export function getRoleLabel(role: WorkspaceRole): string {
  return ROLE_LABELS[role];
}

export function getRoleColor(role: WorkspaceRole): string {
  return ROLE_COLORS[role];
}

export function canPerformAction(role: WorkspaceRole, action: keyof RolePermissions): boolean {
  return DEFAULT_ROLE_PERMISSIONS[role][action];
}

export function isRoleHigherOrEqual(role1: WorkspaceRole, role2: WorkspaceRole): boolean {
  const hierarchy: WorkspaceRole[] = ['owner', 'admin', 'member', 'viewer'];
  return hierarchy.indexOf(role1) <= hierarchy.indexOf(role2);
}

export function getAvailableRolesForAssignment(currentUserRole: WorkspaceRole): WorkspaceRole[] {
  const hierarchy: WorkspaceRole[] = ['owner', 'admin', 'member', 'viewer'];
  const currentIndex = hierarchy.indexOf(currentUserRole);

  // Can only assign roles equal or lower than current role
  // Owners can assign any role, admins can assign admin or lower
  if (currentUserRole === 'owner') {
    return ['admin', 'member', 'viewer'];
  }
  if (currentUserRole === 'admin') {
    return ['admin', 'member', 'viewer'];
  }
  return [];
}

export function createDefaultWorkspace(name: string): WorkspaceCreate {
  return {
    name,
    settings: {
      allow_member_invite: true,
      allow_viewer_export: false,
      require_approval_for_publish: false,
      default_dashboard_visibility: 'workspace',
      default_connection_visibility: 'workspace',
      enable_audit_logging: true,
    },
  };
}

export function formatMemberJoinDate(joinedAt: string): string {
  const date = new Date(joinedAt);
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatLastAccessed(lastAccessedAt?: string): string {
  if (!lastAccessedAt) return 'Never';

  const date = new Date(lastAccessedAt);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}
