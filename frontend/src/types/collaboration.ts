/**
 * Collaboration Types
 *
 * TypeScript types for real-time collaboration features.
 */

// Enums

export enum PresenceStatus {
  ONLINE = 'online',
  AWAY = 'away',
  BUSY = 'busy',
  OFFLINE = 'offline',
}

export enum ActivityType {
  DASHBOARD_CREATED = 'dashboard_created',
  DASHBOARD_UPDATED = 'dashboard_updated',
  DASHBOARD_DELETED = 'dashboard_deleted',
  DASHBOARD_SHARED = 'dashboard_shared',
  DASHBOARD_PUBLISHED = 'dashboard_published',
  CHART_CREATED = 'chart_created',
  CHART_UPDATED = 'chart_updated',
  CHART_DELETED = 'chart_deleted',
  COMMENT_ADDED = 'comment_added',
  COMMENT_REPLIED = 'comment_replied',
  COMMENT_RESOLVED = 'comment_resolved',
  USER_JOINED = 'user_joined',
  USER_LEFT = 'user_left',
  DATA_REFRESHED = 'data_refreshed',
  ALERT_TRIGGERED = 'alert_triggered',
  REPORT_GENERATED = 'report_generated',
  CONNECTION_CREATED = 'connection_created',
  CONNECTION_UPDATED = 'connection_updated',
}

export enum CommentStatus {
  ACTIVE = 'active',
  RESOLVED = 'resolved',
  DELETED = 'deleted',
}

export enum ReactionType {
  LIKE = 'like',
  LOVE = 'love',
  CELEBRATE = 'celebrate',
  THINKING = 'thinking',
  SAD = 'sad',
  ANGRY = 'angry',
}

export enum NotificationType {
  MENTION = 'mention',
  REPLY = 'reply',
  SHARE = 'share',
  COMMENT = 'comment',
  ASSIGNMENT = 'assignment',
  ALERT = 'alert',
  SYSTEM = 'system',
}

export enum WSMessageType {
  // Connection
  CONNECT = 'connect',
  DISCONNECT = 'disconnect',
  PING = 'ping',
  PONG = 'pong',

  // Presence
  PRESENCE_UPDATE = 'presence_update',
  CURSOR_MOVE = 'cursor_move',
  USER_JOINED = 'user_joined',
  USER_LEFT = 'user_left',

  // Collaboration
  EDIT_START = 'edit_start',
  EDIT_END = 'edit_end',
  CHANGE = 'change',
  SYNC = 'sync',

  // Comments
  COMMENT_ADDED = 'comment_added',
  COMMENT_UPDATED = 'comment_updated',
  COMMENT_DELETED = 'comment_deleted',
  REACTION_ADDED = 'reaction_added',
  REACTION_REMOVED = 'reaction_removed',

  // Activity
  ACTIVITY = 'activity',
  NOTIFICATION = 'notification',

  // Errors
  ERROR = 'error',
}

// Presence Types

export interface CursorPosition {
  x: number;
  y: number;
  element_id?: string | null;
  element_type?: string | null;
}

export interface UserPresence {
  user_id: string;
  user_name: string;
  user_email: string;
  avatar_url?: string | null;
  status: PresenceStatus;
  color: string;
  cursor?: CursorPosition | null;
  current_resource_type?: string | null;
  current_resource_id?: string | null;
  last_activity: string;
  connected_at: string;
  device_type?: string | null;
}

export interface PresenceUpdate {
  user_id: string;
  cursor?: CursorPosition | null;
  status?: PresenceStatus | null;
  current_resource_type?: string | null;
  current_resource_id?: string | null;
}

export interface RoomPresence {
  resource_type: string;
  resource_id: string;
  users: UserPresence[];
  total_count: number;
}

export interface PresenceResponse {
  users: UserPresence[];
  room: string;
  your_color: string;
}

// Comment Types

export interface CommentMention {
  user_id: string;
  user_name: string;
  user_email: string;
  start_index: number;
  end_index: number;
}

export interface CommentAttachment {
  id: string;
  file_name: string;
  file_url: string;
  file_type: string;
  file_size: number;
  thumbnail_url?: string | null;
}

export interface CommentReaction {
  reaction_type: ReactionType;
  user_id: string;
  user_name: string;
  created_at: string;
}

export interface CommentCreate {
  content: string;
  resource_type: string;
  resource_id: string;
  parent_id?: string | null;
  mentions?: string[];
  position?: Record<string, unknown> | null;
  attachments?: string[];
}

export interface CommentUpdate {
  content?: string | null;
  status?: CommentStatus | null;
  mentions?: string[] | null;
}

export interface Comment {
  id: string;
  content: string;
  resource_type: string;
  resource_id: string;
  parent_id?: string | null;
  author_id: string;
  author_name: string;
  author_email: string;
  author_avatar?: string | null;
  status: CommentStatus;
  mentions: CommentMention[];
  reactions: CommentReaction[];
  attachments: CommentAttachment[];
  position?: Record<string, unknown> | null;
  reply_count: number;
  is_edited: boolean;
  resolved_by?: string | null;
  resolved_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CommentThread {
  comment: Comment;
  replies: Comment[];
  total_replies: number;
}

export interface CommentListResponse {
  comments: CommentThread[];
  total_count: number;
  has_more: boolean;
}

// Activity Types

export interface ActivityActor {
  user_id: string;
  user_name: string;
  user_email: string;
  avatar_url?: string | null;
}

export interface ActivityTarget {
  resource_type: string;
  resource_id: string;
  resource_name: string;
  resource_url?: string | null;
}

export interface Activity {
  id: string;
  activity_type: ActivityType;
  actor: ActivityActor;
  target: ActivityTarget;
  workspace_id?: string | null;
  description: string;
  metadata: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

export interface ActivityFeed {
  activities: Activity[];
  total_count: number;
  unread_count: number;
  has_more: boolean;
}

// Edit Lock Types

export interface EditLock {
  resource_type: string;
  resource_id: string;
  element_id?: string | null;
  locked_by: string;
  locked_by_name: string;
  locked_at: string;
  expires_at: string;
}

// Session Types

export interface CollaborationSession {
  session_id: string;
  resource_type: string;
  resource_id: string;
  started_at: string;
  participants: UserPresence[];
  active_locks: EditLock[];
  change_count: number;
  last_change_at?: string | null;
}

// Notification Types

export interface Notification {
  id: string;
  notification_type: NotificationType;
  title: string;
  body: string;
  actor?: ActivityActor | null;
  target?: ActivityTarget | null;
  action_url?: string | null;
  is_read: boolean;
  read_at?: string | null;
  created_at: string;
}

export interface NotificationPreferences {
  user_id: string;
  email_mentions: boolean;
  email_replies: boolean;
  email_shares: boolean;
  email_comments: boolean;
  email_assignments: boolean;
  email_alerts: boolean;
  push_mentions: boolean;
  push_replies: boolean;
  push_shares: boolean;
  push_comments: boolean;
  push_assignments: boolean;
  push_alerts: boolean;
  digest_frequency: 'none' | 'daily' | 'weekly';
}

export interface NotificationListResponse {
  notifications: Notification[];
  total_count: number;
  unread_count: number;
  has_more: boolean;
}

// WebSocket Types

export interface WSMessage {
  type: WSMessageType;
  room?: string | null;
  sender_id?: string | null;
  payload: Record<string, unknown>;
  timestamp: string;
}

export interface WSError {
  code: string;
  message: string;
  details?: Record<string, unknown> | null;
}

// Constants

export const PRESENCE_COLORS = [
  '#6366f1', // Indigo
  '#8b5cf6', // Violet
  '#ec4899', // Pink
  '#f43f5e', // Rose
  '#f97316', // Orange
  '#eab308', // Yellow
  '#22c55e', // Green
  '#14b8a6', // Teal
  '#06b6d4', // Cyan
  '#3b82f6', // Blue
];

export const PRESENCE_TIMEOUT_SECONDS = 30;
export const CURSOR_THROTTLE_MS = 50;
export const LOCK_TIMEOUT_SECONDS = 300;
export const HEARTBEAT_INTERVAL_MS = 10000;

// Reaction Emojis
export const REACTION_EMOJIS: Record<ReactionType, string> = {
  [ReactionType.LIKE]: '👍',
  [ReactionType.LOVE]: '❤️',
  [ReactionType.CELEBRATE]: '🎉',
  [ReactionType.THINKING]: '🤔',
  [ReactionType.SAD]: '😢',
  [ReactionType.ANGRY]: '😠',
};

// Activity Icons
export const ACTIVITY_ICONS: Record<ActivityType, string> = {
  [ActivityType.DASHBOARD_CREATED]: 'plus',
  [ActivityType.DASHBOARD_UPDATED]: 'edit',
  [ActivityType.DASHBOARD_DELETED]: 'trash',
  [ActivityType.DASHBOARD_SHARED]: 'share',
  [ActivityType.DASHBOARD_PUBLISHED]: 'globe',
  [ActivityType.CHART_CREATED]: 'bar-chart',
  [ActivityType.CHART_UPDATED]: 'edit',
  [ActivityType.CHART_DELETED]: 'trash',
  [ActivityType.COMMENT_ADDED]: 'message-circle',
  [ActivityType.COMMENT_REPLIED]: 'reply',
  [ActivityType.COMMENT_RESOLVED]: 'check-circle',
  [ActivityType.USER_JOINED]: 'user-plus',
  [ActivityType.USER_LEFT]: 'user-minus',
  [ActivityType.DATA_REFRESHED]: 'refresh-cw',
  [ActivityType.ALERT_TRIGGERED]: 'alert-triangle',
  [ActivityType.REPORT_GENERATED]: 'file-text',
  [ActivityType.CONNECTION_CREATED]: 'database',
  [ActivityType.CONNECTION_UPDATED]: 'database',
};

// Helper Functions

export function getPresenceColor(userIndex: number): string {
  return PRESENCE_COLORS[userIndex % PRESENCE_COLORS.length];
}

export function generateRoomId(resourceType: string, resourceId: string): string {
  return `${resourceType}:${resourceId}`;
}

export function parseRoomId(room: string): { resourceType: string; resourceId: string } {
  const [resourceType, resourceId] = room.split(':');
  return { resourceType, resourceId };
}

export function formatTimeAgo(date: string | Date): string {
  const now = new Date();
  const then = new Date(date);
  const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return then.toLocaleDateString();
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function isLockExpired(lock: EditLock): boolean {
  return new Date(lock.expires_at) < new Date();
}

export function canEdit(locks: EditLock[], userId: string, elementId?: string): boolean {
  const relevantLocks = elementId
    ? locks.filter((l) => l.element_id === elementId)
    : locks.filter((l) => !l.element_id);

  return relevantLocks.every((l) => l.locked_by === userId || isLockExpired(l));
}

export function getReactionCounts(reactions: CommentReaction[]): Record<ReactionType, number> {
  const counts: Record<ReactionType, number> = {
    [ReactionType.LIKE]: 0,
    [ReactionType.LOVE]: 0,
    [ReactionType.CELEBRATE]: 0,
    [ReactionType.THINKING]: 0,
    [ReactionType.SAD]: 0,
    [ReactionType.ANGRY]: 0,
  };

  reactions.forEach((r) => {
    counts[r.reaction_type]++;
  });

  return counts;
}

export function hasUserReacted(
  reactions: CommentReaction[],
  userId: string,
  reactionType?: ReactionType
): boolean {
  return reactions.some(
    (r) => r.user_id === userId && (!reactionType || r.reaction_type === reactionType)
  );
}

// WebSocket Connection Manager (Client-side utility)
export class CollaborationWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private room: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
  private handlers: Map<WSMessageType, ((payload: unknown) => void)[]> = new Map();

  constructor(url: string, room: string) {
    this.url = url;
    this.room = room;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${this.url}?room=${this.room}`);

        this.ws.onopen = () => {
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WSMessage = JSON.parse(event.data);
            this.dispatch(message.type, message.payload);
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
          }
        };

        this.ws.onclose = () => {
          this.stopHeartbeat();
          this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(type: WSMessageType, payload: Record<string, unknown>): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message: WSMessage = {
        type,
        room: this.room,
        payload,
        timestamp: new Date().toISOString(),
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  on(type: WSMessageType, handler: (payload: unknown) => void): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, []);
    }
    this.handlers.get(type)!.push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.handlers.get(type);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index !== -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  private dispatch(type: WSMessageType, payload: unknown): void {
    const handlers = this.handlers.get(type);
    if (handlers) {
      handlers.forEach((handler) => handler(payload));
    }
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.send(WSMessageType.PING, {});
    }, HEARTBEAT_INTERVAL_MS);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      setTimeout(() => this.connect(), delay);
    }
  }
}
