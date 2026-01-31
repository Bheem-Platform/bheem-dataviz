/**
 * Time Intelligence Function Builder Component
 *
 * A form component for creating and editing time intelligence functions.
 */

import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Calculator,
  Clock,
  Plus,
  Trash2,
  ChevronDown,
  Info,
} from 'lucide-react';
import {
  TimeIntelligenceFunction,
  TimePeriodType,
  AggregationType,
  TimeGranularity,
  FiscalCalendarConfig,
  PERIOD_TYPE_OPTIONS,
  AGGREGATION_OPTIONS,
  GRANULARITY_OPTIONS,
  createDefaultTimeFunction,
} from '../../types/timeIntelligence';
import { cn } from '../../lib/utils';

interface TimeIntelligenceFunctionBuilderProps {
  dateColumns: { column: string; type: string }[];
  measureColumns: { column: string; type: string }[];
  initialFunction?: TimeIntelligenceFunction;
  onSave: (func: TimeIntelligenceFunction) => void;
  onCancel?: () => void;
}

export const TimeIntelligenceFunctionBuilder: React.FC<TimeIntelligenceFunctionBuilderProps> = ({
  dateColumns,
  measureColumns,
  initialFunction,
  onSave,
  onCancel,
}) => {
  const [func, setFunc] = useState<TimeIntelligenceFunction>(
    initialFunction || {
      id: `ti_${Date.now()}`,
      name: '',
      periodType: 'ytd',
      dateColumn: dateColumns[0]?.column || '',
      measureColumn: measureColumns[0]?.column || '',
      aggregation: 'sum',
      includeComparison: false,
      includePctChange: false,
    }
  );

  const [showFiscalConfig, setShowFiscalConfig] = useState(func.useFiscalCalendar || false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Update name automatically based on period type and measure
  useEffect(() => {
    if (!initialFunction && func.measureColumn) {
      const periodLabel = PERIOD_TYPE_OPTIONS.find((p) => p.value === func.periodType)?.label || func.periodType;
      setFunc((prev) => ({
        ...prev,
        name: `${periodLabel} ${func.measureColumn}`,
      }));
    }
  }, [func.periodType, func.measureColumn, initialFunction]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!func.name.trim()) {
      newErrors.name = 'Name is required';
    }
    if (!func.dateColumn) {
      newErrors.dateColumn = 'Date column is required';
    }
    if (!func.measureColumn) {
      newErrors.measureColumn = 'Measure column is required';
    }
    if ((func.periodType === 'rolling' || func.periodType === 'trailing') && !func.periods) {
      newErrors.periods = 'Number of periods is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (validate()) {
      onSave(func);
    }
  };

  const updateField = <K extends keyof TimeIntelligenceFunction>(
    field: K,
    value: TimeIntelligenceFunction[K]
  ) => {
    setFunc((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const { [field]: _, ...rest } = prev;
        return rest;
      });
    }
  };

  const needsPeriodsInput = func.periodType === 'rolling' || func.periodType === 'trailing';
  const needsGranularity = needsPeriodsInput;
  const isFiscalPeriod = func.periodType === 'fiscal_ytd' || func.periodType === 'fiscal_qtd';

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="px-4 py-3 border-b bg-gray-50 flex items-center gap-2">
        <Calculator className="h-5 w-5 text-blue-600" />
        <h3 className="font-medium text-gray-900">
          {initialFunction ? 'Edit' : 'New'} Time Intelligence Function
        </h3>
      </div>

      <div className="p-4 space-y-4">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Function Name *
          </label>
          <input
            type="text"
            value={func.name}
            onChange={(e) => updateField('name', e.target.value)}
            className={cn(
              'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
              errors.name ? 'border-red-500' : 'border-gray-300'
            )}
            placeholder="e.g., YTD Revenue"
          />
          {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name}</p>}
        </div>

        {/* Period Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Period Type *
          </label>
          <div className="relative">
            <select
              value={func.periodType}
              onChange={(e) => updateField('periodType', e.target.value as TimePeriodType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none"
            >
              {PERIOD_TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>
          {func.periodType && (
            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
              <Info className="h-3 w-3" />
              {PERIOD_TYPE_OPTIONS.find((p) => p.value === func.periodType)?.description}
            </p>
          )}
        </div>

        {/* Periods input for rolling/trailing */}
        {needsPeriodsInput && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of Periods *
              </label>
              <input
                type="number"
                value={func.periods || ''}
                onChange={(e) => updateField('periods', parseInt(e.target.value) || undefined)}
                min={1}
                className={cn(
                  'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                  errors.periods ? 'border-red-500' : 'border-gray-300'
                )}
                placeholder="e.g., 12"
              />
              {errors.periods && <p className="text-xs text-red-500 mt-1">{errors.periods}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Granularity
              </label>
              <select
                value={func.granularity || 'month'}
                onChange={(e) => updateField('granularity', e.target.value as TimeGranularity)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {GRANULARITY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Date and Measure Columns */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date Column *
            </label>
            <select
              value={func.dateColumn}
              onChange={(e) => updateField('dateColumn', e.target.value)}
              className={cn(
                'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.dateColumn ? 'border-red-500' : 'border-gray-300'
              )}
            >
              <option value="">Select column...</option>
              {dateColumns.map((col) => (
                <option key={col.column} value={col.column}>
                  {col.column}
                </option>
              ))}
            </select>
            {errors.dateColumn && <p className="text-xs text-red-500 mt-1">{errors.dateColumn}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Measure Column *
            </label>
            <select
              value={func.measureColumn}
              onChange={(e) => updateField('measureColumn', e.target.value)}
              className={cn(
                'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.measureColumn ? 'border-red-500' : 'border-gray-300'
              )}
            >
              <option value="">Select column...</option>
              {measureColumns.map((col) => (
                <option key={col.column} value={col.column}>
                  {col.column}
                </option>
              ))}
            </select>
            {errors.measureColumn && (
              <p className="text-xs text-red-500 mt-1">{errors.measureColumn}</p>
            )}
          </div>
        </div>

        {/* Aggregation */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Aggregation
          </label>
          <select
            value={func.aggregation}
            onChange={(e) => updateField('aggregation', e.target.value as AggregationType)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {AGGREGATION_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label} - {option.description}
              </option>
            ))}
          </select>
        </div>

        {/* Comparison Options */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Comparison Options
          </label>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={func.includeComparison || false}
                onChange={(e) => updateField('includeComparison', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Include comparison period</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={func.includePctChange || false}
                onChange={(e) => updateField('includePctChange', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Calculate % change</span>
            </label>
          </div>
        </div>

        {/* Fiscal Calendar */}
        {(isFiscalPeriod || showFiscalConfig) && (
          <div className="border rounded-lg p-4 bg-gray-50">
            <label className="flex items-center gap-2 cursor-pointer mb-3">
              <input
                type="checkbox"
                checked={func.useFiscalCalendar || false}
                onChange={(e) => {
                  updateField('useFiscalCalendar', e.target.checked);
                  setShowFiscalConfig(e.target.checked);
                }}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Use Fiscal Calendar</span>
            </label>

            {func.useFiscalCalendar && (
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Fiscal Year Start Month
                  </label>
                  <select
                    value={func.fiscalConfig?.fiscalYearStartMonth || 1}
                    onChange={(e) =>
                      updateField('fiscalConfig', {
                        ...func.fiscalConfig,
                        fiscalYearStartMonth: parseInt(e.target.value),
                        fiscalYearStartDay: func.fiscalConfig?.fiscalYearStartDay || 1,
                        weekStartsOn: func.fiscalConfig?.weekStartsOn || 0,
                      })
                    }
                    className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    {[
                      'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December'
                    ].map((month, idx) => (
                      <option key={month} value={idx + 1}>
                        {month}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Fiscal Year Start Day
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={31}
                    value={func.fiscalConfig?.fiscalYearStartDay || 1}
                    onChange={(e) =>
                      updateField('fiscalConfig', {
                        ...func.fiscalConfig,
                        fiscalYearStartMonth: func.fiscalConfig?.fiscalYearStartMonth || 1,
                        fiscalYearStartDay: parseInt(e.target.value),
                        weekStartsOn: func.fiscalConfig?.weekStartsOn || 0,
                      })
                    }
                    className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Week Starts On
                  </label>
                  <select
                    value={func.fiscalConfig?.weekStartsOn || 0}
                    onChange={(e) =>
                      updateField('fiscalConfig', {
                        ...func.fiscalConfig,
                        fiscalYearStartMonth: func.fiscalConfig?.fiscalYearStartMonth || 1,
                        fiscalYearStartDay: func.fiscalConfig?.fiscalYearStartDay || 1,
                        weekStartsOn: parseInt(e.target.value),
                      })
                    }
                    className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value={0}>Sunday</option>
                    <option value={1}>Monday</option>
                    <option value={6}>Saturday</option>
                  </select>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Output Column Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Output Column Name (optional)
          </label>
          <input
            type="text"
            value={func.outputColumn || ''}
            onChange={(e) => updateField('outputColumn', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={`${func.periodType}_${func.measureColumn}`}
          />
          <p className="text-xs text-gray-500 mt-1">
            Leave empty to auto-generate from period type and measure
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="px-4 py-3 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg">
        {onCancel && (
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
        )}
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {initialFunction ? 'Update' : 'Add'} Function
        </button>
      </div>
    </div>
  );
};

export default TimeIntelligenceFunctionBuilder;
