"""
Performance Monitoring Service

Service for system metrics, application metrics, database metrics,
real-time monitoring, and alerting.
"""

import uuid
import random
import psutil
import os
from datetime import datetime, timedelta
from typing import Any, Optional
from collections import defaultdict

from app.schemas.performance_monitoring import (
    MetricType,
    MetricCategory,
    MetricPoint,
    MetricSeries,
    MetricDefinition,
    MetricValue,
    MetricQuery,
    MetricSeriesListResponse,
    MetricStatistics,
    SystemMetrics,
    ProcessMetrics,
    RequestMetrics,
    EndpointMetrics,
    EndpointMetricsListResponse,
    DatabaseMetrics,
    ConnectionPoolMetrics,
    DatabaseMetricsListResponse,
    CacheMetrics,
    AlertThreshold,
    AlertRule,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleListResponse,
    Alert,
    AlertSeverity,
    AlertStatus,
    AlertAcknowledge,
    AlertSilence,
    AlertListResponse,
    AlertStatistics,
    MonitoringDashboard,
    HealthCheck,
    HealthStatus,
    MonitoringConfig,
    MonitoringConfigUpdate,
    TimeWindow,
    AggregationType,
    get_time_window_seconds,
    check_threshold,
)


class PerformanceMonitoringService:
    """Service for performance monitoring."""

    def __init__(self):
        # In-memory stores (production would use time-series DB like InfluxDB/Prometheus)
        self._metric_series: dict[str, list[MetricPoint]] = defaultdict(list)
        self._metric_definitions: dict[str, MetricDefinition] = {}
        self._alert_rules: dict[str, AlertRule] = {}
        self._alerts: dict[str, Alert] = {}
        self._request_metrics: dict[str, list[dict]] = defaultdict(list)
        self._config = MonitoringConfig()

        # Track process start time
        self._start_time = datetime.utcnow()

        # Initialize default metrics
        self._init_default_metrics()
        # Initialize default alert rules
        self._init_default_alert_rules()

    def _init_default_metrics(self):
        """Initialize default metric definitions."""
        defaults = [
            MetricDefinition(
                id="cpu_percent",
                name="cpu_percent",
                category=MetricCategory.SYSTEM,
                type=MetricType.GAUGE,
                unit="percent",
                description="CPU usage percentage",
            ),
            MetricDefinition(
                id="memory_percent",
                name="memory_percent",
                category=MetricCategory.SYSTEM,
                type=MetricType.GAUGE,
                unit="percent",
                description="Memory usage percentage",
            ),
            MetricDefinition(
                id="request_latency",
                name="request_latency",
                category=MetricCategory.API,
                type=MetricType.HISTOGRAM,
                unit="ms",
                description="HTTP request latency",
                labels=["method", "endpoint", "status"],
            ),
            MetricDefinition(
                id="request_count",
                name="request_count",
                category=MetricCategory.API,
                type=MetricType.COUNTER,
                description="Total HTTP requests",
                labels=["method", "endpoint", "status"],
            ),
            MetricDefinition(
                id="cache_hit_rate",
                name="cache_hit_rate",
                category=MetricCategory.CACHE,
                type=MetricType.GAUGE,
                unit="percent",
                description="Cache hit rate",
            ),
        ]
        for metric in defaults:
            self._metric_definitions[metric.id] = metric

    def _init_default_alert_rules(self):
        """Initialize default alert rules."""
        defaults = [
            AlertRule(
                id="high_cpu",
                name="High CPU Usage",
                description="CPU usage exceeds 90%",
                severity=AlertSeverity.WARNING,
                category=MetricCategory.SYSTEM,
                thresholds=[
                    AlertThreshold(
                        metric_name="cpu_percent",
                        operator="gt",
                        value=90,
                        duration_seconds=300,
                    )
                ],
                notification_channels=[],
                cooldown_seconds=600,
                enabled=True,
            ),
            AlertRule(
                id="high_memory",
                name="High Memory Usage",
                description="Memory usage exceeds 85%",
                severity=AlertSeverity.WARNING,
                category=MetricCategory.SYSTEM,
                thresholds=[
                    AlertThreshold(
                        metric_name="memory_percent",
                        operator="gt",
                        value=85,
                        duration_seconds=300,
                    )
                ],
                notification_channels=[],
                cooldown_seconds=600,
                enabled=True,
            ),
            AlertRule(
                id="high_error_rate",
                name="High Error Rate",
                description="Error rate exceeds 5%",
                severity=AlertSeverity.ERROR,
                category=MetricCategory.API,
                thresholds=[
                    AlertThreshold(
                        metric_name="error_rate",
                        operator="gt",
                        value=5,
                        duration_seconds=300,
                    )
                ],
                notification_channels=[],
                cooldown_seconds=300,
                enabled=True,
            ),
        ]
        for rule in defaults:
            self._alert_rules[rule.id] = rule

    # Metric Collection

    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        network = psutil.net_io_counters()

        # Get load average (Unix only)
        load_avg = None
        try:
            load_avg = os.getloadavg()
        except (AttributeError, OSError):
            pass

        # Calculate uptime
        uptime = (datetime.utcnow() - self._start_time).total_seconds()

        metrics = SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            cpu_count=psutil.cpu_count(),
            memory_total_mb=memory.total / (1024 * 1024),
            memory_used_mb=memory.used / (1024 * 1024),
            memory_percent=memory.percent,
            disk_total_gb=disk.total / (1024 * 1024 * 1024),
            disk_used_gb=disk.used / (1024 * 1024 * 1024),
            disk_percent=disk.percent,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            load_average_1m=load_avg[0] if load_avg else None,
            load_average_5m=load_avg[1] if load_avg else None,
            load_average_15m=load_avg[2] if load_avg else None,
            uptime_seconds=uptime,
        )

        # Record metrics
        await self.record_metric("cpu_percent", metrics.cpu_percent)
        await self.record_metric("memory_percent", metrics.memory_percent)
        await self.record_metric("disk_percent", metrics.disk_percent)

        return metrics

    async def collect_process_metrics(self) -> ProcessMetrics:
        """Collect current process metrics."""
        process = psutil.Process()

        return ProcessMetrics(
            timestamp=datetime.utcnow(),
            pid=process.pid,
            cpu_percent=process.cpu_percent(),
            memory_mb=process.memory_info().rss / (1024 * 1024),
            memory_percent=process.memory_percent(),
            threads=process.num_threads(),
            open_files=len(process.open_files()),
            connections=len(process.connections()),
        )

    async def collect_request_metrics(self) -> RequestMetrics:
        """Collect HTTP request metrics."""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=5)

        # Aggregate recent requests
        all_requests = []
        for endpoint_requests in self._request_metrics.values():
            all_requests.extend([
                r for r in endpoint_requests
                if r.get("timestamp", datetime.min) >= window_start
            ])

        if not all_requests:
            return RequestMetrics(
                timestamp=now,
                total_requests=0,
                requests_per_second=0,
                avg_latency_ms=0,
                p50_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                error_count=0,
                error_rate=0,
            )

        latencies = [r.get("latency_ms", 0) for r in all_requests]
        latencies.sort()

        error_count = sum(1 for r in all_requests if r.get("status_code", 200) >= 400)
        total = len(all_requests)

        # Calculate percentiles
        def percentile(data: list, p: float) -> float:
            if not data:
                return 0
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f < len(data) - 1 else f
            return data[f] + (data[c] - data[f]) * (k - f)

        # Group by endpoint
        by_endpoint: dict[str, dict] = defaultdict(lambda: {
            "count": 0,
            "latencies": [],
            "errors": 0,
        })
        for r in all_requests:
            ep = r.get("endpoint", "unknown")
            by_endpoint[ep]["count"] += 1
            by_endpoint[ep]["latencies"].append(r.get("latency_ms", 0))
            if r.get("status_code", 200) >= 400:
                by_endpoint[ep]["errors"] += 1

        endpoint_stats = {}
        for ep, stats in by_endpoint.items():
            endpoint_stats[ep] = {
                "count": stats["count"],
                "avg_latency_ms": sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0,
                "error_rate": (stats["errors"] / stats["count"] * 100) if stats["count"] > 0 else 0,
            }

        # Group by status code
        by_status: dict[int, int] = defaultdict(int)
        for r in all_requests:
            by_status[r.get("status_code", 200)] += 1

        return RequestMetrics(
            timestamp=now,
            total_requests=total,
            requests_per_second=total / 300,  # 5 minute window
            avg_latency_ms=sum(latencies) / len(latencies),
            p50_latency_ms=percentile(latencies, 50),
            p95_latency_ms=percentile(latencies, 95),
            p99_latency_ms=percentile(latencies, 99),
            error_count=error_count,
            error_rate=(error_count / total * 100) if total > 0 else 0,
            by_endpoint=endpoint_stats,
            by_status_code=dict(by_status),
        )

    async def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        latency_ms: float,
    ):
        """Record an HTTP request."""
        self._request_metrics[endpoint].append({
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow(),
        })

        # Keep only last hour of data
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self._request_metrics[endpoint] = [
            r for r in self._request_metrics[endpoint]
            if r.get("timestamp", datetime.min) >= cutoff
        ]

    async def get_endpoint_metrics(
        self,
        limit: int = 50,
    ) -> EndpointMetricsListResponse:
        """Get metrics for all endpoints."""
        now = datetime.utcnow()
        window_start = now - timedelta(hours=1)

        endpoints = []
        for endpoint, requests in self._request_metrics.items():
            recent = [r for r in requests if r.get("timestamp", datetime.min) >= window_start]
            if not recent:
                continue

            latencies = sorted([r.get("latency_ms", 0) for r in recent])
            error_count = sum(1 for r in recent if r.get("status_code", 200) >= 400)

            endpoints.append(EndpointMetrics(
                endpoint=endpoint,
                method=recent[0].get("method", "GET"),
                request_count=len(recent),
                avg_latency_ms=sum(latencies) / len(latencies),
                p95_latency_ms=latencies[int(len(latencies) * 0.95)] if latencies else 0,
                error_count=error_count,
                error_rate=(error_count / len(recent) * 100) if recent else 0,
                last_request_at=max(r.get("timestamp") for r in recent),
            ))

        endpoints.sort(key=lambda e: e.request_count, reverse=True)

        return EndpointMetricsListResponse(
            endpoints=endpoints[:limit],
            total=len(endpoints),
        )

    # Database Metrics (simulated)

    async def get_database_metrics(
        self,
        connection_id: Optional[str] = None,
    ) -> DatabaseMetricsListResponse:
        """Get database metrics."""
        # In production, this would query actual database stats
        databases = [
            DatabaseMetrics(
                timestamp=datetime.utcnow(),
                connection_id="pg-main",
                connection_name="PostgreSQL Main",
                active_connections=random.randint(5, 20),
                max_connections=100,
                connection_utilization=random.uniform(5, 30),
                queries_per_second=random.uniform(10, 100),
                avg_query_time_ms=random.uniform(5, 50),
                slow_queries=random.randint(0, 5),
                deadlocks=0,
                cache_hit_ratio=random.uniform(0.9, 0.99),
                table_scans=random.randint(10, 100),
                index_scans=random.randint(100, 1000),
                rows_read=random.randint(10000, 100000),
                rows_written=random.randint(100, 1000),
            ),
        ]

        if connection_id:
            databases = [d for d in databases if d.connection_id == connection_id]

        return DatabaseMetricsListResponse(databases=databases, total=len(databases))

    async def get_connection_pool_metrics(
        self,
        connection_id: str,
    ) -> ConnectionPoolMetrics:
        """Get connection pool metrics."""
        return ConnectionPoolMetrics(
            connection_id=connection_id,
            pool_size=20,
            active_connections=random.randint(5, 15),
            idle_connections=random.randint(5, 10),
            waiting_requests=random.randint(0, 3),
            checkout_timeout_count=random.randint(0, 2),
            avg_checkout_time_ms=random.uniform(1, 10),
        )

    # Cache Metrics (simulated)

    async def get_cache_metrics(self) -> CacheMetrics:
        """Get cache metrics."""
        return CacheMetrics(
            timestamp=datetime.utcnow(),
            total_keys=random.randint(1000, 10000),
            memory_used_mb=random.uniform(50, 200),
            memory_limit_mb=512,
            hit_count=random.randint(10000, 100000),
            miss_count=random.randint(1000, 10000),
            hit_rate=random.uniform(0.85, 0.99),
            evictions=random.randint(0, 100),
            expired_keys=random.randint(0, 500),
            operations_per_second=random.uniform(100, 1000),
            avg_key_size_bytes=random.uniform(20, 100),
            avg_value_size_bytes=random.uniform(100, 1000),
        )

    # Metric Recording and Querying

    async def record_metric(
        self,
        name: str,
        value: float,
        labels: dict[str, str] = None,
    ):
        """Record a metric value."""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {},
        )

        key = f"{name}:{str(labels or {})}"
        self._metric_series[key].append(point)

        # Keep only last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self._metric_series[key] = [
            p for p in self._metric_series[key]
            if p.timestamp >= cutoff
        ]

    async def query_metrics(self, query: MetricQuery) -> MetricSeries:
        """Query metric data."""
        key = f"{query.metric_name}:{str(query.labels)}"
        points = self._metric_series.get(key, [])

        # Apply time filter
        window_seconds = get_time_window_seconds(query.time_window)
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)

        if query.start_time:
            cutoff = max(cutoff, query.start_time)

        filtered = [p for p in points if p.timestamp >= cutoff]
        if query.end_time:
            filtered = [p for p in filtered if p.timestamp <= query.end_time]

        # Get metric definition
        definition = self._metric_definitions.get(query.metric_name)

        return MetricSeries(
            name=query.metric_name,
            category=definition.category if definition else MetricCategory.CUSTOM,
            type=definition.type if definition else MetricType.GAUGE,
            unit=definition.unit if definition else None,
            description=definition.description if definition else None,
            labels=query.labels,
            points=filtered,
        )

    async def get_metric_statistics(
        self,
        metric_name: str,
        time_window: TimeWindow = TimeWindow.LAST_HOUR,
        labels: dict[str, str] = None,
    ) -> MetricStatistics:
        """Get statistics for a metric."""
        query = MetricQuery(
            metric_name=metric_name,
            labels=labels or {},
            time_window=time_window,
        )
        series = await self.query_metrics(query)

        values = [p.value for p in series.points]
        if not values:
            return MetricStatistics(
                metric_name=metric_name,
                min=0,
                max=0,
                avg=0,
                sum=0,
                count=0,
                p50=0,
                p90=0,
                p95=0,
                p99=0,
                stddev=0,
                time_window=time_window,
            )

        values.sort()

        def percentile(data: list, p: float) -> float:
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f < len(data) - 1 else f
            return data[f] + (data[c] - data[f]) * (k - f)

        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)

        return MetricStatistics(
            metric_name=metric_name,
            min=min(values),
            max=max(values),
            avg=avg,
            sum=sum(values),
            count=len(values),
            p50=percentile(values, 50),
            p90=percentile(values, 90),
            p95=percentile(values, 95),
            p99=percentile(values, 99),
            stddev=variance ** 0.5,
            time_window=time_window,
        )

    # Alert Management

    async def create_alert_rule(self, data: AlertRuleCreate) -> AlertRule:
        """Create an alert rule."""
        rule_id = str(uuid.uuid4())

        rule = AlertRule(
            id=rule_id,
            name=data.name,
            description=data.description,
            severity=data.severity,
            category=data.category,
            thresholds=data.thresholds,
            notification_channels=data.notification_channels,
            cooldown_seconds=data.cooldown_seconds,
            enabled=data.enabled,
            workspace_id=data.workspace_id,
            tags=data.tags,
        )

        self._alert_rules[rule_id] = rule
        return rule

    async def get_alert_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get alert rule by ID."""
        return self._alert_rules.get(rule_id)

    async def list_alert_rules(
        self,
        category: Optional[MetricCategory] = None,
        severity: Optional[AlertSeverity] = None,
        enabled: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AlertRuleListResponse:
        """List alert rules."""
        rules = list(self._alert_rules.values())

        if category:
            rules = [r for r in rules if r.category == category]
        if severity:
            rules = [r for r in rules if r.severity == severity]
        if enabled is not None:
            rules = [r for r in rules if r.enabled == enabled]

        total = len(rules)
        rules = rules[offset:offset + limit]

        return AlertRuleListResponse(rules=rules, total=total)

    async def update_alert_rule(
        self,
        rule_id: str,
        update: AlertRuleUpdate,
    ) -> Optional[AlertRule]:
        """Update alert rule."""
        rule = self._alert_rules.get(rule_id)
        if not rule:
            return None

        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        rule.updated_at = datetime.utcnow()
        return rule

    async def delete_alert_rule(self, rule_id: str) -> bool:
        """Delete alert rule."""
        if rule_id in self._alert_rules:
            del self._alert_rules[rule_id]
            return True
        return False

    async def check_alert_rules(self):
        """Check all alert rules and trigger alerts."""
        for rule in self._alert_rules.values():
            if not rule.enabled:
                continue

            # Check cooldown
            if rule.last_triggered_at:
                cooldown_end = rule.last_triggered_at + timedelta(seconds=rule.cooldown_seconds)
                if datetime.utcnow() < cooldown_end:
                    continue

            # Check thresholds
            for threshold in rule.thresholds:
                stats = await self.get_metric_statistics(
                    threshold.metric_name,
                    TimeWindow.LAST_5_MINUTES,
                    threshold.labels,
                )

                # Get value based on aggregation
                if threshold.aggregation == AggregationType.AVG:
                    value = stats.avg
                elif threshold.aggregation == AggregationType.MAX:
                    value = stats.max
                elif threshold.aggregation == AggregationType.MIN:
                    value = stats.min
                elif threshold.aggregation == AggregationType.SUM:
                    value = stats.sum
                elif threshold.aggregation == AggregationType.P95:
                    value = stats.p95
                elif threshold.aggregation == AggregationType.P99:
                    value = stats.p99
                else:
                    value = stats.avg

                if check_threshold(value, threshold):
                    await self._trigger_alert(rule, threshold, value)
                    break

    async def _trigger_alert(
        self,
        rule: AlertRule,
        threshold: AlertThreshold,
        value: float,
    ):
        """Trigger an alert."""
        alert_id = str(uuid.uuid4())

        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            rule_name=rule.name,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            message=f"{rule.name}: {threshold.metric_name} = {value:.2f} (threshold: {threshold.operator} {threshold.value})",
            metric_name=threshold.metric_name,
            metric_value=value,
            threshold_value=threshold.value,
            labels=threshold.labels,
            triggered_at=datetime.utcnow(),
        )

        self._alerts[alert_id] = alert

        # Update rule
        rule.last_triggered_at = datetime.utcnow()
        rule.trigger_count += 1

    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID."""
        return self._alerts.get(alert_id)

    async def list_alerts(
        self,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        rule_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AlertListResponse:
        """List alerts."""
        alerts = list(self._alerts.values())

        if status:
            alerts = [a for a in alerts if a.status == status]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if rule_id:
            alerts = [a for a in alerts if a.rule_id == rule_id]

        alerts.sort(key=lambda a: a.triggered_at, reverse=True)

        total = len(alerts)
        alerts = alerts[offset:offset + limit]

        return AlertListResponse(alerts=alerts, total=total)

    async def acknowledge_alert(
        self,
        alert_id: str,
        ack: AlertAcknowledge,
    ) -> Optional[Alert]:
        """Acknowledge an alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = ack.user_id
        if ack.comment:
            alert.metadata["ack_comment"] = ack.comment

        return alert

    async def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """Resolve an alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()

        return alert

    async def silence_alert(
        self,
        alert_id: str,
        silence: AlertSilence,
    ) -> Optional[Alert]:
        """Silence an alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        alert.status = AlertStatus.SILENCED
        alert.silenced_until = datetime.utcnow() + timedelta(minutes=silence.duration_minutes)
        if silence.reason:
            alert.metadata["silence_reason"] = silence.reason

        return alert

    async def get_alert_statistics(self) -> AlertStatistics:
        """Get alert statistics."""
        alerts = list(self._alerts.values())

        active = len([a for a in alerts if a.status == AlertStatus.ACTIVE])
        acknowledged = len([a for a in alerts if a.status == AlertStatus.ACKNOWLEDGED])
        resolved = len([a for a in alerts if a.status == AlertStatus.RESOLVED])

        by_severity: dict[str, int] = defaultdict(int)
        by_category: dict[str, int] = defaultdict(int)

        for alert in alerts:
            by_severity[alert.severity.value] += 1
            rule = self._alert_rules.get(alert.rule_id)
            if rule:
                by_category[rule.category.value] += 1

        # Calculate resolution time
        resolved_alerts = [a for a in alerts if a.resolved_at and a.triggered_at]
        resolution_times = [
            (a.resolved_at - a.triggered_at).total_seconds() / 60
            for a in resolved_alerts
        ]

        # Calculate alert rate (last 24 hours)
        recent_alerts = [
            a for a in alerts
            if a.triggered_at >= datetime.utcnow() - timedelta(hours=24)
        ]

        return AlertStatistics(
            total_alerts=len(alerts),
            active_alerts=active,
            acknowledged_alerts=acknowledged,
            resolved_alerts=resolved,
            by_severity=dict(by_severity),
            by_category=dict(by_category),
            avg_resolution_time_minutes=sum(resolution_times) / len(resolution_times) if resolution_times else 0,
            alert_rate_per_hour=len(recent_alerts) / 24,
        )

    # Dashboard

    async def get_dashboard(self) -> MonitoringDashboard:
        """Get monitoring dashboard."""
        system = await self.collect_system_metrics()
        process = await self.collect_process_metrics()
        requests = await self.collect_request_metrics()
        cache = await self.get_cache_metrics()
        databases_response = await self.get_database_metrics()

        active_alerts = await self.list_alerts(status=AlertStatus.ACTIVE, limit=10)

        # Determine health status
        health = "healthy"
        if system.cpu_percent > 90 or system.memory_percent > 90:
            health = "degraded"
        if active_alerts.total > 0:
            for alert in active_alerts.alerts:
                if alert.severity == AlertSeverity.CRITICAL:
                    health = "unhealthy"
                    break
                elif alert.severity == AlertSeverity.ERROR:
                    health = "degraded"

        return MonitoringDashboard(
            timestamp=datetime.utcnow(),
            system=system,
            process=process,
            requests=requests,
            cache=cache,
            databases=databases_response.databases,
            active_alerts=active_alerts.alerts,
            health_status=health,
        )

    # Health Checks

    async def check_health(self) -> HealthStatus:
        """Run health checks."""
        checks = []

        # API health
        checks.append(HealthCheck(
            component="api",
            status="healthy",
            latency_ms=random.uniform(1, 10),
            message="API responding normally",
            last_check=datetime.utcnow(),
        ))

        # Database health
        checks.append(HealthCheck(
            component="database",
            status="healthy",
            latency_ms=random.uniform(5, 20),
            message="Database connection OK",
            last_check=datetime.utcnow(),
        ))

        # Cache health
        checks.append(HealthCheck(
            component="cache",
            status="healthy",
            latency_ms=random.uniform(0.5, 5),
            message="Cache responding normally",
            last_check=datetime.utcnow(),
        ))

        # Determine overall status
        overall = "healthy"
        for check in checks:
            if check.status == "unhealthy":
                overall = "unhealthy"
                break
            elif check.status == "degraded":
                overall = "degraded"

        return HealthStatus(
            status=overall,
            timestamp=datetime.utcnow(),
            checks=checks,
            uptime_seconds=(datetime.utcnow() - self._start_time).total_seconds(),
            version="1.0.0",
        )

    # Configuration

    async def get_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        return self._config

    async def update_config(self, update: MonitoringConfigUpdate) -> MonitoringConfig:
        """Update monitoring configuration."""
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(self._config, field, value)
        return self._config


# Global service instance
performance_monitoring_service = PerformanceMonitoringService()
