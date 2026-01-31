"""
Advanced Security Controls Schemas

Pydantic schemas for rate limiting, IP policies, session security,
password policies, API key management, and security configurations.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import datetime


# Enums

class RateLimitScope(str, Enum):
    """Rate limit scope"""
    GLOBAL = "global"
    USER = "user"
    IP = "ip"
    API_KEY = "api_key"
    ENDPOINT = "endpoint"


class RateLimitAction(str, Enum):
    """Action when rate limit exceeded"""
    BLOCK = "block"
    THROTTLE = "throttle"
    LOG_ONLY = "log_only"
    CHALLENGE = "challenge"  # CAPTCHA or MFA


class IPListType(str, Enum):
    """IP list type"""
    ALLOWLIST = "allowlist"
    BLOCKLIST = "blocklist"


class IPMatchType(str, Enum):
    """IP matching type"""
    EXACT = "exact"
    CIDR = "cidr"
    RANGE = "range"
    COUNTRY = "country"


class SessionRisk(str, Enum):
    """Session risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class APIKeyStatus(str, Enum):
    """API key status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class SecurityEventType(str, Enum):
    """Security event types"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    IP_BLOCKED = "ip_blocked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    PERMISSION_DENIED = "permission_denied"
    DATA_EXPORT = "data_export"
    ADMIN_ACTION = "admin_action"


class SecurityRiskLevel(str, Enum):
    """Security risk assessment level"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Rate Limiting Models

class RateLimitRule(BaseModel):
    """Rate limit rule configuration"""
    id: str
    name: str
    description: Optional[str] = None
    scope: RateLimitScope
    endpoint_pattern: Optional[str] = None  # Regex for endpoint matching
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10  # Max burst requests
    action: RateLimitAction = RateLimitAction.BLOCK
    retry_after_seconds: int = 60
    enabled: bool = True
    priority: int = 0  # Higher priority rules evaluated first
    exemptions: list[str] = Field(default_factory=list)  # User IDs or API keys exempt
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RateLimitRuleCreate(BaseModel):
    """Create rate limit rule"""
    name: str
    description: Optional[str] = None
    scope: RateLimitScope
    endpoint_pattern: Optional[str] = None
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    action: RateLimitAction = RateLimitAction.BLOCK
    retry_after_seconds: int = 60
    enabled: bool = True
    priority: int = 0
    exemptions: list[str] = Field(default_factory=list)


class RateLimitRuleUpdate(BaseModel):
    """Update rate limit rule"""
    name: Optional[str] = None
    description: Optional[str] = None
    endpoint_pattern: Optional[str] = None
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    burst_limit: Optional[int] = None
    action: Optional[RateLimitAction] = None
    retry_after_seconds: Optional[int] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None
    exemptions: Optional[list[str]] = None


class RateLimitStatus(BaseModel):
    """Current rate limit status"""
    user_id: Optional[str] = None
    ip_address: str
    api_key: Optional[str] = None
    endpoint: str
    requests_this_minute: int
    requests_this_hour: int
    requests_today: int
    limit_reached: bool
    retry_after: Optional[int] = None
    reset_at: datetime


class RateLimitRuleListResponse(BaseModel):
    """List rate limit rules response"""
    rules: list[RateLimitRule]
    total: int


# IP Policy Models

class IPRule(BaseModel):
    """IP allowlist/blocklist rule"""
    id: str
    list_type: IPListType
    match_type: IPMatchType
    value: str  # IP, CIDR, range, or country code
    description: Optional[str] = None
    organization_id: Optional[str] = None  # None = global
    expires_at: Optional[datetime] = None
    enabled: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IPRuleCreate(BaseModel):
    """Create IP rule"""
    list_type: IPListType
    match_type: IPMatchType
    value: str
    description: Optional[str] = None
    organization_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    enabled: bool = True


class IPRuleUpdate(BaseModel):
    """Update IP rule"""
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    enabled: Optional[bool] = None


class IPCheckResult(BaseModel):
    """IP check result"""
    ip_address: str
    allowed: bool
    matched_rule: Optional[IPRule] = None
    country_code: Optional[str] = None
    is_vpn: bool = False
    is_tor: bool = False
    is_proxy: bool = False
    risk_score: int = 0  # 0-100


class IPRuleListResponse(BaseModel):
    """List IP rules response"""
    rules: list[IPRule]
    total: int


# Session Security Models

class SessionConfig(BaseModel):
    """Session security configuration"""
    organization_id: str
    max_concurrent_sessions: int = 5
    session_timeout_minutes: int = 60
    idle_timeout_minutes: int = 30
    require_reauthentication_minutes: int = 1440  # 24 hours
    bind_to_ip: bool = False
    bind_to_device: bool = False
    detect_concurrent_logins: bool = True
    terminate_other_sessions_on_login: bool = False
    require_mfa_for_new_device: bool = True
    high_risk_actions_require_reauth: bool = True
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SessionConfigUpdate(BaseModel):
    """Update session configuration"""
    max_concurrent_sessions: Optional[int] = None
    session_timeout_minutes: Optional[int] = None
    idle_timeout_minutes: Optional[int] = None
    require_reauthentication_minutes: Optional[int] = None
    bind_to_ip: Optional[bool] = None
    bind_to_device: Optional[bool] = None
    detect_concurrent_logins: Optional[bool] = None
    terminate_other_sessions_on_login: Optional[bool] = None
    require_mfa_for_new_device: Optional[bool] = None
    high_risk_actions_require_reauth: Optional[bool] = None


class ActiveSession(BaseModel):
    """Active session info"""
    id: str
    user_id: str
    ip_address: str
    user_agent: str
    device_type: str
    browser: Optional[str] = None
    os: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    is_current: bool = False
    risk_level: SessionRisk = SessionRisk.LOW


class SessionListResponse(BaseModel):
    """List sessions response"""
    sessions: list[ActiveSession]
    total: int


# Password Policy Models

class PasswordPolicy(BaseModel):
    """Password policy configuration"""
    organization_id: str
    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    special_chars_allowed: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    disallow_common_passwords: bool = True
    disallow_personal_info: bool = True
    password_history_count: int = 5  # Can't reuse last N passwords
    max_age_days: int = 90
    min_age_days: int = 1  # Minimum days before changing again
    lockout_threshold: int = 5  # Failed attempts before lockout
    lockout_duration_minutes: int = 30
    require_password_change_on_first_login: bool = True
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PasswordPolicyUpdate(BaseModel):
    """Update password policy"""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    require_uppercase: Optional[bool] = None
    require_lowercase: Optional[bool] = None
    require_numbers: Optional[bool] = None
    require_special_chars: Optional[bool] = None
    special_chars_allowed: Optional[str] = None
    disallow_common_passwords: Optional[bool] = None
    disallow_personal_info: Optional[bool] = None
    password_history_count: Optional[int] = None
    max_age_days: Optional[int] = None
    min_age_days: Optional[int] = None
    lockout_threshold: Optional[int] = None
    lockout_duration_minutes: Optional[int] = None
    require_password_change_on_first_login: Optional[bool] = None


class PasswordValidationResult(BaseModel):
    """Password validation result"""
    valid: bool
    errors: list[str] = Field(default_factory=list)
    strength_score: int = 0  # 0-100
    strength_label: str = "weak"  # weak, fair, good, strong, excellent
    suggestions: list[str] = Field(default_factory=list)


class PasswordStrengthCheck(BaseModel):
    """Password strength check request"""
    password: str
    user_email: Optional[str] = None  # For personal info check
    user_name: Optional[str] = None


# API Key Models

class APIKey(BaseModel):
    """API key"""
    id: str
    name: str
    description: Optional[str] = None
    key_prefix: str  # First 8 chars for identification
    key_hash: str  # Hashed key
    user_id: str
    organization_id: Optional[str] = None
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    permissions: list[str] = Field(default_factory=list)  # Scoped permissions
    rate_limit_override: Optional[int] = None  # Override default rate limit
    allowed_ips: list[str] = Field(default_factory=list)  # Empty = all IPs
    allowed_origins: list[str] = Field(default_factory=list)  # CORS origins
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    last_used_ip: Optional[str] = None
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[str] = None


class APIKeyCreate(BaseModel):
    """Create API key"""
    name: str
    description: Optional[str] = None
    permissions: list[str] = Field(default_factory=list)
    rate_limit_override: Optional[int] = None
    allowed_ips: list[str] = Field(default_factory=list)
    allowed_origins: list[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None


class APIKeyCreateResponse(BaseModel):
    """API key creation response with plain key"""
    api_key: APIKey
    key: str  # Plain key - shown only once
    warning: str = "Store this key securely. It will not be shown again."


class APIKeyUpdate(BaseModel):
    """Update API key"""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[list[str]] = None
    rate_limit_override: Optional[int] = None
    allowed_ips: Optional[list[str]] = None
    allowed_origins: Optional[list[str]] = None
    expires_at: Optional[datetime] = None


class APIKeyListResponse(BaseModel):
    """List API keys response"""
    api_keys: list[APIKey]
    total: int


class APIKeyUsageStats(BaseModel):
    """API key usage statistics"""
    api_key_id: str
    total_requests: int
    requests_today: int
    requests_this_week: int
    requests_this_month: int
    unique_ips: int
    last_used_at: Optional[datetime] = None
    requests_by_endpoint: dict[str, int] = Field(default_factory=dict)
    requests_by_day: list[dict[str, Any]] = Field(default_factory=list)


# Security Event Models

class SecurityEvent(BaseModel):
    """Security event for audit logging"""
    id: str
    event_type: SecurityEventType
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    ip_address: str
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    success: bool
    risk_level: SecurityRiskLevel = SecurityRiskLevel.NONE
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SecurityEventListResponse(BaseModel):
    """List security events response"""
    events: list[SecurityEvent]
    total: int


# Security Configuration Models

class CORSConfig(BaseModel):
    """CORS configuration"""
    organization_id: str
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])
    allowed_methods: list[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    allowed_headers: list[str] = Field(default_factory=lambda: ["*"])
    exposed_headers: list[str] = Field(default_factory=list)
    allow_credentials: bool = False
    max_age_seconds: int = 86400
    enabled: bool = True
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CORSConfigUpdate(BaseModel):
    """Update CORS configuration"""
    allowed_origins: Optional[list[str]] = None
    allowed_methods: Optional[list[str]] = None
    allowed_headers: Optional[list[str]] = None
    exposed_headers: Optional[list[str]] = None
    allow_credentials: Optional[bool] = None
    max_age_seconds: Optional[int] = None
    enabled: Optional[bool] = None


class CSPConfig(BaseModel):
    """Content Security Policy configuration"""
    organization_id: str
    default_src: list[str] = Field(default_factory=lambda: ["'self'"])
    script_src: list[str] = Field(default_factory=lambda: ["'self'"])
    style_src: list[str] = Field(default_factory=lambda: ["'self'", "'unsafe-inline'"])
    img_src: list[str] = Field(default_factory=lambda: ["'self'", "data:", "https:"])
    font_src: list[str] = Field(default_factory=lambda: ["'self'"])
    connect_src: list[str] = Field(default_factory=lambda: ["'self'"])
    frame_src: list[str] = Field(default_factory=lambda: ["'none'"])
    object_src: list[str] = Field(default_factory=lambda: ["'none'"])
    base_uri: list[str] = Field(default_factory=lambda: ["'self'"])
    form_action: list[str] = Field(default_factory=lambda: ["'self'"])
    report_uri: Optional[str] = None
    report_only: bool = False
    enabled: bool = True
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CSPConfigUpdate(BaseModel):
    """Update CSP configuration"""
    default_src: Optional[list[str]] = None
    script_src: Optional[list[str]] = None
    style_src: Optional[list[str]] = None
    img_src: Optional[list[str]] = None
    font_src: Optional[list[str]] = None
    connect_src: Optional[list[str]] = None
    frame_src: Optional[list[str]] = None
    object_src: Optional[list[str]] = None
    base_uri: Optional[list[str]] = None
    form_action: Optional[list[str]] = None
    report_uri: Optional[str] = None
    report_only: Optional[bool] = None
    enabled: Optional[bool] = None


class SecurityHeaders(BaseModel):
    """Security headers configuration"""
    organization_id: str
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains"
    referrer_policy: str = "strict-origin-when-cross-origin"
    permissions_policy: Optional[str] = None
    custom_headers: dict[str, str] = Field(default_factory=dict)
    enabled: bool = True
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SecurityHeadersUpdate(BaseModel):
    """Update security headers"""
    x_frame_options: Optional[str] = None
    x_content_type_options: Optional[str] = None
    x_xss_protection: Optional[str] = None
    strict_transport_security: Optional[str] = None
    referrer_policy: Optional[str] = None
    permissions_policy: Optional[str] = None
    custom_headers: Optional[dict[str, str]] = None
    enabled: Optional[bool] = None


# Security Overview

class SecurityOverview(BaseModel):
    """Security overview for dashboard"""
    organization_id: str
    security_score: int  # 0-100
    mfa_adoption_percent: float
    api_keys_active: int
    blocked_ips_count: int
    rate_limit_violations_today: int
    failed_logins_today: int
    suspicious_activities_today: int
    password_policy_compliant_percent: float
    sessions_active: int
    last_security_incident: Optional[datetime] = None
    recommendations: list[str] = Field(default_factory=list)


class SecurityRecommendation(BaseModel):
    """Security recommendation"""
    id: str
    title: str
    description: str
    severity: SecurityRiskLevel
    category: str
    action_url: Optional[str] = None
    dismissed: bool = False


# Constants

COMMON_PASSWORDS_FILE = "common_passwords.txt"
DEFAULT_RATE_LIMIT_MINUTE = 60
DEFAULT_RATE_LIMIT_HOUR = 1000
DEFAULT_RATE_LIMIT_DAY = 10000
DEFAULT_SESSION_TIMEOUT = 60  # minutes
DEFAULT_IDLE_TIMEOUT = 30  # minutes
DEFAULT_PASSWORD_MIN_LENGTH = 8
DEFAULT_LOCKOUT_THRESHOLD = 5
DEFAULT_LOCKOUT_DURATION = 30  # minutes


# Helper Functions

def calculate_password_strength(password: str) -> tuple[int, str]:
    """Calculate password strength score and label."""
    score = 0

    # Length scoring
    if len(password) >= 8:
        score += 20
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10

    # Character diversity
    if any(c.isupper() for c in password):
        score += 15
    if any(c.islower() for c in password):
        score += 15
    if any(c.isdigit() for c in password):
        score += 15
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 15

    # Determine label
    if score >= 80:
        label = "excellent"
    elif score >= 60:
        label = "strong"
    elif score >= 40:
        label = "good"
    elif score >= 20:
        label = "fair"
    else:
        label = "weak"

    return min(score, 100), label


def format_rate_limit_key(scope: RateLimitScope, identifier: str, endpoint: Optional[str] = None) -> str:
    """Format rate limit cache key."""
    if endpoint:
        return f"ratelimit:{scope.value}:{identifier}:{endpoint}"
    return f"ratelimit:{scope.value}:{identifier}"


def is_ip_in_cidr(ip: str, cidr: str) -> bool:
    """Check if IP is in CIDR range."""
    import ipaddress
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        return False


def generate_api_key() -> tuple[str, str]:
    """Generate API key and return (key, hash)."""
    import secrets
    import hashlib

    key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash


def get_api_key_prefix(key: str) -> str:
    """Get prefix of API key for identification."""
    return key[:8] if len(key) >= 8 else key
