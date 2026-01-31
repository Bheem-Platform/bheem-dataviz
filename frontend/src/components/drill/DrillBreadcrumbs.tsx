/**
 * Drill Breadcrumbs Component
 *
 * Displays the current drill path as clickable breadcrumbs.
 */

import React from 'react';
import { ChevronRight, Home } from 'lucide-react';
import { DrillHierarchy } from '../../types/drill';
import { useDrillStore } from '../../stores/drillStore';
import { cn } from '../../lib/utils';

interface DrillBreadcrumbsProps {
  dashboardId: string;
  chartId: string;
  hierarchy: DrillHierarchy;
  onLevelClick?: (level: number) => void;
  className?: string;
}

export const DrillBreadcrumbs: React.FC<DrillBreadcrumbsProps> = ({
  dashboardId,
  chartId,
  hierarchy,
  onLevelClick,
  className,
}) => {
  const { getBreadcrumbs, drillToLevel } = useDrillStore();

  const breadcrumbs = getBreadcrumbs(dashboardId, chartId, hierarchy);

  const handleClick = (level: number) => {
    drillToLevel(dashboardId, chartId, hierarchy, level);
    onLevelClick?.(level);
  };

  if (breadcrumbs.length <= 1) {
    return null; // Don't show breadcrumbs at root level
  }

  return (
    <nav
      className={cn(
        'flex items-center gap-1 text-sm overflow-x-auto py-1',
        className
      )}
      aria-label="Drill breadcrumbs"
    >
      {breadcrumbs.map((crumb, index) => (
        <React.Fragment key={crumb.level}>
          {index > 0 && (
            <ChevronRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
          )}
          <button
            onClick={() => handleClick(crumb.level)}
            disabled={crumb.isCurrent}
            className={cn(
              'flex items-center gap-1 px-2 py-1 rounded-md whitespace-nowrap transition-colors',
              crumb.isCurrent
                ? 'bg-blue-100 text-blue-700 font-medium cursor-default'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
            )}
          >
            {index === 0 && <Home className="h-3 w-3" />}
            <span>{crumb.label}</span>
          </button>
        </React.Fragment>
      ))}
    </nav>
  );
};

export default DrillBreadcrumbs;
