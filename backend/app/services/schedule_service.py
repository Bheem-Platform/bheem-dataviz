"""
Schedule Service

Handles schedule management, execution, and alert evaluation.
Integrates with Celery for background task execution.
"""

import logging
from typing import Any, Optional
from datetime import datetime, timedelta
import uuid

from croniter import croniter

from app.schemas.schedule import (
    ScheduleFrequency,
    ScheduleStatus,
    RefreshType,
    AlertSeverity,
    AlertOperator,
    NotificationChannel,
    ScheduleConfig,
    RefreshSchedule,
    AlertRule,
    AlertCondition,
    ScheduleExecution,
    AlertExecution,
    ScheduleSummary,
    AlertSummary,
)

logger = logging.getLogger(__name__)


class ScheduleService:
    """Service for managing schedules and alerts"""

    def __init__(self):
        self._schedules: dict[str, RefreshSchedule] = {}
        self._alerts: dict[str, AlertRule] = {}
        self._schedule_executions: list[ScheduleExecution] = []
        self._alert_executions: list[AlertExecution] = []

    # Schedule Management

    def create_schedule(self, schedule: RefreshSchedule) -> RefreshSchedule:
        """Create a new refresh schedule"""
        if not schedule.id:
            schedule.id = str(uuid.uuid4())

        schedule.created_at = datetime.utcnow().isoformat()
        schedule.updated_at = schedule.created_at
        schedule.next_run_at = self.calculate_next_run(schedule.schedule)

        self._schedules[schedule.id] = schedule
        return schedule

    def update_schedule(self, schedule_id: str, schedule: RefreshSchedule) -> RefreshSchedule:
        """Update an existing schedule"""
        if schedule_id not in self._schedules:
            raise ValueError(f"Schedule {schedule_id} not found")

        schedule.id = schedule_id
        schedule.updated_at = datetime.utcnow().isoformat()
        schedule.created_at = self._schedules[schedule_id].created_at
        schedule.next_run_at = self.calculate_next_run(schedule.schedule)

        self._schedules[schedule_id] = schedule
        return schedule

    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule"""
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return True
        return False

    def get_schedule(self, schedule_id: str) -> Optional[RefreshSchedule]:
        """Get a schedule by ID"""
        return self._schedules.get(schedule_id)

    def list_schedules(
        self,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[ScheduleStatus] = None,
    ) -> list[RefreshSchedule]:
        """List schedules with optional filtering"""
        schedules = list(self._schedules.values())

        if target_type:
            schedules = [s for s in schedules if s.target_type == target_type]
        if target_id:
            schedules = [s for s in schedules if s.target_id == target_id]
        if status:
            schedules = [s for s in schedules if s.status == status]

        return schedules

    def pause_schedule(self, schedule_id: str) -> bool:
        """Pause a schedule"""
        if schedule_id in self._schedules:
            self._schedules[schedule_id].status = ScheduleStatus.PAUSED
            self._schedules[schedule_id].updated_at = datetime.utcnow().isoformat()
            return True
        return False

    def resume_schedule(self, schedule_id: str) -> bool:
        """Resume a paused schedule"""
        if schedule_id in self._schedules:
            self._schedules[schedule_id].status = ScheduleStatus.ACTIVE
            self._schedules[schedule_id].updated_at = datetime.utcnow().isoformat()
            self._schedules[schedule_id].next_run_at = self.calculate_next_run(
                self._schedules[schedule_id].schedule
            )
            return True
        return False

    # Alert Management

    def create_alert(self, alert: AlertRule) -> AlertRule:
        """Create a new alert rule"""
        if not alert.id:
            alert.id = str(uuid.uuid4())

        alert.created_at = datetime.utcnow().isoformat()
        alert.updated_at = alert.created_at

        self._alerts[alert.id] = alert
        return alert

    def update_alert(self, alert_id: str, alert: AlertRule) -> AlertRule:
        """Update an existing alert"""
        if alert_id not in self._alerts:
            raise ValueError(f"Alert {alert_id} not found")

        alert.id = alert_id
        alert.updated_at = datetime.utcnow().isoformat()
        alert.created_at = self._alerts[alert_id].created_at

        self._alerts[alert_id] = alert
        return alert

    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        if alert_id in self._alerts:
            del self._alerts[alert_id]
            return True
        return False

    def get_alert(self, alert_id: str) -> Optional[AlertRule]:
        """Get an alert by ID"""
        return self._alerts.get(alert_id)

    def list_alerts(
        self,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
    ) -> list[AlertRule]:
        """List alerts with optional filtering"""
        alerts = list(self._alerts.values())

        if target_type:
            alerts = [a for a in alerts if a.target_type == target_type]
        if target_id:
            alerts = [a for a in alerts if a.target_id == target_id]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts

    def snooze_alert(self, alert_id: str, until: datetime) -> bool:
        """Snooze an alert until a specific time"""
        if alert_id in self._alerts:
            self._alerts[alert_id].snooze_until = until.isoformat()
            self._alerts[alert_id].updated_at = datetime.utcnow().isoformat()
            return True
        return False

    # Schedule Execution

    def calculate_next_run(self, config: ScheduleConfig) -> Optional[str]:
        """Calculate the next run time for a schedule"""
        now = datetime.utcnow()

        if config.frequency == ScheduleFrequency.ONCE:
            if config.start_time:
                start = datetime.fromisoformat(config.start_time.replace("Z", "+00:00"))
                if start > now:
                    return start.isoformat()
            return None

        elif config.frequency == ScheduleFrequency.HOURLY:
            next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return next_run.isoformat()

        elif config.frequency == ScheduleFrequency.DAILY:
            if config.time:
                next_run = now.replace(
                    hour=config.time.hour,
                    minute=config.time.minute,
                    second=0,
                    microsecond=0,
                )
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run.isoformat()
            return (now + timedelta(days=1)).isoformat()

        elif config.frequency == ScheduleFrequency.WEEKLY and config.weekly:
            # Find next occurrence
            for i in range(7):
                check_date = now + timedelta(days=i)
                if check_date.weekday() in config.weekly.days:
                    next_run = check_date.replace(
                        hour=config.weekly.time.hour,
                        minute=config.weekly.time.minute,
                        second=0,
                        microsecond=0,
                    )
                    if next_run > now:
                        return next_run.isoformat()
            return None

        elif config.frequency == ScheduleFrequency.MONTHLY and config.monthly:
            # Find next occurrence
            current = now.replace(
                hour=config.monthly.time.hour,
                minute=config.monthly.time.minute,
                second=0,
                microsecond=0,
            )
            for _ in range(32):  # Check up to 32 days
                if current.day in config.monthly.days and current > now:
                    return current.isoformat()
                current += timedelta(days=1)
            return None

        elif config.frequency == ScheduleFrequency.CUSTOM and config.cron_expression:
            try:
                cron = croniter(config.cron_expression, now)
                next_run = cron.get_next(datetime)
                return next_run.isoformat()
            except Exception as e:
                logger.error(f"Invalid cron expression: {e}")
                return None

        return None

    def record_execution(
        self,
        schedule_id: str,
        status: str,
        started_at: datetime,
        completed_at: Optional[datetime] = None,
        rows_processed: Optional[int] = None,
        error_message: Optional[str] = None,
        triggered_by: str = "schedule",
    ) -> ScheduleExecution:
        """Record a schedule execution"""
        execution = ScheduleExecution(
            id=str(uuid.uuid4()),
            schedule_id=schedule_id,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat() if completed_at else None,
            status=status,
            duration_seconds=(completed_at - started_at).total_seconds() if completed_at else None,
            rows_processed=rows_processed,
            error_message=error_message,
            triggered_by=triggered_by,
        )

        self._schedule_executions.append(execution)

        # Update schedule status
        if schedule_id in self._schedules:
            self._schedules[schedule_id].last_run_at = started_at.isoformat()
            self._schedules[schedule_id].last_run_status = status
            if status == "failed":
                self._schedules[schedule_id].status = ScheduleStatus.ERROR
            else:
                self._schedules[schedule_id].next_run_at = self.calculate_next_run(
                    self._schedules[schedule_id].schedule
                )

        return execution

    def get_execution_history(
        self,
        schedule_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[ScheduleExecution]:
        """Get execution history"""
        executions = self._schedule_executions

        if schedule_id:
            executions = [e for e in executions if e.schedule_id == schedule_id]

        return sorted(executions, key=lambda e: e.started_at, reverse=True)[:limit]

    # Alert Evaluation

    def evaluate_alert(
        self,
        alert: AlertRule,
        current_values: dict[str, float],
        previous_values: Optional[dict[str, float]] = None,
    ) -> AlertExecution:
        """Evaluate an alert and determine if it should trigger"""
        condition_results = []
        triggered_conditions = []

        for condition in alert.conditions:
            result = self._evaluate_condition(
                condition,
                current_values.get(condition.measure),
                previous_values.get(condition.measure) if previous_values else None,
            )
            condition_results.append({
                "condition_id": condition.id,
                "measure": condition.measure,
                "triggered": result,
                "current_value": current_values.get(condition.measure),
            })

            if result:
                triggered_conditions.append(condition.id)

        # Determine if alert triggers based on logic
        if alert.condition_logic == "AND":
            triggered = len(triggered_conditions) == len(alert.conditions)
        else:  # OR
            triggered = len(triggered_conditions) > 0

        # Check snooze
        if triggered and alert.snooze_until:
            snooze_end = datetime.fromisoformat(alert.snooze_until.replace("Z", "+00:00"))
            if datetime.utcnow() < snooze_end:
                triggered = False

        # Record execution
        execution = AlertExecution(
            id=str(uuid.uuid4()),
            alert_id=alert.id,
            evaluated_at=datetime.utcnow().isoformat(),
            triggered=triggered,
            condition_results=condition_results,
            current_value=list(current_values.values())[0] if current_values else None,
            threshold_value=alert.conditions[0].threshold if alert.conditions else None,
        )

        self._alert_executions.append(execution)

        # Update alert stats
        if triggered and alert.id in self._alerts:
            self._alerts[alert.id].last_triggered_at = datetime.utcnow().isoformat()
            self._alerts[alert.id].trigger_count += 1

        return execution

    def _evaluate_condition(
        self,
        condition: AlertCondition,
        current_value: Optional[float],
        previous_value: Optional[float] = None,
    ) -> bool:
        """Evaluate a single alert condition"""
        if current_value is None:
            return False

        try:
            if condition.operator == AlertOperator.GREATER_THAN:
                return current_value > condition.threshold
            elif condition.operator == AlertOperator.LESS_THAN:
                return current_value < condition.threshold
            elif condition.operator == AlertOperator.EQUALS:
                return current_value == condition.threshold
            elif condition.operator == AlertOperator.NOT_EQUALS:
                return current_value != condition.threshold
            elif condition.operator == AlertOperator.BETWEEN:
                return condition.threshold <= current_value <= (condition.threshold2 or condition.threshold)
            elif condition.operator == AlertOperator.OUTSIDE:
                return not (condition.threshold <= current_value <= (condition.threshold2 or condition.threshold))
            elif condition.operator == AlertOperator.CHANGE_GREATER_THAN:
                if previous_value is None:
                    return False
                change = abs(current_value - previous_value)
                return change > condition.threshold
            elif condition.operator == AlertOperator.CHANGE_LESS_THAN:
                if previous_value is None:
                    return False
                change = abs(current_value - previous_value)
                return change < condition.threshold
            elif condition.operator == AlertOperator.PERCENT_CHANGE_GREATER_THAN:
                if previous_value is None or previous_value == 0:
                    return False
                pct_change = abs((current_value - previous_value) / previous_value * 100)
                return pct_change > condition.threshold
            elif condition.operator == AlertOperator.PERCENT_CHANGE_LESS_THAN:
                if previous_value is None or previous_value == 0:
                    return False
                pct_change = abs((current_value - previous_value) / previous_value * 100)
                return pct_change < condition.threshold
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False

        return False

    def get_alert_history(
        self,
        alert_id: Optional[str] = None,
        triggered_only: bool = False,
        limit: int = 50,
    ) -> list[AlertExecution]:
        """Get alert execution history"""
        executions = self._alert_executions

        if alert_id:
            executions = [e for e in executions if e.alert_id == alert_id]

        if triggered_only:
            executions = [e for e in executions if e.triggered]

        return sorted(executions, key=lambda e: e.evaluated_at, reverse=True)[:limit]

    # Summaries

    def get_schedule_summary(self) -> ScheduleSummary:
        """Get summary of schedule activity"""
        schedules = list(self._schedules.values())
        today = datetime.utcnow().date()

        today_executions = [
            e for e in self._schedule_executions
            if datetime.fromisoformat(e.started_at.replace("Z", "+00:00")).date() == today
        ]

        return ScheduleSummary(
            total_schedules=len(schedules),
            active_schedules=len([s for s in schedules if s.status == ScheduleStatus.ACTIVE]),
            paused_schedules=len([s for s in schedules if s.status == ScheduleStatus.PAUSED]),
            failed_schedules=len([s for s in schedules if s.status == ScheduleStatus.ERROR]),
            executions_today=len(today_executions),
            successful_today=len([e for e in today_executions if e.status == "success"]),
            failed_today=len([e for e in today_executions if e.status == "failed"]),
        )

    def get_alert_summary(self) -> AlertSummary:
        """Get summary of alert activity"""
        alerts = list(self._alerts.values())
        today = datetime.utcnow().date()

        today_triggered = [
            e for e in self._alert_executions
            if e.triggered and datetime.fromisoformat(e.evaluated_at.replace("Z", "+00:00")).date() == today
        ]

        return AlertSummary(
            total_alerts=len(alerts),
            active_alerts=len([a for a in alerts if a.enabled]),
            triggered_today=len(today_triggered),
            critical_active=len([a for a in alerts if a.enabled and a.severity == AlertSeverity.CRITICAL]),
            warning_active=len([a for a in alerts if a.enabled and a.severity == AlertSeverity.WARNING]),
        )


def get_schedule_service() -> ScheduleService:
    """Factory function to get service instance"""
    return ScheduleService()
