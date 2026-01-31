/**
 * Security Audit & Monitoring Types
 *
 * TypeScript types for security auditing, threat detection,
 * anomaly detection, vulnerability management, and incident management.
 */

// Enums

export enum AuditCategory {
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  DATA_ACCESS = 'data_access',
  DATA_MODIFICATION = 'data_modification',
  CONFIGURATION = 'configuration',
  ADMIN_ACTION = 'admin_action',
  SECURITY = 'security',
  SYSTEM = 'system',
}

export enum AuditSeverity {
  DEBUG = 'debug',
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

export enum ThreatType {
  BRUTE_FORCE = 'brute_force',
  CREDENTIAL_STUFFING = 'credential_stuffing',
  SQL_INJECTION = 'sql_injection',
  XSS = 'xss',
  CSRF = 'csrf',
  DDoS = 'ddos',
  DATA_EXFILTRATION = 'data_exfiltration',
  PRIVILEGE_ESCALATION = 'privilege_escalation',
  MALWARE = 'malware',
  PHISHING = 'phishing',
  INSIDER_THREAT = 'insider_threat',
  UNKNOWN = 'unknown',
}

export enum ThreatSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum ThreatStatus {
  DETECTED = 'detected',
  INVESTIGATING = 'investigating',
  CONTAINED = 'contained',
  RESOLVED = 'resolved',
  FALSE_POSITIVE = 'false_positive',
}

export enum IncidentStatus {
  OPEN = 'open',
  INVESTIGATING = 'investigating',
  CONTAINED = 'contained',
  REMEDIATED = 'remediated',
  CLOSED = 'closed',
}

export enum IncidentPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum AnomalyType {
  LOGIN_PATTERN = 'login_pattern',
  ACCESS_PATTERN = 'access_pattern',
  DATA_VOLUME = 'data_volume',
  API_USAGE = 'api_usage',
  GEOGRAPHIC = 'geographic',
  TIME_BASED = 'time_based',
  BEHAVIORAL = 'behavioral',
}

export enum VulnerabilitySeverity {
  NONE = 'none',
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum VulnerabilityStatus {
  OPEN = 'open',
  IN_PROGRESS = 'in_progress',
  REMEDIATED = 'remediated',
  ACCEPTED = 'accepted',
  FALSE_POSITIVE = 'false_positive',
}

// Audit Log Interfaces

export interface AuditLog {
  id: string;
  timestamp: string;
  category: AuditCategory;
  severity: AuditSeverity;
  action: string;
  resource_type: string;
  resource_id?: string;
  user_id?: string;
  user_email?: string;
  organization_id?: string;
  ip_address: string;
  user_agent?: string;
  session_id?: string;
  request_id?: string;
  success: boolean;
  error_code?: string;
  error_message?: string;
  old_value?: Record<string, unknown>;
  new_value?: Record<string, unknown>;
  metadata: Record<string, unknown>;
  geo_location?: Record<string, unknown>;
}

export interface AuditLogCreate {
  category: AuditCategory;
  severity: AuditSeverity;
  action: string;
  resource_type: string;
  resource_id?: string;
  user_id?: string;
  user_email?: string;
  organization_id?: string;
  ip_address: string;
  user_agent?: string;
  session_id?: string;
  success: boolean;
  error_code?: string;
  error_message?: string;
  old_value?: Record<string, unknown>;
  new_value?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface AuditLogListResponse {
  logs: AuditLog[];
  total: number;
}

// Threat Intelligence Interfaces

export interface ThreatIndicator {
  id: string;
  threat_type: ThreatType;
  severity: ThreatSeverity;
  indicator_type: string;
  indicator_value: string;
  description?: string;
  source: string;
  confidence: number;
  first_seen: string;
  last_seen: string;
  times_seen: number;
  tags: string[];
  metadata: Record<string, unknown>;
  active: boolean;
  expires_at?: string;
  created_at: string;
}

export interface ThreatIndicatorCreate {
  threat_type: ThreatType;
  severity: ThreatSeverity;
  indicator_type: string;
  indicator_value: string;
  description?: string;
  source?: string;
  confidence?: number;
  tags?: string[];
  expires_at?: string;
}

export interface ThreatDetection {
  id: string;
  threat_type: ThreatType;
  severity: ThreatSeverity;
  status: ThreatStatus;
  title: string;
  description: string;
  source: string;
  confidence: number;
  affected_resources: string[];
  affected_users: string[];
  indicators: string[];
  ip_addresses: string[];
  user_agents: string[];
  organization_id?: string;
  assigned_to?: string;
  detected_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  resolution_notes?: string;
  related_incidents: string[];
  metadata: Record<string, unknown>;
}

export interface ThreatDetectionListResponse {
  detections: ThreatDetection[];
  total: number;
}

// Anomaly Detection Interfaces

export interface DetectedAnomaly {
  id: string;
  anomaly_type: AnomalyType;
  severity: ThreatSeverity;
  user_id?: string;
  organization_id?: string;
  description: string;
  expected_value?: string;
  actual_value: string;
  deviation_score: number;
  confidence: number;
  ip_address?: string;
  related_events: string[];
  investigated: boolean;
  false_positive: boolean;
  created_at: string;
  investigated_at?: string;
  investigated_by?: string;
}

export interface AnomalyListResponse {
  anomalies: DetectedAnomaly[];
  total: number;
}

// Security Incident Interfaces

export interface SecurityIncident {
  id: string;
  title: string;
  description: string;
  incident_type: ThreatType;
  status: IncidentStatus;
  priority: IncidentPriority;
  severity: ThreatSeverity;
  organization_id: string;
  reported_by: string;
  assigned_to?: string;
  affected_systems: string[];
  affected_users: string[];
  affected_data: string[];
  attack_vectors: string[];
  indicators_of_compromise: string[];
  related_threats: string[];
  timeline: Array<Record<string, unknown>>;
  containment_actions: string[];
  remediation_actions: string[];
  lessons_learned?: string;
  post_mortem_url?: string;
  created_at: string;
  updated_at: string;
  contained_at?: string;
  resolved_at?: string;
  closed_at?: string;
}

export interface SecurityIncidentCreate {
  title: string;
  description: string;
  incident_type: ThreatType;
  priority: IncidentPriority;
  severity: ThreatSeverity;
  organization_id: string;
  affected_systems?: string[];
  affected_users?: string[];
  attack_vectors?: string[];
}

export interface SecurityIncidentUpdate {
  title?: string;
  description?: string;
  status?: IncidentStatus;
  priority?: IncidentPriority;
  assigned_to?: string;
  affected_systems?: string[];
  affected_users?: string[];
  containment_actions?: string[];
  remediation_actions?: string[];
  lessons_learned?: string;
}

export interface SecurityIncidentListResponse {
  incidents: SecurityIncident[];
  total: number;
}

// Vulnerability Interfaces

export interface Vulnerability {
  id: string;
  cve_id?: string;
  title: string;
  description: string;
  severity: VulnerabilitySeverity;
  cvss_score?: number;
  cvss_vector?: string;
  status: VulnerabilityStatus;
  affected_component: string;
  affected_versions: string[];
  organization_id?: string;
  discovered_at: string;
  discovered_by: string;
  assigned_to?: string;
  due_date?: string;
  remediation_steps: string[];
  workaround?: string;
  references: string[];
  exploitability: string;
  patch_available: boolean;
  patch_version?: string;
  verified_at?: string;
  remediated_at?: string;
  created_at: string;
  updated_at: string;
}

export interface VulnerabilityCreate {
  cve_id?: string;
  title: string;
  description: string;
  severity: VulnerabilitySeverity;
  cvss_score?: number;
  affected_component: string;
  affected_versions?: string[];
  organization_id?: string;
  discovered_by: string;
  remediation_steps?: string[];
  references?: string[];
}

export interface VulnerabilityUpdate {
  status?: VulnerabilityStatus;
  assigned_to?: string;
  due_date?: string;
  remediation_steps?: string[];
  workaround?: string;
  patch_available?: boolean;
  patch_version?: string;
}

export interface VulnerabilityListResponse {
  vulnerabilities: Vulnerability[];
  total: number;
}

// Security Metrics Interfaces

export interface SecurityMetrics {
  organization_id: string;
  timestamp: string;
  total_logins_24h: number;
  failed_logins_24h: number;
  unique_users_24h: number;
  mfa_usage_percent: number;
  active_threats: number;
  threats_detected_24h: number;
  threats_resolved_24h: number;
  mean_time_to_detect_hours: number;
  mean_time_to_resolve_hours: number;
  open_incidents: number;
  critical_incidents: number;
  incidents_created_24h: number;
  incidents_resolved_24h: number;
  open_vulnerabilities: number;
  critical_vulnerabilities: number;
  overdue_vulnerabilities: number;
  vulnerabilities_fixed_30d: number;
  anomalies_detected_24h: number;
  false_positive_rate: number;
  audit_log_coverage: number;
  data_classification_coverage: number;
}

export interface SecurityScorecard {
  organization_id: string;
  overall_score: number;
  categories: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  calculated_at: string;
}

// Security Alert Interfaces

export interface SecurityAlert {
  id: string;
  alert_type: string;
  severity: ThreatSeverity;
  title: string;
  message: string;
  source: string;
  organization_id?: string;
  related_entity_type?: string;
  related_entity_id?: string;
  acknowledged: boolean;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved: boolean;
  resolved_at?: string;
  created_at: string;
}

export interface SecurityAlertListResponse {
  alerts: SecurityAlert[];
  total: number;
}

// Constants

export const AUDIT_CATEGORY_LABELS: Record<AuditCategory, string> = {
  [AuditCategory.AUTHENTICATION]: 'Authentication',
  [AuditCategory.AUTHORIZATION]: 'Authorization',
  [AuditCategory.DATA_ACCESS]: 'Data Access',
  [AuditCategory.DATA_MODIFICATION]: 'Data Modification',
  [AuditCategory.CONFIGURATION]: 'Configuration',
  [AuditCategory.ADMIN_ACTION]: 'Admin Action',
  [AuditCategory.SECURITY]: 'Security',
  [AuditCategory.SYSTEM]: 'System',
};

export const AUDIT_SEVERITY_LABELS: Record<AuditSeverity, string> = {
  [AuditSeverity.DEBUG]: 'Debug',
  [AuditSeverity.INFO]: 'Info',
  [AuditSeverity.WARNING]: 'Warning',
  [AuditSeverity.ERROR]: 'Error',
  [AuditSeverity.CRITICAL]: 'Critical',
};

export const THREAT_TYPE_LABELS: Record<ThreatType, string> = {
  [ThreatType.BRUTE_FORCE]: 'Brute Force Attack',
  [ThreatType.CREDENTIAL_STUFFING]: 'Credential Stuffing',
  [ThreatType.SQL_INJECTION]: 'SQL Injection',
  [ThreatType.XSS]: 'Cross-Site Scripting',
  [ThreatType.CSRF]: 'Cross-Site Request Forgery',
  [ThreatType.DDoS]: 'DDoS Attack',
  [ThreatType.DATA_EXFILTRATION]: 'Data Exfiltration',
  [ThreatType.PRIVILEGE_ESCALATION]: 'Privilege Escalation',
  [ThreatType.MALWARE]: 'Malware',
  [ThreatType.PHISHING]: 'Phishing',
  [ThreatType.INSIDER_THREAT]: 'Insider Threat',
  [ThreatType.UNKNOWN]: 'Unknown',
};

export const THREAT_SEVERITY_LABELS: Record<ThreatSeverity, string> = {
  [ThreatSeverity.LOW]: 'Low',
  [ThreatSeverity.MEDIUM]: 'Medium',
  [ThreatSeverity.HIGH]: 'High',
  [ThreatSeverity.CRITICAL]: 'Critical',
};

export const THREAT_STATUS_LABELS: Record<ThreatStatus, string> = {
  [ThreatStatus.DETECTED]: 'Detected',
  [ThreatStatus.INVESTIGATING]: 'Investigating',
  [ThreatStatus.CONTAINED]: 'Contained',
  [ThreatStatus.RESOLVED]: 'Resolved',
  [ThreatStatus.FALSE_POSITIVE]: 'False Positive',
};

export const INCIDENT_STATUS_LABELS: Record<IncidentStatus, string> = {
  [IncidentStatus.OPEN]: 'Open',
  [IncidentStatus.INVESTIGATING]: 'Investigating',
  [IncidentStatus.CONTAINED]: 'Contained',
  [IncidentStatus.REMEDIATED]: 'Remediated',
  [IncidentStatus.CLOSED]: 'Closed',
};

export const INCIDENT_PRIORITY_LABELS: Record<IncidentPriority, string> = {
  [IncidentPriority.LOW]: 'Low',
  [IncidentPriority.MEDIUM]: 'Medium',
  [IncidentPriority.HIGH]: 'High',
  [IncidentPriority.CRITICAL]: 'Critical',
};

export const VULNERABILITY_SEVERITY_LABELS: Record<VulnerabilitySeverity, string> = {
  [VulnerabilitySeverity.NONE]: 'None',
  [VulnerabilitySeverity.LOW]: 'Low',
  [VulnerabilitySeverity.MEDIUM]: 'Medium',
  [VulnerabilitySeverity.HIGH]: 'High',
  [VulnerabilitySeverity.CRITICAL]: 'Critical',
};

export const VULNERABILITY_STATUS_LABELS: Record<VulnerabilityStatus, string> = {
  [VulnerabilityStatus.OPEN]: 'Open',
  [VulnerabilityStatus.IN_PROGRESS]: 'In Progress',
  [VulnerabilityStatus.REMEDIATED]: 'Remediated',
  [VulnerabilityStatus.ACCEPTED]: 'Risk Accepted',
  [VulnerabilityStatus.FALSE_POSITIVE]: 'False Positive',
};

// Helper Functions

export function getAuditSeverityColor(severity: AuditSeverity): string {
  const colors: Record<AuditSeverity, string> = {
    [AuditSeverity.DEBUG]: 'gray',
    [AuditSeverity.INFO]: 'blue',
    [AuditSeverity.WARNING]: 'yellow',
    [AuditSeverity.ERROR]: 'orange',
    [AuditSeverity.CRITICAL]: 'red',
  };
  return colors[severity] || 'gray';
}

export function getThreatSeverityColor(severity: ThreatSeverity): string {
  const colors: Record<ThreatSeverity, string> = {
    [ThreatSeverity.LOW]: 'blue',
    [ThreatSeverity.MEDIUM]: 'yellow',
    [ThreatSeverity.HIGH]: 'orange',
    [ThreatSeverity.CRITICAL]: 'red',
  };
  return colors[severity] || 'gray';
}

export function getThreatStatusColor(status: ThreatStatus): string {
  const colors: Record<ThreatStatus, string> = {
    [ThreatStatus.DETECTED]: 'red',
    [ThreatStatus.INVESTIGATING]: 'yellow',
    [ThreatStatus.CONTAINED]: 'blue',
    [ThreatStatus.RESOLVED]: 'green',
    [ThreatStatus.FALSE_POSITIVE]: 'gray',
  };
  return colors[status] || 'gray';
}

export function getIncidentStatusColor(status: IncidentStatus): string {
  const colors: Record<IncidentStatus, string> = {
    [IncidentStatus.OPEN]: 'red',
    [IncidentStatus.INVESTIGATING]: 'yellow',
    [IncidentStatus.CONTAINED]: 'blue',
    [IncidentStatus.REMEDIATED]: 'green',
    [IncidentStatus.CLOSED]: 'gray',
  };
  return colors[status] || 'gray';
}

export function getVulnerabilitySeverityColor(severity: VulnerabilitySeverity): string {
  const colors: Record<VulnerabilitySeverity, string> = {
    [VulnerabilitySeverity.NONE]: 'gray',
    [VulnerabilitySeverity.LOW]: 'blue',
    [VulnerabilitySeverity.MEDIUM]: 'yellow',
    [VulnerabilitySeverity.HIGH]: 'orange',
    [VulnerabilitySeverity.CRITICAL]: 'red',
  };
  return colors[severity] || 'gray';
}

export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

export function formatDeviationScore(score: number): string {
  return `${score.toFixed(1)}σ`;
}

export function getSecurityScoreColor(score: number): string {
  if (score >= 80) return 'green';
  if (score >= 60) return 'blue';
  if (score >= 40) return 'yellow';
  if (score >= 20) return 'orange';
  return 'red';
}

export function getSecurityScoreLabel(score: number): string {
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Fair';
  if (score >= 20) return 'Poor';
  return 'Critical';
}

export function isVulnerabilityOverdue(vulnerability: Vulnerability): boolean {
  if (!vulnerability.due_date) return false;
  if (vulnerability.status === VulnerabilityStatus.REMEDIATED) return false;
  return new Date(vulnerability.due_date) < new Date();
}

export function formatCVSSScore(score?: number): string {
  if (score === undefined || score === null) return 'N/A';
  return score.toFixed(1);
}

export function getCVSSScoreColor(score?: number): string {
  if (score === undefined || score === null) return 'gray';
  if (score >= 9.0) return 'red';
  if (score >= 7.0) return 'orange';
  if (score >= 4.0) return 'yellow';
  if (score > 0) return 'blue';
  return 'gray';
}

export function getIncidentDuration(incident: SecurityIncident): string {
  const start = new Date(incident.created_at);
  const end = incident.closed_at ? new Date(incident.closed_at) : new Date();
  const diffMs = end.getTime() - start.getTime();
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ${hours % 24}h`;
  return `${hours}h`;
}

export function getThreatIcon(type: ThreatType): string {
  const icons: Record<ThreatType, string> = {
    [ThreatType.BRUTE_FORCE]: 'key',
    [ThreatType.CREDENTIAL_STUFFING]: 'users',
    [ThreatType.SQL_INJECTION]: 'database',
    [ThreatType.XSS]: 'code',
    [ThreatType.CSRF]: 'link',
    [ThreatType.DDoS]: 'cloud-off',
    [ThreatType.DATA_EXFILTRATION]: 'download-cloud',
    [ThreatType.PRIVILEGE_ESCALATION]: 'arrow-up',
    [ThreatType.MALWARE]: 'alert-triangle',
    [ThreatType.PHISHING]: 'mail',
    [ThreatType.INSIDER_THREAT]: 'user-x',
    [ThreatType.UNKNOWN]: 'help-circle',
  };
  return icons[type] || 'alert-circle';
}
