"""
Workspace Management Service

Service for multi-tenant workspace management, member management,
invitations, and workspace settings.
"""

import uuid
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional
from collections import defaultdict

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
    QuotaUsage,
    QuotaUsageListResponse,
    Team,
    TeamCreate,
    TeamUpdate,
    TeamListResponse,
    WorkspaceActivity,
    WorkspaceActivityListResponse,
    ResourceType,
    ResourcePermission,
    RolePermissions,
    get_plan_limits,
    get_role_permissions,
    check_quota,
    PLAN_LIMITS,
)


class WorkspaceManagementService:
    """Service for workspace management."""

    def __init__(self):
        # In-memory stores (production would use database)
        self._workspaces: dict[str, Workspace] = {}
        self._workspace_settings: dict[str, WorkspaceSettings] = {}
        self._members: dict[str, dict[str, WorkspaceMember]] = defaultdict(dict)
        self._invitations: dict[str, Invitation] = {}
        self._teams: dict[str, dict[str, Team]] = defaultdict(dict)
        self._activities: dict[str, list[WorkspaceActivity]] = defaultdict(list)
        self._resource_permissions: dict[str, list[ResourcePermission]] = defaultdict(list)

        # Index for quick lookups
        self._user_workspaces: dict[str, list[str]] = defaultdict(list)
        self._invitation_by_token: dict[str, str] = {}
        self._invitation_by_email: dict[str, list[str]] = defaultdict(list)

    # Workspace Management

    async def create_workspace(
        self,
        data: WorkspaceCreate,
        owner_id: str,
        owner_email: str,
        owner_name: str,
    ) -> Workspace:
        """Create a new workspace."""
        workspace_id = str(uuid.uuid4())

        # Check slug uniqueness
        for ws in self._workspaces.values():
            if ws.slug == data.slug:
                raise ValueError(f"Workspace slug '{data.slug}' already exists")

        workspace = Workspace(
            id=workspace_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            logo_url=data.logo_url,
            status=WorkspaceStatus.ACTIVE,
            plan=data.plan,
            owner_id=owner_id,
            member_count=1,
            settings=data.settings,
            metadata=data.metadata,
            trial_ends_at=datetime.utcnow() + timedelta(days=14) if data.plan == WorkspacePlan.FREE else None,
        )

        self._workspaces[workspace_id] = workspace

        # Create default settings
        limits = get_plan_limits(data.plan)
        settings = WorkspaceSettings(
            workspace_id=workspace_id,
            max_connections=limits.get("max_connections", 10),
            max_dashboards=limits.get("max_dashboards", 50),
            max_members=limits.get("max_members", 10),
        )
        self._workspace_settings[workspace_id] = settings

        # Add owner as member
        owner_member = WorkspaceMember(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            user_id=owner_id,
            email=owner_email,
            name=owner_name,
            role=MemberRole.OWNER,
            status=MemberStatus.ACTIVE,
            permissions={},
        )
        self._members[workspace_id][owner_id] = owner_member
        self._user_workspaces[owner_id].append(workspace_id)

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=owner_id,
            user_name=owner_name,
            action="workspace.created",
            details={"workspace_name": data.name},
        )

        return workspace

    async def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID."""
        return self._workspaces.get(workspace_id)

    async def get_workspace_by_slug(self, slug: str) -> Optional[Workspace]:
        """Get workspace by slug."""
        for workspace in self._workspaces.values():
            if workspace.slug == slug:
                return workspace
        return None

    async def list_workspaces(
        self,
        user_id: Optional[str] = None,
        status: Optional[WorkspaceStatus] = None,
        plan: Optional[WorkspacePlan] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> WorkspaceListResponse:
        """List workspaces."""
        workspaces = list(self._workspaces.values())

        # Filter by user membership
        if user_id:
            user_ws_ids = self._user_workspaces.get(user_id, [])
            workspaces = [w for w in workspaces if w.id in user_ws_ids]

        # Apply filters
        if status:
            workspaces = [w for w in workspaces if w.status == status]
        if plan:
            workspaces = [w for w in workspaces if w.plan == plan]
        if search:
            search_lower = search.lower()
            workspaces = [
                w for w in workspaces
                if search_lower in w.name.lower() or search_lower in w.slug.lower()
            ]

        workspaces.sort(key=lambda w: w.created_at, reverse=True)

        total = len(workspaces)
        workspaces = workspaces[offset:offset + limit]

        return WorkspaceListResponse(workspaces=workspaces, total=total)

    async def update_workspace(
        self,
        workspace_id: str,
        update: WorkspaceUpdate,
        user_id: str,
        user_name: str,
    ) -> Optional[Workspace]:
        """Update workspace."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return None

        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workspace, field, value)

        workspace.updated_at = datetime.utcnow()

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=user_id,
            user_name=user_name,
            action="workspace.updated",
            details={"fields": list(update_data.keys())},
        )

        return workspace

    async def delete_workspace(
        self,
        workspace_id: str,
        user_id: str,
        user_name: str,
    ) -> bool:
        """Delete workspace (soft delete)."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return False

        workspace.status = WorkspaceStatus.DELETED
        workspace.updated_at = datetime.utcnow()

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=user_id,
            user_name=user_name,
            action="workspace.deleted",
        )

        return True

    async def get_workspace_summary(self, workspace_id: str) -> Optional[WorkspaceSummary]:
        """Get workspace summary."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return None

        limits = get_plan_limits(workspace.plan)
        activities = self._activities.get(workspace_id, [])[-10:]

        return WorkspaceSummary(
            workspace_id=workspace_id,
            name=workspace.name,
            plan=workspace.plan,
            status=workspace.status,
            member_count=workspace.member_count,
            dashboard_count=workspace.dashboard_count,
            connection_count=workspace.connection_count,
            chart_count=0,  # Would be calculated
            storage_used_mb=workspace.storage_used_mb,
            storage_limit_mb=limits.get("max_storage_mb", 100),
            api_calls_today=0,  # Would be tracked
            active_users_today=0,  # Would be tracked
            recent_activities=activities,
        )

    async def get_user_workspaces(self, user_id: str) -> UserWorkspaces:
        """Get all workspaces for a user."""
        workspace_ids = self._user_workspaces.get(user_id, [])

        owned = []
        member_of = []

        for ws_id in workspace_ids:
            workspace = self._workspaces.get(ws_id)
            if not workspace or workspace.status == WorkspaceStatus.DELETED:
                continue

            member = self._members.get(ws_id, {}).get(user_id)
            if member and member.role == MemberRole.OWNER:
                owned.append(workspace)
            else:
                member_of.append(workspace)

        # Get pending invitations
        invitation_ids = self._invitation_by_email.get(user_id, [])
        pending_invitations = [
            self._invitations[inv_id]
            for inv_id in invitation_ids
            if inv_id in self._invitations and self._invitations[inv_id].status == InvitationStatus.PENDING
        ]

        return UserWorkspaces(
            owned=owned,
            member_of=member_of,
            pending_invitations=pending_invitations,
        )

    # Workspace Settings

    async def get_workspace_settings(self, workspace_id: str) -> Optional[WorkspaceSettings]:
        """Get workspace settings."""
        return self._workspace_settings.get(workspace_id)

    async def update_workspace_settings(
        self,
        workspace_id: str,
        update: WorkspaceSettingsUpdate,
        user_id: str,
        user_name: str,
    ) -> Optional[WorkspaceSettings]:
        """Update workspace settings."""
        settings = self._workspace_settings.get(workspace_id)
        if not settings:
            return None

        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=user_id,
            user_name=user_name,
            action="workspace.settings_updated",
            details={"fields": list(update_data.keys())},
        )

        return settings

    # Member Management

    async def add_member(
        self,
        workspace_id: str,
        data: WorkspaceMemberCreate,
        user_email: str,
        user_name: str,
        invited_by: str,
    ) -> WorkspaceMember:
        """Add member to workspace."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Check quota
        quota = await self.get_workspace_quota(workspace_id)
        if not check_quota(quota, "members"):
            raise ValueError("Member limit reached")

        member = WorkspaceMember(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            user_id=data.user_id,
            email=user_email,
            name=user_name,
            role=data.role,
            status=MemberStatus.ACTIVE,
            permissions=data.permissions,
            invited_by=invited_by,
        )

        self._members[workspace_id][data.user_id] = member
        self._user_workspaces[data.user_id].append(workspace_id)

        # Update workspace member count
        workspace.member_count += 1

        return member

    async def get_member(
        self,
        workspace_id: str,
        user_id: str,
    ) -> Optional[WorkspaceMember]:
        """Get workspace member."""
        return self._members.get(workspace_id, {}).get(user_id)

    async def list_members(
        self,
        workspace_id: str,
        role: Optional[MemberRole] = None,
        status: Optional[MemberStatus] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> WorkspaceMemberListResponse:
        """List workspace members."""
        members = list(self._members.get(workspace_id, {}).values())

        if role:
            members = [m for m in members if m.role == role]
        if status:
            members = [m for m in members if m.status == status]
        if search:
            search_lower = search.lower()
            members = [
                m for m in members
                if search_lower in m.name.lower() or search_lower in m.email.lower()
            ]

        members.sort(key=lambda m: m.joined_at)

        total = len(members)
        members = members[offset:offset + limit]

        return WorkspaceMemberListResponse(members=members, total=total)

    async def update_member(
        self,
        workspace_id: str,
        user_id: str,
        update: WorkspaceMemberUpdate,
        updated_by: str,
        updated_by_name: str,
    ) -> Optional[WorkspaceMember]:
        """Update member."""
        member = self._members.get(workspace_id, {}).get(user_id)
        if not member:
            return None

        # Cannot change owner role
        if member.role == MemberRole.OWNER and update.role and update.role != MemberRole.OWNER:
            raise ValueError("Cannot change owner role")

        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=updated_by,
            user_name=updated_by_name,
            action="member.updated",
            details={"member_id": user_id, "fields": list(update_data.keys())},
        )

        return member

    async def remove_member(
        self,
        workspace_id: str,
        user_id: str,
        removed_by: str,
        removed_by_name: str,
    ) -> bool:
        """Remove member from workspace."""
        member = self._members.get(workspace_id, {}).get(user_id)
        if not member:
            return False

        # Cannot remove owner
        if member.role == MemberRole.OWNER:
            raise ValueError("Cannot remove workspace owner")

        del self._members[workspace_id][user_id]
        if workspace_id in self._user_workspaces.get(user_id, []):
            self._user_workspaces[user_id].remove(workspace_id)

        # Update workspace member count
        workspace = self._workspaces.get(workspace_id)
        if workspace:
            workspace.member_count -= 1

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=removed_by,
            user_name=removed_by_name,
            action="member.removed",
            details={"member_id": user_id, "member_name": member.name},
        )

        return True

    # Invitations

    async def create_invitation(
        self,
        workspace_id: str,
        data: InvitationCreate,
        invited_by_id: str,
        invited_by_name: str,
    ) -> Invitation:
        """Create workspace invitation."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Check if already a member
        for member in self._members.get(workspace_id, {}).values():
            if member.email == data.email:
                raise ValueError("User is already a member")

        # Check for existing pending invitation
        for inv in self._invitations.values():
            if inv.workspace_id == workspace_id and inv.email == data.email and inv.status == InvitationStatus.PENDING:
                raise ValueError("Invitation already pending")

        invitation_id = str(uuid.uuid4())
        token = secrets.token_urlsafe(32)

        invitation = Invitation(
            id=invitation_id,
            workspace_id=workspace_id,
            workspace_name=workspace.name,
            email=data.email,
            role=data.role,
            status=InvitationStatus.PENDING,
            message=data.message,
            token=token,
            invited_by_id=invited_by_id,
            invited_by_name=invited_by_name,
            expires_at=datetime.utcnow() + timedelta(days=data.expires_in_days),
        )

        self._invitations[invitation_id] = invitation
        self._invitation_by_token[token] = invitation_id
        self._invitation_by_email[data.email].append(invitation_id)

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=invited_by_id,
            user_name=invited_by_name,
            action="invitation.created",
            details={"email": data.email, "role": data.role.value},
        )

        return invitation

    async def create_bulk_invitations(
        self,
        workspace_id: str,
        data: BulkInvitationCreate,
        invited_by_id: str,
        invited_by_name: str,
    ) -> list[Invitation]:
        """Create multiple invitations."""
        invitations = []

        for email in data.emails:
            try:
                invitation = await self.create_invitation(
                    workspace_id=workspace_id,
                    data=InvitationCreate(
                        email=email,
                        role=data.role,
                        message=data.message,
                        expires_in_days=data.expires_in_days,
                    ),
                    invited_by_id=invited_by_id,
                    invited_by_name=invited_by_name,
                )
                invitations.append(invitation)
            except ValueError:
                # Skip already invited/member emails
                pass

        return invitations

    async def get_invitation(self, invitation_id: str) -> Optional[Invitation]:
        """Get invitation by ID."""
        return self._invitations.get(invitation_id)

    async def get_invitation_by_token(self, token: str) -> Optional[Invitation]:
        """Get invitation by token."""
        invitation_id = self._invitation_by_token.get(token)
        if invitation_id:
            return self._invitations.get(invitation_id)
        return None

    async def list_invitations(
        self,
        workspace_id: str,
        status: Optional[InvitationStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> InvitationListResponse:
        """List workspace invitations."""
        invitations = [
            inv for inv in self._invitations.values()
            if inv.workspace_id == workspace_id
        ]

        if status:
            invitations = [inv for inv in invitations if inv.status == status]

        invitations.sort(key=lambda inv: inv.created_at, reverse=True)

        total = len(invitations)
        invitations = invitations[offset:offset + limit]

        return InvitationListResponse(invitations=invitations, total=total)

    async def respond_to_invitation(
        self,
        token: str,
        response: InvitationResponse,
        user_email: str,
        user_name: str,
    ) -> Optional[WorkspaceMember]:
        """Accept or decline invitation."""
        invitation = await self.get_invitation_by_token(token)
        if not invitation:
            raise ValueError("Invalid invitation token")

        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Invitation is no longer pending")

        if invitation.expires_at < datetime.utcnow():
            invitation.status = InvitationStatus.EXPIRED
            raise ValueError("Invitation has expired")

        if not response.accept:
            invitation.status = InvitationStatus.DECLINED
            invitation.declined_at = datetime.utcnow()
            return None

        # Accept invitation
        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = datetime.utcnow()

        # Add as member
        user_id = response.user_id or str(uuid.uuid4())
        member = await self.add_member(
            workspace_id=invitation.workspace_id,
            data=WorkspaceMemberCreate(
                user_id=user_id,
                role=invitation.role,
            ),
            user_email=user_email,
            user_name=user_name,
            invited_by=invitation.invited_by_id,
        )

        return member

    async def cancel_invitation(
        self,
        invitation_id: str,
        cancelled_by: str,
        cancelled_by_name: str,
    ) -> bool:
        """Cancel an invitation."""
        invitation = self._invitations.get(invitation_id)
        if not invitation or invitation.status != InvitationStatus.PENDING:
            return False

        invitation.status = InvitationStatus.CANCELLED

        # Log activity
        await self._log_activity(
            workspace_id=invitation.workspace_id,
            user_id=cancelled_by,
            user_name=cancelled_by_name,
            action="invitation.cancelled",
            details={"email": invitation.email},
        )

        return True

    async def resend_invitation(
        self,
        invitation_id: str,
        resent_by: str,
        resent_by_name: str,
    ) -> Optional[Invitation]:
        """Resend an invitation."""
        invitation = self._invitations.get(invitation_id)
        if not invitation or invitation.status != InvitationStatus.PENDING:
            return None

        # Update expiration
        invitation.expires_at = datetime.utcnow() + timedelta(days=7)

        # Log activity
        await self._log_activity(
            workspace_id=invitation.workspace_id,
            user_id=resent_by,
            user_name=resent_by_name,
            action="invitation.resent",
            details={"email": invitation.email},
        )

        return invitation

    # Quota Management

    async def get_workspace_quota(self, workspace_id: str) -> WorkspaceQuota:
        """Get workspace quota."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        limits = get_plan_limits(workspace.plan)
        members = self._members.get(workspace_id, {})

        member_count = len([m for m in members.values() if m.role != MemberRole.GUEST])
        guest_count = len([m for m in members.values() if m.role == MemberRole.GUEST])

        return WorkspaceQuota(
            workspace_id=workspace_id,
            plan=workspace.plan,
            max_members=limits.get("max_members", 10),
            current_members=member_count,
            max_guests=limits.get("max_guests", 5),
            current_guests=guest_count,
            max_connections=limits.get("max_connections", 10),
            current_connections=workspace.connection_count,
            max_dashboards=limits.get("max_dashboards", 50),
            current_dashboards=workspace.dashboard_count,
            max_charts=limits.get("max_charts", 100),
            current_charts=0,  # Would be calculated
            max_datasets=limits.get("max_datasets", 20),
            current_datasets=0,  # Would be calculated
            max_storage_mb=limits.get("max_storage_mb", 100),
            current_storage_mb=workspace.storage_used_mb,
            max_api_calls_per_day=limits.get("max_api_calls_per_day", 1000),
            current_api_calls_today=0,  # Would be tracked
            max_query_execution_minutes=limits.get("max_query_execution_minutes", 60),
            current_query_minutes_today=0,  # Would be tracked
            max_scheduled_reports=limits.get("max_scheduled_reports", 10),
            current_scheduled_reports=0,  # Would be calculated
            max_alerts=limits.get("max_alerts", 20),
            current_alerts=0,  # Would be calculated
        )

    async def get_quota_usage(self, workspace_id: str) -> QuotaUsageListResponse:
        """Get detailed quota usage."""
        quota = await self.get_workspace_quota(workspace_id)

        usages = [
            QuotaUsage(
                workspace_id=workspace_id,
                resource_type="members",
                limit=quota.max_members,
                used=quota.current_members,
                remaining=quota.max_members - quota.current_members if quota.max_members >= 0 else -1,
                percent_used=round(quota.current_members / quota.max_members * 100, 2) if quota.max_members > 0 else 0,
            ),
            QuotaUsage(
                workspace_id=workspace_id,
                resource_type="connections",
                limit=quota.max_connections,
                used=quota.current_connections,
                remaining=quota.max_connections - quota.current_connections if quota.max_connections >= 0 else -1,
                percent_used=round(quota.current_connections / quota.max_connections * 100, 2) if quota.max_connections > 0 else 0,
            ),
            QuotaUsage(
                workspace_id=workspace_id,
                resource_type="dashboards",
                limit=quota.max_dashboards,
                used=quota.current_dashboards,
                remaining=quota.max_dashboards - quota.current_dashboards if quota.max_dashboards >= 0 else -1,
                percent_used=round(quota.current_dashboards / quota.max_dashboards * 100, 2) if quota.max_dashboards > 0 else 0,
            ),
            QuotaUsage(
                workspace_id=workspace_id,
                resource_type="storage_mb",
                limit=quota.max_storage_mb,
                used=int(quota.current_storage_mb),
                remaining=quota.max_storage_mb - int(quota.current_storage_mb) if quota.max_storage_mb >= 0 else -1,
                percent_used=round(quota.current_storage_mb / quota.max_storage_mb * 100, 2) if quota.max_storage_mb > 0 else 0,
            ),
        ]

        return QuotaUsageListResponse(quotas=usages)

    # Team Management

    async def create_team(
        self,
        workspace_id: str,
        data: TeamCreate,
        created_by: str,
        created_by_name: str,
    ) -> Team:
        """Create a team."""
        team_id = str(uuid.uuid4())

        team = Team(
            id=team_id,
            workspace_id=workspace_id,
            name=data.name,
            description=data.description,
            color=data.color,
            member_ids=data.member_ids,
        )

        self._teams[workspace_id][team_id] = team

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=created_by,
            user_name=created_by_name,
            action="team.created",
            details={"team_name": data.name},
        )

        return team

    async def get_team(self, workspace_id: str, team_id: str) -> Optional[Team]:
        """Get team by ID."""
        return self._teams.get(workspace_id, {}).get(team_id)

    async def list_teams(
        self,
        workspace_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> TeamListResponse:
        """List workspace teams."""
        teams = list(self._teams.get(workspace_id, {}).values())
        teams.sort(key=lambda t: t.name)

        total = len(teams)
        teams = teams[offset:offset + limit]

        return TeamListResponse(teams=teams, total=total)

    async def update_team(
        self,
        workspace_id: str,
        team_id: str,
        update: TeamUpdate,
        updated_by: str,
        updated_by_name: str,
    ) -> Optional[Team]:
        """Update team."""
        team = self._teams.get(workspace_id, {}).get(team_id)
        if not team:
            return None

        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(team, field, value)

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=updated_by,
            user_name=updated_by_name,
            action="team.updated",
            details={"team_id": team_id, "team_name": team.name},
        )

        return team

    async def delete_team(
        self,
        workspace_id: str,
        team_id: str,
        deleted_by: str,
        deleted_by_name: str,
    ) -> bool:
        """Delete team."""
        if team_id not in self._teams.get(workspace_id, {}):
            return False

        team = self._teams[workspace_id][team_id]
        del self._teams[workspace_id][team_id]

        # Log activity
        await self._log_activity(
            workspace_id=workspace_id,
            user_id=deleted_by,
            user_name=deleted_by_name,
            action="team.deleted",
            details={"team_name": team.name},
        )

        return True

    # Activity Logging

    async def _log_activity(
        self,
        workspace_id: str,
        user_id: str,
        user_name: str,
        action: str,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log workspace activity."""
        activity = WorkspaceActivity(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            user_id=user_id,
            user_name=user_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self._activities[workspace_id].append(activity)

        # Keep only last 1000 activities per workspace
        if len(self._activities[workspace_id]) > 1000:
            self._activities[workspace_id] = self._activities[workspace_id][-1000:]

    async def get_workspace_activity(
        self,
        workspace_id: str,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> WorkspaceActivityListResponse:
        """Get workspace activity log."""
        activities = self._activities.get(workspace_id, [])

        if user_id:
            activities = [a for a in activities if a.user_id == user_id]
        if action:
            activities = [a for a in activities if action in a.action]
        if resource_type:
            activities = [a for a in activities if a.resource_type == resource_type]

        activities = sorted(activities, key=lambda a: a.created_at, reverse=True)

        total = len(activities)
        activities = activities[offset:offset + limit]

        return WorkspaceActivityListResponse(activities=activities, total=total)

    # Permission Checks

    async def check_permission(
        self,
        workspace_id: str,
        user_id: str,
        permission: str,
    ) -> bool:
        """Check if user has permission."""
        member = await self.get_member(workspace_id, user_id)
        if not member:
            return False

        role_perms = get_role_permissions(member.role)

        # Check role permission
        if hasattr(role_perms, permission):
            return getattr(role_perms, permission)

        # Check custom permissions
        return member.permissions.get(permission, False)


# Global service instance
workspace_management_service = WorkspaceManagementService()
