"""
Performance Monitoring API Endpoints

Endpoints for system metrics, application metrics, database metrics,
real-time monitoring, and alerting.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.performance_monitoring import (
    MetricCategory,
    MetricSeries,
    MetricQuery,
    MetricSeriesListResponse,
    MetricStatistics,
    SystemMetrics,
    ProcessMetrics,
    RequestMetrics,
    EndpointMetricsListResponse,
    DatabaseMetricsListResponse,
    ConnectionPoolMetrics,
    CacheMetrics,
    AlertRule,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleListResponse,
    AlertSeverity,
    AlertStatus,
    Alert,
    AlertAcknowledge,
    AlertSilence,
    AlertListResponse,
    AlertStatistics,
    MonitoringDashboard,
    HealthStatus,
    MonitoringConfig,
    MonitoringConfigUpdate,
    TimeWindow,
)
from app.services.performance_monitoring_service import performance_monitoring_service

router = APIRouter()


# System Metrics Endpoints

@router.get("/system", response_model=SystemMetrics)
async def get_system_metrics():
    """Get current system metrics."""
    metrics = await performance_monitoring_service.collect_system_metrics()
    return metrics


@router.get("/process", response_model=ProcessMetrics)
async def get_process_metrics():
    """Get current process metrics."""
    metrics = await performance_monitoring_service.collect_process_metrics()
    return metrics


# Request Metrics Endpoints

@router.get("/requests", response_model=RequestMetrics)
async def get_request_metrics():
    """Get HTTP request metrics."""
    metrics = await performance_monitoring_service.collect_request_metrics()
    return metrics


@router.get("/requests/endpoints", response_model=EndpointMetricsListResponse)
async def get_endpoint_metrics(limit: int = Query(50, ge=1, le=200)):
    """Get metrics for all endpoints."""
    metrics = await performance_monitoring_service.get_endpoint_metrics(limit)
    return metrics


@router.post("/requests/record")
async def record_request(
    endpoint: str,
    method: str,
    status_code: int,
    latency_ms: float,
):
    """Record an HTTP request (for middleware integration)."""
    await performance_monitoring_service.record_request(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        latency_ms=latency_ms,
    )
    return {"message": "Request recorded"}


# Database Metrics Endpoints

@router.get("/databases", response_model=DatabaseMetricsListResponse)
async def get_database_metrics(connection_id: Optional[str] = None):
    """Get database metrics."""
    metrics = await performance_monitoring_service.get_database_metrics(connection_id)
    return metrics


@router.get("/databases/{connection_id}/pool", response_model=ConnectionPoolMetrics)
async def get_connection_pool_metrics(connection_id: str):
    """Get connection pool metrics for a database."""
    metrics = await performance_monitoring_service.get_connection_pool_metrics(connection_id)
    return metrics


# Cache Metrics Endpoints

@router.get("/cache", response_model=CacheMetrics)
async def get_cache_metrics():
    """Get cache metrics."""
    metrics = await performance_monitoring_service.get_cache_metrics()
    return metrics


# Metric Query Endpoints

@router.post("/metrics/query", response_model=MetricSeries)
async def query_metrics(query: MetricQuery):
    """Query metric data."""
    series = await performance_monitoring_service.query_metrics(query)
    return series


@router.get("/metrics/{metric_name}/stats", response_model=MetricStatistics)
async def get_metric_statistics(
    metric_name: str,
    time_window: TimeWindow = TimeWindow.LAST_HOUR,
):
    """Get statistics for a metric."""
    stats = await performance_monitoring_service.get_metric_statistics(
        metric_name,
        time_window,
    )
    return stats


@router.post("/metrics/record")
async def record_metric(
    name: str,
    value: float,
    labels: Optional[str] = Query(None, description="JSON-encoded labels"),
):
    """Record a metric value."""
    import json
    label_dict = json.loads(labels) if labels else {}
    await performance_monitoring_service.record_metric(name, value, label_dict)
    return {"message": "Metric recorded"}


# Alert Rule Endpoints

@router.post("/alerts/rules", response_model=AlertRule)
async def create_alert_rule(data: AlertRuleCreate):
    """Create an alert rule."""
    rule = await performance_monitoring_service.create_alert_rule(data)
    return rule


@router.get("/alerts/rules", response_model=AlertRuleListResponse)
async def list_alert_rules(
    category: Optional[MetricCategory] = None,
    severity: Optional[AlertSeverity] = None,
    enabled: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List alert rules."""
    rules = await performance_monitoring_service.list_alert_rules(
        category=category,
        severity=severity,
        enabled=enabled,
        limit=limit,
        offset=offset,
    )
    return rules


@router.get("/alerts/rules/{rule_id}", response_model=AlertRule)
async def get_alert_rule(rule_id: str):
    """Get alert rule by ID."""
    rule = await performance_monitoring_service.get_alert_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return rule


@router.patch("/alerts/rules/{rule_id}", response_model=AlertRule)
async def update_alert_rule(rule_id: str, update: AlertRuleUpdate):
    """Update alert rule."""
    rule = await performance_monitoring_service.update_alert_rule(rule_id, update)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return rule


@router.delete("/alerts/rules/{rule_id}")
async def delete_alert_rule(rule_id: str):
    """Delete alert rule."""
    deleted = await performance_monitoring_service.delete_alert_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return {"message": "Alert rule deleted"}


@router.post("/alerts/rules/{rule_id}/enable")
async def enable_alert_rule(rule_id: str):
    """Enable an alert rule."""
    rule = await performance_monitoring_service.update_alert_rule(
        rule_id,
        AlertRuleUpdate(enabled=True),
    )
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return {"message": "Alert rule enabled"}


@router.post("/alerts/rules/{rule_id}/disable")
async def disable_alert_rule(rule_id: str):
    """Disable an alert rule."""
    rule = await performance_monitoring_service.update_alert_rule(
        rule_id,
        AlertRuleUpdate(enabled=False),
    )
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return {"message": "Alert rule disabled"}


# Alert Endpoints

@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    rule_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List alerts."""
    alerts = await performance_monitoring_service.list_alerts(
        status=status,
        severity=severity,
        rule_id=rule_id,
        limit=limit,
        offset=offset,
    )
    return alerts


@router.get("/alerts/active", response_model=AlertListResponse)
async def list_active_alerts(limit: int = Query(50, ge=1, le=200)):
    """List active alerts."""
    alerts = await performance_monitoring_service.list_alerts(
        status=AlertStatus.ACTIVE,
        limit=limit,
    )
    return alerts


@router.get("/alerts/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """Get alert by ID."""
    alert = await performance_monitoring_service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/acknowledge", response_model=Alert)
async def acknowledge_alert(alert_id: str, ack: AlertAcknowledge):
    """Acknowledge an alert."""
    alert = await performance_monitoring_service.acknowledge_alert(alert_id, ack)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/resolve", response_model=Alert)
async def resolve_alert(alert_id: str):
    """Resolve an alert."""
    alert = await performance_monitoring_service.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/silence", response_model=Alert)
async def silence_alert(alert_id: str, silence: AlertSilence):
    """Silence an alert."""
    alert = await performance_monitoring_service.silence_alert(alert_id, silence)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.get("/alerts/stats", response_model=AlertStatistics)
async def get_alert_statistics():
    """Get alert statistics."""
    stats = await performance_monitoring_service.get_alert_statistics()
    return stats


@router.post("/alerts/check")
async def check_alerts():
    """Manually trigger alert rule checks."""
    await performance_monitoring_service.check_alert_rules()
    return {"message": "Alert rules checked"}


# Dashboard Endpoints

@router.get("/dashboard", response_model=MonitoringDashboard)
async def get_monitoring_dashboard():
    """Get real-time monitoring dashboard."""
    dashboard = await performance_monitoring_service.get_dashboard()
    return dashboard


# Health Endpoints

@router.get("/health", response_model=HealthStatus)
async def get_health_status():
    """Get overall health status."""
    health = await performance_monitoring_service.check_health()
    return health


@router.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe."""
    health = await performance_monitoring_service.check_health()
    if health.status == "unhealthy":
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"status": "ready"}


# Configuration Endpoints

@router.get("/config", response_model=MonitoringConfig)
async def get_monitoring_config():
    """Get monitoring configuration."""
    config = await performance_monitoring_service.get_config()
    return config


@router.put("/config", response_model=MonitoringConfig)
async def update_monitoring_config(update: MonitoringConfigUpdate):
    """Update monitoring configuration."""
    config = await performance_monitoring_service.update_config(update)
    return config
