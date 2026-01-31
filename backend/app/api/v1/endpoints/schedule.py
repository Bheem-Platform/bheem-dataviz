"""
Schedule and Alert API Endpoints

Provides endpoints for managing data refresh schedules and alerts.
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.schemas.schedule import (
    ScheduleStatus,
    AlertSeverity,
    RefreshSchedule,
    AlertRule,
    ScheduleExecution,
    AlertExecution,
    ScheduleSummary,
    AlertSummary,
    SCHEDULE_TEMPLATES,
    ALERT_TEMPLATES,
)
from app.services.schedule_service import get_schedule_service

router = APIRouter()

# Get shared service instance
_service = get_schedule_service()


# Refresh Schedules

@router.get("/schedules", response_model=list[RefreshSchedule])
async def list_schedules(
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    target_id: Optional[str] = Query(None, description="Filter by target ID"),
    status: Optional[ScheduleStatus] = Query(None, description="Filter by status"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all refresh schedules"""
    return _service.list_schedules(
        target_type=target_type,
        target_id=target_id,
        status=status,
    )


@router.post("/schedules", response_model=RefreshSchedule)
async def create_schedule(
    schedule: RefreshSchedule,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new refresh schedule"""
    schedule.created_by = current_user.id
    return _service.create_schedule(schedule)


@router.get("/schedules/{schedule_id}", response_model=RefreshSchedule)
async def get_schedule(
    schedule_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get a specific schedule"""
    schedule = _service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.put("/schedules/{schedule_id}", response_model=RefreshSchedule)
async def update_schedule(
    schedule_id: str,
    schedule: RefreshSchedule,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update a schedule"""
    try:
        return _service.update_schedule(schedule_id, schedule)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Delete a schedule"""
    if not _service.delete_schedule(schedule_id):
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"success": True, "message": "Schedule deleted"}


@router.post("/schedules/{schedule_id}/pause")
async def pause_schedule(
    schedule_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Pause a schedule"""
    if not _service.pause_schedule(schedule_id):
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"success": True, "message": "Schedule paused"}


@router.post("/schedules/{schedule_id}/resume")
async def resume_schedule(
    schedule_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Resume a paused schedule"""
    if not _service.resume_schedule(schedule_id):
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"success": True, "message": "Schedule resumed"}


@router.post("/schedules/{schedule_id}/run")
async def run_schedule_now(
    schedule_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Trigger a schedule to run immediately"""
    schedule = _service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Record manual execution start
    execution = _service.record_execution(
        schedule_id=schedule_id,
        status="running",
        started_at=datetime.utcnow(),
        triggered_by="manual",
    )

    # In production, this would trigger the actual refresh task
    # For now, we just record the execution
    return {
        "success": True,
        "message": "Schedule triggered",
        "execution_id": execution.id,
    }


@router.get("/schedules/{schedule_id}/history", response_model=list[ScheduleExecution])
async def get_schedule_history(
    schedule_id: str,
    limit: int = Query(50, le=100),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get execution history for a schedule"""
    return _service.get_execution_history(schedule_id=schedule_id, limit=limit)


# Alerts

@router.get("/alerts", response_model=list[AlertRule])
async def list_alerts(
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    target_id: Optional[str] = Query(None, description="Filter by target ID"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all alert rules"""
    return _service.list_alerts(
        target_type=target_type,
        target_id=target_id,
        severity=severity,
    )


@router.post("/alerts", response_model=AlertRule)
async def create_alert(
    alert: AlertRule,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new alert rule"""
    alert.created_by = current_user.id
    return _service.create_alert(alert)


@router.get("/alerts/{alert_id}", response_model=AlertRule)
async def get_alert(
    alert_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get a specific alert"""
    alert = _service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/alerts/{alert_id}", response_model=AlertRule)
async def update_alert(
    alert_id: str,
    alert: AlertRule,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update an alert"""
    try:
        return _service.update_alert(alert_id, alert)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Delete an alert"""
    if not _service.delete_alert(alert_id):
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "message": "Alert deleted"}


@router.put("/alerts/{alert_id}/toggle")
async def toggle_alert(
    alert_id: str,
    enabled: bool,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Enable or disable an alert"""
    alert = _service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.enabled = enabled
    _service.update_alert(alert_id, alert)
    return {"success": True, "enabled": enabled}


@router.post("/alerts/{alert_id}/snooze")
async def snooze_alert(
    alert_id: str,
    hours: int = Query(1, ge=1, le=168, description="Hours to snooze"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Snooze an alert for a specified number of hours"""
    from datetime import timedelta

    until = datetime.utcnow() + timedelta(hours=hours)
    if not _service.snooze_alert(alert_id, until):
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"success": True, "snoozed_until": until.isoformat()}


@router.post("/alerts/{alert_id}/evaluate")
async def evaluate_alert_now(
    alert_id: str,
    values: dict[str, float],
    previous_values: Optional[dict[str, float]] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Manually evaluate an alert with provided values"""
    alert = _service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    execution = _service.evaluate_alert(alert, values, previous_values)
    return {
        "triggered": execution.triggered,
        "condition_results": execution.condition_results,
        "execution_id": execution.id,
    }


@router.get("/alerts/{alert_id}/history", response_model=list[AlertExecution])
async def get_alert_history(
    alert_id: str,
    triggered_only: bool = Query(False, description="Only show triggered alerts"),
    limit: int = Query(50, le=100),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get evaluation history for an alert"""
    return _service.get_alert_history(
        alert_id=alert_id,
        triggered_only=triggered_only,
        limit=limit,
    )


# Summaries

@router.get("/summary/schedules", response_model=ScheduleSummary)
async def get_schedule_summary(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get summary of schedule activity"""
    return _service.get_schedule_summary()


@router.get("/summary/alerts", response_model=AlertSummary)
async def get_alert_summary(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get summary of alert activity"""
    return _service.get_alert_summary()


# Templates

@router.get("/templates/schedules")
async def get_schedule_templates(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get available schedule templates"""
    return SCHEDULE_TEMPLATES


@router.get("/templates/alerts")
async def get_alert_templates(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get available alert templates"""
    return ALERT_TEMPLATES


# Execution History (all)

@router.get("/history/executions", response_model=list[ScheduleExecution])
async def get_all_schedule_executions(
    limit: int = Query(50, le=100),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get all schedule execution history"""
    return _service.get_execution_history(limit=limit)


@router.get("/history/alerts", response_model=list[AlertExecution])
async def get_all_alert_executions(
    triggered_only: bool = Query(False),
    limit: int = Query(50, le=100),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get all alert execution history"""
    return _service.get_alert_history(triggered_only=triggered_only, limit=limit)
