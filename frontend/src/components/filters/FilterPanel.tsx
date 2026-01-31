/**
 * Filter Panel Component
 *
 * A panel that displays all slicers for a dashboard or chart.
 */

import React, { useEffect, useState, useCallback } from 'react';
import { Filter, X, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import {
  SlicerConfig,
  FilterType,
  FilterOptionsResponse,
  MultiColumnFilterOptionsResponse,
} from '../../types/filters';
import { useFilterStore } from '../../stores/filterStore';
import { DropdownSlicer } from './DropdownSlicer';
import { DateRangeSlicer } from './DateRangeSlicer';
import { RelativeDateSlicer } from './RelativeDateSlicer';
import { NumericRangeSlicer } from './NumericRangeSlicer';
import { cn } from '../../lib/utils';
import api from '../../lib/api';

interface FilterPanelProps {
  dashboardId: string;
  connectionId: string;
  schemaName: string;
  tableName: string;
  slicers?: SlicerConfig[];
  position?: 'left' | 'right' | 'top';
  collapsible?: boolean;
  onFiltersChange?: () => void;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  dashboardId,
  connectionId,
  schemaName,
  tableName,
  slicers: initialSlicers = [],
  position = 'right',
  collapsible = true,
  onFiltersChange,
}) => {
  const [slicers, setSlicers] = useState<SlicerConfig[]>(initialSlicers);
  const [filterOptions, setFilterOptions] = useState<Record<string, FilterOptionsResponse>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const {
    filterPaneVisible,
    setFilterPaneVisible,
    clearAllFilters,
    hasActiveFilters,
    dashboardFilters,
  } = useFilterStore();

  // Fetch filter options for all slicers
  const fetchFilterOptions = useCallback(async () => {
    if (slicers.length === 0) return;

    setIsLoading(true);
    try {
      const columns = slicers
        .filter((s) => s.type === 'dropdown' || s.type === 'list' || s.type === 'tile')
        .map((s) => s.column);

      if (columns.length > 0) {
        const response = await api.post<MultiColumnFilterOptionsResponse>(
          `/filters/options/${connectionId}/${schemaName}/${tableName}`,
          columns
        );
        setFilterOptions(response.data.columns);
      }

      // Fetch numeric options for between slicers
      for (const slicer of slicers) {
        if (slicer.type === 'between') {
          try {
            const response = await api.get<FilterOptionsResponse>(
              `/filters/options/${connectionId}/${schemaName}/${tableName}/${slicer.column}`
            );
            setFilterOptions((prev) => ({
              ...prev,
              [slicer.column]: response.data,
            }));
          } catch (error) {
            console.error(`Failed to fetch options for ${slicer.column}:`, error);
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch filter options:', error);
    } finally {
      setIsLoading(false);
    }
  }, [slicers, connectionId, schemaName, tableName]);

  // Fetch options on mount and when slicers change
  useEffect(() => {
    fetchFilterOptions();
  }, [fetchFilterOptions]);

  // Notify parent when filters change
  useEffect(() => {
    onFiltersChange?.();
  }, [dashboardFilters, onFiltersChange]);

  // Handle clear all filters
  const handleClearAll = () => {
    clearAllFilters(dashboardId);
  };

  // Handle refresh options
  const handleRefresh = () => {
    fetchFilterOptions();
  };

  // Render appropriate slicer component
  const renderSlicer = (config: SlicerConfig) => {
    const options = filterOptions[config.column];

    switch (config.type) {
      case 'dropdown':
      case 'list':
      case 'tile':
        return (
          <DropdownSlicer
            key={config.column}
            config={config}
            dashboardId={dashboardId}
            options={options?.values || []}
            isLoading={isLoading}
          />
        );

      case 'date_range':
        return (
          <DateRangeSlicer
            key={config.column}
            config={config}
            dashboardId={dashboardId}
            minDate={options?.minDate}
            maxDate={options?.maxDate}
          />
        );

      case 'relative_date':
        return (
          <RelativeDateSlicer
            key={config.column}
            config={config}
            dashboardId={dashboardId}
          />
        );

      case 'between':
        return (
          <NumericRangeSlicer
            key={config.column}
            config={config}
            dashboardId={dashboardId}
            minValue={options?.minValue as number}
            maxValue={options?.maxValue as number}
          />
        );

      default:
        return (
          <DropdownSlicer
            key={config.column}
            config={config}
            dashboardId={dashboardId}
            options={options?.values || []}
            isLoading={isLoading}
          />
        );
    }
  };

  // Don't render if not visible
  if (!filterPaneVisible) {
    return (
      <button
        onClick={() => setFilterPaneVisible(true)}
        className="fixed right-4 top-20 z-40 p-2 bg-white border border-gray-200 rounded-md shadow-sm hover:bg-gray-50"
        title="Show filters"
      >
        <Filter className="h-5 w-5 text-gray-600" />
      </button>
    );
  }

  const hasFilters = hasActiveFilters(dashboardId);

  // Collapsed state
  if (collapsible && isCollapsed) {
    return (
      <div
        className={cn(
          'fixed z-40 bg-white border border-gray-200 shadow-sm',
          position === 'left' && 'left-0 top-20 h-[calc(100vh-5rem)] border-l-0 rounded-r-md',
          position === 'right' && 'right-0 top-20 h-[calc(100vh-5rem)] border-r-0 rounded-l-md',
          position === 'top' && 'top-16 left-0 right-0 border-t-0 rounded-b-md'
        )}
      >
        <button
          onClick={() => setIsCollapsed(false)}
          className="p-2 hover:bg-gray-100 w-full h-full flex items-center justify-center"
          title="Expand filters"
        >
          {position === 'left' ? (
            <ChevronRight className="h-5 w-5 text-gray-600" />
          ) : position === 'right' ? (
            <ChevronLeft className="h-5 w-5 text-gray-600" />
          ) : (
            <Filter className="h-5 w-5 text-gray-600" />
          )}
          {hasFilters && (
            <span className="absolute top-2 right-2 w-2 h-2 bg-blue-500 rounded-full" />
          )}
        </button>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'bg-white border border-gray-200 shadow-sm overflow-hidden flex flex-col',
        position === 'left' && 'fixed left-0 top-20 h-[calc(100vh-5rem)] w-64 border-l-0 rounded-r-md z-40',
        position === 'right' && 'fixed right-0 top-20 h-[calc(100vh-5rem)] w-64 border-r-0 rounded-l-md z-40',
        position === 'top' && 'w-full border-x-0 border-t-0'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-50">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-600" />
          <span className="font-medium text-sm text-gray-700">Filters</span>
          {hasFilters && (
            <span className="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">
              Active
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleRefresh}
            className="p-1 hover:bg-gray-200 rounded"
            title="Refresh options"
          >
            <RefreshCw className={cn(
              'h-4 w-4 text-gray-500',
              isLoading && 'animate-spin'
            )} />
          </button>
          {collapsible && (
            <button
              onClick={() => setIsCollapsed(true)}
              className="p-1 hover:bg-gray-200 rounded"
              title="Collapse"
            >
              {position === 'left' ? (
                <ChevronLeft className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-500" />
              )}
            </button>
          )}
          <button
            onClick={() => setFilterPaneVisible(false)}
            className="p-1 hover:bg-gray-200 rounded"
            title="Hide filters"
          >
            <X className="h-4 w-4 text-gray-500" />
          </button>
        </div>
      </div>

      {/* Slicers */}
      <div
        className={cn(
          'flex-1 overflow-y-auto p-4',
          position === 'top' && 'flex flex-wrap gap-4'
        )}
      >
        {slicers.length === 0 ? (
          <div className="text-sm text-gray-500 text-center py-8">
            No filters configured
          </div>
        ) : (
          <div className={cn(
            position === 'top' ? 'flex flex-wrap gap-4' : 'space-y-4'
          )}>
            {slicers
              .filter((s) => s.visible !== false)
              .sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
              .map(renderSlicer)}
          </div>
        )}
      </div>

      {/* Footer */}
      {hasFilters && (
        <div className="px-4 py-3 border-t bg-gray-50">
          <button
            onClick={handleClearAll}
            className="w-full px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-100"
          >
            Clear All Filters
          </button>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;
