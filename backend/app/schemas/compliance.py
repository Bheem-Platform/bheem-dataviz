"""
Compliance & Data Protection Schemas

Pydantic schemas for GDPR compliance, data retention, consent management,
data subject requests, encryption, and privacy controls.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import datetime, date


# Enums

class ConsentType(str, Enum):
    """Types of consent"""
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    THIRD_PARTY = "third_party"
    ESSENTIAL = "essential"
    PERSONALIZATION = "personalization"
    DATA_PROCESSING = "data_processing"
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"


class ConsentStatus(str, Enum):
    """Consent status"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"


class DataSubjectRequestType(str, Enum):
    """GDPR data subject request types"""
    ACCESS = "access"  # Right to access
    RECTIFICATION = "rectification"  # Right to rectification
    ERASURE = "erasure"  # Right to erasure (right to be forgotten)
    PORTABILITY = "portability"  # Right to data portability
    RESTRICTION = "restriction"  # Right to restriction
    OBJECTION = "objection"  # Right to object
    AUTOMATED_DECISION = "automated_decision"  # Rights related to automated decision-making


class DataSubjectRequestStatus(str, Enum):
    """Request status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DataClassification(str, Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"  # Personally Identifiable Information
    SENSITIVE = "sensitive"  # Special category data


class RetentionAction(str, Enum):
    """Action when retention period expires"""
    DELETE = "delete"
    ANONYMIZE = "anonymize"
    ARCHIVE = "archive"
    REVIEW = "review"


class LegalBasis(str, Enum):
    """GDPR legal basis for processing"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_INTEREST = "public_interest"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class EncryptionAlgorithm(str, Enum):
    """Encryption algorithms"""
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    RSA_4096 = "rsa-4096"
    CHACHA20_POLY1305 = "chacha20-poly1305"


# Consent Models

class ConsentRecord(BaseModel):
    """Individual consent record"""
    id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    version: str  # Version of consent document
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    source: str = "web"  # web, mobile, api, etc.
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConsentRequest(BaseModel):
    """Request to grant/update consent"""
    consent_type: ConsentType
    status: ConsentStatus
    version: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    source: str = "web"


class ConsentBulkRequest(BaseModel):
    """Bulk consent update"""
    consents: list[ConsentRequest]


class ConsentPreferences(BaseModel):
    """User's consent preferences"""
    user_id: str
    marketing: ConsentStatus = ConsentStatus.PENDING
    analytics: ConsentStatus = ConsentStatus.PENDING
    third_party: ConsentStatus = ConsentStatus.PENDING
    personalization: ConsentStatus = ConsentStatus.PENDING
    essential: ConsentStatus = ConsentStatus.GRANTED  # Always granted
    terms_accepted: bool = False
    terms_version: Optional[str] = None
    privacy_accepted: bool = False
    privacy_version: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ConsentAuditLog(BaseModel):
    """Consent change audit log"""
    id: str
    user_id: str
    consent_type: ConsentType
    previous_status: Optional[ConsentStatus] = None
    new_status: ConsentStatus
    changed_by: str  # user_id or "system"
    reason: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConsentListResponse(BaseModel):
    """List consent records response"""
    records: list[ConsentRecord]
    total: int


# Data Subject Request Models

class DataSubjectRequest(BaseModel):
    """GDPR data subject request"""
    id: str
    user_id: str
    request_type: DataSubjectRequestType
    status: DataSubjectRequestStatus
    email: EmailStr
    description: Optional[str] = None
    identity_verified: bool = False
    verification_method: Optional[str] = None
    verified_at: Optional[datetime] = None
    data_categories: list[str] = Field(default_factory=list)  # Specific data requested
    response_deadline: datetime  # GDPR requires response within 30 days
    response_extended: bool = False  # Can extend by 2 months for complex requests
    extension_reason: Optional[str] = None
    completed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    download_url: Optional[str] = None  # For portability requests
    download_expires_at: Optional[datetime] = None
    notes: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DataSubjectRequestCreate(BaseModel):
    """Create data subject request"""
    request_type: DataSubjectRequestType
    email: EmailStr
    description: Optional[str] = None
    data_categories: list[str] = Field(default_factory=list)


class DataSubjectRequestUpdate(BaseModel):
    """Update data subject request"""
    status: Optional[DataSubjectRequestStatus] = None
    identity_verified: Optional[bool] = None
    verification_method: Optional[str] = None
    rejection_reason: Optional[str] = None
    response_extended: Optional[bool] = None
    extension_reason: Optional[str] = None


class DataSubjectRequestListResponse(BaseModel):
    """List data subject requests response"""
    requests: list[DataSubjectRequest]
    total: int


# Data Retention Models

class RetentionPolicy(BaseModel):
    """Data retention policy"""
    id: str
    name: str
    description: Optional[str] = None
    data_category: str  # e.g., "user_data", "logs", "analytics"
    classification: DataClassification
    retention_days: int
    action: RetentionAction
    legal_basis: LegalBasis
    legal_hold: bool = False  # Prevents deletion even if retention expired
    organization_id: Optional[str] = None
    applies_to_tables: list[str] = Field(default_factory=list)
    applies_to_fields: list[str] = Field(default_factory=list)
    enabled: bool = True
    last_executed_at: Optional[datetime] = None
    next_execution_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RetentionPolicyCreate(BaseModel):
    """Create retention policy"""
    name: str
    description: Optional[str] = None
    data_category: str
    classification: DataClassification
    retention_days: int
    action: RetentionAction
    legal_basis: LegalBasis
    organization_id: Optional[str] = None
    applies_to_tables: list[str] = Field(default_factory=list)
    applies_to_fields: list[str] = Field(default_factory=list)
    enabled: bool = True


class RetentionPolicyUpdate(BaseModel):
    """Update retention policy"""
    name: Optional[str] = None
    description: Optional[str] = None
    retention_days: Optional[int] = None
    action: Optional[RetentionAction] = None
    legal_basis: Optional[LegalBasis] = None
    legal_hold: Optional[bool] = None
    applies_to_tables: Optional[list[str]] = None
    applies_to_fields: Optional[list[str]] = None
    enabled: Optional[bool] = None


class RetentionExecution(BaseModel):
    """Retention policy execution record"""
    id: str
    policy_id: str
    policy_name: str
    action: RetentionAction
    records_affected: int
    records_processed: int
    records_failed: int
    status: str  # "completed", "failed", "partial"
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class RetentionPolicyListResponse(BaseModel):
    """List retention policies response"""
    policies: list[RetentionPolicy]
    total: int


# Data Processing Records (GDPR Article 30)

class ProcessingActivity(BaseModel):
    """Record of processing activity"""
    id: str
    name: str
    description: str
    purpose: str
    legal_basis: LegalBasis
    data_categories: list[str]  # Categories of data processed
    data_subjects: list[str]  # Categories of data subjects
    recipients: list[str]  # Recipients of data
    third_country_transfers: list[str] = Field(default_factory=list)  # Countries outside EU
    transfer_safeguards: Optional[str] = None  # e.g., "Standard Contractual Clauses"
    retention_period: str  # Description of retention
    security_measures: list[str] = Field(default_factory=list)
    dpia_required: bool = False  # Data Protection Impact Assessment required
    dpia_conducted: bool = False
    dpia_date: Optional[date] = None
    controller_name: str
    controller_contact: str
    processor_name: Optional[str] = None
    processor_contact: Optional[str] = None
    dpo_contact: Optional[str] = None  # Data Protection Officer
    organization_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProcessingActivityCreate(BaseModel):
    """Create processing activity record"""
    name: str
    description: str
    purpose: str
    legal_basis: LegalBasis
    data_categories: list[str]
    data_subjects: list[str]
    recipients: list[str]
    third_country_transfers: list[str] = Field(default_factory=list)
    transfer_safeguards: Optional[str] = None
    retention_period: str
    security_measures: list[str] = Field(default_factory=list)
    dpia_required: bool = False
    controller_name: str
    controller_contact: str
    processor_name: Optional[str] = None
    processor_contact: Optional[str] = None
    dpo_contact: Optional[str] = None


class ProcessingActivityListResponse(BaseModel):
    """List processing activities response"""
    activities: list[ProcessingActivity]
    total: int


# Data Encryption Models

class EncryptionKey(BaseModel):
    """Encryption key metadata"""
    id: str
    name: str
    algorithm: EncryptionAlgorithm
    key_size: int
    purpose: str  # e.g., "data_at_rest", "data_in_transit", "pii"
    status: str  # "active", "rotating", "retired"
    version: int
    created_at: datetime
    rotated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    organization_id: Optional[str] = None


class EncryptionConfig(BaseModel):
    """Encryption configuration"""
    organization_id: str
    encrypt_at_rest: bool = True
    encrypt_in_transit: bool = True
    encrypt_pii: bool = True
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_rotation_days: int = 90
    auto_rotate_keys: bool = True
    pii_fields: list[str] = Field(default_factory=lambda: [
        "email", "phone", "ssn", "address", "name", "date_of_birth"
    ])
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EncryptionConfigUpdate(BaseModel):
    """Update encryption configuration"""
    encrypt_at_rest: Optional[bool] = None
    encrypt_in_transit: Optional[bool] = None
    encrypt_pii: Optional[bool] = None
    default_algorithm: Optional[EncryptionAlgorithm] = None
    key_rotation_days: Optional[int] = None
    auto_rotate_keys: Optional[bool] = None
    pii_fields: Optional[list[str]] = None


# Privacy Policy Models

class PrivacyDocument(BaseModel):
    """Privacy policy or terms document"""
    id: str
    document_type: str  # "privacy_policy", "terms_of_service", "cookie_policy"
    version: str
    title: str
    content: str
    effective_date: date
    published: bool = False
    published_at: Optional[datetime] = None
    organization_id: Optional[str] = None
    locale: str = "en"
    changelog: Optional[str] = None
    requires_acceptance: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PrivacyDocumentCreate(BaseModel):
    """Create privacy document"""
    document_type: str
    version: str
    title: str
    content: str
    effective_date: date
    organization_id: Optional[str] = None
    locale: str = "en"
    changelog: Optional[str] = None
    requires_acceptance: bool = True


class PrivacyDocumentUpdate(BaseModel):
    """Update privacy document"""
    title: Optional[str] = None
    content: Optional[str] = None
    effective_date: Optional[date] = None
    changelog: Optional[str] = None
    requires_acceptance: Optional[bool] = None


class PrivacyDocumentListResponse(BaseModel):
    """List privacy documents response"""
    documents: list[PrivacyDocument]
    total: int


# Data Anonymization Models

class AnonymizationRule(BaseModel):
    """Data anonymization rule"""
    id: str
    name: str
    description: Optional[str] = None
    field_name: str
    table_name: str
    technique: str  # "hash", "mask", "pseudonymize", "generalize", "suppress", "noise"
    parameters: dict[str, Any] = Field(default_factory=dict)
    preserve_format: bool = False  # Preserve format (e.g., email format)
    reversible: bool = False  # Can be de-anonymized with key
    enabled: bool = True
    organization_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnonymizationRuleCreate(BaseModel):
    """Create anonymization rule"""
    name: str
    description: Optional[str] = None
    field_name: str
    table_name: str
    technique: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    preserve_format: bool = False
    reversible: bool = False
    enabled: bool = True
    organization_id: Optional[str] = None


class AnonymizationExecution(BaseModel):
    """Anonymization execution record"""
    id: str
    rule_id: str
    rule_name: str
    records_processed: int
    records_anonymized: int
    records_failed: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None


# Data Breach Models

class DataBreach(BaseModel):
    """Data breach record"""
    id: str
    title: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    affected_records: int
    affected_data_types: list[str]
    affected_users: int
    discovery_date: datetime
    occurred_date: Optional[datetime] = None
    contained_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    reported_to_authority: bool = False
    authority_report_date: Optional[datetime] = None
    users_notified: bool = False
    notification_date: Optional[datetime] = None
    root_cause: Optional[str] = None
    remediation_steps: list[str] = Field(default_factory=list)
    organization_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DataBreachCreate(BaseModel):
    """Report data breach"""
    title: str
    description: str
    severity: str
    affected_records: int
    affected_data_types: list[str]
    affected_users: int
    discovery_date: datetime
    occurred_date: Optional[datetime] = None


class DataBreachUpdate(BaseModel):
    """Update data breach"""
    contained_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    reported_to_authority: Optional[bool] = None
    authority_report_date: Optional[datetime] = None
    users_notified: Optional[bool] = None
    notification_date: Optional[datetime] = None
    root_cause: Optional[str] = None
    remediation_steps: Optional[list[str]] = None


class DataBreachListResponse(BaseModel):
    """List data breaches response"""
    breaches: list[DataBreach]
    total: int


# Compliance Dashboard Models

class ComplianceStatus(BaseModel):
    """Overall compliance status"""
    organization_id: str
    gdpr_compliant: bool
    consent_coverage: float  # Percentage of users with all consents
    pending_dsr_count: int  # Data subject requests pending
    overdue_dsr_count: int  # Overdue DSRs
    retention_policies_active: int
    retention_policies_executed_today: int
    processing_activities_count: int
    data_breaches_open: int
    encryption_enabled: bool
    last_audit_date: Optional[date] = None
    next_audit_date: Optional[date] = None
    compliance_score: int  # 0-100


class ComplianceAuditLog(BaseModel):
    """Compliance audit log"""
    id: str
    action: str
    resource_type: str
    resource_id: str
    user_id: str
    user_email: str
    ip_address: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ComplianceAuditListResponse(BaseModel):
    """List compliance audit logs response"""
    logs: list[ComplianceAuditLog]
    total: int


# Constants

GDPR_RESPONSE_DAYS = 30
GDPR_EXTENSION_DAYS = 60
BREACH_NOTIFICATION_HOURS = 72
DATA_CATEGORIES = [
    "personal_data",
    "contact_info",
    "financial_data",
    "health_data",
    "location_data",
    "behavioral_data",
    "authentication_data",
    "communication_data",
    "device_data",
    "usage_data",
]

ANONYMIZATION_TECHNIQUES = {
    "hash": "One-way hash (SHA-256)",
    "mask": "Partial masking (e.g., ****@email.com)",
    "pseudonymize": "Replace with pseudonym (reversible)",
    "generalize": "Reduce precision (e.g., age range)",
    "suppress": "Remove entirely",
    "noise": "Add random noise",
}


# Helper Functions

def calculate_dsr_deadline(created_at: datetime, extended: bool = False) -> datetime:
    """Calculate DSR response deadline."""
    from datetime import timedelta
    days = GDPR_EXTENSION_DAYS if extended else GDPR_RESPONSE_DAYS
    return created_at + timedelta(days=days)


def is_dsr_overdue(request: DataSubjectRequest) -> bool:
    """Check if DSR is overdue."""
    if request.status in [DataSubjectRequestStatus.COMPLETED, DataSubjectRequestStatus.REJECTED]:
        return False
    return datetime.utcnow() > request.response_deadline


def mask_email(email: str) -> str:
    """Mask email for privacy."""
    if "@" not in email:
        return "***"
    local, domain = email.split("@")
    if len(local) <= 2:
        return f"{local[0]}***@{domain}"
    return f"{local[0]}***{local[-1]}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone number."""
    if len(phone) < 4:
        return "***"
    return f"***{phone[-4:]}"


def calculate_compliance_score(status: ComplianceStatus) -> int:
    """Calculate overall compliance score."""
    score = 0

    # GDPR compliance base
    if status.gdpr_compliant:
        score += 30

    # Consent coverage (up to 20 points)
    score += int(status.consent_coverage * 20)

    # No overdue DSRs (10 points)
    if status.overdue_dsr_count == 0:
        score += 10

    # Active retention policies (10 points)
    if status.retention_policies_active > 0:
        score += 10

    # Processing activities documented (10 points)
    if status.processing_activities_count > 0:
        score += 10

    # Encryption enabled (10 points)
    if status.encryption_enabled:
        score += 10

    # No open breaches (10 points)
    if status.data_breaches_open == 0:
        score += 10

    return min(score, 100)
