"""
Workspace Management API Endpoints

Endpoints for multi-tenant workspace management, member management,
invitations, and workspace settings.
"""

from fastapi import APIRouter, HTTPException, Query, Header
from typing import Optional

from app.schemas.workspace_management import (
    Workspace,
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceStatus,
    WorkspacePlan,
    WorkspaceSettings,
    WorkspaceSettingsUpdate,
    WorkspaceListResponse,
    WorkspaceSummary,
    UserWorkspaces,
    WorkspaceMember,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceMemberListResponse,
    MemberRole,
    MemberStatus,
    Invitation,
    InvitationCreate,
    BulkInvitationCreate,
    InvitationStatus,
    InvitationListResponse,
    InvitationResponse,
    WorkspaceQuota,
    QuotaUsageListResponse,
    Team,
    TeamCreate,
    TeamUpdate,
    TeamListResponse,
    WorkspaceActivityListResponse,
    ResourceType,
    RolePermissions,
    get_role_permissions,
)
from app.services.workspace_management_service import workspace_management_service

router = APIRouter()


# Helper to get current user (simplified)
def get_current_user(
    x_user_id: str = Header(default="current-user"),
    x_user_email: str = Header(default="user@example.com"),
    x_user_name: str = Header(default="Current User"),
):
    return {"id": x_user_id, "email": x_user_email, "name": x_user_name}


# Workspace Endpoints

@router.post("/workspaces", response_model=Workspace)
async def create_workspace(
    data: WorkspaceCreate,
    x_user_id: str = Header(default="current-user"),
    x_user_email: str = Header(default="user@example.com"),
    x_user_name: str = Header(default="Current User"),
):
    """Create a new workspace."""
    try:
        workspace = await workspace_management_service.create_workspace(
            data=data,
            owner_id=x_user_id,
            owner_email=x_user_email,
            owner_name=x_user_name,
        )
        return workspace
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspaces", response_model=WorkspaceListResponse)
async def list_workspaces(
    status: Optional[WorkspaceStatus] = None,
    plan: Optional[WorkspacePlan] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    x_user_id: str = Header(default="current-user"),
):
    """List workspaces."""
    workspaces = await workspace_management_service.list_workspaces(
        user_id=x_user_id,
        status=status,
        plan=plan,
        search=search,
        limit=limit,
        offset=offset,
    )
    return workspaces


@router.get("/workspaces/me", response_model=UserWorkspaces)
async def get_my_workspaces(x_user_id: str = Header(default="current-user")):
    """Get current user's workspaces."""
    return await workspace_management_service.get_user_workspaces(x_user_id)


@router.get("/workspaces/{workspace_id}", response_model=Workspace)
async def get_workspace(workspace_id: str):
    """Get workspace by ID."""
    workspace = await workspace_management_service.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.get("/workspaces/slug/{slug}", response_model=Workspace)
async def get_workspace_by_slug(slug: str):
    """Get workspace by slug."""
    workspace = await workspace_management_service.get_workspace_by_slug(slug)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.patch("/workspaces/{workspace_id}", response_model=Workspace)
async def update_workspace(
    workspace_id: str,
    update: WorkspaceUpdate,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Update workspace."""
    workspace = await workspace_management_service.update_workspace(
        workspace_id=workspace_id,
        update=update,
        user_id=x_user_id,
        user_name=x_user_name,
    )
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Delete workspace."""
    deleted = await workspace_management_service.delete_workspace(
        workspace_id=workspace_id,
        user_id=x_user_id,
        user_name=x_user_name,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"message": "Workspace deleted"}


@router.get("/workspaces/{workspace_id}/summary", response_model=WorkspaceSummary)
async def get_workspace_summary(workspace_id: str):
    """Get workspace summary."""
    summary = await workspace_management_service.get_workspace_summary(workspace_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return summary


# Workspace Settings Endpoints

@router.get("/workspaces/{workspace_id}/settings", response_model=WorkspaceSettings)
async def get_workspace_settings(workspace_id: str):
    """Get workspace settings."""
    settings = await workspace_management_service.get_workspace_settings(workspace_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return settings


@router.put("/workspaces/{workspace_id}/settings", response_model=WorkspaceSettings)
async def update_workspace_settings(
    workspace_id: str,
    update: WorkspaceSettingsUpdate,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Update workspace settings."""
    settings = await workspace_management_service.update_workspace_settings(
        workspace_id=workspace_id,
        update=update,
        user_id=x_user_id,
        user_name=x_user_name,
    )
    if not settings:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return settings


# Member Endpoints

@router.post("/workspaces/{workspace_id}/members", response_model=WorkspaceMember)
async def add_member(
    workspace_id: str,
    data: WorkspaceMemberCreate,
    user_email: str = Query(...),
    user_name: str = Query(...),
    x_user_id: str = Header(default="current-user"),
):
    """Add member to workspace."""
    try:
        member = await workspace_management_service.add_member(
            workspace_id=workspace_id,
            data=data,
            user_email=user_email,
            user_name=user_name,
            invited_by=x_user_id,
        )
        return member
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspaces/{workspace_id}/members", response_model=WorkspaceMemberListResponse)
async def list_members(
    workspace_id: str,
    role: Optional[MemberRole] = None,
    status: Optional[MemberStatus] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List workspace members."""
    members = await workspace_management_service.list_members(
        workspace_id=workspace_id,
        role=role,
        status=status,
        search=search,
        limit=limit,
        offset=offset,
    )
    return members


@router.get("/workspaces/{workspace_id}/members/{user_id}", response_model=WorkspaceMember)
async def get_member(workspace_id: str, user_id: str):
    """Get workspace member."""
    member = await workspace_management_service.get_member(workspace_id, user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.patch("/workspaces/{workspace_id}/members/{user_id}", response_model=WorkspaceMember)
async def update_member(
    workspace_id: str,
    user_id: str,
    update: WorkspaceMemberUpdate,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Update member."""
    try:
        member = await workspace_management_service.update_member(
            workspace_id=workspace_id,
            user_id=user_id,
            update=update,
            updated_by=x_user_id,
            updated_by_name=x_user_name,
        )
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        return member
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/workspaces/{workspace_id}/members/{user_id}")
async def remove_member(
    workspace_id: str,
    user_id: str,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Remove member from workspace."""
    try:
        removed = await workspace_management_service.remove_member(
            workspace_id=workspace_id,
            user_id=user_id,
            removed_by=x_user_id,
            removed_by_name=x_user_name,
        )
        if not removed:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"message": "Member removed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Invitation Endpoints

@router.post("/workspaces/{workspace_id}/invitations", response_model=Invitation)
async def create_invitation(
    workspace_id: str,
    data: InvitationCreate,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Create workspace invitation."""
    try:
        invitation = await workspace_management_service.create_invitation(
            workspace_id=workspace_id,
            data=data,
            invited_by_id=x_user_id,
            invited_by_name=x_user_name,
        )
        return invitation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/workspaces/{workspace_id}/invitations/bulk")
async def create_bulk_invitations(
    workspace_id: str,
    data: BulkInvitationCreate,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Create multiple invitations."""
    invitations = await workspace_management_service.create_bulk_invitations(
        workspace_id=workspace_id,
        data=data,
        invited_by_id=x_user_id,
        invited_by_name=x_user_name,
    )
    return {"invitations": invitations, "count": len(invitations)}


@router.get("/workspaces/{workspace_id}/invitations", response_model=InvitationListResponse)
async def list_invitations(
    workspace_id: str,
    status: Optional[InvitationStatus] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List workspace invitations."""
    invitations = await workspace_management_service.list_invitations(
        workspace_id=workspace_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return invitations


@router.get("/invitations/{invitation_id}", response_model=Invitation)
async def get_invitation(invitation_id: str):
    """Get invitation by ID."""
    invitation = await workspace_management_service.get_invitation(invitation_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return invitation


@router.get("/invitations/token/{token}", response_model=Invitation)
async def get_invitation_by_token(token: str):
    """Get invitation by token."""
    invitation = await workspace_management_service.get_invitation_by_token(token)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation token")
    return invitation


@router.post("/invitations/token/{token}/respond", response_model=Optional[WorkspaceMember])
async def respond_to_invitation(
    token: str,
    response: InvitationResponse,
    x_user_email: str = Header(default="user@example.com"),
    x_user_name: str = Header(default="Current User"),
):
    """Accept or decline invitation."""
    try:
        member = await workspace_management_service.respond_to_invitation(
            token=token,
            response=response,
            user_email=x_user_email,
            user_name=x_user_name,
        )
        return member
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invitations/{invitation_id}/cancel")
async def cancel_invitation(
    invitation_id: str,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Cancel an invitation."""
    cancelled = await workspace_management_service.cancel_invitation(
        invitation_id=invitation_id,
        cancelled_by=x_user_id,
        cancelled_by_name=x_user_name,
    )
    if not cancelled:
        raise HTTPException(status_code=404, detail="Invitation not found or already processed")
    return {"message": "Invitation cancelled"}


@router.post("/invitations/{invitation_id}/resend", response_model=Invitation)
async def resend_invitation(
    invitation_id: str,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Resend an invitation."""
    invitation = await workspace_management_service.resend_invitation(
        invitation_id=invitation_id,
        resent_by=x_user_id,
        resent_by_name=x_user_name,
    )
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or not pending")
    return invitation


# Quota Endpoints

@router.get("/workspaces/{workspace_id}/quota", response_model=WorkspaceQuota)
async def get_workspace_quota(workspace_id: str):
    """Get workspace quota."""
    try:
        quota = await workspace_management_service.get_workspace_quota(workspace_id)
        return quota
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/workspaces/{workspace_id}/quota/usage", response_model=QuotaUsageListResponse)
async def get_quota_usage(workspace_id: str):
    """Get detailed quota usage."""
    try:
        usage = await workspace_management_service.get_quota_usage(workspace_id)
        return usage
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Team Endpoints

@router.post("/workspaces/{workspace_id}/teams", response_model=Team)
async def create_team(
    workspace_id: str,
    data: TeamCreate,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Create a team."""
    team = await workspace_management_service.create_team(
        workspace_id=workspace_id,
        data=data,
        created_by=x_user_id,
        created_by_name=x_user_name,
    )
    return team


@router.get("/workspaces/{workspace_id}/teams", response_model=TeamListResponse)
async def list_teams(
    workspace_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List workspace teams."""
    teams = await workspace_management_service.list_teams(
        workspace_id=workspace_id,
        limit=limit,
        offset=offset,
    )
    return teams


@router.get("/workspaces/{workspace_id}/teams/{team_id}", response_model=Team)
async def get_team(workspace_id: str, team_id: str):
    """Get team by ID."""
    team = await workspace_management_service.get_team(workspace_id, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.patch("/workspaces/{workspace_id}/teams/{team_id}", response_model=Team)
async def update_team(
    workspace_id: str,
    team_id: str,
    update: TeamUpdate,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Update team."""
    team = await workspace_management_service.update_team(
        workspace_id=workspace_id,
        team_id=team_id,
        update=update,
        updated_by=x_user_id,
        updated_by_name=x_user_name,
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.delete("/workspaces/{workspace_id}/teams/{team_id}")
async def delete_team(
    workspace_id: str,
    team_id: str,
    x_user_id: str = Header(default="current-user"),
    x_user_name: str = Header(default="Current User"),
):
    """Delete team."""
    deleted = await workspace_management_service.delete_team(
        workspace_id=workspace_id,
        team_id=team_id,
        deleted_by=x_user_id,
        deleted_by_name=x_user_name,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": "Team deleted"}


# Activity Endpoints

@router.get("/workspaces/{workspace_id}/activity", response_model=WorkspaceActivityListResponse)
async def get_workspace_activity(
    workspace_id: str,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[ResourceType] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Get workspace activity log."""
    activity = await workspace_management_service.get_workspace_activity(
        workspace_id=workspace_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        limit=limit,
        offset=offset,
    )
    return activity


# Permission Endpoints

@router.get("/workspaces/{workspace_id}/permissions/check")
async def check_permission(
    workspace_id: str,
    permission: str,
    x_user_id: str = Header(default="current-user"),
):
    """Check if user has permission."""
    has_permission = await workspace_management_service.check_permission(
        workspace_id=workspace_id,
        user_id=x_user_id,
        permission=permission,
    )
    return {"permission": permission, "allowed": has_permission}


@router.get("/roles/{role}/permissions", response_model=RolePermissions)
async def get_role_permissions_endpoint(role: MemberRole):
    """Get permissions for a role."""
    return get_role_permissions(role)


@router.get("/roles")
async def list_roles():
    """List all available roles."""
    return {
        "roles": [
            {"role": role.value, "label": role.value.title()}
            for role in MemberRole
        ]
    }
