"""
SDK & API Documentation Schemas

Pydantic schemas for SDK tokens, API keys, rate limiting, and code generation.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class APIKeyType(str, Enum):
    """Types of API keys"""
    PUBLIC = "public"  # Read-only, client-side safe
    PRIVATE = "private"  # Full access, server-side only
    RESTRICTED = "restricted"  # Custom permissions


class APIKeyStatus(str, Enum):
    """API key status"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class SDKLanguage(str, Enum):
    """Supported SDK languages"""
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    CURL = "curl"
    GO = "go"
    RUBY = "ruby"
    PHP = "php"


class EndpointCategory(str, Enum):
    """API endpoint categories"""
    AUTH = "auth"
    CONNECTIONS = "connections"
    DASHBOARDS = "dashboards"
    CHARTS = "charts"
    QUERIES = "queries"
    DATASETS = "datasets"
    TRANSFORMS = "transforms"
    MODELS = "models"
    KPI = "kpi"
    AI = "ai"
    ADMIN = "admin"


class RateLimitPeriod(str, Enum):
    """Rate limit time periods"""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"


# API Key Models

class APIKeyPermissions(BaseModel):
    """Permissions for an API key"""
    # Resource permissions
    can_read_dashboards: bool = True
    can_write_dashboards: bool = False
    can_read_charts: bool = True
    can_write_charts: bool = False
    can_read_connections: bool = True
    can_write_connections: bool = False
    can_execute_queries: bool = True
    can_read_datasets: bool = True
    can_write_datasets: bool = False
    can_read_transforms: bool = True
    can_write_transforms: bool = False
    can_read_models: bool = True
    can_write_models: bool = False

    # Advanced permissions
    can_use_ai: bool = False
    can_embed: bool = True
    can_export: bool = True
    can_admin: bool = False

    # Workspace restrictions
    workspace_ids: list[str] = Field(default_factory=list)  # Empty = all workspaces
    dashboard_ids: list[str] = Field(default_factory=list)  # Empty = all dashboards


class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""
    requests_per_second: Optional[int] = None
    requests_per_minute: Optional[int] = 60
    requests_per_hour: Optional[int] = 1000
    requests_per_day: Optional[int] = 10000
    requests_per_month: Optional[int] = None
    burst_limit: int = 10  # Max burst above rate limit
    enabled: bool = True


class APIKey(BaseModel):
    """API key model"""
    id: str
    name: str
    description: Optional[str] = None
    key_prefix: str  # First 8 chars for identification
    key_hash: str  # Hashed full key

    key_type: APIKeyType = APIKeyType.PRIVATE
    status: APIKeyStatus = APIKeyStatus.ACTIVE

    # Ownership
    user_id: str
    workspace_id: Optional[str] = None
    organization_id: Optional[str] = None

    # Permissions
    permissions: APIKeyPermissions = Field(default_factory=APIKeyPermissions)
    rate_limits: RateLimitConfig = Field(default_factory=RateLimitConfig)

    # Security
    allowed_ips: list[str] = Field(default_factory=list)  # Empty = all IPs
    allowed_domains: list[str] = Field(default_factory=list)  # For CORS
    allowed_referrers: list[str] = Field(default_factory=list)

    # Expiration
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    # Metadata
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class APIKeyCreate(BaseModel):
    """Create API key request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    key_type: APIKeyType = APIKeyType.PRIVATE
    workspace_id: Optional[str] = None
    permissions: Optional[APIKeyPermissions] = None
    rate_limits: Optional[RateLimitConfig] = None
    allowed_ips: list[str] = Field(default_factory=list)
    allowed_domains: list[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)
    tags: list[str] = Field(default_factory=list)


class APIKeyUpdate(BaseModel):
    """Update API key request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    permissions: Optional[APIKeyPermissions] = None
    rate_limits: Optional[RateLimitConfig] = None
    allowed_ips: Optional[list[str]] = None
    allowed_domains: Optional[list[str]] = None
    status: Optional[APIKeyStatus] = None
    tags: Optional[list[str]] = None


class APIKeyResponse(BaseModel):
    """API key response (includes full key only on creation)"""
    api_key: APIKey
    key: Optional[str] = None  # Full key, only returned on creation


class APIKeyListResponse(BaseModel):
    """List of API keys"""
    keys: list[APIKey]
    total: int


# Usage Tracking Models

class UsageRecord(BaseModel):
    """Single usage record"""
    id: str
    api_key_id: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: int
    request_size_bytes: int
    response_size_bytes: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class UsageStats(BaseModel):
    """Usage statistics for a period"""
    api_key_id: str
    period_start: datetime
    period_end: datetime

    # Request counts
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0

    # By endpoint
    requests_by_endpoint: dict[str, int] = Field(default_factory=dict)
    requests_by_method: dict[str, int] = Field(default_factory=dict)
    requests_by_status: dict[int, int] = Field(default_factory=dict)

    # Performance
    avg_response_time_ms: float = 0
    p50_response_time_ms: float = 0
    p95_response_time_ms: float = 0
    p99_response_time_ms: float = 0

    # Data transfer
    total_request_bytes: int = 0
    total_response_bytes: int = 0

    # Unique
    unique_ips: int = 0
    unique_endpoints: int = 0


class UsageStatsResponse(BaseModel):
    """Usage stats response"""
    stats: UsageStats
    daily_breakdown: list[dict[str, Any]] = Field(default_factory=list)
    top_endpoints: list[dict[str, Any]] = Field(default_factory=list)


# Rate Limit Models

class RateLimitStatus(BaseModel):
    """Current rate limit status"""
    api_key_id: str
    period: RateLimitPeriod
    limit: int
    remaining: int
    reset_at: datetime
    is_limited: bool = False


class RateLimitResponse(BaseModel):
    """Rate limit info in response headers"""
    limit: int
    remaining: int
    reset: int  # Unix timestamp
    retry_after: Optional[int] = None  # Seconds until retry


# SDK Configuration Models

class SDKConfig(BaseModel):
    """SDK configuration for embedding"""
    api_key: str  # Public key
    base_url: str = "https://api.dataviz.bheemkodee.com"
    version: str = "1.0"

    # Feature flags
    enable_interactions: bool = True
    enable_export: bool = True
    enable_fullscreen: bool = True
    enable_comments: bool = False
    enable_refresh: bool = True

    # Theming
    theme: str = "light"  # light, dark, auto
    locale: str = "en"
    custom_css: Optional[str] = None

    # Security
    allowed_domains: list[str] = Field(default_factory=list)

    # Callbacks
    on_load: Optional[str] = None  # JS function name
    on_error: Optional[str] = None
    on_interaction: Optional[str] = None


class SDKInitOptions(BaseModel):
    """SDK initialization options"""
    container: str  # DOM selector or element ID
    resource_type: str  # dashboard, chart
    resource_id: str
    config: SDKConfig

    # Display options
    width: str = "100%"
    height: str = "600px"
    responsive: bool = True

    # Initial state
    filters: Optional[dict[str, Any]] = None
    variables: Optional[dict[str, Any]] = None


# Code Generation Models

class CodeSnippet(BaseModel):
    """Generated code snippet"""
    language: SDKLanguage
    code: str
    filename: Optional[str] = None
    description: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)


class CodeGenerationRequest(BaseModel):
    """Request to generate code"""
    language: SDKLanguage
    resource_type: str  # dashboard, chart, query
    resource_id: str
    include_auth: bool = True
    include_error_handling: bool = True
    include_types: bool = True  # For TS
    options: dict[str, Any] = Field(default_factory=dict)


class CodeGenerationResponse(BaseModel):
    """Generated code response"""
    snippets: list[CodeSnippet]
    setup_instructions: str
    documentation_url: Optional[str] = None


# API Documentation Models

class APIParameter(BaseModel):
    """API parameter documentation"""
    name: str
    type: str
    required: bool = False
    description: Optional[str] = None
    default: Optional[Any] = None
    enum_values: list[str] = Field(default_factory=list)
    example: Optional[Any] = None


class APIEndpoint(BaseModel):
    """API endpoint documentation"""
    path: str
    method: str
    summary: str
    description: Optional[str] = None
    category: EndpointCategory
    tags: list[str] = Field(default_factory=list)

    # Parameters
    path_params: list[APIParameter] = Field(default_factory=list)
    query_params: list[APIParameter] = Field(default_factory=list)
    body_schema: Optional[dict[str, Any]] = None

    # Response
    response_schema: Optional[dict[str, Any]] = None
    response_examples: dict[str, Any] = Field(default_factory=dict)

    # Security
    requires_auth: bool = True
    required_permissions: list[str] = Field(default_factory=list)
    rate_limited: bool = True

    # Metadata
    deprecated: bool = False
    version: str = "v1"


class APIEndpointGroup(BaseModel):
    """Group of related endpoints"""
    name: str
    description: Optional[str] = None
    category: EndpointCategory
    endpoints: list[APIEndpoint]


class APIDocumentation(BaseModel):
    """Full API documentation"""
    title: str = "Bheem DataViz API"
    version: str = "1.0.0"
    description: str = "REST API for Bheem DataViz platform"
    base_url: str = "https://api.dataviz.bheemkodee.com/api/v1"

    # Authentication
    auth_description: str = ""
    auth_examples: dict[str, str] = Field(default_factory=dict)

    # Endpoints
    groups: list[APIEndpointGroup] = Field(default_factory=list)

    # Schemas
    schemas: dict[str, Any] = Field(default_factory=dict)

    # SDKs
    sdk_languages: list[SDKLanguage] = Field(default_factory=list)
    sdk_download_urls: dict[str, str] = Field(default_factory=dict)


# Webhook Models (for SDK events)

class SDKWebhookEvent(BaseModel):
    """SDK event sent to webhooks"""
    id: str
    event_type: str  # embed.loaded, embed.error, embed.interaction
    api_key_id: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SDKWebhookConfig(BaseModel):
    """Webhook configuration for SDK events"""
    id: str
    api_key_id: str
    url: str
    secret: str  # For signature verification
    events: list[str] = Field(default_factory=list)  # Event types to send
    enabled: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None


# Constants

DEFAULT_RATE_LIMITS = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    requests_per_day=10000,
    burst_limit=10,
)

PUBLIC_KEY_RATE_LIMITS = RateLimitConfig(
    requests_per_minute=30,
    requests_per_hour=500,
    requests_per_day=5000,
    burst_limit=5,
)

SDK_LANGUAGES_INFO = {
    SDKLanguage.JAVASCRIPT: {
        "name": "JavaScript",
        "package": "@bheem/dataviz-sdk",
        "install": "npm install @bheem/dataviz-sdk",
    },
    SDKLanguage.TYPESCRIPT: {
        "name": "TypeScript",
        "package": "@bheem/dataviz-sdk",
        "install": "npm install @bheem/dataviz-sdk",
    },
    SDKLanguage.PYTHON: {
        "name": "Python",
        "package": "bheem-dataviz",
        "install": "pip install bheem-dataviz",
    },
    SDKLanguage.REACT: {
        "name": "React",
        "package": "@bheem/dataviz-react",
        "install": "npm install @bheem/dataviz-react",
    },
    SDKLanguage.VUE: {
        "name": "Vue",
        "package": "@bheem/dataviz-vue",
        "install": "npm install @bheem/dataviz-vue",
    },
    SDKLanguage.CURL: {
        "name": "cURL",
        "package": None,
        "install": None,
    },
}


# Helper Functions

def generate_api_key_prefix() -> str:
    """Generate API key prefix for identification"""
    import secrets
    return f"bv_{secrets.token_hex(4)}"


def hash_api_key(key: str) -> str:
    """Hash API key for storage"""
    import hashlib
    return hashlib.sha256(key.encode()).hexdigest()


def generate_full_api_key(prefix: str) -> str:
    """Generate full API key"""
    import secrets
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def mask_api_key(key: str) -> str:
    """Mask API key for display"""
    if len(key) < 12:
        return "*" * len(key)
    return f"{key[:8]}...{key[-4:]}"


def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    import re
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'

    return bool(
        re.match(ipv4_pattern, ip) or
        re.match(ipv6_pattern, ip) or
        re.match(cidr_pattern, ip)
    )
