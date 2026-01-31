"""
Mobile Optimization Schemas

Pydantic schemas for mobile-optimized views and settings.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class LayoutMode(str, Enum):
    """Dashboard layout modes"""
    AUTO = "auto"
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class GestureType(str, Enum):
    """Touch gesture types"""
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PINCH = "pinch"
    SPREAD = "spread"


class GestureAction(str, Enum):
    """Actions triggered by gestures"""
    SELECT = "select"
    DRILL_DOWN = "drill_down"
    DRILL_UP = "drill_up"
    FILTER = "filter"
    EXPAND = "expand"
    COLLAPSE = "collapse"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    REFRESH = "refresh"
    SHARE = "share"
    EXPORT = "export"
    NEXT_CHART = "next_chart"
    PREV_CHART = "prev_chart"


class SyncStatus(str, Enum):
    """Offline sync status"""
    SYNCED = "synced"
    PENDING = "pending"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"


# Breakpoint Configuration

class Breakpoint(BaseModel):
    """Screen size breakpoint"""
    name: str
    min_width: int
    max_width: Optional[int] = None
    columns: int = 1
    gutter: int = 16
    margin: int = 16


DEFAULT_BREAKPOINTS = [
    Breakpoint(name="mobile", min_width=0, max_width=639, columns=1, gutter=8, margin=12),
    Breakpoint(name="tablet", min_width=640, max_width=1023, columns=2, gutter=16, margin=16),
    Breakpoint(name="desktop", min_width=1024, max_width=1279, columns=4, gutter=20, margin=20),
    Breakpoint(name="large", min_width=1280, max_width=None, columns=6, gutter=24, margin=24),
]


# Mobile Layout Configuration

class MobileChartConfig(BaseModel):
    """Chart configuration for mobile"""
    chart_id: str
    order: int = 0  # Display order on mobile
    visible: bool = True
    collapsed: bool = False
    height: int = 250
    simplified: bool = True  # Use simplified rendering
    touch_enabled: bool = True
    swipe_navigation: bool = True


class MobileDashboardLayout(BaseModel):
    """Mobile-specific dashboard layout"""
    dashboard_id: str
    enabled: bool = True
    layout_mode: LayoutMode = LayoutMode.AUTO

    # Chart configurations
    charts: list[MobileChartConfig] = Field(default_factory=list)

    # Layout settings
    stack_charts: bool = True  # Stack charts vertically
    show_chart_titles: bool = True
    compact_headers: bool = True
    hide_empty_charts: bool = True

    # Filter settings
    filter_position: str = "top"  # top, bottom, modal
    collapsible_filters: bool = True
    quick_filters_count: int = 3

    # Navigation
    show_navigation: bool = True
    bottom_navigation: bool = True
    swipe_between_charts: bool = True

    # Pull to refresh
    pull_to_refresh: bool = True

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Gesture Configuration

class GestureBinding(BaseModel):
    """Gesture to action binding"""
    gesture: GestureType
    action: GestureAction
    target: Optional[str] = None  # Element type: chart, filter, etc.
    params: dict[str, Any] = Field(default_factory=dict)


class GestureConfig(BaseModel):
    """Gesture configuration"""
    enabled: bool = True
    bindings: list[GestureBinding] = Field(default_factory=list)
    haptic_feedback: bool = True
    gesture_hints: bool = True  # Show gesture hints on long press


DEFAULT_GESTURE_BINDINGS = [
    GestureBinding(gesture=GestureType.TAP, action=GestureAction.SELECT),
    GestureBinding(gesture=GestureType.DOUBLE_TAP, action=GestureAction.DRILL_DOWN),
    GestureBinding(gesture=GestureType.LONG_PRESS, action=GestureAction.EXPAND),
    GestureBinding(gesture=GestureType.SWIPE_LEFT, action=GestureAction.NEXT_CHART),
    GestureBinding(gesture=GestureType.SWIPE_RIGHT, action=GestureAction.PREV_CHART),
    GestureBinding(gesture=GestureType.SWIPE_DOWN, action=GestureAction.REFRESH),
    GestureBinding(gesture=GestureType.PINCH, action=GestureAction.ZOOM_OUT),
    GestureBinding(gesture=GestureType.SPREAD, action=GestureAction.ZOOM_IN),
]


# Offline Configuration

class OfflineDataConfig(BaseModel):
    """Configuration for offline data"""
    enabled: bool = True
    max_cache_size_mb: int = 100
    cache_duration_hours: int = 24
    auto_sync: bool = True
    sync_on_wifi_only: bool = False
    priority_dashboards: list[str] = Field(default_factory=list)


class CachedDashboard(BaseModel):
    """Cached dashboard data"""
    dashboard_id: str
    dashboard_name: str
    cached_at: datetime
    expires_at: datetime
    size_bytes: int
    sync_status: SyncStatus
    charts_cached: int
    last_synced_at: Optional[datetime] = None
    pending_changes: int = 0


class OfflineSyncStatus(BaseModel):
    """Overall offline sync status"""
    enabled: bool
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    total_cached_mb: float
    max_cache_mb: int
    dashboards_cached: int
    pending_uploads: int
    sync_errors: int


# Push Notifications

class NotificationPreference(BaseModel):
    """Push notification preferences"""
    enabled: bool = True
    alert_notifications: bool = True
    report_notifications: bool = True
    mention_notifications: bool = True
    schedule_notifications: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None


class PushNotification(BaseModel):
    """Push notification"""
    id: str
    title: str
    body: str
    type: str  # alert, report, mention, etc.
    data: dict[str, Any] = Field(default_factory=dict)
    action_url: Optional[str] = None
    created_at: datetime
    read: bool = False
    read_at: Optional[datetime] = None


# Mobile User Settings

class MobileUserSettings(BaseModel):
    """User-specific mobile settings"""
    user_id: str
    layout_mode_preference: LayoutMode = LayoutMode.AUTO
    default_dashboard_id: Optional[str] = None
    quick_access_dashboards: list[str] = Field(default_factory=list)
    gesture_config: GestureConfig = Field(default_factory=GestureConfig)
    offline_config: OfflineDataConfig = Field(default_factory=OfflineDataConfig)
    notification_preferences: NotificationPreference = Field(default_factory=NotificationPreference)
    dark_mode: str = "auto"  # auto, light, dark
    font_size: str = "medium"  # small, medium, large
    data_saver_mode: bool = False
    biometric_auth: bool = False


# Device Information

class DeviceInfo(BaseModel):
    """Device information for analytics"""
    device_id: Optional[str] = None
    platform: str  # ios, android, web
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    screen_width: int
    screen_height: int
    pixel_ratio: float = 1.0
    is_tablet: bool = False
    supports_touch: bool = True
    push_token: Optional[str] = None


# Mobile Analytics

class MobileAnalyticsEvent(BaseModel):
    """Mobile analytics event"""
    event_type: str
    user_id: Optional[str] = None
    device_info: DeviceInfo
    dashboard_id: Optional[str] = None
    chart_id: Optional[str] = None
    gesture: Optional[GestureType] = None
    duration_ms: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime


class MobileUsageStats(BaseModel):
    """Mobile usage statistics"""
    total_sessions: int
    total_duration_minutes: int
    avg_session_duration_minutes: float
    most_viewed_dashboards: list[dict[str, Any]]
    gesture_usage: dict[str, int]
    offline_views: int
    device_breakdown: dict[str, int]


# Responsive Image

class ResponsiveImage(BaseModel):
    """Responsive image configuration"""
    original_url: str
    thumbnail_url: Optional[str] = None
    mobile_url: Optional[str] = None
    tablet_url: Optional[str] = None
    desktop_url: Optional[str] = None
    width: int
    height: int
    format: str = "webp"


# Mobile API Response Wrappers

class MobileResponse(BaseModel):
    """Wrapper for mobile API responses"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    cache_key: Optional[str] = None
    cache_ttl_seconds: int = 300
    offline_available: bool = False


class MobileDashboardResponse(BaseModel):
    """Mobile-optimized dashboard response"""
    dashboard_id: str
    name: str
    layout: MobileDashboardLayout
    charts: list[dict[str, Any]]
    filters: list[dict[str, Any]]
    last_updated: datetime
    cache_key: str
    offline_available: bool = False


# Constants

SUPPORTED_GESTURES = [g.value for g in GestureType]
SUPPORTED_ACTIONS = [a.value for a in GestureAction]

MOBILE_CHART_MIN_HEIGHT = 150
MOBILE_CHART_MAX_HEIGHT = 400
MOBILE_CHART_DEFAULT_HEIGHT = 250

DEFAULT_CACHE_DURATION_HOURS = 24
MAX_OFFLINE_DASHBOARDS = 10
MAX_CACHE_SIZE_MB = 500


# Helper Functions

def get_breakpoint_for_width(width: int) -> Breakpoint:
    """Get the appropriate breakpoint for a screen width"""
    for bp in reversed(DEFAULT_BREAKPOINTS):
        if width >= bp.min_width:
            if bp.max_width is None or width <= bp.max_width:
                return bp
    return DEFAULT_BREAKPOINTS[0]


def calculate_chart_height(
    base_height: int,
    screen_height: int,
    chart_count: int,
    layout_mode: LayoutMode,
) -> int:
    """Calculate optimal chart height for mobile"""
    if layout_mode == LayoutMode.MOBILE:
        # On mobile, show roughly 2 charts visible at once
        max_height = (screen_height - 150) // 2
        return min(base_height, max_height, MOBILE_CHART_MAX_HEIGHT)
    elif layout_mode == LayoutMode.TABLET:
        return min(base_height, 350)
    return base_height


def simplify_chart_config(chart_config: dict) -> dict:
    """Simplify chart configuration for mobile rendering"""
    simplified = chart_config.copy()

    # Reduce data points
    if "data" in simplified and isinstance(simplified["data"], list):
        if len(simplified["data"]) > 50:
            step = len(simplified["data"]) // 50
            simplified["data"] = simplified["data"][::step]

    # Simplify options
    options = simplified.get("options", {})
    options["animation"] = {"duration": 200}  # Faster animations
    options["responsive"] = True
    options["maintainAspectRatio"] = False

    # Reduce legend complexity
    if "legend" in options:
        options["legend"]["display"] = len(simplified.get("data", [])) <= 5

    simplified["options"] = options
    return simplified
