"""
Caching Layer Schemas

Pydantic schemas for cache management, TTL policies, cache warming,
and invalidation strategies.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class CacheType(str, Enum):
    """Types of cached data"""
    QUERY_RESULT = "query_result"
    DATASET_PREVIEW = "dataset_preview"
    CHART_DATA = "chart_data"
    DASHBOARD_DATA = "dashboard_data"
    CONNECTION_SCHEMA = "connection_schema"
    TABLE_METADATA = "table_metadata"
    FILTER_OPTIONS = "filter_options"
    KPI_VALUE = "kpi_value"
    TRANSFORM_RESULT = "transform_result"
    API_RESPONSE = "api_response"
    USER_SESSION = "user_session"
    COMPUTED_METRIC = "computed_metric"


class CacheStatus(str, Enum):
    """Cache entry status"""
    VALID = "valid"
    STALE = "stale"
    EXPIRED = "expired"
    WARMING = "warming"
    INVALIDATED = "invalidated"


class InvalidationStrategy(str, Enum):
    """Cache invalidation strategies"""
    TTL = "ttl"  # Time-to-live based
    EVENT = "event"  # Event-based invalidation
    MANUAL = "manual"  # Manual invalidation
    LRU = "lru"  # Least recently used
    LFU = "lfu"  # Least frequently used
    SIZE = "size"  # Size-based eviction


class CacheEventType(str, Enum):
    """Events that can trigger cache invalidation"""
    DATA_UPDATED = "data_updated"
    SCHEMA_CHANGED = "schema_changed"
    CONNECTION_MODIFIED = "connection_modified"
    TRANSFORM_MODIFIED = "transform_modified"
    MODEL_MODIFIED = "model_modified"
    DASHBOARD_MODIFIED = "dashboard_modified"
    CHART_MODIFIED = "chart_modified"
    BULK_INVALIDATION = "bulk_invalidation"


class CompressionType(str, Enum):
    """Compression types for cached data"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"


# Cache Key Models

class CacheKey(BaseModel):
    """Cache key structure"""
    type: CacheType
    identifier: str
    version: str = "v1"
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    params_hash: Optional[str] = None

    def to_string(self) -> str:
        """Convert to Redis key string."""
        parts = [self.type.value, self.identifier]
        if self.workspace_id:
            parts.append(f"ws:{self.workspace_id}")
        if self.user_id:
            parts.append(f"u:{self.user_id}")
        if self.params_hash:
            parts.append(f"p:{self.params_hash}")
        parts.append(self.version)
        return ":".join(parts)


class CacheKeyPattern(BaseModel):
    """Pattern for matching cache keys"""
    type: Optional[CacheType] = None
    identifier_pattern: str = "*"
    workspace_id: Optional[str] = None

    def to_pattern(self) -> str:
        """Convert to Redis pattern."""
        type_part = self.type.value if self.type else "*"
        parts = [type_part, self.identifier_pattern]
        if self.workspace_id:
            parts.append(f"ws:{self.workspace_id}")
        else:
            parts.append("*")
        parts.append("*")  # version wildcard
        return ":".join(parts)


# Cache Entry Models

class CacheEntry(BaseModel):
    """Cached data entry"""
    key: str
    type: CacheType
    data: Any
    size_bytes: int
    compression: CompressionType = CompressionType.NONE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: int
    status: CacheStatus = CacheStatus.VALID
    metadata: dict[str, Any] = Field(default_factory=dict)


class CacheEntryInfo(BaseModel):
    """Cache entry info without data"""
    key: str
    type: CacheType
    size_bytes: int
    compression: CompressionType
    created_at: datetime
    expires_at: Optional[datetime] = None
    accessed_at: datetime
    access_count: int
    ttl_remaining: int
    status: CacheStatus


class CacheSet(BaseModel):
    """Request to set cache entry"""
    key: CacheKey
    data: Any
    ttl_seconds: Optional[int] = None  # Use default if not specified
    compression: CompressionType = CompressionType.GZIP
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CacheGet(BaseModel):
    """Request to get cache entry"""
    key: CacheKey
    update_access_time: bool = True


# TTL Policy Models

class TTLPolicy(BaseModel):
    """TTL policy configuration"""
    id: str
    name: str
    description: Optional[str] = None
    cache_type: CacheType
    default_ttl_seconds: int = 3600
    max_ttl_seconds: int = 86400
    min_ttl_seconds: int = 60
    stale_while_revalidate_seconds: int = 300
    adaptive_ttl: bool = False
    adaptive_config: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class TTLPolicyCreate(BaseModel):
    """Create TTL policy request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    cache_type: CacheType
    default_ttl_seconds: int = Field(3600, ge=60, le=604800)
    max_ttl_seconds: int = Field(86400, ge=60, le=604800)
    min_ttl_seconds: int = Field(60, ge=10, le=3600)
    stale_while_revalidate_seconds: int = Field(300, ge=0, le=3600)
    adaptive_ttl: bool = False


class TTLPolicyUpdate(BaseModel):
    """Update TTL policy request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    default_ttl_seconds: Optional[int] = Field(None, ge=60, le=604800)
    max_ttl_seconds: Optional[int] = Field(None, ge=60, le=604800)
    min_ttl_seconds: Optional[int] = Field(None, ge=10, le=3600)
    stale_while_revalidate_seconds: Optional[int] = Field(None, ge=0, le=3600)
    adaptive_ttl: Optional[bool] = None


# Cache Warming Models

class CacheWarmingTask(BaseModel):
    """Cache warming task"""
    id: str
    name: str
    description: Optional[str] = None
    cache_type: CacheType
    target_keys: list[dict[str, Any]]
    schedule: Optional[str] = None  # Cron expression
    priority: int = 5  # 1-10
    enabled: bool = True
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[str] = None
    last_run_duration_ms: Optional[int] = None
    keys_warmed: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CacheWarmingTaskCreate(BaseModel):
    """Create cache warming task"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    cache_type: CacheType
    target_keys: list[dict[str, Any]]
    schedule: Optional[str] = None
    priority: int = Field(5, ge=1, le=10)
    enabled: bool = True


class CacheWarmingResult(BaseModel):
    """Cache warming execution result"""
    task_id: str
    started_at: datetime
    completed_at: datetime
    total_keys: int
    keys_warmed: int
    keys_failed: int
    duration_ms: int
    errors: list[dict[str, str]]


# Invalidation Models

class InvalidationRule(BaseModel):
    """Cache invalidation rule"""
    id: str
    name: str
    description: Optional[str] = None
    event_type: CacheEventType
    target_cache_types: list[CacheType]
    key_patterns: list[str]
    delay_seconds: int = 0  # Delay before invalidation
    cascade: bool = False  # Invalidate dependent caches
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InvalidationRuleCreate(BaseModel):
    """Create invalidation rule"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    event_type: CacheEventType
    target_cache_types: list[CacheType]
    key_patterns: list[str]
    delay_seconds: int = Field(0, ge=0, le=300)
    cascade: bool = False


class InvalidationRequest(BaseModel):
    """Manual invalidation request"""
    cache_type: Optional[CacheType] = None
    key_pattern: str = "*"
    workspace_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    reason: Optional[str] = None


class InvalidationResult(BaseModel):
    """Invalidation result"""
    keys_matched: int
    keys_invalidated: int
    errors: int
    duration_ms: int


class InvalidationEvent(BaseModel):
    """Cache invalidation event"""
    id: str
    event_type: CacheEventType
    source: str
    affected_keys: list[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


# Cache Statistics Models

class CacheTypeStats(BaseModel):
    """Statistics for a cache type"""
    type: CacheType
    entry_count: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    hit_rate: float
    avg_entry_size_bytes: float
    avg_ttl_seconds: float
    oldest_entry_age_seconds: int
    newest_entry_age_seconds: int


class CacheStats(BaseModel):
    """Overall cache statistics"""
    total_entries: int
    total_size_bytes: int
    total_hits: int
    total_misses: int
    overall_hit_rate: float
    memory_used_bytes: int
    memory_limit_bytes: int
    memory_usage_percent: float
    evictions: int
    by_type: list[CacheTypeStats]
    connected: bool
    uptime_seconds: int


class CacheHealthStatus(BaseModel):
    """Cache health status"""
    healthy: bool
    redis_connected: bool
    memory_ok: bool
    hit_rate_ok: bool
    latency_ms: float
    warnings: list[str]
    last_check: datetime = Field(default_factory=datetime.utcnow)


# Response Models

class TTLPolicyListResponse(BaseModel):
    """List TTL policies response"""
    policies: list[TTLPolicy]
    total: int


class CacheWarmingTaskListResponse(BaseModel):
    """List cache warming tasks response"""
    tasks: list[CacheWarmingTask]
    total: int


class InvalidationRuleListResponse(BaseModel):
    """List invalidation rules response"""
    rules: list[InvalidationRule]
    total: int


class CacheKeyListResponse(BaseModel):
    """List cache keys response"""
    keys: list[CacheEntryInfo]
    total: int
    cursor: Optional[str] = None


class InvalidationEventListResponse(BaseModel):
    """List invalidation events response"""
    events: list[InvalidationEvent]
    total: int


# Constants

DEFAULT_TTL_BY_TYPE: dict[CacheType, int] = {
    CacheType.QUERY_RESULT: 3600,  # 1 hour
    CacheType.DATASET_PREVIEW: 1800,  # 30 minutes
    CacheType.CHART_DATA: 900,  # 15 minutes
    CacheType.DASHBOARD_DATA: 600,  # 10 minutes
    CacheType.CONNECTION_SCHEMA: 7200,  # 2 hours
    CacheType.TABLE_METADATA: 3600,  # 1 hour
    CacheType.FILTER_OPTIONS: 1800,  # 30 minutes
    CacheType.KPI_VALUE: 300,  # 5 minutes
    CacheType.TRANSFORM_RESULT: 3600,  # 1 hour
    CacheType.API_RESPONSE: 300,  # 5 minutes
    CacheType.USER_SESSION: 86400,  # 24 hours
    CacheType.COMPUTED_METRIC: 600,  # 10 minutes
}

COMPRESSION_THRESHOLD_BYTES = 1024  # Compress data larger than 1KB

MAX_CACHE_ENTRY_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


# Helper Functions

def generate_cache_key(
    cache_type: CacheType,
    identifier: str,
    workspace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    params: Optional[dict] = None,
) -> str:
    """Generate a cache key string."""
    import hashlib
    import json

    key = CacheKey(
        type=cache_type,
        identifier=identifier,
        workspace_id=workspace_id,
        user_id=user_id,
    )

    if params:
        params_str = json.dumps(params, sort_keys=True)
        key.params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]

    return key.to_string()


def parse_cache_key(key_string: str) -> CacheKey:
    """Parse a cache key string."""
    parts = key_string.split(":")
    cache_type = CacheType(parts[0])
    identifier = parts[1]
    workspace_id = None
    user_id = None
    params_hash = None
    version = "v1"

    for part in parts[2:]:
        if part.startswith("ws:"):
            workspace_id = part[3:]
        elif part.startswith("u:"):
            user_id = part[2:]
        elif part.startswith("p:"):
            params_hash = part[2:]
        elif part.startswith("v"):
            version = part

    return CacheKey(
        type=cache_type,
        identifier=identifier,
        workspace_id=workspace_id,
        user_id=user_id,
        params_hash=params_hash,
        version=version,
    )


def calculate_ttl(
    cache_type: CacheType,
    data_age_seconds: Optional[int] = None,
    data_volatility: Optional[float] = None,
    custom_policy: Optional[TTLPolicy] = None,
) -> int:
    """Calculate adaptive TTL based on data characteristics."""
    base_ttl = DEFAULT_TTL_BY_TYPE.get(cache_type, 3600)

    if custom_policy:
        base_ttl = custom_policy.default_ttl_seconds

        if custom_policy.adaptive_ttl:
            # Reduce TTL for volatile data
            if data_volatility is not None and data_volatility > 0.5:
                base_ttl = int(base_ttl * (1 - data_volatility * 0.5))

            # Reduce TTL for frequently updated data
            if data_age_seconds is not None and data_age_seconds < 300:
                base_ttl = int(base_ttl * 0.5)

        base_ttl = max(custom_policy.min_ttl_seconds, min(base_ttl, custom_policy.max_ttl_seconds))

    return base_ttl


def should_compress(data_size: int, compression: CompressionType) -> bool:
    """Determine if data should be compressed."""
    if compression == CompressionType.NONE:
        return False
    return data_size > COMPRESSION_THRESHOLD_BYTES


def estimate_cache_size(data: Any) -> int:
    """Estimate the size of data in bytes."""
    import json
    import sys

    try:
        # Try JSON serialization for accurate size
        json_str = json.dumps(data)
        return len(json_str.encode('utf-8'))
    except (TypeError, ValueError):
        # Fall back to sys.getsizeof for non-JSON data
        return sys.getsizeof(data)
