"""
Background Jobs API Endpoints

Endpoints for job queue management, task scheduling, retry policies,
progress tracking, and job history.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.schemas.background_jobs import (
    Job,
    JobCreate,
    JobUpdate,
    JobStatus,
    JobPriority,
    JobType,
    JobProgress,
    JobResult,
    JobListResponse,
    JobHistoryListResponse,
    JobHistoryStats,
    Schedule,
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleListResponse,
    ScheduleRunListResponse,
    RetryPolicy,
    RetryPolicyCreate,
    RetryPolicyUpdate,
    RetryPolicyListResponse,
    Worker,
    WorkerStatus,
    WorkerHeartbeat,
    WorkerListResponse,
    QueueStats,
    JobsDashboard,
    JobsConfig,
    JobsConfigUpdate,
)
from app.services.background_jobs_service import background_jobs_service

router = APIRouter()


# Job Endpoints

@router.post("/jobs", response_model=Job)
async def create_job(data: JobCreate):
    """Create a new background job."""
    job = await background_jobs_service.create_job(data)
    return job


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    status: Optional[JobStatus] = None,
    job_type: Optional[JobType] = None,
    priority: Optional[JobPriority] = None,
    workspace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List jobs with filters."""
    tag_list = tags.split(",") if tags else None
    jobs = await background_jobs_service.list_jobs(
        status=status,
        job_type=job_type,
        priority=priority,
        workspace_id=workspace_id,
        user_id=user_id,
        tags=tag_list,
        limit=limit,
        offset=offset,
    )
    return jobs


@router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get job by ID."""
    job = await background_jobs_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/jobs/{job_id}", response_model=Job)
async def update_job(job_id: str, update: JobUpdate):
    """Update job fields."""
    job = await background_jobs_service.update_job(job_id, update)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job."""
    deleted = await background_jobs_service.delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted"}


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a pending or running job."""
    cancelled = await background_jobs_service.cancel_job(job_id)
    if not cancelled:
        raise HTTPException(status_code=400, detail="Cannot cancel job")
    return {"message": "Job cancelled"}


@router.post("/jobs/{job_id}/retry", response_model=Job)
async def retry_job(job_id: str):
    """Retry a failed job."""
    job = await background_jobs_service.retry_job(job_id)
    if not job:
        raise HTTPException(status_code=400, detail="Cannot retry job")
    return job


# Job Progress Endpoints

@router.post("/jobs/{job_id}/progress", response_model=Job)
async def update_job_progress(job_id: str, progress: float, message: Optional[str] = None):
    """Update job progress."""
    job = await background_jobs_service.update_progress(
        JobProgress(job_id=job_id, progress=progress, message=message)
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/jobs/{job_id}/start", response_model=Job)
async def start_job(job_id: str, worker_id: str):
    """Mark job as started."""
    job = await background_jobs_service.start_job(job_id, worker_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/jobs/{job_id}/complete", response_model=Job)
async def complete_job(job_id: str, result: JobResult):
    """Mark job as completed."""
    result.job_id = job_id
    job = await background_jobs_service.complete_job(result)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# Schedule Endpoints

@router.post("/schedules", response_model=Schedule)
async def create_schedule(data: ScheduleCreate):
    """Create a scheduled job."""
    schedule = await background_jobs_service.create_schedule(data)
    return schedule


@router.get("/schedules", response_model=ScheduleListResponse)
async def list_schedules(
    job_type: Optional[JobType] = None,
    enabled: Optional[bool] = None,
    workspace_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List schedules."""
    schedules = await background_jobs_service.list_schedules(
        job_type=job_type,
        enabled=enabled,
        workspace_id=workspace_id,
        limit=limit,
        offset=offset,
    )
    return schedules


@router.get("/schedules/{schedule_id}", response_model=Schedule)
async def get_schedule(schedule_id: str):
    """Get schedule by ID."""
    schedule = await background_jobs_service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.patch("/schedules/{schedule_id}", response_model=Schedule)
async def update_schedule(schedule_id: str, update: ScheduleUpdate):
    """Update schedule fields."""
    schedule = await background_jobs_service.update_schedule(schedule_id, update)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """Delete a schedule."""
    deleted = await background_jobs_service.delete_schedule(schedule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted"}


@router.post("/schedules/{schedule_id}/run", response_model=Job)
async def run_schedule_now(schedule_id: str):
    """Trigger a scheduled job immediately."""
    job = await background_jobs_service.run_schedule_now(schedule_id)
    if not job:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return job


@router.post("/schedules/{schedule_id}/enable")
async def enable_schedule(schedule_id: str):
    """Enable a schedule."""
    schedule = await background_jobs_service.update_schedule(
        schedule_id,
        ScheduleUpdate(enabled=True),
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule enabled"}


@router.post("/schedules/{schedule_id}/disable")
async def disable_schedule(schedule_id: str):
    """Disable a schedule."""
    schedule = await background_jobs_service.update_schedule(
        schedule_id,
        ScheduleUpdate(enabled=False),
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule disabled"}


@router.get("/schedules/{schedule_id}/runs", response_model=ScheduleRunListResponse)
async def get_schedule_runs(schedule_id: str, limit: int = Query(50, ge=1, le=200)):
    """Get schedule run history."""
    runs = await background_jobs_service.get_schedule_runs(schedule_id, limit)
    return runs


# Retry Policy Endpoints

@router.post("/retry-policies", response_model=RetryPolicy)
async def create_retry_policy(data: RetryPolicyCreate):
    """Create a retry policy."""
    policy = await background_jobs_service.create_retry_policy(data)
    return policy


@router.get("/retry-policies", response_model=RetryPolicyListResponse)
async def list_retry_policies():
    """List all retry policies."""
    policies = await background_jobs_service.list_retry_policies()
    return policies


@router.get("/retry-policies/{policy_id}", response_model=RetryPolicy)
async def get_retry_policy(policy_id: str):
    """Get retry policy by ID."""
    policy = await background_jobs_service.get_retry_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Retry policy not found")
    return policy


@router.patch("/retry-policies/{policy_id}", response_model=RetryPolicy)
async def update_retry_policy(policy_id: str, update: RetryPolicyUpdate):
    """Update retry policy."""
    policy = await background_jobs_service.update_retry_policy(policy_id, update)
    if not policy:
        raise HTTPException(status_code=404, detail="Retry policy not found")
    return policy


@router.delete("/retry-policies/{policy_id}")
async def delete_retry_policy(policy_id: str):
    """Delete a retry policy."""
    deleted = await background_jobs_service.delete_retry_policy(policy_id)
    if not deleted:
        raise HTTPException(status_code=400, detail="Cannot delete retry policy")
    return {"message": "Retry policy deleted"}


# Worker Endpoints

@router.post("/workers/register", response_model=Worker)
async def register_worker(
    name: str,
    hostname: str,
    job_types: str = Query(..., description="Comma-separated job types"),
    max_concurrent_jobs: int = 1,
):
    """Register a new worker."""
    types = [JobType(t.strip()) for t in job_types.split(",")]
    worker = await background_jobs_service.register_worker(
        name=name,
        hostname=hostname,
        job_types=types,
        max_concurrent_jobs=max_concurrent_jobs,
    )
    return worker


@router.get("/workers", response_model=WorkerListResponse)
async def list_workers(status: Optional[WorkerStatus] = None):
    """List workers."""
    workers = await background_jobs_service.list_workers(status)
    return workers


@router.post("/workers/{worker_id}/heartbeat", response_model=Worker)
async def worker_heartbeat(
    worker_id: str,
    status: WorkerStatus,
    current_job_id: Optional[str] = None,
    memory_usage_mb: Optional[float] = None,
    cpu_usage_percent: Optional[float] = None,
):
    """Update worker heartbeat."""
    heartbeat = WorkerHeartbeat(
        worker_id=worker_id,
        status=status,
        current_job_id=current_job_id,
        memory_usage_mb=memory_usage_mb,
        cpu_usage_percent=cpu_usage_percent,
    )
    worker = await background_jobs_service.worker_heartbeat(heartbeat)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.delete("/workers/{worker_id}")
async def unregister_worker(worker_id: str):
    """Unregister a worker."""
    deleted = await background_jobs_service.unregister_worker(worker_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Worker not found")
    return {"message": "Worker unregistered"}


@router.get("/workers/{worker_id}/next-job", response_model=Job)
async def get_next_job_for_worker(worker_id: str):
    """Get next job for a worker to process."""
    job = await background_jobs_service.get_next_job_for_worker(worker_id)
    if not job:
        raise HTTPException(status_code=404, detail="No jobs available")
    return job


# Job History Endpoints

@router.get("/history", response_model=JobHistoryListResponse)
async def get_job_history(
    job_type: Optional[JobType] = None,
    status: Optional[JobStatus] = None,
    workspace_id: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Get job execution history."""
    history = await background_jobs_service.get_job_history(
        job_type=job_type,
        status=status,
        workspace_id=workspace_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return history


@router.get("/history/stats", response_model=JobHistoryStats)
async def get_job_history_stats(
    workspace_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """Get job history statistics."""
    stats = await background_jobs_service.get_job_history_stats(
        workspace_id=workspace_id,
        start_date=start_date,
        end_date=end_date,
    )
    return stats


# Queue Endpoints

@router.get("/queues/{queue_name}/stats", response_model=QueueStats)
async def get_queue_stats(queue_name: str):
    """Get statistics for a job queue."""
    stats = await background_jobs_service.get_queue_stats(queue_name)
    if not stats:
        raise HTTPException(status_code=404, detail="Queue not found")
    return stats


@router.get("/queues/stats")
async def get_all_queue_stats():
    """Get statistics for all queues."""
    stats = await background_jobs_service.get_all_queue_stats()
    return {"queues": stats}


# Dashboard Endpoints

@router.get("/dashboard", response_model=JobsDashboard)
async def get_jobs_dashboard():
    """Get jobs dashboard summary."""
    dashboard = await background_jobs_service.get_dashboard()
    return dashboard


# Configuration Endpoints

@router.get("/config", response_model=JobsConfig)
async def get_jobs_config():
    """Get jobs configuration."""
    config = await background_jobs_service.get_config()
    return config


@router.put("/config", response_model=JobsConfig)
async def update_jobs_config(update: JobsConfigUpdate):
    """Update jobs configuration."""
    config = await background_jobs_service.update_config(update)
    return config


# Cleanup Endpoints

@router.post("/cleanup")
async def cleanup_old_jobs():
    """Clean up old completed/failed jobs."""
    count = await background_jobs_service.cleanup_old_jobs()
    return {"message": f"Cleaned up {count} jobs"}


# Bulk Operations

@router.post("/jobs/bulk/cancel")
async def bulk_cancel_jobs(job_ids: list[str]):
    """Cancel multiple jobs."""
    cancelled = 0
    for job_id in job_ids:
        if await background_jobs_service.cancel_job(job_id):
            cancelled += 1
    return {"cancelled": cancelled, "total": len(job_ids)}


@router.post("/jobs/bulk/retry")
async def bulk_retry_jobs(job_ids: list[str]):
    """Retry multiple failed jobs."""
    retried = 0
    for job_id in job_ids:
        if await background_jobs_service.retry_job(job_id):
            retried += 1
    return {"retried": retried, "total": len(job_ids)}


@router.delete("/jobs/bulk")
async def bulk_delete_jobs(job_ids: list[str]):
    """Delete multiple jobs."""
    deleted = 0
    for job_id in job_ids:
        if await background_jobs_service.delete_job(job_id):
            deleted += 1
    return {"deleted": deleted, "total": len(job_ids)}
