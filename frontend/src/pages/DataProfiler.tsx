/**
 * Data Profiler Page
 *
 * Analyze and profile datasets for quality and statistics.
 */

import { useState, useEffect } from 'react';
import {
  BarChart2,
  Database,
  FileSpreadsheet,
  Search,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Info,
  Hash,
  Type,
  Calendar,
  ToggleLeft,
  Loader2,
} from 'lucide-react';
import { profilerApi } from '@/lib/api';

interface TopValue {
  value: string;
  count: number;
  percent: number;
}

interface ColumnProfile {
  name: string;
  data_type: string;
  sql_type: string;
  null_count: number;
  null_percent: number;
  unique_count: number;
  unique_percent: number;
  min_value?: string;
  max_value?: string;
  mean?: number;
  median?: number;
  std_dev?: number;
  top_values: TopValue[];
}

interface DatasetProfile {
  connection_id: string;
  connection_name: string;
  schema_name: string;
  table_name: string;
  row_count: number;
  column_count: number;
  columns: ColumnProfile[];
  profiled_at: string;
  quality_score: number;
  has_temporal: boolean;
  has_numeric: boolean;
  has_categorical: boolean;
}

interface Connection {
  id: string;
  name: string;
  type: string;
  database: string;
}

interface Table {
  schema_name: string;
  table_name: string;
  row_count: number | null;
  column_count: number;
}

const dataTypeIcons: Record<string, React.ElementType> = {
  numeric: Hash,
  temporal: Calendar,
  categorical: Type,
  boolean: ToggleLeft,
  text: Type,
  unknown: Info,
};

export function DataProfiler() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [tables, setTables] = useState<Table[]>([]);
  const [profile, setProfile] = useState<DatasetProfile | null>(null);
  const [selectedConnection, setSelectedConnection] = useState<string>('');
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [selectedSchema, setSelectedSchema] = useState<string>('');
  const [isProfiling, setIsProfiling] = useState(false);
  const [isLoadingConnections, setIsLoadingConnections] = useState(true);
  const [isLoadingTables, setIsLoadingTables] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Load connections on mount
  useEffect(() => {
    loadConnections();
  }, []);

  // Load tables when connection changes
  useEffect(() => {
    if (selectedConnection) {
      loadTables(selectedConnection);
      setProfile(null);
      setSelectedTable('');
      setSelectedSchema('');
    }
  }, [selectedConnection]);

  const loadConnections = async () => {
    setIsLoadingConnections(true);
    setError(null);
    try {
      const response = await profilerApi.getConnections();
      setConnections(response.data);
    } catch (err: any) {
      setError('Failed to load connections');
      console.error('Failed to load connections:', err);
    } finally {
      setIsLoadingConnections(false);
    }
  };

  const loadTables = async (connectionId: string) => {
    setIsLoadingTables(true);
    setError(null);
    try {
      const response = await profilerApi.getTables(connectionId);
      setTables(response.data);
    } catch (err: any) {
      setError('Failed to load tables');
      console.error('Failed to load tables:', err);
    } finally {
      setIsLoadingTables(false);
    }
  };

  const handleRunProfile = async () => {
    if (!selectedConnection || !selectedTable || !selectedSchema) {
      setError('Please select a connection and table');
      return;
    }

    setIsProfiling(true);
    setError(null);
    try {
      const response = await profilerApi.profileTable(
        selectedConnection,
        selectedSchema,
        selectedTable
      );
      setProfile(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to profile table');
      console.error('Failed to profile table:', err);
    } finally {
      setIsProfiling(false);
    }
  };

  const handleTableSelect = (value: string) => {
    const [schema, table] = value.split('.');
    setSelectedSchema(schema);
    setSelectedTable(table);
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-amber-600';
    return 'text-red-600';
  };

  const filteredColumns = profile?.columns.filter(col =>
    col.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Data Profiler
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Analyze dataset quality and statistics
              </p>
            </div>
            <button
              onClick={handleRunProfile}
              disabled={isProfiling || !selectedConnection || !selectedTable}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {isProfiling ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4" />
              )}
              {isProfiling ? 'Profiling...' : 'Run Profile'}
            </button>
          </div>

          {/* Source Selection */}
          <div className="mt-6 flex gap-4">
            <select
              value={selectedConnection}
              onChange={(e) => setSelectedConnection(e.target.value)}
              disabled={isLoadingConnections}
              className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white min-w-[200px]"
            >
              <option value="">
                {isLoadingConnections ? 'Loading...' : 'Select Connection'}
              </option>
              {connections.map((conn) => (
                <option key={conn.id} value={conn.id}>
                  {conn.name} ({conn.type})
                </option>
              ))}
            </select>
            <select
              value={selectedSchema && selectedTable ? `${selectedSchema}.${selectedTable}` : ''}
              onChange={(e) => handleTableSelect(e.target.value)}
              disabled={isLoadingTables || !selectedConnection}
              className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white min-w-[200px]"
            >
              <option value="">
                {isLoadingTables ? 'Loading...' : 'Select Table'}
              </option>
              {tables.map((t) => (
                <option key={`${t.schema_name}.${t.table_name}`} value={`${t.schema_name}.${t.table_name}`}>
                  {t.schema_name}.{t.table_name} {t.row_count ? `(${t.row_count.toLocaleString()} rows)` : ''}
                </option>
              ))}
            </select>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}
        </div>
      </div>

      {profile && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Database className="w-4 h-4" />
                Table
              </div>
              <div className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                {profile.table_name}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <FileSpreadsheet className="w-4 h-4" />
                Rows
              </div>
              <div className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                {profile.row_count.toLocaleString()}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <BarChart2 className="w-4 h-4" />
                Columns
              </div>
              <div className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                {profile.column_count}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <CheckCircle className="w-4 h-4" />
                Quality Score
              </div>
              <div className={`mt-1 text-lg font-semibold ${getQualityColor(profile.quality_score)}`}>
                {profile.quality_score}%
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Calendar className="w-4 h-4" />
                Profiled At
              </div>
              <div className="mt-1 text-sm font-medium text-gray-900 dark:text-white">
                {new Date(profile.profiled_at).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Data Type Summary */}
          <div className="mb-6 flex gap-4">
            {profile.has_temporal && (
              <span className="px-3 py-1 bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 rounded-full text-sm">
                Has Temporal Data
              </span>
            )}
            {profile.has_numeric && (
              <span className="px-3 py-1 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded-full text-sm">
                Has Numeric Data
              </span>
            )}
            {profile.has_categorical && (
              <span className="px-3 py-1 bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 rounded-full text-sm">
                Has Categorical Data
              </span>
            )}
          </div>

          {/* Search */}
          <div className="mb-4">
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search columns..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              />
            </div>
          </div>

          {/* Column Profiles */}
          <div className="space-y-4">
            {filteredColumns.map((column) => {
              const TypeIcon = dataTypeIcons[column.data_type] || Info;
              const hasNulls = column.null_percent > 0;

              return (
                <div key={column.name} className="bg-white dark:bg-gray-800 rounded-lg shadow">
                  <div className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                          <TypeIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                        </div>
                        <div>
                          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                            {column.name}
                          </h3>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {column.sql_type} ({column.data_type})
                          </p>
                        </div>
                      </div>
                      {hasNulls && (
                        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 rounded">
                          <AlertTriangle className="w-3 h-3" />
                          {column.null_percent.toFixed(2)}% nulls
                        </span>
                      )}
                    </div>

                    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Unique Values:</span>
                        <span className="ml-2 font-medium text-gray-900 dark:text-white">
                          {column.unique_count.toLocaleString()} ({column.unique_percent.toFixed(1)}%)
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Null Count:</span>
                        <span className="ml-2 font-medium text-gray-900 dark:text-white">
                          {column.null_count.toLocaleString()}
                        </span>
                      </div>
                      {column.min_value && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Min:</span>
                          <span className="ml-2 font-medium text-gray-900 dark:text-white">
                            {column.min_value}
                          </span>
                        </div>
                      )}
                      {column.max_value && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Max:</span>
                          <span className="ml-2 font-medium text-gray-900 dark:text-white">
                            {column.max_value}
                          </span>
                        </div>
                      )}
                      {column.mean !== undefined && column.mean !== null && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Mean:</span>
                          <span className="ml-2 font-medium text-gray-900 dark:text-white">
                            {column.mean.toFixed(2)}
                          </span>
                        </div>
                      )}
                      {column.std_dev !== undefined && column.std_dev !== null && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Std Dev:</span>
                          <span className="ml-2 font-medium text-gray-900 dark:text-white">
                            {column.std_dev.toFixed(2)}
                          </span>
                        </div>
                      )}
                    </div>

                    {column.top_values && column.top_values.length > 0 && (
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Top Values
                        </h4>
                        <div className="space-y-2">
                          {column.top_values.slice(0, 5).map((tv, idx) => (
                            <div key={idx} className="flex items-center gap-2">
                              <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
                                <div
                                  className="h-full bg-blue-500"
                                  style={{ width: `${Math.min(tv.percent * 1.2, 100)}%` }}
                                />
                              </div>
                              <span className="text-sm text-gray-600 dark:text-gray-400 w-32 truncate">
                                {tv.value}
                              </span>
                              <span className="text-sm text-gray-500 w-16 text-right">
                                {tv.percent.toFixed(1)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {!profile && !isProfiling && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center bg-white dark:bg-gray-800 rounded-lg shadow p-12">
            <BarChart2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Select a data source
            </h3>
            <p className="mt-1 text-gray-500 dark:text-gray-400">
              Choose a connection and table to profile
            </p>
          </div>
        </div>
      )}

      {isProfiling && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center bg-white dark:bg-gray-800 rounded-lg shadow p-12">
            <Loader2 className="w-16 h-16 text-blue-500 mx-auto mb-4 animate-spin" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Profiling table...
            </h3>
            <p className="mt-1 text-gray-500 dark:text-gray-400">
              Analyzing {selectedSchema}.{selectedTable}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataProfiler;
