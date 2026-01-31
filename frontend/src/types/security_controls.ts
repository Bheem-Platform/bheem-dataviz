/**
 * Advanced Security Controls Types
 *
 * TypeScript types for rate limiting, IP policies, session security,
 * password policies, API keys, and security configurations.
 */

// Enums

export enum RateLimitScope {
  GLOBAL = 'global',
  USER = 'user',
  IP = 'ip',
  API_KEY = 'api_key',
  ENDPOINT = 'endpoint',
}

export enum RateLimitAction {
  BLOCK = 'block',
  THROTTLE = 'throttle',
  LOG_ONLY = 'log_only',
  CHALLENGE = 'challenge',
}

export enum IPListType {
  ALLOWLIST = 'allowlist',
  BLOCKLIST = 'blocklist',
}

export enum IPMatchType {
  EXACT = 'exact',
  CIDR = 'cidr',
  RANGE = 'range',
  COUNTRY = 'country',
}

export enum SessionRisk {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum APIKeyStatus {
  ACTIVE = 'active',
  EXPIRED = 'expired',
  REVOKED = 'revoked',
  SUSPENDED = 'suspended',
}

export enum SecurityEventType {
  LOGIN_SUCCESS = 'login_success',
  LOGIN_FAILURE = 'login_failure',
  LOGOUT = 'logout',
  PASSWORD_CHANGE = 'password_change',
  MFA_ENABLED = 'mfa_enabled',
  MFA_DISABLED = 'mfa_disabled',
  API_KEY_CREATED = 'api_key_created',
  API_KEY_REVOKED = 'api_key_revoked',
  RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded',
  IP_BLOCKED = 'ip_blocked',
  SUSPICIOUS_ACTIVITY = 'suspicious_activity',
  PERMISSION_DENIED = 'permission_denied',
  DATA_EXPORT = 'data_export',
  ADMIN_ACTION = 'admin_action',
}

export enum SecurityRiskLevel {
  NONE = 'none',
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

// Rate Limiting Interfaces

export interface RateLimitRule {
  id: string;
  name: string;
  description?: string;
  scope: RateLimitScope;
  endpoint_pattern?: string;
  requests_per_minute: number;
  requests_per_hour: number;
  requests_per_day: number;
  burst_limit: number;
  action: RateLimitAction;
  retry_after_seconds: number;
  enabled: boolean;
  priority: number;
  exemptions: string[];
  created_at: string;
  updated_at: string;
}

export interface RateLimitRuleCreate {
  name: string;
  description?: string;
  scope: RateLimitScope;
  endpoint_pattern?: string;
  requests_per_minute?: number;
  requests_per_hour?: number;
  requests_per_day?: number;
  burst_limit?: number;
  action?: RateLimitAction;
  retry_after_seconds?: number;
  enabled?: boolean;
  priority?: number;
  exemptions?: string[];
}

export interface RateLimitRuleUpdate {
  name?: string;
  description?: string;
  endpoint_pattern?: string;
  requests_per_minute?: number;
  requests_per_hour?: number;
  requests_per_day?: number;
  burst_limit?: number;
  action?: RateLimitAction;
  retry_after_seconds?: number;
  enabled?: boolean;
  priority?: number;
  exemptions?: string[];
}

export interface RateLimitStatus {
  user_id?: string;
  ip_address: string;
  api_key?: string;
  endpoint: string;
  requests_this_minute: number;
  requests_this_hour: number;
  requests_today: number;
  limit_reached: boolean;
  retry_after?: number;
  reset_at: string;
}

export interface RateLimitRuleListResponse {
  rules: RateLimitRule[];
  total: number;
}

// IP Policy Interfaces

export interface IPRule {
  id: string;
  list_type: IPListType;
  match_type: IPMatchType;
  value: string;
  description?: string;
  organization_id?: string;
  expires_at?: string;
  enabled: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface IPRuleCreate {
  list_type: IPListType;
  match_type: IPMatchType;
  value: string;
  description?: string;
  organization_id?: string;
  expires_at?: string;
  enabled?: boolean;
}

export interface IPRuleUpdate {
  description?: string;
  expires_at?: string;
  enabled?: boolean;
}

export interface IPCheckResult {
  ip_address: string;
  allowed: boolean;
  matched_rule?: IPRule;
  country_code?: string;
  is_vpn: boolean;
  is_tor: boolean;
  is_proxy: boolean;
  risk_score: number;
}

export interface IPRuleListResponse {
  rules: IPRule[];
  total: number;
}

// Session Security Interfaces

export interface SessionConfig {
  organization_id: string;
  max_concurrent_sessions: number;
  session_timeout_minutes: number;
  idle_timeout_minutes: number;
  require_reauthentication_minutes: number;
  bind_to_ip: boolean;
  bind_to_device: boolean;
  detect_concurrent_logins: boolean;
  terminate_other_sessions_on_login: boolean;
  require_mfa_for_new_device: boolean;
  high_risk_actions_require_reauth: boolean;
  updated_at: string;
}

export interface SessionConfigUpdate {
  max_concurrent_sessions?: number;
  session_timeout_minutes?: number;
  idle_timeout_minutes?: number;
  require_reauthentication_minutes?: number;
  bind_to_ip?: boolean;
  bind_to_device?: boolean;
  detect_concurrent_logins?: boolean;
  terminate_other_sessions_on_login?: boolean;
  require_mfa_for_new_device?: boolean;
  high_risk_actions_require_reauth?: boolean;
}

export interface ActiveSession {
  id: string;
  user_id: string;
  ip_address: string;
  user_agent: string;
  device_type: string;
  browser?: string;
  os?: string;
  location?: string;
  created_at: string;
  last_activity_at: string;
  expires_at: string;
  is_current: boolean;
  risk_level: SessionRisk;
}

export interface SessionListResponse {
  sessions: ActiveSession[];
  total: number;
}

// Password Policy Interfaces

export interface PasswordPolicy {
  organization_id: string;
  min_length: number;
  max_length: number;
  require_uppercase: boolean;
  require_lowercase: boolean;
  require_numbers: boolean;
  require_special_chars: boolean;
  special_chars_allowed: string;
  disallow_common_passwords: boolean;
  disallow_personal_info: boolean;
  password_history_count: number;
  max_age_days: number;
  min_age_days: number;
  lockout_threshold: number;
  lockout_duration_minutes: number;
  require_password_change_on_first_login: boolean;
  updated_at: string;
}

export interface PasswordPolicyUpdate {
  min_length?: number;
  max_length?: number;
  require_uppercase?: boolean;
  require_lowercase?: boolean;
  require_numbers?: boolean;
  require_special_chars?: boolean;
  special_chars_allowed?: string;
  disallow_common_passwords?: boolean;
  disallow_personal_info?: boolean;
  password_history_count?: number;
  max_age_days?: number;
  min_age_days?: number;
  lockout_threshold?: number;
  lockout_duration_minutes?: number;
  require_password_change_on_first_login?: boolean;
}

export interface PasswordValidationResult {
  valid: boolean;
  errors: string[];
  strength_score: number;
  strength_label: string;
  suggestions: string[];
}

export interface PasswordStrengthCheck {
  password: string;
  user_email?: string;
  user_name?: string;
}

// API Key Interfaces

export interface APIKey {
  id: string;
  name: string;
  description?: string;
  key_prefix: string;
  key_hash: string;
  user_id: string;
  organization_id?: string;
  status: APIKeyStatus;
  permissions: string[];
  rate_limit_override?: number;
  allowed_ips: string[];
  allowed_origins: string[];
  expires_at?: string;
  last_used_at?: string;
  last_used_ip?: string;
  usage_count: number;
  created_at: string;
  revoked_at?: string;
  revoked_by?: string;
}

export interface APIKeyCreate {
  name: string;
  description?: string;
  permissions?: string[];
  rate_limit_override?: number;
  allowed_ips?: string[];
  allowed_origins?: string[];
  expires_at?: string;
}

export interface APIKeyCreateResponse {
  api_key: APIKey;
  key: string;
  warning: string;
}

export interface APIKeyUpdate {
  name?: string;
  description?: string;
  permissions?: string[];
  rate_limit_override?: number;
  allowed_ips?: string[];
  allowed_origins?: string[];
  expires_at?: string;
}

export interface APIKeyListResponse {
  api_keys: APIKey[];
  total: number;
}

export interface APIKeyUsageStats {
  api_key_id: string;
  total_requests: number;
  requests_today: number;
  requests_this_week: number;
  requests_this_month: number;
  unique_ips: number;
  last_used_at?: string;
  requests_by_endpoint: Record<string, number>;
  requests_by_day: Array<Record<string, unknown>>;
}

// Security Event Interfaces

export interface SecurityEvent {
  id: string;
  event_type: SecurityEventType;
  user_id?: string;
  organization_id?: string;
  ip_address: string;
  user_agent?: string;
  resource_type?: string;
  resource_id?: string;
  action: string;
  success: boolean;
  risk_level: SecurityRiskLevel;
  details: Record<string, unknown>;
  created_at: string;
}

export interface SecurityEventListResponse {
  events: SecurityEvent[];
  total: number;
}

// CORS & Security Headers Interfaces

export interface CORSConfig {
  organization_id: string;
  allowed_origins: string[];
  allowed_methods: string[];
  allowed_headers: string[];
  exposed_headers: string[];
  allow_credentials: boolean;
  max_age_seconds: number;
  enabled: boolean;
  updated_at: string;
}

export interface CORSConfigUpdate {
  allowed_origins?: string[];
  allowed_methods?: string[];
  allowed_headers?: string[];
  exposed_headers?: string[];
  allow_credentials?: boolean;
  max_age_seconds?: number;
  enabled?: boolean;
}

export interface CSPConfig {
  organization_id: string;
  default_src: string[];
  script_src: string[];
  style_src: string[];
  img_src: string[];
  font_src: string[];
  connect_src: string[];
  frame_src: string[];
  object_src: string[];
  base_uri: string[];
  form_action: string[];
  report_uri?: string;
  report_only: boolean;
  enabled: boolean;
  updated_at: string;
}

export interface CSPConfigUpdate {
  default_src?: string[];
  script_src?: string[];
  style_src?: string[];
  img_src?: string[];
  font_src?: string[];
  connect_src?: string[];
  frame_src?: string[];
  object_src?: string[];
  base_uri?: string[];
  form_action?: string[];
  report_uri?: string;
  report_only?: boolean;
  enabled?: boolean;
}

export interface SecurityHeaders {
  organization_id: string;
  x_frame_options: string;
  x_content_type_options: string;
  x_xss_protection: string;
  strict_transport_security: string;
  referrer_policy: string;
  permissions_policy?: string;
  custom_headers: Record<string, string>;
  enabled: boolean;
  updated_at: string;
}

export interface SecurityHeadersUpdate {
  x_frame_options?: string;
  x_content_type_options?: string;
  x_xss_protection?: string;
  strict_transport_security?: string;
  referrer_policy?: string;
  permissions_policy?: string;
  custom_headers?: Record<string, string>;
  enabled?: boolean;
}

// Security Overview Interfaces

export interface SecurityOverview {
  organization_id: string;
  security_score: number;
  mfa_adoption_percent: number;
  api_keys_active: number;
  blocked_ips_count: number;
  rate_limit_violations_today: number;
  failed_logins_today: number;
  suspicious_activities_today: number;
  password_policy_compliant_percent: number;
  sessions_active: number;
  last_security_incident?: string;
  recommendations: string[];
}

export interface SecurityRecommendation {
  id: string;
  title: string;
  description: string;
  severity: SecurityRiskLevel;
  category: string;
  action_url?: string;
  dismissed: boolean;
}

// Constants

export const RATE_LIMIT_SCOPE_LABELS: Record<RateLimitScope, string> = {
  [RateLimitScope.GLOBAL]: 'Global',
  [RateLimitScope.USER]: 'Per User',
  [RateLimitScope.IP]: 'Per IP Address',
  [RateLimitScope.API_KEY]: 'Per API Key',
  [RateLimitScope.ENDPOINT]: 'Per Endpoint',
};

export const RATE_LIMIT_ACTION_LABELS: Record<RateLimitAction, string> = {
  [RateLimitAction.BLOCK]: 'Block Request',
  [RateLimitAction.THROTTLE]: 'Throttle',
  [RateLimitAction.LOG_ONLY]: 'Log Only',
  [RateLimitAction.CHALLENGE]: 'Challenge (CAPTCHA)',
};

export const IP_LIST_TYPE_LABELS: Record<IPListType, string> = {
  [IPListType.ALLOWLIST]: 'Allowlist',
  [IPListType.BLOCKLIST]: 'Blocklist',
};

export const SESSION_RISK_LABELS: Record<SessionRisk, string> = {
  [SessionRisk.LOW]: 'Low Risk',
  [SessionRisk.MEDIUM]: 'Medium Risk',
  [SessionRisk.HIGH]: 'High Risk',
  [SessionRisk.CRITICAL]: 'Critical Risk',
};

export const API_KEY_STATUS_LABELS: Record<APIKeyStatus, string> = {
  [APIKeyStatus.ACTIVE]: 'Active',
  [APIKeyStatus.EXPIRED]: 'Expired',
  [APIKeyStatus.REVOKED]: 'Revoked',
  [APIKeyStatus.SUSPENDED]: 'Suspended',
};

export const SECURITY_EVENT_LABELS: Record<SecurityEventType, string> = {
  [SecurityEventType.LOGIN_SUCCESS]: 'Login Success',
  [SecurityEventType.LOGIN_FAILURE]: 'Login Failure',
  [SecurityEventType.LOGOUT]: 'Logout',
  [SecurityEventType.PASSWORD_CHANGE]: 'Password Changed',
  [SecurityEventType.MFA_ENABLED]: 'MFA Enabled',
  [SecurityEventType.MFA_DISABLED]: 'MFA Disabled',
  [SecurityEventType.API_KEY_CREATED]: 'API Key Created',
  [SecurityEventType.API_KEY_REVOKED]: 'API Key Revoked',
  [SecurityEventType.RATE_LIMIT_EXCEEDED]: 'Rate Limit Exceeded',
  [SecurityEventType.IP_BLOCKED]: 'IP Blocked',
  [SecurityEventType.SUSPICIOUS_ACTIVITY]: 'Suspicious Activity',
  [SecurityEventType.PERMISSION_DENIED]: 'Permission Denied',
  [SecurityEventType.DATA_EXPORT]: 'Data Export',
  [SecurityEventType.ADMIN_ACTION]: 'Admin Action',
};

export const SECURITY_RISK_LABELS: Record<SecurityRiskLevel, string> = {
  [SecurityRiskLevel.NONE]: 'None',
  [SecurityRiskLevel.LOW]: 'Low',
  [SecurityRiskLevel.MEDIUM]: 'Medium',
  [SecurityRiskLevel.HIGH]: 'High',
  [SecurityRiskLevel.CRITICAL]: 'Critical',
};

// Helper Functions

export function getRateLimitActionColor(action: RateLimitAction): string {
  const colors: Record<RateLimitAction, string> = {
    [RateLimitAction.BLOCK]: 'red',
    [RateLimitAction.THROTTLE]: 'orange',
    [RateLimitAction.LOG_ONLY]: 'blue',
    [RateLimitAction.CHALLENGE]: 'yellow',
  };
  return colors[action] || 'gray';
}

export function getIPListTypeColor(type: IPListType): string {
  return type === IPListType.ALLOWLIST ? 'green' : 'red';
}

export function getSessionRiskColor(risk: SessionRisk): string {
  const colors: Record<SessionRisk, string> = {
    [SessionRisk.LOW]: 'green',
    [SessionRisk.MEDIUM]: 'yellow',
    [SessionRisk.HIGH]: 'orange',
    [SessionRisk.CRITICAL]: 'red',
  };
  return colors[risk] || 'gray';
}

export function getAPIKeyStatusColor(status: APIKeyStatus): string {
  const colors: Record<APIKeyStatus, string> = {
    [APIKeyStatus.ACTIVE]: 'green',
    [APIKeyStatus.EXPIRED]: 'gray',
    [APIKeyStatus.REVOKED]: 'red',
    [APIKeyStatus.SUSPENDED]: 'yellow',
  };
  return colors[status] || 'gray';
}

export function getSecurityRiskColor(level: SecurityRiskLevel): string {
  const colors: Record<SecurityRiskLevel, string> = {
    [SecurityRiskLevel.NONE]: 'gray',
    [SecurityRiskLevel.LOW]: 'blue',
    [SecurityRiskLevel.MEDIUM]: 'yellow',
    [SecurityRiskLevel.HIGH]: 'orange',
    [SecurityRiskLevel.CRITICAL]: 'red',
  };
  return colors[level] || 'gray';
}

export function getSecurityEventIcon(type: SecurityEventType): string {
  const icons: Record<SecurityEventType, string> = {
    [SecurityEventType.LOGIN_SUCCESS]: 'log-in',
    [SecurityEventType.LOGIN_FAILURE]: 'x-circle',
    [SecurityEventType.LOGOUT]: 'log-out',
    [SecurityEventType.PASSWORD_CHANGE]: 'key',
    [SecurityEventType.MFA_ENABLED]: 'shield',
    [SecurityEventType.MFA_DISABLED]: 'shield-off',
    [SecurityEventType.API_KEY_CREATED]: 'plus-circle',
    [SecurityEventType.API_KEY_REVOKED]: 'minus-circle',
    [SecurityEventType.RATE_LIMIT_EXCEEDED]: 'zap-off',
    [SecurityEventType.IP_BLOCKED]: 'ban',
    [SecurityEventType.SUSPICIOUS_ACTIVITY]: 'alert-triangle',
    [SecurityEventType.PERMISSION_DENIED]: 'lock',
    [SecurityEventType.DATA_EXPORT]: 'download',
    [SecurityEventType.ADMIN_ACTION]: 'settings',
  };
  return icons[type] || 'activity';
}

export function formatPasswordStrength(score: number): { label: string; color: string } {
  if (score >= 80) return { label: 'Excellent', color: 'green' };
  if (score >= 60) return { label: 'Strong', color: 'blue' };
  if (score >= 40) return { label: 'Good', color: 'yellow' };
  if (score >= 20) return { label: 'Fair', color: 'orange' };
  return { label: 'Weak', color: 'red' };
}

export function formatSecurityScore(score: number): { label: string; color: string } {
  if (score >= 80) return { label: 'Excellent', color: 'green' };
  if (score >= 60) return { label: 'Good', color: 'blue' };
  if (score >= 40) return { label: 'Fair', color: 'yellow' };
  if (score >= 20) return { label: 'Poor', color: 'orange' };
  return { label: 'Critical', color: 'red' };
}

export function formatRateLimit(
  requestsPerMinute: number,
  requestsPerHour: number,
  requestsPerDay: number
): string {
  const parts: string[] = [];
  if (requestsPerMinute) parts.push(`${requestsPerMinute}/min`);
  if (requestsPerHour) parts.push(`${requestsPerHour}/hr`);
  if (requestsPerDay) parts.push(`${requestsPerDay}/day`);
  return parts.join(', ');
}

export function formatAPIKeyPrefix(key: APIKey): string {
  return `${key.key_prefix}...`;
}

export function isAPIKeyExpiringSoon(key: APIKey, daysThreshold: number = 7): boolean {
  if (!key.expires_at) return false;
  const expiryDate = new Date(key.expires_at);
  const now = new Date();
  const diffDays = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  return diffDays > 0 && diffDays <= daysThreshold;
}

export function formatSessionDuration(session: ActiveSession): string {
  const created = new Date(session.created_at);
  const now = new Date();
  const diffMs = now.getTime() - created.getTime();
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

export function formatDeviceInfo(session: ActiveSession): string {
  const parts: string[] = [];
  if (session.browser) parts.push(session.browser);
  if (session.os) parts.push(`on ${session.os}`);
  if (session.location) parts.push(`from ${session.location}`);
  return parts.join(' ') || session.device_type;
}

export function getPasswordPolicyDescription(policy: PasswordPolicy): string[] {
  const requirements: string[] = [];
  requirements.push(`Minimum ${policy.min_length} characters`);
  if (policy.require_uppercase) requirements.push('At least one uppercase letter');
  if (policy.require_lowercase) requirements.push('At least one lowercase letter');
  if (policy.require_numbers) requirements.push('At least one number');
  if (policy.require_special_chars) requirements.push('At least one special character');
  if (policy.disallow_common_passwords) requirements.push('Cannot be a common password');
  if (policy.password_history_count > 0) {
    requirements.push(`Cannot reuse last ${policy.password_history_count} passwords`);
  }
  return requirements;
}

export function calculateSessionsAtRisk(sessions: ActiveSession[]): number {
  return sessions.filter(
    (s) => s.risk_level === SessionRisk.HIGH || s.risk_level === SessionRisk.CRITICAL
  ).length;
}
