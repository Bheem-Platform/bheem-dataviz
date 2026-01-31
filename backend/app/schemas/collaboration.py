"""
Collaboration Schemas

Pydantic schemas for real-time collaboration features.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class PresenceStatus(str, Enum):
    """User presence status"""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"


class ActivityType(str, Enum):
    """Activity types for feed"""
    DASHBOARD_CREATED = "dashboard_created"
    DASHBOARD_UPDATED = "dashboard_updated"
    DASHBOARD_DELETED = "dashboard_deleted"
    DASHBOARD_SHARED = "dashboard_shared"
    DASHBOARD_PUBLISHED = "dashboard_published"
    CHART_CREATED = "chart_created"
    CHART_UPDATED = "chart_updated"
    CHART_DELETED = "chart_deleted"
    COMMENT_ADDED = "comment_added"
    COMMENT_REPLIED = "comment_replied"
    COMMENT_RESOLVED = "comment_resolved"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    DATA_REFRESHED = "data_refreshed"
    ALERT_TRIGGERED = "alert_triggered"
    REPORT_GENERATED = "report_generated"
    CONNECTION_CREATED = "connection_created"
    CONNECTION_UPDATED = "connection_updated"


class CommentStatus(str, Enum):
    """Comment status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    DELETED = "deleted"


class ReactionType(str, Enum):
    """Comment reaction types"""
    LIKE = "like"
    LOVE = "love"
    CELEBRATE = "celebrate"
    THINKING = "thinking"
    SAD = "sad"
    ANGRY = "angry"


# Presence Models

class CursorPosition(BaseModel):
    """User cursor position on canvas"""
    x: float
    y: float
    element_id: Optional[str] = None
    element_type: Optional[str] = None  # chart, filter, widget


class UserPresence(BaseModel):
    """Real-time user presence"""
    user_id: str
    user_name: str
    user_email: str
    avatar_url: Optional[str] = None
    status: PresenceStatus = PresenceStatus.ONLINE
    color: str = "#6366f1"  # User's presence color
    cursor: Optional[CursorPosition] = None
    current_resource_type: Optional[str] = None  # dashboard, chart, etc.
    current_resource_id: Optional[str] = None
    last_activity: datetime
    connected_at: datetime
    device_type: Optional[str] = None  # desktop, mobile, tablet


class PresenceUpdate(BaseModel):
    """Presence update message"""
    user_id: str
    cursor: Optional[CursorPosition] = None
    status: Optional[PresenceStatus] = None
    current_resource_type: Optional[str] = None
    current_resource_id: Optional[str] = None


class RoomPresence(BaseModel):
    """All users present in a resource room"""
    resource_type: str
    resource_id: str
    users: list[UserPresence]
    total_count: int


# Comment Models

class CommentMention(BaseModel):
    """Mention in a comment"""
    user_id: str
    user_name: str
    user_email: str
    start_index: int
    end_index: int


class CommentAttachment(BaseModel):
    """Attachment in a comment"""
    id: str
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    thumbnail_url: Optional[str] = None


class CommentReaction(BaseModel):
    """Reaction on a comment"""
    reaction_type: ReactionType
    user_id: str
    user_name: str
    created_at: datetime


class CommentCreate(BaseModel):
    """Create a new comment"""
    content: str = Field(..., min_length=1, max_length=10000)
    resource_type: str  # dashboard, chart, dataset, etc.
    resource_id: str
    parent_id: Optional[str] = None  # For replies
    mentions: list[str] = Field(default_factory=list)  # User IDs mentioned
    position: Optional[dict[str, Any]] = None  # Position on canvas (x, y, element_id)
    attachments: list[str] = Field(default_factory=list)  # Attachment IDs


class CommentUpdate(BaseModel):
    """Update a comment"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    status: Optional[CommentStatus] = None
    mentions: Optional[list[str]] = None


class Comment(BaseModel):
    """Full comment object"""
    id: str
    content: str
    resource_type: str
    resource_id: str
    parent_id: Optional[str] = None
    author_id: str
    author_name: str
    author_email: str
    author_avatar: Optional[str] = None
    status: CommentStatus = CommentStatus.ACTIVE
    mentions: list[CommentMention] = Field(default_factory=list)
    reactions: list[CommentReaction] = Field(default_factory=list)
    attachments: list[CommentAttachment] = Field(default_factory=list)
    position: Optional[dict[str, Any]] = None
    reply_count: int = 0
    is_edited: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentThread(BaseModel):
    """Comment with replies"""
    comment: Comment
    replies: list[Comment] = Field(default_factory=list)
    total_replies: int = 0


# Activity Feed Models

class ActivityActor(BaseModel):
    """Actor who performed the activity"""
    user_id: str
    user_name: str
    user_email: str
    avatar_url: Optional[str] = None


class ActivityTarget(BaseModel):
    """Target of the activity"""
    resource_type: str
    resource_id: str
    resource_name: str
    resource_url: Optional[str] = None


class Activity(BaseModel):
    """Activity feed item"""
    id: str
    activity_type: ActivityType
    actor: ActivityActor
    target: ActivityTarget
    workspace_id: Optional[str] = None
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityFeed(BaseModel):
    """Paginated activity feed"""
    activities: list[Activity]
    total_count: int
    unread_count: int
    has_more: bool


# WebSocket Message Models

class WSMessageType(str, Enum):
    """WebSocket message types"""
    # Connection
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"

    # Presence
    PRESENCE_UPDATE = "presence_update"
    CURSOR_MOVE = "cursor_move"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"

    # Collaboration
    EDIT_START = "edit_start"
    EDIT_END = "edit_end"
    CHANGE = "change"
    SYNC = "sync"

    # Comments
    COMMENT_ADDED = "comment_added"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"

    # Activity
    ACTIVITY = "activity"
    NOTIFICATION = "notification"

    # Errors
    ERROR = "error"


class WSMessage(BaseModel):
    """WebSocket message structure"""
    type: WSMessageType
    room: Optional[str] = None  # Resource room (e.g., "dashboard:uuid")
    sender_id: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WSError(BaseModel):
    """WebSocket error message"""
    code: str
    message: str
    details: Optional[dict[str, Any]] = None


# Collaboration Session Models

class EditLock(BaseModel):
    """Lock on a resource being edited"""
    resource_type: str
    resource_id: str
    element_id: Optional[str] = None  # Specific element locked
    locked_by: str
    locked_by_name: str
    locked_at: datetime
    expires_at: datetime


class CollaborationSession(BaseModel):
    """Active collaboration session"""
    session_id: str
    resource_type: str
    resource_id: str
    started_at: datetime
    participants: list[UserPresence]
    active_locks: list[EditLock] = Field(default_factory=list)
    change_count: int = 0
    last_change_at: Optional[datetime] = None


# Notification Models

class NotificationType(str, Enum):
    """Notification types"""
    MENTION = "mention"
    REPLY = "reply"
    SHARE = "share"
    COMMENT = "comment"
    ASSIGNMENT = "assignment"
    ALERT = "alert"
    SYSTEM = "system"


class Notification(BaseModel):
    """User notification"""
    id: str
    notification_type: NotificationType
    title: str
    body: str
    actor: Optional[ActivityActor] = None
    target: Optional[ActivityTarget] = None
    action_url: Optional[str] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str
    email_mentions: bool = True
    email_replies: bool = True
    email_shares: bool = True
    email_comments: bool = False
    email_assignments: bool = True
    email_alerts: bool = True
    push_mentions: bool = True
    push_replies: bool = True
    push_shares: bool = True
    push_comments: bool = True
    push_assignments: bool = True
    push_alerts: bool = True
    digest_frequency: str = "daily"  # none, daily, weekly


# Response Models

class PresenceResponse(BaseModel):
    """Presence API response"""
    users: list[UserPresence]
    room: str
    your_color: str


class CommentListResponse(BaseModel):
    """Comment list response"""
    comments: list[CommentThread]
    total_count: int
    has_more: bool


class NotificationListResponse(BaseModel):
    """Notification list response"""
    notifications: list[Notification]
    total_count: int
    unread_count: int
    has_more: bool


# Helper Constants

PRESENCE_COLORS = [
    "#6366f1",  # Indigo
    "#8b5cf6",  # Violet
    "#ec4899",  # Pink
    "#f43f5e",  # Rose
    "#f97316",  # Orange
    "#eab308",  # Yellow
    "#22c55e",  # Green
    "#14b8a6",  # Teal
    "#06b6d4",  # Cyan
    "#3b82f6",  # Blue
]

PRESENCE_TIMEOUT_SECONDS = 30
CURSOR_THROTTLE_MS = 50
LOCK_TIMEOUT_SECONDS = 300


def get_presence_color(user_index: int) -> str:
    """Get a consistent color for a user based on their index"""
    return PRESENCE_COLORS[user_index % len(PRESENCE_COLORS)]


def generate_room_id(resource_type: str, resource_id: str) -> str:
    """Generate a room ID for WebSocket subscriptions"""
    return f"{resource_type}:{resource_id}"
