"""
Workspace API Endpoints

Provides endpoints for workspace management, membership, and permissions.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceSummary,
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    InvitationCreate,
    InvitationResponse,
    InvitationAccept,
    BulkInvite,
    BulkInviteResponse,
    ObjectPermissionCreate,
    ObjectPermissionResponse,
    PermissionCheck,
    PermissionCheckResponse,
    TransferOwnership,
    WorkspaceSettings,
    WorkspaceRole,
    InviteStatus,
    ROLE_PERMISSIONS,
)
from app.services.workspace_service import get_workspace_service

router = APIRouter()


# ========================================================================
# WORKSPACE CRUD
# ========================================================================

@router.get("/", response_model=list[WorkspaceSummary])
async def list_workspaces(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all workspaces the current user is a member of"""
    service = get_workspace_service(db)
    return await service.list_user_workspaces(current_user.id)


@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workspace"""
    service = get_workspace_service(db)
    workspace = await service.create_workspace(
        data=data,
        owner_id=current_user.id,
    )

    member_count = await service.get_member_count(str(workspace.id))

    return WorkspaceResponse(
        id=str(workspace.id),
        name=workspace.name,
        slug=workspace.slug,
        description=workspace.description,
        owner_id=str(workspace.owner_id),
        is_personal=workspace.is_personal,
        is_default=workspace.is_default,
        logo_url=workspace.logo_url,
        primary_color=workspace.primary_color,
        settings=workspace.settings or {},
        is_active=workspace.is_active,
        member_count=member_count,
        dashboard_count=0,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )


@router.get("/personal", response_model=WorkspaceResponse)
async def get_personal_workspace(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get or create the current user's personal workspace"""
    service = get_workspace_service(db)
    workspace = await service.get_or_create_personal_workspace(
        user_id=current_user.id,
        user_email=current_user.email,
    )

    member_count = await service.get_member_count(str(workspace.id))

    return WorkspaceResponse(
        id=str(workspace.id),
        name=workspace.name,
        slug=workspace.slug,
        description=workspace.description,
        owner_id=str(workspace.owner_id),
        is_personal=workspace.is_personal,
        is_default=workspace.is_default,
        logo_url=workspace.logo_url,
        primary_color=workspace.primary_color,
        settings=workspace.settings or {},
        is_active=workspace.is_active,
        member_count=member_count,
        dashboard_count=0,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a workspace by ID"""
    service = get_workspace_service(db)

    # Verify membership
    member = await service.get_member(workspace_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    workspace = await service.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    member_count = await service.get_member_count(workspace_id)

    return WorkspaceResponse(
        id=str(workspace.id),
        name=workspace.name,
        slug=workspace.slug,
        description=workspace.description,
        owner_id=str(workspace.owner_id),
        is_personal=workspace.is_personal,
        is_default=workspace.is_default,
        logo_url=workspace.logo_url,
        primary_color=workspace.primary_color,
        settings=workspace.settings or {},
        is_active=workspace.is_active,
        member_count=member_count,
        dashboard_count=0,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    data: WorkspaceUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a workspace"""
    service = get_workspace_service(db)

    # Check permission
    has_permission = await service.check_permission(
        workspace_id,
        current_user.id,
        "can_manage_workspace",
    )
    if not has_permission:
        # Allow admin to update non-ownership fields
        member = await service.get_member(workspace_id, current_user.id)
        if not member or member.role.value not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    workspace = await service.update_workspace(workspace_id, data)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    member_count = await service.get_member_count(workspace_id)

    return WorkspaceResponse(
        id=str(workspace.id),
        name=workspace.name,
        slug=workspace.slug,
        description=workspace.description,
        owner_id=str(workspace.owner_id),
        is_personal=workspace.is_personal,
        is_default=workspace.is_default,
        logo_url=workspace.logo_url,
        primary_color=workspace.primary_color,
        settings=workspace.settings or {},
        is_active=workspace.is_active,
        member_count=member_count,
        dashboard_count=0,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a workspace (owner only)"""
    service = get_workspace_service(db)

    workspace = await service.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if str(workspace.owner_id) != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner can delete a workspace")

    try:
        await service.delete_workspace(workspace_id)
        return {"success": True, "message": "Workspace deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workspace_id}/transfer-ownership")
async def transfer_ownership(
    workspace_id: str,
    data: TransferOwnership,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transfer workspace ownership to another member"""
    service = get_workspace_service(db)

    try:
        await service.transfer_ownership(
            workspace_id=workspace_id,
            current_owner_id=current_user.id,
            new_owner_id=data.new_owner_id,
        )
        return {"success": True, "message": "Ownership transferred"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========================================================================
# MEMBERS
# ========================================================================

@router.get("/{workspace_id}/members", response_model=list[MemberResponse])
async def list_members(
    workspace_id: str,
    include_inactive: bool = Query(False),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List workspace members"""
    service = get_workspace_service(db)

    # Verify membership
    member = await service.get_member(workspace_id, current_user.id)
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    members = await service.list_members(workspace_id, include_inactive)

    return [
        MemberResponse(
            id=str(m.id),
            workspace_id=str(m.workspace_id),
            user_id=str(m.user_id),
            role=WorkspaceRole(m.role.value),
            custom_permissions=m.custom_permissions or {},
            is_active=m.is_active,
            joined_at=m.joined_at,
            last_accessed_at=m.last_accessed_at,
        )
        for m in members
    ]


@router.post("/{workspace_id}/members", response_model=MemberResponse)
async def add_member(
    workspace_id: str,
    data: MemberCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a member to a workspace (admin only)"""
    service = get_workspace_service(db)

    has_permission = await service.check_permission(
        workspace_id,
        current_user.id,
        "can_manage_members",
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        member = await service.add_member(
            workspace_id=workspace_id,
            user_id=data.user_id,
            role=data.role,
            invited_by=current_user.id,
        )

        return MemberResponse(
            id=str(member.id),
            workspace_id=str(member.workspace_id),
            user_id=str(member.user_id),
            role=WorkspaceRole(member.role.value),
            custom_permissions=member.custom_permissions or {},
            is_active=member.is_active,
            joined_at=member.joined_at,
            last_accessed_at=member.last_accessed_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{workspace_id}/members/{user_id}", response_model=MemberResponse)
async def update_member(
    workspace_id: str,
    user_id: str,
    data: MemberUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a workspace member"""
    service = get_workspace_service(db)

    has_permission = await service.check_permission(
        workspace_id,
        current_user.id,
        "can_manage_members",
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    member = await service.update_member(workspace_id, user_id, data)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    return MemberResponse(
        id=str(member.id),
        workspace_id=str(member.workspace_id),
        user_id=str(member.user_id),
        role=WorkspaceRole(member.role.value),
        custom_permissions=member.custom_permissions or {},
        is_active=member.is_active,
        joined_at=member.joined_at,
        last_accessed_at=member.last_accessed_at,
    )


@router.delete("/{workspace_id}/members/{user_id}")
async def remove_member(
    workspace_id: str,
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from a workspace"""
    service = get_workspace_service(db)

    # Allow self-removal or admin removal
    if user_id != current_user.id:
        has_permission = await service.check_permission(
            workspace_id,
            current_user.id,
            "can_manage_members",
        )
        if not has_permission:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        if not await service.remove_member(workspace_id, user_id):
            raise HTTPException(status_code=404, detail="Member not found")
        return {"success": True, "message": "Member removed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========================================================================
# INVITATIONS
# ========================================================================

@router.get("/{workspace_id}/invitations", response_model=list[InvitationResponse])
async def list_invitations(
    workspace_id: str,
    status: Optional[InviteStatus] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List workspace invitations"""
    service = get_workspace_service(db)

    has_permission = await service.check_permission(
        workspace_id,
        current_user.id,
        "can_manage_members",
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    invitations = await service.list_invitations(workspace_id, status)

    return [
        InvitationResponse(
            id=str(inv.id),
            workspace_id=str(inv.workspace_id),
            email=inv.email,
            role=WorkspaceRole(inv.role.value),
            status=InviteStatus(inv.status.value),
            message=inv.message,
            invited_by=str(inv.invited_by),
            expires_at=inv.expires_at,
            created_at=inv.created_at,
            accepted_at=inv.accepted_at,
        )
        for inv in invitations
    ]


@router.post("/{workspace_id}/invitations", response_model=InvitationResponse)
async def create_invitation(
    workspace_id: str,
    data: InvitationCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a workspace invitation"""
    service = get_workspace_service(db)

    has_permission = await service.check_permission(
        workspace_id,
        current_user.id,
        "can_manage_members",
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        invitation = await service.create_invitation(
            workspace_id=workspace_id,
            data=data,
            invited_by=current_user.id,
        )

        return InvitationResponse(
            id=str(invitation.id),
            workspace_id=str(invitation.workspace_id),
            email=invitation.email,
            role=WorkspaceRole(invitation.role.value),
            status=InviteStatus(invitation.status.value),
            message=invitation.message,
            invited_by=str(invitation.invited_by),
            expires_at=invitation.expires_at,
            created_at=invitation.created_at,
            accepted_at=invitation.accepted_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workspace_id}/invitations/bulk", response_model=BulkInviteResponse)
async def bulk_invite(
    workspace_id: str,
    data: BulkInvite,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send bulk invitations"""
    service = get_workspace_service(db)

    has_permission = await service.check_permission(
        workspace_id,
        current_user.id,
        "can_manage_members",
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    sent = []
    failed = []

    for email in data.emails:
        try:
            await service.create_invitation(
                workspace_id=workspace_id,
                data=InvitationCreate(
                    email=email,
                    role=data.role,
                    message=data.message,
                ),
                invited_by=current_user.id,
            )
            sent.append(email)
        except ValueError as e:
            failed.append({"email": email, "reason": str(e)})

    return BulkInviteResponse(
        sent=sent,
        failed=failed,
        total_sent=len(sent),
        total_failed=len(failed),
    )


@router.post("/invitations/accept", response_model=MemberResponse)
async def accept_invitation(
    data: InvitationAccept,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept a workspace invitation"""
    service = get_workspace_service(db)

    try:
        member = await service.accept_invitation(
            token=data.token,
            user_id=current_user.id,
        )

        return MemberResponse(
            id=str(member.id),
            workspace_id=str(member.workspace_id),
            user_id=str(member.user_id),
            role=WorkspaceRole(member.role.value),
            custom_permissions=member.custom_permissions or {},
            is_active=member.is_active,
            joined_at=member.joined_at,
            last_accessed_at=member.last_accessed_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invitations/decline")
async def decline_invitation(
    data: InvitationAccept,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Decline a workspace invitation"""
    service = get_workspace_service(db)

    if not await service.decline_invitation(data.token):
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")

    return {"success": True, "message": "Invitation declined"}


@router.delete("/{workspace_id}/invitations/{invitation_id}")
async def cancel_invitation(
    workspace_id: str,
    invitation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a pending invitation"""
    service = get_workspace_service(db)

    has_permission = await service.check_permission(
        workspace_id,
        current_user.id,
        "can_manage_members",
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if not await service.cancel_invitation(invitation_id):
        raise HTTPException(status_code=404, detail="Invitation not found or not pending")

    return {"success": True, "message": "Invitation cancelled"}


# ========================================================================
# PERMISSIONS
# ========================================================================

@router.post("/{workspace_id}/check-permission", response_model=PermissionCheckResponse)
async def check_permission(
    workspace_id: str,
    data: PermissionCheck,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if user has permission for an action"""
    service = get_workspace_service(db)

    allowed = await service.check_permission(
        workspace_id=workspace_id,
        user_id=current_user.id,
        action=data.action,
        object_type=data.object_type,
        object_id=data.object_id,
    )

    return PermissionCheckResponse(allowed=allowed)


@router.post("/{workspace_id}/permissions", response_model=ObjectPermissionResponse)
async def set_object_permission(
    workspace_id: str,
    data: ObjectPermissionCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set object-level permissions"""
    service = get_workspace_service(db)

    has_permission = await service.check_permission(
        workspace_id,
        current_user.id,
        "can_manage_members",
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        permission = await service.set_object_permission(
            workspace_id=workspace_id,
            data=data,
            created_by=current_user.id,
        )

        return ObjectPermissionResponse(
            id=str(permission.id),
            workspace_id=str(permission.workspace_id),
            object_type=permission.object_type,
            object_id=str(permission.object_id),
            user_id=str(permission.user_id) if permission.user_id else None,
            role=WorkspaceRole(permission.role.value) if permission.role else None,
            can_view=permission.can_view,
            can_edit=permission.can_edit,
            can_delete=permission.can_delete,
            can_share=permission.can_share,
            can_export=permission.can_export,
            created_at=permission.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========================================================================
# ROLE PERMISSIONS INFO
# ========================================================================

@router.get("/roles/permissions")
async def get_role_permissions(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get default permissions for each role"""
    return ROLE_PERMISSIONS
