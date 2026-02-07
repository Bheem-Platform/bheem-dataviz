"""
Workspace Service

Handles workspace management, membership, and permissions.
"""

import logging
import secrets
import re
from typing import Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.workspace import (
    Workspace,
    WorkspaceMember,
    WorkspaceInvitation,
    ObjectPermission,
)
from app.models.user import User
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
    ObjectPermissionCreate,
    ObjectPermissionResponse,
    WorkspaceRole,
    InviteStatus,
    ROLE_PERMISSIONS,
)

logger = logging.getLogger(__name__)


class WorkspaceService:
    """Service for workspace operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # USER MANAGEMENT (for foreign key compliance)
    # ========================================================================

    async def get_or_create_local_user(
        self,
        passport_user_id: str,
        email: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        company_code: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> User:
        """
        Find or create a local user record based on BheemPassport user data.
        This is needed because workspace tables have foreign key constraints to users.id.
        """
        # Check if user exists by passport_user_id
        result = await self.db.execute(
            select(User).where(User.passport_user_id == passport_user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            return user

        # Map role to simple string
        user_role = "user"
        if role:
            role_lower = role.lower()
            if role_lower in ["admin", "superadmin"]:
                user_role = "admin"
            elif role_lower == "viewer":
                user_role = "viewer"

        user = User(
            passport_user_id=passport_user_id,
            email=email,
            full_name=name or email.split("@")[0],
            role=user_role,
            status="active",
            company_code=company_code or "DEFAULT",
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Created local user record for passport user {passport_user_id}")
        return user

    async def get_local_user_id(self, passport_user_id: str) -> Optional[str]:
        """Get the local user ID from passport user ID"""
        result = await self.db.execute(
            select(User.id).where(User.passport_user_id == passport_user_id)
        )
        user_id = result.scalar_one_or_none()
        return str(user_id) if user_id else None

    # ========================================================================
    # WORKSPACE CRUD
    # ========================================================================

    async def create_workspace(
        self,
        data: WorkspaceCreate,
        owner_id: str,
        is_personal: bool = False,
    ) -> Workspace:
        """Create a new workspace"""
        # Generate slug if not provided
        slug = data.slug or self._generate_slug(data.name)

        # Ensure unique slug
        slug = await self._ensure_unique_slug(slug)

        workspace = Workspace(
            name=data.name,
            slug=slug,
            description=data.description,
            owner_id=owner_id,
            is_personal=is_personal,
            logo_url=data.logo_url,
            primary_color=data.primary_color,
            settings=data.settings or {},
        )

        self.db.add(workspace)
        await self.db.commit()
        await self.db.refresh(workspace)

        # Add owner as a member with owner role
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role='owner',
            joined_at=datetime.utcnow(),
        )
        self.db.add(member)
        await self.db.commit()

        return workspace

    async def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get a workspace by ID"""
        result = await self.db.execute(
            select(Workspace)
            .where(Workspace.id == workspace_id)
            .options(selectinload(Workspace.members))
        )
        return result.scalar_one_or_none()

    async def get_workspace_by_slug(self, slug: str) -> Optional[Workspace]:
        """Get a workspace by slug"""
        result = await self.db.execute(
            select(Workspace)
            .where(Workspace.slug == slug)
            .options(selectinload(Workspace.members))
        )
        return result.scalar_one_or_none()

    async def update_workspace(
        self,
        workspace_id: str,
        data: WorkspaceUpdate,
    ) -> Optional[Workspace]:
        """Update a workspace"""
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workspace, field, value)

        workspace.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(workspace)

        return workspace

    async def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace"""
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            return False

        # Prevent deleting personal workspaces
        if workspace.is_personal:
            raise ValueError("Cannot delete personal workspace")

        await self.db.delete(workspace)
        await self.db.commit()
        return True

    async def list_user_workspaces(self, user_id: str) -> list[WorkspaceSummary]:
        """List all workspaces a user is a member of"""
        result = await self.db.execute(
            select(Workspace, WorkspaceMember.role)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(
                and_(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.is_active == True,
                    Workspace.is_active == True,
                )
            )
            .order_by(Workspace.is_default.desc(), Workspace.name)
        )

        workspaces = []
        for workspace, role in result.all():
            # role is now a string from database, not an enum
            role_str = role.value if hasattr(role, 'value') else role
            workspaces.append(WorkspaceSummary(
                id=str(workspace.id),
                name=workspace.name,
                slug=workspace.slug,
                is_personal=workspace.is_personal,
                is_default=workspace.is_default,
                role=WorkspaceRole(role_str),
                logo_url=workspace.logo_url,
                primary_color=workspace.primary_color,
            ))

        return workspaces

    async def get_or_create_personal_workspace(self, user_id: str, user_email: str) -> Workspace:
        """Get or create a personal workspace for a user"""
        # Check if personal workspace exists
        result = await self.db.execute(
            select(Workspace)
            .where(
                and_(
                    Workspace.owner_id == user_id,
                    Workspace.is_personal == True,
                )
            )
        )
        workspace = result.scalar_one_or_none()

        if workspace:
            return workspace

        # Create personal workspace
        name = f"{user_email.split('@')[0]}'s Workspace"
        return await self.create_workspace(
            data=WorkspaceCreate(name=name),
            owner_id=user_id,
            is_personal=True,
        )

    # ========================================================================
    # MEMBERSHIP MANAGEMENT
    # ========================================================================

    async def add_member(
        self,
        workspace_id: str,
        user_id: str,
        role: WorkspaceRole = WorkspaceRole.MEMBER,
        invited_by: Optional[str] = None,
    ) -> WorkspaceMember:
        """Add a member to a workspace"""
        # Check if already a member
        existing = await self.get_member(workspace_id, user_id)
        if existing:
            raise ValueError("User is already a member of this workspace")

        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role.value if hasattr(role, 'value') else role,
            invited_by=invited_by,
            invited_at=datetime.utcnow() if invited_by else None,
            joined_at=datetime.utcnow(),
        )

        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)

        return member

    async def get_member(
        self,
        workspace_id: str,
        user_id: str,
    ) -> Optional[WorkspaceMember]:
        """Get a workspace member"""
        result = await self.db.execute(
            select(WorkspaceMember)
            .where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_member(
        self,
        workspace_id: str,
        user_id: str,
        data: MemberUpdate,
    ) -> Optional[WorkspaceMember]:
        """Update a workspace member"""
        member = await self.get_member(workspace_id, user_id)
        if not member:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Handle role update
        if "role" in update_data:
            role_value = update_data.pop("role")
            if role_value:
                member.role = role_value.value if hasattr(role_value, 'value') else role_value

        for field, value in update_data.items():
            setattr(member, field, value)

        member.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(member)

        return member

    async def remove_member(
        self,
        workspace_id: str,
        user_id: str,
    ) -> bool:
        """Remove a member from a workspace"""
        member = await self.get_member(workspace_id, user_id)
        if not member:
            return False

        # Prevent removing the owner
        if member.role == 'owner':
            raise ValueError("Cannot remove workspace owner. Transfer ownership first.")

        await self.db.delete(member)
        await self.db.commit()
        return True

    async def list_members(
        self,
        workspace_id: str,
        include_inactive: bool = False,
    ) -> list[tuple]:
        """List all members of a workspace with user details"""
        query = (
            select(WorkspaceMember, User)
            .join(User, WorkspaceMember.user_id == User.id)
            .where(WorkspaceMember.workspace_id == workspace_id)
        )

        if not include_inactive:
            query = query.where(WorkspaceMember.is_active == True)

        result = await self.db.execute(query.order_by(WorkspaceMember.joined_at))
        return list(result.all())

    async def get_member_count(self, workspace_id: str) -> int:
        """Get count of active members"""
        result = await self.db.execute(
            select(func.count(WorkspaceMember.id))
            .where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.is_active == True,
                )
            )
        )
        return result.scalar() or 0

    async def transfer_ownership(
        self,
        workspace_id: str,
        current_owner_id: str,
        new_owner_id: str,
    ) -> bool:
        """Transfer workspace ownership to another member"""
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            return False

        if str(workspace.owner_id) != current_owner_id:
            raise ValueError("Only the current owner can transfer ownership")

        # Verify new owner is a member
        new_owner_member = await self.get_member(workspace_id, new_owner_id)
        if not new_owner_member:
            raise ValueError("New owner must be a member of the workspace")

        # Update workspace owner
        workspace.owner_id = new_owner_id

        # Update roles
        current_owner_member = await self.get_member(workspace_id, current_owner_id)
        if current_owner_member:
            current_owner_member.role = 'admin'

        new_owner_member.role = 'owner'

        await self.db.commit()
        return True

    # ========================================================================
    # INVITATIONS
    # ========================================================================

    async def create_invitation(
        self,
        workspace_id: str,
        data: InvitationCreate,
        invited_by: str,
    ) -> WorkspaceInvitation:
        """Create a workspace invitation"""
        # Check if invitation already exists
        existing = await self.db.execute(
            select(WorkspaceInvitation)
            .where(
                and_(
                    WorkspaceInvitation.workspace_id == workspace_id,
                    WorkspaceInvitation.email == data.email,
                    WorkspaceInvitation.status == 'pending',
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Invitation already pending for this email")

        # Generate secure token
        token = secrets.token_urlsafe(32)

        invitation = WorkspaceInvitation(
            workspace_id=workspace_id,
            email=data.email,
            role=data.role.value if hasattr(data.role, 'value') else data.role,
            token=token,
            invited_by=invited_by,
            message=data.message,
            expires_at=datetime.utcnow() + timedelta(days=data.expires_in_days),
        )

        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)

        return invitation

    async def get_invitation_by_token(self, token: str) -> Optional[WorkspaceInvitation]:
        """Get an invitation by token"""
        result = await self.db.execute(
            select(WorkspaceInvitation)
            .where(WorkspaceInvitation.token == token)
            .options(selectinload(WorkspaceInvitation.workspace))
        )
        return result.scalar_one_or_none()

    async def accept_invitation(
        self,
        token: str,
        user_id: str,
    ) -> WorkspaceMember:
        """Accept a workspace invitation"""
        invitation = await self.get_invitation_by_token(token)
        if not invitation:
            raise ValueError("Invalid invitation token")

        if invitation.status != 'pending':
            raise ValueError(f"Invitation is {invitation.status}")

        if invitation.expires_at < datetime.utcnow():
            invitation.status = 'expired'
            await self.db.commit()
            raise ValueError("Invitation has expired")

        # Add member
        member = await self.add_member(
            workspace_id=str(invitation.workspace_id),
            user_id=user_id,
            role=WorkspaceRole(invitation.role if isinstance(invitation.role, str) else invitation.role.value),
            invited_by=str(invitation.invited_by),
        )

        # Update invitation status
        invitation.status = 'accepted'
        invitation.accepted_at = datetime.utcnow()
        await self.db.commit()

        return member

    async def decline_invitation(self, token: str) -> bool:
        """Decline a workspace invitation"""
        invitation = await self.get_invitation_by_token(token)
        if not invitation:
            return False

        if invitation.status != 'pending':
            return False

        invitation.status = 'declined'
        await self.db.commit()
        return True

    async def list_invitations(
        self,
        workspace_id: str,
        status: Optional[InviteStatus] = None,
    ) -> list[WorkspaceInvitation]:
        """List workspace invitations"""
        query = select(WorkspaceInvitation).where(
            WorkspaceInvitation.workspace_id == workspace_id
        )

        if status:
            query = query.where(
                WorkspaceInvitation.status == (status.value if hasattr(status, 'value') else status)
            )

        result = await self.db.execute(query.order_by(WorkspaceInvitation.created_at.desc()))
        return list(result.scalars().all())

    async def cancel_invitation(self, invitation_id: str) -> bool:
        """Cancel a pending invitation"""
        result = await self.db.execute(
            select(WorkspaceInvitation).where(WorkspaceInvitation.id == invitation_id)
        )
        invitation = result.scalar_one_or_none()

        if not invitation or invitation.status != 'pending':
            return False

        await self.db.delete(invitation)
        await self.db.commit()
        return True

    # ========================================================================
    # PERMISSIONS
    # ========================================================================

    async def check_permission(
        self,
        workspace_id: str,
        user_id: str,
        action: str,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
    ) -> bool:
        """Check if a user has permission to perform an action"""
        member = await self.get_member(workspace_id, user_id)
        if not member or not member.is_active:
            return False

        role = WorkspaceRole(member.role if isinstance(member.role, str) else member.role.value)

        # Check custom permissions first
        if member.custom_permissions and action in member.custom_permissions:
            return member.custom_permissions[action]

        # Check object-level permissions if applicable
        if object_type and object_id:
            obj_perm = await self._get_object_permission(
                workspace_id, user_id, role, object_type, object_id
            )
            if obj_perm:
                action_map = {
                    "view": obj_perm.can_view,
                    "edit": obj_perm.can_edit,
                    "delete": obj_perm.can_delete,
                    "share": obj_perm.can_share,
                    "export": obj_perm.can_export,
                }
                if action in action_map:
                    return action_map[action]

        # Fall back to role defaults
        role_permissions = ROLE_PERMISSIONS.get(role, {})
        return role_permissions.get(action, False)

    async def _get_object_permission(
        self,
        workspace_id: str,
        user_id: str,
        role: WorkspaceRole,
        object_type: str,
        object_id: str,
    ) -> Optional[ObjectPermission]:
        """Get object-level permission"""
        result = await self.db.execute(
            select(ObjectPermission)
            .where(
                and_(
                    ObjectPermission.workspace_id == workspace_id,
                    ObjectPermission.object_type == object_type,
                    ObjectPermission.object_id == object_id,
                    or_(
                        ObjectPermission.user_id == user_id,
                        ObjectPermission.role == (role.value if hasattr(role, 'value') else role),
                    )
                )
            )
            .order_by(ObjectPermission.user_id.desc())  # User-specific takes priority
        )
        return result.scalars().first()

    async def set_object_permission(
        self,
        workspace_id: str,
        data: ObjectPermissionCreate,
        created_by: str,
    ) -> ObjectPermission:
        """Set object-level permission"""
        if not data.user_id and not data.role:
            raise ValueError("Either user_id or role must be specified")

        # Check if permission already exists
        query = select(ObjectPermission).where(
            and_(
                ObjectPermission.workspace_id == workspace_id,
                ObjectPermission.object_type == data.object_type,
                ObjectPermission.object_id == data.object_id,
            )
        )

        if data.user_id:
            query = query.where(ObjectPermission.user_id == data.user_id)
        else:
            query = query.where(ObjectPermission.role == (data.role.value if hasattr(data.role, 'value') else data.role))

        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing permission
            existing.can_view = data.can_view
            existing.can_edit = data.can_edit
            existing.can_delete = data.can_delete
            existing.can_share = data.can_share
            existing.can_export = data.can_export
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        # Create new permission
        permission = ObjectPermission(
            workspace_id=workspace_id,
            object_type=data.object_type,
            object_id=data.object_id,
            user_id=data.user_id,
            role=(data.role.value if hasattr(data.role, 'value') else data.role) if data.role else None,
            can_view=data.can_view,
            can_edit=data.can_edit,
            can_delete=data.can_delete,
            can_share=data.can_share,
            can_export=data.can_export,
            created_by=created_by,
        )

        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)

        return permission

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _generate_slug(self, name: str) -> str:
        """Generate a URL-friendly slug from a name"""
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')[:50]

    async def _ensure_unique_slug(self, slug: str) -> str:
        """Ensure slug is unique, appending number if needed"""
        original_slug = slug
        counter = 1

        while True:
            result = await self.db.execute(
                select(func.count(Workspace.id))
                .where(Workspace.slug == slug)
            )
            if result.scalar() == 0:
                return slug

            slug = f"{original_slug}-{counter}"
            counter += 1

            if counter > 100:
                # Fallback to random suffix
                slug = f"{original_slug}-{secrets.token_hex(4)}"
                break

        return slug


def get_workspace_service(db: AsyncSession) -> WorkspaceService:
    """Factory function to get workspace service instance"""
    return WorkspaceService(db)
