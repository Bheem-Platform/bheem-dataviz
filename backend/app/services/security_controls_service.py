"""
Advanced Security Controls Service

Service for managing rate limiting, IP policies, session security,
password policies, API keys, and security configurations.
"""

import hashlib
import secrets
import ipaddress
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from collections import defaultdict

from app.schemas.security_controls import (
    RateLimitRule, RateLimitRuleCreate, RateLimitRuleUpdate,
    RateLimitScope, RateLimitAction, RateLimitStatus, RateLimitRuleListResponse,
    IPRule, IPRuleCreate, IPRuleUpdate, IPListType, IPMatchType, IPCheckResult, IPRuleListResponse,
    SessionConfig, SessionConfigUpdate, ActiveSession, SessionListResponse, SessionRisk,
    PasswordPolicy, PasswordPolicyUpdate, PasswordValidationResult, PasswordStrengthCheck,
    APIKey, APIKeyCreate, APIKeyCreateResponse, APIKeyUpdate, APIKeyListResponse,
    APIKeyStatus, APIKeyUsageStats,
    SecurityEvent, SecurityEventType, SecurityEventListResponse, SecurityRiskLevel,
    CORSConfig, CORSConfigUpdate, CSPConfig, CSPConfigUpdate,
    SecurityHeaders, SecurityHeadersUpdate,
    SecurityOverview, SecurityRecommendation,
    calculate_password_strength, generate_api_key, get_api_key_prefix,
)


class SecurityControlsService:
    """Service for advanced security controls."""

    def __init__(self):
        # In-memory stores (use database in production)
        self._rate_limit_rules: Dict[str, RateLimitRule] = {}
        self._rate_limit_counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._rate_limit_windows: Dict[str, datetime] = {}
        self._ip_rules: Dict[str, IPRule] = {}
        self._session_configs: Dict[str, SessionConfig] = {}
        self._active_sessions: Dict[str, ActiveSession] = {}
        self._password_policies: Dict[str, PasswordPolicy] = {}
        self._password_history: Dict[str, List[str]] = defaultdict(list)
        self._api_keys: Dict[str, APIKey] = {}
        self._api_key_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._security_events: List[SecurityEvent] = []
        self._cors_configs: Dict[str, CORSConfig] = {}
        self._csp_configs: Dict[str, CSPConfig] = {}
        self._security_headers: Dict[str, SecurityHeaders] = {}
        self._common_passwords: set = self._load_common_passwords()

        # Initialize default rules
        self._init_default_rate_limits()

    def _load_common_passwords(self) -> set:
        """Load common passwords list."""
        # In production, load from file
        return {
            "password", "123456", "12345678", "qwerty", "abc123",
            "monkey", "1234567", "letmein", "trustno1", "dragon",
            "baseball", "iloveyou", "master", "sunshine", "ashley",
            "foobar", "passw0rd", "shadow", "123123", "654321",
            "superman", "qazwsx", "michael", "football", "password1",
        }

    def _init_default_rate_limits(self):
        """Initialize default rate limit rules."""
        default_rules = [
            RateLimitRule(
                id="default-global",
                name="Default Global Limit",
                description="Default rate limit for all requests",
                scope=RateLimitScope.GLOBAL,
                requests_per_minute=100,
                requests_per_hour=5000,
                requests_per_day=50000,
                burst_limit=20,
                action=RateLimitAction.BLOCK,
            ),
            RateLimitRule(
                id="auth-endpoints",
                name="Authentication Endpoints",
                description="Stricter limits for auth endpoints",
                scope=RateLimitScope.ENDPOINT,
                endpoint_pattern=r"^/api/v1/auth/.*",
                requests_per_minute=10,
                requests_per_hour=100,
                requests_per_day=500,
                burst_limit=5,
                action=RateLimitAction.BLOCK,
                priority=10,
            ),
        ]
        for rule in default_rules:
            self._rate_limit_rules[rule.id] = rule

    # Rate Limiting

    def create_rate_limit_rule(self, data: RateLimitRuleCreate) -> RateLimitRule:
        """Create a rate limit rule."""
        rule_id = f"rule-{secrets.token_hex(8)}"
        rule = RateLimitRule(
            id=rule_id,
            **data.model_dump(),
        )
        self._rate_limit_rules[rule_id] = rule
        return rule

    def get_rate_limit_rule(self, rule_id: str) -> Optional[RateLimitRule]:
        """Get rate limit rule by ID."""
        return self._rate_limit_rules.get(rule_id)

    def update_rate_limit_rule(self, rule_id: str, data: RateLimitRuleUpdate) -> Optional[RateLimitRule]:
        """Update rate limit rule."""
        rule = self._rate_limit_rules.get(rule_id)
        if not rule:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rule, key, value)
        rule.updated_at = datetime.utcnow()

        return rule

    def delete_rate_limit_rule(self, rule_id: str) -> bool:
        """Delete rate limit rule."""
        if rule_id in self._rate_limit_rules:
            del self._rate_limit_rules[rule_id]
            return True
        return False

    def list_rate_limit_rules(self, skip: int = 0, limit: int = 50) -> RateLimitRuleListResponse:
        """List all rate limit rules."""
        rules = sorted(
            self._rate_limit_rules.values(),
            key=lambda r: (-r.priority, r.name),
        )
        return RateLimitRuleListResponse(
            rules=rules[skip:skip + limit],
            total=len(rules),
        )

    def check_rate_limit(
        self,
        ip_address: str,
        endpoint: str,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> RateLimitStatus:
        """Check rate limit for request."""
        now = datetime.utcnow()

        # Find applicable rules
        applicable_rules = []
        for rule in self._rate_limit_rules.values():
            if not rule.enabled:
                continue

            # Check endpoint pattern
            if rule.endpoint_pattern:
                if not re.match(rule.endpoint_pattern, endpoint):
                    continue

            # Check exemptions
            if user_id and user_id in rule.exemptions:
                continue
            if api_key and api_key in rule.exemptions:
                continue

            applicable_rules.append(rule)

        # Sort by priority (highest first)
        applicable_rules.sort(key=lambda r: -r.priority)

        # Use first applicable rule or default
        rule = applicable_rules[0] if applicable_rules else None

        if not rule:
            # No rate limiting
            return RateLimitStatus(
                ip_address=ip_address,
                endpoint=endpoint,
                user_id=user_id,
                api_key=api_key,
                requests_this_minute=0,
                requests_this_hour=0,
                requests_today=0,
                limit_reached=False,
                reset_at=now + timedelta(minutes=1),
            )

        # Determine key based on scope
        if rule.scope == RateLimitScope.USER and user_id:
            key = f"user:{user_id}"
        elif rule.scope == RateLimitScope.API_KEY and api_key:
            key = f"apikey:{api_key}"
        elif rule.scope == RateLimitScope.ENDPOINT:
            key = f"endpoint:{ip_address}:{endpoint}"
        else:
            key = f"ip:{ip_address}"

        # Get current counters
        minute_key = f"{key}:minute:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"{key}:hour:{now.strftime('%Y%m%d%H')}"
        day_key = f"{key}:day:{now.strftime('%Y%m%d')}"

        requests_minute = self._rate_limit_counters[minute_key]["count"]
        requests_hour = self._rate_limit_counters[hour_key]["count"]
        requests_day = self._rate_limit_counters[day_key]["count"]

        # Check limits
        limit_reached = (
            requests_minute >= rule.requests_per_minute or
            requests_hour >= rule.requests_per_hour or
            requests_day >= rule.requests_per_day
        )

        retry_after = None
        if limit_reached:
            retry_after = rule.retry_after_seconds

        # Increment counters if not blocked
        if not limit_reached:
            self._rate_limit_counters[minute_key]["count"] += 1
            self._rate_limit_counters[hour_key]["count"] += 1
            self._rate_limit_counters[day_key]["count"] += 1

        return RateLimitStatus(
            ip_address=ip_address,
            endpoint=endpoint,
            user_id=user_id,
            api_key=api_key,
            requests_this_minute=requests_minute + (0 if limit_reached else 1),
            requests_this_hour=requests_hour + (0 if limit_reached else 1),
            requests_today=requests_day + (0 if limit_reached else 1),
            limit_reached=limit_reached,
            retry_after=retry_after,
            reset_at=now + timedelta(minutes=1),
        )

    # IP Policies

    def create_ip_rule(self, data: IPRuleCreate, created_by: str) -> IPRule:
        """Create IP allowlist/blocklist rule."""
        rule_id = f"ip-{secrets.token_hex(8)}"
        rule = IPRule(
            id=rule_id,
            created_by=created_by,
            **data.model_dump(),
        )
        self._ip_rules[rule_id] = rule
        return rule

    def get_ip_rule(self, rule_id: str) -> Optional[IPRule]:
        """Get IP rule by ID."""
        return self._ip_rules.get(rule_id)

    def update_ip_rule(self, rule_id: str, data: IPRuleUpdate) -> Optional[IPRule]:
        """Update IP rule."""
        rule = self._ip_rules.get(rule_id)
        if not rule:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rule, key, value)
        rule.updated_at = datetime.utcnow()

        return rule

    def delete_ip_rule(self, rule_id: str) -> bool:
        """Delete IP rule."""
        if rule_id in self._ip_rules:
            del self._ip_rules[rule_id]
            return True
        return False

    def list_ip_rules(
        self,
        list_type: Optional[IPListType] = None,
        organization_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> IPRuleListResponse:
        """List IP rules."""
        rules = list(self._ip_rules.values())

        if list_type:
            rules = [r for r in rules if r.list_type == list_type]
        if organization_id:
            rules = [r for r in rules if r.organization_id == organization_id or r.organization_id is None]

        rules.sort(key=lambda r: r.created_at, reverse=True)
        return IPRuleListResponse(
            rules=rules[skip:skip + limit],
            total=len(rules),
        )

    def check_ip(self, ip_address: str, organization_id: Optional[str] = None) -> IPCheckResult:
        """Check if IP is allowed."""
        # Get applicable rules
        rules = [
            r for r in self._ip_rules.values()
            if r.enabled and (r.organization_id is None or r.organization_id == organization_id)
        ]

        # Check expiration
        now = datetime.utcnow()
        rules = [r for r in rules if not r.expires_at or r.expires_at > now]

        matched_rule = None
        allowed = True  # Default allow if no blocklist matches

        for rule in rules:
            matches = False

            if rule.match_type == IPMatchType.EXACT:
                matches = ip_address == rule.value
            elif rule.match_type == IPMatchType.CIDR:
                try:
                    matches = ipaddress.ip_address(ip_address) in ipaddress.ip_network(rule.value, strict=False)
                except ValueError:
                    pass
            elif rule.match_type == IPMatchType.RANGE:
                # Format: "192.168.1.1-192.168.1.255"
                try:
                    start, end = rule.value.split("-")
                    ip = ipaddress.ip_address(ip_address)
                    matches = ipaddress.ip_address(start) <= ip <= ipaddress.ip_address(end)
                except (ValueError, TypeError):
                    pass

            if matches:
                matched_rule = rule
                if rule.list_type == IPListType.BLOCKLIST:
                    allowed = False
                    break
                elif rule.list_type == IPListType.ALLOWLIST:
                    allowed = True

        return IPCheckResult(
            ip_address=ip_address,
            allowed=allowed,
            matched_rule=matched_rule,
            risk_score=0 if allowed else 100,
        )

    # Session Security

    def get_session_config(self, organization_id: str) -> SessionConfig:
        """Get session configuration."""
        if organization_id not in self._session_configs:
            self._session_configs[organization_id] = SessionConfig(organization_id=organization_id)
        return self._session_configs[organization_id]

    def update_session_config(self, organization_id: str, data: SessionConfigUpdate) -> SessionConfig:
        """Update session configuration."""
        config = self.get_session_config(organization_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(config, key, value)
        config.updated_at = datetime.utcnow()
        return config

    def create_session(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
        device_type: str = "desktop",
        browser: Optional[str] = None,
        os: Optional[str] = None,
    ) -> ActiveSession:
        """Create a new session."""
        session_id = f"sess-{secrets.token_hex(16)}"
        now = datetime.utcnow()

        session = ActiveSession(
            id=session_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
            browser=browser,
            os=os,
            created_at=now,
            last_activity_at=now,
            expires_at=now + timedelta(hours=1),
            risk_level=SessionRisk.LOW,
        )

        self._active_sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ActiveSession]:
        """Get session by ID."""
        return self._active_sessions.get(session_id)

    def list_user_sessions(self, user_id: str, current_session_id: Optional[str] = None) -> SessionListResponse:
        """List active sessions for user."""
        sessions = [
            s for s in self._active_sessions.values()
            if s.user_id == user_id and s.expires_at > datetime.utcnow()
        ]

        # Mark current session
        for session in sessions:
            session.is_current = session.id == current_session_id

        sessions.sort(key=lambda s: s.last_activity_at, reverse=True)
        return SessionListResponse(sessions=sessions, total=len(sessions))

    def terminate_session(self, session_id: str) -> bool:
        """Terminate a session."""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            return True
        return False

    def terminate_all_user_sessions(self, user_id: str, except_session_id: Optional[str] = None) -> int:
        """Terminate all sessions for user."""
        sessions_to_remove = [
            s.id for s in self._active_sessions.values()
            if s.user_id == user_id and s.id != except_session_id
        ]
        for session_id in sessions_to_remove:
            del self._active_sessions[session_id]
        return len(sessions_to_remove)

    def update_session_activity(self, session_id: str) -> Optional[ActiveSession]:
        """Update session last activity."""
        session = self._active_sessions.get(session_id)
        if session:
            session.last_activity_at = datetime.utcnow()
        return session

    # Password Policies

    def get_password_policy(self, organization_id: str) -> PasswordPolicy:
        """Get password policy."""
        if organization_id not in self._password_policies:
            self._password_policies[organization_id] = PasswordPolicy(organization_id=organization_id)
        return self._password_policies[organization_id]

    def update_password_policy(self, organization_id: str, data: PasswordPolicyUpdate) -> PasswordPolicy:
        """Update password policy."""
        policy = self.get_password_policy(organization_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(policy, key, value)
        policy.updated_at = datetime.utcnow()
        return policy

    def validate_password(
        self,
        password: str,
        organization_id: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> PasswordValidationResult:
        """Validate password against policy."""
        policy = self.get_password_policy(organization_id)
        errors = []
        suggestions = []

        # Length checks
        if len(password) < policy.min_length:
            errors.append(f"Password must be at least {policy.min_length} characters")
        if len(password) > policy.max_length:
            errors.append(f"Password must not exceed {policy.max_length} characters")

        # Character requirements
        if policy.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
            suggestions.append("Add an uppercase letter")

        if policy.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
            suggestions.append("Add a lowercase letter")

        if policy.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
            suggestions.append("Add a number")

        if policy.require_special_chars:
            if not any(c in policy.special_chars_allowed for c in password):
                errors.append("Password must contain at least one special character")
                suggestions.append(f"Add a special character: {policy.special_chars_allowed[:10]}...")

        # Common password check
        if policy.disallow_common_passwords and password.lower() in self._common_passwords:
            errors.append("Password is too common")
            suggestions.append("Choose a more unique password")

        # Personal info check
        if policy.disallow_personal_info:
            password_lower = password.lower()
            if user_email:
                email_parts = user_email.lower().split("@")[0]
                if email_parts in password_lower:
                    errors.append("Password cannot contain your email")
            if user_name:
                name_parts = user_name.lower().split()
                for part in name_parts:
                    if len(part) > 2 and part in password_lower:
                        errors.append("Password cannot contain parts of your name")
                        break

        # Password history check
        if user_id and policy.password_history_count > 0:
            history = self._password_history.get(user_id, [])
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash in history[-policy.password_history_count:]:
                errors.append(f"Cannot reuse one of your last {policy.password_history_count} passwords")

        # Calculate strength
        strength_score, strength_label = calculate_password_strength(password)

        return PasswordValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            strength_score=strength_score,
            strength_label=strength_label,
            suggestions=suggestions,
        )

    def check_password_strength(self, data: PasswordStrengthCheck) -> PasswordValidationResult:
        """Check password strength without policy validation."""
        strength_score, strength_label = calculate_password_strength(data.password)

        suggestions = []
        if len(data.password) < 12:
            suggestions.append("Use at least 12 characters")
        if not any(c.isupper() for c in data.password):
            suggestions.append("Add uppercase letters")
        if not any(c.isdigit() for c in data.password):
            suggestions.append("Add numbers")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in data.password):
            suggestions.append("Add special characters")

        return PasswordValidationResult(
            valid=strength_score >= 40,
            errors=[],
            strength_score=strength_score,
            strength_label=strength_label,
            suggestions=suggestions,
        )

    def add_password_to_history(self, user_id: str, password: str):
        """Add password hash to user's history."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self._password_history[user_id].append(password_hash)
        # Keep only last N passwords based on max policy
        self._password_history[user_id] = self._password_history[user_id][-10:]

    # API Keys

    def create_api_key(self, user_id: str, organization_id: Optional[str], data: APIKeyCreate) -> APIKeyCreateResponse:
        """Create a new API key."""
        key, key_hash = generate_api_key()
        key_id = f"ak-{secrets.token_hex(8)}"

        api_key = APIKey(
            id=key_id,
            key_prefix=get_api_key_prefix(key),
            key_hash=key_hash,
            user_id=user_id,
            organization_id=organization_id,
            **data.model_dump(),
        )

        self._api_keys[key_id] = api_key

        return APIKeyCreateResponse(
            api_key=api_key,
            key=key,
        )

    def get_api_key(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID."""
        return self._api_keys.get(key_id)

    def validate_api_key(self, key: str) -> Optional[APIKey]:
        """Validate API key and return if valid."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        for api_key in self._api_keys.values():
            if api_key.key_hash == key_hash:
                # Check status
                if api_key.status != APIKeyStatus.ACTIVE:
                    return None

                # Check expiration
                if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                    api_key.status = APIKeyStatus.EXPIRED
                    return None

                # Update usage
                api_key.last_used_at = datetime.utcnow()
                api_key.usage_count += 1

                return api_key

        return None

    def update_api_key(self, key_id: str, data: APIKeyUpdate) -> Optional[APIKey]:
        """Update API key."""
        api_key = self._api_keys.get(key_id)
        if not api_key:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(api_key, key, value)

        return api_key

    def revoke_api_key(self, key_id: str, revoked_by: str) -> bool:
        """Revoke an API key."""
        api_key = self._api_keys.get(key_id)
        if not api_key:
            return False

        api_key.status = APIKeyStatus.REVOKED
        api_key.revoked_at = datetime.utcnow()
        api_key.revoked_by = revoked_by
        return True

    def list_api_keys(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        status: Optional[APIKeyStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> APIKeyListResponse:
        """List API keys."""
        keys = list(self._api_keys.values())

        if user_id:
            keys = [k for k in keys if k.user_id == user_id]
        if organization_id:
            keys = [k for k in keys if k.organization_id == organization_id]
        if status:
            keys = [k for k in keys if k.status == status]

        keys.sort(key=lambda k: k.created_at, reverse=True)
        return APIKeyListResponse(
            api_keys=keys[skip:skip + limit],
            total=len(keys),
        )

    def get_api_key_usage(self, key_id: str) -> Optional[APIKeyUsageStats]:
        """Get API key usage statistics."""
        api_key = self._api_keys.get(key_id)
        if not api_key:
            return None

        # In production, this would query from metrics/analytics
        return APIKeyUsageStats(
            api_key_id=key_id,
            total_requests=api_key.usage_count,
            requests_today=0,
            requests_this_week=0,
            requests_this_month=api_key.usage_count,
            unique_ips=1,
            last_used_at=api_key.last_used_at,
        )

    # Security Events

    def log_security_event(
        self,
        event_type: SecurityEventType,
        ip_address: str,
        success: bool,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: str = "",
        user_agent: Optional[str] = None,
        risk_level: SecurityRiskLevel = SecurityRiskLevel.NONE,
        details: Optional[Dict[str, Any]] = None,
    ) -> SecurityEvent:
        """Log a security event."""
        event = SecurityEvent(
            id=f"evt-{secrets.token_hex(8)}",
            event_type=event_type,
            user_id=user_id,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action or event_type.value,
            success=success,
            risk_level=risk_level,
            details=details or {},
        )

        self._security_events.append(event)

        # Keep only last 10000 events in memory
        if len(self._security_events) > 10000:
            self._security_events = self._security_events[-10000:]

        return event

    def list_security_events(
        self,
        event_type: Optional[SecurityEventType] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        risk_level: Optional[SecurityRiskLevel] = None,
        success: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> SecurityEventListResponse:
        """List security events."""
        events = list(self._security_events)

        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if organization_id:
            events = [e for e in events if e.organization_id == organization_id]
        if risk_level:
            events = [e for e in events if e.risk_level == risk_level]
        if success is not None:
            events = [e for e in events if e.success == success]

        events.sort(key=lambda e: e.created_at, reverse=True)
        return SecurityEventListResponse(
            events=events[skip:skip + limit],
            total=len(events),
        )

    # CORS & Security Headers

    def get_cors_config(self, organization_id: str) -> CORSConfig:
        """Get CORS configuration."""
        if organization_id not in self._cors_configs:
            self._cors_configs[organization_id] = CORSConfig(organization_id=organization_id)
        return self._cors_configs[organization_id]

    def update_cors_config(self, organization_id: str, data: CORSConfigUpdate) -> CORSConfig:
        """Update CORS configuration."""
        config = self.get_cors_config(organization_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(config, key, value)
        config.updated_at = datetime.utcnow()
        return config

    def get_csp_config(self, organization_id: str) -> CSPConfig:
        """Get CSP configuration."""
        if organization_id not in self._csp_configs:
            self._csp_configs[organization_id] = CSPConfig(organization_id=organization_id)
        return self._csp_configs[organization_id]

    def update_csp_config(self, organization_id: str, data: CSPConfigUpdate) -> CSPConfig:
        """Update CSP configuration."""
        config = self.get_csp_config(organization_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(config, key, value)
        config.updated_at = datetime.utcnow()
        return config

    def get_security_headers(self, organization_id: str) -> SecurityHeaders:
        """Get security headers configuration."""
        if organization_id not in self._security_headers:
            self._security_headers[organization_id] = SecurityHeaders(organization_id=organization_id)
        return self._security_headers[organization_id]

    def update_security_headers(self, organization_id: str, data: SecurityHeadersUpdate) -> SecurityHeaders:
        """Update security headers."""
        headers = self.get_security_headers(organization_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(headers, key, value)
        headers.updated_at = datetime.utcnow()
        return headers

    # Security Overview

    def get_security_overview(self, organization_id: str) -> SecurityOverview:
        """Get security overview for organization."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Count events today
        events_today = [
            e for e in self._security_events
            if e.organization_id == organization_id and e.created_at >= today_start
        ]

        failed_logins = len([
            e for e in events_today
            if e.event_type == SecurityEventType.LOGIN_FAILURE
        ])

        rate_limit_violations = len([
            e for e in events_today
            if e.event_type == SecurityEventType.RATE_LIMIT_EXCEEDED
        ])

        suspicious = len([
            e for e in events_today
            if e.risk_level in [SecurityRiskLevel.HIGH, SecurityRiskLevel.CRITICAL]
        ])

        # Count active API keys
        api_keys_active = len([
            k for k in self._api_keys.values()
            if k.organization_id == organization_id and k.status == APIKeyStatus.ACTIVE
        ])

        # Count blocked IPs
        blocked_ips = len([
            r for r in self._ip_rules.values()
            if r.organization_id == organization_id and
               r.list_type == IPListType.BLOCKLIST and r.enabled
        ])

        # Active sessions
        sessions_active = len([
            s for s in self._active_sessions.values()
            if s.expires_at > now
        ])

        # Calculate security score
        score = 70  # Base score
        if api_keys_active > 0:
            score += 5
        if blocked_ips > 0:
            score += 5
        if failed_logins < 10:
            score += 10
        if rate_limit_violations == 0:
            score += 10

        # Recommendations
        recommendations = []
        if failed_logins > 10:
            recommendations.append("High number of failed login attempts detected")
        if rate_limit_violations > 0:
            recommendations.append("Rate limit violations detected - review limits")

        return SecurityOverview(
            organization_id=organization_id,
            security_score=min(score, 100),
            mfa_adoption_percent=75.0,  # Would calculate from user data
            api_keys_active=api_keys_active,
            blocked_ips_count=blocked_ips,
            rate_limit_violations_today=rate_limit_violations,
            failed_logins_today=failed_logins,
            suspicious_activities_today=suspicious,
            password_policy_compliant_percent=90.0,  # Would calculate
            sessions_active=sessions_active,
            recommendations=recommendations,
        )

    def get_security_recommendations(self, organization_id: str) -> List[SecurityRecommendation]:
        """Get security recommendations."""
        recommendations = []

        # Check password policy
        policy = self.get_password_policy(organization_id)
        if policy.min_length < 12:
            recommendations.append(SecurityRecommendation(
                id="pwd-length",
                title="Increase minimum password length",
                description="Consider increasing minimum password length to 12+ characters",
                severity=SecurityRiskLevel.MEDIUM,
                category="password_policy",
            ))

        # Check session config
        session_config = self.get_session_config(organization_id)
        if not session_config.require_mfa_for_new_device:
            recommendations.append(SecurityRecommendation(
                id="mfa-new-device",
                title="Require MFA for new devices",
                description="Enable MFA requirement when users log in from new devices",
                severity=SecurityRiskLevel.MEDIUM,
                category="session_security",
            ))

        return recommendations


# Create singleton instance
security_controls_service = SecurityControlsService()
