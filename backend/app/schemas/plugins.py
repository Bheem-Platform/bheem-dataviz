"""
Plugin Architecture Schemas

Pydantic schemas for plugin manifests, lifecycle, hooks, and registry.
"""

from typing import Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class PluginType(str, Enum):
    """Types of plugins"""
    CONNECTOR = "connector"  # Data source connectors
    VISUALIZATION = "visualization"  # Custom chart types
    TRANSFORM = "transform"  # Data transformations
    EXPORT = "export"  # Export formats
    AUTH = "auth"  # Authentication providers
    THEME = "theme"  # UI themes
    WIDGET = "widget"  # Dashboard widgets
    INTEGRATION = "integration"  # Third-party integrations
    AI = "ai"  # AI/ML extensions


class PluginStatus(str, Enum):
    """Plugin status"""
    AVAILABLE = "available"  # In registry, not installed
    INSTALLED = "installed"  # Installed but not enabled
    ENABLED = "enabled"  # Active and running
    DISABLED = "disabled"  # Installed but disabled
    ERROR = "error"  # Failed to load
    UPDATING = "updating"  # Being updated
    DEPRECATED = "deprecated"  # Marked for removal


class HookType(str, Enum):
    """Plugin hook types"""
    # Data hooks
    BEFORE_QUERY = "before_query"
    AFTER_QUERY = "after_query"
    BEFORE_TRANSFORM = "before_transform"
    AFTER_TRANSFORM = "after_transform"

    # UI hooks
    DASHBOARD_RENDER = "dashboard_render"
    CHART_RENDER = "chart_render"
    SIDEBAR_MENU = "sidebar_menu"
    TOOLBAR_ACTION = "toolbar_action"
    CONTEXT_MENU = "context_menu"

    # Auth hooks
    BEFORE_AUTH = "before_auth"
    AFTER_AUTH = "after_auth"

    # Export hooks
    BEFORE_EXPORT = "before_export"
    AFTER_EXPORT = "after_export"

    # Lifecycle hooks
    ON_INSTALL = "on_install"
    ON_ENABLE = "on_enable"
    ON_DISABLE = "on_disable"
    ON_UNINSTALL = "on_uninstall"
    ON_UPDATE = "on_update"


class PermissionScope(str, Enum):
    """Plugin permission scopes"""
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    READ_CONFIG = "read_config"
    WRITE_CONFIG = "write_config"
    NETWORK = "network"
    STORAGE = "storage"
    UI = "ui"
    AUTH = "auth"
    ADMIN = "admin"


# Manifest Models

class PluginAuthor(BaseModel):
    """Plugin author information"""
    name: str
    email: Optional[str] = None
    url: Optional[str] = None


class PluginDependency(BaseModel):
    """Plugin dependency"""
    plugin_id: str
    version: str  # Semver range, e.g., "^1.0.0"
    optional: bool = False


class PluginAsset(BaseModel):
    """Plugin asset (JS, CSS, images)"""
    type: str  # js, css, image, font
    path: str
    load_on: str = "enable"  # enable, dashboard, chart, etc.
    priority: int = 0


class PluginConfig(BaseModel):
    """Plugin configuration schema"""
    key: str
    type: str  # string, number, boolean, select, json
    label: str
    description: Optional[str] = None
    default: Optional[Any] = None
    required: bool = False
    options: list[dict[str, Any]] = Field(default_factory=list)  # For select type
    validation: Optional[dict[str, Any]] = None


class PluginHook(BaseModel):
    """Plugin hook registration"""
    type: HookType
    handler: str  # Function name or path
    priority: int = 10  # Lower = runs first
    async_: bool = Field(False, alias="async")
    conditions: dict[str, Any] = Field(default_factory=dict)


class PluginEndpoint(BaseModel):
    """Custom API endpoint provided by plugin"""
    path: str
    method: str
    handler: str
    description: Optional[str] = None
    requires_auth: bool = True


class PluginManifest(BaseModel):
    """Plugin manifest (plugin.json)"""
    # Required fields
    id: str  # Unique identifier, e.g., "bheem-connector-snowflake"
    name: str
    version: str  # Semver
    description: str
    type: PluginType

    # Author info
    author: PluginAuthor
    license: str = "MIT"
    homepage: Optional[str] = None
    repository: Optional[str] = None

    # Compatibility
    min_app_version: str = "1.0.0"
    max_app_version: Optional[str] = None

    # Entry points
    main: Optional[str] = None  # Server-side entry
    client: Optional[str] = None  # Client-side entry

    # Dependencies
    dependencies: list[PluginDependency] = Field(default_factory=list)
    peer_dependencies: list[str] = Field(default_factory=list)

    # Permissions
    permissions: list[PermissionScope] = Field(default_factory=list)

    # Configuration
    config_schema: list[PluginConfig] = Field(default_factory=list)

    # Hooks
    hooks: list[PluginHook] = Field(default_factory=list)

    # API endpoints
    endpoints: list[PluginEndpoint] = Field(default_factory=list)

    # Assets
    assets: list[PluginAsset] = Field(default_factory=list)

    # UI contributions
    sidebar_items: list[dict[str, Any]] = Field(default_factory=list)
    settings_pages: list[dict[str, Any]] = Field(default_factory=list)

    # Keywords for search
    keywords: list[str] = Field(default_factory=list)

    # Metadata
    icon: Optional[str] = None
    banner: Optional[str] = None
    screenshots: list[str] = Field(default_factory=list)
    changelog: Optional[str] = None


# Plugin Instance Models

class PluginInstance(BaseModel):
    """Installed plugin instance"""
    id: str
    manifest: PluginManifest
    status: PluginStatus = PluginStatus.INSTALLED

    # Installation info
    installed_at: datetime
    installed_by: str
    updated_at: Optional[datetime] = None
    version_installed: str

    # Configuration
    config: dict[str, Any] = Field(default_factory=dict)

    # Runtime
    enabled_at: Optional[datetime] = None
    disabled_at: Optional[datetime] = None
    last_error: Optional[str] = None
    error_count: int = 0

    # Usage
    load_time_ms: Optional[int] = None
    memory_usage_bytes: Optional[int] = None

    # Workspace scoping
    workspace_id: Optional[str] = None  # None = global
    enabled_workspaces: list[str] = Field(default_factory=list)


class PluginInstall(BaseModel):
    """Request to install a plugin"""
    plugin_id: str  # From registry
    version: Optional[str] = None  # None = latest
    config: dict[str, Any] = Field(default_factory=dict)
    workspace_id: Optional[str] = None
    enable_after_install: bool = True


class PluginUpdate(BaseModel):
    """Request to update a plugin"""
    config: Optional[dict[str, Any]] = None
    enabled_workspaces: Optional[list[str]] = None


# Registry Models

class RegistryPlugin(BaseModel):
    """Plugin in the registry"""
    id: str
    manifest: PluginManifest

    # Registry metadata
    downloads: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    verified: bool = False
    featured: bool = False

    # Versions
    versions: list[str] = Field(default_factory=list)
    latest_version: str

    # Timestamps
    published_at: datetime
    updated_at: Optional[datetime] = None


class RegistrySearchResult(BaseModel):
    """Registry search results"""
    plugins: list[RegistryPlugin]
    total: int
    page: int
    page_size: int
    has_more: bool


class RegistrySearchQuery(BaseModel):
    """Registry search query"""
    query: Optional[str] = None
    type: Optional[PluginType] = None
    keywords: list[str] = Field(default_factory=list)
    verified_only: bool = False
    sort_by: str = "downloads"  # downloads, rating, updated, name
    page: int = 1
    page_size: int = 20


# Hook Execution Models

class HookContext(BaseModel):
    """Context passed to hook handlers"""
    hook_type: HookType
    plugin_id: str
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HookResult(BaseModel):
    """Result from hook execution"""
    plugin_id: str
    hook_type: HookType
    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int = 0


class HookChainResult(BaseModel):
    """Result from executing a chain of hooks"""
    hook_type: HookType
    results: list[HookResult]
    final_data: dict[str, Any]
    total_time_ms: int
    any_failed: bool


# Event Models

class PluginEvent(BaseModel):
    """Plugin lifecycle event"""
    id: str
    plugin_id: str
    event_type: str  # installed, enabled, disabled, error, etc.
    timestamp: datetime
    user_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)


# Response Models

class PluginListResponse(BaseModel):
    """List of plugins response"""
    plugins: list[PluginInstance]
    total: int


class PluginStatsResponse(BaseModel):
    """Plugin statistics"""
    total_installed: int
    total_enabled: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    total_hooks_registered: int
    recent_errors: list[dict[str, Any]]


# Constants

OFFICIAL_REGISTRY_URL = "https://plugins.dataviz.bheemkodee.com"

DEFAULT_PLUGIN_CONFIG = {
    "enabled": True,
    "log_level": "info",
    "timeout_ms": 5000,
}

PLUGIN_TYPE_ICONS = {
    PluginType.CONNECTOR: "database",
    PluginType.VISUALIZATION: "bar-chart",
    PluginType.TRANSFORM: "git-branch",
    PluginType.EXPORT: "download",
    PluginType.AUTH: "lock",
    PluginType.THEME: "palette",
    PluginType.WIDGET: "layout",
    PluginType.INTEGRATION: "plug",
    PluginType.AI: "brain",
}

PLUGIN_TYPE_LABELS = {
    PluginType.CONNECTOR: "Data Connector",
    PluginType.VISUALIZATION: "Visualization",
    PluginType.TRANSFORM: "Transform",
    PluginType.EXPORT: "Export Format",
    PluginType.AUTH: "Authentication",
    PluginType.THEME: "Theme",
    PluginType.WIDGET: "Widget",
    PluginType.INTEGRATION: "Integration",
    PluginType.AI: "AI Extension",
}


# Helper Functions

def validate_semver(version: str) -> bool:
    """Validate semver version string."""
    import re
    pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    return bool(re.match(pattern, version))


def compare_versions(v1: str, v2: str) -> int:
    """Compare two semver versions. Returns -1, 0, or 1."""
    def parse(v):
        parts = v.split('-')[0].split('.')
        return [int(p) for p in parts]

    p1, p2 = parse(v1), parse(v2)

    for a, b in zip(p1, p2):
        if a < b:
            return -1
        if a > b:
            return 1

    return 0


def is_compatible(plugin_version: str, min_version: str, max_version: Optional[str] = None) -> bool:
    """Check if plugin is compatible with app version."""
    if compare_versions(plugin_version, min_version) < 0:
        return False

    if max_version and compare_versions(plugin_version, max_version) > 0:
        return False

    return True


def generate_plugin_id(author: str, name: str) -> str:
    """Generate a plugin ID from author and name."""
    import re
    author_slug = re.sub(r'[^a-z0-9-]', '', author.lower().replace(' ', '-'))
    name_slug = re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))
    return f"{author_slug}-{name_slug}"
