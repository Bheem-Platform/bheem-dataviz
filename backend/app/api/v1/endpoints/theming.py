"""
Theming & White-Label API Endpoints

REST API for themes, branding, and CSS generation.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.theming_service import ThemingService
from app.schemas.theming import (
    ThemeMode,
    ThemeScope,
    Theme,
    ThemeCreate,
    ThemeUpdate,
    Branding,
    BrandingCreate,
    BrandingUpdate,
    UserThemePreferences,
    GeneratedCSS,
    ThemeListResponse,
    ThemePreviewResponse,
)

router = APIRouter()


# Themes

@router.get("/themes", response_model=ThemeListResponse)
async def list_themes(
    workspace_id: Optional[str] = Query(None),
    scope: Optional[ThemeScope] = Query(None),
    mode: Optional[ThemeMode] = Query(None),
    include_system: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """
    List available themes.

    Returns system themes and workspace-specific themes.
    """
    service = ThemingService(db)
    return await service.list_themes(workspace_id, scope, mode, include_system)


@router.post("/themes", response_model=Theme)
async def create_theme(
    data: ThemeCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new theme."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ThemingService(db)
    return await service.create_theme(user_id, data)


@router.get("/themes/{theme_id}", response_model=Theme)
async def get_theme(
    theme_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a theme by ID."""
    service = ThemingService(db)
    theme = await service.get_theme(theme_id)

    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    return theme


@router.patch("/themes/{theme_id}", response_model=Theme)
async def update_theme(
    theme_id: str,
    data: ThemeUpdate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update a theme."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ThemingService(db)
    try:
        theme = await service.update_theme(theme_id, user_id, data)
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        return theme
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/themes/{theme_id}")
async def delete_theme(
    theme_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete a theme."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ThemingService(db)
    try:
        success = await service.delete_theme(theme_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Theme not found")
        return {"deleted": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/themes/{theme_id}/duplicate", response_model=Theme)
async def duplicate_theme(
    theme_id: str,
    name: str = Query(..., description="Name for the duplicated theme"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Duplicate a theme."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ThemingService(db)
    theme = await service.duplicate_theme(theme_id, user_id, name)

    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    return theme


# Presets

@router.get("/presets")
async def get_preset_themes(
    db: AsyncSession = Depends(get_db),
):
    """Get available theme presets."""
    service = ThemingService(db)
    return {"presets": await service.get_preset_themes()}


@router.post("/themes/{theme_id}/apply-preset", response_model=Theme)
async def apply_preset_to_theme(
    theme_id: str,
    preset_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Apply a preset to a theme."""
    service = ThemingService(db)
    try:
        theme = await service.apply_preset(theme_id, preset_id)
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        return theme
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# CSS Generation

@router.get("/themes/{theme_id}/css", response_model=GeneratedCSS)
async def get_theme_css(
    theme_id: str,
    minify: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """Get generated CSS for a theme."""
    service = ThemingService(db)
    try:
        return await service.generate_css(theme_id, minify)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/themes/{theme_id}/css.css")
async def get_theme_css_file(
    theme_id: str,
    minify: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """Get CSS file for a theme (for direct inclusion)."""
    service = ThemingService(db)
    try:
        result = await service.generate_css(theme_id, minify)
        return Response(
            content=result.css,
            media_type="text/css",
            headers={"Cache-Control": f"public, max-age=3600, immutable"},
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Theme not found")


# Preview

@router.get("/themes/{theme_id}/preview", response_model=ThemePreviewResponse)
async def get_theme_preview(
    theme_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get theme preview with CSS and sample components."""
    service = ThemingService(db)
    try:
        return await service.get_theme_preview(theme_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Branding

@router.get("/branding/{workspace_id}", response_model=Branding)
async def get_branding(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get branding configuration for a workspace."""
    service = ThemingService(db)
    branding = await service.get_branding(workspace_id)

    if not branding:
        raise HTTPException(status_code=404, detail="Branding not found")

    return branding


@router.post("/branding", response_model=Branding)
async def create_branding(
    data: BrandingCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create branding configuration for a workspace."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ThemingService(db)
    try:
        return await service.create_branding(user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/branding/{workspace_id}", response_model=Branding)
async def update_branding(
    workspace_id: str,
    data: BrandingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update branding configuration."""
    service = ThemingService(db)
    branding = await service.update_branding(workspace_id, data)

    if not branding:
        raise HTTPException(status_code=404, detail="Branding not found")

    return branding


@router.delete("/branding/{workspace_id}")
async def delete_branding(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete branding configuration."""
    service = ThemingService(db)
    success = await service.delete_branding(workspace_id)

    if not success:
        raise HTTPException(status_code=404, detail="Branding not found")

    return {"deleted": True}


@router.post("/branding/{workspace_id}/verify-domain")
async def verify_custom_domain(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Verify custom domain configuration."""
    service = ThemingService(db)
    try:
        return await service.verify_custom_domain(workspace_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# User Preferences

@router.get("/preferences", response_model=UserThemePreferences)
async def get_user_preferences(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get current user's theme preferences."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ThemingService(db)
    return await service.get_user_preferences(user_id)


@router.put("/preferences", response_model=UserThemePreferences)
async def update_user_preferences(
    mode: Optional[ThemeMode] = Query(None),
    theme_id: Optional[str] = Query(None),
    font_size: Optional[str] = Query(None),
    reduce_motion: Optional[bool] = Query(None),
    high_contrast: Optional[bool] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update user's theme preferences."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ThemingService(db)
    return await service.update_user_preferences(
        user_id, mode, theme_id, font_size, reduce_motion, high_contrast
    )


# Active Theme

@router.get("/active", response_model=Theme)
async def get_active_theme(
    workspace_id: Optional[str] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get the active theme for the current user/workspace."""
    user_id = getattr(request.state, "user_id", None)

    service = ThemingService(db)
    return await service.resolve_active_theme(user_id, workspace_id)


@router.get("/active/css.css")
async def get_active_theme_css(
    workspace_id: Optional[str] = Query(None),
    minify: bool = Query(True),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get CSS for the active theme."""
    user_id = getattr(request.state, "user_id", None)

    service = ThemingService(db)
    theme = await service.resolve_active_theme(user_id, workspace_id)
    result = await service.generate_css(theme.id, minify)

    return Response(
        content=result.css,
        media_type="text/css",
        headers={"Cache-Control": "private, max-age=300"},
    )
