"""
Mobile API Endpoints

REST API for mobile optimization features.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.mobile_service import MobileService
from app.schemas.mobile import (
    MobileDashboardLayout,
    MobileChartConfig,
    MobileUserSettings,
    GestureConfig,
    OfflineDataConfig,
    NotificationPreference,
    DeviceInfo,
    MobileAnalyticsEvent,
    MobileDashboardResponse,
    CachedDashboard,
    OfflineSyncStatus,
    PushNotification,
    MobileUsageStats,
    LayoutMode,
)

router = APIRouter()


# Mobile Dashboard Layouts

@router.get("/dashboard/{dashboard_id}/layout", response_model=MobileDashboardLayout)
async def get_mobile_layout(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get mobile layout configuration for a dashboard."""
    service = MobileService(db)
    layout = await service.get_mobile_layout(dashboard_id)

    if not layout:
        raise HTTPException(status_code=404, detail="Mobile layout not found")

    return layout


@router.put("/dashboard/{dashboard_id}/layout", response_model=MobileDashboardLayout)
async def save_mobile_layout(
    dashboard_id: str,
    layout: MobileDashboardLayout,
    db: AsyncSession = Depends(get_db),
):
    """Save mobile layout configuration for a dashboard."""
    layout.dashboard_id = dashboard_id
    service = MobileService(db)
    return await service.save_mobile_layout(layout)


@router.post("/dashboard/{dashboard_id}/layout/generate", response_model=MobileDashboardLayout)
async def generate_mobile_layout(
    dashboard_id: str,
    charts: list[dict],
    db: AsyncSession = Depends(get_db),
):
    """
    Auto-generate a mobile layout for a dashboard.

    Analyzes the charts and creates an optimized mobile layout.
    """
    service = MobileService(db)
    return await service.auto_generate_mobile_layout(dashboard_id, charts)


@router.get("/dashboard/{dashboard_id}", response_model=MobileDashboardResponse)
async def get_mobile_dashboard(
    dashboard_id: str,
    device_width: int = Query(375, description="Device screen width"),
    charts: str = Query("[]", description="Charts data as JSON"),
    filters: str = Query("[]", description="Filters data as JSON"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get mobile-optimized dashboard data.

    Returns the dashboard with optimized charts and layout for the device.
    """
    import json

    try:
        charts_data = json.loads(charts)
        filters_data = json.loads(filters)
    except json.JSONDecodeError:
        charts_data = []
        filters_data = []

    service = MobileService(db)
    return await service.get_mobile_dashboard(
        dashboard_id=dashboard_id,
        device_width=device_width,
        charts_data=charts_data,
        filters_data=filters_data,
    )


# User Settings

@router.get("/settings", response_model=MobileUserSettings)
async def get_user_settings(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get user's mobile settings."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    return await service.get_user_settings(user_id)


@router.put("/settings", response_model=MobileUserSettings)
async def save_user_settings(
    settings: MobileUserSettings,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Save user's mobile settings."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    settings.user_id = user_id

    service = MobileService(db)
    return await service.save_user_settings(settings)


@router.patch("/settings", response_model=MobileUserSettings)
async def update_user_settings(
    updates: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update specific user settings."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    return await service.update_user_settings(user_id, updates)


# Gestures

@router.get("/gestures/defaults")
async def get_default_gestures(
    db: AsyncSession = Depends(get_db),
):
    """Get default gesture bindings."""
    service = MobileService(db)
    return await service.get_gesture_bindings()


@router.put("/settings/gestures", response_model=MobileUserSettings)
async def update_gesture_settings(
    gesture_config: GestureConfig,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update user's gesture settings."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    return await service.update_user_settings(
        user_id,
        {"gesture_config": gesture_config.model_dump()}
    )


# Offline / Caching

@router.post("/cache/dashboard/{dashboard_id}", response_model=CachedDashboard)
async def cache_dashboard(
    dashboard_id: str,
    dashboard_name: str = Query(..., description="Dashboard name"),
    dashboard_data: dict = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Cache a dashboard for offline use.

    Stores the dashboard data locally for offline viewing.
    """
    user_id = "00000000-0000-0000-0000-000000000000"
    if request:
        user_id = getattr(request.state, "user_id", user_id)

    service = MobileService(db)
    return await service.cache_dashboard(
        dashboard_id=dashboard_id,
        dashboard_name=dashboard_name,
        dashboard_data=dashboard_data or {},
        user_id=user_id,
    )


@router.get("/cache/dashboard/{dashboard_id}")
async def get_cached_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get cached dashboard data."""
    service = MobileService(db)
    data = await service.get_cached_dashboard(dashboard_id)

    if not data:
        raise HTTPException(status_code=404, detail="Dashboard not cached")

    return data


@router.get("/cache/dashboards", response_model=list[CachedDashboard])
async def list_cached_dashboards(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """List all cached dashboards."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    return await service.list_cached_dashboards(user_id)


@router.delete("/cache/dashboard/{dashboard_id}")
async def remove_cached_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove a cached dashboard."""
    service = MobileService(db)
    success = await service.remove_cached_dashboard(dashboard_id)

    if not success:
        raise HTTPException(status_code=404, detail="Dashboard not cached")

    return {"message": "Cache removed"}


@router.get("/sync/status", response_model=OfflineSyncStatus)
async def get_sync_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get offline sync status."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    return await service.get_sync_status(user_id)


@router.post("/sync")
async def sync_offline_changes(
    changes: list[dict],
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Sync offline changes to server.

    Uploads pending changes made while offline.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    return await service.sync_offline_changes(user_id, changes)


# Push Notifications

@router.post("/device/register")
async def register_device(
    device_info: DeviceInfo,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a device for push notifications.

    Call this when the app starts or when push token changes.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    return await service.register_device(user_id, device_info)


@router.get("/notifications", response_model=list[PushNotification])
async def get_notifications(
    unread_only: bool = Query(False, description="Only return unread"),
    limit: int = Query(50, ge=1, le=100),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get user's notifications."""
    user_id = "00000000-0000-0000-0000-000000000000"
    if request:
        user_id = getattr(request.state, "user_id", user_id)

    service = MobileService(db)
    return await service.get_notifications(user_id, unread_only, limit)


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    success = await service.mark_notification_read(user_id, notification_id)

    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"message": "Marked as read"}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    count = await service.mark_all_notifications_read(user_id)

    return {"marked_read": count}


@router.put("/settings/notifications", response_model=MobileUserSettings)
async def update_notification_settings(
    preferences: NotificationPreference,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update notification preferences."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = MobileService(db)
    return await service.update_user_settings(
        user_id,
        {"notification_preferences": preferences.model_dump()}
    )


# Analytics

@router.post("/analytics/event")
async def track_analytics_event(
    event: MobileAnalyticsEvent,
    db: AsyncSession = Depends(get_db),
):
    """Track a mobile analytics event."""
    service = MobileService(db)
    await service.track_event(event)
    return {"tracked": True}


@router.get("/analytics/stats", response_model=MobileUsageStats)
async def get_usage_stats(
    days: int = Query(30, ge=1, le=365),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get mobile usage statistics."""
    user_id = None
    if request:
        user_id = getattr(request.state, "user_id", None)

    service = MobileService(db)
    return await service.get_usage_stats(user_id=user_id, days=days)


# Breakpoints

@router.get("/breakpoints")
async def get_breakpoints(
    db: AsyncSession = Depends(get_db),
):
    """Get supported screen breakpoints."""
    service = MobileService(db)
    return await service.get_breakpoints()


# Device Detection

@router.get("/detect")
async def detect_device(
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    screen_width: int = Query(0, description="Screen width"),
    screen_height: int = Query(0, description="Screen height"),
):
    """
    Detect device type from request.

    Returns recommended settings for the device.
    """
    is_mobile = False
    is_tablet = False

    if user_agent:
        ua_lower = user_agent.lower()
        is_mobile = any(x in ua_lower for x in ["mobile", "android", "iphone"])
        is_tablet = any(x in ua_lower for x in ["ipad", "tablet"])

    # Detect from screen size
    if screen_width > 0:
        if screen_width < 640:
            is_mobile = True
        elif screen_width < 1024:
            is_tablet = True

    layout_mode = LayoutMode.DESKTOP
    if is_mobile:
        layout_mode = LayoutMode.MOBILE
    elif is_tablet:
        layout_mode = LayoutMode.TABLET

    return {
        "is_mobile": is_mobile,
        "is_tablet": is_tablet,
        "is_desktop": not is_mobile and not is_tablet,
        "recommended_layout": layout_mode,
        "screen_width": screen_width,
        "screen_height": screen_height,
        "supports_touch": is_mobile or is_tablet,
    }
