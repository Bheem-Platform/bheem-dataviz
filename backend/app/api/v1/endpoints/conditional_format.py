"""
Conditional Format API Endpoints

Provides endpoints for managing conditional formatting rules.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.dashboard import SavedChart
from app.schemas.conditional_format import (
    ConditionalFormat,
    ChartConditionalFormats,
    FormatTemplate,
    DEFAULT_FORMAT_TEMPLATES,
    ICON_SETS,
)
from app.services.conditional_format_service import get_conditional_format_service

router = APIRouter()


@router.get("/chart/{chart_id}", response_model=ChartConditionalFormats)
async def get_chart_formats(
    chart_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get all conditional formats for a chart.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    formats_config = chart.conditional_formats or []

    return ChartConditionalFormats(
        chart_id=chart_id,
        formats=[ConditionalFormat(**f) for f in formats_config],
    )


@router.put("/chart/{chart_id}")
async def update_chart_formats(
    chart_id: str,
    formats: ChartConditionalFormats,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update all conditional formats for a chart.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    chart.conditional_formats = [f.model_dump() for f in formats.formats]
    db.commit()

    return {"success": True, "message": "Conditional formats updated"}


@router.post("/chart/{chart_id}/format")
async def add_format(
    chart_id: str,
    format: ConditionalFormat,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Add a new conditional format to a chart.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    formats = chart.conditional_formats or []

    # Check for duplicate ID
    if any(f.get("id") == format.id for f in formats):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format with ID '{format.id}' already exists",
        )

    formats.append(format.model_dump())
    chart.conditional_formats = formats
    db.commit()

    return {"success": True, "format_id": format.id}


@router.put("/chart/{chart_id}/format/{format_id}")
async def update_format(
    chart_id: str,
    format_id: str,
    format: ConditionalFormat,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update a specific conditional format.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    formats = chart.conditional_formats or []

    # Find and update the format
    found = False
    for i, f in enumerate(formats):
        if f.get("id") == format_id:
            formats[i] = format.model_dump()
            found = True
            break

    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format '{format_id}' not found",
        )

    chart.conditional_formats = formats
    db.commit()

    return {"success": True, "message": "Format updated"}


@router.delete("/chart/{chart_id}/format/{format_id}")
async def delete_format(
    chart_id: str,
    format_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a conditional format from a chart.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    formats = chart.conditional_formats or []
    original_count = len(formats)

    formats = [f for f in formats if f.get("id") != format_id]

    if len(formats) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format '{format_id}' not found",
        )

    chart.conditional_formats = formats
    db.commit()

    return {"success": True, "message": "Format deleted"}


@router.post("/evaluate")
async def evaluate_formats(
    data: list[dict[str, Any]],
    formats: list[ConditionalFormat],
    current_user: dict = Depends(get_current_user),
):
    """
    Evaluate conditional formats on a dataset.

    Returns the data with formatting information attached.
    """
    service = get_conditional_format_service()
    result = service.evaluate_formats(data, formats)

    return {"data": result}


@router.post("/evaluate/chart/{chart_id}")
async def evaluate_chart_formats(
    chart_id: str,
    data: list[dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Evaluate a chart's conditional formats on provided data.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    formats_config = chart.conditional_formats or []
    formats = [ConditionalFormat(**f) for f in formats_config]

    service = get_conditional_format_service()
    result = service.evaluate_formats(data, formats)

    return {"data": result}


@router.get("/templates", response_model=list[FormatTemplate])
async def get_format_templates(
    current_user: dict = Depends(get_current_user),
):
    """
    Get predefined format templates.
    """
    return DEFAULT_FORMAT_TEMPLATES


@router.get("/icon-sets")
async def get_icon_sets(
    current_user: dict = Depends(get_current_user),
):
    """
    Get available icon sets.
    """
    return ICON_SETS


@router.post("/preview")
async def preview_format(
    sample_data: list[dict[str, Any]],
    format: ConditionalFormat,
    current_user: dict = Depends(get_current_user),
):
    """
    Preview a conditional format on sample data.

    Useful for testing formats before saving.
    """
    service = get_conditional_format_service()
    result = service.evaluate_formats(sample_data, [format])

    return {
        "preview": result,
        "format_applied_count": sum(
            1 for row in result
            if row.get("_formats", {}).get(format.column)
        ),
    }


@router.put("/chart/{chart_id}/reorder")
async def reorder_formats(
    chart_id: str,
    format_ids: list[str],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Reorder conditional formats by updating their priorities.

    The order of format_ids determines the new priority order.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    formats = chart.conditional_formats or []

    # Create lookup
    format_lookup = {f.get("id"): f for f in formats}

    # Update priorities
    for priority, format_id in enumerate(format_ids):
        if format_id in format_lookup:
            format_lookup[format_id]["priority"] = priority

    chart.conditional_formats = list(format_lookup.values())
    db.commit()

    return {"success": True, "message": "Formats reordered"}


@router.put("/chart/{chart_id}/format/{format_id}/toggle")
async def toggle_format(
    chart_id: str,
    format_id: str,
    enabled: bool,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Enable or disable a conditional format.
    """
    chart = db.query(SavedChart).filter(SavedChart.id == chart_id).first()
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        )

    formats = chart.conditional_formats or []

    # Find and toggle the format
    found = False
    for f in formats:
        if f.get("id") == format_id:
            f["enabled"] = enabled
            found = True
            break

    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Format '{format_id}' not found",
        )

    chart.conditional_formats = formats
    db.commit()

    return {"success": True, "enabled": enabled}
