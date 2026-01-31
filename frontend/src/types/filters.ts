/**
 * Types for advanced filters and slicers
 */

// Filter types
export type FilterType =
  | 'dropdown'
  | 'list'
  | 'tile'
  | 'between'
  | 'relative_date'
  | 'date_range'
  | 'hierarchy'
  | 'search';

// Filter operators
export type FilterOperator =
  | '='
  | '!='
  | '>'
  | '>='
  | '<'
  | '<='
  | 'in'
  | 'not_in'
  | 'between'
  | 'like'
  | 'not_like'
  | 'starts_with'
  | 'ends_with'
  | 'contains'
  | 'is_null'
  | 'is_not_null';

// Date granularity
export type DateGranularity = 'day' | 'week' | 'month' | 'quarter' | 'year';

// Relative date unit
export type RelativeDateUnit = 'day' | 'week' | 'month' | 'quarter' | 'year';

// ============== Filter Value Types ==============

export interface RelativeDateOption {
  label: string;
  value: number;
  unit: RelativeDateUnit;
}

export interface DateConfig {
  granularity: DateGranularity;
  relativeOptions: RelativeDateOption[];
  minDate?: string;
  maxDate?: string;
  defaultRangeDays: number;
  includeTime: boolean;
}

export interface NumericConfig {
  minValue?: number;
  maxValue?: number;
  step: number;
  format: string;
  showHistogram: boolean;
}

export interface HierarchyLevel {
  column: string;
  label: string;
  parentColumn?: string;
}

export interface HierarchyConfig {
  levels: HierarchyLevel[];
  expandAll: boolean;
  singleSelectPerLevel: boolean;
}

// ============== Slicer Configuration ==============

export interface SlicerConfig {
  type: FilterType;
  column: string;
  label?: string;

  // Common options
  multiSelect: boolean;
  selectAllEnabled: boolean;
  searchEnabled: boolean;
  showCount: boolean;
  defaultValues?: any[];

  // Type-specific configs
  dateConfig?: DateConfig;
  numericConfig?: NumericConfig;
  hierarchyConfig?: HierarchyConfig;

  // Display options
  width: number;
  collapsed: boolean;
  visible: boolean;
  sortOrder: number;
}

// ============== Filter Condition ==============

export interface FilterCondition {
  column: string;
  operator: FilterOperator;
  value?: any;
  value2?: any; // For BETWEEN operator
  dataType?: string;
}

export interface RelativeDateFilter {
  column: string;
  value: number;
  unit: RelativeDateUnit;
  includeCurrent: boolean;
}

export interface DateRangeFilter {
  column: string;
  startDate?: string;
  endDate?: string;
  includeStart: boolean;
  includeEnd: boolean;
}

export interface FilterGroup {
  logic: 'and' | 'or';
  conditions: (FilterCondition | FilterGroup)[];
}

// ============== Filter Options ==============

export interface FilterOptionValue {
  value: any;
  label?: string;
  count?: number;
  children?: FilterOptionValue[];
}

export interface FilterOptionsResponse {
  column: string;
  dataType: string;
  totalCount: number;
  distinctCount: number;
  nullCount: number;
  values: FilterOptionValue[];
  minValue?: any;
  maxValue?: any;
  minDate?: string;
  maxDate?: string;
}

export interface MultiColumnFilterOptionsResponse {
  columns: Record<string, FilterOptionsResponse>;
}

// ============== Dashboard Filter State ==============

export interface DashboardFilterState {
  dashboardId: string;
  filters: Record<string, any>;
  dateFilters: Record<string, RelativeDateFilter | DateRangeFilter>;
  crossFilterSource?: string;
  updatedAt: string;
}

export interface ChartFilterState {
  chartId: string;
  appliedFilters: FilterCondition[];
  inheritedFromDashboard: boolean;
  localOverrides: Record<string, any>;
}

// ============== Global Filter Configuration ==============

export interface GlobalFilterConfig {
  slicers: SlicerConfig[];
  crossFilterEnabled: boolean;
  syncSlicers: boolean;
  filterPaneVisible: boolean;
  filterPanePosition: 'left' | 'right' | 'top';
}

// ============== Filter Preset ==============

export interface SavedFilterPreset {
  id: string;
  name: string;
  description?: string;
  dashboardId?: string;
  chartId?: string;
  filters: FilterCondition[];
  slicers: SlicerConfig[];
  isDefault: boolean;
  createdBy?: string;
  createdAt: string;
  updatedAt: string;
}

// ============== Cross-Filter ==============

export interface CrossFilterEvent {
  sourceChartId: string;
  selectedData: Record<string, any>;
  action: 'add' | 'remove' | 'replace';
}

export interface CrossFilterConfig {
  enabled: boolean;
  sourceCharts: string[];
  targetCharts: string[];
  columnMappings: Record<string, string>;
}

// ============== API Request/Response Types ==============

export interface ApplyFiltersRequest {
  filters: FilterCondition[];
  dateFilters: (RelativeDateFilter | DateRangeFilter)[];
  limit: number;
}

export interface SaveFiltersRequest {
  name: string;
  description?: string;
  filters: FilterCondition[];
  slicers: SlicerConfig[];
  isDefault: boolean;
}

// ============== Default Values ==============

export const DEFAULT_RELATIVE_DATE_OPTIONS: RelativeDateOption[] = [
  { label: 'Today', value: 0, unit: 'day' },
  { label: 'Yesterday', value: 1, unit: 'day' },
  { label: 'Last 7 Days', value: 7, unit: 'day' },
  { label: 'Last 14 Days', value: 14, unit: 'day' },
  { label: 'Last 30 Days', value: 30, unit: 'day' },
  { label: 'Last 90 Days', value: 90, unit: 'day' },
  { label: 'This Week', value: 0, unit: 'week' },
  { label: 'Last Week', value: 1, unit: 'week' },
  { label: 'This Month', value: 0, unit: 'month' },
  { label: 'Last Month', value: 1, unit: 'month' },
  { label: 'Last 3 Months', value: 3, unit: 'month' },
  { label: 'Last 6 Months', value: 6, unit: 'month' },
  { label: 'This Quarter', value: 0, unit: 'quarter' },
  { label: 'Last Quarter', value: 1, unit: 'quarter' },
  { label: 'This Year', value: 0, unit: 'year' },
  { label: 'Last Year', value: 1, unit: 'year' },
];

export const DEFAULT_SLICER_CONFIG: Partial<SlicerConfig> = {
  multiSelect: true,
  selectAllEnabled: true,
  searchEnabled: true,
  showCount: false,
  width: 200,
  collapsed: false,
  visible: true,
  sortOrder: 0,
};
