"""
Billing & Usage Quotas Schemas

Pydantic schemas for subscriptions, billing, invoices, payment methods,
usage tracking, and quota management.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    PAUSED = "paused"
    INCOMPLETE = "incomplete"


class BillingInterval(str, Enum):
    """Billing interval"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELED = "canceled"


class InvoiceStatus(str, Enum):
    """Invoice status"""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class PaymentMethodType(str, Enum):
    """Payment method types"""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    INVOICE = "invoice"


class UsageMetricType(str, Enum):
    """Types of usage metrics"""
    API_CALLS = "api_calls"
    STORAGE_MB = "storage_mb"
    QUERY_MINUTES = "query_minutes"
    DASHBOARD_VIEWS = "dashboard_views"
    EXPORT_COUNT = "export_count"
    MEMBER_COUNT = "member_count"
    CONNECTION_COUNT = "connection_count"
    SCHEDULED_REPORTS = "scheduled_reports"


class CreditType(str, Enum):
    """Types of credits"""
    PROMOTIONAL = "promotional"
    REFERRAL = "referral"
    COMPENSATION = "compensation"
    PREPAID = "prepaid"


# Plan Models

class PlanFeature(BaseModel):
    """Feature included in a plan"""
    code: str
    name: str
    description: Optional[str] = None
    included: bool = True
    limit: Optional[int] = None  # None = unlimited
    unit: Optional[str] = None


class Plan(BaseModel):
    """Subscription plan"""
    id: str
    name: str
    description: Optional[str] = None
    tier: int  # 0=free, 1=starter, 2=pro, 3=business, 4=enterprise
    price_monthly: float
    price_yearly: float
    currency: str = "USD"
    features: list[PlanFeature] = Field(default_factory=list)
    limits: dict[str, int] = Field(default_factory=dict)
    is_public: bool = True
    is_popular: bool = False
    trial_days: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class PlanComparison(BaseModel):
    """Plan comparison for pricing page"""
    plans: list[Plan]
    feature_categories: list[dict[str, Any]]


# Subscription Models

class SubscriptionCreate(BaseModel):
    """Create subscription"""
    workspace_id: str
    plan_id: str
    billing_interval: BillingInterval = BillingInterval.MONTHLY
    payment_method_id: Optional[str] = None
    coupon_code: Optional[str] = None
    trial_days: Optional[int] = None


class Subscription(BaseModel):
    """Subscription details"""
    id: str
    workspace_id: str
    plan_id: str
    plan_name: str
    status: SubscriptionStatus
    billing_interval: BillingInterval
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    cancel_at_period_end: bool = False
    payment_method_id: Optional[str] = None
    quantity: int = 1
    unit_amount: float
    currency: str = "USD"
    discount_percent: float = 0
    coupon_code: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionUpdate(BaseModel):
    """Update subscription"""
    plan_id: Optional[str] = None
    billing_interval: Optional[BillingInterval] = None
    payment_method_id: Optional[str] = None
    quantity: Optional[int] = None
    coupon_code: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None


class SubscriptionUsage(BaseModel):
    """Subscription usage summary"""
    subscription_id: str
    period_start: datetime
    period_end: datetime
    metrics: dict[str, dict[str, Any]]  # metric -> {used, limit, percent}


# Invoice Models

class InvoiceLineItem(BaseModel):
    """Invoice line item"""
    id: str
    description: str
    quantity: int
    unit_amount: float
    amount: float
    currency: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Invoice(BaseModel):
    """Invoice"""
    id: str
    number: str
    workspace_id: str
    subscription_id: Optional[str] = None
    status: InvoiceStatus
    currency: str = "USD"
    subtotal: float
    tax: float = 0
    tax_percent: float = 0
    discount: float = 0
    total: float
    amount_paid: float = 0
    amount_due: float
    line_items: list[InvoiceLineItem] = Field(default_factory=list)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    pdf_url: Optional[str] = None
    hosted_invoice_url: Optional[str] = None
    billing_reason: Optional[str] = None
    notes: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InvoiceListResponse(BaseModel):
    """List invoices response"""
    invoices: list[Invoice]
    total: int


# Payment Models

class PaymentMethodCreate(BaseModel):
    """Create payment method"""
    type: PaymentMethodType
    is_default: bool = False
    # Card details (if type=card)
    card_number: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    card_cvc: Optional[str] = None
    # Billing details
    billing_name: Optional[str] = None
    billing_email: Optional[str] = None
    billing_address: Optional[dict[str, str]] = None


class PaymentMethod(BaseModel):
    """Payment method"""
    id: str
    workspace_id: str
    type: PaymentMethodType
    is_default: bool
    # Card info (masked)
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    # Billing details
    billing_name: Optional[str] = None
    billing_email: Optional[str] = None
    billing_address: Optional[dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Payment(BaseModel):
    """Payment record"""
    id: str
    workspace_id: str
    invoice_id: Optional[str] = None
    subscription_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    status: PaymentStatus
    amount: float
    currency: str = "USD"
    description: Optional[str] = None
    failure_reason: Optional[str] = None
    refund_amount: float = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentListResponse(BaseModel):
    """List payments response"""
    payments: list[Payment]
    total: int


# Usage Models

class UsageRecord(BaseModel):
    """Usage record"""
    id: str
    workspace_id: str
    subscription_id: Optional[str] = None
    metric_type: UsageMetricType
    quantity: float
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class UsageSummary(BaseModel):
    """Usage summary for a period"""
    workspace_id: str
    period_start: datetime
    period_end: datetime
    metrics: dict[str, dict[str, Any]]  # metric -> {total, limit, percent, daily_breakdown}


class UsageAlert(BaseModel):
    """Usage alert"""
    id: str
    workspace_id: str
    metric_type: UsageMetricType
    threshold_percent: int  # e.g., 80 for 80%
    notification_channels: list[str] = Field(default_factory=list)
    is_enabled: bool = True
    last_triggered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UsageAlertCreate(BaseModel):
    """Create usage alert"""
    metric_type: UsageMetricType
    threshold_percent: int
    notification_channels: list[str] = Field(default_factory=list)


# Credit Models

class Credit(BaseModel):
    """Account credit"""
    id: str
    workspace_id: str
    type: CreditType
    amount: float
    currency: str = "USD"
    remaining: float
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CreditApplication(BaseModel):
    """Credit application to invoice"""
    id: str
    credit_id: str
    invoice_id: str
    amount: float
    applied_at: datetime = Field(default_factory=datetime.utcnow)


class CreditBalance(BaseModel):
    """Credit balance summary"""
    workspace_id: str
    total_credits: float
    available_credits: float
    expiring_soon: float
    currency: str = "USD"
    credits: list[Credit]


# Coupon Models

class Coupon(BaseModel):
    """Discount coupon"""
    id: str
    code: str
    name: str
    description: Optional[str] = None
    discount_type: str  # "percent" or "fixed"
    discount_value: float
    currency: str = "USD"
    duration: str  # "once", "forever", "repeating"
    duration_months: Optional[int] = None
    max_redemptions: Optional[int] = None
    redemption_count: int = 0
    applies_to_plans: list[str] = Field(default_factory=list)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CouponValidation(BaseModel):
    """Coupon validation result"""
    valid: bool
    coupon: Optional[Coupon] = None
    error_message: Optional[str] = None
    discount_amount: Optional[float] = None


# Billing Settings

class BillingSettings(BaseModel):
    """Workspace billing settings"""
    workspace_id: str
    billing_email: Optional[str] = None
    billing_name: Optional[str] = None
    billing_address: Optional[dict[str, str]] = None
    tax_id: Optional[str] = None
    tax_id_type: Optional[str] = None
    auto_collection: bool = True
    invoice_prefix: Optional[str] = None
    default_payment_method_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BillingSettingsUpdate(BaseModel):
    """Update billing settings"""
    billing_email: Optional[str] = None
    billing_name: Optional[str] = None
    billing_address: Optional[dict[str, str]] = None
    tax_id: Optional[str] = None
    tax_id_type: Optional[str] = None
    auto_collection: Optional[bool] = None
    invoice_prefix: Optional[str] = None
    default_payment_method_id: Optional[str] = None


# Billing Portal

class BillingPortalSession(BaseModel):
    """Billing portal session"""
    url: str
    expires_at: datetime


# Response Models

class BillingOverview(BaseModel):
    """Billing overview for dashboard"""
    workspace_id: str
    subscription: Optional[Subscription] = None
    current_plan: Optional[Plan] = None
    usage_summary: Optional[UsageSummary] = None
    credit_balance: Optional[CreditBalance] = None
    upcoming_invoice: Optional[Invoice] = None
    payment_methods: list[PaymentMethod] = Field(default_factory=list)
    recent_invoices: list[Invoice] = Field(default_factory=list)


class SubscriptionPreview(BaseModel):
    """Preview subscription change"""
    current_plan: Plan
    new_plan: Plan
    proration_amount: float
    new_amount: float
    currency: str
    effective_date: datetime
    credit_applied: float = 0


# Constants

PLAN_FEATURES = {
    "dashboards": {"name": "Dashboards", "unit": "dashboards"},
    "charts": {"name": "Charts", "unit": "charts"},
    "connections": {"name": "Data Connections", "unit": "connections"},
    "members": {"name": "Team Members", "unit": "members"},
    "storage": {"name": "Storage", "unit": "GB"},
    "api_calls": {"name": "API Calls", "unit": "calls/month"},
    "query_minutes": {"name": "Query Execution", "unit": "minutes/month"},
    "scheduled_reports": {"name": "Scheduled Reports", "unit": "reports"},
    "alerts": {"name": "Alerts", "unit": "alerts"},
    "ai_queries": {"name": "AI Queries", "unit": "queries/month"},
    "support": {"name": "Support", "unit": ""},
    "sso": {"name": "SSO/SAML", "unit": ""},
    "audit_logs": {"name": "Audit Logs", "unit": "days retention"},
    "custom_branding": {"name": "Custom Branding", "unit": ""},
    "api_access": {"name": "API Access", "unit": ""},
}

DEFAULT_PLANS = [
    {
        "id": "plan_free",
        "name": "Free",
        "tier": 0,
        "price_monthly": 0,
        "price_yearly": 0,
        "limits": {
            "dashboards": 5,
            "charts": 20,
            "connections": 2,
            "members": 3,
            "storage": 100,
            "api_calls": 100,
            "query_minutes": 10,
            "scheduled_reports": 0,
            "alerts": 0,
        },
    },
    {
        "id": "plan_starter",
        "name": "Starter",
        "tier": 1,
        "price_monthly": 29,
        "price_yearly": 290,
        "limits": {
            "dashboards": 20,
            "charts": 100,
            "connections": 5,
            "members": 5,
            "storage": 500,
            "api_calls": 1000,
            "query_minutes": 60,
            "scheduled_reports": 5,
            "alerts": 10,
        },
    },
    {
        "id": "plan_pro",
        "name": "Pro",
        "tier": 2,
        "price_monthly": 79,
        "price_yearly": 790,
        "is_popular": True,
        "limits": {
            "dashboards": 100,
            "charts": 500,
            "connections": 20,
            "members": 25,
            "storage": 5000,
            "api_calls": 10000,
            "query_minutes": 300,
            "scheduled_reports": 25,
            "alerts": 50,
        },
    },
    {
        "id": "plan_business",
        "name": "Business",
        "tier": 3,
        "price_monthly": 199,
        "price_yearly": 1990,
        "limits": {
            "dashboards": 500,
            "charts": 2500,
            "connections": 50,
            "members": 100,
            "storage": 25000,
            "api_calls": 100000,
            "query_minutes": 1000,
            "scheduled_reports": 100,
            "alerts": 200,
        },
    },
    {
        "id": "plan_enterprise",
        "name": "Enterprise",
        "tier": 4,
        "price_monthly": 0,  # Custom pricing
        "price_yearly": 0,
        "limits": {
            "dashboards": -1,  # Unlimited
            "charts": -1,
            "connections": -1,
            "members": -1,
            "storage": -1,
            "api_calls": -1,
            "query_minutes": -1,
            "scheduled_reports": -1,
            "alerts": -1,
        },
    },
]


# Helper Functions

def calculate_proration(
    current_plan: Plan,
    new_plan: Plan,
    days_remaining: int,
    total_days: int,
    billing_interval: BillingInterval,
) -> float:
    """Calculate proration amount for plan change."""
    current_price = current_plan.price_yearly if billing_interval == BillingInterval.YEARLY else current_plan.price_monthly
    new_price = new_plan.price_yearly if billing_interval == BillingInterval.YEARLY else new_plan.price_monthly

    if billing_interval == BillingInterval.YEARLY:
        daily_rate_current = current_price / 365
        daily_rate_new = new_price / 365
    else:
        daily_rate_current = current_price / 30
        daily_rate_new = new_price / 30

    # Credit for unused time on current plan
    credit = daily_rate_current * days_remaining
    # Charge for new plan's remaining time
    charge = daily_rate_new * days_remaining

    return round(charge - credit, 2)


def is_upgrade(current_plan: Plan, new_plan: Plan) -> bool:
    """Check if plan change is an upgrade."""
    return new_plan.tier > current_plan.tier


def get_usage_percent(used: float, limit: int) -> float:
    """Calculate usage percentage."""
    if limit == -1:  # Unlimited
        return 0
    if limit == 0:
        return 100 if used > 0 else 0
    return min(100, round((used / limit) * 100, 2))
