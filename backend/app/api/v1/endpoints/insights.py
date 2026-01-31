"""
Quick Insights API Endpoints

Provides endpoints for automated data insights including
trend detection, outlier detection, and correlation analysis.
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from motor.motor_asyncio import AsyncIOMotorClient

from app.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.schemas.insights import (
    InsightType,
    InsightsRequest,
    DatasetInsightsRequest,
    InsightsResponse,
    DataProfile,
    TrendAnalysisRequest,
    TrendAnalysisResponse,
    OutlierDetectionRequest,
    OutlierDetectionResponse,
    CorrelationAnalysisRequest,
    CorrelationMatrix,
    INSIGHT_TEMPLATES,
    CHART_SUGGESTIONS,
)
from app.services.insights_service import get_insights_service

router = APIRouter()


# Main Insights Generation

@router.post("/analyze", response_model=InsightsResponse)
async def analyze_data(
    data: list[dict[str, Any]] = Body(..., description="Data to analyze"),
    columns: list[str] = Body(None, description="Columns to analyze"),
    date_column: Optional[str] = Body(None, description="Date column for time analysis"),
    measure_columns: list[str] = Body(None, description="Numeric columns"),
    dimension_columns: list[str] = Body(None, description="Categorical columns"),
    insight_types: list[InsightType] = Body(None, description="Types of insights to generate"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Analyze data and generate insights.

    Accepts raw data and returns detected patterns, trends, outliers,
    correlations, and other insights.
    """
    service = get_insights_service()
    return await service.generate_insights(
        data=data,
        columns=columns,
        date_column=date_column,
        measure_columns=measure_columns,
        dimension_columns=dimension_columns,
        insight_types=insight_types,
    )


@router.post("/analyze/chart/{chart_id}", response_model=InsightsResponse)
async def analyze_chart_data(
    chart_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Generate insights for a specific chart's data.

    Fetches the chart's data and runs insight analysis.
    """
    # Get chart
    chart = await db.dataviz.charts.find_one({"id": chart_id})
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    # Get chart data - this would typically execute the chart's query
    # For now, return empty insights
    service = get_insights_service()

    # TODO: Implement chart data fetching
    return await service.generate_insights(
        data=[],
        columns=[],
    )


@router.post("/analyze/dataset/{dataset_id}", response_model=InsightsResponse)
async def analyze_dataset(
    dataset_id: str,
    limit_rows: int = Query(10000, le=100000),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Generate insights for a dataset.

    Analyzes the dataset and returns detected insights.
    """
    # Get dataset
    dataset = await db.dataviz.datasets.find_one({"id": dataset_id})
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    service = get_insights_service()

    # TODO: Implement dataset data fetching
    return await service.generate_insights(
        data=[],
        columns=[],
    )


# Trend Analysis

@router.post("/trends", response_model=InsightsResponse)
async def detect_trends(
    data: list[dict[str, Any]] = Body(...),
    date_column: str = Body(..., description="Column containing dates"),
    value_columns: list[str] = Body(..., description="Numeric columns to analyze"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Detect trends in time series data.

    Analyzes date-based data to find increasing, decreasing,
    or stable trends.
    """
    service = get_insights_service()
    return await service.generate_insights(
        data=data,
        date_column=date_column,
        measure_columns=value_columns,
        insight_types=[InsightType.TREND],
    )


# Outlier Detection

@router.post("/outliers", response_model=InsightsResponse)
async def detect_outliers(
    data: list[dict[str, Any]] = Body(...),
    columns: list[str] = Body(..., description="Columns to check for outliers"),
    method: str = Body("iqr", description="Detection method: iqr, zscore"),
    threshold: float = Body(1.5, description="Threshold for detection"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Detect outliers in numeric columns.

    Uses IQR or Z-score methods to identify outlier values.
    """
    service = get_insights_service()
    return await service.generate_insights(
        data=data,
        measure_columns=columns,
        insight_types=[InsightType.OUTLIER],
    )


# Correlation Analysis

@router.post("/correlations", response_model=InsightsResponse)
async def analyze_correlations(
    data: list[dict[str, Any]] = Body(...),
    columns: list[str] = Body(..., description="Columns to analyze (min 2)"),
    min_correlation: float = Body(0.5, ge=0, le=1, description="Minimum correlation to report"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Analyze correlations between numeric columns.

    Returns pairs of columns with significant correlation.
    """
    if len(columns) < 2:
        raise HTTPException(status_code=400, detail="At least 2 columns required")

    service = get_insights_service()
    return await service.generate_insights(
        data=data,
        measure_columns=columns,
        insight_types=[InsightType.CORRELATION],
    )


# Distribution Analysis

@router.post("/distribution", response_model=InsightsResponse)
async def analyze_distribution(
    data: list[dict[str, Any]] = Body(...),
    columns: list[str] = Body(..., description="Columns to analyze"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Analyze the distribution of numeric columns.

    Returns distribution type (normal, skewed, etc.) and statistics.
    """
    service = get_insights_service()
    return await service.generate_insights(
        data=data,
        measure_columns=columns,
        insight_types=[InsightType.DISTRIBUTION],
    )


# Data Profile

@router.post("/profile", response_model=DataProfile)
async def profile_data(
    data: list[dict[str, Any]] = Body(...),
    columns: list[str] = Body(None, description="Columns to profile"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Generate a data profile.

    Returns statistics and metadata for each column including
    null counts, unique values, and basic statistics.
    """
    service = get_insights_service()

    if not columns and data:
        columns = list(data[0].keys())

    profile = service._generate_data_profile(data, columns or [])
    return profile


# Top/Bottom Performers

@router.post("/performers", response_model=InsightsResponse)
async def identify_performers(
    data: list[dict[str, Any]] = Body(...),
    measure: str = Body(..., description="Measure column"),
    dimension: str = Body(..., description="Dimension to group by"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Identify top and bottom performers.

    Groups data by dimension and ranks by measure.
    """
    service = get_insights_service()
    return await service.generate_insights(
        data=data,
        measure_columns=[measure],
        dimension_columns=[dimension],
        insight_types=[InsightType.TOP_PERFORMER, InsightType.BOTTOM_PERFORMER],
    )


# Comparison Analysis

@router.post("/compare", response_model=InsightsResponse)
async def compare_groups(
    data: list[dict[str, Any]] = Body(...),
    measures: list[str] = Body(..., description="Measure columns"),
    dimensions: list[str] = Body(..., description="Dimension columns"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Compare measures across dimension values.

    Analyzes variance and differences across groups.
    """
    service = get_insights_service()
    return await service.generate_insights(
        data=data,
        measure_columns=measures,
        dimension_columns=dimensions,
        insight_types=[InsightType.COMPARISON],
    )


# Templates and Configuration

@router.get("/templates")
async def get_insight_templates(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get insight message templates"""
    return {
        "templates": INSIGHT_TEMPLATES,
        "chart_suggestions": CHART_SUGGESTIONS,
    }


@router.get("/types")
async def get_insight_types(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get available insight types"""
    return {
        "types": [
            {
                "value": t.value,
                "label": t.value.replace("_", " ").title(),
                "description": {
                    InsightType.TREND: "Detect increasing or decreasing patterns over time",
                    InsightType.OUTLIER: "Find values significantly different from the norm",
                    InsightType.CORRELATION: "Discover relationships between columns",
                    InsightType.DISTRIBUTION: "Understand how values are spread",
                    InsightType.COMPARISON: "Compare values across categories",
                    InsightType.ANOMALY: "Detect unusual patterns or behaviors",
                    InsightType.SEASONALITY: "Find recurring patterns",
                    InsightType.GROWTH: "Measure changes over periods",
                    InsightType.TOP_PERFORMER: "Identify leading values",
                    InsightType.BOTTOM_PERFORMER: "Identify underperforming values",
                    InsightType.SIGNIFICANT_CHANGE: "Detect major changes",
                }.get(t, ""),
                "suggested_chart": CHART_SUGGESTIONS.get(t, "bar"),
            }
            for t in InsightType
        ]
    }


# Quick Insights for Dashboard

@router.post("/dashboard/{dashboard_id}/quick")
async def get_dashboard_quick_insights(
    dashboard_id: str,
    max_insights: int = Query(5, le=20),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Get quick insights for a dashboard.

    Analyzes all charts in the dashboard and returns top insights.
    """
    # Get dashboard
    dashboard = await db.dataviz.dashboards.find_one({"id": dashboard_id})
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # TODO: Implement dashboard data analysis
    return {
        "dashboard_id": dashboard_id,
        "insights": [],
        "summary": {
            "total_insights": 0,
            "by_severity": {"high": 0, "medium": 0, "low": 0},
        },
    }


# Scheduled Analysis

@router.post("/schedule/{target_type}/{target_id}")
async def schedule_insight_analysis(
    target_type: str,
    target_id: str,
    frequency: str = Body("daily", description="Analysis frequency"),
    insight_types: list[InsightType] = Body(None),
    notify_on_high: bool = Body(True),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Schedule recurring insight analysis.

    Sets up automated analysis that runs on a schedule.
    """
    schedule_doc = {
        "id": str(__import__("uuid").uuid4()),
        "target_type": target_type,
        "target_id": target_id,
        "frequency": frequency,
        "insight_types": [t.value for t in insight_types] if insight_types else None,
        "notify_on_high": notify_on_high,
        "created_by": current_user.id,
        "created_at": __import__("datetime").datetime.utcnow(),
        "enabled": True,
    }

    await db.dataviz.insight_schedules.insert_one(schedule_doc)

    return {
        "success": True,
        "schedule_id": schedule_doc["id"],
        "message": f"Insight analysis scheduled to run {frequency}",
    }
