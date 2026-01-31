"""
Report Subscription Service

Business logic for report subscription management including
subscriptions, notifications, digests, and preferences.
"""

from datetime import datetime, timedelta
from typing import Optional, Any
import uuid

from app.schemas.report_subscription import (
    SubscriptionType, SubscriptionStatus, ResourceType, NotificationChannel,
    DigestFrequency, ThresholdOperator,
    Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionListResponse,
    SubscriptionNotification, NotificationDelivery, NotificationListResponse,
    Digest, DigestItem, DigestListResponse,
    GlobalNotificationPreferences, UserSubscriptionPreferences,
    SubscriptionStats, NotificationConfig, ThresholdCondition,
    evaluate_threshold, is_in_quiet_hours,
)


class ReportSubscriptionService:
    """Service for managing report subscriptions."""

    def __init__(self):
        # In-memory stores (replace with database in production)
        self.subscriptions: dict[str, Subscription] = {}
        self.notifications: dict[str, SubscriptionNotification] = {}
        self.digests: dict[str, Digest] = {}
        self.user_preferences: dict[str, UserSubscriptionPreferences] = {}

    # Subscription CRUD Operations

    def create_subscription(
        self,
        user_id: str,
        data: SubscriptionCreate,
        organization_id: Optional[str] = None,
    ) -> Subscription:
        """Create a new subscription."""
        subscription_id = f"sub-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        subscription = Subscription(
            id=subscription_id,
            user_id=user_id,
            organization_id=organization_id,
            resource_type=data.resource_type,
            resource_id=data.resource_id,
            resource_name=data.resource_name,
            subscription_type=data.subscription_type,
            notification_channels=data.notification_channels,
            status=SubscriptionStatus.ACTIVE if data.is_active else SubscriptionStatus.PAUSED,
            is_active=data.is_active,
            schedule=data.schedule,
            digest_config=data.digest_config,
            threshold_conditions=data.threshold_conditions,
            filters=data.filters,
            expires_at=data.expires_at,
            created_at=now,
            updated_at=now,
        )

        self.subscriptions[subscription_id] = subscription
        return subscription

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.subscriptions.get(subscription_id)

    def list_subscriptions(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None,
        subscription_type: Optional[SubscriptionType] = None,
        status: Optional[SubscriptionStatus] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> SubscriptionListResponse:
        """List subscriptions with filtering."""
        subscriptions = list(self.subscriptions.values())

        if user_id:
            subscriptions = [s for s in subscriptions if s.user_id == user_id]

        if organization_id:
            subscriptions = [s for s in subscriptions if s.organization_id == organization_id]

        if resource_type:
            subscriptions = [s for s in subscriptions if s.resource_type == resource_type]

        if resource_id:
            subscriptions = [s for s in subscriptions if s.resource_id == resource_id]

        if subscription_type:
            subscriptions = [s for s in subscriptions if s.subscription_type == subscription_type]

        if status:
            subscriptions = [s for s in subscriptions if s.status == status]

        if is_active is not None:
            subscriptions = [s for s in subscriptions if s.is_active == is_active]

        # Sort by created_at descending
        subscriptions.sort(key=lambda x: x.created_at, reverse=True)

        total = len(subscriptions)
        subscriptions = subscriptions[skip:skip + limit]

        return SubscriptionListResponse(subscriptions=subscriptions, total=total)

    def update_subscription(
        self,
        subscription_id: str,
        data: SubscriptionUpdate,
    ) -> Optional[Subscription]:
        """Update a subscription."""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return None

        if data.resource_name is not None:
            subscription.resource_name = data.resource_name

        if data.subscription_type is not None:
            subscription.subscription_type = data.subscription_type

        if data.notification_channels is not None:
            subscription.notification_channels = data.notification_channels

        if data.schedule is not None:
            subscription.schedule = data.schedule

        if data.digest_config is not None:
            subscription.digest_config = data.digest_config

        if data.threshold_conditions is not None:
            subscription.threshold_conditions = data.threshold_conditions

        if data.filters is not None:
            subscription.filters = data.filters

        if data.is_active is not None:
            subscription.is_active = data.is_active
            if data.is_active and subscription.status == SubscriptionStatus.PAUSED:
                subscription.status = SubscriptionStatus.ACTIVE
            elif not data.is_active and subscription.status == SubscriptionStatus.ACTIVE:
                subscription.status = SubscriptionStatus.PAUSED

        if data.status is not None:
            subscription.status = data.status

        if data.expires_at is not None:
            subscription.expires_at = data.expires_at

        subscription.updated_at = datetime.utcnow()

        return subscription

    def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a subscription."""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            return True
        return False

    def pause_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Pause a subscription."""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return None

        subscription.is_active = False
        subscription.status = SubscriptionStatus.PAUSED
        subscription.updated_at = datetime.utcnow()
        return subscription

    def resume_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Resume a paused subscription."""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return None

        subscription.is_active = True
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.updated_at = datetime.utcnow()
        return subscription

    # Notification Management

    def create_notification(
        self,
        subscription: Subscription,
        notification_type: str,
        title: str,
        message: str,
        data: dict[str, Any] = {},
    ) -> SubscriptionNotification:
        """Create and send a notification."""
        notification_id = f"notif-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        # Check user preferences for quiet hours
        preferences = self.get_user_preferences(subscription.user_id)
        if preferences and is_in_quiet_hours(preferences.global_preferences):
            # Queue for later delivery
            pass

        # Create deliveries for each channel
        deliveries = []
        for channel_config in subscription.notification_channels:
            if not channel_config.enabled:
                continue

            delivery = NotificationDelivery(
                channel=channel_config.channel,
                success=True,  # Simulated
                delivered_at=now,
            )
            deliveries.append(delivery)

        notification = SubscriptionNotification(
            id=notification_id,
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            resource_type=subscription.resource_type,
            resource_id=subscription.resource_id,
            resource_name=subscription.resource_name,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data,
            deliveries=deliveries,
            created_at=now,
        )

        self.notifications[notification_id] = notification

        # Update subscription stats
        subscription.last_notified_at = now
        subscription.notification_count += 1

        return notification

    def get_notification(self, notification_id: str) -> Optional[SubscriptionNotification]:
        """Get notification by ID."""
        return self.notifications.get(notification_id)

    def list_notifications(
        self,
        user_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> NotificationListResponse:
        """List notifications with filtering."""
        notifications = list(self.notifications.values())

        if user_id:
            notifications = [n for n in notifications if n.user_id == user_id]

        if subscription_id:
            notifications = [n for n in notifications if n.subscription_id == subscription_id]

        if resource_type:
            notifications = [n for n in notifications if n.resource_type == resource_type]

        if unread_only:
            notifications = [n for n in notifications if not n.read]

        # Sort by created_at descending
        notifications.sort(key=lambda x: x.created_at, reverse=True)

        unread_count = len([n for n in notifications if not n.read])
        total = len(notifications)
        notifications = notifications[skip:skip + limit]

        return NotificationListResponse(
            notifications=notifications,
            total=total,
            unread_count=unread_count,
        )

    def mark_notification_read(self, notification_id: str) -> Optional[SubscriptionNotification]:
        """Mark a notification as read."""
        notification = self.notifications.get(notification_id)
        if not notification:
            return None

        notification.read = True
        notification.read_at = datetime.utcnow()
        return notification

    def mark_all_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        count = 0
        now = datetime.utcnow()
        for notification in self.notifications.values():
            if notification.user_id == user_id and not notification.read:
                notification.read = True
                notification.read_at = now
                count += 1
        return count

    def record_click(self, notification_id: str) -> Optional[SubscriptionNotification]:
        """Record that a notification was clicked."""
        notification = self.notifications.get(notification_id)
        if not notification:
            return None

        notification.clicked = True
        notification.clicked_at = datetime.utcnow()
        if not notification.read:
            notification.read = True
            notification.read_at = notification.clicked_at
        return notification

    # Digest Management

    def create_digest(
        self,
        user_id: str,
        digest_type: DigestFrequency,
        items: list[DigestItem],
    ) -> Digest:
        """Create a digest."""
        digest_id = f"digest-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        # Calculate period
        if digest_type == DigestFrequency.DAILY:
            period_start = now - timedelta(days=1)
        elif digest_type == DigestFrequency.WEEKLY:
            period_start = now - timedelta(weeks=1)
        elif digest_type == DigestFrequency.BIWEEKLY:
            period_start = now - timedelta(weeks=2)
        else:  # Monthly
            period_start = now - timedelta(days=30)

        # Generate highlights
        highlights = []
        if items:
            highlights.append(f"{len(items)} updates across your subscriptions")

        digest = Digest(
            id=digest_id,
            user_id=user_id,
            digest_type=digest_type,
            period_start=period_start,
            period_end=now,
            items=items,
            total_items=len(items),
            highlights=highlights,
            created_at=now,
        )

        self.digests[digest_id] = digest
        return digest

    def get_digest(self, digest_id: str) -> Optional[Digest]:
        """Get digest by ID."""
        return self.digests.get(digest_id)

    def list_digests(
        self,
        user_id: str,
        digest_type: Optional[DigestFrequency] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> DigestListResponse:
        """List digests for a user."""
        digests = [d for d in self.digests.values() if d.user_id == user_id]

        if digest_type:
            digests = [d for d in digests if d.digest_type == digest_type]

        digests.sort(key=lambda x: x.created_at, reverse=True)

        total = len(digests)
        digests = digests[skip:skip + limit]

        return DigestListResponse(digests=digests, total=total)

    def send_digest(self, digest_id: str) -> bool:
        """Mark digest as sent."""
        digest = self.digests.get(digest_id)
        if not digest:
            return False

        digest.sent_at = datetime.utcnow()
        return True

    # User Preferences Management

    def get_user_preferences(self, user_id: str) -> Optional[UserSubscriptionPreferences]:
        """Get user's subscription preferences."""
        return self.user_preferences.get(user_id)

    def update_user_preferences(
        self,
        user_id: str,
        global_preferences: Optional[GlobalNotificationPreferences] = None,
        channel_preferences: Optional[dict[str, bool]] = None,
        resource_preferences: Optional[dict[str, bool]] = None,
        muted_resources: Optional[list[str]] = None,
    ) -> UserSubscriptionPreferences:
        """Update user's subscription preferences."""
        existing = self.user_preferences.get(user_id)

        if existing:
            if global_preferences:
                existing.global_preferences = global_preferences
            if channel_preferences:
                existing.channel_preferences.update(channel_preferences)
            if resource_preferences:
                existing.resource_preferences.update(resource_preferences)
            if muted_resources is not None:
                existing.muted_resources = muted_resources
            existing.updated_at = datetime.utcnow()
            return existing
        else:
            preferences = UserSubscriptionPreferences(
                user_id=user_id,
                global_preferences=global_preferences or GlobalNotificationPreferences(),
                channel_preferences=channel_preferences or {},
                resource_preferences=resource_preferences or {},
                muted_resources=muted_resources or [],
                updated_at=datetime.utcnow(),
            )
            self.user_preferences[user_id] = preferences
            return preferences

    def mute_resource(self, user_id: str, resource_id: str) -> UserSubscriptionPreferences:
        """Mute notifications for a specific resource."""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            preferences = self.update_user_preferences(user_id)

        if resource_id not in preferences.muted_resources:
            preferences.muted_resources.append(resource_id)
            preferences.updated_at = datetime.utcnow()

        return preferences

    def unmute_resource(self, user_id: str, resource_id: str) -> UserSubscriptionPreferences:
        """Unmute notifications for a specific resource."""
        preferences = self.get_user_preferences(user_id)
        if not preferences:
            return self.update_user_preferences(user_id)

        if resource_id in preferences.muted_resources:
            preferences.muted_resources.remove(resource_id)
            preferences.updated_at = datetime.utcnow()

        return preferences

    # Threshold Evaluation

    def check_thresholds(
        self,
        subscription: Subscription,
        current_values: dict[str, float],
        previous_values: Optional[dict[str, float]] = None,
    ) -> list[ThresholdCondition]:
        """Check which threshold conditions are triggered."""
        triggered = []

        for condition in subscription.threshold_conditions:
            current = current_values.get(condition.metric_name)
            if current is None:
                continue

            previous = previous_values.get(condition.metric_name) if previous_values else None

            if evaluate_threshold(current, condition, previous):
                triggered.append(condition)

        return triggered

    def process_threshold_subscriptions(
        self,
        resource_type: ResourceType,
        resource_id: str,
        current_values: dict[str, float],
        previous_values: Optional[dict[str, float]] = None,
    ) -> list[SubscriptionNotification]:
        """Process all threshold subscriptions for a resource."""
        notifications = []

        subscriptions = [
            s for s in self.subscriptions.values()
            if s.resource_type == resource_type
            and s.resource_id == resource_id
            and s.subscription_type == SubscriptionType.ON_THRESHOLD
            and s.is_active
            and s.status == SubscriptionStatus.ACTIVE
        ]

        for subscription in subscriptions:
            triggered = self.check_thresholds(subscription, current_values, previous_values)

            for condition in triggered:
                notification = self.create_notification(
                    subscription=subscription,
                    notification_type="threshold",
                    title=f"Threshold Alert: {condition.metric_name}",
                    message=f"{condition.metric_name} has crossed the threshold",
                    data={
                        "condition": condition.model_dump(),
                        "current_value": current_values.get(condition.metric_name),
                        "previous_value": previous_values.get(condition.metric_name) if previous_values else None,
                    },
                )
                notifications.append(notification)

        return notifications

    # Statistics

    def get_stats(self, organization_id: str) -> SubscriptionStats:
        """Get subscription statistics for organization."""
        subscriptions = [s for s in self.subscriptions.values() if s.organization_id == organization_id]
        notifications = [n for n in self.notifications.values()
                        if any(s.organization_id == organization_id for s in self.subscriptions.values()
                              if s.id == n.subscription_id)]

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        notifications_today = [n for n in notifications if n.created_at >= today_start]
        notifications_week = [n for n in notifications if n.created_at >= week_start]
        notifications_month = [n for n in notifications if n.created_at >= month_start]

        by_type = {}
        for s in subscriptions:
            t = s.subscription_type.value
            by_type[t] = by_type.get(t, 0) + 1

        by_resource = {}
        for s in subscriptions:
            r = s.resource_type.value
            by_resource[r] = by_resource.get(r, 0) + 1

        by_channel = {}
        for s in subscriptions:
            for nc in s.notification_channels:
                c = nc.channel.value
                by_channel[c] = by_channel.get(c, 0) + 1

        read_notifications = [n for n in notifications if n.read]
        clicked_notifications = [n for n in notifications if n.clicked]

        open_rate = len(read_notifications) / len(notifications) if notifications else 0
        click_rate = len(clicked_notifications) / len(notifications) if notifications else 0

        cancelled = len([s for s in subscriptions if s.status == SubscriptionStatus.CANCELLED])
        total_ever = len(subscriptions) + cancelled
        unsubscribe_rate = cancelled / total_ever if total_ever else 0

        return SubscriptionStats(
            organization_id=organization_id,
            total_subscriptions=len(subscriptions),
            active_subscriptions=len([s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE]),
            subscriptions_by_type=by_type,
            subscriptions_by_resource=by_resource,
            subscriptions_by_channel=by_channel,
            notifications_sent_today=len(notifications_today),
            notifications_sent_this_week=len(notifications_week),
            notifications_sent_this_month=len(notifications_month),
            open_rate=open_rate,
            click_rate=click_rate,
            unsubscribe_rate=unsubscribe_rate,
        )


# Global service instance
report_subscription_service = ReportSubscriptionService()
