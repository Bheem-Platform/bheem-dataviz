"""
Query Optimization Schemas

Pydantic schemas for query plans, cost estimation, query suggestions,
and performance monitoring.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class QueryPlanNodeType(str, Enum):
    """Types of query plan nodes"""
    SEQ_SCAN = "seq_scan"
    INDEX_SCAN = "index_scan"
    INDEX_ONLY_SCAN = "index_only_scan"
    BITMAP_SCAN = "bitmap_scan"
    NESTED_LOOP = "nested_loop"
    HASH_JOIN = "hash_join"
    MERGE_JOIN = "merge_join"
    SORT = "sort"
    AGGREGATE = "aggregate"
    GROUP_BY = "group_by"
    LIMIT = "limit"
    SUBQUERY = "subquery"
    CTE = "cte"
    UNION = "union"
    MATERIALIZE = "materialize"
    FILTER = "filter"


class QueryComplexity(str, Enum):
    """Query complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class OptimizationStatus(str, Enum):
    """Optimization status"""
    NOT_ANALYZED = "not_analyzed"
    ANALYZING = "analyzing"
    OPTIMIZED = "optimized"
    NEEDS_ATTENTION = "needs_attention"
    CRITICAL = "critical"


class SuggestionPriority(str, Enum):
    """Suggestion priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuggestionCategory(str, Enum):
    """Categories of optimization suggestions"""
    INDEX = "index"
    JOIN = "join"
    FILTER = "filter"
    AGGREGATION = "aggregation"
    SUBQUERY = "subquery"
    LIMIT = "limit"
    CACHING = "caching"
    SCHEMA = "schema"
    STATISTICS = "statistics"


class QuerySourceType(str, Enum):
    """Source of the query"""
    CHART = "chart"
    DASHBOARD = "dashboard"
    SQL_LAB = "sql_lab"
    API = "api"
    TRANSFORM = "transform"
    SCHEDULED = "scheduled"
    KODEE = "kodee"


# Query Plan Models

class QueryPlanNode(BaseModel):
    """Node in a query execution plan"""
    id: str
    type: QueryPlanNodeType
    label: str
    table_name: Optional[str] = None
    index_name: Optional[str] = None
    condition: Optional[str] = None
    estimated_rows: int = 0
    actual_rows: Optional[int] = None
    estimated_cost: float = 0.0
    actual_cost: Optional[float] = None
    width: int = 0  # Average row width in bytes
    loops: int = 1
    startup_cost: float = 0.0
    total_cost: float = 0.0
    execution_time_ms: Optional[float] = None
    children: list["QueryPlanNode"] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    is_bottleneck: bool = False


class QueryPlan(BaseModel):
    """Complete query execution plan"""
    id: str
    query_hash: str
    sql: str
    connection_id: str
    root_node: QueryPlanNode
    total_cost: float
    estimated_rows: int
    actual_rows: Optional[int] = None
    execution_time_ms: Optional[float] = None
    planning_time_ms: Optional[float] = None
    complexity: QueryComplexity
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryPlanRequest(BaseModel):
    """Request to analyze a query plan"""
    sql: str
    connection_id: str
    explain_analyze: bool = False
    explain_buffers: bool = False
    explain_verbose: bool = False


class QueryPlanComparison(BaseModel):
    """Comparison between two query plans"""
    original_plan: QueryPlan
    optimized_plan: QueryPlan
    cost_reduction_percent: float
    row_estimate_diff: float
    execution_time_improvement_ms: Optional[float] = None
    improvements: list[str]


# Cost Estimation Models

class CostComponent(BaseModel):
    """Component of query cost"""
    name: str
    description: str
    estimated_cost: float
    percentage: float
    io_cost: float = 0.0
    cpu_cost: float = 0.0


class CostEstimate(BaseModel):
    """Query cost estimate"""
    query_hash: str
    total_cost: float
    io_cost: float
    cpu_cost: float
    startup_cost: float
    row_estimate: int
    width_estimate: int  # Average row width in bytes
    data_transfer_mb: float
    components: list[CostComponent]
    complexity: QueryComplexity
    estimated_duration_ms: float
    confidence: float  # 0-1, based on statistics freshness


class CostEstimateRequest(BaseModel):
    """Request for cost estimation"""
    sql: str
    connection_id: str
    include_components: bool = True


class ResourceUsageEstimate(BaseModel):
    """Estimated resource usage for a query"""
    memory_mb: float
    temp_space_mb: float
    io_operations: int
    cpu_time_ms: float
    network_transfer_mb: float


# Query Suggestion Models

class QuerySuggestion(BaseModel):
    """Optimization suggestion for a query"""
    id: str
    category: SuggestionCategory
    priority: SuggestionPriority
    title: str
    description: str
    impact: str
    original_snippet: Optional[str] = None
    suggested_snippet: Optional[str] = None
    estimated_improvement_percent: float
    implementation_effort: str  # low, medium, high
    auto_applicable: bool = False


class IndexSuggestion(BaseModel):
    """Suggested index creation"""
    table_name: str
    schema_name: str
    columns: list[str]
    index_type: str = "btree"  # btree, hash, gin, gist
    unique: bool = False
    partial_condition: Optional[str] = None
    estimated_size_mb: float
    estimated_improvement_percent: float
    create_statement: str
    priority: SuggestionPriority


class QueryRewrite(BaseModel):
    """Suggested query rewrite"""
    original_sql: str
    rewritten_sql: str
    rewrite_type: str  # join_order, subquery_to_join, add_index_hint, etc.
    description: str
    estimated_improvement_percent: float
    confidence: float


class OptimizationResult(BaseModel):
    """Result of query optimization analysis"""
    query_hash: str
    original_sql: str
    status: OptimizationStatus
    complexity: QueryComplexity
    cost_estimate: CostEstimate
    suggestions: list[QuerySuggestion]
    index_suggestions: list[IndexSuggestion]
    rewrites: list[QueryRewrite]
    bottlenecks: list[str]
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


# Query Performance Models

class QueryExecution(BaseModel):
    """Record of query execution"""
    id: str
    query_hash: str
    sql: str
    connection_id: str
    source_type: QuerySourceType
    source_id: Optional[str] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    execution_time_ms: float
    rows_returned: int
    rows_scanned: int
    bytes_processed: int
    cached: bool = False
    cache_hit: bool = False
    status: str  # success, error, timeout, cancelled
    error_message: Optional[str] = None
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryPerformanceStats(BaseModel):
    """Performance statistics for a query"""
    query_hash: str
    sql_preview: str
    execution_count: int
    total_execution_time_ms: float
    avg_execution_time_ms: float
    min_execution_time_ms: float
    max_execution_time_ms: float
    p50_execution_time_ms: float
    p95_execution_time_ms: float
    p99_execution_time_ms: float
    avg_rows_returned: float
    total_rows_scanned: int
    cache_hit_rate: float
    error_rate: float
    last_executed_at: datetime
    first_executed_at: datetime


class SlowQuery(BaseModel):
    """Slow query record"""
    id: str
    query_hash: str
    sql: str
    connection_id: str
    execution_time_ms: float
    threshold_ms: float
    rows_scanned: int
    rows_returned: int
    source_type: QuerySourceType
    source_id: Optional[str] = None
    user_id: Optional[str] = None
    optimization_status: OptimizationStatus
    suggestions_count: int
    executed_at: datetime


# Query History Models

class QueryHistoryEntry(BaseModel):
    """Entry in query history"""
    id: str
    query_hash: str
    sql: str
    connection_id: str
    source_type: QuerySourceType
    source_id: Optional[str] = None
    user_id: Optional[str] = None
    execution_time_ms: float
    rows_returned: int
    status: str
    executed_at: datetime
    tags: list[str] = Field(default_factory=list)


class QueryHistoryStats(BaseModel):
    """Statistics from query history"""
    total_queries: int
    unique_queries: int
    total_execution_time_ms: float
    avg_execution_time_ms: float
    slow_query_count: int
    error_count: int
    cache_hit_rate: float
    by_source: dict[str, int]
    by_hour: list[dict[str, Any]]
    top_slow_queries: list[SlowQuery]


# Configuration Models

class OptimizationConfig(BaseModel):
    """Query optimization configuration"""
    slow_query_threshold_ms: int = 1000
    auto_analyze: bool = True
    auto_suggest_indexes: bool = True
    max_suggestions_per_query: int = 10
    cache_plans: bool = True
    plan_cache_ttl_seconds: int = 3600
    collect_statistics: bool = True
    statistics_sample_rate: float = 0.1


class OptimizationConfigUpdate(BaseModel):
    """Update optimization configuration"""
    slow_query_threshold_ms: Optional[int] = None
    auto_analyze: Optional[bool] = None
    auto_suggest_indexes: Optional[bool] = None
    max_suggestions_per_query: Optional[int] = None
    cache_plans: Optional[bool] = None
    plan_cache_ttl_seconds: Optional[int] = None
    collect_statistics: Optional[bool] = None
    statistics_sample_rate: Optional[float] = None


# Response Models

class QueryPlanListResponse(BaseModel):
    """List query plans response"""
    plans: list[QueryPlan]
    total: int


class QuerySuggestionListResponse(BaseModel):
    """List query suggestions response"""
    suggestions: list[QuerySuggestion]
    total: int


class SlowQueryListResponse(BaseModel):
    """List slow queries response"""
    queries: list[SlowQuery]
    total: int


class QueryHistoryListResponse(BaseModel):
    """List query history response"""
    entries: list[QueryHistoryEntry]
    total: int


class IndexSuggestionListResponse(BaseModel):
    """List index suggestions response"""
    suggestions: list[IndexSuggestion]
    total: int


# Constants

COMPLEXITY_THRESHOLDS = {
    "simple": {"cost": 100, "joins": 0, "subqueries": 0},
    "moderate": {"cost": 1000, "joins": 2, "subqueries": 1},
    "complex": {"cost": 10000, "joins": 5, "subqueries": 3},
    "very_complex": {"cost": float("inf"), "joins": float("inf"), "subqueries": float("inf")},
}

SLOW_QUERY_THRESHOLDS = {
    "warning": 500,  # ms
    "slow": 1000,  # ms
    "very_slow": 5000,  # ms
    "critical": 30000,  # ms
}

SUGGESTION_TEMPLATES = {
    SuggestionCategory.INDEX: "Consider creating an index on {table}.{columns}",
    SuggestionCategory.JOIN: "Optimize join order: {suggestion}",
    SuggestionCategory.FILTER: "Add filter on {column} to reduce scanned rows",
    SuggestionCategory.AGGREGATION: "Pre-aggregate data or use materialized view",
    SuggestionCategory.SUBQUERY: "Convert subquery to JOIN for better performance",
    SuggestionCategory.LIMIT: "Add LIMIT clause to reduce result set",
    SuggestionCategory.CACHING: "Enable query caching for this frequently-run query",
}


# Helper Functions

def calculate_query_complexity(
    cost: float,
    join_count: int,
    subquery_count: int,
) -> QueryComplexity:
    """Calculate query complexity based on metrics."""
    if cost <= COMPLEXITY_THRESHOLDS["simple"]["cost"] and join_count == 0 and subquery_count == 0:
        return QueryComplexity.SIMPLE
    elif cost <= COMPLEXITY_THRESHOLDS["moderate"]["cost"] and join_count <= 2 and subquery_count <= 1:
        return QueryComplexity.MODERATE
    elif cost <= COMPLEXITY_THRESHOLDS["complex"]["cost"] and join_count <= 5 and subquery_count <= 3:
        return QueryComplexity.COMPLEX
    else:
        return QueryComplexity.VERY_COMPLEX


def get_slow_query_severity(execution_time_ms: float) -> str:
    """Get severity level for a slow query."""
    if execution_time_ms >= SLOW_QUERY_THRESHOLDS["critical"]:
        return "critical"
    elif execution_time_ms >= SLOW_QUERY_THRESHOLDS["very_slow"]:
        return "very_slow"
    elif execution_time_ms >= SLOW_QUERY_THRESHOLDS["slow"]:
        return "slow"
    elif execution_time_ms >= SLOW_QUERY_THRESHOLDS["warning"]:
        return "warning"
    return "normal"


def hash_query(sql: str) -> str:
    """Generate a hash for a SQL query."""
    import hashlib
    import re

    # Normalize whitespace
    normalized = " ".join(sql.split())
    # Remove comments
    normalized = re.sub(r'--.*$', '', normalized, flags=re.MULTILINE)
    normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
    # Lowercase
    normalized = normalized.lower().strip()

    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def estimate_row_width(columns: list[dict[str, Any]]) -> int:
    """Estimate average row width based on column types."""
    type_sizes = {
        "integer": 4,
        "bigint": 8,
        "smallint": 2,
        "real": 4,
        "double": 8,
        "numeric": 16,
        "boolean": 1,
        "date": 4,
        "timestamp": 8,
        "text": 100,  # Estimate
        "varchar": 50,  # Estimate
        "json": 500,  # Estimate
        "uuid": 16,
    }

    total = 24  # Header overhead
    for col in columns:
        col_type = col.get("type", "text").lower()
        for type_name, size in type_sizes.items():
            if type_name in col_type:
                total += size
                break
        else:
            total += 50  # Default estimate

    return total
