"""
Two-Factor Authentication API Endpoints

REST API for TOTP, SMS, email verification, backup codes,
trusted devices, and recovery management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.two_factor_auth import (
    MFAMethod,
    TOTPSetupResponse, TOTPVerifyRequest,
    SMSSetupRequest, SMSSetupResponse, SMSVerifyRequest,
    EmailMFASetupRequest, EmailMFASetupResponse, EmailMFAVerifyRequest,
    BackupCodesResponse, BackupCodeVerifyRequest,
    TrustedDevice, TrustDeviceRequest, TrustedDeviceListResponse,
    MFAChallenge, MFAChallengeResponse, MFAVerificationResult,
    RecoveryMethod, RecoveryRequest, RecoveryResponse,
    UserMFAConfig, UserMFAConfigUpdate,
    MFAPolicy, MFAPolicyUpdate,
    MFAEventListResponse, MFAStatusResponse,
)
from app.services.two_factor_auth_service import two_factor_auth_service

router = APIRouter()


# MFA Status

@router.get("/users/{user_id}/mfa/status", response_model=MFAStatusResponse, tags=["mfa-status"])
async def get_mfa_status(user_id: str):
    """Get MFA status for user."""
    return two_factor_auth_service.get_mfa_status(user_id)


@router.get("/users/{user_id}/mfa/config", response_model=UserMFAConfig, tags=["mfa-status"])
async def get_mfa_config(user_id: str):
    """Get full MFA configuration."""
    return two_factor_auth_service.get_mfa_config(user_id)


@router.patch("/users/{user_id}/mfa/config", response_model=UserMFAConfig, tags=["mfa-status"])
async def update_mfa_config(user_id: str, data: UserMFAConfigUpdate):
    """Update MFA configuration."""
    return two_factor_auth_service.update_mfa_config(user_id, data)


# TOTP (Authenticator App)

@router.post("/users/{user_id}/mfa/totp/setup", response_model=TOTPSetupResponse, tags=["totp"])
async def setup_totp(
    user_id: str,
    user_email: str = Query(..., description="User's email for TOTP label"),
):
    """Initialize TOTP setup. Returns QR code and backup codes."""
    return two_factor_auth_service.setup_totp(user_id, user_email)


@router.post("/users/{user_id}/mfa/totp/verify-setup", tags=["totp"])
async def verify_totp_setup(
    user_id: str,
    data: TOTPVerifyRequest,
    ip_address: Optional[str] = Query(None),
):
    """Verify TOTP code to complete setup."""
    if two_factor_auth_service.verify_totp_setup(data.setup_token, data.code, ip_address):
        return {"success": True, "message": "TOTP enabled successfully"}
    raise HTTPException(status_code=400, detail="Invalid verification code or setup expired")


@router.post("/users/{user_id}/mfa/totp/verify", tags=["totp"])
async def verify_totp(
    user_id: str,
    code: str = Query(..., min_length=6, max_length=6),
):
    """Verify TOTP code for authentication."""
    if two_factor_auth_service.verify_totp(user_id, code):
        return {"valid": True}
    return {"valid": False}


@router.post("/users/{user_id}/mfa/totp/disable", tags=["totp"])
async def disable_totp(
    user_id: str,
    code: str = Query(..., description="Current TOTP code to confirm"),
):
    """Disable TOTP after verification."""
    if two_factor_auth_service.disable_totp(user_id, code):
        return {"success": True, "message": "TOTP disabled"}
    raise HTTPException(status_code=400, detail="Invalid verification code")


# SMS MFA

@router.post("/users/{user_id}/mfa/sms/setup", response_model=SMSSetupResponse, tags=["sms"])
async def setup_sms(user_id: str, data: SMSSetupRequest):
    """Initialize SMS MFA setup."""
    return two_factor_auth_service.setup_sms(user_id, data.phone_number)


@router.post("/users/{user_id}/mfa/sms/verify-setup", tags=["sms"])
async def verify_sms_setup(
    user_id: str,
    data: SMSVerifyRequest,
    ip_address: Optional[str] = Query(None),
):
    """Verify SMS code to complete setup."""
    if two_factor_auth_service.verify_sms_setup(data.setup_token, data.code, ip_address):
        return {"success": True, "message": "SMS MFA enabled successfully"}
    raise HTTPException(status_code=400, detail="Invalid verification code or setup expired")


@router.post("/users/{user_id}/mfa/sms/send", tags=["sms"])
async def send_sms_code(user_id: str):
    """Send SMS verification code."""
    token = two_factor_auth_service.send_sms_code(user_id)
    if not token:
        raise HTTPException(status_code=400, detail="SMS MFA not configured")
    return {"verification_token": token, "message": "SMS code sent"}


@router.post("/users/{user_id}/mfa/sms/verify", tags=["sms"])
async def verify_sms(
    user_id: str,
    token: str = Query(...),
    code: str = Query(..., min_length=6, max_length=6),
):
    """Verify SMS code."""
    if two_factor_auth_service.verify_sms(user_id, token, code):
        return {"valid": True}
    return {"valid": False}


# Email MFA

@router.post("/users/{user_id}/mfa/email/setup", response_model=EmailMFASetupResponse, tags=["email-mfa"])
async def setup_email_mfa(
    user_id: str,
    email: str = Query(..., description="Email address for MFA"),
):
    """Initialize email MFA setup."""
    return two_factor_auth_service.setup_email_mfa(user_id, email)


@router.post("/users/{user_id}/mfa/email/verify-setup", tags=["email-mfa"])
async def verify_email_mfa_setup(
    user_id: str,
    data: EmailMFAVerifyRequest,
    ip_address: Optional[str] = Query(None),
):
    """Verify email code to complete setup."""
    if two_factor_auth_service.verify_email_mfa_setup(data.setup_token, data.code, ip_address):
        return {"success": True, "message": "Email MFA enabled successfully"}
    raise HTTPException(status_code=400, detail="Invalid verification code or setup expired")


@router.post("/users/{user_id}/mfa/email/send", tags=["email-mfa"])
async def send_email_code(user_id: str):
    """Send email verification code."""
    token = two_factor_auth_service.send_email_code(user_id)
    if not token:
        raise HTTPException(status_code=400, detail="Email MFA not configured")
    return {"verification_token": token, "message": "Email code sent"}


@router.post("/users/{user_id}/mfa/email/verify", tags=["email-mfa"])
async def verify_email_mfa(
    user_id: str,
    token: str = Query(...),
    code: str = Query(..., min_length=6, max_length=6),
):
    """Verify email MFA code."""
    if two_factor_auth_service.verify_email_mfa(user_id, token, code):
        return {"valid": True}
    return {"valid": False}


# Backup Codes

@router.post("/users/{user_id}/mfa/backup-codes/regenerate", response_model=BackupCodesResponse, tags=["backup-codes"])
async def regenerate_backup_codes(user_id: str):
    """Regenerate backup codes. Old codes will be invalidated."""
    result = two_factor_auth_service.regenerate_backup_codes(user_id)
    if not result:
        raise HTTPException(status_code=400, detail="MFA must be enabled to generate backup codes")
    return result


@router.post("/users/{user_id}/mfa/backup-codes/verify", tags=["backup-codes"])
async def verify_backup_code(user_id: str, data: BackupCodeVerifyRequest):
    """Verify and consume backup code."""
    if two_factor_auth_service.verify_backup_code(user_id, data.code):
        return {"valid": True, "message": "Backup code used successfully"}
    return {"valid": False, "message": "Invalid backup code"}


# Trusted Devices

@router.get("/users/{user_id}/mfa/devices", response_model=TrustedDeviceListResponse, tags=["trusted-devices"])
async def list_trusted_devices(user_id: str):
    """List trusted devices for user."""
    return two_factor_auth_service.list_trusted_devices(user_id)


@router.post("/users/{user_id}/mfa/devices/trust", response_model=TrustedDevice, tags=["trusted-devices"])
async def trust_device(
    user_id: str,
    data: TrustDeviceRequest,
    device_type: str = Query("desktop"),
    browser: Optional[str] = Query(None),
    os: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
):
    """Add device to trusted list."""
    return two_factor_auth_service.trust_device(
        user_id, data.device_id, data.name,
        device_type, browser, os, ip_address,
        data.trust_duration_days or 30,
    )


@router.get("/users/{user_id}/mfa/devices/{device_id}/check", tags=["trusted-devices"])
async def check_device_trust(user_id: str, device_id: str):
    """Check if device is trusted."""
    trusted = two_factor_auth_service.is_device_trusted(user_id, device_id)
    return {"trusted": trusted}


@router.delete("/users/{user_id}/mfa/devices/{device_id}", tags=["trusted-devices"])
async def revoke_device_trust(user_id: str, device_id: str):
    """Revoke trust from device."""
    if two_factor_auth_service.revoke_device_trust(user_id, device_id):
        return {"success": True, "message": "Device trust revoked"}
    raise HTTPException(status_code=404, detail="Device not found")


# MFA Challenge Flow

@router.post("/mfa/challenge", response_model=MFAChallenge, tags=["mfa-challenge"])
async def create_mfa_challenge(
    user_id: str = Query(...),
    device_id: Optional[str] = Query(None),
    device_type: Optional[str] = Query(None),
    browser: Optional[str] = Query(None),
    os: Optional[str] = Query(None),
):
    """Create MFA challenge for authentication."""
    device_info = {}
    if device_id:
        device_info = {
            "device_id": device_id,
            "device_type": device_type,
            "browser": browser,
            "os": os,
        }

    challenge = two_factor_auth_service.create_mfa_challenge(user_id, device_info)
    if not challenge:
        raise HTTPException(status_code=400, detail="MFA not enabled for user")
    return challenge


@router.post("/mfa/challenge/{challenge_id}/verify", response_model=MFAVerificationResult, tags=["mfa-challenge"])
async def verify_mfa_challenge(
    challenge_id: str,
    response: MFAChallengeResponse,
    ip_address: Optional[str] = Query(None),
):
    """Verify MFA challenge response."""
    return two_factor_auth_service.verify_mfa_challenge(challenge_id, response, ip_address)


# Recovery

@router.post("/users/{user_id}/mfa/recovery/initiate", response_model=RecoveryResponse, tags=["recovery"])
async def initiate_recovery(
    user_id: str,
    method: RecoveryMethod = Query(...),
    email: Optional[str] = Query(None),
):
    """Initiate account recovery."""
    return two_factor_auth_service.initiate_recovery(user_id, method, email)


@router.post("/mfa/recovery/complete", response_model=RecoveryResponse, tags=["recovery"])
async def complete_recovery(token: str = Query(...)):
    """Complete account recovery."""
    return two_factor_auth_service.complete_recovery(token)


# MFA Policy (Organization)

@router.get("/organizations/{org_id}/mfa/policy", response_model=MFAPolicy, tags=["mfa-policy"])
async def get_mfa_policy(org_id: str):
    """Get MFA policy for organization."""
    return two_factor_auth_service.get_mfa_policy(org_id)


@router.put("/organizations/{org_id}/mfa/policy", response_model=MFAPolicy, tags=["mfa-policy"])
async def update_mfa_policy(org_id: str, data: MFAPolicyUpdate):
    """Update MFA policy."""
    return two_factor_auth_service.update_mfa_policy(org_id, data)


# MFA Events

@router.get("/users/{user_id}/mfa/events", response_model=MFAEventListResponse, tags=["mfa-events"])
async def get_mfa_events(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get MFA events for user."""
    return two_factor_auth_service.get_mfa_events(user_id, skip, limit)
