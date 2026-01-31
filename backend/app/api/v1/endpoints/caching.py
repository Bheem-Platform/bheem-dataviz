"""
Caching API Endpoints

REST API for cache management, TTL policies, cache warming,
and invalidation strategies.
"""

from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.caching_service import CachingService
from app.schemas.caching import (
    CacheType,
    CacheEventType,
    CacheEntryInfo,
    TTLPolicy,
    TTLPolicyCreate,
    TTLPolicyUpdate,
    TTLPolicyListResponse,
    CacheWarmingTask,
    CacheWarmingTaskCreate,
    CacheWarmingTaskListResponse,
    CacheWarmingResult,
    InvalidationRule,
    InvalidationRuleCreate,
    InvalidationRuleListResponse,
    InvalidationRequest,
    InvalidationResult,
    InvalidationEventListResponse,
    CacheKeyListResponse,
    CacheStats,
    CacheHealthStatus,
)

router = APIRouter()


# ==================== CACHE OPERATIONS ====================

@router.get("/keys", response_model=CacheKeyListResponse)
async def list_cache_keys(
    cache_type: Optional[CacheType] = Query(None),
    pattern: str = Query("*"),
    workspace_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    cursor: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List cache keys with optional filters."""
    service = CachingService(db)
    return await service.list_keys(cache_type, pattern, workspace_id, limit, cursor)


@router.get("/keys/{key}", response_model=CacheEntryInfo)
async def get_cache_entry_info(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """Get info about a cache entry."""
    service = CachingService(db)
    info = await service.get_entry_info(key)

    if not info:
        raise HTTPException(status_code=404, detail="Cache entry not found")

    return info


@router.delete("/keys/{key}")
async def delete_cache_entry(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a cache entry."""
    service = CachingService(db)
    success = await service.delete(key)

    if not success:
        raise HTTPException(status_code=404, detail="Cache entry not found")

    return {"deleted": True}


@router.post("/set")
async def set_cache_entry(
    cache_type: CacheType = Query(...),
    identifier: str = Query(...),
    data: Any = Body(...),
    workspace_id: Optional[str] = Query(None),
    ttl_seconds: Optional[int] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    db: AsyncSession = Depends(get_db),
):
    """Set a cache entry."""
    service = CachingService(db)

    tag_list = tags.split(",") if tags else []

    key = await service.set(
        cache_type=cache_type,
        identifier=identifier,
        data=data,
        workspace_id=workspace_id,
        ttl_seconds=ttl_seconds,
        tags=tag_list,
    )

    return {"key": key, "success": True}


@router.get("/get")
async def get_cache_entry(
    cache_type: CacheType = Query(...),
    identifier: str = Query(...),
    workspace_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get a cache entry value."""
    service = CachingService(db)

    data = await service.get(
        cache_type=cache_type,
        identifier=identifier,
        workspace_id=workspace_id,
    )

    if data is None:
        raise HTTPException(status_code=404, detail="Cache entry not found or expired")

    return {"data": data, "found": True}


@router.get("/exists")
async def check_cache_exists(
    cache_type: CacheType = Query(...),
    identifier: str = Query(...),
    workspace_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Check if a cache entry exists."""
    service = CachingService(db)

    exists = await service.exists(
        cache_type=cache_type,
        identifier=identifier,
        workspace_id=workspace_id,
    )

    return {"exists": exists}


# ==================== TTL POLICIES ====================

@router.get("/policies", response_model=TTLPolicyListResponse)
async def list_ttl_policies(
    cache_type: Optional[CacheType] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List TTL policies."""
    service = CachingService(db)
    return await service.list_ttl_policies(cache_type)


@router.post("/policies", response_model=TTLPolicy)
async def create_ttl_policy(
    data: TTLPolicyCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a TTL policy."""
    service = CachingService(db)
    return await service.create_ttl_policy(data)


@router.get("/policies/{policy_id}", response_model=TTLPolicy)
async def get_ttl_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a TTL policy."""
    service = CachingService(db)
    policy = await service.get_ttl_policy(policy_id)

    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    return policy


@router.patch("/policies/{policy_id}", response_model=TTLPolicy)
async def update_ttl_policy(
    policy_id: str,
    data: TTLPolicyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a TTL policy."""
    service = CachingService(db)
    policy = await service.update_ttl_policy(policy_id, data)

    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    return policy


@router.delete("/policies/{policy_id}")
async def delete_ttl_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a TTL policy."""
    service = CachingService(db)
    success = await service.delete_ttl_policy(policy_id)

    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")

    return {"deleted": True}


# ==================== CACHE WARMING ====================

@router.get("/warming", response_model=CacheWarmingTaskListResponse)
async def list_warming_tasks(
    db: AsyncSession = Depends(get_db),
):
    """List cache warming tasks."""
    service = CachingService(db)
    return await service.list_warming_tasks()


@router.post("/warming", response_model=CacheWarmingTask)
async def create_warming_task(
    data: CacheWarmingTaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a cache warming task."""
    service = CachingService(db)
    return await service.create_warming_task(data)


@router.get("/warming/{task_id}", response_model=CacheWarmingTask)
async def get_warming_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a cache warming task."""
    service = CachingService(db)
    task = await service.get_warming_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.delete("/warming/{task_id}")
async def delete_warming_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a cache warming task."""
    service = CachingService(db)
    success = await service.delete_warming_task(task_id)

    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"deleted": True}


@router.post("/warming/{task_id}/execute", response_model=CacheWarmingResult)
async def execute_warming_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Execute a cache warming task."""
    service = CachingService(db)
    try:
        return await service.execute_warming_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/warm-all")
async def warm_all_tasks(
    db: AsyncSession = Depends(get_db),
):
    """Execute all enabled cache warming tasks."""
    service = CachingService(db)
    tasks = await service.list_warming_tasks()

    results = []
    for task in tasks.tasks:
        if task.enabled:
            result = await service.execute_warming_task(task.id)
            results.append({
                "task_id": task.id,
                "keys_warmed": result.keys_warmed,
                "duration_ms": result.duration_ms,
            })

    return {"tasks_executed": len(results), "results": results}


# ==================== INVALIDATION ====================

@router.get("/invalidation/rules", response_model=InvalidationRuleListResponse)
async def list_invalidation_rules(
    db: AsyncSession = Depends(get_db),
):
    """List invalidation rules."""
    service = CachingService(db)
    return await service.list_invalidation_rules()


@router.post("/invalidation/rules", response_model=InvalidationRule)
async def create_invalidation_rule(
    data: InvalidationRuleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create an invalidation rule."""
    service = CachingService(db)
    return await service.create_invalidation_rule(data)


@router.get("/invalidation/rules/{rule_id}", response_model=InvalidationRule)
async def get_invalidation_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get an invalidation rule."""
    service = CachingService(db)
    rule = await service.get_invalidation_rule(rule_id)

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return rule


@router.delete("/invalidation/rules/{rule_id}")
async def delete_invalidation_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete an invalidation rule."""
    service = CachingService(db)
    success = await service.delete_invalidation_rule(rule_id)

    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")

    return {"deleted": True}


@router.post("/invalidate", response_model=InvalidationResult)
async def invalidate_cache(
    request: InvalidationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Invalidate cache entries."""
    service = CachingService(db)
    return await service.invalidate(request)


@router.post("/invalidate/by-type/{cache_type}", response_model=InvalidationResult)
async def invalidate_by_type(
    cache_type: CacheType,
    workspace_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Invalidate all cache entries of a specific type."""
    service = CachingService(db)
    request = InvalidationRequest(
        cache_type=cache_type,
        workspace_id=workspace_id,
        reason=f"Bulk invalidation for {cache_type.value}",
    )
    return await service.invalidate(request)


@router.post("/invalidate/event", response_model=InvalidationResult)
async def trigger_invalidation_event(
    event_type: CacheEventType = Query(...),
    source: str = Query("api"),
    db: AsyncSession = Depends(get_db),
):
    """Trigger cache invalidation based on event."""
    service = CachingService(db)
    return await service.trigger_invalidation_event(event_type, source)


@router.get("/invalidation/events", response_model=InvalidationEventListResponse)
async def list_invalidation_events(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List recent invalidation events."""
    service = CachingService(db)
    return await service.list_invalidation_events(limit)


# ==================== STATISTICS & HEALTH ====================

@router.get("/stats", response_model=CacheStats)
async def get_cache_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get cache statistics."""
    service = CachingService(db)
    return await service.get_stats()


@router.get("/health", response_model=CacheHealthStatus)
async def get_cache_health(
    db: AsyncSession = Depends(get_db),
):
    """Get cache health status."""
    service = CachingService(db)
    return await service.get_health()


# ==================== MANAGEMENT ====================

@router.post("/clear")
async def clear_all_cache(
    confirm: bool = Query(False, description="Confirm clearing all cache"),
    db: AsyncSession = Depends(get_db),
):
    """Clear all cache entries."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must confirm=true to clear all cache",
        )

    service = CachingService(db)
    count = await service.clear_all()

    return {"cleared": True, "entries_removed": count}


@router.post("/clear/{cache_type}")
async def clear_cache_type(
    cache_type: CacheType,
    db: AsyncSession = Depends(get_db),
):
    """Clear all cache entries of a specific type."""
    service = CachingService(db)
    count = await service.clear_type(cache_type)

    return {"cleared": True, "cache_type": cache_type.value, "entries_removed": count}


@router.get("/types")
async def get_cache_types():
    """Get available cache types."""
    return {
        "types": [
            {"value": t.value, "label": t.value.replace("_", " ").title()}
            for t in CacheType
        ]
    }


@router.get("/defaults")
async def get_cache_defaults():
    """Get default cache configuration."""
    from app.schemas.caching import DEFAULT_TTL_BY_TYPE, COMPRESSION_THRESHOLD_BYTES, MAX_CACHE_ENTRY_SIZE_BYTES

    return {
        "default_ttl_by_type": {k.value: v for k, v in DEFAULT_TTL_BY_TYPE.items()},
        "compression_threshold_bytes": COMPRESSION_THRESHOLD_BYTES,
        "max_entry_size_bytes": MAX_CACHE_ENTRY_SIZE_BYTES,
    }
