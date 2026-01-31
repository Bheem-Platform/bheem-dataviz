"""
Administration Dashboard API Endpoints

REST API for the admin dashboard, system health, statistics,
alerts, and administrative controls.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.admin_dashboard import (
    SystemHealthStatus, AlertLevel, TimeRange,
    MetricValue, MetricTimeSeries,
    SystemHealth, ResourceUsage,
    UserStats, SessionStats, WorkspaceStats,
    RevenueStats, SubscriptionStats, PlatformUsageStats,
    SystemAlert, AlertSummary, SystemAlertListResponse,
    AdminActivity, RecentActivity, AdminActivityListResponse,
    SystemConfig, SystemConfigUpdate,
    AdminDashboardSummary, DashboardWidget, AdminDashboardConfig,
    AdminReport, ReportSchedule, AdminReportListResponse,
    QuickAction, QuickActionResult,
)
from app.services.admin_dashboard_service import admin_dashboard_service

router = APIRouter()


# Dashboard Summary

@router.get("/dashboard", response_model=AdminDashboardSummary, tags=["dashboard"])
async def get_dashboard_summary():
    """Get complete admin dashboard summary."""
    return admin_dashboard_service.get_dashboard_summary()


@router.get("/dashboard/config", response_model=AdminDashboardConfig, tags=["dashboard"])
async def get_dashboard_config(
    admin_id: str = Query(..., description="Admin user ID"),
):
    """Get dashboard configuration for admin."""
    return admin_dashboard_service.get_dashboard_config(admin_id)


@router.put("/dashboard/config", response_model=AdminDashboardConfig, tags=["dashboard"])
async def update_dashboard_config(
    config: AdminDashboardConfig,
    admin_id: str = Query(..., description="Admin user ID"),
):
    """Update dashboard configuration."""
    return admin_dashboard_service.update_dashboard_config(admin_id, config)


# System Health

@router.get("/health", response_model=SystemHealth, tags=["health"])
async def get_system_health():
    """Get overall system health status."""
    return admin_dashboard_service.get_system_health()


@router.get("/resources", response_model=ResourceUsage, tags=["health"])
async def get_resource_usage():
    """Get current resource usage."""
    return admin_dashboard_service.get_resource_usage()


# Key Metrics

@router.get("/metrics", response_model=list[MetricValue], tags=["metrics"])
async def get_key_metrics():
    """Get key metrics for dashboard."""
    return admin_dashboard_service.get_key_metrics()


# Statistics

@router.get("/stats/users", response_model=UserStats, tags=["statistics"])
async def get_user_stats(
    time_range: TimeRange = TimeRange.LAST_30_DAYS,
):
    """Get user statistics."""
    return admin_dashboard_service.get_user_stats(time_range)


@router.get("/stats/sessions", response_model=SessionStats, tags=["statistics"])
async def get_session_stats():
    """Get session statistics."""
    return admin_dashboard_service.get_session_stats()


@router.get("/stats/workspaces", response_model=WorkspaceStats, tags=["statistics"])
async def get_workspace_stats(
    time_range: TimeRange = TimeRange.LAST_30_DAYS,
):
    """Get workspace statistics."""
    return admin_dashboard_service.get_workspace_stats(time_range)


@router.get("/stats/revenue", response_model=RevenueStats, tags=["statistics"])
async def get_revenue_stats(
    time_range: TimeRange = TimeRange.LAST_30_DAYS,
):
    """Get revenue statistics."""
    return admin_dashboard_service.get_revenue_stats(time_range)


@router.get("/stats/subscriptions", response_model=SubscriptionStats, tags=["statistics"])
async def get_subscription_stats():
    """Get subscription statistics."""
    return admin_dashboard_service.get_subscription_stats()


@router.get("/stats/usage", response_model=PlatformUsageStats, tags=["statistics"])
async def get_platform_usage_stats():
    """Get platform usage statistics."""
    return admin_dashboard_service.get_platform_usage_stats()


# Alerts

@router.get("/alerts", response_model=SystemAlertListResponse, tags=["alerts"])
async def list_alerts(
    level: Optional[AlertLevel] = None,
    acknowledged: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List system alerts."""
    alerts, total = admin_dashboard_service.get_alerts(level, acknowledged, skip, limit)
    return SystemAlertListResponse(alerts=alerts, total=total)


@router.get("/alerts/summary", response_model=AlertSummary, tags=["alerts"])
async def get_alert_summary():
    """Get alert summary."""
    return admin_dashboard_service.get_alert_summary()


@router.post("/alerts", response_model=SystemAlert, tags=["alerts"])
async def create_alert(
    level: AlertLevel = Query(...),
    title: str = Query(...),
    message: str = Query(...),
    source: str = Query("manual"),
):
    """Create a system alert."""
    return admin_dashboard_service.create_alert(level, title, message, source)


@router.post("/alerts/{alert_id}/acknowledge", response_model=SystemAlert, tags=["alerts"])
async def acknowledge_alert(
    alert_id: str,
    admin_id: str = Query(..., description="Admin acknowledging the alert"),
):
    """Acknowledge an alert."""
    alert = admin_dashboard_service.acknowledge_alert(alert_id, admin_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/resolve", response_model=SystemAlert, tags=["alerts"])
async def resolve_alert(alert_id: str):
    """Resolve an alert."""
    alert = admin_dashboard_service.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


# Admin Activity

@router.get("/activity", response_model=AdminActivityListResponse, tags=["activity"])
async def list_admin_activities(
    admin_id: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List admin activities."""
    activities, total = admin_dashboard_service.get_admin_activities(admin_id, action, skip, limit)
    return AdminActivityListResponse(activities=activities, total=total)


@router.get("/activity/recent", response_model=RecentActivity, tags=["activity"])
async def get_recent_activity():
    """Get recent activity summary."""
    return admin_dashboard_service.get_recent_activity()


@router.post("/activity/log", response_model=AdminActivity, tags=["activity"])
async def log_admin_activity(
    admin_id: str = Query(...),
    admin_name: str = Query(...),
    action: str = Query(...),
    target_type: str = Query(...),
    target_id: Optional[str] = Query(None),
    target_name: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
):
    """Log an admin activity."""
    return admin_dashboard_service.log_admin_activity(
        admin_id, admin_name, action, target_type, target_id, target_name, ip_address=ip_address
    )


# System Configuration

@router.get("/config", response_model=SystemConfig, tags=["configuration"])
async def get_system_config():
    """Get system configuration."""
    return admin_dashboard_service.get_system_config()


@router.put("/config", response_model=SystemConfig, tags=["configuration"])
async def update_system_config(
    data: SystemConfigUpdate,
    admin_id: str = Query(..., description="Admin making the change"),
):
    """Update system configuration."""
    return admin_dashboard_service.update_system_config(data, admin_id)


@router.post("/config/maintenance/enable", tags=["configuration"])
async def enable_maintenance_mode(
    message: Optional[str] = Query(None, description="Maintenance message"),
    admin_id: str = Query(...),
):
    """Enable maintenance mode."""
    config = admin_dashboard_service.update_system_config(
        SystemConfigUpdate(maintenance_mode=True, maintenance_message=message),
        admin_id,
    )
    return {"status": "enabled", "message": config.maintenance_message}


@router.post("/config/maintenance/disable", tags=["configuration"])
async def disable_maintenance_mode(admin_id: str = Query(...)):
    """Disable maintenance mode."""
    admin_dashboard_service.update_system_config(
        SystemConfigUpdate(maintenance_mode=False, maintenance_message=None),
        admin_id,
    )
    return {"status": "disabled"}


# Quick Actions

@router.get("/actions", response_model=list[QuickAction], tags=["quick-actions"])
async def get_quick_actions():
    """Get available quick actions."""
    return admin_dashboard_service.get_quick_actions()


@router.post("/actions/{action_id}/execute", response_model=QuickActionResult, tags=["quick-actions"])
async def execute_quick_action(
    action_id: str,
    admin_id: str = Query(..., description="Admin executing the action"),
    parameters: Optional[str] = Query(None, description="JSON parameters"),
):
    """Execute a quick action."""
    import json
    params = json.loads(parameters) if parameters else None
    return admin_dashboard_service.execute_quick_action(action_id, admin_id, params)


# Reports

@router.post("/reports", response_model=AdminReport, tags=["reports"])
async def generate_report(
    report_type: str = Query(..., description="Type: usage, revenue, growth, audit"),
    name: str = Query(...),
    format: str = Query("pdf", description="Format: pdf, csv, excel"),
    time_range: TimeRange = TimeRange.LAST_30_DAYS,
    admin_id: str = Query(...),
    parameters: Optional[str] = Query(None, description="JSON parameters"),
):
    """Generate an admin report."""
    import json
    params = json.loads(parameters) if parameters else None
    return admin_dashboard_service.generate_report(
        report_type, name, format, time_range, admin_id, params
    )


@router.get("/reports", response_model=AdminReportListResponse, tags=["reports"])
async def list_reports(
    report_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List generated reports."""
    reports, total = admin_dashboard_service.get_reports(report_type, skip, limit)
    return AdminReportListResponse(reports=reports, total=total)


@router.get("/reports/{report_id}/download", tags=["reports"])
async def download_report(report_id: str):
    """Download a generated report."""
    # In production, this would stream the file
    raise HTTPException(
        status_code=501,
        detail="Report download not implemented in demo mode",
    )
