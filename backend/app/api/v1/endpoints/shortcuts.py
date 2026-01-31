"""
Shortcuts & Command Palette API Endpoints

REST API for keyboard shortcuts and command palette features.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.shortcuts_service import ShortcutsService
from app.schemas.shortcuts import (
    CommandCategory,
    ShortcutScope,
    KeyBinding,
    Shortcut,
    ShortcutOverride,
    ShortcutAction,
    ActionType,
    Command,
    CommandGroup,
    ShortcutPreferences,
    CommandHistory,
    CommandSearchResponse,
)

router = APIRouter()


# Shortcuts

@router.get("/shortcuts", response_model=list[Shortcut])
async def list_shortcuts(
    scope: Optional[ShortcutScope] = Query(None),
    category: Optional[CommandCategory] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all keyboard shortcuts.

    Returns shortcuts filtered by scope and category, with user overrides applied.
    """
    user_id = getattr(request.state, "user_id", None)

    service = ShortcutsService(db)
    return await service.get_shortcuts(user_id, scope, category)


@router.get("/shortcuts/{shortcut_id}", response_model=Shortcut)
async def get_shortcut(
    shortcut_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single shortcut."""
    service = ShortcutsService(db)
    shortcut = await service.get_shortcut(shortcut_id)

    if not shortcut:
        raise HTTPException(status_code=404, detail="Shortcut not found")

    return shortcut


@router.post("/shortcuts", response_model=Shortcut)
async def create_custom_shortcut(
    name: str = Query(...),
    key: str = Query(..., description="Main key"),
    modifiers: str = Query("", description="Comma-separated modifiers: cmd,shift,alt,ctrl"),
    action_type: ActionType = Query(...),
    action_target: str = Query(...),
    category: CommandCategory = Query(CommandCategory.SYSTEM),
    scope: ShortcutScope = Query(ShortcutScope.GLOBAL),
    description: Optional[str] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a custom keyboard shortcut."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    import uuid
    mods = [m.strip() for m in modifiers.split(",") if m.strip()]

    shortcut = Shortcut(
        id=f"custom:{uuid.uuid4()}",
        name=name,
        description=description,
        category=category,
        key_binding=KeyBinding(key=key, modifiers=mods),
        action=ShortcutAction(action_type=action_type, target=action_target),
        scope=scope,
    )

    service = ShortcutsService(db)
    return await service.create_custom_shortcut(user_id, shortcut)


@router.put("/shortcuts/{shortcut_id}/override", response_model=Shortcut)
async def override_shortcut(
    shortcut_id: str,
    key: Optional[str] = Query(None),
    modifiers: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Override a shortcut's key binding or enabled state."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    key_binding = None
    if key:
        mods = [m.strip() for m in (modifiers or "").split(",") if m.strip()]
        key_binding = KeyBinding(key=key, modifiers=mods)

    override = ShortcutOverride(
        shortcut_id=shortcut_id,
        key_binding=key_binding,
        enabled=enabled,
    )

    service = ShortcutsService(db)
    result = await service.override_shortcut(user_id, override)

    if not result:
        raise HTTPException(status_code=404, detail="Shortcut not found")

    return result


@router.post("/shortcuts/{shortcut_id}/reset", response_model=Shortcut)
async def reset_shortcut(
    shortcut_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Reset a shortcut to its default."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ShortcutsService(db)
    result = await service.reset_shortcut(user_id, shortcut_id)

    if not result:
        raise HTTPException(status_code=404, detail="Shortcut not found")

    return result


@router.post("/shortcuts/reset-all")
async def reset_all_shortcuts(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Reset all shortcuts to defaults."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ShortcutsService(db)
    await service.reset_all_shortcuts(user_id)

    return {"reset": True}


@router.get("/shortcuts/categories")
async def get_shortcut_categories(
    db: AsyncSession = Depends(get_db),
):
    """Get all shortcut categories with counts."""
    service = ShortcutsService(db)
    return await service.get_shortcut_categories()


# Command Palette

@router.get("/commands", response_model=list[CommandGroup])
async def list_commands(
    category: Optional[CommandCategory] = Query(None),
    include_recent: bool = Query(True),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all commands for the command palette.

    Returns commands grouped by category.
    """
    user_id = getattr(request.state, "user_id", None)

    service = ShortcutsService(db)
    return await service.get_commands(user_id, category, include_recent)


@router.get("/commands/search", response_model=CommandSearchResponse)
async def search_commands(
    q: str = Query(..., min_length=1, description="Search query"),
    category: Optional[CommandCategory] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Search commands by query."""
    user_id = getattr(request.state, "user_id", None)

    service = ShortcutsService(db)
    return await service.search_commands(q, user_id, category, limit)


@router.post("/commands/{command_id}/execute")
async def execute_command(
    command_id: str,
    context: Optional[dict] = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Execute a command and record it in history."""
    user_id = getattr(request.state, "user_id", None)

    service = ShortcutsService(db)
    return await service.execute_command(command_id, user_id, context)


# Preferences

@router.get("/preferences", response_model=ShortcutPreferences)
async def get_preferences(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get user's shortcut preferences."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ShortcutsService(db)
    return await service.get_user_preferences(user_id)


@router.put("/preferences", response_model=ShortcutPreferences)
async def update_preferences(
    updates: dict,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update user's shortcut preferences."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ShortcutsService(db)
    return await service.update_user_preferences(user_id, updates)


# History

@router.get("/history", response_model=CommandHistory)
async def get_command_history(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get user's command history."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ShortcutsService(db)
    return await service.get_command_history(user_id)


@router.delete("/history")
async def clear_command_history(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Clear command history."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ShortcutsService(db)
    await service.clear_history(user_id)

    return {"cleared": True}


# Favorites

@router.post("/favorites/{command_id}")
async def add_favorite(
    command_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Add a command to favorites."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ShortcutsService(db)
    await service.add_favorite(user_id, command_id)

    return {"added": True}


@router.delete("/favorites/{command_id}")
async def remove_favorite(
    command_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Remove a command from favorites."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = ShortcutsService(db)
    await service.remove_favorite(user_id, command_id)

    return {"removed": True}
