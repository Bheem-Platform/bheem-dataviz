/**
 * Drill Types
 *
 * TypeScript types for drill-down and drillthrough operations.
 */

// Enums

export type DrillDirection = 'up' | 'down';

export type DrillType =
  | 'drill_down'
  | 'drill_up'
  | 'drillthrough'
  | 'expand'
  | 'collapse';

// Hierarchy Types

export interface DrillHierarchyLevel {
  column: string;
  label: string;
  sortOrder?: 'asc' | 'desc';
  format?: string;
}

export interface DrillHierarchy {
  id: string;
  name: string;
  levels: DrillHierarchyLevel[];
  defaultLevel?: number;
}

// Drill Path & State

export interface DrillPath {
  hierarchyId: string;
  currentLevel: number;
  filters: Record<string, any>;
  breadcrumbs: DrillBreadcrumb[];
}

export interface DrillBreadcrumb {
  level: number;
  column: string;
  label: string;
  value: any;
}

export interface FormattedBreadcrumb {
  level: number;
  label: string;
  value: any;
  isCurrent: boolean;
}

// Drill Request/Response

export interface DrillRequest {
  chartId: string;
  hierarchyId: string;
  direction: DrillDirection;
  clickedValue?: any;
  currentPath?: DrillPath;
}

export interface DrillResponse {
  success: boolean;
  newPath: DrillPath;
  data?: Record<string, any>[];
  query?: string;
  canDrillDown: boolean;
  canDrillUp: boolean;
}

// Drillthrough Types

export interface DrillthroughField {
  sourceColumn: string;
  targetParameter: string;
  passAllFilters?: boolean;
}

export interface DrillthroughTarget {
  id: string;
  name: string;
  targetType: 'page' | 'report' | 'url';
  targetId?: string;
  targetUrl?: string;
  fieldMappings: DrillthroughField[];
  openInNewTab?: boolean;
  icon?: string;
}

export interface DrillthroughConfig {
  enabled: boolean;
  targets: DrillthroughTarget[];
  defaultTargetId?: string;
}

export interface DrillthroughRequest {
  sourceChartId: string;
  targetId: string;
  clickedData: Record<string, any>;
  currentFilters?: Record<string, any>;
}

export interface DrillthroughResponse {
  success: boolean;
  targetType: string;
  targetUrl?: string;
  targetFilters: Record<string, any>;
  error?: string;
}

// Chart Drill Configuration

export interface ChartDrillConfig {
  drillEnabled: boolean;
  hierarchies: DrillHierarchy[];
  defaultHierarchyId?: string;
  drillthrough?: DrillthroughConfig;
  showDrillButtons: boolean;
  showBreadcrumbs: boolean;
  allowMultiLevelExpand?: boolean;
}

// Drill State

export interface ChartDrillState {
  chartId: string;
  activeHierarchyId?: string;
  currentPath?: DrillPath;
  expandedItems: string[];
  lastDrillthrough?: Record<string, any>;
}

export interface DashboardDrillState {
  dashboardId: string;
  chartStates: Record<string, ChartDrillState>;
  globalDrillPath?: DrillPath;
  syncDrill: boolean;
}

// Drill History

export interface DrillHistoryEntry {
  timestamp: string;
  chartId: string;
  operation: DrillType;
  fromLevel: number;
  toLevel: number;
  clickedValue?: any;
}

export interface DrillHistory {
  dashboardId: string;
  entries: DrillHistoryEntry[];
  currentIndex: number;
  maxEntries: number;
}

// Default configurations

export const DEFAULT_DRILL_CONFIG: ChartDrillConfig = {
  drillEnabled: true,
  hierarchies: [],
  showDrillButtons: true,
  showBreadcrumbs: true,
  allowMultiLevelExpand: false,
};

export const COMMON_HIERARCHIES: DrillHierarchy[] = [
  {
    id: 'time_hierarchy',
    name: 'Time',
    levels: [
      { column: 'year', label: 'Year' },
      { column: 'quarter', label: 'Quarter' },
      { column: 'month', label: 'Month' },
      { column: 'week', label: 'Week' },
      { column: 'day', label: 'Day' },
    ],
  },
  {
    id: 'geography_hierarchy',
    name: 'Geography',
    levels: [
      { column: 'country', label: 'Country' },
      { column: 'region', label: 'Region' },
      { column: 'state', label: 'State' },
      { column: 'city', label: 'City' },
    ],
  },
  {
    id: 'product_hierarchy',
    name: 'Product',
    levels: [
      { column: 'category', label: 'Category' },
      { column: 'subcategory', label: 'Subcategory' },
      { column: 'product', label: 'Product' },
    ],
  },
];

// Helper function to create an empty drill path
export function createEmptyDrillPath(hierarchyId: string): DrillPath {
  return {
    hierarchyId,
    currentLevel: 0,
    filters: {},
    breadcrumbs: [],
  };
}

// Helper function to check if drill-down is possible
export function canDrillDown(
  drillPath: DrillPath,
  hierarchy: DrillHierarchy
): boolean {
  return drillPath.currentLevel < hierarchy.levels.length - 1;
}

// Helper function to check if drill-up is possible
export function canDrillUp(drillPath: DrillPath): boolean {
  return drillPath.currentLevel > 0;
}
