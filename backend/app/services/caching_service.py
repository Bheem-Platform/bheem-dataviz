"""
Caching Service

Business logic for cache management, TTL policies, cache warming,
and invalidation strategies.
"""

import uuid
import json
import gzip
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any

from app.schemas.caching import (
    CacheType,
    CacheStatus,
    InvalidationStrategy,
    CacheEventType,
    CompressionType,
    CacheKey,
    CacheKeyPattern,
    CacheEntry,
    CacheEntryInfo,
    CacheSet,
    CacheGet,
    TTLPolicy,
    TTLPolicyCreate,
    TTLPolicyUpdate,
    CacheWarmingTask,
    CacheWarmingTaskCreate,
    CacheWarmingResult,
    InvalidationRule,
    InvalidationRuleCreate,
    InvalidationRequest,
    InvalidationResult,
    InvalidationEvent,
    CacheTypeStats,
    CacheStats,
    CacheHealthStatus,
    TTLPolicyListResponse,
    CacheWarmingTaskListResponse,
    InvalidationRuleListResponse,
    CacheKeyListResponse,
    InvalidationEventListResponse,
    DEFAULT_TTL_BY_TYPE,
    COMPRESSION_THRESHOLD_BYTES,
    MAX_CACHE_ENTRY_SIZE_BYTES,
    generate_cache_key,
    calculate_ttl,
    estimate_cache_size,
)


class CachingService:
    """Service for cache management."""

    def __init__(self, db=None):
        self.db = db
        # In-memory cache store (production would use Redis)
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_metadata: dict[str, CacheEntry] = {}
        self._ttl_policies: dict[str, TTLPolicy] = {}
        self._warming_tasks: dict[str, CacheWarmingTask] = {}
        self._invalidation_rules: dict[str, InvalidationRule] = {}
        self._invalidation_events: list[InvalidationEvent] = []
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "by_type": {t: {"hits": 0, "misses": 0} for t in CacheType},
        }
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Initialize default TTL policies and invalidation rules."""
        # Default TTL policies
        for cache_type, ttl in DEFAULT_TTL_BY_TYPE.items():
            policy = TTLPolicy(
                id=f"default_{cache_type.value}",
                name=f"Default {cache_type.value.replace('_', ' ').title()}",
                description=f"Default TTL policy for {cache_type.value}",
                cache_type=cache_type,
                default_ttl_seconds=ttl,
                max_ttl_seconds=ttl * 4,
                min_ttl_seconds=max(60, ttl // 10),
            )
            self._ttl_policies[policy.id] = policy

        # Default invalidation rules
        rules = [
            InvalidationRule(
                id="rule_data_update",
                name="Data Update Invalidation",
                description="Invalidate caches when data is updated",
                event_type=CacheEventType.DATA_UPDATED,
                target_cache_types=[CacheType.QUERY_RESULT, CacheType.CHART_DATA, CacheType.KPI_VALUE],
                key_patterns=["*"],
                cascade=True,
                enabled=True,
            ),
            InvalidationRule(
                id="rule_schema_change",
                name="Schema Change Invalidation",
                description="Invalidate schema caches when schema changes",
                event_type=CacheEventType.SCHEMA_CHANGED,
                target_cache_types=[CacheType.CONNECTION_SCHEMA, CacheType.TABLE_METADATA],
                key_patterns=["*"],
                cascade=True,
                enabled=True,
            ),
            InvalidationRule(
                id="rule_connection_modified",
                name="Connection Modified Invalidation",
                description="Invalidate all connection-related caches",
                event_type=CacheEventType.CONNECTION_MODIFIED,
                target_cache_types=[
                    CacheType.QUERY_RESULT,
                    CacheType.CONNECTION_SCHEMA,
                    CacheType.TABLE_METADATA,
                    CacheType.FILTER_OPTIONS,
                ],
                key_patterns=["*"],
                cascade=True,
                enabled=True,
            ),
        ]
        for rule in rules:
            self._invalidation_rules[rule.id] = rule

        # Sample cache warming task
        warming_task = CacheWarmingTask(
            id="warm_popular_dashboards",
            name="Warm Popular Dashboards",
            description="Pre-cache data for frequently accessed dashboards",
            cache_type=CacheType.DASHBOARD_DATA,
            target_keys=[
                {"dashboard_id": "dashboard_001"},
                {"dashboard_id": "dashboard_002"},
            ],
            schedule="0 */4 * * *",  # Every 4 hours
            priority=8,
            enabled=True,
        )
        self._warming_tasks[warming_task.id] = warming_task

    # ==================== CORE CACHE OPERATIONS ====================

    async def get(
        self,
        cache_type: CacheType,
        identifier: str,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> Optional[Any]:
        """Get value from cache."""
        key = generate_cache_key(cache_type, identifier, workspace_id, user_id, params)

        entry = self._cache_metadata.get(key)
        if not entry:
            self._stats["misses"] += 1
            self._stats["by_type"][cache_type]["misses"] += 1
            return None

        # Check if expired
        if entry.expires_at and entry.expires_at < datetime.utcnow():
            await self._remove_entry(key)
            self._stats["misses"] += 1
            self._stats["by_type"][cache_type]["misses"] += 1
            return None

        # Update access stats
        entry.accessed_at = datetime.utcnow()
        entry.access_count += 1

        self._stats["hits"] += 1
        self._stats["by_type"][cache_type]["hits"] += 1

        # Decompress if needed
        data = self._cache.get(key)
        if entry.compression == CompressionType.GZIP and data:
            data = self._decompress_gzip(data)

        return data

    async def set(
        self,
        cache_type: CacheType,
        identifier: str,
        data: Any,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        params: Optional[dict] = None,
        ttl_seconds: Optional[int] = None,
        compression: CompressionType = CompressionType.GZIP,
        tags: list[str] = None,
        metadata: dict[str, Any] = None,
    ) -> str:
        """Set value in cache."""
        key = generate_cache_key(cache_type, identifier, workspace_id, user_id, params)

        # Get TTL from policy if not specified
        if ttl_seconds is None:
            policy = self._get_policy_for_type(cache_type)
            ttl_seconds = policy.default_ttl_seconds if policy else DEFAULT_TTL_BY_TYPE.get(cache_type, 3600)

        # Calculate size and compress if needed
        data_to_store = data
        actual_compression = CompressionType.NONE
        size_bytes = estimate_cache_size(data)

        if compression != CompressionType.NONE and size_bytes > COMPRESSION_THRESHOLD_BYTES:
            if compression == CompressionType.GZIP:
                data_to_store = self._compress_gzip(data)
                actual_compression = CompressionType.GZIP
                size_bytes = len(data_to_store)

        # Check size limit
        if size_bytes > MAX_CACHE_ENTRY_SIZE_BYTES:
            raise ValueError(f"Cache entry too large: {size_bytes} bytes")

        # Create entry
        now = datetime.utcnow()
        entry = CacheEntry(
            key=key,
            type=cache_type,
            data=None,  # Data stored separately
            size_bytes=size_bytes,
            compression=actual_compression,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
            accessed_at=now,
            access_count=0,
            ttl_seconds=ttl_seconds,
            status=CacheStatus.VALID,
            metadata=metadata or {},
        )

        if tags:
            entry.metadata["tags"] = tags

        self._cache[key] = data_to_store
        self._cache_metadata[key] = entry

        return key

    async def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        return await self._remove_entry(key)

    async def exists(
        self,
        cache_type: CacheType,
        identifier: str,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> bool:
        """Check if key exists in cache."""
        key = generate_cache_key(cache_type, identifier, workspace_id, user_id, params)
        entry = self._cache_metadata.get(key)

        if not entry:
            return False

        # Check if expired
        if entry.expires_at and entry.expires_at < datetime.utcnow():
            await self._remove_entry(key)
            return False

        return True

    async def get_or_set(
        self,
        cache_type: CacheType,
        identifier: str,
        factory_fn,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        params: Optional[dict] = None,
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """Get from cache or compute and set."""
        cached = await self.get(cache_type, identifier, workspace_id, user_id, params)
        if cached is not None:
            return cached

        # Compute value
        data = await factory_fn() if callable(factory_fn) else factory_fn

        # Store in cache
        await self.set(
            cache_type, identifier, data,
            workspace_id=workspace_id,
            user_id=user_id,
            params=params,
            ttl_seconds=ttl_seconds,
        )

        return data

    async def _remove_entry(self, key: str) -> bool:
        """Remove a cache entry."""
        if key in self._cache:
            del self._cache[key]
        if key in self._cache_metadata:
            del self._cache_metadata[key]
            return True
        return False

    def _compress_gzip(self, data: Any) -> bytes:
        """Compress data using gzip."""
        json_str = json.dumps(data)
        return gzip.compress(json_str.encode('utf-8'))

    def _decompress_gzip(self, data: bytes) -> Any:
        """Decompress gzip data."""
        if isinstance(data, bytes):
            json_str = gzip.decompress(data).decode('utf-8')
            return json.loads(json_str)
        return data

    def _get_policy_for_type(self, cache_type: CacheType) -> Optional[TTLPolicy]:
        """Get TTL policy for cache type."""
        policy_id = f"default_{cache_type.value}"
        return self._ttl_policies.get(policy_id)

    # ==================== CACHE LISTING & INFO ====================

    async def list_keys(
        self,
        cache_type: Optional[CacheType] = None,
        pattern: str = "*",
        workspace_id: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
    ) -> CacheKeyListResponse:
        """List cache keys matching criteria."""
        keys = []
        now = datetime.utcnow()

        for key, entry in self._cache_metadata.items():
            # Filter by type
            if cache_type and entry.type != cache_type:
                continue

            # Filter by workspace
            if workspace_id and workspace_id not in key:
                continue

            # Filter by pattern (simplified)
            if pattern != "*" and pattern not in key:
                continue

            # Calculate TTL remaining
            ttl_remaining = 0
            if entry.expires_at:
                ttl_remaining = max(0, int((entry.expires_at - now).total_seconds()))

            keys.append(CacheEntryInfo(
                key=key,
                type=entry.type,
                size_bytes=entry.size_bytes,
                compression=entry.compression,
                created_at=entry.created_at,
                expires_at=entry.expires_at,
                accessed_at=entry.accessed_at,
                access_count=entry.access_count,
                ttl_remaining=ttl_remaining,
                status=entry.status,
            ))

        # Sort by access time (most recent first)
        keys.sort(key=lambda k: k.accessed_at, reverse=True)

        return CacheKeyListResponse(
            keys=keys[:limit],
            total=len(keys),
            cursor=None,  # Simplified - no pagination cursor
        )

    async def get_entry_info(self, key: str) -> Optional[CacheEntryInfo]:
        """Get info about a cache entry."""
        entry = self._cache_metadata.get(key)
        if not entry:
            return None

        now = datetime.utcnow()
        ttl_remaining = 0
        if entry.expires_at:
            ttl_remaining = max(0, int((entry.expires_at - now).total_seconds()))

        return CacheEntryInfo(
            key=key,
            type=entry.type,
            size_bytes=entry.size_bytes,
            compression=entry.compression,
            created_at=entry.created_at,
            expires_at=entry.expires_at,
            accessed_at=entry.accessed_at,
            access_count=entry.access_count,
            ttl_remaining=ttl_remaining,
            status=entry.status,
        )

    # ==================== TTL POLICIES ====================

    async def list_ttl_policies(
        self, cache_type: Optional[CacheType] = None
    ) -> TTLPolicyListResponse:
        """List TTL policies."""
        policies = list(self._ttl_policies.values())

        if cache_type:
            policies = [p for p in policies if p.cache_type == cache_type]

        return TTLPolicyListResponse(policies=policies, total=len(policies))

    async def create_ttl_policy(self, data: TTLPolicyCreate) -> TTLPolicy:
        """Create a TTL policy."""
        policy_id = f"policy_{uuid.uuid4().hex[:12]}"

        policy = TTLPolicy(
            id=policy_id,
            name=data.name,
            description=data.description,
            cache_type=data.cache_type,
            default_ttl_seconds=data.default_ttl_seconds,
            max_ttl_seconds=data.max_ttl_seconds,
            min_ttl_seconds=data.min_ttl_seconds,
            stale_while_revalidate_seconds=data.stale_while_revalidate_seconds,
            adaptive_ttl=data.adaptive_ttl,
        )

        self._ttl_policies[policy_id] = policy
        return policy

    async def get_ttl_policy(self, policy_id: str) -> Optional[TTLPolicy]:
        """Get a TTL policy."""
        return self._ttl_policies.get(policy_id)

    async def update_ttl_policy(
        self, policy_id: str, data: TTLPolicyUpdate
    ) -> Optional[TTLPolicy]:
        """Update a TTL policy."""
        policy = self._ttl_policies.get(policy_id)
        if not policy:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(policy, field, value)

        policy.updated_at = datetime.utcnow()
        return policy

    async def delete_ttl_policy(self, policy_id: str) -> bool:
        """Delete a TTL policy."""
        if policy_id in self._ttl_policies:
            del self._ttl_policies[policy_id]
            return True
        return False

    # ==================== CACHE WARMING ====================

    async def list_warming_tasks(self) -> CacheWarmingTaskListResponse:
        """List cache warming tasks."""
        tasks = list(self._warming_tasks.values())
        return CacheWarmingTaskListResponse(tasks=tasks, total=len(tasks))

    async def create_warming_task(self, data: CacheWarmingTaskCreate) -> CacheWarmingTask:
        """Create a cache warming task."""
        task_id = f"warm_{uuid.uuid4().hex[:12]}"

        task = CacheWarmingTask(
            id=task_id,
            name=data.name,
            description=data.description,
            cache_type=data.cache_type,
            target_keys=data.target_keys,
            schedule=data.schedule,
            priority=data.priority,
            enabled=data.enabled,
        )

        self._warming_tasks[task_id] = task
        return task

    async def get_warming_task(self, task_id: str) -> Optional[CacheWarmingTask]:
        """Get a cache warming task."""
        return self._warming_tasks.get(task_id)

    async def delete_warming_task(self, task_id: str) -> bool:
        """Delete a cache warming task."""
        if task_id in self._warming_tasks:
            del self._warming_tasks[task_id]
            return True
        return False

    async def execute_warming_task(self, task_id: str) -> CacheWarmingResult:
        """Execute a cache warming task."""
        task = self._warming_tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")

        started_at = datetime.utcnow()
        keys_warmed = 0
        keys_failed = 0
        errors = []

        for target in task.target_keys:
            try:
                # Simulate warming (in production, fetch actual data)
                identifier = list(target.values())[0] if target else "unknown"
                await self.set(
                    task.cache_type,
                    identifier,
                    {"warmed": True, "timestamp": datetime.utcnow().isoformat()},
                    ttl_seconds=DEFAULT_TTL_BY_TYPE.get(task.cache_type, 3600),
                )
                keys_warmed += 1
            except Exception as e:
                keys_failed += 1
                errors.append({"key": str(target), "error": str(e)})

        completed_at = datetime.utcnow()
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Update task stats
        task.last_run_at = completed_at
        task.last_run_status = "success" if keys_failed == 0 else "partial"
        task.last_run_duration_ms = duration_ms
        task.keys_warmed += keys_warmed

        return CacheWarmingResult(
            task_id=task_id,
            started_at=started_at,
            completed_at=completed_at,
            total_keys=len(task.target_keys),
            keys_warmed=keys_warmed,
            keys_failed=keys_failed,
            duration_ms=duration_ms,
            errors=errors,
        )

    # ==================== INVALIDATION ====================

    async def list_invalidation_rules(self) -> InvalidationRuleListResponse:
        """List invalidation rules."""
        rules = list(self._invalidation_rules.values())
        return InvalidationRuleListResponse(rules=rules, total=len(rules))

    async def create_invalidation_rule(self, data: InvalidationRuleCreate) -> InvalidationRule:
        """Create an invalidation rule."""
        rule_id = f"rule_{uuid.uuid4().hex[:12]}"

        rule = InvalidationRule(
            id=rule_id,
            name=data.name,
            description=data.description,
            event_type=data.event_type,
            target_cache_types=data.target_cache_types,
            key_patterns=data.key_patterns,
            delay_seconds=data.delay_seconds,
            cascade=data.cascade,
        )

        self._invalidation_rules[rule_id] = rule
        return rule

    async def get_invalidation_rule(self, rule_id: str) -> Optional[InvalidationRule]:
        """Get an invalidation rule."""
        return self._invalidation_rules.get(rule_id)

    async def delete_invalidation_rule(self, rule_id: str) -> bool:
        """Delete an invalidation rule."""
        if rule_id in self._invalidation_rules:
            del self._invalidation_rules[rule_id]
            return True
        return False

    async def invalidate(self, request: InvalidationRequest) -> InvalidationResult:
        """Invalidate cache entries."""
        started_at = datetime.utcnow()
        keys_matched = 0
        keys_invalidated = 0
        errors = 0

        keys_to_remove = []

        for key, entry in self._cache_metadata.items():
            # Filter by type
            if request.cache_type and entry.type != request.cache_type:
                continue

            # Filter by workspace
            if request.workspace_id and request.workspace_id not in key:
                continue

            # Filter by pattern (simplified)
            if request.key_pattern != "*" and request.key_pattern not in key:
                continue

            # Filter by tags
            if request.tags:
                entry_tags = entry.metadata.get("tags", [])
                if not any(tag in entry_tags for tag in request.tags):
                    continue

            keys_matched += 1
            keys_to_remove.append(key)

        # Remove matched keys
        for key in keys_to_remove:
            try:
                await self._remove_entry(key)
                keys_invalidated += 1
            except Exception:
                errors += 1

        completed_at = datetime.utcnow()
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Log invalidation event
        event = InvalidationEvent(
            id=f"event_{uuid.uuid4().hex[:12]}",
            event_type=CacheEventType.BULK_INVALIDATION,
            source="manual",
            affected_keys=keys_to_remove[:100],  # Limit stored keys
            metadata={"reason": request.reason, "pattern": request.key_pattern},
        )
        self._invalidation_events.append(event)

        return InvalidationResult(
            keys_matched=keys_matched,
            keys_invalidated=keys_invalidated,
            errors=errors,
            duration_ms=duration_ms,
        )

    async def trigger_invalidation_event(
        self,
        event_type: CacheEventType,
        source: str,
        metadata: dict[str, Any] = None,
    ) -> InvalidationResult:
        """Trigger cache invalidation based on event."""
        total_result = InvalidationResult(
            keys_matched=0,
            keys_invalidated=0,
            errors=0,
            duration_ms=0,
        )

        for rule in self._invalidation_rules.values():
            if not rule.enabled or rule.event_type != event_type:
                continue

            for cache_type in rule.target_cache_types:
                for pattern in rule.key_patterns:
                    request = InvalidationRequest(
                        cache_type=cache_type,
                        key_pattern=pattern,
                    )
                    result = await self.invalidate(request)
                    total_result.keys_matched += result.keys_matched
                    total_result.keys_invalidated += result.keys_invalidated
                    total_result.errors += result.errors
                    total_result.duration_ms += result.duration_ms

        # Log event
        event = InvalidationEvent(
            id=f"event_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            source=source,
            affected_keys=[],
            metadata=metadata or {},
        )
        self._invalidation_events.append(event)

        return total_result

    async def list_invalidation_events(
        self, limit: int = 100
    ) -> InvalidationEventListResponse:
        """List recent invalidation events."""
        events = sorted(
            self._invalidation_events,
            key=lambda e: e.timestamp,
            reverse=True,
        )[:limit]
        return InvalidationEventListResponse(events=events, total=len(events))

    # ==================== STATISTICS & HEALTH ====================

    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        total_entries = len(self._cache_metadata)
        total_size = sum(e.size_bytes for e in self._cache_metadata.values())
        total_hits = self._stats["hits"]
        total_misses = self._stats["misses"]

        hit_rate = 0.0
        if total_hits + total_misses > 0:
            hit_rate = total_hits / (total_hits + total_misses)

        # By type stats
        by_type = []
        for cache_type in CacheType:
            type_entries = [e for e in self._cache_metadata.values() if e.type == cache_type]
            type_size = sum(e.size_bytes for e in type_entries)
            type_hits = self._stats["by_type"][cache_type]["hits"]
            type_misses = self._stats["by_type"][cache_type]["misses"]
            type_hit_rate = 0.0
            if type_hits + type_misses > 0:
                type_hit_rate = type_hits / (type_hits + type_misses)

            now = datetime.utcnow()
            ages = [(now - e.created_at).total_seconds() for e in type_entries]

            by_type.append(CacheTypeStats(
                type=cache_type,
                entry_count=len(type_entries),
                total_size_bytes=type_size,
                hit_count=type_hits,
                miss_count=type_misses,
                hit_rate=type_hit_rate,
                avg_entry_size_bytes=type_size / max(1, len(type_entries)),
                avg_ttl_seconds=sum(e.ttl_seconds for e in type_entries) / max(1, len(type_entries)),
                oldest_entry_age_seconds=int(max(ages)) if ages else 0,
                newest_entry_age_seconds=int(min(ages)) if ages else 0,
            ))

        return CacheStats(
            total_entries=total_entries,
            total_size_bytes=total_size,
            total_hits=total_hits,
            total_misses=total_misses,
            overall_hit_rate=hit_rate,
            memory_used_bytes=total_size,
            memory_limit_bytes=100 * 1024 * 1024,  # 100 MB default
            memory_usage_percent=(total_size / (100 * 1024 * 1024)) * 100,
            evictions=self._stats["evictions"],
            by_type=by_type,
            connected=True,
            uptime_seconds=3600,  # Placeholder
        )

    async def get_health(self) -> CacheHealthStatus:
        """Get cache health status."""
        stats = await self.get_stats()

        warnings = []
        memory_ok = stats.memory_usage_percent < 90
        hit_rate_ok = stats.overall_hit_rate > 0.5 or (stats.total_hits + stats.total_misses) < 100

        if not memory_ok:
            warnings.append(f"High memory usage: {stats.memory_usage_percent:.1f}%")
        if not hit_rate_ok:
            warnings.append(f"Low hit rate: {stats.overall_hit_rate:.1%}")

        return CacheHealthStatus(
            healthy=memory_ok and hit_rate_ok,
            redis_connected=True,  # Simulated
            memory_ok=memory_ok,
            hit_rate_ok=hit_rate_ok,
            latency_ms=0.5,  # Simulated
            warnings=warnings,
        )

    async def clear_all(self) -> int:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        self._cache_metadata.clear()
        self._stats["evictions"] += count
        return count

    async def clear_type(self, cache_type: CacheType) -> int:
        """Clear all entries of a specific type."""
        keys_to_remove = [
            key for key, entry in self._cache_metadata.items()
            if entry.type == cache_type
        ]

        for key in keys_to_remove:
            await self._remove_entry(key)

        self._stats["evictions"] += len(keys_to_remove)
        return len(keys_to_remove)
