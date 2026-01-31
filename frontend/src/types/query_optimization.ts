/**
 * Query Optimization Types
 *
 * TypeScript types for query plans, cost estimation, optimization suggestions,
 * and performance monitoring.
 */

// Enums

export enum QueryPlanNodeType {
  SEQ_SCAN = 'seq_scan',
  INDEX_SCAN = 'index_scan',
  INDEX_ONLY_SCAN = 'index_only_scan',
  BITMAP_SCAN = 'bitmap_scan',
  NESTED_LOOP = 'nested_loop',
  HASH_JOIN = 'hash_join',
  MERGE_JOIN = 'merge_join',
  SORT = 'sort',
  AGGREGATE = 'aggregate',
  GROUP_BY = 'group_by',
  LIMIT = 'limit',
  SUBQUERY = 'subquery',
  CTE = 'cte',
  UNION = 'union',
  MATERIALIZE = 'materialize',
  FILTER = 'filter',
}

export enum QueryComplexity {
  SIMPLE = 'simple',
  MODERATE = 'moderate',
  COMPLEX = 'complex',
  VERY_COMPLEX = 'very_complex',
}

export enum OptimizationStatus {
  NOT_ANALYZED = 'not_analyzed',
  ANALYZING = 'analyzing',
  OPTIMIZED = 'optimized',
  NEEDS_ATTENTION = 'needs_attention',
  CRITICAL = 'critical',
}

export enum SuggestionPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum SuggestionCategory {
  INDEX = 'index',
  JOIN = 'join',
  FILTER = 'filter',
  AGGREGATION = 'aggregation',
  SUBQUERY = 'subquery',
  LIMIT = 'limit',
  CACHING = 'caching',
  SCHEMA = 'schema',
  STATISTICS = 'statistics',
}

export enum QuerySourceType {
  CHART = 'chart',
  DASHBOARD = 'dashboard',
  SQL_LAB = 'sql_lab',
  API = 'api',
  TRANSFORM = 'transform',
  SCHEDULED = 'scheduled',
  KODEE = 'kodee',
}

// Query Plan Types

export interface QueryPlanNode {
  id: string;
  type: QueryPlanNodeType;
  label: string;
  table_name?: string | null;
  index_name?: string | null;
  condition?: string | null;
  estimated_rows: number;
  actual_rows?: number | null;
  estimated_cost: number;
  actual_cost?: number | null;
  width: number;
  loops: number;
  startup_cost: number;
  total_cost: number;
  execution_time_ms?: number | null;
  children: QueryPlanNode[];
  warnings: string[];
  is_bottleneck: boolean;
}

export interface QueryPlan {
  id: string;
  query_hash: string;
  sql: string;
  connection_id: string;
  root_node: QueryPlanNode;
  total_cost: number;
  estimated_rows: number;
  actual_rows?: number | null;
  execution_time_ms?: number | null;
  planning_time_ms?: number | null;
  complexity: QueryComplexity;
  analyzed_at: string;
  metadata: Record<string, unknown>;
}

export interface QueryPlanRequest {
  sql: string;
  connection_id: string;
  explain_analyze?: boolean;
  explain_buffers?: boolean;
  explain_verbose?: boolean;
}

export interface QueryPlanComparison {
  original_plan: QueryPlan;
  optimized_plan: QueryPlan;
  cost_reduction_percent: number;
  row_estimate_diff: number;
  execution_time_improvement_ms?: number | null;
  improvements: string[];
}

// Cost Estimation Types

export interface CostComponent {
  name: string;
  description: string;
  estimated_cost: number;
  percentage: number;
  io_cost: number;
  cpu_cost: number;
}

export interface CostEstimate {
  query_hash: string;
  total_cost: number;
  io_cost: number;
  cpu_cost: number;
  startup_cost: number;
  row_estimate: number;
  width_estimate: number;
  data_transfer_mb: number;
  components: CostComponent[];
  complexity: QueryComplexity;
  estimated_duration_ms: number;
  confidence: number;
}

export interface CostEstimateRequest {
  sql: string;
  connection_id: string;
  include_components?: boolean;
}

export interface ResourceUsageEstimate {
  memory_mb: number;
  temp_space_mb: number;
  io_operations: number;
  cpu_time_ms: number;
  network_transfer_mb: number;
}

// Query Suggestion Types

export interface QuerySuggestion {
  id: string;
  category: SuggestionCategory;
  priority: SuggestionPriority;
  title: string;
  description: string;
  impact: string;
  original_snippet?: string | null;
  suggested_snippet?: string | null;
  estimated_improvement_percent: number;
  implementation_effort: string;
  auto_applicable: boolean;
}

export interface IndexSuggestion {
  table_name: string;
  schema_name: string;
  columns: string[];
  index_type: string;
  unique: boolean;
  partial_condition?: string | null;
  estimated_size_mb: number;
  estimated_improvement_percent: number;
  create_statement: string;
  priority: SuggestionPriority;
}

export interface QueryRewrite {
  original_sql: string;
  rewritten_sql: string;
  rewrite_type: string;
  description: string;
  estimated_improvement_percent: number;
  confidence: number;
}

export interface OptimizationResult {
  query_hash: string;
  original_sql: string;
  status: OptimizationStatus;
  complexity: QueryComplexity;
  cost_estimate: CostEstimate;
  suggestions: QuerySuggestion[];
  index_suggestions: IndexSuggestion[];
  rewrites: QueryRewrite[];
  bottlenecks: string[];
  analyzed_at: string;
}

// Query Execution Types

export interface QueryExecution {
  id: string;
  query_hash: string;
  sql: string;
  connection_id: string;
  source_type: QuerySourceType;
  source_id?: string | null;
  user_id?: string | null;
  workspace_id?: string | null;
  execution_time_ms: number;
  rows_returned: number;
  rows_scanned: number;
  bytes_processed: number;
  cached: boolean;
  cache_hit: boolean;
  status: string;
  error_message?: string | null;
  executed_at: string;
  metadata: Record<string, unknown>;
}

export interface QueryPerformanceStats {
  query_hash: string;
  sql_preview: string;
  execution_count: number;
  total_execution_time_ms: number;
  avg_execution_time_ms: number;
  min_execution_time_ms: number;
  max_execution_time_ms: number;
  p50_execution_time_ms: number;
  p95_execution_time_ms: number;
  p99_execution_time_ms: number;
  avg_rows_returned: number;
  total_rows_scanned: number;
  cache_hit_rate: number;
  error_rate: number;
  last_executed_at: string;
  first_executed_at: string;
}

export interface SlowQuery {
  id: string;
  query_hash: string;
  sql: string;
  connection_id: string;
  execution_time_ms: number;
  threshold_ms: number;
  rows_scanned: number;
  rows_returned: number;
  source_type: QuerySourceType;
  source_id?: string | null;
  user_id?: string | null;
  optimization_status: OptimizationStatus;
  suggestions_count: number;
  executed_at: string;
}

// Query History Types

export interface QueryHistoryEntry {
  id: string;
  query_hash: string;
  sql: string;
  connection_id: string;
  source_type: QuerySourceType;
  source_id?: string | null;
  user_id?: string | null;
  execution_time_ms: number;
  rows_returned: number;
  status: string;
  executed_at: string;
  tags: string[];
}

export interface QueryHistoryStats {
  total_queries: number;
  unique_queries: number;
  total_execution_time_ms: number;
  avg_execution_time_ms: number;
  slow_query_count: number;
  error_count: number;
  cache_hit_rate: number;
  by_source: Record<string, number>;
  by_hour: Array<Record<string, unknown>>;
  top_slow_queries: SlowQuery[];
}

// Configuration Types

export interface OptimizationConfig {
  slow_query_threshold_ms: number;
  auto_analyze: boolean;
  auto_suggest_indexes: boolean;
  max_suggestions_per_query: number;
  cache_plans: boolean;
  plan_cache_ttl_seconds: number;
  collect_statistics: boolean;
  statistics_sample_rate: number;
}

export interface OptimizationConfigUpdate {
  slow_query_threshold_ms?: number;
  auto_analyze?: boolean;
  auto_suggest_indexes?: boolean;
  max_suggestions_per_query?: number;
  cache_plans?: boolean;
  plan_cache_ttl_seconds?: number;
  collect_statistics?: boolean;
  statistics_sample_rate?: number;
}

// Response Types

export interface QueryPlanListResponse {
  plans: QueryPlan[];
  total: number;
}

export interface QuerySuggestionListResponse {
  suggestions: QuerySuggestion[];
  total: number;
}

export interface SlowQueryListResponse {
  queries: SlowQuery[];
  total: number;
}

export interface QueryHistoryListResponse {
  entries: QueryHistoryEntry[];
  total: number;
}

export interface IndexSuggestionListResponse {
  suggestions: IndexSuggestion[];
  total: number;
}

// Dashboard Types

export interface OptimizationDashboardSummary {
  total_queries_analyzed: number;
  slow_queries_count: number;
  critical_queries_count: number;
  avg_execution_time_ms: number;
  cache_hit_rate: number;
  pending_suggestions: number;
  recent_improvements: number;
  top_bottlenecks: string[];
}

export interface PerformanceTrend {
  date: string;
  total_queries: number;
  avg_execution_time_ms: number;
  slow_queries: number;
  cache_hit_rate: number;
}

// Constants

export const COMPLEXITY_LABELS: Record<QueryComplexity, string> = {
  [QueryComplexity.SIMPLE]: 'Simple',
  [QueryComplexity.MODERATE]: 'Moderate',
  [QueryComplexity.COMPLEX]: 'Complex',
  [QueryComplexity.VERY_COMPLEX]: 'Very Complex',
};

export const COMPLEXITY_COLORS: Record<QueryComplexity, string> = {
  [QueryComplexity.SIMPLE]: 'green',
  [QueryComplexity.MODERATE]: 'blue',
  [QueryComplexity.COMPLEX]: 'yellow',
  [QueryComplexity.VERY_COMPLEX]: 'red',
};

export const OPTIMIZATION_STATUS_LABELS: Record<OptimizationStatus, string> = {
  [OptimizationStatus.NOT_ANALYZED]: 'Not Analyzed',
  [OptimizationStatus.ANALYZING]: 'Analyzing',
  [OptimizationStatus.OPTIMIZED]: 'Optimized',
  [OptimizationStatus.NEEDS_ATTENTION]: 'Needs Attention',
  [OptimizationStatus.CRITICAL]: 'Critical',
};

export const OPTIMIZATION_STATUS_COLORS: Record<OptimizationStatus, string> = {
  [OptimizationStatus.NOT_ANALYZED]: 'gray',
  [OptimizationStatus.ANALYZING]: 'blue',
  [OptimizationStatus.OPTIMIZED]: 'green',
  [OptimizationStatus.NEEDS_ATTENTION]: 'yellow',
  [OptimizationStatus.CRITICAL]: 'red',
};

export const SUGGESTION_PRIORITY_LABELS: Record<SuggestionPriority, string> = {
  [SuggestionPriority.LOW]: 'Low',
  [SuggestionPriority.MEDIUM]: 'Medium',
  [SuggestionPriority.HIGH]: 'High',
  [SuggestionPriority.CRITICAL]: 'Critical',
};

export const SUGGESTION_PRIORITY_COLORS: Record<SuggestionPriority, string> = {
  [SuggestionPriority.LOW]: 'gray',
  [SuggestionPriority.MEDIUM]: 'blue',
  [SuggestionPriority.HIGH]: 'yellow',
  [SuggestionPriority.CRITICAL]: 'red',
};

export const SUGGESTION_CATEGORY_LABELS: Record<SuggestionCategory, string> = {
  [SuggestionCategory.INDEX]: 'Index',
  [SuggestionCategory.JOIN]: 'Join',
  [SuggestionCategory.FILTER]: 'Filter',
  [SuggestionCategory.AGGREGATION]: 'Aggregation',
  [SuggestionCategory.SUBQUERY]: 'Subquery',
  [SuggestionCategory.LIMIT]: 'Limit',
  [SuggestionCategory.CACHING]: 'Caching',
  [SuggestionCategory.SCHEMA]: 'Schema',
  [SuggestionCategory.STATISTICS]: 'Statistics',
};

export const QUERY_SOURCE_LABELS: Record<QuerySourceType, string> = {
  [QuerySourceType.CHART]: 'Chart',
  [QuerySourceType.DASHBOARD]: 'Dashboard',
  [QuerySourceType.SQL_LAB]: 'SQL Lab',
  [QuerySourceType.API]: 'API',
  [QuerySourceType.TRANSFORM]: 'Transform',
  [QuerySourceType.SCHEDULED]: 'Scheduled',
  [QuerySourceType.KODEE]: 'Kodee',
};

export const NODE_TYPE_LABELS: Record<QueryPlanNodeType, string> = {
  [QueryPlanNodeType.SEQ_SCAN]: 'Sequential Scan',
  [QueryPlanNodeType.INDEX_SCAN]: 'Index Scan',
  [QueryPlanNodeType.INDEX_ONLY_SCAN]: 'Index Only Scan',
  [QueryPlanNodeType.BITMAP_SCAN]: 'Bitmap Scan',
  [QueryPlanNodeType.NESTED_LOOP]: 'Nested Loop',
  [QueryPlanNodeType.HASH_JOIN]: 'Hash Join',
  [QueryPlanNodeType.MERGE_JOIN]: 'Merge Join',
  [QueryPlanNodeType.SORT]: 'Sort',
  [QueryPlanNodeType.AGGREGATE]: 'Aggregate',
  [QueryPlanNodeType.GROUP_BY]: 'Group By',
  [QueryPlanNodeType.LIMIT]: 'Limit',
  [QueryPlanNodeType.SUBQUERY]: 'Subquery',
  [QueryPlanNodeType.CTE]: 'CTE',
  [QueryPlanNodeType.UNION]: 'Union',
  [QueryPlanNodeType.MATERIALIZE]: 'Materialize',
  [QueryPlanNodeType.FILTER]: 'Filter',
};

export const SLOW_QUERY_THRESHOLDS = {
  warning: 500,
  slow: 1000,
  very_slow: 5000,
  critical: 30000,
};

// Helper Functions

export function formatExecutionTime(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(0)}μs`;
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

export function formatCost(cost: number): string {
  if (cost < 1000) return cost.toFixed(2);
  if (cost < 1000000) return `${(cost / 1000).toFixed(1)}K`;
  return `${(cost / 1000000).toFixed(1)}M`;
}

export function formatRows(rows: number): string {
  if (rows < 1000) return rows.toString();
  if (rows < 1000000) return `${(rows / 1000).toFixed(1)}K`;
  return `${(rows / 1000000).toFixed(1)}M`;
}

export function getSlowQuerySeverity(executionTimeMs: number): string {
  if (executionTimeMs >= SLOW_QUERY_THRESHOLDS.critical) return 'critical';
  if (executionTimeMs >= SLOW_QUERY_THRESHOLDS.very_slow) return 'very_slow';
  if (executionTimeMs >= SLOW_QUERY_THRESHOLDS.slow) return 'slow';
  if (executionTimeMs >= SLOW_QUERY_THRESHOLDS.warning) return 'warning';
  return 'normal';
}

export function getSlowQuerySeverityColor(severity: string): string {
  switch (severity) {
    case 'critical':
      return 'red';
    case 'very_slow':
      return 'orange';
    case 'slow':
      return 'yellow';
    case 'warning':
      return 'blue';
    default:
      return 'green';
  }
}

export function getComplexityColor(complexity: QueryComplexity): string {
  return COMPLEXITY_COLORS[complexity] || 'gray';
}

export function getOptimizationStatusColor(status: OptimizationStatus): string {
  return OPTIMIZATION_STATUS_COLORS[status] || 'gray';
}

export function getPriorityColor(priority: SuggestionPriority): string {
  return SUGGESTION_PRIORITY_COLORS[priority] || 'gray';
}

export function calculateImprovement(original: number, optimized: number): number {
  if (original === 0) return 0;
  return ((original - optimized) / original) * 100;
}

export function isBottleneckNode(node: QueryPlanNode): boolean {
  return (
    node.is_bottleneck ||
    node.type === QueryPlanNodeType.SEQ_SCAN ||
    (node.estimated_rows > 10000 && node.type === QueryPlanNodeType.NESTED_LOOP)
  );
}

export function getNodeWarnings(node: QueryPlanNode): string[] {
  const warnings: string[] = [...node.warnings];

  if (node.type === QueryPlanNodeType.SEQ_SCAN && node.estimated_rows > 1000) {
    warnings.push('Sequential scan on large table - consider adding an index');
  }

  if (node.actual_rows != null && node.estimated_rows > 0) {
    const ratio = node.actual_rows / node.estimated_rows;
    if (ratio > 10 || ratio < 0.1) {
      warnings.push('Row estimate significantly different from actual - statistics may be stale');
    }
  }

  return warnings;
}

// State Management

export interface QueryOptimizationState {
  plans: QueryPlan[];
  currentPlan: QueryPlan | null;
  suggestions: QuerySuggestion[];
  indexSuggestions: IndexSuggestion[];
  slowQueries: SlowQuery[];
  history: QueryHistoryEntry[];
  historyStats: QueryHistoryStats | null;
  config: OptimizationConfig | null;
  dashboardSummary: OptimizationDashboardSummary | null;
  performanceTrends: PerformanceTrend[];
  isLoading: boolean;
  isAnalyzing: boolean;
  error: string | null;
}

export function createInitialQueryOptimizationState(): QueryOptimizationState {
  return {
    plans: [],
    currentPlan: null,
    suggestions: [],
    indexSuggestions: [],
    slowQueries: [],
    history: [],
    historyStats: null,
    config: null,
    dashboardSummary: null,
    performanceTrends: [],
    isLoading: false,
    isAnalyzing: false,
    error: null,
  };
}
