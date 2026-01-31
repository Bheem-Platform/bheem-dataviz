"""
Advanced Sharing Schemas

Pydantic schemas for public links, password protection, and sharing features.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime
import hashlib
import secrets


# Enums

class ShareType(str, Enum):
    """Types of shared resources"""
    DASHBOARD = "dashboard"
    CHART = "chart"
    REPORT = "report"
    DATASET = "dataset"


class ShareAccess(str, Enum):
    """Access levels for shared links"""
    VIEW = "view"
    INTERACT = "interact"  # Can use filters, drill-down
    EXPORT = "export"  # Can export data
    FULL = "full"  # All permissions


class LinkStatus(str, Enum):
    """Status of a share link"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DISABLED = "disabled"


class ShareVisibility(str, Enum):
    """Visibility settings"""
    PUBLIC = "public"  # Anyone with link
    PASSWORD = "password"  # Requires password
    EMAIL = "email"  # Restricted to emails
    DOMAIN = "domain"  # Restricted to domain


# Share Link Models

class ShareLinkCreate(BaseModel):
    """Create a share link"""
    resource_type: ShareType
    resource_id: str
    name: Optional[str] = None
    description: Optional[str] = None

    # Access settings
    access_level: ShareAccess = ShareAccess.VIEW
    visibility: ShareVisibility = ShareVisibility.PUBLIC

    # Password protection
    password: Optional[str] = Field(None, min_length=4, max_length=100)

    # Email/Domain restrictions
    allowed_emails: list[str] = Field(default_factory=list)
    allowed_domains: list[str] = Field(default_factory=list)

    # Expiration
    expires_at: Optional[datetime] = None
    max_views: Optional[int] = Field(None, ge=1)

    # Branding
    custom_slug: Optional[str] = Field(None, min_length=3, max_length=50)
    hide_branding: bool = False
    custom_logo_url: Optional[str] = None

    # Analytics
    track_views: bool = True
    require_name: bool = False  # Require viewer to enter name

    # Filters/State
    preset_filters: Optional[dict[str, Any]] = None
    locked_filters: bool = False  # Prevent filter changes

    # Display options
    show_toolbar: bool = True
    show_export: bool = False
    fullscreen_only: bool = False
    theme: str = "light"  # light, dark, auto

    workspace_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ShareLinkUpdate(BaseModel):
    """Update a share link"""
    name: Optional[str] = None
    description: Optional[str] = None
    access_level: Optional[ShareAccess] = None
    visibility: Optional[ShareVisibility] = None
    password: Optional[str] = None
    allowed_emails: Optional[list[str]] = None
    allowed_domains: Optional[list[str]] = None
    expires_at: Optional[datetime] = None
    max_views: Optional[int] = None
    is_active: Optional[bool] = None
    hide_branding: Optional[bool] = None
    custom_logo_url: Optional[str] = None
    preset_filters: Optional[dict[str, Any]] = None
    locked_filters: Optional[bool] = None
    show_toolbar: Optional[bool] = None
    show_export: Optional[bool] = None
    theme: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class ShareLink(BaseModel):
    """Full share link object"""
    id: str
    token: str  # Unique share token
    short_code: str  # Short shareable code
    custom_slug: Optional[str] = None

    resource_type: ShareType
    resource_id: str
    resource_name: str

    name: Optional[str] = None
    description: Optional[str] = None

    # Access
    access_level: ShareAccess
    visibility: ShareVisibility
    has_password: bool = False

    # Restrictions
    allowed_emails: list[str] = Field(default_factory=list)
    allowed_domains: list[str] = Field(default_factory=list)

    # Expiration
    expires_at: Optional[datetime] = None
    max_views: Optional[int] = None

    # Status
    status: LinkStatus = LinkStatus.ACTIVE
    is_active: bool = True

    # Branding
    hide_branding: bool = False
    custom_logo_url: Optional[str] = None

    # Display
    preset_filters: Optional[dict[str, Any]] = None
    locked_filters: bool = False
    show_toolbar: bool = True
    show_export: bool = False
    fullscreen_only: bool = False
    theme: str = "light"

    # Analytics
    track_views: bool = True
    require_name: bool = False
    view_count: int = 0
    unique_viewers: int = 0
    last_viewed_at: Optional[datetime] = None

    # URLs
    share_url: str
    embed_url: str
    qr_code_url: Optional[str] = None

    # Owner
    created_by: str
    created_by_name: str
    workspace_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# View/Access Models

class ShareAccessRequest(BaseModel):
    """Request access to a shared resource"""
    token: str
    password: Optional[str] = None
    viewer_email: Optional[str] = None
    viewer_name: Optional[str] = None


class ShareAccessResponse(BaseModel):
    """Response after validating share access"""
    valid: bool
    access_level: Optional[ShareAccess] = None
    resource_type: Optional[ShareType] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    preset_filters: Optional[dict[str, Any]] = None
    locked_filters: bool = False
    show_toolbar: bool = True
    show_export: bool = False
    theme: str = "light"
    error: Optional[str] = None
    session_token: Optional[str] = None  # For tracking the session


class ShareView(BaseModel):
    """Record of a share view"""
    id: str
    share_link_id: str
    viewer_ip: Optional[str] = None
    viewer_email: Optional[str] = None
    viewer_name: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    device_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    interactions: int = 0
    viewed_at: datetime

    class Config:
        from_attributes = True


# Analytics Models

class ShareAnalytics(BaseModel):
    """Analytics for a share link"""
    share_link_id: str
    total_views: int
    unique_viewers: int
    avg_duration_seconds: float
    total_interactions: int

    views_by_day: list[dict[str, Any]]  # [{date, count}]
    views_by_country: list[dict[str, Any]]  # [{country, count}]
    views_by_device: list[dict[str, Any]]  # [{device, count}]
    views_by_referrer: list[dict[str, Any]]  # [{referrer, count}]

    top_viewers: list[dict[str, Any]]  # [{email/name, views, last_viewed}]
    recent_views: list[ShareView]

    period_start: datetime
    period_end: datetime


# QR Code Models

class QRCodeConfig(BaseModel):
    """QR code generation config"""
    size: int = Field(256, ge=64, le=1024)
    format: str = "png"  # png, svg
    error_correction: str = "M"  # L, M, Q, H
    foreground_color: str = "#000000"
    background_color: str = "#FFFFFF"
    include_logo: bool = False
    logo_url: Optional[str] = None
    logo_size_percent: int = 20


class QRCodeResponse(BaseModel):
    """Generated QR code response"""
    share_link_id: str
    qr_code_url: str
    qr_code_data: Optional[str] = None  # Base64 encoded
    share_url: str
    expires_at: Optional[datetime] = None


# Bulk Operations

class BulkShareCreate(BaseModel):
    """Create multiple share links"""
    resource_ids: list[str]
    resource_type: ShareType
    settings: ShareLinkCreate


class BulkShareResponse(BaseModel):
    """Response for bulk share creation"""
    created: list[ShareLink]
    failed: list[dict[str, str]]  # [{resource_id, error}]
    total_created: int
    total_failed: int


# Email Sharing

class EmailShareRequest(BaseModel):
    """Send share link via email"""
    share_link_id: str
    recipients: list[str] = Field(..., min_items=1, max_items=50)
    subject: Optional[str] = None
    message: Optional[str] = None
    include_preview: bool = True


class EmailShareResponse(BaseModel):
    """Response for email sharing"""
    sent_to: list[str]
    failed: list[dict[str, str]]  # [{email, error}]


# Share Templates

class ShareTemplate(BaseModel):
    """Reusable share settings template"""
    id: str
    name: str
    description: Optional[str] = None
    settings: ShareLinkCreate
    is_default: bool = False
    created_by: str
    workspace_id: Optional[str] = None
    created_at: datetime


# Constants

SHARE_TOKEN_LENGTH = 32
SHORT_CODE_LENGTH = 8
SESSION_TOKEN_LENGTH = 64
MAX_VIEWS_DEFAULT = None
EXPIRES_DAYS_DEFAULT = None


# Helper Functions

def generate_share_token() -> str:
    """Generate a secure share token"""
    return secrets.token_urlsafe(SHARE_TOKEN_LENGTH)


def generate_short_code() -> str:
    """Generate a short shareable code"""
    return secrets.token_urlsafe(SHORT_CODE_LENGTH)[:SHORT_CODE_LENGTH]


def generate_session_token() -> str:
    """Generate a viewer session token"""
    return secrets.token_urlsafe(SESSION_TOKEN_LENGTH)


def hash_password(password: str) -> str:
    """Hash a password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed


def validate_email_domain(email: str, allowed_domains: list[str]) -> bool:
    """Check if email domain is allowed"""
    if not allowed_domains:
        return True
    domain = email.split("@")[-1].lower()
    return any(domain == d.lower() or domain.endswith(f".{d.lower()}") for d in allowed_domains)


def validate_email_access(email: str, allowed_emails: list[str]) -> bool:
    """Check if email is in allowed list"""
    if not allowed_emails:
        return True
    return email.lower() in [e.lower() for e in allowed_emails]


def is_link_expired(link: ShareLink) -> bool:
    """Check if a share link has expired"""
    if link.expires_at and link.expires_at < datetime.utcnow():
        return True
    if link.max_views and link.view_count >= link.max_views:
        return True
    return False


def build_share_url(base_url: str, short_code: str, custom_slug: Optional[str] = None) -> str:
    """Build the full share URL"""
    identifier = custom_slug or short_code
    return f"{base_url}/s/{identifier}"


def build_embed_url(base_url: str, token: str) -> str:
    """Build the embed URL"""
    return f"{base_url}/embed/{token}"
