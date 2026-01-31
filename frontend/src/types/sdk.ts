/**
 * SDK & API Management Types
 *
 * TypeScript types for API keys, usage tracking, rate limits, and code generation.
 */

// Enums

export enum APIKeyType {
  PUBLIC = 'public',
  PRIVATE = 'private',
  RESTRICTED = 'restricted',
}

export enum APIKeyStatus {
  ACTIVE = 'active',
  REVOKED = 'revoked',
  EXPIRED = 'expired',
  SUSPENDED = 'suspended',
}

export enum SDKLanguage {
  JAVASCRIPT = 'javascript',
  TYPESCRIPT = 'typescript',
  PYTHON = 'python',
  REACT = 'react',
  VUE = 'vue',
  ANGULAR = 'angular',
  CURL = 'curl',
  GO = 'go',
  RUBY = 'ruby',
  PHP = 'php',
}

export enum EndpointCategory {
  AUTH = 'auth',
  CONNECTIONS = 'connections',
  DASHBOARDS = 'dashboards',
  CHARTS = 'charts',
  QUERIES = 'queries',
  DATASETS = 'datasets',
  TRANSFORMS = 'transforms',
  MODELS = 'models',
  KPI = 'kpi',
  AI = 'ai',
  ADMIN = 'admin',
}

export enum RateLimitPeriod {
  SECOND = 'second',
  MINUTE = 'minute',
  HOUR = 'hour',
  DAY = 'day',
  MONTH = 'month',
}

// API Key Types

export interface APIKeyPermissions {
  can_read_dashboards: boolean;
  can_write_dashboards: boolean;
  can_read_charts: boolean;
  can_write_charts: boolean;
  can_read_connections: boolean;
  can_write_connections: boolean;
  can_execute_queries: boolean;
  can_read_datasets: boolean;
  can_write_datasets: boolean;
  can_read_transforms: boolean;
  can_write_transforms: boolean;
  can_read_models: boolean;
  can_write_models: boolean;
  can_use_ai: boolean;
  can_embed: boolean;
  can_export: boolean;
  can_admin: boolean;
  workspace_ids: string[];
  dashboard_ids: string[];
}

export interface RateLimitConfig {
  requests_per_second?: number | null;
  requests_per_minute?: number | null;
  requests_per_hour?: number | null;
  requests_per_day?: number | null;
  requests_per_month?: number | null;
  burst_limit: number;
  enabled: boolean;
}

export interface APIKey {
  id: string;
  name: string;
  description?: string | null;
  key_prefix: string;
  key_hash: string;
  key_type: APIKeyType;
  status: APIKeyStatus;
  user_id: string;
  workspace_id?: string | null;
  organization_id?: string | null;
  permissions: APIKeyPermissions;
  rate_limits: RateLimitConfig;
  allowed_ips: string[];
  allowed_domains: string[];
  allowed_referrers: string[];
  expires_at?: string | null;
  last_used_at?: string | null;
  created_at: string;
  updated_at?: string | null;
  created_by: string;
  tags: string[];
  metadata: Record<string, unknown>;
}

export interface APIKeyCreate {
  name: string;
  description?: string | null;
  key_type?: APIKeyType;
  workspace_id?: string | null;
  permissions?: Partial<APIKeyPermissions> | null;
  rate_limits?: Partial<RateLimitConfig> | null;
  allowed_ips?: string[];
  allowed_domains?: string[];
  expires_in_days?: number | null;
  tags?: string[];
}

export interface APIKeyUpdate {
  name?: string | null;
  description?: string | null;
  permissions?: Partial<APIKeyPermissions> | null;
  rate_limits?: Partial<RateLimitConfig> | null;
  allowed_ips?: string[] | null;
  allowed_domains?: string[] | null;
  status?: APIKeyStatus | null;
  tags?: string[] | null;
}

export interface APIKeyResponse {
  api_key: APIKey;
  key?: string | null; // Full key only on creation
}

export interface APIKeyListResponse {
  keys: APIKey[];
  total: number;
}

// Usage Tracking Types

export interface UsageRecord {
  id: string;
  api_key_id: string;
  endpoint: string;
  method: string;
  status_code: number;
  response_time_ms: number;
  request_size_bytes: number;
  response_size_bytes: number;
  ip_address?: string | null;
  user_agent?: string | null;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface UsageStats {
  api_key_id: string;
  period_start: string;
  period_end: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  rate_limited_requests: number;
  requests_by_endpoint: Record<string, number>;
  requests_by_method: Record<string, number>;
  requests_by_status: Record<number, number>;
  avg_response_time_ms: number;
  p50_response_time_ms: number;
  p95_response_time_ms: number;
  p99_response_time_ms: number;
  total_request_bytes: number;
  total_response_bytes: number;
  unique_ips: number;
  unique_endpoints: number;
}

export interface UsageStatsResponse {
  stats: UsageStats;
  daily_breakdown: Array<{
    date: string;
    requests: number;
    errors: number;
  }>;
  top_endpoints: Array<{
    endpoint: string;
    count: number;
  }>;
}

// Rate Limit Types

export interface RateLimitStatus {
  api_key_id: string;
  period: RateLimitPeriod;
  limit: number;
  remaining: number;
  reset_at: string;
  is_limited: boolean;
}

// Code Generation Types

export interface CodeSnippet {
  language: SDKLanguage;
  code: string;
  filename?: string | null;
  description?: string | null;
  dependencies: string[];
}

export interface CodeGenerationRequest {
  language: SDKLanguage;
  resource_type: string;
  resource_id: string;
  include_auth?: boolean;
  include_error_handling?: boolean;
  include_types?: boolean;
  options?: Record<string, unknown>;
}

export interface CodeGenerationResponse {
  snippets: CodeSnippet[];
  setup_instructions: string;
  documentation_url?: string | null;
}

// API Documentation Types

export interface APIParameter {
  name: string;
  type: string;
  required: boolean;
  description?: string | null;
  default?: unknown;
  enum_values: string[];
  example?: unknown;
}

export interface APIEndpoint {
  path: string;
  method: string;
  summary: string;
  description?: string | null;
  category: EndpointCategory;
  tags: string[];
  path_params: APIParameter[];
  query_params: APIParameter[];
  body_schema?: Record<string, unknown> | null;
  response_schema?: Record<string, unknown> | null;
  response_examples: Record<string, unknown>;
  requires_auth: boolean;
  required_permissions: string[];
  rate_limited: boolean;
  deprecated: boolean;
  version: string;
}

export interface APIEndpointGroup {
  name: string;
  description?: string | null;
  category: EndpointCategory;
  endpoints: APIEndpoint[];
}

export interface APIDocumentation {
  title: string;
  version: string;
  description: string;
  base_url: string;
  auth_description: string;
  auth_examples: Record<string, string>;
  groups: APIEndpointGroup[];
  schemas: Record<string, unknown>;
  sdk_languages: SDKLanguage[];
  sdk_download_urls: Record<string, string>;
}

// SDK Configuration Types

export interface SDKConfig {
  version: string;
  base_url: string;
  embed_url: string;
  cdn_url: string;
  supported_languages: string[];
  features: {
    embed: boolean;
    export: boolean;
    interactions: boolean;
    comments: boolean;
    ai: boolean;
  };
}

export interface EmbedInfo {
  embed_url: string;
  iframe_code: string;
  js_snippet: string;
}

// Constants

export const API_KEY_TYPE_LABELS: Record<APIKeyType, string> = {
  [APIKeyType.PUBLIC]: 'Public',
  [APIKeyType.PRIVATE]: 'Private',
  [APIKeyType.RESTRICTED]: 'Restricted',
};

export const API_KEY_STATUS_LABELS: Record<APIKeyStatus, string> = {
  [APIKeyStatus.ACTIVE]: 'Active',
  [APIKeyStatus.REVOKED]: 'Revoked',
  [APIKeyStatus.EXPIRED]: 'Expired',
  [APIKeyStatus.SUSPENDED]: 'Suspended',
};

export const API_KEY_STATUS_COLORS: Record<APIKeyStatus, string> = {
  [APIKeyStatus.ACTIVE]: 'green',
  [APIKeyStatus.REVOKED]: 'red',
  [APIKeyStatus.EXPIRED]: 'gray',
  [APIKeyStatus.SUSPENDED]: 'yellow',
};

export const SDK_LANGUAGE_INFO: Record<SDKLanguage, { name: string; icon: string }> = {
  [SDKLanguage.JAVASCRIPT]: { name: 'JavaScript', icon: 'file-code' },
  [SDKLanguage.TYPESCRIPT]: { name: 'TypeScript', icon: 'file-code' },
  [SDKLanguage.PYTHON]: { name: 'Python', icon: 'file-code' },
  [SDKLanguage.REACT]: { name: 'React', icon: 'atom' },
  [SDKLanguage.VUE]: { name: 'Vue', icon: 'file-code' },
  [SDKLanguage.ANGULAR]: { name: 'Angular', icon: 'file-code' },
  [SDKLanguage.CURL]: { name: 'cURL', icon: 'terminal' },
  [SDKLanguage.GO]: { name: 'Go', icon: 'file-code' },
  [SDKLanguage.RUBY]: { name: 'Ruby', icon: 'gem' },
  [SDKLanguage.PHP]: { name: 'PHP', icon: 'file-code' },
};

export const RATE_LIMIT_PERIOD_LABELS: Record<RateLimitPeriod, string> = {
  [RateLimitPeriod.SECOND]: 'Per Second',
  [RateLimitPeriod.MINUTE]: 'Per Minute',
  [RateLimitPeriod.HOUR]: 'Per Hour',
  [RateLimitPeriod.DAY]: 'Per Day',
  [RateLimitPeriod.MONTH]: 'Per Month',
};

// Helper Functions

export function maskAPIKey(key: string): string {
  if (key.length < 12) return '*'.repeat(key.length);
  return `${key.slice(0, 8)}...${key.slice(-4)}`;
}

export function formatKeyPrefix(prefix: string): string {
  return prefix.replace('bv_', 'bv_****_');
}

export function isKeyExpired(key: APIKey): boolean {
  if (!key.expires_at) return false;
  return new Date(key.expires_at) < new Date();
}

export function getKeyStatusColor(key: APIKey): string {
  if (key.status !== APIKeyStatus.ACTIVE) {
    return API_KEY_STATUS_COLORS[key.status];
  }
  if (isKeyExpired(key)) {
    return 'gray';
  }
  return 'green';
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

export function formatResponseTime(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function calculateUsagePercentage(used: number, limit: number): number {
  if (limit === 0) return 0;
  return Math.min(100, (used / limit) * 100);
}

export function getUsageColor(percentage: number): string {
  if (percentage >= 90) return 'red';
  if (percentage >= 75) return 'yellow';
  return 'green';
}

// Default Values

export function createDefaultPermissions(): APIKeyPermissions {
  return {
    can_read_dashboards: true,
    can_write_dashboards: false,
    can_read_charts: true,
    can_write_charts: false,
    can_read_connections: true,
    can_write_connections: false,
    can_execute_queries: true,
    can_read_datasets: true,
    can_write_datasets: false,
    can_read_transforms: true,
    can_write_transforms: false,
    can_read_models: true,
    can_write_models: false,
    can_use_ai: false,
    can_embed: true,
    can_export: true,
    can_admin: false,
    workspace_ids: [],
    dashboard_ids: [],
  };
}

export function createDefaultRateLimits(): RateLimitConfig {
  return {
    requests_per_minute: 60,
    requests_per_hour: 1000,
    requests_per_day: 10000,
    burst_limit: 10,
    enabled: true,
  };
}

// Copy to Clipboard

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    const success = document.execCommand('copy');
    document.body.removeChild(textarea);
    return success;
  }
}

// Code Highlighting (simple version)

export function highlightCode(code: string, language: SDKLanguage): string {
  // Basic keyword highlighting for display
  const keywords: Record<string, string[]> = {
    javascript: ['const', 'let', 'var', 'function', 'async', 'await', 'import', 'from', 'export', 'return', 'if', 'else', 'for', 'while'],
    typescript: ['const', 'let', 'var', 'function', 'async', 'await', 'import', 'from', 'export', 'return', 'if', 'else', 'for', 'while', 'interface', 'type'],
    python: ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'for', 'while', 'with', 'as', 'async', 'await'],
  };

  const langKeywords = keywords[language] || [];

  let highlighted = code;
  langKeywords.forEach((keyword) => {
    const regex = new RegExp(`\\b${keyword}\\b`, 'g');
    highlighted = highlighted.replace(regex, `<span class="keyword">${keyword}</span>`);
  });

  // Highlight strings
  highlighted = highlighted.replace(/(["'`])([^"'`]*)\1/g, '<span class="string">$&</span>');

  // Highlight comments
  highlighted = highlighted.replace(/(\/\/.*$|#.*$)/gm, '<span class="comment">$&</span>');

  return highlighted;
}

// API Key Form State

export interface APIKeyFormState {
  name: string;
  description: string;
  keyType: APIKeyType;
  workspaceId: string;
  permissions: APIKeyPermissions;
  rateLimits: RateLimitConfig;
  allowedIps: string[];
  allowedDomains: string[];
  expiresInDays: number | null;
  tags: string[];
}

export function createInitialFormState(): APIKeyFormState {
  return {
    name: '',
    description: '',
    keyType: APIKeyType.PRIVATE,
    workspaceId: '',
    permissions: createDefaultPermissions(),
    rateLimits: createDefaultRateLimits(),
    allowedIps: [],
    allowedDomains: [],
    expiresInDays: null,
    tags: [],
  };
}

export function formStateToCreateRequest(state: APIKeyFormState): APIKeyCreate {
  return {
    name: state.name,
    description: state.description || null,
    key_type: state.keyType,
    workspace_id: state.workspaceId || null,
    permissions: state.permissions,
    rate_limits: state.rateLimits,
    allowed_ips: state.allowedIps,
    allowed_domains: state.allowedDomains,
    expires_in_days: state.expiresInDays,
    tags: state.tags,
  };
}
