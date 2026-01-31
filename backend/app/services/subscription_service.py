"""
Subscription and Alert Service

Handles data alerts and dashboard subscriptions.
"""

import uuid
import asyncio
import hashlib
import hmac
import json
from typing import Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
import logging
import httpx
from croniter import croniter

from app.schemas.subscriptions import (
    DataAlertCreate,
    DataAlertUpdate,
    DataAlertResponse,
    AlertThreshold,
    AlertTriggerEvent,
    AlertHistory,
    AlertStatus,
    AlertSeverity,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionDelivery,
    SubscriptionStatus,
    SubscriptionFrequency,
    NotificationChannel,
    NotificationConfig,
    AlertSummary,
    SubscriptionSummary,
    evaluate_threshold,
    build_alert_message,
)


logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing subscriptions and data alerts."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._alerts: dict[str, dict] = {}  # In-memory store (use DB in production)
        self._subscriptions: dict[str, dict] = {}
        self._alert_history: list[dict] = []
        self._subscription_deliveries: list[dict] = []

    # Data Alerts

    async def create_alert(
        self,
        data: DataAlertCreate,
        created_by: str,
    ) -> DataAlertResponse:
        """Create a new data alert."""
        alert_id = str(uuid.uuid4())
        now = datetime.utcnow()

        alert = {
            "id": alert_id,
            "name": data.name,
            "description": data.description,
            "enabled": data.enabled,
            "target_type": data.target_type,
            "target_id": data.target_id,
            "metric_column": data.metric_column,
            "thresholds": [t.model_dump() for t in data.thresholds],
            "evaluation_frequency": data.evaluation_frequency,
            "cooldown_minutes": data.cooldown_minutes,
            "notifications": [n.model_dump() for n in data.notifications],
            "workspace_id": data.workspace_id,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
            "last_evaluated_at": None,
            "last_triggered_at": None,
            "trigger_count": 0,
            "status": AlertStatus.ACTIVE,
            "tags": data.tags,
            "metadata": data.metadata,
        }

        self._alerts[alert_id] = alert

        return self._to_alert_response(alert)

    async def get_alert(self, alert_id: str) -> Optional[DataAlertResponse]:
        """Get an alert by ID."""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None
        return self._to_alert_response(alert)

    async def list_alerts(
        self,
        workspace_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        enabled_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[DataAlertResponse]:
        """List alerts with optional filtering."""
        alerts = list(self._alerts.values())

        if workspace_id:
            alerts = [a for a in alerts if a.get("workspace_id") == workspace_id]
        if target_type:
            alerts = [a for a in alerts if a.get("target_type") == target_type]
        if target_id:
            alerts = [a for a in alerts if a.get("target_id") == target_id]
        if enabled_only:
            alerts = [a for a in alerts if a.get("enabled")]

        # Sort by created_at descending
        alerts.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)

        # Paginate
        alerts = alerts[skip:skip + limit]

        return [self._to_alert_response(a) for a in alerts]

    async def update_alert(
        self,
        alert_id: str,
        data: DataAlertUpdate,
    ) -> Optional[DataAlertResponse]:
        """Update an alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "thresholds" and value is not None:
                alert["thresholds"] = [t.model_dump() if hasattr(t, 'model_dump') else t for t in value]
            elif field == "notifications" and value is not None:
                alert["notifications"] = [n.model_dump() if hasattr(n, 'model_dump') else n for n in value]
            else:
                alert[field] = value

        alert["updated_at"] = datetime.utcnow()

        return self._to_alert_response(alert)

    async def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert."""
        if alert_id in self._alerts:
            del self._alerts[alert_id]
            return True
        return False

    async def pause_alert(self, alert_id: str) -> Optional[DataAlertResponse]:
        """Pause an alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        alert["enabled"] = False
        alert["status"] = AlertStatus.PAUSED
        alert["updated_at"] = datetime.utcnow()

        return self._to_alert_response(alert)

    async def resume_alert(self, alert_id: str) -> Optional[DataAlertResponse]:
        """Resume a paused alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        alert["enabled"] = True
        alert["status"] = AlertStatus.ACTIVE
        alert["updated_at"] = datetime.utcnow()

        return self._to_alert_response(alert)

    async def evaluate_alert(
        self,
        alert_id: str,
        current_value: float,
        previous_value: Optional[float] = None,
    ) -> Optional[AlertTriggerEvent]:
        """Evaluate an alert against current data."""
        alert = self._alerts.get(alert_id)
        if not alert or not alert.get("enabled"):
            return None

        # Check cooldown
        last_triggered = alert.get("last_triggered_at")
        cooldown = alert.get("cooldown_minutes", 60)
        if last_triggered:
            cooldown_end = last_triggered + timedelta(minutes=cooldown)
            if datetime.utcnow() < cooldown_end:
                return None

        # Evaluate thresholds
        triggered_threshold = None
        for threshold_data in alert.get("thresholds", []):
            threshold = AlertThreshold(**threshold_data)
            if evaluate_threshold(threshold, current_value, previous_value):
                triggered_threshold = threshold
                break

        if not triggered_threshold:
            alert["last_evaluated_at"] = datetime.utcnow()
            return None

        # Create trigger event
        trigger_event = AlertTriggerEvent(
            alert_id=alert_id,
            alert_name=alert["name"],
            triggered_at=datetime.utcnow(),
            threshold=triggered_threshold,
            current_value=current_value,
            previous_value=previous_value,
            target_type=alert["target_type"],
            target_id=alert["target_id"],
            severity=triggered_threshold.severity,
            message=build_alert_message(
                alert["name"],
                triggered_threshold,
                current_value,
            ),
        )

        # Update alert state
        alert["last_evaluated_at"] = datetime.utcnow()
        alert["last_triggered_at"] = datetime.utcnow()
        alert["trigger_count"] = alert.get("trigger_count", 0) + 1
        alert["status"] = AlertStatus.TRIGGERED

        # Record history
        history_entry = {
            "id": str(uuid.uuid4()),
            "alert_id": alert_id,
            "triggered_at": trigger_event.triggered_at,
            "threshold_triggered": triggered_threshold.model_dump(),
            "value_at_trigger": current_value,
            "severity": triggered_threshold.severity,
            "notification_sent": False,
            "notification_channels": [],
        }
        self._alert_history.append(history_entry)

        # Send notifications
        await self._send_alert_notifications(alert, trigger_event, history_entry)

        return trigger_event

    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
    ) -> Optional[DataAlertResponse]:
        """Acknowledge a triggered alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        alert["status"] = AlertStatus.ACKNOWLEDGED
        alert["updated_at"] = datetime.utcnow()

        # Update latest history entry
        for history in reversed(self._alert_history):
            if history["alert_id"] == alert_id and not history.get("acknowledged_by"):
                history["acknowledged_by"] = acknowledged_by
                history["acknowledged_at"] = datetime.utcnow()
                break

        return self._to_alert_response(alert)

    async def get_alert_history(
        self,
        alert_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[AlertHistory]:
        """Get alert trigger history."""
        history = self._alert_history

        if alert_id:
            history = [h for h in history if h["alert_id"] == alert_id]

        history.sort(key=lambda x: x.get("triggered_at", datetime.min), reverse=True)
        history = history[:limit]

        return [AlertHistory(**h) for h in history]

    # Dashboard Subscriptions

    async def create_subscription(
        self,
        data: SubscriptionCreate,
        created_by: str,
    ) -> SubscriptionResponse:
        """Create a new dashboard subscription."""
        subscription_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Calculate next send time
        next_send = self._calculate_next_send(data.schedule, now)

        subscription = {
            "id": subscription_id,
            "name": data.name,
            "description": data.description,
            "enabled": data.enabled,
            "dashboard_id": data.dashboard_id,
            "schedule": data.schedule.model_dump(),
            "content": data.content.model_dump(),
            "recipients": data.recipients,
            "notification_channel": data.notification_channel,
            "filter_state": data.filter_state,
            "workspace_id": data.workspace_id,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
            "last_sent_at": None,
            "next_send_at": next_send,
            "send_count": 0,
            "status": SubscriptionStatus.ACTIVE,
            "metadata": data.metadata,
        }

        self._subscriptions[subscription_id] = subscription

        return self._to_subscription_response(subscription)

    async def get_subscription(self, subscription_id: str) -> Optional[SubscriptionResponse]:
        """Get a subscription by ID."""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return None
        return self._to_subscription_response(subscription)

    async def list_subscriptions(
        self,
        workspace_id: Optional[str] = None,
        dashboard_id: Optional[str] = None,
        created_by: Optional[str] = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SubscriptionResponse]:
        """List subscriptions with optional filtering."""
        subscriptions = list(self._subscriptions.values())

        if workspace_id:
            subscriptions = [s for s in subscriptions if s.get("workspace_id") == workspace_id]
        if dashboard_id:
            subscriptions = [s for s in subscriptions if s.get("dashboard_id") == dashboard_id]
        if created_by:
            subscriptions = [s for s in subscriptions if s.get("created_by") == created_by]
        if active_only:
            subscriptions = [s for s in subscriptions if s.get("enabled")]

        subscriptions.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        subscriptions = subscriptions[skip:skip + limit]

        return [self._to_subscription_response(s) for s in subscriptions]

    async def update_subscription(
        self,
        subscription_id: str,
        data: SubscriptionUpdate,
    ) -> Optional[SubscriptionResponse]:
        """Update a subscription."""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "schedule" and value is not None:
                subscription["schedule"] = value.model_dump() if hasattr(value, 'model_dump') else value
                # Recalculate next send time
                from app.schemas.subscriptions import SubscriptionSchedule
                schedule = SubscriptionSchedule(**subscription["schedule"])
                subscription["next_send_at"] = self._calculate_next_send(schedule, datetime.utcnow())
            elif field == "content" and value is not None:
                subscription["content"] = value.model_dump() if hasattr(value, 'model_dump') else value
            else:
                subscription[field] = value

        subscription["updated_at"] = datetime.utcnow()

        return self._to_subscription_response(subscription)

    async def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a subscription."""
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            return True
        return False

    async def pause_subscription(self, subscription_id: str) -> Optional[SubscriptionResponse]:
        """Pause a subscription."""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return None

        subscription["enabled"] = False
        subscription["status"] = SubscriptionStatus.PAUSED
        subscription["updated_at"] = datetime.utcnow()

        return self._to_subscription_response(subscription)

    async def resume_subscription(self, subscription_id: str) -> Optional[SubscriptionResponse]:
        """Resume a paused subscription."""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return None

        subscription["enabled"] = True
        subscription["status"] = SubscriptionStatus.ACTIVE
        subscription["updated_at"] = datetime.utcnow()

        # Recalculate next send time
        from app.schemas.subscriptions import SubscriptionSchedule
        schedule = SubscriptionSchedule(**subscription["schedule"])
        subscription["next_send_at"] = self._calculate_next_send(schedule, datetime.utcnow())

        return self._to_subscription_response(subscription)

    async def send_subscription_now(
        self,
        subscription_id: str,
    ) -> Optional[SubscriptionDelivery]:
        """Manually trigger a subscription delivery."""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return None

        delivery = await self._deliver_subscription(subscription)
        return delivery

    async def get_subscription_deliveries(
        self,
        subscription_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[SubscriptionDelivery]:
        """Get subscription delivery history."""
        deliveries = self._subscription_deliveries

        if subscription_id:
            deliveries = [d for d in deliveries if d["subscription_id"] == subscription_id]

        deliveries.sort(key=lambda x: x.get("sent_at", datetime.min), reverse=True)
        deliveries = deliveries[:limit]

        return [SubscriptionDelivery(**d) for d in deliveries]

    # Summaries

    async def get_alert_summary(
        self,
        workspace_id: Optional[str] = None,
    ) -> AlertSummary:
        """Get summary of alerts."""
        alerts = list(self._alerts.values())

        if workspace_id:
            alerts = [a for a in alerts if a.get("workspace_id") == workspace_id]

        today = datetime.utcnow().date()
        triggered_today = [
            a for a in alerts
            if a.get("last_triggered_at") and a["last_triggered_at"].date() == today
        ]

        by_severity = {}
        for alert in alerts:
            for threshold in alert.get("thresholds", []):
                severity = threshold.get("severity", "warning")
                by_severity[severity] = by_severity.get(severity, 0) + 1

        recent_history = await self.get_alert_history(limit=10)

        return AlertSummary(
            total_alerts=len(alerts),
            active_alerts=len([a for a in alerts if a.get("enabled")]),
            triggered_today=len(triggered_today),
            critical_alerts=by_severity.get("critical", 0),
            alerts_by_severity=by_severity,
            recent_triggers=[
                AlertTriggerEvent(
                    alert_id=h.alert_id,
                    alert_name=self._alerts.get(h.alert_id, {}).get("name", "Unknown"),
                    triggered_at=h.triggered_at,
                    threshold=h.threshold_triggered,
                    current_value=h.value_at_trigger,
                    target_type=self._alerts.get(h.alert_id, {}).get("target_type", ""),
                    target_id=self._alerts.get(h.alert_id, {}).get("target_id", ""),
                    severity=h.severity,
                    message="",
                )
                for h in recent_history
            ],
        )

    async def get_subscription_summary(
        self,
        workspace_id: Optional[str] = None,
    ) -> SubscriptionSummary:
        """Get summary of subscriptions."""
        subscriptions = list(self._subscriptions.values())

        if workspace_id:
            subscriptions = [s for s in subscriptions if s.get("workspace_id") == workspace_id]

        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)

        sent_today = [
            s for s in subscriptions
            if s.get("last_sent_at") and s["last_sent_at"].date() == today
        ]

        sent_this_week = [
            s for s in subscriptions
            if s.get("last_sent_at") and s["last_sent_at"].date() >= week_ago
        ]

        by_frequency = {}
        for sub in subscriptions:
            freq = sub.get("schedule", {}).get("frequency", "unknown")
            by_frequency[freq] = by_frequency.get(freq, 0) + 1

        recent_deliveries = await self.get_subscription_deliveries(limit=10)

        return SubscriptionSummary(
            total_subscriptions=len(subscriptions),
            active_subscriptions=len([s for s in subscriptions if s.get("enabled")]),
            sent_today=len(sent_today),
            sent_this_week=len(sent_this_week),
            subscriptions_by_frequency=by_frequency,
            recent_deliveries=recent_deliveries,
        )

    # Private Methods

    async def _send_alert_notifications(
        self,
        alert: dict,
        trigger_event: AlertTriggerEvent,
        history_entry: dict,
    ):
        """Send notifications for a triggered alert."""
        notifications = alert.get("notifications", [])
        channels_sent = []

        for notification_data in notifications:
            notification = NotificationConfig(**notification_data)
            try:
                if notification.channel == NotificationChannel.EMAIL:
                    await self._send_email_notification(notification, trigger_event)
                    channels_sent.append("email")
                elif notification.channel == NotificationChannel.SLACK:
                    await self._send_slack_notification(notification, trigger_event)
                    channels_sent.append("slack")
                elif notification.channel == NotificationChannel.WEBHOOK:
                    await self._send_webhook_notification(notification, trigger_event)
                    channels_sent.append("webhook")
                elif notification.channel == NotificationChannel.TEAMS:
                    await self._send_teams_notification(notification, trigger_event)
                    channels_sent.append("teams")
            except Exception as e:
                logger.error(f"Failed to send {notification.channel} notification: {e}")

        history_entry["notification_sent"] = len(channels_sent) > 0
        history_entry["notification_channels"] = channels_sent

    async def _send_email_notification(
        self,
        notification: NotificationConfig,
        trigger_event: AlertTriggerEvent,
    ):
        """Send email notification."""
        # In production, integrate with email service (SendGrid, SES, etc.)
        logger.info(f"Would send email for alert: {trigger_event.alert_name}")

    async def _send_slack_notification(
        self,
        notification: NotificationConfig,
        trigger_event: AlertTriggerEvent,
    ):
        """Send Slack notification."""
        if not notification.slack:
            return

        payload = {
            "text": trigger_event.message,
            "username": notification.slack.username,
            "icon_emoji": notification.slack.icon_emoji,
            "attachments": [
                {
                    "color": SEVERITY_COLORS.get(trigger_event.severity, "#808080"),
                    "fields": [
                        {
                            "title": "Alert",
                            "value": trigger_event.alert_name,
                            "short": True,
                        },
                        {
                            "title": "Severity",
                            "value": trigger_event.severity.value,
                            "short": True,
                        },
                        {
                            "title": "Current Value",
                            "value": str(trigger_event.current_value),
                            "short": True,
                        },
                        {
                            "title": "Threshold",
                            "value": str(trigger_event.threshold.value),
                            "short": True,
                        },
                    ],
                    "ts": int(trigger_event.triggered_at.timestamp()),
                }
            ],
        }

        async with httpx.AsyncClient() as client:
            await client.post(notification.slack.webhook_url, json=payload)

    async def _send_webhook_notification(
        self,
        notification: NotificationConfig,
        trigger_event: AlertTriggerEvent,
    ):
        """Send webhook notification."""
        if not notification.webhook:
            return

        payload = trigger_event.model_dump(mode="json")

        headers = notification.webhook.headers.copy()

        # Sign payload if secret is configured
        if notification.webhook.secret:
            payload_str = json.dumps(payload)
            signature = hmac.new(
                notification.webhook.secret.encode(),
                payload_str.encode(),
                hashlib.sha256,
            ).hexdigest()
            headers["X-Signature-256"] = f"sha256={signature}"

        async with httpx.AsyncClient() as client:
            if notification.webhook.method.upper() == "POST":
                await client.post(
                    notification.webhook.url,
                    json=payload,
                    headers=headers,
                )
            elif notification.webhook.method.upper() == "PUT":
                await client.put(
                    notification.webhook.url,
                    json=payload,
                    headers=headers,
                )

    async def _send_teams_notification(
        self,
        notification: NotificationConfig,
        trigger_event: AlertTriggerEvent,
    ):
        """Send Microsoft Teams notification."""
        if not notification.teams:
            return

        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": trigger_event.message,
            "themeColor": SEVERITY_COLORS.get(trigger_event.severity, "808080").replace("#", ""),
            "title": f"Alert: {trigger_event.alert_name}",
            "sections": [
                {
                    "facts": [
                        {"name": "Severity", "value": trigger_event.severity.value},
                        {"name": "Current Value", "value": str(trigger_event.current_value)},
                        {"name": "Threshold", "value": str(trigger_event.threshold.value)},
                        {"name": "Time", "value": trigger_event.triggered_at.isoformat()},
                    ],
                    "text": trigger_event.message,
                }
            ],
        }

        async with httpx.AsyncClient() as client:
            await client.post(notification.teams.webhook_url, json=payload)

    async def _deliver_subscription(
        self,
        subscription: dict,
    ) -> SubscriptionDelivery:
        """Deliver a subscription."""
        delivery_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # In production, generate the actual report here
        # This would involve:
        # 1. Rendering the dashboard with filters
        # 2. Generating PDF/HTML/Excel
        # 3. Sending via the configured channel

        delivery = {
            "id": delivery_id,
            "subscription_id": subscription["id"],
            "sent_at": now,
            "recipients": subscription["recipients"],
            "success": True,
            "error_message": None,
            "file_urls": [],
        }

        self._subscription_deliveries.append(delivery)

        # Update subscription
        subscription["last_sent_at"] = now
        subscription["send_count"] = subscription.get("send_count", 0) + 1

        # Calculate next send time
        from app.schemas.subscriptions import SubscriptionSchedule
        schedule = SubscriptionSchedule(**subscription["schedule"])
        subscription["next_send_at"] = self._calculate_next_send(schedule, now)

        return SubscriptionDelivery(**delivery)

    def _calculate_next_send(
        self,
        schedule,
        from_time: datetime,
    ) -> Optional[datetime]:
        """Calculate next send time for a subscription."""
        if schedule.frequency == SubscriptionFrequency.IMMEDIATE:
            return None

        if schedule.cron_expression:
            cron = croniter(schedule.cron_expression, from_time)
            return cron.get_next(datetime)

        if schedule.frequency == SubscriptionFrequency.HOURLY:
            return from_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        if schedule.frequency == SubscriptionFrequency.DAILY:
            next_day = from_time.date() + timedelta(days=1)
            send_time = schedule.time_of_day or datetime.min.time()
            return datetime.combine(next_day, send_time)

        if schedule.frequency == SubscriptionFrequency.WEEKLY:
            days_ahead = (schedule.day_of_week or 0) - from_time.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_day = from_time.date() + timedelta(days=days_ahead)
            send_time = schedule.time_of_day or datetime.min.time()
            return datetime.combine(next_day, send_time)

        if schedule.frequency == SubscriptionFrequency.MONTHLY:
            next_month = from_time.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=min(schedule.day_of_month or 1, 28))
            send_time = schedule.time_of_day or datetime.min.time()
            return datetime.combine(next_month.date(), send_time)

        return None

    def _to_alert_response(self, alert: dict) -> DataAlertResponse:
        """Convert alert dict to response schema."""
        return DataAlertResponse(
            id=alert["id"],
            name=alert["name"],
            description=alert.get("description"),
            enabled=alert["enabled"],
            target_type=alert["target_type"],
            target_id=alert["target_id"],
            metric_column=alert.get("metric_column"),
            thresholds=[AlertThreshold(**t) for t in alert.get("thresholds", [])],
            evaluation_frequency=alert["evaluation_frequency"],
            cooldown_minutes=alert["cooldown_minutes"],
            notifications=[NotificationConfig(**n) for n in alert.get("notifications", [])],
            workspace_id=alert.get("workspace_id"),
            created_by=alert["created_by"],
            created_at=alert["created_at"],
            updated_at=alert["updated_at"],
            last_evaluated_at=alert.get("last_evaluated_at"),
            last_triggered_at=alert.get("last_triggered_at"),
            trigger_count=alert.get("trigger_count", 0),
            status=alert.get("status", AlertStatus.ACTIVE),
            tags=alert.get("tags", []),
            metadata=alert.get("metadata", {}),
        )

    def _to_subscription_response(self, subscription: dict) -> SubscriptionResponse:
        """Convert subscription dict to response schema."""
        from app.schemas.subscriptions import SubscriptionSchedule, SubscriptionContent

        return SubscriptionResponse(
            id=subscription["id"],
            name=subscription["name"],
            description=subscription.get("description"),
            enabled=subscription["enabled"],
            dashboard_id=subscription["dashboard_id"],
            schedule=SubscriptionSchedule(**subscription["schedule"]),
            content=SubscriptionContent(**subscription["content"]),
            recipients=subscription["recipients"],
            notification_channel=subscription["notification_channel"],
            filter_state=subscription.get("filter_state"),
            workspace_id=subscription.get("workspace_id"),
            created_by=subscription["created_by"],
            created_at=subscription["created_at"],
            updated_at=subscription["updated_at"],
            last_sent_at=subscription.get("last_sent_at"),
            next_send_at=subscription.get("next_send_at"),
            send_count=subscription.get("send_count", 0),
            status=subscription.get("status", SubscriptionStatus.ACTIVE),
            metadata=subscription.get("metadata", {}),
        )


# Severity colors for notifications
SEVERITY_COLORS = {
    AlertSeverity.INFO: "#3b82f6",
    AlertSeverity.WARNING: "#f59e0b",
    AlertSeverity.CRITICAL: "#ef4444",
}
