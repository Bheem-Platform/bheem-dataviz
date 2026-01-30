# Quick Charts Feature - Product Scope Document

> **Feature Name:** Quick Charts / Intelligent Auto-Chart Generation
> **Priority:** P1 - High Impact Feature
> **Estimated Effort:** 2-3 weeks
> **Status:** Scoping Complete

---

## 1. Executive Summary

### What is Quick Charts?

Quick Charts is an intelligent feature that automatically analyzes connected data sources and generates relevant, ready-to-use chart visualizations. When a user connects a database or uploads a CSV, the system:

1. **Profiles the data** - Analyzes column types, cardinality, relationships
2. **Recommends charts** - Suggests 3-5 optimal visualizations
3. **Generates configs** - Creates complete chart configurations
4. **Enables one-click add** - User can add to dashboard instantly

### User Journey

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         QUICK CHARTS USER FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
    │   Connect    │       │   System     │       │    View      │
    │   Database   │──────>│   Analyzes   │──────>│   Quick      │
    │   or CSV     │       │   Data       │       │   Charts     │
    └──────────────┘       └──────────────┘       └──────────────┘
                                                         │
                           ┌─────────────────────────────┼─────────────────┐
                           │                             │                 │
                           ▼                             ▼                 ▼
                    ┌──────────────┐           ┌──────────────┐    ┌──────────────┐
                    │  Add to      │           │  Customize   │    │  Dismiss /   │
                    │  Dashboard   │           │  in Builder  │    │  Skip        │
                    └──────────────┘           └──────────────┘    └──────────────┘
```

### Why Build This?

| Benefit | Impact |
|---------|--------|
| **Faster Time-to-Insight** | Users see value in < 30 seconds |
| **Lower Learning Curve** | No chart type knowledge needed |
| **Higher Engagement** | "Wow factor" drives adoption |
| **Competitive Parity** | Power BI, Tableau have this |
| **Upsell Path** | Basic free, AI-powered premium |

---

## 2. Feature Specifications

### 2.1 Entry Points

Users can access Quick Charts from multiple locations:

| Entry Point | Trigger | Context |
|-------------|---------|---------|
| **After Connection** | User creates new connection | Show for new connection's tables |
| **Home Page Section** | Always visible | Show for recent/popular tables |
| **Quick Charts Page** | `/quick-charts` route | Full exploration interface |
| **Table Context Menu** | Click on table name | Show for specific table |
| **Empty Dashboard** | New dashboard created | Suggest charts to add |

### 2.2 Core Functionality

#### A. Data Profiling Engine

Automatically analyze tables to understand data characteristics:

```typescript
interface ColumnProfile {
  name: string;
  dataType: 'categorical' | 'numeric' | 'temporal' | 'text' | 'boolean';

  // Statistics
  rowCount: number;
  nullCount: number;
  nullPercent: number;
  distinctCount: number;
  cardinality: 'low' | 'medium' | 'high';  // <10, 10-100, >100

  // For numeric
  min?: number;
  max?: number;
  mean?: number;

  // For temporal
  minDate?: string;
  maxDate?: string;
  granularity?: 'minute' | 'hour' | 'day' | 'week' | 'month' | 'year';

  // For categorical
  topValues?: Array<{ value: string; count: number }>;
}

interface TableProfile {
  connectionId: string;
  schema: string;
  tableName: string;
  rowCount: number;
  columns: ColumnProfile[];

  // Derived insights
  hasTemporal: boolean;
  hasNumeric: boolean;
  hasCategorical: boolean;
  suggestedDimensions: string[];
  suggestedMeasures: string[];
}
```

#### B. Chart Recommendation Engine

Rule-based intelligence to suggest optimal chart types:

```typescript
interface ChartRecommendation {
  id: string;
  chartType: ChartType;
  confidence: number;  // 0-1 score
  reason: string;      // "Bar chart works well for comparing categories"

  // Pre-configured query
  dimensions: Array<{
    column: string;
    alias: string;
  }>;
  measures: Array<{
    column: string;
    aggregation: 'sum' | 'count' | 'avg' | 'min' | 'max';
    alias: string;
  }>;

  // Pre-configured chart
  chartConfig: EChartsOption;

  // Metadata
  title: string;       // Auto-generated: "Sales by Region"
  description: string; // "Shows total sales broken down by region"
}
```

#### C. Chart Type Selection Rules

| Data Pattern | Recommended Chart | Confidence |
|--------------|-------------------|------------|
| 1 categorical (low cardinality) + 1 numeric | **Pie / Donut** | 0.9 |
| 1 categorical (medium cardinality) + 1 numeric | **Bar Chart** | 0.95 |
| 1 temporal + 1 numeric | **Line Chart** | 0.95 |
| 1 temporal + 2+ numeric | **Multi-Line Chart** | 0.9 |
| 2 numeric columns | **Scatter Plot** | 0.85 |
| 1 categorical + 2 numeric | **Grouped Bar** | 0.85 |
| Single numeric (aggregatable) | **KPI Card** | 0.9 |
| 4+ columns, no clear pattern | **Table** | 0.7 |
| Hierarchical categories | **Treemap** | 0.8 |
| Percentage/proportion data | **Pie Chart** | 0.85 |
| Funnel-like sequential data | **Funnel Chart** | 0.75 |

#### D. Smart Title Generation

Auto-generate meaningful chart titles:

```typescript
function generateTitle(
  measure: string,
  dimension: string,
  aggregation: string
): string {
  // Pattern: "{Aggregation} {Measure} by {Dimension}"

  const aggLabels = {
    sum: 'Total',
    count: 'Count of',
    avg: 'Average',
    min: 'Minimum',
    max: 'Maximum'
  };

  // Examples:
  // "Total Revenue by Region"
  // "Count of Orders by Status"
  // "Average Price by Category"

  return `${aggLabels[aggregation]} ${humanize(measure)} by ${humanize(dimension)}`;
}
```

### 2.3 User Interface

#### A. Quick Charts Page (`/quick-charts`)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Quick Charts                                        [Connection ▼]     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Select a table to explore:                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 🔍 Search tables...                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ 📊 orders    │ │ 📊 products  │ │ 📊 customers │ │ 📊 sales     │   │
│  │ 15,234 rows  │ │ 1,205 rows   │ │ 8,432 rows   │ │ 45,678 rows  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Suggested Charts for "orders"                      [Refresh] [Settings]│
│                                                                         │
│  ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐│
│  │  📊 Bar Chart       │ │  📈 Line Chart      │ │  🥧 Pie Chart       ││
│  │                     │ │                     │ │                     ││
│  │  ┌───────────────┐  │ │  ┌───────────────┐  │ │  ┌───────────────┐  ││
│  │  │ ████          │  │ │  │    /\    /\   │  │ │  │    ████       │  ││
│  │  │ ████ ███      │  │ │  │   /  \  /  \  │  │ │  │  ██    ██     │  ││
│  │  │ ████ ███ ██   │  │ │  │  /    \/    \ │  │ │  │ ██      ██    │  ││
│  │  └───────────────┘  │ │  └───────────────┘  │ │  └───────────────┘  ││
│  │                     │ │                     │ │                     ││
│  │  Total Sales by     │ │  Orders Over Time   │ │  Orders by Status   ││
│  │  Region             │ │                     │ │                     ││
│  │                     │ │                     │ │                     ││
│  │  Confidence: 95%    │ │  Confidence: 92%    │ │  Confidence: 88%    ││
│  │                     │ │                     │ │                     ││
│  │ [Add to Dashboard]  │ │ [Add to Dashboard]  │ │ [Add to Dashboard]  ││
│  │ [Customize]         │ │ [Customize]         │ │ [Customize]         ││
│  └─────────────────────┘ └─────────────────────┘ └─────────────────────┘│
│                                                                         │
│  ┌─────────────────────┐ ┌─────────────────────┐                        │
│  │  🎯 KPI Card        │ │  📋 Table View      │                        │
│  │                     │ │                     │                        │
│  │  ┌───────────────┐  │ │  ┌───────────────┐  │                        │
│  │  │   $1.2M       │  │ │  │ ID | Name | $ │  │                        │
│  │  │   Total Rev   │  │ │  │ 1  | Prod | 99│  │                        │
│  │  │   ▲ 12.5%     │  │ │  │ 2  | Item | 45│  │                        │
│  │  └───────────────┘  │ │  └───────────────┘  │                        │
│  │                     │ │                     │                        │
│  │  Total Order Value  │ │  All Orders Data    │                        │
│  │                     │ │                     │                        │
│  │  Confidence: 90%    │ │  Confidence: 70%    │                        │
│  │                     │ │                     │                        │
│  │ [Add to Dashboard]  │ │ [Add to Dashboard]  │                        │
│  │ [Customize]         │ │ [Customize]         │                        │
│  └─────────────────────┘ └─────────────────────┘                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### B. Home Page Integration

Add new section to existing home page:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Explore Your Data                                        [See All →]   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  We found interesting patterns in your data:                            │
│                                                                         │
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐     │
│  │ Total Revenue by  │ │ Orders Over Time  │ │ Top 10 Products   │     │
│  │ Category          │ │                   │ │                   │     │
│  │ [Mini Chart]      │ │ [Mini Chart]      │ │ [Mini Chart]      │     │
│  │ [+ Add]           │ │ [+ Add]           │ │ [+ Add]           │     │
│  └───────────────────┘ └───────────────────┘ └───────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### C. Post-Connection Modal

Show immediately after creating a new connection:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                    [X]  │
│                                                                         │
│                    ✅ Connection Successful!                            │
│                                                                         │
│         We found 12 tables in your "Production DB" database.            │
│                                                                         │
│  ───────────────────────────────────────────────────────────────────── │
│                                                                         │
│  Here are some charts we can create automatically:                      │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  📊 Sales by Region    │  📈 Revenue Trend    │  🎯 Total Orders │   │
│  │  [Preview]             │  [Preview]           │  [Preview]       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ [Explore Quick Charts]          [Skip and Go to Connections]    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Add to Dashboard Flow

When user clicks "Add to Dashboard":

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Add Chart to Dashboard                                            [X]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Chart: "Total Sales by Region"                                         │
│                                                                         │
│  Select destination:                                                    │
│                                                                         │
│  ○ Create new dashboard                                                 │
│    Dashboard name: [____________________]                               │
│                                                                         │
│  ● Add to existing dashboard                                            │
│    ┌─────────────────────────────────────────────────────────────────┐ │
│    │ 📊 Sales Overview Dashboard                              [Select]│ │
│    │ 📊 Q4 Performance                                        [Select]│ │
│    │ 📊 Executive Summary                                     [Select]│ │
│    └─────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │               [Cancel]              [Add Chart]                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technical Architecture

### 3.1 System Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         QUICK CHARTS ARCHITECTURE                         │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │     │   Backend   │     │  Profiler   │     │  Database   │
│   React     │     │   FastAPI   │     │   Service   │     │  PostgreSQL │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      │ GET /quick-charts │                   │                   │
      │ ?connection_id=X  │                   │                   │
      │ &table=orders     │                   │                   │
      │──────────────────>│                   │                   │
      │                   │                   │                   │
      │                   │ profile_table()   │                   │
      │                   │──────────────────>│                   │
      │                   │                   │                   │
      │                   │                   │ SELECT columns,   │
      │                   │                   │ types, stats      │
      │                   │                   │──────────────────>│
      │                   │                   │<──────────────────│
      │                   │                   │                   │
      │                   │<──────────────────│                   │
      │                   │   TableProfile    │                   │
      │                   │                   │                   │
      │                   │ recommend_charts()│                   │
      │                   │──────────────────>│                   │
      │                   │                   │                   │
      │                   │<──────────────────│                   │
      │                   │   ChartRecommendations                │
      │                   │                   │                   │
      │<──────────────────│                   │                   │
      │   QuickChartSuggestions               │                   │
      │                   │                   │                   │
      │ Render chart      │                   │                   │
      │ previews          │                   │                   │
      │                   │                   │                   │
```

### 3.2 New Backend Components

#### A. Data Profiler Service

**File:** `/backend/app/services/data_profiler_service.py`

```python
from typing import List, Optional, Dict, Any
from enum import Enum
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

class ColumnDataType(str, Enum):
    CATEGORICAL = "categorical"
    NUMERIC = "numeric"
    TEMPORAL = "temporal"
    TEXT = "text"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"

class Cardinality(str, Enum):
    LOW = "low"        # < 10 distinct values
    MEDIUM = "medium"  # 10-100 distinct values
    HIGH = "high"      # > 100 distinct values

class DataProfiler:
    """
    Analyzes database tables to understand data characteristics
    for intelligent chart recommendations.
    """

    # SQL type mappings
    NUMERIC_TYPES = {'integer', 'bigint', 'smallint', 'decimal', 'numeric',
                     'real', 'double precision', 'float', 'int', 'tinyint'}
    TEMPORAL_TYPES = {'date', 'timestamp', 'datetime', 'time',
                      'timestamp with time zone', 'timestamp without time zone'}
    BOOLEAN_TYPES = {'boolean', 'bool', 'bit'}

    async def profile_table(
        self,
        connection_id: str,
        schema: str,
        table: str,
        sample_size: int = 10000
    ) -> TableProfile:
        """
        Profile a table and return column statistics.
        """
        # 1. Get column metadata
        columns = await self._get_columns(connection_id, schema, table)

        # 2. Get row count
        row_count = await self._get_row_count(connection_id, schema, table)

        # 3. Profile each column
        column_profiles = []
        for col in columns:
            profile = await self._profile_column(
                connection_id, schema, table, col,
                row_count, sample_size
            )
            column_profiles.append(profile)

        # 4. Derive insights
        return TableProfile(
            connection_id=connection_id,
            schema=schema,
            table_name=table,
            row_count=row_count,
            columns=column_profiles,
            has_temporal=any(c.data_type == ColumnDataType.TEMPORAL for c in column_profiles),
            has_numeric=any(c.data_type == ColumnDataType.NUMERIC for c in column_profiles),
            has_categorical=any(c.data_type == ColumnDataType.CATEGORICAL for c in column_profiles),
            suggested_dimensions=self._suggest_dimensions(column_profiles),
            suggested_measures=self._suggest_measures(column_profiles)
        )

    async def _profile_column(
        self,
        connection_id: str,
        schema: str,
        table: str,
        column: ColumnInfo,
        total_rows: int,
        sample_size: int
    ) -> ColumnProfile:
        """
        Profile a single column with statistics.
        """
        data_type = self._categorize_type(column.type)

        # Build stats query based on type
        stats = await self._get_column_stats(
            connection_id, schema, table, column.name, data_type
        )

        return ColumnProfile(
            name=column.name,
            data_type=data_type,
            row_count=total_rows,
            null_count=stats.get('null_count', 0),
            null_percent=stats.get('null_count', 0) / total_rows * 100 if total_rows > 0 else 0,
            distinct_count=stats.get('distinct_count', 0),
            cardinality=self._calculate_cardinality(stats.get('distinct_count', 0)),
            min_value=stats.get('min_value'),
            max_value=stats.get('max_value'),
            mean=stats.get('mean'),
            top_values=stats.get('top_values', [])
        )

    def _categorize_type(self, sql_type: str) -> ColumnDataType:
        """
        Categorize SQL type into data type for chart selection.
        """
        sql_type_lower = sql_type.lower()

        if any(t in sql_type_lower for t in self.NUMERIC_TYPES):
            return ColumnDataType.NUMERIC
        elif any(t in sql_type_lower for t in self.TEMPORAL_TYPES):
            return ColumnDataType.TEMPORAL
        elif any(t in sql_type_lower for t in self.BOOLEAN_TYPES):
            return ColumnDataType.BOOLEAN
        elif 'char' in sql_type_lower or 'text' in sql_type_lower:
            # Could be categorical or text - check cardinality
            return ColumnDataType.CATEGORICAL  # Will refine based on cardinality
        else:
            return ColumnDataType.UNKNOWN

    def _calculate_cardinality(self, distinct_count: int) -> Cardinality:
        if distinct_count < 10:
            return Cardinality.LOW
        elif distinct_count <= 100:
            return Cardinality.MEDIUM
        else:
            return Cardinality.HIGH

    def _suggest_dimensions(self, columns: List[ColumnProfile]) -> List[str]:
        """
        Suggest columns suitable for dimensions (GROUP BY).
        """
        dimensions = []
        for col in columns:
            if col.data_type == ColumnDataType.CATEGORICAL and col.cardinality in [Cardinality.LOW, Cardinality.MEDIUM]:
                dimensions.append(col.name)
            elif col.data_type == ColumnDataType.TEMPORAL:
                dimensions.append(col.name)
        return dimensions

    def _suggest_measures(self, columns: List[ColumnProfile]) -> List[str]:
        """
        Suggest columns suitable for measures (aggregation).
        """
        measures = []
        for col in columns:
            if col.data_type == ColumnDataType.NUMERIC:
                measures.append(col.name)
        return measures
```

#### B. Chart Recommendation Service

**File:** `/backend/app/services/chart_recommendation_service.py`

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import uuid

@dataclass
class ChartRecommendation:
    id: str
    chart_type: str
    confidence: float
    reason: str
    title: str
    description: str
    dimensions: List[Dict[str, str]]
    measures: List[Dict[str, str]]
    chart_config: Dict[str, Any]
    query_config: Dict[str, Any]

class ChartRecommender:
    """
    Recommends optimal chart types based on data profile.
    Uses rule-based heuristics for fast, deterministic results.
    """

    # Chart type rules
    CHART_RULES = [
        {
            "type": "kpi",
            "requires": {"numeric": 1},
            "max_dimensions": 0,
            "confidence": 0.90,
            "reason": "Single metric display for key performance indicators"
        },
        {
            "type": "pie",
            "requires": {"categorical_low": 1, "numeric": 1},
            "max_distinct": 8,
            "confidence": 0.88,
            "reason": "Pie chart shows proportion breakdown for small categories"
        },
        {
            "type": "donut",
            "requires": {"categorical_low": 1, "numeric": 1},
            "max_distinct": 10,
            "confidence": 0.85,
            "reason": "Donut chart provides proportion view with center space"
        },
        {
            "type": "bar",
            "requires": {"categorical": 1, "numeric": 1},
            "confidence": 0.95,
            "reason": "Bar chart is ideal for comparing categories"
        },
        {
            "type": "horizontal-bar",
            "requires": {"categorical": 1, "numeric": 1},
            "min_distinct": 8,
            "confidence": 0.88,
            "reason": "Horizontal bars work better for many categories with long labels"
        },
        {
            "type": "line",
            "requires": {"temporal": 1, "numeric": 1},
            "confidence": 0.95,
            "reason": "Line chart shows trends over time"
        },
        {
            "type": "area",
            "requires": {"temporal": 1, "numeric": 1},
            "confidence": 0.85,
            "reason": "Area chart emphasizes magnitude of change over time"
        },
        {
            "type": "scatter",
            "requires": {"numeric": 2},
            "confidence": 0.85,
            "reason": "Scatter plot reveals correlation between two variables"
        },
        {
            "type": "table",
            "requires": {},
            "min_columns": 4,
            "confidence": 0.70,
            "reason": "Table view for detailed multi-column data exploration"
        }
    ]

    def recommend(
        self,
        profile: TableProfile,
        max_recommendations: int = 5
    ) -> List[ChartRecommendation]:
        """
        Generate chart recommendations based on table profile.
        """
        recommendations = []

        # Categorize available columns
        categorized = self._categorize_columns(profile.columns)

        # Try each chart rule
        for rule in self.CHART_RULES:
            if self._matches_rule(categorized, rule, profile):
                recommendation = self._build_recommendation(
                    rule, categorized, profile
                )
                if recommendation:
                    recommendations.append(recommendation)

        # Sort by confidence, take top N
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        return recommendations[:max_recommendations]

    def _categorize_columns(self, columns: List[ColumnProfile]) -> Dict[str, List[ColumnProfile]]:
        """
        Group columns by their data type and cardinality.
        """
        return {
            "numeric": [c for c in columns if c.data_type == ColumnDataType.NUMERIC],
            "temporal": [c for c in columns if c.data_type == ColumnDataType.TEMPORAL],
            "categorical": [c for c in columns if c.data_type == ColumnDataType.CATEGORICAL],
            "categorical_low": [c for c in columns
                              if c.data_type == ColumnDataType.CATEGORICAL
                              and c.cardinality == Cardinality.LOW],
            "categorical_medium": [c for c in columns
                                  if c.data_type == ColumnDataType.CATEGORICAL
                                  and c.cardinality == Cardinality.MEDIUM],
            "boolean": [c for c in columns if c.data_type == ColumnDataType.BOOLEAN],
            "all": columns
        }

    def _matches_rule(
        self,
        categorized: Dict[str, List[ColumnProfile]],
        rule: Dict,
        profile: TableProfile
    ) -> bool:
        """
        Check if available columns match a chart rule.
        """
        requires = rule.get("requires", {})

        for col_type, min_count in requires.items():
            if len(categorized.get(col_type, [])) < min_count:
                return False

        # Check additional constraints
        if "max_distinct" in rule:
            cat_cols = categorized.get("categorical_low", []) or categorized.get("categorical", [])
            if cat_cols and cat_cols[0].distinct_count > rule["max_distinct"]:
                return False

        if "min_distinct" in rule:
            cat_cols = categorized.get("categorical", [])
            if cat_cols and cat_cols[0].distinct_count < rule["min_distinct"]:
                return False

        if "min_columns" in rule:
            if len(profile.columns) < rule["min_columns"]:
                return False

        return True

    def _build_recommendation(
        self,
        rule: Dict,
        categorized: Dict[str, List[ColumnProfile]],
        profile: TableProfile
    ) -> Optional[ChartRecommendation]:
        """
        Build a complete chart recommendation with config.
        """
        chart_type = rule["type"]

        # Select columns for this chart
        dimension_col = None
        measure_col = None

        if chart_type in ["bar", "horizontal-bar", "pie", "donut"]:
            dimension_col = (categorized.get("categorical_low") or
                           categorized.get("categorical_medium") or
                           categorized.get("categorical", [None]))[0]
            measure_col = categorized.get("numeric", [None])[0]
        elif chart_type in ["line", "area"]:
            dimension_col = categorized.get("temporal", [None])[0]
            measure_col = categorized.get("numeric", [None])[0]
        elif chart_type == "scatter":
            numerics = categorized.get("numeric", [])
            if len(numerics) >= 2:
                dimension_col = numerics[0]
                measure_col = numerics[1]
        elif chart_type == "kpi":
            measure_col = categorized.get("numeric", [None])[0]

        # Skip if we don't have required columns
        if chart_type != "table" and chart_type != "kpi" and not dimension_col:
            return None
        if chart_type != "table" and not measure_col:
            return None

        # Generate title
        title = self._generate_title(chart_type, dimension_col, measure_col, profile)

        # Build configs
        dimensions = []
        measures = []

        if dimension_col:
            dimensions.append({
                "column": dimension_col.name,
                "alias": self._humanize(dimension_col.name)
            })

        if measure_col:
            aggregation = "sum" if "amount" in measure_col.name.lower() or "price" in measure_col.name.lower() or "total" in measure_col.name.lower() else "count"
            measures.append({
                "column": measure_col.name,
                "aggregation": aggregation,
                "alias": f"{aggregation.title()} of {self._humanize(measure_col.name)}"
            })

        # Build ECharts config
        chart_config = self._build_echarts_config(
            chart_type, dimensions, measures, title
        )

        # Build query config
        query_config = self._build_query_config(
            profile, dimensions, measures
        )

        return ChartRecommendation(
            id=str(uuid.uuid4()),
            chart_type=chart_type,
            confidence=rule["confidence"],
            reason=rule["reason"],
            title=title,
            description=f"Automatically generated {chart_type} chart",
            dimensions=dimensions,
            measures=measures,
            chart_config=chart_config,
            query_config=query_config
        )

    def _generate_title(
        self,
        chart_type: str,
        dimension: Optional[ColumnProfile],
        measure: Optional[ColumnProfile],
        profile: TableProfile
    ) -> str:
        """
        Generate a human-readable chart title.
        """
        if chart_type == "kpi" and measure:
            return f"Total {self._humanize(measure.name)}"

        if chart_type == "table":
            return f"{self._humanize(profile.table_name)} Data"

        if dimension and measure:
            return f"{self._humanize(measure.name)} by {self._humanize(dimension.name)}"

        return f"{self._humanize(profile.table_name)} Overview"

    def _humanize(self, name: str) -> str:
        """
        Convert column_name to Human Name.
        """
        return name.replace("_", " ").replace("-", " ").title()

    def _build_echarts_config(
        self,
        chart_type: str,
        dimensions: List[Dict],
        measures: List[Dict],
        title: str
    ) -> Dict[str, Any]:
        """
        Build ECharts option configuration.
        """
        # Base config
        config = {
            "title": {"text": title, "left": "center"},
            "tooltip": {"trigger": "axis" if chart_type in ["line", "bar", "area"] else "item"},
            "legend": {"show": True, "bottom": 0}
        }

        if chart_type in ["bar", "horizontal-bar"]:
            config.update({
                "xAxis": {"type": "category" if chart_type == "bar" else "value"},
                "yAxis": {"type": "value" if chart_type == "bar" else "category"},
                "series": [{"type": "bar", "name": measures[0]["alias"] if measures else "Value"}]
            })
        elif chart_type == "line":
            config.update({
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "line", "smooth": True, "name": measures[0]["alias"] if measures else "Value"}]
            })
        elif chart_type == "area":
            config.update({
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "line", "areaStyle": {}, "smooth": True}]
            })
        elif chart_type in ["pie", "donut"]:
            config.update({
                "series": [{
                    "type": "pie",
                    "radius": ["40%", "70%"] if chart_type == "donut" else "70%",
                    "label": {"show": True, "formatter": "{b}: {d}%"}
                }]
            })
        elif chart_type == "scatter":
            config.update({
                "xAxis": {"type": "value"},
                "yAxis": {"type": "value"},
                "series": [{"type": "scatter", "symbolSize": 10}]
            })
        elif chart_type == "kpi":
            config = {
                "type": "kpi",
                "title": title,
                "format": "number",
                "showTrend": True
            }

        return config

    def _build_query_config(
        self,
        profile: TableProfile,
        dimensions: List[Dict],
        measures: List[Dict]
    ) -> Dict[str, Any]:
        """
        Build query configuration for data fetching.
        """
        return {
            "schema": profile.schema,
            "table": profile.table_name,
            "dimensions": dimensions,
            "measures": measures,
            "filters": [],
            "sort": [],
            "limit": 1000
        }
```

#### C. API Endpoint

**File:** `/backend/app/api/v1/endpoints/quickcharts.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from uuid import UUID

from app.services.data_profiler_service import DataProfiler
from app.services.chart_recommendation_service import ChartRecommender
from app.schemas.quickchart import (
    QuickChartRequest,
    QuickChartResponse,
    TableProfile,
    ChartRecommendation
)
from app.api.deps import get_current_user

router = APIRouter()

profiler = DataProfiler()
recommender = ChartRecommender()

@router.get("/tables/{connection_id}")
async def list_tables_for_quickcharts(
    connection_id: UUID,
    current_user = Depends(get_current_user)
) -> List[dict]:
    """
    List tables with row counts for quick chart selection.
    """
    tables = await profiler.list_tables(str(connection_id))
    return tables

@router.get("/suggestions/{connection_id}/{schema}/{table}")
async def get_quick_chart_suggestions(
    connection_id: UUID,
    schema: str,
    table: str,
    max_suggestions: int = 5,
    current_user = Depends(get_current_user)
) -> QuickChartResponse:
    """
    Analyze a table and return intelligent chart suggestions.
    """
    try:
        # Profile the table
        profile = await profiler.profile_table(
            str(connection_id), schema, table
        )

        # Generate recommendations
        recommendations = recommender.recommend(
            profile, max_recommendations=max_suggestions
        )

        return QuickChartResponse(
            connection_id=str(connection_id),
            schema=schema,
            table=table,
            profile=profile,
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-from-suggestion")
async def create_chart_from_suggestion(
    suggestion_id: str,
    dashboard_id: Optional[UUID] = None,
    current_user = Depends(get_current_user)
) -> dict:
    """
    Create a saved chart from a quick chart suggestion.
    Optionally add to a dashboard.
    """
    # Implementation: Create SavedChart from suggestion
    pass

@router.get("/home-suggestions")
async def get_home_quick_suggestions(
    current_user = Depends(get_current_user)
) -> List[ChartRecommendation]:
    """
    Get quick chart suggestions for the home page.
    Analyzes recent connections and popular tables.
    """
    # Get user's recent connections
    # Pick most used tables
    # Return 3-5 suggestions
    pass
```

### 3.3 New Frontend Components

#### A. Quick Charts Page

**File:** `/frontend/src/pages/QuickCharts.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Loader2, Plus, Pencil, Sparkles } from 'lucide-react';

interface ChartRecommendation {
  id: string;
  chart_type: string;
  confidence: number;
  reason: string;
  title: string;
  description: string;
  chart_config: any;
  query_config: any;
}

export default function QuickCharts() {
  const [selectedConnection, setSelectedConnection] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);

  // Fetch connections
  const { data: connections } = useQuery({
    queryKey: ['connections'],
    queryFn: () => api.get('/connections').then(r => r.data)
  });

  // Fetch tables for selected connection
  const { data: tables } = useQuery({
    queryKey: ['tables', selectedConnection],
    queryFn: () => api.get(`/connections/${selectedConnection}/tables`).then(r => r.data),
    enabled: !!selectedConnection
  });

  // Fetch suggestions for selected table
  const { data: suggestions, isLoading: loadingSuggestions } = useQuery({
    queryKey: ['quickcharts', selectedConnection, selectedTable],
    queryFn: () => api.get(
      `/quickcharts/suggestions/${selectedConnection}/public/${selectedTable}`
    ).then(r => r.data),
    enabled: !!selectedConnection && !!selectedTable
  });

  // Create chart mutation
  const createChart = useMutation({
    mutationFn: (recommendation: ChartRecommendation) =>
      api.post('/charts', {
        name: recommendation.title,
        chart_type: recommendation.chart_type,
        chart_config: recommendation.chart_config,
        query_config: recommendation.query_config,
        connection_id: selectedConnection
      })
  });

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-6 h-6 text-yellow-500" />
        <h1 className="text-2xl font-bold">Quick Charts</h1>
      </div>

      <p className="text-gray-600 mb-6">
        Select a data source and table to automatically generate chart suggestions.
      </p>

      {/* Selection Controls */}
      <div className="flex gap-4 mb-8">
        <Select
          placeholder="Select connection..."
          value={selectedConnection}
          onChange={setSelectedConnection}
          options={connections?.map(c => ({ value: c.id, label: c.name }))}
        />

        <Select
          placeholder="Select table..."
          value={selectedTable}
          onChange={setSelectedTable}
          options={tables?.map(t => ({
            value: t.name,
            label: `${t.name} (${t.row_count?.toLocaleString()} rows)`
          }))}
          disabled={!selectedConnection}
        />
      </div>

      {/* Loading State */}
      {loadingSuggestions && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          <span className="ml-2">Analyzing your data...</span>
        </div>
      )}

      {/* Chart Suggestions Grid */}
      {suggestions?.recommendations && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {suggestions.recommendations.map((rec: ChartRecommendation) => (
            <Card key={rec.id} className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">{rec.title}</h3>
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                  {Math.round(rec.confidence * 100)}% match
                </span>
              </div>

              <p className="text-sm text-gray-500 mb-4">{rec.reason}</p>

              {/* Chart Preview */}
              <div className="h-48 mb-4">
                <ReactECharts
                  option={rec.chart_config}
                  style={{ height: '100%', width: '100%' }}
                  opts={{ renderer: 'canvas' }}
                />
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={() => createChart.mutate(rec)}
                  disabled={createChart.isPending}
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Add to Dashboard
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => navigate(`/charts/new`, { state: { fromQuickChart: rec } })}
                >
                  <Pencil className="w-4 h-4 mr-1" />
                  Customize
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Empty State */}
      {suggestions?.recommendations?.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No chart suggestions available for this table.</p>
          <p className="text-sm">Try selecting a table with more varied data types.</p>
        </div>
      )}
    </div>
  );
}
```

#### B. Quick Chart Suggestions Component (for Home Page)

**File:** `/frontend/src/components/dashboard/QuickChartSuggestions.tsx`

```typescript
import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface QuickChartSuggestion {
  id: string;
  title: string;
  chart_type: string;
  chart_config: any;
  confidence: number;
  table_name: string;
}

interface Props {
  suggestions: QuickChartSuggestion[];
  onAddChart: (suggestion: QuickChartSuggestion) => void;
}

export function QuickChartSuggestions({ suggestions, onAddChart }: Props) {
  const navigate = useNavigate();

  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <section className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold">Explore Your Data</h2>
          <p className="text-sm text-gray-500">
            We found interesting patterns in your recent data
          </p>
        </div>
        <Button variant="ghost" onClick={() => navigate('/quick-charts')}>
          See All <ArrowRight className="w-4 h-4 ml-1" />
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {suggestions.slice(0, 3).map((suggestion) => (
          <Card
            key={suggestion.id}
            className="p-4 hover:shadow-md transition-shadow cursor-pointer"
          >
            <h3 className="font-medium text-sm mb-2">{suggestion.title}</h3>
            <p className="text-xs text-gray-400 mb-3">
              From: {suggestion.table_name}
            </p>

            {/* Mini Chart Preview */}
            <div className="h-32 mb-3">
              <ReactECharts
                option={{
                  ...suggestion.chart_config,
                  title: { show: false },
                  legend: { show: false },
                  grid: { top: 10, right: 10, bottom: 20, left: 30 }
                }}
                style={{ height: '100%', width: '100%' }}
                opts={{ renderer: 'canvas' }}
              />
            </div>

            <Button
              size="sm"
              className="w-full"
              onClick={() => onAddChart(suggestion)}
            >
              <Plus className="w-4 h-4 mr-1" />
              Add to Dashboard
            </Button>
          </Card>
        ))}
      </div>
    </section>
  );
}
```

---

## 4. Database Schema Changes

### New Tables

```sql
-- Store cached table profiles for performance
CREATE TABLE table_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID REFERENCES connections(id) ON DELETE CASCADE,
    schema_name VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    row_count BIGINT,
    profile_data JSONB NOT NULL,  -- Full column profiles
    profiled_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,  -- Cache expiration

    UNIQUE(connection_id, schema_name, table_name)
);

-- Store user interactions with suggestions for ML training
CREATE TABLE quickchart_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    connection_id UUID NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    suggestion_id VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'viewed', 'added', 'customized', 'dismissed'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast lookup
CREATE INDEX idx_table_profiles_lookup
ON table_profiles(connection_id, schema_name, table_name);

CREATE INDEX idx_quickchart_interactions_user
ON quickchart_interactions(user_id, created_at DESC);
```

---

## 5. API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/quickcharts/tables/{connection_id}` | List tables with metadata |
| GET | `/api/v1/quickcharts/suggestions/{connection_id}/{schema}/{table}` | Get chart suggestions for table |
| POST | `/api/v1/quickcharts/create-from-suggestion` | Create chart from suggestion |
| GET | `/api/v1/quickcharts/home-suggestions` | Get suggestions for home page |
| POST | `/api/v1/quickcharts/interaction` | Log user interaction (analytics) |

---

## 6. Implementation Phases

### Phase 1: Core Engine (Week 1)

**Backend:**
- [ ] Create `DataProfiler` service
- [ ] Create `ChartRecommender` service
- [ ] Add `/quickcharts/suggestions` endpoint
- [ ] Unit tests for recommendation logic

**Deliverable:** API returns chart suggestions for any table

### Phase 2: UI Implementation (Week 2)

**Frontend:**
- [ ] Create `/quick-charts` page
- [ ] Build `QuickChartSuggestions` component
- [ ] Integrate chart preview with ECharts
- [ ] Add "Add to Dashboard" flow

**Deliverable:** Users can browse and use quick charts

### Phase 3: Integration & Polish (Week 3)

**Integration:**
- [ ] Add home page section
- [ ] Post-connection modal
- [ ] Table context menu integration
- [ ] Error handling & edge cases

**Polish:**
- [ ] Loading states & animations
- [ ] Empty states
- [ ] Mobile responsiveness
- [ ] Performance optimization (caching)

**Deliverable:** Feature complete and production-ready

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Adoption Rate** | 60% of users try Quick Charts | Track page visits |
| **Conversion Rate** | 40% add at least one chart | Track "Add to Dashboard" clicks |
| **Time to First Chart** | < 2 minutes | Measure new user journey |
| **Suggestion Accuracy** | 80% positive feedback | Track which suggestions are used |
| **Engagement Lift** | 25% more dashboards created | Compare before/after |

---

## 8. Future Enhancements (Post-MVP)

### Phase 2: AI-Powered (Month 2)

- LLM-generated chart titles and descriptions
- Natural language question generation
- Smart insight narratives

### Phase 3: Learning System (Month 3)

- Track which suggestions users accept
- Train ML model on user preferences
- Personalized recommendations

### Phase 4: Advanced Features (Month 4)

- Cross-table relationship detection
- Automatic join suggestions
- Anomaly highlighting in suggestions

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Slow profiling on large tables** | Poor UX | Sample data (10k rows), async processing |
| **Irrelevant suggestions** | User frustration | Provide "Customize" escape hatch, iterate on rules |
| **Chart rendering issues** | Broken previews | Fallback to placeholder, error boundaries |
| **Schema edge cases** | Missing suggestions | Handle nulls gracefully, default to table view |

---

## 10. Dependencies

### External
- None (uses existing ECharts, no new AI APIs required for MVP)

### Internal
- Connection service (existing)
- Chart creation API (existing)
- Dashboard API (existing)

### Team
- 1 Backend developer (1.5 weeks)
- 1 Frontend developer (1.5 weeks)
- Design review (2-3 hours)
- QA testing (2-3 days)

---

## Appendix: Example Suggestions

### Example 1: E-commerce Orders Table

**Table:** `orders`
**Columns:** `order_id`, `customer_id`, `order_date`, `total_amount`, `status`, `region`

**Suggestions:**
1. **Line Chart** - "Orders Over Time" (order_date vs count)
2. **Bar Chart** - "Revenue by Region" (region vs sum of total_amount)
3. **Pie Chart** - "Orders by Status" (status vs count)
4. **KPI Card** - "Total Revenue" (sum of total_amount)
5. **Table** - "Recent Orders" (all columns, sorted by date)

### Example 2: Product Catalog

**Table:** `products`
**Columns:** `product_id`, `name`, `category`, `price`, `stock_quantity`, `created_at`

**Suggestions:**
1. **Bar Chart** - "Products by Category" (category vs count)
2. **Horizontal Bar** - "Average Price by Category" (category vs avg price)
3. **Scatter Plot** - "Price vs Stock" (price vs stock_quantity)
4. **KPI Card** - "Total Products" (count)
5. **Table** - "Product Catalog" (all columns)

---

**Document Version:** 1.0.0
**Created:** 2026-01-28
**Author:** AI Analysis Engine
**Status:** Ready for Review
