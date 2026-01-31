/**
 * Zustand store for managing filter state across the application
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import {
  FilterCondition,
  RelativeDateFilter,
  DateRangeFilter,
  SlicerConfig,
  FilterOptionsResponse,
  CrossFilterEvent,
} from '../types/filters';

// ============== Types ==============

interface FilterSelection {
  column: string;
  values: any[];
  operator?: string;
}

interface DashboardFilters {
  selections: Record<string, FilterSelection>;
  dateFilters: Record<string, RelativeDateFilter | DateRangeFilter>;
  crossFilterSource?: string;
}

interface FilterState {
  // Dashboard-level filter state (persisted per dashboard)
  dashboardFilters: Record<string, DashboardFilters>;

  // Chart-level filter overrides
  chartFilterOverrides: Record<string, FilterCondition[]>;

  // Slicer configurations per dashboard
  slicerConfigs: Record<string, SlicerConfig[]>;

  // Cached filter options (for performance)
  filterOptions: Record<string, FilterOptionsResponse>;

  // UI state
  filterPaneVisible: boolean;
  activeSlicerId?: string;
  isLoading: boolean;

  // Actions
  setFilterSelection: (dashboardId: string, column: string, values: any[], operator?: string) => void;
  clearFilterSelection: (dashboardId: string, column: string) => void;
  clearAllFilters: (dashboardId: string) => void;

  setDateFilter: (dashboardId: string, column: string, filter: RelativeDateFilter | DateRangeFilter) => void;
  clearDateFilter: (dashboardId: string, column: string) => void;

  setChartFilterOverride: (chartId: string, filters: FilterCondition[]) => void;
  clearChartFilterOverride: (chartId: string) => void;

  setSlicerConfigs: (dashboardId: string, configs: SlicerConfig[]) => void;
  updateSlicerConfig: (dashboardId: string, column: string, updates: Partial<SlicerConfig>) => void;

  setFilterOptions: (key: string, options: FilterOptionsResponse) => void;
  clearFilterOptions: (key?: string) => void;

  setCrossFilterSource: (dashboardId: string, sourceChartId?: string) => void;
  applyCrossFilter: (dashboardId: string, event: CrossFilterEvent) => void;

  setFilterPaneVisible: (visible: boolean) => void;
  setActiveSlicerId: (slicerId?: string) => void;
  setIsLoading: (loading: boolean) => void;

  // Selectors
  getActiveFilters: (dashboardId: string) => FilterCondition[];
  getFilterSelectionForColumn: (dashboardId: string, column: string) => any[];
  hasActiveFilters: (dashboardId: string) => boolean;
}

// ============== Store ==============

export const useFilterStore = create<FilterState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        dashboardFilters: {},
        chartFilterOverrides: {},
        slicerConfigs: {},
        filterOptions: {},
        filterPaneVisible: true,
        activeSlicerId: undefined,
        isLoading: false,

        // Set a filter selection for a column
        setFilterSelection: (dashboardId, column, values, operator = 'in') => {
          set((state) => {
            const dashboardState = state.dashboardFilters[dashboardId] || {
              selections: {},
              dateFilters: {},
            };

            return {
              dashboardFilters: {
                ...state.dashboardFilters,
                [dashboardId]: {
                  ...dashboardState,
                  selections: {
                    ...dashboardState.selections,
                    [column]: { column, values, operator },
                  },
                },
              },
            };
          });
        },

        // Clear a filter selection for a column
        clearFilterSelection: (dashboardId, column) => {
          set((state) => {
            const dashboardState = state.dashboardFilters[dashboardId];
            if (!dashboardState) return state;

            const { [column]: removed, ...remainingSelections } = dashboardState.selections;

            return {
              dashboardFilters: {
                ...state.dashboardFilters,
                [dashboardId]: {
                  ...dashboardState,
                  selections: remainingSelections,
                },
              },
            };
          });
        },

        // Clear all filters for a dashboard
        clearAllFilters: (dashboardId) => {
          set((state) => ({
            dashboardFilters: {
              ...state.dashboardFilters,
              [dashboardId]: {
                selections: {},
                dateFilters: {},
                crossFilterSource: undefined,
              },
            },
          }));
        },

        // Set a date filter
        setDateFilter: (dashboardId, column, filter) => {
          set((state) => {
            const dashboardState = state.dashboardFilters[dashboardId] || {
              selections: {},
              dateFilters: {},
            };

            return {
              dashboardFilters: {
                ...state.dashboardFilters,
                [dashboardId]: {
                  ...dashboardState,
                  dateFilters: {
                    ...dashboardState.dateFilters,
                    [column]: filter,
                  },
                },
              },
            };
          });
        },

        // Clear a date filter
        clearDateFilter: (dashboardId, column) => {
          set((state) => {
            const dashboardState = state.dashboardFilters[dashboardId];
            if (!dashboardState) return state;

            const { [column]: removed, ...remainingDateFilters } = dashboardState.dateFilters;

            return {
              dashboardFilters: {
                ...state.dashboardFilters,
                [dashboardId]: {
                  ...dashboardState,
                  dateFilters: remainingDateFilters,
                },
              },
            };
          });
        },

        // Set chart-level filter overrides
        setChartFilterOverride: (chartId, filters) => {
          set((state) => ({
            chartFilterOverrides: {
              ...state.chartFilterOverrides,
              [chartId]: filters,
            },
          }));
        },

        // Clear chart-level filter overrides
        clearChartFilterOverride: (chartId) => {
          set((state) => {
            const { [chartId]: removed, ...remaining } = state.chartFilterOverrides;
            return { chartFilterOverrides: remaining };
          });
        },

        // Set slicer configurations for a dashboard
        setSlicerConfigs: (dashboardId, configs) => {
          set((state) => ({
            slicerConfigs: {
              ...state.slicerConfigs,
              [dashboardId]: configs,
            },
          }));
        },

        // Update a specific slicer config
        updateSlicerConfig: (dashboardId, column, updates) => {
          set((state) => {
            const configs = state.slicerConfigs[dashboardId] || [];
            const updatedConfigs = configs.map((config) =>
              config.column === column ? { ...config, ...updates } : config
            );

            return {
              slicerConfigs: {
                ...state.slicerConfigs,
                [dashboardId]: updatedConfigs,
              },
            };
          });
        },

        // Cache filter options
        setFilterOptions: (key, options) => {
          set((state) => ({
            filterOptions: {
              ...state.filterOptions,
              [key]: options,
            },
          }));
        },

        // Clear filter options cache
        clearFilterOptions: (key) => {
          set((state) => {
            if (key) {
              const { [key]: removed, ...remaining } = state.filterOptions;
              return { filterOptions: remaining };
            }
            return { filterOptions: {} };
          });
        },

        // Set cross-filter source
        setCrossFilterSource: (dashboardId, sourceChartId) => {
          set((state) => {
            const dashboardState = state.dashboardFilters[dashboardId] || {
              selections: {},
              dateFilters: {},
            };

            return {
              dashboardFilters: {
                ...state.dashboardFilters,
                [dashboardId]: {
                  ...dashboardState,
                  crossFilterSource: sourceChartId,
                },
              },
            };
          });
        },

        // Apply cross-filter from a chart selection
        applyCrossFilter: (dashboardId, event) => {
          const { selectedData, action } = event;

          set((state) => {
            const dashboardState = state.dashboardFilters[dashboardId] || {
              selections: {},
              dateFilters: {},
            };

            let newSelections = { ...dashboardState.selections };

            if (action === 'replace') {
              // Replace all cross-filter selections
              newSelections = {};
              for (const [column, value] of Object.entries(selectedData)) {
                newSelections[column] = {
                  column,
                  values: Array.isArray(value) ? value : [value],
                  operator: 'in',
                };
              }
            } else if (action === 'add') {
              // Add to existing selections
              for (const [column, value] of Object.entries(selectedData)) {
                const existing = newSelections[column]?.values || [];
                const newValues = Array.isArray(value) ? value : [value];
                newSelections[column] = {
                  column,
                  values: [...new Set([...existing, ...newValues])],
                  operator: 'in',
                };
              }
            } else if (action === 'remove') {
              // Remove from existing selections
              for (const [column, value] of Object.entries(selectedData)) {
                const existing = newSelections[column]?.values || [];
                const removeValues = Array.isArray(value) ? value : [value];
                const remaining = existing.filter((v) => !removeValues.includes(v));
                if (remaining.length > 0) {
                  newSelections[column] = {
                    column,
                    values: remaining,
                    operator: 'in',
                  };
                } else {
                  delete newSelections[column];
                }
              }
            }

            return {
              dashboardFilters: {
                ...state.dashboardFilters,
                [dashboardId]: {
                  ...dashboardState,
                  selections: newSelections,
                  crossFilterSource: event.sourceChartId,
                },
              },
            };
          });
        },

        // UI state setters
        setFilterPaneVisible: (visible) => set({ filterPaneVisible: visible }),
        setActiveSlicerId: (slicerId) => set({ activeSlicerId: slicerId }),
        setIsLoading: (loading) => set({ isLoading: loading }),

        // Get active filters as FilterCondition array
        getActiveFilters: (dashboardId) => {
          const state = get();
          const dashboardState = state.dashboardFilters[dashboardId];
          if (!dashboardState) return [];

          const conditions: FilterCondition[] = [];

          // Convert selections to conditions
          for (const selection of Object.values(dashboardState.selections)) {
            if (selection.values.length > 0) {
              conditions.push({
                column: selection.column,
                operator: (selection.operator as any) || 'in',
                value: selection.values.length === 1 ? selection.values[0] : selection.values,
              });
            }
          }

          return conditions;
        },

        // Get filter selection for a specific column
        getFilterSelectionForColumn: (dashboardId, column) => {
          const state = get();
          const dashboardState = state.dashboardFilters[dashboardId];
          return dashboardState?.selections[column]?.values || [];
        },

        // Check if dashboard has active filters
        hasActiveFilters: (dashboardId) => {
          const state = get();
          const dashboardState = state.dashboardFilters[dashboardId];
          if (!dashboardState) return false;

          const hasSelections = Object.keys(dashboardState.selections).length > 0;
          const hasDateFilters = Object.keys(dashboardState.dateFilters).length > 0;

          return hasSelections || hasDateFilters;
        },
      }),
      {
        name: 'bheem-filter-storage',
        partialize: (state) => ({
          dashboardFilters: state.dashboardFilters,
          slicerConfigs: state.slicerConfigs,
        }),
      }
    ),
    { name: 'FilterStore' }
  )
);

// ============== Selectors (for use with shallow comparison) ==============

export const selectFilterSelections = (dashboardId: string) => (state: FilterState) =>
  state.dashboardFilters[dashboardId]?.selections || {};

export const selectDateFilters = (dashboardId: string) => (state: FilterState) =>
  state.dashboardFilters[dashboardId]?.dateFilters || {};

export const selectSlicerConfigs = (dashboardId: string) => (state: FilterState) =>
  state.slicerConfigs[dashboardId] || [];

export const selectFilterOptions = (key: string) => (state: FilterState) =>
  state.filterOptions[key];
