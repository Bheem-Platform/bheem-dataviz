"""
Two-Factor Authentication Schemas

Pydantic schemas for TOTP, SMS, email verification, backup codes,
trusted devices, and recovery options.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import datetime


# Enums

class MFAMethod(str, Enum):
    """MFA method types"""
    TOTP = "totp"  # Authenticator apps
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_KEY = "hardware_key"  # FIDO2/WebAuthn
    PUSH = "push"  # Push notifications


class MFAStatus(str, Enum):
    """MFA setup status"""
    NOT_CONFIGURED = "not_configured"
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    DISABLED = "disabled"


class VerificationStatus(str, Enum):
    """Verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    FAILED = "failed"


class TrustLevel(str, Enum):
    """Device trust level"""
    UNTRUSTED = "untrusted"
    TRUSTED = "trusted"
    REMEMBERED = "remembered"


# TOTP Models

class TOTPSetupRequest(BaseModel):
    """Request TOTP setup"""
    method: MFAMethod = MFAMethod.TOTP


class TOTPSetupResponse(BaseModel):
    """TOTP setup response with QR code"""
    secret: str
    qr_code_url: str  # data:image/png;base64,...
    qr_code_uri: str  # otpauth:// URI
    backup_codes: list[str]
    expires_at: datetime
    setup_token: str  # Token to complete setup


class TOTPVerifyRequest(BaseModel):
    """Verify TOTP code to complete setup"""
    setup_token: str
    code: str


class TOTPConfig(BaseModel):
    """User's TOTP configuration"""
    user_id: str
    status: MFAStatus
    secret_encrypted: Optional[str] = None
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30
    issuer: str = "Bheem DataViz"
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None


# SMS MFA Models

class SMSSetupRequest(BaseModel):
    """Request SMS MFA setup"""
    phone_number: str


class SMSSetupResponse(BaseModel):
    """SMS setup response"""
    phone_number_masked: str  # +1***456
    verification_sent: bool
    expires_at: datetime
    setup_token: str


class SMSVerifyRequest(BaseModel):
    """Verify SMS code"""
    setup_token: str
    code: str


class SMSConfig(BaseModel):
    """User's SMS MFA configuration"""
    user_id: str
    status: MFAStatus
    phone_number_encrypted: Optional[str] = None
    phone_number_masked: Optional[str] = None
    country_code: Optional[str] = None
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None


# Email MFA Models

class EmailMFASetupRequest(BaseModel):
    """Request email MFA setup"""
    email: Optional[EmailStr] = None  # Uses account email if not specified


class EmailMFASetupResponse(BaseModel):
    """Email MFA setup response"""
    email_masked: str  # j***@example.com
    verification_sent: bool
    expires_at: datetime
    setup_token: str


class EmailMFAVerifyRequest(BaseModel):
    """Verify email MFA code"""
    setup_token: str
    code: str


class EmailMFAConfig(BaseModel):
    """User's email MFA configuration"""
    user_id: str
    status: MFAStatus
    email: Optional[str] = None
    email_masked: Optional[str] = None
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None


# Hardware Key (FIDO2/WebAuthn) Models

class WebAuthnRegistrationOptions(BaseModel):
    """WebAuthn registration options"""
    challenge: str
    rp_id: str
    rp_name: str
    user_id: str
    user_name: str
    user_display_name: str
    attestation: str = "none"
    authenticator_selection: dict[str, Any] = Field(default_factory=dict)
    timeout: int = 60000
    exclude_credentials: list[dict[str, Any]] = Field(default_factory=list)


class WebAuthnRegistrationResponse(BaseModel):
    """WebAuthn registration response from client"""
    credential_id: str
    client_data_json: str
    attestation_object: str
    transports: list[str] = Field(default_factory=list)


class WebAuthnCredential(BaseModel):
    """Stored WebAuthn credential"""
    id: str
    user_id: str
    credential_id: str
    public_key: str
    sign_count: int
    transports: list[str]
    name: str  # User-provided name for the key
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None


class WebAuthnAuthenticationOptions(BaseModel):
    """WebAuthn authentication options"""
    challenge: str
    timeout: int = 60000
    rp_id: str
    allow_credentials: list[dict[str, Any]]
    user_verification: str = "preferred"


class WebAuthnAuthenticationResponse(BaseModel):
    """WebAuthn authentication response from client"""
    credential_id: str
    client_data_json: str
    authenticator_data: str
    signature: str
    user_handle: Optional[str] = None


# Backup Codes Models

class BackupCodesConfig(BaseModel):
    """Backup codes configuration"""
    user_id: str
    codes_total: int = 10
    codes_remaining: int = 10
    codes_hashed: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None


class BackupCodesResponse(BaseModel):
    """New backup codes response"""
    codes: list[str]  # Plain text codes (shown once)
    codes_total: int
    generated_at: datetime
    warning: str = "Store these codes securely. They will not be shown again."


class BackupCodeVerifyRequest(BaseModel):
    """Verify backup code"""
    code: str


# Trusted Device Models

class TrustedDevice(BaseModel):
    """Trusted device"""
    id: str
    user_id: str
    device_id: str  # Fingerprint or generated ID
    name: str
    device_type: str  # desktop, mobile, tablet
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    trust_level: TrustLevel
    trusted_until: Optional[datetime] = None  # None = indefinite
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None


class TrustDeviceRequest(BaseModel):
    """Trust device request"""
    device_id: str
    name: Optional[str] = None
    trust_duration_days: Optional[int] = 30  # None = indefinite


class TrustedDeviceListResponse(BaseModel):
    """List trusted devices response"""
    devices: list[TrustedDevice]
    total: int


# MFA Challenge Models

class MFAChallenge(BaseModel):
    """MFA challenge for login"""
    challenge_id: str
    user_id: str
    available_methods: list[MFAMethod]
    preferred_method: MFAMethod
    challenge_token: str  # Temporary token for this challenge
    expires_at: datetime
    attempts_remaining: int = 3
    device_info: dict[str, Any] = Field(default_factory=dict)


class MFAChallengeResponse(BaseModel):
    """Response to MFA challenge"""
    challenge_id: str
    method: MFAMethod
    code: Optional[str] = None  # For TOTP, SMS, Email
    webauthn_response: Optional[WebAuthnAuthenticationResponse] = None
    trust_device: bool = False
    trust_duration_days: Optional[int] = 30


class MFAVerificationResult(BaseModel):
    """MFA verification result"""
    success: bool
    method: MFAMethod
    device_trusted: bool = False
    error_message: Optional[str] = None
    attempts_remaining: Optional[int] = None


# Recovery Models

class RecoveryMethod(str, Enum):
    """Recovery methods"""
    BACKUP_CODE = "backup_code"
    EMAIL = "email"
    ADMIN_RESET = "admin_reset"
    SECURITY_QUESTIONS = "security_questions"


class RecoveryRequest(BaseModel):
    """Account recovery request"""
    user_id: str
    method: RecoveryMethod
    email: Optional[str] = None
    backup_code: Optional[str] = None
    security_answers: Optional[dict[str, str]] = None


class RecoveryToken(BaseModel):
    """Recovery token"""
    id: str
    user_id: str
    token_hash: str
    method: RecoveryMethod
    expires_at: datetime
    used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RecoveryResponse(BaseModel):
    """Recovery response"""
    success: bool
    message: str
    recovery_token: Optional[str] = None  # For completing recovery
    next_step: Optional[str] = None


# User MFA Configuration

class UserMFAConfig(BaseModel):
    """Complete MFA configuration for user"""
    user_id: str
    mfa_enabled: bool
    mfa_enforced: bool  # Required by organization
    primary_method: Optional[MFAMethod] = None
    totp: Optional[TOTPConfig] = None
    sms: Optional[SMSConfig] = None
    email: Optional[EmailMFAConfig] = None
    hardware_keys: list[WebAuthnCredential] = Field(default_factory=list)
    backup_codes: Optional[BackupCodesConfig] = None
    trusted_devices: list[TrustedDevice] = Field(default_factory=list)
    recovery_email: Optional[str] = None
    last_mfa_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserMFAConfigUpdate(BaseModel):
    """Update MFA configuration"""
    primary_method: Optional[MFAMethod] = None
    recovery_email: Optional[EmailStr] = None


# Organization MFA Policy

class MFAPolicy(BaseModel):
    """Organization MFA policy"""
    organization_id: str
    mfa_required: bool = False
    allowed_methods: list[MFAMethod] = Field(
        default_factory=lambda: [MFAMethod.TOTP, MFAMethod.EMAIL]
    )
    require_backup_codes: bool = True
    max_trusted_devices: int = 5
    trust_device_max_days: int = 30
    grace_period_days: int = 7  # Days to enable MFA after requirement
    enforce_for_admins: bool = True
    enforce_for_api_access: bool = False
    remember_device_option: bool = True
    bypass_for_internal_ips: bool = False
    internal_ip_ranges: list[str] = Field(default_factory=list)


class MFAPolicyUpdate(BaseModel):
    """Update MFA policy"""
    mfa_required: Optional[bool] = None
    allowed_methods: Optional[list[MFAMethod]] = None
    require_backup_codes: Optional[bool] = None
    max_trusted_devices: Optional[int] = None
    trust_device_max_days: Optional[int] = None
    grace_period_days: Optional[int] = None
    enforce_for_admins: Optional[bool] = None
    enforce_for_api_access: Optional[bool] = None
    remember_device_option: Optional[bool] = None
    bypass_for_internal_ips: Optional[bool] = None
    internal_ip_ranges: Optional[list[str]] = None


# MFA Event Logging

class MFAEvent(BaseModel):
    """MFA event for audit"""
    id: str
    user_id: str
    event_type: str  # setup, verify, disable, recovery, etc.
    method: Optional[MFAMethod] = None
    success: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MFAEventListResponse(BaseModel):
    """List MFA events response"""
    events: list[MFAEvent]
    total: int


# Response Models

class MFAStatusResponse(BaseModel):
    """MFA status response"""
    mfa_enabled: bool
    mfa_enforced: bool
    methods_configured: list[MFAMethod]
    primary_method: Optional[MFAMethod] = None
    backup_codes_remaining: int = 0
    trusted_devices_count: int = 0
    grace_period_ends_at: Optional[datetime] = None


# Constants

MFA_CODE_LENGTH = 6
MFA_CODE_EXPIRY_MINUTES = 10
BACKUP_CODE_LENGTH = 8
BACKUP_CODE_COUNT = 10
TOTP_SETUP_EXPIRY_MINUTES = 15
TRUSTED_DEVICE_DEFAULT_DAYS = 30
MAX_MFA_ATTEMPTS = 3

MFA_METHOD_LABELS = {
    MFAMethod.TOTP: "Authenticator App",
    MFAMethod.SMS: "SMS",
    MFAMethod.EMAIL: "Email",
    MFAMethod.HARDWARE_KEY: "Security Key",
    MFAMethod.PUSH: "Push Notification",
}


# Helper Functions

def mask_email(email: str) -> str:
    """Mask email for display."""
    if "@" not in email:
        return "***"
    local, domain = email.split("@")
    if len(local) <= 2:
        return f"{local[0]}***@{domain}"
    return f"{local[0]}***{local[-1]}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone number for display."""
    if len(phone) < 4:
        return "***"
    return f"{phone[:3]}***{phone[-3:]}"


def generate_backup_code() -> str:
    """Generate a backup code."""
    import secrets
    return secrets.token_hex(BACKUP_CODE_LENGTH // 2).upper()


def generate_numeric_code(length: int = MFA_CODE_LENGTH) -> str:
    """Generate numeric verification code."""
    import secrets
    return "".join(str(secrets.randbelow(10)) for _ in range(length))
