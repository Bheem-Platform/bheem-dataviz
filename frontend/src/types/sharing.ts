/**
 * Advanced Sharing Types
 *
 * TypeScript types for public links, password protection, and sharing features.
 */

// Enums

export enum ShareType {
  DASHBOARD = 'dashboard',
  CHART = 'chart',
  REPORT = 'report',
  DATASET = 'dataset',
}

export enum ShareAccess {
  VIEW = 'view',
  INTERACT = 'interact',
  EXPORT = 'export',
  FULL = 'full',
}

export enum LinkStatus {
  ACTIVE = 'active',
  EXPIRED = 'expired',
  REVOKED = 'revoked',
  DISABLED = 'disabled',
}

export enum ShareVisibility {
  PUBLIC = 'public',
  PASSWORD = 'password',
  EMAIL = 'email',
  DOMAIN = 'domain',
}

// Share Link Types

export interface ShareLinkCreate {
  resource_type: ShareType;
  resource_id: string;
  name?: string | null;
  description?: string | null;
  access_level?: ShareAccess;
  visibility?: ShareVisibility;
  password?: string | null;
  allowed_emails?: string[];
  allowed_domains?: string[];
  expires_at?: string | null;
  max_views?: number | null;
  custom_slug?: string | null;
  hide_branding?: boolean;
  custom_logo_url?: string | null;
  track_views?: boolean;
  require_name?: boolean;
  preset_filters?: Record<string, unknown> | null;
  locked_filters?: boolean;
  show_toolbar?: boolean;
  show_export?: boolean;
  fullscreen_only?: boolean;
  theme?: 'light' | 'dark' | 'auto';
  workspace_id?: string | null;
  metadata?: Record<string, unknown>;
}

export interface ShareLinkUpdate {
  name?: string | null;
  description?: string | null;
  access_level?: ShareAccess | null;
  visibility?: ShareVisibility | null;
  password?: string | null;
  allowed_emails?: string[] | null;
  allowed_domains?: string[] | null;
  expires_at?: string | null;
  max_views?: number | null;
  is_active?: boolean | null;
  hide_branding?: boolean | null;
  custom_logo_url?: string | null;
  preset_filters?: Record<string, unknown> | null;
  locked_filters?: boolean | null;
  show_toolbar?: boolean | null;
  show_export?: boolean | null;
  theme?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface ShareLink {
  id: string;
  token: string;
  short_code: string;
  custom_slug?: string | null;
  resource_type: ShareType;
  resource_id: string;
  resource_name: string;
  name?: string | null;
  description?: string | null;
  access_level: ShareAccess;
  visibility: ShareVisibility;
  has_password: boolean;
  allowed_emails: string[];
  allowed_domains: string[];
  expires_at?: string | null;
  max_views?: number | null;
  status: LinkStatus;
  is_active: boolean;
  hide_branding: boolean;
  custom_logo_url?: string | null;
  preset_filters?: Record<string, unknown> | null;
  locked_filters: boolean;
  show_toolbar: boolean;
  show_export: boolean;
  fullscreen_only: boolean;
  theme: string;
  track_views: boolean;
  require_name: boolean;
  view_count: number;
  unique_viewers: number;
  last_viewed_at?: string | null;
  share_url: string;
  embed_url: string;
  qr_code_url?: string | null;
  created_by: string;
  created_by_name: string;
  workspace_id?: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

// Access Types

export interface ShareAccessRequest {
  token: string;
  password?: string | null;
  viewer_email?: string | null;
  viewer_name?: string | null;
}

export interface ShareAccessResponse {
  valid: boolean;
  access_level?: ShareAccess | null;
  resource_type?: ShareType | null;
  resource_id?: string | null;
  resource_name?: string | null;
  preset_filters?: Record<string, unknown> | null;
  locked_filters: boolean;
  show_toolbar: boolean;
  show_export: boolean;
  theme: string;
  error?: string | null;
  session_token?: string | null;
}

export interface ShareView {
  id: string;
  share_link_id: string;
  viewer_ip?: string | null;
  viewer_email?: string | null;
  viewer_name?: string | null;
  user_agent?: string | null;
  referrer?: string | null;
  country?: string | null;
  city?: string | null;
  device_type?: string | null;
  duration_seconds?: number | null;
  interactions: number;
  viewed_at: string;
}

// Analytics Types

export interface ShareAnalytics {
  share_link_id: string;
  total_views: number;
  unique_viewers: number;
  avg_duration_seconds: number;
  total_interactions: number;
  views_by_day: Array<{ date: string; count: number }>;
  views_by_country: Array<{ country: string; count: number }>;
  views_by_device: Array<{ device: string; count: number }>;
  views_by_referrer: Array<{ referrer: string; count: number }>;
  top_viewers: Array<{ name: string; views: number; last_viewed: string }>;
  recent_views: ShareView[];
  period_start: string;
  period_end: string;
}

// QR Code Types

export interface QRCodeConfig {
  size?: number;
  format?: 'png' | 'svg';
  error_correction?: 'L' | 'M' | 'Q' | 'H';
  foreground_color?: string;
  background_color?: string;
  include_logo?: boolean;
  logo_url?: string | null;
  logo_size_percent?: number;
}

export interface QRCodeResponse {
  share_link_id: string;
  qr_code_url: string;
  qr_code_data?: string | null;
  share_url: string;
  expires_at?: string | null;
}

// Email Sharing Types

export interface EmailShareRequest {
  share_link_id: string;
  recipients: string[];
  subject?: string | null;
  message?: string | null;
  include_preview?: boolean;
}

export interface EmailShareResponse {
  sent_to: string[];
  failed: Array<{ email: string; error: string }>;
}

// Template Types

export interface ShareTemplate {
  id: string;
  name: string;
  description?: string | null;
  settings: ShareLinkCreate;
  is_default: boolean;
  created_by: string;
  workspace_id?: string | null;
  created_at: string;
}

// Bulk Operation Types

export interface BulkShareCreate {
  resource_ids: string[];
  resource_type: ShareType;
  settings: ShareLinkCreate;
}

export interface BulkShareResponse {
  created: ShareLink[];
  failed: Array<{ resource_id: string; error: string }>;
  total_created: number;
  total_failed: number;
}

// Constants

export const ACCESS_LEVEL_LABELS: Record<ShareAccess, string> = {
  [ShareAccess.VIEW]: 'View Only',
  [ShareAccess.INTERACT]: 'Interactive',
  [ShareAccess.EXPORT]: 'Can Export',
  [ShareAccess.FULL]: 'Full Access',
};

export const VISIBILITY_LABELS: Record<ShareVisibility, string> = {
  [ShareVisibility.PUBLIC]: 'Anyone with the link',
  [ShareVisibility.PASSWORD]: 'Password protected',
  [ShareVisibility.EMAIL]: 'Specific emails only',
  [ShareVisibility.DOMAIN]: 'Specific domains only',
};

export const STATUS_LABELS: Record<LinkStatus, string> = {
  [LinkStatus.ACTIVE]: 'Active',
  [LinkStatus.EXPIRED]: 'Expired',
  [LinkStatus.REVOKED]: 'Revoked',
  [LinkStatus.DISABLED]: 'Disabled',
};

export const RESOURCE_TYPE_LABELS: Record<ShareType, string> = {
  [ShareType.DASHBOARD]: 'Dashboard',
  [ShareType.CHART]: 'Chart',
  [ShareType.REPORT]: 'Report',
  [ShareType.DATASET]: 'Dataset',
};

// Helper Functions

export function isLinkExpired(link: ShareLink): boolean {
  if (link.expires_at && new Date(link.expires_at) < new Date()) {
    return true;
  }
  if (link.max_views && link.view_count >= link.max_views) {
    return true;
  }
  return false;
}

export function isLinkActive(link: ShareLink): boolean {
  return link.is_active && link.status === LinkStatus.ACTIVE && !isLinkExpired(link);
}

export function formatExpiration(expiresAt: string | null | undefined): string {
  if (!expiresAt) return 'Never';

  const date = new Date(expiresAt);
  const now = new Date();
  const diff = date.getTime() - now.getTime();

  if (diff < 0) return 'Expired';
  if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours`;
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} days`;
  return date.toLocaleDateString();
}

export function formatViews(views: number, maxViews?: number | null): string {
  if (maxViews) {
    return `${views} / ${maxViews}`;
  }
  return views.toString();
}

export function generateShareUrl(baseUrl: string, shortCode: string, customSlug?: string | null): string {
  const identifier = customSlug || shortCode;
  return `${baseUrl}/s/${identifier}`;
}

export function generateEmbedUrl(baseUrl: string, token: string): string {
  return `${baseUrl}/embed/${token}`;
}

export function generateEmbedCode(embedUrl: string, width = '100%', height = '600px'): string {
  return `<iframe src="${embedUrl}" width="${width}" height="${height}" frameborder="0" allowfullscreen></iframe>`;
}

export function copyToClipboard(text: string): Promise<boolean> {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text).then(() => true).catch(() => false);
  }
  // Fallback for older browsers
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.left = '-999999px';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  try {
    document.execCommand('copy');
    document.body.removeChild(textArea);
    return Promise.resolve(true);
  } catch {
    document.body.removeChild(textArea);
    return Promise.resolve(false);
  }
}

export function validatePassword(password: string): { valid: boolean; message?: string } {
  if (password.length < 4) {
    return { valid: false, message: 'Password must be at least 4 characters' };
  }
  if (password.length > 100) {
    return { valid: false, message: 'Password must be less than 100 characters' };
  }
  return { valid: true };
}

export function validateSlug(slug: string): { valid: boolean; message?: string } {
  if (slug.length < 3) {
    return { valid: false, message: 'Slug must be at least 3 characters' };
  }
  if (slug.length > 50) {
    return { valid: false, message: 'Slug must be less than 50 characters' };
  }
  if (!/^[a-z0-9-]+$/.test(slug)) {
    return { valid: false, message: 'Slug can only contain lowercase letters, numbers, and hyphens' };
  }
  return { valid: true };
}

export function getShareTypeIcon(type: ShareType): string {
  switch (type) {
    case ShareType.DASHBOARD:
      return 'layout-dashboard';
    case ShareType.CHART:
      return 'bar-chart';
    case ShareType.REPORT:
      return 'file-text';
    case ShareType.DATASET:
      return 'database';
    default:
      return 'share';
  }
}

export function getVisibilityIcon(visibility: ShareVisibility): string {
  switch (visibility) {
    case ShareVisibility.PUBLIC:
      return 'globe';
    case ShareVisibility.PASSWORD:
      return 'lock';
    case ShareVisibility.EMAIL:
      return 'mail';
    case ShareVisibility.DOMAIN:
      return 'building';
    default:
      return 'eye';
  }
}
