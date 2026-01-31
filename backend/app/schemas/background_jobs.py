"""
Background Jobs Schemas

Pydantic schemas for job queue management, task scheduling, retry policies,
progress tracking, and job history.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"
    TIMEOUT = "timeout"


class JobPriority(str, Enum):
    """Job priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class JobType(str, Enum):
    """Types of background jobs"""
    QUERY_EXECUTION = "query_execution"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    REPORT_GENERATION = "report_generation"
    DASHBOARD_REFRESH = "dashboard_refresh"
    CACHE_WARMING = "cache_warming"
    SCHEMA_SYNC = "schema_sync"
    TRANSFORM_EXECUTION = "transform_execution"
    ALERT_CHECK = "alert_check"
    NOTIFICATION_SEND = "notification_send"
    CLEANUP = "cleanup"
    ANALYTICS = "analytics"
    CUSTOM = "custom"


class ScheduleType(str, Enum):
    """Types of job schedules"""
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RetryStrategy(str, Enum):
    """Retry strategies for failed jobs"""
    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


class WorkerStatus(str, Enum):
    """Worker status"""
    IDLE = "idle"
    BUSY = "busy"
    PAUSED = "paused"
    OFFLINE = "offline"


# Job Models

class JobCreate(BaseModel):
    """Create a new job"""
    name: str
    job_type: JobType
    priority: JobPriority = JobPriority.NORMAL
    payload: dict[str, Any] = Field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    timeout_seconds: int = 3600
    retry_policy_id: Optional[str] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Job(BaseModel):
    """Background job"""
    id: str
    name: str
    job_type: JobType
    status: JobStatus
    priority: JobPriority
    payload: dict[str, Any]
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[dict[str, Any]] = None
    progress: float = 0.0  # 0-100
    progress_message: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_seconds: int
    retry_count: int = 0
    max_retries: int = 0
    retry_policy_id: Optional[str] = None
    worker_id: Optional[str] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class JobUpdate(BaseModel):
    """Update job fields"""
    status: Optional[JobStatus] = None
    priority: Optional[JobPriority] = None
    progress: Optional[float] = None
    progress_message: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    tags: Optional[list[str]] = None


class JobProgress(BaseModel):
    """Job progress update"""
    job_id: str
    progress: float
    message: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class JobResult(BaseModel):
    """Job execution result"""
    job_id: str
    status: JobStatus
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[dict[str, Any]] = None
    execution_time_ms: float
    completed_at: datetime


# Schedule Models

class ScheduleCreate(BaseModel):
    """Create a scheduled job"""
    name: str
    description: Optional[str] = None
    job_type: JobType
    schedule_type: ScheduleType
    schedule_config: dict[str, Any]  # cron expression, interval, etc.
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: JobPriority = JobPriority.NORMAL
    timeout_seconds: int = 3600
    retry_policy_id: Optional[str] = None
    enabled: bool = True
    workspace_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class Schedule(BaseModel):
    """Scheduled job definition"""
    id: str
    name: str
    description: Optional[str] = None
    job_type: JobType
    schedule_type: ScheduleType
    schedule_config: dict[str, Any]
    payload: dict[str, Any]
    priority: JobPriority
    timeout_seconds: int
    retry_policy_id: Optional[str] = None
    enabled: bool
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    last_run_status: Optional[JobStatus] = None
    run_count: int = 0
    failure_count: int = 0
    workspace_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ScheduleUpdate(BaseModel):
    """Update schedule fields"""
    name: Optional[str] = None
    description: Optional[str] = None
    schedule_type: Optional[ScheduleType] = None
    schedule_config: Optional[dict[str, Any]] = None
    payload: Optional[dict[str, Any]] = None
    priority: Optional[JobPriority] = None
    timeout_seconds: Optional[int] = None
    retry_policy_id: Optional[str] = None
    enabled: Optional[bool] = None
    tags: Optional[list[str]] = None


class ScheduleRun(BaseModel):
    """Record of a scheduled job run"""
    id: str
    schedule_id: str
    job_id: str
    status: JobStatus
    scheduled_time: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None


# Retry Policy Models

class RetryPolicyCreate(BaseModel):
    """Create retry policy"""
    name: str
    description: Optional[str] = None
    strategy: RetryStrategy
    max_retries: int = 3
    initial_delay_seconds: int = 60
    max_delay_seconds: int = 3600
    multiplier: float = 2.0  # For exponential backoff
    retry_on_statuses: list[str] = Field(default_factory=lambda: ["failed", "timeout"])
    retry_on_errors: list[str] = Field(default_factory=list)  # Error code patterns


class RetryPolicy(BaseModel):
    """Retry policy definition"""
    id: str
    name: str
    description: Optional[str] = None
    strategy: RetryStrategy
    max_retries: int
    initial_delay_seconds: int
    max_delay_seconds: int
    multiplier: float
    retry_on_statuses: list[str]
    retry_on_errors: list[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RetryPolicyUpdate(BaseModel):
    """Update retry policy"""
    name: Optional[str] = None
    description: Optional[str] = None
    strategy: Optional[RetryStrategy] = None
    max_retries: Optional[int] = None
    initial_delay_seconds: Optional[int] = None
    max_delay_seconds: Optional[int] = None
    multiplier: Optional[float] = None
    retry_on_statuses: Optional[list[str]] = None
    retry_on_errors: Optional[list[str]] = None


# Worker Models

class Worker(BaseModel):
    """Background job worker"""
    id: str
    name: str
    hostname: str
    status: WorkerStatus
    current_job_id: Optional[str] = None
    job_types: list[JobType]
    max_concurrent_jobs: int = 1
    jobs_processed: int = 0
    jobs_failed: int = 0
    last_heartbeat: datetime
    started_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkerHeartbeat(BaseModel):
    """Worker heartbeat update"""
    worker_id: str
    status: WorkerStatus
    current_job_id: Optional[str] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


# Queue Models

class QueueStats(BaseModel):
    """Job queue statistics"""
    name: str
    pending_count: int
    running_count: int
    completed_count: int
    failed_count: int
    avg_wait_time_ms: float
    avg_execution_time_ms: float
    throughput_per_minute: float
    oldest_pending_age_seconds: float


class QueueConfig(BaseModel):
    """Queue configuration"""
    name: str
    job_types: list[JobType]
    max_workers: int = 4
    max_queue_size: int = 10000
    default_timeout_seconds: int = 3600
    default_priority: JobPriority = JobPriority.NORMAL
    rate_limit_per_minute: Optional[int] = None


# Job History Models

class JobHistoryEntry(BaseModel):
    """Job history entry"""
    id: str
    job_id: str
    job_name: str
    job_type: JobType
    status: JobStatus
    priority: JobPriority
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    execution_time_ms: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: datetime
    tags: list[str] = Field(default_factory=list)


class JobHistoryStats(BaseModel):
    """Job history statistics"""
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    cancelled_jobs: int
    avg_execution_time_ms: float
    total_execution_time_ms: float
    success_rate: float
    by_type: dict[str, int]
    by_status: dict[str, int]
    by_hour: list[dict[str, Any]]
    slowest_jobs: list[JobHistoryEntry]


# Response Models

class JobListResponse(BaseModel):
    """List jobs response"""
    jobs: list[Job]
    total: int


class ScheduleListResponse(BaseModel):
    """List schedules response"""
    schedules: list[Schedule]
    total: int


class RetryPolicyListResponse(BaseModel):
    """List retry policies response"""
    policies: list[RetryPolicy]
    total: int


class WorkerListResponse(BaseModel):
    """List workers response"""
    workers: list[Worker]
    total: int


class JobHistoryListResponse(BaseModel):
    """List job history response"""
    entries: list[JobHistoryEntry]
    total: int


class ScheduleRunListResponse(BaseModel):
    """List schedule runs response"""
    runs: list[ScheduleRun]
    total: int


# Dashboard Models

class JobsDashboard(BaseModel):
    """Jobs dashboard summary"""
    active_jobs: int
    pending_jobs: int
    completed_today: int
    failed_today: int
    success_rate: float
    avg_wait_time_ms: float
    avg_execution_time_ms: float
    active_workers: int
    total_workers: int
    queues: list[QueueStats]
    recent_failures: list[Job]


# Configuration

class JobsConfig(BaseModel):
    """Background jobs configuration"""
    enabled: bool = True
    max_workers: int = 4
    default_timeout_seconds: int = 3600
    max_retry_attempts: int = 3
    cleanup_completed_after_hours: int = 168  # 1 week
    cleanup_failed_after_hours: int = 720  # 30 days
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 100


class JobsConfigUpdate(BaseModel):
    """Update jobs configuration"""
    enabled: Optional[bool] = None
    max_workers: Optional[int] = None
    default_timeout_seconds: Optional[int] = None
    max_retry_attempts: Optional[int] = None
    cleanup_completed_after_hours: Optional[int] = None
    cleanup_failed_after_hours: Optional[int] = None
    rate_limit_enabled: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = None


# Constants

JOB_TYPE_LABELS = {
    JobType.QUERY_EXECUTION: "Query Execution",
    JobType.DATA_EXPORT: "Data Export",
    JobType.DATA_IMPORT: "Data Import",
    JobType.REPORT_GENERATION: "Report Generation",
    JobType.DASHBOARD_REFRESH: "Dashboard Refresh",
    JobType.CACHE_WARMING: "Cache Warming",
    JobType.SCHEMA_SYNC: "Schema Sync",
    JobType.TRANSFORM_EXECUTION: "Transform Execution",
    JobType.ALERT_CHECK: "Alert Check",
    JobType.NOTIFICATION_SEND: "Notification Send",
    JobType.CLEANUP: "Cleanup",
    JobType.ANALYTICS: "Analytics",
    JobType.CUSTOM: "Custom",
}

JOB_STATUS_LABELS = {
    JobStatus.PENDING: "Pending",
    JobStatus.QUEUED: "Queued",
    JobStatus.RUNNING: "Running",
    JobStatus.COMPLETED: "Completed",
    JobStatus.FAILED: "Failed",
    JobStatus.CANCELLED: "Cancelled",
    JobStatus.RETRY: "Retry",
    JobStatus.TIMEOUT: "Timeout",
}

PRIORITY_ORDER = {
    JobPriority.CRITICAL: 0,
    JobPriority.HIGH: 1,
    JobPriority.NORMAL: 2,
    JobPriority.LOW: 3,
}


# Helper Functions

def calculate_next_retry_delay(
    retry_count: int,
    policy: RetryPolicy,
) -> int:
    """Calculate delay before next retry."""
    if policy.strategy == RetryStrategy.NONE:
        return 0
    elif policy.strategy == RetryStrategy.FIXED:
        delay = policy.initial_delay_seconds
    elif policy.strategy == RetryStrategy.LINEAR:
        delay = policy.initial_delay_seconds * (retry_count + 1)
    else:  # exponential
        delay = policy.initial_delay_seconds * (policy.multiplier ** retry_count)

    return min(int(delay), policy.max_delay_seconds)


def parse_cron_expression(cron: str) -> dict[str, Any]:
    """Parse cron expression into components."""
    parts = cron.split()
    if len(parts) != 5:
        raise ValueError("Invalid cron expression: expected 5 parts")

    return {
        "minute": parts[0],
        "hour": parts[1],
        "day_of_month": parts[2],
        "month": parts[3],
        "day_of_week": parts[4],
    }


def get_priority_order(priority: JobPriority) -> int:
    """Get numeric order for priority sorting."""
    return PRIORITY_ORDER.get(priority, 2)


def is_terminal_status(status: JobStatus) -> bool:
    """Check if job status is terminal (won't change)."""
    return status in [
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.CANCELLED,
    ]


def can_retry(job: Job, policy: Optional[RetryPolicy]) -> bool:
    """Check if job can be retried."""
    if not policy or policy.strategy == RetryStrategy.NONE:
        return False
    if job.retry_count >= policy.max_retries:
        return False
    if job.status.value not in policy.retry_on_statuses:
        return False
    return True
