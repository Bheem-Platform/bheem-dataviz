"""
Collaboration API Endpoints

REST API for real-time collaboration features.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.collaboration_service import CollaborationService
from app.schemas.collaboration import (
    PresenceStatus,
    ActivityType,
    ReactionType,
    NotificationType,
    PresenceUpdate,
    RoomPresence,
    CommentCreate,
    CommentUpdate,
    Comment,
    CommentThread,
    Activity,
    ActivityFeed,
    EditLock,
    CollaborationSession,
    Notification,
    NotificationPreferences,
    PresenceResponse,
    CommentListResponse,
    NotificationListResponse,
    generate_room_id,
)

router = APIRouter()


# Presence Endpoints

@router.post("/presence/join", response_model=PresenceResponse)
async def join_room(
    resource_type: str = Query(..., description="Resource type (dashboard, chart, etc.)"),
    resource_id: str = Query(..., description="Resource ID"),
    device_type: Optional[str] = Query(None, description="Device type"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Join a collaboration room.

    Returns your presence info and list of other users in the room.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    user_name = getattr(request.state, "user_name", "Anonymous User")
    user_email = getattr(request.state, "user_email", "anonymous@example.com")

    room = generate_room_id(resource_type, resource_id)
    service = CollaborationService(db)

    presence = await service.join_room(
        room=room,
        user_id=user_id,
        user_name=user_name,
        user_email=user_email,
        device_type=device_type,
    )

    room_presence = await service.get_room_presence(room)

    return PresenceResponse(
        users=room_presence.users,
        room=room,
        your_color=presence.color,
    )


@router.post("/presence/leave")
async def leave_room(
    resource_type: str = Query(...),
    resource_id: str = Query(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Leave a collaboration room."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    room = generate_room_id(resource_type, resource_id)

    service = CollaborationService(db)
    success = await service.leave_room(room, user_id)

    return {"left": success}


@router.post("/presence/update")
async def update_presence(
    resource_type: str = Query(...),
    resource_id: str = Query(...),
    update: PresenceUpdate = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update presence (cursor position, status, etc.)."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    room = generate_room_id(resource_type, resource_id)

    if update is None:
        update = PresenceUpdate(user_id=user_id)

    service = CollaborationService(db)
    presence = await service.update_presence(room, user_id, update)

    if not presence:
        raise HTTPException(status_code=404, detail="Not in room")

    return presence


@router.get("/presence/{resource_type}/{resource_id}", response_model=RoomPresence)
async def get_room_presence(
    resource_type: str,
    resource_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all users present in a resource room."""
    room = generate_room_id(resource_type, resource_id)
    service = CollaborationService(db)
    return await service.get_room_presence(room)


@router.post("/presence/heartbeat")
async def heartbeat(
    resource_type: str = Query(...),
    resource_id: str = Query(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Send heartbeat to maintain presence."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    room = generate_room_id(resource_type, resource_id)

    service = CollaborationService(db)
    success = await service.heartbeat(room, user_id)

    return {"alive": success}


# Comment Endpoints

@router.post("/comments", response_model=Comment)
async def create_comment(
    comment: CommentCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new comment on a resource."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    user_name = getattr(request.state, "user_name", "Anonymous User")
    user_email = getattr(request.state, "user_email", "anonymous@example.com")

    service = CollaborationService(db)
    return await service.create_comment(
        comment_data=comment,
        author_id=user_id,
        author_name=user_name,
        author_email=user_email,
    )


@router.get("/comments/{resource_type}/{resource_id}", response_model=CommentListResponse)
async def list_comments(
    resource_type: str,
    resource_id: str,
    include_resolved: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List comments for a resource."""
    service = CollaborationService(db)
    threads, total = await service.list_comments(
        resource_type=resource_type,
        resource_id=resource_id,
        include_resolved=include_resolved,
        skip=skip,
        limit=limit,
    )

    return CommentListResponse(
        comments=threads,
        total_count=total,
        has_more=skip + limit < total,
    )


@router.get("/comments/single/{comment_id}", response_model=Comment)
async def get_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single comment."""
    service = CollaborationService(db)
    comment = await service.get_comment(comment_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@router.patch("/comments/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: str,
    update: CommentUpdate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update a comment."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    comment = await service.update_comment(comment_id, update, user_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")

    return comment


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete a comment."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    success = await service.delete_comment(comment_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")

    return {"deleted": True}


@router.post("/comments/{comment_id}/resolve", response_model=Comment)
async def resolve_comment(
    comment_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Resolve a comment thread."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    from app.schemas.collaboration import CommentStatus
    comment = await service.update_comment(
        comment_id,
        CommentUpdate(status=CommentStatus.RESOLVED),
        user_id,
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@router.post("/comments/{comment_id}/reactions", response_model=Comment)
async def add_reaction(
    comment_id: str,
    reaction_type: ReactionType = Query(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Add a reaction to a comment."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    user_name = getattr(request.state, "user_name", "Anonymous User")

    service = CollaborationService(db)
    comment = await service.add_reaction(comment_id, reaction_type, user_id, user_name)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@router.delete("/comments/{comment_id}/reactions", response_model=Comment)
async def remove_reaction(
    comment_id: str,
    reaction_type: ReactionType = Query(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Remove a reaction from a comment."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    comment = await service.remove_reaction(comment_id, reaction_type, user_id)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


# Activity Feed Endpoints

@router.get("/activity", response_model=ActivityFeed)
async def get_activity_feed(
    workspace_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None, description="Filter by actor"),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    activity_types: Optional[str] = Query(None, description="Comma-separated activity types"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get activity feed."""
    types = None
    if activity_types:
        types = [ActivityType(t.strip()) for t in activity_types.split(",")]

    service = CollaborationService(db)
    return await service.get_activity_feed(
        workspace_id=workspace_id,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        activity_types=types,
        skip=skip,
        limit=limit,
    )


@router.post("/activity/log", response_model=Activity)
async def log_activity(
    activity_type: ActivityType,
    target_type: str,
    target_id: str,
    target_name: str,
    description: str,
    workspace_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Manually log an activity."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    user_name = getattr(request.state, "user_name", "Anonymous User")
    user_email = getattr(request.state, "user_email", "anonymous@example.com")

    service = CollaborationService(db)
    return await service.log_activity(
        activity_type=activity_type,
        actor_id=user_id,
        actor_name=user_name,
        actor_email=user_email,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        description=description,
        workspace_id=workspace_id,
        metadata=metadata,
    )


# Edit Lock Endpoints

@router.post("/locks/acquire", response_model=EditLock)
async def acquire_lock(
    resource_type: str = Query(...),
    resource_id: str = Query(...),
    element_id: Optional[str] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Acquire an edit lock on a resource.

    Returns the lock if acquired, or raises 409 if already locked.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    user_name = getattr(request.state, "user_name", "Anonymous User")

    service = CollaborationService(db)
    lock = await service.acquire_lock(
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        user_name=user_name,
        element_id=element_id,
    )

    if not lock:
        raise HTTPException(
            status_code=409,
            detail="Resource is locked by another user",
        )

    return lock


@router.post("/locks/release")
async def release_lock(
    resource_type: str = Query(...),
    resource_id: str = Query(...),
    element_id: Optional[str] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Release an edit lock."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    success = await service.release_lock(
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        element_id=element_id,
    )

    return {"released": success}


@router.get("/locks/{resource_type}/{resource_id}", response_model=list[EditLock])
async def get_locks(
    resource_type: str,
    resource_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all active locks for a resource."""
    service = CollaborationService(db)
    return await service.get_locks(resource_type, resource_id)


# Notification Endpoints

@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get user's notifications."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    notifications, total, unread = await service.get_notifications(
        user_id=user_id,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
    )

    return NotificationListResponse(
        notifications=notifications,
        total_count=total,
        unread_count=unread,
        has_more=skip + limit < total,
    )


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    success = await service.mark_notification_read(user_id, notification_id)

    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"marked_read": True}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    count = await service.mark_all_notifications_read(user_id)

    return {"marked_read": count}


@router.get("/notifications/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get user's notification preferences."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    return await service.get_notification_preferences(user_id)


@router.put("/notifications/preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    updates: dict,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update user's notification preferences."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = CollaborationService(db)
    return await service.update_notification_preferences(user_id, updates)


# Session Endpoints

@router.get("/sessions/{resource_type}/{resource_id}", response_model=CollaborationSession)
async def get_session(
    resource_type: str,
    resource_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get or create a collaboration session."""
    service = CollaborationService(db)
    session = await service.start_session(resource_type, resource_id)
    return session


@router.post("/sessions/{resource_type}/{resource_id}/change")
async def record_change(
    resource_type: str,
    resource_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Record a change in a collaboration session."""
    service = CollaborationService(db)
    await service.record_change(resource_type, resource_id)
    return {"recorded": True}
