"""
Background Jobs Service

Service for managing background jobs, task scheduling, retry policies,
progress tracking, and job history.
"""

import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional
from collections import defaultdict

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
    JobHistoryEntry,
    JobHistoryStats,
    JobHistoryListResponse,
    Schedule,
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleType,
    ScheduleRun,
    ScheduleListResponse,
    ScheduleRunListResponse,
    RetryPolicy,
    RetryPolicyCreate,
    RetryPolicyUpdate,
    RetryStrategy,
    RetryPolicyListResponse,
    Worker,
    WorkerStatus,
    WorkerHeartbeat,
    WorkerListResponse,
    QueueStats,
    QueueConfig,
    JobsDashboard,
    JobsConfig,
    JobsConfigUpdate,
    calculate_next_retry_delay,
    is_terminal_status,
    can_retry,
    get_priority_order,
)


class BackgroundJobsService:
    """Service for background job management."""

    def __init__(self):
        # In-memory stores (production would use Redis/database)
        self._jobs: dict[str, Job] = {}
        self._schedules: dict[str, Schedule] = {}
        self._schedule_runs: dict[str, list[ScheduleRun]] = defaultdict(list)
        self._retry_policies: dict[str, RetryPolicy] = {}
        self._workers: dict[str, Worker] = {}
        self._job_history: list[JobHistoryEntry] = []
        self._queues: dict[str, QueueConfig] = {}
        self._config = JobsConfig()

        # Initialize default retry policies
        self._init_default_policies()
        # Initialize default queues
        self._init_default_queues()

    def _init_default_policies(self):
        """Initialize default retry policies."""
        default_policy = RetryPolicy(
            id="default",
            name="Default Retry Policy",
            description="Exponential backoff with 3 retries",
            strategy=RetryStrategy.EXPONENTIAL,
            max_retries=3,
            initial_delay_seconds=60,
            max_delay_seconds=3600,
            multiplier=2.0,
            retry_on_statuses=["failed", "timeout"],
            retry_on_errors=[],
        )
        self._retry_policies["default"] = default_policy

        aggressive_policy = RetryPolicy(
            id="aggressive",
            name="Aggressive Retry Policy",
            description="Quick retries for transient failures",
            strategy=RetryStrategy.FIXED,
            max_retries=5,
            initial_delay_seconds=10,
            max_delay_seconds=300,
            multiplier=1.0,
            retry_on_statuses=["failed", "timeout"],
            retry_on_errors=["connection", "timeout"],
        )
        self._retry_policies["aggressive"] = aggressive_policy

    def _init_default_queues(self):
        """Initialize default job queues."""
        self._queues["default"] = QueueConfig(
            name="default",
            job_types=[JobType.CUSTOM],
            max_workers=4,
            max_queue_size=10000,
        )
        self._queues["high_priority"] = QueueConfig(
            name="high_priority",
            job_types=[JobType.ALERT_CHECK, JobType.NOTIFICATION_SEND],
            max_workers=2,
            max_queue_size=1000,
            default_priority=JobPriority.HIGH,
        )
        self._queues["heavy"] = QueueConfig(
            name="heavy",
            job_types=[JobType.DATA_EXPORT, JobType.DATA_IMPORT, JobType.REPORT_GENERATION],
            max_workers=2,
            max_queue_size=500,
            default_timeout_seconds=7200,
        )

    # Job Management

    async def create_job(self, data: JobCreate) -> Job:
        """Create a new background job."""
        job_id = str(uuid.uuid4())

        # Determine retry policy
        max_retries = 0
        retry_policy_id = data.retry_policy_id
        if retry_policy_id and retry_policy_id in self._retry_policies:
            max_retries = self._retry_policies[retry_policy_id].max_retries

        job = Job(
            id=job_id,
            name=data.name,
            job_type=data.job_type,
            status=JobStatus.PENDING,
            priority=data.priority,
            payload=data.payload,
            scheduled_at=data.scheduled_at,
            timeout_seconds=data.timeout_seconds,
            max_retries=max_retries,
            retry_policy_id=retry_policy_id,
            workspace_id=data.workspace_id,
            user_id=data.user_id,
            tags=data.tags,
            metadata=data.metadata,
        )

        self._jobs[job_id] = job
        return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self._jobs.get(job_id)

    async def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[JobType] = None,
        priority: Optional[JobPriority] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> JobListResponse:
        """List jobs with filters."""
        jobs = list(self._jobs.values())

        # Apply filters
        if status:
            jobs = [j for j in jobs if j.status == status]
        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]
        if priority:
            jobs = [j for j in jobs if j.priority == priority]
        if workspace_id:
            jobs = [j for j in jobs if j.workspace_id == workspace_id]
        if user_id:
            jobs = [j for j in jobs if j.user_id == user_id]
        if tags:
            jobs = [j for j in jobs if any(t in j.tags for t in tags)]

        # Sort by priority then creation time
        jobs.sort(key=lambda j: (get_priority_order(j.priority), j.created_at))

        total = len(jobs)
        jobs = jobs[offset:offset + limit]

        return JobListResponse(jobs=jobs, total=total)

    async def update_job(self, job_id: str, update: JobUpdate) -> Optional[Job]:
        """Update job fields."""
        job = self._jobs.get(job_id)
        if not job:
            return None

        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        job.updated_at = datetime.utcnow()
        return job

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job."""
        job = self._jobs.get(job_id)
        if not job:
            return False

        if job.status in [JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            job.updated_at = datetime.utcnow()

            # Add to history
            await self._add_to_history(job)
            return True

        return False

    async def retry_job(self, job_id: str) -> Optional[Job]:
        """Retry a failed job."""
        job = self._jobs.get(job_id)
        if not job or job.status not in [JobStatus.FAILED, JobStatus.TIMEOUT]:
            return None

        # Check retry policy
        policy = None
        if job.retry_policy_id:
            policy = self._retry_policies.get(job.retry_policy_id)

        if policy and job.retry_count >= policy.max_retries:
            return None

        # Reset job for retry
        job.status = JobStatus.RETRY
        job.retry_count += 1
        job.error_message = None
        job.error_details = None
        job.started_at = None
        job.completed_at = None
        job.progress = 0.0
        job.progress_message = None
        job.updated_at = datetime.utcnow()

        return job

    async def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False

    # Job Progress

    async def update_progress(self, progress: JobProgress) -> Optional[Job]:
        """Update job progress."""
        job = self._jobs.get(progress.job_id)
        if not job:
            return None

        job.progress = min(max(progress.progress, 0), 100)
        if progress.message:
            job.progress_message = progress.message
        if progress.metadata:
            job.metadata.update(progress.metadata)
        job.updated_at = datetime.utcnow()

        return job

    async def start_job(self, job_id: str, worker_id: str) -> Optional[Job]:
        """Mark job as started."""
        job = self._jobs.get(job_id)
        if not job:
            return None

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.worker_id = worker_id
        job.updated_at = datetime.utcnow()

        return job

    async def complete_job(self, result: JobResult) -> Optional[Job]:
        """Mark job as completed."""
        job = self._jobs.get(result.job_id)
        if not job:
            return None

        job.status = result.status
        job.result = result.result
        job.error_message = result.error_message
        job.error_details = result.error_details
        job.completed_at = result.completed_at
        job.progress = 100 if result.status == JobStatus.COMPLETED else job.progress
        job.updated_at = datetime.utcnow()

        # Add to history
        await self._add_to_history(job, result.execution_time_ms)

        return job

    # Schedule Management

    async def create_schedule(self, data: ScheduleCreate) -> Schedule:
        """Create a scheduled job."""
        schedule_id = str(uuid.uuid4())

        next_run = await self._calculate_next_run(
            data.schedule_type,
            data.schedule_config,
        )

        schedule = Schedule(
            id=schedule_id,
            name=data.name,
            description=data.description,
            job_type=data.job_type,
            schedule_type=data.schedule_type,
            schedule_config=data.schedule_config,
            payload=data.payload,
            priority=data.priority,
            timeout_seconds=data.timeout_seconds,
            retry_policy_id=data.retry_policy_id,
            enabled=data.enabled,
            next_run_at=next_run,
            workspace_id=data.workspace_id,
            tags=data.tags,
        )

        self._schedules[schedule_id] = schedule
        return schedule

    async def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get schedule by ID."""
        return self._schedules.get(schedule_id)

    async def list_schedules(
        self,
        job_type: Optional[JobType] = None,
        enabled: Optional[bool] = None,
        workspace_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ScheduleListResponse:
        """List schedules with filters."""
        schedules = list(self._schedules.values())

        if job_type:
            schedules = [s for s in schedules if s.job_type == job_type]
        if enabled is not None:
            schedules = [s for s in schedules if s.enabled == enabled]
        if workspace_id:
            schedules = [s for s in schedules if s.workspace_id == workspace_id]

        schedules.sort(key=lambda s: s.next_run_at or datetime.max)

        total = len(schedules)
        schedules = schedules[offset:offset + limit]

        return ScheduleListResponse(schedules=schedules, total=total)

    async def update_schedule(
        self,
        schedule_id: str,
        update: ScheduleUpdate,
    ) -> Optional[Schedule]:
        """Update schedule fields."""
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return None

        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)

        # Recalculate next run if schedule changed
        if "schedule_type" in update_data or "schedule_config" in update_data:
            schedule.next_run_at = await self._calculate_next_run(
                schedule.schedule_type,
                schedule.schedule_config,
            )

        schedule.updated_at = datetime.utcnow()
        return schedule

    async def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return True
        return False

    async def run_schedule_now(self, schedule_id: str) -> Optional[Job]:
        """Trigger a scheduled job immediately."""
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return None

        # Create job from schedule
        job = await self.create_job(JobCreate(
            name=f"{schedule.name} (Manual Run)",
            job_type=schedule.job_type,
            priority=schedule.priority,
            payload=schedule.payload,
            timeout_seconds=schedule.timeout_seconds,
            retry_policy_id=schedule.retry_policy_id,
            workspace_id=schedule.workspace_id,
            tags=schedule.tags + ["manual_run"],
        ))

        # Record schedule run
        run = ScheduleRun(
            id=str(uuid.uuid4()),
            schedule_id=schedule_id,
            job_id=job.id,
            status=job.status,
            scheduled_time=datetime.utcnow(),
        )
        self._schedule_runs[schedule_id].append(run)

        return job

    async def get_schedule_runs(
        self,
        schedule_id: str,
        limit: int = 50,
    ) -> ScheduleRunListResponse:
        """Get schedule run history."""
        runs = self._schedule_runs.get(schedule_id, [])
        runs = sorted(runs, key=lambda r: r.scheduled_time, reverse=True)

        return ScheduleRunListResponse(
            runs=runs[:limit],
            total=len(runs),
        )

    async def _calculate_next_run(
        self,
        schedule_type: ScheduleType,
        config: dict[str, Any],
    ) -> Optional[datetime]:
        """Calculate next run time for schedule."""
        now = datetime.utcnow()

        if schedule_type == ScheduleType.ONCE:
            run_at = config.get("run_at")
            if run_at:
                return datetime.fromisoformat(run_at) if isinstance(run_at, str) else run_at
            return None

        elif schedule_type == ScheduleType.INTERVAL:
            interval_seconds = config.get("interval_seconds", 3600)
            return now + timedelta(seconds=interval_seconds)

        elif schedule_type == ScheduleType.DAILY:
            hour = config.get("hour", 0)
            minute = config.get("minute", 0)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        elif schedule_type == ScheduleType.WEEKLY:
            day_of_week = config.get("day_of_week", 0)  # 0 = Monday
            hour = config.get("hour", 0)
            minute = config.get("minute", 0)
            days_ahead = day_of_week - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(weeks=1)
            return next_run

        elif schedule_type == ScheduleType.MONTHLY:
            day = config.get("day", 1)
            hour = config.get("hour", 0)
            minute = config.get("minute", 0)
            next_run = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
            return next_run

        elif schedule_type == ScheduleType.CRON:
            # Simplified cron - in production use croniter library
            return now + timedelta(hours=1)

        return None

    # Retry Policy Management

    async def create_retry_policy(self, data: RetryPolicyCreate) -> RetryPolicy:
        """Create a retry policy."""
        policy_id = str(uuid.uuid4())

        policy = RetryPolicy(
            id=policy_id,
            name=data.name,
            description=data.description,
            strategy=data.strategy,
            max_retries=data.max_retries,
            initial_delay_seconds=data.initial_delay_seconds,
            max_delay_seconds=data.max_delay_seconds,
            multiplier=data.multiplier,
            retry_on_statuses=data.retry_on_statuses,
            retry_on_errors=data.retry_on_errors,
        )

        self._retry_policies[policy_id] = policy
        return policy

    async def get_retry_policy(self, policy_id: str) -> Optional[RetryPolicy]:
        """Get retry policy by ID."""
        return self._retry_policies.get(policy_id)

    async def list_retry_policies(self) -> RetryPolicyListResponse:
        """List all retry policies."""
        policies = list(self._retry_policies.values())
        return RetryPolicyListResponse(policies=policies, total=len(policies))

    async def update_retry_policy(
        self,
        policy_id: str,
        update: RetryPolicyUpdate,
    ) -> Optional[RetryPolicy]:
        """Update retry policy."""
        policy = self._retry_policies.get(policy_id)
        if not policy:
            return None

        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)

        return policy

    async def delete_retry_policy(self, policy_id: str) -> bool:
        """Delete a retry policy."""
        if policy_id in self._retry_policies and policy_id not in ["default", "aggressive"]:
            del self._retry_policies[policy_id]
            return True
        return False

    # Worker Management

    async def register_worker(
        self,
        name: str,
        hostname: str,
        job_types: list[JobType],
        max_concurrent_jobs: int = 1,
    ) -> Worker:
        """Register a new worker."""
        worker_id = str(uuid.uuid4())

        worker = Worker(
            id=worker_id,
            name=name,
            hostname=hostname,
            status=WorkerStatus.IDLE,
            job_types=job_types,
            max_concurrent_jobs=max_concurrent_jobs,
            last_heartbeat=datetime.utcnow(),
            started_at=datetime.utcnow(),
        )

        self._workers[worker_id] = worker
        return worker

    async def worker_heartbeat(self, heartbeat: WorkerHeartbeat) -> Optional[Worker]:
        """Update worker heartbeat."""
        worker = self._workers.get(heartbeat.worker_id)
        if not worker:
            return None

        worker.status = heartbeat.status
        worker.current_job_id = heartbeat.current_job_id
        worker.last_heartbeat = datetime.utcnow()

        if heartbeat.memory_usage_mb:
            worker.metadata["memory_usage_mb"] = heartbeat.memory_usage_mb
        if heartbeat.cpu_usage_percent:
            worker.metadata["cpu_usage_percent"] = heartbeat.cpu_usage_percent

        return worker

    async def unregister_worker(self, worker_id: str) -> bool:
        """Unregister a worker."""
        if worker_id in self._workers:
            del self._workers[worker_id]
            return True
        return False

    async def list_workers(
        self,
        status: Optional[WorkerStatus] = None,
    ) -> WorkerListResponse:
        """List workers."""
        workers = list(self._workers.values())

        if status:
            workers = [w for w in workers if w.status == status]

        return WorkerListResponse(workers=workers, total=len(workers))

    async def get_next_job_for_worker(self, worker_id: str) -> Optional[Job]:
        """Get next job for a worker to process."""
        worker = self._workers.get(worker_id)
        if not worker or worker.status != WorkerStatus.IDLE:
            return None

        # Find pending jobs that match worker's job types
        pending_jobs = [
            j for j in self._jobs.values()
            if j.status in [JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RETRY]
            and j.job_type in worker.job_types
            and (j.scheduled_at is None or j.scheduled_at <= datetime.utcnow())
        ]

        if not pending_jobs:
            return None

        # Sort by priority and creation time
        pending_jobs.sort(key=lambda j: (get_priority_order(j.priority), j.created_at))

        return pending_jobs[0]

    # Job History

    async def _add_to_history(
        self,
        job: Job,
        execution_time_ms: Optional[float] = None,
    ):
        """Add completed job to history."""
        if execution_time_ms is None and job.started_at and job.completed_at:
            execution_time_ms = (job.completed_at - job.started_at).total_seconds() * 1000

        entry = JobHistoryEntry(
            id=str(uuid.uuid4()),
            job_id=job.id,
            job_name=job.name,
            job_type=job.job_type,
            status=job.status,
            priority=job.priority,
            workspace_id=job.workspace_id,
            user_id=job.user_id,
            execution_time_ms=execution_time_ms,
            retry_count=job.retry_count,
            error_message=job.error_message,
            scheduled_at=job.scheduled_at,
            started_at=job.started_at,
            completed_at=job.completed_at or datetime.utcnow(),
            tags=job.tags,
        )

        self._job_history.append(entry)

    async def get_job_history(
        self,
        job_type: Optional[JobType] = None,
        status: Optional[JobStatus] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> JobHistoryListResponse:
        """Get job execution history."""
        entries = self._job_history.copy()

        if job_type:
            entries = [e for e in entries if e.job_type == job_type]
        if status:
            entries = [e for e in entries if e.status == status]
        if workspace_id:
            entries = [e for e in entries if e.workspace_id == workspace_id]
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if start_date:
            entries = [e for e in entries if e.completed_at >= start_date]
        if end_date:
            entries = [e for e in entries if e.completed_at <= end_date]

        entries.sort(key=lambda e: e.completed_at, reverse=True)

        total = len(entries)
        entries = entries[offset:offset + limit]

        return JobHistoryListResponse(entries=entries, total=total)

    async def get_job_history_stats(
        self,
        workspace_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> JobHistoryStats:
        """Get job history statistics."""
        entries = self._job_history.copy()

        if workspace_id:
            entries = [e for e in entries if e.workspace_id == workspace_id]
        if start_date:
            entries = [e for e in entries if e.completed_at >= start_date]
        if end_date:
            entries = [e for e in entries if e.completed_at <= end_date]

        if not entries:
            return JobHistoryStats(
                total_jobs=0,
                completed_jobs=0,
                failed_jobs=0,
                cancelled_jobs=0,
                avg_execution_time_ms=0,
                total_execution_time_ms=0,
                success_rate=0,
                by_type={},
                by_status={},
                by_hour=[],
                slowest_jobs=[],
            )

        # Calculate statistics
        completed = [e for e in entries if e.status == JobStatus.COMPLETED]
        failed = [e for e in entries if e.status == JobStatus.FAILED]
        cancelled = [e for e in entries if e.status == JobStatus.CANCELLED]

        exec_times = [e.execution_time_ms for e in entries if e.execution_time_ms]
        total_exec_time = sum(exec_times) if exec_times else 0
        avg_exec_time = total_exec_time / len(exec_times) if exec_times else 0

        # Group by type
        by_type: dict[str, int] = defaultdict(int)
        for e in entries:
            by_type[e.job_type.value] += 1

        # Group by status
        by_status: dict[str, int] = defaultdict(int)
        for e in entries:
            by_status[e.status.value] += 1

        # Group by hour
        by_hour: dict[int, dict[str, int]] = defaultdict(lambda: {"count": 0, "failures": 0})
        for e in entries:
            hour = e.completed_at.hour
            by_hour[hour]["count"] += 1
            if e.status == JobStatus.FAILED:
                by_hour[hour]["failures"] += 1

        by_hour_list = [
            {"hour": h, **stats}
            for h, stats in sorted(by_hour.items())
        ]

        # Slowest jobs
        entries_with_time = [e for e in entries if e.execution_time_ms]
        entries_with_time.sort(key=lambda e: e.execution_time_ms or 0, reverse=True)

        return JobHistoryStats(
            total_jobs=len(entries),
            completed_jobs=len(completed),
            failed_jobs=len(failed),
            cancelled_jobs=len(cancelled),
            avg_execution_time_ms=avg_exec_time,
            total_execution_time_ms=total_exec_time,
            success_rate=len(completed) / len(entries) if entries else 0,
            by_type=dict(by_type),
            by_status=dict(by_status),
            by_hour=by_hour_list,
            slowest_jobs=entries_with_time[:10],
        )

    # Queue Management

    async def get_queue_stats(self, queue_name: str) -> Optional[QueueStats]:
        """Get statistics for a job queue."""
        queue = self._queues.get(queue_name)
        if not queue:
            return None

        # Get jobs for this queue's job types
        queue_jobs = [
            j for j in self._jobs.values()
            if j.job_type in queue.job_types
        ]

        pending = [j for j in queue_jobs if j.status in [JobStatus.PENDING, JobStatus.QUEUED]]
        running = [j for j in queue_jobs if j.status == JobStatus.RUNNING]
        completed = [j for j in queue_jobs if j.status == JobStatus.COMPLETED]
        failed = [j for j in queue_jobs if j.status == JobStatus.FAILED]

        # Calculate wait times
        wait_times = []
        for j in completed + running:
            if j.created_at and j.started_at:
                wait_times.append((j.started_at - j.created_at).total_seconds() * 1000)

        # Calculate execution times
        exec_times = []
        for j in completed:
            if j.started_at and j.completed_at:
                exec_times.append((j.completed_at - j.started_at).total_seconds() * 1000)

        # Calculate oldest pending age
        oldest_age = 0
        if pending:
            oldest = min(pending, key=lambda j: j.created_at)
            oldest_age = (datetime.utcnow() - oldest.created_at).total_seconds()

        return QueueStats(
            name=queue_name,
            pending_count=len(pending),
            running_count=len(running),
            completed_count=len(completed),
            failed_count=len(failed),
            avg_wait_time_ms=sum(wait_times) / len(wait_times) if wait_times else 0,
            avg_execution_time_ms=sum(exec_times) / len(exec_times) if exec_times else 0,
            throughput_per_minute=len(completed) / 60 if completed else 0,
            oldest_pending_age_seconds=oldest_age,
        )

    async def get_all_queue_stats(self) -> list[QueueStats]:
        """Get statistics for all queues."""
        stats = []
        for queue_name in self._queues:
            queue_stats = await self.get_queue_stats(queue_name)
            if queue_stats:
                stats.append(queue_stats)
        return stats

    # Dashboard

    async def get_dashboard(self) -> JobsDashboard:
        """Get jobs dashboard summary."""
        jobs = list(self._jobs.values())
        workers = list(self._workers.values())

        # Count jobs by status
        active = [j for j in jobs if j.status == JobStatus.RUNNING]
        pending = [j for j in jobs if j.status in [JobStatus.PENDING, JobStatus.QUEUED]]

        # Today's stats
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_history = [e for e in self._job_history if e.completed_at >= today]
        completed_today = len([e for e in today_history if e.status == JobStatus.COMPLETED])
        failed_today = len([e for e in today_history if e.status == JobStatus.FAILED])

        # Calculate averages
        wait_times = []
        exec_times = []
        for j in jobs:
            if j.created_at and j.started_at:
                wait_times.append((j.started_at - j.created_at).total_seconds() * 1000)
            if j.started_at and j.completed_at:
                exec_times.append((j.completed_at - j.started_at).total_seconds() * 1000)

        # Recent failures
        recent_failures = [j for j in jobs if j.status == JobStatus.FAILED]
        recent_failures.sort(key=lambda j: j.completed_at or datetime.min, reverse=True)

        return JobsDashboard(
            active_jobs=len(active),
            pending_jobs=len(pending),
            completed_today=completed_today,
            failed_today=failed_today,
            success_rate=completed_today / (completed_today + failed_today) if (completed_today + failed_today) > 0 else 0,
            avg_wait_time_ms=sum(wait_times) / len(wait_times) if wait_times else 0,
            avg_execution_time_ms=sum(exec_times) / len(exec_times) if exec_times else 0,
            active_workers=len([w for w in workers if w.status == WorkerStatus.BUSY]),
            total_workers=len(workers),
            queues=await self.get_all_queue_stats(),
            recent_failures=recent_failures[:5],
        )

    # Configuration

    async def get_config(self) -> JobsConfig:
        """Get jobs configuration."""
        return self._config

    async def update_config(self, update: JobsConfigUpdate) -> JobsConfig:
        """Update jobs configuration."""
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(self._config, field, value)
        return self._config

    # Cleanup

    async def cleanup_old_jobs(self) -> int:
        """Clean up old completed/failed jobs."""
        now = datetime.utcnow()
        completed_cutoff = now - timedelta(hours=self._config.cleanup_completed_after_hours)
        failed_cutoff = now - timedelta(hours=self._config.cleanup_failed_after_hours)

        jobs_to_remove = []
        for job_id, job in self._jobs.items():
            if job.status == JobStatus.COMPLETED and job.completed_at and job.completed_at < completed_cutoff:
                jobs_to_remove.append(job_id)
            elif job.status == JobStatus.FAILED and job.completed_at and job.completed_at < failed_cutoff:
                jobs_to_remove.append(job_id)

        for job_id in jobs_to_remove:
            del self._jobs[job_id]

        return len(jobs_to_remove)


# Global service instance
background_jobs_service = BackgroundJobsService()
