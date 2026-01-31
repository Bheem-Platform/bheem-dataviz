/**
 * Dropdown Slicer Component
 *
 * A multi-select dropdown filter for categorical data.
 */

import React, { useState, useMemo, useCallback } from 'react';
import { Check, ChevronDown, Search, X } from 'lucide-react';
import { SlicerConfig, FilterOptionValue } from '../../types/filters';
import { useFilterStore } from '../../stores/filterStore';
import { cn } from '../../lib/utils';

interface DropdownSlicerProps {
  config: SlicerConfig;
  dashboardId: string;
  options: FilterOptionValue[];
  isLoading?: boolean;
  onSearch?: (query: string) => void;
}

export const DropdownSlicer: React.FC<DropdownSlicerProps> = ({
  config,
  dashboardId,
  options,
  isLoading = false,
  onSearch,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const {
    setFilterSelection,
    clearFilterSelection,
    getFilterSelectionForColumn,
  } = useFilterStore();

  const selectedValues = getFilterSelectionForColumn(dashboardId, config.column);

  // Filter options based on search
  const filteredOptions = useMemo(() => {
    if (!searchQuery) return options;
    const query = searchQuery.toLowerCase();
    return options.filter((opt) => {
      const label = opt.label || String(opt.value);
      return label.toLowerCase().includes(query);
    });
  }, [options, searchQuery]);

  // Handle selection toggle
  const handleToggleValue = useCallback(
    (value: any) => {
      const isSelected = selectedValues.includes(value);

      if (config.multiSelect) {
        const newValues = isSelected
          ? selectedValues.filter((v) => v !== value)
          : [...selectedValues, value];

        if (newValues.length > 0) {
          setFilterSelection(dashboardId, config.column, newValues);
        } else {
          clearFilterSelection(dashboardId, config.column);
        }
      } else {
        // Single select
        if (isSelected) {
          clearFilterSelection(dashboardId, config.column);
        } else {
          setFilterSelection(dashboardId, config.column, [value]);
        }
        setIsOpen(false);
      }
    },
    [selectedValues, config.multiSelect, config.column, dashboardId, setFilterSelection, clearFilterSelection]
  );

  // Handle select all
  const handleSelectAll = useCallback(() => {
    const allValues = filteredOptions.map((opt) => opt.value);
    setFilterSelection(dashboardId, config.column, allValues);
  }, [filteredOptions, dashboardId, config.column, setFilterSelection]);

  // Handle clear all
  const handleClearAll = useCallback(() => {
    clearFilterSelection(dashboardId, config.column);
    setSearchQuery('');
  }, [dashboardId, config.column, clearFilterSelection]);

  // Handle search
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    onSearch?.(query);
  };

  // Get display label
  const getDisplayLabel = () => {
    if (selectedValues.length === 0) {
      return config.label || config.column;
    }
    if (selectedValues.length === 1) {
      const selected = options.find((opt) => opt.value === selectedValues[0]);
      return selected?.label || String(selectedValues[0]);
    }
    return `${selectedValues.length} selected`;
  };

  const isAllSelected = selectedValues.length === options.length && options.length > 0;

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
          selectedValues.length > 0 ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        )}
      >
        <span className={cn(
          'truncate',
          selectedValues.length > 0 ? 'text-blue-700 font-medium' : 'text-gray-700'
        )}>
          {getDisplayLabel()}
        </span>
        <div className="flex items-center gap-1">
          {selectedValues.length > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleClearAll();
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
          <div className="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg">
            {/* Search */}
            {config.searchEnabled && (
              <div className="p-2 border-b">
                <div className="relative">
                  <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={handleSearchChange}
                    placeholder="Search..."
                    className="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    autoFocus
                  />
                </div>
              </div>
            )}

            {/* Select All / Clear All */}
            {config.selectAllEnabled && config.multiSelect && (
              <div className="flex items-center justify-between px-3 py-2 border-b bg-gray-50 text-xs">
                <button
                  onClick={handleSelectAll}
                  className="text-blue-600 hover:text-blue-800"
                >
                  Select All
                </button>
                <button
                  onClick={handleClearAll}
                  className="text-gray-600 hover:text-gray-800"
                >
                  Clear
                </button>
              </div>
            )}

            {/* Options List */}
            <div className="max-h-60 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500" />
                </div>
              ) : filteredOptions.length === 0 ? (
                <div className="px-3 py-4 text-sm text-gray-500 text-center">
                  No options found
                </div>
              ) : (
                filteredOptions.map((option) => {
                  const isSelected = selectedValues.includes(option.value);
                  return (
                    <button
                      key={String(option.value)}
                      onClick={() => handleToggleValue(option.value)}
                      className={cn(
                        'w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-gray-100',
                        isSelected && 'bg-blue-50'
                      )}
                    >
                      <div className="flex items-center gap-2">
                        {config.multiSelect && (
                          <div className={cn(
                            'w-4 h-4 border rounded flex items-center justify-center',
                            isSelected
                              ? 'bg-blue-500 border-blue-500'
                              : 'border-gray-300'
                          )}>
                            {isSelected && <Check className="h-3 w-3 text-white" />}
                          </div>
                        )}
                        <span className={cn(
                          'truncate',
                          isSelected && 'font-medium text-blue-700'
                        )}>
                          {option.label || String(option.value)}
                        </span>
                      </div>
                      {config.showCount && option.count !== undefined && (
                        <span className="text-xs text-gray-400">
                          {option.count.toLocaleString()}
                        </span>
                      )}
                    </button>
                  );
                })
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DropdownSlicer;
