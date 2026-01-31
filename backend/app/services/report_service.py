"""
Report Service

Handles report template management and generation.
"""

import uuid
import asyncio
from typing import Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import io
import base64

from app.schemas.reports import (
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportTemplateResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportJob,
    ReportFormat,
    PageConfig,
    BrandingConfig,
    ReportSection,
    DashboardExportRequest,
    ChartExportRequest,
    ScheduledReport,
    ScheduledReportConfig,
    TemplatePreview,
    TemplateCategory,
    BUILT_IN_TEMPLATES,
    FORMAT_EXTENSIONS,
    FORMAT_MIME_TYPES,
)


logger = logging.getLogger(__name__)


class ReportService:
    """Service for managing reports and exports."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._templates: dict[str, dict] = {}
        self._jobs: dict[str, dict] = {}
        self._scheduled_reports: dict[str, dict] = {}

    # Template Management

    async def create_template(
        self,
        data: ReportTemplateCreate,
        created_by: str,
    ) -> ReportTemplateResponse:
        """Create a new report template."""
        template_id = str(uuid.uuid4())
        now = datetime.utcnow()

        template = {
            "id": template_id,
            "name": data.name,
            "description": data.description,
            "page_config": data.page_config.model_dump(),
            "branding": data.branding.model_dump(),
            "sections": [s.model_dump() for s in data.sections],
            "workspace_id": data.workspace_id,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
            "is_public": data.is_public,
            "usage_count": 0,
            "tags": data.tags,
        }

        self._templates[template_id] = template

        return self._to_template_response(template)

    async def get_template(self, template_id: str) -> Optional[ReportTemplateResponse]:
        """Get a template by ID."""
        template = self._templates.get(template_id)
        if not template:
            return None
        return self._to_template_response(template)

    async def list_templates(
        self,
        workspace_id: Optional[str] = None,
        created_by: Optional[str] = None,
        is_public: Optional[bool] = None,
        tags: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ReportTemplateResponse]:
        """List templates with optional filtering."""
        templates = list(self._templates.values())

        if workspace_id:
            templates = [t for t in templates if t.get("workspace_id") == workspace_id]
        if created_by:
            templates = [t for t in templates if t.get("created_by") == created_by]
        if is_public is not None:
            templates = [t for t in templates if t.get("is_public") == is_public]
        if tags:
            templates = [
                t for t in templates
                if any(tag in t.get("tags", []) for tag in tags)
            ]

        templates.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        templates = templates[skip:skip + limit]

        return [self._to_template_response(t) for t in templates]

    async def update_template(
        self,
        template_id: str,
        data: ReportTemplateUpdate,
    ) -> Optional[ReportTemplateResponse]:
        """Update a template."""
        template = self._templates.get(template_id)
        if not template:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "page_config" and value is not None:
                template["page_config"] = value.model_dump() if hasattr(value, 'model_dump') else value
            elif field == "branding" and value is not None:
                template["branding"] = value.model_dump() if hasattr(value, 'model_dump') else value
            elif field == "sections" and value is not None:
                template["sections"] = [s.model_dump() if hasattr(s, 'model_dump') else s for s in value]
            else:
                template[field] = value

        template["updated_at"] = datetime.utcnow()

        return self._to_template_response(template)

    async def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False

    async def duplicate_template(
        self,
        template_id: str,
        new_name: str,
        created_by: str,
    ) -> Optional[ReportTemplateResponse]:
        """Duplicate a template."""
        template = self._templates.get(template_id)
        if not template:
            return None

        new_id = str(uuid.uuid4())
        now = datetime.utcnow()

        new_template = {
            **template,
            "id": new_id,
            "name": new_name,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
            "is_public": False,
            "usage_count": 0,
        }

        self._templates[new_id] = new_template

        return self._to_template_response(new_template)

    # Report Generation

    async def generate_report(
        self,
        request: ReportGenerateRequest,
        created_by: str,
    ) -> ReportGenerateResponse:
        """Generate a report."""
        job_id = str(uuid.uuid4())
        now = datetime.utcnow()

        job = {
            "id": job_id,
            "template_id": request.template_id,
            "dashboard_id": request.dashboard_id,
            "title": request.title,
            "format": request.format,
            "status": "pending",
            "progress": 0,
            "created_by": created_by,
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "error_message": None,
            "download_url": None,
            "file_size": None,
            "expires_at": now + timedelta(hours=24),
            "request": request.model_dump(),
        }

        self._jobs[job_id] = job

        # Start generation in background
        asyncio.create_task(self._process_report_job(job_id))

        return ReportGenerateResponse(
            job_id=job_id,
            status="pending",
            format=request.format,
            message="Report generation started",
        )

    async def get_job_status(self, job_id: str) -> Optional[ReportJob]:
        """Get report generation job status."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        return ReportJob(**{k: v for k, v in job.items() if k != "request"})

    async def list_jobs(
        self,
        created_by: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[ReportJob]:
        """List report generation jobs."""
        jobs = list(self._jobs.values())

        if created_by:
            jobs = [j for j in jobs if j.get("created_by") == created_by]
        if status:
            jobs = [j for j in jobs if j.get("status") == status]

        jobs.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        jobs = jobs[:limit]

        return [ReportJob(**{k: v for k, v in j.items() if k != "request"}) for j in jobs]

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        job = self._jobs.get(job_id)
        if not job or job["status"] != "pending":
            return False

        job["status"] = "cancelled"
        return True

    async def _process_report_job(self, job_id: str):
        """Process a report generation job."""
        job = self._jobs.get(job_id)
        if not job:
            return

        try:
            job["status"] = "processing"
            job["started_at"] = datetime.utcnow()
            job["progress"] = 10

            request_data = job["request"]
            report_format = request_data.get("format", "pdf")

            # Simulate processing steps
            await asyncio.sleep(0.5)
            job["progress"] = 30

            # Generate content based on format
            if report_format == ReportFormat.PDF:
                content = await self._generate_pdf_report(request_data)
            elif report_format == ReportFormat.HTML:
                content = await self._generate_html_report(request_data)
            elif report_format == ReportFormat.EXCEL:
                content = await self._generate_excel_report(request_data)
            else:
                content = await self._generate_html_report(request_data)

            job["progress"] = 80

            # In production, save to object storage and return URL
            # For now, simulate completion
            job["progress"] = 100
            job["status"] = "completed"
            job["completed_at"] = datetime.utcnow()
            job["download_url"] = f"/api/v1/reports/download/{job_id}"
            job["file_size"] = len(content) if isinstance(content, bytes) else len(content.encode())

            # Increment template usage count
            if job.get("template_id") and job["template_id"] in self._templates:
                self._templates[job["template_id"]]["usage_count"] += 1

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            job["status"] = "failed"
            job["error_message"] = str(e)
            job["completed_at"] = datetime.utcnow()

    async def _generate_pdf_report(self, request_data: dict) -> bytes:
        """Generate PDF report."""
        # In production, use a library like weasyprint, reportlab, or puppeteer
        html_content = await self._generate_html_report(request_data)

        # Placeholder - in production, convert HTML to PDF
        return html_content.encode()

    async def _generate_html_report(self, request_data: dict) -> str:
        """Generate HTML report."""
        title = request_data.get("title", "Report")
        subtitle = request_data.get("subtitle", "")

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1f2937; line-height: 1.6; }}
        .report-container {{ max-width: 1000px; margin: 0 auto; padding: 40px; }}
        .cover-page {{ text-align: center; padding: 100px 20px; page-break-after: always; }}
        .cover-title {{ font-size: 36px; font-weight: 700; margin-bottom: 16px; }}
        .cover-subtitle {{ font-size: 18px; color: #6b7280; margin-bottom: 40px; }}
        .cover-date {{ font-size: 14px; color: #9ca3af; }}
        .section {{ margin-bottom: 40px; page-break-inside: avoid; }}
        .section-title {{ font-size: 24px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #e5e7eb; }}
        .chart-container {{ background: #f9fafb; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .kpi-card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; }}
        .kpi-label {{ font-size: 14px; color: #6b7280; margin-bottom: 8px; }}
        .kpi-value {{ font-size: 32px; font-weight: 700; color: #1f2937; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        tr:hover {{ background: #f9fafb; }}
        .page-break {{ page-break-after: always; }}
        @media print {{
            body {{ print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
            .report-container {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="cover-page">
            <h1 class="cover-title">{title}</h1>
            {f'<p class="cover-subtitle">{subtitle}</p>' if subtitle else ''}
            <p class="cover-date">Generated on {datetime.utcnow().strftime('%B %d, %Y')}</p>
        </div>

        <div class="section">
            <h2 class="section-title">Overview</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Total Revenue</div>
                    <div class="kpi-value">$1.2M</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Growth Rate</div>
                    <div class="kpi-value">+15%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Active Users</div>
                    <div class="kpi-value">45.2K</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Conversion</div>
                    <div class="kpi-value">3.2%</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Summary</h2>
            <p>This report provides an overview of key metrics and performance indicators.
            The data presented covers the reporting period and highlights important trends
            and insights for decision-making.</p>
        </div>
    </div>
</body>
</html>
        """

        return html

    async def _generate_excel_report(self, request_data: dict) -> bytes:
        """Generate Excel report."""
        # In production, use openpyxl or xlsxwriter
        # For now, return placeholder
        return b"Excel content placeholder"

    # Dashboard Export

    async def export_dashboard(
        self,
        request: DashboardExportRequest,
        created_by: str,
    ) -> ReportGenerateResponse:
        """Export a dashboard."""
        generate_request = ReportGenerateRequest(
            dashboard_id=request.dashboard_id,
            title=request.title or "Dashboard Export",
            format=request.format,
            include_cover_page=False,
        )

        return await self.generate_report(generate_request, created_by)

    async def export_chart(
        self,
        request: ChartExportRequest,
    ) -> dict[str, Any]:
        """Export a single chart as image."""
        # In production, render chart and return image data
        return {
            "chart_id": request.chart_id,
            "format": request.format,
            "width": request.width,
            "height": request.height,
            "data": base64.b64encode(b"PNG image data").decode(),
            "content_type": f"image/{request.format}",
        }

    # Scheduled Reports

    async def create_scheduled_report(
        self,
        name: str,
        config: ScheduledReportConfig,
        schedule: str,
        recipients: list[str],
        created_by: str,
        workspace_id: Optional[str] = None,
    ) -> ScheduledReport:
        """Create a scheduled report."""
        report_id = str(uuid.uuid4())
        now = datetime.utcnow()

        scheduled = {
            "id": report_id,
            "name": name,
            "config": config.model_dump(),
            "schedule": schedule,
            "recipients": recipients,
            "enabled": True,
            "workspace_id": workspace_id,
            "created_by": created_by,
            "created_at": now,
            "last_generated_at": None,
            "next_generation_at": self._calculate_next_run(schedule, now),
        }

        self._scheduled_reports[report_id] = scheduled

        return ScheduledReport(**scheduled)

    async def list_scheduled_reports(
        self,
        workspace_id: Optional[str] = None,
        enabled_only: bool = False,
    ) -> list[ScheduledReport]:
        """List scheduled reports."""
        reports = list(self._scheduled_reports.values())

        if workspace_id:
            reports = [r for r in reports if r.get("workspace_id") == workspace_id]
        if enabled_only:
            reports = [r for r in reports if r.get("enabled")]

        return [ScheduledReport(**r) for r in reports]

    async def delete_scheduled_report(self, report_id: str) -> bool:
        """Delete a scheduled report."""
        if report_id in self._scheduled_reports:
            del self._scheduled_reports[report_id]
            return True
        return False

    # Template Library

    async def get_template_categories(self) -> list[TemplateCategory]:
        """Get template categories."""
        categories = [
            {"id": "business", "name": "Business", "description": "General business reports"},
            {"id": "finance", "name": "Finance", "description": "Financial reports and analysis"},
            {"id": "sales", "name": "Sales", "description": "Sales performance reports"},
            {"id": "marketing", "name": "Marketing", "description": "Marketing analytics"},
            {"id": "operations", "name": "Operations", "description": "Operational dashboards"},
            {"id": "custom", "name": "Custom", "description": "User-created templates"},
        ]

        # Count templates per category
        for cat in categories:
            cat["template_count"] = sum(
                1 for t in self._templates.values()
                if t.get("category") == cat["id"]
            )
            # Add built-in templates
            cat["template_count"] += sum(
                1 for t in BUILT_IN_TEMPLATES
                if t.get("category") == cat["id"]
            )

        return [TemplateCategory(**c) for c in categories]

    async def get_built_in_templates(self) -> list[TemplatePreview]:
        """Get built-in report templates."""
        return [
            TemplatePreview(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                category=t["category"],
                tags=t["tags"],
                is_public=True,
            )
            for t in BUILT_IN_TEMPLATES
        ]

    # Helper Methods

    def _calculate_next_run(self, schedule: str, from_time: datetime) -> datetime:
        """Calculate next run time from cron schedule."""
        try:
            from croniter import croniter
            cron = croniter(schedule, from_time)
            return cron.get_next(datetime)
        except Exception:
            # Default to next day at 9 AM
            return from_time.replace(hour=9, minute=0, second=0) + timedelta(days=1)

    def _to_template_response(self, template: dict) -> ReportTemplateResponse:
        """Convert template dict to response schema."""
        return ReportTemplateResponse(
            id=template["id"],
            name=template["name"],
            description=template.get("description"),
            page_config=PageConfig(**template.get("page_config", {})),
            branding=BrandingConfig(**template.get("branding", {})),
            sections=[ReportSection(**s) for s in template.get("sections", [])],
            workspace_id=template.get("workspace_id"),
            created_by=template["created_by"],
            created_at=template["created_at"],
            updated_at=template["updated_at"],
            is_public=template.get("is_public", False),
            usage_count=template.get("usage_count", 0),
            tags=template.get("tags", []),
        )
