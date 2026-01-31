"""
Performance Monitoring Schemas

Pydantic schemas for system metrics, application metrics, database metrics,
real-time monitoring, and alerting.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricCategory(str, Enum):
    """Categories of metrics"""
    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    QUERY = "query"
    JOB = "job"
    CUSTOM = "custom"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


class ComparisonOperator(str, Enum):
    """Comparison operators for thresholds"""
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    EQUAL = "eq"
    NOT_EQUAL = "ne"


class AggregationType(str, Enum):
    """Aggregation types for metrics"""
    AVG = "avg"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    P50 = "p50"
    P90 = "p90"
    P95 = "p95"
    P99 = "p99"


class TimeWindow(str, Enum):
    """Time windows for metrics"""
    LAST_MINUTE = "1m"
    LAST_5_MINUTES = "5m"
    LAST_15_MINUTES = "15m"
    LAST_HOUR = "1h"
    LAST_6_HOURS = "6h"
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"


# Metric Models

class MetricPoint(BaseModel):
    """Single metric data point"""
    timestamp: datetime
    value: float
    labels: dict[str, str] = Field(default_factory=dict)


class MetricSeries(BaseModel):
    """Time series of metric points"""
    name: str
    category: MetricCategory
    type: MetricType
    unit: Optional[str] = None
    description: Optional[str] = None
    labels: dict[str, str] = Field(default_factory=dict)
    points: list[MetricPoint] = Field(default_factory=list)


class MetricDefinition(BaseModel):
    """Metric definition"""
    id: str
    name: str
    category: MetricCategory
    type: MetricType
    unit: Optional[str] = None
    description: Optional[str] = None
    labels: list[str] = Field(default_factory=list)
    enabled: bool = True
    retention_days: int = 30


class MetricValue(BaseModel):
    """Current metric value"""
    name: str
    value: float
    timestamp: datetime
    labels: dict[str, str] = Field(default_factory=dict)


class MetricQuery(BaseModel):
    """Query for metrics"""
    metric_name: str
    labels: dict[str, str] = Field(default_factory=dict)
    aggregation: AggregationType = AggregationType.AVG
    time_window: TimeWindow = TimeWindow.LAST_HOUR
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    step_seconds: int = 60


# System Metrics

class SystemMetrics(BaseModel):
    """System-level metrics"""
    timestamp: datetime
    cpu_percent: float
    cpu_count: int
    memory_total_mb: float
    memory_used_mb: float
    memory_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    load_average_1m: Optional[float] = None
    load_average_5m: Optional[float] = None
    load_average_15m: Optional[float] = None
    uptime_seconds: float


class ProcessMetrics(BaseModel):
    """Process-level metrics"""
    timestamp: datetime
    pid: int
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    threads: int
    open_files: int
    connections: int


# Application Metrics

class RequestMetrics(BaseModel):
    """HTTP request metrics"""
    timestamp: datetime
    total_requests: int
    requests_per_second: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_count: int
    error_rate: float
    by_endpoint: dict[str, dict[str, Any]] = Field(default_factory=dict)
    by_status_code: dict[int, int] = Field(default_factory=dict)


class EndpointMetrics(BaseModel):
    """Metrics for a specific endpoint"""
    endpoint: str
    method: str
    request_count: int
    avg_latency_ms: float
    p95_latency_ms: float
    error_count: int
    error_rate: float
    last_request_at: Optional[datetime] = None


# Database Metrics

class DatabaseMetrics(BaseModel):
    """Database-level metrics"""
    timestamp: datetime
    connection_id: str
    connection_name: str
    active_connections: int
    max_connections: int
    connection_utilization: float
    queries_per_second: float
    avg_query_time_ms: float
    slow_queries: int
    deadlocks: int
    cache_hit_ratio: float
    table_scans: int
    index_scans: int
    rows_read: int
    rows_written: int


class ConnectionPoolMetrics(BaseModel):
    """Connection pool metrics"""
    connection_id: str
    pool_size: int
    active_connections: int
    idle_connections: int
    waiting_requests: int
    checkout_timeout_count: int
    avg_checkout_time_ms: float


# Cache Metrics

class CacheMetrics(BaseModel):
    """Cache metrics"""
    timestamp: datetime
    total_keys: int
    memory_used_mb: float
    memory_limit_mb: float
    hit_count: int
    miss_count: int
    hit_rate: float
    evictions: int
    expired_keys: int
    operations_per_second: float
    avg_key_size_bytes: float
    avg_value_size_bytes: float


# Alert Models

class AlertThreshold(BaseModel):
    """Alert threshold definition"""
    metric_name: str
    operator: ComparisonOperator
    value: float
    duration_seconds: int = 60  # How long condition must be true
    aggregation: AggregationType = AggregationType.AVG
    labels: dict[str, str] = Field(default_factory=dict)


class AlertRuleCreate(BaseModel):
    """Create an alert rule"""
    name: str
    description: Optional[str] = None
    severity: AlertSeverity
    category: MetricCategory
    thresholds: list[AlertThreshold]
    notification_channels: list[str] = Field(default_factory=list)
    cooldown_seconds: int = 300
    enabled: bool = True
    workspace_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class AlertRule(BaseModel):
    """Alert rule definition"""
    id: str
    name: str
    description: Optional[str] = None
    severity: AlertSeverity
    category: MetricCategory
    thresholds: list[AlertThreshold]
    notification_channels: list[str]
    cooldown_seconds: int
    enabled: bool
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    workspace_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AlertRuleUpdate(BaseModel):
    """Update alert rule"""
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    thresholds: Optional[list[AlertThreshold]] = None
    notification_channels: Optional[list[str]] = None
    cooldown_seconds: Optional[int] = None
    enabled: Optional[bool] = None
    tags: Optional[list[str]] = None


class Alert(BaseModel):
    """Active alert instance"""
    id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    metric_name: str
    metric_value: float
    threshold_value: float
    labels: dict[str, str] = Field(default_factory=dict)
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    silenced_until: Optional[datetime] = None
    notification_sent: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlertAcknowledge(BaseModel):
    """Acknowledge an alert"""
    user_id: str
    comment: Optional[str] = None


class AlertSilence(BaseModel):
    """Silence an alert"""
    duration_minutes: int
    reason: Optional[str] = None


# Dashboard Models

class MonitoringDashboard(BaseModel):
    """Real-time monitoring dashboard"""
    timestamp: datetime
    system: SystemMetrics
    process: ProcessMetrics
    requests: RequestMetrics
    cache: CacheMetrics
    databases: list[DatabaseMetrics]
    active_alerts: list[Alert]
    health_status: str  # healthy, degraded, unhealthy


class HealthCheck(BaseModel):
    """System health check result"""
    component: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    last_check: datetime
    details: dict[str, Any] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    """Overall health status"""
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    checks: list[HealthCheck]
    uptime_seconds: float
    version: str


# Configuration

class MonitoringConfig(BaseModel):
    """Monitoring configuration"""
    enabled: bool = True
    collection_interval_seconds: int = 60
    retention_days: int = 30
    enable_system_metrics: bool = True
    enable_application_metrics: bool = True
    enable_database_metrics: bool = True
    enable_cache_metrics: bool = True
    slow_request_threshold_ms: int = 1000
    alert_cooldown_seconds: int = 300


class MonitoringConfigUpdate(BaseModel):
    """Update monitoring configuration"""
    enabled: Optional[bool] = None
    collection_interval_seconds: Optional[int] = None
    retention_days: Optional[int] = None
    enable_system_metrics: Optional[bool] = None
    enable_application_metrics: Optional[bool] = None
    enable_database_metrics: Optional[bool] = None
    enable_cache_metrics: Optional[bool] = None
    slow_request_threshold_ms: Optional[int] = None
    alert_cooldown_seconds: Optional[int] = None


# Response Models

class MetricSeriesListResponse(BaseModel):
    """List metric series response"""
    series: list[MetricSeries]
    total: int


class AlertRuleListResponse(BaseModel):
    """List alert rules response"""
    rules: list[AlertRule]
    total: int


class AlertListResponse(BaseModel):
    """List alerts response"""
    alerts: list[Alert]
    total: int


class EndpointMetricsListResponse(BaseModel):
    """List endpoint metrics response"""
    endpoints: list[EndpointMetrics]
    total: int


class DatabaseMetricsListResponse(BaseModel):
    """List database metrics response"""
    databases: list[DatabaseMetrics]
    total: int


# Statistics Models

class MetricStatistics(BaseModel):
    """Statistics for a metric"""
    metric_name: str
    min: float
    max: float
    avg: float
    sum: float
    count: int
    p50: float
    p90: float
    p95: float
    p99: float
    stddev: float
    time_window: TimeWindow


class AlertStatistics(BaseModel):
    """Alert statistics"""
    total_alerts: int
    active_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    by_severity: dict[str, int]
    by_category: dict[str, int]
    avg_resolution_time_minutes: float
    alert_rate_per_hour: float


# Constants

METRIC_CATEGORY_LABELS = {
    MetricCategory.SYSTEM: "System",
    MetricCategory.APPLICATION: "Application",
    MetricCategory.DATABASE: "Database",
    MetricCategory.CACHE: "Cache",
    MetricCategory.API: "API",
    MetricCategory.QUERY: "Query",
    MetricCategory.JOB: "Job",
    MetricCategory.CUSTOM: "Custom",
}

ALERT_SEVERITY_LABELS = {
    AlertSeverity.INFO: "Info",
    AlertSeverity.WARNING: "Warning",
    AlertSeverity.ERROR: "Error",
    AlertSeverity.CRITICAL: "Critical",
}

ALERT_SEVERITY_COLORS = {
    AlertSeverity.INFO: "blue",
    AlertSeverity.WARNING: "yellow",
    AlertSeverity.ERROR: "orange",
    AlertSeverity.CRITICAL: "red",
}

ALERT_STATUS_LABELS = {
    AlertStatus.ACTIVE: "Active",
    AlertStatus.ACKNOWLEDGED: "Acknowledged",
    AlertStatus.RESOLVED: "Resolved",
    AlertStatus.SILENCED: "Silenced",
}

TIME_WINDOW_SECONDS = {
    TimeWindow.LAST_MINUTE: 60,
    TimeWindow.LAST_5_MINUTES: 300,
    TimeWindow.LAST_15_MINUTES: 900,
    TimeWindow.LAST_HOUR: 3600,
    TimeWindow.LAST_6_HOURS: 21600,
    TimeWindow.LAST_24_HOURS: 86400,
    TimeWindow.LAST_7_DAYS: 604800,
    TimeWindow.LAST_30_DAYS: 2592000,
}


# Helper Functions

def get_time_window_seconds(window: TimeWindow) -> int:
    """Get seconds for time window."""
    return TIME_WINDOW_SECONDS.get(window, 3600)


def check_threshold(
    value: float,
    threshold: AlertThreshold,
) -> bool:
    """Check if value exceeds threshold."""
    op = threshold.operator
    target = threshold.value

    if op == ComparisonOperator.GREATER_THAN:
        return value > target
    elif op == ComparisonOperator.GREATER_THAN_OR_EQUAL:
        return value >= target
    elif op == ComparisonOperator.LESS_THAN:
        return value < target
    elif op == ComparisonOperator.LESS_THAN_OR_EQUAL:
        return value <= target
    elif op == ComparisonOperator.EQUAL:
        return value == target
    elif op == ComparisonOperator.NOT_EQUAL:
        return value != target

    return False


def format_metric_value(value: float, unit: Optional[str]) -> str:
    """Format metric value with unit."""
    if unit == "bytes":
        if value >= 1073741824:
            return f"{value / 1073741824:.2f} GB"
        elif value >= 1048576:
            return f"{value / 1048576:.2f} MB"
        elif value >= 1024:
            return f"{value / 1024:.2f} KB"
        return f"{value:.0f} B"
    elif unit == "percent":
        return f"{value:.1f}%"
    elif unit == "ms":
        if value >= 1000:
            return f"{value / 1000:.2f}s"
        return f"{value:.0f}ms"
    elif unit == "seconds":
        if value >= 3600:
            return f"{value / 3600:.1f}h"
        elif value >= 60:
            return f"{value / 60:.1f}m"
        return f"{value:.0f}s"
    elif unit:
        return f"{value:.2f} {unit}"
    return f"{value:.2f}"


def get_health_status_color(status: str) -> str:
    """Get color for health status."""
    if status == "healthy":
        return "green"
    elif status == "degraded":
        return "yellow"
    return "red"
