/**
 * Billing & Usage Quotas Types
 *
 * TypeScript types for subscriptions, billing, invoices, payment methods,
 * usage tracking, and quota management.
 */

// Enums

export enum SubscriptionStatus {
  ACTIVE = 'active',
  TRIALING = 'trialing',
  PAST_DUE = 'past_due',
  CANCELED = 'canceled',
  UNPAID = 'unpaid',
  PAUSED = 'paused',
  INCOMPLETE = 'incomplete',
}

export enum BillingInterval {
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  YEARLY = 'yearly',
}

export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  SUCCEEDED = 'succeeded',
  FAILED = 'failed',
  REFUNDED = 'refunded',
  PARTIALLY_REFUNDED = 'partially_refunded',
  CANCELED = 'canceled',
}

export enum InvoiceStatus {
  DRAFT = 'draft',
  OPEN = 'open',
  PAID = 'paid',
  VOID = 'void',
  UNCOLLECTIBLE = 'uncollectible',
}

export enum PaymentMethodType {
  CARD = 'card',
  BANK_TRANSFER = 'bank_transfer',
  PAYPAL = 'paypal',
  INVOICE = 'invoice',
}

export enum UsageMetricType {
  API_CALLS = 'api_calls',
  STORAGE_MB = 'storage_mb',
  QUERY_MINUTES = 'query_minutes',
  DASHBOARD_VIEWS = 'dashboard_views',
  EXPORT_COUNT = 'export_count',
  MEMBER_COUNT = 'member_count',
  CONNECTION_COUNT = 'connection_count',
  SCHEDULED_REPORTS = 'scheduled_reports',
}

export enum CreditType {
  PROMOTIONAL = 'promotional',
  REFERRAL = 'referral',
  COMPENSATION = 'compensation',
  PREPAID = 'prepaid',
}

// Plan Interfaces

export interface PlanFeature {
  code: string;
  name: string;
  description?: string;
  included: boolean;
  limit?: number;
  unit?: string;
}

export interface Plan {
  id: string;
  name: string;
  description?: string;
  tier: number;
  price_monthly: number;
  price_yearly: number;
  currency: string;
  features: PlanFeature[];
  limits: Record<string, number>;
  is_public: boolean;
  is_popular: boolean;
  trial_days: number;
  metadata: Record<string, unknown>;
}

export interface PlanComparison {
  plans: Plan[];
  feature_categories: Array<{
    name: string;
    features: string[];
  }>;
}

// Subscription Interfaces

export interface SubscriptionCreate {
  workspace_id: string;
  plan_id: string;
  billing_interval?: BillingInterval;
  payment_method_id?: string;
  coupon_code?: string;
  trial_days?: number;
}

export interface Subscription {
  id: string;
  workspace_id: string;
  plan_id: string;
  plan_name: string;
  status: SubscriptionStatus;
  billing_interval: BillingInterval;
  current_period_start: string;
  current_period_end: string;
  trial_start?: string;
  trial_end?: string;
  canceled_at?: string;
  cancel_at_period_end: boolean;
  payment_method_id?: string;
  quantity: number;
  unit_amount: number;
  currency: string;
  discount_percent: number;
  coupon_code?: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionUpdate {
  plan_id?: string;
  billing_interval?: BillingInterval;
  payment_method_id?: string;
  quantity?: number;
  coupon_code?: string;
  cancel_at_period_end?: boolean;
}

export interface SubscriptionUsage {
  subscription_id: string;
  period_start: string;
  period_end: string;
  metrics: Record<string, {
    used: number;
    limit: number;
    percent: number;
  }>;
}

export interface SubscriptionPreview {
  current_plan: Plan;
  new_plan: Plan;
  proration_amount: number;
  new_amount: number;
  currency: string;
  effective_date: string;
  credit_applied: number;
}

// Invoice Interfaces

export interface InvoiceLineItem {
  id: string;
  description: string;
  quantity: number;
  unit_amount: number;
  amount: number;
  currency: string;
  period_start?: string;
  period_end?: string;
  metadata: Record<string, unknown>;
}

export interface Invoice {
  id: string;
  number: string;
  workspace_id: string;
  subscription_id?: string;
  status: InvoiceStatus;
  currency: string;
  subtotal: number;
  tax: number;
  tax_percent: number;
  discount: number;
  total: number;
  amount_paid: number;
  amount_due: number;
  line_items: InvoiceLineItem[];
  period_start?: string;
  period_end?: string;
  due_date?: string;
  paid_at?: string;
  pdf_url?: string;
  hosted_invoice_url?: string;
  billing_reason?: string;
  notes?: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface InvoiceListResponse {
  invoices: Invoice[];
  total: number;
}

// Payment Interfaces

export interface PaymentMethodCreate {
  type: PaymentMethodType;
  is_default?: boolean;
  card_number?: string;
  card_exp_month?: number;
  card_exp_year?: number;
  card_cvc?: string;
  billing_name?: string;
  billing_email?: string;
  billing_address?: Record<string, string>;
}

export interface PaymentMethod {
  id: string;
  workspace_id: string;
  type: PaymentMethodType;
  is_default: boolean;
  card_brand?: string;
  card_last4?: string;
  card_exp_month?: number;
  card_exp_year?: number;
  billing_name?: string;
  billing_email?: string;
  billing_address?: Record<string, string>;
  created_at: string;
}

export interface Payment {
  id: string;
  workspace_id: string;
  invoice_id?: string;
  subscription_id?: string;
  payment_method_id?: string;
  status: PaymentStatus;
  amount: number;
  currency: string;
  description?: string;
  failure_reason?: string;
  refund_amount: number;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface PaymentListResponse {
  payments: Payment[];
  total: number;
}

// Usage Interfaces

export interface UsageRecord {
  id: string;
  workspace_id: string;
  subscription_id?: string;
  metric_type: UsageMetricType;
  quantity: number;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface UsageSummary {
  workspace_id: string;
  period_start: string;
  period_end: string;
  metrics: Record<string, {
    total: number;
    limit: number;
    percent: number;
    daily_breakdown: Record<string, number>;
  }>;
}

export interface UsageAlert {
  id: string;
  workspace_id: string;
  metric_type: UsageMetricType;
  threshold_percent: number;
  notification_channels: string[];
  is_enabled: boolean;
  last_triggered_at?: string;
  created_at: string;
}

export interface UsageAlertCreate {
  metric_type: UsageMetricType;
  threshold_percent: number;
  notification_channels?: string[];
}

// Credit Interfaces

export interface Credit {
  id: string;
  workspace_id: string;
  type: CreditType;
  amount: number;
  currency: string;
  remaining: number;
  description?: string;
  expires_at?: string;
  created_at: string;
}

export interface CreditApplication {
  id: string;
  credit_id: string;
  invoice_id: string;
  amount: number;
  applied_at: string;
}

export interface CreditBalance {
  workspace_id: string;
  total_credits: number;
  available_credits: number;
  expiring_soon: number;
  currency: string;
  credits: Credit[];
}

// Coupon Interfaces

export interface Coupon {
  id: string;
  code: string;
  name: string;
  description?: string;
  discount_type: string;
  discount_value: number;
  currency: string;
  duration: string;
  duration_months?: number;
  max_redemptions?: number;
  redemption_count: number;
  applies_to_plans: string[];
  valid_from?: string;
  valid_until?: string;
  is_active: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface CouponValidation {
  valid: boolean;
  coupon?: Coupon;
  error_message?: string;
  discount_amount?: number;
}

// Billing Settings Interfaces

export interface BillingSettings {
  workspace_id: string;
  billing_email?: string;
  billing_name?: string;
  billing_address?: Record<string, string>;
  tax_id?: string;
  tax_id_type?: string;
  auto_collection: boolean;
  invoice_prefix?: string;
  default_payment_method_id?: string;
  metadata: Record<string, unknown>;
}

export interface BillingSettingsUpdate {
  billing_email?: string;
  billing_name?: string;
  billing_address?: Record<string, string>;
  tax_id?: string;
  tax_id_type?: string;
  auto_collection?: boolean;
  invoice_prefix?: string;
  default_payment_method_id?: string;
}

// Billing Portal

export interface BillingPortalSession {
  url: string;
  expires_at: string;
}

// Overview Interface

export interface BillingOverview {
  workspace_id: string;
  subscription?: Subscription;
  current_plan?: Plan;
  usage_summary?: UsageSummary;
  credit_balance?: CreditBalance;
  upcoming_invoice?: Invoice;
  payment_methods: PaymentMethod[];
  recent_invoices: Invoice[];
}

// Constants

export const SUBSCRIPTION_STATUS_LABELS: Record<SubscriptionStatus, string> = {
  [SubscriptionStatus.ACTIVE]: 'Active',
  [SubscriptionStatus.TRIALING]: 'Trial',
  [SubscriptionStatus.PAST_DUE]: 'Past Due',
  [SubscriptionStatus.CANCELED]: 'Canceled',
  [SubscriptionStatus.UNPAID]: 'Unpaid',
  [SubscriptionStatus.PAUSED]: 'Paused',
  [SubscriptionStatus.INCOMPLETE]: 'Incomplete',
};

export const BILLING_INTERVAL_LABELS: Record<BillingInterval, string> = {
  [BillingInterval.MONTHLY]: 'Monthly',
  [BillingInterval.QUARTERLY]: 'Quarterly',
  [BillingInterval.YEARLY]: 'Yearly',
};

export const PAYMENT_STATUS_LABELS: Record<PaymentStatus, string> = {
  [PaymentStatus.PENDING]: 'Pending',
  [PaymentStatus.PROCESSING]: 'Processing',
  [PaymentStatus.SUCCEEDED]: 'Succeeded',
  [PaymentStatus.FAILED]: 'Failed',
  [PaymentStatus.REFUNDED]: 'Refunded',
  [PaymentStatus.PARTIALLY_REFUNDED]: 'Partially Refunded',
  [PaymentStatus.CANCELED]: 'Canceled',
};

export const INVOICE_STATUS_LABELS: Record<InvoiceStatus, string> = {
  [InvoiceStatus.DRAFT]: 'Draft',
  [InvoiceStatus.OPEN]: 'Open',
  [InvoiceStatus.PAID]: 'Paid',
  [InvoiceStatus.VOID]: 'Void',
  [InvoiceStatus.UNCOLLECTIBLE]: 'Uncollectible',
};

export const PAYMENT_METHOD_LABELS: Record<PaymentMethodType, string> = {
  [PaymentMethodType.CARD]: 'Credit Card',
  [PaymentMethodType.BANK_TRANSFER]: 'Bank Transfer',
  [PaymentMethodType.PAYPAL]: 'PayPal',
  [PaymentMethodType.INVOICE]: 'Invoice',
};

export const USAGE_METRIC_LABELS: Record<UsageMetricType, string> = {
  [UsageMetricType.API_CALLS]: 'API Calls',
  [UsageMetricType.STORAGE_MB]: 'Storage (MB)',
  [UsageMetricType.QUERY_MINUTES]: 'Query Minutes',
  [UsageMetricType.DASHBOARD_VIEWS]: 'Dashboard Views',
  [UsageMetricType.EXPORT_COUNT]: 'Exports',
  [UsageMetricType.MEMBER_COUNT]: 'Team Members',
  [UsageMetricType.CONNECTION_COUNT]: 'Connections',
  [UsageMetricType.SCHEDULED_REPORTS]: 'Scheduled Reports',
};

export const CREDIT_TYPE_LABELS: Record<CreditType, string> = {
  [CreditType.PROMOTIONAL]: 'Promotional',
  [CreditType.REFERRAL]: 'Referral',
  [CreditType.COMPENSATION]: 'Compensation',
  [CreditType.PREPAID]: 'Prepaid',
};

// Helper Functions

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

export function formatPrice(plan: Plan, interval: BillingInterval): string {
  const price = interval === BillingInterval.YEARLY ? plan.price_yearly : plan.price_monthly;
  if (price === 0 && plan.tier === 0) return 'Free';
  if (price === 0 && plan.tier > 3) return 'Contact Us';
  return formatCurrency(price);
}

export function getYearlySavings(plan: Plan): number {
  const monthly_total = plan.price_monthly * 12;
  const yearly_price = plan.price_yearly;
  return monthly_total - yearly_price;
}

export function getYearlySavingsPercent(plan: Plan): number {
  const savings = getYearlySavings(plan);
  const monthly_total = plan.price_monthly * 12;
  if (monthly_total === 0) return 0;
  return Math.round((savings / monthly_total) * 100);
}

export function getSubscriptionStatusColor(status: SubscriptionStatus): string {
  const colors: Record<SubscriptionStatus, string> = {
    [SubscriptionStatus.ACTIVE]: 'green',
    [SubscriptionStatus.TRIALING]: 'blue',
    [SubscriptionStatus.PAST_DUE]: 'orange',
    [SubscriptionStatus.CANCELED]: 'gray',
    [SubscriptionStatus.UNPAID]: 'red',
    [SubscriptionStatus.PAUSED]: 'yellow',
    [SubscriptionStatus.INCOMPLETE]: 'gray',
  };
  return colors[status] || 'gray';
}

export function getInvoiceStatusColor(status: InvoiceStatus): string {
  const colors: Record<InvoiceStatus, string> = {
    [InvoiceStatus.DRAFT]: 'gray',
    [InvoiceStatus.OPEN]: 'blue',
    [InvoiceStatus.PAID]: 'green',
    [InvoiceStatus.VOID]: 'gray',
    [InvoiceStatus.UNCOLLECTIBLE]: 'red',
  };
  return colors[status] || 'gray';
}

export function getPaymentStatusColor(status: PaymentStatus): string {
  const colors: Record<PaymentStatus, string> = {
    [PaymentStatus.PENDING]: 'yellow',
    [PaymentStatus.PROCESSING]: 'blue',
    [PaymentStatus.SUCCEEDED]: 'green',
    [PaymentStatus.FAILED]: 'red',
    [PaymentStatus.REFUNDED]: 'gray',
    [PaymentStatus.PARTIALLY_REFUNDED]: 'orange',
    [PaymentStatus.CANCELED]: 'gray',
  };
  return colors[status] || 'gray';
}

export function getUsagePercent(used: number, limit: number): number {
  if (limit === -1) return 0; // Unlimited
  if (limit === 0) return used > 0 ? 100 : 0;
  return Math.min(100, Math.round((used / limit) * 100));
}

export function getUsageStatus(percent: number): 'ok' | 'warning' | 'critical' {
  if (percent >= 100) return 'critical';
  if (percent >= 80) return 'warning';
  return 'ok';
}

export function formatLimit(limit: number, unit?: string): string {
  if (limit === -1) return 'Unlimited';
  if (unit === 'GB') return `${limit / 1000} GB`;
  return limit.toLocaleString() + (unit ? ` ${unit}` : '');
}

export function getDaysUntilRenewal(subscription: Subscription): number {
  const end = new Date(subscription.current_period_end);
  const now = new Date();
  const diff = end.getTime() - now.getTime();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}

export function isTrialEnding(subscription: Subscription, daysThreshold: number = 3): boolean {
  if (subscription.status !== SubscriptionStatus.TRIALING || !subscription.trial_end) {
    return false;
  }
  const end = new Date(subscription.trial_end);
  const now = new Date();
  const diff = end.getTime() - now.getTime();
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
  return days <= daysThreshold;
}

export function getCardBrandIcon(brand?: string): string {
  const icons: Record<string, string> = {
    visa: '💳',
    mastercard: '💳',
    amex: '💳',
    discover: '💳',
  };
  return icons[brand?.toLowerCase() || ''] || '💳';
}
