"""
Embed API Endpoints

REST API for embed token management and content serving.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.embed_service import EmbedService
from app.schemas.embed import (
    EmbedTokenCreate,
    EmbedTokenUpdate,
    EmbedTokenResponse,
    EmbedTokenSummary,
    EmbedValidationRequest,
    EmbedValidationResponse,
    EmbedSessionStart,
    EmbedSessionResponse,
    EmbedSessionEnd,
    EmbedSessionTrack,
    EmbedAnalyticsSummary,
    EmbedTokenAnalytics,
    DomainWhitelistCreate,
    DomainWhitelistResponse,
    EmbedCodeRequest,
    EmbedCodeResponse,
    EmbedResourceType,
    EmbedSDKConfig,
)

router = APIRouter()


# Token Management

@router.post("/tokens", response_model=EmbedTokenResponse)
async def create_embed_token(
    token_data: EmbedTokenCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new embed token.

    Returns the token with the plain token value (only available at creation).
    Store this token securely - it cannot be retrieved later.
    """
    # Get user ID from auth context
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        user_id = "00000000-0000-0000-0000-000000000000"  # TODO: Require auth

    embed_service = EmbedService(db)
    response, plain_token = await embed_service.create_token(token_data, user_id)
    response.token = plain_token  # Include plain token in response

    return response


@router.get("/tokens", response_model=list[EmbedTokenSummary])
async def list_embed_tokens(
    request: Request,
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    active_only: bool = Query(True, description="Only return active tokens"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List embed tokens with optional filtering."""
    user_id = getattr(request.state, "user_id", None)

    embed_service = EmbedService(db)
    tokens = await embed_service.list_tokens(
        created_by=user_id,
        workspace_id=workspace_id,
        resource_type=resource_type,
        resource_id=resource_id,
        active_only=active_only,
        skip=skip,
        limit=limit,
    )

    return tokens


@router.get("/tokens/{token_id}", response_model=EmbedTokenResponse)
async def get_embed_token(
    token_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific embed token by ID."""
    embed_service = EmbedService(db)
    token = await embed_service.get_token(token_id)

    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    return token


@router.patch("/tokens/{token_id}", response_model=EmbedTokenResponse)
async def update_embed_token(
    token_id: str,
    update_data: EmbedTokenUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an embed token."""
    embed_service = EmbedService(db)
    token = await embed_service.update_token(token_id, update_data)

    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    return token


@router.post("/tokens/{token_id}/revoke")
async def revoke_embed_token(
    token_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke an embed token.

    The token will no longer be valid for embedding.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    embed_service = EmbedService(db)
    success = await embed_service.revoke_token(token_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Token not found")

    return {"message": "Token revoked successfully"}


@router.delete("/tokens/{token_id}")
async def delete_embed_token(
    token_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Permanently delete an embed token."""
    embed_service = EmbedService(db)
    success = await embed_service.delete_token(token_id)

    if not success:
        raise HTTPException(status_code=404, detail="Token not found")

    return {"message": "Token deleted successfully"}


# Token Validation (Public)

@router.post("/validate", response_model=EmbedValidationResponse)
async def validate_embed_token(
    validation: EmbedValidationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate an embed token.

    This is the primary endpoint used by the embed SDK to verify
    tokens and get resource permissions.
    """
    embed_service = EmbedService(db)
    result = await embed_service.validate_token(
        plain_token=validation.token,
        origin=validation.origin,
    )

    return result


# Session Management (Public)

@router.post("/session/start", response_model=EmbedSessionResponse)
async def start_embed_session(
    session_start: EmbedSessionStart,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Start an embed session.

    Called when embedded content is loaded. Returns resource
    information and permissions.
    """
    # Get client info from request
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    embed_service = EmbedService(db)
    session = await embed_service.start_session(
        plain_token=session_start.token,
        origin_url=session_start.origin_url,
        referrer=session_start.referrer,
        ip_address=ip_address,
        user_agent=user_agent or session_start.user_agent,
    )

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return session


@router.post("/session/end")
async def end_embed_session(
    session_end: EmbedSessionEnd,
    db: AsyncSession = Depends(get_db),
):
    """
    End an embed session.

    Called when the user leaves the embedded content.
    Records session metrics.
    """
    embed_service = EmbedService(db)
    success = await embed_service.end_session(
        session_id=session_end.session_id,
        duration_seconds=session_end.duration_seconds,
        interaction_count=session_end.interaction_count,
        filter_changes=session_end.filter_changes,
        exports_count=session_end.exports_count,
    )

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session ended"}


@router.post("/session/track")
async def track_session_event(
    event: EmbedSessionTrack,
    db: AsyncSession = Depends(get_db),
):
    """
    Track an event in an embed session.

    Used for analytics and engagement tracking.
    """
    embed_service = EmbedService(db)
    success = await embed_service.track_event(
        session_id=event.session_id,
        event_type=event.event_type,
        event_data=event.event_data,
    )

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Event tracked"}


# Analytics

@router.get("/analytics/token/{token_id}", response_model=EmbedTokenAnalytics)
async def get_token_analytics(
    token_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for a specific embed token."""
    embed_service = EmbedService(db)
    analytics = await embed_service.get_token_analytics(
        token_id=token_id,
        start_date=start_date,
        end_date=end_date,
    )

    if not analytics:
        raise HTTPException(status_code=404, detail="Token not found")

    return analytics


@router.get("/analytics/summary", response_model=EmbedAnalyticsSummary)
async def get_analytics_summary(
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated embed analytics summary."""
    embed_service = EmbedService(db)
    summary = await embed_service.get_analytics_summary(
        workspace_id=workspace_id,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
    )

    return summary


# Whitelist Management

@router.get("/whitelist", response_model=list[DomainWhitelistResponse])
async def list_whitelist(
    workspace_id: str = Query(..., description="Workspace ID"),
    db: AsyncSession = Depends(get_db),
):
    """List whitelisted domains for a workspace."""
    embed_service = EmbedService(db)
    return await embed_service.list_whitelist(workspace_id)


@router.post("/whitelist", response_model=DomainWhitelistResponse)
async def add_to_whitelist(
    workspace_id: str,
    domain_data: DomainWhitelistCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Add a domain to the whitelist."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    embed_service = EmbedService(db)
    return await embed_service.add_domain_to_whitelist(
        workspace_id=workspace_id,
        data=domain_data,
        added_by=user_id,
    )


@router.delete("/whitelist/{whitelist_id}")
async def remove_from_whitelist(
    whitelist_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove a domain from the whitelist."""
    embed_service = EmbedService(db)
    success = await embed_service.remove_from_whitelist(whitelist_id)

    if not success:
        raise HTTPException(status_code=404, detail="Whitelist entry not found")

    return {"message": "Domain removed from whitelist"}


# Code Generation

@router.post("/code", response_model=EmbedCodeResponse)
async def generate_embed_code(
    code_request: EmbedCodeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate embed code for a token.

    Returns HTML iframe code and optional JavaScript SDK snippets.
    """
    # Determine base URL
    base_url = str(request.base_url).rstrip("/")

    embed_service = EmbedService(db)
    code = await embed_service.generate_embed_code(
        token_id=code_request.token_id,
        request=code_request,
        base_url=base_url,
    )

    if not code:
        raise HTTPException(status_code=404, detail="Token not found")

    return code


# SDK Configuration

@router.get("/sdk/config", response_model=EmbedSDKConfig)
async def get_sdk_config(
    request: Request,
):
    """Get SDK configuration for the embed client."""
    base_url = str(request.base_url).rstrip("/")

    return EmbedSDKConfig(
        base_url=base_url,
        default_theme="auto",
        auto_resize=True,
        loading_indicator=True,
        error_handling="display",
    )


# Embed Content Serving (Public)

@router.get("/{token_id}", response_class=HTMLResponse)
async def serve_embed(
    token_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Serve embedded content.

    This endpoint renders the actual dashboard/chart for embedding.
    It validates the token and returns an HTML page with the content.
    """
    # Get token by ID (we use ID for URL, not the actual token value)
    embed_service = EmbedService(db)
    token = await embed_service.get_token(token_id)

    if not token:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>Embed Error</title></head>
            <body style="display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
                <div style="text-align:center;">
                    <h2>Content Not Found</h2>
                    <p>The embedded content could not be found.</p>
                </div>
            </body>
            </html>
            """,
            status_code=404,
        )

    if not token.is_active:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head><title>Embed Error</title></head>
            <body style="display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
                <div style="text-align:center;">
                    <h2>Content Unavailable</h2>
                    <p>This embedded content is no longer available.</p>
                </div>
            </body>
            </html>
            """,
            status_code=403,
        )

    # Build embed page
    base_url = str(request.base_url).rstrip("/")
    theme_class = f"theme-{token.theme}" if token.theme != "auto" else ""

    html = f"""
    <!DOCTYPE html>
    <html lang="en" class="{theme_class}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{token.name}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html, body {{ height: 100%; width: 100%; overflow: hidden; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; }}
            .embed-container {{ height: 100%; width: 100%; display: flex; flex-direction: column; }}
            .embed-header {{ padding: 12px 16px; border-bottom: 1px solid #e5e7eb; display: {'flex' if token.show_header else 'none'}; align-items: center; justify-content: space-between; }}
            .embed-header h1 {{ font-size: 16px; font-weight: 600; color: #111827; }}
            .embed-toolbar {{ padding: 8px 16px; border-bottom: 1px solid #e5e7eb; display: {'flex' if token.show_toolbar else 'none'}; gap: 8px; }}
            .embed-content {{ flex: 1; overflow: auto; padding: 16px; }}
            .loading {{ display: flex; justify-content: center; align-items: center; height: 100%; }}
            .spinner {{ width: 40px; height: 40px; border: 3px solid #e5e7eb; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
            .theme-dark body {{ background: #1f2937; color: #f9fafb; }}
            .theme-dark .embed-header {{ border-color: #374151; }}
            .theme-dark .embed-header h1 {{ color: #f9fafb; }}
            {token.custom_css or ''}
        </style>
    </head>
    <body>
        <div class="embed-container">
            <header class="embed-header">
                <h1>{token.name}</h1>
            </header>
            <div class="embed-toolbar">
                <!-- Toolbar content injected by JS -->
            </div>
            <main class="embed-content" id="embed-content">
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            </main>
        </div>
        <script>
            // Embed configuration
            window.EMBED_CONFIG = {{
                tokenId: '{token_id}',
                resourceType: '{token.resource_type}',
                resourceId: '{token.resource_id}',
                permissions: {{
                    interactions: {str(token.allow_interactions).lower()},
                    export: {str(token.allow_export).lower()},
                    fullscreen: {str(token.allow_fullscreen).lower()},
                    comments: {str(token.allow_comments).lower()}
                }},
                baseUrl: '{base_url}'
            }};

            // Load content
            async function loadContent() {{
                try {{
                    // Start session
                    const session = await fetch('{base_url}/api/v1/embed/session/start', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            token: '{token_id}',
                            origin_url: window.location.href,
                            referrer: document.referrer
                        }})
                    }}).then(r => r.json());

                    // Store session ID
                    window.EMBED_SESSION_ID = session.session_id;

                    // Load actual content based on resource type
                    const content = document.getElementById('embed-content');
                    content.innerHTML = '<div style="text-align:center;padding:40px;"><p>Loading {token.resource_type}...</p></div>';

                    // In production, this would load the actual dashboard/chart
                    // For now, show placeholder
                    setTimeout(() => {{
                        content.innerHTML = `
                            <div style="text-align:center;padding:40px;">
                                <h2>{token.resource_type.title()} Content</h2>
                                <p>Resource ID: {token.resource_id}</p>
                                <p style="color:#6b7280;margin-top:16px;">Embedded successfully</p>
                            </div>
                        `;
                    }}, 1000);

                }} catch (err) {{
                    document.getElementById('embed-content').innerHTML = `
                        <div style="text-align:center;padding:40px;color:#dc2626;">
                            <h2>Error Loading Content</h2>
                            <p>${{err.message}}</p>
                        </div>
                    `;
                }}
            }}

            // Track session end on page unload
            window.addEventListener('beforeunload', () => {{
                if (window.EMBED_SESSION_ID) {{
                    navigator.sendBeacon('{base_url}/api/v1/embed/session/end', JSON.stringify({{
                        session_id: window.EMBED_SESSION_ID
                    }}));
                }}
            }});

            loadContent();
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html)


# Quick embed URL generator

@router.get("/quick/{resource_type}/{resource_id}")
async def get_quick_embed(
    resource_type: str,
    resource_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Get or create a quick embed token for a resource.

    Creates a temporary token if none exists.
    """
    # Check for existing active token
    embed_service = EmbedService(db)
    tokens = await embed_service.list_tokens(
        resource_type=resource_type,
        resource_id=resource_id,
        active_only=True,
        limit=1,
    )

    if tokens:
        token = await embed_service.get_token(tokens[0].id)
        base_url = str(request.base_url).rstrip("/")
        return {
            "token_id": token.id,
            "embed_url": f"{base_url}/api/v1/embed/{token.id}",
            "existing": True,
        }

    # Create new token
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    token_data = EmbedTokenCreate(
        name=f"{resource_type.title()} Embed",
        resource_type=resource_type,
        resource_id=resource_id,
    )

    response, plain_token = await embed_service.create_token(token_data, user_id)
    base_url = str(request.base_url).rstrip("/")

    return {
        "token_id": response.id,
        "token": plain_token,
        "embed_url": f"{base_url}/api/v1/embed/{response.id}",
        "existing": False,
    }
