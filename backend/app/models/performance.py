"""
Performance Models

Database models for performance monitoring and optimization.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.database import Base


class QueryPerformance(Base):
    """
    Query performance tracking for optimization.
    """
    __tablename__ = "query_performance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Query identification
    query_hash = Column(String(64), nullable=False, index=True)
    query_text = Column(Text, nullable=True)
    query_type = Column(String(50), nullable=True)  # select, aggregate, join

    # Source
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.id", ondelete="SET NULL"), nullable=True)
    dashboard_id = Column(UUID(as_uuid=True), nullable=True)
    chart_id = Column(UUID(as_uuid=True), nullable=True)

    # Execution metrics
    execution_time_ms = Column(Integer, nullable=False)
    rows_returned = Column(Integer, nullable=True)
    bytes_processed = Column(Float, nullable=True)

    # Resource usage
    cpu_time_ms = Column(Integer, nullable=True)
    memory_bytes = Column(Float, nullable=True)
    io_reads = Column(Integer, nullable=True)

    # Cache
    cache_hit = Column(Boolean, default=False)
    cache_key = Column(String(255), nullable=True)

    # User context
    user_id = Column(UUID(as_uuid=True), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamp
    executed_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('ix_query_performance_hash_date', query_hash, executed_at),
        Index('ix_query_performance_connection_date', connection_id, executed_at),
    )


class SlowQueryLog(Base):
    """
    Log of slow queries for investigation.
    """
    __tablename__ = "slow_query_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Query details
    query_hash = Column(String(64), nullable=False, index=True)
    query_text = Column(Text, nullable=False)

    # Performance
    execution_time_ms = Column(Integer, nullable=False)
    threshold_ms = Column(Integer, nullable=False)
    times_over_threshold = Column(Float, nullable=True)

    # Analysis
    explain_plan = Column(JSONB, nullable=True)
    optimization_suggestions = Column(JSONB, default=[])

    # Source
    connection_id = Column(UUID(as_uuid=True), nullable=True)
    connection_type = Column(String(50), nullable=True)

    # Context
    user_id = Column(UUID(as_uuid=True), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Status
    status = Column(String(50), default="new")  # new, investigating, optimized, ignored
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamp
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('ix_slow_query_logs_status_date', status, detected_at),
    )


class DashboardPerformance(Base):
    """
    Dashboard load performance tracking.
    """
    __tablename__ = "dashboard_performance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)

    # Load metrics
    total_load_time_ms = Column(Integer, nullable=False)
    query_time_ms = Column(Integer, nullable=True)
    render_time_ms = Column(Integer, nullable=True)

    # Component breakdown
    chart_timings = Column(JSONB, default={})
    slowest_chart_id = Column(UUID(as_uuid=True), nullable=True)
    slowest_chart_time_ms = Column(Integer, nullable=True)

    # Data metrics
    total_rows_loaded = Column(Integer, nullable=True)
    total_queries = Column(Integer, nullable=True)
    cache_hits = Column(Integer, default=0)
    cache_misses = Column(Integer, default=0)

    # Client info
    user_id = Column(UUID(as_uuid=True), nullable=True)
    device_type = Column(String(50), nullable=True)
    browser = Column(String(50), nullable=True)
    viewport_width = Column(Integer, nullable=True)

    # Timestamp
    loaded_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('ix_dashboard_performance_dashboard_date', dashboard_id, loaded_at),
    )


class SystemMetric(Base):
    """
    System-wide performance metrics.
    """
    __tablename__ = "system_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metric info
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # gauge, counter, histogram

    # Value
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)

    # Dimensions
    dimensions = Column(JSONB, default={})

    # Aggregation
    aggregation_type = Column(String(20), default="instant")  # instant, minute, hour, day

    # Timestamp
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('ix_system_metrics_name_date', metric_name, recorded_at),
    )


class PerformanceAlert(Base):
    """
    Performance-related alerts.
    """
    __tablename__ = "performance_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Alert info
    alert_type = Column(String(100), nullable=False)  # slow_query, high_load, cache_miss_rate
    severity = Column(String(20), nullable=False)  # warning, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Threshold
    metric_name = Column(String(100), nullable=True)
    threshold_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)

    # Context
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Status
    status = Column(String(50), default="open")  # open, acknowledged, resolved
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    triggered_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('ix_performance_alerts_status_date', status, triggered_at),
    )


class CacheStats(Base):
    """
    Cache performance statistics.
    """
    __tablename__ = "cache_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    granularity = Column(String(20), default="hour")  # minute, hour, day

    # Cache type
    cache_type = Column(String(50), nullable=False)  # query, dashboard, schema

    # Metrics
    total_requests = Column(Integer, default=0)
    cache_hits = Column(Integer, default=0)
    cache_misses = Column(Integer, default=0)
    hit_rate = Column(Float, default=0)

    # Size
    entries_count = Column(Integer, default=0)
    total_size_bytes = Column(Float, default=0)

    # Evictions
    evictions = Column(Integer, default=0)
    expirations = Column(Integer, default=0)

    # Latency
    avg_hit_latency_ms = Column(Float, default=0)
    avg_miss_latency_ms = Column(Float, default=0)

    # Workspace
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index('ix_cache_stats_type_period', cache_type, period_start),
    )
