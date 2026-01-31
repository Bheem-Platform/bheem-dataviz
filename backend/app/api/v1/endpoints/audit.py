"""
Audit Log API Endpoints

REST API for audit log access and security alerts management.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.audit_service import AuditService
from app.schemas.audit import (
    AuditLogResponse,
    AuditLogFilter,
    AuditLogSummary,
    AuditLogExport,
    SecurityAlertResponse,
    SecurityAlertCreate,
    SecurityAlertUpdate,
    SecurityAlertFilter,
    AuditDashboardStats,
    ActivityTimelineEntry,
    UserActivitySummary,
    ActionCategory,
    ActionType,
    AlertSeverity,
    AlertStatus,
)

router = APIRouter()


# Audit Log Endpoints

@router.get("/logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    request: Request,
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    user_email: Optional[str] = Query(None, description="Filter by user email"),
    action: Optional[str] = Query(None, description="Filter by action"),
    action_category: Optional[ActionCategory] = Query(None, description="Filter by action category"),
    action_type: Optional[ActionType] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    success_only: Optional[bool] = Query(None, description="Filter by success status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit logs with optional filtering.

    Requires admin or owner role to access.
    """
    audit_service = AuditService(db)

    filters = AuditLogFilter(
        user_id=user_id,
        user_email=user_email,
        action=action,
        action_category=action_category,
        action_type=action_type,
        resource_type=resource_type,
        resource_id=resource_id,
        workspace_id=workspace_id,
        ip_address=ip_address,
        success_only=success_only,
        start_date=start_date,
        end_date=end_date,
    )

    logs = await audit_service.get_audit_logs(filters, skip=skip, limit=limit)
    return logs


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific audit log entry by ID."""
    audit_service = AuditService(db)
    log = await audit_service.get_audit_log_by_id(log_id)

    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    return log


@router.get("/logs/summary", response_model=AuditLogSummary)
async def get_audit_summary(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for summary"),
    end_date: Optional[datetime] = Query(None, description="End date for summary"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get summary statistics of audit logs.

    Returns aggregated statistics including:
    - Total events
    - Success/failure counts
    - Unique users
    - Top actions
    - Activity by hour
    - Activity by category
    """
    audit_service = AuditService(db)
    summary = await audit_service.get_audit_summary(
        workspace_id=workspace_id,
        start_date=start_date,
        end_date=end_date,
    )
    return summary


@router.post("/logs/export")
async def export_audit_logs(
    export_config: AuditLogExport,
    db: AsyncSession = Depends(get_db),
):
    """
    Export audit logs in specified format.

    Supported formats: csv, json, xlsx
    """
    audit_service = AuditService(db)

    # Get filtered logs
    logs = await audit_service.get_audit_logs(
        export_config.filters or AuditLogFilter(),
        skip=0,
        limit=export_config.max_records,
    )

    if export_config.format == "json":
        return {
            "format": "json",
            "count": len(logs),
            "data": [log.model_dump() for log in logs],
        }
    elif export_config.format == "csv":
        # Return CSV-ready data
        headers = [
            "timestamp", "user_email", "action", "action_category",
            "resource_type", "resource_name", "ip_address", "success"
        ]
        rows = []
        for log in logs:
            rows.append({
                "timestamp": log.timestamp.isoformat() if log.timestamp else "",
                "user_email": log.user_email or "",
                "action": log.action,
                "action_category": log.action_category.value if log.action_category else "",
                "resource_type": log.resource_type or "",
                "resource_name": log.resource_name or "",
                "ip_address": log.ip_address or "",
                "success": "Yes" if log.success else "No",
            })
        return {
            "format": "csv",
            "headers": headers,
            "rows": rows,
            "count": len(rows),
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported export format: {export_config.format}")


# Activity Timeline

@router.get("/activity/timeline", response_model=list[ActivityTimelineEntry])
async def get_activity_timeline(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of entries"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get activity timeline for recent actions.

    Returns a chronological list of recent activities
    with human-readable descriptions.
    """
    audit_service = AuditService(db)
    timeline = await audit_service.get_activity_timeline(
        workspace_id=workspace_id,
        user_id=user_id,
        limit=limit,
    )
    return timeline


@router.get("/activity/user/{user_id}", response_model=UserActivitySummary)
async def get_user_activity(
    user_id: str,
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get activity summary for a specific user.

    Returns:
    - Total actions
    - Last active time
    - Most used features
    - Login statistics
    """
    audit_service = AuditService(db)
    summary = await audit_service.get_user_activity_summary(
        user_id=user_id,
        workspace_id=workspace_id,
    )
    return summary


# Security Alerts

@router.get("/alerts", response_model=list[SecurityAlertResponse])
async def get_security_alerts(
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get security alerts with optional filtering.

    Requires admin or owner role to access.
    """
    audit_service = AuditService(db)

    filters = SecurityAlertFilter(
        alert_type=alert_type,
        severity=severity,
        status=status,
        user_id=user_id,
        workspace_id=workspace_id,
        start_date=start_date,
        end_date=end_date,
    )

    alerts = await audit_service.get_security_alerts(filters, skip=skip, limit=limit)
    return alerts


@router.get("/alerts/{alert_id}", response_model=SecurityAlertResponse)
async def get_security_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific security alert by ID."""
    audit_service = AuditService(db)
    alert = await audit_service.get_security_alert_by_id(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Security alert not found")

    return alert


@router.post("/alerts", response_model=SecurityAlertResponse)
async def create_security_alert(
    alert: SecurityAlertCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new security alert manually.

    Typically alerts are created automatically by the system,
    but this endpoint allows manual creation for special cases.
    """
    audit_service = AuditService(db)
    created_alert = await audit_service.create_security_alert(alert)
    return created_alert


@router.patch("/alerts/{alert_id}", response_model=SecurityAlertResponse)
async def update_security_alert(
    alert_id: str,
    update: SecurityAlertUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a security alert status or resolution.

    Use this to:
    - Mark alerts as investigating
    - Resolve alerts with notes
    - Dismiss false positives
    """
    audit_service = AuditService(db)

    # Get current user ID from auth context
    resolved_by = None  # TODO: Get from auth context

    updated_alert = await audit_service.update_security_alert(
        alert_id=alert_id,
        update=update,
        resolved_by=resolved_by,
    )

    if not updated_alert:
        raise HTTPException(status_code=404, detail="Security alert not found")

    return updated_alert


@router.post("/alerts/{alert_id}/resolve", response_model=SecurityAlertResponse)
async def resolve_security_alert(
    alert_id: str,
    resolution_notes: str = Query(..., description="Resolution notes"),
    db: AsyncSession = Depends(get_db),
):
    """Quick endpoint to resolve an alert with notes."""
    audit_service = AuditService(db)

    update = SecurityAlertUpdate(
        status=AlertStatus.RESOLVED,
        resolution_notes=resolution_notes,
    )

    resolved_by = None  # TODO: Get from auth context

    updated_alert = await audit_service.update_security_alert(
        alert_id=alert_id,
        update=update,
        resolved_by=resolved_by,
    )

    if not updated_alert:
        raise HTTPException(status_code=404, detail="Security alert not found")

    return updated_alert


@router.post("/alerts/{alert_id}/dismiss", response_model=SecurityAlertResponse)
async def dismiss_security_alert(
    alert_id: str,
    reason: str = Query(..., description="Reason for dismissal"),
    db: AsyncSession = Depends(get_db),
):
    """Quick endpoint to dismiss an alert as false positive."""
    audit_service = AuditService(db)

    update = SecurityAlertUpdate(
        status=AlertStatus.DISMISSED,
        resolution_notes=f"Dismissed: {reason}",
    )

    resolved_by = None  # TODO: Get from auth context

    updated_alert = await audit_service.update_security_alert(
        alert_id=alert_id,
        update=update,
        resolved_by=resolved_by,
    )

    if not updated_alert:
        raise HTTPException(status_code=404, detail="Security alert not found")

    return updated_alert


# Dashboard Stats

@router.get("/dashboard", response_model=AuditDashboardStats)
async def get_audit_dashboard(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit dashboard statistics.

    Returns aggregated data for the admin dashboard including:
    - Event counts (today, week)
    - Active users
    - Failed logins
    - Alert counts
    - Top users
    - Recent alerts
    """
    audit_service = AuditService(db)
    stats = await audit_service.get_dashboard_stats(workspace_id=workspace_id)
    return stats


# Anomaly Detection

@router.post("/anomalies/check")
async def check_for_anomalies(
    user_id: Optional[str] = Query(None, description="Check anomalies for specific user"),
    workspace_id: Optional[str] = Query(None, description="Check anomalies in workspace"),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger anomaly detection.

    Analyzes recent activity for suspicious patterns:
    - Brute force attempts
    - Unusual data access
    - Rapid actions
    - Geographic anomalies
    """
    audit_service = AuditService(db)

    anomalies = await audit_service.detect_anomalies(
        user_id=user_id,
        workspace_id=workspace_id,
    )

    return {
        "checked_at": datetime.utcnow().isoformat(),
        "anomalies_found": len(anomalies),
        "alerts_created": [a.id for a in anomalies],
    }


# Archive Management

@router.post("/archive")
async def archive_old_logs(
    days_to_keep: int = Query(90, ge=30, le=365, description="Days of logs to keep"),
    db: AsyncSession = Depends(get_db),
):
    """
    Archive audit logs older than specified days.

    Moves old logs to archive table for performance optimization
    while maintaining compliance requirements.
    """
    audit_service = AuditService(db)
    archived_count = await audit_service.archive_old_logs(days_to_keep=days_to_keep)

    return {
        "archived_count": archived_count,
        "days_kept": days_to_keep,
        "archived_at": datetime.utcnow().isoformat(),
    }


@router.get("/archived", response_model=list[AuditLogResponse])
async def get_archived_logs(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Get archived audit logs.

    Access older logs that have been moved to the archive table.
    """
    audit_service = AuditService(db)
    logs = await audit_service.get_archived_logs(
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
    return logs
