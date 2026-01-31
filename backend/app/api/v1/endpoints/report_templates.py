"""
Report Templates API Endpoints

REST API for managing report templates, versions, categories, and instances.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.report_template import (
    TemplateType, TemplateStatus,
    ReportTemplate, ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateListResponse,
    TemplateVersion, TemplateVersionListResponse,
    TemplateCategory, TemplateCategoryCreate, TemplateCategoryListResponse,
    TemplateInstance, TemplateInstanceCreate, TemplateInstanceListResponse,
)
from app.services.report_template_service import report_template_service

router = APIRouter()


# Template CRUD Endpoints

@router.post("/", response_model=ReportTemplate, tags=["report-templates"])
async def create_template(
    data: ReportTemplateCreate,
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Create a new report template."""
    return report_template_service.create_template(user_id, data, organization_id)


@router.get("/", response_model=ReportTemplateListResponse, tags=["report-templates"])
async def list_templates(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    template_type: Optional[TemplateType] = Query(None),
    status: Optional[TemplateStatus] = Query(None),
    category: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List report templates with filtering."""
    return report_template_service.list_templates(
        user_id, organization_id, template_type, status,
        category, is_public, search, skip, limit
    )


@router.get("/system", response_model=ReportTemplateListResponse, tags=["report-templates"])
async def list_system_templates(
    template_type: Optional[TemplateType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List system (built-in) templates."""
    return report_template_service.list_templates(
        is_public=True, template_type=template_type, skip=skip, limit=limit
    )


@router.get("/{template_id}", response_model=ReportTemplate, tags=["report-templates"])
async def get_template(template_id: str):
    """Get template by ID."""
    template = report_template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.patch("/{template_id}", response_model=ReportTemplate, tags=["report-templates"])
async def update_template(
    template_id: str,
    data: ReportTemplateUpdate,
    user_id: str = Query(...),
):
    """Update a report template."""
    template = report_template_service.update_template(template_id, data, user_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or cannot be modified")
    return template


@router.delete("/{template_id}", tags=["report-templates"])
async def delete_template(template_id: str):
    """Delete a report template."""
    if report_template_service.delete_template(template_id):
        return {"success": True, "message": "Template deleted"}
    raise HTTPException(status_code=400, detail="Cannot delete template (not found or system template)")


@router.post("/{template_id}/duplicate", response_model=ReportTemplate, tags=["report-templates"])
async def duplicate_template(
    template_id: str,
    user_id: str = Query(...),
    new_name: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
):
    """Duplicate a template."""
    template = report_template_service.duplicate_template(
        template_id, user_id, new_name, organization_id
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/{template_id}/publish", response_model=ReportTemplate, tags=["report-templates"])
async def publish_template(
    template_id: str,
    user_id: str = Query(...),
):
    """Publish a draft template."""
    from app.schemas.report_template import ReportTemplateUpdate
    update_data = ReportTemplateUpdate(status=TemplateStatus.PUBLISHED)
    template = report_template_service.update_template(template_id, update_data, user_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/{template_id}/archive", response_model=ReportTemplate, tags=["report-templates"])
async def archive_template(
    template_id: str,
    user_id: str = Query(...),
):
    """Archive a template."""
    from app.schemas.report_template import ReportTemplateUpdate
    update_data = ReportTemplateUpdate(status=TemplateStatus.ARCHIVED)
    template = report_template_service.update_template(template_id, update_data, user_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


# Version Management Endpoints

@router.get("/{template_id}/versions", response_model=TemplateVersionListResponse, tags=["template-versions"])
async def list_versions(
    template_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List versions for a template."""
    template = report_template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return report_template_service.list_versions(template_id, skip, limit)


@router.get("/versions/{version_id}", response_model=TemplateVersion, tags=["template-versions"])
async def get_version(version_id: str):
    """Get a specific version."""
    version = report_template_service.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.post("/{template_id}/versions/{version_id}/restore", response_model=ReportTemplate, tags=["template-versions"])
async def restore_version(
    template_id: str,
    version_id: str,
    user_id: str = Query(...),
):
    """Restore a template to a previous version."""
    template = report_template_service.restore_version(template_id, version_id, user_id)
    if not template:
        raise HTTPException(status_code=400, detail="Cannot restore version")
    return template


# Category Endpoints

@router.get("/categories/", response_model=TemplateCategoryListResponse, tags=["template-categories"])
async def list_categories(
    parent_id: Optional[str] = Query(None),
):
    """List template categories."""
    return report_template_service.list_categories(parent_id)


@router.post("/categories/", response_model=TemplateCategory, tags=["template-categories"])
async def create_category(data: TemplateCategoryCreate):
    """Create a template category."""
    return report_template_service.create_category(data)


@router.delete("/categories/{category_id}", tags=["template-categories"])
async def delete_category(category_id: str):
    """Delete a category."""
    if report_template_service.delete_category(category_id):
        return {"success": True, "message": "Category deleted"}
    raise HTTPException(status_code=400, detail="Cannot delete category (not found or has templates)")


# Template Instance Endpoints

@router.post("/instances", response_model=TemplateInstance, tags=["template-instances"])
async def create_instance(
    data: TemplateInstanceCreate,
    user_id: str = Query(...),
    organization_id: Optional[str] = Query(None),
):
    """Create a template instance for report generation."""
    instance = report_template_service.create_instance(user_id, data, organization_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Template not found")
    return instance


@router.get("/instances", response_model=TemplateInstanceListResponse, tags=["template-instances"])
async def list_instances(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    template_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List template instances."""
    return report_template_service.list_instances(
        user_id, organization_id, template_id, skip, limit
    )


@router.get("/instances/{instance_id}", response_model=TemplateInstance, tags=["template-instances"])
async def get_instance(instance_id: str):
    """Get instance by ID."""
    instance = report_template_service.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance


@router.patch("/instances/{instance_id}", response_model=TemplateInstance, tags=["template-instances"])
async def update_instance(
    instance_id: str,
    placeholder_values: Optional[dict] = None,
    filters: Optional[dict] = None,
    parameters: Optional[dict] = None,
):
    """Update a template instance."""
    instance = report_template_service.update_instance(
        instance_id, placeholder_values, filters, parameters
    )
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance


@router.delete("/instances/{instance_id}", tags=["template-instances"])
async def delete_instance(instance_id: str):
    """Delete an instance."""
    if report_template_service.delete_instance(instance_id):
        return {"success": True, "message": "Instance deleted"}
    raise HTTPException(status_code=404, detail="Instance not found")
