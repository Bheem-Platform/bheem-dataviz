"""
Subscriptions and Alerts API Endpoints

REST API for data alerts and dashboard subscriptions.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.subscription_service import SubscriptionService
from app.schemas.subscriptions import (
    DataAlertCreate,
    DataAlertUpdate,
    DataAlertResponse,
    AlertHistory,
    AlertTriggerEvent,
    AlertSummary,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionDelivery,
    SubscriptionSummary,
    AlertStatus,
    NotificationChannel,
)

router = APIRouter()


# Data Alerts

@router.post("/alerts", response_model=DataAlertResponse)
async def create_alert(
    alert_data: DataAlertCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new data alert.

    Data alerts monitor metrics and trigger notifications
    when thresholds are breached.

    **Example use cases:**
    - Alert when sales drop below target
    - Notify when error rate exceeds threshold
    - Warn when inventory falls below minimum
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SubscriptionService(db)
    return await service.create_alert(alert_data, user_id)


@router.get("/alerts", response_model=list[DataAlertResponse])
async def list_alerts(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    target_id: Optional[str] = Query(None, description="Filter by target ID"),
    enabled_only: bool = Query(False, description="Only return enabled alerts"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List data alerts with optional filtering."""
    service = SubscriptionService(db)
    return await service.list_alerts(
        workspace_id=workspace_id,
        target_type=target_type,
        target_id=target_id,
        enabled_only=enabled_only,
        skip=skip,
        limit=limit,
    )


@router.get("/alerts/{alert_id}", response_model=DataAlertResponse)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific data alert by ID."""
    service = SubscriptionService(db)
    alert = await service.get_alert(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.patch("/alerts/{alert_id}", response_model=DataAlertResponse)
async def update_alert(
    alert_id: str,
    update_data: DataAlertUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a data alert."""
    service = SubscriptionService(db)
    alert = await service.update_alert(alert_id, update_data)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a data alert."""
    service = SubscriptionService(db)
    success = await service.delete_alert(alert_id)

    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"message": "Alert deleted successfully"}


@router.post("/alerts/{alert_id}/pause", response_model=DataAlertResponse)
async def pause_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Pause a data alert."""
    service = SubscriptionService(db)
    alert = await service.pause_alert(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.post("/alerts/{alert_id}/resume", response_model=DataAlertResponse)
async def resume_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Resume a paused alert."""
    service = SubscriptionService(db)
    alert = await service.resume_alert(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.post("/alerts/{alert_id}/evaluate")
async def evaluate_alert(
    alert_id: str,
    current_value: float = Query(..., description="Current metric value"),
    previous_value: Optional[float] = Query(None, description="Previous metric value"),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually evaluate an alert against provided values.

    Useful for testing alert configurations.
    """
    service = SubscriptionService(db)
    trigger_event = await service.evaluate_alert(
        alert_id=alert_id,
        current_value=current_value,
        previous_value=previous_value,
    )

    return {
        "triggered": trigger_event is not None,
        "event": trigger_event.model_dump() if trigger_event else None,
    }


@router.post("/alerts/{alert_id}/acknowledge", response_model=DataAlertResponse)
async def acknowledge_alert(
    alert_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge a triggered alert."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SubscriptionService(db)
    alert = await service.acknowledge_alert(alert_id, user_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.get("/alerts/{alert_id}/history", response_model=list[AlertHistory])
async def get_alert_history(
    alert_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get trigger history for a specific alert."""
    service = SubscriptionService(db)
    return await service.get_alert_history(alert_id=alert_id, limit=limit)


@router.get("/alerts/history/all", response_model=list[AlertHistory])
async def get_all_alert_history(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get trigger history for all alerts."""
    service = SubscriptionService(db)
    return await service.get_alert_history(limit=limit)


@router.get("/alerts/summary", response_model=AlertSummary)
async def get_alert_summary(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    db: AsyncSession = Depends(get_db),
):
    """Get summary statistics for alerts."""
    service = SubscriptionService(db)
    return await service.get_alert_summary(workspace_id=workspace_id)


# Dashboard Subscriptions

@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new dashboard subscription.

    Subscriptions deliver dashboard snapshots on a schedule
    via email or other channels.

    **Features:**
    - Schedule: daily, weekly, monthly, or custom cron
    - Content: PDF, HTML, or Excel
    - Filters: Apply saved filter states
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SubscriptionService(db)
    return await service.create_subscription(subscription_data, user_id)


@router.get("/subscriptions", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    dashboard_id: Optional[str] = Query(None, description="Filter by dashboard"),
    active_only: bool = Query(False, description="Only return active subscriptions"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """List subscriptions with optional filtering."""
    created_by = None
    if request:
        created_by = getattr(request.state, "user_id", None)

    service = SubscriptionService(db)
    return await service.list_subscriptions(
        workspace_id=workspace_id,
        dashboard_id=dashboard_id,
        created_by=created_by,
        active_only=active_only,
        skip=skip,
        limit=limit,
    )


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific subscription by ID."""
    service = SubscriptionService(db)
    subscription = await service.get_subscription(subscription_id)

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return subscription


@router.patch("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    update_data: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a subscription."""
    service = SubscriptionService(db)
    subscription = await service.update_subscription(subscription_id, update_data)

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return subscription


@router.delete("/subscriptions/{subscription_id}")
async def delete_subscription(
    subscription_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a subscription."""
    service = SubscriptionService(db)
    success = await service.delete_subscription(subscription_id)

    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return {"message": "Subscription deleted successfully"}


@router.post("/subscriptions/{subscription_id}/pause", response_model=SubscriptionResponse)
async def pause_subscription(
    subscription_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Pause a subscription."""
    service = SubscriptionService(db)
    subscription = await service.pause_subscription(subscription_id)

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return subscription


@router.post("/subscriptions/{subscription_id}/resume", response_model=SubscriptionResponse)
async def resume_subscription(
    subscription_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Resume a paused subscription."""
    service = SubscriptionService(db)
    subscription = await service.resume_subscription(subscription_id)

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return subscription


@router.post("/subscriptions/{subscription_id}/send", response_model=SubscriptionDelivery)
async def send_subscription_now(
    subscription_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger a subscription delivery.

    Sends the subscription immediately regardless of schedule.
    """
    service = SubscriptionService(db)
    delivery = await service.send_subscription_now(subscription_id)

    if not delivery:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return delivery


@router.get("/subscriptions/{subscription_id}/deliveries", response_model=list[SubscriptionDelivery])
async def get_subscription_deliveries(
    subscription_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get delivery history for a specific subscription."""
    service = SubscriptionService(db)
    return await service.get_subscription_deliveries(
        subscription_id=subscription_id,
        limit=limit,
    )


@router.get("/subscriptions/deliveries/all", response_model=list[SubscriptionDelivery])
async def get_all_subscription_deliveries(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get delivery history for all subscriptions."""
    service = SubscriptionService(db)
    return await service.get_subscription_deliveries(limit=limit)


@router.get("/subscriptions/summary", response_model=SubscriptionSummary)
async def get_subscription_summary(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    db: AsyncSession = Depends(get_db),
):
    """Get summary statistics for subscriptions."""
    service = SubscriptionService(db)
    return await service.get_subscription_summary(workspace_id=workspace_id)


# Notification Channel Info

@router.get("/channels")
async def list_notification_channels():
    """List available notification channels."""
    return [
        {
            "channel": NotificationChannel.EMAIL,
            "name": "Email",
            "description": "Send notifications via email",
            "config_fields": ["recipients", "subject_template", "include_chart_image"],
        },
        {
            "channel": NotificationChannel.SLACK,
            "name": "Slack",
            "description": "Send notifications to Slack channels",
            "config_fields": ["webhook_url", "channel", "username"],
        },
        {
            "channel": NotificationChannel.WEBHOOK,
            "name": "Webhook",
            "description": "Send notifications to custom webhooks",
            "config_fields": ["url", "method", "headers", "secret"],
        },
        {
            "channel": NotificationChannel.TEAMS,
            "name": "Microsoft Teams",
            "description": "Send notifications to Microsoft Teams",
            "config_fields": ["webhook_url"],
        },
        {
            "channel": NotificationChannel.IN_APP,
            "name": "In-App",
            "description": "Show notifications within the application",
            "config_fields": [],
        },
    ]


# Test Endpoints

@router.post("/test/email")
async def test_email_notification(
    recipients: list[str],
    subject: str = "Test Alert Notification",
):
    """
    Send a test email notification.

    Use this to verify email configuration.
    """
    # In production, actually send the email
    return {
        "success": True,
        "message": f"Test email would be sent to {len(recipients)} recipients",
        "recipients": recipients,
    }


@router.post("/test/slack")
async def test_slack_notification(
    webhook_url: str,
    message: str = "Test alert from Bheem DataViz",
):
    """
    Send a test Slack notification.

    Use this to verify Slack webhook configuration.
    """
    import httpx

    payload = {
        "text": message,
        "username": "Bheem DataViz",
        "icon_emoji": ":chart_with_upwards_trend:",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
        return {"success": True, "message": "Test notification sent"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/test/webhook")
async def test_webhook_notification(
    url: str,
    method: str = "POST",
):
    """
    Send a test webhook notification.

    Use this to verify webhook configuration.
    """
    import httpx

    payload = {
        "type": "test",
        "message": "Test webhook from Bheem DataViz",
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        async with httpx.AsyncClient() as client:
            if method.upper() == "POST":
                response = await client.post(url, json=payload)
            else:
                response = await client.put(url, json=payload)
            return {
                "success": response.is_success,
                "status_code": response.status_code,
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


from datetime import datetime
