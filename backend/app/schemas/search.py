"""
Global Search & Navigation Schemas

Pydantic schemas for unified search, recent items, and quick navigation.
"""

from typing import Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class ResourceType(str, Enum):
    """Types of searchable resources"""
    DASHBOARD = "dashboard"
    CHART = "chart"
    CONNECTION = "connection"
    DATASET = "dataset"
    QUERY = "query"
    TRANSFORM = "transform"
    SEMANTIC_MODEL = "semantic_model"
    KPI = "kpi"
    REPORT = "report"
    USER = "user"
    WORKSPACE = "workspace"


class SearchScope(str, Enum):
    """Search scope"""
    ALL = "all"
    OWNED = "owned"  # Created by user
    SHARED = "shared"  # Shared with user
    WORKSPACE = "workspace"  # Within workspace


class SortField(str, Enum):
    """Fields to sort by"""
    RELEVANCE = "relevance"
    NAME = "name"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    VIEWED_AT = "viewed_at"
    VIEW_COUNT = "view_count"


class SortOrder(str, Enum):
    """Sort order"""
    ASC = "asc"
    DESC = "desc"


# Search Models

class SearchFilter(BaseModel):
    """Filter for search queries"""
    resource_types: list[ResourceType] = Field(default_factory=list)
    workspace_ids: list[str] = Field(default_factory=list)
    created_by: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)
    is_favorite: Optional[bool] = None


class SearchQuery(BaseModel):
    """Search query parameters"""
    query: str = Field(..., min_length=1, max_length=500)
    filters: SearchFilter = Field(default_factory=SearchFilter)
    scope: SearchScope = SearchScope.ALL
    sort_by: SortField = SortField.RELEVANCE
    sort_order: SortOrder = SortOrder.DESC
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    include_content: bool = False  # Search in content/SQL too


class SearchHighlight(BaseModel):
    """Highlighted match in search result"""
    field: str  # name, description, tags, etc.
    snippet: str  # Text with highlights
    positions: list[tuple[int, int]] = Field(default_factory=list)  # Start, end positions


class SearchResult(BaseModel):
    """Single search result"""
    id: str
    resource_type: ResourceType
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    url: str  # Navigation URL
    thumbnail_url: Optional[str] = None

    # Ownership
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None

    # Metadata
    tags: list[str] = Field(default_factory=list)
    is_favorite: bool = False
    is_shared: bool = False
    view_count: int = 0

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_viewed_at: Optional[datetime] = None

    # Search relevance
    score: float = 0
    highlights: list[SearchHighlight] = Field(default_factory=list)

    # Additional context
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Search response with results and metadata"""
    results: list[SearchResult]
    total: int
    query: str
    took_ms: int
    facets: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)  # Resource type counts, etc.
    suggestions: list[str] = Field(default_factory=list)
    has_more: bool = False


# Recent Items Models

class RecentItem(BaseModel):
    """Recently accessed item"""
    id: str
    resource_type: ResourceType
    resource_id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    url: str
    thumbnail_url: Optional[str] = None

    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None

    accessed_at: datetime
    access_count: int = 1
    action: str = "viewed"  # viewed, edited, created

    metadata: dict[str, Any] = Field(default_factory=dict)


class RecentItemsResponse(BaseModel):
    """List of recent items"""
    items: list[RecentItem]
    total: int


# Favorites Models

class Favorite(BaseModel):
    """Favorite item"""
    id: str
    user_id: str
    resource_type: ResourceType
    resource_id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    url: str

    workspace_id: Optional[str] = None
    display_order: int = 0  # For custom ordering
    folder: Optional[str] = None  # Optional folder/category
    notes: Optional[str] = None  # User notes

    added_at: datetime


class FavoritesResponse(BaseModel):
    """List of favorites"""
    favorites: list[Favorite]
    total: int
    folders: list[str] = Field(default_factory=list)


class FavoriteCreate(BaseModel):
    """Create a favorite"""
    resource_type: ResourceType
    resource_id: str
    folder: Optional[str] = None
    notes: Optional[str] = None


class FavoriteUpdate(BaseModel):
    """Update a favorite"""
    folder: Optional[str] = None
    notes: Optional[str] = None
    display_order: Optional[int] = None


# Quick Navigation Models

class NavigationItem(BaseModel):
    """Navigation item for quick access"""
    id: str
    label: str
    icon: Optional[str] = None
    url: str
    shortcut: Optional[str] = None  # Keyboard shortcut hint
    badge: Optional[str] = None  # Badge text (e.g., count)
    children: list["NavigationItem"] = Field(default_factory=list)
    is_active: bool = False
    is_expanded: bool = False


class NavigationSection(BaseModel):
    """Section of navigation items"""
    id: str
    label: str
    items: list[NavigationItem]
    collapsible: bool = True
    is_collapsed: bool = False


class QuickNavResponse(BaseModel):
    """Quick navigation data"""
    sections: list[NavigationSection]
    pinned: list[NavigationItem]  # Pinned items
    recent: list[NavigationItem]  # Recent items for quick access


# Suggestions Models

class SearchSuggestion(BaseModel):
    """Autocomplete suggestion"""
    text: str
    type: str  # query, resource, tag, user
    icon: Optional[str] = None
    url: Optional[str] = None  # If direct navigation
    metadata: dict[str, Any] = Field(default_factory=dict)


class SuggestionsResponse(BaseModel):
    """Autocomplete suggestions response"""
    suggestions: list[SearchSuggestion]
    query: str


# Index Status Models

class IndexStatus(BaseModel):
    """Search index status"""
    resource_type: ResourceType
    total_documents: int
    last_indexed_at: Optional[datetime] = None
    is_indexing: bool = False
    errors: int = 0


class SearchIndexStatus(BaseModel):
    """Overall search index status"""
    indices: list[IndexStatus]
    total_documents: int
    last_full_reindex: Optional[datetime] = None
    is_healthy: bool = True


# Constants

RESOURCE_TYPE_ICONS: dict[ResourceType, str] = {
    ResourceType.DASHBOARD: "layout-dashboard",
    ResourceType.CHART: "bar-chart",
    ResourceType.CONNECTION: "database",
    ResourceType.DATASET: "table",
    ResourceType.QUERY: "code",
    ResourceType.TRANSFORM: "git-branch",
    ResourceType.SEMANTIC_MODEL: "cube",
    ResourceType.KPI: "trending-up",
    ResourceType.REPORT: "file-text",
    ResourceType.USER: "user",
    ResourceType.WORKSPACE: "folder",
}

RESOURCE_TYPE_ROUTES: dict[ResourceType, str] = {
    ResourceType.DASHBOARD: "/dashboards",
    ResourceType.CHART: "/charts",
    ResourceType.CONNECTION: "/connections",
    ResourceType.DATASET: "/datasets",
    ResourceType.QUERY: "/sql-lab",
    ResourceType.TRANSFORM: "/transforms",
    ResourceType.SEMANTIC_MODEL: "/models",
    ResourceType.KPI: "/kpis",
    ResourceType.REPORT: "/reports",
    ResourceType.USER: "/users",
    ResourceType.WORKSPACE: "/workspaces",
}

MAX_RECENT_ITEMS = 50
MAX_FAVORITES = 100
MAX_SEARCH_RESULTS = 100


# Helper Functions

def get_resource_url(resource_type: ResourceType, resource_id: str) -> str:
    """Build URL for a resource"""
    base = RESOURCE_TYPE_ROUTES.get(resource_type, "")
    return f"{base}/{resource_id}"


def get_resource_icon(resource_type: ResourceType) -> str:
    """Get icon for a resource type"""
    return RESOURCE_TYPE_ICONS.get(resource_type, "file")


def highlight_text(text: str, query: str) -> str:
    """Add highlight markers to text"""
    if not query or not text:
        return text

    import re
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark>{m.group()}</mark>", text)


def calculate_relevance_score(
    query: str,
    name: str,
    description: str = "",
    tags: list[str] = None,
) -> float:
    """Calculate relevance score for a search result"""
    query_lower = query.lower()
    score = 0.0

    # Exact name match
    if name.lower() == query_lower:
        score += 100

    # Name starts with query
    elif name.lower().startswith(query_lower):
        score += 75

    # Name contains query
    elif query_lower in name.lower():
        score += 50

    # Description contains query
    if description and query_lower in description.lower():
        score += 20

    # Tags contain query
    if tags:
        for tag in tags:
            if query_lower in tag.lower():
                score += 10
                break

    return score
