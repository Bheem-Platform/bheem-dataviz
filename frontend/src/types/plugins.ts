/**
 * Plugin Architecture Types
 *
 * TypeScript types for plugin manifests, lifecycle, hooks, and registry.
 */

// Enums

export enum PluginType {
  CONNECTOR = 'connector',
  VISUALIZATION = 'visualization',
  TRANSFORM = 'transform',
  EXPORT = 'export',
  AUTH = 'auth',
  THEME = 'theme',
  WIDGET = 'widget',
  INTEGRATION = 'integration',
  AI = 'ai',
}

export enum PluginStatus {
  AVAILABLE = 'available',
  INSTALLED = 'installed',
  ENABLED = 'enabled',
  DISABLED = 'disabled',
  ERROR = 'error',
  UPDATING = 'updating',
  DEPRECATED = 'deprecated',
}

export enum HookType {
  BEFORE_QUERY = 'before_query',
  AFTER_QUERY = 'after_query',
  BEFORE_TRANSFORM = 'before_transform',
  AFTER_TRANSFORM = 'after_transform',
  DASHBOARD_RENDER = 'dashboard_render',
  CHART_RENDER = 'chart_render',
  SIDEBAR_MENU = 'sidebar_menu',
  TOOLBAR_ACTION = 'toolbar_action',
  CONTEXT_MENU = 'context_menu',
  BEFORE_AUTH = 'before_auth',
  AFTER_AUTH = 'after_auth',
  BEFORE_EXPORT = 'before_export',
  AFTER_EXPORT = 'after_export',
  ON_INSTALL = 'on_install',
  ON_ENABLE = 'on_enable',
  ON_DISABLE = 'on_disable',
  ON_UNINSTALL = 'on_uninstall',
  ON_UPDATE = 'on_update',
}

export enum PermissionScope {
  READ_DATA = 'read_data',
  WRITE_DATA = 'write_data',
  READ_CONFIG = 'read_config',
  WRITE_CONFIG = 'write_config',
  NETWORK = 'network',
  STORAGE = 'storage',
  UI = 'ui',
  AUTH = 'auth',
  ADMIN = 'admin',
}

// Manifest Types

export interface PluginAuthor {
  name: string;
  email?: string | null;
  url?: string | null;
}

export interface PluginDependency {
  plugin_id: string;
  version: string;
  optional: boolean;
}

export interface PluginAsset {
  type: string;
  path: string;
  load_on: string;
  priority: number;
}

export interface PluginConfig {
  key: string;
  type: string;
  label: string;
  description?: string | null;
  default?: unknown;
  required: boolean;
  options: Array<Record<string, unknown>>;
  validation?: Record<string, unknown> | null;
}

export interface PluginHook {
  type: HookType;
  handler: string;
  priority: number;
  async: boolean;
  conditions: Record<string, unknown>;
}

export interface PluginEndpoint {
  path: string;
  method: string;
  handler: string;
  description?: string | null;
  requires_auth: boolean;
}

export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  description: string;
  type: PluginType;
  author: PluginAuthor;
  license: string;
  homepage?: string | null;
  repository?: string | null;
  min_app_version: string;
  max_app_version?: string | null;
  main?: string | null;
  client?: string | null;
  dependencies: PluginDependency[];
  peer_dependencies: string[];
  permissions: PermissionScope[];
  config_schema: PluginConfig[];
  hooks: PluginHook[];
  endpoints: PluginEndpoint[];
  assets: PluginAsset[];
  sidebar_items: Array<Record<string, unknown>>;
  settings_pages: Array<Record<string, unknown>>;
  keywords: string[];
  icon?: string | null;
  banner?: string | null;
  screenshots: string[];
  changelog?: string | null;
}

// Plugin Instance Types

export interface PluginInstance {
  id: string;
  manifest: PluginManifest;
  status: PluginStatus;
  installed_at: string;
  installed_by: string;
  updated_at?: string | null;
  version_installed: string;
  config: Record<string, unknown>;
  enabled_at?: string | null;
  disabled_at?: string | null;
  last_error?: string | null;
  error_count: number;
  load_time_ms?: number | null;
  memory_usage_bytes?: number | null;
  workspace_id?: string | null;
  enabled_workspaces: string[];
}

export interface PluginInstall {
  plugin_id: string;
  version?: string | null;
  config?: Record<string, unknown>;
  workspace_id?: string | null;
  enable_after_install?: boolean;
}

export interface PluginUpdate {
  config?: Record<string, unknown> | null;
  enabled_workspaces?: string[] | null;
}

// Registry Types

export interface RegistryPlugin {
  id: string;
  manifest: PluginManifest;
  downloads: number;
  rating: number;
  reviews_count: number;
  verified: boolean;
  featured: boolean;
  versions: string[];
  latest_version: string;
  published_at: string;
  updated_at?: string | null;
}

export interface RegistrySearchResult {
  plugins: RegistryPlugin[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface RegistrySearchQuery {
  query?: string | null;
  type?: PluginType | null;
  keywords?: string[];
  verified_only?: boolean;
  sort_by?: string;
  page?: number;
  page_size?: number;
}

// Hook Types

export interface HookContext {
  hook_type: HookType;
  plugin_id: string;
  user_id?: string | null;
  workspace_id?: string | null;
  resource_type?: string | null;
  resource_id?: string | null;
  data: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface HookResult {
  plugin_id: string;
  hook_type: HookType;
  success: boolean;
  data?: Record<string, unknown> | null;
  error?: string | null;
  execution_time_ms: number;
}

export interface HookChainResult {
  hook_type: HookType;
  results: HookResult[];
  final_data: Record<string, unknown>;
  total_time_ms: number;
  any_failed: boolean;
}

// Event Types

export interface PluginEvent {
  id: string;
  plugin_id: string;
  event_type: string;
  timestamp: string;
  user_id?: string | null;
  details: Record<string, unknown>;
}

// Response Types

export interface PluginListResponse {
  plugins: PluginInstance[];
  total: number;
}

export interface PluginStatsResponse {
  total_installed: number;
  total_enabled: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  total_hooks_registered: number;
  recent_errors: Array<{
    plugin_id: string;
    error: string;
    timestamp: string;
  }>;
}

export interface UpdateCheckResult {
  updates_available: number;
  plugins: Array<{
    plugin_id: string;
    current_version: string;
    latest_version: string;
    plugin_name: string;
  }>;
}

// Constants

export const PLUGIN_TYPE_LABELS: Record<PluginType, string> = {
  [PluginType.CONNECTOR]: 'Data Connector',
  [PluginType.VISUALIZATION]: 'Visualization',
  [PluginType.TRANSFORM]: 'Transform',
  [PluginType.EXPORT]: 'Export Format',
  [PluginType.AUTH]: 'Authentication',
  [PluginType.THEME]: 'Theme',
  [PluginType.WIDGET]: 'Widget',
  [PluginType.INTEGRATION]: 'Integration',
  [PluginType.AI]: 'AI Extension',
};

export const PLUGIN_TYPE_ICONS: Record<PluginType, string> = {
  [PluginType.CONNECTOR]: 'database',
  [PluginType.VISUALIZATION]: 'bar-chart',
  [PluginType.TRANSFORM]: 'git-branch',
  [PluginType.EXPORT]: 'download',
  [PluginType.AUTH]: 'lock',
  [PluginType.THEME]: 'palette',
  [PluginType.WIDGET]: 'layout',
  [PluginType.INTEGRATION]: 'plug',
  [PluginType.AI]: 'brain',
};

export const PLUGIN_STATUS_LABELS: Record<PluginStatus, string> = {
  [PluginStatus.AVAILABLE]: 'Available',
  [PluginStatus.INSTALLED]: 'Installed',
  [PluginStatus.ENABLED]: 'Enabled',
  [PluginStatus.DISABLED]: 'Disabled',
  [PluginStatus.ERROR]: 'Error',
  [PluginStatus.UPDATING]: 'Updating',
  [PluginStatus.DEPRECATED]: 'Deprecated',
};

export const PLUGIN_STATUS_COLORS: Record<PluginStatus, string> = {
  [PluginStatus.AVAILABLE]: 'gray',
  [PluginStatus.INSTALLED]: 'blue',
  [PluginStatus.ENABLED]: 'green',
  [PluginStatus.DISABLED]: 'yellow',
  [PluginStatus.ERROR]: 'red',
  [PluginStatus.UPDATING]: 'blue',
  [PluginStatus.DEPRECATED]: 'orange',
};

export const PERMISSION_LABELS: Record<PermissionScope, string> = {
  [PermissionScope.READ_DATA]: 'Read Data',
  [PermissionScope.WRITE_DATA]: 'Write Data',
  [PermissionScope.READ_CONFIG]: 'Read Configuration',
  [PermissionScope.WRITE_CONFIG]: 'Write Configuration',
  [PermissionScope.NETWORK]: 'Network Access',
  [PermissionScope.STORAGE]: 'Storage Access',
  [PermissionScope.UI]: 'UI Modifications',
  [PermissionScope.AUTH]: 'Authentication',
  [PermissionScope.ADMIN]: 'Admin Access',
};

// Helper Functions

export function isPluginEnabled(plugin: PluginInstance): boolean {
  return plugin.status === PluginStatus.ENABLED;
}

export function isPluginInstalled(plugin: PluginInstance): boolean {
  return [
    PluginStatus.INSTALLED,
    PluginStatus.ENABLED,
    PluginStatus.DISABLED,
  ].includes(plugin.status);
}

export function hasUpdate(installed: PluginInstance, registry: RegistryPlugin): boolean {
  return compareVersions(registry.latest_version, installed.version_installed) > 0;
}

export function compareVersions(v1: string, v2: string): number {
  const parse = (v: string) => v.split('-')[0].split('.').map(Number);
  const p1 = parse(v1);
  const p2 = parse(v2);

  for (let i = 0; i < Math.max(p1.length, p2.length); i++) {
    const a = p1[i] || 0;
    const b = p2[i] || 0;
    if (a < b) return -1;
    if (a > b) return 1;
  }
  return 0;
}

export function formatDownloads(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return count.toString();
}

export function formatRating(rating: number): string {
  return rating.toFixed(1);
}

export function getStarRating(rating: number): number[] {
  const stars = [];
  for (let i = 1; i <= 5; i++) {
    if (rating >= i) {
      stars.push(1); // Full star
    } else if (rating >= i - 0.5) {
      stars.push(0.5); // Half star
    } else {
      stars.push(0); // Empty star
    }
  }
  return stars;
}

// Config Form Helpers

export interface ConfigFormField {
  key: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'json';
  label: string;
  description?: string;
  defaultValue?: unknown;
  required: boolean;
  options?: Array<{ value: unknown; label: string }>;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
}

export function manifestConfigToFormFields(schema: PluginConfig[]): ConfigFormField[] {
  return schema.map((config) => ({
    key: config.key,
    type: config.type as ConfigFormField['type'],
    label: config.label,
    description: config.description || undefined,
    defaultValue: config.default,
    required: config.required,
    options: config.options.map((opt) => ({
      value: opt.value,
      label: opt.label as string,
    })),
    validation: config.validation as ConfigFormField['validation'],
  }));
}

export function validateConfig(
  config: Record<string, unknown>,
  schema: PluginConfig[]
): { valid: boolean; errors: Record<string, string> } {
  const errors: Record<string, string> = {};

  for (const field of schema) {
    const value = config[field.key];

    if (field.required && (value === undefined || value === null || value === '')) {
      errors[field.key] = `${field.label} is required`;
      continue;
    }

    if (value !== undefined && field.validation) {
      const val = field.validation as Record<string, unknown>;
      if (field.type === 'number') {
        const num = Number(value);
        if (val.min !== undefined && num < (val.min as number)) {
          errors[field.key] = `Must be at least ${val.min}`;
        }
        if (val.max !== undefined && num > (val.max as number)) {
          errors[field.key] = `Must be at most ${val.max}`;
        }
      }
      if (field.type === 'string' && val.pattern) {
        const regex = new RegExp(val.pattern as string);
        if (!regex.test(String(value))) {
          errors[field.key] = (val.message as string) || 'Invalid format';
        }
      }
    }
  }

  return { valid: Object.keys(errors).length === 0, errors };
}

// Plugin State Management

export interface PluginManagerState {
  installedPlugins: PluginInstance[];
  registryPlugins: RegistryPlugin[];
  selectedPlugin: PluginInstance | RegistryPlugin | null;
  isLoading: boolean;
  error: string | null;
  searchQuery: string;
  filterType: PluginType | null;
  filterStatus: PluginStatus | null;
  sortBy: 'name' | 'downloads' | 'rating' | 'updated';
  stats: PluginStatsResponse | null;
  updatesAvailable: UpdateCheckResult | null;
}

export function createInitialPluginState(): PluginManagerState {
  return {
    installedPlugins: [],
    registryPlugins: [],
    selectedPlugin: null,
    isLoading: false,
    error: null,
    searchQuery: '',
    filterType: null,
    filterStatus: null,
    sortBy: 'downloads',
    stats: null,
    updatesAvailable: null,
  };
}
