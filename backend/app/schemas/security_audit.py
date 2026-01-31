"""
Security Audit & Monitoring Schemas

Pydantic schemas for security auditing, intrusion detection,
anomaly detection, threat intelligence, and security incident management.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class AuditCategory(str, Enum):
    """Audit event categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    CONFIGURATION = "configuration"
    ADMIN_ACTION = "admin_action"
    SECURITY = "security"
    SYSTEM = "system"


class AuditSeverity(str, Enum):
    """Audit event severity"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ThreatType(str, Enum):
    """Threat types"""
    BRUTE_FORCE = "brute_force"
    CREDENTIAL_STUFFING = "credential_stuffing"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDoS = "ddos"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    MALWARE = "malware"
    PHISHING = "phishing"
    INSIDER_THREAT = "insider_threat"
    UNKNOWN = "unknown"


class ThreatSeverity(str, Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatStatus(str, Enum):
    """Threat status"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class IncidentStatus(str, Enum):
    """Security incident status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    REMEDIATED = "remediated"
    CLOSED = "closed"


class IncidentPriority(str, Enum):
    """Incident priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(str, Enum):
    """Anomaly types"""
    LOGIN_PATTERN = "login_pattern"
    ACCESS_PATTERN = "access_pattern"
    DATA_VOLUME = "data_volume"
    API_USAGE = "api_usage"
    GEOGRAPHIC = "geographic"
    TIME_BASED = "time_based"
    BEHAVIORAL = "behavioral"


class VulnerabilitySeverity(str, Enum):
    """Vulnerability severity (CVSS-based)"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VulnerabilityStatus(str, Enum):
    """Vulnerability status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REMEDIATED = "remediated"
    ACCEPTED = "accepted"  # Risk accepted
    FALSE_POSITIVE = "false_positive"


# Audit Log Models

class AuditLog(BaseModel):
    """Security audit log entry"""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    category: AuditCategory
    severity: AuditSeverity
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    organization_id: Optional[str] = None
    ip_address: str
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    old_value: Optional[dict[str, Any]] = None
    new_value: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    geo_location: Optional[dict[str, Any]] = None


class AuditLogCreate(BaseModel):
    """Create audit log entry"""
    category: AuditCategory
    severity: AuditSeverity
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    organization_id: Optional[str] = None
    ip_address: str
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    old_value: Optional[dict[str, Any]] = None
    new_value: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogListResponse(BaseModel):
    """List audit logs response"""
    logs: list[AuditLog]
    total: int


class AuditLogFilter(BaseModel):
    """Audit log filter criteria"""
    category: Optional[AuditCategory] = None
    severity: Optional[AuditSeverity] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    ip_address: Optional[str] = None
    success: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# Threat Detection Models

class ThreatIndicator(BaseModel):
    """Threat indicator"""
    id: str
    threat_type: ThreatType
    severity: ThreatSeverity
    indicator_type: str  # ip, domain, hash, email, etc.
    indicator_value: str
    description: Optional[str] = None
    source: str  # internal, external feed, manual
    confidence: float  # 0.0 - 1.0
    first_seen: datetime
    last_seen: datetime
    times_seen: int = 1
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    active: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ThreatIndicatorCreate(BaseModel):
    """Create threat indicator"""
    threat_type: ThreatType
    severity: ThreatSeverity
    indicator_type: str
    indicator_value: str
    description: Optional[str] = None
    source: str = "manual"
    confidence: float = 0.8
    tags: list[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None


class ThreatDetection(BaseModel):
    """Detected threat"""
    id: str
    threat_type: ThreatType
    severity: ThreatSeverity
    status: ThreatStatus
    title: str
    description: str
    source: str  # Rule, ML, external
    confidence: float
    affected_resources: list[str] = Field(default_factory=list)
    affected_users: list[str] = Field(default_factory=list)
    indicators: list[str] = Field(default_factory=list)  # Indicator IDs
    ip_addresses: list[str] = Field(default_factory=list)
    user_agents: list[str] = Field(default_factory=list)
    organization_id: Optional[str] = None
    assigned_to: Optional[str] = None
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    related_incidents: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ThreatDetectionListResponse(BaseModel):
    """List threat detections response"""
    detections: list[ThreatDetection]
    total: int


# Anomaly Detection Models

class AnomalyBaseline(BaseModel):
    """Behavioral baseline for anomaly detection"""
    id: str
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    baseline_type: str  # login_times, access_patterns, data_volume
    metrics: dict[str, Any]  # Statistical measures
    sample_count: int
    last_updated: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DetectedAnomaly(BaseModel):
    """Detected anomaly"""
    id: str
    anomaly_type: AnomalyType
    severity: ThreatSeverity
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    description: str
    expected_value: Optional[str] = None
    actual_value: str
    deviation_score: float  # Standard deviations from normal
    confidence: float
    ip_address: Optional[str] = None
    related_events: list[str] = Field(default_factory=list)
    investigated: bool = False
    false_positive: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    investigated_at: Optional[datetime] = None
    investigated_by: Optional[str] = None


class AnomalyListResponse(BaseModel):
    """List anomalies response"""
    anomalies: list[DetectedAnomaly]
    total: int


# Security Incident Models

class SecurityIncident(BaseModel):
    """Security incident"""
    id: str
    title: str
    description: str
    incident_type: ThreatType
    status: IncidentStatus
    priority: IncidentPriority
    severity: ThreatSeverity
    organization_id: str
    reported_by: str
    assigned_to: Optional[str] = None
    affected_systems: list[str] = Field(default_factory=list)
    affected_users: list[str] = Field(default_factory=list)
    affected_data: list[str] = Field(default_factory=list)
    attack_vectors: list[str] = Field(default_factory=list)
    indicators_of_compromise: list[str] = Field(default_factory=list)
    related_threats: list[str] = Field(default_factory=list)
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    containment_actions: list[str] = Field(default_factory=list)
    remediation_actions: list[str] = Field(default_factory=list)
    lessons_learned: Optional[str] = None
    post_mortem_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    contained_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class SecurityIncidentCreate(BaseModel):
    """Create security incident"""
    title: str
    description: str
    incident_type: ThreatType
    priority: IncidentPriority
    severity: ThreatSeverity
    organization_id: str
    affected_systems: list[str] = Field(default_factory=list)
    affected_users: list[str] = Field(default_factory=list)
    attack_vectors: list[str] = Field(default_factory=list)


class SecurityIncidentUpdate(BaseModel):
    """Update security incident"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None
    priority: Optional[IncidentPriority] = None
    assigned_to: Optional[str] = None
    affected_systems: Optional[list[str]] = None
    affected_users: Optional[list[str]] = None
    containment_actions: Optional[list[str]] = None
    remediation_actions: Optional[list[str]] = None
    lessons_learned: Optional[str] = None


class SecurityIncidentListResponse(BaseModel):
    """List security incidents response"""
    incidents: list[SecurityIncident]
    total: int


# Vulnerability Management Models

class Vulnerability(BaseModel):
    """Security vulnerability"""
    id: str
    cve_id: Optional[str] = None
    title: str
    description: str
    severity: VulnerabilitySeverity
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    status: VulnerabilityStatus
    affected_component: str
    affected_versions: list[str] = Field(default_factory=list)
    organization_id: Optional[str] = None
    discovered_at: datetime
    discovered_by: str  # scanner, manual, external report
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    remediation_steps: list[str] = Field(default_factory=list)
    workaround: Optional[str] = None
    references: list[str] = Field(default_factory=list)
    exploitability: str = "unknown"  # none, poc, active
    patch_available: bool = False
    patch_version: Optional[str] = None
    verified_at: Optional[datetime] = None
    remediated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VulnerabilityCreate(BaseModel):
    """Create vulnerability"""
    cve_id: Optional[str] = None
    title: str
    description: str
    severity: VulnerabilitySeverity
    cvss_score: Optional[float] = None
    affected_component: str
    affected_versions: list[str] = Field(default_factory=list)
    organization_id: Optional[str] = None
    discovered_by: str
    remediation_steps: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


class VulnerabilityUpdate(BaseModel):
    """Update vulnerability"""
    status: Optional[VulnerabilityStatus] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    remediation_steps: Optional[list[str]] = None
    workaround: Optional[str] = None
    patch_available: Optional[bool] = None
    patch_version: Optional[str] = None


class VulnerabilityListResponse(BaseModel):
    """List vulnerabilities response"""
    vulnerabilities: list[Vulnerability]
    total: int


# Security Metrics Models

class SecurityMetrics(BaseModel):
    """Security metrics dashboard data"""
    organization_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Authentication metrics
    total_logins_24h: int = 0
    failed_logins_24h: int = 0
    unique_users_24h: int = 0
    mfa_usage_percent: float = 0.0

    # Threat metrics
    active_threats: int = 0
    threats_detected_24h: int = 0
    threats_resolved_24h: int = 0
    mean_time_to_detect_hours: float = 0.0
    mean_time_to_resolve_hours: float = 0.0

    # Incident metrics
    open_incidents: int = 0
    critical_incidents: int = 0
    incidents_created_24h: int = 0
    incidents_resolved_24h: int = 0

    # Vulnerability metrics
    open_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    overdue_vulnerabilities: int = 0
    vulnerabilities_fixed_30d: int = 0

    # Anomaly metrics
    anomalies_detected_24h: int = 0
    false_positive_rate: float = 0.0

    # Compliance metrics
    audit_log_coverage: float = 100.0
    data_classification_coverage: float = 0.0


class SecurityTrend(BaseModel):
    """Security trend data"""
    metric: str
    period: str  # daily, weekly, monthly
    data_points: list[dict[str, Any]] = Field(default_factory=list)


class SecurityScorecard(BaseModel):
    """Security scorecard"""
    organization_id: str
    overall_score: int  # 0-100
    categories: dict[str, int] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


# Alert Models

class SecurityAlert(BaseModel):
    """Security alert"""
    id: str
    alert_type: str
    severity: ThreatSeverity
    title: str
    message: str
    source: str
    organization_id: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SecurityAlertListResponse(BaseModel):
    """List security alerts response"""
    alerts: list[SecurityAlert]
    total: int


# Constants

AUDIT_RETENTION_DAYS = 365
THREAT_INDICATOR_DEFAULT_EXPIRY_DAYS = 90
ANOMALY_DETECTION_WINDOW_HOURS = 24
VULNERABILITY_SLA_DAYS = {
    VulnerabilitySeverity.CRITICAL: 7,
    VulnerabilitySeverity.HIGH: 30,
    VulnerabilitySeverity.MEDIUM: 90,
    VulnerabilitySeverity.LOW: 180,
}

AUDIT_CATEGORY_LABELS = {
    AuditCategory.AUTHENTICATION: "Authentication",
    AuditCategory.AUTHORIZATION: "Authorization",
    AuditCategory.DATA_ACCESS: "Data Access",
    AuditCategory.DATA_MODIFICATION: "Data Modification",
    AuditCategory.CONFIGURATION: "Configuration",
    AuditCategory.ADMIN_ACTION: "Admin Action",
    AuditCategory.SECURITY: "Security",
    AuditCategory.SYSTEM: "System",
}

THREAT_TYPE_LABELS = {
    ThreatType.BRUTE_FORCE: "Brute Force Attack",
    ThreatType.CREDENTIAL_STUFFING: "Credential Stuffing",
    ThreatType.SQL_INJECTION: "SQL Injection",
    ThreatType.XSS: "Cross-Site Scripting",
    ThreatType.CSRF: "Cross-Site Request Forgery",
    ThreatType.DDoS: "DDoS Attack",
    ThreatType.DATA_EXFILTRATION: "Data Exfiltration",
    ThreatType.PRIVILEGE_ESCALATION: "Privilege Escalation",
    ThreatType.MALWARE: "Malware",
    ThreatType.PHISHING: "Phishing",
    ThreatType.INSIDER_THREAT: "Insider Threat",
    ThreatType.UNKNOWN: "Unknown",
}


# Helper Functions

def calculate_cvss_severity(score: float) -> VulnerabilitySeverity:
    """Calculate severity from CVSS score."""
    if score >= 9.0:
        return VulnerabilitySeverity.CRITICAL
    if score >= 7.0:
        return VulnerabilitySeverity.HIGH
    if score >= 4.0:
        return VulnerabilitySeverity.MEDIUM
    if score > 0:
        return VulnerabilitySeverity.LOW
    return VulnerabilitySeverity.NONE


def get_vulnerability_sla_date(severity: VulnerabilitySeverity, discovered_at: datetime) -> datetime:
    """Get SLA date for vulnerability remediation."""
    from datetime import timedelta
    days = VULNERABILITY_SLA_DAYS.get(severity, 90)
    return discovered_at + timedelta(days=days)


def calculate_security_score(metrics: SecurityMetrics) -> int:
    """Calculate overall security score from metrics."""
    score = 100

    # Deduct for failed logins (max 10 points)
    if metrics.total_logins_24h > 0:
        failure_rate = metrics.failed_logins_24h / metrics.total_logins_24h
        score -= min(int(failure_rate * 100), 10)

    # Deduct for active threats (5 points each, max 20)
    score -= min(metrics.active_threats * 5, 20)

    # Deduct for open incidents (5 points each, max 20)
    score -= min(metrics.open_incidents * 5, 20)

    # Deduct for critical vulnerabilities (10 points each, max 20)
    score -= min(metrics.critical_vulnerabilities * 10, 20)

    # Add for MFA usage (up to 10 points)
    score += int(metrics.mfa_usage_percent * 0.1)

    return max(0, min(100, score))
