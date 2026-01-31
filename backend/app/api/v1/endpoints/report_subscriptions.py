"""
Report Subscriptions API Endpoints

REST API for managing report subscriptions, notifications,
digests, and user preferences.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.report_subscription import (
    SubscriptionType, SubscriptionStatus, ResourceType, DigestFrequency,
    Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionListResponse,
    SubscriptionNotification, NotificationListResponse,
    Digest, DigestListResponse,
    GlobalNotificationPreferences, UserSubscriptionPreferences,
    SubscriptionStats,
)
from app.services.report_subscription_service import report_subscription_service

router = APIRouter()


# Subscription CRUD Endpoints

@router.post("/", response_model=Subscription, tags=["report-subscriptions"])
async def create_subscription(
    data: SubscriptionCreate,
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Create a new subscription."""
    return report_subscription_service.create_subscription(user_id, data, organization_id)


@router.get("/", response_model=SubscriptionListResponse, tags=["report-subscriptions"])
async def list_subscriptions(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    resource_type: Optional[ResourceType] = Query(None),
    resource_id: Optional[str] = Query(None),
    subscription_type: Optional[SubscriptionType] = Query(None),
    status: Optional[SubscriptionStatus] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List subscriptions with filtering."""
    return report_subscription_service.list_subscriptions(
        user_id, organization_id, resource_type, resource_id,
        subscription_type, status, is_active, skip, limit
    )


@router.get("/{subscription_id}", response_model=Subscription, tags=["report-subscriptions"])
async def get_subscription(subscription_id: str):
    """Get subscription by ID."""
    subscription = report_subscription_service.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.patch("/{subscription_id}", response_model=Subscription, tags=["report-subscriptions"])
async def update_subscription(
    subscription_id: str,
    data: SubscriptionUpdate,
):
    """Update a subscription."""
    subscription = report_subscription_service.update_subscription(subscription_id, data)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.delete("/{subscription_id}", tags=["report-subscriptions"])
async def delete_subscription(subscription_id: str):
    """Delete a subscription."""
    if report_subscription_service.delete_subscription(subscription_id):
        return {"success": True, "message": "Subscription deleted"}
    raise HTTPException(status_code=404, detail="Subscription not found")


@router.post("/{subscription_id}/pause", response_model=Subscription, tags=["report-subscriptions"])
async def pause_subscription(subscription_id: str):
    """Pause a subscription."""
    subscription = report_subscription_service.pause_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.post("/{subscription_id}/resume", response_model=Subscription, tags=["report-subscriptions"])
async def resume_subscription(subscription_id: str):
    """Resume a paused subscription."""
    subscription = report_subscription_service.resume_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


# Notification Endpoints

@router.get("/notifications/", response_model=NotificationListResponse, tags=["subscription-notifications"])
async def list_notifications(
    user_id: Optional[str] = Query(None),
    subscription_id: Optional[str] = Query(None),
    resource_type: Optional[ResourceType] = Query(None),
    unread_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List notifications with filtering."""
    return report_subscription_service.list_notifications(
        user_id, subscription_id, resource_type, unread_only, skip, limit
    )


@router.get("/notifications/{notification_id}", response_model=SubscriptionNotification, tags=["subscription-notifications"])
async def get_notification(notification_id: str):
    """Get notification by ID."""
    notification = report_subscription_service.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.post("/notifications/{notification_id}/read", response_model=SubscriptionNotification, tags=["subscription-notifications"])
async def mark_notification_read(notification_id: str):
    """Mark a notification as read."""
    notification = report_subscription_service.mark_notification_read(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.post("/notifications/mark-all-read", tags=["subscription-notifications"])
async def mark_all_notifications_read(user_id: str = Query(...)):
    """Mark all notifications as read for a user."""
    count = report_subscription_service.mark_all_read(user_id)
    return {"success": True, "marked_count": count}


@router.post("/notifications/{notification_id}/click", response_model=SubscriptionNotification, tags=["subscription-notifications"])
async def record_notification_click(notification_id: str):
    """Record that a notification was clicked."""
    notification = report_subscription_service.record_click(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


# Digest Endpoints

@router.get("/digests/", response_model=DigestListResponse, tags=["subscription-digests"])
async def list_digests(
    user_id: str = Query(...),
    digest_type: Optional[DigestFrequency] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List digests for a user."""
    return report_subscription_service.list_digests(user_id, digest_type, skip, limit)


@router.get("/digests/{digest_id}", response_model=Digest, tags=["subscription-digests"])
async def get_digest(digest_id: str):
    """Get digest by ID."""
    digest = report_subscription_service.get_digest(digest_id)
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    return digest


@router.post("/digests/{digest_id}/send", tags=["subscription-digests"])
async def send_digest(digest_id: str):
    """Mark a digest as sent."""
    if report_subscription_service.send_digest(digest_id):
        return {"success": True, "message": "Digest marked as sent"}
    raise HTTPException(status_code=404, detail="Digest not found")


# User Preferences Endpoints

@router.get("/preferences/{user_id}", response_model=UserSubscriptionPreferences, tags=["subscription-preferences"])
async def get_user_preferences(user_id: str):
    """Get user's subscription preferences."""
    preferences = report_subscription_service.get_user_preferences(user_id)
    if not preferences:
        # Return default preferences
        preferences = report_subscription_service.update_user_preferences(user_id)
    return preferences


@router.put("/preferences/{user_id}", response_model=UserSubscriptionPreferences, tags=["subscription-preferences"])
async def update_user_preferences(
    user_id: str,
    global_preferences: Optional[GlobalNotificationPreferences] = None,
    channel_preferences: Optional[dict] = None,
    resource_preferences: Optional[dict] = None,
    muted_resources: Optional[list] = None,
):
    """Update user's subscription preferences."""
    return report_subscription_service.update_user_preferences(
        user_id, global_preferences, channel_preferences, resource_preferences, muted_resources
    )


@router.post("/preferences/{user_id}/mute/{resource_id}", response_model=UserSubscriptionPreferences, tags=["subscription-preferences"])
async def mute_resource(user_id: str, resource_id: str):
    """Mute notifications for a specific resource."""
    return report_subscription_service.mute_resource(user_id, resource_id)


@router.post("/preferences/{user_id}/unmute/{resource_id}", response_model=UserSubscriptionPreferences, tags=["subscription-preferences"])
async def unmute_resource(user_id: str, resource_id: str):
    """Unmute notifications for a specific resource."""
    return report_subscription_service.unmute_resource(user_id, resource_id)


# Statistics Endpoints

@router.get("/stats/{organization_id}", response_model=SubscriptionStats, tags=["subscription-stats"])
async def get_subscription_stats(organization_id: str):
    """Get subscription statistics for organization."""
    return report_subscription_service.get_stats(organization_id)


# Threshold Processing (for webhook/internal use)

@router.post("/process-thresholds", tags=["subscription-processing"])
async def process_thresholds(
    resource_type: ResourceType = Query(...),
    resource_id: str = Query(...),
    current_values: dict = None,
    previous_values: dict = None,
):
    """Process threshold subscriptions for a resource."""
    if current_values is None:
        current_values = {}

    notifications = report_subscription_service.process_threshold_subscriptions(
        resource_type, resource_id, current_values, previous_values
    )

    return {
        "success": True,
        "notifications_sent": len(notifications),
        "notification_ids": [n.id for n in notifications],
    }
