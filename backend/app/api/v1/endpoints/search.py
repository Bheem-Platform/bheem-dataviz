"""
Global Search & Navigation API Endpoints

REST API for unified search, recent items, favorites, and quick navigation.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.search_service import SearchService
from app.schemas.search import (
    ResourceType,
    SearchScope,
    SortField,
    SortOrder,
    SearchFilter,
    SearchQuery,
    SearchResponse,
    RecentItem,
    RecentItemsResponse,
    Favorite,
    FavoritesResponse,
    FavoriteCreate,
    FavoriteUpdate,
    QuickNavResponse,
    SuggestionsResponse,
    SearchIndexStatus,
)

router = APIRouter()


# Search

@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    types: Optional[str] = Query(None, description="Comma-separated resource types"),
    scope: SearchScope = Query(SearchScope.ALL),
    sort_by: SortField = Query(SortField.RELEVANCE),
    sort_order: SortOrder = Query(SortOrder.DESC),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_content: bool = Query(False),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    workspace_id: Optional[str] = Query(None),
    created_by: Optional[str] = Query(None),
    is_favorite: Optional[bool] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Global search across all resource types.

    Searches dashboards, charts, connections, datasets, queries, and more.
    Supports filtering, sorting, and pagination.
    """
    user_id = getattr(request.state, "user_id", None)

    # Parse resource types
    resource_types = []
    if types:
        for t in types.split(","):
            t = t.strip().lower()
            try:
                resource_types.append(ResourceType(t))
            except ValueError:
                pass

    # Parse tags
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    # Build filter
    filters = SearchFilter(
        resource_types=resource_types,
        workspace_ids=[workspace_id] if workspace_id else [],
        created_by=created_by,
        tags=tag_list,
        is_favorite=is_favorite,
    )

    # Build query
    query = SearchQuery(
        query=q,
        filters=filters,
        scope=scope,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
        include_content=include_content,
    )

    service = SearchService(db)
    return await service.search(query, user_id)


@router.post("/search", response_model=SearchResponse)
async def search_advanced(
    query: SearchQuery = Body(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Advanced search with full query object.

    Allows complex filtering with date ranges and multiple workspaces.
    """
    user_id = getattr(request.state, "user_id", None)

    service = SearchService(db)
    return await service.search(query, user_id)


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    q: str = Query(..., min_length=1, description="Query prefix"),
    limit: int = Query(10, ge=1, le=20),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get autocomplete suggestions for search.

    Returns matching resources and query suggestions.
    """
    user_id = getattr(request.state, "user_id", None)

    service = SearchService(db)
    return await service.get_suggestions(q, user_id, limit)


# Recent Items

@router.get("/recent", response_model=RecentItemsResponse)
async def get_recent_items(
    types: Optional[str] = Query(None, description="Comma-separated resource types"),
    limit: int = Query(20, ge=1, le=50),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's recently accessed items.

    Returns items sorted by most recently accessed.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    # Parse resource types
    resource_types = None
    if types:
        resource_types = []
        for t in types.split(","):
            t = t.strip().lower()
            try:
                resource_types.append(ResourceType(t))
            except ValueError:
                pass

    service = SearchService(db)
    return await service.get_recent_items(user_id, resource_types, limit)


@router.post("/recent", response_model=RecentItem)
async def add_recent_item(
    resource_type: ResourceType = Query(...),
    resource_id: str = Query(...),
    name: str = Query(...),
    action: str = Query("viewed"),
    description: Optional[str] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Add or update a recent item.

    Called when user views, edits, or creates a resource.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SearchService(db)
    return await service.add_recent_item(
        user_id, resource_type, resource_id, name, action, description
    )


@router.delete("/recent")
async def clear_recent_items(
    resource_type: Optional[ResourceType] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Clear recent items.

    Optionally filter by resource type.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SearchService(db)
    await service.clear_recent_items(user_id, resource_type)

    return {"cleared": True}


# Favorites

@router.get("/favorites", response_model=FavoritesResponse)
async def get_favorites(
    resource_type: Optional[ResourceType] = Query(None),
    folder: Optional[str] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's favorites.

    Optionally filter by resource type or folder.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SearchService(db)
    return await service.get_favorites(user_id, resource_type, folder)


@router.post("/favorites", response_model=Favorite)
async def add_favorite(
    resource_type: ResourceType = Query(...),
    resource_id: str = Query(...),
    name: str = Query(...),
    description: Optional[str] = Query(None),
    folder: Optional[str] = Query(None),
    notes: Optional[str] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Add a resource to favorites."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    data = FavoriteCreate(
        resource_type=resource_type,
        resource_id=resource_id,
        folder=folder,
        notes=notes,
    )

    service = SearchService(db)
    return await service.add_favorite(user_id, data, name, description)


@router.put("/favorites/{favorite_id}", response_model=Favorite)
async def update_favorite(
    favorite_id: str,
    folder: Optional[str] = Query(None),
    notes: Optional[str] = Query(None),
    display_order: Optional[int] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update a favorite's metadata."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    data = FavoriteUpdate(
        folder=folder,
        notes=notes,
        display_order=display_order,
    )

    service = SearchService(db)
    result = await service.update_favorite(user_id, favorite_id, data)

    if not result:
        raise HTTPException(status_code=404, detail="Favorite not found")

    return result


@router.delete("/favorites")
async def remove_favorite(
    resource_type: ResourceType = Query(...),
    resource_id: str = Query(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Remove a resource from favorites."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SearchService(db)
    removed = await service.remove_favorite(user_id, resource_type, resource_id)

    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")

    return {"removed": True}


@router.put("/favorites/reorder", response_model=list[Favorite])
async def reorder_favorites(
    favorite_ids: list[str] = Body(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Reorder favorites."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SearchService(db)
    return await service.reorder_favorites(user_id, favorite_ids)


# Quick Navigation

@router.get("/nav", response_model=QuickNavResponse)
async def get_quick_nav(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get quick navigation data.

    Returns navigation sections, pinned items, and recent items.
    """
    user_id = getattr(request.state, "user_id", None)

    service = SearchService(db)
    return await service.get_quick_nav(user_id)


# Index Management (Admin)

@router.get("/index/status", response_model=SearchIndexStatus)
async def get_index_status(
    db: AsyncSession = Depends(get_db),
):
    """Get search index status."""
    service = SearchService(db)
    return await service.get_index_status()


@router.post("/index/resource")
async def index_resource(
    resource_type: ResourceType = Query(...),
    resource_id: str = Query(...),
    data: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Index a resource for search."""
    service = SearchService(db)
    await service.index_resource(resource_type, resource_id, data)

    return {"indexed": True}


@router.delete("/index/resource")
async def remove_from_index(
    resource_type: ResourceType = Query(...),
    resource_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Remove a resource from the search index."""
    service = SearchService(db)
    await service.remove_from_index(resource_type, resource_id)

    return {"removed": True}


@router.post("/index/reindex")
async def reindex_all(
    db: AsyncSession = Depends(get_db),
):
    """Trigger full reindex of all resources."""
    service = SearchService(db)
    await service.reindex_all()

    return {"reindex": "started"}
