"""
Shortcuts & Command Palette Schemas

Pydantic schemas for keyboard shortcuts and command palette features.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class CommandCategory(str, Enum):
    """Command categories for organization"""
    NAVIGATION = "navigation"
    DASHBOARD = "dashboard"
    CHART = "chart"
    DATA = "data"
    EDIT = "edit"
    VIEW = "view"
    HELP = "help"
    SYSTEM = "system"
    RECENT = "recent"
    FAVORITE = "favorite"


class ActionType(str, Enum):
    """Types of actions that can be triggered"""
    NAVIGATE = "navigate"  # Navigate to a route
    OPEN = "open"  # Open a resource
    CREATE = "create"  # Create new resource
    SEARCH = "search"  # Search action
    TOGGLE = "toggle"  # Toggle state
    EXECUTE = "execute"  # Execute function
    MODAL = "modal"  # Open modal
    EXTERNAL = "external"  # External link


class ShortcutScope(str, Enum):
    """Scope where shortcut is active"""
    GLOBAL = "global"  # Active everywhere
    DASHBOARD = "dashboard"  # Only in dashboard view
    CHART = "chart"  # Only in chart builder
    EDITOR = "editor"  # Only in SQL/code editor
    TABLE = "table"  # Only in table view
    MODAL = "modal"  # Only when modal is open


# Shortcut Models

class KeyBinding(BaseModel):
    """Single key binding"""
    key: str  # Main key (e.g., 'k', 'Enter', 'Escape')
    modifiers: list[str] = Field(default_factory=list)  # ['cmd', 'shift', 'alt', 'ctrl']
    display: Optional[str] = None  # Display string (e.g., '⌘K')


class ShortcutAction(BaseModel):
    """Action triggered by shortcut"""
    action_type: ActionType
    target: Optional[str] = None  # Route, function name, or resource ID
    params: dict[str, Any] = Field(default_factory=dict)


class Shortcut(BaseModel):
    """Keyboard shortcut definition"""
    id: str
    name: str
    description: Optional[str] = None
    category: CommandCategory
    key_binding: KeyBinding
    action: ShortcutAction
    scope: ShortcutScope = ShortcutScope.GLOBAL
    enabled: bool = True
    is_default: bool = True
    is_customizable: bool = True


class ShortcutOverride(BaseModel):
    """User override for a shortcut"""
    shortcut_id: str
    key_binding: Optional[KeyBinding] = None  # New binding
    enabled: Optional[bool] = None  # Override enabled state


# Command Palette Models

class CommandIcon(BaseModel):
    """Icon for a command"""
    type: str = "lucide"  # lucide, emoji, url
    value: str  # Icon name, emoji, or URL


class Command(BaseModel):
    """Command palette item"""
    id: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[CommandIcon] = None
    category: CommandCategory
    keywords: list[str] = Field(default_factory=list)  # Search keywords
    action: ShortcutAction
    shortcut: Optional[KeyBinding] = None  # Associated shortcut
    score: float = 0  # Relevance score for sorting
    is_recent: bool = False
    is_favorite: bool = False
    last_used: Optional[datetime] = None
    use_count: int = 0


class CommandGroup(BaseModel):
    """Group of commands"""
    id: str
    name: str
    commands: list[Command]
    priority: int = 0


class CommandPaletteState(BaseModel):
    """Current state of command palette"""
    is_open: bool = False
    query: str = ""
    selected_index: int = 0
    mode: str = "search"  # search, recent, actions
    filter_category: Optional[CommandCategory] = None


# User Preferences

class ShortcutPreferences(BaseModel):
    """User's shortcut preferences"""
    user_id: str
    overrides: list[ShortcutOverride] = Field(default_factory=list)
    disabled_shortcuts: list[str] = Field(default_factory=list)  # Shortcut IDs to disable
    custom_shortcuts: list[Shortcut] = Field(default_factory=list)
    show_hints: bool = True  # Show shortcut hints in UI
    enable_vim_mode: bool = False  # Vim-like navigation
    hold_time_ms: int = 500  # Time to show shortcut overlay
    updated_at: Optional[datetime] = None


class RecentCommand(BaseModel):
    """Recently used command"""
    command_id: str
    used_at: datetime
    context: Optional[dict[str, Any]] = None  # Context when used


class CommandHistory(BaseModel):
    """Command usage history"""
    user_id: str
    recent_commands: list[RecentCommand] = Field(default_factory=list, max_length=50)
    favorite_commands: list[str] = Field(default_factory=list, max_length=20)  # Command IDs
    command_counts: dict[str, int] = Field(default_factory=dict)


# Search Models

class CommandSearchResult(BaseModel):
    """Search result from command palette"""
    command: Command
    match_type: str  # title, keyword, description
    match_positions: list[int] = Field(default_factory=list)  # Positions of matched chars
    score: float


class CommandSearchResponse(BaseModel):
    """Response from command search"""
    results: list[CommandSearchResult]
    total: int
    query: str
    suggestions: list[str] = Field(default_factory=list)


# Default Commands and Shortcuts

DEFAULT_SHORTCUTS: list[Shortcut] = [
    # Navigation
    Shortcut(
        id="open_command_palette",
        name="Open Command Palette",
        description="Open the command palette for quick actions",
        category=CommandCategory.SYSTEM,
        key_binding=KeyBinding(key="k", modifiers=["cmd"], display="⌘K"),
        action=ShortcutAction(action_type=ActionType.MODAL, target="command_palette"),
    ),
    Shortcut(
        id="go_home",
        name="Go to Home",
        description="Navigate to the home page",
        category=CommandCategory.NAVIGATION,
        key_binding=KeyBinding(key="h", modifiers=["cmd", "shift"], display="⌘⇧H"),
        action=ShortcutAction(action_type=ActionType.NAVIGATE, target="/home"),
    ),
    Shortcut(
        id="go_dashboards",
        name="Go to Dashboards",
        description="Navigate to dashboards list",
        category=CommandCategory.NAVIGATION,
        key_binding=KeyBinding(key="d", modifiers=["cmd", "shift"], display="⌘⇧D"),
        action=ShortcutAction(action_type=ActionType.NAVIGATE, target="/dashboards"),
    ),
    Shortcut(
        id="go_connections",
        name="Go to Connections",
        description="Navigate to data connections",
        category=CommandCategory.NAVIGATION,
        key_binding=KeyBinding(key="c", modifiers=["cmd", "shift"], display="⌘⇧C"),
        action=ShortcutAction(action_type=ActionType.NAVIGATE, target="/connections"),
    ),
    Shortcut(
        id="go_sql_lab",
        name="Go to SQL Lab",
        description="Open the SQL editor",
        category=CommandCategory.NAVIGATION,
        key_binding=KeyBinding(key="s", modifiers=["cmd", "shift"], display="⌘⇧S"),
        action=ShortcutAction(action_type=ActionType.NAVIGATE, target="/sql-lab"),
    ),

    # Dashboard
    Shortcut(
        id="new_dashboard",
        name="New Dashboard",
        description="Create a new dashboard",
        category=CommandCategory.DASHBOARD,
        key_binding=KeyBinding(key="n", modifiers=["cmd"], display="⌘N"),
        action=ShortcutAction(action_type=ActionType.NAVIGATE, target="/dashboards/new"),
        scope=ShortcutScope.DASHBOARD,
    ),
    Shortcut(
        id="save_dashboard",
        name="Save Dashboard",
        description="Save current dashboard",
        category=CommandCategory.DASHBOARD,
        key_binding=KeyBinding(key="s", modifiers=["cmd"], display="⌘S"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="save_dashboard"),
        scope=ShortcutScope.DASHBOARD,
    ),
    Shortcut(
        id="refresh_dashboard",
        name="Refresh Dashboard",
        description="Refresh all charts",
        category=CommandCategory.DASHBOARD,
        key_binding=KeyBinding(key="r", modifiers=["cmd"], display="⌘R"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="refresh_dashboard"),
        scope=ShortcutScope.DASHBOARD,
    ),

    # Chart
    Shortcut(
        id="new_chart",
        name="New Chart",
        description="Create a new chart",
        category=CommandCategory.CHART,
        key_binding=KeyBinding(key="n", modifiers=["cmd", "shift"], display="⌘⇧N"),
        action=ShortcutAction(action_type=ActionType.NAVIGATE, target="/charts/new"),
    ),

    # Edit
    Shortcut(
        id="undo",
        name="Undo",
        description="Undo last action",
        category=CommandCategory.EDIT,
        key_binding=KeyBinding(key="z", modifiers=["cmd"], display="⌘Z"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="undo"),
    ),
    Shortcut(
        id="redo",
        name="Redo",
        description="Redo last undone action",
        category=CommandCategory.EDIT,
        key_binding=KeyBinding(key="z", modifiers=["cmd", "shift"], display="⌘⇧Z"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="redo"),
    ),
    Shortcut(
        id="copy",
        name="Copy",
        description="Copy selected items",
        category=CommandCategory.EDIT,
        key_binding=KeyBinding(key="c", modifiers=["cmd"], display="⌘C"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="copy"),
    ),
    Shortcut(
        id="paste",
        name="Paste",
        description="Paste copied items",
        category=CommandCategory.EDIT,
        key_binding=KeyBinding(key="v", modifiers=["cmd"], display="⌘V"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="paste"),
    ),
    Shortcut(
        id="delete",
        name="Delete",
        description="Delete selected items",
        category=CommandCategory.EDIT,
        key_binding=KeyBinding(key="Backspace", modifiers=[], display="⌫"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="delete"),
    ),

    # View
    Shortcut(
        id="toggle_sidebar",
        name="Toggle Sidebar",
        description="Show or hide the sidebar",
        category=CommandCategory.VIEW,
        key_binding=KeyBinding(key="b", modifiers=["cmd"], display="⌘B"),
        action=ShortcutAction(action_type=ActionType.TOGGLE, target="sidebar"),
    ),
    Shortcut(
        id="toggle_fullscreen",
        name="Toggle Fullscreen",
        description="Enter or exit fullscreen mode",
        category=CommandCategory.VIEW,
        key_binding=KeyBinding(key="f", modifiers=["cmd", "shift"], display="⌘⇧F"),
        action=ShortcutAction(action_type=ActionType.TOGGLE, target="fullscreen"),
    ),
    Shortcut(
        id="zoom_in",
        name="Zoom In",
        description="Increase zoom level",
        category=CommandCategory.VIEW,
        key_binding=KeyBinding(key="+", modifiers=["cmd"], display="⌘+"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="zoom_in"),
    ),
    Shortcut(
        id="zoom_out",
        name="Zoom Out",
        description="Decrease zoom level",
        category=CommandCategory.VIEW,
        key_binding=KeyBinding(key="-", modifiers=["cmd"], display="⌘-"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="zoom_out"),
    ),

    # Help
    Shortcut(
        id="show_shortcuts",
        name="Show Keyboard Shortcuts",
        description="Display all keyboard shortcuts",
        category=CommandCategory.HELP,
        key_binding=KeyBinding(key="?", modifiers=["shift"], display="?"),
        action=ShortcutAction(action_type=ActionType.MODAL, target="shortcuts_modal"),
    ),

    # System
    Shortcut(
        id="search",
        name="Search",
        description="Open global search",
        category=CommandCategory.SYSTEM,
        key_binding=KeyBinding(key="/", modifiers=[], display="/"),
        action=ShortcutAction(action_type=ActionType.MODAL, target="search"),
    ),
    Shortcut(
        id="escape",
        name="Close/Cancel",
        description="Close modal or cancel action",
        category=CommandCategory.SYSTEM,
        key_binding=KeyBinding(key="Escape", modifiers=[], display="Esc"),
        action=ShortcutAction(action_type=ActionType.EXECUTE, target="escape"),
        is_customizable=False,
    ),
]


# Helper Functions

def get_modifier_symbol(modifier: str) -> str:
    """Get display symbol for a modifier key"""
    symbols = {
        "cmd": "⌘",
        "ctrl": "⌃",
        "alt": "⌥",
        "shift": "⇧",
        "meta": "⌘",
    }
    return symbols.get(modifier.lower(), modifier)


def format_key_binding(binding: KeyBinding) -> str:
    """Format a key binding for display"""
    if binding.display:
        return binding.display

    parts = [get_modifier_symbol(m) for m in binding.modifiers]
    parts.append(binding.key.upper() if len(binding.key) == 1 else binding.key)
    return "".join(parts)


def match_key_event(binding: KeyBinding, key: str, modifiers: list[str]) -> bool:
    """Check if a key event matches a binding"""
    if binding.key.lower() != key.lower():
        return False

    binding_mods = set(m.lower() for m in binding.modifiers)
    event_mods = set(m.lower() for m in modifiers)

    return binding_mods == event_mods


def fuzzy_match(query: str, text: str) -> tuple[bool, float, list[int]]:
    """
    Fuzzy match a query against text.
    Returns (matched, score, positions).
    """
    query = query.lower()
    text = text.lower()

    if not query:
        return True, 1.0, []

    positions = []
    query_idx = 0
    consecutive = 0
    score = 0

    for text_idx, char in enumerate(text):
        if query_idx < len(query) and char == query[query_idx]:
            positions.append(text_idx)

            # Bonus for consecutive matches
            if positions and text_idx == positions[-1] + 1:
                consecutive += 1
                score += consecutive * 2
            else:
                consecutive = 0
                score += 1

            # Bonus for word starts
            if text_idx == 0 or text[text_idx - 1] in " -_":
                score += 5

            query_idx += 1

    matched = query_idx == len(query)
    final_score = score / len(text) if matched else 0

    return matched, final_score, positions
