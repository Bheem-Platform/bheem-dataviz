"""
Export & Document Generation Service

Service for generating PDF, Excel, PowerPoint, and image exports
from dashboards, charts, and data.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

from app.schemas.export import (
    ExportFormat, ExportStatus, ExportType,
    ExportRequest, ExportJob, ExportJobUpdate, ExportJobListResponse,
    ExportPreset, ExportPresetCreate, ExportPresetListResponse,
    ExportHistoryEntry, ExportHistoryListResponse,
    ExportStats,
    PDFExportConfig, ExcelExportConfig, PowerPointExportConfig,
    ImageExportConfig, CSVExportConfig, JSONExportConfig,
    generate_export_filename, get_file_extension, get_mime_type,
    DEFAULT_EXPORT_EXPIRY_HOURS, EXPORT_RETENTION_DAYS,
)


class ExportService:
    """Service for document export functionality."""

    def __init__(self):
        # In-memory stores (use database/object storage in production)
        self._export_jobs: Dict[str, ExportJob] = {}
        self._export_presets: Dict[str, ExportPreset] = {}
        self._export_history: List[ExportHistoryEntry] = []

        # Initialize default presets
        self._init_default_presets()

    def _init_default_presets(self):
        """Initialize default export presets."""
        default_presets = [
            ExportPreset(
                id="preset-pdf-default",
                name="Standard PDF",
                description="Default PDF export with A4 landscape",
                export_type=ExportType.DASHBOARD,
                format=ExportFormat.PDF,
                config=PDFExportConfig().model_dump(),
                user_id="system",
                is_default=True,
                is_shared=True,
            ),
            ExportPreset(
                id="preset-excel-default",
                name="Standard Excel",
                description="Default Excel export with formatting",
                export_type=ExportType.DASHBOARD,
                format=ExportFormat.EXCEL,
                config=ExcelExportConfig().model_dump(),
                user_id="system",
                is_default=True,
                is_shared=True,
            ),
            ExportPreset(
                id="preset-png-high",
                name="High Quality Image",
                description="PNG export at 300 DPI for printing",
                export_type=ExportType.CHART,
                format=ExportFormat.PNG,
                config=ImageExportConfig().model_dump(),
                user_id="system",
                is_default=True,
                is_shared=True,
            ),
        ]
        for preset in default_presets:
            self._export_presets[preset.id] = preset

    # Export Jobs

    def create_export_job(
        self,
        user_id: str,
        request: ExportRequest,
        organization_id: Optional[str] = None,
    ) -> ExportJob:
        """Create a new export job."""
        job_id = f"export-{secrets.token_hex(8)}"
        now = datetime.utcnow()

        # Generate filename if not provided
        filename = request.filename
        if not filename:
            source_name = self._get_source_name(request.export_type, request.source_id)
            filename = generate_export_filename(source_name, request.format)

        # Build config based on format
        config = {}
        if request.format == ExportFormat.PDF and request.pdf_config:
            config = request.pdf_config.model_dump()
        elif request.format == ExportFormat.EXCEL and request.excel_config:
            config = request.excel_config.model_dump()
        elif request.format == ExportFormat.POWERPOINT and request.powerpoint_config:
            config = request.powerpoint_config.model_dump()
        elif request.format in [ExportFormat.PNG, ExportFormat.JPEG, ExportFormat.SVG]:
            config = (request.image_config or ImageExportConfig()).model_dump()
        elif request.format == ExportFormat.CSV:
            config = (request.csv_config or CSVExportConfig()).model_dump()
        elif request.format == ExportFormat.JSON:
            config = (request.json_config or JSONExportConfig()).model_dump()

        job = ExportJob(
            id=job_id,
            user_id=user_id,
            organization_id=organization_id,
            export_type=request.export_type,
            format=request.format,
            source_id=request.source_id,
            source_name=self._get_source_name(request.export_type, request.source_id),
            filename=filename,
            status=ExportStatus.PENDING,
            config=config,
            expires_at=now + timedelta(hours=DEFAULT_EXPORT_EXPIRY_HOURS),
            metadata={
                "filters": request.filters,
                "parameters": request.parameters,
                "notify": request.notify_on_completion,
                "notification_email": request.notification_email,
            },
        )

        self._export_jobs[job_id] = job

        # Start processing (in production, this would be a background task)
        self._process_export_job(job_id)

        return job

    def _get_source_name(self, export_type: ExportType, source_id: str) -> str:
        """Get display name for export source."""
        # In production, this would query the actual source
        type_names = {
            ExportType.DASHBOARD: "Dashboard",
            ExportType.CHART: "Chart",
            ExportType.REPORT: "Report",
            ExportType.QUERY_RESULT: "Query Result",
            ExportType.DATA_TABLE: "Data Table",
        }
        return f"{type_names.get(export_type, 'Export')}_{source_id[:8]}"

    def _process_export_job(self, job_id: str):
        """Process an export job (simulation)."""
        job = self._export_jobs.get(job_id)
        if not job:
            return

        # Update status to processing
        job.status = ExportStatus.PROCESSING
        job.started_at = datetime.utcnow()
        job.progress = 10

        # Simulate export processing
        # In production, this would:
        # 1. Fetch data from source
        # 2. Apply filters/parameters
        # 3. Generate document using appropriate library
        # 4. Upload to object storage
        # 5. Update job with file URL

        # Simulate completion
        job.progress = 100
        job.status = ExportStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.file_size = 1024 * 50  # 50 KB simulated
        job.file_url = f"/exports/{job_id}/{job.filename}"

        # Add to history
        duration = (job.completed_at - job.started_at).total_seconds() if job.started_at else 0
        history_entry = ExportHistoryEntry(
            id=f"hist-{secrets.token_hex(8)}",
            job_id=job_id,
            user_id=job.user_id,
            export_type=job.export_type,
            format=job.format,
            source_id=job.source_id,
            source_name=job.source_name,
            filename=job.filename,
            file_size=job.file_size,
            status=job.status,
            duration_seconds=duration,
        )
        self._export_history.append(history_entry)

    def get_export_job(self, job_id: str) -> Optional[ExportJob]:
        """Get export job by ID."""
        return self._export_jobs.get(job_id)

    def update_export_job(self, job_id: str, data: ExportJobUpdate) -> Optional[ExportJob]:
        """Update export job."""
        job = self._export_jobs.get(job_id)
        if not job:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(job, key, value)

        if data.status == ExportStatus.COMPLETED:
            job.completed_at = datetime.utcnow()

        return job

    def cancel_export_job(self, job_id: str) -> bool:
        """Cancel an export job."""
        job = self._export_jobs.get(job_id)
        if not job:
            return False

        if job.status in [ExportStatus.COMPLETED, ExportStatus.FAILED, ExportStatus.CANCELLED]:
            return False

        job.status = ExportStatus.CANCELLED
        return True

    def list_export_jobs(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        status: Optional[ExportStatus] = None,
        format: Optional[ExportFormat] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ExportJobListResponse:
        """List export jobs."""
        jobs = list(self._export_jobs.values())

        if user_id:
            jobs = [j for j in jobs if j.user_id == user_id]
        if organization_id:
            jobs = [j for j in jobs if j.organization_id == organization_id]
        if status:
            jobs = [j for j in jobs if j.status == status]
        if format:
            jobs = [j for j in jobs if j.format == format]

        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return ExportJobListResponse(
            jobs=jobs[skip:skip + limit],
            total=len(jobs),
        )

    def download_export(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get export file for download."""
        job = self._export_jobs.get(job_id)
        if not job or job.status != ExportStatus.COMPLETED:
            return None

        # Increment download count
        job.download_count += 1

        # Update history
        for entry in self._export_history:
            if entry.job_id == job_id:
                entry.downloaded = True
                entry.downloaded_at = datetime.utcnow()
                break

        return {
            "filename": job.filename,
            "file_url": job.file_url,
            "mime_type": get_mime_type(job.format),
            "file_size": job.file_size,
        }

    def delete_export_job(self, job_id: str) -> bool:
        """Delete an export job."""
        if job_id in self._export_jobs:
            # In production, also delete file from storage
            del self._export_jobs[job_id]
            return True
        return False

    def cleanup_expired_exports(self) -> int:
        """Clean up expired export jobs."""
        now = datetime.utcnow()
        expired_ids = [
            j.id for j in self._export_jobs.values()
            if j.expires_at and j.expires_at < now
        ]

        for job_id in expired_ids:
            self._export_jobs[job_id].status = ExportStatus.EXPIRED
            # In production, also delete files from storage

        return len(expired_ids)

    # Export Presets

    def create_export_preset(
        self,
        user_id: str,
        data: ExportPresetCreate,
        organization_id: Optional[str] = None,
    ) -> ExportPreset:
        """Create export preset."""
        preset_id = f"preset-{secrets.token_hex(8)}"

        preset = ExportPreset(
            id=preset_id,
            user_id=user_id,
            organization_id=organization_id,
            **data.model_dump(),
        )

        # If setting as default, unset other defaults
        if data.is_default:
            for existing in self._export_presets.values():
                if (existing.user_id == user_id and
                    existing.export_type == data.export_type and
                    existing.format == data.format):
                    existing.is_default = False

        self._export_presets[preset_id] = preset
        return preset

    def get_export_preset(self, preset_id: str) -> Optional[ExportPreset]:
        """Get export preset by ID."""
        return self._export_presets.get(preset_id)

    def get_default_preset(
        self,
        user_id: str,
        export_type: ExportType,
        format: ExportFormat,
    ) -> Optional[ExportPreset]:
        """Get default preset for user and format."""
        # First check user's default
        for preset in self._export_presets.values():
            if (preset.user_id == user_id and
                preset.export_type == export_type and
                preset.format == format and
                preset.is_default):
                return preset

        # Fall back to system default
        for preset in self._export_presets.values():
            if (preset.user_id == "system" and
                preset.export_type == export_type and
                preset.format == format and
                preset.is_default):
                return preset

        return None

    def update_export_preset(
        self,
        preset_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        is_default: Optional[bool] = None,
        is_shared: Optional[bool] = None,
    ) -> Optional[ExportPreset]:
        """Update export preset."""
        preset = self._export_presets.get(preset_id)
        if not preset:
            return None

        if name:
            preset.name = name
        if description is not None:
            preset.description = description
        if config:
            preset.config = config
        if is_default is not None:
            preset.is_default = is_default
        if is_shared is not None:
            preset.is_shared = is_shared

        preset.updated_at = datetime.utcnow()
        return preset

    def delete_export_preset(self, preset_id: str) -> bool:
        """Delete export preset."""
        if preset_id in self._export_presets:
            # Don't delete system presets
            if self._export_presets[preset_id].user_id == "system":
                return False
            del self._export_presets[preset_id]
            return True
        return False

    def list_export_presets(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        export_type: Optional[ExportType] = None,
        format: Optional[ExportFormat] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ExportPresetListResponse:
        """List export presets."""
        presets = list(self._export_presets.values())

        # Filter to user's presets + shared presets + system presets
        if user_id:
            presets = [
                p for p in presets
                if p.user_id == user_id or p.is_shared or p.user_id == "system"
            ]
        if organization_id:
            presets = [
                p for p in presets
                if p.organization_id == organization_id or p.organization_id is None
            ]
        if export_type:
            presets = [p for p in presets if p.export_type == export_type]
        if format:
            presets = [p for p in presets if p.format == format]

        presets.sort(key=lambda p: (not p.is_default, p.name))
        return ExportPresetListResponse(
            presets=presets[skip:skip + limit],
            total=len(presets),
        )

    # Export History

    def get_export_history(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        format: Optional[ExportFormat] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ExportHistoryListResponse:
        """Get export history."""
        entries = list(self._export_history)

        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if format:
            entries = [e for e in entries if e.format == format]

        entries.sort(key=lambda e: e.created_at, reverse=True)
        return ExportHistoryListResponse(
            entries=entries[skip:skip + limit],
            total=len(entries),
        )

    # Export Statistics

    def get_export_stats(self, organization_id: str) -> ExportStats:
        """Get export statistics for organization."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        jobs = [
            j for j in self._export_jobs.values()
            if j.organization_id == organization_id
        ]

        completed_jobs = [j for j in jobs if j.status == ExportStatus.COMPLETED]

        # Count by time period
        exports_today = len([j for j in completed_jobs if j.created_at >= today_start])
        exports_week = len([j for j in completed_jobs if j.created_at >= week_start])
        exports_month = len([j for j in completed_jobs if j.created_at >= month_start])

        # Count by format
        exports_by_format = {}
        for j in completed_jobs:
            fmt = j.format.value
            exports_by_format[fmt] = exports_by_format.get(fmt, 0) + 1

        # Count by type
        exports_by_type = {}
        for j in completed_jobs:
            t = j.export_type.value
            exports_by_type[t] = exports_by_type.get(t, 0) + 1

        # Calculate totals
        total_size = sum(j.file_size or 0 for j in completed_jobs)
        durations = [
            (j.completed_at - j.started_at).total_seconds()
            for j in completed_jobs
            if j.started_at and j.completed_at
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Success rate
        total_jobs = len(jobs)
        success_rate = len(completed_jobs) / total_jobs if total_jobs > 0 else 1.0

        return ExportStats(
            organization_id=organization_id,
            total_exports=len(completed_jobs),
            exports_today=exports_today,
            exports_this_week=exports_week,
            exports_this_month=exports_month,
            exports_by_format=exports_by_format,
            exports_by_type=exports_by_type,
            total_file_size_bytes=total_size,
            average_duration_seconds=avg_duration,
            success_rate=success_rate,
        )

    # Quick Export Methods

    def quick_export_pdf(
        self,
        user_id: str,
        source_id: str,
        export_type: ExportType = ExportType.DASHBOARD,
        organization_id: Optional[str] = None,
    ) -> ExportJob:
        """Quick PDF export with default settings."""
        request = ExportRequest(
            export_type=export_type,
            format=ExportFormat.PDF,
            source_id=source_id,
            pdf_config=PDFExportConfig(),
        )
        return self.create_export_job(user_id, request, organization_id)

    def quick_export_excel(
        self,
        user_id: str,
        source_id: str,
        export_type: ExportType = ExportType.DATA_TABLE,
        organization_id: Optional[str] = None,
    ) -> ExportJob:
        """Quick Excel export with default settings."""
        request = ExportRequest(
            export_type=export_type,
            format=ExportFormat.EXCEL,
            source_id=source_id,
            excel_config=ExcelExportConfig(),
        )
        return self.create_export_job(user_id, request, organization_id)

    def quick_export_image(
        self,
        user_id: str,
        source_id: str,
        format: ExportFormat = ExportFormat.PNG,
        export_type: ExportType = ExportType.CHART,
        organization_id: Optional[str] = None,
    ) -> ExportJob:
        """Quick image export with default settings."""
        request = ExportRequest(
            export_type=export_type,
            format=format,
            source_id=source_id,
            image_config=ImageExportConfig(format=format),
        )
        return self.create_export_job(user_id, request, organization_id)


# Create singleton instance
export_service = ExportService()
