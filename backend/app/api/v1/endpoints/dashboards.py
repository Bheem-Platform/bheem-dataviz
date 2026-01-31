"""Dashboard and saved chart API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.dashboard import Dashboard as DashboardModel, SavedChart as SavedChartModel, SuggestedQuestion as SuggestedQuestionModel
from app.models.transform import TransformRecipe as TransformRecipeModel
from app.schemas.dashboard import (
    Dashboard, DashboardCreate, DashboardUpdate, DashboardSummary,
    SavedChart, SavedChartCreate, SavedChartUpdate,
    SuggestedQuestion, SuggestedQuestionCreate,
    HomePageData, TransformRecipeSummary
)
from app.core.security import get_current_user, CurrentUser

router = APIRouter()


# ============== Home Page ==============

@router.get("/home", response_model=HomePageData)
async def get_home_page_data(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get data for the home page dashboard grid."""

    # Get featured dashboards
    featured_result = await db.execute(
        select(DashboardModel)
        .where(DashboardModel.is_featured == True)
        .order_by(DashboardModel.updated_at.desc())
        .limit(6)
    )
    featured_dashboards = featured_result.scalars().all()

    # Get chart counts for dashboards
    featured_summaries = []
    for dashboard in featured_dashboards:
        count_result = await db.execute(
            select(func.count(SavedChartModel.id))
            .where(SavedChartModel.dashboard_id == dashboard.id)
        )
        chart_count = count_result.scalar() or 0
        featured_summaries.append(DashboardSummary(
            id=dashboard.id,
            name=dashboard.name,
            description=dashboard.description,
            icon=dashboard.icon,
            is_public=dashboard.is_public,
            is_featured=dashboard.is_featured,
            chart_count=chart_count,
            created_at=dashboard.created_at,
            updated_at=dashboard.updated_at
        ))

    # Get recent charts
    recent_result = await db.execute(
        select(SavedChartModel)
        .order_by(SavedChartModel.updated_at.desc())
        .limit(8)
    )
    recent_charts = recent_result.scalars().all()

    # Get favorite charts
    favorite_result = await db.execute(
        select(SavedChartModel)
        .where(SavedChartModel.is_favorite == True)
        .order_by(SavedChartModel.updated_at.desc())
        .limit(8)
    )
    favorite_charts = favorite_result.scalars().all()

    # Get suggested questions
    questions_result = await db.execute(
        select(SuggestedQuestionModel)
        .where(SuggestedQuestionModel.is_active == True)
        .order_by(SuggestedQuestionModel.sort_order)
        .limit(6)
    )
    suggested_questions = questions_result.scalars().all()

    # Get recent transform recipes
    transforms_result = await db.execute(
        select(TransformRecipeModel)
        .order_by(TransformRecipeModel.updated_at.desc())
        .limit(6)
    )
    transforms = transforms_result.scalars().all()

    transform_summaries = [
        TransformRecipeSummary(
            id=t.id,
            name=t.name,
            description=t.description,
            connection_id=t.connection_id,
            source_table=t.source_table,
            source_schema=t.source_schema,
            steps_count=len(t.steps) if t.steps else 0,
            row_count=t.row_count,
            last_executed=t.last_executed,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in transforms
    ]

    return HomePageData(
        featured_dashboards=featured_summaries,
        recent_charts=recent_charts,
        favorite_charts=favorite_charts,
        suggested_questions=suggested_questions,
        recent_transforms=transform_summaries
    )


# ============== Dashboards ==============

@router.get("/", response_model=List[DashboardSummary])
async def list_dashboards(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """List all dashboards with chart counts."""
    result = await db.execute(
        select(DashboardModel).order_by(DashboardModel.updated_at.desc())
    )
    dashboards = result.scalars().all()

    summaries = []
    for dashboard in dashboards:
        count_result = await db.execute(
            select(func.count(SavedChartModel.id))
            .where(SavedChartModel.dashboard_id == dashboard.id)
        )
        chart_count = count_result.scalar() or 0
        summaries.append(DashboardSummary(
            id=dashboard.id,
            name=dashboard.name,
            description=dashboard.description,
            icon=dashboard.icon,
            is_public=dashboard.is_public,
            is_featured=dashboard.is_featured,
            chart_count=chart_count,
            created_at=dashboard.created_at,
            updated_at=dashboard.updated_at
        ))

    return summaries


@router.post("/", response_model=Dashboard)
async def create_dashboard(
    dashboard: DashboardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Create a new dashboard."""
    db_dashboard = DashboardModel(**dashboard.model_dump())
    db.add(db_dashboard)
    await db.commit()
    await db.refresh(db_dashboard)

    # Fetch with charts relationship loaded to avoid lazy loading issues
    result = await db.execute(
        select(DashboardModel)
        .options(selectinload(DashboardModel.charts))
        .where(DashboardModel.id == db_dashboard.id)
    )
    return result.scalar_one()


@router.get("/{dashboard_id}", response_model=Dashboard)
async def get_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get a dashboard with all its charts."""
    result = await db.execute(
        select(DashboardModel)
        .options(selectinload(DashboardModel.charts))
        .where(DashboardModel.id == dashboard_id)
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    return dashboard


@router.patch("/{dashboard_id}", response_model=Dashboard)
async def update_dashboard(
    dashboard_id: UUID,
    dashboard_update: DashboardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Update a dashboard."""
    result = await db.execute(
        select(DashboardModel).where(DashboardModel.id == dashboard_id)
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    update_data = dashboard_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dashboard, field, value)

    await db.commit()

    # Fetch with charts relationship loaded to avoid lazy loading issues
    result = await db.execute(
        select(DashboardModel)
        .options(selectinload(DashboardModel.charts))
        .where(DashboardModel.id == dashboard_id)
    )
    return result.scalar_one()


@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Delete a dashboard and all its charts."""
    result = await db.execute(
        select(DashboardModel).where(DashboardModel.id == dashboard_id)
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    await db.delete(dashboard)
    await db.commit()
    return {"status": "deleted"}


# ============== Saved Charts ==============

@router.get("/charts/all", response_model=List[SavedChart])
async def list_all_charts(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """List all saved charts."""
    result = await db.execute(
        select(SavedChartModel)
        .order_by(SavedChartModel.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/charts", response_model=SavedChart)
async def create_chart(
    chart: SavedChartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Save a new chart."""
    db_chart = SavedChartModel(**chart.model_dump())
    db.add(db_chart)
    await db.commit()
    await db.refresh(db_chart)
    return db_chart


@router.get("/charts/{chart_id}", response_model=SavedChart)
async def get_chart(
    chart_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get a saved chart."""
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    # Update view count
    chart.view_count += 1
    chart.last_viewed_at = datetime.utcnow()
    await db.commit()

    return chart


@router.patch("/charts/{chart_id}", response_model=SavedChart)
async def update_chart(
    chart_id: UUID,
    chart_update: SavedChartUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Update a saved chart."""
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    update_data = chart_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chart, field, value)

    await db.commit()
    await db.refresh(chart)
    return chart


@router.delete("/charts/{chart_id}")
async def delete_chart(
    chart_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Delete a saved chart."""
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    await db.delete(chart)
    await db.commit()
    return {"status": "deleted"}


@router.post("/charts/{chart_id}/favorite", response_model=SavedChart)
async def toggle_favorite(
    chart_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Toggle favorite status of a chart."""
    result = await db.execute(
        select(SavedChartModel).where(SavedChartModel.id == chart_id)
    )
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    chart.is_favorite = not chart.is_favorite
    await db.commit()
    await db.refresh(chart)
    return chart


# ============== Suggested Questions ==============

@router.get("/questions", response_model=List[SuggestedQuestion])
async def list_suggested_questions(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """List all suggested questions."""
    result = await db.execute(
        select(SuggestedQuestionModel)
        .where(SuggestedQuestionModel.is_active == True)
        .order_by(SuggestedQuestionModel.sort_order)
    )
    return result.scalars().all()


@router.post("/questions", response_model=SuggestedQuestion)
async def create_suggested_question(
    question: SuggestedQuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Create a new suggested question."""
    db_question = SuggestedQuestionModel(**question.model_dump())
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return db_question


@router.delete("/questions/{question_id}")
async def delete_suggested_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Delete a suggested question."""
    result = await db.execute(
        select(SuggestedQuestionModel).where(SuggestedQuestionModel.id == question_id)
    )
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    await db.delete(question)
    await db.commit()
    return {"status": "deleted"}
