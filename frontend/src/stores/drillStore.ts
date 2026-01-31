/**
 * Drill Store
 *
 * Zustand store for managing drill-down and drillthrough state.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
  DrillPath,
  DrillHierarchy,
  ChartDrillState,
  DashboardDrillState,
  DrillHistoryEntry,
  DrillType,
  createEmptyDrillPath,
} from '../types/drill';

interface DrillStore {
  // State
  dashboardDrillStates: Record<string, DashboardDrillState>;
  drillHistory: Record<string, DrillHistoryEntry[]>;
  syncDrillEnabled: Record<string, boolean>;

  // Actions - Drill State
  initDashboardDrillState: (dashboardId: string) => void;
  getChartDrillState: (dashboardId: string, chartId: string) => ChartDrillState | null;
  setChartDrillState: (dashboardId: string, chartId: string, state: Partial<ChartDrillState>) => void;
  clearChartDrillState: (dashboardId: string, chartId: string) => void;
  clearAllDrillStates: (dashboardId: string) => void;

  // Actions - Drill Path
  setDrillPath: (dashboardId: string, chartId: string, path: DrillPath) => void;
  drillDown: (
    dashboardId: string,
    chartId: string,
    hierarchy: DrillHierarchy,
    clickedValue: any
  ) => DrillPath | null;
  drillUp: (dashboardId: string, chartId: string, hierarchy: DrillHierarchy) => DrillPath | null;
  drillToLevel: (
    dashboardId: string,
    chartId: string,
    hierarchy: DrillHierarchy,
    targetLevel: number
  ) => DrillPath | null;
  resetDrill: (dashboardId: string, chartId: string) => void;

  // Actions - Hierarchy
  setActiveHierarchy: (dashboardId: string, chartId: string, hierarchyId: string) => void;

  // Actions - Expanded Items
  toggleExpandedItem: (dashboardId: string, chartId: string, itemKey: string) => void;
  setExpandedItems: (dashboardId: string, chartId: string, items: string[]) => void;
  clearExpandedItems: (dashboardId: string, chartId: string) => void;

  // Actions - Sync Drill
  setSyncDrill: (dashboardId: string, enabled: boolean) => void;
  setGlobalDrillPath: (dashboardId: string, path: DrillPath | null) => void;

  // Actions - History
  addHistoryEntry: (dashboardId: string, entry: Omit<DrillHistoryEntry, 'timestamp'>) => void;
  undoDrill: (dashboardId: string) => void;
  redoDrill: (dashboardId: string) => void;
  clearHistory: (dashboardId: string) => void;

  // Selectors
  canUndo: (dashboardId: string) => boolean;
  canRedo: (dashboardId: string) => boolean;
  getBreadcrumbs: (dashboardId: string, chartId: string, hierarchy: DrillHierarchy) => any[];
}

export const useDrillStore = create<DrillStore>()(
  persist(
    (set, get) => ({
      // Initial State
      dashboardDrillStates: {},
      drillHistory: {},
      syncDrillEnabled: {},

      // Initialize dashboard drill state
      initDashboardDrillState: (dashboardId) => {
        const current = get().dashboardDrillStates[dashboardId];
        if (!current) {
          set((state) => ({
            dashboardDrillStates: {
              ...state.dashboardDrillStates,
              [dashboardId]: {
                dashboardId,
                chartStates: {},
                syncDrill: false,
              },
            },
          }));
        }
      },

      // Get chart drill state
      getChartDrillState: (dashboardId, chartId) => {
        const dashboardState = get().dashboardDrillStates[dashboardId];
        return dashboardState?.chartStates[chartId] || null;
      },

      // Set chart drill state
      setChartDrillState: (dashboardId, chartId, state) => {
        set((store) => {
          const dashboardState = store.dashboardDrillStates[dashboardId] || {
            dashboardId,
            chartStates: {},
            syncDrill: false,
          };

          const currentChartState = dashboardState.chartStates[chartId] || {
            chartId,
            expandedItems: [],
          };

          return {
            dashboardDrillStates: {
              ...store.dashboardDrillStates,
              [dashboardId]: {
                ...dashboardState,
                chartStates: {
                  ...dashboardState.chartStates,
                  [chartId]: {
                    ...currentChartState,
                    ...state,
                  },
                },
              },
            },
          };
        });
      },

      // Clear chart drill state
      clearChartDrillState: (dashboardId, chartId) => {
        set((store) => {
          const dashboardState = store.dashboardDrillStates[dashboardId];
          if (!dashboardState) return store;

          const { [chartId]: removed, ...remaining } = dashboardState.chartStates;

          return {
            dashboardDrillStates: {
              ...store.dashboardDrillStates,
              [dashboardId]: {
                ...dashboardState,
                chartStates: remaining,
              },
            },
          };
        });
      },

      // Clear all drill states for a dashboard
      clearAllDrillStates: (dashboardId) => {
        set((store) => ({
          dashboardDrillStates: {
            ...store.dashboardDrillStates,
            [dashboardId]: {
              dashboardId,
              chartStates: {},
              syncDrill: false,
            },
          },
        }));
      },

      // Set drill path directly
      setDrillPath: (dashboardId, chartId, path) => {
        get().setChartDrillState(dashboardId, chartId, {
          currentPath: path,
          activeHierarchyId: path.hierarchyId,
        });
      },

      // Drill down
      drillDown: (dashboardId, chartId, hierarchy, clickedValue) => {
        const currentState = get().getChartDrillState(dashboardId, chartId);
        const currentPath = currentState?.currentPath || createEmptyDrillPath(hierarchy.id);

        const currentLevel = currentPath.currentLevel;
        const maxLevel = hierarchy.levels.length - 1;

        // Can't drill down further
        if (currentLevel >= maxLevel) return null;

        const currentLevelConfig = hierarchy.levels[currentLevel];

        // Build new path
        const newPath: DrillPath = {
          hierarchyId: hierarchy.id,
          currentLevel: currentLevel + 1,
          filters: {
            ...currentPath.filters,
            [currentLevelConfig.column]: clickedValue,
          },
          breadcrumbs: [
            ...currentPath.breadcrumbs,
            {
              level: currentLevel,
              column: currentLevelConfig.column,
              label: currentLevelConfig.label,
              value: clickedValue,
            },
          ],
        };

        // Update state
        get().setChartDrillState(dashboardId, chartId, {
          currentPath: newPath,
          activeHierarchyId: hierarchy.id,
        });

        // Add history entry
        get().addHistoryEntry(dashboardId, {
          chartId,
          operation: 'drill_down',
          fromLevel: currentLevel,
          toLevel: currentLevel + 1,
          clickedValue,
        });

        // Sync drill if enabled
        if (get().syncDrillEnabled[dashboardId]) {
          get().setGlobalDrillPath(dashboardId, newPath);
        }

        return newPath;
      },

      // Drill up
      drillUp: (dashboardId, chartId, hierarchy) => {
        const currentState = get().getChartDrillState(dashboardId, chartId);
        const currentPath = currentState?.currentPath;

        if (!currentPath || currentPath.currentLevel <= 0) return null;

        const newLevel = currentPath.currentLevel - 1;
        const newBreadcrumbs = currentPath.breadcrumbs.slice(0, -1);
        const removedCrumb = currentPath.breadcrumbs[currentPath.breadcrumbs.length - 1];

        // Build new filters without the removed level
        const newFilters = { ...currentPath.filters };
        if (removedCrumb) {
          delete newFilters[removedCrumb.column];
        }

        const newPath: DrillPath = {
          hierarchyId: hierarchy.id,
          currentLevel: newLevel,
          filters: newFilters,
          breadcrumbs: newBreadcrumbs,
        };

        // Update state
        get().setChartDrillState(dashboardId, chartId, {
          currentPath: newPath,
        });

        // Add history entry
        get().addHistoryEntry(dashboardId, {
          chartId,
          operation: 'drill_up',
          fromLevel: currentPath.currentLevel,
          toLevel: newLevel,
        });

        return newPath;
      },

      // Drill to specific level (for breadcrumb navigation)
      drillToLevel: (dashboardId, chartId, hierarchy, targetLevel) => {
        const currentState = get().getChartDrillState(dashboardId, chartId);
        const currentPath = currentState?.currentPath;

        if (!currentPath) return null;

        // Clicking "All" - reset to level 0
        if (targetLevel === 0) {
          const newPath = createEmptyDrillPath(hierarchy.id);
          get().setChartDrillState(dashboardId, chartId, {
            currentPath: newPath,
          });
          return newPath;
        }

        // Keep only breadcrumbs up to target level
        const newBreadcrumbs = currentPath.breadcrumbs.slice(0, targetLevel);

        // Rebuild filters from remaining breadcrumbs
        const newFilters: Record<string, any> = {};
        for (const crumb of newBreadcrumbs) {
          newFilters[crumb.column] = crumb.value;
        }

        const newPath: DrillPath = {
          hierarchyId: hierarchy.id,
          currentLevel: targetLevel,
          filters: newFilters,
          breadcrumbs: newBreadcrumbs,
        };

        get().setChartDrillState(dashboardId, chartId, {
          currentPath: newPath,
        });

        return newPath;
      },

      // Reset drill to initial state
      resetDrill: (dashboardId, chartId) => {
        get().setChartDrillState(dashboardId, chartId, {
          currentPath: undefined,
          expandedItems: [],
        });
      },

      // Set active hierarchy
      setActiveHierarchy: (dashboardId, chartId, hierarchyId) => {
        get().setChartDrillState(dashboardId, chartId, {
          activeHierarchyId: hierarchyId,
          currentPath: createEmptyDrillPath(hierarchyId),
        });
      },

      // Toggle expanded item
      toggleExpandedItem: (dashboardId, chartId, itemKey) => {
        const currentState = get().getChartDrillState(dashboardId, chartId);
        const expanded = currentState?.expandedItems || [];

        const newExpanded = expanded.includes(itemKey)
          ? expanded.filter((k) => k !== itemKey)
          : [...expanded, itemKey];

        get().setChartDrillState(dashboardId, chartId, {
          expandedItems: newExpanded,
        });
      },

      // Set expanded items
      setExpandedItems: (dashboardId, chartId, items) => {
        get().setChartDrillState(dashboardId, chartId, {
          expandedItems: items,
        });
      },

      // Clear expanded items
      clearExpandedItems: (dashboardId, chartId) => {
        get().setChartDrillState(dashboardId, chartId, {
          expandedItems: [],
        });
      },

      // Set sync drill
      setSyncDrill: (dashboardId, enabled) => {
        set((state) => ({
          syncDrillEnabled: {
            ...state.syncDrillEnabled,
            [dashboardId]: enabled,
          },
        }));

        if (enabled) {
          // Update dashboard state
          set((state) => {
            const dashboardState = state.dashboardDrillStates[dashboardId];
            if (!dashboardState) return state;

            return {
              dashboardDrillStates: {
                ...state.dashboardDrillStates,
                [dashboardId]: {
                  ...dashboardState,
                  syncDrill: true,
                },
              },
            };
          });
        }
      },

      // Set global drill path for synced drilling
      setGlobalDrillPath: (dashboardId, path) => {
        set((state) => {
          const dashboardState = state.dashboardDrillStates[dashboardId];
          if (!dashboardState) return state;

          return {
            dashboardDrillStates: {
              ...state.dashboardDrillStates,
              [dashboardId]: {
                ...dashboardState,
                globalDrillPath: path || undefined,
              },
            },
          };
        });
      },

      // Add history entry
      addHistoryEntry: (dashboardId, entry) => {
        set((state) => {
          const history = state.drillHistory[dashboardId] || [];
          const newEntry: DrillHistoryEntry = {
            ...entry,
            timestamp: new Date().toISOString(),
          };

          // Keep last 50 entries
          const newHistory = [...history, newEntry].slice(-50);

          return {
            drillHistory: {
              ...state.drillHistory,
              [dashboardId]: newHistory,
            },
          };
        });
      },

      // Undo drill (placeholder - would need more state)
      undoDrill: (dashboardId) => {
        // TODO: Implement proper undo/redo with history index
        console.log('Undo drill for', dashboardId);
      },

      // Redo drill (placeholder)
      redoDrill: (dashboardId) => {
        // TODO: Implement proper undo/redo
        console.log('Redo drill for', dashboardId);
      },

      // Clear history
      clearHistory: (dashboardId) => {
        set((state) => ({
          drillHistory: {
            ...state.drillHistory,
            [dashboardId]: [],
          },
        }));
      },

      // Check if undo is possible
      canUndo: (dashboardId) => {
        const history = get().drillHistory[dashboardId] || [];
        return history.length > 0;
      },

      // Check if redo is possible
      canRedo: (dashboardId) => {
        // TODO: Implement with proper history index
        return false;
      },

      // Get breadcrumbs for display
      getBreadcrumbs: (dashboardId, chartId, hierarchy) => {
        const state = get().getChartDrillState(dashboardId, chartId);
        const path = state?.currentPath;

        // Start with "All" breadcrumb
        const breadcrumbs = [
          {
            level: 0,
            label: 'All',
            value: null,
            isCurrent: !path || path.currentLevel === 0,
          },
        ];

        if (!path || !path.breadcrumbs.length) {
          return breadcrumbs;
        }

        // Add breadcrumbs from path
        path.breadcrumbs.forEach((crumb, index) => {
          const levelConfig = hierarchy.levels[crumb.level];
          let displayValue = crumb.value;

          // Apply format if available
          if (levelConfig?.format && displayValue != null) {
            try {
              displayValue = levelConfig.format.replace('{value}', String(displayValue));
            } catch {
              // Keep original value
            }
          }

          breadcrumbs.push({
            level: crumb.level + 1,
            label: `${levelConfig?.label || crumb.column}: ${displayValue}`,
            value: crumb.value,
            isCurrent: index === path.breadcrumbs.length - 1,
          });
        });

        return breadcrumbs;
      },
    }),
    {
      name: 'bheem-drill-storage',
      partialize: (state) => ({
        dashboardDrillStates: state.dashboardDrillStates,
        syncDrillEnabled: state.syncDrillEnabled,
      }),
    }
  )
);

export default useDrillStore;
