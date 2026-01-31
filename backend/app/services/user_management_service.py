"""
User & Role Management Service

Provides user profile management, role/permission management,
session management, and audit logging.
"""

import hashlib
import secrets
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional
from user_agents import parse as parse_user_agent

from app.schemas.user_management import (
    User, UserCreate, UserUpdate, UserAdminUpdate, UserProfile, UserStatus, UserType,
    UserPreferences, UserPreferencesUpdate,
    Role, RoleCreate, RoleUpdate, RoleAssignment, RoleAssignmentCreate,
    Permission, PermissionGroup, PermissionScope, UserPermissions,
    Session, SessionCreate, SessionStatus, SessionInfo,
    MFASetup, MFABackupCodes,
    PasswordPolicy, PasswordChange,
    AuditLogEntry, AuditAction, AuditLogQuery,
    UserListResponse, RoleListResponse, SessionListResponse, AuditLogResponse,
    PermissionListResponse, UserStatistics, AuthProvider,
    SYSTEM_ROLES, PERMISSION_CATEGORIES, ALL_PERMISSIONS,
    has_permission, validate_password, get_role_permissions, merge_permissions
)


class UserManagementService:
    """Service for user and role management."""

    def __init__(self):
        # In-memory stores (production would use database)
        self.users: dict[str, User] = {}
        self.user_passwords: dict[str, str] = {}  # user_id -> hashed password
        self.user_preferences: dict[str, UserPreferences] = {}
        self.roles: dict[str, Role] = {}
        self.role_assignments: dict[str, RoleAssignment] = {}
        self.sessions: dict[str, Session] = {}
        self.audit_logs: list[AuditLogEntry] = []
        self.mfa_secrets: dict[str, str] = {}  # user_id -> secret
        self.backup_codes: dict[str, list[str]] = {}  # user_id -> codes
        self.password_history: dict[str, list[str]] = {}  # user_id -> old hashes

        self.password_policy = PasswordPolicy()
        self._initialize_system_roles()

    def _initialize_system_roles(self):
        """Initialize system roles."""
        for role_key, role_data in SYSTEM_ROLES.items():
            role_id = f"role_{role_key}"
            self.roles[role_id] = Role(
                id=role_id,
                name=role_data["name"],
                description=role_data["description"],
                scope=PermissionScope.GLOBAL,
                permissions=role_data["permissions"],
                is_system=True,
                is_default=(role_key == "user"),
            )

    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000
        )
        return f"{salt}:{pwd_hash.hex()}"

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against hash."""
        try:
            salt, pwd_hash = hashed.split(":")
            new_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode(),
                salt.encode(),
                100000
            )
            return new_hash.hex() == pwd_hash
        except Exception:
            return False

    def _generate_id(self, prefix: str = "usr") -> str:
        """Generate a unique ID."""
        return f"{prefix}_{secrets.token_hex(12)}"

    # User Management

    def create_user(self, data: UserCreate, created_by: Optional[str] = None) -> User:
        """Create a new user."""
        # Check email uniqueness
        for user in self.users.values():
            if user.email.lower() == data.email.lower():
                raise ValueError("Email already registered")

        user_id = self._generate_id("usr")
        now = datetime.utcnow()

        user = User(
            id=user_id,
            email=data.email.lower(),
            name=data.name,
            display_name=data.display_name or data.name,
            avatar_url=data.avatar_url,
            user_type=data.user_type,
            status=UserStatus.PENDING_VERIFICATION if data.auth_provider == AuthProvider.LOCAL else UserStatus.ACTIVE,
            auth_provider=data.auth_provider,
            auth_provider_id=data.auth_provider_id,
            phone=data.phone,
            timezone=data.timezone,
            locale=data.locale,
            email_verified=data.auth_provider != AuthProvider.LOCAL,
            metadata=data.metadata,
            created_at=now,
            updated_at=now,
        )

        # Store password if local auth
        if data.password and data.auth_provider == AuthProvider.LOCAL:
            valid, errors = validate_password(data.password, self.password_policy)
            if not valid:
                raise ValueError(f"Password validation failed: {', '.join(errors)}")
            self.user_passwords[user_id] = self._hash_password(data.password)

        self.users[user_id] = user

        # Initialize preferences
        self.user_preferences[user_id] = UserPreferences(user_id=user_id)

        # Assign default role
        default_role = next((r for r in self.roles.values() if r.is_default), None)
        if default_role:
            self._assign_role(user_id, default_role.id, created_by or "system")

        # Log audit
        self._log_audit(
            user_id=user_id,
            user_email=user.email,
            action=AuditAction.LOGIN,  # Use LOGIN as placeholder for creation
            details={"action": "user_created", "created_by": created_by},
        )

        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        email_lower = email.lower()
        for user in self.users.values():
            if user.email.lower() == email_lower:
                return user
        return None

    def update_user(self, user_id: str, data: UserUpdate) -> Optional[User]:
        """Update user profile."""
        user = self.users.get(user_id)
        if not user:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        user.updated_at = datetime.utcnow()

        self._log_audit(
            user_id=user_id,
            user_email=user.email,
            action=AuditAction.PROFILE_UPDATE,
            details={"updated_fields": list(update_data.keys())},
        )

        return user

    def admin_update_user(self, user_id: str, data: UserAdminUpdate, admin_id: str) -> Optional[User]:
        """Admin user update."""
        user = self.users.get(user_id)
        if not user:
            return None

        update_data = data.model_dump(exclude_unset=True)
        old_status = user.status

        for field, value in update_data.items():
            setattr(user, field, value)
        user.updated_at = datetime.utcnow()

        # Log status changes
        if "status" in update_data and update_data["status"] != old_status:
            if update_data["status"] == UserStatus.LOCKED:
                self._log_audit(user_id, user.email, AuditAction.ACCOUNT_LOCKED, {"by": admin_id})
            elif old_status == UserStatus.LOCKED:
                self._log_audit(user_id, user.email, AuditAction.ACCOUNT_UNLOCKED, {"by": admin_id})

        return user

    def delete_user(self, user_id: str, deleted_by: str) -> bool:
        """Soft delete user."""
        user = self.users.get(user_id)
        if not user:
            return False

        user.status = UserStatus.DELETED
        user.updated_at = datetime.utcnow()

        # Revoke all sessions
        for session in self.sessions.values():
            if session.user_id == user_id and session.status == SessionStatus.ACTIVE:
                session.status = SessionStatus.REVOKED
                session.revoked_at = datetime.utcnow()
                session.revoked_reason = "User deleted"

        return True

    def list_users(
        self,
        status: Optional[UserStatus] = None,
        user_type: Optional[UserType] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> UserListResponse:
        """List users with filters."""
        users = list(self.users.values())

        # Filter out deleted
        users = [u for u in users if u.status != UserStatus.DELETED]

        if status:
            users = [u for u in users if u.status == status]
        if user_type:
            users = [u for u in users if u.user_type == user_type]
        if search:
            search_lower = search.lower()
            users = [u for u in users if search_lower in u.email.lower() or search_lower in u.name.lower()]

        total = len(users)
        users = users[skip:skip + limit]

        return UserListResponse(users=users, total=total)

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get public user profile."""
        user = self.users.get(user_id)
        if not user:
            return None

        return UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            timezone=user.timezone,
            locale=user.locale,
            created_at=user.created_at,
        )

    # User Preferences

    def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences."""
        return self.user_preferences.get(user_id)

    def update_preferences(self, user_id: str, data: UserPreferencesUpdate) -> Optional[UserPreferences]:
        """Update user preferences."""
        prefs = self.user_preferences.get(user_id)
        if not prefs:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prefs, field, value)

        return prefs

    # Password Management

    def change_password(self, user_id: str, data: PasswordChange, ip_address: Optional[str] = None) -> bool:
        """Change user password."""
        user = self.users.get(user_id)
        if not user:
            return False

        current_hash = self.user_passwords.get(user_id)
        if not current_hash or not self._verify_password(data.current_password, current_hash):
            self._log_audit(
                user_id, user.email, AuditAction.PASSWORD_CHANGE,
                {"success": False, "reason": "Invalid current password"},
                ip_address=ip_address, success=False
            )
            raise ValueError("Invalid current password")

        # Validate new password
        valid, errors = validate_password(data.new_password, self.password_policy)
        if not valid:
            raise ValueError(f"Password validation failed: {', '.join(errors)}")

        # Check password history
        history = self.password_history.get(user_id, [])
        for old_hash in history[-self.password_policy.history_count:]:
            if self._verify_password(data.new_password, old_hash):
                raise ValueError("Cannot reuse recent passwords")

        # Update password
        new_hash = self._hash_password(data.new_password)
        history.append(current_hash)
        self.password_history[user_id] = history[-self.password_policy.history_count:]
        self.user_passwords[user_id] = new_hash
        user.password_changed_at = datetime.utcnow()

        self._log_audit(user_id, user.email, AuditAction.PASSWORD_CHANGE, {"success": True}, ip_address=ip_address)

        return True

    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password."""
        hashed = self.user_passwords.get(user_id)
        if not hashed:
            return False
        return self._verify_password(password, hashed)

    # MFA Management

    def setup_mfa(self, user_id: str) -> Optional[MFASetup]:
        """Setup MFA for user."""
        user = self.users.get(user_id)
        if not user:
            return None

        # Generate secret
        secret = pyotp.random_base32()
        self.mfa_secrets[user_id] = secret

        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(user.email, issuer_name="Bheem DataViz")

        qr = qrcode.make(provisioning_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.backup_codes[user_id] = backup_codes

        return MFASetup(
            secret=secret,
            qr_code_url=f"data:image/png;base64,{qr_base64}",
            backup_codes=backup_codes,
        )

    def verify_mfa(self, user_id: str, code: str) -> bool:
        """Verify MFA code."""
        secret = self.mfa_secrets.get(user_id)
        if not secret:
            return False

        totp = pyotp.TOTP(secret)
        if totp.verify(code, valid_window=1):
            return True

        # Check backup codes
        codes = self.backup_codes.get(user_id, [])
        if code.upper() in codes:
            codes.remove(code.upper())
            return True

        return False

    def enable_mfa(self, user_id: str, code: str) -> bool:
        """Enable MFA after verification."""
        if not self.verify_mfa(user_id, code):
            return False

        user = self.users.get(user_id)
        if user:
            user.mfa_enabled = True
            user.mfa_method = "totp"
            self._log_audit(user_id, user.email, AuditAction.MFA_ENABLED, {})
            return True
        return False

    def disable_mfa(self, user_id: str, code: str) -> bool:
        """Disable MFA."""
        if not self.verify_mfa(user_id, code):
            return False

        user = self.users.get(user_id)
        if user:
            user.mfa_enabled = False
            user.mfa_method = None
            del self.mfa_secrets[user_id]
            del self.backup_codes[user_id]
            self._log_audit(user_id, user.email, AuditAction.MFA_DISABLED, {})
            return True
        return False

    def regenerate_backup_codes(self, user_id: str) -> Optional[MFABackupCodes]:
        """Regenerate backup codes."""
        if user_id not in self.mfa_secrets:
            return None

        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.backup_codes[user_id] = codes

        return MFABackupCodes(codes=codes, generated_at=datetime.utcnow())

    # Role Management

    def create_role(self, data: RoleCreate, created_by: str) -> Role:
        """Create a custom role."""
        role_id = self._generate_id("role")

        role = Role(
            id=role_id,
            name=data.name,
            description=data.description,
            scope=data.scope,
            permissions=data.permissions,
            is_system=False,
            workspace_id=data.workspace_id,
            metadata=data.metadata,
        )

        self.roles[role_id] = role
        return role

    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self.roles.get(role_id)

    def update_role(self, role_id: str, data: RoleUpdate) -> Optional[Role]:
        """Update role."""
        role = self.roles.get(role_id)
        if not role or role.is_system:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)
        role.updated_at = datetime.utcnow()

        return role

    def delete_role(self, role_id: str) -> bool:
        """Delete role."""
        role = self.roles.get(role_id)
        if not role or role.is_system:
            return False

        # Remove role assignments
        self.role_assignments = {
            k: v for k, v in self.role_assignments.items()
            if v.role_id != role_id
        }

        del self.roles[role_id]
        return True

    def list_roles(
        self,
        scope: Optional[PermissionScope] = None,
        workspace_id: Optional[str] = None,
        include_system: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> RoleListResponse:
        """List roles."""
        roles = list(self.roles.values())

        if not include_system:
            roles = [r for r in roles if not r.is_system]
        if scope:
            roles = [r for r in roles if r.scope == scope]
        if workspace_id:
            roles = [r for r in roles if r.workspace_id == workspace_id or r.workspace_id is None]

        # Count users per role
        for role in roles:
            role.user_count = sum(1 for a in self.role_assignments.values() if a.role_id == role.id)

        total = len(roles)
        roles = roles[skip:skip + limit]

        return RoleListResponse(roles=roles, total=total)

    # Role Assignment

    def _assign_role(self, user_id: str, role_id: str, assigned_by: str, workspace_id: Optional[str] = None, expires_at: Optional[datetime] = None):
        """Internal role assignment."""
        role = self.roles.get(role_id)
        if not role:
            return None

        assignment_id = self._generate_id("ra")
        assignment = RoleAssignment(
            id=assignment_id,
            user_id=user_id,
            role_id=role_id,
            role_name=role.name,
            workspace_id=workspace_id,
            assigned_by=assigned_by,
            expires_at=expires_at,
        )

        self.role_assignments[assignment_id] = assignment
        return assignment

    def assign_role(self, data: RoleAssignmentCreate, assigned_by: str) -> Optional[RoleAssignment]:
        """Assign role to user."""
        user = self.users.get(data.user_id)
        role = self.roles.get(data.role_id)
        if not user or not role:
            return None

        # Check if already assigned
        for assignment in self.role_assignments.values():
            if (assignment.user_id == data.user_id and
                assignment.role_id == data.role_id and
                assignment.workspace_id == data.workspace_id):
                return assignment

        assignment = self._assign_role(
            data.user_id, data.role_id, assigned_by,
            data.workspace_id, data.expires_at
        )

        if assignment:
            self._log_audit(
                data.user_id, user.email, AuditAction.PERMISSION_CHANGED,
                {"role_assigned": role.name, "by": assigned_by}
            )

        return assignment

    def revoke_role(self, assignment_id: str, revoked_by: str) -> bool:
        """Revoke role assignment."""
        assignment = self.role_assignments.get(assignment_id)
        if not assignment:
            return False

        user = self.users.get(assignment.user_id)
        if user:
            self._log_audit(
                assignment.user_id, user.email, AuditAction.PERMISSION_CHANGED,
                {"role_revoked": assignment.role_name, "by": revoked_by}
            )

        del self.role_assignments[assignment_id]
        return True

    def get_user_roles(self, user_id: str, workspace_id: Optional[str] = None) -> list[RoleAssignment]:
        """Get roles assigned to user."""
        assignments = []
        for assignment in self.role_assignments.values():
            if assignment.user_id == user_id:
                if workspace_id is None or assignment.workspace_id in (None, workspace_id):
                    # Check expiration
                    if assignment.expires_at and assignment.expires_at < datetime.utcnow():
                        continue
                    assignments.append(assignment)
        return assignments

    # Permissions

    def get_user_permissions(self, user_id: str, workspace_id: Optional[str] = None) -> UserPermissions:
        """Get all permissions for a user."""
        global_perms: list[str] = []
        workspace_perms: dict[str, list[str]] = {}

        for assignment in self.role_assignments.values():
            if assignment.user_id != user_id:
                continue
            if assignment.expires_at and assignment.expires_at < datetime.utcnow():
                continue

            role = self.roles.get(assignment.role_id)
            if not role:
                continue

            if assignment.workspace_id is None:
                global_perms.extend(role.permissions)
            else:
                if assignment.workspace_id not in workspace_perms:
                    workspace_perms[assignment.workspace_id] = []
                workspace_perms[assignment.workspace_id].extend(role.permissions)

        # Calculate effective permissions
        effective = list(set(global_perms))
        if workspace_id and workspace_id in workspace_perms:
            effective = list(set(effective + workspace_perms[workspace_id]))

        return UserPermissions(
            user_id=user_id,
            global_permissions=list(set(global_perms)),
            workspace_permissions={k: list(set(v)) for k, v in workspace_perms.items()},
            effective_permissions=effective,
        )

    def check_permission(self, user_id: str, permission: str, workspace_id: Optional[str] = None) -> bool:
        """Check if user has permission."""
        user_perms = self.get_user_permissions(user_id, workspace_id)
        return has_permission(user_perms.effective_permissions, permission)

    def get_all_permissions(self) -> PermissionListResponse:
        """Get all available permissions."""
        permissions = []
        groups = []

        for category, perms in PERMISSION_CATEGORIES.items():
            group_perms = []
            for perm in perms:
                action = perm.split(":")[1]
                p = Permission(
                    id=perm,
                    name=f"{category.title()} - {action.title()}",
                    code=perm,
                    description=f"Permission to {action} {category}",
                    category=category,
                    scope=PermissionScope.GLOBAL,
                    is_sensitive=(action in ["delete", "impersonate", "manage"]),
                )
                permissions.append(p)
                group_perms.append(p)

            groups.append(PermissionGroup(
                id=f"group_{category}",
                name=category.title(),
                category=category,
                permissions=group_perms,
            ))

        return PermissionListResponse(permissions=permissions, groups=groups)

    # Session Management

    def create_session(
        self,
        data: SessionCreate,
        expires_in_hours: int = 24,
    ) -> Session:
        """Create user session."""
        session_id = self._generate_id("sess")
        now = datetime.utcnow()

        # Parse user agent
        device_info = data.device_info or {}
        if data.user_agent:
            ua = parse_user_agent(data.user_agent)
            device_info.update({
                "browser": ua.browser.family,
                "browser_version": ua.browser.version_string,
                "os": ua.os.family,
                "os_version": ua.os.version_string,
                "device": ua.device.family,
                "is_mobile": ua.is_mobile,
                "is_tablet": ua.is_tablet,
                "is_pc": ua.is_pc,
            })

        session = Session(
            id=session_id,
            user_id=data.user_id,
            status=SessionStatus.ACTIVE,
            device_info=device_info,
            ip_address=data.ip_address,
            user_agent=data.user_agent,
            last_activity_at=now,
            expires_at=now + timedelta(hours=expires_in_hours),
            created_at=now,
        )

        self.sessions[session_id] = session

        # Update user
        user = self.users.get(data.user_id)
        if user:
            user.last_login_at = now
            user.login_count += 1
            user.failed_login_count = 0
            self._log_audit(data.user_id, user.email, AuditAction.SESSION_CREATED, {"session_id": session_id}, ip_address=data.ip_address)

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        # Check expiration
        if session.expires_at < datetime.utcnow():
            session.status = SessionStatus.EXPIRED
            return None

        return session

    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity."""
        session = self.sessions.get(session_id)
        if not session or session.status != SessionStatus.ACTIVE:
            return False

        session.last_activity_at = datetime.utcnow()

        # Update user activity
        user = self.users.get(session.user_id)
        if user:
            user.last_active_at = datetime.utcnow()

        return True

    def revoke_session(self, session_id: str, reason: Optional[str] = None) -> bool:
        """Revoke session."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.status = SessionStatus.REVOKED
        session.revoked_at = datetime.utcnow()
        session.revoked_reason = reason

        user = self.users.get(session.user_id)
        if user:
            self._log_audit(session.user_id, user.email, AuditAction.SESSION_REVOKED, {"session_id": session_id, "reason": reason})

        return True

    def revoke_all_sessions(self, user_id: str, except_session_id: Optional[str] = None) -> int:
        """Revoke all user sessions."""
        count = 0
        for session in self.sessions.values():
            if session.user_id == user_id and session.status == SessionStatus.ACTIVE:
                if except_session_id and session.id == except_session_id:
                    continue
                session.status = SessionStatus.REVOKED
                session.revoked_at = datetime.utcnow()
                session.revoked_reason = "All sessions revoked"
                count += 1
        return count

    def get_user_sessions(self, user_id: str, current_session_id: Optional[str] = None) -> SessionListResponse:
        """Get all user sessions."""
        sessions = []
        for session in self.sessions.values():
            if session.user_id == user_id and session.status == SessionStatus.ACTIVE:
                device_info = session.device_info
                sessions.append(SessionInfo(
                    id=session.id,
                    device_type="mobile" if device_info.get("is_mobile") else ("tablet" if device_info.get("is_tablet") else "desktop"),
                    browser=device_info.get("browser"),
                    os=device_info.get("os"),
                    location=session.location,
                    ip_address=session.ip_address,
                    is_current=(session.id == current_session_id),
                    last_activity_at=session.last_activity_at,
                    created_at=session.created_at,
                ))

        return SessionListResponse(sessions=sessions, total=len(sessions))

    # Audit Logging

    def _log_audit(
        self,
        user_id: str,
        user_email: str,
        action: AuditAction,
        details: dict,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ):
        """Log audit entry."""
        entry = AuditLogEntry(
            id=self._generate_id("audit"),
            user_id=user_id,
            user_email=user_email,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )
        self.audit_logs.append(entry)

    def log_login_attempt(
        self,
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """Log login attempt."""
        user = self.get_user_by_email(email)
        user_id = user.id if user else "unknown"

        if not success and user:
            user.failed_login_count += 1
            if user.failed_login_count >= self.password_policy.lockout_threshold:
                user.status = UserStatus.LOCKED
                user.locked_until = datetime.utcnow() + timedelta(minutes=self.password_policy.lockout_duration_minutes)
                self._log_audit(user_id, email, AuditAction.ACCOUNT_LOCKED, {"reason": "Too many failed attempts"}, ip_address)

        self._log_audit(
            user_id, email,
            AuditAction.LOGIN if success else AuditAction.LOGIN_FAILED,
            {},
            ip_address, user_agent, success, error_message
        )

    def query_audit_logs(self, query: AuditLogQuery) -> AuditLogResponse:
        """Query audit logs."""
        entries = self.audit_logs.copy()

        if query.user_id:
            entries = [e for e in entries if e.user_id == query.user_id]
        if query.action:
            entries = [e for e in entries if e.action == query.action]
        if query.resource_type:
            entries = [e for e in entries if e.resource_type == query.resource_type]
        if query.success is not None:
            entries = [e for e in entries if e.success == query.success]
        if query.start_date:
            entries = [e for e in entries if e.created_at >= query.start_date]
        if query.end_date:
            entries = [e for e in entries if e.created_at <= query.end_date]

        # Sort by created_at descending
        entries.sort(key=lambda x: x.created_at, reverse=True)

        total = len(entries)
        entries = entries[query.skip:query.skip + query.limit]

        return AuditLogResponse(entries=entries, total=total)

    # Statistics

    def get_statistics(self) -> UserStatistics:
        """Get user statistics."""
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        users = list(self.users.values())
        active_users = [u for u in users if u.status == UserStatus.ACTIVE]

        return UserStatistics(
            total_users=len(users),
            active_users=len(active_users),
            inactive_users=len([u for u in users if u.status == UserStatus.INACTIVE]),
            locked_users=len([u for u in users if u.status == UserStatus.LOCKED]),
            pending_verification=len([u for u in users if u.status == UserStatus.PENDING_VERIFICATION]),
            users_by_type={t.value: len([u for u in users if u.user_type == t]) for t in UserType},
            users_by_provider={p.value: len([u for u in users if u.auth_provider == p]) for p in AuthProvider},
            mfa_enabled_count=len([u for u in users if u.mfa_enabled]),
            new_users_today=len([u for u in users if u.created_at >= today]),
            new_users_this_week=len([u for u in users if u.created_at >= week_ago]),
            new_users_this_month=len([u for u in users if u.created_at >= month_ago]),
            active_sessions=len([s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE]),
        )


# Global service instance
user_management_service = UserManagementService()
