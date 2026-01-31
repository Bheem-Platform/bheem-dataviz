"""
Plugin Management API Endpoints

REST API for plugin lifecycle, registry, and hook management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.plugin_service import PluginService
from app.schemas.plugins import (
    PluginType,
    PluginStatus,
    HookType,
    PluginInstance,
    PluginInstall,
    PluginUpdate,
    RegistryPlugin,
    RegistrySearchResult,
    RegistrySearchQuery,
    HookContext,
    HookChainResult,
    PluginListResponse,
    PluginStatsResponse,
    PluginEvent,
)

router = APIRouter()


# Installed Plugins

@router.get("/installed", response_model=PluginListResponse)
async def list_installed_plugins(
    workspace_id: Optional[str] = Query(None),
    plugin_type: Optional[PluginType] = Query(None),
    status: Optional[PluginStatus] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all installed plugins.

    Optionally filter by workspace, type, or status.
    """
    service = PluginService(db)
    return await service.list_plugins(workspace_id, plugin_type, status)


@router.get("/installed/{plugin_id}", response_model=PluginInstance)
async def get_installed_plugin(
    plugin_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get details of an installed plugin."""
    service = PluginService(db)
    plugin = await service.get_plugin(plugin_id)

    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return plugin


@router.post("/install", response_model=PluginInstance)
async def install_plugin(
    data: PluginInstall,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Install a plugin from the registry.

    The plugin will be enabled automatically unless enable_after_install is false.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = PluginService(db)
    try:
        return await service.install_plugin(user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/installed/{plugin_id}")
async def uninstall_plugin(
    plugin_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Uninstall a plugin."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = PluginService(db)
    success = await service.uninstall_plugin(plugin_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return {"uninstalled": True}


@router.post("/installed/{plugin_id}/enable", response_model=PluginInstance)
async def enable_plugin(
    plugin_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Enable an installed plugin."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = PluginService(db)
    try:
        return await service.enable_plugin(plugin_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable plugin: {str(e)}")


@router.post("/installed/{plugin_id}/disable", response_model=PluginInstance)
async def disable_plugin(
    plugin_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Disable a plugin."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = PluginService(db)
    try:
        return await service.disable_plugin(plugin_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/installed/{plugin_id}", response_model=PluginInstance)
async def update_plugin_config(
    plugin_id: str,
    data: PluginUpdate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update plugin configuration."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = PluginService(db)
    try:
        return await service.update_plugin(plugin_id, user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/installed/{plugin_id}/update-version", response_model=PluginInstance)
async def update_plugin_version(
    plugin_id: str,
    version: Optional[str] = Query(None, description="Target version (null = latest)"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update plugin to a new version."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = PluginService(db)
    try:
        return await service.update_plugin_version(plugin_id, user_id, version)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Registry

@router.get("/registry", response_model=RegistrySearchResult)
async def search_registry(
    q: Optional[str] = Query(None, description="Search query"),
    type: Optional[PluginType] = Query(None),
    keywords: Optional[str] = Query(None, description="Comma-separated keywords"),
    verified_only: bool = Query(False),
    sort_by: str = Query("downloads", description="downloads, rating, updated, name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Search the plugin registry.

    Returns paginated list of available plugins.
    """
    keyword_list = []
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

    query = RegistrySearchQuery(
        query=q,
        type=type,
        keywords=keyword_list,
        verified_only=verified_only,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )

    service = PluginService(db)
    return await service.search_registry(query)


@router.get("/registry/{plugin_id}", response_model=RegistryPlugin)
async def get_registry_plugin(
    plugin_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get plugin details from the registry."""
    service = PluginService(db)
    plugin = await service.get_registry_plugin(plugin_id)

    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found in registry")

    return plugin


@router.get("/registry/featured", response_model=list[RegistryPlugin])
async def get_featured_plugins(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Get featured plugins from the registry."""
    service = PluginService(db)
    return await service.get_featured_plugins(limit)


# Statistics & Updates

@router.get("/stats", response_model=PluginStatsResponse)
async def get_plugin_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get plugin statistics."""
    service = PluginService(db)
    return await service.get_plugin_stats()


@router.get("/updates")
async def check_for_updates(
    db: AsyncSession = Depends(get_db),
):
    """Check for available plugin updates."""
    service = PluginService(db)
    updates = await service.check_updates()

    return {
        "updates_available": len(updates),
        "plugins": updates,
    }


# Events

@router.get("/events", response_model=list[PluginEvent])
async def get_plugin_events(
    plugin_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get plugin events/audit log."""
    service = PluginService(db)
    return await service.get_plugin_events(plugin_id, limit)


# Hooks (Admin/Debug)

@router.post("/hooks/execute", response_model=HookChainResult)
async def execute_hooks(
    hook_type: HookType = Query(...),
    data: dict = Body(default={}),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Execute hooks of a specific type.

    This is primarily for testing and debugging.
    """
    user_id = getattr(request.state, "user_id", None)

    context = HookContext(
        hook_type=hook_type,
        plugin_id="system",
        user_id=user_id,
        data=data,
    )

    service = PluginService(db)
    return await service.execute_hooks(hook_type, context)


@router.get("/hooks")
async def list_registered_hooks(
    db: AsyncSession = Depends(get_db),
):
    """List all registered hooks by type."""
    service = PluginService(db)

    hooks_info = {}
    for hook_type in HookType:
        hooks = service._hooks.get(hook_type, [])
        hooks_info[hook_type.value] = [
            {"plugin_id": h[0], "priority": h[2]}
            for h in hooks
        ]

    return {
        "hooks": hooks_info,
        "total": sum(len(h) for h in hooks_info.values()),
    }


# Plugin Types

@router.get("/types")
async def get_plugin_types():
    """Get available plugin types with descriptions."""
    from app.schemas.plugins import PLUGIN_TYPE_LABELS, PLUGIN_TYPE_ICONS

    return {
        "types": [
            {
                "id": t.value,
                "label": PLUGIN_TYPE_LABELS[t],
                "icon": PLUGIN_TYPE_ICONS[t],
            }
            for t in PluginType
        ]
    }


# Bulk Operations

@router.post("/bulk/enable")
async def bulk_enable_plugins(
    plugin_ids: list[str] = Body(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Enable multiple plugins."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = PluginService(db)
    results = []

    for plugin_id in plugin_ids:
        try:
            await service.enable_plugin(plugin_id, user_id)
            results.append({"plugin_id": plugin_id, "success": True})
        except Exception as e:
            results.append({"plugin_id": plugin_id, "success": False, "error": str(e)})

    return {"results": results}


@router.post("/bulk/disable")
async def bulk_disable_plugins(
    plugin_ids: list[str] = Body(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Disable multiple plugins."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = PluginService(db)
    results = []

    for plugin_id in plugin_ids:
        try:
            await service.disable_plugin(plugin_id, user_id)
            results.append({"plugin_id": plugin_id, "success": True})
        except Exception as e:
            results.append({"plugin_id": plugin_id, "success": False, "error": str(e)})

    return {"results": results}
