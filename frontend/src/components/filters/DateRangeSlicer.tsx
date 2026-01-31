/**
 * Date Range Slicer Component
 *
 * A date picker for selecting date ranges.
 */

import React, { useState, useCallback } from 'react';
import { Calendar, ChevronDown, X } from 'lucide-react';
import { format, parseISO, isValid } from 'date-fns';
import { SlicerConfig, DateRangeFilter } from '../../types/filters';
import { useFilterStore } from '../../stores/filterStore';
import { cn } from '../../lib/utils';

interface DateRangeSlicerProps {
  config: SlicerConfig;
  dashboardId: string;
  minDate?: string;
  maxDate?: string;
}

export const DateRangeSlicer: React.FC<DateRangeSlicerProps> = ({
  config,
  dashboardId,
  minDate,
  maxDate,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const { dashboardFilters, setDateFilter, clearDateFilter } = useFilterStore();

  // Get current date filter
  const currentFilter = dashboardFilters[dashboardId]?.dateFilters?.[config.column] as DateRangeFilter | undefined;

  const [startDate, setStartDate] = useState<string>(currentFilter?.startDate || '');
  const [endDate, setEndDate] = useState<string>(currentFilter?.endDate || '');

  // Apply date range filter
  const handleApply = useCallback(() => {
    if (startDate || endDate) {
      const filter: DateRangeFilter = {
        column: config.column,
        startDate: startDate || undefined,
        endDate: endDate || undefined,
        includeStart: true,
        includeEnd: true,
      };
      setDateFilter(dashboardId, config.column, filter);
    }
    setIsOpen(false);
  }, [startDate, endDate, dashboardId, config.column, setDateFilter]);

  // Clear date range filter
  const handleClear = useCallback(() => {
    setStartDate('');
    setEndDate('');
    clearDateFilter(dashboardId, config.column);
    setIsOpen(false);
  }, [dashboardId, config.column, clearDateFilter]);

  // Format date for display
  const formatDateForDisplay = (dateStr?: string) => {
    if (!dateStr) return '';
    try {
      const date = parseISO(dateStr);
      return isValid(date) ? format(date, 'MMM d, yyyy') : dateStr;
    } catch {
      return dateStr;
    }
  };

  // Get display label
  const getDisplayLabel = () => {
    if (!currentFilter?.startDate && !currentFilter?.endDate) {
      return config.label || config.column;
    }

    const start = formatDateForDisplay(currentFilter.startDate);
    const end = formatDateForDisplay(currentFilter.endDate);

    if (start && end) {
      return `${start} - ${end}`;
    }
    if (start) {
      return `From ${start}`;
    }
    if (end) {
      return `Until ${end}`;
    }
    return config.label || config.column;
  };

  const hasFilter = currentFilter?.startDate || currentFilter?.endDate;

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
          <div className="absolute z-20 mt-1 w-72 bg-white border border-gray-200 rounded-md shadow-lg p-4">
            <div className="space-y-4">
              {/* Start Date */}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  min={minDate}
                  max={endDate || maxDate}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              {/* End Date */}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate || minDate}
                  max={maxDate}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              {/* Actions */}
              <div className="flex items-center justify-end gap-2 pt-2 border-t">
                <button
                  onClick={handleClear}
                  className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800"
                >
                  Clear
                </button>
                <button
                  onClick={handleApply}
                  className="px-3 py-1.5 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600"
                >
                  Apply
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DateRangeSlicer;
