/**
 * User & Role Management Types
 *
 * TypeScript types for user profiles, roles, permissions, sessions,
 * and administrative user management.
 */

// Enums

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
  PENDING_VERIFICATION = 'pending_verification',
  LOCKED = 'locked',
  DELETED = 'deleted',
}

export enum UserType {
  REGULAR = 'regular',
  ADMIN = 'admin',
  SERVICE = 'service',
  API = 'api',
  SYSTEM = 'system',
}

export enum AuthProvider {
  LOCAL = 'local',
  GOOGLE = 'google',
  GITHUB = 'github',
  MICROSOFT = 'microsoft',
  OKTA = 'okta',
  SAML = 'saml',
  LDAP = 'ldap',
}

export enum SessionStatus {
  ACTIVE = 'active',
  EXPIRED = 'expired',
  REVOKED = 'revoked',
  LOGGED_OUT = 'logged_out',
}

export enum PermissionScope {
  GLOBAL = 'global',
  WORKSPACE = 'workspace',
  RESOURCE = 'resource',
}

export enum AuditAction {
  LOGIN = 'login',
  LOGOUT = 'logout',
  LOGIN_FAILED = 'login_failed',
  PASSWORD_CHANGE = 'password_change',
  PASSWORD_RESET = 'password_reset',
  PROFILE_UPDATE = 'profile_update',
  MFA_ENABLED = 'mfa_enabled',
  MFA_DISABLED = 'mfa_disabled',
  ACCOUNT_LOCKED = 'account_locked',
  ACCOUNT_UNLOCKED = 'account_unlocked',
  SESSION_CREATED = 'session_created',
  SESSION_REVOKED = 'session_revoked',
  API_KEY_CREATED = 'api_key_created',
  API_KEY_REVOKED = 'api_key_revoked',
  PERMISSION_CHANGED = 'permission_changed',
}

// User Interfaces

export interface UserCreate {
  email: string;
  password?: string;
  name: string;
  display_name?: string;
  avatar_url?: string;
  user_type?: UserType;
  auth_provider?: AuthProvider;
  auth_provider_id?: string;
  phone?: string;
  timezone?: string;
  locale?: string;
  metadata?: Record<string, unknown>;
}

export interface User {
  id: string;
  email: string;
  name: string;
  display_name?: string;
  avatar_url?: string;
  user_type: UserType;
  status: UserStatus;
  auth_provider: AuthProvider;
  auth_provider_id?: string;
  phone?: string;
  timezone: string;
  locale: string;
  email_verified: boolean;
  phone_verified: boolean;
  mfa_enabled: boolean;
  mfa_method?: string;
  last_login_at?: string;
  last_active_at?: string;
  login_count: number;
  failed_login_count: number;
  locked_until?: string;
  password_changed_at?: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface UserUpdate {
  name?: string;
  display_name?: string;
  avatar_url?: string;
  phone?: string;
  timezone?: string;
  locale?: string;
  metadata?: Record<string, unknown>;
}

export interface UserAdminUpdate {
  name?: string;
  display_name?: string;
  email?: string;
  user_type?: UserType;
  status?: UserStatus;
  email_verified?: boolean;
  phone_verified?: boolean;
  mfa_enabled?: boolean;
  metadata?: Record<string, unknown>;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  display_name?: string;
  avatar_url?: string;
  timezone: string;
  locale: string;
  created_at: string;
}

export interface UserPreferences {
  user_id: string;
  theme: string;
  language: string;
  date_format: string;
  time_format: string;
  number_format: string;
  first_day_of_week: number;
  default_workspace_id?: string;
  notifications: Record<string, boolean>;
  email_notifications: Record<string, boolean>;
  dashboard_settings: Record<string, unknown>;
  chart_defaults: Record<string, unknown>;
}

export interface UserPreferencesUpdate {
  theme?: string;
  language?: string;
  date_format?: string;
  time_format?: string;
  number_format?: string;
  first_day_of_week?: number;
  default_workspace_id?: string;
  notifications?: Record<string, boolean>;
  email_notifications?: Record<string, boolean>;
  dashboard_settings?: Record<string, unknown>;
  chart_defaults?: Record<string, unknown>;
}

// Role Interfaces

export interface RoleCreate {
  name: string;
  description?: string;
  scope?: PermissionScope;
  permissions?: string[];
  is_system?: boolean;
  workspace_id?: string;
  metadata?: Record<string, unknown>;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  scope: PermissionScope;
  permissions: string[];
  is_system: boolean;
  is_default: boolean;
  workspace_id?: string;
  user_count: number;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface RoleUpdate {
  name?: string;
  description?: string;
  permissions?: string[];
  metadata?: Record<string, unknown>;
}

export interface RoleAssignment {
  id: string;
  user_id: string;
  role_id: string;
  role_name: string;
  workspace_id?: string;
  assigned_by: string;
  assigned_at: string;
  expires_at?: string;
}

export interface RoleAssignmentCreate {
  user_id: string;
  role_id: string;
  workspace_id?: string;
  expires_at?: string;
}

// Permission Interfaces

export interface Permission {
  id: string;
  name: string;
  code: string;
  description?: string;
  category: string;
  scope: PermissionScope;
  is_sensitive: boolean;
}

export interface PermissionGroup {
  id: string;
  name: string;
  description?: string;
  category: string;
  permissions: Permission[];
}

export interface UserPermissions {
  user_id: string;
  global_permissions: string[];
  workspace_permissions: Record<string, string[]>;
  effective_permissions: string[];
}

// Session Interfaces

export interface SessionCreate {
  user_id: string;
  device_info?: Record<string, unknown>;
  ip_address?: string;
  user_agent?: string;
}

export interface Session {
  id: string;
  user_id: string;
  status: SessionStatus;
  device_info: Record<string, unknown>;
  ip_address?: string;
  user_agent?: string;
  location?: string;
  is_current: boolean;
  last_activity_at: string;
  expires_at: string;
  created_at: string;
  revoked_at?: string;
  revoked_reason?: string;
}

export interface SessionInfo {
  id: string;
  device_type: string;
  browser?: string;
  os?: string;
  location?: string;
  ip_address?: string;
  is_current: boolean;
  last_activity_at: string;
  created_at: string;
}

// MFA Interfaces

export interface MFASetup {
  secret: string;
  qr_code_url: string;
  backup_codes: string[];
}

export interface MFAVerify {
  code: string;
}

export interface MFABackupCodes {
  codes: string[];
  generated_at: string;
}

// Password Interfaces

export interface PasswordChange {
  current_password: string;
  new_password: string;
}

export interface PasswordReset {
  token: string;
  new_password: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordPolicy {
  min_length: number;
  max_length: number;
  require_uppercase: boolean;
  require_lowercase: boolean;
  require_numbers: boolean;
  require_special_chars: boolean;
  special_chars: string;
  disallow_common: boolean;
  disallow_username: boolean;
  max_age_days: number;
  history_count: number;
  lockout_threshold: number;
  lockout_duration_minutes: number;
}

// Audit Interfaces

export interface AuditLogEntry {
  id: string;
  user_id: string;
  user_email: string;
  action: AuditAction;
  resource_type?: string;
  resource_id?: string;
  details: Record<string, unknown>;
  ip_address?: string;
  user_agent?: string;
  location?: string;
  success: boolean;
  error_message?: string;
  created_at: string;
}

export interface AuditLogQuery {
  user_id?: string;
  action?: AuditAction;
  resource_type?: string;
  success?: boolean;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}

// Response Interfaces

export interface UserListResponse {
  users: User[];
  total: number;
}

export interface RoleListResponse {
  roles: Role[];
  total: number;
}

export interface SessionListResponse {
  sessions: SessionInfo[];
  total: number;
}

export interface AuditLogResponse {
  entries: AuditLogEntry[];
  total: number;
}

export interface PermissionListResponse {
  permissions: Permission[];
  groups: PermissionGroup[];
}

// Auth Interfaces

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
  mfa_required: boolean;
  mfa_token?: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  expires_in: number;
}

// Statistics Interface

export interface UserStatistics {
  total_users: number;
  active_users: number;
  inactive_users: number;
  locked_users: number;
  pending_verification: number;
  users_by_type: Record<string, number>;
  users_by_provider: Record<string, number>;
  mfa_enabled_count: number;
  new_users_today: number;
  new_users_this_week: number;
  new_users_this_month: number;
  active_sessions: number;
}

// Constants

export const USER_STATUS_LABELS: Record<UserStatus, string> = {
  [UserStatus.ACTIVE]: 'Active',
  [UserStatus.INACTIVE]: 'Inactive',
  [UserStatus.SUSPENDED]: 'Suspended',
  [UserStatus.PENDING_VERIFICATION]: 'Pending Verification',
  [UserStatus.LOCKED]: 'Locked',
  [UserStatus.DELETED]: 'Deleted',
};

export const USER_TYPE_LABELS: Record<UserType, string> = {
  [UserType.REGULAR]: 'Regular',
  [UserType.ADMIN]: 'Admin',
  [UserType.SERVICE]: 'Service Account',
  [UserType.API]: 'API User',
  [UserType.SYSTEM]: 'System',
};

export const AUTH_PROVIDER_LABELS: Record<AuthProvider, string> = {
  [AuthProvider.LOCAL]: 'Email/Password',
  [AuthProvider.GOOGLE]: 'Google',
  [AuthProvider.GITHUB]: 'GitHub',
  [AuthProvider.MICROSOFT]: 'Microsoft',
  [AuthProvider.OKTA]: 'Okta',
  [AuthProvider.SAML]: 'SAML SSO',
  [AuthProvider.LDAP]: 'LDAP',
};

export const SESSION_STATUS_LABELS: Record<SessionStatus, string> = {
  [SessionStatus.ACTIVE]: 'Active',
  [SessionStatus.EXPIRED]: 'Expired',
  [SessionStatus.REVOKED]: 'Revoked',
  [SessionStatus.LOGGED_OUT]: 'Logged Out',
};

export const PERMISSION_SCOPE_LABELS: Record<PermissionScope, string> = {
  [PermissionScope.GLOBAL]: 'Global',
  [PermissionScope.WORKSPACE]: 'Workspace',
  [PermissionScope.RESOURCE]: 'Resource',
};

export const AUDIT_ACTION_LABELS: Record<AuditAction, string> = {
  [AuditAction.LOGIN]: 'Login',
  [AuditAction.LOGOUT]: 'Logout',
  [AuditAction.LOGIN_FAILED]: 'Login Failed',
  [AuditAction.PASSWORD_CHANGE]: 'Password Changed',
  [AuditAction.PASSWORD_RESET]: 'Password Reset',
  [AuditAction.PROFILE_UPDATE]: 'Profile Updated',
  [AuditAction.MFA_ENABLED]: 'MFA Enabled',
  [AuditAction.MFA_DISABLED]: 'MFA Disabled',
  [AuditAction.ACCOUNT_LOCKED]: 'Account Locked',
  [AuditAction.ACCOUNT_UNLOCKED]: 'Account Unlocked',
  [AuditAction.SESSION_CREATED]: 'Session Created',
  [AuditAction.SESSION_REVOKED]: 'Session Revoked',
  [AuditAction.API_KEY_CREATED]: 'API Key Created',
  [AuditAction.API_KEY_REVOKED]: 'API Key Revoked',
  [AuditAction.PERMISSION_CHANGED]: 'Permission Changed',
};

export const PERMISSION_CATEGORIES = {
  profile: ['profile:read', 'profile:update'],
  users: ['users:read', 'users:create', 'users:update', 'users:delete', 'users:impersonate'],
  roles: ['roles:read', 'roles:create', 'roles:update', 'roles:delete', 'roles:assign'],
  workspaces: ['workspaces:read', 'workspaces:create', 'workspaces:update', 'workspaces:delete', 'workspaces:manage'],
  dashboards: ['dashboards:read', 'dashboards:create', 'dashboards:update', 'dashboards:delete', 'dashboards:share'],
  charts: ['charts:read', 'charts:create', 'charts:update', 'charts:delete'],
  connections: ['connections:read', 'connections:create', 'connections:update', 'connections:delete', 'connections:test'],
  datasets: ['datasets:read', 'datasets:create', 'datasets:update', 'datasets:delete'],
  queries: ['queries:execute', 'queries:read', 'queries:create', 'queries:update', 'queries:delete'],
  reports: ['reports:read', 'reports:create', 'reports:schedule', 'reports:export'],
  admin: ['admin:access', 'admin:settings', 'audit:read', 'system:manage'],
};

// Helper Functions

export function hasPermission(userPermissions: string[], required: string): boolean {
  if (userPermissions.includes('*')) return true;
  if (userPermissions.includes(required)) return true;
  const category = required.split(':')[0];
  if (userPermissions.includes(`${category}:*`)) return true;
  return false;
}

export function validatePassword(
  password: string,
  policy: PasswordPolicy
): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (password.length < policy.min_length) {
    errors.push(`Password must be at least ${policy.min_length} characters`);
  }
  if (password.length > policy.max_length) {
    errors.push(`Password must be at most ${policy.max_length} characters`);
  }
  if (policy.require_uppercase && !/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  if (policy.require_lowercase && !/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  if (policy.require_numbers && !/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  if (policy.require_special_chars && !new RegExp(`[${policy.special_chars.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&')}]`).test(password)) {
    errors.push(`Password must contain at least one special character (${policy.special_chars})`);
  }

  return { valid: errors.length === 0, errors };
}

export function getUserStatusColor(status: UserStatus): string {
  const colors: Record<UserStatus, string> = {
    [UserStatus.ACTIVE]: 'green',
    [UserStatus.INACTIVE]: 'gray',
    [UserStatus.SUSPENDED]: 'orange',
    [UserStatus.PENDING_VERIFICATION]: 'blue',
    [UserStatus.LOCKED]: 'red',
    [UserStatus.DELETED]: 'gray',
  };
  return colors[status] || 'gray';
}

export function getSessionDeviceIcon(deviceType: string): string {
  const icons: Record<string, string> = {
    desktop: '🖥️',
    mobile: '📱',
    tablet: '📱',
  };
  return icons[deviceType] || '💻';
}

export function formatLastActive(dateString: string): string {
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

export function getAuditActionIcon(action: AuditAction): string {
  const icons: Record<AuditAction, string> = {
    [AuditAction.LOGIN]: '🔓',
    [AuditAction.LOGOUT]: '🔒',
    [AuditAction.LOGIN_FAILED]: '❌',
    [AuditAction.PASSWORD_CHANGE]: '🔑',
    [AuditAction.PASSWORD_RESET]: '🔄',
    [AuditAction.PROFILE_UPDATE]: '✏️',
    [AuditAction.MFA_ENABLED]: '🛡️',
    [AuditAction.MFA_DISABLED]: '🔓',
    [AuditAction.ACCOUNT_LOCKED]: '🔒',
    [AuditAction.ACCOUNT_UNLOCKED]: '🔓',
    [AuditAction.SESSION_CREATED]: '➕',
    [AuditAction.SESSION_REVOKED]: '➖',
    [AuditAction.API_KEY_CREATED]: '🔑',
    [AuditAction.API_KEY_REVOKED]: '🗑️',
    [AuditAction.PERMISSION_CHANGED]: '👥',
  };
  return icons[action] || '📝';
}

export function getPermissionCategory(permission: string): string {
  return permission.split(':')[0];
}

export function getPermissionAction(permission: string): string {
  return permission.split(':')[1] || '';
}
