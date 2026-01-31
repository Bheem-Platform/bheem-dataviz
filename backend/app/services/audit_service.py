"""
Audit Service

Handles audit logging, querying, and security alert generation.
"""

import logging
import asyncio
from typing import Any, Optional
from datetime import datetime, timedelta
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.models.audit import AuditLog, SecurityAlert, AuditAction, AlertType
from app.schemas.audit import (
    AuditLogCreate,
    AuditLogResponse,
    AuditLogFilter,
    AuditLogSummary,
    SecurityAlertCreate,
    SecurityAlertResponse,
    SecurityAlertFilter,
    AlertSeverity,
    AlertStatus,
    ActivityTimelineEntry,
    UserActivitySummary,
    AuditDashboardStats,
    sanitize_request_body,
    format_action_description,
    ACTION_ICONS,
    ACTION_COLORS,
)

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._log_queue: list[AuditLogCreate] = []
        self._queue_lock = asyncio.Lock()

    # ========================================================================
    # AUDIT LOG OPERATIONS
    # ========================================================================

    async def log(
        self,
        action: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        request_body: Optional[dict] = None,
        response_status: Optional[int] = None,
        duration_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditLog:
        """Create an audit log entry"""
        # Parse action to extract category and type
        action_parts = action.split(".")
        action_category = action_parts[0] if len(action_parts) >= 1 else None
        action_type = action_parts[1] if len(action_parts) >= 2 else None

        # Sanitize request body
        sanitized_body = sanitize_request_body(request_body) if request_body else None

        audit_log = AuditLog(
            action=action,
            action_category=action_category,
            action_type=action_type,
            user_id=user_id,
            user_email=user_email,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            request_method=request_method,
            request_path=request_path,
            request_body=sanitized_body,
            response_status=response_status,
            duration_ms=duration_ms,
            workspace_id=workspace_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            success=1 if success else 0,
            error_message=error_message,
            metadata=metadata or {},
        )

        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)

        # Check for security anomalies
        await self._check_security_anomalies(audit_log)

        return audit_log

    async def log_async(self, data: AuditLogCreate) -> None:
        """Queue an audit log for async writing (non-blocking)"""
        async with self._queue_lock:
            self._log_queue.append(data)

            # Flush queue if it gets too large
            if len(self._log_queue) >= 100:
                await self._flush_queue()

    async def _flush_queue(self) -> None:
        """Flush the audit log queue to database"""
        if not self._log_queue:
            return

        logs_to_write = self._log_queue.copy()
        self._log_queue.clear()

        try:
            for data in logs_to_write:
                await self.log(**data.model_dump())
        except Exception as e:
            logger.error(f"Error flushing audit queue: {e}")

    async def get_log(self, log_id: str) -> Optional[AuditLog]:
        """Get a single audit log by ID"""
        result = await self.db.execute(
            select(AuditLog).where(AuditLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def query_logs(
        self,
        filters: AuditLogFilter,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """Query audit logs with filtering and pagination"""
        query = select(AuditLog)

        # Apply filters
        conditions = []

        if filters.user_id:
            conditions.append(AuditLog.user_id == filters.user_id)
        if filters.user_email:
            conditions.append(AuditLog.user_email.ilike(f"%{filters.user_email}%"))
        if filters.action:
            conditions.append(AuditLog.action == filters.action)
        if filters.action_category:
            conditions.append(AuditLog.action_category == filters.action_category.value)
        if filters.action_type:
            conditions.append(AuditLog.action_type == filters.action_type.value)
        if filters.resource_type:
            conditions.append(AuditLog.resource_type == filters.resource_type)
        if filters.resource_id:
            conditions.append(AuditLog.resource_id == filters.resource_id)
        if filters.workspace_id:
            conditions.append(AuditLog.workspace_id == filters.workspace_id)
        if filters.ip_address:
            conditions.append(AuditLog.ip_address == filters.ip_address)
        if filters.success_only is not None:
            conditions.append(AuditLog.success == (1 if filters.success_only else 0))
        if filters.start_date:
            conditions.append(AuditLog.timestamp >= filters.start_date)
        if filters.end_date:
            conditions.append(AuditLog.timestamp <= filters.end_date)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count(AuditLog.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(desc(AuditLog.timestamp))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def get_summary(
        self,
        workspace_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AuditLogSummary:
        """Get summary statistics for audit logs"""
        conditions = []

        if workspace_id:
            conditions.append(AuditLog.workspace_id == workspace_id)
        if start_date:
            conditions.append(AuditLog.timestamp >= start_date)
        if end_date:
            conditions.append(AuditLog.timestamp <= end_date)

        where_clause = and_(*conditions) if conditions else True

        # Total events
        total_result = await self.db.execute(
            select(func.count(AuditLog.id)).where(where_clause)
        )
        total_events = total_result.scalar() or 0

        # Successful events
        success_result = await self.db.execute(
            select(func.count(AuditLog.id)).where(
                and_(where_clause, AuditLog.success == 1)
            )
        )
        successful_events = success_result.scalar() or 0

        # Unique users
        users_result = await self.db.execute(
            select(func.count(func.distinct(AuditLog.user_id))).where(where_clause)
        )
        unique_users = users_result.scalar() or 0

        # Top actions
        top_actions_result = await self.db.execute(
            select(AuditLog.action, func.count(AuditLog.id).label("count"))
            .where(where_clause)
            .group_by(AuditLog.action)
            .order_by(desc("count"))
            .limit(10)
        )
        top_actions = [
            {"action": row[0], "count": row[1]}
            for row in top_actions_result.all()
        ]

        # Activity by category
        category_result = await self.db.execute(
            select(AuditLog.action_category, func.count(AuditLog.id).label("count"))
            .where(where_clause)
            .group_by(AuditLog.action_category)
        )
        activity_by_category = {
            row[0]: row[1]
            for row in category_result.all()
            if row[0]
        }

        return AuditLogSummary(
            total_events=total_events,
            successful_events=successful_events,
            failed_events=total_events - successful_events,
            unique_users=unique_users,
            top_actions=top_actions,
            activity_by_hour=[],  # Could add hourly breakdown
            activity_by_category=activity_by_category,
        )

    async def get_activity_timeline(
        self,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[ActivityTimelineEntry]:
        """Get activity timeline"""
        query = select(AuditLog)

        conditions = []
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if workspace_id:
            conditions.append(AuditLog.workspace_id == workspace_id)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(AuditLog.timestamp)).limit(limit)

        result = await self.db.execute(query)
        logs = result.scalars().all()

        timeline = []
        for log in logs:
            description = format_action_description(
                log.action,
                log.resource_type,
                log.resource_name,
            )

            timeline.append(ActivityTimelineEntry(
                timestamp=log.timestamp,
                action=log.action,
                description=description,
                user_name=log.user_name,
                user_email=log.user_email,
                resource_type=log.resource_type,
                resource_name=log.resource_name,
                success=log.success == 1,
                icon=ACTION_ICONS.get(log.action),
                color=ACTION_COLORS.get(log.action),
            ))

        return timeline

    async def get_user_activity(self, user_id: str) -> UserActivitySummary:
        """Get activity summary for a specific user"""
        # Total actions
        total_result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(AuditLog.user_id == user_id)
        )
        total_actions = total_result.scalar() or 0

        # Last active
        last_active_result = await self.db.execute(
            select(func.max(AuditLog.timestamp))
            .where(AuditLog.user_id == user_id)
        )
        last_active = last_active_result.scalar()

        # Login count
        login_result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.action == AuditAction.AUTH_LOGIN,
                )
            )
        )
        login_count = login_result.scalar() or 0

        # Failed login count
        failed_login_result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.action == AuditAction.AUTH_LOGIN_FAILED,
                )
            )
        )
        failed_login_count = failed_login_result.scalar() or 0

        # Most used features
        features_result = await self.db.execute(
            select(AuditLog.action_category, func.count(AuditLog.id).label("count"))
            .where(AuditLog.user_id == user_id)
            .group_by(AuditLog.action_category)
            .order_by(desc("count"))
            .limit(5)
        )
        most_used_features = [
            {"category": row[0], "count": row[1]}
            for row in features_result.all()
            if row[0]
        ]

        # Get user email
        user_result = await self.db.execute(
            select(AuditLog.user_email, AuditLog.user_name)
            .where(AuditLog.user_id == user_id)
            .limit(1)
        )
        user_row = user_result.first()

        return UserActivitySummary(
            user_id=user_id,
            user_email=user_row[0] if user_row else None,
            user_name=user_row[1] if user_row else None,
            total_actions=total_actions,
            last_active=last_active,
            most_used_features=most_used_features,
            login_count=login_count,
            failed_login_count=failed_login_count,
        )

    # ========================================================================
    # SECURITY ALERTS
    # ========================================================================

    async def create_alert(
        self,
        alert_type: str,
        severity: AlertSeverity,
        title: str,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        related_audit_ids: list[str] = None,
        workspace_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SecurityAlert:
        """Create a security alert"""
        alert = SecurityAlert(
            alert_type=alert_type,
            severity=severity.value,
            title=title,
            description=description,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            related_audit_ids=related_audit_ids or [],
            workspace_id=workspace_id,
            metadata=metadata or {},
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        logger.warning(f"Security alert created: {alert_type} - {title}")

        return alert

    async def get_alert(self, alert_id: str) -> Optional[SecurityAlert]:
        """Get a security alert by ID"""
        result = await self.db.execute(
            select(SecurityAlert).where(SecurityAlert.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def update_alert(
        self,
        alert_id: str,
        status: Optional[AlertStatus] = None,
        resolution_notes: Optional[str] = None,
        resolved_by: Optional[str] = None,
    ) -> Optional[SecurityAlert]:
        """Update a security alert"""
        alert = await self.get_alert(alert_id)
        if not alert:
            return None

        if status:
            alert.status = status.value
            if status in [AlertStatus.RESOLVED, AlertStatus.DISMISSED]:
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = resolved_by

        if resolution_notes:
            alert.resolution_notes = resolution_notes

        await self.db.commit()
        await self.db.refresh(alert)

        return alert

    async def query_alerts(
        self,
        filters: SecurityAlertFilter,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[SecurityAlert], int]:
        """Query security alerts with filtering"""
        query = select(SecurityAlert)

        conditions = []
        if filters.alert_type:
            conditions.append(SecurityAlert.alert_type == filters.alert_type)
        if filters.severity:
            conditions.append(SecurityAlert.severity == filters.severity.value)
        if filters.status:
            conditions.append(SecurityAlert.status == filters.status.value)
        if filters.user_id:
            conditions.append(SecurityAlert.user_id == filters.user_id)
        if filters.workspace_id:
            conditions.append(SecurityAlert.workspace_id == filters.workspace_id)
        if filters.start_date:
            conditions.append(SecurityAlert.created_at >= filters.start_date)
        if filters.end_date:
            conditions.append(SecurityAlert.created_at <= filters.end_date)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count(SecurityAlert.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(desc(SecurityAlert.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        alerts = list(result.scalars().all())

        return alerts, total

    # ========================================================================
    # SECURITY ANOMALY DETECTION
    # ========================================================================

    async def _check_security_anomalies(self, log: AuditLog) -> None:
        """Check for security anomalies and create alerts if needed"""
        try:
            # Check for brute force attempts
            if log.action == AuditAction.AUTH_LOGIN_FAILED:
                await self._check_brute_force(log)

            # Check for unusual data access patterns
            if log.action in [AuditAction.DATA_EXPORT, AuditAction.QUERY_EXECUTE]:
                await self._check_unusual_data_access(log)

        except Exception as e:
            logger.error(f"Error checking security anomalies: {e}")

    async def _check_brute_force(self, log: AuditLog) -> None:
        """Check for brute force login attempts"""
        # Count failed logins in last 15 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=15)

        result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(
                and_(
                    AuditLog.action == AuditAction.AUTH_LOGIN_FAILED,
                    AuditLog.timestamp >= cutoff,
                    or_(
                        AuditLog.ip_address == log.ip_address,
                        AuditLog.user_email == log.user_email,
                    )
                )
            )
        )
        failed_count = result.scalar() or 0

        if failed_count >= 5:
            # Check if alert already exists
            existing = await self.db.execute(
                select(SecurityAlert)
                .where(
                    and_(
                        SecurityAlert.alert_type == AlertType.BRUTE_FORCE_ATTEMPT,
                        SecurityAlert.status == "open",
                        or_(
                            SecurityAlert.ip_address == log.ip_address,
                            SecurityAlert.user_email == log.user_email,
                        ),
                        SecurityAlert.created_at >= cutoff,
                    )
                )
            )

            if not existing.scalar_one_or_none():
                await self.create_alert(
                    alert_type=AlertType.BRUTE_FORCE_ATTEMPT,
                    severity=AlertSeverity.HIGH,
                    title=f"Brute force attempt detected",
                    description=f"{failed_count} failed login attempts in 15 minutes from IP {log.ip_address}",
                    user_email=log.user_email,
                    ip_address=log.ip_address,
                )

    async def _check_unusual_data_access(self, log: AuditLog) -> None:
        """Check for unusual data access patterns"""
        # Count data exports in last hour
        cutoff = datetime.utcnow() - timedelta(hours=1)

        result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(
                and_(
                    AuditLog.action.in_([AuditAction.DATA_EXPORT, AuditAction.QUERY_EXECUTE]),
                    AuditLog.user_id == log.user_id,
                    AuditLog.timestamp >= cutoff,
                )
            )
        )
        export_count = result.scalar() or 0

        if export_count >= 20:
            # Check if alert already exists
            existing = await self.db.execute(
                select(SecurityAlert)
                .where(
                    and_(
                        SecurityAlert.alert_type == AlertType.MASS_DATA_EXPORT,
                        SecurityAlert.status == "open",
                        SecurityAlert.user_id == log.user_id,
                        SecurityAlert.created_at >= cutoff,
                    )
                )
            )

            if not existing.scalar_one_or_none():
                await self.create_alert(
                    alert_type=AlertType.MASS_DATA_EXPORT,
                    severity=AlertSeverity.MEDIUM,
                    title=f"Unusual data access pattern detected",
                    description=f"User performed {export_count} data exports/queries in the last hour",
                    user_id=str(log.user_id),
                    user_email=log.user_email,
                )

    # ========================================================================
    # DASHBOARD STATS
    # ========================================================================

    async def get_dashboard_stats(
        self,
        workspace_id: Optional[str] = None,
    ) -> AuditDashboardStats:
        """Get statistics for the audit dashboard"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)

        base_condition = AuditLog.workspace_id == workspace_id if workspace_id else True

        # Events today
        today_result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(and_(base_condition, AuditLog.timestamp >= today))
        )
        total_events_today = today_result.scalar() or 0

        # Events this week
        week_result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(and_(base_condition, AuditLog.timestamp >= week_ago))
        )
        total_events_week = week_result.scalar() or 0

        # Active users today
        users_result = await self.db.execute(
            select(func.count(func.distinct(AuditLog.user_id)))
            .where(and_(base_condition, AuditLog.timestamp >= today))
        )
        active_users_today = users_result.scalar() or 0

        # Failed logins today
        failed_result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(
                and_(
                    base_condition,
                    AuditLog.timestamp >= today,
                    AuditLog.action == AuditAction.AUTH_LOGIN_FAILED,
                )
            )
        )
        failed_logins_today = failed_result.scalar() or 0

        # Open alerts
        alert_condition = SecurityAlert.workspace_id == workspace_id if workspace_id else True
        open_alerts_result = await self.db.execute(
            select(func.count(SecurityAlert.id))
            .where(and_(alert_condition, SecurityAlert.status == "open"))
        )
        open_alerts = open_alerts_result.scalar() or 0

        # Critical alerts
        critical_result = await self.db.execute(
            select(func.count(SecurityAlert.id))
            .where(
                and_(
                    alert_condition,
                    SecurityAlert.status == "open",
                    SecurityAlert.severity == "critical",
                )
            )
        )
        critical_alerts = critical_result.scalar() or 0

        # Top users
        top_users_result = await self.db.execute(
            select(AuditLog.user_email, func.count(AuditLog.id).label("count"))
            .where(and_(base_condition, AuditLog.timestamp >= today))
            .group_by(AuditLog.user_email)
            .order_by(desc("count"))
            .limit(5)
        )
        top_users = [
            {"email": row[0], "count": row[1]}
            for row in top_users_result.all()
            if row[0]
        ]

        # Recent alerts
        recent_alerts_result = await self.db.execute(
            select(SecurityAlert)
            .where(alert_condition)
            .order_by(desc(SecurityAlert.created_at))
            .limit(5)
        )
        recent_alerts = [
            SecurityAlertResponse(
                id=str(a.id),
                alert_type=a.alert_type,
                severity=AlertSeverity(a.severity),
                title=a.title,
                description=a.description,
                created_at=a.created_at,
                resolved_at=a.resolved_at,
                user_id=str(a.user_id) if a.user_id else None,
                user_email=a.user_email,
                ip_address=a.ip_address,
                related_audit_ids=a.related_audit_ids or [],
                workspace_id=str(a.workspace_id) if a.workspace_id else None,
                status=AlertStatus(a.status),
                resolved_by=str(a.resolved_by) if a.resolved_by else None,
                resolution_notes=a.resolution_notes,
                metadata=a.extra_metadata or {},
            )
            for a in recent_alerts_result.scalars().all()
        ]

        return AuditDashboardStats(
            total_events_today=total_events_today,
            total_events_week=total_events_week,
            active_users_today=active_users_today,
            failed_logins_today=failed_logins_today,
            open_alerts=open_alerts,
            critical_alerts=critical_alerts,
            top_users=top_users,
            recent_alerts=recent_alerts,
        )


    async def detect_anomalies(
        self,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> list[SecurityAlert]:
        """Detect anomalies in recent activity (stub implementation)"""
        # TODO: Implement full anomaly detection
        return []

    async def archive_old_logs(self, days_to_keep: int = 90) -> int:
        """Archive logs older than specified days (stub implementation)"""
        # TODO: Implement log archiving
        return 0

    async def get_archived_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list:
        """Get archived logs (stub implementation)"""
        # TODO: Implement archived log retrieval
        return []


def get_audit_service(db: AsyncSession) -> AuditService:
    """Factory function to get audit service instance"""
    return AuditService(db)
