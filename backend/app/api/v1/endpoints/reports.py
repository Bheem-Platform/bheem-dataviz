"""
Reports API Endpoints

REST API for report templates, generation, and export.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.database import get_db
from app.services.report_service import ReportService
from app.schemas.reports import (
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportTemplateResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportJob,
    ReportFormat,
    DashboardExportRequest,
    ChartExportRequest,
    ScheduledReport,
    ScheduledReportConfig,
    TemplatePreview,
    TemplateCategory,
    FORMAT_EXTENSIONS,
    FORMAT_MIME_TYPES,
)

router = APIRouter()


# Template Management

@router.post("/templates", response_model=ReportTemplateResponse)
async def create_template(
    template_data: ReportTemplateCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new report template.

    Templates define the structure, branding, and content
    of generated reports.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ReportService(db)
    return await service.create_template(template_data, user_id)


@router.get("/templates", response_model=list[ReportTemplateResponse])
async def list_templates(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """List report templates with optional filtering."""
    created_by = None
    if request:
        created_by = getattr(request.state, "user_id", None)

    tag_list = tags.split(",") if tags else None

    service = ReportService(db)
    return await service.list_templates(
        workspace_id=workspace_id,
        created_by=created_by,
        is_public=is_public,
        tags=tag_list,
        skip=skip,
        limit=limit,
    )


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific report template by ID."""
    service = ReportService(db)
    template = await service.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.patch("/templates/{template_id}", response_model=ReportTemplateResponse)
async def update_template(
    template_id: str,
    update_data: ReportTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a report template."""
    service = ReportService(db)
    template = await service.update_template(template_id, update_data)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a report template."""
    service = ReportService(db)
    success = await service.delete_template(template_id)

    if not success:
        raise HTTPException(status_code=404, detail="Template not found")

    return {"message": "Template deleted successfully"}


@router.post("/templates/{template_id}/duplicate", response_model=ReportTemplateResponse)
async def duplicate_template(
    template_id: str,
    new_name: str = Query(..., description="Name for the duplicated template"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Duplicate an existing template."""
    user_id = "00000000-0000-0000-0000-000000000000"
    if request:
        user_id = getattr(request.state, "user_id", user_id)

    service = ReportService(db)
    template = await service.duplicate_template(template_id, new_name, user_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


# Report Generation

@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_report(
    generate_request: ReportGenerateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a report.

    Starts a background job to generate the report.
    Use the returned job_id to check status and download.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ReportService(db)
    return await service.generate_report(generate_request, user_id)


@router.get("/jobs/{job_id}", response_model=ReportJob)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get report generation job status."""
    service = ReportService(db)
    job = await service.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/jobs", response_model=list[ReportJob])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """List report generation jobs."""
    created_by = None
    if request:
        created_by = getattr(request.state, "user_id", None)

    service = ReportService(db)
    return await service.list_jobs(
        created_by=created_by,
        status=status,
        limit=limit,
    )


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a pending job."""
    service = ReportService(db)
    success = await service.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Job not found or cannot be cancelled"
        )

    return {"message": "Job cancelled"}


@router.get("/download/{job_id}")
async def download_report(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download a generated report."""
    service = ReportService(db)
    job = await service.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Report not ready. Status: {job.status}"
        )

    # In production, fetch from object storage
    # For now, return placeholder
    content = b"Report content placeholder"
    filename = f"report{FORMAT_EXTENSIONS.get(job.format, '.pdf')}"
    content_type = FORMAT_MIME_TYPES.get(job.format, "application/pdf")

    return StreamingResponse(
        io.BytesIO(content),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# Dashboard Export

@router.post("/export/dashboard", response_model=ReportGenerateResponse)
async def export_dashboard(
    export_request: DashboardExportRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Export a dashboard as PDF, HTML, or Excel.

    This is a convenience endpoint for quick dashboard exports.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ReportService(db)
    return await service.export_dashboard(export_request, user_id)


@router.post("/export/chart")
async def export_chart(
    export_request: ChartExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Export a single chart as image.

    Returns the chart as PNG, JPEG, SVG, or PDF.
    """
    service = ReportService(db)
    return await service.export_chart(export_request)


# Scheduled Reports

@router.post("/scheduled", response_model=ScheduledReport)
async def create_scheduled_report(
    name: str = Query(..., description="Schedule name"),
    config: ScheduledReportConfig = None,
    schedule: str = Query(..., description="Cron expression"),
    recipients: list[str] = Query(..., description="Email recipients"),
    workspace_id: Optional[str] = Query(None, description="Workspace ID"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a scheduled report.

    The report will be generated automatically according to
    the specified cron schedule.
    """
    user_id = "00000000-0000-0000-0000-000000000000"
    if request:
        user_id = getattr(request.state, "user_id", user_id)

    service = ReportService(db)
    return await service.create_scheduled_report(
        name=name,
        config=config,
        schedule=schedule,
        recipients=recipients,
        created_by=user_id,
        workspace_id=workspace_id,
    )


@router.get("/scheduled", response_model=list[ScheduledReport])
async def list_scheduled_reports(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    enabled_only: bool = Query(False, description="Only return enabled"),
    db: AsyncSession = Depends(get_db),
):
    """List scheduled reports."""
    service = ReportService(db)
    return await service.list_scheduled_reports(
        workspace_id=workspace_id,
        enabled_only=enabled_only,
    )


@router.delete("/scheduled/{report_id}")
async def delete_scheduled_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a scheduled report."""
    service = ReportService(db)
    success = await service.delete_scheduled_report(report_id)

    if not success:
        raise HTTPException(status_code=404, detail="Scheduled report not found")

    return {"message": "Scheduled report deleted"}


# Template Library

@router.get("/library/categories", response_model=list[TemplateCategory])
async def get_template_categories(
    db: AsyncSession = Depends(get_db),
):
    """Get available template categories."""
    service = ReportService(db)
    return await service.get_template_categories()


@router.get("/library/built-in", response_model=list[TemplatePreview])
async def get_built_in_templates(
    db: AsyncSession = Depends(get_db),
):
    """Get built-in report templates."""
    service = ReportService(db)
    return await service.get_built_in_templates()


# Format Information

@router.get("/formats")
async def get_available_formats():
    """Get available report formats and their details."""
    return [
        {
            "format": ReportFormat.PDF,
            "name": "PDF",
            "description": "Portable Document Format - best for printing and sharing",
            "extension": ".pdf",
            "supports_charts": True,
            "supports_tables": True,
            "supports_images": True,
        },
        {
            "format": ReportFormat.HTML,
            "name": "HTML",
            "description": "Web page - interactive and linkable",
            "extension": ".html",
            "supports_charts": True,
            "supports_tables": True,
            "supports_images": True,
        },
        {
            "format": ReportFormat.EXCEL,
            "name": "Excel",
            "description": "Spreadsheet - best for data analysis",
            "extension": ".xlsx",
            "supports_charts": True,
            "supports_tables": True,
            "supports_images": False,
        },
        {
            "format": ReportFormat.POWERPOINT,
            "name": "PowerPoint",
            "description": "Presentation - best for meetings",
            "extension": ".pptx",
            "supports_charts": True,
            "supports_tables": True,
            "supports_images": True,
        },
        {
            "format": ReportFormat.IMAGE,
            "name": "Image",
            "description": "PNG/JPEG - best for embedding",
            "extension": ".png",
            "supports_charts": True,
            "supports_tables": False,
            "supports_images": False,
        },
    ]
