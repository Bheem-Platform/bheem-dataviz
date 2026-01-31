"""
Billing Models

Database models for billing, plans, invoices, and usage tracking.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class BillingPlan(Base):
    """
    Billing plan model for subscription tiers.
    """
    __tablename__ = "billing_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Plan info
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Pricing
    price_monthly = Column(Float, default=0)
    price_yearly = Column(Float, default=0)
    currency = Column(String(3), default="USD")

    # Limits
    max_users = Column(Integer, nullable=True)  # null = unlimited
    max_dashboards = Column(Integer, nullable=True)
    max_connections = Column(Integer, nullable=True)
    max_queries_per_day = Column(Integer, nullable=True)
    max_storage_gb = Column(Float, nullable=True)
    max_api_calls_per_month = Column(Integer, nullable=True)

    # Features
    features = Column(JSONB, default=[])
    feature_flags = Column(JSONB, default={})

    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace_subscriptions = relationship("WorkspaceSubscription", back_populates="plan")


class WorkspaceSubscription(Base):
    """
    Workspace subscription model linking workspaces to billing plans.
    """
    __tablename__ = "workspace_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("billing_plans.id", ondelete="RESTRICT"), nullable=False)

    # Subscription details
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    status = Column(String(50), default="active")  # active, past_due, cancelled, trialing

    # Trial
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    is_trial = Column(Boolean, default=False)

    # Billing dates
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)

    # Payment
    payment_method_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # Quantity
    quantity = Column(Integer, default=1)  # Number of seats

    # Discount
    discount_percent = Column(Float, default=0)
    discount_ends_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    plan = relationship("BillingPlan", back_populates="workspace_subscriptions")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")


class Invoice(Base):
    """
    Invoice model for billing history.
    """
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    subscription_id = Column(UUID(as_uuid=True), ForeignKey("workspace_subscriptions.id", ondelete="CASCADE"), nullable=False)

    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="draft")  # draft, open, paid, void, uncollectible

    # Amounts
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, default=0)
    discount = Column(Float, default=0)
    total = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")

    # Dates
    invoice_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    due_date = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Period
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    # Line items
    line_items = Column(JSONB, default=[])

    # Payment
    payment_intent_id = Column(String(255), nullable=True)
    stripe_invoice_id = Column(String(255), nullable=True)

    # PDF
    pdf_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("WorkspaceSubscription", back_populates="invoices")

    __table_args__ = (
        Index('ix_invoices_subscription_date', subscription_id, invoice_date),
    )


class UsageRecord(Base):
    """
    Usage tracking model for metered billing.
    """
    __tablename__ = "usage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)

    # Usage type
    usage_type = Column(String(50), nullable=False)  # queries, api_calls, storage, exports

    # Metrics
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)  # count, bytes, seconds

    # Time
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    # Context
    user_id = Column(UUID(as_uuid=True), nullable=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)

    # Extra data
    extra_data = Column(JSONB, default={})

    __table_args__ = (
        Index('ix_usage_records_workspace_type_date', workspace_id, usage_type, recorded_at),
    )


class UsageSummary(Base):
    """
    Daily usage summary for efficient querying.
    """
    __tablename__ = "usage_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)

    # Period
    date = Column(DateTime(timezone=True), nullable=False)

    # Aggregated metrics
    total_queries = Column(Integer, default=0)
    total_api_calls = Column(Integer, default=0)
    total_exports = Column(Integer, default=0)
    storage_used_bytes = Column(Float, default=0)
    active_users = Column(Integer, default=0)

    # Details
    queries_by_type = Column(JSONB, default={})
    top_users = Column(JSONB, default=[])

    __table_args__ = (
        Index('ix_usage_summaries_workspace_date', workspace_id, date, unique=True),
    )
