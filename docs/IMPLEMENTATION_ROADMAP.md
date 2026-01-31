# Bheem DataViz - Comprehensive Implementation Roadmap

> **Document Version:** 1.0.0
> **Created:** 2026-01-30
> **Target Completion:** 30 weeks (~7-8 months)

---

## Executive Summary

Based on comprehensive gap analysis comparing Bheem DataViz with industry leaders (Power BI, Tableau, Metabase, Apache Superset), **Bheem DataViz currently covers ~45% of Power BI's core features**. This document provides a detailed end-to-end implementation roadmap to achieve competitive parity.

### Current State Assessment

| Category | Current Coverage | Gap Status |
|----------|------------------|------------|
| Data Connectivity | 50% | PostgreSQL, MySQL, MongoDB, CSV, Excel working; BigQuery, Snowflake scaffolded only |
| Data Transformation | 40% | Basic transforms; missing profiling, incremental refresh, pivot/unpivot |
| Data Modeling | 35% | Basic semantic layer; missing DAX-like language, time intelligence |
| Visualization | 40% | 12 chart types; missing drill-down, conditional formatting, slicers |
| AI/ML Features | 10% | Endpoints scaffolded; Kodee NL-to-SQL not implemented |
| Collaboration | 25% | Basic auth; missing workspaces, RLS, subscriptions, alerts |
| Administration | 15% | Minimal; missing audit logs, usage analytics, admin portal |
| Developer Tools | 30% | Basic REST API; missing Embed SDK, custom visuals |

---

## Table of Contents

1. [Competitive Gap Analysis](#competitive-gap-analysis)
2. [Phase 1: Foundation (Weeks 1-8)](#phase-1-foundation-weeks-1-8)
3. [Phase 2: AI & Analytics (Weeks 9-16)](#phase-2-ai--analytics-weeks-9-16)
4. [Phase 3: Collaboration & Enterprise (Weeks 17-24)](#phase-3-collaboration--enterprise-weeks-17-24)
5. [Phase 4: Performance & Polish (Weeks 25-30)](#phase-4-performance--polish-weeks-25-30)
6. [Implementation Best Practices](#implementation-best-practices)
7. [Summary Timeline](#summary-timeline)

---

## Competitive Gap Analysis

### vs Power BI (Market Leader)

| Feature | Power BI | Bheem DataViz | Priority |
|---------|----------|---------------|----------|
| 600+ Connectors | ✅ | 5 implemented | P1 |
| Power Query ETL | ✅ Full M language | Basic SQL transforms | P2 |
| DAX Calculations | ✅ 500+ functions | 6 aggregations only | P1 |
| Copilot AI | ✅ NL queries, insights | Scaffolded only | P1 |
| Row-Level Security | ✅ Dynamic filters | Not implemented | P1 |
| Real-time Streaming | ✅ Push/stream datasets | Not implemented | P3 |
| Mobile Apps | ✅ Native iOS/Android | Not implemented | P3 |
| Embed SDK | ✅ Full JavaScript SDK | Not implemented | P1 |

### vs Tableau

| Feature | Tableau | Bheem DataViz | Priority |
|---------|---------|---------------|----------|
| Tableau Prep | ✅ Visual ETL | Basic transforms | P2 |
| Ask Data/Pulse | ✅ NL queries | Scaffolded | P1 |
| LOD Expressions | ✅ Advanced calculations | Not implemented | P2 |
| Story Points | ✅ Narrative visualization | Not implemented | P3 |

### vs Open Source (Metabase/Superset)

**Advantages Bheem DataViz Already Has:**
- ✅ Better semantic layer than Metabase
- ✅ Transform builder (Superset relies on external ETL)
- ✅ BheemFlow automation integration
- ✅ Flat pricing ($49/month vs per-user)

**Gaps vs Open Source:**
- Metabot AI (Metabase has better AI than current Bheem)
- 50+ visualizations (Superset)
- Embedded analytics SDK (both have this)

### Complete Feature Matrix

| Category | Feature | Power BI | Tableau | Metabase | Superset | Bheem DataViz |
|----------|---------|----------|---------|----------|----------|---------------|
| **Connectivity** | PostgreSQL | ✅ | ✅ | ✅ | ✅ | ✅ |
| | MySQL | ✅ | ✅ | ✅ | ✅ | ✅ |
| | MongoDB | ✅ | ✅ | ✅ | ✅ | ✅ |
| | BigQuery | ✅ | ✅ | ✅ | ✅ | 🟡 Scaffolded |
| | Snowflake | ✅ | ✅ | ✅ | ✅ | 🟡 Scaffolded |
| | 100+ Connectors | ✅ | ✅ | ⚠️ | ⚠️ | ❌ |
| **Transforms** | Visual ETL | ✅ | ✅ | ⚠️ | ❌ | ✅ Basic |
| | Data Profiling | ✅ | ✅ | ❌ | ❌ | ❌ |
| | Incremental Refresh | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Modeling** | Semantic Layer | ✅ | ✅ | ❌ | ⚠️ | ✅ Basic |
| | DAX/Calculations | ✅ | ✅ LOD | ⚠️ | ⚠️ | ⚠️ Basic |
| | Time Intelligence | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ Basic |
| **Visualization** | Chart Types | 40+ | 50+ | 20+ | 50+ | 12 |
| | Drill Down | ✅ | ✅ | ✅ | ✅ | ❌ |
| | Conditional Format | ✅ | ✅ | ⚠️ | ⚠️ | ❌ |
| | Advanced Slicers | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ Basic |
| **AI/ML** | NL Queries | ✅ Copilot | ✅ Pulse | ✅ Metabot | ❌ | 🟡 Scaffolded |
| | Auto Insights | ✅ | ✅ | ❌ | ❌ | 🟡 Scaffolded |
| | Forecasting | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Collaboration** | Workspaces | ✅ | ✅ | ✅ | ✅ | ❌ |
| | Row-Level Security | ✅ | ✅ | ⚠️ | ✅ | ❌ |
| | Subscriptions | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| | Alerts | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| **Admin** | Audit Logs | ✅ | ✅ | ⚠️ | ⚠️ | ❌ |
| | Usage Analytics | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ Basic |
| **Developer** | REST API | ✅ | ✅ | ✅ | ✅ | ⚠️ Partial |
| | Embed SDK | ✅ | ✅ | ✅ | ✅ | ❌ |

**Legend:** ✅ Full | ⚠️ Partial | 🟡 Scaffolded | ❌ Missing

---

## Phase 1: Foundation (Weeks 1-8)

### Critical MVP Features

These features are blocking production use and must be implemented first.

---

### 1.1 Advanced Slicers & Filters (Weeks 1-3)

**Current Gap:** Basic dropdown filters only; no date ranges, relative dates, hierarchy slicers

#### Week 1: Backend Filter Framework

```
Day 1-2: Design filter schema
├── Create FilterConfig Pydantic model
├── Support types: dropdown, list, tile, between, relative_date, date_range, hierarchy
└── Add to SavedChart and Dashboard models

Day 3-4: Implement filter processing service
├── backend/app/services/filter_service.py
├── Parse filter expressions to SQL WHERE clauses
└── Handle relative date calculations (last N days/weeks/months)

Day 5: API endpoints
├── GET /charts/{id}/filter-options (enhanced)
├── POST /charts/{id}/filters (save filter state)
└── GET /dashboards/{id}/global-filters
```

#### Week 2: Frontend Slicer Components

```
Day 1-2: Create slicer component library
├── frontend/src/components/filters/DropdownSlicer.tsx
├── frontend/src/components/filters/DateRangeSlicer.tsx
├── frontend/src/components/filters/RelativeDateSlicer.tsx
├── frontend/src/components/filters/NumericRangeSlicer.tsx
└── frontend/src/components/filters/HierarchySlicer.tsx

Day 3-4: Integrate with ChartBuilder
├── Add filter panel to chart configuration
├── Implement filter state management (Zustand)
└── Connect filters to chart re-rendering

Day 5: Dashboard-level filters
├── Global filter bar component
├── Cross-filter interactions between charts
└── Filter sync across dashboard widgets
```

#### Week 3: Testing & Polish

```
├── Unit tests for filter service
├── Integration tests for filter API
├── E2E tests for slicer interactions
└── Performance optimization for large filter lists
```

#### Files to Create/Modify

```
backend/
├── app/schemas/filter.py (new)
├── app/services/filter_service.py (new)
├── app/api/v1/endpoints/charts.py (modify)
└── app/api/v1/endpoints/dashboards.py (modify)

frontend/src/
├── components/filters/ (new directory)
│   ├── index.ts
│   ├── DropdownSlicer.tsx
│   ├── DateRangeSlicer.tsx
│   ├── RelativeDateSlicer.tsx
│   ├── NumericRangeSlicer.tsx
│   ├── HierarchySlicer.tsx
│   └── FilterPanel.tsx
├── stores/filterStore.ts (new - Zustand)
└── pages/ChartBuilder.tsx (modify)
```

#### Slicer Types Schema

```typescript
interface SlicerConfig {
  type:
    | 'dropdown'        // Single/multi-select dropdown
    | 'list'            // Vertical list with checkboxes
    | 'tile'            // Horizontal button tiles
    | 'between'         // Numeric range slider
    | 'relative_date'   // Last N days/weeks/months
    | 'date_range'      // Calendar date picker
    | 'hierarchy'       // Expandable tree
    | 'search';         // Type-ahead search

  // Common options
  multiSelect: boolean;
  selectAll: boolean;
  searchEnabled: boolean;

  // For date slicers
  dateConfig?: {
    granularity: 'day' | 'week' | 'month' | 'quarter' | 'year';
    relativeOptions: Array<{
      label: string;
      value: number;
      unit: 'day' | 'week' | 'month' | 'year';
    }>;
  };

  // For numeric slicers
  numericConfig?: {
    min: number;
    max: number;
    step: number;
    format: string;
  };
}
```

#### Best Practices

- Use debouncing (300ms) for filter changes to avoid excessive API calls
- Implement filter caching to avoid re-fetching filter options
- Support URL state for shareable filtered views
- Use React Query for filter option caching

---

### 1.2 Drill-Down & Drillthrough (Weeks 3-4)

**Current Gap:** No hierarchy navigation or cross-report drilling

#### Implementation Steps

```
Week 3-4: Drill Implementation

Day 1-2: Backend drill configuration
├── Add drill_config to SavedChart schema
│   {
│     "drill_hierarchy": ["year", "quarter", "month", "day"],
│     "drillthrough_target": "dashboard_id" or "chart_id",
│     "drillthrough_filters": [...]
│   }
├── Create drill query builder service
└── Implement drill state tracking

Day 3-4: Frontend drill interactions
├── Add drill icons to chart tooltips
├── Implement drill-down (expand hierarchy)
├── Implement drill-up (collapse hierarchy)
├── Implement drillthrough (navigate to target)
└── Breadcrumb trail for drill path

Day 5: Cross-filtering
├── Click on chart element filters other charts
├── Implement selection highlighting
└── Clear selection button
```

#### Schema Design

```python
class DrillConfig(BaseModel):
    drill_type: Literal["down", "through", "both"]
    hierarchy: List[str]  # ["year", "quarter", "month"]
    drillthrough_target_id: Optional[UUID]
    drillthrough_target_type: Optional[Literal["dashboard", "chart"]]
    pass_filters: bool = True
```

---

### 1.3 Conditional Formatting (Weeks 4-5)

**Current Gap:** No rules-based formatting, data bars, or icon sets

#### Implementation Steps

```
Week 4-5: Conditional Formatting

Day 1-2: Schema and backend
├── ConditionalFormat Pydantic model
│   - color_scale (gradient)
│   - data_bars (in-cell bars)
│   - icon_set (arrows, circles, flags)
│   - rules (if-then formatting)
├── Add conditional_formats to SavedChart
└── Implement format evaluation service

Day 3-4: Frontend implementation
├── ConditionalFormatBuilder component
├── Color scale picker with gradient preview
├── Rule builder with conditions
└── Icon set selector

Day 5: Apply formatting to visuals
├── Table cell formatting
├── KPI card formatting
└── Chart series coloring
```

#### Format Types Schema

```typescript
interface ConditionalFormat {
  type: 'color_scale' | 'data_bars' | 'icon_set' | 'rules';

  colorScale?: {
    minimum: { type: 'lowest' | 'number'; value?: number; color: string };
    center?: { type: 'number' | 'percent'; value: number; color: string };
    maximum: { type: 'highest' | 'number'; value?: number; color: string };
  };

  dataBars?: {
    positiveColor: string;
    negativeColor: string;
    showValue: boolean;
    minValue: 'auto' | number;
    maxValue: 'auto' | number;
  };

  iconSet?: {
    icons: 'arrows' | 'circles' | 'flags' | 'stars';
    thresholds: Array<{ value: number; icon: string }>;
    reverseOrder: boolean;
  };

  rules?: Array<{
    condition: {
      operator: '>' | '>=' | '<' | '<=' | '=' | '!=' | 'between' | 'contains';
      value: any;
      value2?: any; // For 'between'
    };
    format: {
      backgroundColor?: string;
      fontColor?: string;
      bold?: boolean;
      italic?: boolean;
    };
  }>;
}
```

---

### 1.4 Time Intelligence Functions (Weeks 5-6)

**Current Gap:** Only basic previous period comparison; missing YTD, MTD, QTD, rolling calculations

#### Implementation Steps

```
Week 5-6: Time Intelligence

Day 1-2: Time intelligence service
├── backend/app/services/time_intelligence_service.py
├── Implement functions:
│   - YTD, PYTD, YTD_GROWTH
│   - MTD, PMTD, MTD_GROWTH
│   - QTD, PQTD
│   - ROLLING_3M, ROLLING_6M, ROLLING_12M
│   - YOY, MOM, QOQ
│   - RUNNING_TOTAL, RUNNING_AVG
└── SQL generation for each database type

Day 3-4: Semantic model integration
├── Add time_intelligence config to measures
├── Date column auto-detection
└── Fiscal calendar support

Day 5-6: Frontend
├── Time intelligence picker in measure editor
├── Quick measure templates
└── Preview calculated values
```

#### Service Implementation

```python
class TimeIntelligenceService:
    TIME_FUNCTIONS = {
        # Year-to-Date
        "YTD": """
            SUM(CASE WHEN {date_col} >= DATE_TRUNC('year', CURRENT_DATE)
                      AND {date_col} <= CURRENT_DATE
                 THEN {measure_col} ELSE 0 END)
        """,
        "PYTD": """
            SUM(CASE WHEN {date_col} >= DATE_TRUNC('year', CURRENT_DATE - INTERVAL '1 year')
                      AND {date_col} <= CURRENT_DATE - INTERVAL '1 year'
                 THEN {measure_col} ELSE 0 END)
        """,
        "YTD_GROWTH": "(YTD - PYTD) / NULLIF(PYTD, 0) * 100",

        # Month-to-Date
        "MTD": """
            SUM(CASE WHEN {date_col} >= DATE_TRUNC('month', CURRENT_DATE)
                      AND {date_col} <= CURRENT_DATE
                 THEN {measure_col} ELSE 0 END)
        """,
        "PMTD": """
            SUM(CASE WHEN {date_col} >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
                      AND {date_col} <= CURRENT_DATE - INTERVAL '1 month'
                 THEN {measure_col} ELSE 0 END)
        """,

        # Rolling Calculations
        "ROLLING_3M": """
            SUM({measure_col}) OVER (
                ORDER BY {date_col}
                ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
            )
        """,
        "ROLLING_6M": """
            SUM({measure_col}) OVER (
                ORDER BY {date_col}
                ROWS BETWEEN 179 PRECEDING AND CURRENT ROW
            )
        """,
        "ROLLING_12M": """
            SUM({measure_col}) OVER (
                ORDER BY {date_col}
                ROWS BETWEEN 364 PRECEDING AND CURRENT ROW
            )
        """,

        # Period Over Period
        "YOY": "((current_year - prior_year) / NULLIF(prior_year, 0)) * 100",
        "MOM": "((current_month - prior_month) / NULLIF(prior_month, 0)) * 100",
        "QOQ": "((current_quarter - prior_quarter) / NULLIF(prior_quarter, 0)) * 100",

        # Cumulative
        "RUNNING_TOTAL": """
            SUM({measure_col}) OVER (
                ORDER BY {date_col}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            )
        """,
    }

    async def calculate(
        self,
        function_name: str,
        measure_column: str,
        date_column: str,
        connection_id: str,
        table: str,
        filters: List[Filter] = None
    ) -> TimeIntelligenceResult:
        """Generate and execute time intelligence SQL."""
        pass
```

---

### 1.5 Row-Level Security (Weeks 6-7)

**Current Gap:** No dynamic data filtering based on user identity

#### Implementation Steps

```
Week 6-7: Row-Level Security

Day 1-2: Database models
├── backend/app/models/security.py
│   - RLSRule (filter expression per table)
│   - RLSRoleAssignment (user/group mapping)
├── Alembic migration
└── RLS service for filter injection

Day 3-4: RLS management API
├── POST /api/v1/security/rls-rules
├── GET /api/v1/security/rls-rules
├── PUT /api/v1/security/rls-rules/{id}
├── DELETE /api/v1/security/rls-rules/{id}
└── POST /api/v1/security/rls-rules/{id}/test

Day 5: Query injection
├── Modify query execution to apply RLS filters
├── Support USERNAME(), USERPRINCIPALNAME() functions
└── Handle multiple rules (AND/OR logic)

Day 6-7: Frontend
├── RLS management page
├── Rule builder with expression editor
└── User/group assignment interface
```

#### RLS Models

```python
# backend/app/models/security.py
from sqlalchemy import Column, String, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class RLSRule(Base):
    __tablename__ = "rls_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    semantic_model_id = Column(UUID(as_uuid=True), ForeignKey("semantic_models.id"))
    name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    filter_expression = Column(Text, nullable=False)  # e.g., "[Region] = USERNAME()"
    is_active = Column(Boolean, default=True)

    # Relationships
    roles = relationship("RLSRoleAssignment", back_populates="rule", cascade="all, delete-orphan")

class RLSRoleAssignment(Base):
    __tablename__ = "rls_role_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rls_rules.id"))
    role_type = Column(String(50), nullable=False)  # 'user', 'group', 'email_domain'
    role_value = Column(String(255), nullable=False)  # user_id, group_id, or '@company.com'

    rule = relationship("RLSRule", back_populates="roles")
```

#### RLS Service

```python
# backend/app/services/rls_service.py
class RLSService:
    async def apply_rls_filter(
        self,
        query: str,
        user: User,
        semantic_model_id: str
    ) -> str:
        """Apply RLS filters to a query based on user identity."""
        # Get applicable rules
        rules = await self.get_user_rules(user, semantic_model_id)

        if not rules:
            return query  # No RLS rules

        # Build WHERE clause additions
        filters = []
        for rule in rules:
            # Replace USERNAME() with actual user email
            expression = rule.filter_expression.replace(
                "USERNAME()", f"'{user.email}'"
            )
            # Replace USERPRINCIPALNAME() with user ID
            expression = expression.replace(
                "USERPRINCIPALNAME()", f"'{user.id}'"
            )
            filters.append(f"({expression})")

        # Inject into query
        rls_where = " AND ".join(filters)
        modified_query = self.inject_where_clause(query, rls_where)

        return modified_query

    async def get_user_rules(self, user: User, semantic_model_id: str) -> List[RLSRule]:
        """Get all RLS rules that apply to a user."""
        async with get_db() as db:
            # Query rules where user is assigned directly or via group/domain
            result = await db.execute(
                select(RLSRule)
                .join(RLSRoleAssignment)
                .where(
                    RLSRule.semantic_model_id == semantic_model_id,
                    RLSRule.is_active == True,
                    or_(
                        and_(RLSRoleAssignment.role_type == 'user',
                             RLSRoleAssignment.role_value == str(user.id)),
                        and_(RLSRoleAssignment.role_type == 'email_domain',
                             user.email.endswith(RLSRoleAssignment.role_value)),
                    )
                )
            )
            return result.scalars().all()
```

#### RLS Rule Expression Examples

```sql
-- Filter by user's region (user attribute lookup)
[Region] = USERLOOKUP('region')

-- Filter by user's email domain
[Company] IN (SELECT company FROM user_companies WHERE email = USERNAME())

-- Dynamic date filter based on user's data retention policy
[Date] >= DATEADD('day', -USERLOOKUP('data_retention_days'), CURRENT_DATE)

-- Manager sees their team's data
[ManagerEmail] = USERNAME() OR [EmployeeEmail] = USERNAME()
```

---

### 1.6 Scheduled Refresh & Alerts (Weeks 7-8)

**Current Gap:** No automatic data refresh or threshold-based notifications

#### Implementation Steps

```
Week 7-8: Scheduling & Alerts

Day 1-2: Background job infrastructure
├── Add Celery or APScheduler to backend
├── Redis as task broker
├── backend/app/tasks/scheduler.py
└── Schedule management service

Day 3-4: Scheduled refresh
├── Refresh model (connection, schedule, status)
├── CRON expression support
├── Refresh execution logic
└── Failure notification

Day 5-6: Alert system
├── Alert model (metric, condition, recipients)
├── Alert evaluation service
├── Threshold operators: >, <, =, change_by %
└── Email/webhook notification

Day 7-8: Frontend
├── Schedule configuration UI
├── Alert builder with condition preview
└── Subscription management page
```

#### Subscription & Alert Models

```python
# backend/app/models/subscription.py
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'scheduled', 'alert'

    # Target
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id"), nullable=True)
    chart_id = Column(UUID(as_uuid=True), ForeignKey("saved_charts.id"), nullable=True)

    # Schedule (for scheduled type)
    schedule_cron = Column(String(100))  # "0 9 * * 1-5" = 9am weekdays
    timezone = Column(String(50), default="UTC")

    # Alert condition (for alert type)
    alert_metric = Column(String(255))
    alert_operator = Column(String(20))  # '>', '<', '=', '>=', '<=', 'change_by'
    alert_threshold = Column(Float)
    alert_last_value = Column(Float)

    # Recipients
    recipients = Column(JSONB)  # [{"type": "email", "value": "user@example.com"}]

    # Status
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    next_run = Column(DateTime)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Celery Task Setup

```python
# backend/app/tasks/refresh_tasks.py
from celery import Celery
from app.core.config import settings

celery_app = Celery('dataviz', broker=settings.REDIS_URL)

@celery_app.task
def refresh_connection_data(connection_id: str):
    """Refresh data for a connection on schedule."""
    # Implementation
    pass

@celery_app.task
def evaluate_alerts():
    """Check all active alerts and send notifications."""
    # Implementation
    pass

@celery_app.task
def send_scheduled_report(subscription_id: str):
    """Generate and send a scheduled report."""
    # Implementation
    pass

# Schedule configuration
celery_app.conf.beat_schedule = {
    'evaluate-alerts-every-5-minutes': {
        'task': 'app.tasks.refresh_tasks.evaluate_alerts',
        'schedule': 300.0,  # 5 minutes
    },
}
```

#### Alert Evaluation Service

```python
# backend/app/services/alert_service.py
class AlertService:
    async def evaluate_alerts(self):
        """Evaluate all active alerts and trigger notifications."""
        active_alerts = await self.get_active_alerts()

        for alert in active_alerts:
            try:
                current_value = await self.calculate_metric(alert)

                if self.should_trigger(alert, current_value):
                    await self.send_alert(alert, current_value)
                    await self.update_last_triggered(alert, current_value)

            except Exception as e:
                await self.log_alert_error(alert, e)

    def should_trigger(self, alert: Subscription, value: float) -> bool:
        """Determine if an alert condition is met."""
        ops = {
            '>': lambda v, t: v > t,
            '<': lambda v, t: v < t,
            '>=': lambda v, t: v >= t,
            '<=': lambda v, t: v <= t,
            '=': lambda v, t: v == t,
            'change_by': lambda v, t: abs(v - (alert.alert_last_value or 0)) > t,
        }
        return ops[alert.alert_operator](value, alert.alert_threshold)

    async def send_alert(self, alert: Subscription, value: float):
        """Send alert notification to all recipients."""
        for recipient in alert.recipients:
            if recipient['type'] == 'email':
                await self.send_email_alert(recipient['value'], alert, value)
            elif recipient['type'] == 'webhook':
                await self.send_webhook_alert(recipient['value'], alert, value)
```

---

## Phase 2: AI & Analytics (Weeks 9-16)

### 2.1 Kodee NL-to-SQL (Weeks 9-12)

**Current Gap:** AI endpoints scaffolded but not implemented

#### Week 9-10: Core NL Engine

```
Day 1-3: Schema context builder
├── Extract table/column metadata
├── Include semantic model context
├── Sample data for context
└── Foreign key relationships

Day 4-5: OpenAI integration
├── Prompt engineering for SQL generation
├── Few-shot examples per database type
└── Response parsing and validation

Day 6-10: Query validation & execution
├── SQL syntax validation
├── Security checks (no DROP, DELETE, etc.)
├── Query execution with timeout
└── Result formatting
```

#### Week 11-12: Frontend & Refinement

```
├── Chat interface for Kodee
├── Query explanation display
├── Suggested questions based on schema
├── Conversation history
└── Feedback loop for improving prompts
```

#### NL Service Implementation

```python
# backend/app/services/kodee_service.py
class KodeeNLService:
    SYSTEM_PROMPT = """
    You are a SQL expert assistant. Convert natural language questions to SQL queries.

    Rules:
    1. Only generate SELECT statements
    2. Use table and column names exactly as provided
    3. Apply appropriate aggregations for metrics
    4. Include relevant JOINs based on relationships
    5. Limit results to 1000 rows unless specified
    6. Use aliases for calculated columns

    Database: {database_type}

    Schema:
    {schema_context}

    Semantic Model (business terms):
    {semantic_context}

    Foreign Key Relationships:
    {relationships}

    Sample Data (first 3 rows per table):
    {sample_data}
    """

    async def process_question(
        self,
        question: str,
        connection_id: str,
        semantic_model_id: Optional[str] = None
    ) -> NLQueryResult:
        # 1. Build context
        schema = await self.get_schema_context(connection_id)
        semantic = await self.get_semantic_context(semantic_model_id) if semantic_model_id else None
        relationships = await self.get_relationships(connection_id)
        samples = await self.get_sample_data(connection_id)

        # 2. Build prompt
        prompt = self.SYSTEM_PROMPT.format(
            database_type=await self.get_db_type(connection_id),
            schema_context=schema,
            semantic_context=semantic or "Not available",
            relationships=relationships,
            sample_data=samples
        )

        # 3. Call OpenAI
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        # 4. Parse response
        result = json.loads(response.choices[0].message.content)
        sql = result.get("sql")
        explanation = result.get("explanation")

        # 5. Validate SQL (security check)
        validated_sql = await self.validate_query(sql, connection_id)

        # 6. Suggest visualization
        chart_type = self.suggest_chart(question, sql)

        return NLQueryResult(
            question=question,
            sql=validated_sql,
            explanation=explanation,
            suggested_chart=chart_type,
            confidence=result.get("confidence", 0.8)
        )

    async def validate_query(self, sql: str, connection_id: str) -> str:
        """Validate SQL for security and syntax."""
        # Block dangerous operations
        forbidden = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        sql_upper = sql.upper()
        for keyword in forbidden:
            if keyword in sql_upper:
                raise SecurityError(f"Forbidden SQL operation: {keyword}")

        # Validate syntax by preparing (not executing) the query
        # ...

        return sql

    def suggest_chart(self, question: str, sql: str) -> str:
        """Suggest appropriate chart type based on query."""
        question_lower = question.lower()

        if any(word in question_lower for word in ['trend', 'over time', 'by month', 'by year']):
            return 'line'
        elif any(word in question_lower for word in ['compare', 'vs', 'versus', 'comparison']):
            return 'bar'
        elif any(word in question_lower for word in ['distribution', 'breakdown', 'share', 'percent']):
            return 'pie'
        elif any(word in question_lower for word in ['top', 'ranking', 'best', 'worst']):
            return 'horizontal_bar'
        elif 'GROUP BY' in sql.upper() and sql.upper().count(',') > 1:
            return 'grouped_bar'
        else:
            return 'table'
```

---

### 2.2 Quick Insights (Weeks 13-14)

#### Implementation Steps

```
Week 13-14: Auto-Discovery Insights

Day 1-3: Statistical analysis service
├── Trend detection (linear regression)
├── Outlier detection (IQR, Z-score)
├── Correlation analysis
└── Distribution analysis

Day 4-5: Insight ranking
├── Score insights by significance
├── Filter redundant insights
└── Generate natural language descriptions

Day 6-7: Frontend
├── Insights panel on data preview
├── Insight cards with mini-visualizations
└── "Explain this" button on charts
```

#### Insights Service

```python
# backend/app/services/insights_service.py
class InsightsService:
    INSIGHT_TYPES = [
        "trend",           # Upward/downward trends
        "outlier",         # Statistical outliers
        "seasonality",     # Repeating patterns
        "correlation",     # Column relationships
        "concentration",   # Value distribution skew
        "segment",         # Notable subgroups
        "change_point",    # Sudden shifts
    ]

    async def analyze_dataset(
        self,
        connection_id: str,
        table: str,
        columns: List[str]
    ) -> List[Insight]:
        insights = []

        # Run parallel analysis
        tasks = [
            self.detect_trends(connection_id, table, columns),
            self.detect_outliers(connection_id, table, columns),
            self.detect_correlations(connection_id, table, columns),
            self.detect_segments(connection_id, table, columns),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful insights
        for result in results:
            if isinstance(result, list):
                insights.extend(result)

        # Rank and return top insights
        ranked = self.rank_insights(insights)
        return ranked[:10]  # Top 10 insights

    async def detect_trends(self, connection_id: str, table: str, columns: List[str]) -> List[Insight]:
        """Detect upward/downward trends in time series data."""
        insights = []
        # Implementation using linear regression
        return insights

    async def detect_outliers(self, connection_id: str, table: str, columns: List[str]) -> List[Insight]:
        """Detect statistical outliers using IQR method."""
        insights = []
        # Implementation
        return insights

    def rank_insights(self, insights: List[Insight]) -> List[Insight]:
        """Rank insights by significance and novelty."""
        return sorted(insights, key=lambda x: x.significance_score, reverse=True)
```

---

### 2.3 Cloud Connectors (Weeks 15-16)

**Current Gap:** BigQuery, Snowflake scaffolded but not implemented

#### Week 15-16: Cloud Data Warehouses

```
Day 1-3: BigQuery connector
├── Service account authentication
├── Schema introspection
├── Query execution
└── Cost estimation

Day 4-6: Snowflake connector
├── Key-pair authentication
├── Warehouse selection
├── Schema browser
└── Query execution

Day 7-8: Testing & documentation
```

#### BigQuery Service

```python
# backend/app/services/bigquery_service.py
from google.cloud import bigquery
from google.oauth2 import service_account

class BigQueryService:
    async def connect(self, credentials_json: dict, project_id: str) -> bigquery.Client:
        """Create BigQuery client from service account credentials."""
        credentials = service_account.Credentials.from_service_account_info(
            credentials_json,
            scopes=["https://www.googleapis.com/auth/bigquery.readonly"]
        )
        return bigquery.Client(credentials=credentials, project=project_id)

    async def test_connection(self, client: bigquery.Client) -> bool:
        """Test BigQuery connection."""
        try:
            list(client.list_datasets(max_results=1))
            return True
        except Exception:
            return False

    async def get_datasets(self, client: bigquery.Client) -> List[str]:
        """List all datasets in the project."""
        return [ds.dataset_id for ds in client.list_datasets()]

    async def get_tables(self, client: bigquery.Client, dataset: str) -> List[Table]:
        """List tables in a dataset with metadata."""
        tables = client.list_tables(dataset)
        return [
            {
                "name": t.table_id,
                "type": t.table_type,
                "full_id": f"{t.project}.{t.dataset_id}.{t.table_id}"
            }
            for t in tables
        ]

    async def get_columns(self, client: bigquery.Client, dataset: str, table: str) -> List[Column]:
        """Get column information for a table."""
        table_ref = client.get_table(f"{dataset}.{table}")
        return [
            {
                "name": field.name,
                "type": field.field_type,
                "mode": field.mode,
                "description": field.description
            }
            for field in table_ref.schema
        ]

    async def execute_query(
        self,
        client: bigquery.Client,
        sql: str,
        timeout: int = 30
    ) -> QueryResult:
        """Execute a BigQuery SQL query."""
        job_config = bigquery.QueryJobConfig(
            use_query_cache=True,
            maximum_bytes_billed=10 * 1024 * 1024 * 1024  # 10 GB limit
        )

        job = client.query(sql, job_config=job_config)
        results = job.result(timeout=timeout)

        return QueryResult(
            columns=[f.name for f in results.schema],
            rows=[dict(row) for row in results],
            total_bytes_processed=job.total_bytes_processed,
            cache_hit=job.cache_hit
        )

    async def estimate_query_cost(self, client: bigquery.Client, sql: str) -> float:
        """Estimate query cost in USD."""
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = client.query(sql, job_config=job_config)

        bytes_processed = job.total_bytes_processed
        # BigQuery pricing: $5 per TB
        cost = (bytes_processed / (1024 ** 4)) * 5
        return round(cost, 4)
```

#### Snowflake Service

```python
# backend/app/services/snowflake_service.py
import snowflake.connector
from cryptography.hazmat.primitives import serialization

class SnowflakeService:
    async def connect(
        self,
        account: str,
        user: str,
        private_key_pem: str,
        warehouse: str,
        database: str = None,
        schema: str = None
    ) -> snowflake.connector.SnowflakeConnection:
        """Create Snowflake connection using key-pair authentication."""
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )

        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        return snowflake.connector.connect(
            account=account,
            user=user,
            private_key=private_key_bytes,
            warehouse=warehouse,
            database=database,
            schema=schema
        )

    async def get_warehouses(self, conn) -> List[str]:
        """List available warehouses."""
        cursor = conn.cursor()
        cursor.execute("SHOW WAREHOUSES")
        return [row[0] for row in cursor.fetchall()]

    async def get_databases(self, conn) -> List[str]:
        """List available databases."""
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        return [row[1] for row in cursor.fetchall()]

    async def get_schemas(self, conn, database: str) -> List[str]:
        """List schemas in a database."""
        cursor = conn.cursor()
        cursor.execute(f"SHOW SCHEMAS IN DATABASE {database}")
        return [row[1] for row in cursor.fetchall()]

    async def get_tables(self, conn, database: str, schema: str) -> List[Table]:
        """List tables in a schema."""
        cursor = conn.cursor()
        cursor.execute(f"SHOW TABLES IN {database}.{schema}")
        return [
            {"name": row[1], "database": database, "schema": schema}
            for row in cursor.fetchall()
        ]

    async def execute_query(self, conn, sql: str, timeout: int = 30) -> QueryResult:
        """Execute a Snowflake SQL query."""
        cursor = conn.cursor()
        cursor.execute(sql)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        return QueryResult(
            columns=columns,
            rows=[dict(zip(columns, row)) for row in rows]
        )
```

---

## Phase 3: Collaboration & Enterprise (Weeks 17-24)

### 3.1 Workspaces (Weeks 17-18)

```
Week 17-18: Team Workspaces

Day 1-3: Workspace model
├── Workspace (name, description, owner)
├── WorkspaceMember (user, role: Admin/Member/Viewer)
├── Move dashboards/charts to workspace scope
└── API endpoints

Day 4-6: Permission system
├── Workspace-level permissions
├── Object-level overrides
└── Permission checking middleware

Day 7-8: Frontend
├── Workspace switcher
├── Member management UI
└── Permission indicators
```

#### Workspace Models

```python
# backend/app/models/workspace.py
class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_personal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("WorkspaceMember", back_populates="workspace")
    dashboards = relationship("Dashboard", back_populates="workspace")

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    role = Column(String(50), nullable=False)  # 'admin', 'member', 'viewer'

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")
```

---

### 3.2 Audit Logging (Weeks 19-20)

```
Week 19-20: Audit System

Day 1-3: Audit infrastructure
├── AuditLog model
├── Audit middleware (auto-capture)
├── Sensitive data sanitization
└── Async logging (don't block requests)

Day 4-5: Audit API
├── GET /api/v1/admin/audit-logs
├── Filtering by user, action, resource
└── Export to CSV

Day 6-8: Admin dashboard
├── Activity timeline
├── User activity summary
└── Security alerts
```

#### Audit Log Model

```python
# backend/app/models/audit.py
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Actor
    user_id = Column(UUID(as_uuid=True), index=True)
    user_email = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Action
    action = Column(String(100), index=True)  # 'dashboard.view', 'chart.create', etc.
    resource_type = Column(String(50), index=True)
    resource_id = Column(UUID(as_uuid=True), index=True)
    resource_name = Column(String(255))

    # Details
    request_method = Column(String(10))
    request_path = Column(String(500))
    request_body = Column(JSONB)  # Sanitized, no passwords
    response_status = Column(Integer)
    duration_ms = Column(Integer)

    # Context
    workspace_id = Column(UUID(as_uuid=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

# Audit Actions
AUDIT_ACTIONS = {
    # Authentication
    "auth.login": "User logged in",
    "auth.logout": "User logged out",
    "auth.login_failed": "Failed login attempt",

    # Dashboards
    "dashboard.view": "Viewed dashboard",
    "dashboard.create": "Created dashboard",
    "dashboard.update": "Updated dashboard",
    "dashboard.delete": "Deleted dashboard",
    "dashboard.share": "Shared dashboard",

    # Charts
    "chart.view": "Viewed chart",
    "chart.create": "Created chart",
    "chart.update": "Updated chart",
    "chart.delete": "Deleted chart",
    "chart.export": "Exported chart",

    # Data
    "connection.create": "Created connection",
    "connection.test": "Tested connection",
    "query.execute": "Executed query",
    "data.export": "Exported data",

    # Admin
    "user.invite": "Invited user",
    "role.assign": "Assigned role",
    "settings.update": "Updated settings",
}
```

#### Audit Middleware

```python
# backend/app/middleware/audit.py
from starlette.middleware.base import BaseHTTPMiddleware
import time

class AuditMiddleware(BaseHTTPMiddleware):
    AUDITED_PATHS = ['/api/v1/dashboards', '/api/v1/charts', '/api/v1/connections']
    EXCLUDED_METHODS = ['OPTIONS', 'HEAD']

    async def dispatch(self, request: Request, call_next):
        # Skip non-audited paths
        if not any(request.url.path.startswith(p) for p in self.AUDITED_PATHS):
            return await call_next(request)

        if request.method in self.EXCLUDED_METHODS:
            return await call_next(request)

        # Capture request details
        start_time = time.time()
        request_body = await self.safe_get_body(request)

        # Process request
        response = await call_next(request)

        # Log audit entry (async, non-blocking)
        asyncio.create_task(self.log_audit(
            request=request,
            response=response,
            request_body=request_body,
            duration_ms=int((time.time() - start_time) * 1000)
        ))

        return response

    async def safe_get_body(self, request: Request) -> dict:
        """Safely extract and sanitize request body."""
        try:
            body = await request.json()
            # Remove sensitive fields
            return self.sanitize_body(body)
        except:
            return {}

    def sanitize_body(self, body: dict) -> dict:
        """Remove sensitive data from request body."""
        sensitive_keys = ['password', 'secret', 'token', 'key', 'credential']
        sanitized = {}
        for k, v in body.items():
            if any(s in k.lower() for s in sensitive_keys):
                sanitized[k] = '[REDACTED]'
            elif isinstance(v, dict):
                sanitized[k] = self.sanitize_body(v)
            else:
                sanitized[k] = v
        return sanitized
```

---

### 3.3 Embed SDK (Weeks 21-24)

```
Week 21-24: JavaScript Embed SDK

Week 21: Token & authentication
├── Embed token generation endpoint
├── Token scoping (specific dashboard/chart)
└── Token expiration handling

Week 22: SDK core
├── BheemEmbed class
├── iframe communication (postMessage)
├── Event system (loaded, error, dataSelected)
└── Filter/slicer control

Week 23: SDK features
├── setFilters(), getFilters()
├── refresh(), exportData()
├── Theme customization
└── Layout options

Week 24: Documentation & examples
├── npm package setup
├── React wrapper component
├── Documentation site
└── Example applications
```

#### Embed SDK TypeScript

```typescript
// sdk/javascript/src/BheemEmbed.ts

export interface EmbedConfig {
  // Authentication
  accessToken: string;
  tokenType: 'AAD' | 'Embed';

  // Target
  type: 'dashboard' | 'chart' | 'report';
  id: string;

  // Container
  container: HTMLElement;

  // Embed URL (optional, defaults to production)
  embedUrl?: string;

  // Display options
  settings?: {
    navContentPaneEnabled?: boolean;
    filterPaneEnabled?: boolean;
    background?: 'transparent' | 'default';
    layoutType?: 'desktop' | 'mobile' | 'custom';
  };

  // Initial state
  filters?: EmbedFilter[];
  slicers?: EmbedSlicer[];
  bookmark?: string;
  pageName?: string;
}

export interface EmbedFilter {
  $schema: string;
  target: {
    table: string;
    column: string;
  };
  operator: 'In' | 'NotIn' | 'Contains' | 'StartsWith' | 'Between';
  values: any[];
}

export interface EmbedSlicer {
  selector: {
    $schema: string;
    visualName: string;
  };
  state: {
    filters: EmbedFilter[];
  };
}

export type EmbedEventType = 'loaded' | 'error' | 'dataSelected' | 'pageChanged' | 'buttonClicked';

export class BheemEmbed {
  private iframe: HTMLIFrameElement;
  private config: EmbedConfig;
  private eventHandlers: Map<EmbedEventType, Function[]>;
  private messageQueue: Map<string, { resolve: Function; reject: Function }>;
  private isLoaded: boolean = false;

  constructor(config: EmbedConfig) {
    this.config = config;
    this.eventHandlers = new Map();
    this.messageQueue = new Map();
    this.initialize();
  }

  private initialize() {
    // Create iframe
    this.iframe = document.createElement('iframe');
    this.iframe.src = this.buildEmbedUrl();
    this.iframe.style.border = 'none';
    this.iframe.style.width = '100%';
    this.iframe.style.height = '100%';
    this.iframe.allow = 'fullscreen';

    // Setup message listener
    window.addEventListener('message', this.handleMessage.bind(this));

    // Append to container
    this.config.container.innerHTML = '';
    this.config.container.appendChild(this.iframe);
  }

  private buildEmbedUrl(): string {
    const baseUrl = this.config.embedUrl || 'https://dataviz.bheemkodee.com/embed';
    const params = new URLSearchParams({
      type: this.config.type,
      id: this.config.id,
      token: this.config.accessToken,
    });

    if (this.config.settings) {
      params.set('settings', JSON.stringify(this.config.settings));
    }

    return `${baseUrl}?${params.toString()}`;
  }

  private handleMessage(event: MessageEvent) {
    // Verify origin
    const allowedOrigins = [
      'https://dataviz.bheemkodee.com',
      this.config.embedUrl?.replace(/\/embed$/, '') || ''
    ];

    if (!allowedOrigins.includes(event.origin)) {
      return;
    }

    const { type, payload, requestId } = event.data;

    // Handle response to a request
    if (requestId && this.messageQueue.has(requestId)) {
      const { resolve, reject } = this.messageQueue.get(requestId)!;
      this.messageQueue.delete(requestId);

      if (type === 'error') {
        reject(new Error(payload.message));
      } else {
        resolve(payload);
      }
      return;
    }

    // Handle events
    switch (type) {
      case 'loaded':
        this.isLoaded = true;
        this.emit('loaded', payload);
        break;
      case 'error':
        this.emit('error', payload);
        break;
      case 'dataSelected':
        this.emit('dataSelected', payload);
        break;
      case 'pageChanged':
        this.emit('pageChanged', payload);
        break;
      case 'buttonClicked':
        this.emit('buttonClicked', payload);
        break;
    }
  }

  private postMessage<T>(type: string, payload?: any): Promise<T> {
    return new Promise((resolve, reject) => {
      const requestId = crypto.randomUUID();

      this.messageQueue.set(requestId, { resolve, reject });

      this.iframe.contentWindow?.postMessage(
        { type, payload, requestId },
        '*'
      );

      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.messageQueue.has(requestId)) {
          this.messageQueue.delete(requestId);
          reject(new Error('Request timeout'));
        }
      }, 30000);
    });
  }

  private emit(event: EmbedEventType, data: any) {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  // Public API

  async setFilters(filters: EmbedFilter[]): Promise<void> {
    return this.postMessage('setFilters', { filters });
  }

  async getFilters(): Promise<EmbedFilter[]> {
    return this.postMessage('getFilters');
  }

  async clearFilters(): Promise<void> {
    return this.postMessage('clearFilters');
  }

  async refresh(): Promise<void> {
    return this.postMessage('refresh');
  }

  async exportData(format: 'csv' | 'xlsx' | 'pdf'): Promise<Blob> {
    const result = await this.postMessage<{ data: string; mimeType: string }>('export', { format });
    const binaryString = atob(result.data);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return new Blob([bytes], { type: result.mimeType });
  }

  async setPage(pageName: string): Promise<void> {
    return this.postMessage('setPage', { pageName });
  }

  async getPages(): Promise<Array<{ name: string; displayName: string }>> {
    return this.postMessage('getPages');
  }

  async print(): Promise<void> {
    return this.postMessage('print');
  }

  async fullscreen(enable: boolean = true): Promise<void> {
    if (enable) {
      this.iframe.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  }

  on(event: EmbedEventType, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }

  off(event: EmbedEventType, handler?: Function): void {
    if (!handler) {
      this.eventHandlers.delete(event);
      return;
    }

    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  destroy(): void {
    window.removeEventListener('message', this.handleMessage.bind(this));
    this.iframe.remove();
    this.eventHandlers.clear();
    this.messageQueue.clear();
  }
}

// React wrapper
export function useBheemEmbed(config: Omit<EmbedConfig, 'container'>) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const embedRef = React.useRef<BheemEmbed | null>(null);

  React.useEffect(() => {
    if (containerRef.current && config.accessToken) {
      embedRef.current = new BheemEmbed({
        ...config,
        container: containerRef.current,
      });

      return () => {
        embedRef.current?.destroy();
      };
    }
  }, [config.accessToken, config.id, config.type]);

  return {
    containerRef,
    embed: embedRef.current,
  };
}
```

---

## Phase 4: Performance & Polish (Weeks 25-30)

### 4.1 Query Caching (Week 25)

```python
# backend/app/services/cache_service.py
import aioredis
import hashlib
import json
from cachetools import TTLCache

class CacheService:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL)
        self.local_cache = TTLCache(maxsize=1000, ttl=60)  # 1-minute local cache

    async def get_or_execute(
        self,
        query_hash: str,
        connection_id: str,
        execute_fn: Callable,
        ttl: int = 300
    ) -> QueryResult:
        """Get cached result or execute query and cache."""
        cache_key = f"query:{connection_id}:{query_hash}"

        # L1: Local memory cache
        if cache_key in self.local_cache:
            return self.local_cache[cache_key]

        # L2: Redis cache
        cached = await self.redis.get(cache_key)
        if cached:
            result = json.loads(cached)
            self.local_cache[cache_key] = result
            return result

        # Execute query
        result = await execute_fn()

        # Cache result
        serialized = json.dumps(result, default=str)
        await self.redis.setex(cache_key, ttl, serialized)
        self.local_cache[cache_key] = result

        return result

    async def invalidate_connection(self, connection_id: str):
        """Invalidate all cached queries for a connection."""
        pattern = f"query:{connection_id}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

        # Clear local cache entries
        to_delete = [k for k in self.local_cache if k.startswith(f"query:{connection_id}:")]
        for key in to_delete:
            del self.local_cache[key]

    @staticmethod
    def hash_query(sql: str, params: dict = None) -> str:
        """Generate cache key from query and params."""
        content = f"{sql}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
```

---

### 4.2 Additional Chart Types (Weeks 26-27)

```
Week 26-27: Visualization Expansion

Charts to add:
├── Treemap (hierarchical data)
├── Waterfall (variance analysis)
├── Sankey (flow diagrams)
├── Heatmap (correlation matrices)
├── Box Plot (statistical distribution)
├── Bullet Chart (performance vs target)
├── Sparklines (inline trends in tables)
└── Matrix/Pivot Table (expandable rows/columns)
```

---

### 4.3 Data Profiling (Weeks 28-29)

```
Week 28-29: Data Quality Analysis

Day 1-3: Profiling service
├── Column statistics (min, max, mean, median, std)
├── Null percentage
├── Distinct count
├── Value distribution (top 10)
└── Data type inference

Day 4-5: Quality scoring
├── Completeness score
├── Uniqueness score
├── Pattern detection
└── Anomaly flags

Day 6-8: Frontend
├── Profile panel in data preview
├── Quality indicators on columns
└── Profiling on transform outputs
```

#### Data Profile Schema

```typescript
interface DataProfile {
  columnName: string;
  dataType: string;

  // Quality Metrics
  totalRows: number;
  validRows: number;
  errorRows: number;
  emptyRows: number;
  qualityPercent: number;

  // Distribution
  distinctCount: number;
  uniquePercent: number;
  minValue: any;
  maxValue: any;

  // For numeric columns
  mean?: number;
  median?: number;
  stdDev?: number;
  percentile25?: number;
  percentile75?: number;

  // For text columns
  minLength?: number;
  maxLength?: number;
  avgLength?: number;

  // Value Distribution (top 10)
  valueDistribution: Array<{
    value: any;
    count: number;
    percent: number;
  }>;
}
```

---

### 4.4 Mobile Optimization (Week 30)

```
Week 30: Responsive Design

Day 1-3: Dashboard mobile layout
├── Responsive grid (single column on mobile)
├── Touch-friendly slicers
└── Swipe navigation between charts

Day 4-5: Chart mobile optimization
├── Responsive chart sizing
├── Simplified tooltips
└── Pinch-to-zoom on charts
```

---

## Implementation Best Practices

### 1. Code Organization

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/       # Route handlers (thin layer)
│   │   └── dependencies.py  # Shared dependencies
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── security.py      # Auth utilities
│   │   └── exceptions.py    # Custom exceptions
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic (thick layer)
│   └── tasks/               # Background jobs
├── alembic/                 # Migrations
└── tests/                   # Test suite

frontend/src/
├── components/
│   ├── common/              # Shared components
│   ├── charts/              # Chart components
│   ├── filters/             # Filter/slicer components
│   └── ui/                  # Primitives
├── pages/                   # Route pages
├── stores/                  # Zustand stores
├── services/                # API clients
├── hooks/                   # Custom hooks
└── utils/                   # Utilities
```

### 2. API Design Principles

```python
# Use consistent response structure
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any]
    error: Optional[ErrorDetail]
    meta: Optional[MetaInfo]

# Use proper HTTP methods
POST   /connections          # Create
GET    /connections          # List
GET    /connections/{id}     # Get one
PUT    /connections/{id}     # Full update
PATCH  /connections/{id}     # Partial update
DELETE /connections/{id}     # Delete

# Use query params for filtering
GET /dashboards?workspace_id=xxx&is_public=true&limit=10&offset=0

# Use request body for complex operations
POST /charts/{id}/render
{
  "filters": [...],
  "date_range": {...}
}
```

### 3. Error Handling

```python
# backend/app/core/exceptions.py
class DataVizException(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code

class ConnectionError(DataVizException):
    def __init__(self, message: str):
        super().__init__(message, "CONNECTION_ERROR", 400)

class QueryTimeoutError(DataVizException):
    def __init__(self):
        super().__init__("Query exceeded timeout limit", "QUERY_TIMEOUT", 408)

class RLSViolationError(DataVizException):
    def __init__(self):
        super().__init__("Access denied by row-level security", "RLS_VIOLATION", 403)

# Global exception handler
@app.exception_handler(DataVizException)
async def dataviz_exception_handler(request: Request, exc: DataVizException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )
```

### 4. Testing Strategy

```python
# Unit tests for services
async def test_time_intelligence_ytd():
    service = TimeIntelligenceService()
    result = await service.calculate(
        function_name="YTD",
        measure_column="revenue",
        date_column="order_date",
        connection_id="test-conn",
        table="orders"
    )
    assert result.value > 0

# Integration tests for APIs
async def test_create_dashboard():
    response = await client.post(
        "/api/v1/dashboards",
        json={"name": "Test", "workspace_id": workspace_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["success"] == True

# E2E tests with Playwright
async def test_chart_builder_flow():
    await page.goto("/charts/new")
    await page.click("[data-testid=connection-select]")
    await page.click("text=Test Connection")
    await page.click("[data-testid=table-select]")
    await page.click("text=orders")
    # ... continue flow
```

### 5. Performance Guidelines

```python
# Use async everywhere
async def get_tables(connection_id: str) -> List[Table]:
    async with get_db() as db:
        result = await db.execute(...)
        return result.scalars().all()

# Use connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300
)

# Implement pagination
@router.get("/dashboards")
async def list_dashboards(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0)
):
    ...

# Use caching for expensive operations
@cache(ttl=300)
async def get_schema_metadata(connection_id: str):
    ...

# Debounce frontend requests
const debouncedSearch = useDebouncedCallback(
    (value) => fetchResults(value),
    300
);
```

### 6. Security Checklist

- [ ] Encrypt database passwords at rest (Fernet)
- [ ] Use parameterized queries (prevent SQL injection)
- [ ] Validate and sanitize all user inputs
- [ ] Implement rate limiting on sensitive endpoints
- [ ] Log all authentication attempts
- [ ] Rotate JWT secrets regularly
- [ ] Use HTTPS in production
- [ ] Implement CORS properly
- [ ] Sanitize error messages (no stack traces in production)
- [ ] Apply RLS before every query
- [ ] Audit log all data access
- [ ] Implement CSRF protection

---

## Summary Timeline

| Phase | Weeks | Features | Effort |
|-------|-------|----------|--------|
| **Phase 1: Foundation** | 1-8 | Slicers, Drill-down, Conditional Formatting, Time Intelligence, RLS, Scheduling | 8 weeks |
| **Phase 2: AI & Analytics** | 9-16 | Kodee NL-to-SQL, Quick Insights, BigQuery/Snowflake | 8 weeks |
| **Phase 3: Enterprise** | 17-24 | Workspaces, Audit Logs, Embed SDK | 8 weeks |
| **Phase 4: Polish** | 25-30 | Caching, More Charts, Data Profiling, Mobile | 6 weeks |

**Total: ~30 weeks (7-8 months) for competitive parity**

---

## Priority Recommendation

**Start with Phase 1 (Weeks 1-8)** as these features are critical blockers:

1. **Advanced Slicers** - Users can't explore data effectively without them
2. **Drill-down** - Essential for any BI tool
3. **Time Intelligence** - Required for business reporting
4. **RLS** - Required for multi-tenant deployments
5. **Scheduled Refresh** - Users expect automatic updates

After Phase 1, the platform will be production-ready for most use cases. Phase 2-4 features add competitive differentiation and enterprise capabilities.

---

## Success Metrics

Track progress with these KPIs:

| Metric | Current | Target (Phase 1) | Target (Full) |
|--------|---------|------------------|---------------|
| Feature Coverage vs Power BI | 45% | 65% | 85% |
| Chart Types | 12 | 15 | 25+ |
| Data Connectors | 5 | 7 | 15+ |
| AI Features | 0% | 30% | 80% |
| Enterprise Features | 15% | 50% | 90% |

---

**Document Version:** 1.0.0
**Created:** 2026-01-30
**Maintained By:** Bheem Development Team
