"""
Advanced Security Controls API Endpoints

REST API for rate limiting, IP policies, session security,
password policies, API keys, and security configurations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.security_controls import (
    RateLimitRule, RateLimitRuleCreate, RateLimitRuleUpdate,
    RateLimitScope, RateLimitStatus, RateLimitRuleListResponse,
    IPRule, IPRuleCreate, IPRuleUpdate, IPListType, IPCheckResult, IPRuleListResponse,
    SessionConfig, SessionConfigUpdate, ActiveSession, SessionListResponse,
    PasswordPolicy, PasswordPolicyUpdate, PasswordValidationResult, PasswordStrengthCheck,
    APIKey, APIKeyCreate, APIKeyCreateResponse, APIKeyUpdate, APIKeyListResponse,
    APIKeyStatus, APIKeyUsageStats,
    SecurityEvent, SecurityEventType, SecurityEventListResponse, SecurityRiskLevel,
    CORSConfig, CORSConfigUpdate, CSPConfig, CSPConfigUpdate,
    SecurityHeaders, SecurityHeadersUpdate,
    SecurityOverview, SecurityRecommendation,
)
from app.services.security_controls_service import security_controls_service

router = APIRouter()


# Rate Limiting

@router.post("/rate-limits", response_model=RateLimitRule, tags=["rate-limiting"])
async def create_rate_limit_rule(data: RateLimitRuleCreate):
    """Create a rate limit rule."""
    return security_controls_service.create_rate_limit_rule(data)


@router.get("/rate-limits", response_model=RateLimitRuleListResponse, tags=["rate-limiting"])
async def list_rate_limit_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List all rate limit rules."""
    return security_controls_service.list_rate_limit_rules(skip, limit)


@router.get("/rate-limits/{rule_id}", response_model=RateLimitRule, tags=["rate-limiting"])
async def get_rate_limit_rule(rule_id: str):
    """Get rate limit rule by ID."""
    rule = security_controls_service.get_rate_limit_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rate limit rule not found")
    return rule


@router.patch("/rate-limits/{rule_id}", response_model=RateLimitRule, tags=["rate-limiting"])
async def update_rate_limit_rule(rule_id: str, data: RateLimitRuleUpdate):
    """Update rate limit rule."""
    rule = security_controls_service.update_rate_limit_rule(rule_id, data)
    if not rule:
        raise HTTPException(status_code=404, detail="Rate limit rule not found")
    return rule


@router.delete("/rate-limits/{rule_id}", tags=["rate-limiting"])
async def delete_rate_limit_rule(rule_id: str):
    """Delete rate limit rule."""
    if security_controls_service.delete_rate_limit_rule(rule_id):
        return {"success": True, "message": "Rate limit rule deleted"}
    raise HTTPException(status_code=404, detail="Rate limit rule not found")


@router.post("/rate-limits/check", response_model=RateLimitStatus, tags=["rate-limiting"])
async def check_rate_limit(
    ip_address: str = Query(...),
    endpoint: str = Query(...),
    user_id: Optional[str] = Query(None),
    api_key: Optional[str] = Query(None),
):
    """Check rate limit status for a request."""
    return security_controls_service.check_rate_limit(ip_address, endpoint, user_id, api_key)


# IP Policies

@router.post("/ip-rules", response_model=IPRule, tags=["ip-policies"])
async def create_ip_rule(
    data: IPRuleCreate,
    created_by: str = Query(..., description="Admin user ID"),
):
    """Create IP allowlist/blocklist rule."""
    return security_controls_service.create_ip_rule(data, created_by)


@router.get("/ip-rules", response_model=IPRuleListResponse, tags=["ip-policies"])
async def list_ip_rules(
    list_type: Optional[IPListType] = Query(None),
    organization_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List IP rules."""
    return security_controls_service.list_ip_rules(list_type, organization_id, skip, limit)


@router.get("/ip-rules/{rule_id}", response_model=IPRule, tags=["ip-policies"])
async def get_ip_rule(rule_id: str):
    """Get IP rule by ID."""
    rule = security_controls_service.get_ip_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="IP rule not found")
    return rule


@router.patch("/ip-rules/{rule_id}", response_model=IPRule, tags=["ip-policies"])
async def update_ip_rule(rule_id: str, data: IPRuleUpdate):
    """Update IP rule."""
    rule = security_controls_service.update_ip_rule(rule_id, data)
    if not rule:
        raise HTTPException(status_code=404, detail="IP rule not found")
    return rule


@router.delete("/ip-rules/{rule_id}", tags=["ip-policies"])
async def delete_ip_rule(rule_id: str):
    """Delete IP rule."""
    if security_controls_service.delete_ip_rule(rule_id):
        return {"success": True, "message": "IP rule deleted"}
    raise HTTPException(status_code=404, detail="IP rule not found")


@router.post("/ip-rules/check", response_model=IPCheckResult, tags=["ip-policies"])
async def check_ip(
    ip_address: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Check if IP is allowed."""
    return security_controls_service.check_ip(ip_address, organization_id)


# Session Security

@router.get("/organizations/{org_id}/session-config", response_model=SessionConfig, tags=["session-security"])
async def get_session_config(org_id: str):
    """Get session security configuration."""
    return security_controls_service.get_session_config(org_id)


@router.patch("/organizations/{org_id}/session-config", response_model=SessionConfig, tags=["session-security"])
async def update_session_config(org_id: str, data: SessionConfigUpdate):
    """Update session security configuration."""
    return security_controls_service.update_session_config(org_id, data)


@router.get("/users/{user_id}/sessions", response_model=SessionListResponse, tags=["session-security"])
async def list_user_sessions(
    user_id: str,
    current_session_id: Optional[str] = Query(None),
):
    """List active sessions for user."""
    return security_controls_service.list_user_sessions(user_id, current_session_id)


@router.post("/sessions", response_model=ActiveSession, tags=["session-security"])
async def create_session(
    user_id: str = Query(...),
    ip_address: str = Query(...),
    user_agent: str = Query(...),
    device_type: str = Query("desktop"),
    browser: Optional[str] = Query(None),
    os: Optional[str] = Query(None),
):
    """Create a new session."""
    return security_controls_service.create_session(
        user_id, ip_address, user_agent, device_type, browser, os
    )


@router.delete("/sessions/{session_id}", tags=["session-security"])
async def terminate_session(session_id: str):
    """Terminate a session."""
    if security_controls_service.terminate_session(session_id):
        return {"success": True, "message": "Session terminated"}
    raise HTTPException(status_code=404, detail="Session not found")


@router.post("/users/{user_id}/sessions/terminate-all", tags=["session-security"])
async def terminate_all_sessions(
    user_id: str,
    except_session_id: Optional[str] = Query(None, description="Session to keep active"),
):
    """Terminate all sessions for user."""
    count = security_controls_service.terminate_all_user_sessions(user_id, except_session_id)
    return {"success": True, "sessions_terminated": count}


@router.post("/sessions/{session_id}/activity", response_model=ActiveSession, tags=["session-security"])
async def update_session_activity(session_id: str):
    """Update session last activity timestamp."""
    session = security_controls_service.update_session_activity(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# Password Policies

@router.get("/organizations/{org_id}/password-policy", response_model=PasswordPolicy, tags=["password-policy"])
async def get_password_policy(org_id: str):
    """Get password policy."""
    return security_controls_service.get_password_policy(org_id)


@router.patch("/organizations/{org_id}/password-policy", response_model=PasswordPolicy, tags=["password-policy"])
async def update_password_policy(org_id: str, data: PasswordPolicyUpdate):
    """Update password policy."""
    return security_controls_service.update_password_policy(org_id, data)


@router.post("/organizations/{org_id}/password/validate", response_model=PasswordValidationResult, tags=["password-policy"])
async def validate_password(
    org_id: str,
    password: str = Query(..., min_length=1),
    user_id: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    user_name: Optional[str] = Query(None),
):
    """Validate password against policy."""
    return security_controls_service.validate_password(
        password, org_id, user_id, user_email, user_name
    )


@router.post("/password/strength", response_model=PasswordValidationResult, tags=["password-policy"])
async def check_password_strength(data: PasswordStrengthCheck):
    """Check password strength without policy validation."""
    return security_controls_service.check_password_strength(data)


# API Keys

@router.post("/api-keys", response_model=APIKeyCreateResponse, tags=["api-keys"])
async def create_api_key(
    data: APIKeyCreate,
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Create a new API key."""
    return security_controls_service.create_api_key(user_id, organization_id, data)


@router.get("/api-keys", response_model=APIKeyListResponse, tags=["api-keys"])
async def list_api_keys(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    status: Optional[APIKeyStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List API keys."""
    return security_controls_service.list_api_keys(user_id, organization_id, status, skip, limit)


@router.get("/api-keys/{key_id}", response_model=APIKey, tags=["api-keys"])
async def get_api_key(key_id: str):
    """Get API key by ID."""
    key = security_controls_service.get_api_key(key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key


@router.patch("/api-keys/{key_id}", response_model=APIKey, tags=["api-keys"])
async def update_api_key(key_id: str, data: APIKeyUpdate):
    """Update API key."""
    key = security_controls_service.update_api_key(key_id, data)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key


@router.post("/api-keys/{key_id}/revoke", tags=["api-keys"])
async def revoke_api_key(
    key_id: str,
    revoked_by: str = Query(..., description="User ID revoking the key"),
):
    """Revoke an API key."""
    if security_controls_service.revoke_api_key(key_id, revoked_by):
        return {"success": True, "message": "API key revoked"}
    raise HTTPException(status_code=404, detail="API key not found")


@router.post("/api-keys/validate", response_model=APIKey, tags=["api-keys"])
async def validate_api_key(key: str = Query(..., description="API key to validate")):
    """Validate an API key."""
    api_key = security_controls_service.validate_api_key(key)
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


@router.get("/api-keys/{key_id}/usage", response_model=APIKeyUsageStats, tags=["api-keys"])
async def get_api_key_usage(key_id: str):
    """Get API key usage statistics."""
    usage = security_controls_service.get_api_key_usage(key_id)
    if not usage:
        raise HTTPException(status_code=404, detail="API key not found")
    return usage


# Security Events

@router.get("/events", response_model=SecurityEventListResponse, tags=["security-events"])
async def list_security_events(
    event_type: Optional[SecurityEventType] = Query(None),
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    risk_level: Optional[SecurityRiskLevel] = Query(None),
    success: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List security events."""
    return security_controls_service.list_security_events(
        event_type, user_id, organization_id, risk_level, success, skip, limit
    )


@router.post("/events", response_model=SecurityEvent, tags=["security-events"])
async def log_security_event(
    event_type: SecurityEventType = Query(...),
    ip_address: str = Query(...),
    success: bool = Query(...),
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    action: str = Query(""),
    user_agent: Optional[str] = Query(None),
    risk_level: SecurityRiskLevel = Query(SecurityRiskLevel.NONE),
):
    """Log a security event."""
    return security_controls_service.log_security_event(
        event_type=event_type,
        ip_address=ip_address,
        success=success,
        user_id=user_id,
        organization_id=organization_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        user_agent=user_agent,
        risk_level=risk_level,
    )


# CORS & Security Headers

@router.get("/organizations/{org_id}/cors", response_model=CORSConfig, tags=["security-config"])
async def get_cors_config(org_id: str):
    """Get CORS configuration."""
    return security_controls_service.get_cors_config(org_id)


@router.patch("/organizations/{org_id}/cors", response_model=CORSConfig, tags=["security-config"])
async def update_cors_config(org_id: str, data: CORSConfigUpdate):
    """Update CORS configuration."""
    return security_controls_service.update_cors_config(org_id, data)


@router.get("/organizations/{org_id}/csp", response_model=CSPConfig, tags=["security-config"])
async def get_csp_config(org_id: str):
    """Get Content Security Policy configuration."""
    return security_controls_service.get_csp_config(org_id)


@router.patch("/organizations/{org_id}/csp", response_model=CSPConfig, tags=["security-config"])
async def update_csp_config(org_id: str, data: CSPConfigUpdate):
    """Update Content Security Policy configuration."""
    return security_controls_service.update_csp_config(org_id, data)


@router.get("/organizations/{org_id}/security-headers", response_model=SecurityHeaders, tags=["security-config"])
async def get_security_headers(org_id: str):
    """Get security headers configuration."""
    return security_controls_service.get_security_headers(org_id)


@router.patch("/organizations/{org_id}/security-headers", response_model=SecurityHeaders, tags=["security-config"])
async def update_security_headers(org_id: str, data: SecurityHeadersUpdate):
    """Update security headers configuration."""
    return security_controls_service.update_security_headers(org_id, data)


# Security Overview

@router.get("/organizations/{org_id}/overview", response_model=SecurityOverview, tags=["security-overview"])
async def get_security_overview(org_id: str):
    """Get security overview for organization."""
    return security_controls_service.get_security_overview(org_id)


@router.get("/organizations/{org_id}/recommendations", tags=["security-overview"])
async def get_security_recommendations(org_id: str):
    """Get security recommendations for organization."""
    recommendations = security_controls_service.get_security_recommendations(org_id)
    return {"recommendations": recommendations, "total": len(recommendations)}
