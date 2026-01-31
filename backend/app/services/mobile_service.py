"""
Mobile Service

Handles mobile-optimized views, offline caching, and device settings.
"""

import uuid
from typing import Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.mobile import (
    LayoutMode,
    MobileDashboardLayout,
    MobileChartConfig,
    GestureConfig,
    GestureBinding,
    OfflineDataConfig,
    CachedDashboard,
    OfflineSyncStatus,
    NotificationPreference,
    PushNotification,
    MobileUserSettings,
    DeviceInfo,
    MobileAnalyticsEvent,
    MobileUsageStats,
    MobileDashboardResponse,
    SyncStatus,
    DEFAULT_BREAKPOINTS,
    DEFAULT_GESTURE_BINDINGS,
    get_breakpoint_for_width,
    calculate_chart_height,
    simplify_chart_config,
)


logger = logging.getLogger(__name__)


class MobileService:
    """Service for mobile optimization features."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._layouts: dict[str, dict] = {}  # dashboard_id -> layout
        self._user_settings: dict[str, dict] = {}  # user_id -> settings
        self._cached_dashboards: dict[str, dict] = {}  # dashboard_id -> cache
        self._notifications: dict[str, list] = {}  # user_id -> notifications
        self._analytics_events: list[dict] = []

    # Mobile Dashboard Layouts

    async def get_mobile_layout(
        self,
        dashboard_id: str,
    ) -> Optional[MobileDashboardLayout]:
        """Get mobile layout for a dashboard."""
        layout = self._layouts.get(dashboard_id)
        if layout:
            return MobileDashboardLayout(**layout)
        return None

    async def save_mobile_layout(
        self,
        layout: MobileDashboardLayout,
    ) -> MobileDashboardLayout:
        """Save mobile layout for a dashboard."""
        now = datetime.utcnow()

        layout_dict = layout.model_dump()
        layout_dict["updated_at"] = now
        if "created_at" not in layout_dict or not layout_dict["created_at"]:
            layout_dict["created_at"] = now

        self._layouts[layout.dashboard_id] = layout_dict

        return MobileDashboardLayout(**layout_dict)

    async def get_mobile_dashboard(
        self,
        dashboard_id: str,
        device_width: int,
        charts_data: list[dict],
        filters_data: list[dict],
    ) -> MobileDashboardResponse:
        """Get mobile-optimized dashboard response."""
        # Get or create layout
        layout = await self.get_mobile_layout(dashboard_id)
        if not layout:
            layout = MobileDashboardLayout(
                dashboard_id=dashboard_id,
                charts=[
                    MobileChartConfig(chart_id=c.get("id", ""), order=i)
                    for i, c in enumerate(charts_data)
                ],
            )

        # Get breakpoint
        breakpoint = get_breakpoint_for_width(device_width)

        # Optimize charts for mobile
        optimized_charts = []
        for chart in charts_data:
            chart_id = chart.get("id", "")
            mobile_config = next(
                (c for c in layout.charts if c.chart_id == chart_id),
                None
            )

            if mobile_config and not mobile_config.visible:
                continue

            optimized_chart = chart.copy()

            # Simplify for mobile
            if breakpoint.name == "mobile" and layout.layout_mode in [LayoutMode.AUTO, LayoutMode.MOBILE]:
                optimized_chart = simplify_chart_config(optimized_chart)
                if mobile_config:
                    optimized_chart["height"] = mobile_config.height

            optimized_charts.append(optimized_chart)

        # Sort by mobile order
        chart_order = {c.chart_id: c.order for c in layout.charts}
        optimized_charts.sort(key=lambda c: chart_order.get(c.get("id", ""), 999))

        return MobileDashboardResponse(
            dashboard_id=dashboard_id,
            name=f"Dashboard {dashboard_id}",  # In production, get from DB
            layout=layout,
            charts=optimized_charts,
            filters=filters_data[:layout.quick_filters_count] if layout.collapsible_filters else filters_data,
            last_updated=datetime.utcnow(),
            cache_key=f"mobile-{dashboard_id}-{device_width}",
            offline_available=dashboard_id in self._cached_dashboards,
        )

    async def auto_generate_mobile_layout(
        self,
        dashboard_id: str,
        charts: list[dict],
    ) -> MobileDashboardLayout:
        """Auto-generate a mobile layout for a dashboard."""
        chart_configs = []

        for i, chart in enumerate(charts):
            chart_type = chart.get("type", "")
            chart_id = chart.get("id", str(uuid.uuid4()))

            # Determine optimal height based on chart type
            if chart_type in ["kpi", "number", "gauge"]:
                height = 150
            elif chart_type in ["table", "pivot"]:
                height = 300
            else:
                height = 250

            chart_configs.append(MobileChartConfig(
                chart_id=chart_id,
                order=i,
                visible=True,
                height=height,
                simplified=chart_type not in ["table", "pivot"],
                touch_enabled=True,
            ))

        layout = MobileDashboardLayout(
            dashboard_id=dashboard_id,
            enabled=True,
            charts=chart_configs,
            stack_charts=True,
            show_chart_titles=True,
            compact_headers=True,
            pull_to_refresh=True,
        )

        return await self.save_mobile_layout(layout)

    # User Settings

    async def get_user_settings(
        self,
        user_id: str,
    ) -> MobileUserSettings:
        """Get user's mobile settings."""
        settings = self._user_settings.get(user_id)
        if settings:
            return MobileUserSettings(**settings)

        # Return defaults
        return MobileUserSettings(
            user_id=user_id,
            gesture_config=GestureConfig(
                bindings=[GestureBinding(**b.model_dump()) for b in DEFAULT_GESTURE_BINDINGS]
            ),
        )

    async def save_user_settings(
        self,
        settings: MobileUserSettings,
    ) -> MobileUserSettings:
        """Save user's mobile settings."""
        self._user_settings[settings.user_id] = settings.model_dump()
        return settings

    async def update_user_settings(
        self,
        user_id: str,
        updates: dict[str, Any],
    ) -> MobileUserSettings:
        """Update specific user settings."""
        current = await self.get_user_settings(user_id)
        current_dict = current.model_dump()

        for key, value in updates.items():
            if key in current_dict:
                current_dict[key] = value

        updated = MobileUserSettings(**current_dict)
        return await self.save_user_settings(updated)

    # Offline Caching

    async def cache_dashboard(
        self,
        dashboard_id: str,
        dashboard_name: str,
        dashboard_data: dict,
        user_id: str,
    ) -> CachedDashboard:
        """Cache a dashboard for offline use."""
        now = datetime.utcnow()

        # Calculate size (rough estimate)
        import json
        data_str = json.dumps(dashboard_data)
        size_bytes = len(data_str.encode('utf-8'))

        cache_entry = {
            "dashboard_id": dashboard_id,
            "dashboard_name": dashboard_name,
            "cached_at": now,
            "expires_at": now + timedelta(hours=24),
            "size_bytes": size_bytes,
            "sync_status": SyncStatus.SYNCED,
            "charts_cached": len(dashboard_data.get("charts", [])),
            "last_synced_at": now,
            "pending_changes": 0,
            "data": dashboard_data,
        }

        self._cached_dashboards[dashboard_id] = cache_entry

        return CachedDashboard(**{k: v for k, v in cache_entry.items() if k != "data"})

    async def get_cached_dashboard(
        self,
        dashboard_id: str,
    ) -> Optional[dict]:
        """Get cached dashboard data."""
        cache = self._cached_dashboards.get(dashboard_id)
        if not cache:
            return None

        # Check expiration
        if cache["expires_at"] < datetime.utcnow():
            cache["sync_status"] = SyncStatus.PENDING
            return cache.get("data")

        return cache.get("data")

    async def list_cached_dashboards(
        self,
        user_id: str,
    ) -> list[CachedDashboard]:
        """List all cached dashboards."""
        return [
            CachedDashboard(**{k: v for k, v in c.items() if k != "data"})
            for c in self._cached_dashboards.values()
        ]

    async def remove_cached_dashboard(
        self,
        dashboard_id: str,
    ) -> bool:
        """Remove a cached dashboard."""
        if dashboard_id in self._cached_dashboards:
            del self._cached_dashboards[dashboard_id]
            return True
        return False

    async def get_sync_status(
        self,
        user_id: str,
    ) -> OfflineSyncStatus:
        """Get overall offline sync status."""
        caches = list(self._cached_dashboards.values())

        total_size = sum(c.get("size_bytes", 0) for c in caches)
        pending = sum(1 for c in caches if c.get("sync_status") == SyncStatus.PENDING)
        errors = sum(1 for c in caches if c.get("sync_status") == SyncStatus.ERROR)

        settings = await self.get_user_settings(user_id)

        return OfflineSyncStatus(
            enabled=settings.offline_config.enabled,
            last_sync=max((c.get("last_synced_at") for c in caches), default=None),
            next_sync=datetime.utcnow() + timedelta(minutes=15),
            total_cached_mb=total_size / (1024 * 1024),
            max_cache_mb=settings.offline_config.max_cache_size_mb,
            dashboards_cached=len(caches),
            pending_uploads=pending,
            sync_errors=errors,
        )

    async def sync_offline_changes(
        self,
        user_id: str,
        changes: list[dict],
    ) -> dict:
        """Sync offline changes to server."""
        synced = 0
        errors = []

        for change in changes:
            try:
                # Process each change
                # In production, apply to database
                synced += 1
            except Exception as e:
                errors.append({"change": change, "error": str(e)})

        return {
            "synced": synced,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Push Notifications

    async def register_device(
        self,
        user_id: str,
        device_info: DeviceInfo,
    ) -> dict:
        """Register a device for push notifications."""
        # In production, store in database
        return {
            "registered": True,
            "user_id": user_id,
            "device_id": device_info.device_id or str(uuid.uuid4()),
            "platform": device_info.platform,
        }

    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[PushNotification]:
        """Get user's notifications."""
        notifications = self._notifications.get(user_id, [])

        if unread_only:
            notifications = [n for n in notifications if not n.get("read")]

        notifications.sort(key=lambda n: n.get("created_at", datetime.min), reverse=True)
        notifications = notifications[:limit]

        return [PushNotification(**n) for n in notifications]

    async def mark_notification_read(
        self,
        user_id: str,
        notification_id: str,
    ) -> bool:
        """Mark a notification as read."""
        notifications = self._notifications.get(user_id, [])

        for n in notifications:
            if n.get("id") == notification_id:
                n["read"] = True
                n["read_at"] = datetime.utcnow()
                return True

        return False

    async def mark_all_notifications_read(
        self,
        user_id: str,
    ) -> int:
        """Mark all notifications as read."""
        notifications = self._notifications.get(user_id, [])
        now = datetime.utcnow()
        count = 0

        for n in notifications:
            if not n.get("read"):
                n["read"] = True
                n["read_at"] = now
                count += 1

        return count

    async def send_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        notification_type: str,
        data: dict = None,
        action_url: str = None,
    ) -> PushNotification:
        """Send a push notification to a user."""
        notification = {
            "id": str(uuid.uuid4()),
            "title": title,
            "body": body,
            "type": notification_type,
            "data": data or {},
            "action_url": action_url,
            "created_at": datetime.utcnow(),
            "read": False,
        }

        if user_id not in self._notifications:
            self._notifications[user_id] = []

        self._notifications[user_id].append(notification)

        # In production, send via FCM/APNS
        logger.info(f"Notification sent to {user_id}: {title}")

        return PushNotification(**notification)

    # Analytics

    async def track_event(
        self,
        event: MobileAnalyticsEvent,
    ):
        """Track a mobile analytics event."""
        self._analytics_events.append(event.model_dump())

    async def get_usage_stats(
        self,
        user_id: Optional[str] = None,
        days: int = 30,
    ) -> MobileUsageStats:
        """Get mobile usage statistics."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        events = [
            e for e in self._analytics_events
            if e.get("timestamp", datetime.min) >= cutoff
        ]

        if user_id:
            events = [e for e in events if e.get("user_id") == user_id]

        # Calculate stats
        sessions = set()
        total_duration = 0
        dashboard_views = {}
        gesture_usage = {}
        offline_views = 0
        device_types = {}

        for event in events:
            # Session tracking
            device_id = event.get("device_info", {}).get("device_id")
            if device_id:
                sessions.add(device_id)

            # Duration
            if event.get("duration_ms"):
                total_duration += event["duration_ms"]

            # Dashboard views
            if event.get("dashboard_id"):
                dashboard_views[event["dashboard_id"]] = dashboard_views.get(event["dashboard_id"], 0) + 1

            # Gestures
            if event.get("gesture"):
                gesture_usage[event["gesture"]] = gesture_usage.get(event["gesture"], 0) + 1

            # Offline
            if event.get("metadata", {}).get("offline"):
                offline_views += 1

            # Device types
            platform = event.get("device_info", {}).get("platform", "unknown")
            device_types[platform] = device_types.get(platform, 0) + 1

        session_count = len(sessions) or 1
        avg_duration = (total_duration / session_count / 1000 / 60) if total_duration else 0

        # Most viewed dashboards
        most_viewed = [
            {"dashboard_id": k, "views": v}
            for k, v in sorted(dashboard_views.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        return MobileUsageStats(
            total_sessions=session_count,
            total_duration_minutes=int(total_duration / 1000 / 60),
            avg_session_duration_minutes=round(avg_duration, 1),
            most_viewed_dashboards=most_viewed,
            gesture_usage=gesture_usage,
            offline_views=offline_views,
            device_breakdown=device_types,
        )

    # Breakpoints

    async def get_breakpoints(self) -> list[dict]:
        """Get supported breakpoints."""
        return [bp.model_dump() for bp in DEFAULT_BREAKPOINTS]

    async def get_gesture_bindings(self) -> list[dict]:
        """Get default gesture bindings."""
        return [gb.model_dump() for gb in DEFAULT_GESTURE_BINDINGS]
