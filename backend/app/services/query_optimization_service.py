"""
Query Optimization Service

Business logic for query plans, cost estimation, query suggestions,
and performance monitoring.
"""

import uuid
import re
from datetime import datetime, timedelta
from typing import Optional, Any
from collections import defaultdict

from app.schemas.query_optimization import (
    QueryPlanNodeType,
    QueryComplexity,
    OptimizationStatus,
    SuggestionPriority,
    SuggestionCategory,
    QuerySourceType,
    QueryPlanNode,
    QueryPlan,
    QueryPlanRequest,
    QueryPlanComparison,
    CostComponent,
    CostEstimate,
    CostEstimateRequest,
    ResourceUsageEstimate,
    QuerySuggestion,
    IndexSuggestion,
    QueryRewrite,
    OptimizationResult,
    QueryExecution,
    QueryPerformanceStats,
    SlowQuery,
    QueryHistoryEntry,
    QueryHistoryStats,
    OptimizationConfig,
    OptimizationConfigUpdate,
    QueryPlanListResponse,
    QuerySuggestionListResponse,
    SlowQueryListResponse,
    QueryHistoryListResponse,
    IndexSuggestionListResponse,
    calculate_query_complexity,
    get_slow_query_severity,
    hash_query,
    SLOW_QUERY_THRESHOLDS,
)


class QueryOptimizationService:
    """Service for query optimization."""

    def __init__(self, db=None):
        self.db = db
        # In-memory stores
        self._query_plans: dict[str, QueryPlan] = {}
        self._query_executions: list[QueryExecution] = []
        self._slow_queries: list[SlowQuery] = []
        self._index_suggestions: dict[str, IndexSuggestion] = {}
        self._config = OptimizationConfig()
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize sample data."""
        # Sample slow query
        slow_query = SlowQuery(
            id="slow_001",
            query_hash="abc123def456",
            sql="SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.created_at > '2024-01-01'",
            connection_id="conn_001",
            execution_time_ms=3500,
            threshold_ms=1000,
            rows_scanned=1500000,
            rows_returned=50000,
            source_type=QuerySourceType.CHART,
            source_id="chart_001",
            optimization_status=OptimizationStatus.NEEDS_ATTENTION,
            suggestions_count=3,
            executed_at=datetime.utcnow() - timedelta(hours=2),
        )
        self._slow_queries.append(slow_query)

        # Sample index suggestion
        index_suggestion = IndexSuggestion(
            table_name="orders",
            schema_name="public",
            columns=["customer_id", "created_at"],
            index_type="btree",
            unique=False,
            estimated_size_mb=25.5,
            estimated_improvement_percent=45.0,
            create_statement="CREATE INDEX idx_orders_customer_created ON public.orders (customer_id, created_at)",
            priority=SuggestionPriority.HIGH,
        )
        self._index_suggestions["idx_orders_customer_created"] = index_suggestion

    # ==================== QUERY PLAN ANALYSIS ====================

    async def analyze_query_plan(self, request: QueryPlanRequest) -> QueryPlan:
        """Analyze a query and return its execution plan."""
        query_hash = hash_query(request.sql)

        # Parse SQL to extract information
        parsed = self._parse_sql(request.sql)

        # Build plan tree
        root_node = self._build_plan_tree(parsed)

        # Calculate complexity
        complexity = calculate_query_complexity(
            cost=root_node.total_cost,
            join_count=parsed.get("join_count", 0),
            subquery_count=parsed.get("subquery_count", 0),
        )

        plan = QueryPlan(
            id=f"plan_{uuid.uuid4().hex[:12]}",
            query_hash=query_hash,
            sql=request.sql,
            connection_id=request.connection_id,
            root_node=root_node,
            total_cost=root_node.total_cost,
            estimated_rows=root_node.estimated_rows,
            complexity=complexity,
            metadata={"parsed": parsed},
        )

        self._query_plans[plan.id] = plan
        return plan

    def _parse_sql(self, sql: str) -> dict[str, Any]:
        """Parse SQL to extract query components."""
        sql_upper = sql.upper()

        # Count joins
        join_count = len(re.findall(r'\bJOIN\b', sql_upper))

        # Count subqueries
        subquery_count = sql_upper.count('(SELECT')

        # Detect aggregations
        has_aggregation = any(
            agg in sql_upper for agg in ['COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(', 'GROUP BY']
        )

        # Detect sorting
        has_order_by = 'ORDER BY' in sql_upper

        # Detect limit
        has_limit = 'LIMIT' in sql_upper

        # Extract tables (simplified)
        tables = re.findall(r'\bFROM\s+(\w+)', sql, re.IGNORECASE)
        tables.extend(re.findall(r'\bJOIN\s+(\w+)', sql, re.IGNORECASE))

        # Extract columns in WHERE
        where_columns = re.findall(r'WHERE.*?(\w+)\s*[=<>]', sql, re.IGNORECASE)

        return {
            "join_count": join_count,
            "subquery_count": subquery_count,
            "has_aggregation": has_aggregation,
            "has_order_by": has_order_by,
            "has_limit": has_limit,
            "tables": list(set(tables)),
            "where_columns": where_columns,
        }

    def _build_plan_tree(self, parsed: dict[str, Any]) -> QueryPlanNode:
        """Build a simulated query plan tree."""
        children = []
        total_cost = 100.0  # Base cost

        # Add scan nodes for tables
        for i, table in enumerate(parsed.get("tables", [])):
            scan_type = QueryPlanNodeType.SEQ_SCAN
            if i > 0:  # Assume index available for joined tables
                scan_type = QueryPlanNodeType.INDEX_SCAN

            scan_node = QueryPlanNode(
                id=f"scan_{i}",
                type=scan_type,
                label=f"{'Index' if scan_type == QueryPlanNodeType.INDEX_SCAN else 'Sequential'} Scan on {table}",
                table_name=table,
                estimated_rows=10000 // (i + 1),
                estimated_cost=50.0 / (i + 1),
                total_cost=50.0 / (i + 1),
            )
            children.append(scan_node)
            total_cost += scan_node.total_cost

        # Add join nodes
        for i in range(parsed.get("join_count", 0)):
            join_node = QueryPlanNode(
                id=f"join_{i}",
                type=QueryPlanNodeType.HASH_JOIN,
                label=f"Hash Join",
                estimated_rows=5000,
                estimated_cost=200.0,
                total_cost=200.0,
            )
            total_cost += join_node.total_cost

        # Add aggregation if present
        if parsed.get("has_aggregation"):
            agg_node = QueryPlanNode(
                id="aggregate",
                type=QueryPlanNodeType.AGGREGATE,
                label="Aggregate",
                estimated_rows=100,
                estimated_cost=50.0,
                total_cost=50.0,
            )
            total_cost += agg_node.total_cost

        # Add sort if present
        if parsed.get("has_order_by"):
            sort_node = QueryPlanNode(
                id="sort",
                type=QueryPlanNodeType.SORT,
                label="Sort",
                estimated_rows=1000,
                estimated_cost=100.0,
                total_cost=100.0,
            )
            total_cost += sort_node.total_cost

        # Root node
        root = QueryPlanNode(
            id="root",
            type=QueryPlanNodeType.SEQ_SCAN if len(parsed.get("tables", [])) == 1 else QueryPlanNodeType.HASH_JOIN,
            label="Query Result",
            estimated_rows=1000,
            estimated_cost=total_cost,
            total_cost=total_cost,
            children=children,
        )

        # Mark bottlenecks
        if total_cost > 1000:
            root.is_bottleneck = True
            root.warnings.append("High total cost - consider optimization")

        return root

    async def get_query_plan(self, plan_id: str) -> Optional[QueryPlan]:
        """Get a query plan by ID."""
        return self._query_plans.get(plan_id)

    async def list_query_plans(
        self,
        connection_id: Optional[str] = None,
        complexity: Optional[QueryComplexity] = None,
        limit: int = 50,
    ) -> QueryPlanListResponse:
        """List query plans."""
        plans = list(self._query_plans.values())

        if connection_id:
            plans = [p for p in plans if p.connection_id == connection_id]
        if complexity:
            plans = [p for p in plans if p.complexity == complexity]

        plans = sorted(plans, key=lambda p: p.analyzed_at, reverse=True)[:limit]

        return QueryPlanListResponse(plans=plans, total=len(plans))

    async def compare_plans(
        self, original_sql: str, optimized_sql: str, connection_id: str
    ) -> QueryPlanComparison:
        """Compare two query plans."""
        original = await self.analyze_query_plan(
            QueryPlanRequest(sql=original_sql, connection_id=connection_id)
        )
        optimized = await self.analyze_query_plan(
            QueryPlanRequest(sql=optimized_sql, connection_id=connection_id)
        )

        cost_reduction = 0.0
        if original.total_cost > 0:
            cost_reduction = ((original.total_cost - optimized.total_cost) / original.total_cost) * 100

        row_diff = optimized.estimated_rows - original.estimated_rows

        improvements = []
        if cost_reduction > 0:
            improvements.append(f"Cost reduced by {cost_reduction:.1f}%")
        if optimized.complexity.value < original.complexity.value:
            improvements.append(f"Complexity reduced from {original.complexity.value} to {optimized.complexity.value}")

        return QueryPlanComparison(
            original_plan=original,
            optimized_plan=optimized,
            cost_reduction_percent=cost_reduction,
            row_estimate_diff=row_diff,
            improvements=improvements,
        )

    # ==================== COST ESTIMATION ====================

    async def estimate_cost(self, request: CostEstimateRequest) -> CostEstimate:
        """Estimate query execution cost."""
        query_hash = hash_query(request.sql)
        parsed = self._parse_sql(request.sql)

        # Calculate base costs
        io_cost = 50.0 * len(parsed.get("tables", []))
        cpu_cost = 25.0 + (10.0 * parsed.get("join_count", 0))
        startup_cost = 10.0

        total_cost = io_cost + cpu_cost + startup_cost

        # Add costs for operations
        if parsed.get("has_aggregation"):
            cpu_cost += 50.0
            total_cost += 50.0
        if parsed.get("has_order_by"):
            cpu_cost += 30.0
            total_cost += 30.0

        # Estimate rows and width
        row_estimate = 1000 * len(parsed.get("tables", []))
        if parsed.get("has_limit"):
            row_estimate = min(row_estimate, 100)

        width_estimate = 100  # bytes per row

        # Estimate data transfer
        data_transfer_mb = (row_estimate * width_estimate) / (1024 * 1024)

        # Calculate complexity
        complexity = calculate_query_complexity(
            total_cost, parsed.get("join_count", 0), parsed.get("subquery_count", 0)
        )

        # Estimate duration
        estimated_duration = total_cost * 0.5  # Simplified: 0.5ms per cost unit

        # Build components
        components = []
        if request.include_components:
            if io_cost > 0:
                components.append(CostComponent(
                    name="I/O Operations",
                    description="Reading data from disk/cache",
                    estimated_cost=io_cost,
                    percentage=(io_cost / total_cost) * 100,
                    io_cost=io_cost,
                ))
            if cpu_cost > 0:
                components.append(CostComponent(
                    name="CPU Processing",
                    description="Filtering, joining, and computing",
                    estimated_cost=cpu_cost,
                    percentage=(cpu_cost / total_cost) * 100,
                    cpu_cost=cpu_cost,
                ))
            if startup_cost > 0:
                components.append(CostComponent(
                    name="Startup",
                    description="Query planning and initialization",
                    estimated_cost=startup_cost,
                    percentage=(startup_cost / total_cost) * 100,
                ))

        return CostEstimate(
            query_hash=query_hash,
            total_cost=total_cost,
            io_cost=io_cost,
            cpu_cost=cpu_cost,
            startup_cost=startup_cost,
            row_estimate=row_estimate,
            width_estimate=width_estimate,
            data_transfer_mb=data_transfer_mb,
            components=components,
            complexity=complexity,
            estimated_duration_ms=estimated_duration,
            confidence=0.85,
        )

    async def estimate_resources(self, sql: str, connection_id: str) -> ResourceUsageEstimate:
        """Estimate resource usage for a query."""
        cost = await self.estimate_cost(CostEstimateRequest(sql=sql, connection_id=connection_id))

        return ResourceUsageEstimate(
            memory_mb=cost.row_estimate * cost.width_estimate / (1024 * 1024) * 2,  # 2x for working memory
            temp_space_mb=cost.data_transfer_mb * 0.5,
            io_operations=int(cost.io_cost * 10),
            cpu_time_ms=cost.cpu_cost * 0.3,
            network_transfer_mb=cost.data_transfer_mb,
        )

    # ==================== OPTIMIZATION SUGGESTIONS ====================

    async def analyze_and_suggest(
        self, sql: str, connection_id: str
    ) -> OptimizationResult:
        """Analyze a query and generate optimization suggestions."""
        query_hash = hash_query(sql)
        parsed = self._parse_sql(sql)
        cost = await self.estimate_cost(CostEstimateRequest(sql=sql, connection_id=connection_id))

        suggestions = []
        index_suggestions = []
        rewrites = []
        bottlenecks = []

        # Check for missing WHERE clause on large tables
        if not re.search(r'\bWHERE\b', sql, re.IGNORECASE) and len(parsed.get("tables", [])) > 0:
            suggestions.append(QuerySuggestion(
                id=f"sug_{uuid.uuid4().hex[:8]}",
                category=SuggestionCategory.FILTER,
                priority=SuggestionPriority.HIGH,
                title="Add WHERE clause",
                description="Query scans entire table without filtering. Add a WHERE clause to reduce rows scanned.",
                impact="Could reduce execution time by 50-90%",
                estimated_improvement_percent=70.0,
                implementation_effort="low",
                auto_applicable=False,
            ))

        # Check for SELECT *
        if re.search(r'SELECT\s+\*', sql, re.IGNORECASE):
            suggestions.append(QuerySuggestion(
                id=f"sug_{uuid.uuid4().hex[:8]}",
                category=SuggestionCategory.FILTER,
                priority=SuggestionPriority.MEDIUM,
                title="Specify columns instead of SELECT *",
                description="Using SELECT * retrieves all columns. Specify only needed columns to reduce data transfer.",
                impact="Reduces data transfer and memory usage",
                estimated_improvement_percent=20.0,
                implementation_effort="low",
                auto_applicable=False,
            ))

        # Check for missing LIMIT
        if not parsed.get("has_limit") and not parsed.get("has_aggregation"):
            suggestions.append(QuerySuggestion(
                id=f"sug_{uuid.uuid4().hex[:8]}",
                category=SuggestionCategory.LIMIT,
                priority=SuggestionPriority.MEDIUM,
                title="Add LIMIT clause",
                description="Query returns all matching rows. Add LIMIT to prevent returning excessive data.",
                impact="Prevents memory issues and improves response time",
                estimated_improvement_percent=30.0,
                implementation_effort="low",
                auto_applicable=True,
            ))

        # Suggest indexes for WHERE columns
        for column in parsed.get("where_columns", []):
            for table in parsed.get("tables", []):
                index_suggestions.append(IndexSuggestion(
                    table_name=table,
                    schema_name="public",
                    columns=[column],
                    index_type="btree",
                    unique=False,
                    estimated_size_mb=10.0,
                    estimated_improvement_percent=40.0,
                    create_statement=f"CREATE INDEX idx_{table}_{column} ON public.{table} ({column})",
                    priority=SuggestionPriority.HIGH,
                ))

        # Check for subqueries that could be JOINs
        if parsed.get("subquery_count", 0) > 0:
            suggestions.append(QuerySuggestion(
                id=f"sug_{uuid.uuid4().hex[:8]}",
                category=SuggestionCategory.SUBQUERY,
                priority=SuggestionPriority.HIGH,
                title="Convert subquery to JOIN",
                description="Subqueries can often be rewritten as JOINs for better performance.",
                impact="Can significantly reduce execution time",
                estimated_improvement_percent=50.0,
                implementation_effort="medium",
                auto_applicable=False,
            ))

        # Identify bottlenecks
        if cost.total_cost > 1000:
            bottlenecks.append("High total query cost")
        if cost.io_cost > cost.cpu_cost * 2:
            bottlenecks.append("I/O bound - consider adding indexes")
        if parsed.get("join_count", 0) > 3:
            bottlenecks.append("Multiple joins - consider optimizing join order")

        # Determine status
        status = OptimizationStatus.OPTIMIZED
        if len(bottlenecks) > 0 or cost.total_cost > 500:
            status = OptimizationStatus.NEEDS_ATTENTION
        if cost.total_cost > 5000 or len(suggestions) > 5:
            status = OptimizationStatus.CRITICAL

        return OptimizationResult(
            query_hash=query_hash,
            original_sql=sql,
            status=status,
            complexity=cost.complexity,
            cost_estimate=cost,
            suggestions=suggestions,
            index_suggestions=index_suggestions[:5],  # Limit suggestions
            rewrites=rewrites,
            bottlenecks=bottlenecks,
        )

    async def list_index_suggestions(
        self,
        connection_id: Optional[str] = None,
        priority: Optional[SuggestionPriority] = None,
    ) -> IndexSuggestionListResponse:
        """List index suggestions."""
        suggestions = list(self._index_suggestions.values())

        if priority:
            suggestions = [s for s in suggestions if s.priority == priority]

        return IndexSuggestionListResponse(suggestions=suggestions, total=len(suggestions))

    # ==================== QUERY EXECUTION TRACKING ====================

    async def record_execution(
        self,
        sql: str,
        connection_id: str,
        execution_time_ms: float,
        rows_returned: int,
        rows_scanned: int,
        source_type: QuerySourceType,
        source_id: Optional[str] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        cached: bool = False,
        cache_hit: bool = False,
    ) -> QueryExecution:
        """Record a query execution."""
        query_hash = hash_query(sql)

        execution = QueryExecution(
            id=f"exec_{uuid.uuid4().hex[:12]}",
            query_hash=query_hash,
            sql=sql,
            connection_id=connection_id,
            source_type=source_type,
            source_id=source_id,
            user_id=user_id,
            workspace_id=workspace_id,
            execution_time_ms=execution_time_ms,
            rows_returned=rows_returned,
            rows_scanned=rows_scanned,
            bytes_processed=rows_scanned * 100,  # Estimate
            cached=cached,
            cache_hit=cache_hit,
            status=status,
            error_message=error_message,
        )

        self._query_executions.append(execution)

        # Check if it's a slow query
        if execution_time_ms >= self._config.slow_query_threshold_ms and status == "success":
            slow_query = SlowQuery(
                id=f"slow_{uuid.uuid4().hex[:12]}",
                query_hash=query_hash,
                sql=sql,
                connection_id=connection_id,
                execution_time_ms=execution_time_ms,
                threshold_ms=self._config.slow_query_threshold_ms,
                rows_scanned=rows_scanned,
                rows_returned=rows_returned,
                source_type=source_type,
                source_id=source_id,
                user_id=user_id,
                optimization_status=OptimizationStatus.NOT_ANALYZED,
                suggestions_count=0,
                executed_at=datetime.utcnow(),
            )
            self._slow_queries.append(slow_query)

        return execution

    async def get_query_stats(self, query_hash: str) -> Optional[QueryPerformanceStats]:
        """Get performance statistics for a query."""
        executions = [e for e in self._query_executions if e.query_hash == query_hash]

        if not executions:
            return None

        times = [e.execution_time_ms for e in executions]
        times.sort()

        cache_hits = sum(1 for e in executions if e.cache_hit)
        errors = sum(1 for e in executions if e.status == "error")

        return QueryPerformanceStats(
            query_hash=query_hash,
            sql_preview=executions[0].sql[:100] + "..." if len(executions[0].sql) > 100 else executions[0].sql,
            execution_count=len(executions),
            total_execution_time_ms=sum(times),
            avg_execution_time_ms=sum(times) / len(times),
            min_execution_time_ms=min(times),
            max_execution_time_ms=max(times),
            p50_execution_time_ms=times[len(times) // 2],
            p95_execution_time_ms=times[int(len(times) * 0.95)] if len(times) >= 20 else times[-1],
            p99_execution_time_ms=times[int(len(times) * 0.99)] if len(times) >= 100 else times[-1],
            avg_rows_returned=sum(e.rows_returned for e in executions) / len(executions),
            total_rows_scanned=sum(e.rows_scanned for e in executions),
            cache_hit_rate=cache_hits / len(executions) if executions else 0,
            error_rate=errors / len(executions) if executions else 0,
            last_executed_at=max(e.executed_at for e in executions),
            first_executed_at=min(e.executed_at for e in executions),
        )

    async def list_slow_queries(
        self,
        connection_id: Optional[str] = None,
        source_type: Optional[QuerySourceType] = None,
        min_execution_time_ms: Optional[float] = None,
        limit: int = 50,
    ) -> SlowQueryListResponse:
        """List slow queries."""
        queries = list(self._slow_queries)

        if connection_id:
            queries = [q for q in queries if q.connection_id == connection_id]
        if source_type:
            queries = [q for q in queries if q.source_type == source_type]
        if min_execution_time_ms:
            queries = [q for q in queries if q.execution_time_ms >= min_execution_time_ms]

        queries = sorted(queries, key=lambda q: q.execution_time_ms, reverse=True)[:limit]

        return SlowQueryListResponse(queries=queries, total=len(queries))

    async def list_query_history(
        self,
        connection_id: Optional[str] = None,
        source_type: Optional[QuerySourceType] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> QueryHistoryListResponse:
        """List query execution history."""
        entries = []
        for e in self._query_executions:
            if connection_id and e.connection_id != connection_id:
                continue
            if source_type and e.source_type != source_type:
                continue
            if user_id and e.user_id != user_id:
                continue

            entries.append(QueryHistoryEntry(
                id=e.id,
                query_hash=e.query_hash,
                sql=e.sql,
                connection_id=e.connection_id,
                source_type=e.source_type,
                source_id=e.source_id,
                user_id=e.user_id,
                execution_time_ms=e.execution_time_ms,
                rows_returned=e.rows_returned,
                status=e.status,
                executed_at=e.executed_at,
            ))

        entries = sorted(entries, key=lambda e: e.executed_at, reverse=True)[:limit]

        return QueryHistoryListResponse(entries=entries, total=len(entries))

    async def get_history_stats(
        self,
        connection_id: Optional[str] = None,
        hours: int = 24,
    ) -> QueryHistoryStats:
        """Get query history statistics."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        executions = [
            e for e in self._query_executions
            if e.executed_at >= cutoff and (not connection_id or e.connection_id == connection_id)
        ]

        unique_hashes = set(e.query_hash for e in executions)
        slow_count = sum(1 for e in executions if e.execution_time_ms >= self._config.slow_query_threshold_ms)
        error_count = sum(1 for e in executions if e.status == "error")
        cache_hits = sum(1 for e in executions if e.cache_hit)

        # By source
        by_source = defaultdict(int)
        for e in executions:
            by_source[e.source_type.value] += 1

        # By hour
        by_hour = []
        for i in range(hours):
            hour_start = cutoff + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)
            hour_execs = [e for e in executions if hour_start <= e.executed_at < hour_end]
            by_hour.append({
                "hour": hour_start.isoformat(),
                "count": len(hour_execs),
                "avg_time_ms": sum(e.execution_time_ms for e in hour_execs) / max(1, len(hour_execs)),
            })

        return QueryHistoryStats(
            total_queries=len(executions),
            unique_queries=len(unique_hashes),
            total_execution_time_ms=sum(e.execution_time_ms for e in executions),
            avg_execution_time_ms=sum(e.execution_time_ms for e in executions) / max(1, len(executions)),
            slow_query_count=slow_count,
            error_count=error_count,
            cache_hit_rate=cache_hits / max(1, len(executions)),
            by_source=dict(by_source),
            by_hour=by_hour,
            top_slow_queries=(await self.list_slow_queries(connection_id=connection_id, limit=10)).queries,
        )

    # ==================== CONFIGURATION ====================

    async def get_config(self) -> OptimizationConfig:
        """Get optimization configuration."""
        return self._config

    async def update_config(self, update: OptimizationConfigUpdate) -> OptimizationConfig:
        """Update optimization configuration."""
        for field, value in update.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(self._config, field, value)
        return self._config


# Singleton instance
query_optimization_service = QueryOptimizationService()
