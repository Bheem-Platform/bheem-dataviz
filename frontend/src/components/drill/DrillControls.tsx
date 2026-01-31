/**
 * Drill Controls Component
 *
 * Provides drill up/down buttons and hierarchy selection.
 */

import React, { useState } from 'react';
import {
  ChevronUp,
  ChevronDown,
  Layers,
  RotateCcw,
  ChevronRight,
} from 'lucide-react';
import { DrillHierarchy, canDrillDown, canDrillUp } from '../../types/drill';
import { useDrillStore } from '../../stores/drillStore';
import { cn } from '../../lib/utils';

interface DrillControlsProps {
  dashboardId: string;
  chartId: string;
  hierarchies: DrillHierarchy[];
  onDrillChange?: () => void;
  showHierarchySelector?: boolean;
  compact?: boolean;
  className?: string;
}

export const DrillControls: React.FC<DrillControlsProps> = ({
  dashboardId,
  chartId,
  hierarchies,
  onDrillChange,
  showHierarchySelector = true,
  compact = false,
  className,
}) => {
  const [showHierarchyMenu, setShowHierarchyMenu] = useState(false);

  const {
    getChartDrillState,
    drillUp,
    resetDrill,
    setActiveHierarchy,
  } = useDrillStore();

  const chartState = getChartDrillState(dashboardId, chartId);
  const activeHierarchyId = chartState?.activeHierarchyId || hierarchies[0]?.id;
  const activeHierarchy = hierarchies.find((h) => h.id === activeHierarchyId);
  const currentPath = chartState?.currentPath;

  // Check drill capabilities
  const drillDownPossible = activeHierarchy && currentPath
    ? canDrillDown(currentPath, activeHierarchy)
    : !!activeHierarchy;

  const drillUpPossible = currentPath ? canDrillUp(currentPath) : false;

  const handleDrillUp = () => {
    if (activeHierarchy && drillUpPossible) {
      drillUp(dashboardId, chartId, activeHierarchy);
      onDrillChange?.();
    }
  };

  const handleReset = () => {
    resetDrill(dashboardId, chartId);
    onDrillChange?.();
  };

  const handleHierarchyChange = (hierarchyId: string) => {
    setActiveHierarchy(dashboardId, chartId, hierarchyId);
    setShowHierarchyMenu(false);
    onDrillChange?.();
  };

  if (hierarchies.length === 0) {
    return null;
  }

  const currentLevel = currentPath?.currentLevel ?? 0;
  const maxLevel = activeHierarchy?.levels.length ?? 1;
  const currentLevelName = activeHierarchy?.levels[currentLevel]?.label || 'All';

  return (
    <div
      className={cn(
        'flex items-center gap-2',
        compact && 'gap-1',
        className
      )}
    >
      {/* Hierarchy Selector */}
      {showHierarchySelector && hierarchies.length > 1 && (
        <div className="relative">
          <button
            onClick={() => setShowHierarchyMenu(!showHierarchyMenu)}
            className={cn(
              'flex items-center gap-1 px-2 py-1 text-sm rounded-md border border-gray-300',
              'bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500',
              compact && 'px-1.5 py-0.5 text-xs'
            )}
            title="Select hierarchy"
          >
            <Layers className={cn('h-4 w-4 text-gray-500', compact && 'h-3 w-3')} />
            <span className="text-gray-700">{activeHierarchy?.name || 'Select'}</span>
            <ChevronRight
              className={cn(
                'h-3 w-3 text-gray-400 transition-transform',
                showHierarchyMenu && 'rotate-90'
              )}
            />
          </button>

          {/* Hierarchy Dropdown */}
          {showHierarchyMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowHierarchyMenu(false)}
              />
              <div className="absolute z-20 mt-1 w-48 bg-white border border-gray-200 rounded-md shadow-lg py-1">
                {hierarchies.map((h) => (
                  <button
                    key={h.id}
                    onClick={() => handleHierarchyChange(h.id)}
                    className={cn(
                      'w-full text-left px-3 py-2 text-sm hover:bg-gray-100',
                      h.id === activeHierarchyId && 'bg-blue-50 text-blue-700 font-medium'
                    )}
                  >
                    <div className="font-medium">{h.name}</div>
                    <div className="text-xs text-gray-500">
                      {h.levels.map((l) => l.label).join(' > ')}
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Current Level Indicator */}
      <div
        className={cn(
          'px-2 py-1 text-sm bg-gray-100 rounded-md text-gray-600',
          compact && 'px-1.5 py-0.5 text-xs'
        )}
        title={`Level ${currentLevel + 1} of ${maxLevel}`}
      >
        {currentLevelName}
      </div>

      {/* Drill Up Button */}
      <button
        onClick={handleDrillUp}
        disabled={!drillUpPossible}
        className={cn(
          'p-1.5 rounded-md border transition-colors',
          drillUpPossible
            ? 'border-gray-300 bg-white hover:bg-gray-50 text-gray-700'
            : 'border-gray-200 bg-gray-50 text-gray-300 cursor-not-allowed',
          compact && 'p-1'
        )}
        title="Drill up"
      >
        <ChevronUp className={cn('h-4 w-4', compact && 'h-3 w-3')} />
      </button>

      {/* Drill Down Indicator (actual drill-down happens on chart click) */}
      <div
        className={cn(
          'p-1.5 rounded-md border',
          drillDownPossible
            ? 'border-blue-300 bg-blue-50 text-blue-600'
            : 'border-gray-200 bg-gray-50 text-gray-300',
          compact && 'p-1'
        )}
        title={drillDownPossible ? 'Click chart to drill down' : 'At lowest level'}
      >
        <ChevronDown className={cn('h-4 w-4', compact && 'h-3 w-3')} />
      </div>

      {/* Reset Button */}
      {currentLevel > 0 && (
        <button
          onClick={handleReset}
          className={cn(
            'p-1.5 rounded-md border border-gray-300 bg-white hover:bg-gray-50 text-gray-700',
            compact && 'p-1'
          )}
          title="Reset drill"
        >
          <RotateCcw className={cn('h-4 w-4', compact && 'h-3 w-3')} />
        </button>
      )}
    </div>
  );
};

export default DrillControls;
