"""
Two-Factor Authentication Service

Provides TOTP, SMS, email verification, backup codes,
trusted devices, and recovery management.
"""

import secrets
import hashlib
import base64
import io
import pyotp
import qrcode
from datetime import datetime, timedelta
from typing import Optional

from app.schemas.two_factor_auth import (
    MFAMethod, MFAStatus, VerificationStatus, TrustLevel,
    TOTPSetupResponse, TOTPConfig,
    SMSSetupResponse, SMSConfig,
    EmailMFASetupResponse, EmailMFAConfig,
    WebAuthnCredential, WebAuthnRegistrationOptions, WebAuthnAuthenticationOptions,
    BackupCodesConfig, BackupCodesResponse,
    TrustedDevice, TrustedDeviceListResponse,
    MFAChallenge, MFAChallengeResponse, MFAVerificationResult,
    RecoveryMethod, RecoveryToken, RecoveryResponse,
    UserMFAConfig, UserMFAConfigUpdate,
    MFAPolicy, MFAPolicyUpdate,
    MFAEvent, MFAEventListResponse, MFAStatusResponse,
    MFA_CODE_LENGTH, MFA_CODE_EXPIRY_MINUTES, BACKUP_CODE_COUNT,
    TOTP_SETUP_EXPIRY_MINUTES, TRUSTED_DEVICE_DEFAULT_DAYS, MAX_MFA_ATTEMPTS,
    mask_email, mask_phone, generate_backup_code, generate_numeric_code,
)


class TwoFactorAuthService:
    """Service for two-factor authentication."""

    def __init__(self):
        # In-memory stores (production would use database + encrypted storage)
        self.user_mfa_configs: dict[str, UserMFAConfig] = {}
        self.totp_secrets: dict[str, str] = {}  # user_id -> secret (encrypted in prod)
        self.pending_setups: dict[str, dict] = {}  # setup_token -> setup data
        self.mfa_challenges: dict[str, MFAChallenge] = {}
        self.verification_codes: dict[str, dict] = {}  # token -> {code, user_id, expires}
        self.recovery_tokens: dict[str, RecoveryToken] = {}
        self.mfa_policies: dict[str, MFAPolicy] = {}
        self.mfa_events: list[MFAEvent] = []

        self.issuer = "Bheem DataViz"

    def _generate_id(self, prefix: str = "id") -> str:
        """Generate a unique ID."""
        return f"{prefix}_{secrets.token_hex(12)}"

    def _hash_code(self, code: str) -> str:
        """Hash a code for storage."""
        return hashlib.sha256(code.encode()).hexdigest()

    def _log_event(
        self,
        user_id: str,
        event_type: str,
        method: Optional[MFAMethod] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_id: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        """Log MFA event."""
        event = MFAEvent(
            id=self._generate_id("evt"),
            user_id=user_id,
            event_type=event_type,
            method=method,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            details=details or {},
        )
        self.mfa_events.append(event)

    def _get_or_create_config(self, user_id: str) -> UserMFAConfig:
        """Get or create user MFA config."""
        if user_id not in self.user_mfa_configs:
            self.user_mfa_configs[user_id] = UserMFAConfig(
                user_id=user_id,
                mfa_enabled=False,
                mfa_enforced=False,
            )
        return self.user_mfa_configs[user_id]

    # TOTP Methods

    def setup_totp(self, user_id: str, user_email: str) -> TOTPSetupResponse:
        """Initialize TOTP setup."""
        # Generate secret
        secret = pyotp.random_base32()

        # Create TOTP instance
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(user_email, issuer_name=self.issuer)

        # Generate QR code
        qr = qrcode.make(provisioning_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Generate backup codes
        backup_codes = [generate_backup_code() for _ in range(BACKUP_CODE_COUNT)]

        # Create setup token
        setup_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=TOTP_SETUP_EXPIRY_MINUTES)

        # Store pending setup
        self.pending_setups[setup_token] = {
            "user_id": user_id,
            "method": MFAMethod.TOTP,
            "secret": secret,
            "backup_codes": backup_codes,
            "expires_at": expires_at,
        }

        self._log_event(user_id, "totp_setup_started", MFAMethod.TOTP)

        return TOTPSetupResponse(
            secret=secret,
            qr_code_url=f"data:image/png;base64,{qr_base64}",
            qr_code_uri=provisioning_uri,
            backup_codes=backup_codes,
            expires_at=expires_at,
            setup_token=setup_token,
        )

    def verify_totp_setup(self, setup_token: str, code: str, ip_address: Optional[str] = None) -> bool:
        """Verify TOTP code to complete setup."""
        setup_data = self.pending_setups.get(setup_token)
        if not setup_data:
            return False

        if datetime.utcnow() > setup_data["expires_at"]:
            del self.pending_setups[setup_token]
            return False

        user_id = setup_data["user_id"]
        secret = setup_data["secret"]

        # Verify code
        totp = pyotp.TOTP(secret)
        if not totp.verify(code, valid_window=1):
            self._log_event(user_id, "totp_setup_failed", MFAMethod.TOTP, False, ip_address)
            return False

        # Store configuration
        config = self._get_or_create_config(user_id)
        config.totp = TOTPConfig(
            user_id=user_id,
            status=MFAStatus.ACTIVE,
            secret_encrypted=secret,  # Would encrypt in production
            created_at=datetime.utcnow(),
            verified_at=datetime.utcnow(),
        )

        # Store backup codes
        backup_codes = setup_data["backup_codes"]
        config.backup_codes = BackupCodesConfig(
            user_id=user_id,
            codes_total=len(backup_codes),
            codes_remaining=len(backup_codes),
            codes_hashed=[self._hash_code(c) for c in backup_codes],
        )

        self.totp_secrets[user_id] = secret
        config.mfa_enabled = True
        if not config.primary_method:
            config.primary_method = MFAMethod.TOTP
        config.updated_at = datetime.utcnow()

        del self.pending_setups[setup_token]

        self._log_event(user_id, "totp_setup_completed", MFAMethod.TOTP, True, ip_address)
        return True

    def verify_totp(self, user_id: str, code: str) -> bool:
        """Verify TOTP code for authentication."""
        secret = self.totp_secrets.get(user_id)
        if not secret:
            return False

        totp = pyotp.TOTP(secret)
        valid = totp.verify(code, valid_window=1)

        if valid:
            config = self._get_or_create_config(user_id)
            if config.totp:
                config.totp.last_used_at = datetime.utcnow()
            config.last_mfa_at = datetime.utcnow()

        return valid

    def disable_totp(self, user_id: str, code: str) -> bool:
        """Disable TOTP after verification."""
        if not self.verify_totp(user_id, code):
            self._log_event(user_id, "totp_disable_failed", MFAMethod.TOTP, False)
            return False

        config = self._get_or_create_config(user_id)
        config.totp = None
        if user_id in self.totp_secrets:
            del self.totp_secrets[user_id]

        # Update primary method if needed
        if config.primary_method == MFAMethod.TOTP:
            config.primary_method = self._get_fallback_method(config)

        # Disable MFA if no methods remain
        if not self._has_any_method(config):
            config.mfa_enabled = False

        config.updated_at = datetime.utcnow()

        self._log_event(user_id, "totp_disabled", MFAMethod.TOTP)
        return True

    # SMS Methods

    def setup_sms(self, user_id: str, phone_number: str) -> SMSSetupResponse:
        """Initialize SMS MFA setup."""
        # Generate verification code
        code = generate_numeric_code()
        setup_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=MFA_CODE_EXPIRY_MINUTES)

        # Store pending setup
        self.pending_setups[setup_token] = {
            "user_id": user_id,
            "method": MFAMethod.SMS,
            "phone_number": phone_number,
            "code": code,
            "expires_at": expires_at,
        }

        # In production, send SMS here
        print(f"SMS verification code for {phone_number}: {code}")

        self._log_event(user_id, "sms_setup_started", MFAMethod.SMS)

        return SMSSetupResponse(
            phone_number_masked=mask_phone(phone_number),
            verification_sent=True,
            expires_at=expires_at,
            setup_token=setup_token,
        )

    def verify_sms_setup(self, setup_token: str, code: str, ip_address: Optional[str] = None) -> bool:
        """Verify SMS code to complete setup."""
        setup_data = self.pending_setups.get(setup_token)
        if not setup_data or setup_data["method"] != MFAMethod.SMS:
            return False

        if datetime.utcnow() > setup_data["expires_at"]:
            del self.pending_setups[setup_token]
            return False

        if setup_data["code"] != code:
            self._log_event(setup_data["user_id"], "sms_setup_failed", MFAMethod.SMS, False, ip_address)
            return False

        user_id = setup_data["user_id"]
        phone_number = setup_data["phone_number"]

        config = self._get_or_create_config(user_id)
        config.sms = SMSConfig(
            user_id=user_id,
            status=MFAStatus.ACTIVE,
            phone_number_encrypted=phone_number,  # Would encrypt in production
            phone_number_masked=mask_phone(phone_number),
            created_at=datetime.utcnow(),
            verified_at=datetime.utcnow(),
        )

        config.mfa_enabled = True
        if not config.primary_method:
            config.primary_method = MFAMethod.SMS
        config.updated_at = datetime.utcnow()

        del self.pending_setups[setup_token]

        self._log_event(user_id, "sms_setup_completed", MFAMethod.SMS, True, ip_address)
        return True

    def send_sms_code(self, user_id: str) -> Optional[str]:
        """Send SMS verification code."""
        config = self._get_or_create_config(user_id)
        if not config.sms or config.sms.status != MFAStatus.ACTIVE:
            return None

        code = generate_numeric_code()
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=MFA_CODE_EXPIRY_MINUTES)

        self.verification_codes[token] = {
            "user_id": user_id,
            "method": MFAMethod.SMS,
            "code": code,
            "expires_at": expires_at,
        }

        # In production, send SMS
        print(f"SMS code: {code}")

        return token

    def verify_sms(self, user_id: str, token: str, code: str) -> bool:
        """Verify SMS code."""
        verification = self.verification_codes.get(token)
        if not verification:
            return False

        if verification["user_id"] != user_id:
            return False

        if datetime.utcnow() > verification["expires_at"]:
            del self.verification_codes[token]
            return False

        if verification["code"] != code:
            return False

        del self.verification_codes[token]

        config = self._get_or_create_config(user_id)
        if config.sms:
            config.sms.last_used_at = datetime.utcnow()
        config.last_mfa_at = datetime.utcnow()

        return True

    # Email MFA Methods

    def setup_email_mfa(self, user_id: str, email: str) -> EmailMFASetupResponse:
        """Initialize email MFA setup."""
        code = generate_numeric_code()
        setup_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=MFA_CODE_EXPIRY_MINUTES)

        self.pending_setups[setup_token] = {
            "user_id": user_id,
            "method": MFAMethod.EMAIL,
            "email": email,
            "code": code,
            "expires_at": expires_at,
        }

        # In production, send email
        print(f"Email verification code for {email}: {code}")

        self._log_event(user_id, "email_mfa_setup_started", MFAMethod.EMAIL)

        return EmailMFASetupResponse(
            email_masked=mask_email(email),
            verification_sent=True,
            expires_at=expires_at,
            setup_token=setup_token,
        )

    def verify_email_mfa_setup(self, setup_token: str, code: str, ip_address: Optional[str] = None) -> bool:
        """Verify email code to complete setup."""
        setup_data = self.pending_setups.get(setup_token)
        if not setup_data or setup_data["method"] != MFAMethod.EMAIL:
            return False

        if datetime.utcnow() > setup_data["expires_at"]:
            del self.pending_setups[setup_token]
            return False

        if setup_data["code"] != code:
            self._log_event(setup_data["user_id"], "email_mfa_setup_failed", MFAMethod.EMAIL, False, ip_address)
            return False

        user_id = setup_data["user_id"]
        email = setup_data["email"]

        config = self._get_or_create_config(user_id)
        config.email = EmailMFAConfig(
            user_id=user_id,
            status=MFAStatus.ACTIVE,
            email=email,
            email_masked=mask_email(email),
            created_at=datetime.utcnow(),
            verified_at=datetime.utcnow(),
        )

        config.mfa_enabled = True
        if not config.primary_method:
            config.primary_method = MFAMethod.EMAIL
        config.updated_at = datetime.utcnow()

        del self.pending_setups[setup_token]

        self._log_event(user_id, "email_mfa_setup_completed", MFAMethod.EMAIL, True, ip_address)
        return True

    def send_email_code(self, user_id: str) -> Optional[str]:
        """Send email verification code."""
        config = self._get_or_create_config(user_id)
        if not config.email or config.email.status != MFAStatus.ACTIVE:
            return None

        code = generate_numeric_code()
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=MFA_CODE_EXPIRY_MINUTES)

        self.verification_codes[token] = {
            "user_id": user_id,
            "method": MFAMethod.EMAIL,
            "code": code,
            "expires_at": expires_at,
        }

        # In production, send email
        print(f"Email code: {code}")

        return token

    def verify_email_mfa(self, user_id: str, token: str, code: str) -> bool:
        """Verify email MFA code."""
        verification = self.verification_codes.get(token)
        if not verification or verification["user_id"] != user_id:
            return False

        if datetime.utcnow() > verification["expires_at"]:
            del self.verification_codes[token]
            return False

        if verification["code"] != code:
            return False

        del self.verification_codes[token]

        config = self._get_or_create_config(user_id)
        if config.email:
            config.email.last_used_at = datetime.utcnow()
        config.last_mfa_at = datetime.utcnow()

        return True

    # Backup Codes

    def regenerate_backup_codes(self, user_id: str) -> Optional[BackupCodesResponse]:
        """Regenerate backup codes."""
        config = self._get_or_create_config(user_id)
        if not config.mfa_enabled:
            return None

        codes = [generate_backup_code() for _ in range(BACKUP_CODE_COUNT)]

        config.backup_codes = BackupCodesConfig(
            user_id=user_id,
            codes_total=len(codes),
            codes_remaining=len(codes),
            codes_hashed=[self._hash_code(c) for c in codes],
        )
        config.updated_at = datetime.utcnow()

        self._log_event(user_id, "backup_codes_regenerated")

        return BackupCodesResponse(
            codes=codes,
            codes_total=len(codes),
            generated_at=datetime.utcnow(),
        )

    def verify_backup_code(self, user_id: str, code: str) -> bool:
        """Verify and consume backup code."""
        config = self._get_or_create_config(user_id)
        if not config.backup_codes or config.backup_codes.codes_remaining <= 0:
            return False

        code_hash = self._hash_code(code.upper().replace("-", "").replace(" ", ""))

        if code_hash in config.backup_codes.codes_hashed:
            config.backup_codes.codes_hashed.remove(code_hash)
            config.backup_codes.codes_remaining -= 1
            config.backup_codes.last_used_at = datetime.utcnow()
            config.last_mfa_at = datetime.utcnow()

            self._log_event(user_id, "backup_code_used")
            return True

        return False

    # Trusted Devices

    def trust_device(
        self,
        user_id: str,
        device_id: str,
        name: Optional[str] = None,
        device_type: str = "desktop",
        browser: Optional[str] = None,
        os: Optional[str] = None,
        ip_address: Optional[str] = None,
        trust_days: int = TRUSTED_DEVICE_DEFAULT_DAYS,
    ) -> TrustedDevice:
        """Add trusted device."""
        config = self._get_or_create_config(user_id)

        # Remove existing device with same ID
        config.trusted_devices = [d for d in config.trusted_devices if d.device_id != device_id]

        device = TrustedDevice(
            id=self._generate_id("dev"),
            user_id=user_id,
            device_id=device_id,
            name=name or f"{browser or 'Unknown'} on {os or 'Unknown'}",
            device_type=device_type,
            browser=browser,
            os=os,
            ip_address=ip_address,
            trust_level=TrustLevel.TRUSTED,
            trusted_until=datetime.utcnow() + timedelta(days=trust_days) if trust_days > 0 else None,
        )

        config.trusted_devices.append(device)
        config.updated_at = datetime.utcnow()

        self._log_event(user_id, "device_trusted", device_id=device_id)

        return device

    def is_device_trusted(self, user_id: str, device_id: str) -> bool:
        """Check if device is trusted."""
        config = self._get_or_create_config(user_id)

        for device in config.trusted_devices:
            if device.device_id == device_id:
                if device.trusted_until and device.trusted_until < datetime.utcnow():
                    return False
                device.last_used_at = datetime.utcnow()
                return True

        return False

    def revoke_device_trust(self, user_id: str, device_id: str) -> bool:
        """Revoke trust from device."""
        config = self._get_or_create_config(user_id)

        original_count = len(config.trusted_devices)
        config.trusted_devices = [d for d in config.trusted_devices if d.device_id != device_id]

        if len(config.trusted_devices) < original_count:
            config.updated_at = datetime.utcnow()
            self._log_event(user_id, "device_trust_revoked", device_id=device_id)
            return True

        return False

    def list_trusted_devices(self, user_id: str) -> TrustedDeviceListResponse:
        """List trusted devices."""
        config = self._get_or_create_config(user_id)

        # Filter out expired devices
        now = datetime.utcnow()
        active_devices = [
            d for d in config.trusted_devices
            if not d.trusted_until or d.trusted_until > now
        ]

        return TrustedDeviceListResponse(devices=active_devices, total=len(active_devices))

    # MFA Challenge Flow

    def create_mfa_challenge(
        self,
        user_id: str,
        device_info: Optional[dict] = None,
    ) -> Optional[MFAChallenge]:
        """Create MFA challenge for authentication."""
        config = self._get_or_create_config(user_id)
        if not config.mfa_enabled:
            return None

        available_methods = self._get_available_methods(config)
        if not available_methods:
            return None

        challenge_id = self._generate_id("chal")
        challenge_token = secrets.token_urlsafe(32)

        challenge = MFAChallenge(
            challenge_id=challenge_id,
            user_id=user_id,
            available_methods=available_methods,
            preferred_method=config.primary_method or available_methods[0],
            challenge_token=challenge_token,
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            device_info=device_info or {},
        )

        self.mfa_challenges[challenge_id] = challenge

        return challenge

    def verify_mfa_challenge(
        self,
        challenge_id: str,
        response: MFAChallengeResponse,
        ip_address: Optional[str] = None,
    ) -> MFAVerificationResult:
        """Verify MFA challenge response."""
        challenge = self.mfa_challenges.get(challenge_id)
        if not challenge:
            return MFAVerificationResult(
                success=False,
                method=response.method,
                error_message="Challenge not found or expired",
            )

        if datetime.utcnow() > challenge.expires_at:
            del self.mfa_challenges[challenge_id]
            return MFAVerificationResult(
                success=False,
                method=response.method,
                error_message="Challenge expired",
            )

        if challenge.attempts_remaining <= 0:
            del self.mfa_challenges[challenge_id]
            return MFAVerificationResult(
                success=False,
                method=response.method,
                error_message="Too many attempts",
            )

        user_id = challenge.user_id
        verified = False

        if response.method == MFAMethod.TOTP and response.code:
            verified = self.verify_totp(user_id, response.code)
        elif response.method == MFAMethod.SMS and response.code:
            # Would need verification token for SMS
            pass
        elif response.method == MFAMethod.EMAIL and response.code:
            # Would need verification token for email
            pass

        # Try backup code as fallback
        if not verified and response.code:
            verified = self.verify_backup_code(user_id, response.code)

        if verified:
            del self.mfa_challenges[challenge_id]

            # Trust device if requested
            device_trusted = False
            if response.trust_device and challenge.device_info.get("device_id"):
                self.trust_device(
                    user_id,
                    challenge.device_info["device_id"],
                    device_type=challenge.device_info.get("device_type", "desktop"),
                    browser=challenge.device_info.get("browser"),
                    os=challenge.device_info.get("os"),
                    ip_address=ip_address,
                    trust_days=response.trust_duration_days or TRUSTED_DEVICE_DEFAULT_DAYS,
                )
                device_trusted = True

            self._log_event(user_id, "mfa_verified", response.method, True, ip_address)

            return MFAVerificationResult(
                success=True,
                method=response.method,
                device_trusted=device_trusted,
            )

        challenge.attempts_remaining -= 1
        self._log_event(user_id, "mfa_failed", response.method, False, ip_address)

        return MFAVerificationResult(
            success=False,
            method=response.method,
            error_message="Invalid code",
            attempts_remaining=challenge.attempts_remaining,
        )

    # Recovery

    def initiate_recovery(
        self,
        user_id: str,
        method: RecoveryMethod,
        email: Optional[str] = None,
    ) -> RecoveryResponse:
        """Initiate account recovery."""
        if method == RecoveryMethod.EMAIL:
            # Send recovery email
            token = secrets.token_urlsafe(32)
            self.recovery_tokens[token] = RecoveryToken(
                id=self._generate_id("rec"),
                user_id=user_id,
                token_hash=self._hash_code(token),
                method=method,
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )

            self._log_event(user_id, "recovery_initiated", details={"method": method.value})

            return RecoveryResponse(
                success=True,
                message="Recovery email sent",
                next_step="Check your email for the recovery link",
            )

        return RecoveryResponse(
            success=False,
            message="Recovery method not supported",
        )

    def complete_recovery(self, token: str) -> RecoveryResponse:
        """Complete account recovery."""
        recovery = self.recovery_tokens.get(token)
        if not recovery:
            return RecoveryResponse(success=False, message="Invalid recovery token")

        if datetime.utcnow() > recovery.expires_at:
            del self.recovery_tokens[token]
            return RecoveryResponse(success=False, message="Recovery token expired")

        user_id = recovery.user_id

        # Disable MFA
        config = self._get_or_create_config(user_id)
        config.mfa_enabled = False
        config.totp = None
        config.sms = None
        config.email = None
        config.backup_codes = None
        config.primary_method = None
        config.updated_at = datetime.utcnow()

        if user_id in self.totp_secrets:
            del self.totp_secrets[user_id]

        recovery.used_at = datetime.utcnow()
        del self.recovery_tokens[token]

        self._log_event(user_id, "recovery_completed", details={"method": recovery.method.value})

        return RecoveryResponse(
            success=True,
            message="MFA has been disabled. Please set up new MFA methods.",
        )

    # MFA Policy

    def get_mfa_policy(self, organization_id: str) -> MFAPolicy:
        """Get MFA policy for organization."""
        if organization_id not in self.mfa_policies:
            self.mfa_policies[organization_id] = MFAPolicy(organization_id=organization_id)
        return self.mfa_policies[organization_id]

    def update_mfa_policy(self, organization_id: str, data: MFAPolicyUpdate) -> MFAPolicy:
        """Update MFA policy."""
        policy = self.get_mfa_policy(organization_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)

        return policy

    # Status & Configuration

    def get_mfa_status(self, user_id: str) -> MFAStatusResponse:
        """Get MFA status for user."""
        config = self._get_or_create_config(user_id)

        methods_configured = self._get_available_methods(config)

        return MFAStatusResponse(
            mfa_enabled=config.mfa_enabled,
            mfa_enforced=config.mfa_enforced,
            methods_configured=methods_configured,
            primary_method=config.primary_method,
            backup_codes_remaining=config.backup_codes.codes_remaining if config.backup_codes else 0,
            trusted_devices_count=len(config.trusted_devices),
        )

    def get_mfa_config(self, user_id: str) -> UserMFAConfig:
        """Get full MFA configuration."""
        return self._get_or_create_config(user_id)

    def update_mfa_config(self, user_id: str, data: UserMFAConfigUpdate) -> UserMFAConfig:
        """Update MFA configuration."""
        config = self._get_or_create_config(user_id)

        if data.primary_method:
            available = self._get_available_methods(config)
            if data.primary_method in available:
                config.primary_method = data.primary_method

        if data.recovery_email:
            config.recovery_email = data.recovery_email

        config.updated_at = datetime.utcnow()
        return config

    # Event Logs

    def get_mfa_events(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> MFAEventListResponse:
        """Get MFA events for user."""
        events = [e for e in self.mfa_events if e.user_id == user_id]
        events.sort(key=lambda x: x.created_at, reverse=True)

        total = len(events)
        events = events[skip:skip + limit]

        return MFAEventListResponse(events=events, total=total)

    # Helper Methods

    def _get_available_methods(self, config: UserMFAConfig) -> list[MFAMethod]:
        """Get available MFA methods for user."""
        methods = []
        if config.totp and config.totp.status == MFAStatus.ACTIVE:
            methods.append(MFAMethod.TOTP)
        if config.sms and config.sms.status == MFAStatus.ACTIVE:
            methods.append(MFAMethod.SMS)
        if config.email and config.email.status == MFAStatus.ACTIVE:
            methods.append(MFAMethod.EMAIL)
        if config.hardware_keys:
            methods.append(MFAMethod.HARDWARE_KEY)
        return methods

    def _get_fallback_method(self, config: UserMFAConfig) -> Optional[MFAMethod]:
        """Get fallback MFA method."""
        methods = self._get_available_methods(config)
        return methods[0] if methods else None

    def _has_any_method(self, config: UserMFAConfig) -> bool:
        """Check if user has any MFA method configured."""
        return len(self._get_available_methods(config)) > 0


# Global service instance
two_factor_auth_service = TwoFactorAuthService()
