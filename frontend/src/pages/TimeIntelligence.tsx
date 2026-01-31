/**
 * Time Intelligence Page
 *
 * Allows users to create and manage time intelligence calculations.
 */

import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Calculator,
  Plus,
  Search,
  Play,
  Trash2,
  Edit2,
  Copy,
  Download,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  Table,
  FileCode,
} from 'lucide-react';
import {
  TimeIntelligenceFunction,
  TimeIntelligenceResult,
  PERIOD_TYPE_OPTIONS,
  AGGREGATION_OPTIONS,
  formatPctChange,
  getComparisonLabel,
} from '../types/timeIntelligence';
import { TimeIntelligenceFunctionBuilder } from '../components/time-intelligence/TimeIntelligenceFunctionBuilder';
import api, { timeIntelligenceApi, connectionsApi } from '../lib/api';
import { cn } from '../lib/utils';

interface Connection {
  id: string;
  name: string;
  type: string;
}

interface TableInfo {
  schema_name: string;
  name: string;
  type: string;
  reference_count?: number;
}

interface TableColumn {
  name: string;
  type: string;
  nullable?: boolean;
}

const TimeIntelligence: React.FC = () => {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [selectedConnection, setSelectedConnection] = useState<string>('');
  const [allTables, setAllTables] = useState<TableInfo[]>([]);
  const [schemas, setSchemas] = useState<string[]>([]);
  const [selectedSchema, setSelectedSchema] = useState<string>('');
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [columns, setColumns] = useState<TableColumn[]>([]);
  const [tablesLoading, setTablesLoading] = useState(false);
  const [columnsLoading, setColumnsLoading] = useState(false);

  const [functions, setFunctions] = useState<TimeIntelligenceFunction[]>([]);
  const [results, setResults] = useState<TimeIntelligenceResult[]>([]);
  const [generatedSql, setGeneratedSql] = useState<string>('');

  const [isLoading, setIsLoading] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const [showBuilder, setShowBuilder] = useState(false);
  const [editingFunction, setEditingFunction] = useState<TimeIntelligenceFunction | null>(null);
  const [showSql, setShowSql] = useState(false);

  // Fetch connections on mount
  useEffect(() => {
    fetchConnections();
  }, []);

  // Fetch tables when connection changes
  useEffect(() => {
    if (selectedConnection) {
      fetchTables(selectedConnection);
    } else {
      setAllTables([]);
      setSchemas([]);
      setTables([]);
      setSelectedSchema('');
      setSelectedTable('');
      setColumns([]);
    }
  }, [selectedConnection]);

  // Filter tables when schema changes
  useEffect(() => {
    if (selectedSchema) {
      const filtered = allTables.filter(t => t.schema_name === selectedSchema);
      setTables(filtered);
      setSelectedTable('');
      setColumns([]);
    } else {
      setTables([]);
    }
  }, [selectedSchema, allTables]);

  // Fetch columns when table changes
  useEffect(() => {
    if (selectedConnection && selectedSchema && selectedTable) {
      fetchColumns(selectedConnection, selectedSchema, selectedTable);
    } else {
      setColumns([]);
    }
  }, [selectedConnection, selectedSchema, selectedTable]);

  const fetchConnections = async () => {
    setIsLoading(true);
    try {
      const response = await connectionsApi.list();
      setConnections(response.data || []);
    } catch (error) {
      console.error('Failed to fetch connections:', error);
      setFetchError('Failed to load connections');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTables = async (connectionId: string) => {
    setTablesLoading(true);
    try {
      const response = await api.get(`/connections/${connectionId}/tables`);
      const tableList = response.data || [];
      setAllTables(tableList);

      // Extract unique schemas from tables
      const uniqueSchemas: string[] = [...new Set(tableList.map((t: TableInfo) => t.schema_name))] as string[];
      setSchemas(uniqueSchemas);

      // Auto-select first schema if only one
      if (uniqueSchemas.length === 1) {
        setSelectedSchema(uniqueSchemas[0] as string);
      } else {
        setSelectedSchema('');
      }
      setSelectedTable('');
      setColumns([]);
    } catch (error) {
      console.error('Failed to fetch tables:', error);
      setAllTables([]);
      setSchemas([]);
    } finally {
      setTablesLoading(false);
    }
  };

  const fetchColumns = async (connectionId: string, schema: string, table: string) => {
    setColumnsLoading(true);
    try {
      const response = await api.get(`/connections/${connectionId}/tables/${schema}/${table}/columns`);
      setColumns(response.data || []);
    } catch (error) {
      console.error('Failed to fetch columns:', error);
      setColumns([]);
    } finally {
      setColumnsLoading(false);
    }
  };

  const dateColumns = columns.filter((col) =>
    ['date', 'datetime', 'timestamp', 'timestamptz'].some((t) =>
      col.type.toLowerCase().includes(t)
    )
  ).map(col => ({ column: col.name, type: col.type }));

  const measureColumns = columns.filter((col) =>
    ['int', 'float', 'decimal', 'numeric', 'double', 'real', 'bigint', 'smallint'].some((t) =>
      col.type.toLowerCase().includes(t)
    )
  ).map(col => ({ column: col.name, type: col.type }));

  const handleAddFunction = (func: TimeIntelligenceFunction) => {
    if (editingFunction) {
      setFunctions((prev) => prev.map((f) => (f.id === func.id ? func : f)));
    } else {
      setFunctions((prev) => [...prev, func]);
    }
    setShowBuilder(false);
    setEditingFunction(null);
  };

  const handleEditFunction = (func: TimeIntelligenceFunction) => {
    setEditingFunction(func);
    setShowBuilder(true);
  };

  const handleDeleteFunction = (funcId: string) => {
    setFunctions((prev) => prev.filter((f) => f.id !== funcId));
  };

  const handleDuplicateFunction = (func: TimeIntelligenceFunction) => {
    const duplicated: TimeIntelligenceFunction = {
      ...func,
      id: `ti_${Date.now()}`,
      name: `${func.name} (Copy)`,
    };
    setFunctions((prev) => [...prev, duplicated]);
  };

  const handleExecute = async () => {
    if (!selectedConnection || !selectedSchema || !selectedTable || functions.length === 0) {
      setError('Please select a data source and add at least one function');
      return;
    }

    setIsExecuting(true);
    setError(null);

    try {
      // Convert functions to snake_case for backend
      const convertedFunctions = functions.map(func => ({
        id: func.id,
        name: func.name,
        period_type: func.periodType,
        date_column: func.dateColumn,
        measure_column: func.measureColumn,
        aggregation: func.aggregation,
        periods: func.periods,
        offset: func.offset,
        granularity: func.granularity,
        use_fiscal_calendar: func.useFiscalCalendar || false,
        fiscal_config: func.fiscalConfig ? {
          fiscal_year_start_month: func.fiscalConfig.fiscalYearStartMonth,
          fiscal_year_start_day: func.fiscalConfig.fiscalYearStartDay,
          week_starts_on: func.fiscalConfig.weekStartsOn,
        } : undefined,
        start_date: func.startDate,
        end_date: func.endDate,
        output_column: func.outputColumn,
        include_comparison: func.includeComparison || false,
        include_pct_change: func.includePctChange || false,
      }));

      const response = await timeIntelligenceApi.calculate({
        connection_id: selectedConnection,
        schema_name: selectedSchema,
        table_name: selectedTable,
        functions: convertedFunctions,
      });

      // Convert results back to camelCase for frontend
      console.log('API Response:', response.data);
      const convertedResults = (response.data.results || []).map((r: any) => {
        console.log('Raw result item:', r);
        return {
          functionId: r.function_id,
          value: r.value,
          comparisonValue: r.comparison_value,
          pctChange: r.pct_change,
          periodStart: r.period_start,
          periodEnd: r.period_end,
          comparisonPeriodStart: r.comparison_period_start,
          comparisonPeriodEnd: r.comparison_period_end,
        };
      });
      console.log('Converted results:', convertedResults);

      setResults(convertedResults);
      setGeneratedSql(response.data.query || '');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to execute calculations';
      setError(errorMessage);
      console.error('Calculation error:', err);
    } finally {
      setIsExecuting(false);
    }
  };

  const getResultForFunction = (funcId: string): TimeIntelligenceResult | undefined => {
    return results.find((r) => r.functionId === funcId);
  };

  const formatValue = (value: number | undefined): string => {
    if (value === undefined || value === null) return '-';
    return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  };

  const getPctChangeColor = (pctChange: number | undefined): string => {
    if (pctChange === undefined || pctChange === null) return 'text-gray-500';
    if (pctChange > 0) return 'text-green-600';
    if (pctChange < 0) return 'text-red-600';
    return 'text-gray-500';
  };

  const getPctChangeIcon = (pctChange: number | undefined) => {
    if (pctChange === undefined || pctChange === null) return <Minus className="h-4 w-4" />;
    if (pctChange > 0) return <TrendingUp className="h-4 w-4" />;
    if (pctChange < 0) return <TrendingDown className="h-4 w-4" />;
    return <Minus className="h-4 w-4" />;
  };

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Calculator className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900">Time Intelligence</h1>
                <p className="text-sm text-gray-500">
                  Create time-based calculations like YTD, MTD, rolling averages, and comparisons
                </p>
              </div>
            </div>
            <button
              onClick={handleExecute}
              disabled={isExecuting || functions.length === 0 || !selectedTable}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isExecuting ? (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              Execute
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-24">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Panel - Data Source & Functions */}
          <div className="col-span-5 space-y-4">
            {/* Data Source Selection */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm p-4">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Data Source</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Connection</label>
                  <select
                    value={selectedConnection}
                    onChange={(e) => setSelectedConnection(e.target.value)}
                    disabled={isLoading}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
                  >
                    <option value="">{isLoading ? 'Loading...' : 'Select connection...'}</option>
                    {connections.map((conn) => (
                      <option key={conn.id} value={conn.id}>
                        {conn.name} ({conn.type})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Schema</label>
                    <select
                      value={selectedSchema}
                      onChange={(e) => setSelectedSchema(e.target.value)}
                      disabled={!selectedConnection || tablesLoading}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    >
                      <option value="">{tablesLoading ? 'Loading...' : 'Select schema...'}</option>
                      {schemas.map((schema) => (
                        <option key={schema} value={schema}>
                          {schema}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Table</label>
                    <select
                      value={selectedTable}
                      onChange={(e) => setSelectedTable(e.target.value)}
                      disabled={!selectedSchema || tablesLoading}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    >
                      <option value="">{tablesLoading ? 'Loading...' : 'Select table...'}</option>
                      {tables.map((table) => (
                        <option key={table.name} value={table.name}>
                          {table.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Functions List */}
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
              <div className="px-4 py-3 border-b flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-900">Functions</h3>
                <button
                  onClick={() => {
                    setEditingFunction(null);
                    setShowBuilder(true);
                  }}
                  disabled={dateColumns.length === 0 || measureColumns.length === 0}
                  className="flex items-center gap-1 px-2 py-1 text-sm text-purple-600 hover:bg-purple-50 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Plus className="h-4 w-4" />
                  Add
                </button>
              </div>

              {functions.length === 0 ? (
                <div className="p-8 text-center">
                  <Calculator className="h-10 w-10 text-gray-300 mx-auto mb-3" />
                  <p className="text-sm text-gray-500 mb-2">No functions defined</p>
                  <p className="text-xs text-gray-400">
                    Select a data source and add time intelligence functions
                  </p>
                </div>
              ) : (
                <div className="divide-y">
                  {functions.map((func) => {
                    const result = getResultForFunction(func.id);
                    const periodLabel = PERIOD_TYPE_OPTIONS.find(
                      (p) => p.value === func.periodType
                    )?.label;

                    return (
                      <div key={func.id} className="p-3 hover:bg-gray-50">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <h4 className="text-sm font-medium text-gray-900 truncate">
                              {func.name}
                            </h4>
                            <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                              <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded">
                                {periodLabel}
                              </span>
                              <span>{func.measureColumn}</span>
                              <span className="text-gray-300">|</span>
                              <span>{func.aggregation.toUpperCase()}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 ml-2">
                            <button
                              onClick={() => handleEditFunction(func)}
                              className="p-1 text-gray-400 hover:text-gray-600 rounded"
                            >
                              <Edit2 className="h-3.5 w-3.5" />
                            </button>
                            <button
                              onClick={() => handleDuplicateFunction(func)}
                              className="p-1 text-gray-400 hover:text-gray-600 rounded"
                            >
                              <Copy className="h-3.5 w-3.5" />
                            </button>
                            <button
                              onClick={() => handleDeleteFunction(func.id)}
                              className="p-1 text-gray-400 hover:text-red-600 rounded"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        </div>

                        {/* Result */}
                        {result && (
                          <div className="mt-2 p-2 bg-gray-50 rounded">
                            <div className="flex items-center justify-between">
                              <span className="text-lg font-semibold text-gray-900">
                                {formatValue(result.value)}
                              </span>
                              {result.pctChange !== undefined && (
                                <span
                                  className={cn(
                                    'flex items-center gap-1 text-sm',
                                    getPctChangeColor(result.pctChange)
                                  )}
                                >
                                  {getPctChangeIcon(result.pctChange)}
                                  {formatPctChange(result.pctChange)}
                                </span>
                              )}
                            </div>
                            {result.comparisonValue !== undefined && (
                              <p className="text-xs text-gray-500 mt-1">
                                {getComparisonLabel(func.periodType)}:{' '}
                                {formatValue(result.comparisonValue)}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Function Builder Modal */}
            {showBuilder && (
              <TimeIntelligenceFunctionBuilder
                dateColumns={dateColumns}
                measureColumns={measureColumns}
                initialFunction={editingFunction || undefined}
                onSave={handleAddFunction}
                onCancel={() => {
                  setShowBuilder(false);
                  setEditingFunction(null);
                }}
              />
            )}
          </div>

          {/* Right Panel - Results */}
          <div className="col-span-7">
            {fetchError && (
              <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm">
                <strong>Warning:</strong> {fetchError}
              </div>
            )}

            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            {/* Results Summary */}
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
              <div className="px-4 py-3 border-b flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-900">Results</h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowSql(!showSql)}
                    className={cn(
                      'flex items-center gap-1 px-2 py-1 text-sm rounded',
                      showSql
                        ? 'bg-purple-100 text-purple-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    )}
                  >
                    <FileCode className="h-4 w-4" />
                    SQL
                  </button>
                </div>
              </div>

              {showSql && generatedSql ? (
                <div className="p-4">
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs overflow-x-auto">
                    {generatedSql}
                  </pre>
                </div>
              ) : results.length === 0 ? (
                <div className="p-12 text-center">
                  <Clock className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No results yet</h3>
                  <p className="text-sm text-gray-500">
                    Add time intelligence functions and click Execute to see results
                  </p>
                </div>
              ) : (
                <div className="p-4">
                  <div className="grid grid-cols-2 gap-4">
                    {functions.map((func) => {
                      const result = getResultForFunction(func.id);
                      if (!result) return null;

                      return (
                        <div
                          key={func.id}
                          className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                        >
                          <h4 className="text-sm font-medium text-gray-700 mb-2">{func.name}</h4>
                          <p className="text-2xl font-bold text-gray-900">
                            {formatValue(result.value)}
                          </p>

                          {(result.comparisonValue !== undefined ||
                            result.pctChange !== undefined) && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              {result.comparisonValue !== undefined && (
                                <div className="flex justify-between text-sm">
                                  <span className="text-gray-500">
                                    {getComparisonLabel(func.periodType)}
                                  </span>
                                  <span className="text-gray-900">
                                    {formatValue(result.comparisonValue)}
                                  </span>
                                </div>
                              )}
                              {result.pctChange !== undefined && (
                                <div className="flex justify-between text-sm mt-1">
                                  <span className="text-gray-500">Change</span>
                                  <span
                                    className={cn(
                                      'flex items-center gap-1',
                                      getPctChangeColor(result.pctChange)
                                    )}
                                  >
                                    {getPctChangeIcon(result.pctChange)}
                                    {formatPctChange(result.pctChange)}
                                  </span>
                                </div>
                              )}
                            </div>
                          )}

                          {result.periodStart && result.periodEnd && (
                            <p className="text-xs text-gray-400 mt-3">
                              {result.periodStart} to {result.periodEnd}
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TimeIntelligence;
