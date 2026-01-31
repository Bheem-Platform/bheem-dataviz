/**
 * Hierarchy Slicer Component
 *
 * A tree-like slicer for hierarchical data (e.g., Region > Country > City).
 */

import React, { useState, useCallback, useMemo } from 'react';
import { ChevronRight, ChevronDown, Check, X, Search } from 'lucide-react';
import { SlicerConfig, FilterOptionValue, HierarchyLevel } from '../../types/filters';
import { useFilterStore } from '../../stores/filterStore';
import { cn } from '../../lib/utils';

interface HierarchySlicerProps {
  config: SlicerConfig;
  dashboardId: string;
  options: FilterOptionValue[];
  levels: HierarchyLevel[];
  isLoading?: boolean;
  onSearch?: (query: string) => void;
}

interface TreeNodeProps {
  node: FilterOptionValue;
  level: number;
  selectedValues: Map<string, any[]>;
  onToggle: (column: string, value: any, isSelected: boolean) => void;
  config: SlicerConfig;
  levels: HierarchyLevel[];
  expandedNodes: Set<string>;
  onExpandToggle: (nodeId: string) => void;
  searchQuery: string;
}

const TreeNode: React.FC<TreeNodeProps> = ({
  node,
  level,
  selectedValues,
  onToggle,
  config,
  levels,
  expandedNodes,
  onExpandToggle,
  searchQuery,
}) => {
  const currentLevel = levels[level];
  const nodeId = `${currentLevel?.column || 'root'}-${node.value}`;
  const isExpanded = expandedNodes.has(nodeId);
  const hasChildren = node.children && node.children.length > 0;

  const columnSelections = selectedValues.get(currentLevel?.column || '') || [];
  const isSelected = columnSelections.includes(node.value);

  // Filter children by search query
  const visibleChildren = useMemo(() => {
    if (!node.children || !searchQuery) return node.children;
    return node.children.filter((child) => {
      const label = (child.label || String(child.value)).toLowerCase();
      return label.includes(searchQuery.toLowerCase());
    });
  }, [node.children, searchQuery]);

  const matchesSearch = !searchQuery ||
    (node.label || String(node.value)).toLowerCase().includes(searchQuery.toLowerCase());

  // Don't render nodes that don't match search and have no matching children
  if (!matchesSearch && (!visibleChildren || visibleChildren.length === 0)) {
    return null;
  }

  return (
    <div className="select-none">
      <div
        className={cn(
          'flex items-center py-1.5 px-2 hover:bg-gray-100 cursor-pointer rounded',
          isSelected && 'bg-blue-50'
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
      >
        {/* Expand/Collapse Toggle */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            if (hasChildren) {
              onExpandToggle(nodeId);
            }
          }}
          className={cn(
            'w-5 h-5 flex items-center justify-center mr-1',
            !hasChildren && 'invisible'
          )}
        >
          {hasChildren && (
            isExpanded ? (
              <ChevronDown className="h-4 w-4 text-gray-500" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-500" />
            )
          )}
        </button>

        {/* Selection Checkbox */}
        <button
          onClick={() => onToggle(currentLevel?.column || '', node.value, isSelected)}
          className={cn(
            'w-4 h-4 border rounded flex items-center justify-center mr-2 flex-shrink-0',
            isSelected
              ? 'bg-blue-500 border-blue-500'
              : 'border-gray-300 hover:border-gray-400'
          )}
        >
          {isSelected && <Check className="h-3 w-3 text-white" />}
        </button>

        {/* Label */}
        <span
          className={cn(
            'text-sm truncate flex-1',
            isSelected && 'font-medium text-blue-700'
          )}
          onClick={() => onToggle(currentLevel?.column || '', node.value, isSelected)}
        >
          {node.label || String(node.value)}
        </span>

        {/* Count */}
        {config.showCount && node.count !== undefined && (
          <span className="text-xs text-gray-400 ml-2">
            {node.count.toLocaleString()}
          </span>
        )}
      </div>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div>
          {visibleChildren?.map((child, idx) => (
            <TreeNode
              key={`${child.value}-${idx}`}
              node={child}
              level={level + 1}
              selectedValues={selectedValues}
              onToggle={onToggle}
              config={config}
              levels={levels}
              expandedNodes={expandedNodes}
              onExpandToggle={onExpandToggle}
              searchQuery={searchQuery}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const HierarchySlicer: React.FC<HierarchySlicerProps> = ({
  config,
  dashboardId,
  options,
  levels,
  isLoading = false,
  onSearch,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(() => {
    // Expand all nodes if configured
    if (config.hierarchyConfig?.expandAll) {
      const expanded = new Set<string>();
      const addAllNodes = (nodes: FilterOptionValue[], level: number) => {
        nodes.forEach((node) => {
          const currentLevel = levels[level];
          if (currentLevel) {
            expanded.add(`${currentLevel.column}-${node.value}`);
          }
          if (node.children) {
            addAllNodes(node.children, level + 1);
          }
        });
      };
      addAllNodes(options, 0);
      return expanded;
    }
    return new Set();
  });

  const {
    setFilterSelection,
    clearFilterSelection,
    getFilterSelectionForColumn,
  } = useFilterStore();

  // Build selected values map for all hierarchy levels
  const selectedValues = useMemo(() => {
    const map = new Map<string, any[]>();
    levels.forEach((level) => {
      map.set(level.column, getFilterSelectionForColumn(dashboardId, level.column));
    });
    return map;
  }, [levels, dashboardId, getFilterSelectionForColumn]);

  // Count total selections
  const totalSelections = useMemo(() => {
    let count = 0;
    selectedValues.forEach((values) => {
      count += values.length;
    });
    return count;
  }, [selectedValues]);

  // Handle node toggle
  const handleToggle = useCallback(
    (column: string, value: any, isSelected: boolean) => {
      const currentSelections = selectedValues.get(column) || [];
      const singleSelectPerLevel = config.hierarchyConfig?.singleSelectPerLevel;

      if (isSelected) {
        // Remove selection
        const newSelections = currentSelections.filter((v) => v !== value);
        if (newSelections.length > 0) {
          setFilterSelection(dashboardId, column, newSelections);
        } else {
          clearFilterSelection(dashboardId, column);
        }
      } else {
        // Add selection
        if (singleSelectPerLevel) {
          setFilterSelection(dashboardId, column, [value]);
        } else {
          setFilterSelection(dashboardId, column, [...currentSelections, value]);
        }
      }
    },
    [selectedValues, config.hierarchyConfig?.singleSelectPerLevel, dashboardId, setFilterSelection, clearFilterSelection]
  );

  // Handle expand toggle
  const handleExpandToggle = useCallback((nodeId: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  }, []);

  // Handle clear all
  const handleClearAll = useCallback(() => {
    levels.forEach((level) => {
      clearFilterSelection(dashboardId, level.column);
    });
    setSearchQuery('');
  }, [levels, dashboardId, clearFilterSelection]);

  // Handle expand all
  const handleExpandAll = useCallback(() => {
    const expanded = new Set<string>();
    const addAllNodes = (nodes: FilterOptionValue[], level: number) => {
      nodes.forEach((node) => {
        const currentLevel = levels[level];
        if (currentLevel) {
          expanded.add(`${currentLevel.column}-${node.value}`);
        }
        if (node.children) {
          addAllNodes(node.children, level + 1);
        }
      });
    };
    addAllNodes(options, 0);
    setExpandedNodes(expanded);
  }, [options, levels]);

  // Handle collapse all
  const handleCollapseAll = useCallback(() => {
    setExpandedNodes(new Set());
  }, []);

  // Handle search
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    onSearch?.(query);
  };

  // Get display label
  const getDisplayLabel = () => {
    if (totalSelections === 0) {
      return config.label || 'Select...';
    }
    return `${totalSelections} selected`;
  };

  return (
    <div className="relative" style={{ width: config.width || 280 }}>
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
          totalSelections > 0 ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        )}
      >
        <span
          className={cn(
            'truncate',
            totalSelections > 0 ? 'text-blue-700 font-medium' : 'text-gray-700'
          )}
        >
          {getDisplayLabel()}
        </span>
        <div className="flex items-center gap-1">
          {totalSelections > 0 && (
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
          <ChevronDown
            className={cn(
              'h-4 w-4 text-gray-500 transition-transform',
              isOpen && 'rotate-180'
            )}
          />
        </div>
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />

          {/* Dropdown */}
          <div className="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg min-w-[280px]">
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

            {/* Toolbar */}
            <div className="flex items-center justify-between px-3 py-2 border-b bg-gray-50 text-xs">
              <div className="flex items-center gap-2">
                <button
                  onClick={handleExpandAll}
                  className="text-gray-600 hover:text-gray-800"
                >
                  Expand All
                </button>
                <span className="text-gray-300">|</span>
                <button
                  onClick={handleCollapseAll}
                  className="text-gray-600 hover:text-gray-800"
                >
                  Collapse All
                </button>
              </div>
              <button
                onClick={handleClearAll}
                className="text-gray-600 hover:text-gray-800"
              >
                Clear
              </button>
            </div>

            {/* Hierarchy Levels Header */}
            {levels.length > 0 && (
              <div className="px-3 py-1.5 border-b bg-gray-50 text-xs text-gray-500 flex gap-2">
                {levels.map((level, idx) => (
                  <span key={level.column}>
                    {level.label}
                    {idx < levels.length - 1 && ' →'}
                  </span>
                ))}
              </div>
            )}

            {/* Tree View */}
            <div className="max-h-72 overflow-y-auto p-1">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500" />
                </div>
              ) : options.length === 0 ? (
                <div className="px-3 py-4 text-sm text-gray-500 text-center">
                  No options found
                </div>
              ) : (
                options.map((option, idx) => (
                  <TreeNode
                    key={`${option.value}-${idx}`}
                    node={option}
                    level={0}
                    selectedValues={selectedValues}
                    onToggle={handleToggle}
                    config={config}
                    levels={levels}
                    expandedNodes={expandedNodes}
                    onExpandToggle={handleExpandToggle}
                    searchQuery={searchQuery}
                  />
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default HierarchySlicer;
