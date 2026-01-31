/**
 * Drill Context Component
 *
 * Provides drill functionality context to chart components.
 * Wraps charts and handles drill interactions.
 */

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DrillHierarchy,
  DrillthroughConfig,
  DrillthroughTarget,
  ChartDrillConfig,
  DrillPath,
} from '../../types/drill';
import { useDrillStore } from '../../stores/drillStore';
import { api } from '../../lib/api';
import { DrillthroughMenu } from './DrillthroughMenu';

interface DrillContextValue {
  // Config
  dashboardId: string;
  chartId: string;
  drillConfig: ChartDrillConfig;
  activeHierarchy: DrillHierarchy | null;

  // State
  currentPath: DrillPath | null;
  canDrillDown: boolean;
  canDrillUp: boolean;

  // Actions
  handleDrillDown: (clickedValue: any, clickedData?: Record<string, any>) => void;
  handleDrillUp: () => void;
  handleDrillToLevel: (level: number) => void;
  handleReset: () => void;
  handleDrillthrough: (target: DrillthroughTarget, clickedData: Record<string, any>) => void;

  // Context Menu
  showDrillthroughMenu: (position: { x: number; y: number }, clickedData: Record<string, any>) => void;
  hideDrillthroughMenu: () => void;
}

const DrillContext = createContext<DrillContextValue | null>(null);

export const useDrill = () => {
  const context = useContext(DrillContext);
  if (!context) {
    throw new Error('useDrill must be used within a DrillProvider');
  }
  return context;
};

interface DrillProviderProps {
  children: ReactNode;
  dashboardId: string;
  chartId: string;
  drillConfig: ChartDrillConfig;
  onDataRefresh?: (filters: Record<string, any>) => void;
}

export const DrillProvider: React.FC<DrillProviderProps> = ({
  children,
  dashboardId,
  chartId,
  drillConfig,
  onDataRefresh,
}) => {
  const navigate = useNavigate();

  const {
    getChartDrillState,
    drillDown,
    drillUp,
    drillToLevel,
    resetDrill,
  } = useDrillStore();

  // Drillthrough menu state
  const [drillthroughMenuState, setDrillthroughMenuState] = useState<{
    visible: boolean;
    position: { x: number; y: number };
    clickedData: Record<string, any>;
  }>({
    visible: false,
    position: { x: 0, y: 0 },
    clickedData: {},
  });

  // Get current state
  const chartState = getChartDrillState(dashboardId, chartId);
  const currentPath = chartState?.currentPath || null;

  // Get active hierarchy
  const activeHierarchyId = chartState?.activeHierarchyId || drillConfig.defaultHierarchyId || drillConfig.hierarchies[0]?.id;
  const activeHierarchy = drillConfig.hierarchies.find((h) => h.id === activeHierarchyId) || null;

  // Calculate drill capabilities
  const canDrillDownState = activeHierarchy
    ? (currentPath?.currentLevel ?? 0) < activeHierarchy.levels.length - 1
    : false;

  const canDrillUpState = (currentPath?.currentLevel ?? 0) > 0;

  // Handle drill down
  const handleDrillDown = useCallback(
    (clickedValue: any, clickedData?: Record<string, any>) => {
      if (!activeHierarchy || !canDrillDownState) return;

      const newPath = drillDown(dashboardId, chartId, activeHierarchy, clickedValue);

      if (newPath && onDataRefresh) {
        onDataRefresh(newPath.filters);
      }
    },
    [activeHierarchy, canDrillDownState, dashboardId, chartId, drillDown, onDataRefresh]
  );

  // Handle drill up
  const handleDrillUp = useCallback(() => {
    if (!activeHierarchy || !canDrillUpState) return;

    const newPath = drillUp(dashboardId, chartId, activeHierarchy);

    if (newPath && onDataRefresh) {
      onDataRefresh(newPath.filters);
    }
  }, [activeHierarchy, canDrillUpState, dashboardId, chartId, drillUp, onDataRefresh]);

  // Handle drill to specific level
  const handleDrillToLevel = useCallback(
    (level: number) => {
      if (!activeHierarchy) return;

      const newPath = drillToLevel(dashboardId, chartId, activeHierarchy, level);

      if (newPath && onDataRefresh) {
        onDataRefresh(newPath.filters);
      }
    },
    [activeHierarchy, dashboardId, chartId, drillToLevel, onDataRefresh]
  );

  // Handle reset
  const handleReset = useCallback(() => {
    resetDrill(dashboardId, chartId);

    if (onDataRefresh) {
      onDataRefresh({});
    }
  }, [dashboardId, chartId, resetDrill, onDataRefresh]);

  // Handle drillthrough
  const handleDrillthrough = useCallback(
    async (target: DrillthroughTarget, clickedData: Record<string, any>) => {
      try {
        // Build target filters from field mappings
        const targetFilters: Record<string, any> = {};
        for (const mapping of target.fieldMappings) {
          if (clickedData[mapping.sourceColumn] !== undefined) {
            targetFilters[mapping.targetParameter] = clickedData[mapping.sourceColumn];
          }
        }

        // Navigate based on target type
        if (target.targetType === 'url') {
          let url = target.targetUrl || '';

          // Append filters as query params
          if (Object.keys(targetFilters).length > 0) {
            const params = new URLSearchParams(targetFilters).toString();
            url += (url.includes('?') ? '&' : '?') + params;
          }

          if (target.openInNewTab) {
            window.open(url, '_blank');
          } else {
            window.location.href = url;
          }
        } else if (target.targetType === 'page') {
          // Navigate to page within dashboard
          const params = new URLSearchParams(targetFilters).toString();
          const url = `/dashboard/${dashboardId}?page=${target.targetId}${params ? '&' + params : ''}`;

          if (target.openInNewTab) {
            window.open(url, '_blank');
          } else {
            navigate(url);
          }
        } else if (target.targetType === 'report') {
          // Navigate to different report/dashboard
          const params = new URLSearchParams(targetFilters).toString();
          const url = `/dashboard/${target.targetId}${params ? '?' + params : ''}`;

          if (target.openInNewTab) {
            window.open(url, '_blank');
          } else {
            navigate(url);
          }
        }
      } catch (error) {
        console.error('Drillthrough failed:', error);
      }

      // Close menu
      setDrillthroughMenuState((prev) => ({ ...prev, visible: false }));
    },
    [dashboardId, navigate]
  );

  // Show drillthrough menu
  const showDrillthroughMenu = useCallback(
    (position: { x: number; y: number }, clickedData: Record<string, any>) => {
      if (!drillConfig.drillthrough?.enabled) return;

      setDrillthroughMenuState({
        visible: true,
        position,
        clickedData,
      });
    },
    [drillConfig.drillthrough]
  );

  // Hide drillthrough menu
  const hideDrillthroughMenu = useCallback(() => {
    setDrillthroughMenuState((prev) => ({ ...prev, visible: false }));
  }, []);

  const contextValue: DrillContextValue = {
    dashboardId,
    chartId,
    drillConfig,
    activeHierarchy,
    currentPath,
    canDrillDown: canDrillDownState,
    canDrillUp: canDrillUpState,
    handleDrillDown,
    handleDrillUp,
    handleDrillToLevel,
    handleReset,
    handleDrillthrough,
    showDrillthroughMenu,
    hideDrillthroughMenu,
  };

  return (
    <DrillContext.Provider value={contextValue}>
      {children}

      {/* Drillthrough Context Menu */}
      {drillthroughMenuState.visible && drillConfig.drillthrough && (
        <DrillthroughMenu
          config={drillConfig.drillthrough}
          clickedData={drillthroughMenuState.clickedData}
          position={drillthroughMenuState.position}
          onSelect={(target) =>
            handleDrillthrough(target, drillthroughMenuState.clickedData)
          }
          onClose={hideDrillthroughMenu}
        />
      )}
    </DrillContext.Provider>
  );
};

export default DrillProvider;
