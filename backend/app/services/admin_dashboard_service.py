"""
Administration Dashboard Service

Provides aggregated data for the admin dashboard including system health,
user statistics, revenue metrics, and administrative controls.
"""

import secrets
import psutil
from datetime import datetime, timedelta
from typing import Optional

from app.schemas.admin_dashboard import (
    SystemHealthStatus, AlertLevel, TrendDirection, TimeRange,
    MetricValue, MetricTimeSeries,
    ServiceHealth, SystemHealth, ResourceUsage,
    UserStats, SessionStats, WorkspaceStats,
    RevenueStats, SubscriptionStats, PlatformUsageStats,
    SystemAlert, AlertSummary,
    AdminActivity, RecentActivity,
    SystemConfig, SystemConfigUpdate,
    AdminDashboardSummary, DashboardWidget, AdminDashboardConfig,
    AdminReport, ReportSchedule,
    QuickAction, QuickActionResult,
    DEFAULT_DASHBOARD_WIDGETS, QUICK_ACTIONS,
    calculate_trend, get_health_status_from_checks,
)


class AdminDashboardService:
    """Service for admin dashboard operations."""

    def __init__(self):
        # In-memory stores
        self.alerts: dict[str, SystemAlert] = {}
        self.admin_activities: list[AdminActivity] = []
        self.reports: dict[str, AdminReport] = {}
        self.report_schedules: dict[str, ReportSchedule] = {}
        self.config = SystemConfig()
        self.dashboard_configs: dict[str, AdminDashboardConfig] = {}

        # Simulated data stores (in production, these would come from other services)
        self._mock_data_initialized = False

    def _generate_id(self, prefix: str = "id") -> str:
        """Generate a unique ID."""
        return f"{prefix}_{secrets.token_hex(12)}"

    def _ensure_mock_data(self):
        """Ensure mock data is initialized for demo purposes."""
        if self._mock_data_initialized:
            return

        # Create some sample alerts
        self.alerts["alert_1"] = SystemAlert(
            id="alert_1",
            level=AlertLevel.WARNING,
            title="High Memory Usage",
            message="Memory usage has exceeded 80% threshold",
            source="monitoring",
        )
        self.alerts["alert_2"] = SystemAlert(
            id="alert_2",
            level=AlertLevel.INFO,
            title="Scheduled Maintenance",
            message="Scheduled maintenance window: Sunday 2AM-4AM UTC",
            source="system",
            acknowledged=True,
            acknowledged_by="admin",
            acknowledged_at=datetime.utcnow() - timedelta(hours=2),
        )

        self._mock_data_initialized = True

    # System Health

    def get_system_health(self) -> SystemHealth:
        """Get overall system health status."""
        services = []

        # Check database
        services.append(ServiceHealth(
            name="database",
            status=SystemHealthStatus.HEALTHY,
            latency_ms=5.2,
            last_check_at=datetime.utcnow(),
        ))

        # Check cache (Redis)
        services.append(ServiceHealth(
            name="cache",
            status=SystemHealthStatus.HEALTHY,
            latency_ms=1.1,
            last_check_at=datetime.utcnow(),
        ))

        # Check API
        services.append(ServiceHealth(
            name="api",
            status=SystemHealthStatus.HEALTHY,
            latency_ms=15.5,
            last_check_at=datetime.utcnow(),
        ))

        # Check background jobs
        services.append(ServiceHealth(
            name="background_jobs",
            status=SystemHealthStatus.HEALTHY,
            latency_ms=None,
            last_check_at=datetime.utcnow(),
            details={"pending_jobs": 12, "active_workers": 4},
        ))

        overall_status = get_health_status_from_checks(services)

        return SystemHealth(
            status=overall_status,
            services=services,
            uptime_percent=99.95,
            active_incidents=0,
        )

    def get_resource_usage(self) -> ResourceUsage:
        """Get current resource usage."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            network_in_mbps=0,
            network_out_mbps=0,
            active_connections=150,  # Simulated
        )

    # Statistics

    def get_user_stats(self, time_range: TimeRange = TimeRange.LAST_30_DAYS) -> UserStats:
        """Get user statistics."""
        # In production, this would query the user management service
        return UserStats(
            total_users=1250,
            active_users=890,
            new_users_today=15,
            new_users_this_week=82,
            new_users_this_month=320,
            mfa_enabled_percent=35.5,
            users_by_status={"active": 890, "inactive": 280, "locked": 12, "pending": 68},
            users_by_type={"regular": 1180, "admin": 25, "service": 45},
            users_by_auth_provider={"local": 750, "google": 350, "github": 100, "microsoft": 50},
            user_growth=[
                {"date": (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d"), "count": 1250 - i * 10}
                for i in range(30, 0, -1)
            ],
        )

    def get_session_stats(self) -> SessionStats:
        """Get session statistics."""
        return SessionStats(
            active_sessions=425,
            sessions_today=890,
            avg_session_duration_minutes=45.5,
            sessions_by_device={"desktop": 520, "mobile": 280, "tablet": 90},
            sessions_by_location={"US": 450, "UK": 120, "DE": 80, "IN": 75, "Other": 165},
            peak_concurrent_today=312,
        )

    def get_workspace_stats(self, time_range: TimeRange = TimeRange.LAST_30_DAYS) -> WorkspaceStats:
        """Get workspace statistics."""
        return WorkspaceStats(
            total_workspaces=420,
            active_workspaces=385,
            new_workspaces_this_month=45,
            workspaces_by_plan={"free": 280, "starter": 85, "pro": 40, "business": 12, "enterprise": 3},
            workspaces_by_status={"active": 385, "trial": 25, "suspended": 10},
            avg_members_per_workspace=3.8,
            workspace_growth=[
                {"date": (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d"), "count": 420 - i * 1.5}
                for i in range(30, 0, -1)
            ],
        )

    def get_revenue_stats(self, time_range: TimeRange = TimeRange.LAST_30_DAYS) -> RevenueStats:
        """Get revenue statistics."""
        return RevenueStats(
            mrr=15800.00,
            arr=189600.00,
            revenue_this_month=15800.00,
            revenue_this_year=142500.00,
            avg_revenue_per_user=12.64,
            churn_rate=2.5,
            revenue_by_plan={"starter": 2465, "pro": 7905, "business": 3588, "enterprise": 1842},
            revenue_growth=[
                {"date": (datetime.utcnow() - timedelta(days=i * 30)).strftime("%Y-%m"), "amount": 15800 - i * 500}
                for i in range(12, 0, -1)
            ],
        )

    def get_subscription_stats(self) -> SubscriptionStats:
        """Get subscription statistics."""
        return SubscriptionStats(
            total_subscriptions=420,
            active_subscriptions=385,
            trial_subscriptions=25,
            canceled_this_month=8,
            subscriptions_by_plan={"free": 280, "starter": 85, "pro": 40, "business": 12, "enterprise": 3},
            subscriptions_by_interval={"monthly": 95, "yearly": 45},
            conversion_rate=32.5,
        )

    def get_platform_usage_stats(self) -> PlatformUsageStats:
        """Get platform usage statistics."""
        return PlatformUsageStats(
            total_dashboards=1850,
            total_charts=12500,
            total_connections=580,
            total_queries_today=45000,
            total_api_calls_today=125000,
            storage_used_gb=450.5,
            storage_total_gb=1000.0,
            query_minutes_today=2850.5,
            most_active_workspaces=[
                {"workspace_id": "ws_1", "name": "Analytics Team", "activity_score": 95},
                {"workspace_id": "ws_2", "name": "Marketing", "activity_score": 88},
                {"workspace_id": "ws_3", "name": "Sales Ops", "activity_score": 82},
            ],
            popular_features=[
                {"feature": "dashboard_builder", "usage_count": 15000},
                {"feature": "sql_query", "usage_count": 12000},
                {"feature": "chart_export", "usage_count": 8500},
                {"feature": "ai_insights", "usage_count": 3500},
            ],
        )

    # Key Metrics

    def get_key_metrics(self) -> list[MetricValue]:
        """Get key metrics for dashboard."""
        return [
            MetricValue(
                name="Total Users",
                value=1250,
                previous_value=1180,
                trend=TrendDirection.UP,
                change_percent=5.9,
            ),
            MetricValue(
                name="Active Users",
                value=890,
                previous_value=850,
                trend=TrendDirection.UP,
                change_percent=4.7,
            ),
            MetricValue(
                name="MRR",
                value=15800,
                previous_value=15200,
                unit="USD",
                trend=TrendDirection.UP,
                change_percent=3.9,
            ),
            MetricValue(
                name="Churn Rate",
                value=2.5,
                previous_value=2.8,
                unit="%",
                trend=TrendDirection.DOWN,
                change_percent=-10.7,
            ),
            MetricValue(
                name="Avg Response Time",
                value=125,
                previous_value=130,
                unit="ms",
                trend=TrendDirection.DOWN,
                change_percent=-3.8,
            ),
            MetricValue(
                name="Error Rate",
                value=0.05,
                previous_value=0.08,
                unit="%",
                trend=TrendDirection.DOWN,
                change_percent=-37.5,
            ),
        ]

    # Alerts

    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        acknowledged: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[SystemAlert], int]:
        """Get system alerts."""
        self._ensure_mock_data()

        alerts = list(self.alerts.values())

        if level:
            alerts = [a for a in alerts if a.level == level]
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]

        alerts.sort(key=lambda x: x.created_at, reverse=True)
        total = len(alerts)
        alerts = alerts[skip:skip + limit]

        return alerts, total

    def get_alert_summary(self) -> AlertSummary:
        """Get alert summary."""
        self._ensure_mock_data()

        alerts = list(self.alerts.values())
        unacknowledged = [a for a in alerts if not a.acknowledged and not a.resolved_at]

        by_level = {}
        for level in AlertLevel:
            by_level[level.value] = len([a for a in alerts if a.level == level])

        recent = sorted(alerts, key=lambda x: x.created_at, reverse=True)[:5]

        return AlertSummary(
            total_alerts=len(alerts),
            unacknowledged=len(unacknowledged),
            by_level=by_level,
            recent_alerts=recent,
        )

    def create_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        source: str,
    ) -> SystemAlert:
        """Create a system alert."""
        alert_id = self._generate_id("alert")

        alert = SystemAlert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            source=source,
        )

        self.alerts[alert_id] = alert
        return alert

    def acknowledge_alert(self, alert_id: str, admin_id: str) -> Optional[SystemAlert]:
        """Acknowledge an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return None

        alert.acknowledged = True
        alert.acknowledged_by = admin_id
        alert.acknowledged_at = datetime.utcnow()

        return alert

    def resolve_alert(self, alert_id: str) -> Optional[SystemAlert]:
        """Resolve an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return None

        alert.resolved_at = datetime.utcnow()
        return alert

    # Admin Activity

    def log_admin_activity(
        self,
        admin_id: str,
        admin_name: str,
        action: str,
        target_type: str,
        target_id: Optional[str] = None,
        target_name: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> AdminActivity:
        """Log admin activity."""
        activity = AdminActivity(
            id=self._generate_id("activity"),
            admin_id=admin_id,
            admin_name=admin_name,
            action=action,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            details=details or {},
            ip_address=ip_address,
        )

        self.admin_activities.append(activity)
        return activity

    def get_admin_activities(
        self,
        admin_id: Optional[str] = None,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AdminActivity], int]:
        """Get admin activities."""
        activities = self.admin_activities.copy()

        if admin_id:
            activities = [a for a in activities if a.admin_id == admin_id]
        if action:
            activities = [a for a in activities if a.action == action]

        activities.sort(key=lambda x: x.created_at, reverse=True)
        total = len(activities)
        activities = activities[skip:skip + limit]

        return activities, total

    def get_recent_activity(self) -> RecentActivity:
        """Get recent activity summary."""
        admin_activities, _ = self.get_admin_activities(limit=10)

        # Simulated user activities
        user_activities = [
            {"user": "john@example.com", "action": "created dashboard", "target": "Sales Overview", "time": "5m ago"},
            {"user": "jane@example.com", "action": "shared chart", "target": "Revenue Trends", "time": "12m ago"},
            {"user": "bob@example.com", "action": "connected database", "target": "Production DB", "time": "25m ago"},
        ]

        # Simulated system events
        system_events = [
            {"event": "backup_completed", "message": "Daily backup completed successfully", "time": "1h ago"},
            {"event": "cache_cleared", "message": "Cache cleared by admin", "time": "2h ago"},
        ]

        return RecentActivity(
            user_activities=user_activities,
            admin_activities=admin_activities,
            system_events=system_events,
        )

    # System Configuration

    def get_system_config(self) -> SystemConfig:
        """Get system configuration."""
        return self.config

    def update_system_config(self, data: SystemConfigUpdate, admin_id: str) -> SystemConfig:
        """Update system configuration."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(self.config, field, value)

        # Log the config change
        self.log_admin_activity(
            admin_id=admin_id,
            admin_name="Admin",  # Would look up actual name
            action="update_config",
            target_type="system_config",
            details={"updated_fields": list(update_data.keys())},
        )

        return self.config

    # Dashboard Configuration

    def get_dashboard_config(self, admin_id: str) -> AdminDashboardConfig:
        """Get dashboard configuration for admin."""
        if admin_id not in self.dashboard_configs:
            self.dashboard_configs[admin_id] = AdminDashboardConfig(
                widgets=DEFAULT_DASHBOARD_WIDGETS,
            )
        return self.dashboard_configs[admin_id]

    def update_dashboard_config(self, admin_id: str, config: AdminDashboardConfig) -> AdminDashboardConfig:
        """Update dashboard configuration."""
        self.dashboard_configs[admin_id] = config
        return config

    # Dashboard Summary

    def get_dashboard_summary(self) -> AdminDashboardSummary:
        """Get complete admin dashboard summary."""
        return AdminDashboardSummary(
            system_health=self.get_system_health(),
            resource_usage=self.get_resource_usage(),
            key_metrics=self.get_key_metrics(),
            user_stats=self.get_user_stats(),
            workspace_stats=self.get_workspace_stats(),
            revenue_stats=self.get_revenue_stats(),
            subscription_stats=self.get_subscription_stats(),
            usage_stats=self.get_platform_usage_stats(),
            alert_summary=self.get_alert_summary(),
            recent_activity=self.get_recent_activity(),
        )

    # Quick Actions

    def get_quick_actions(self) -> list[QuickAction]:
        """Get available quick actions."""
        return QUICK_ACTIONS

    def execute_quick_action(self, action_id: str, admin_id: str, parameters: Optional[dict] = None) -> QuickActionResult:
        """Execute a quick action."""
        action = next((a for a in QUICK_ACTIONS if a.id == action_id), None)
        if not action:
            return QuickActionResult(
                success=False,
                message="Action not found",
            )

        # Log the action
        self.log_admin_activity(
            admin_id=admin_id,
            admin_name="Admin",
            action=f"quick_action_{action_id}",
            target_type="system",
            details=parameters or {},
        )

        # Execute action (simplified)
        if action_id == "clear_cache":
            return QuickActionResult(
                success=True,
                message="Cache cleared successfully",
                details={"entries_cleared": 1250},
            )
        elif action_id == "enable_maintenance":
            self.config.maintenance_mode = True
            return QuickActionResult(
                success=True,
                message="Maintenance mode enabled",
            )
        elif action_id == "export_users":
            return QuickActionResult(
                success=True,
                message="User export started",
                details={"job_id": self._generate_id("job")},
            )

        return QuickActionResult(
            success=True,
            message=f"Action '{action.name}' executed",
        )

    # Reports

    def generate_report(
        self,
        report_type: str,
        name: str,
        format: str,
        time_range: TimeRange,
        admin_id: str,
        parameters: Optional[dict] = None,
    ) -> AdminReport:
        """Generate an admin report."""
        report_id = self._generate_id("report")

        report = AdminReport(
            id=report_id,
            name=name,
            type=report_type,
            format=format,
            time_range=time_range,
            generated_at=datetime.utcnow(),
            generated_by=admin_id,
            download_url=f"/api/v1/admin/reports/{report_id}/download",
            expires_at=datetime.utcnow() + timedelta(days=7),
            parameters=parameters or {},
        )

        self.reports[report_id] = report
        return report

    def get_reports(
        self,
        report_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AdminReport], int]:
        """Get generated reports."""
        reports = list(self.reports.values())

        if report_type:
            reports = [r for r in reports if r.type == report_type]

        reports.sort(key=lambda x: x.generated_at, reverse=True)
        total = len(reports)
        reports = reports[skip:skip + limit]

        return reports, total


# Global service instance
admin_dashboard_service = AdminDashboardService()
