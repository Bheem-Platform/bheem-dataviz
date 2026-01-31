"""
Scheduled Report Service

Business logic for scheduled report management including
schedule CRUD, execution, and delivery.
"""

from datetime import datetime, timedelta
from typing import Optional, Any
import uuid

from app.schemas.scheduled_report import (
    ScheduleFrequency, ScheduleStatus, ExecutionStatus, DeliveryMethod,
    ScheduledReport, ScheduledReportCreate, ScheduledReportUpdate, ScheduledReportListResponse,
    ReportExecution, ReportExecutionListResponse,
    DeliveryResult, ExecutionLog, ScheduleStats,
    RecurrencePattern, DateRange, DeliveryConfig, ReportSourceConfig,
    get_next_run_time, is_schedule_due,
)


class ScheduledReportService:
    """Service for managing scheduled reports."""

    def __init__(self):
        # In-memory stores (replace with database in production)
        self.schedules: dict[str, ScheduledReport] = {}
        self.executions: dict[str, ReportExecution] = {}

    # Schedule CRUD Operations

    def create_schedule(
        self,
        user_id: str,
        data: ScheduledReportCreate,
        organization_id: Optional[str] = None,
    ) -> ScheduledReport:
        """Create a new scheduled report."""
        schedule_id = f"sched-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        # Calculate next run time
        next_run = get_next_run_time(data.recurrence)
        if data.date_range.start_date > now:
            next_run = max(next_run, data.date_range.start_date)

        schedule = ScheduledReport(
            id=schedule_id,
            user_id=user_id,
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            source_config=data.source_config,
            recurrence=data.recurrence,
            delivery_configs=data.delivery_configs,
            date_range=data.date_range,
            status=ScheduleStatus.ACTIVE if data.is_active else ScheduleStatus.PAUSED,
            is_active=data.is_active,
            notify_on_failure=data.notify_on_failure,
            failure_notification_emails=data.failure_notification_emails,
            tags=data.tags,
            next_run_at=next_run,
            created_at=now,
            updated_at=now,
        )

        self.schedules[schedule_id] = schedule
        return schedule

    def get_schedule(self, schedule_id: str) -> Optional[ScheduledReport]:
        """Get schedule by ID."""
        return self.schedules.get(schedule_id)

    def list_schedules(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        status: Optional[ScheduleStatus] = None,
        is_active: Optional[bool] = None,
        source_type: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ScheduledReportListResponse:
        """List schedules with filtering."""
        schedules = list(self.schedules.values())

        if user_id:
            schedules = [s for s in schedules if s.user_id == user_id]

        if organization_id:
            schedules = [s for s in schedules if s.organization_id == organization_id]

        if status:
            schedules = [s for s in schedules if s.status == status]

        if is_active is not None:
            schedules = [s for s in schedules if s.is_active == is_active]

        if source_type:
            schedules = [s for s in schedules if s.source_config.source_type == source_type]

        if search:
            search_lower = search.lower()
            schedules = [
                s for s in schedules
                if search_lower in s.name.lower()
                or (s.description and search_lower in s.description.lower())
                or any(search_lower in tag.lower() for tag in s.tags)
            ]

        # Sort by next_run_at
        schedules.sort(key=lambda x: x.next_run_at or datetime.max)

        total = len(schedules)
        schedules = schedules[skip:skip + limit]

        return ScheduledReportListResponse(schedules=schedules, total=total)

    def update_schedule(
        self,
        schedule_id: str,
        data: ScheduledReportUpdate,
    ) -> Optional[ScheduledReport]:
        """Update a schedule."""
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return None

        recurrence_changed = False

        if data.name is not None:
            schedule.name = data.name

        if data.description is not None:
            schedule.description = data.description

        if data.source_config is not None:
            schedule.source_config = data.source_config

        if data.recurrence is not None:
            schedule.recurrence = data.recurrence
            recurrence_changed = True

        if data.delivery_configs is not None:
            schedule.delivery_configs = data.delivery_configs

        if data.date_range is not None:
            schedule.date_range = data.date_range
            recurrence_changed = True

        if data.is_active is not None:
            schedule.is_active = data.is_active
            if data.is_active and schedule.status == ScheduleStatus.PAUSED:
                schedule.status = ScheduleStatus.ACTIVE
            elif not data.is_active and schedule.status == ScheduleStatus.ACTIVE:
                schedule.status = ScheduleStatus.PAUSED

        if data.status is not None:
            schedule.status = data.status

        if data.notify_on_failure is not None:
            schedule.notify_on_failure = data.notify_on_failure

        if data.failure_notification_emails is not None:
            schedule.failure_notification_emails = data.failure_notification_emails

        if data.tags is not None:
            schedule.tags = data.tags

        # Recalculate next run time if recurrence changed
        if recurrence_changed:
            schedule.next_run_at = get_next_run_time(schedule.recurrence)

        schedule.updated_at = datetime.utcnow()

        return schedule

    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        if schedule_id in self.schedules:
            # Delete associated executions
            self.executions = {
                k: v for k, v in self.executions.items()
                if v.schedule_id != schedule_id
            }
            del self.schedules[schedule_id]
            return True
        return False

    def pause_schedule(self, schedule_id: str) -> Optional[ScheduledReport]:
        """Pause a schedule."""
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return None

        schedule.is_active = False
        schedule.status = ScheduleStatus.PAUSED
        schedule.updated_at = datetime.utcnow()
        return schedule

    def resume_schedule(self, schedule_id: str) -> Optional[ScheduledReport]:
        """Resume a paused schedule."""
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return None

        schedule.is_active = True
        schedule.status = ScheduleStatus.ACTIVE
        schedule.next_run_at = get_next_run_time(schedule.recurrence)
        schedule.updated_at = datetime.utcnow()
        return schedule

    # Execution Management

    def trigger_execution(
        self,
        schedule_id: str,
        triggered_by: str = "manual",
    ) -> Optional[ReportExecution]:
        """Trigger a report execution."""
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return None

        execution_id = f"exec-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        execution = ReportExecution(
            id=execution_id,
            schedule_id=schedule_id,
            schedule_name=schedule.name,
            user_id=schedule.user_id,
            organization_id=schedule.organization_id,
            status=ExecutionStatus.PENDING,
            started_at=now,
            source_config=schedule.source_config,
            export_format=schedule.source_config.export_format,
            delivery_results=[],
            logs=[
                ExecutionLog(
                    timestamp=now,
                    level="info",
                    message=f"Execution triggered by {triggered_by}",
                )
            ],
            triggered_by=triggered_by,
        )

        self.executions[execution_id] = execution

        # Simulate execution start
        self._start_execution(execution_id)

        return execution

    def _start_execution(self, execution_id: str):
        """Start execution (simulation)."""
        execution = self.executions.get(execution_id)
        if not execution:
            return

        execution.status = ExecutionStatus.RUNNING
        execution.logs.append(ExecutionLog(
            timestamp=datetime.utcnow(),
            level="info",
            message="Execution started",
        ))

        # In production, this would queue the actual report generation
        # For now, simulate completion
        self._complete_execution(execution_id)

    def _complete_execution(self, execution_id: str, success: bool = True, error: Optional[str] = None):
        """Complete execution (simulation)."""
        execution = self.executions.get(execution_id)
        if not execution:
            return

        now = datetime.utcnow()
        execution.completed_at = now
        execution.duration_seconds = (now - execution.started_at).total_seconds()

        if success:
            execution.status = ExecutionStatus.COMPLETED
            execution.file_size_bytes = 1024 * 100  # Simulated 100KB
            execution.file_url = f"/downloads/{execution_id}.{execution.export_format}"

            # Simulate delivery results
            schedule = self.schedules.get(execution.schedule_id)
            if schedule:
                for delivery_config in schedule.delivery_configs:
                    execution.delivery_results.append(DeliveryResult(
                        method=delivery_config.method,
                        success=True,
                        message="Delivered successfully",
                        delivered_at=now,
                        recipient_count=1,
                        file_url=execution.file_url,
                    ))

            execution.logs.append(ExecutionLog(
                timestamp=now,
                level="info",
                message="Execution completed successfully",
            ))

            # Update schedule stats
            if schedule:
                schedule.last_run_at = now
                schedule.last_run_status = ExecutionStatus.COMPLETED
                schedule.total_runs += 1
                schedule.successful_runs += 1
                schedule.next_run_at = get_next_run_time(schedule.recurrence, now)
        else:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = error or "Unknown error"

            execution.logs.append(ExecutionLog(
                timestamp=now,
                level="error",
                message=f"Execution failed: {error}",
            ))

            # Update schedule stats
            schedule = self.schedules.get(execution.schedule_id)
            if schedule:
                schedule.last_run_at = now
                schedule.last_run_status = ExecutionStatus.FAILED
                schedule.total_runs += 1
                schedule.failed_runs += 1
                schedule.next_run_at = get_next_run_time(schedule.recurrence, now)

    def get_execution(self, execution_id: str) -> Optional[ReportExecution]:
        """Get execution by ID."""
        return self.executions.get(execution_id)

    def list_executions(
        self,
        schedule_id: Optional[str] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ReportExecutionListResponse:
        """List executions with filtering."""
        executions = list(self.executions.values())

        if schedule_id:
            executions = [e for e in executions if e.schedule_id == schedule_id]

        if user_id:
            executions = [e for e in executions if e.user_id == user_id]

        if organization_id:
            executions = [e for e in executions if e.organization_id == organization_id]

        if status:
            executions = [e for e in executions if e.status == status]

        if from_date:
            executions = [e for e in executions if e.started_at >= from_date]

        if to_date:
            executions = [e for e in executions if e.started_at <= to_date]

        # Sort by started_at descending
        executions.sort(key=lambda x: x.started_at, reverse=True)

        total = len(executions)
        executions = executions[skip:skip + limit]

        return ReportExecutionListResponse(executions=executions, total=total)

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution."""
        execution = self.executions.get(execution_id)
        if not execution or execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
            return False

        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        execution.logs.append(ExecutionLog(
            timestamp=datetime.utcnow(),
            level="info",
            message="Execution cancelled by user",
        ))

        return True

    def retry_execution(self, execution_id: str) -> Optional[ReportExecution]:
        """Retry a failed execution."""
        original = self.executions.get(execution_id)
        if not original or original.status != ExecutionStatus.FAILED:
            return None

        return self.trigger_execution(original.schedule_id, triggered_by="retry")

    # Due Schedules

    def get_due_schedules(self) -> list[ScheduledReport]:
        """Get all schedules that are due to run."""
        return [s for s in self.schedules.values() if is_schedule_due(s)]

    def process_due_schedules(self) -> list[ReportExecution]:
        """Process all due schedules and trigger executions."""
        due_schedules = self.get_due_schedules()
        executions = []

        for schedule in due_schedules:
            execution = self.trigger_execution(schedule.id, triggered_by="schedule")
            if execution:
                executions.append(execution)

        return executions

    # Statistics

    def get_stats(self, organization_id: str) -> ScheduleStats:
        """Get schedule statistics for organization."""
        schedules = [s for s in self.schedules.values() if s.organization_id == organization_id]
        executions = [e for e in self.executions.values() if e.organization_id == organization_id]

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        executions_today = [e for e in executions if e.started_at >= today_start]
        executions_week = [e for e in executions if e.started_at >= week_start]
        executions_month = [e for e in executions if e.started_at >= month_start]

        completed_executions = [e for e in executions if e.status == ExecutionStatus.COMPLETED]
        success_rate = len(completed_executions) / len(executions) if executions else 0

        avg_duration = sum(
            e.duration_seconds for e in completed_executions if e.duration_seconds
        ) / len(completed_executions) if completed_executions else 0

        by_frequency = {}
        for s in schedules:
            freq = s.recurrence.frequency.value
            by_frequency[freq] = by_frequency.get(freq, 0) + 1

        by_format = {}
        for s in schedules:
            fmt = s.source_config.export_format
            by_format[fmt] = by_format.get(fmt, 0) + 1

        by_delivery = {}
        for s in schedules:
            for dc in s.delivery_configs:
                method = dc.method.value
                by_delivery[method] = by_delivery.get(method, 0) + 1

        upcoming = [s for s in schedules if s.next_run_at and s.next_run_at > now]

        return ScheduleStats(
            organization_id=organization_id,
            total_schedules=len(schedules),
            active_schedules=len([s for s in schedules if s.status == ScheduleStatus.ACTIVE]),
            paused_schedules=len([s for s in schedules if s.status == ScheduleStatus.PAUSED]),
            total_executions=len(executions),
            executions_today=len(executions_today),
            executions_this_week=len(executions_week),
            executions_this_month=len(executions_month),
            success_rate=success_rate,
            average_duration_seconds=avg_duration,
            by_frequency=by_frequency,
            by_format=by_format,
            by_delivery_method=by_delivery,
            upcoming_executions=len(upcoming),
        )


# Global service instance
scheduled_report_service = ScheduledReportService()
