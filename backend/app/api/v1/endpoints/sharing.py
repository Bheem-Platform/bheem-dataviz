"""
Sharing API Endpoints

REST API for public links, password protection, and sharing features.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.sharing_service import SharingService
from app.schemas.sharing import (
    ShareType,
    ShareAccess,
    ShareLinkCreate,
    ShareLinkUpdate,
    ShareLink,
    ShareAccessRequest,
    ShareAccessResponse,
    ShareAnalytics,
    QRCodeConfig,
    QRCodeResponse,
    EmailShareRequest,
    EmailShareResponse,
    ShareTemplate,
)

router = APIRouter()


# Share Link CRUD

@router.post("/links", response_model=ShareLink)
async def create_share_link(
    data: ShareLinkCreate,
    resource_name: str = Query(..., description="Name of the resource being shared"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new share link.

    Creates a shareable link for a dashboard, chart, report, or dataset.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    user_name = getattr(request.state, "user_name", "Anonymous User")

    service = SharingService(db)
    try:
        return await service.create_share_link(
            data=data,
            resource_name=resource_name,
            created_by=user_id,
            created_by_name=user_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/links", response_model=list[ShareLink])
async def list_share_links(
    workspace_id: Optional[str] = Query(None),
    resource_type: Optional[ShareType] = Query(None),
    resource_id: Optional[str] = Query(None),
    include_revoked: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """List share links created by the current user."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SharingService(db)
    links, total = await service.list_share_links(
        user_id=user_id,
        workspace_id=workspace_id,
        resource_type=resource_type,
        resource_id=resource_id,
        include_revoked=include_revoked,
        skip=skip,
        limit=limit,
    )

    return links


@router.get("/links/{link_id}", response_model=ShareLink)
async def get_share_link(
    link_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a share link by ID."""
    service = SharingService(db)
    link = await service.get_share_link(link_id)

    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")

    return link


@router.patch("/links/{link_id}", response_model=ShareLink)
async def update_share_link(
    link_id: str,
    update: ShareLinkUpdate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update a share link."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SharingService(db)
    link = await service.update_share_link(link_id, update, user_id)

    if not link:
        raise HTTPException(status_code=404, detail="Share link not found or not authorized")

    return link


@router.delete("/links/{link_id}")
async def delete_share_link(
    link_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete a share link."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SharingService(db)
    success = await service.delete_share_link(link_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Share link not found or not authorized")

    return {"deleted": True}


@router.post("/links/{link_id}/revoke", response_model=ShareLink)
async def revoke_share_link(
    link_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Revoke a share link (soft delete)."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SharingService(db)
    link = await service.revoke_share_link(link_id, user_id)

    if not link:
        raise HTTPException(status_code=404, detail="Share link not found or not authorized")

    return link


# Access Validation (Public endpoints)

@router.post("/access", response_model=ShareAccessResponse)
async def validate_share_access(
    data: ShareAccessRequest,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    db: AsyncSession = Depends(get_db),
):
    """
    Validate access to a shared resource.

    This is a public endpoint used when accessing a share link.
    """
    # Get client IP
    viewer_ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else None

    service = SharingService(db)
    return await service.validate_access(
        request=data,
        viewer_ip=viewer_ip,
        user_agent=user_agent,
    )


@router.get("/access/{code}", response_model=ShareAccessResponse)
async def access_by_code(
    code: str,
    password: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    db: AsyncSession = Depends(get_db),
):
    """
    Access a shared resource by short code or custom slug.

    This is a public endpoint for accessing share links.
    """
    viewer_ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else None

    service = SharingService(db)
    return await service.validate_access(
        request=ShareAccessRequest(
            token=code,
            password=password,
            viewer_email=email,
            viewer_name=name,
        ),
        viewer_ip=viewer_ip,
        user_agent=user_agent,
    )


# Analytics

@router.get("/links/{link_id}/analytics", response_model=ShareAnalytics)
async def get_share_analytics(
    link_id: str,
    days: int = Query(30, ge=1, le=365),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for a share link."""
    service = SharingService(db)
    analytics = await service.get_share_analytics(link_id, days)

    if not analytics:
        raise HTTPException(status_code=404, detail="Share link not found")

    return analytics


# QR Code

@router.post("/links/{link_id}/qr", response_model=QRCodeResponse)
async def generate_qr_code(
    link_id: str,
    config: Optional[QRCodeConfig] = None,
    db: AsyncSession = Depends(get_db),
):
    """Generate QR code for a share link."""
    service = SharingService(db)
    qr = await service.generate_qr_code(link_id, config)

    if not qr:
        raise HTTPException(status_code=404, detail="Share link not found")

    return qr


@router.get("/qr/{link_id}.{format}")
async def get_qr_code_image(
    link_id: str,
    format: str = "png",
    size: int = Query(256, ge=64, le=1024),
    db: AsyncSession = Depends(get_db),
):
    """
    Get QR code image for a share link.

    Returns the actual QR code image file.
    """
    # In production, generate and return actual QR code image
    # For now, return a placeholder response
    return {
        "message": "QR code generation not implemented",
        "link_id": link_id,
        "format": format,
        "size": size,
    }


# Email Sharing

@router.post("/links/{link_id}/email", response_model=EmailShareResponse)
async def send_share_email(
    link_id: str,
    data: EmailShareRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Send share link via email."""
    user_name = getattr(request.state, "user_name", "Anonymous User")
    user_email = getattr(request.state, "user_email", "anonymous@example.com")

    data.share_link_id = link_id

    service = SharingService(db)
    return await service.send_share_email(
        request=data,
        sender_name=user_name,
        sender_email=user_email,
    )


# Templates

@router.post("/templates", response_model=ShareTemplate)
async def create_template(
    name: str = Query(...),
    settings: ShareLinkCreate = None,
    description: Optional[str] = Query(None),
    workspace_id: Optional[str] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a share settings template."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SharingService(db)
    return await service.create_template(
        name=name,
        settings=settings or ShareLinkCreate(
            resource_type=ShareType.DASHBOARD,
            resource_id="template",
        ),
        created_by=user_id,
        workspace_id=workspace_id,
        description=description,
    )


@router.get("/templates", response_model=list[ShareTemplate])
async def list_templates(
    workspace_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List share settings templates."""
    service = SharingService(db)
    return await service.list_templates(workspace_id)


# Quick Share Helpers

@router.post("/quick/{resource_type}/{resource_id}", response_model=ShareLink)
async def quick_share(
    resource_type: ShareType,
    resource_id: str,
    resource_name: str = Query(...),
    access_level: ShareAccess = Query(ShareAccess.VIEW),
    expires_in_days: Optional[int] = Query(None, ge=1, le=365),
    require_password: bool = Query(False),
    password: Optional[str] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Quick share a resource with minimal configuration.

    Creates a share link with sensible defaults.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    user_name = getattr(request.state, "user_name", "Anonymous User")

    from datetime import datetime, timedelta

    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    data = ShareLinkCreate(
        resource_type=resource_type,
        resource_id=resource_id,
        access_level=access_level,
        visibility="password" if require_password else "public",
        password=password if require_password else None,
        expires_at=expires_at,
    )

    service = SharingService(db)
    return await service.create_share_link(
        data=data,
        resource_name=resource_name,
        created_by=user_id,
        created_by_name=user_name,
    )


# Bulk Operations

@router.post("/bulk/create")
async def bulk_create_share_links(
    resource_type: ShareType,
    resource_ids: list[str],
    access_level: ShareAccess = Query(ShareAccess.VIEW),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create share links for multiple resources."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")
    user_name = getattr(request.state, "user_name", "Anonymous User")

    service = SharingService(db)
    created = []
    failed = []

    for resource_id in resource_ids:
        try:
            data = ShareLinkCreate(
                resource_type=resource_type,
                resource_id=resource_id,
                access_level=access_level,
            )
            link = await service.create_share_link(
                data=data,
                resource_name=f"{resource_type.value} {resource_id[:8]}",
                created_by=user_id,
                created_by_name=user_name,
            )
            created.append(link)
        except Exception as e:
            failed.append({"resource_id": resource_id, "error": str(e)})

    return {
        "created": created,
        "failed": failed,
        "total_created": len(created),
        "total_failed": len(failed),
    }


@router.post("/bulk/revoke")
async def bulk_revoke_share_links(
    link_ids: list[str],
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Revoke multiple share links."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SharingService(db)
    revoked = []
    failed = []

    for link_id in link_ids:
        result = await service.revoke_share_link(link_id, user_id)
        if result:
            revoked.append(link_id)
        else:
            failed.append(link_id)

    return {
        "revoked": revoked,
        "failed": failed,
        "total_revoked": len(revoked),
        "total_failed": len(failed),
    }
