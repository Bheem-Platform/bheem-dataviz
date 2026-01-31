/**
 * Format Rule Editor Component
 *
 * Editor for creating/editing conditional formatting rules.
 */

import React, { useState } from 'react';
import { Plus, Trash2, GripVertical, ChevronDown, ChevronUp } from 'lucide-react';
import {
  ConditionalFormat,
  FormatType,
  FormatRule,
  ComparisonOperator,
  createDefaultFormat,
  colorToHex,
} from '../../types/conditionalFormat';
import { ColorPicker } from './ColorPicker';
import { GradientPicker } from './GradientPicker';
import { cn } from '../../lib/utils';

interface FormatRuleEditorProps {
  format: ConditionalFormat;
  onChange: (format: ConditionalFormat) => void;
  onDelete: () => void;
  columns: { name: string; label: string; type: string }[];
  className?: string;
}

const COMPARISON_OPERATORS: { value: ComparisonOperator; label: string; needsValue: boolean; needsValue2: boolean }[] = [
  { value: 'greater_than', label: 'Greater than', needsValue: true, needsValue2: false },
  { value: 'greater_than_or_equal', label: 'Greater than or equal', needsValue: true, needsValue2: false },
  { value: 'less_than', label: 'Less than', needsValue: true, needsValue2: false },
  { value: 'less_than_or_equal', label: 'Less than or equal', needsValue: true, needsValue2: false },
  { value: 'equals', label: 'Equals', needsValue: true, needsValue2: false },
  { value: 'not_equals', label: 'Not equals', needsValue: true, needsValue2: false },
  { value: 'between', label: 'Between', needsValue: true, needsValue2: true },
  { value: 'not_between', label: 'Not between', needsValue: true, needsValue2: true },
  { value: 'contains', label: 'Contains', needsValue: true, needsValue2: false },
  { value: 'not_contains', label: 'Does not contain', needsValue: true, needsValue2: false },
  { value: 'starts_with', label: 'Starts with', needsValue: true, needsValue2: false },
  { value: 'ends_with', label: 'Ends with', needsValue: true, needsValue2: false },
  { value: 'is_blank', label: 'Is blank', needsValue: false, needsValue2: false },
  { value: 'is_not_blank', label: 'Is not blank', needsValue: false, needsValue2: false },
];

const FORMAT_TYPES: { value: FormatType; label: string; description: string }[] = [
  { value: 'color_scale', label: 'Color Scale', description: 'Gradient colors based on value' },
  { value: 'data_bar', label: 'Data Bars', description: 'Bar visualization in cells' },
  { value: 'icon_set', label: 'Icon Set', description: 'Icons based on thresholds' },
  { value: 'rules', label: 'Custom Rules', description: 'Rule-based formatting' },
  { value: 'top_bottom', label: 'Top/Bottom', description: 'Highlight top or bottom values' },
  { value: 'above_below_avg', label: 'Above/Below Average', description: 'Compare to average' },
];

export const FormatRuleEditor: React.FC<FormatRuleEditorProps> = ({
  format,
  onChange,
  onDelete,
  columns,
  className,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const handleTypeChange = (type: FormatType) => {
    const newFormat = createDefaultFormat(format.column, type);
    newFormat.id = format.id;
    newFormat.name = format.name;
    newFormat.priority = format.priority;
    onChange(newFormat);
  };

  const handleColumnChange = (column: string) => {
    onChange({ ...format, column });
  };

  const handleToggleEnabled = () => {
    onChange({ ...format, enabled: !format.enabled });
  };

  // Render type-specific editor
  const renderTypeEditor = () => {
    switch (format.type) {
      case 'color_scale':
        return format.colorScale && (
          <GradientPicker
            value={format.colorScale}
            onChange={(colorScale) => onChange({ ...format, colorScale })}
          />
        );

      case 'data_bar':
        return format.dataBar && (
          <div className="space-y-3">
            <ColorPicker
              value={format.dataBar.fillColor}
              onChange={(fillColor) =>
                onChange({ ...format, dataBar: { ...format.dataBar!, fillColor } })
              }
              label="Bar Color"
            />
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={format.dataBar.showValue}
                  onChange={(e) =>
                    onChange({
                      ...format,
                      dataBar: { ...format.dataBar!, showValue: e.target.checked },
                    })
                  }
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Show value</span>
              </label>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Min Length (%)
                </label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={format.dataBar.minLength}
                  onChange={(e) =>
                    onChange({
                      ...format,
                      dataBar: { ...format.dataBar!, minLength: Number(e.target.value) },
                    })
                  }
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Max Length (%)
                </label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={format.dataBar.maxLength}
                  onChange={(e) =>
                    onChange({
                      ...format,
                      dataBar: { ...format.dataBar!, maxLength: Number(e.target.value) },
                    })
                  }
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md"
                />
              </div>
            </div>
          </div>
        );

      case 'icon_set':
        return format.iconSet && (
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Icon Set
              </label>
              <select
                value={format.iconSet.iconSet}
                onChange={(e) =>
                  onChange({
                    ...format,
                    iconSet: { ...format.iconSet!, iconSet: e.target.value },
                  })
                }
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md"
              >
                <option value="traffic_light">Traffic Lights</option>
                <option value="arrows_3">Arrows (3)</option>
                <option value="arrows_5">Arrows (5)</option>
                <option value="triangles">Triangles</option>
                <option value="stars">Stars</option>
                <option value="flags">Flags</option>
                <option value="checkmarks">Checkmarks</option>
              </select>
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={format.iconSet.reverseOrder}
                  onChange={(e) =>
                    onChange({
                      ...format,
                      iconSet: { ...format.iconSet!, reverseOrder: e.target.checked },
                    })
                  }
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Reverse order</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={format.iconSet.showIconOnly}
                  onChange={(e) =>
                    onChange({
                      ...format,
                      iconSet: { ...format.iconSet!, showIconOnly: e.target.checked },
                    })
                  }
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Icon only</span>
              </label>
            </div>
          </div>
        );

      case 'rules':
        return format.rules && (
          <RulesEditor
            rules={format.rules.rules}
            onChange={(rules) =>
              onChange({ ...format, rules: { ...format.rules!, rules } })
            }
          />
        );

      case 'top_bottom':
        return format.topBottom && (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Type
                </label>
                <select
                  value={format.topBottom.type}
                  onChange={(e) =>
                    onChange({
                      ...format,
                      topBottom: { ...format.topBottom!, type: e.target.value as 'top' | 'bottom' },
                    })
                  }
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md"
                >
                  <option value="top">Top</option>
                  <option value="bottom">Bottom</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Count
                </label>
                <input
                  type="number"
                  min={1}
                  value={format.topBottom.count}
                  onChange={(e) =>
                    onChange({
                      ...format,
                      topBottom: { ...format.topBottom!, count: Number(e.target.value) },
                    })
                  }
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md"
                />
              </div>
            </div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={format.topBottom.isPercent}
                onChange={(e) =>
                  onChange({
                    ...format,
                    topBottom: { ...format.topBottom!, isPercent: e.target.checked },
                  })
                }
                className="rounded border-gray-300"
              />
              <span className="text-sm text-gray-700">Percentage</span>
            </label>
            <ColorPicker
              value={format.topBottom.style.background?.color || { hex: '#FFEB84' }}
              onChange={(color) =>
                onChange({
                  ...format,
                  topBottom: {
                    ...format.topBottom!,
                    style: { ...format.topBottom!.style, background: { color } },
                  },
                })
              }
              label="Highlight Color"
            />
          </div>
        );

      case 'above_below_avg':
        return format.aboveBelowAvg && (
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Type
              </label>
              <select
                value={format.aboveBelowAvg.type}
                onChange={(e) =>
                  onChange({
                    ...format,
                    aboveBelowAvg: { ...format.aboveBelowAvg!, type: e.target.value as any },
                  })
                }
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md"
              >
                <option value="above">Above average</option>
                <option value="above_or_equal">Above or equal to average</option>
                <option value="below">Below average</option>
                <option value="below_or_equal">Below or equal to average</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <ColorPicker
                value={format.aboveBelowAvg.aboveStyle.background?.color || { hex: '#63BE7B' }}
                onChange={(color) =>
                  onChange({
                    ...format,
                    aboveBelowAvg: {
                      ...format.aboveBelowAvg!,
                      aboveStyle: { background: { color } },
                    },
                  })
                }
                label="Above Color"
              />
              <ColorPicker
                value={format.aboveBelowAvg.belowStyle?.background?.color || { hex: '#F8696B' }}
                onChange={(color) =>
                  onChange({
                    ...format,
                    aboveBelowAvg: {
                      ...format.aboveBelowAvg!,
                      belowStyle: { background: { color } },
                    },
                  })
                }
                label="Below Color"
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div
      className={cn(
        'border border-gray-200 rounded-lg bg-white',
        !format.enabled && 'opacity-60',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b bg-gray-50">
        <GripVertical className="h-4 w-4 text-gray-400 cursor-grab" />

        <input
          type="checkbox"
          checked={format.enabled}
          onChange={handleToggleEnabled}
          className="rounded border-gray-300"
        />

        <div className="flex-1 min-w-0">
          <input
            type="text"
            value={format.name || ''}
            onChange={(e) => onChange({ ...format, name: e.target.value })}
            placeholder="Rule name"
            className="w-full px-2 py-1 text-sm border-0 bg-transparent focus:outline-none focus:ring-1 focus:ring-blue-500 rounded"
          />
        </div>

        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 hover:bg-gray-200 rounded"
        >
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-gray-500" />
          ) : (
            <ChevronDown className="h-4 w-4 text-gray-500" />
          )}
        </button>

        <button
          type="button"
          onClick={onDelete}
          className="p-1 hover:bg-red-100 rounded text-gray-500 hover:text-red-600"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {/* Body */}
      {isExpanded && (
        <div className="p-4 space-y-4">
          {/* Column & Type Selection */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Apply to Column
              </label>
              <select
                value={format.column}
                onChange={(e) => handleColumnChange(e.target.value)}
                className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md"
              >
                {columns.map((col) => (
                  <option key={col.name} value={col.name}>
                    {col.label || col.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Format Type
              </label>
              <select
                value={format.type}
                onChange={(e) => handleTypeChange(e.target.value as FormatType)}
                className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-md"
              >
                {FORMAT_TYPES.map((ft) => (
                  <option key={ft.value} value={ft.value}>
                    {ft.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Type-specific editor */}
          <div className="pt-2 border-t">
            {renderTypeEditor()}
          </div>
        </div>
      )}
    </div>
  );
};

// Rules Editor Sub-component
interface RulesEditorProps {
  rules: FormatRule[];
  onChange: (rules: FormatRule[]) => void;
}

const RulesEditor: React.FC<RulesEditorProps> = ({ rules, onChange }) => {
  const addRule = () => {
    const newRule: FormatRule = {
      id: `rule_${Date.now()}`,
      priority: rules.length,
      enabled: true,
      stopIfTrue: false,
      operator: 'greater_than',
      value: 0,
      style: {
        background: { color: { hex: '#FFEB84' } },
      },
    };
    onChange([...rules, newRule]);
  };

  const updateRule = (index: number, updates: Partial<FormatRule>) => {
    const newRules = [...rules];
    newRules[index] = { ...newRules[index], ...updates };
    onChange(newRules);
  };

  const deleteRule = (index: number) => {
    onChange(rules.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3">
      {rules.map((rule, index) => {
        const operatorConfig = COMPARISON_OPERATORS.find((o) => o.value === rule.operator);

        return (
          <div key={rule.id} className="flex items-start gap-2 p-2 bg-gray-50 rounded-md">
            <div className="flex-1 grid grid-cols-4 gap-2">
              {/* Operator */}
              <select
                value={rule.operator}
                onChange={(e) => updateRule(index, { operator: e.target.value as ComparisonOperator })}
                className="px-2 py-1 text-xs border border-gray-300 rounded-md"
              >
                {COMPARISON_OPERATORS.map((op) => (
                  <option key={op.value} value={op.value}>
                    {op.label}
                  </option>
                ))}
              </select>

              {/* Value 1 */}
              {operatorConfig?.needsValue && (
                <input
                  type="text"
                  value={rule.value ?? ''}
                  onChange={(e) => updateRule(index, { value: e.target.value })}
                  placeholder="Value"
                  className="px-2 py-1 text-xs border border-gray-300 rounded-md"
                />
              )}

              {/* Value 2 (for between) */}
              {operatorConfig?.needsValue2 && (
                <input
                  type="text"
                  value={rule.value2 ?? ''}
                  onChange={(e) => updateRule(index, { value2: e.target.value })}
                  placeholder="And"
                  className="px-2 py-1 text-xs border border-gray-300 rounded-md"
                />
              )}

              {/* Color */}
              <div className="flex items-center gap-1">
                <input
                  type="color"
                  value={colorToHex(rule.style.background?.color || { hex: '#FFEB84' })}
                  onChange={(e) =>
                    updateRule(index, {
                      style: { ...rule.style, background: { color: { hex: e.target.value } } },
                    })
                  }
                  className="w-6 h-6 rounded cursor-pointer"
                />
              </div>
            </div>

            <button
              type="button"
              onClick={() => deleteRule(index)}
              className="p-1 hover:bg-red-100 rounded text-gray-500 hover:text-red-600"
            >
              <Trash2 className="h-3 w-3" />
            </button>
          </div>
        );
      })}

      <button
        type="button"
        onClick={addRule}
        className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
      >
        <Plus className="h-4 w-4" />
        Add Rule
      </button>
    </div>
  );
};

export default FormatRuleEditor;
