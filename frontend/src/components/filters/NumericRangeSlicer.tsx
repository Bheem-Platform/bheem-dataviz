/**
 * Numeric Range Slicer Component
 *
 * A slider/input for selecting numeric ranges.
 */

import React, { useState, useCallback, useEffect } from 'react';
import { ChevronDown, X } from 'lucide-react';
import { SlicerConfig } from '../../types/filters';
import { useFilterStore } from '../../stores/filterStore';
import { cn } from '../../lib/utils';

interface NumericRangeSlicerProps {
  config: SlicerConfig;
  dashboardId: string;
  minValue?: number;
  maxValue?: number;
}

export const NumericRangeSlicer: React.FC<NumericRangeSlicerProps> = ({
  config,
  dashboardId,
  minValue = config.numericConfig?.minValue ?? 0,
  maxValue = config.numericConfig?.maxValue ?? 100,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const {
    setFilterSelection,
    clearFilterSelection,
    getFilterSelectionForColumn,
  } = useFilterStore();

  // Get current selection
  const currentSelection = getFilterSelectionForColumn(dashboardId, config.column);

  // Parse current range from selection
  const [rangeMin, setRangeMin] = useState<number>(
    currentSelection[0]?.min ?? minValue
  );
  const [rangeMax, setRangeMax] = useState<number>(
    currentSelection[0]?.max ?? maxValue
  );

  // Update local state when selection changes
  useEffect(() => {
    if (currentSelection.length > 0 && currentSelection[0]) {
      setRangeMin(currentSelection[0].min ?? minValue);
      setRangeMax(currentSelection[0].max ?? maxValue);
    } else {
      setRangeMin(minValue);
      setRangeMax(maxValue);
    }
  }, [currentSelection, minValue, maxValue]);

  // Apply range filter
  const handleApply = useCallback(() => {
    const isDefault = rangeMin === minValue && rangeMax === maxValue;
    if (isDefault) {
      clearFilterSelection(dashboardId, config.column);
    } else {
      setFilterSelection(
        dashboardId,
        config.column,
        [{ min: rangeMin, max: rangeMax }],
        'between'
      );
    }
    setIsOpen(false);
  }, [rangeMin, rangeMax, minValue, maxValue, dashboardId, config.column, setFilterSelection, clearFilterSelection]);

  // Clear filter
  const handleClear = useCallback(() => {
    setRangeMin(minValue);
    setRangeMax(maxValue);
    clearFilterSelection(dashboardId, config.column);
    setIsOpen(false);
  }, [minValue, maxValue, dashboardId, config.column, clearFilterSelection]);

  // Format value for display
  const formatValue = (value: number) => {
    const format = config.numericConfig?.format || '{value}';
    return format.replace('{value}', value.toLocaleString());
  };

  // Get display label
  const getDisplayLabel = () => {
    const hasFilter = currentSelection.length > 0 && currentSelection[0];
    if (hasFilter) {
      return `${formatValue(rangeMin)} - ${formatValue(rangeMax)}`;
    }
    return config.label || config.column;
  };

  const hasFilter = currentSelection.length > 0;
  const step = config.numericConfig?.step ?? 1;

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
        <span className={cn(
          'truncate',
          hasFilter ? 'text-blue-700 font-medium' : 'text-gray-700'
        )}>
          {getDisplayLabel()}
        </span>
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
              {/* Range Display */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Range:</span>
                <span className="font-medium">
                  {formatValue(rangeMin)} - {formatValue(rangeMax)}
                </span>
              </div>

              {/* Min Value Input */}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Minimum
                </label>
                <input
                  type="number"
                  value={rangeMin}
                  onChange={(e) => setRangeMin(Number(e.target.value))}
                  min={minValue}
                  max={rangeMax}
                  step={step}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              {/* Range Slider */}
              <div className="pt-2">
                <input
                  type="range"
                  min={minValue}
                  max={maxValue}
                  step={step}
                  value={rangeMin}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    if (val <= rangeMax) setRangeMin(val);
                  }}
                  className="w-full accent-blue-500"
                />
                <input
                  type="range"
                  min={minValue}
                  max={maxValue}
                  step={step}
                  value={rangeMax}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    if (val >= rangeMin) setRangeMax(val);
                  }}
                  className="w-full accent-blue-500"
                />
              </div>

              {/* Max Value Input */}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Maximum
                </label>
                <input
                  type="number"
                  value={rangeMax}
                  onChange={(e) => setRangeMax(Number(e.target.value))}
                  min={rangeMin}
                  max={maxValue}
                  step={step}
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

export default NumericRangeSlicer;
