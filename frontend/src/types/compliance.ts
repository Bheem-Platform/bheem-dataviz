/**
 * Compliance & Data Protection Types
 *
 * TypeScript types for GDPR compliance, consent management,
 * data subject requests, retention policies, and privacy controls.
 */

// Enums

export enum ConsentType {
  MARKETING = 'marketing',
  ANALYTICS = 'analytics',
  THIRD_PARTY = 'third_party',
  ESSENTIAL = 'essential',
  PERSONALIZATION = 'personalization',
  DATA_PROCESSING = 'data_processing',
  TERMS_OF_SERVICE = 'terms_of_service',
  PRIVACY_POLICY = 'privacy_policy',
}

export enum ConsentStatus {
  GRANTED = 'granted',
  DENIED = 'denied',
  WITHDRAWN = 'withdrawn',
  PENDING = 'pending',
  EXPIRED = 'expired',
}

export enum DataSubjectRequestType {
  ACCESS = 'access',
  RECTIFICATION = 'rectification',
  ERASURE = 'erasure',
  PORTABILITY = 'portability',
  RESTRICTION = 'restriction',
  OBJECTION = 'objection',
  AUTOMATED_DECISION = 'automated_decision',
}

export enum DataSubjectRequestStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled',
}

export enum DataClassification {
  PUBLIC = 'public',
  INTERNAL = 'internal',
  CONFIDENTIAL = 'confidential',
  RESTRICTED = 'restricted',
  PII = 'pii',
  SENSITIVE = 'sensitive',
}

export enum RetentionAction {
  DELETE = 'delete',
  ANONYMIZE = 'anonymize',
  ARCHIVE = 'archive',
  REVIEW = 'review',
}

export enum LegalBasis {
  CONSENT = 'consent',
  CONTRACT = 'contract',
  LEGAL_OBLIGATION = 'legal_obligation',
  VITAL_INTERESTS = 'vital_interests',
  PUBLIC_INTEREST = 'public_interest',
  LEGITIMATE_INTERESTS = 'legitimate_interests',
}

export enum EncryptionAlgorithm {
  AES_256_GCM = 'aes-256-gcm',
  AES_256_CBC = 'aes-256-cbc',
  RSA_4096 = 'rsa-4096',
  CHACHA20_POLY1305 = 'chacha20-poly1305',
}

// Consent Interfaces

export interface ConsentRecord {
  id: string;
  user_id: string;
  consent_type: ConsentType;
  status: ConsentStatus;
  version: string;
  ip_address?: string;
  user_agent?: string;
  source: string;
  granted_at?: string;
  withdrawn_at?: string;
  expires_at?: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ConsentRequest {
  consent_type: ConsentType;
  status: ConsentStatus;
  version: string;
  ip_address?: string;
  user_agent?: string;
  source?: string;
}

export interface ConsentBulkRequest {
  consents: ConsentRequest[];
}

export interface ConsentPreferences {
  user_id: string;
  marketing: ConsentStatus;
  analytics: ConsentStatus;
  third_party: ConsentStatus;
  personalization: ConsentStatus;
  essential: ConsentStatus;
  terms_accepted: boolean;
  terms_version?: string;
  privacy_accepted: boolean;
  privacy_version?: string;
  last_updated: string;
}

export interface ConsentAuditLog {
  id: string;
  user_id: string;
  consent_type: ConsentType;
  previous_status?: ConsentStatus;
  new_status: ConsentStatus;
  changed_by: string;
  reason?: string;
  ip_address?: string;
  created_at: string;
}

export interface ConsentListResponse {
  records: ConsentRecord[];
  total: number;
}

// Data Subject Request Interfaces

export interface DataSubjectRequest {
  id: string;
  user_id: string;
  request_type: DataSubjectRequestType;
  status: DataSubjectRequestStatus;
  email: string;
  description?: string;
  identity_verified: boolean;
  verification_method?: string;
  verified_at?: string;
  data_categories: string[];
  response_deadline: string;
  response_extended: boolean;
  extension_reason?: string;
  completed_at?: string;
  rejection_reason?: string;
  download_url?: string;
  download_expires_at?: string;
  notes: Array<Record<string, unknown>>;
  created_at: string;
  updated_at: string;
}

export interface DataSubjectRequestCreate {
  request_type: DataSubjectRequestType;
  email: string;
  description?: string;
  data_categories?: string[];
}

export interface DataSubjectRequestUpdate {
  status?: DataSubjectRequestStatus;
  identity_verified?: boolean;
  verification_method?: string;
  rejection_reason?: string;
  response_extended?: boolean;
  extension_reason?: string;
}

export interface DataSubjectRequestListResponse {
  requests: DataSubjectRequest[];
  total: number;
}

// Retention Policy Interfaces

export interface RetentionPolicy {
  id: string;
  name: string;
  description?: string;
  data_category: string;
  classification: DataClassification;
  retention_days: number;
  action: RetentionAction;
  legal_basis: LegalBasis;
  legal_hold: boolean;
  organization_id?: string;
  applies_to_tables: string[];
  applies_to_fields: string[];
  enabled: boolean;
  last_executed_at?: string;
  next_execution_at?: string;
  created_at: string;
  updated_at: string;
}

export interface RetentionPolicyCreate {
  name: string;
  description?: string;
  data_category: string;
  classification: DataClassification;
  retention_days: number;
  action: RetentionAction;
  legal_basis: LegalBasis;
  organization_id?: string;
  applies_to_tables?: string[];
  applies_to_fields?: string[];
  enabled?: boolean;
}

export interface RetentionPolicyUpdate {
  name?: string;
  description?: string;
  retention_days?: number;
  action?: RetentionAction;
  legal_basis?: LegalBasis;
  legal_hold?: boolean;
  applies_to_tables?: string[];
  applies_to_fields?: string[];
  enabled?: boolean;
}

export interface RetentionExecution {
  id: string;
  policy_id: string;
  policy_name: string;
  action: RetentionAction;
  records_affected: number;
  records_processed: number;
  records_failed: number;
  status: string;
  error_message?: string;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
}

export interface RetentionPolicyListResponse {
  policies: RetentionPolicy[];
  total: number;
}

// Processing Activity Interfaces

export interface ProcessingActivity {
  id: string;
  name: string;
  description: string;
  purpose: string;
  legal_basis: LegalBasis;
  data_categories: string[];
  data_subjects: string[];
  recipients: string[];
  third_country_transfers: string[];
  transfer_safeguards?: string;
  retention_period: string;
  security_measures: string[];
  dpia_required: boolean;
  dpia_conducted: boolean;
  dpia_date?: string;
  controller_name: string;
  controller_contact: string;
  processor_name?: string;
  processor_contact?: string;
  dpo_contact?: string;
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export interface ProcessingActivityCreate {
  name: string;
  description: string;
  purpose: string;
  legal_basis: LegalBasis;
  data_categories: string[];
  data_subjects: string[];
  recipients: string[];
  third_country_transfers?: string[];
  transfer_safeguards?: string;
  retention_period: string;
  security_measures?: string[];
  dpia_required?: boolean;
  controller_name: string;
  controller_contact: string;
  processor_name?: string;
  processor_contact?: string;
  dpo_contact?: string;
}

export interface ProcessingActivityListResponse {
  activities: ProcessingActivity[];
  total: number;
}

// Encryption Interfaces

export interface EncryptionKey {
  id: string;
  name: string;
  algorithm: EncryptionAlgorithm;
  key_size: number;
  purpose: string;
  status: string;
  version: number;
  created_at: string;
  rotated_at?: string;
  expires_at?: string;
  organization_id?: string;
}

export interface EncryptionConfig {
  organization_id: string;
  encrypt_at_rest: boolean;
  encrypt_in_transit: boolean;
  encrypt_pii: boolean;
  default_algorithm: EncryptionAlgorithm;
  key_rotation_days: number;
  auto_rotate_keys: boolean;
  pii_fields: string[];
  updated_at: string;
}

export interface EncryptionConfigUpdate {
  encrypt_at_rest?: boolean;
  encrypt_in_transit?: boolean;
  encrypt_pii?: boolean;
  default_algorithm?: EncryptionAlgorithm;
  key_rotation_days?: number;
  auto_rotate_keys?: boolean;
  pii_fields?: string[];
}

// Privacy Document Interfaces

export interface PrivacyDocument {
  id: string;
  document_type: string;
  version: string;
  title: string;
  content: string;
  effective_date: string;
  published: boolean;
  published_at?: string;
  organization_id?: string;
  locale: string;
  changelog?: string;
  requires_acceptance: boolean;
  created_at: string;
  updated_at: string;
}

export interface PrivacyDocumentCreate {
  document_type: string;
  version: string;
  title: string;
  content: string;
  effective_date: string;
  organization_id?: string;
  locale?: string;
  changelog?: string;
  requires_acceptance?: boolean;
}

export interface PrivacyDocumentUpdate {
  title?: string;
  content?: string;
  effective_date?: string;
  changelog?: string;
  requires_acceptance?: boolean;
}

export interface PrivacyDocumentListResponse {
  documents: PrivacyDocument[];
  total: number;
}

// Anonymization Interfaces

export interface AnonymizationRule {
  id: string;
  name: string;
  description?: string;
  field_name: string;
  table_name: string;
  technique: string;
  parameters: Record<string, unknown>;
  preserve_format: boolean;
  reversible: boolean;
  enabled: boolean;
  organization_id?: string;
  created_at: string;
}

export interface AnonymizationRuleCreate {
  name: string;
  description?: string;
  field_name: string;
  table_name: string;
  technique: string;
  parameters?: Record<string, unknown>;
  preserve_format?: boolean;
  reversible?: boolean;
  enabled?: boolean;
  organization_id?: string;
}

// Data Breach Interfaces

export interface DataBreach {
  id: string;
  title: string;
  description: string;
  severity: string;
  affected_records: number;
  affected_data_types: string[];
  affected_users: number;
  discovery_date: string;
  occurred_date?: string;
  contained_date?: string;
  resolved_date?: string;
  reported_to_authority: boolean;
  authority_report_date?: string;
  users_notified: boolean;
  notification_date?: string;
  root_cause?: string;
  remediation_steps: string[];
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export interface DataBreachCreate {
  title: string;
  description: string;
  severity: string;
  affected_records: number;
  affected_data_types: string[];
  affected_users: number;
  discovery_date: string;
  occurred_date?: string;
}

export interface DataBreachUpdate {
  contained_date?: string;
  resolved_date?: string;
  reported_to_authority?: boolean;
  authority_report_date?: string;
  users_notified?: boolean;
  notification_date?: string;
  root_cause?: string;
  remediation_steps?: string[];
}

export interface DataBreachListResponse {
  breaches: DataBreach[];
  total: number;
}

// Compliance Status Interfaces

export interface ComplianceStatus {
  organization_id: string;
  gdpr_compliant: boolean;
  consent_coverage: number;
  pending_dsr_count: number;
  overdue_dsr_count: number;
  retention_policies_active: number;
  retention_policies_executed_today: number;
  processing_activities_count: number;
  data_breaches_open: number;
  encryption_enabled: boolean;
  last_audit_date?: string;
  next_audit_date?: string;
  compliance_score: number;
}

export interface ComplianceAuditLog {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  user_id: string;
  user_email: string;
  ip_address: string;
  details: Record<string, unknown>;
  created_at: string;
}

export interface ComplianceAuditListResponse {
  logs: ComplianceAuditLog[];
  total: number;
}

// Constants

export const GDPR_RESPONSE_DAYS = 30;
export const GDPR_EXTENSION_DAYS = 60;
export const BREACH_NOTIFICATION_HOURS = 72;

export const CONSENT_TYPE_LABELS: Record<ConsentType, string> = {
  [ConsentType.MARKETING]: 'Marketing Communications',
  [ConsentType.ANALYTICS]: 'Analytics & Statistics',
  [ConsentType.THIRD_PARTY]: 'Third-Party Sharing',
  [ConsentType.ESSENTIAL]: 'Essential Cookies',
  [ConsentType.PERSONALIZATION]: 'Personalization',
  [ConsentType.DATA_PROCESSING]: 'Data Processing',
  [ConsentType.TERMS_OF_SERVICE]: 'Terms of Service',
  [ConsentType.PRIVACY_POLICY]: 'Privacy Policy',
};

export const CONSENT_STATUS_LABELS: Record<ConsentStatus, string> = {
  [ConsentStatus.GRANTED]: 'Granted',
  [ConsentStatus.DENIED]: 'Denied',
  [ConsentStatus.WITHDRAWN]: 'Withdrawn',
  [ConsentStatus.PENDING]: 'Pending',
  [ConsentStatus.EXPIRED]: 'Expired',
};

export const DSR_TYPE_LABELS: Record<DataSubjectRequestType, string> = {
  [DataSubjectRequestType.ACCESS]: 'Right to Access',
  [DataSubjectRequestType.RECTIFICATION]: 'Right to Rectification',
  [DataSubjectRequestType.ERASURE]: 'Right to Erasure',
  [DataSubjectRequestType.PORTABILITY]: 'Right to Portability',
  [DataSubjectRequestType.RESTRICTION]: 'Right to Restriction',
  [DataSubjectRequestType.OBJECTION]: 'Right to Object',
  [DataSubjectRequestType.AUTOMATED_DECISION]: 'Automated Decision Making',
};

export const DSR_STATUS_LABELS: Record<DataSubjectRequestStatus, string> = {
  [DataSubjectRequestStatus.PENDING]: 'Pending',
  [DataSubjectRequestStatus.IN_PROGRESS]: 'In Progress',
  [DataSubjectRequestStatus.COMPLETED]: 'Completed',
  [DataSubjectRequestStatus.REJECTED]: 'Rejected',
  [DataSubjectRequestStatus.CANCELLED]: 'Cancelled',
};

export const DATA_CLASSIFICATION_LABELS: Record<DataClassification, string> = {
  [DataClassification.PUBLIC]: 'Public',
  [DataClassification.INTERNAL]: 'Internal',
  [DataClassification.CONFIDENTIAL]: 'Confidential',
  [DataClassification.RESTRICTED]: 'Restricted',
  [DataClassification.PII]: 'PII',
  [DataClassification.SENSITIVE]: 'Sensitive',
};

export const RETENTION_ACTION_LABELS: Record<RetentionAction, string> = {
  [RetentionAction.DELETE]: 'Delete',
  [RetentionAction.ANONYMIZE]: 'Anonymize',
  [RetentionAction.ARCHIVE]: 'Archive',
  [RetentionAction.REVIEW]: 'Review',
};

export const LEGAL_BASIS_LABELS: Record<LegalBasis, string> = {
  [LegalBasis.CONSENT]: 'Consent',
  [LegalBasis.CONTRACT]: 'Contract',
  [LegalBasis.LEGAL_OBLIGATION]: 'Legal Obligation',
  [LegalBasis.VITAL_INTERESTS]: 'Vital Interests',
  [LegalBasis.PUBLIC_INTEREST]: 'Public Interest',
  [LegalBasis.LEGITIMATE_INTERESTS]: 'Legitimate Interests',
};

// Helper Functions

export function getConsentStatusColor(status: ConsentStatus): string {
  const colors: Record<ConsentStatus, string> = {
    [ConsentStatus.GRANTED]: 'green',
    [ConsentStatus.DENIED]: 'red',
    [ConsentStatus.WITHDRAWN]: 'orange',
    [ConsentStatus.PENDING]: 'yellow',
    [ConsentStatus.EXPIRED]: 'gray',
  };
  return colors[status] || 'gray';
}

export function getDSRStatusColor(status: DataSubjectRequestStatus): string {
  const colors: Record<DataSubjectRequestStatus, string> = {
    [DataSubjectRequestStatus.PENDING]: 'yellow',
    [DataSubjectRequestStatus.IN_PROGRESS]: 'blue',
    [DataSubjectRequestStatus.COMPLETED]: 'green',
    [DataSubjectRequestStatus.REJECTED]: 'red',
    [DataSubjectRequestStatus.CANCELLED]: 'gray',
  };
  return colors[status] || 'gray';
}

export function getDataClassificationColor(classification: DataClassification): string {
  const colors: Record<DataClassification, string> = {
    [DataClassification.PUBLIC]: 'green',
    [DataClassification.INTERNAL]: 'blue',
    [DataClassification.CONFIDENTIAL]: 'yellow',
    [DataClassification.RESTRICTED]: 'orange',
    [DataClassification.PII]: 'red',
    [DataClassification.SENSITIVE]: 'purple',
  };
  return colors[classification] || 'gray';
}

export function getBreachSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    low: 'yellow',
    medium: 'orange',
    high: 'red',
    critical: 'purple',
  };
  return colors[severity] || 'gray';
}

export function calculateDSRDeadline(createdAt: string, extended: boolean = false): Date {
  const created = new Date(createdAt);
  const days = extended ? GDPR_EXTENSION_DAYS : GDPR_RESPONSE_DAYS;
  return new Date(created.getTime() + days * 24 * 60 * 60 * 1000);
}

export function isDSROverdue(request: DataSubjectRequest): boolean {
  if (
    request.status === DataSubjectRequestStatus.COMPLETED ||
    request.status === DataSubjectRequestStatus.REJECTED
  ) {
    return false;
  }
  return new Date() > new Date(request.response_deadline);
}

export function getDaysUntilDSRDeadline(request: DataSubjectRequest): number {
  const deadline = new Date(request.response_deadline);
  const now = new Date();
  const diffMs = deadline.getTime() - now.getTime();
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
}

export function formatRetentionPeriod(days: number): string {
  if (days >= 365) {
    const years = Math.floor(days / 365);
    return years === 1 ? '1 year' : `${years} years`;
  }
  if (days >= 30) {
    const months = Math.floor(days / 30);
    return months === 1 ? '1 month' : `${months} months`;
  }
  return days === 1 ? '1 day' : `${days} days`;
}

export function formatComplianceScore(score: number): { label: string; color: string } {
  if (score >= 90) return { label: 'Excellent', color: 'green' };
  if (score >= 70) return { label: 'Good', color: 'blue' };
  if (score >= 50) return { label: 'Fair', color: 'yellow' };
  if (score >= 30) return { label: 'Poor', color: 'orange' };
  return { label: 'Critical', color: 'red' };
}

export function getConsentCoverageSummary(preferences: ConsentPreferences): string {
  const total = 4; // marketing, analytics, third_party, personalization
  let granted = 0;
  if (preferences.marketing === ConsentStatus.GRANTED) granted++;
  if (preferences.analytics === ConsentStatus.GRANTED) granted++;
  if (preferences.third_party === ConsentStatus.GRANTED) granted++;
  if (preferences.personalization === ConsentStatus.GRANTED) granted++;
  return `${granted} of ${total} consents granted`;
}

export function needsReConsent(
  currentVersion: string,
  acceptedVersion?: string
): boolean {
  if (!acceptedVersion) return true;
  // Simple version comparison - in production use semver
  return currentVersion !== acceptedVersion;
}
