"""
Billing & Usage Quotas API Endpoints

REST API for subscriptions, billing, invoices, payment methods,
usage tracking, and quota management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.schemas.billing import (
    Plan, PlanComparison,
    Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionStatus,
    SubscriptionUsage, SubscriptionPreview, BillingInterval,
    Invoice, InvoiceStatus, InvoiceListResponse,
    PaymentMethod, PaymentMethodCreate,
    Payment, PaymentListResponse,
    UsageRecord, UsageSummary, UsageMetricType, UsageAlert, UsageAlertCreate,
    Credit, CreditType, CreditBalance,
    Coupon, CouponValidation,
    BillingSettings, BillingSettingsUpdate,
    BillingOverview, BillingPortalSession,
)
from app.services.billing_service import billing_service

router = APIRouter()


# Plan Endpoints

@router.get("/plans", response_model=list[Plan], tags=["plans"])
async def list_plans(include_private: bool = False):
    """List available subscription plans."""
    return billing_service.list_plans(include_private)


@router.get("/plans/{plan_id}", response_model=Plan, tags=["plans"])
async def get_plan(plan_id: str):
    """Get plan details."""
    plan = billing_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.get("/plans/compare", response_model=PlanComparison, tags=["plans"])
async def get_plan_comparison():
    """Get plan comparison for pricing page."""
    return billing_service.get_plan_comparison()


# Subscription Endpoints

@router.post("/subscriptions", response_model=Subscription, tags=["subscriptions"])
async def create_subscription(data: SubscriptionCreate):
    """Create a new subscription."""
    try:
        return billing_service.create_subscription(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscriptions/{subscription_id}", response_model=Subscription, tags=["subscriptions"])
async def get_subscription(subscription_id: str):
    """Get subscription details."""
    sub = billing_service.get_subscription(subscription_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub


@router.get("/workspaces/{workspace_id}/subscription", response_model=Subscription, tags=["subscriptions"])
async def get_workspace_subscription(workspace_id: str):
    """Get active subscription for workspace."""
    sub = billing_service.get_workspace_subscription(workspace_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return sub


@router.patch("/subscriptions/{subscription_id}", response_model=Subscription, tags=["subscriptions"])
async def update_subscription(subscription_id: str, data: SubscriptionUpdate):
    """Update subscription."""
    sub = billing_service.update_subscription(subscription_id, data)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub


@router.post("/subscriptions/{subscription_id}/cancel", response_model=Subscription, tags=["subscriptions"])
async def cancel_subscription(
    subscription_id: str,
    immediate: bool = Query(False, description="Cancel immediately instead of at period end"),
):
    """Cancel subscription."""
    sub = billing_service.cancel_subscription(subscription_id, immediate)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub


@router.post("/subscriptions/{subscription_id}/reactivate", response_model=Subscription, tags=["subscriptions"])
async def reactivate_subscription(subscription_id: str):
    """Reactivate a canceled subscription."""
    sub = billing_service.reactivate_subscription(subscription_id)
    if not sub:
        raise HTTPException(status_code=400, detail="Cannot reactivate subscription")
    return sub


@router.get("/subscriptions/{subscription_id}/preview-change", response_model=SubscriptionPreview, tags=["subscriptions"])
async def preview_subscription_change(
    subscription_id: str,
    new_plan_id: str = Query(..., description="New plan ID"),
):
    """Preview subscription plan change."""
    preview = billing_service.preview_subscription_change(subscription_id, new_plan_id)
    if not preview:
        raise HTTPException(status_code=400, detail="Cannot preview change")
    return preview


@router.get("/subscriptions/{subscription_id}/usage", response_model=SubscriptionUsage, tags=["subscriptions"])
async def get_subscription_usage(subscription_id: str):
    """Get subscription usage summary."""
    usage = billing_service.get_subscription_usage(subscription_id)
    if not usage:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return usage


# Invoice Endpoints

@router.get("/workspaces/{workspace_id}/invoices", response_model=InvoiceListResponse, tags=["invoices"])
async def list_invoices(
    workspace_id: str,
    status: Optional[InvoiceStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List invoices for workspace."""
    return billing_service.list_invoices(workspace_id, status, skip, limit)


@router.get("/invoices/{invoice_id}", response_model=Invoice, tags=["invoices"])
async def get_invoice(invoice_id: str):
    """Get invoice details."""
    invoice = billing_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/invoices/{invoice_id}/pay", response_model=Payment, tags=["invoices"])
async def pay_invoice(
    invoice_id: str,
    payment_method_id: Optional[str] = Query(None),
):
    """Pay an invoice."""
    payment = billing_service.pay_invoice(invoice_id, payment_method_id)
    if not payment:
        raise HTTPException(status_code=400, detail="Cannot process payment")
    return payment


# Payment Method Endpoints

@router.post("/workspaces/{workspace_id}/payment-methods", response_model=PaymentMethod, tags=["payment-methods"])
async def add_payment_method(workspace_id: str, data: PaymentMethodCreate):
    """Add payment method."""
    return billing_service.add_payment_method(workspace_id, data)


@router.get("/workspaces/{workspace_id}/payment-methods", response_model=list[PaymentMethod], tags=["payment-methods"])
async def list_payment_methods(workspace_id: str):
    """List payment methods for workspace."""
    return billing_service.list_payment_methods(workspace_id)


@router.delete("/payment-methods/{payment_method_id}", tags=["payment-methods"])
async def delete_payment_method(payment_method_id: str):
    """Delete payment method."""
    if not billing_service.delete_payment_method(payment_method_id):
        raise HTTPException(status_code=404, detail="Payment method not found")
    return {"status": "deleted"}


@router.post("/workspaces/{workspace_id}/payment-methods/{payment_method_id}/default", tags=["payment-methods"])
async def set_default_payment_method(workspace_id: str, payment_method_id: str):
    """Set default payment method."""
    if not billing_service.set_default_payment_method(workspace_id, payment_method_id):
        raise HTTPException(status_code=400, detail="Cannot set default payment method")
    return {"status": "success"}


# Usage Endpoints

@router.post("/workspaces/{workspace_id}/usage", response_model=UsageRecord, tags=["usage"])
async def record_usage(
    workspace_id: str,
    metric_type: UsageMetricType = Query(...),
    quantity: float = Query(..., gt=0),
    metadata: Optional[str] = Query(None, description="JSON metadata"),
):
    """Record usage for a metric."""
    import json
    meta = json.loads(metadata) if metadata else None
    return billing_service.record_usage(workspace_id, metric_type, quantity, meta)


@router.get("/workspaces/{workspace_id}/usage", response_model=UsageSummary, tags=["usage"])
async def get_usage_summary(
    workspace_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    """Get usage summary for workspace."""
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    return billing_service.get_usage_summary(workspace_id, start, end)


# Usage Alert Endpoints

@router.post("/workspaces/{workspace_id}/usage-alerts", response_model=UsageAlert, tags=["usage-alerts"])
async def create_usage_alert(workspace_id: str, data: UsageAlertCreate):
    """Create usage alert."""
    return billing_service.create_usage_alert(workspace_id, data)


@router.get("/workspaces/{workspace_id}/usage-alerts", response_model=list[UsageAlert], tags=["usage-alerts"])
async def list_usage_alerts(workspace_id: str):
    """List usage alerts for workspace."""
    return billing_service.list_usage_alerts(workspace_id)


@router.delete("/usage-alerts/{alert_id}", tags=["usage-alerts"])
async def delete_usage_alert(alert_id: str):
    """Delete usage alert."""
    if not billing_service.delete_usage_alert(alert_id):
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "deleted"}


# Credit Endpoints

@router.post("/workspaces/{workspace_id}/credits", response_model=Credit, tags=["credits"])
async def add_credit(
    workspace_id: str,
    amount: float = Query(..., gt=0),
    credit_type: CreditType = Query(...),
    description: Optional[str] = Query(None),
    expires_at: Optional[str] = Query(None),
):
    """Add credit to workspace."""
    expires = datetime.fromisoformat(expires_at) if expires_at else None
    return billing_service.add_credit(workspace_id, amount, credit_type, description, expires)


@router.get("/workspaces/{workspace_id}/credits", response_model=CreditBalance, tags=["credits"])
async def get_credit_balance(workspace_id: str):
    """Get credit balance for workspace."""
    return billing_service.get_credit_balance(workspace_id)


# Coupon Endpoints

@router.post("/coupons/validate", response_model=CouponValidation, tags=["coupons"])
async def validate_coupon(
    code: str = Query(...),
    plan_id: Optional[str] = Query(None),
):
    """Validate a coupon code."""
    return billing_service.validate_coupon(code, plan_id)


@router.post("/coupons", response_model=Coupon, tags=["coupons"])
async def create_coupon(
    code: str = Query(...),
    name: str = Query(...),
    discount_type: str = Query(..., regex="^(percent|fixed)$"),
    discount_value: float = Query(..., gt=0),
    duration: str = Query("once", regex="^(once|forever|repeating)$"),
    duration_months: Optional[int] = Query(None),
    max_redemptions: Optional[int] = Query(None),
    valid_until: Optional[str] = Query(None),
):
    """Create a coupon (admin only)."""
    expires = datetime.fromisoformat(valid_until) if valid_until else None
    return billing_service.create_coupon(
        code, name, discount_type, discount_value, duration,
        duration_months=duration_months,
        max_redemptions=max_redemptions,
        valid_until=expires,
    )


# Billing Settings Endpoints

@router.get("/workspaces/{workspace_id}/billing-settings", response_model=BillingSettings, tags=["billing-settings"])
async def get_billing_settings(workspace_id: str):
    """Get billing settings for workspace."""
    return billing_service.get_billing_settings(workspace_id)


@router.put("/workspaces/{workspace_id}/billing-settings", response_model=BillingSettings, tags=["billing-settings"])
async def update_billing_settings(workspace_id: str, data: BillingSettingsUpdate):
    """Update billing settings."""
    return billing_service.update_billing_settings(workspace_id, data)


# Billing Overview

@router.get("/workspaces/{workspace_id}/billing", response_model=BillingOverview, tags=["billing"])
async def get_billing_overview(workspace_id: str):
    """Get billing overview for workspace dashboard."""
    return billing_service.get_billing_overview(workspace_id)


@router.post("/workspaces/{workspace_id}/billing/portal", response_model=BillingPortalSession, tags=["billing"])
async def create_billing_portal_session(
    workspace_id: str,
    return_url: str = Query(..., description="URL to return to after portal session"),
):
    """Create billing portal session."""
    return billing_service.create_billing_portal_session(workspace_id, return_url)
