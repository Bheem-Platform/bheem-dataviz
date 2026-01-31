"""
Embed Service

Handles embed token generation, validation, and analytics.
"""

import secrets
import hashlib
import uuid
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import selectinload
import logging

from app.models.embed import (
    EmbedToken,
    EmbedSession,
    EmbedAnalytics,
    EmbedWhitelist,
    EmbedResourceType,
)
from app.schemas.embed import (
    EmbedTokenCreate,
    EmbedTokenUpdate,
    EmbedTokenResponse,
    EmbedTokenSummary,
    EmbedValidationResponse,
    EmbedSessionResponse,
    EmbedAnalyticsSummary,
    EmbedTokenAnalytics,
    DomainWhitelistCreate,
    DomainWhitelistResponse,
    EmbedCodeRequest,
    EmbedCodeResponse,
    generate_iframe_html,
    generate_sdk_snippet,
    generate_react_component,
    generate_vue_component,
    validate_domain,
    TOKEN_LENGTH,
    TOKEN_PREFIX,
)


logger = logging.getLogger(__name__)


class EmbedService:
    """Service for managing embedded content tokens and sessions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Token Management

    async def create_token(
        self,
        data: EmbedTokenCreate,
        created_by: str,
    ) -> tuple[EmbedTokenResponse, str]:
        """
        Create a new embed token.

        Returns the token response and the plain token value.
        The plain token is only available at creation time.
        """
        # Generate secure token
        plain_token = TOKEN_PREFIX + secrets.token_urlsafe(TOKEN_LENGTH)
        token_hash = self._hash_token(plain_token)

        # Create token record
        embed_token = EmbedToken(
            token_hash=token_hash,
            name=data.name,
            description=data.description,
            created_by=uuid.UUID(created_by),
            workspace_id=uuid.UUID(data.workspace_id) if data.workspace_id else None,
            resource_type=data.resource_type.value,
            resource_id=uuid.UUID(data.resource_id),
            allow_interactions=data.allow_interactions,
            allow_export=data.allow_export,
            allow_fullscreen=data.allow_fullscreen,
            allow_comments=data.allow_comments,
            theme=data.theme.value,
            show_header=data.show_header,
            show_toolbar=data.show_toolbar,
            custom_css=data.custom_css,
            allowed_domains=data.allowed_domains,
            expires_at=data.expires_at,
            max_views=data.max_views,
            settings=data.settings,
        )

        self.db.add(embed_token)
        await self.db.commit()
        await self.db.refresh(embed_token)

        response = self._to_response(embed_token)
        response.token = plain_token  # Only available at creation

        return response, plain_token

    async def get_token(self, token_id: str) -> Optional[EmbedTokenResponse]:
        """Get an embed token by ID."""
        result = await self.db.execute(
            select(EmbedToken).where(EmbedToken.id == uuid.UUID(token_id))
        )
        token = result.scalar_one_or_none()

        if not token:
            return None

        return self._to_response(token)

    async def list_tokens(
        self,
        created_by: Optional[str] = None,
        workspace_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> list[EmbedTokenSummary]:
        """List embed tokens with optional filtering."""
        query = select(EmbedToken)

        if created_by:
            query = query.where(EmbedToken.created_by == uuid.UUID(created_by))
        if workspace_id:
            query = query.where(EmbedToken.workspace_id == uuid.UUID(workspace_id))
        if resource_type:
            query = query.where(EmbedToken.resource_type == resource_type)
        if resource_id:
            query = query.where(EmbedToken.resource_id == uuid.UUID(resource_id))
        if active_only:
            query = query.where(EmbedToken.is_active == True)

        query = query.order_by(EmbedToken.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        tokens = result.scalars().all()

        return [
            EmbedTokenSummary(
                id=str(t.id),
                name=t.name,
                resource_type=t.resource_type,
                resource_id=str(t.resource_id),
                is_active=t.is_active,
                view_count=t.view_count,
                created_at=t.created_at,
                expires_at=t.expires_at,
                last_used_at=t.last_used_at,
            )
            for t in tokens
        ]

    async def update_token(
        self,
        token_id: str,
        data: EmbedTokenUpdate,
    ) -> Optional[EmbedTokenResponse]:
        """Update an embed token."""
        result = await self.db.execute(
            select(EmbedToken).where(EmbedToken.id == uuid.UUID(token_id))
        )
        token = result.scalar_one_or_none()

        if not token:
            return None

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(token, field):
                setattr(token, field, value)

        await self.db.commit()
        await self.db.refresh(token)

        return self._to_response(token)

    async def revoke_token(
        self,
        token_id: str,
        revoked_by: str,
    ) -> bool:
        """Revoke an embed token."""
        result = await self.db.execute(
            select(EmbedToken).where(EmbedToken.id == uuid.UUID(token_id))
        )
        token = result.scalar_one_or_none()

        if not token:
            return False

        token.is_active = False
        token.revoked_at = datetime.utcnow()
        token.revoked_by = uuid.UUID(revoked_by)

        await self.db.commit()
        return True

    async def delete_token(self, token_id: str) -> bool:
        """Permanently delete an embed token."""
        result = await self.db.execute(
            select(EmbedToken).where(EmbedToken.id == uuid.UUID(token_id))
        )
        token = result.scalar_one_or_none()

        if not token:
            return False

        await self.db.delete(token)
        await self.db.commit()
        return True

    # Token Validation

    async def validate_token(
        self,
        plain_token: str,
        origin: Optional[str] = None,
    ) -> EmbedValidationResponse:
        """
        Validate an embed token.

        Checks:
        - Token exists and is valid
        - Token is active
        - Token has not expired
        - Token has not exceeded max views
        - Origin domain is allowed
        """
        token_hash = self._hash_token(plain_token)

        result = await self.db.execute(
            select(EmbedToken).where(EmbedToken.token_hash == token_hash)
        )
        token = result.scalar_one_or_none()

        if not token:
            return EmbedValidationResponse(
                valid=False,
                error="Invalid token",
            )

        # Check if active
        if not token.is_active:
            return EmbedValidationResponse(
                valid=False,
                error="Token has been revoked",
            )

        # Check expiration
        if token.expires_at and token.expires_at < datetime.utcnow():
            return EmbedValidationResponse(
                valid=False,
                error="Token has expired",
            )

        # Check max views
        if token.max_views and token.view_count >= token.max_views:
            return EmbedValidationResponse(
                valid=False,
                error="Token has exceeded maximum views",
            )

        # Check domain
        if origin and token.allowed_domains:
            domain = self._extract_domain(origin)
            if not validate_domain(domain, token.allowed_domains):
                return EmbedValidationResponse(
                    valid=False,
                    error="Origin domain not allowed",
                )

        # Generate session ID
        session_id = str(uuid.uuid4())

        return EmbedValidationResponse(
            valid=True,
            resource_type=token.resource_type,
            resource_id=str(token.resource_id),
            permissions={
                "allow_interactions": token.allow_interactions,
                "allow_export": token.allow_export,
                "allow_fullscreen": token.allow_fullscreen,
                "allow_comments": token.allow_comments,
            },
            appearance={
                "theme": token.theme,
                "show_header": token.show_header,
                "show_toolbar": token.show_toolbar,
                "custom_css": token.custom_css,
            },
            session_id=session_id,
        )

    # Session Management

    async def start_session(
        self,
        plain_token: str,
        origin_url: Optional[str] = None,
        referrer: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[EmbedSessionResponse]:
        """Start an embed session."""
        # Validate token first
        validation = await self.validate_token(plain_token, origin_url)
        if not validation.valid:
            return None

        # Get token
        token_hash = self._hash_token(plain_token)
        result = await self.db.execute(
            select(EmbedToken).where(EmbedToken.token_hash == token_hash)
        )
        token = result.scalar_one_or_none()

        if not token:
            return None

        # Parse user agent for device info
        device_type = self._detect_device_type(user_agent)
        browser = self._detect_browser(user_agent)
        os = self._detect_os(user_agent)

        # Create session
        session = EmbedSession(
            token_id=token.id,
            session_id=validation.session_id,
            origin_domain=self._extract_domain(origin_url) if origin_url else None,
            origin_url=origin_url,
            referrer=referrer,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
            browser=browser,
            os=os,
        )

        self.db.add(session)

        # Increment view count and update last used
        token.view_count += 1
        token.last_used_at = datetime.utcnow()

        await self.db.commit()

        return EmbedSessionResponse(
            session_id=validation.session_id,
            resource_type=validation.resource_type,
            resource_id=validation.resource_id,
            permissions=validation.permissions,
            appearance=validation.appearance,
        )

    async def end_session(
        self,
        session_id: str,
        duration_seconds: Optional[int] = None,
        interaction_count: Optional[int] = None,
        filter_changes: Optional[int] = None,
        exports_count: Optional[int] = None,
    ) -> bool:
        """End an embed session and record metrics."""
        result = await self.db.execute(
            select(EmbedSession).where(EmbedSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            return False

        session.ended_at = datetime.utcnow()
        if duration_seconds is not None:
            session.duration_seconds = duration_seconds
        if interaction_count is not None:
            session.interaction_count = interaction_count
        if filter_changes is not None:
            session.filter_changes = filter_changes
        if exports_count is not None:
            session.exports_count = exports_count

        await self.db.commit()
        return True

    async def track_event(
        self,
        session_id: str,
        event_type: str,
        event_data: dict = None,
    ) -> bool:
        """Track an event in an embed session."""
        result = await self.db.execute(
            select(EmbedSession).where(EmbedSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            return False

        # Update counters based on event type
        if event_type == "interaction":
            session.interaction_count += 1
        elif event_type == "filter_change":
            session.filter_changes += 1
        elif event_type == "export":
            session.exports_count += 1

        # Store event in metadata
        if event_data:
            events = session.extra_metadata.get("events", [])
            events.append({
                "type": event_type,
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat(),
            })
            session.extra_metadata["events"] = events[-100]  # Keep last 100 events

        await self.db.commit()
        return True

    # Analytics

    async def get_token_analytics(
        self,
        token_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> EmbedTokenAnalytics:
        """Get analytics for a specific token."""
        # Set default date range (last 30 days)
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Get token
        result = await self.db.execute(
            select(EmbedToken).where(EmbedToken.id == uuid.UUID(token_id))
        )
        token = result.scalar_one_or_none()

        if not token:
            return None

        # Get session stats
        sessions_query = select(
            func.count(EmbedSession.id).label("total_sessions"),
            func.avg(EmbedSession.duration_seconds).label("avg_duration"),
        ).where(
            and_(
                EmbedSession.token_id == uuid.UUID(token_id),
                EmbedSession.started_at >= start_date,
                EmbedSession.started_at <= end_date,
            )
        )

        sessions_result = await self.db.execute(sessions_query)
        session_stats = sessions_result.one()

        # Get top domains
        domains_query = select(
            EmbedSession.origin_domain,
            func.count(EmbedSession.id).label("count"),
        ).where(
            and_(
                EmbedSession.token_id == uuid.UUID(token_id),
                EmbedSession.origin_domain.isnot(None),
            )
        ).group_by(EmbedSession.origin_domain).order_by(
            func.count(EmbedSession.id).desc()
        ).limit(5)

        domains_result = await self.db.execute(domains_query)
        top_domains = [row.origin_domain for row in domains_result.all()]

        return EmbedTokenAnalytics(
            token_id=str(token.id),
            token_name=token.name,
            total_views=token.view_count,
            unique_sessions=session_stats.total_sessions or 0,
            avg_duration_seconds=float(session_stats.avg_duration or 0),
            last_viewed_at=token.last_used_at,
            top_domains=top_domains,
        )

    async def get_analytics_summary(
        self,
        workspace_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> EmbedAnalyticsSummary:
        """Get aggregated analytics summary."""
        # Set default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Build token filter
        token_conditions = []
        if workspace_id:
            token_conditions.append(EmbedToken.workspace_id == uuid.UUID(workspace_id))
        if resource_type:
            token_conditions.append(EmbedToken.resource_type == resource_type)
        if resource_id:
            token_conditions.append(EmbedToken.resource_id == uuid.UUID(resource_id))

        # Get token IDs
        token_query = select(EmbedToken.id)
        if token_conditions:
            token_query = token_query.where(and_(*token_conditions))
        token_result = await self.db.execute(token_query)
        token_ids = [row[0] for row in token_result.all()]

        if not token_ids:
            return EmbedAnalyticsSummary(
                total_views=0,
                unique_sessions=0,
                total_interactions=0,
                total_exports=0,
                avg_duration_seconds=0,
                views_by_device={},
                views_by_date=[],
                top_domains=[],
            )

        # Get session stats
        session_query = select(
            func.count(EmbedSession.id).label("total_sessions"),
            func.sum(EmbedSession.interaction_count).label("total_interactions"),
            func.sum(EmbedSession.exports_count).label("total_exports"),
            func.avg(EmbedSession.duration_seconds).label("avg_duration"),
        ).where(
            and_(
                EmbedSession.token_id.in_(token_ids),
                EmbedSession.started_at >= start_date,
                EmbedSession.started_at <= end_date,
            )
        )

        session_result = await self.db.execute(session_query)
        stats = session_result.one()

        # Get total views from tokens
        views_query = select(func.sum(EmbedToken.view_count)).where(
            EmbedToken.id.in_(token_ids)
        )
        views_result = await self.db.execute(views_query)
        total_views = views_result.scalar() or 0

        # Device breakdown
        device_query = select(
            EmbedSession.device_type,
            func.count(EmbedSession.id).label("count"),
        ).where(
            EmbedSession.token_id.in_(token_ids)
        ).group_by(EmbedSession.device_type)

        device_result = await self.db.execute(device_query)
        views_by_device = {
            row.device_type or "unknown": row.count
            for row in device_result.all()
        }

        # Daily views
        daily_query = select(
            func.date(EmbedSession.started_at).label("date"),
            func.count(EmbedSession.id).label("views"),
        ).where(
            and_(
                EmbedSession.token_id.in_(token_ids),
                EmbedSession.started_at >= start_date,
                EmbedSession.started_at <= end_date,
            )
        ).group_by(func.date(EmbedSession.started_at)).order_by("date")

        daily_result = await self.db.execute(daily_query)
        views_by_date = [
            {"date": row.date.isoformat(), "views": row.views}
            for row in daily_result.all()
        ]

        # Top domains
        domains_query = select(
            EmbedSession.origin_domain,
            func.count(EmbedSession.id).label("count"),
        ).where(
            and_(
                EmbedSession.token_id.in_(token_ids),
                EmbedSession.origin_domain.isnot(None),
            )
        ).group_by(EmbedSession.origin_domain).order_by(
            func.count(EmbedSession.id).desc()
        ).limit(10)

        domains_result = await self.db.execute(domains_query)
        top_domains = [
            {"domain": row.origin_domain, "views": row.count}
            for row in domains_result.all()
        ]

        return EmbedAnalyticsSummary(
            total_views=total_views,
            unique_sessions=stats.total_sessions or 0,
            total_interactions=stats.total_interactions or 0,
            total_exports=stats.total_exports or 0,
            avg_duration_seconds=float(stats.avg_duration or 0),
            views_by_device=views_by_device,
            views_by_date=views_by_date,
            top_domains=top_domains,
        )

    # Whitelist Management

    async def add_domain_to_whitelist(
        self,
        workspace_id: str,
        data: DomainWhitelistCreate,
        added_by: str,
    ) -> DomainWhitelistResponse:
        """Add a domain to the workspace whitelist."""
        whitelist = EmbedWhitelist(
            workspace_id=uuid.UUID(workspace_id),
            domain=data.domain,
            is_wildcard=data.is_wildcard,
            added_by=uuid.UUID(added_by),
            notes=data.notes,
        )

        self.db.add(whitelist)
        await self.db.commit()
        await self.db.refresh(whitelist)

        return DomainWhitelistResponse.model_validate(whitelist)

    async def list_whitelist(
        self,
        workspace_id: str,
    ) -> list[DomainWhitelistResponse]:
        """List all whitelisted domains for a workspace."""
        result = await self.db.execute(
            select(EmbedWhitelist).where(
                and_(
                    EmbedWhitelist.workspace_id == uuid.UUID(workspace_id),
                    EmbedWhitelist.is_active == True,
                )
            ).order_by(EmbedWhitelist.domain)
        )
        entries = result.scalars().all()

        return [DomainWhitelistResponse.model_validate(e) for e in entries]

    async def remove_from_whitelist(
        self,
        whitelist_id: str,
    ) -> bool:
        """Remove a domain from the whitelist."""
        result = await self.db.execute(
            select(EmbedWhitelist).where(
                EmbedWhitelist.id == uuid.UUID(whitelist_id)
            )
        )
        entry = result.scalar_one_or_none()

        if not entry:
            return False

        entry.is_active = False
        await self.db.commit()
        return True

    # Code Generation

    async def generate_embed_code(
        self,
        token_id: str,
        request: EmbedCodeRequest,
        base_url: str,
    ) -> Optional[EmbedCodeResponse]:
        """Generate embed code for a token."""
        result = await self.db.execute(
            select(EmbedToken).where(EmbedToken.id == uuid.UUID(token_id))
        )
        token = result.scalar_one_or_none()

        if not token:
            return None

        # For code generation, we need to re-create a displayable token
        # This is a security consideration - in production, use a different approach
        iframe_url = f"{base_url}/embed/{token_id}"

        html = generate_iframe_html(
            url=iframe_url,
            width=request.width,
            height=request.height,
            title=token.name,
            allow_fullscreen=token.allow_fullscreen,
        )

        response = EmbedCodeResponse(
            html=html,
            iframe_url=iframe_url,
        )

        if request.include_sdk:
            response.javascript = generate_sdk_snippet(token_id, "embed-container")

        if request.framework == "react":
            response.react_component = generate_react_component(token_id)
        elif request.framework == "vue":
            response.vue_component = generate_vue_component(token_id)

        return response

    # Helper Methods

    def _hash_token(self, plain_token: str) -> str:
        """Hash a token for secure storage."""
        return hashlib.sha256(plain_token.encode()).hexdigest()

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc or parsed.path.split("/")[0]
        except Exception:
            return url

    def _detect_device_type(self, user_agent: Optional[str]) -> str:
        """Detect device type from user agent."""
        if not user_agent:
            return "unknown"

        ua_lower = user_agent.lower()
        if "mobile" in ua_lower or "android" in ua_lower and "mobile" in ua_lower:
            return "mobile"
        elif "tablet" in ua_lower or "ipad" in ua_lower:
            return "tablet"
        else:
            return "desktop"

    def _detect_browser(self, user_agent: Optional[str]) -> Optional[str]:
        """Detect browser from user agent."""
        if not user_agent:
            return None

        ua_lower = user_agent.lower()
        if "chrome" in ua_lower:
            return "chrome"
        elif "firefox" in ua_lower:
            return "firefox"
        elif "safari" in ua_lower:
            return "safari"
        elif "edge" in ua_lower:
            return "edge"
        elif "opera" in ua_lower:
            return "opera"
        return "other"

    def _detect_os(self, user_agent: Optional[str]) -> Optional[str]:
        """Detect OS from user agent."""
        if not user_agent:
            return None

        ua_lower = user_agent.lower()
        if "windows" in ua_lower:
            return "windows"
        elif "mac" in ua_lower:
            return "macos"
        elif "linux" in ua_lower:
            return "linux"
        elif "android" in ua_lower:
            return "android"
        elif "iphone" in ua_lower or "ipad" in ua_lower:
            return "ios"
        return "other"

    def _to_response(self, token: EmbedToken) -> EmbedTokenResponse:
        """Convert EmbedToken model to response schema."""
        return EmbedTokenResponse(
            id=str(token.id),
            name=token.name,
            description=token.description,
            created_by=str(token.created_by),
            workspace_id=str(token.workspace_id) if token.workspace_id else None,
            resource_type=token.resource_type,
            resource_id=str(token.resource_id),
            allow_interactions=token.allow_interactions,
            allow_export=token.allow_export,
            allow_fullscreen=token.allow_fullscreen,
            allow_comments=token.allow_comments,
            theme=token.theme,
            show_header=token.show_header,
            show_toolbar=token.show_toolbar,
            custom_css=token.custom_css,
            allowed_domains=token.allowed_domains or [],
            expires_at=token.expires_at,
            max_views=token.max_views,
            view_count=token.view_count,
            is_active=token.is_active,
            revoked_at=token.revoked_at,
            created_at=token.created_at,
            last_used_at=token.last_used_at,
            settings=token.settings or {},
        )
