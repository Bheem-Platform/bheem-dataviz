/**
 * RLS Condition Editor Component
 *
 * Allows editing of individual RLS conditions within a policy.
 */

import React from 'react';
import { Trash2 } from 'lucide-react';
import {
  RLSCondition,
  RLSOperator,
  RLSFilterType,
  UserAttributeType,
  RLS_OPERATOR_OPTIONS,
  USER_ATTRIBUTE_OPTIONS,
} from '../../types/rls';
import { cn } from '../../lib/utils';

interface RLSConditionEditorProps {
  condition: RLSCondition;
  columns: { column: string; type: string }[];
  onChange: (condition: RLSCondition) => void;
  onDelete: () => void;
}

export const RLSConditionEditor: React.FC<RLSConditionEditorProps> = ({
  condition,
  columns,
  onChange,
  onDelete,
}) => {
  const updateField = <K extends keyof RLSCondition>(field: K, value: RLSCondition[K]) => {
    onChange({ ...condition, [field]: value });
  };

  const needsValue = !['is_null', 'is_not_null'].includes(condition.operator);
  const needsUserAttribute = condition.filterType === 'dynamic';
  const needsExpression = condition.filterType === 'expression';

  return (
    <div className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex-1 grid grid-cols-12 gap-2">
        {/* Column */}
        <div className="col-span-3">
          <label className="block text-xs text-gray-500 mb-1">Column</label>
          <select
            value={condition.column}
            onChange={(e) => updateField('column', e.target.value)}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Select...</option>
            {columns.map((col) => (
              <option key={col.column} value={col.column}>
                {col.column}
              </option>
            ))}
          </select>
        </div>

        {/* Operator */}
        <div className="col-span-2">
          <label className="block text-xs text-gray-500 mb-1">Operator</label>
          <select
            value={condition.operator}
            onChange={(e) => updateField('operator', e.target.value as RLSOperator)}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {RLS_OPERATOR_OPTIONS.map((op) => (
              <option key={op.value} value={op.value}>
                {op.label}
              </option>
            ))}
          </select>
        </div>

        {/* Filter Type */}
        <div className="col-span-2">
          <label className="block text-xs text-gray-500 mb-1">Filter Type</label>
          <select
            value={condition.filterType}
            onChange={(e) => updateField('filterType', e.target.value as RLSFilterType)}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="static">Static Value</option>
            <option value="dynamic">User Attribute</option>
            <option value="expression">Expression</option>
          </select>
        </div>

        {/* Value / User Attribute / Expression */}
        {needsValue && (
          <div className="col-span-4">
            {condition.filterType === 'static' && (
              <>
                <label className="block text-xs text-gray-500 mb-1">Value</label>
                <input
                  type="text"
                  value={condition.value || ''}
                  onChange={(e) => updateField('value', e.target.value)}
                  placeholder="Enter value..."
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </>
            )}

            {condition.filterType === 'dynamic' && (
              <>
                <label className="block text-xs text-gray-500 mb-1">User Attribute</label>
                <div className="flex gap-2">
                  <select
                    value={condition.userAttribute || ''}
                    onChange={(e) => updateField('userAttribute', e.target.value as UserAttributeType)}
                    className="flex-1 px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="">Select...</option>
                    {USER_ATTRIBUTE_OPTIONS.map((attr) => (
                      <option key={attr.value} value={attr.value}>
                        {attr.label}
                      </option>
                    ))}
                  </select>
                  {condition.userAttribute === 'custom' && (
                    <input
                      type="text"
                      value={condition.customAttribute || ''}
                      onChange={(e) => updateField('customAttribute', e.target.value)}
                      placeholder="Attribute name"
                      className="flex-1 px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  )}
                </div>
              </>
            )}

            {condition.filterType === 'expression' && (
              <>
                <label className="block text-xs text-gray-500 mb-1">Expression</label>
                <input
                  type="text"
                  value={condition.expression || ''}
                  onChange={(e) => updateField('expression', e.target.value)}
                  placeholder="e.g., CURRENT_USER()"
                  className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </>
            )}
          </div>
        )}
      </div>

      {/* Delete Button */}
      <button
        onClick={onDelete}
        className="mt-5 p-1.5 text-gray-400 hover:text-red-600 rounded transition-colors"
        title="Remove condition"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </div>
  );
};

export default RLSConditionEditor;
