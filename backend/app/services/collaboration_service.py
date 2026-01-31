"""
Collaboration Service

Handles real-time collaboration, presence, comments, and activity feeds.
"""

import uuid
from typing import Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.collaboration import (
    PresenceStatus,
    ActivityType,
    CommentStatus,
    ReactionType,
    NotificationType,
    CursorPosition,
    UserPresence,
    PresenceUpdate,
    RoomPresence,
    CommentCreate,
    CommentUpdate,
    Comment,
    CommentThread,
    CommentMention,
    CommentReaction,
    Activity,
    ActivityActor,
    ActivityTarget,
    ActivityFeed,
    EditLock,
    CollaborationSession,
    Notification,
    NotificationPreferences,
    WSMessage,
    WSMessageType,
    PRESENCE_TIMEOUT_SECONDS,
    LOCK_TIMEOUT_SECONDS,
    get_presence_color,
    generate_room_id,
)


logger = logging.getLogger(__name__)


class CollaborationService:
    """Service for real-time collaboration features."""

    def __init__(self, db: AsyncSession):
        self.db = db
        # In-memory stores (production would use Redis)
        self._presence: dict[str, dict[str, UserPresence]] = {}  # room -> user_id -> presence
        self._comments: dict[str, dict] = {}  # comment_id -> comment
        self._activities: list[dict] = []
        self._notifications: dict[str, list[dict]] = {}  # user_id -> notifications
        self._locks: dict[str, EditLock] = {}  # lock_key -> lock
        self._sessions: dict[str, CollaborationSession] = {}  # session_id -> session
        self._notification_prefs: dict[str, dict] = {}  # user_id -> preferences
        self._user_colors: dict[str, str] = {}  # user_id -> color

    # Presence Management

    async def join_room(
        self,
        room: str,
        user_id: str,
        user_name: str,
        user_email: str,
        avatar_url: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> UserPresence:
        """Join a collaboration room."""
        if room not in self._presence:
            self._presence[room] = {}

        # Assign consistent color
        if user_id not in self._user_colors:
            color_index = len(self._user_colors)
            self._user_colors[user_id] = get_presence_color(color_index)

        now = datetime.utcnow()
        presence = UserPresence(
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            avatar_url=avatar_url,
            status=PresenceStatus.ONLINE,
            color=self._user_colors[user_id],
            current_resource_type=room.split(":")[0] if ":" in room else None,
            current_resource_id=room.split(":")[1] if ":" in room else None,
            last_activity=now,
            connected_at=now,
            device_type=device_type,
        )

        self._presence[room][user_id] = presence
        logger.info(f"User {user_name} joined room {room}")

        return presence

    async def leave_room(
        self,
        room: str,
        user_id: str,
    ) -> bool:
        """Leave a collaboration room."""
        if room in self._presence and user_id in self._presence[room]:
            del self._presence[room][user_id]
            logger.info(f"User {user_id} left room {room}")

            # Clean up empty rooms
            if not self._presence[room]:
                del self._presence[room]

            # Release any locks held by this user
            await self._release_user_locks(user_id)

            return True
        return False

    async def update_presence(
        self,
        room: str,
        user_id: str,
        update: PresenceUpdate,
    ) -> Optional[UserPresence]:
        """Update user presence in a room."""
        if room not in self._presence or user_id not in self._presence[room]:
            return None

        presence = self._presence[room][user_id]

        if update.cursor:
            presence.cursor = update.cursor
        if update.status:
            presence.status = update.status
        if update.current_resource_type:
            presence.current_resource_type = update.current_resource_type
        if update.current_resource_id:
            presence.current_resource_id = update.current_resource_id

        presence.last_activity = datetime.utcnow()
        self._presence[room][user_id] = presence

        return presence

    async def get_room_presence(
        self,
        room: str,
    ) -> RoomPresence:
        """Get all users present in a room."""
        users = list(self._presence.get(room, {}).values())

        # Filter out stale presences
        cutoff = datetime.utcnow() - timedelta(seconds=PRESENCE_TIMEOUT_SECONDS)
        active_users = [u for u in users if u.last_activity > cutoff]

        resource_parts = room.split(":") if ":" in room else ["", ""]

        return RoomPresence(
            resource_type=resource_parts[0],
            resource_id=resource_parts[1] if len(resource_parts) > 1 else "",
            users=active_users,
            total_count=len(active_users),
        )

    async def heartbeat(
        self,
        room: str,
        user_id: str,
    ) -> bool:
        """Update user's last activity timestamp."""
        if room in self._presence and user_id in self._presence[room]:
            self._presence[room][user_id].last_activity = datetime.utcnow()
            return True
        return False

    # Comment Management

    async def create_comment(
        self,
        comment_data: CommentCreate,
        author_id: str,
        author_name: str,
        author_email: str,
        author_avatar: Optional[str] = None,
    ) -> Comment:
        """Create a new comment."""
        now = datetime.utcnow()
        comment_id = str(uuid.uuid4())

        # Process mentions
        mentions = []
        for user_id in comment_data.mentions:
            # In production, look up user details
            mentions.append(CommentMention(
                user_id=user_id,
                user_name=f"User {user_id[:8]}",
                user_email=f"{user_id[:8]}@example.com",
                start_index=0,
                end_index=0,
            ))

        comment = Comment(
            id=comment_id,
            content=comment_data.content,
            resource_type=comment_data.resource_type,
            resource_id=comment_data.resource_id,
            parent_id=comment_data.parent_id,
            author_id=author_id,
            author_name=author_name,
            author_email=author_email,
            author_avatar=author_avatar,
            status=CommentStatus.ACTIVE,
            mentions=mentions,
            reactions=[],
            attachments=[],
            position=comment_data.position,
            reply_count=0,
            is_edited=False,
            created_at=now,
            updated_at=now,
        )

        self._comments[comment_id] = comment.model_dump()

        # Update parent reply count
        if comment_data.parent_id and comment_data.parent_id in self._comments:
            self._comments[comment_data.parent_id]["reply_count"] += 1

        # Create notifications for mentions
        for mention in mentions:
            await self._create_notification(
                user_id=mention.user_id,
                notification_type=NotificationType.MENTION,
                title="You were mentioned",
                body=f"{author_name} mentioned you in a comment",
                actor=ActivityActor(
                    user_id=author_id,
                    user_name=author_name,
                    user_email=author_email,
                    avatar_url=author_avatar,
                ),
                target=ActivityTarget(
                    resource_type=comment_data.resource_type,
                    resource_id=comment_data.resource_id,
                    resource_name=f"{comment_data.resource_type} comment",
                ),
            )

        # Log activity
        await self.log_activity(
            activity_type=ActivityType.COMMENT_ADDED,
            actor_id=author_id,
            actor_name=author_name,
            actor_email=author_email,
            target_type=comment_data.resource_type,
            target_id=comment_data.resource_id,
            target_name=f"Comment on {comment_data.resource_type}",
            description=f"{author_name} added a comment",
        )

        return comment

    async def update_comment(
        self,
        comment_id: str,
        update: CommentUpdate,
        user_id: str,
    ) -> Optional[Comment]:
        """Update a comment."""
        if comment_id not in self._comments:
            return None

        comment_dict = self._comments[comment_id]

        # Only author can edit content
        if update.content and comment_dict["author_id"] != user_id:
            return None

        if update.content:
            comment_dict["content"] = update.content
            comment_dict["is_edited"] = True
        if update.status:
            comment_dict["status"] = update.status
            if update.status == CommentStatus.RESOLVED:
                comment_dict["resolved_by"] = user_id
                comment_dict["resolved_at"] = datetime.utcnow()

        comment_dict["updated_at"] = datetime.utcnow()
        self._comments[comment_id] = comment_dict

        return Comment(**comment_dict)

    async def delete_comment(
        self,
        comment_id: str,
        user_id: str,
    ) -> bool:
        """Delete (soft) a comment."""
        if comment_id not in self._comments:
            return False

        comment_dict = self._comments[comment_id]

        # Only author can delete
        if comment_dict["author_id"] != user_id:
            return False

        comment_dict["status"] = CommentStatus.DELETED
        comment_dict["updated_at"] = datetime.utcnow()
        self._comments[comment_id] = comment_dict

        return True

    async def get_comment(
        self,
        comment_id: str,
    ) -> Optional[Comment]:
        """Get a single comment."""
        if comment_id not in self._comments:
            return None
        return Comment(**self._comments[comment_id])

    async def list_comments(
        self,
        resource_type: str,
        resource_id: str,
        include_resolved: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[CommentThread], int]:
        """List comments for a resource."""
        # Filter comments
        comments = [
            c for c in self._comments.values()
            if c["resource_type"] == resource_type
            and c["resource_id"] == resource_id
            and c["parent_id"] is None  # Top-level only
            and (include_resolved or c["status"] != CommentStatus.RESOLVED)
            and c["status"] != CommentStatus.DELETED
        ]

        # Sort by created_at descending
        comments.sort(key=lambda c: c["created_at"], reverse=True)
        total = len(comments)

        # Paginate
        comments = comments[skip:skip + limit]

        # Build threads with replies
        threads = []
        for comment_dict in comments:
            comment = Comment(**comment_dict)

            # Get replies
            replies = [
                Comment(**c) for c in self._comments.values()
                if c["parent_id"] == comment.id
                and c["status"] != CommentStatus.DELETED
            ]
            replies.sort(key=lambda r: r.created_at)

            threads.append(CommentThread(
                comment=comment,
                replies=replies,
                total_replies=len(replies),
            ))

        return threads, total

    async def add_reaction(
        self,
        comment_id: str,
        reaction_type: ReactionType,
        user_id: str,
        user_name: str,
    ) -> Optional[Comment]:
        """Add a reaction to a comment."""
        if comment_id not in self._comments:
            return None

        comment_dict = self._comments[comment_id]

        # Check if already reacted with same type
        reactions = comment_dict.get("reactions", [])
        existing = next(
            (r for r in reactions if r["user_id"] == user_id and r["reaction_type"] == reaction_type),
            None
        )

        if existing:
            return Comment(**comment_dict)

        # Add reaction
        reactions.append({
            "reaction_type": reaction_type,
            "user_id": user_id,
            "user_name": user_name,
            "created_at": datetime.utcnow(),
        })
        comment_dict["reactions"] = reactions
        self._comments[comment_id] = comment_dict

        return Comment(**comment_dict)

    async def remove_reaction(
        self,
        comment_id: str,
        reaction_type: ReactionType,
        user_id: str,
    ) -> Optional[Comment]:
        """Remove a reaction from a comment."""
        if comment_id not in self._comments:
            return None

        comment_dict = self._comments[comment_id]
        reactions = comment_dict.get("reactions", [])

        # Remove reaction
        reactions = [
            r for r in reactions
            if not (r["user_id"] == user_id and r["reaction_type"] == reaction_type)
        ]
        comment_dict["reactions"] = reactions
        self._comments[comment_id] = comment_dict

        return Comment(**comment_dict)

    # Activity Feed

    async def log_activity(
        self,
        activity_type: ActivityType,
        actor_id: str,
        actor_name: str,
        actor_email: str,
        target_type: str,
        target_id: str,
        target_name: str,
        description: str,
        workspace_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        actor_avatar: Optional[str] = None,
        target_url: Optional[str] = None,
    ) -> Activity:
        """Log an activity."""
        activity = Activity(
            id=str(uuid.uuid4()),
            activity_type=activity_type,
            actor=ActivityActor(
                user_id=actor_id,
                user_name=actor_name,
                user_email=actor_email,
                avatar_url=actor_avatar,
            ),
            target=ActivityTarget(
                resource_type=target_type,
                resource_id=target_id,
                resource_name=target_name,
                resource_url=target_url,
            ),
            workspace_id=workspace_id,
            description=description,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )

        self._activities.append(activity.model_dump())
        logger.info(f"Activity logged: {activity_type} by {actor_name}")

        return activity

    async def get_activity_feed(
        self,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        activity_types: Optional[list[ActivityType]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ActivityFeed:
        """Get activity feed."""
        activities = self._activities.copy()

        # Apply filters
        if workspace_id:
            activities = [a for a in activities if a.get("workspace_id") == workspace_id]
        if user_id:
            activities = [a for a in activities if a["actor"]["user_id"] == user_id]
        if resource_type:
            activities = [a for a in activities if a["target"]["resource_type"] == resource_type]
        if resource_id:
            activities = [a for a in activities if a["target"]["resource_id"] == resource_id]
        if activity_types:
            type_values = [t.value for t in activity_types]
            activities = [a for a in activities if a["activity_type"] in type_values]

        # Sort by created_at descending
        activities.sort(key=lambda a: a["created_at"], reverse=True)
        total = len(activities)

        # Paginate
        activities = activities[skip:skip + limit]

        unread_count = sum(1 for a in activities if not a.get("is_read", False))

        return ActivityFeed(
            activities=[Activity(**a) for a in activities],
            total_count=total,
            unread_count=unread_count,
            has_more=skip + limit < total,
        )

    # Edit Locks

    async def acquire_lock(
        self,
        resource_type: str,
        resource_id: str,
        user_id: str,
        user_name: str,
        element_id: Optional[str] = None,
    ) -> Optional[EditLock]:
        """Acquire an edit lock on a resource."""
        lock_key = f"{resource_type}:{resource_id}"
        if element_id:
            lock_key += f":{element_id}"

        # Check existing lock
        if lock_key in self._locks:
            existing = self._locks[lock_key]
            # Allow same user to refresh lock
            if existing.locked_by != user_id:
                # Check if expired
                if existing.expires_at > datetime.utcnow():
                    return None  # Lock held by another user

        now = datetime.utcnow()
        lock = EditLock(
            resource_type=resource_type,
            resource_id=resource_id,
            element_id=element_id,
            locked_by=user_id,
            locked_by_name=user_name,
            locked_at=now,
            expires_at=now + timedelta(seconds=LOCK_TIMEOUT_SECONDS),
        )

        self._locks[lock_key] = lock
        return lock

    async def release_lock(
        self,
        resource_type: str,
        resource_id: str,
        user_id: str,
        element_id: Optional[str] = None,
    ) -> bool:
        """Release an edit lock."""
        lock_key = f"{resource_type}:{resource_id}"
        if element_id:
            lock_key += f":{element_id}"

        if lock_key in self._locks:
            lock = self._locks[lock_key]
            if lock.locked_by == user_id:
                del self._locks[lock_key]
                return True
        return False

    async def get_locks(
        self,
        resource_type: str,
        resource_id: str,
    ) -> list[EditLock]:
        """Get all locks for a resource."""
        prefix = f"{resource_type}:{resource_id}"
        now = datetime.utcnow()

        locks = []
        for key, lock in list(self._locks.items()):
            if key.startswith(prefix):
                if lock.expires_at > now:
                    locks.append(lock)
                else:
                    # Clean up expired lock
                    del self._locks[key]

        return locks

    async def _release_user_locks(self, user_id: str):
        """Release all locks held by a user."""
        for key in list(self._locks.keys()):
            if self._locks[key].locked_by == user_id:
                del self._locks[key]

    # Notifications

    async def _create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        body: str,
        actor: Optional[ActivityActor] = None,
        target: Optional[ActivityTarget] = None,
        action_url: Optional[str] = None,
    ) -> Notification:
        """Create a notification for a user."""
        notification = Notification(
            id=str(uuid.uuid4()),
            notification_type=notification_type,
            title=title,
            body=body,
            actor=actor,
            target=target,
            action_url=action_url,
            created_at=datetime.utcnow(),
        )

        if user_id not in self._notifications:
            self._notifications[user_id] = []

        self._notifications[user_id].append(notification.model_dump())
        return notification

    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Notification], int, int]:
        """Get notifications for a user."""
        notifications = self._notifications.get(user_id, [])

        if unread_only:
            notifications = [n for n in notifications if not n.get("is_read", False)]

        # Sort by created_at descending
        notifications.sort(key=lambda n: n["created_at"], reverse=True)
        total = len(notifications)
        unread = sum(1 for n in self._notifications.get(user_id, []) if not n.get("is_read", False))

        # Paginate
        notifications = notifications[skip:skip + limit]

        return [Notification(**n) for n in notifications], total, unread

    async def mark_notification_read(
        self,
        user_id: str,
        notification_id: str,
    ) -> bool:
        """Mark a notification as read."""
        notifications = self._notifications.get(user_id, [])

        for n in notifications:
            if n["id"] == notification_id:
                n["is_read"] = True
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
            if not n.get("is_read", False):
                n["is_read"] = True
                n["read_at"] = now
                count += 1

        return count

    async def get_notification_preferences(
        self,
        user_id: str,
    ) -> NotificationPreferences:
        """Get user's notification preferences."""
        prefs = self._notification_prefs.get(user_id)
        if prefs:
            return NotificationPreferences(**prefs)

        # Return defaults
        return NotificationPreferences(user_id=user_id)

    async def update_notification_preferences(
        self,
        user_id: str,
        updates: dict[str, Any],
    ) -> NotificationPreferences:
        """Update user's notification preferences."""
        current = await self.get_notification_preferences(user_id)
        current_dict = current.model_dump()

        for key, value in updates.items():
            if key in current_dict and key != "user_id":
                current_dict[key] = value

        self._notification_prefs[user_id] = current_dict
        return NotificationPreferences(**current_dict)

    # Collaboration Sessions

    async def start_session(
        self,
        resource_type: str,
        resource_id: str,
    ) -> CollaborationSession:
        """Start or get a collaboration session."""
        session_key = generate_room_id(resource_type, resource_id)

        if session_key in self._sessions:
            session = self._sessions[session_key]
            # Update participants from presence
            room_presence = await self.get_room_presence(session_key)
            session.participants = room_presence.users
            return session

        session = CollaborationSession(
            session_id=str(uuid.uuid4()),
            resource_type=resource_type,
            resource_id=resource_id,
            started_at=datetime.utcnow(),
            participants=[],
            active_locks=[],
            change_count=0,
        )

        self._sessions[session_key] = session
        return session

    async def get_session(
        self,
        resource_type: str,
        resource_id: str,
    ) -> Optional[CollaborationSession]:
        """Get a collaboration session."""
        session_key = generate_room_id(resource_type, resource_id)
        session = self._sessions.get(session_key)

        if session:
            # Update participants and locks
            room_presence = await self.get_room_presence(session_key)
            session.participants = room_presence.users
            session.active_locks = await self.get_locks(resource_type, resource_id)

        return session

    async def record_change(
        self,
        resource_type: str,
        resource_id: str,
    ):
        """Record a change in a session."""
        session_key = generate_room_id(resource_type, resource_id)
        if session_key in self._sessions:
            self._sessions[session_key].change_count += 1
            self._sessions[session_key].last_change_at = datetime.utcnow()
