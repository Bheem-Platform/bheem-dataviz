"""
Audit Middleware

Automatically captures and logs API requests for audit trail.
"""

import time
import uuid
from typing import Callable, Optional
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json
import logging

from app.schemas.audit import AuditLogCreate, sanitize_request_body, ActionCategory, ActionType


logger = logging.getLogger(__name__)


# Route patterns to audit actions mapping
ROUTE_ACTION_MAP = {
    # Authentication
    ("POST", "/api/v1/auth/login"): ("auth.login", ActionCategory.AUTH, ActionType.LOGIN),
    ("POST", "/api/v1/auth/logout"): ("auth.logout", ActionCategory.AUTH, ActionType.LOGOUT),
    ("POST", "/api/v1/auth/register"): ("auth.register", ActionCategory.AUTH, ActionType.CREATE),
    ("POST", "/api/v1/auth/refresh"): ("auth.token_refresh", ActionCategory.AUTH, ActionType.EXECUTE),

    # Dashboards
    ("GET", "/api/v1/dashboards"): ("dashboard.list", ActionCategory.DASHBOARD, ActionType.VIEW),
    ("POST", "/api/v1/dashboards"): ("dashboard.create", ActionCategory.DASHBOARD, ActionType.CREATE),
    ("GET", "/api/v1/dashboards/{id}"): ("dashboard.view", ActionCategory.DASHBOARD, ActionType.VIEW),
    ("PUT", "/api/v1/dashboards/{id}"): ("dashboard.update", ActionCategory.DASHBOARD, ActionType.UPDATE),
    ("PATCH", "/api/v1/dashboards/{id}"): ("dashboard.update", ActionCategory.DASHBOARD, ActionType.UPDATE),
    ("DELETE", "/api/v1/dashboards/{id}"): ("dashboard.delete", ActionCategory.DASHBOARD, ActionType.DELETE),
    ("POST", "/api/v1/dashboards/{id}/share"): ("dashboard.share", ActionCategory.DASHBOARD, ActionType.SHARE),
    ("POST", "/api/v1/dashboards/{id}/export"): ("dashboard.export", ActionCategory.DASHBOARD, ActionType.EXPORT),

    # Charts
    ("GET", "/api/v1/charts"): ("chart.list", ActionCategory.CHART, ActionType.VIEW),
    ("POST", "/api/v1/charts"): ("chart.create", ActionCategory.CHART, ActionType.CREATE),
    ("GET", "/api/v1/charts/{id}"): ("chart.view", ActionCategory.CHART, ActionType.VIEW),
    ("PUT", "/api/v1/charts/{id}"): ("chart.update", ActionCategory.CHART, ActionType.UPDATE),
    ("PATCH", "/api/v1/charts/{id}"): ("chart.update", ActionCategory.CHART, ActionType.UPDATE),
    ("DELETE", "/api/v1/charts/{id}"): ("chart.delete", ActionCategory.CHART, ActionType.DELETE),
    ("POST", "/api/v1/charts/{id}/export"): ("chart.export", ActionCategory.CHART, ActionType.EXPORT),

    # Connections
    ("GET", "/api/v1/connections"): ("connection.list", ActionCategory.CONNECTION, ActionType.VIEW),
    ("POST", "/api/v1/connections"): ("connection.create", ActionCategory.CONNECTION, ActionType.CREATE),
    ("GET", "/api/v1/connections/{id}"): ("connection.view", ActionCategory.CONNECTION, ActionType.VIEW),
    ("PUT", "/api/v1/connections/{id}"): ("connection.update", ActionCategory.CONNECTION, ActionType.UPDATE),
    ("DELETE", "/api/v1/connections/{id}"): ("connection.delete", ActionCategory.CONNECTION, ActionType.DELETE),
    ("POST", "/api/v1/connections/{id}/test"): ("connection.test", ActionCategory.CONNECTION, ActionType.EXECUTE),

    # Queries
    ("POST", "/api/v1/queries/execute"): ("query.execute", ActionCategory.QUERY, ActionType.EXECUTE),
    ("POST", "/api/v1/queries"): ("query.save", ActionCategory.QUERY, ActionType.CREATE),
    ("GET", "/api/v1/queries/{id}"): ("query.view", ActionCategory.QUERY, ActionType.VIEW),

    # Data export
    ("POST", "/api/v1/data/export"): ("data.export", ActionCategory.DATA, ActionType.EXPORT),
    ("POST", "/api/v1/datasets/{id}/export"): ("data.export", ActionCategory.DATA, ActionType.EXPORT),

    # Workspaces
    ("GET", "/api/v1/workspaces"): ("workspace.list", ActionCategory.WORKSPACE, ActionType.VIEW),
    ("POST", "/api/v1/workspaces"): ("workspace.create", ActionCategory.WORKSPACE, ActionType.CREATE),
    ("GET", "/api/v1/workspaces/{id}"): ("workspace.view", ActionCategory.WORKSPACE, ActionType.VIEW),
    ("PUT", "/api/v1/workspaces/{id}"): ("workspace.update", ActionCategory.WORKSPACE, ActionType.UPDATE),
    ("DELETE", "/api/v1/workspaces/{id}"): ("workspace.delete", ActionCategory.WORKSPACE, ActionType.DELETE),
    ("POST", "/api/v1/workspaces/{id}/members"): ("workspace.member_add", ActionCategory.WORKSPACE, ActionType.CREATE),
    ("DELETE", "/api/v1/workspaces/{id}/members/{member_id}"): ("workspace.member_remove", ActionCategory.WORKSPACE, ActionType.DELETE),
    ("POST", "/api/v1/workspaces/{id}/invitations"): ("workspace.invite", ActionCategory.WORKSPACE, ActionType.CREATE),

    # Admin
    ("POST", "/api/v1/admin/users"): ("admin.user_create", ActionCategory.ADMIN, ActionType.CREATE),
    ("PUT", "/api/v1/admin/users/{id}"): ("admin.user_update", ActionCategory.ADMIN, ActionType.UPDATE),
    ("DELETE", "/api/v1/admin/users/{id}"): ("admin.user_delete", ActionCategory.ADMIN, ActionType.DELETE),
    ("PUT", "/api/v1/admin/users/{id}/role"): ("admin.role_change", ActionCategory.ADMIN, ActionType.UPDATE),
}

# Paths to skip auditing
SKIP_PATHS = {
    "/api/v1/health",
    "/api/v1/audit/logs",
    "/api/v1/audit/alerts",
    "/api/v1/audit/dashboard",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
}


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    # Check X-Forwarded-For header (from reverse proxies)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    # Fall back to direct client
    if request.client:
        return request.client.host

    return "unknown"


def match_route_pattern(method: str, path: str) -> Optional[tuple]:
    """
    Match a request path to a route pattern.

    Handles path parameters like {id} by normalizing the path.
    """
    # First try exact match
    key = (method, path)
    if key in ROUTE_ACTION_MAP:
        return ROUTE_ACTION_MAP[key]

    # Try pattern matching for paths with IDs
    path_parts = path.split("/")

    for (route_method, route_pattern), action_info in ROUTE_ACTION_MAP.items():
        if route_method != method:
            continue

        pattern_parts = route_pattern.split("/")
        if len(pattern_parts) != len(path_parts):
            continue

        match = True
        for p_part, r_part in zip(path_parts, pattern_parts):
            if r_part.startswith("{") and r_part.endswith("}"):
                # This is a parameter, accept any value
                continue
            if p_part != r_part:
                match = False
                break

        if match:
            return action_info

    return None


def extract_resource_info(path: str, body: Optional[dict]) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract resource type, ID, and name from request.

    Returns (resource_type, resource_id, resource_name)
    """
    path_parts = path.strip("/").split("/")

    resource_type = None
    resource_id = None
    resource_name = None

    # Common resource paths: /api/v1/{resource}/{id}
    if len(path_parts) >= 3:
        resource_type = path_parts[2] if len(path_parts) > 2 else None
        # Singularize common plurals
        if resource_type:
            if resource_type.endswith("s"):
                resource_type = resource_type[:-1]  # dashboards -> dashboard

    if len(path_parts) >= 4:
        potential_id = path_parts[3]
        # Check if it looks like a UUID or ID
        if len(potential_id) >= 8 and "-" in potential_id:
            resource_id = potential_id

    # Try to get name from request body
    if body:
        resource_name = body.get("name") or body.get("title")

    return resource_type, resource_id, resource_name


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically logs API requests to the audit trail.

    Captures:
    - Request method, path, query params
    - User information (from auth context)
    - Response status and timing
    - Request body (sanitized)
    """

    def __init__(self, app: ASGIApp, audit_service_factory: Callable):
        super().__init__(app)
        self.audit_service_factory = audit_service_factory

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip certain paths
        if request.url.path in SKIP_PATHS or any(request.url.path.startswith(p) for p in SKIP_PATHS):
            return await call_next(request)

        # Skip non-API routes
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Start timing
        start_time = time.time()

        # Get request body if present
        body = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = json.loads(body_bytes)
            except Exception:
                pass

        # Match route to action
        action_info = match_route_pattern(request.method, request.url.path)

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Only log if we have action info or it's a significant request
        if action_info or response.status_code >= 400:
            try:
                await self._log_request(
                    request=request,
                    response=response,
                    action_info=action_info,
                    body=body,
                    duration_ms=duration_ms,
                )
            except Exception as e:
                logger.error(f"Failed to log audit entry: {e}")

        return response

    async def _log_request(
        self,
        request: Request,
        response: Response,
        action_info: Optional[tuple],
        body: Optional[dict],
        duration_ms: int,
    ):
        """Create and save audit log entry."""
        # Determine action details
        if action_info:
            action, action_category, action_type = action_info
        else:
            # Default action based on method
            action = f"api.{request.method.lower()}"
            action_category = ActionCategory.SYSTEM
            action_type = ActionType.EXECUTE

        # Extract resource info
        resource_type, resource_id, resource_name = extract_resource_info(
            request.url.path,
            body,
        )

        # Get user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        user_email = getattr(request.state, "user_email", None)
        session_id = getattr(request.state, "session_id", None)
        workspace_id = getattr(request.state, "workspace_id", None)

        # Create audit log entry
        audit_log = AuditLogCreate(
            action=action,
            action_category=action_category,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            user_id=user_id,
            user_email=user_email,
            session_id=session_id,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            request_method=request.method,
            request_path=request.url.path,
            request_body=sanitize_request_body(body) if body else None,
            response_status=response.status_code,
            duration_ms=duration_ms,
            workspace_id=workspace_id,
            success=response.status_code < 400,
            error_message=None if response.status_code < 400 else f"HTTP {response.status_code}",
        )

        # Save to database
        audit_service = await self.audit_service_factory()
        await audit_service.log_action(audit_log)


def create_audit_middleware(app: ASGIApp, db_session_factory: Callable) -> AuditMiddleware:
    """
    Factory function to create audit middleware with database session.

    Usage:
        app.add_middleware(
            AuditMiddleware,
            audit_service_factory=lambda: AuditService(get_db())
        )
    """
    async def audit_service_factory():
        from app.services.audit_service import AuditService
        async for db in db_session_factory():
            return AuditService(db)

    return AuditMiddleware(app, audit_service_factory)
