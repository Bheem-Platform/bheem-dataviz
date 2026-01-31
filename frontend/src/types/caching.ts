/**
 * Caching Layer Types
 *
 * TypeScript types for cache management, TTL policies, cache warming,
 * and invalidation strategies.
 */

// Enums

export enum CacheType {
  QUERY_RESULT = 'query_result',
  DATASET_PREVIEW = 'dataset_preview',
  CHART_DATA = 'chart_data',
  DASHBOARD_DATA = 'dashboard_data',
  CONNECTION_SCHEMA = 'connection_schema',
  TABLE_METADATA = 'table_metadata',
  FILTER_OPTIONS = 'filter_options',
  KPI_VALUE = 'kpi_value',
  TRANSFORM_RESULT = 'transform_result',
  API_RESPONSE = 'api_response',
  USER_SESSION = 'user_session',
  COMPUTED_METRIC = 'computed_metric',
}

export enum CacheStatus {
  VALID = 'valid',
  STALE = 'stale',
  EXPIRED = 'expired',
  WARMING = 'warming',
  INVALIDATED = 'invalidated',
}

export enum InvalidationStrategy {
  TTL = 'ttl',
  EVENT = 'event',
  MANUAL = 'manual',
  LRU = 'lru',
  LFU = 'lfu',
  SIZE = 'size',
}

export enum CacheEventType {
  DATA_UPDATED = 'data_updated',
  SCHEMA_CHANGED = 'schema_changed',
  CONNECTION_MODIFIED = 'connection_modified',
  TRANSFORM_MODIFIED = 'transform_modified',
  MODEL_MODIFIED = 'model_modified',
  DASHBOARD_MODIFIED = 'dashboard_modified',
  CHART_MODIFIED = 'chart_modified',
  BULK_INVALIDATION = 'bulk_invalidation',
}

export enum CompressionType {
  NONE = 'none',
  GZIP = 'gzip',
  LZ4 = 'lz4',
  ZSTD = 'zstd',
}

// Cache Entry Types

export interface CacheEntryInfo {
  key: string;
  type: CacheType;
  size_bytes: number;
  compression: CompressionType;
  created_at: string;
  expires_at?: string | null;
  accessed_at: string;
  access_count: number;
  ttl_remaining: number;
  status: CacheStatus;
}

// TTL Policy Types

export interface TTLPolicy {
  id: string;
  name: string;
  description?: string | null;
  cache_type: CacheType;
  default_ttl_seconds: number;
  max_ttl_seconds: number;
  min_ttl_seconds: number;
  stale_while_revalidate_seconds: number;
  adaptive_ttl: boolean;
  adaptive_config?: Record<string, unknown> | null;
  created_at: string;
  updated_at?: string | null;
}

export interface TTLPolicyCreate {
  name: string;
  description?: string;
  cache_type: CacheType;
  default_ttl_seconds?: number;
  max_ttl_seconds?: number;
  min_ttl_seconds?: number;
  stale_while_revalidate_seconds?: number;
  adaptive_ttl?: boolean;
}

export interface TTLPolicyUpdate {
  name?: string;
  description?: string;
  default_ttl_seconds?: number;
  max_ttl_seconds?: number;
  min_ttl_seconds?: number;
  stale_while_revalidate_seconds?: number;
  adaptive_ttl?: boolean;
}

// Cache Warming Types

export interface CacheWarmingTask {
  id: string;
  name: string;
  description?: string | null;
  cache_type: CacheType;
  target_keys: Array<Record<string, unknown>>;
  schedule?: string | null;
  priority: number;
  enabled: boolean;
  last_run_at?: string | null;
  last_run_status?: string | null;
  last_run_duration_ms?: number | null;
  keys_warmed: number;
  created_at: string;
}

export interface CacheWarmingTaskCreate {
  name: string;
  description?: string;
  cache_type: CacheType;
  target_keys: Array<Record<string, unknown>>;
  schedule?: string;
  priority?: number;
  enabled?: boolean;
}

export interface CacheWarmingResult {
  task_id: string;
  started_at: string;
  completed_at: string;
  total_keys: number;
  keys_warmed: number;
  keys_failed: number;
  duration_ms: number;
  errors: Array<{ key: string; error: string }>;
}

// Invalidation Types

export interface InvalidationRule {
  id: string;
  name: string;
  description?: string | null;
  event_type: CacheEventType;
  target_cache_types: CacheType[];
  key_patterns: string[];
  delay_seconds: number;
  cascade: boolean;
  enabled: boolean;
  created_at: string;
}

export interface InvalidationRuleCreate {
  name: string;
  description?: string;
  event_type: CacheEventType;
  target_cache_types: CacheType[];
  key_patterns: string[];
  delay_seconds?: number;
  cascade?: boolean;
}

export interface InvalidationRequest {
  cache_type?: CacheType;
  key_pattern?: string;
  workspace_id?: string;
  tags?: string[];
  reason?: string;
}

export interface InvalidationResult {
  keys_matched: number;
  keys_invalidated: number;
  errors: number;
  duration_ms: number;
}

export interface InvalidationEvent {
  id: string;
  event_type: CacheEventType;
  source: string;
  affected_keys: string[];
  timestamp: string;
  metadata: Record<string, unknown>;
}

// Statistics Types

export interface CacheTypeStats {
  type: CacheType;
  entry_count: number;
  total_size_bytes: number;
  hit_count: number;
  miss_count: number;
  hit_rate: number;
  avg_entry_size_bytes: number;
  avg_ttl_seconds: number;
  oldest_entry_age_seconds: number;
  newest_entry_age_seconds: number;
}

export interface CacheStats {
  total_entries: number;
  total_size_bytes: number;
  total_hits: number;
  total_misses: number;
  overall_hit_rate: number;
  memory_used_bytes: number;
  memory_limit_bytes: number;
  memory_usage_percent: number;
  evictions: number;
  by_type: CacheTypeStats[];
  connected: boolean;
  uptime_seconds: number;
}

export interface CacheHealthStatus {
  healthy: boolean;
  redis_connected: boolean;
  memory_ok: boolean;
  hit_rate_ok: boolean;
  latency_ms: number;
  warnings: string[];
  last_check: string;
}

// Response Types

export interface TTLPolicyListResponse {
  policies: TTLPolicy[];
  total: number;
}

export interface CacheWarmingTaskListResponse {
  tasks: CacheWarmingTask[];
  total: number;
}

export interface InvalidationRuleListResponse {
  rules: InvalidationRule[];
  total: number;
}

export interface CacheKeyListResponse {
  keys: CacheEntryInfo[];
  total: number;
  cursor?: string | null;
}

export interface InvalidationEventListResponse {
  events: InvalidationEvent[];
  total: number;
}

// Constants

export const CACHE_TYPE_LABELS: Record<CacheType, string> = {
  [CacheType.QUERY_RESULT]: 'Query Result',
  [CacheType.DATASET_PREVIEW]: 'Dataset Preview',
  [CacheType.CHART_DATA]: 'Chart Data',
  [CacheType.DASHBOARD_DATA]: 'Dashboard Data',
  [CacheType.CONNECTION_SCHEMA]: 'Connection Schema',
  [CacheType.TABLE_METADATA]: 'Table Metadata',
  [CacheType.FILTER_OPTIONS]: 'Filter Options',
  [CacheType.KPI_VALUE]: 'KPI Value',
  [CacheType.TRANSFORM_RESULT]: 'Transform Result',
  [CacheType.API_RESPONSE]: 'API Response',
  [CacheType.USER_SESSION]: 'User Session',
  [CacheType.COMPUTED_METRIC]: 'Computed Metric',
};

export const CACHE_STATUS_LABELS: Record<CacheStatus, string> = {
  [CacheStatus.VALID]: 'Valid',
  [CacheStatus.STALE]: 'Stale',
  [CacheStatus.EXPIRED]: 'Expired',
  [CacheStatus.WARMING]: 'Warming',
  [CacheStatus.INVALIDATED]: 'Invalidated',
};

export const CACHE_STATUS_COLORS: Record<CacheStatus, string> = {
  [CacheStatus.VALID]: 'green',
  [CacheStatus.STALE]: 'yellow',
  [CacheStatus.EXPIRED]: 'red',
  [CacheStatus.WARMING]: 'blue',
  [CacheStatus.INVALIDATED]: 'gray',
};

export const CACHE_EVENT_LABELS: Record<CacheEventType, string> = {
  [CacheEventType.DATA_UPDATED]: 'Data Updated',
  [CacheEventType.SCHEMA_CHANGED]: 'Schema Changed',
  [CacheEventType.CONNECTION_MODIFIED]: 'Connection Modified',
  [CacheEventType.TRANSFORM_MODIFIED]: 'Transform Modified',
  [CacheEventType.MODEL_MODIFIED]: 'Model Modified',
  [CacheEventType.DASHBOARD_MODIFIED]: 'Dashboard Modified',
  [CacheEventType.CHART_MODIFIED]: 'Chart Modified',
  [CacheEventType.BULK_INVALIDATION]: 'Bulk Invalidation',
};

export const DEFAULT_TTL_BY_TYPE: Record<CacheType, number> = {
  [CacheType.QUERY_RESULT]: 3600,
  [CacheType.DATASET_PREVIEW]: 1800,
  [CacheType.CHART_DATA]: 900,
  [CacheType.DASHBOARD_DATA]: 600,
  [CacheType.CONNECTION_SCHEMA]: 7200,
  [CacheType.TABLE_METADATA]: 3600,
  [CacheType.FILTER_OPTIONS]: 1800,
  [CacheType.KPI_VALUE]: 300,
  [CacheType.TRANSFORM_RESULT]: 3600,
  [CacheType.API_RESPONSE]: 300,
  [CacheType.USER_SESSION]: 86400,
  [CacheType.COMPUTED_METRIC]: 600,
};

// Helper Functions

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function formatTTL(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}

export function formatHitRate(rate: number): string {
  return `${(rate * 100).toFixed(1)}%`;
}

export function getCacheStatusColor(status: CacheStatus): string {
  return CACHE_STATUS_COLORS[status] || 'gray';
}

export function getHealthStatusColor(healthy: boolean): string {
  return healthy ? 'green' : 'red';
}

export function calculateCacheEfficiency(stats: CacheStats): number {
  const totalOps = stats.total_hits + stats.total_misses;
  if (totalOps === 0) return 0;
  return stats.total_hits / totalOps;
}

export function estimateMemorySavings(stats: CacheStats): number {
  // Estimate based on hit rate and average entry size
  const avgSize = stats.total_entries > 0
    ? stats.total_size_bytes / stats.total_entries
    : 0;
  return stats.total_hits * avgSize;
}

// State Management

export interface CachingState {
  keys: CacheEntryInfo[];
  stats: CacheStats | null;
  health: CacheHealthStatus | null;
  policies: TTLPolicy[];
  warmingTasks: CacheWarmingTask[];
  invalidationRules: InvalidationRule[];
  invalidationEvents: InvalidationEvent[];
  isLoading: boolean;
  error: string | null;
  selectedCacheType: CacheType | null;
}

export function createInitialCachingState(): CachingState {
  return {
    keys: [],
    stats: null,
    health: null,
    policies: [],
    warmingTasks: [],
    invalidationRules: [],
    invalidationEvents: [],
    isLoading: false,
    error: null,
    selectedCacheType: null,
  };
}

// Cache Key Helpers

export function parseCacheKey(key: string): {
  type: string;
  identifier: string;
  workspace?: string;
  user?: string;
  params?: string;
} {
  const parts = key.split(':');
  const result: ReturnType<typeof parseCacheKey> = {
    type: parts[0] || '',
    identifier: parts[1] || '',
  };

  for (const part of parts.slice(2)) {
    if (part.startsWith('ws:')) {
      result.workspace = part.slice(3);
    } else if (part.startsWith('u:')) {
      result.user = part.slice(2);
    } else if (part.startsWith('p:')) {
      result.params = part.slice(2);
    }
  }

  return result;
}

export function formatCacheKey(key: string): string {
  const parsed = parseCacheKey(key);
  let formatted = `${parsed.type}/${parsed.identifier}`;
  if (parsed.workspace) formatted += ` [ws:${parsed.workspace.slice(0, 8)}]`;
  if (parsed.params) formatted += ` [${parsed.params}]`;
  return formatted;
}
