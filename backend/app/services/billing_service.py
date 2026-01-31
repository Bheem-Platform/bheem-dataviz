"""
Billing & Usage Quotas Service

Provides subscription management, billing, invoicing, payment methods,
usage tracking, and quota management.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from app.schemas.billing import (
    Plan, PlanFeature, PlanComparison,
    Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionStatus,
    SubscriptionUsage, SubscriptionPreview, BillingInterval,
    Invoice, InvoiceLineItem, InvoiceStatus, InvoiceListResponse,
    PaymentMethod, PaymentMethodCreate, PaymentMethodType,
    Payment, PaymentStatus, PaymentListResponse,
    UsageRecord, UsageSummary, UsageMetricType, UsageAlert, UsageAlertCreate,
    Credit, CreditType, CreditBalance, CreditApplication,
    Coupon, CouponValidation,
    BillingSettings, BillingSettingsUpdate,
    BillingOverview, BillingPortalSession,
    DEFAULT_PLANS, PLAN_FEATURES,
    calculate_proration, is_upgrade, get_usage_percent,
)


class BillingService:
    """Service for billing and usage management."""

    def __init__(self):
        # In-memory stores (production would use Stripe/database)
        self.plans: dict[str, Plan] = {}
        self.subscriptions: dict[str, Subscription] = {}
        self.invoices: dict[str, Invoice] = {}
        self.payment_methods: dict[str, PaymentMethod] = {}
        self.payments: dict[str, Payment] = {}
        self.usage_records: list[UsageRecord] = []
        self.usage_alerts: dict[str, UsageAlert] = {}
        self.credits: dict[str, Credit] = {}
        self.credit_applications: list[CreditApplication] = []
        self.coupons: dict[str, Coupon] = {}
        self.billing_settings: dict[str, BillingSettings] = {}

        self._initialize_plans()

    def _initialize_plans(self):
        """Initialize default plans."""
        for plan_data in DEFAULT_PLANS:
            features = []
            for feature_code, limit in plan_data.get("limits", {}).items():
                feature_info = PLAN_FEATURES.get(feature_code, {})
                features.append(PlanFeature(
                    code=feature_code,
                    name=feature_info.get("name", feature_code),
                    included=True,
                    limit=limit if limit != -1 else None,
                    unit=feature_info.get("unit"),
                ))

            plan = Plan(
                id=plan_data["id"],
                name=plan_data["name"],
                tier=plan_data["tier"],
                price_monthly=plan_data["price_monthly"],
                price_yearly=plan_data["price_yearly"],
                features=features,
                limits=plan_data.get("limits", {}),
                is_popular=plan_data.get("is_popular", False),
                trial_days=14 if plan_data["tier"] > 0 else 0,
            )
            self.plans[plan.id] = plan

    def _generate_id(self, prefix: str = "id") -> str:
        """Generate a unique ID."""
        return f"{prefix}_{secrets.token_hex(12)}"

    # Plan Management

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan by ID."""
        return self.plans.get(plan_id)

    def list_plans(self, include_private: bool = False) -> list[Plan]:
        """List available plans."""
        plans = list(self.plans.values())
        if not include_private:
            plans = [p for p in plans if p.is_public]
        return sorted(plans, key=lambda x: x.tier)

    def get_plan_comparison(self) -> PlanComparison:
        """Get plan comparison for pricing page."""
        plans = self.list_plans()

        # Group features by category
        categories = [
            {
                "name": "Core Features",
                "features": ["dashboards", "charts", "connections", "members"],
            },
            {
                "name": "Data & Processing",
                "features": ["storage", "api_calls", "query_minutes"],
            },
            {
                "name": "Automation",
                "features": ["scheduled_reports", "alerts", "ai_queries"],
            },
            {
                "name": "Enterprise",
                "features": ["sso", "audit_logs", "custom_branding", "api_access"],
            },
        ]

        return PlanComparison(plans=plans, feature_categories=categories)

    # Subscription Management

    def create_subscription(self, data: SubscriptionCreate) -> Subscription:
        """Create a new subscription."""
        plan = self.plans.get(data.plan_id)
        if not plan:
            raise ValueError("Plan not found")

        # Check for existing subscription
        for sub in self.subscriptions.values():
            if sub.workspace_id == data.workspace_id and sub.status in [
                SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING
            ]:
                raise ValueError("Workspace already has an active subscription")

        sub_id = self._generate_id("sub")
        now = datetime.utcnow()

        # Calculate period
        if data.billing_interval == BillingInterval.YEARLY:
            period_end = now + timedelta(days=365)
            unit_amount = plan.price_yearly
        elif data.billing_interval == BillingInterval.QUARTERLY:
            period_end = now + timedelta(days=90)
            unit_amount = plan.price_monthly * 3 * 0.9  # 10% discount
        else:
            period_end = now + timedelta(days=30)
            unit_amount = plan.price_monthly

        # Handle trial
        trial_days = data.trial_days if data.trial_days is not None else plan.trial_days
        trial_end = now + timedelta(days=trial_days) if trial_days > 0 else None
        status = SubscriptionStatus.TRIALING if trial_end else SubscriptionStatus.ACTIVE

        # Apply coupon
        discount = 0
        if data.coupon_code:
            validation = self.validate_coupon(data.coupon_code, data.plan_id)
            if validation.valid and validation.coupon:
                if validation.coupon.discount_type == "percent":
                    discount = validation.coupon.discount_value
                else:
                    unit_amount -= validation.coupon.discount_value
                    unit_amount = max(0, unit_amount)

        subscription = Subscription(
            id=sub_id,
            workspace_id=data.workspace_id,
            plan_id=data.plan_id,
            plan_name=plan.name,
            status=status,
            billing_interval=data.billing_interval,
            current_period_start=now,
            current_period_end=period_end,
            trial_start=now if trial_end else None,
            trial_end=trial_end,
            payment_method_id=data.payment_method_id,
            unit_amount=unit_amount,
            discount_percent=discount,
            coupon_code=data.coupon_code,
        )

        self.subscriptions[sub_id] = subscription

        # Create initial invoice (if not trial)
        if status == SubscriptionStatus.ACTIVE:
            self._create_subscription_invoice(subscription)

        return subscription

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.subscriptions.get(subscription_id)

    def get_workspace_subscription(self, workspace_id: str) -> Optional[Subscription]:
        """Get active subscription for workspace."""
        for sub in self.subscriptions.values():
            if sub.workspace_id == workspace_id and sub.status in [
                SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING, SubscriptionStatus.PAST_DUE
            ]:
                return sub
        return None

    def update_subscription(self, subscription_id: str, data: SubscriptionUpdate) -> Optional[Subscription]:
        """Update subscription."""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return None

        if data.plan_id and data.plan_id != sub.plan_id:
            # Plan change
            new_plan = self.plans.get(data.plan_id)
            if new_plan:
                sub.plan_id = new_plan.id
                sub.plan_name = new_plan.name
                # Recalculate amount
                if sub.billing_interval == BillingInterval.YEARLY:
                    sub.unit_amount = new_plan.price_yearly
                else:
                    sub.unit_amount = new_plan.price_monthly

        if data.billing_interval:
            sub.billing_interval = data.billing_interval
        if data.payment_method_id:
            sub.payment_method_id = data.payment_method_id
        if data.cancel_at_period_end is not None:
            sub.cancel_at_period_end = data.cancel_at_period_end
            if data.cancel_at_period_end:
                sub.canceled_at = datetime.utcnow()

        sub.updated_at = datetime.utcnow()
        return sub

    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> Optional[Subscription]:
        """Cancel subscription."""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return None

        sub.canceled_at = datetime.utcnow()
        if immediate:
            sub.status = SubscriptionStatus.CANCELED
        else:
            sub.cancel_at_period_end = True

        sub.updated_at = datetime.utcnow()
        return sub

    def reactivate_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Reactivate canceled subscription."""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return None

        if sub.status == SubscriptionStatus.CANCELED:
            # Create new subscription instead
            return None

        sub.cancel_at_period_end = False
        sub.canceled_at = None
        sub.updated_at = datetime.utcnow()
        return sub

    def preview_subscription_change(
        self, subscription_id: str, new_plan_id: str
    ) -> Optional[SubscriptionPreview]:
        """Preview subscription plan change."""
        sub = self.subscriptions.get(subscription_id)
        current_plan = self.plans.get(sub.plan_id) if sub else None
        new_plan = self.plans.get(new_plan_id)

        if not sub or not current_plan or not new_plan:
            return None

        days_remaining = (sub.current_period_end - datetime.utcnow()).days
        total_days = (sub.current_period_end - sub.current_period_start).days

        proration = calculate_proration(
            current_plan, new_plan, days_remaining, total_days, sub.billing_interval
        )

        new_amount = new_plan.price_yearly if sub.billing_interval == BillingInterval.YEARLY else new_plan.price_monthly

        return SubscriptionPreview(
            current_plan=current_plan,
            new_plan=new_plan,
            proration_amount=proration,
            new_amount=new_amount,
            currency=sub.currency,
            effective_date=datetime.utcnow(),
        )

    def get_subscription_usage(self, subscription_id: str) -> Optional[SubscriptionUsage]:
        """Get subscription usage summary."""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return None

        plan = self.plans.get(sub.plan_id)
        if not plan:
            return None

        # Calculate usage for current period
        metrics = {}
        for metric_type in UsageMetricType:
            used = self._calculate_usage(
                sub.workspace_id, metric_type,
                sub.current_period_start, sub.current_period_end
            )
            limit = plan.limits.get(metric_type.value, -1)
            metrics[metric_type.value] = {
                "used": used,
                "limit": limit,
                "percent": get_usage_percent(used, limit),
            }

        return SubscriptionUsage(
            subscription_id=subscription_id,
            period_start=sub.current_period_start,
            period_end=sub.current_period_end,
            metrics=metrics,
        )

    # Invoice Management

    def _create_subscription_invoice(self, subscription: Subscription) -> Invoice:
        """Create invoice for subscription."""
        invoice_id = self._generate_id("inv")
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m')}-{secrets.token_hex(4).upper()}"

        amount = subscription.unit_amount * subscription.quantity
        discount = amount * (subscription.discount_percent / 100)
        total = amount - discount

        line_items = [
            InvoiceLineItem(
                id=self._generate_id("li"),
                description=f"{subscription.plan_name} - {subscription.billing_interval.value}",
                quantity=subscription.quantity,
                unit_amount=subscription.unit_amount,
                amount=amount,
                currency=subscription.currency,
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end,
            )
        ]

        invoice = Invoice(
            id=invoice_id,
            number=invoice_number,
            workspace_id=subscription.workspace_id,
            subscription_id=subscription.id,
            status=InvoiceStatus.OPEN,
            currency=subscription.currency,
            subtotal=amount,
            discount=discount,
            total=total,
            amount_due=total,
            line_items=line_items,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            due_date=datetime.utcnow() + timedelta(days=30),
            billing_reason="subscription_create",
        )

        self.invoices[invoice_id] = invoice
        return invoice

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by ID."""
        return self.invoices.get(invoice_id)

    def list_invoices(
        self,
        workspace_id: str,
        status: Optional[InvoiceStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> InvoiceListResponse:
        """List invoices for workspace."""
        invoices = [i for i in self.invoices.values() if i.workspace_id == workspace_id]

        if status:
            invoices = [i for i in invoices if i.status == status]

        invoices.sort(key=lambda x: x.created_at, reverse=True)
        total = len(invoices)
        invoices = invoices[skip:skip + limit]

        return InvoiceListResponse(invoices=invoices, total=total)

    def pay_invoice(self, invoice_id: str, payment_method_id: Optional[str] = None) -> Optional[Payment]:
        """Pay an invoice."""
        invoice = self.invoices.get(invoice_id)
        if not invoice or invoice.status != InvoiceStatus.OPEN:
            return None

        payment_id = self._generate_id("pay")
        payment = Payment(
            id=payment_id,
            workspace_id=invoice.workspace_id,
            invoice_id=invoice_id,
            subscription_id=invoice.subscription_id,
            payment_method_id=payment_method_id,
            status=PaymentStatus.SUCCEEDED,
            amount=invoice.amount_due,
            currency=invoice.currency,
            description=f"Payment for invoice {invoice.number}",
        )

        self.payments[payment_id] = payment

        # Update invoice
        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.utcnow()
        invoice.amount_paid = invoice.amount_due
        invoice.amount_due = 0

        return payment

    # Payment Methods

    def add_payment_method(self, workspace_id: str, data: PaymentMethodCreate) -> PaymentMethod:
        """Add payment method."""
        pm_id = self._generate_id("pm")

        # Mask card details
        card_last4 = data.card_number[-4:] if data.card_number else None

        payment_method = PaymentMethod(
            id=pm_id,
            workspace_id=workspace_id,
            type=data.type,
            is_default=data.is_default,
            card_brand="visa" if card_last4 else None,  # Simplified
            card_last4=card_last4,
            card_exp_month=data.card_exp_month,
            card_exp_year=data.card_exp_year,
            billing_name=data.billing_name,
            billing_email=data.billing_email,
            billing_address=data.billing_address,
        )

        # If this is default, unset others
        if data.is_default:
            for pm in self.payment_methods.values():
                if pm.workspace_id == workspace_id:
                    pm.is_default = False

        self.payment_methods[pm_id] = payment_method
        return payment_method

    def list_payment_methods(self, workspace_id: str) -> list[PaymentMethod]:
        """List payment methods for workspace."""
        return [pm for pm in self.payment_methods.values() if pm.workspace_id == workspace_id]

    def delete_payment_method(self, payment_method_id: str) -> bool:
        """Delete payment method."""
        if payment_method_id in self.payment_methods:
            del self.payment_methods[payment_method_id]
            return True
        return False

    def set_default_payment_method(self, workspace_id: str, payment_method_id: str) -> bool:
        """Set default payment method."""
        pm = self.payment_methods.get(payment_method_id)
        if not pm or pm.workspace_id != workspace_id:
            return False

        for other_pm in self.payment_methods.values():
            if other_pm.workspace_id == workspace_id:
                other_pm.is_default = (other_pm.id == payment_method_id)

        return True

    # Usage Tracking

    def record_usage(
        self,
        workspace_id: str,
        metric_type: UsageMetricType,
        quantity: float,
        metadata: Optional[dict] = None,
    ) -> UsageRecord:
        """Record usage."""
        record_id = self._generate_id("usage")
        sub = self.get_workspace_subscription(workspace_id)

        record = UsageRecord(
            id=record_id,
            workspace_id=workspace_id,
            subscription_id=sub.id if sub else None,
            metric_type=metric_type,
            quantity=quantity,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
        )

        self.usage_records.append(record)

        # Check usage alerts
        self._check_usage_alerts(workspace_id, metric_type)

        return record

    def _calculate_usage(
        self,
        workspace_id: str,
        metric_type: UsageMetricType,
        start: datetime,
        end: datetime,
    ) -> float:
        """Calculate total usage for a metric in a period."""
        total = 0
        for record in self.usage_records:
            if (record.workspace_id == workspace_id and
                record.metric_type == metric_type and
                start <= record.timestamp <= end):
                total += record.quantity
        return total

    def get_usage_summary(
        self,
        workspace_id: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> UsageSummary:
        """Get usage summary."""
        if not end:
            end = datetime.utcnow()
        if not start:
            start = end - timedelta(days=30)

        sub = self.get_workspace_subscription(workspace_id)
        plan = self.plans.get(sub.plan_id) if sub else self.plans.get("plan_free")

        metrics = {}
        for metric_type in UsageMetricType:
            total = self._calculate_usage(workspace_id, metric_type, start, end)
            limit = plan.limits.get(metric_type.value, -1) if plan else -1

            # Daily breakdown
            daily = {}
            current = start
            while current <= end:
                day_end = min(current + timedelta(days=1), end)
                daily[current.strftime("%Y-%m-%d")] = self._calculate_usage(
                    workspace_id, metric_type, current, day_end
                )
                current = day_end

            metrics[metric_type.value] = {
                "total": total,
                "limit": limit,
                "percent": get_usage_percent(total, limit),
                "daily_breakdown": daily,
            }

        return UsageSummary(
            workspace_id=workspace_id,
            period_start=start,
            period_end=end,
            metrics=metrics,
        )

    # Usage Alerts

    def create_usage_alert(self, workspace_id: str, data: UsageAlertCreate) -> UsageAlert:
        """Create usage alert."""
        alert_id = self._generate_id("alert")

        alert = UsageAlert(
            id=alert_id,
            workspace_id=workspace_id,
            metric_type=data.metric_type,
            threshold_percent=data.threshold_percent,
            notification_channels=data.notification_channels,
        )

        self.usage_alerts[alert_id] = alert
        return alert

    def list_usage_alerts(self, workspace_id: str) -> list[UsageAlert]:
        """List usage alerts for workspace."""
        return [a for a in self.usage_alerts.values() if a.workspace_id == workspace_id]

    def delete_usage_alert(self, alert_id: str) -> bool:
        """Delete usage alert."""
        if alert_id in self.usage_alerts:
            del self.usage_alerts[alert_id]
            return True
        return False

    def _check_usage_alerts(self, workspace_id: str, metric_type: UsageMetricType):
        """Check and trigger usage alerts."""
        sub = self.get_workspace_subscription(workspace_id)
        if not sub:
            return

        plan = self.plans.get(sub.plan_id)
        if not plan:
            return

        limit = plan.limits.get(metric_type.value, -1)
        if limit == -1:
            return

        current_usage = self._calculate_usage(
            workspace_id, metric_type,
            sub.current_period_start, datetime.utcnow()
        )
        percent = get_usage_percent(current_usage, limit)

        for alert in self.usage_alerts.values():
            if (alert.workspace_id == workspace_id and
                alert.metric_type == metric_type and
                alert.is_enabled and
                percent >= alert.threshold_percent):
                # Would trigger notification here
                alert.last_triggered_at = datetime.utcnow()

    # Credits

    def add_credit(
        self,
        workspace_id: str,
        amount: float,
        credit_type: CreditType,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Credit:
        """Add credit to workspace."""
        credit_id = self._generate_id("cred")

        credit = Credit(
            id=credit_id,
            workspace_id=workspace_id,
            type=credit_type,
            amount=amount,
            remaining=amount,
            description=description,
            expires_at=expires_at,
        )

        self.credits[credit_id] = credit
        return credit

    def get_credit_balance(self, workspace_id: str) -> CreditBalance:
        """Get credit balance for workspace."""
        credits = [c for c in self.credits.values()
                   if c.workspace_id == workspace_id and c.remaining > 0]

        # Filter expired
        now = datetime.utcnow()
        active_credits = [c for c in credits if not c.expires_at or c.expires_at > now]

        total = sum(c.remaining for c in active_credits)
        expiring_soon = sum(
            c.remaining for c in active_credits
            if c.expires_at and c.expires_at < now + timedelta(days=30)
        )

        return CreditBalance(
            workspace_id=workspace_id,
            total_credits=total,
            available_credits=total,
            expiring_soon=expiring_soon,
            credits=active_credits,
        )

    # Coupons

    def create_coupon(
        self,
        code: str,
        name: str,
        discount_type: str,
        discount_value: float,
        duration: str = "once",
        **kwargs,
    ) -> Coupon:
        """Create a coupon."""
        coupon_id = self._generate_id("coup")

        coupon = Coupon(
            id=coupon_id,
            code=code.upper(),
            name=name,
            discount_type=discount_type,
            discount_value=discount_value,
            duration=duration,
            **kwargs,
        )

        self.coupons[coupon_id] = coupon
        return coupon

    def validate_coupon(self, code: str, plan_id: Optional[str] = None) -> CouponValidation:
        """Validate a coupon code."""
        code_upper = code.upper()
        coupon = None

        for c in self.coupons.values():
            if c.code == code_upper:
                coupon = c
                break

        if not coupon:
            return CouponValidation(valid=False, error_message="Invalid coupon code")

        if not coupon.is_active:
            return CouponValidation(valid=False, error_message="Coupon is no longer active")

        now = datetime.utcnow()
        if coupon.valid_from and coupon.valid_from > now:
            return CouponValidation(valid=False, error_message="Coupon is not yet valid")

        if coupon.valid_until and coupon.valid_until < now:
            return CouponValidation(valid=False, error_message="Coupon has expired")

        if coupon.max_redemptions and coupon.redemption_count >= coupon.max_redemptions:
            return CouponValidation(valid=False, error_message="Coupon redemption limit reached")

        if plan_id and coupon.applies_to_plans and plan_id not in coupon.applies_to_plans:
            return CouponValidation(valid=False, error_message="Coupon does not apply to this plan")

        return CouponValidation(valid=True, coupon=coupon)

    # Billing Settings

    def get_billing_settings(self, workspace_id: str) -> BillingSettings:
        """Get billing settings."""
        if workspace_id not in self.billing_settings:
            self.billing_settings[workspace_id] = BillingSettings(workspace_id=workspace_id)
        return self.billing_settings[workspace_id]

    def update_billing_settings(
        self, workspace_id: str, data: BillingSettingsUpdate
    ) -> BillingSettings:
        """Update billing settings."""
        settings = self.get_billing_settings(workspace_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        return settings

    # Billing Overview

    def get_billing_overview(self, workspace_id: str) -> BillingOverview:
        """Get billing overview for dashboard."""
        subscription = self.get_workspace_subscription(workspace_id)
        current_plan = self.plans.get(subscription.plan_id) if subscription else None

        usage_summary = None
        if subscription:
            usage_summary = self.get_usage_summary(
                workspace_id,
                subscription.current_period_start,
                datetime.utcnow(),
            )

        credit_balance = self.get_credit_balance(workspace_id)
        payment_methods = self.list_payment_methods(workspace_id)
        invoices_response = self.list_invoices(workspace_id, limit=5)

        # Get upcoming invoice (simplified)
        upcoming_invoice = None
        if subscription and subscription.status == SubscriptionStatus.ACTIVE:
            # Would calculate upcoming invoice here
            pass

        return BillingOverview(
            workspace_id=workspace_id,
            subscription=subscription,
            current_plan=current_plan,
            usage_summary=usage_summary,
            credit_balance=credit_balance,
            upcoming_invoice=upcoming_invoice,
            payment_methods=payment_methods,
            recent_invoices=invoices_response.invoices,
        )

    def create_billing_portal_session(self, workspace_id: str, return_url: str) -> BillingPortalSession:
        """Create billing portal session (Stripe-like)."""
        # In production, this would create a Stripe billing portal session
        return BillingPortalSession(
            url=f"/billing/portal?workspace={workspace_id}&return={return_url}",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )


# Global service instance
billing_service = BillingService()
