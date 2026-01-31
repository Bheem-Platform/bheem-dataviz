"""
Global Search & Navigation Service

Business logic for unified search, recent items, favorites, and quick navigation.
"""

from typing import Optional
from datetime import datetime, timedelta
import re
from collections import defaultdict

from app.schemas.search import (
    ResourceType,
    SearchScope,
    SortField,
    SortOrder,
    SearchFilter,
    SearchQuery,
    SearchHighlight,
    SearchResult,
    SearchResponse,
    RecentItem,
    RecentItemsResponse,
    Favorite,
    FavoritesResponse,
    FavoriteCreate,
    FavoriteUpdate,
    NavigationItem,
    NavigationSection,
    QuickNavResponse,
    SearchSuggestion,
    SuggestionsResponse,
    IndexStatus,
    SearchIndexStatus,
    get_resource_url,
    get_resource_icon,
    highlight_text,
    calculate_relevance_score,
    MAX_RECENT_ITEMS,
    MAX_FAVORITES,
    MAX_SEARCH_RESULTS,
    RESOURCE_TYPE_ICONS,
    RESOURCE_TYPE_ROUTES,
)


class SearchService:
    """Service for global search and navigation."""

    def __init__(self, db=None):
        self.db = db

    # In-memory stores (production would use database + search engine)
    _search_index: dict[ResourceType, list[dict]] = defaultdict(list)
    _recent_items: dict[str, list[RecentItem]] = defaultdict(list)
    _favorites: dict[str, list[Favorite]] = defaultdict(list)
    _popular_queries: list[str] = []

    async def search(
        self,
        query: SearchQuery,
        user_id: Optional[str] = None,
    ) -> SearchResponse:
        """
        Perform global search across all resource types.
        """
        start_time = datetime.utcnow()
        results: list[SearchResult] = []
        facets: dict[str, list[dict]] = {"resource_types": []}

        # Determine which resource types to search
        resource_types = query.filters.resource_types or list(ResourceType)

        # Search each resource type
        for resource_type in resource_types:
            type_results = await self._search_resource_type(
                query.query,
                resource_type,
                query.filters,
                query.scope,
                user_id,
                query.include_content,
            )
            results.extend(type_results)

        # Calculate facets
        type_counts = defaultdict(int)
        for result in results:
            type_counts[result.resource_type] += 1

        facets["resource_types"] = [
            {"type": rt.value, "count": count}
            for rt, count in type_counts.items()
        ]

        # Sort results
        results = self._sort_results(results, query.sort_by, query.sort_order)

        # Get total before pagination
        total = len(results)

        # Apply pagination
        results = results[query.skip : query.skip + query.limit]

        # Generate suggestions
        suggestions = await self._generate_suggestions(query.query)

        # Calculate time taken
        took_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Track popular query
        self._track_popular_query(query.query)

        return SearchResponse(
            results=results,
            total=total,
            query=query.query,
            took_ms=took_ms,
            facets=facets,
            suggestions=suggestions[:5],
            has_more=total > query.skip + query.limit,
        )

    async def _search_resource_type(
        self,
        query: str,
        resource_type: ResourceType,
        filters: SearchFilter,
        scope: SearchScope,
        user_id: Optional[str],
        include_content: bool,
    ) -> list[SearchResult]:
        """Search within a specific resource type."""
        results = []

        # Get indexed documents for this type
        documents = self._search_index.get(resource_type, [])

        # Also include mock data for demonstration
        if not documents:
            documents = self._get_mock_documents(resource_type)

        for doc in documents:
            # Apply filters
            if not self._matches_filters(doc, filters, scope, user_id):
                continue

            # Calculate relevance
            score = calculate_relevance_score(
                query,
                doc.get("name", ""),
                doc.get("description", ""),
                doc.get("tags", []),
            )

            # Include content search if enabled
            if include_content and "content" in doc:
                if query.lower() in doc["content"].lower():
                    score += 15

            if score > 0:
                # Generate highlights
                highlights = self._generate_highlights(query, doc)

                # Check if favorite
                is_favorite = self._is_favorite(user_id, doc["id"]) if user_id else False

                result = SearchResult(
                    id=doc["id"],
                    resource_type=resource_type,
                    name=doc.get("name", ""),
                    description=doc.get("description"),
                    icon=get_resource_icon(resource_type),
                    url=get_resource_url(resource_type, doc["id"]),
                    thumbnail_url=doc.get("thumbnail_url"),
                    created_by=doc.get("created_by"),
                    created_by_name=doc.get("created_by_name"),
                    workspace_id=doc.get("workspace_id"),
                    workspace_name=doc.get("workspace_name"),
                    tags=doc.get("tags", []),
                    is_favorite=is_favorite,
                    is_shared=doc.get("is_shared", False),
                    view_count=doc.get("view_count", 0),
                    created_at=doc.get("created_at", datetime.utcnow()),
                    updated_at=doc.get("updated_at"),
                    last_viewed_at=doc.get("last_viewed_at"),
                    score=score,
                    highlights=highlights,
                    metadata=doc.get("metadata", {}),
                )
                results.append(result)

        return results

    def _matches_filters(
        self,
        doc: dict,
        filters: SearchFilter,
        scope: SearchScope,
        user_id: Optional[str],
    ) -> bool:
        """Check if document matches filters."""
        # Workspace filter
        if filters.workspace_ids:
            if doc.get("workspace_id") not in filters.workspace_ids:
                return False

        # Created by filter
        if filters.created_by:
            if doc.get("created_by") != filters.created_by:
                return False

        # Date filters
        created_at = doc.get("created_at")
        if created_at:
            if filters.created_after and created_at < filters.created_after:
                return False
            if filters.created_before and created_at > filters.created_before:
                return False

        updated_at = doc.get("updated_at")
        if updated_at:
            if filters.updated_after and updated_at < filters.updated_after:
                return False
            if filters.updated_before and updated_at > filters.updated_before:
                return False

        # Tags filter
        if filters.tags:
            doc_tags = set(doc.get("tags", []))
            if not doc_tags.intersection(filters.tags):
                return False

        # Favorite filter
        if filters.is_favorite is not None and user_id:
            is_fav = self._is_favorite(user_id, doc["id"])
            if is_fav != filters.is_favorite:
                return False

        # Scope filter
        if scope == SearchScope.OWNED and user_id:
            if doc.get("created_by") != user_id:
                return False
        elif scope == SearchScope.SHARED:
            if not doc.get("is_shared"):
                return False

        return True

    def _sort_results(
        self,
        results: list[SearchResult],
        sort_by: SortField,
        sort_order: SortOrder,
    ) -> list[SearchResult]:
        """Sort search results."""
        reverse = sort_order == SortOrder.DESC

        if sort_by == SortField.RELEVANCE:
            return sorted(results, key=lambda r: r.score, reverse=True)
        elif sort_by == SortField.NAME:
            return sorted(results, key=lambda r: r.name.lower(), reverse=reverse)
        elif sort_by == SortField.CREATED_AT:
            return sorted(results, key=lambda r: r.created_at, reverse=reverse)
        elif sort_by == SortField.UPDATED_AT:
            return sorted(
                results,
                key=lambda r: r.updated_at or r.created_at,
                reverse=reverse,
            )
        elif sort_by == SortField.VIEWED_AT:
            return sorted(
                results,
                key=lambda r: r.last_viewed_at or datetime.min,
                reverse=reverse,
            )
        elif sort_by == SortField.VIEW_COUNT:
            return sorted(results, key=lambda r: r.view_count, reverse=reverse)

        return results

    def _generate_highlights(
        self,
        query: str,
        doc: dict,
    ) -> list[SearchHighlight]:
        """Generate search highlights for a document."""
        highlights = []
        query_lower = query.lower()

        # Check name
        name = doc.get("name", "")
        if query_lower in name.lower():
            highlights.append(
                SearchHighlight(
                    field="name",
                    snippet=highlight_text(name, query),
                    positions=self._find_positions(name, query),
                )
            )

        # Check description
        desc = doc.get("description", "")
        if desc and query_lower in desc.lower():
            # Truncate to snippet
            idx = desc.lower().find(query_lower)
            start = max(0, idx - 50)
            end = min(len(desc), idx + len(query) + 50)
            snippet = ("..." if start > 0 else "") + desc[start:end] + ("..." if end < len(desc) else "")

            highlights.append(
                SearchHighlight(
                    field="description",
                    snippet=highlight_text(snippet, query),
                    positions=self._find_positions(desc, query),
                )
            )

        # Check tags
        for tag in doc.get("tags", []):
            if query_lower in tag.lower():
                highlights.append(
                    SearchHighlight(
                        field="tags",
                        snippet=highlight_text(tag, query),
                        positions=self._find_positions(tag, query),
                    )
                )
                break

        return highlights

    def _find_positions(self, text: str, query: str) -> list[tuple[int, int]]:
        """Find positions of query matches in text."""
        positions = []
        text_lower = text.lower()
        query_lower = query.lower()

        start = 0
        while True:
            idx = text_lower.find(query_lower, start)
            if idx == -1:
                break
            positions.append((idx, idx + len(query)))
            start = idx + 1

        return positions

    async def _generate_suggestions(self, query: str) -> list[str]:
        """Generate search suggestions based on query."""
        suggestions = []

        # Add popular queries that start with query
        for popular in self._popular_queries[:20]:
            if popular.lower().startswith(query.lower()) and popular != query:
                suggestions.append(popular)

        # Add resource type suggestions
        for rt in ResourceType:
            if query.lower() in rt.value.lower():
                suggestions.append(f"type:{rt.value}")

        return suggestions[:10]

    def _track_popular_query(self, query: str) -> None:
        """Track query for suggestions."""
        if query and len(query) >= 2:
            if query not in self._popular_queries:
                self._popular_queries.insert(0, query)
                self._popular_queries = self._popular_queries[:100]

    def _is_favorite(self, user_id: str, resource_id: str) -> bool:
        """Check if resource is favorited."""
        favorites = self._favorites.get(user_id, [])
        return any(f.resource_id == resource_id for f in favorites)

    def _get_mock_documents(self, resource_type: ResourceType) -> list[dict]:
        """Get mock documents for demonstration."""
        base_time = datetime.utcnow()

        mock_data = {
            ResourceType.DASHBOARD: [
                {
                    "id": "dash-001",
                    "name": "Sales Overview",
                    "description": "Comprehensive sales dashboard with KPIs",
                    "tags": ["sales", "kpi", "overview"],
                    "created_at": base_time - timedelta(days=30),
                    "updated_at": base_time - timedelta(days=1),
                    "view_count": 156,
                },
                {
                    "id": "dash-002",
                    "name": "Marketing Analytics",
                    "description": "Marketing campaign performance metrics",
                    "tags": ["marketing", "analytics"],
                    "created_at": base_time - timedelta(days=20),
                    "view_count": 89,
                },
            ],
            ResourceType.CHART: [
                {
                    "id": "chart-001",
                    "name": "Revenue Trend",
                    "description": "Monthly revenue trend line chart",
                    "tags": ["revenue", "trend"],
                    "created_at": base_time - timedelta(days=15),
                    "view_count": 234,
                },
                {
                    "id": "chart-002",
                    "name": "Customer Distribution",
                    "description": "Pie chart showing customer segments",
                    "tags": ["customers", "segments"],
                    "created_at": base_time - timedelta(days=10),
                    "view_count": 67,
                },
            ],
            ResourceType.CONNECTION: [
                {
                    "id": "conn-001",
                    "name": "Production Database",
                    "description": "PostgreSQL production database connection",
                    "tags": ["postgres", "production"],
                    "created_at": base_time - timedelta(days=60),
                    "view_count": 45,
                },
            ],
            ResourceType.DATASET: [
                {
                    "id": "ds-001",
                    "name": "Sales Data 2024",
                    "description": "Complete sales data for 2024",
                    "tags": ["sales", "2024"],
                    "created_at": base_time - timedelta(days=5),
                    "view_count": 123,
                },
            ],
        }

        return mock_data.get(resource_type, [])

    # Recent Items

    async def get_recent_items(
        self,
        user_id: str,
        resource_types: Optional[list[ResourceType]] = None,
        limit: int = 20,
    ) -> RecentItemsResponse:
        """Get user's recently accessed items."""
        items = self._recent_items.get(user_id, [])

        # Filter by resource type
        if resource_types:
            items = [i for i in items if i.resource_type in resource_types]

        # Sort by access time (most recent first)
        items = sorted(items, key=lambda i: i.accessed_at, reverse=True)

        # Apply limit
        items = items[:limit]

        return RecentItemsResponse(items=items, total=len(items))

    async def add_recent_item(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        name: str,
        action: str = "viewed",
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> RecentItem:
        """Add or update a recent item."""
        import uuid

        items = self._recent_items.get(user_id, [])

        # Check if item already exists
        existing = None
        for item in items:
            if item.resource_type == resource_type and item.resource_id == resource_id:
                existing = item
                break

        now = datetime.utcnow()

        if existing:
            # Update existing
            items.remove(existing)
            new_item = RecentItem(
                id=existing.id,
                resource_type=resource_type,
                resource_id=resource_id,
                name=name,
                description=description,
                icon=get_resource_icon(resource_type),
                url=get_resource_url(resource_type, resource_id),
                accessed_at=now,
                access_count=existing.access_count + 1,
                action=action,
                metadata=metadata or {},
            )
        else:
            # Create new
            new_item = RecentItem(
                id=str(uuid.uuid4()),
                resource_type=resource_type,
                resource_id=resource_id,
                name=name,
                description=description,
                icon=get_resource_icon(resource_type),
                url=get_resource_url(resource_type, resource_id),
                accessed_at=now,
                access_count=1,
                action=action,
                metadata=metadata or {},
            )

        # Add to front of list
        items.insert(0, new_item)

        # Trim to max size
        self._recent_items[user_id] = items[:MAX_RECENT_ITEMS]

        return new_item

    async def clear_recent_items(
        self,
        user_id: str,
        resource_type: Optional[ResourceType] = None,
    ) -> None:
        """Clear recent items."""
        if resource_type:
            items = self._recent_items.get(user_id, [])
            self._recent_items[user_id] = [
                i for i in items if i.resource_type != resource_type
            ]
        else:
            self._recent_items[user_id] = []

    # Favorites

    async def get_favorites(
        self,
        user_id: str,
        resource_type: Optional[ResourceType] = None,
        folder: Optional[str] = None,
    ) -> FavoritesResponse:
        """Get user's favorites."""
        favorites = self._favorites.get(user_id, [])

        # Filter by resource type
        if resource_type:
            favorites = [f for f in favorites if f.resource_type == resource_type]

        # Filter by folder
        if folder:
            favorites = [f for f in favorites if f.folder == folder]

        # Sort by display order
        favorites = sorted(favorites, key=lambda f: f.display_order)

        # Get unique folders
        all_favorites = self._favorites.get(user_id, [])
        folders = list(set(f.folder for f in all_favorites if f.folder))

        return FavoritesResponse(
            favorites=favorites,
            total=len(favorites),
            folders=folders,
        )

    async def add_favorite(
        self,
        user_id: str,
        data: FavoriteCreate,
        name: str,
        description: Optional[str] = None,
    ) -> Favorite:
        """Add a favorite."""
        import uuid

        favorites = self._favorites.get(user_id, [])

        # Check if already favorited
        for fav in favorites:
            if (
                fav.resource_type == data.resource_type
                and fav.resource_id == data.resource_id
            ):
                return fav

        # Get next display order
        max_order = max((f.display_order for f in favorites), default=-1)

        favorite = Favorite(
            id=str(uuid.uuid4()),
            user_id=user_id,
            resource_type=data.resource_type,
            resource_id=data.resource_id,
            name=name,
            description=description,
            icon=get_resource_icon(data.resource_type),
            url=get_resource_url(data.resource_type, data.resource_id),
            display_order=max_order + 1,
            folder=data.folder,
            notes=data.notes,
            added_at=datetime.utcnow(),
        )

        favorites.append(favorite)

        # Enforce max
        if len(favorites) > MAX_FAVORITES:
            favorites = favorites[:MAX_FAVORITES]

        self._favorites[user_id] = favorites

        return favorite

    async def update_favorite(
        self,
        user_id: str,
        favorite_id: str,
        data: FavoriteUpdate,
    ) -> Optional[Favorite]:
        """Update a favorite."""
        favorites = self._favorites.get(user_id, [])

        for i, fav in enumerate(favorites):
            if fav.id == favorite_id:
                updated = Favorite(
                    id=fav.id,
                    user_id=fav.user_id,
                    resource_type=fav.resource_type,
                    resource_id=fav.resource_id,
                    name=fav.name,
                    description=fav.description,
                    icon=fav.icon,
                    url=fav.url,
                    workspace_id=fav.workspace_id,
                    display_order=data.display_order if data.display_order is not None else fav.display_order,
                    folder=data.folder if data.folder is not None else fav.folder,
                    notes=data.notes if data.notes is not None else fav.notes,
                    added_at=fav.added_at,
                )
                favorites[i] = updated
                return updated

        return None

    async def remove_favorite(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
    ) -> bool:
        """Remove a favorite."""
        favorites = self._favorites.get(user_id, [])
        original_len = len(favorites)

        favorites = [
            f
            for f in favorites
            if not (f.resource_type == resource_type and f.resource_id == resource_id)
        ]

        self._favorites[user_id] = favorites

        return len(favorites) < original_len

    async def reorder_favorites(
        self,
        user_id: str,
        favorite_ids: list[str],
    ) -> list[Favorite]:
        """Reorder favorites."""
        favorites = self._favorites.get(user_id, [])
        favorites_by_id = {f.id: f for f in favorites}

        reordered = []
        for i, fid in enumerate(favorite_ids):
            if fid in favorites_by_id:
                fav = favorites_by_id[fid]
                updated = Favorite(
                    id=fav.id,
                    user_id=fav.user_id,
                    resource_type=fav.resource_type,
                    resource_id=fav.resource_id,
                    name=fav.name,
                    description=fav.description,
                    icon=fav.icon,
                    url=fav.url,
                    workspace_id=fav.workspace_id,
                    display_order=i,
                    folder=fav.folder,
                    notes=fav.notes,
                    added_at=fav.added_at,
                )
                reordered.append(updated)
                del favorites_by_id[fid]

        # Add remaining favorites
        for fav in favorites_by_id.values():
            reordered.append(fav)

        self._favorites[user_id] = reordered

        return reordered

    # Quick Navigation

    async def get_quick_nav(self, user_id: Optional[str] = None) -> QuickNavResponse:
        """Get quick navigation data."""
        # Build navigation sections
        sections = [
            NavigationSection(
                id="main",
                label="Main",
                items=[
                    NavigationItem(
                        id="nav-home",
                        label="Home",
                        icon="home",
                        url="/",
                        shortcut="G H",
                    ),
                    NavigationItem(
                        id="nav-dashboards",
                        label="Dashboards",
                        icon="layout-dashboard",
                        url="/dashboards",
                        shortcut="G D",
                    ),
                    NavigationItem(
                        id="nav-charts",
                        label="Charts",
                        icon="bar-chart",
                        url="/charts",
                        shortcut="G C",
                    ),
                    NavigationItem(
                        id="nav-datasets",
                        label="Datasets",
                        icon="table",
                        url="/datasets",
                        shortcut="G S",
                    ),
                ],
            ),
            NavigationSection(
                id="data",
                label="Data",
                items=[
                    NavigationItem(
                        id="nav-connections",
                        label="Connections",
                        icon="database",
                        url="/connections",
                    ),
                    NavigationItem(
                        id="nav-queries",
                        label="SQL Lab",
                        icon="code",
                        url="/sql-lab",
                        shortcut="G Q",
                    ),
                    NavigationItem(
                        id="nav-transforms",
                        label="Transforms",
                        icon="git-branch",
                        url="/transforms",
                    ),
                    NavigationItem(
                        id="nav-models",
                        label="Semantic Models",
                        icon="cube",
                        url="/models",
                    ),
                ],
            ),
            NavigationSection(
                id="analytics",
                label="Analytics",
                items=[
                    NavigationItem(
                        id="nav-kpis",
                        label="KPIs",
                        icon="trending-up",
                        url="/kpis",
                    ),
                    NavigationItem(
                        id="nav-reports",
                        label="Reports",
                        icon="file-text",
                        url="/reports",
                    ),
                    NavigationItem(
                        id="nav-insights",
                        label="Insights",
                        icon="lightbulb",
                        url="/insights",
                    ),
                ],
            ),
        ]

        # Get pinned items (favorites)
        pinned = []
        if user_id:
            favorites = await self.get_favorites(user_id)
            for fav in favorites.favorites[:5]:
                pinned.append(
                    NavigationItem(
                        id=f"pinned-{fav.id}",
                        label=fav.name,
                        icon=fav.icon,
                        url=fav.url,
                    )
                )

        # Get recent items
        recent = []
        if user_id:
            recent_items = await self.get_recent_items(user_id, limit=5)
            for item in recent_items.items:
                recent.append(
                    NavigationItem(
                        id=f"recent-{item.id}",
                        label=item.name,
                        icon=item.icon,
                        url=item.url,
                    )
                )

        return QuickNavResponse(
            sections=sections,
            pinned=pinned,
            recent=recent,
        )

    # Suggestions

    async def get_suggestions(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> SuggestionsResponse:
        """Get autocomplete suggestions."""
        suggestions = []

        if len(query) < 1:
            return SuggestionsResponse(suggestions=[], query=query)

        query_lower = query.lower()

        # Search in indexed resources
        for resource_type in ResourceType:
            docs = self._search_index.get(resource_type, [])
            docs = docs or self._get_mock_documents(resource_type)

            for doc in docs:
                name = doc.get("name", "")
                if query_lower in name.lower():
                    suggestions.append(
                        SearchSuggestion(
                            text=name,
                            type="resource",
                            icon=get_resource_icon(resource_type),
                            url=get_resource_url(resource_type, doc["id"]),
                            metadata={"resource_type": resource_type.value},
                        )
                    )

                    if len(suggestions) >= limit:
                        break

            if len(suggestions) >= limit:
                break

        # Add query suggestions
        for popular in self._popular_queries[:10]:
            if query_lower in popular.lower() and popular != query:
                suggestions.append(
                    SearchSuggestion(
                        text=popular,
                        type="query",
                        icon="search",
                    )
                )

        return SuggestionsResponse(
            suggestions=suggestions[:limit],
            query=query,
        )

    # Index Management

    async def index_resource(
        self,
        resource_type: ResourceType,
        resource_id: str,
        data: dict,
    ) -> None:
        """Add or update a resource in the search index."""
        docs = self._search_index[resource_type]

        # Remove existing
        docs = [d for d in docs if d.get("id") != resource_id]

        # Add new
        data["id"] = resource_id
        docs.append(data)

        self._search_index[resource_type] = docs

    async def remove_from_index(
        self,
        resource_type: ResourceType,
        resource_id: str,
    ) -> None:
        """Remove a resource from the search index."""
        docs = self._search_index[resource_type]
        self._search_index[resource_type] = [
            d for d in docs if d.get("id") != resource_id
        ]

    async def get_index_status(self) -> SearchIndexStatus:
        """Get search index status."""
        indices = []
        total_docs = 0

        for resource_type in ResourceType:
            docs = self._search_index.get(resource_type, [])
            count = len(docs)
            total_docs += count

            indices.append(
                IndexStatus(
                    resource_type=resource_type,
                    total_documents=count,
                    last_indexed_at=datetime.utcnow() if count > 0 else None,
                    is_indexing=False,
                    errors=0,
                )
            )

        return SearchIndexStatus(
            indices=indices,
            total_documents=total_docs,
            last_full_reindex=datetime.utcnow() - timedelta(hours=1),
            is_healthy=True,
        )

    async def reindex_all(self) -> None:
        """Trigger full reindex (placeholder for production implementation)."""
        # In production, this would trigger a background job
        # to reindex all resources from the database
        pass
