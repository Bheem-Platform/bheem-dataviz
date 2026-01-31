/**
 * Two-Factor Authentication Types
 *
 * TypeScript types for TOTP, SMS, email verification, backup codes,
 * trusted devices, and recovery options.
 */

// Enums

export enum MFAMethod {
  TOTP = 'totp',
  SMS = 'sms',
  EMAIL = 'email',
  HARDWARE_KEY = 'hardware_key',
  PUSH = 'push',
}

export enum MFAStatus {
  NOT_CONFIGURED = 'not_configured',
  PENDING_VERIFICATION = 'pending_verification',
  ACTIVE = 'active',
  DISABLED = 'disabled',
}

export enum VerificationStatus {
  PENDING = 'pending',
  VERIFIED = 'verified',
  EXPIRED = 'expired',
  FAILED = 'failed',
}

export enum TrustLevel {
  UNTRUSTED = 'untrusted',
  TRUSTED = 'trusted',
  REMEMBERED = 'remembered',
}

export enum RecoveryMethod {
  BACKUP_CODE = 'backup_code',
  EMAIL = 'email',
  ADMIN_RESET = 'admin_reset',
  SECURITY_QUESTIONS = 'security_questions',
}

// TOTP Interfaces

export interface TOTPSetupRequest {
  method: MFAMethod;
}

export interface TOTPSetupResponse {
  secret: string;
  qr_code_url: string;
  qr_code_uri: string;
  backup_codes: string[];
  expires_at: string;
  setup_token: string;
}

export interface TOTPVerifyRequest {
  setup_token: string;
  code: string;
}

export interface TOTPConfig {
  user_id: string;
  status: MFAStatus;
  secret_encrypted?: string;
  algorithm: string;
  digits: number;
  period: number;
  issuer: string;
  created_at?: string;
  last_used_at?: string;
  verified_at?: string;
}

// SMS MFA Interfaces

export interface SMSSetupRequest {
  phone_number: string;
}

export interface SMSSetupResponse {
  phone_number_masked: string;
  verification_sent: boolean;
  expires_at: string;
  setup_token: string;
}

export interface SMSVerifyRequest {
  setup_token: string;
  code: string;
}

export interface SMSConfig {
  user_id: string;
  status: MFAStatus;
  phone_number_encrypted?: string;
  phone_number_masked?: string;
  country_code?: string;
  created_at?: string;
  last_used_at?: string;
  verified_at?: string;
}

// Email MFA Interfaces

export interface EmailMFASetupRequest {
  email?: string;
}

export interface EmailMFASetupResponse {
  email_masked: string;
  verification_sent: boolean;
  expires_at: string;
  setup_token: string;
}

export interface EmailMFAVerifyRequest {
  setup_token: string;
  code: string;
}

export interface EmailMFAConfig {
  user_id: string;
  status: MFAStatus;
  email?: string;
  email_masked?: string;
  created_at?: string;
  last_used_at?: string;
  verified_at?: string;
}

// Hardware Key (WebAuthn) Interfaces

export interface WebAuthnRegistrationOptions {
  challenge: string;
  rp_id: string;
  rp_name: string;
  user_id: string;
  user_name: string;
  user_display_name: string;
  attestation: string;
  authenticator_selection: Record<string, unknown>;
  timeout: number;
  exclude_credentials: Array<Record<string, unknown>>;
}

export interface WebAuthnRegistrationResponse {
  credential_id: string;
  client_data_json: string;
  attestation_object: string;
  transports: string[];
}

export interface WebAuthnCredential {
  id: string;
  user_id: string;
  credential_id: string;
  public_key: string;
  sign_count: number;
  transports: string[];
  name: string;
  created_at: string;
  last_used_at?: string;
}

export interface WebAuthnAuthenticationOptions {
  challenge: string;
  timeout: number;
  rp_id: string;
  allow_credentials: Array<Record<string, unknown>>;
  user_verification: string;
}

export interface WebAuthnAuthenticationResponse {
  credential_id: string;
  client_data_json: string;
  authenticator_data: string;
  signature: string;
  user_handle?: string;
}

// Backup Codes Interfaces

export interface BackupCodesConfig {
  user_id: string;
  codes_total: number;
  codes_remaining: number;
  codes_hashed: string[];
  generated_at: string;
  last_used_at?: string;
}

export interface BackupCodesResponse {
  codes: string[];
  codes_total: number;
  generated_at: string;
  warning: string;
}

export interface BackupCodeVerifyRequest {
  code: string;
}

// Trusted Device Interfaces

export interface TrustedDevice {
  id: string;
  user_id: string;
  device_id: string;
  name: string;
  device_type: string;
  browser?: string;
  os?: string;
  ip_address?: string;
  location?: string;
  trust_level: TrustLevel;
  trusted_until?: string;
  created_at: string;
  last_used_at?: string;
}

export interface TrustDeviceRequest {
  device_id: string;
  name?: string;
  trust_duration_days?: number;
}

export interface TrustedDeviceListResponse {
  devices: TrustedDevice[];
  total: number;
}

// MFA Challenge Interfaces

export interface MFAChallenge {
  challenge_id: string;
  user_id: string;
  available_methods: MFAMethod[];
  preferred_method: MFAMethod;
  challenge_token: string;
  expires_at: string;
  attempts_remaining: number;
  device_info: Record<string, unknown>;
}

export interface MFAChallengeResponse {
  challenge_id: string;
  method: MFAMethod;
  code?: string;
  webauthn_response?: WebAuthnAuthenticationResponse;
  trust_device: boolean;
  trust_duration_days?: number;
}

export interface MFAVerificationResult {
  success: boolean;
  method: MFAMethod;
  device_trusted: boolean;
  error_message?: string;
  attempts_remaining?: number;
}

// Recovery Interfaces

export interface RecoveryRequest {
  user_id: string;
  method: RecoveryMethod;
  email?: string;
  backup_code?: string;
  security_answers?: Record<string, string>;
}

export interface RecoveryToken {
  id: string;
  user_id: string;
  token_hash: string;
  method: RecoveryMethod;
  expires_at: string;
  used_at?: string;
  created_at: string;
}

export interface RecoveryResponse {
  success: boolean;
  message: string;
  recovery_token?: string;
  next_step?: string;
}

// User MFA Configuration Interfaces

export interface UserMFAConfig {
  user_id: string;
  mfa_enabled: boolean;
  mfa_enforced: boolean;
  primary_method?: MFAMethod;
  totp?: TOTPConfig;
  sms?: SMSConfig;
  email?: EmailMFAConfig;
  hardware_keys: WebAuthnCredential[];
  backup_codes?: BackupCodesConfig;
  trusted_devices: TrustedDevice[];
  recovery_email?: string;
  last_mfa_at?: string;
  created_at: string;
  updated_at: string;
}

export interface UserMFAConfigUpdate {
  primary_method?: MFAMethod;
  recovery_email?: string;
}

// Organization MFA Policy Interfaces

export interface MFAPolicy {
  organization_id: string;
  mfa_required: boolean;
  allowed_methods: MFAMethod[];
  require_backup_codes: boolean;
  max_trusted_devices: number;
  trust_device_max_days: number;
  grace_period_days: number;
  enforce_for_admins: boolean;
  enforce_for_api_access: boolean;
  remember_device_option: boolean;
  bypass_for_internal_ips: boolean;
  internal_ip_ranges: string[];
}

export interface MFAPolicyUpdate {
  mfa_required?: boolean;
  allowed_methods?: MFAMethod[];
  require_backup_codes?: boolean;
  max_trusted_devices?: number;
  trust_device_max_days?: number;
  grace_period_days?: number;
  enforce_for_admins?: boolean;
  enforce_for_api_access?: boolean;
  remember_device_option?: boolean;
  bypass_for_internal_ips?: boolean;
  internal_ip_ranges?: string[];
}

// MFA Event Interfaces

export interface MFAEvent {
  id: string;
  user_id: string;
  event_type: string;
  method?: MFAMethod;
  success: boolean;
  ip_address?: string;
  user_agent?: string;
  device_id?: string;
  details: Record<string, unknown>;
  created_at: string;
}

export interface MFAEventListResponse {
  events: MFAEvent[];
  total: number;
}

// MFA Status Response

export interface MFAStatusResponse {
  mfa_enabled: boolean;
  mfa_enforced: boolean;
  methods_configured: MFAMethod[];
  primary_method?: MFAMethod;
  backup_codes_remaining: number;
  trusted_devices_count: number;
  grace_period_ends_at?: string;
}

// Constants

export const MFA_CODE_LENGTH = 6;
export const MFA_CODE_EXPIRY_MINUTES = 10;
export const BACKUP_CODE_LENGTH = 8;
export const BACKUP_CODE_COUNT = 10;
export const TOTP_SETUP_EXPIRY_MINUTES = 15;
export const TRUSTED_DEVICE_DEFAULT_DAYS = 30;
export const MAX_MFA_ATTEMPTS = 3;

export const MFA_METHOD_LABELS: Record<MFAMethod, string> = {
  [MFAMethod.TOTP]: 'Authenticator App',
  [MFAMethod.SMS]: 'SMS',
  [MFAMethod.EMAIL]: 'Email',
  [MFAMethod.HARDWARE_KEY]: 'Security Key',
  [MFAMethod.PUSH]: 'Push Notification',
};

export const MFA_STATUS_LABELS: Record<MFAStatus, string> = {
  [MFAStatus.NOT_CONFIGURED]: 'Not Configured',
  [MFAStatus.PENDING_VERIFICATION]: 'Pending Verification',
  [MFAStatus.ACTIVE]: 'Active',
  [MFAStatus.DISABLED]: 'Disabled',
};

export const TRUST_LEVEL_LABELS: Record<TrustLevel, string> = {
  [TrustLevel.UNTRUSTED]: 'Untrusted',
  [TrustLevel.TRUSTED]: 'Trusted',
  [TrustLevel.REMEMBERED]: 'Remembered',
};

export const RECOVERY_METHOD_LABELS: Record<RecoveryMethod, string> = {
  [RecoveryMethod.BACKUP_CODE]: 'Backup Code',
  [RecoveryMethod.EMAIL]: 'Email',
  [RecoveryMethod.ADMIN_RESET]: 'Admin Reset',
  [RecoveryMethod.SECURITY_QUESTIONS]: 'Security Questions',
};

// Helper Functions

export function getMFAMethodIcon(method: MFAMethod): string {
  const icons: Record<MFAMethod, string> = {
    [MFAMethod.TOTP]: 'smartphone',
    [MFAMethod.SMS]: 'message-square',
    [MFAMethod.EMAIL]: 'mail',
    [MFAMethod.HARDWARE_KEY]: 'key',
    [MFAMethod.PUSH]: 'bell',
  };
  return icons[method] || 'shield';
}

export function getMFAStatusColor(status: MFAStatus): string {
  const colors: Record<MFAStatus, string> = {
    [MFAStatus.NOT_CONFIGURED]: 'gray',
    [MFAStatus.PENDING_VERIFICATION]: 'yellow',
    [MFAStatus.ACTIVE]: 'green',
    [MFAStatus.DISABLED]: 'red',
  };
  return colors[status] || 'gray';
}

export function getTrustLevelColor(level: TrustLevel): string {
  const colors: Record<TrustLevel, string> = {
    [TrustLevel.UNTRUSTED]: 'red',
    [TrustLevel.TRUSTED]: 'green',
    [TrustLevel.REMEMBERED]: 'blue',
  };
  return colors[level] || 'gray';
}

export function maskEmail(email: string): string {
  if (!email.includes('@')) return '***';
  const [local, domain] = email.split('@');
  if (local.length <= 2) return `${local[0]}***@${domain}`;
  return `${local[0]}***${local[local.length - 1]}@${domain}`;
}

export function maskPhone(phone: string): string {
  if (phone.length < 4) return '***';
  return `${phone.slice(0, 3)}***${phone.slice(-3)}`;
}

export function formatDeviceInfo(device: TrustedDevice): string {
  const parts: string[] = [];
  if (device.browser) parts.push(device.browser);
  if (device.os) parts.push(`on ${device.os}`);
  if (device.location) parts.push(`from ${device.location}`);
  return parts.join(' ') || device.device_type;
}

export function isDeviceTrustExpired(device: TrustedDevice): boolean {
  if (!device.trusted_until) return false;
  return new Date(device.trusted_until) < new Date();
}

export function getDaysUntilExpiry(expiryDate: string): number {
  const expiry = new Date(expiryDate);
  const now = new Date();
  const diffMs = expiry.getTime() - now.getTime();
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
}

export function formatBackupCodeRemaining(remaining: number, total: number): string {
  if (remaining === 0) return 'No backup codes remaining';
  if (remaining === 1) return '1 backup code remaining';
  return `${remaining} of ${total} backup codes remaining`;
}

export function getBackupCodeWarningLevel(remaining: number): 'ok' | 'warning' | 'critical' {
  if (remaining <= 1) return 'critical';
  if (remaining <= 3) return 'warning';
  return 'ok';
}

export function formatMFAEventType(eventType: string): string {
  const types: Record<string, string> = {
    setup: 'Setup',
    verify: 'Verification',
    disable: 'Disabled',
    recovery: 'Recovery',
    device_trust: 'Device Trusted',
    device_revoke: 'Device Revoked',
    backup_code_used: 'Backup Code Used',
    challenge_created: 'Challenge Created',
    challenge_verified: 'Challenge Verified',
    challenge_failed: 'Challenge Failed',
  };
  return types[eventType] || eventType;
}

export function getMFASecurityScore(config: UserMFAConfig): number {
  let score = 0;

  // Base MFA enabled
  if (config.mfa_enabled) score += 30;

  // TOTP is most secure
  if (config.totp?.status === MFAStatus.ACTIVE) score += 25;

  // Hardware key is very secure
  if (config.hardware_keys.length > 0) score += 25;

  // Backup codes available
  if (config.backup_codes && config.backup_codes.codes_remaining > 0) score += 10;

  // Recovery email set
  if (config.recovery_email) score += 5;

  // Multiple methods configured
  const methodsActive = [
    config.totp?.status === MFAStatus.ACTIVE,
    config.sms?.status === MFAStatus.ACTIVE,
    config.email?.status === MFAStatus.ACTIVE,
    config.hardware_keys.length > 0,
  ].filter(Boolean).length;

  if (methodsActive >= 2) score += 5;

  return Math.min(score, 100);
}

export function getSecurityScoreLabel(score: number): string {
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Fair';
  if (score >= 20) return 'Weak';
  return 'Not Configured';
}

export function getSecurityScoreColor(score: number): string {
  if (score >= 80) return 'green';
  if (score >= 60) return 'blue';
  if (score >= 40) return 'yellow';
  if (score >= 20) return 'orange';
  return 'red';
}
