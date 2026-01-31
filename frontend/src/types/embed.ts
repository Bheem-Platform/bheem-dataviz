/**
 * Embed SDK Types
 *
 * TypeScript types for embedding dashboards and charts.
 */

// Enums

export type EmbedResourceType = 'dashboard' | 'chart' | 'report';

export type EmbedTheme = 'light' | 'dark' | 'auto' | 'custom';

export type DeviceType = 'desktop' | 'mobile' | 'tablet' | 'unknown';

// Token Types

export interface EmbedToken {
  id: string;
  name: string;
  description?: string;
  token?: string; // Only available on creation
  created_by: string;
  workspace_id?: string;
  resource_type: EmbedResourceType;
  resource_id: string;

  // Permissions
  allow_interactions: boolean;
  allow_export: boolean;
  allow_fullscreen: boolean;
  allow_comments: boolean;

  // Appearance
  theme: EmbedTheme;
  show_header: boolean;
  show_toolbar: boolean;
  custom_css?: string;

  // Restrictions
  allowed_domains: string[];
  expires_at?: string;
  max_views?: number;
  view_count: number;

  // Status
  is_active: boolean;
  revoked_at?: string;

  // Timestamps
  created_at: string;
  last_used_at?: string;

  // Settings
  settings: Record<string, unknown>;
}

export interface EmbedTokenCreate {
  name: string;
  description?: string;
  resource_type: EmbedResourceType;
  resource_id: string;
  workspace_id?: string;

  // Permissions
  allow_interactions?: boolean;
  allow_export?: boolean;
  allow_fullscreen?: boolean;
  allow_comments?: boolean;

  // Appearance
  theme?: EmbedTheme;
  show_header?: boolean;
  show_toolbar?: boolean;
  custom_css?: string;

  // Restrictions
  allowed_domains?: string[];
  expires_at?: string;
  max_views?: number;

  // Settings
  settings?: Record<string, unknown>;
}

export interface EmbedTokenUpdate {
  name?: string;
  description?: string;

  // Permissions
  allow_interactions?: boolean;
  allow_export?: boolean;
  allow_fullscreen?: boolean;
  allow_comments?: boolean;

  // Appearance
  theme?: EmbedTheme;
  show_header?: boolean;
  show_toolbar?: boolean;
  custom_css?: string;

  // Restrictions
  allowed_domains?: string[];
  expires_at?: string;
  max_views?: number;

  // Status
  is_active?: boolean;

  // Settings
  settings?: Record<string, unknown>;
}

export interface EmbedTokenSummary {
  id: string;
  name: string;
  resource_type: EmbedResourceType;
  resource_id: string;
  is_active: boolean;
  view_count: number;
  created_at: string;
  expires_at?: string;
  last_used_at?: string;
}

// Validation Types

export interface EmbedValidationRequest {
  token: string;
  origin?: string;
}

export interface EmbedValidationResponse {
  valid: boolean;
  resource_type?: EmbedResourceType;
  resource_id?: string;
  permissions?: {
    allow_interactions: boolean;
    allow_export: boolean;
    allow_fullscreen: boolean;
    allow_comments: boolean;
  };
  appearance?: {
    theme: string;
    show_header: boolean;
    show_toolbar: boolean;
    custom_css?: string;
  };
  error?: string;
  session_id?: string;
}

// Session Types

export interface EmbedSessionStart {
  token: string;
  origin_url?: string;
  referrer?: string;
  user_agent?: string;
}

export interface EmbedSessionResponse {
  session_id: string;
  resource_type: EmbedResourceType;
  resource_id: string;
  permissions: {
    allow_interactions: boolean;
    allow_export: boolean;
    allow_fullscreen: boolean;
    allow_comments: boolean;
  };
  appearance: {
    theme: string;
    show_header: boolean;
    show_toolbar: boolean;
    custom_css?: string;
  };
}

export interface EmbedSessionEnd {
  session_id: string;
  duration_seconds?: number;
  interaction_count?: number;
  filter_changes?: number;
  exports_count?: number;
}

export interface EmbedSessionTrack {
  session_id: string;
  event_type: string;
  event_data?: Record<string, unknown>;
}

// Analytics Types

export interface EmbedAnalyticsSummary {
  total_views: number;
  unique_sessions: number;
  total_interactions: number;
  total_exports: number;
  avg_duration_seconds: number;
  views_by_device: Record<string, number>;
  views_by_date: Array<{ date: string; views: number }>;
  top_domains: Array<{ domain: string; views: number }>;
}

export interface EmbedTokenAnalytics {
  token_id: string;
  token_name: string;
  total_views: number;
  unique_sessions: number;
  avg_duration_seconds: number;
  last_viewed_at?: string;
  top_domains: string[];
}

// Whitelist Types

export interface DomainWhitelistCreate {
  domain: string;
  is_wildcard?: boolean;
  notes?: string;
}

export interface DomainWhitelistEntry {
  id: string;
  domain: string;
  is_wildcard: boolean;
  is_active: boolean;
  added_at: string;
  notes?: string;
}

// Code Generation Types

export interface EmbedCodeRequest {
  token_id: string;
  width?: string;
  height?: string;
  include_sdk?: boolean;
  framework?: 'vanilla' | 'react' | 'vue' | 'angular';
}

export interface EmbedCodeResponse {
  html: string;
  javascript?: string;
  react_component?: string;
  vue_component?: string;
  iframe_url: string;
}

// SDK Configuration

export interface EmbedSDKConfig {
  base_url: string;
  default_theme: EmbedTheme;
  auto_resize: boolean;
  loading_indicator: boolean;
  error_handling: 'display' | 'callback' | 'silent';
  sandbox_attributes: string[];
}

// Quick Embed

export interface QuickEmbedResponse {
  token_id: string;
  token?: string; // Only for new tokens
  embed_url: string;
  existing: boolean;
}

// SDK Events

export interface EmbedEvent {
  type: 'load' | 'error' | 'interaction' | 'filter' | 'export' | 'resize';
  data?: unknown;
  timestamp: string;
}

export interface EmbedLoadEvent extends EmbedEvent {
  type: 'load';
  data: {
    resource_type: EmbedResourceType;
    resource_id: string;
  };
}

export interface EmbedErrorEvent extends EmbedEvent {
  type: 'error';
  data: {
    code: string;
    message: string;
  };
}

export interface EmbedInteractionEvent extends EmbedEvent {
  type: 'interaction';
  data: {
    action: string;
    target?: string;
    value?: unknown;
  };
}

// Constants

export const EMBED_THEME_LABELS: Record<EmbedTheme, string> = {
  light: 'Light',
  dark: 'Dark',
  auto: 'Auto (System)',
  custom: 'Custom',
};

export const DEVICE_TYPE_LABELS: Record<DeviceType, string> = {
  desktop: 'Desktop',
  mobile: 'Mobile',
  tablet: 'Tablet',
  unknown: 'Unknown',
};

export const RESOURCE_TYPE_LABELS: Record<EmbedResourceType, string> = {
  dashboard: 'Dashboard',
  chart: 'Chart',
  report: 'Report',
};

// Helper Functions

export function generateIframeHtml(
  url: string,
  options: {
    width?: string;
    height?: string;
    title?: string;
    allowFullscreen?: boolean;
  } = {}
): string {
  const {
    width = '100%',
    height = '600px',
    title = 'Embedded Content',
    allowFullscreen = true,
  } = options;

  return `<iframe
  src="${url}"
  width="${width}"
  height="${height}"
  title="${title}"
  frameborder="0"
  ${allowFullscreen ? 'allowfullscreen="true"' : ''}
  sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
  style="border: none; border-radius: 8px;"
></iframe>`;
}

export function formatViewCount(count: number): string {
  if (count < 1000) return count.toString();
  if (count < 1000000) return `${(count / 1000).toFixed(1)}K`;
  return `${(count / 1000000).toFixed(1)}M`;
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return `${hours}h ${mins}m`;
}

export function isTokenExpired(token: EmbedToken): boolean {
  if (!token.expires_at) return false;
  return new Date(token.expires_at) < new Date();
}

export function isTokenViewLimitReached(token: EmbedToken): boolean {
  if (!token.max_views) return false;
  return token.view_count >= token.max_views;
}

export function getTokenStatus(
  token: EmbedToken
): 'active' | 'expired' | 'revoked' | 'limit_reached' {
  if (token.revoked_at) return 'revoked';
  if (!token.is_active) return 'revoked';
  if (isTokenExpired(token)) return 'expired';
  if (isTokenViewLimitReached(token)) return 'limit_reached';
  return 'active';
}

export function getTokenStatusLabel(status: ReturnType<typeof getTokenStatus>): string {
  const labels: Record<ReturnType<typeof getTokenStatus>, string> = {
    active: 'Active',
    expired: 'Expired',
    revoked: 'Revoked',
    limit_reached: 'Limit Reached',
  };
  return labels[status];
}

export function getTokenStatusColor(status: ReturnType<typeof getTokenStatus>): string {
  const colors: Record<ReturnType<typeof getTokenStatus>, string> = {
    active: 'green',
    expired: 'yellow',
    revoked: 'red',
    limit_reached: 'orange',
  };
  return colors[status];
}

export function validateDomain(domain: string, allowedDomains: string[]): boolean {
  if (!allowedDomains.length) return true;

  for (const allowed of allowedDomains) {
    if (allowed.startsWith('*.')) {
      const suffix = allowed.slice(2);
      if (domain.endsWith(suffix) || domain === suffix.slice(1)) {
        return true;
      }
    } else if (domain === allowed) {
      return true;
    }
  }

  return false;
}
