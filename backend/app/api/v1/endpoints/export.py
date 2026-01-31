"""
Export & Document Generation API Endpoints

REST API for creating and managing document exports including
PDF, Excel, PowerPoint, and image exports.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional

from app.schemas.export import (
    ExportFormat, ExportStatus, ExportType,
    ExportRequest, ExportJob, ExportJobUpdate, ExportJobListResponse,
    ExportPreset, ExportPresetCreate, ExportPresetListResponse,
    ExportHistoryListResponse, ExportStats,
    get_mime_type,
)
from app.services.export_service import export_service

router = APIRouter()


# Export Jobs

@router.post("/jobs", response_model=ExportJob, tags=["export-jobs"])
async def create_export_job(
    data: ExportRequest,
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Create a new export job."""
    return export_service.create_export_job(user_id, data, organization_id)


@router.get("/jobs", response_model=ExportJobListResponse, tags=["export-jobs"])
async def list_export_jobs(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    status: Optional[ExportStatus] = Query(None),
    format: Optional[ExportFormat] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List export jobs."""
    return export_service.list_export_jobs(
        user_id, organization_id, status, format, skip, limit
    )


@router.get("/jobs/{job_id}", response_model=ExportJob, tags=["export-jobs"])
async def get_export_job(job_id: str):
    """Get export job by ID."""
    job = export_service.get_export_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    return job


@router.patch("/jobs/{job_id}", response_model=ExportJob, tags=["export-jobs"])
async def update_export_job(job_id: str, data: ExportJobUpdate):
    """Update export job status."""
    job = export_service.update_export_job(job_id, data)
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found")
    return job


@router.post("/jobs/{job_id}/cancel", tags=["export-jobs"])
async def cancel_export_job(job_id: str):
    """Cancel an export job."""
    if export_service.cancel_export_job(job_id):
        return {"success": True, "message": "Export job cancelled"}
    raise HTTPException(status_code=400, detail="Cannot cancel job (not found or already completed)")


@router.delete("/jobs/{job_id}", tags=["export-jobs"])
async def delete_export_job(job_id: str):
    """Delete an export job and its file."""
    if export_service.delete_export_job(job_id):
        return {"success": True, "message": "Export job deleted"}
    raise HTTPException(status_code=404, detail="Export job not found")


@router.get("/jobs/{job_id}/download", tags=["export-jobs"])
async def download_export(job_id: str):
    """Get download information for completed export."""
    download_info = export_service.download_export(job_id)
    if not download_info:
        raise HTTPException(status_code=404, detail="Export not found or not ready")
    return download_info


@router.post("/cleanup", tags=["export-jobs"])
async def cleanup_expired_exports():
    """Clean up expired export jobs."""
    count = export_service.cleanup_expired_exports()
    return {"success": True, "expired_count": count}


# Quick Export Endpoints

@router.post("/quick/pdf", response_model=ExportJob, tags=["quick-export"])
async def quick_export_pdf(
    source_id: str = Query(...),
    export_type: ExportType = Query(ExportType.DASHBOARD),
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Quick PDF export with default settings."""
    return export_service.quick_export_pdf(user_id, source_id, export_type, organization_id)


@router.post("/quick/excel", response_model=ExportJob, tags=["quick-export"])
async def quick_export_excel(
    source_id: str = Query(...),
    export_type: ExportType = Query(ExportType.DATA_TABLE),
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Quick Excel export with default settings."""
    return export_service.quick_export_excel(user_id, source_id, export_type, organization_id)


@router.post("/quick/image", response_model=ExportJob, tags=["quick-export"])
async def quick_export_image(
    source_id: str = Query(...),
    format: ExportFormat = Query(ExportFormat.PNG),
    export_type: ExportType = Query(ExportType.CHART),
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Quick image export with default settings."""
    if format not in [ExportFormat.PNG, ExportFormat.JPEG, ExportFormat.SVG]:
        raise HTTPException(status_code=400, detail="Invalid image format")
    return export_service.quick_export_image(user_id, source_id, format, export_type, organization_id)


# Export Presets

@router.post("/presets", response_model=ExportPreset, tags=["export-presets"])
async def create_export_preset(
    data: ExportPresetCreate,
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Create export preset."""
    return export_service.create_export_preset(user_id, data, organization_id)


@router.get("/presets", response_model=ExportPresetListResponse, tags=["export-presets"])
async def list_export_presets(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    export_type: Optional[ExportType] = Query(None),
    format: Optional[ExportFormat] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List export presets."""
    return export_service.list_export_presets(
        user_id, organization_id, export_type, format, skip, limit
    )


@router.get("/presets/default", response_model=ExportPreset, tags=["export-presets"])
async def get_default_preset(
    user_id: str = Query(...),
    export_type: ExportType = Query(...),
    format: ExportFormat = Query(...),
):
    """Get default preset for user and format."""
    preset = export_service.get_default_preset(user_id, export_type, format)
    if not preset:
        raise HTTPException(status_code=404, detail="No default preset found")
    return preset


@router.get("/presets/{preset_id}", response_model=ExportPreset, tags=["export-presets"])
async def get_export_preset(preset_id: str):
    """Get export preset by ID."""
    preset = export_service.get_export_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset


@router.patch("/presets/{preset_id}", response_model=ExportPreset, tags=["export-presets"])
async def update_export_preset(
    preset_id: str,
    name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    is_default: Optional[bool] = Query(None),
    is_shared: Optional[bool] = Query(None),
):
    """Update export preset."""
    preset = export_service.update_export_preset(
        preset_id, name, description, None, is_default, is_shared
    )
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset


@router.delete("/presets/{preset_id}", tags=["export-presets"])
async def delete_export_preset(preset_id: str):
    """Delete export preset."""
    if export_service.delete_export_preset(preset_id):
        return {"success": True, "message": "Preset deleted"}
    raise HTTPException(status_code=400, detail="Cannot delete preset (not found or system preset)")


# Export History

@router.get("/history", response_model=ExportHistoryListResponse, tags=["export-history"])
async def get_export_history(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    format: Optional[ExportFormat] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get export history."""
    return export_service.get_export_history(user_id, organization_id, format, skip, limit)


# Export Statistics

@router.get("/stats/{organization_id}", response_model=ExportStats, tags=["export-stats"])
async def get_export_stats(organization_id: str):
    """Get export statistics for organization."""
    return export_service.get_export_stats(organization_id)


# Export Formats Info

@router.get("/formats", tags=["export-info"])
async def get_export_formats():
    """Get available export formats and their details."""
    from app.schemas.export import EXPORT_FILE_EXTENSIONS, EXPORT_MIME_TYPES

    formats = []
    for fmt in ExportFormat:
        formats.append({
            "format": fmt.value,
            "extension": EXPORT_FILE_EXTENSIONS.get(fmt),
            "mime_type": EXPORT_MIME_TYPES.get(fmt),
            "supported_types": _get_supported_types(fmt),
        })

    return {"formats": formats}


def _get_supported_types(format: ExportFormat) -> list[str]:
    """Get supported export types for a format."""
    if format == ExportFormat.PDF:
        return [ExportType.DASHBOARD.value, ExportType.REPORT.value, ExportType.CHART.value]
    elif format == ExportFormat.EXCEL:
        return [ExportType.DASHBOARD.value, ExportType.DATA_TABLE.value, ExportType.QUERY_RESULT.value]
    elif format == ExportFormat.POWERPOINT:
        return [ExportType.DASHBOARD.value, ExportType.REPORT.value]
    elif format in [ExportFormat.PNG, ExportFormat.JPEG, ExportFormat.SVG]:
        return [ExportType.CHART.value, ExportType.DASHBOARD.value]
    elif format == ExportFormat.CSV:
        return [ExportType.DATA_TABLE.value, ExportType.QUERY_RESULT.value]
    elif format == ExportFormat.JSON:
        return [ExportType.DATA_TABLE.value, ExportType.QUERY_RESULT.value, ExportType.CHART.value]
    return []
