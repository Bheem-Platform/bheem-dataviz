/**
 * Global Search & Navigation Types
 *
 * TypeScript types for unified search, recent items, favorites, and quick navigation.
 */

// Enums

export enum ResourceType {
  DASHBOARD = 'dashboard',
  CHART = 'chart',
  CONNECTION = 'connection',
  DATASET = 'dataset',
  QUERY = 'query',
  TRANSFORM = 'transform',
  SEMANTIC_MODEL = 'semantic_model',
  KPI = 'kpi',
  REPORT = 'report',
  USER = 'user',
  WORKSPACE = 'workspace',
}

export enum SearchScope {
  ALL = 'all',
  OWNED = 'owned',
  SHARED = 'shared',
  WORKSPACE = 'workspace',
}

export enum SortField {
  RELEVANCE = 'relevance',
  NAME = 'name',
  CREATED_AT = 'created_at',
  UPDATED_AT = 'updated_at',
  VIEWED_AT = 'viewed_at',
  VIEW_COUNT = 'view_count',
}

export enum SortOrder {
  ASC = 'asc',
  DESC = 'desc',
}

// Search Types

export interface SearchFilter {
  resource_types: ResourceType[];
  workspace_ids: string[];
  created_by?: string | null;
  created_after?: string | null;
  created_before?: string | null;
  updated_after?: string | null;
  updated_before?: string | null;
  tags: string[];
  is_favorite?: boolean | null;
}

export interface SearchQuery {
  query: string;
  filters: SearchFilter;
  scope: SearchScope;
  sort_by: SortField;
  sort_order: SortOrder;
  skip: number;
  limit: number;
  include_content: boolean;
}

export interface SearchHighlight {
  field: string;
  snippet: string;
  positions: [number, number][];
}

export interface SearchResult {
  id: string;
  resource_type: ResourceType;
  name: string;
  description?: string | null;
  icon?: string | null;
  url: string;
  thumbnail_url?: string | null;
  created_by?: string | null;
  created_by_name?: string | null;
  workspace_id?: string | null;
  workspace_name?: string | null;
  tags: string[];
  is_favorite: boolean;
  is_shared: boolean;
  view_count: number;
  created_at: string;
  updated_at?: string | null;
  last_viewed_at?: string | null;
  score: number;
  highlights: SearchHighlight[];
  metadata: Record<string, unknown>;
}

export interface SearchFacet {
  type: string;
  count: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  took_ms: number;
  facets: {
    resource_types: SearchFacet[];
    [key: string]: unknown[];
  };
  suggestions: string[];
  has_more: boolean;
}

// Recent Items Types

export interface RecentItem {
  id: string;
  resource_type: ResourceType;
  resource_id: string;
  name: string;
  description?: string | null;
  icon?: string | null;
  url: string;
  thumbnail_url?: string | null;
  workspace_id?: string | null;
  workspace_name?: string | null;
  accessed_at: string;
  access_count: number;
  action: string;
  metadata: Record<string, unknown>;
}

export interface RecentItemsResponse {
  items: RecentItem[];
  total: number;
}

// Favorites Types

export interface Favorite {
  id: string;
  user_id: string;
  resource_type: ResourceType;
  resource_id: string;
  name: string;
  description?: string | null;
  icon?: string | null;
  url: string;
  workspace_id?: string | null;
  display_order: number;
  folder?: string | null;
  notes?: string | null;
  added_at: string;
}

export interface FavoritesResponse {
  favorites: Favorite[];
  total: number;
  folders: string[];
}

export interface FavoriteCreate {
  resource_type: ResourceType;
  resource_id: string;
  folder?: string | null;
  notes?: string | null;
}

export interface FavoriteUpdate {
  folder?: string | null;
  notes?: string | null;
  display_order?: number | null;
}

// Navigation Types

export interface NavigationItem {
  id: string;
  label: string;
  icon?: string | null;
  url: string;
  shortcut?: string | null;
  badge?: string | null;
  children: NavigationItem[];
  is_active: boolean;
  is_expanded: boolean;
}

export interface NavigationSection {
  id: string;
  label: string;
  items: NavigationItem[];
  collapsible: boolean;
  is_collapsed: boolean;
}

export interface QuickNavResponse {
  sections: NavigationSection[];
  pinned: NavigationItem[];
  recent: NavigationItem[];
}

// Suggestions Types

export interface SearchSuggestion {
  text: string;
  type: string;
  icon?: string | null;
  url?: string | null;
  metadata: Record<string, unknown>;
}

export interface SuggestionsResponse {
  suggestions: SearchSuggestion[];
  query: string;
}

// Index Types

export interface IndexStatus {
  resource_type: ResourceType;
  total_documents: number;
  last_indexed_at?: string | null;
  is_indexing: boolean;
  errors: number;
}

export interface SearchIndexStatus {
  indices: IndexStatus[];
  total_documents: number;
  last_full_reindex?: string | null;
  is_healthy: boolean;
}

// Constants

export const RESOURCE_TYPE_LABELS: Record<ResourceType, string> = {
  [ResourceType.DASHBOARD]: 'Dashboard',
  [ResourceType.CHART]: 'Chart',
  [ResourceType.CONNECTION]: 'Connection',
  [ResourceType.DATASET]: 'Dataset',
  [ResourceType.QUERY]: 'Query',
  [ResourceType.TRANSFORM]: 'Transform',
  [ResourceType.SEMANTIC_MODEL]: 'Semantic Model',
  [ResourceType.KPI]: 'KPI',
  [ResourceType.REPORT]: 'Report',
  [ResourceType.USER]: 'User',
  [ResourceType.WORKSPACE]: 'Workspace',
};

export const RESOURCE_TYPE_ICONS: Record<ResourceType, string> = {
  [ResourceType.DASHBOARD]: 'layout-dashboard',
  [ResourceType.CHART]: 'bar-chart',
  [ResourceType.CONNECTION]: 'database',
  [ResourceType.DATASET]: 'table',
  [ResourceType.QUERY]: 'code',
  [ResourceType.TRANSFORM]: 'git-branch',
  [ResourceType.SEMANTIC_MODEL]: 'cube',
  [ResourceType.KPI]: 'trending-up',
  [ResourceType.REPORT]: 'file-text',
  [ResourceType.USER]: 'user',
  [ResourceType.WORKSPACE]: 'folder',
};

export const RESOURCE_TYPE_COLORS: Record<ResourceType, string> = {
  [ResourceType.DASHBOARD]: 'blue',
  [ResourceType.CHART]: 'green',
  [ResourceType.CONNECTION]: 'purple',
  [ResourceType.DATASET]: 'orange',
  [ResourceType.QUERY]: 'cyan',
  [ResourceType.TRANSFORM]: 'pink',
  [ResourceType.SEMANTIC_MODEL]: 'indigo',
  [ResourceType.KPI]: 'red',
  [ResourceType.REPORT]: 'gray',
  [ResourceType.USER]: 'teal',
  [ResourceType.WORKSPACE]: 'yellow',
};

// Helper Functions

export function getResourceLabel(type: ResourceType): string {
  return RESOURCE_TYPE_LABELS[type] || type;
}

export function getResourceIcon(type: ResourceType): string {
  return RESOURCE_TYPE_ICONS[type] || 'file';
}

export function getResourceColor(type: ResourceType): string {
  return RESOURCE_TYPE_COLORS[type] || 'gray';
}

export function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const weeks = Math.floor(days / 7);
  const months = Math.floor(days / 30);

  if (months > 0) return `${months}mo ago`;
  if (weeks > 0) return `${weeks}w ago`;
  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return 'Just now';
}

export function highlightMatches(text: string, positions: [number, number][]): string {
  if (!positions.length) return text;

  let result = '';
  let lastEnd = 0;

  for (const [start, end] of positions) {
    result += text.slice(lastEnd, start);
    result += `<mark>${text.slice(start, end)}</mark>`;
    lastEnd = end;
  }

  result += text.slice(lastEnd);
  return result;
}

export function createDefaultFilter(): SearchFilter {
  return {
    resource_types: [],
    workspace_ids: [],
    created_by: null,
    created_after: null,
    created_before: null,
    updated_after: null,
    updated_before: null,
    tags: [],
    is_favorite: null,
  };
}

export function createDefaultSearchQuery(query: string): SearchQuery {
  return {
    query,
    filters: createDefaultFilter(),
    scope: SearchScope.ALL,
    sort_by: SortField.RELEVANCE,
    sort_order: SortOrder.DESC,
    skip: 0,
    limit: 20,
    include_content: false,
  };
}

// Search State Management

export interface SearchState {
  query: string;
  results: SearchResult[];
  total: number;
  isLoading: boolean;
  error: string | null;
  filters: SearchFilter;
  sortBy: SortField;
  sortOrder: SortOrder;
  page: number;
  pageSize: number;
  suggestions: string[];
  selectedTypes: ResourceType[];
  recentSearches: string[];
}

export function createInitialSearchState(): SearchState {
  return {
    query: '',
    results: [],
    total: 0,
    isLoading: false,
    error: null,
    filters: createDefaultFilter(),
    sortBy: SortField.RELEVANCE,
    sortOrder: SortOrder.DESC,
    page: 0,
    pageSize: 20,
    suggestions: [],
    selectedTypes: [],
    recentSearches: [],
  };
}

// Global Search Component Helper

export interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (result: SearchResult) => void;
  placeholder?: string;
  defaultTypes?: ResourceType[];
  autoFocus?: boolean;
}

export interface SearchResultItemProps {
  result: SearchResult;
  isSelected: boolean;
  onClick: () => void;
  showType?: boolean;
  showDescription?: boolean;
}

// Keyboard Navigation

export interface SearchKeyboardHandlers {
  onArrowDown: () => void;
  onArrowUp: () => void;
  onEnter: () => void;
  onEscape: () => void;
  onTab: () => void;
}

export function handleSearchKeyboard(
  event: KeyboardEvent,
  handlers: SearchKeyboardHandlers
): boolean {
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      handlers.onArrowDown();
      return true;
    case 'ArrowUp':
      event.preventDefault();
      handlers.onArrowUp();
      return true;
    case 'Enter':
      event.preventDefault();
      handlers.onEnter();
      return true;
    case 'Escape':
      handlers.onEscape();
      return true;
    case 'Tab':
      event.preventDefault();
      handlers.onTab();
      return true;
    default:
      return false;
  }
}

// Debounce utility for search input

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => {
      func(...args);
    }, wait);
  };
}

// Recent searches management

const RECENT_SEARCHES_KEY = 'bheem_recent_searches';
const MAX_RECENT_SEARCHES = 10;

export function getRecentSearches(): string[] {
  try {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function addRecentSearch(query: string): void {
  if (!query.trim()) return;

  const recent = getRecentSearches();
  const filtered = recent.filter((q) => q !== query);
  filtered.unshift(query);

  localStorage.setItem(
    RECENT_SEARCHES_KEY,
    JSON.stringify(filtered.slice(0, MAX_RECENT_SEARCHES))
  );
}

export function clearRecentSearches(): void {
  localStorage.removeItem(RECENT_SEARCHES_KEY);
}
