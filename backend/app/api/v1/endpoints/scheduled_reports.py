"""
Scheduled Reports API Endpoints

REST API for managing scheduled report automation including
schedules, executions, and delivery configurations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.schemas.scheduled_report import (
    ScheduleStatus, ExecutionStatus,
    ScheduledReport, ScheduledReportCreate, ScheduledReportUpdate, ScheduledReportListResponse,
    ReportExecution, ReportExecutionListResponse, ScheduleStats,
)
from app.services.scheduled_report_service import scheduled_report_service

router = APIRouter()


# Schedule CRUD Endpoints

@router.post("/", response_model=ScheduledReport, tags=["scheduled-reports"])
async def create_schedule(
    data: ScheduledReportCreate,
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Create a new scheduled report."""
    return scheduled_report_service.create_schedule(user_id, data, organization_id)


@router.get("/", response_model=ScheduledReportListResponse, tags=["scheduled-reports"])
async def list_schedules(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    status: Optional[ScheduleStatus] = Query(None),
    is_active: Optional[bool] = Query(None),
    source_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List scheduled reports with filtering."""
    return scheduled_report_service.list_schedules(
        user_id, organization_id, status, is_active,
        source_type, search, skip, limit
    )


@router.get("/due", response_model=list[ScheduledReport], tags=["scheduled-reports"])
async def get_due_schedules():
    """Get all schedules that are due to run."""
    return scheduled_report_service.get_due_schedules()


@router.get("/{schedule_id}", response_model=ScheduledReport, tags=["scheduled-reports"])
async def get_schedule(schedule_id: str):
    """Get schedule by ID."""
    schedule = scheduled_report_service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.patch("/{schedule_id}", response_model=ScheduledReport, tags=["scheduled-reports"])
async def update_schedule(
    schedule_id: str,
    data: ScheduledReportUpdate,
):
    """Update a scheduled report."""
    schedule = scheduled_report_service.update_schedule(schedule_id, data)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.delete("/{schedule_id}", tags=["scheduled-reports"])
async def delete_schedule(schedule_id: str):
    """Delete a scheduled report."""
    if scheduled_report_service.delete_schedule(schedule_id):
        return {"success": True, "message": "Schedule deleted"}
    raise HTTPException(status_code=404, detail="Schedule not found")


@router.post("/{schedule_id}/pause", response_model=ScheduledReport, tags=["scheduled-reports"])
async def pause_schedule(schedule_id: str):
    """Pause a scheduled report."""
    schedule = scheduled_report_service.pause_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.post("/{schedule_id}/resume", response_model=ScheduledReport, tags=["scheduled-reports"])
async def resume_schedule(schedule_id: str):
    """Resume a paused scheduled report."""
    schedule = scheduled_report_service.resume_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.post("/{schedule_id}/trigger", response_model=ReportExecution, tags=["scheduled-reports"])
async def trigger_execution(schedule_id: str):
    """Manually trigger a scheduled report execution."""
    execution = scheduled_report_service.trigger_execution(schedule_id, triggered_by="manual")
    if not execution:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return execution


# Execution Endpoints

@router.get("/executions/", response_model=ReportExecutionListResponse, tags=["report-executions"])
async def list_executions(
    schedule_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    status: Optional[ExecutionStatus] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List report executions with filtering."""
    return scheduled_report_service.list_executions(
        schedule_id, user_id, organization_id, status,
        from_date, to_date, skip, limit
    )


@router.get("/executions/{execution_id}", response_model=ReportExecution, tags=["report-executions"])
async def get_execution(execution_id: str):
    """Get execution by ID."""
    execution = scheduled_report_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.post("/executions/{execution_id}/cancel", tags=["report-executions"])
async def cancel_execution(execution_id: str):
    """Cancel a running execution."""
    if scheduled_report_service.cancel_execution(execution_id):
        return {"success": True, "message": "Execution cancelled"}
    raise HTTPException(status_code=400, detail="Cannot cancel execution (not found or already completed)")


@router.post("/executions/{execution_id}/retry", response_model=ReportExecution, tags=["report-executions"])
async def retry_execution(execution_id: str):
    """Retry a failed execution."""
    execution = scheduled_report_service.retry_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=400, detail="Cannot retry execution (not found or not failed)")
    return execution


# Processing Endpoints

@router.post("/process-due", response_model=list[ReportExecution], tags=["scheduled-reports"])
async def process_due_schedules():
    """Process all due schedules and trigger executions."""
    return scheduled_report_service.process_due_schedules()


# Statistics Endpoints

@router.get("/stats/{organization_id}", response_model=ScheduleStats, tags=["schedule-stats"])
async def get_schedule_stats(organization_id: str):
    """Get schedule statistics for organization."""
    return scheduled_report_service.get_stats(organization_id)
