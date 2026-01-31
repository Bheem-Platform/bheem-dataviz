/**
 * Mobile Optimization Types
 *
 * TypeScript types for mobile-optimized views and settings.
 */

// Enums

export enum LayoutMode {
  AUTO = 'auto',
  DESKTOP = 'desktop',
  TABLET = 'tablet',
  MOBILE = 'mobile',
}

export enum GestureType {
  TAP = 'tap',
  DOUBLE_TAP = 'double_tap',
  LONG_PRESS = 'long_press',
  SWIPE_LEFT = 'swipe_left',
  SWIPE_RIGHT = 'swipe_right',
  SWIPE_UP = 'swipe_up',
  SWIPE_DOWN = 'swipe_down',
  PINCH = 'pinch',
  SPREAD = 'spread',
}

export enum GestureAction {
  SELECT = 'select',
  DRILL_DOWN = 'drill_down',
  DRILL_UP = 'drill_up',
  FILTER = 'filter',
  EXPAND = 'expand',
  COLLAPSE = 'collapse',
  ZOOM_IN = 'zoom_in',
  ZOOM_OUT = 'zoom_out',
  REFRESH = 'refresh',
  SHARE = 'share',
  EXPORT = 'export',
  NEXT_CHART = 'next_chart',
  PREV_CHART = 'prev_chart',
}

export enum SyncStatus {
  SYNCED = 'synced',
  PENDING = 'pending',
  SYNCING = 'syncing',
  CONFLICT = 'conflict',
  ERROR = 'error',
}

// Breakpoint Configuration

export interface Breakpoint {
  name: string;
  min_width: number;
  max_width?: number | null;
  columns: number;
  gutter: number;
  margin: number;
}

export const DEFAULT_BREAKPOINTS: Breakpoint[] = [
  { name: 'mobile', min_width: 0, max_width: 639, columns: 1, gutter: 8, margin: 12 },
  { name: 'tablet', min_width: 640, max_width: 1023, columns: 2, gutter: 16, margin: 16 },
  { name: 'desktop', min_width: 1024, max_width: 1279, columns: 4, gutter: 20, margin: 20 },
  { name: 'large', min_width: 1280, max_width: null, columns: 6, gutter: 24, margin: 24 },
];

// Mobile Layout Configuration

export interface MobileChartConfig {
  chart_id: string;
  order: number;
  visible: boolean;
  collapsed: boolean;
  height: number;
  simplified: boolean;
  touch_enabled: boolean;
  swipe_navigation: boolean;
}

export interface MobileDashboardLayout {
  dashboard_id: string;
  enabled: boolean;
  layout_mode: LayoutMode;
  charts: MobileChartConfig[];
  stack_charts: boolean;
  show_chart_titles: boolean;
  compact_headers: boolean;
  hide_empty_charts: boolean;
  filter_position: 'top' | 'bottom' | 'modal';
  collapsible_filters: boolean;
  quick_filters_count: number;
  show_navigation: boolean;
  bottom_navigation: boolean;
  swipe_between_charts: boolean;
  pull_to_refresh: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

// Gesture Configuration

export interface GestureBinding {
  gesture: GestureType;
  action: GestureAction;
  target?: string | null;
  params: Record<string, unknown>;
}

export interface GestureConfig {
  enabled: boolean;
  bindings: GestureBinding[];
  haptic_feedback: boolean;
  gesture_hints: boolean;
}

export const DEFAULT_GESTURE_BINDINGS: GestureBinding[] = [
  { gesture: GestureType.TAP, action: GestureAction.SELECT, params: {} },
  { gesture: GestureType.DOUBLE_TAP, action: GestureAction.DRILL_DOWN, params: {} },
  { gesture: GestureType.LONG_PRESS, action: GestureAction.EXPAND, params: {} },
  { gesture: GestureType.SWIPE_LEFT, action: GestureAction.NEXT_CHART, params: {} },
  { gesture: GestureType.SWIPE_RIGHT, action: GestureAction.PREV_CHART, params: {} },
  { gesture: GestureType.SWIPE_DOWN, action: GestureAction.REFRESH, params: {} },
  { gesture: GestureType.PINCH, action: GestureAction.ZOOM_OUT, params: {} },
  { gesture: GestureType.SPREAD, action: GestureAction.ZOOM_IN, params: {} },
];

// Offline Configuration

export interface OfflineDataConfig {
  enabled: boolean;
  max_cache_size_mb: number;
  cache_duration_hours: number;
  auto_sync: boolean;
  sync_on_wifi_only: boolean;
  priority_dashboards: string[];
}

export interface CachedDashboard {
  dashboard_id: string;
  dashboard_name: string;
  cached_at: string;
  expires_at: string;
  size_bytes: number;
  sync_status: SyncStatus;
  charts_cached: number;
  last_synced_at?: string | null;
  pending_changes: number;
}

export interface OfflineSyncStatus {
  enabled: boolean;
  last_sync?: string | null;
  next_sync?: string | null;
  total_cached_mb: number;
  max_cache_mb: number;
  dashboards_cached: number;
  pending_uploads: number;
  sync_errors: number;
}

// Push Notifications

export interface NotificationPreference {
  enabled: boolean;
  alert_notifications: boolean;
  report_notifications: boolean;
  mention_notifications: boolean;
  schedule_notifications: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start?: string | null;
  quiet_hours_end?: string | null;
}

export interface PushNotification {
  id: string;
  title: string;
  body: string;
  type: string;
  data: Record<string, unknown>;
  action_url?: string | null;
  created_at: string;
  read: boolean;
  read_at?: string | null;
}

// Mobile User Settings

export interface MobileUserSettings {
  user_id: string;
  layout_mode_preference: LayoutMode;
  default_dashboard_id?: string | null;
  quick_access_dashboards: string[];
  gesture_config: GestureConfig;
  offline_config: OfflineDataConfig;
  notification_preferences: NotificationPreference;
  dark_mode: 'auto' | 'light' | 'dark';
  font_size: 'small' | 'medium' | 'large';
  data_saver_mode: boolean;
  biometric_auth: boolean;
}

// Device Information

export interface DeviceInfo {
  device_id?: string | null;
  platform: 'ios' | 'android' | 'web';
  os_version?: string | null;
  app_version?: string | null;
  screen_width: number;
  screen_height: number;
  pixel_ratio: number;
  is_tablet: boolean;
  supports_touch: boolean;
  push_token?: string | null;
}

// Mobile Analytics

export interface MobileAnalyticsEvent {
  event_type: string;
  user_id?: string | null;
  device_info: DeviceInfo;
  dashboard_id?: string | null;
  chart_id?: string | null;
  gesture?: GestureType | null;
  duration_ms?: number | null;
  metadata: Record<string, unknown>;
  timestamp: string;
}

export interface MobileUsageStats {
  total_sessions: number;
  total_duration_minutes: number;
  avg_session_duration_minutes: number;
  most_viewed_dashboards: Array<{ dashboard_id: string; views: number }>;
  gesture_usage: Record<string, number>;
  offline_views: number;
  device_breakdown: Record<string, number>;
}

// Responsive Image

export interface ResponsiveImage {
  original_url: string;
  thumbnail_url?: string | null;
  mobile_url?: string | null;
  tablet_url?: string | null;
  desktop_url?: string | null;
  width: number;
  height: number;
  format: string;
}

// Mobile API Response Wrappers

export interface MobileResponse<T = unknown> {
  success: boolean;
  data?: T | null;
  error?: string | null;
  cache_key?: string | null;
  cache_ttl_seconds: number;
  offline_available: boolean;
}

export interface MobileDashboardResponse {
  dashboard_id: string;
  name: string;
  layout: MobileDashboardLayout;
  charts: Record<string, unknown>[];
  filters: Record<string, unknown>[];
  last_updated: string;
  cache_key: string;
  offline_available: boolean;
}

// Device Detection Response

export interface DeviceDetectionResult {
  is_mobile: boolean;
  is_tablet: boolean;
  is_desktop: boolean;
  recommended_layout: LayoutMode;
  screen_width: number;
  screen_height: number;
  supports_touch: boolean;
}

// Constants

export const MOBILE_CHART_MIN_HEIGHT = 150;
export const MOBILE_CHART_MAX_HEIGHT = 400;
export const MOBILE_CHART_DEFAULT_HEIGHT = 250;

export const DEFAULT_CACHE_DURATION_HOURS = 24;
export const MAX_OFFLINE_DASHBOARDS = 10;
export const MAX_CACHE_SIZE_MB = 500;

// Helper Functions

export function getBreakpointForWidth(width: number): Breakpoint {
  for (let i = DEFAULT_BREAKPOINTS.length - 1; i >= 0; i--) {
    const bp = DEFAULT_BREAKPOINTS[i];
    if (width >= bp.min_width) {
      if (bp.max_width === null || bp.max_width === undefined || width <= bp.max_width) {
        return bp;
      }
    }
  }
  return DEFAULT_BREAKPOINTS[0];
}

export function calculateChartHeight(
  baseHeight: number,
  screenHeight: number,
  chartCount: number,
  layoutMode: LayoutMode
): number {
  if (layoutMode === LayoutMode.MOBILE) {
    const maxHeight = Math.floor((screenHeight - 150) / 2);
    return Math.min(baseHeight, maxHeight, MOBILE_CHART_MAX_HEIGHT);
  } else if (layoutMode === LayoutMode.TABLET) {
    return Math.min(baseHeight, 350);
  }
  return baseHeight;
}

export function isMobileDevice(): boolean {
  if (typeof window === 'undefined') return false;
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
}

export function isTabletDevice(): boolean {
  if (typeof window === 'undefined') return false;
  const userAgent = navigator.userAgent.toLowerCase();
  return /ipad|tablet|playbook|silk/i.test(userAgent) ||
    (userAgent.includes('android') && !userAgent.includes('mobile'));
}

export function getDeviceInfo(): Partial<DeviceInfo> {
  if (typeof window === 'undefined') {
    return { platform: 'web', screen_width: 0, screen_height: 0 };
  }

  const userAgent = navigator.userAgent.toLowerCase();
  let platform: 'ios' | 'android' | 'web' = 'web';

  if (/iphone|ipad|ipod/.test(userAgent)) {
    platform = 'ios';
  } else if (/android/.test(userAgent)) {
    platform = 'android';
  }

  return {
    platform,
    screen_width: window.screen.width,
    screen_height: window.screen.height,
    pixel_ratio: window.devicePixelRatio || 1,
    is_tablet: isTabletDevice(),
    supports_touch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
  };
}

export function formatCacheSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function isCacheExpired(expiresAt: string): boolean {
  return new Date(expiresAt) < new Date();
}

export function createDefaultMobileLayout(dashboardId: string): MobileDashboardLayout {
  return {
    dashboard_id: dashboardId,
    enabled: true,
    layout_mode: LayoutMode.AUTO,
    charts: [],
    stack_charts: true,
    show_chart_titles: true,
    compact_headers: true,
    hide_empty_charts: true,
    filter_position: 'top',
    collapsible_filters: true,
    quick_filters_count: 3,
    show_navigation: true,
    bottom_navigation: true,
    swipe_between_charts: true,
    pull_to_refresh: true,
  };
}

export function createDefaultUserSettings(userId: string): MobileUserSettings {
  return {
    user_id: userId,
    layout_mode_preference: LayoutMode.AUTO,
    quick_access_dashboards: [],
    gesture_config: {
      enabled: true,
      bindings: [...DEFAULT_GESTURE_BINDINGS],
      haptic_feedback: true,
      gesture_hints: true,
    },
    offline_config: {
      enabled: true,
      max_cache_size_mb: 100,
      cache_duration_hours: 24,
      auto_sync: true,
      sync_on_wifi_only: false,
      priority_dashboards: [],
    },
    notification_preferences: {
      enabled: true,
      alert_notifications: true,
      report_notifications: true,
      mention_notifications: true,
      schedule_notifications: true,
      quiet_hours_enabled: false,
    },
    dark_mode: 'auto',
    font_size: 'medium',
    data_saver_mode: false,
    biometric_auth: false,
  };
}
