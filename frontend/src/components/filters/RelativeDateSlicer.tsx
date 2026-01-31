/**
 * Relative Date Slicer Component
 *
 * A slicer for selecting relative date ranges (e.g., "Last 7 Days").
 */

import React, { useState, useCallback } from 'react';
import { Calendar, ChevronDown, X } from 'lucide-react';
import { SlicerConfig, RelativeDateFilter, DEFAULT_RELATIVE_DATE_OPTIONS, RelativeDateOption } from '../../types/filters';
import { useFilterStore } from '../../stores/filterStore';
import { cn } from '../../lib/utils';

interface RelativeDateSlicerProps {
  config: SlicerConfig;
  dashboardId: string;
  options?: RelativeDateOption[];
}

export const RelativeDateSlicer: React.FC<RelativeDateSlicerProps> = ({
  config,
  dashboardId,
  options = config.dateConfig?.relativeOptions || DEFAULT_RELATIVE_DATE_OPTIONS,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const { dashboardFilters, setDateFilter, clearDateFilter } = useFilterStore();

  // Get current date filter
  const currentFilter = dashboardFilters[dashboardId]?.dateFilters?.[config.column] as RelativeDateFilter | undefined;

  // Find selected option
  const selectedOption = options.find(
    (opt) => currentFilter && opt.value === currentFilter.value && opt.unit === currentFilter.unit
  );

  // Handle option selection
  const handleSelect = useCallback(
    (option: RelativeDateOption) => {
      const filter: RelativeDateFilter = {
        column: config.column,
        value: option.value,
        unit: option.unit,
        includeCurrent: true,
      };
      setDateFilter(dashboardId, config.column, filter);
      setIsOpen(false);
    },
    [dashboardId, config.column, setDateFilter]
  );

  // Handle clear
  const handleClear = useCallback(() => {
    clearDateFilter(dashboardId, config.column);
    setIsOpen(false);
  }, [dashboardId, config.column, clearDateFilter]);

  // Get display label
  const getDisplayLabel = () => {
    if (selectedOption) {
      return selectedOption.label;
    }
    return config.label || config.column;
  };

  // Group options by unit for better organization
  const groupedOptions = options.reduce((groups, option) => {
    const group = option.unit;
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push(option);
    return groups;
  }, {} as Record<string, RelativeDateOption[]>);

  const hasFilter = !!currentFilter;

  return (
    <div className="relative" style={{ width: config.width || 200 }}>
      {/* Label */}
      {config.label && (
        <label className="block text-xs font-medium text-gray-500 mb-1">
          {config.label}
        </label>
      )}

      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'w-full flex items-center justify-between px-3 py-2 text-sm rounded-md border',
          'bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500',
          hasFilter ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        )}
      >
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-gray-500" />
          <span className={cn(
            'truncate',
            hasFilter ? 'text-blue-700 font-medium' : 'text-gray-700'
          )}>
            {getDisplayLabel()}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {hasFilter && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleClear();
              }}
              className="p-0.5 hover:bg-gray-200 rounded"
            >
              <X className="h-3 w-3 text-gray-500" />
            </button>
          )}
          <ChevronDown className={cn(
            'h-4 w-4 text-gray-500 transition-transform',
            isOpen && 'rotate-180'
          )} />
        </div>
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute z-20 mt-1 w-56 bg-white border border-gray-200 rounded-md shadow-lg max-h-80 overflow-y-auto">
            {/* Options */}
            <div className="py-1">
              {Object.entries(groupedOptions).map(([unit, unitOptions]) => (
                <div key={unit}>
                  <div className="px-3 py-1.5 text-xs font-medium text-gray-500 bg-gray-50 uppercase">
                    {unit}s
                  </div>
                  {unitOptions.map((option) => {
                    const isSelected =
                      currentFilter &&
                      option.value === currentFilter.value &&
                      option.unit === currentFilter.unit;

                    return (
                      <button
                        key={`${option.unit}-${option.value}`}
                        onClick={() => handleSelect(option)}
                        className={cn(
                          'w-full text-left px-3 py-2 text-sm hover:bg-gray-100',
                          isSelected && 'bg-blue-50 text-blue-700 font-medium'
                        )}
                      >
                        {option.label}
                      </button>
                    );
                  })}
                </div>
              ))}
            </div>

            {/* Clear Button */}
            {hasFilter && (
              <div className="border-t px-3 py-2">
                <button
                  onClick={handleClear}
                  className="w-full text-sm text-gray-600 hover:text-gray-800"
                >
                  Clear selection
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default RelativeDateSlicer;
