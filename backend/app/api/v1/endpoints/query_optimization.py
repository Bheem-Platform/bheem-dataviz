"""
Query Optimization API Endpoints

Endpoints for query plan analysis, cost estimation, optimization suggestions,
and performance monitoring.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.schemas.query_optimization import (
    QueryPlanRequest,
    QueryPlan,
    QueryPlanComparison,
    QueryPlanListResponse,
    CostEstimateRequest,
    CostEstimate,
    ResourceUsageEstimate,
    QuerySuggestion,
    QuerySuggestionListResponse,
    IndexSuggestion,
    IndexSuggestionListResponse,
    QueryRewrite,
    OptimizationResult,
    QueryExecution,
    QueryPerformanceStats,
    SlowQuery,
    SlowQueryListResponse,
    QueryHistoryEntry,
    QueryHistoryListResponse,
    QueryHistoryStats,
    OptimizationConfig,
    OptimizationConfigUpdate,
    QuerySourceType,
    OptimizationStatus,
)
from app.services.query_optimization_service import query_optimization_service

router = APIRouter()


# Query Plan Endpoints

@router.post("/plans/analyze", response_model=QueryPlan)
async def analyze_query_plan(request: QueryPlanRequest):
    """Analyze query execution plan."""
    try:
        plan = await query_optimization_service.analyze_query_plan(
            sql=request.sql,
            connection_id=request.connection_id,
            explain_analyze=request.explain_analyze,
            explain_buffers=request.explain_buffers,
            explain_verbose=request.explain_verbose,
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}", response_model=QueryPlan)
async def get_query_plan(plan_id: str):
    """Get a specific query plan."""
    plan = await query_optimization_service.get_query_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Query plan not found")
    return plan


@router.get("/plans", response_model=QueryPlanListResponse)
async def list_query_plans(
    connection_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List query plans."""
    plans = await query_optimization_service.list_query_plans(
        connection_id=connection_id,
        limit=limit,
        offset=offset,
    )
    return plans


@router.post("/plans/compare", response_model=QueryPlanComparison)
async def compare_query_plans(
    original_sql: str,
    optimized_sql: str,
    connection_id: str,
):
    """Compare two query plans."""
    try:
        comparison = await query_optimization_service.compare_query_plans(
            original_sql=original_sql,
            optimized_sql=optimized_sql,
            connection_id=connection_id,
        )
        return comparison
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/plans/{plan_id}")
async def delete_query_plan(plan_id: str):
    """Delete a query plan."""
    deleted = await query_optimization_service.delete_query_plan(plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Query plan not found")
    return {"message": "Query plan deleted"}


# Cost Estimation Endpoints

@router.post("/cost/estimate", response_model=CostEstimate)
async def estimate_query_cost(request: CostEstimateRequest):
    """Estimate query cost."""
    try:
        estimate = await query_optimization_service.estimate_query_cost(
            sql=request.sql,
            connection_id=request.connection_id,
            include_components=request.include_components,
        )
        return estimate
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cost/resources", response_model=ResourceUsageEstimate)
async def estimate_resource_usage(request: CostEstimateRequest):
    """Estimate resource usage for a query."""
    try:
        estimate = await query_optimization_service.estimate_resource_usage(
            sql=request.sql,
            connection_id=request.connection_id,
        )
        return estimate
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Optimization Suggestions Endpoints

@router.post("/optimize", response_model=OptimizationResult)
async def optimize_query(
    sql: str,
    connection_id: str,
    auto_apply: bool = False,
):
    """Analyze and optimize a query."""
    try:
        result = await query_optimization_service.optimize_query(
            sql=sql,
            connection_id=connection_id,
            auto_apply=auto_apply,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/suggestions/{query_hash}", response_model=QuerySuggestionListResponse)
async def get_query_suggestions(query_hash: str):
    """Get optimization suggestions for a query."""
    suggestions = await query_optimization_service.get_suggestions(query_hash)
    return suggestions


@router.post("/suggestions/{suggestion_id}/apply")
async def apply_suggestion(suggestion_id: str, query_hash: str):
    """Apply an optimization suggestion."""
    try:
        result = await query_optimization_service.apply_suggestion(
            suggestion_id=suggestion_id,
            query_hash=query_hash,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/suggestions/{suggestion_id}/dismiss")
async def dismiss_suggestion(suggestion_id: str, query_hash: str):
    """Dismiss an optimization suggestion."""
    dismissed = await query_optimization_service.dismiss_suggestion(
        suggestion_id=suggestion_id,
        query_hash=query_hash,
    )
    if not dismissed:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return {"message": "Suggestion dismissed"}


# Index Suggestions Endpoints

@router.get("/indexes/suggestions", response_model=IndexSuggestionListResponse)
async def get_index_suggestions(
    connection_id: Optional[str] = None,
    table_name: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """Get index creation suggestions."""
    suggestions = await query_optimization_service.get_index_suggestions(
        connection_id=connection_id,
        table_name=table_name,
        limit=limit,
    )
    return suggestions


@router.post("/indexes/analyze")
async def analyze_missing_indexes(connection_id: str):
    """Analyze and suggest missing indexes for a connection."""
    try:
        suggestions = await query_optimization_service.analyze_missing_indexes(
            connection_id=connection_id,
        )
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Query Rewrite Endpoints

@router.post("/rewrite", response_model=QueryRewrite)
async def rewrite_query(
    sql: str,
    connection_id: str,
):
    """Get query rewrite suggestions."""
    try:
        rewrite = await query_optimization_service.suggest_query_rewrite(
            sql=sql,
            connection_id=connection_id,
        )
        return rewrite
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Query Execution Tracking Endpoints

@router.post("/executions", response_model=QueryExecution)
async def record_query_execution(
    sql: str,
    connection_id: str,
    execution_time_ms: float,
    rows_returned: int,
    rows_scanned: int = 0,
    bytes_processed: int = 0,
    source_type: QuerySourceType = QuerySourceType.API,
    source_id: Optional[str] = None,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    cached: bool = False,
    cache_hit: bool = False,
    status: str = "success",
    error_message: Optional[str] = None,
):
    """Record a query execution."""
    execution = await query_optimization_service.record_query_execution(
        sql=sql,
        connection_id=connection_id,
        execution_time_ms=execution_time_ms,
        rows_returned=rows_returned,
        rows_scanned=rows_scanned,
        bytes_processed=bytes_processed,
        source_type=source_type,
        source_id=source_id,
        user_id=user_id,
        workspace_id=workspace_id,
        cached=cached,
        cache_hit=cache_hit,
        status=status,
        error_message=error_message,
    )
    return execution


@router.get("/executions/{query_hash}/stats", response_model=QueryPerformanceStats)
async def get_query_performance_stats(query_hash: str):
    """Get performance statistics for a query."""
    stats = await query_optimization_service.get_query_performance_stats(query_hash)
    if not stats:
        raise HTTPException(status_code=404, detail="No statistics found for query")
    return stats


# Slow Query Endpoints

@router.get("/slow-queries", response_model=SlowQueryListResponse)
async def list_slow_queries(
    connection_id: Optional[str] = None,
    source_type: Optional[QuerySourceType] = None,
    status: Optional[OptimizationStatus] = None,
    min_execution_time_ms: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List slow queries."""
    queries = await query_optimization_service.list_slow_queries(
        connection_id=connection_id,
        source_type=source_type,
        status=status,
        min_execution_time_ms=min_execution_time_ms,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return queries


@router.get("/slow-queries/{query_id}", response_model=SlowQuery)
async def get_slow_query(query_id: str):
    """Get details of a slow query."""
    query = await query_optimization_service.get_slow_query(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Slow query not found")
    return query


@router.post("/slow-queries/{query_id}/optimize")
async def optimize_slow_query(query_id: str):
    """Analyze and optimize a slow query."""
    try:
        result = await query_optimization_service.optimize_slow_query(query_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/slow-queries/{query_id}/status")
async def update_slow_query_status(
    query_id: str,
    status: OptimizationStatus,
):
    """Update optimization status of a slow query."""
    updated = await query_optimization_service.update_slow_query_status(
        query_id=query_id,
        status=status,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Slow query not found")
    return {"message": "Status updated"}


# Query History Endpoints

@router.get("/history", response_model=QueryHistoryListResponse)
async def get_query_history(
    connection_id: Optional[str] = None,
    source_type: Optional[QuerySourceType] = None,
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Get query execution history."""
    history = await query_optimization_service.get_query_history(
        connection_id=connection_id,
        source_type=source_type,
        user_id=user_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        search=search,
        limit=limit,
        offset=offset,
    )
    return history


@router.get("/history/stats", response_model=QueryHistoryStats)
async def get_query_history_stats(
    connection_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """Get query history statistics."""
    stats = await query_optimization_service.get_query_history_stats(
        connection_id=connection_id,
        start_date=start_date,
        end_date=end_date,
    )
    return stats


@router.delete("/history/{entry_id}")
async def delete_history_entry(entry_id: str):
    """Delete a query history entry."""
    deleted = await query_optimization_service.delete_history_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History entry not found")
    return {"message": "History entry deleted"}


@router.delete("/history")
async def clear_query_history(
    connection_id: Optional[str] = None,
    before_date: Optional[datetime] = None,
):
    """Clear query history."""
    count = await query_optimization_service.clear_query_history(
        connection_id=connection_id,
        before_date=before_date,
    )
    return {"message": f"Cleared {count} history entries"}


# Configuration Endpoints

@router.get("/config", response_model=OptimizationConfig)
async def get_optimization_config():
    """Get query optimization configuration."""
    return await query_optimization_service.get_config()


@router.put("/config", response_model=OptimizationConfig)
async def update_optimization_config(update: OptimizationConfigUpdate):
    """Update query optimization configuration."""
    config = await query_optimization_service.update_config(update)
    return config


# Dashboard Endpoints

@router.get("/dashboard/summary")
async def get_optimization_dashboard():
    """Get optimization dashboard summary."""
    summary = await query_optimization_service.get_dashboard_summary()
    return summary


@router.get("/dashboard/trends")
async def get_performance_trends(
    connection_id: Optional[str] = None,
    days: int = Query(7, ge=1, le=90),
):
    """Get query performance trends."""
    trends = await query_optimization_service.get_performance_trends(
        connection_id=connection_id,
        days=days,
    )
    return trends
