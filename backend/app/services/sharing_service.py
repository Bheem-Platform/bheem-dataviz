"""
Sharing Service

Handles public links, password protection, and sharing features.
"""

import uuid
import base64
from typing import Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.sharing import (
    ShareType,
    ShareAccess,
    LinkStatus,
    ShareVisibility,
    ShareLinkCreate,
    ShareLinkUpdate,
    ShareLink,
    ShareAccessRequest,
    ShareAccessResponse,
    ShareView,
    ShareAnalytics,
    QRCodeConfig,
    QRCodeResponse,
    EmailShareRequest,
    EmailShareResponse,
    ShareTemplate,
    generate_share_token,
    generate_short_code,
    generate_session_token,
    hash_password,
    verify_password,
    validate_email_domain,
    validate_email_access,
    is_link_expired,
    build_share_url,
    build_embed_url,
)


logger = logging.getLogger(__name__)


class SharingService:
    """Service for advanced sharing features."""

    def __init__(self, db: AsyncSession, base_url: str = "https://dataviz.bheemkodee.com"):
        self.db = db
        self.base_url = base_url
        # In-memory stores (production would use database)
        self._share_links: dict[str, dict] = {}  # id -> link
        self._share_views: dict[str, list[dict]] = {}  # link_id -> views
        self._templates: dict[str, dict] = {}  # id -> template
        self._sessions: dict[str, dict] = {}  # session_token -> session
        self._short_codes: dict[str, str] = {}  # short_code -> link_id
        self._slugs: dict[str, str] = {}  # custom_slug -> link_id

    # Share Link Management

    async def create_share_link(
        self,
        data: ShareLinkCreate,
        resource_name: str,
        created_by: str,
        created_by_name: str,
    ) -> ShareLink:
        """Create a new share link."""
        now = datetime.utcnow()
        link_id = str(uuid.uuid4())
        token = generate_share_token()
        short_code = generate_short_code()

        # Ensure unique short_code
        while short_code in self._short_codes:
            short_code = generate_short_code()

        # Check custom slug uniqueness
        if data.custom_slug:
            if data.custom_slug in self._slugs:
                raise ValueError("Custom slug is already in use")
            self._slugs[data.custom_slug] = link_id

        self._short_codes[short_code] = link_id

        # Hash password if provided
        password_hash = None
        if data.password:
            password_hash = hash_password(data.password)

        link_dict = {
            "id": link_id,
            "token": token,
            "short_code": short_code,
            "custom_slug": data.custom_slug,
            "resource_type": data.resource_type,
            "resource_id": data.resource_id,
            "resource_name": resource_name,
            "name": data.name,
            "description": data.description,
            "access_level": data.access_level,
            "visibility": data.visibility,
            "password_hash": password_hash,
            "has_password": data.password is not None,
            "allowed_emails": data.allowed_emails,
            "allowed_domains": data.allowed_domains,
            "expires_at": data.expires_at,
            "max_views": data.max_views,
            "status": LinkStatus.ACTIVE,
            "is_active": True,
            "hide_branding": data.hide_branding,
            "custom_logo_url": data.custom_logo_url,
            "preset_filters": data.preset_filters,
            "locked_filters": data.locked_filters,
            "show_toolbar": data.show_toolbar,
            "show_export": data.show_export,
            "fullscreen_only": data.fullscreen_only,
            "theme": data.theme,
            "track_views": data.track_views,
            "require_name": data.require_name,
            "view_count": 0,
            "unique_viewers": 0,
            "last_viewed_at": None,
            "share_url": build_share_url(self.base_url, short_code, data.custom_slug),
            "embed_url": build_embed_url(self.base_url, token),
            "qr_code_url": None,
            "created_by": created_by,
            "created_by_name": created_by_name,
            "workspace_id": data.workspace_id,
            "metadata": data.metadata,
            "created_at": now,
            "updated_at": now,
        }

        self._share_links[link_id] = link_dict
        self._share_views[link_id] = []

        # Remove password_hash from response
        response_dict = {k: v for k, v in link_dict.items() if k != "password_hash"}
        return ShareLink(**response_dict)

    async def get_share_link(
        self,
        link_id: str,
    ) -> Optional[ShareLink]:
        """Get a share link by ID."""
        link_dict = self._share_links.get(link_id)
        if not link_dict:
            return None

        response_dict = {k: v for k, v in link_dict.items() if k != "password_hash"}
        return ShareLink(**response_dict)

    async def get_share_link_by_token(
        self,
        token: str,
    ) -> Optional[ShareLink]:
        """Get a share link by token."""
        for link_dict in self._share_links.values():
            if link_dict["token"] == token:
                response_dict = {k: v for k, v in link_dict.items() if k != "password_hash"}
                return ShareLink(**response_dict)
        return None

    async def get_share_link_by_code(
        self,
        code: str,
    ) -> Optional[ShareLink]:
        """Get a share link by short code or custom slug."""
        # Check custom slugs first
        link_id = self._slugs.get(code) or self._short_codes.get(code)
        if link_id:
            return await self.get_share_link(link_id)
        return None

    async def update_share_link(
        self,
        link_id: str,
        update: ShareLinkUpdate,
        user_id: str,
    ) -> Optional[ShareLink]:
        """Update a share link."""
        if link_id not in self._share_links:
            return None

        link_dict = self._share_links[link_id]

        # Only owner can update
        if link_dict["created_by"] != user_id:
            return None

        # Update fields
        if update.name is not None:
            link_dict["name"] = update.name
        if update.description is not None:
            link_dict["description"] = update.description
        if update.access_level is not None:
            link_dict["access_level"] = update.access_level
        if update.visibility is not None:
            link_dict["visibility"] = update.visibility
        if update.password is not None:
            link_dict["password_hash"] = hash_password(update.password)
            link_dict["has_password"] = True
        if update.allowed_emails is not None:
            link_dict["allowed_emails"] = update.allowed_emails
        if update.allowed_domains is not None:
            link_dict["allowed_domains"] = update.allowed_domains
        if update.expires_at is not None:
            link_dict["expires_at"] = update.expires_at
        if update.max_views is not None:
            link_dict["max_views"] = update.max_views
        if update.is_active is not None:
            link_dict["is_active"] = update.is_active
            link_dict["status"] = LinkStatus.ACTIVE if update.is_active else LinkStatus.DISABLED
        if update.hide_branding is not None:
            link_dict["hide_branding"] = update.hide_branding
        if update.custom_logo_url is not None:
            link_dict["custom_logo_url"] = update.custom_logo_url
        if update.preset_filters is not None:
            link_dict["preset_filters"] = update.preset_filters
        if update.locked_filters is not None:
            link_dict["locked_filters"] = update.locked_filters
        if update.show_toolbar is not None:
            link_dict["show_toolbar"] = update.show_toolbar
        if update.show_export is not None:
            link_dict["show_export"] = update.show_export
        if update.theme is not None:
            link_dict["theme"] = update.theme
        if update.metadata is not None:
            link_dict["metadata"] = update.metadata

        link_dict["updated_at"] = datetime.utcnow()
        self._share_links[link_id] = link_dict

        response_dict = {k: v for k, v in link_dict.items() if k != "password_hash"}
        return ShareLink(**response_dict)

    async def delete_share_link(
        self,
        link_id: str,
        user_id: str,
    ) -> bool:
        """Delete a share link."""
        if link_id not in self._share_links:
            return False

        link_dict = self._share_links[link_id]

        # Only owner can delete
        if link_dict["created_by"] != user_id:
            return False

        # Clean up mappings
        short_code = link_dict["short_code"]
        custom_slug = link_dict.get("custom_slug")

        if short_code in self._short_codes:
            del self._short_codes[short_code]
        if custom_slug and custom_slug in self._slugs:
            del self._slugs[custom_slug]

        del self._share_links[link_id]
        if link_id in self._share_views:
            del self._share_views[link_id]

        return True

    async def revoke_share_link(
        self,
        link_id: str,
        user_id: str,
    ) -> Optional[ShareLink]:
        """Revoke a share link (soft delete)."""
        if link_id not in self._share_links:
            return None

        link_dict = self._share_links[link_id]

        if link_dict["created_by"] != user_id:
            return None

        link_dict["status"] = LinkStatus.REVOKED
        link_dict["is_active"] = False
        link_dict["updated_at"] = datetime.utcnow()

        self._share_links[link_id] = link_dict

        response_dict = {k: v for k, v in link_dict.items() if k != "password_hash"}
        return ShareLink(**response_dict)

    async def list_share_links(
        self,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        resource_type: Optional[ShareType] = None,
        resource_id: Optional[str] = None,
        include_revoked: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ShareLink], int]:
        """List share links with filters."""
        links = list(self._share_links.values())

        # Apply filters
        if user_id:
            links = [l for l in links if l["created_by"] == user_id]
        if workspace_id:
            links = [l for l in links if l.get("workspace_id") == workspace_id]
        if resource_type:
            links = [l for l in links if l["resource_type"] == resource_type]
        if resource_id:
            links = [l for l in links if l["resource_id"] == resource_id]
        if not include_revoked:
            links = [l for l in links if l["status"] != LinkStatus.REVOKED]

        # Sort by created_at descending
        links.sort(key=lambda l: l["created_at"], reverse=True)
        total = len(links)

        # Paginate
        links = links[skip:skip + limit]

        return [ShareLink(**{k: v for k, v in l.items() if k != "password_hash"}) for l in links], total

    # Access Validation

    async def validate_access(
        self,
        request: ShareAccessRequest,
        viewer_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ShareAccessResponse:
        """Validate access to a shared resource."""
        # Find link by token
        link = await self.get_share_link_by_token(request.token)
        if not link:
            # Try short code
            link = await self.get_share_link_by_code(request.token)

        if not link:
            return ShareAccessResponse(valid=False, error="Invalid share link")

        # Check if active
        if not link.is_active:
            return ShareAccessResponse(valid=False, error="This share link is no longer active")

        # Check if revoked
        if link.status == LinkStatus.REVOKED:
            return ShareAccessResponse(valid=False, error="This share link has been revoked")

        # Check expiration
        if is_link_expired(link):
            # Update status
            if link.id in self._share_links:
                self._share_links[link.id]["status"] = LinkStatus.EXPIRED
            return ShareAccessResponse(valid=False, error="This share link has expired")

        # Get full link data for password check
        link_dict = self._share_links.get(link.id, {})

        # Check password
        if link.visibility == ShareVisibility.PASSWORD:
            if not request.password:
                return ShareAccessResponse(valid=False, error="Password required")
            if not verify_password(request.password, link_dict.get("password_hash", "")):
                return ShareAccessResponse(valid=False, error="Incorrect password")

        # Check email restrictions
        if link.visibility == ShareVisibility.EMAIL:
            if not request.viewer_email:
                return ShareAccessResponse(valid=False, error="Email required")
            if not validate_email_access(request.viewer_email, link.allowed_emails):
                return ShareAccessResponse(valid=False, error="Email not authorized")

        # Check domain restrictions
        if link.visibility == ShareVisibility.DOMAIN:
            if not request.viewer_email:
                return ShareAccessResponse(valid=False, error="Email required")
            if not validate_email_domain(request.viewer_email, link.allowed_domains):
                return ShareAccessResponse(valid=False, error="Email domain not authorized")

        # Check name requirement
        if link.require_name and not request.viewer_name:
            return ShareAccessResponse(valid=False, error="Name required")

        # Record view
        if link.track_views:
            await self._record_view(
                link_id=link.id,
                viewer_email=request.viewer_email,
                viewer_name=request.viewer_name,
                viewer_ip=viewer_ip,
                user_agent=user_agent,
            )

        # Generate session token
        session_token = generate_session_token()
        self._sessions[session_token] = {
            "link_id": link.id,
            "viewer_email": request.viewer_email,
            "viewer_name": request.viewer_name,
            "started_at": datetime.utcnow(),
            "interactions": 0,
        }

        return ShareAccessResponse(
            valid=True,
            access_level=link.access_level,
            resource_type=link.resource_type,
            resource_id=link.resource_id,
            resource_name=link.resource_name,
            preset_filters=link.preset_filters,
            locked_filters=link.locked_filters,
            show_toolbar=link.show_toolbar,
            show_export=link.show_export,
            theme=link.theme,
            session_token=session_token,
        )

    async def _record_view(
        self,
        link_id: str,
        viewer_email: Optional[str] = None,
        viewer_name: Optional[str] = None,
        viewer_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Record a view of a share link."""
        view = {
            "id": str(uuid.uuid4()),
            "share_link_id": link_id,
            "viewer_ip": viewer_ip,
            "viewer_email": viewer_email,
            "viewer_name": viewer_name,
            "user_agent": user_agent,
            "referrer": None,
            "country": None,
            "city": None,
            "device_type": self._detect_device(user_agent),
            "duration_seconds": None,
            "interactions": 0,
            "viewed_at": datetime.utcnow(),
        }

        if link_id not in self._share_views:
            self._share_views[link_id] = []

        self._share_views[link_id].append(view)

        # Update link stats
        if link_id in self._share_links:
            link = self._share_links[link_id]
            link["view_count"] = link.get("view_count", 0) + 1
            link["last_viewed_at"] = datetime.utcnow()

            # Count unique viewers
            unique_emails = set()
            unique_ips = set()
            for v in self._share_views[link_id]:
                if v.get("viewer_email"):
                    unique_emails.add(v["viewer_email"])
                elif v.get("viewer_ip"):
                    unique_ips.add(v["viewer_ip"])

            link["unique_viewers"] = len(unique_emails) + len(unique_ips)
            self._share_links[link_id] = link

    def _detect_device(self, user_agent: Optional[str]) -> str:
        """Detect device type from user agent."""
        if not user_agent:
            return "unknown"
        ua = user_agent.lower()
        if "mobile" in ua or "android" in ua:
            return "mobile"
        if "tablet" in ua or "ipad" in ua:
            return "tablet"
        return "desktop"

    # Analytics

    async def get_share_analytics(
        self,
        link_id: str,
        days: int = 30,
    ) -> Optional[ShareAnalytics]:
        """Get analytics for a share link."""
        if link_id not in self._share_links:
            return None

        views = self._share_views.get(link_id, [])
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Filter by date range
        recent_views = [v for v in views if v["viewed_at"] >= cutoff]

        # Calculate stats
        total_views = len(recent_views)
        unique_emails = set(v["viewer_email"] for v in recent_views if v.get("viewer_email"))
        unique_ips = set(v["viewer_ip"] for v in recent_views if v.get("viewer_ip"))
        unique_viewers = len(unique_emails) + len(unique_ips)

        durations = [v["duration_seconds"] for v in recent_views if v.get("duration_seconds")]
        avg_duration = sum(durations) / len(durations) if durations else 0

        total_interactions = sum(v.get("interactions", 0) for v in recent_views)

        # Views by day
        views_by_day = {}
        for v in recent_views:
            day = v["viewed_at"].date().isoformat()
            views_by_day[day] = views_by_day.get(day, 0) + 1

        # Views by country
        views_by_country = {}
        for v in recent_views:
            country = v.get("country") or "Unknown"
            views_by_country[country] = views_by_country.get(country, 0) + 1

        # Views by device
        views_by_device = {}
        for v in recent_views:
            device = v.get("device_type") or "unknown"
            views_by_device[device] = views_by_device.get(device, 0) + 1

        # Top viewers
        viewer_counts = {}
        viewer_last_viewed = {}
        for v in recent_views:
            key = v.get("viewer_email") or v.get("viewer_name") or v.get("viewer_ip") or "Anonymous"
            viewer_counts[key] = viewer_counts.get(key, 0) + 1
            viewer_last_viewed[key] = max(viewer_last_viewed.get(key, datetime.min), v["viewed_at"])

        top_viewers = sorted(
            [{"name": k, "views": viewer_counts[k], "last_viewed": viewer_last_viewed[k]}
             for k in viewer_counts],
            key=lambda x: x["views"],
            reverse=True
        )[:10]

        return ShareAnalytics(
            share_link_id=link_id,
            total_views=total_views,
            unique_viewers=unique_viewers,
            avg_duration_seconds=avg_duration,
            total_interactions=total_interactions,
            views_by_day=[{"date": k, "count": v} for k, v in sorted(views_by_day.items())],
            views_by_country=[{"country": k, "count": v} for k, v in views_by_country.items()],
            views_by_device=[{"device": k, "count": v} for k, v in views_by_device.items()],
            views_by_referrer=[],
            top_viewers=top_viewers,
            recent_views=[ShareView(**v) for v in recent_views[-10:]],
            period_start=cutoff,
            period_end=datetime.utcnow(),
        )

    # QR Code

    async def generate_qr_code(
        self,
        link_id: str,
        config: Optional[QRCodeConfig] = None,
    ) -> Optional[QRCodeResponse]:
        """Generate QR code for a share link."""
        link = await self.get_share_link(link_id)
        if not link:
            return None

        config = config or QRCodeConfig()

        # Generate QR code (simplified - in production use qrcode library)
        qr_data = f"QR:{link.share_url}"

        # In production, generate actual QR code image
        qr_code_url = f"{self.base_url}/api/v1/sharing/qr/{link_id}.{config.format}"

        # Update link with QR URL
        if link_id in self._share_links:
            self._share_links[link_id]["qr_code_url"] = qr_code_url

        return QRCodeResponse(
            share_link_id=link_id,
            qr_code_url=qr_code_url,
            qr_code_data=base64.b64encode(qr_data.encode()).decode(),
            share_url=link.share_url,
            expires_at=link.expires_at,
        )

    # Email Sharing

    async def send_share_email(
        self,
        request: EmailShareRequest,
        sender_name: str,
        sender_email: str,
    ) -> EmailShareResponse:
        """Send share link via email."""
        link = await self.get_share_link(request.share_link_id)
        if not link:
            return EmailShareResponse(sent_to=[], failed=[{"email": "all", "error": "Link not found"}])

        sent = []
        failed = []

        for email in request.recipients:
            try:
                # In production, send actual email
                logger.info(f"Would send share email to {email} for link {link.share_url}")
                sent.append(email)
            except Exception as e:
                failed.append({"email": email, "error": str(e)})

        return EmailShareResponse(sent_to=sent, failed=failed)

    # Templates

    async def create_template(
        self,
        name: str,
        settings: ShareLinkCreate,
        created_by: str,
        workspace_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ShareTemplate:
        """Create a share settings template."""
        template = ShareTemplate(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            settings=settings,
            is_default=False,
            created_by=created_by,
            workspace_id=workspace_id,
            created_at=datetime.utcnow(),
        )

        self._templates[template.id] = template.model_dump()
        return template

    async def list_templates(
        self,
        workspace_id: Optional[str] = None,
    ) -> list[ShareTemplate]:
        """List share templates."""
        templates = list(self._templates.values())

        if workspace_id:
            templates = [t for t in templates if t.get("workspace_id") == workspace_id]

        return [ShareTemplate(**t) for t in templates]
