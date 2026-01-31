"""
Embed Schemas

Pydantic schemas for embed SDK API.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime


# Enums

class EmbedResourceType(str, Enum):
    """Types of embeddable resources"""
    DASHBOARD = "dashboard"
    CHART = "chart"
    REPORT = "report"


class EmbedTheme(str, Enum):
    """Embed themes"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    CUSTOM = "custom"


class DeviceType(str, Enum):
    """Device classifications"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    UNKNOWN = "unknown"


# Token Schemas

class EmbedTokenBase(BaseModel):
    """Base embed token schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    resource_type: EmbedResourceType
    resource_id: str


class EmbedTokenCreate(EmbedTokenBase):
    """Schema for creating an embed token"""
    workspace_id: Optional[str] = None

    # Permissions
    allow_interactions: bool = True
    allow_export: bool = False
    allow_fullscreen: bool = True
    allow_comments: bool = False

    # Appearance
    theme: EmbedTheme = EmbedTheme.AUTO
    show_header: bool = True
    show_toolbar: bool = False
    custom_css: Optional[str] = None

    # Restrictions
    allowed_domains: list[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
    max_views: Optional[int] = Field(None, ge=1)

    # Additional settings
    settings: dict[str, Any] = Field(default_factory=dict)


class EmbedTokenUpdate(BaseModel):
    """Schema for updating an embed token"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

    # Permissions
    allow_interactions: Optional[bool] = None
    allow_export: Optional[bool] = None
    allow_fullscreen: Optional[bool] = None
    allow_comments: Optional[bool] = None

    # Appearance
    theme: Optional[EmbedTheme] = None
    show_header: Optional[bool] = None
    show_toolbar: Optional[bool] = None
    custom_css: Optional[str] = None

    # Restrictions
    allowed_domains: Optional[list[str]] = None
    expires_at: Optional[datetime] = None
    max_views: Optional[int] = Field(None, ge=1)

    # Status
    is_active: Optional[bool] = None

    # Settings
    settings: Optional[dict[str, Any]] = None


class EmbedTokenResponse(EmbedTokenBase):
    """Schema for embed token response"""
    id: str
    token: Optional[str] = None  # Only included on creation
    created_by: str
    workspace_id: Optional[str] = None

    # Permissions
    allow_interactions: bool
    allow_export: bool
    allow_fullscreen: bool
    allow_comments: bool

    # Appearance
    theme: EmbedTheme
    show_header: bool
    show_toolbar: bool
    custom_css: Optional[str] = None

    # Restrictions
    allowed_domains: list[str]
    expires_at: Optional[datetime] = None
    max_views: Optional[int] = None
    view_count: int

    # Status
    is_active: bool
    revoked_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime
    last_used_at: Optional[datetime] = None

    # Settings
    settings: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class EmbedTokenSummary(BaseModel):
    """Summary of embed token for lists"""
    id: str
    name: str
    resource_type: EmbedResourceType
    resource_id: str
    is_active: bool
    view_count: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None


# Embed URL Schemas

class EmbedUrlRequest(BaseModel):
    """Request to generate an embed URL"""
    token_id: str
    params: dict[str, Any] = Field(default_factory=dict)


class EmbedUrlResponse(BaseModel):
    """Generated embed URL response"""
    url: str
    iframe_html: str
    token_id: str
    expires_at: Optional[datetime] = None


# Embed Validation

class EmbedValidationRequest(BaseModel):
    """Request to validate an embed token"""
    token: str
    origin: Optional[str] = None


class EmbedValidationResponse(BaseModel):
    """Result of embed token validation"""
    valid: bool
    resource_type: Optional[EmbedResourceType] = None
    resource_id: Optional[str] = None
    permissions: dict[str, bool] = Field(default_factory=dict)
    appearance: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    session_id: Optional[str] = None


# Session Schemas

class EmbedSessionStart(BaseModel):
    """Request to start an embed session"""
    token: str
    origin_url: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None


class EmbedSessionResponse(BaseModel):
    """Embed session response"""
    session_id: str
    resource_type: EmbedResourceType
    resource_id: str
    permissions: dict[str, bool]
    appearance: dict[str, Any]


class EmbedSessionEnd(BaseModel):
    """Request to end an embed session"""
    session_id: str
    duration_seconds: Optional[int] = None
    interaction_count: Optional[int] = None
    filter_changes: Optional[int] = None
    exports_count: Optional[int] = None


class EmbedSessionTrack(BaseModel):
    """Track an embed session event"""
    session_id: str
    event_type: str  # interaction, filter_change, export, etc.
    event_data: dict[str, Any] = Field(default_factory=dict)


# Analytics Schemas

class EmbedAnalyticsRequest(BaseModel):
    """Request for embed analytics"""
    token_id: Optional[str] = None
    resource_type: Optional[EmbedResourceType] = None
    resource_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    granularity: str = "day"  # day, week, month


class EmbedAnalyticsSummary(BaseModel):
    """Summary of embed analytics"""
    total_views: int
    unique_sessions: int
    total_interactions: int
    total_exports: int
    avg_duration_seconds: float
    views_by_device: dict[str, int]
    views_by_date: list[dict[str, Any]]
    top_domains: list[dict[str, Any]]


class EmbedTokenAnalytics(BaseModel):
    """Analytics for a specific token"""
    token_id: str
    token_name: str
    total_views: int
    unique_sessions: int
    avg_duration_seconds: float
    last_viewed_at: Optional[datetime] = None
    top_domains: list[str]


# Whitelist Schemas

class DomainWhitelistCreate(BaseModel):
    """Create a domain whitelist entry"""
    domain: str
    is_wildcard: bool = False
    notes: Optional[str] = None


class DomainWhitelistResponse(BaseModel):
    """Domain whitelist entry response"""
    id: str
    domain: str
    is_wildcard: bool
    is_active: bool
    added_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# SDK Configuration

class EmbedSDKConfig(BaseModel):
    """SDK configuration for the embed client"""
    base_url: str
    default_theme: EmbedTheme = EmbedTheme.AUTO
    auto_resize: bool = True
    loading_indicator: bool = True
    error_handling: str = "display"  # display, callback, silent
    sandbox_attributes: list[str] = Field(
        default_factory=lambda: [
            "allow-scripts",
            "allow-same-origin",
            "allow-popups",
            "allow-forms",
        ]
    )


# JavaScript SDK Code Generation

class EmbedCodeRequest(BaseModel):
    """Request to generate embed code"""
    token_id: str
    width: str = "100%"
    height: str = "600px"
    include_sdk: bool = True
    framework: str = "vanilla"  # vanilla, react, vue, angular


class EmbedCodeResponse(BaseModel):
    """Generated embed code"""
    html: str
    javascript: Optional[str] = None
    react_component: Optional[str] = None
    vue_component: Optional[str] = None
    iframe_url: str


# Helper Functions

def generate_iframe_html(
    url: str,
    width: str = "100%",
    height: str = "600px",
    title: str = "Embedded Dashboard",
    allow_fullscreen: bool = True,
) -> str:
    """Generate iframe HTML for embedding"""
    fullscreen_attr = 'allowfullscreen="true"' if allow_fullscreen else ''

    return f'''<iframe
  src="{url}"
  width="{width}"
  height="{height}"
  title="{title}"
  frameborder="0"
  {fullscreen_attr}
  sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
  style="border: none; border-radius: 8px;"
></iframe>'''


def generate_sdk_snippet(token: str, container_id: str = "embed-container") -> str:
    """Generate JavaScript SDK snippet"""
    return f'''<div id="{container_id}"></div>
<script src="/embed/sdk.js"></script>
<script>
  BheemEmbed.render({{
    token: '{token}',
    container: '#{container_id}',
    onLoad: function() {{ console.log('Embed loaded'); }},
    onError: function(err) {{ console.error('Embed error:', err); }},
    onInteraction: function(event) {{ console.log('Interaction:', event); }}
  }});
</script>'''


def generate_react_component(token: str) -> str:
    """Generate React component code"""
    return f'''import {{ BheemEmbed }} from '@bheem/embed-sdk';

function EmbeddedDashboard() {{
  return (
    <BheemEmbed
      token="{token}"
      width="100%"
      height="600px"
      onLoad={{() => console.log('Loaded')}}
      onError={{(err) => console.error(err)}}
    />
  );
}}

export default EmbeddedDashboard;'''


def generate_vue_component(token: str) -> str:
    """Generate Vue component code"""
    return f'''<template>
  <bheem-embed
    token="{token}"
    width="100%"
    height="600px"
    @load="onLoad"
    @error="onError"
  />
</template>

<script>
import {{ BheemEmbed }} from '@bheem/embed-sdk/vue';

export default {{
  components: {{ BheemEmbed }},
  methods: {{
    onLoad() {{ console.log('Loaded'); }},
    onError(err) {{ console.error(err); }}
  }}
}};
</script>'''


def validate_domain(domain: str, allowed_domains: list[str]) -> bool:
    """
    Validate if a domain is in the allowed list.

    Supports wildcard domains like *.example.com
    """
    if not allowed_domains:
        return True  # No restrictions

    for allowed in allowed_domains:
        if allowed.startswith("*."):
            # Wildcard match
            suffix = allowed[2:]
            if domain.endswith(suffix) or domain == suffix[1:]:
                return True
        elif domain == allowed:
            return True

    return False


# Token Constants

TOKEN_LENGTH = 32
TOKEN_PREFIX = "bhe_"  # Bheem Embed token prefix
DEFAULT_EXPIRY_DAYS = 365
MAX_ALLOWED_DOMAINS = 50
