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
  TrendingUp,
  Layers,
  ChevronDown,
  Zap,
  Target,
  Activity,
  Sparkles,
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

const dataTypeColors: Record<string, { bg: string; text: string; border: string }> = {
  numeric: { bg: 'bg-emerald-50 dark:bg-emerald-900/30', text: 'text-emerald-600 dark:text-emerald-400', border: 'border-emerald-200 dark:border-emerald-800' },
  temporal: { bg: 'bg-blue-50 dark:bg-blue-900/30', text: 'text-blue-600 dark:text-blue-400', border: 'border-blue-200 dark:border-blue-800' },
  categorical: { bg: 'bg-purple-50 dark:bg-purple-900/30', text: 'text-purple-600 dark:text-purple-400', border: 'border-purple-200 dark:border-purple-800' },
  boolean: { bg: 'bg-amber-50 dark:bg-amber-900/30', text: 'text-amber-600 dark:text-amber-400', border: 'border-amber-200 dark:border-amber-800' },
  text: { bg: 'bg-indigo-50 dark:bg-indigo-900/30', text: 'text-indigo-600 dark:text-indigo-400', border: 'border-indigo-200 dark:border-indigo-800' },
  unknown: { bg: 'bg-gray-50 dark:bg-gray-900/30', text: 'text-gray-600 dark:text-gray-400', border: 'border-gray-200 dark:border-gray-800' },
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
  const [expandedColumns, setExpandedColumns] = useState<Set<string>>(new Set());

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

  const toggleColumnExpand = (columnName: string) => {
    setExpandedColumns(prev => {
      const next = new Set(prev);
      if (next.has(columnName)) {
        next.delete(columnName);
      } else {
        next.add(columnName);
      }
      return next;
    });
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return { bg: 'bg-emerald-500', text: 'text-emerald-600 dark:text-emerald-400' };
    if (score >= 70) return { bg: 'bg-amber-500', text: 'text-amber-600 dark:text-amber-400' };
    return { bg: 'bg-red-500', text: 'text-red-600 dark:text-red-400' };
  };

  const filteredColumns = profile?.columns.filter(col =>
    col.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-white to-indigo-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-950/20">
      {/* Header */}
      <div className="px-6 lg:px-8 py-6 border-b border-gray-200/60 dark:border-gray-700/60 bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto">
          {/* Title Row */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                <BarChart2 className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Data Profiler
                </h1>
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  Analyze dataset quality, statistics and distributions
                </p>
              </div>
            </div>
            <button
              onClick={handleRunProfile}
              disabled={isProfiling || !selectedConnection || !selectedTable}
              className="group flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium rounded-xl hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isProfiling ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
              )}
              {isProfiling ? 'Profiling...' : 'Run Profile'}
            </button>
          </div>

          {/* Controls Row */}
          <div className="flex flex-wrap gap-4">
            {/* Connection Select */}
            <div className="relative min-w-[240px]">
              <Database className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={selectedConnection}
                onChange={(e) => setSelectedConnection(e.target.value)}
                disabled={isLoadingConnections}
                className="w-full pl-10 pr-10 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all disabled:opacity-50"
              >
                <option value="">
                  {isLoadingConnections ? 'Loading connections...' : 'Select Connection'}
                </option>
                {connections.map((conn) => (
                  <option key={conn.id} value={conn.id}>
                    {conn.name} ({conn.type})
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>

            {/* Table Select */}
            <div className="relative min-w-[280px]">
              <Layers className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={selectedSchema && selectedTable ? `${selectedSchema}.${selectedTable}` : ''}
                onChange={(e) => handleTableSelect(e.target.value)}
                disabled={isLoadingTables || !selectedConnection}
                className="w-full pl-10 pr-10 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all disabled:opacity-50"
              >
                <option value="">
                  {isLoadingTables ? 'Loading tables...' : 'Select Table'}
                </option>
                {tables.map((t) => (
                  <option key={`${t.schema_name}.${t.table_name}`} value={`${t.schema_name}.${t.table_name}`}>
                    {t.schema_name}.{t.table_name} {t.row_count ? `(${t.row_count.toLocaleString()} rows)` : ''}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 text-sm flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/50 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-4 h-4 text-red-500" />
              </div>
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          {profile && (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
                {/* Table Name */}
                <div className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-xl hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300">
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <Database className="w-4 h-4 text-indigo-500" />
                    <span>Table</span>
                  </div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                    {profile.table_name}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">{profile.schema_name}</div>
                </div>

                {/* Row Count */}
                <div className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-xl hover:shadow-purple-500/10 hover:border-purple-300 dark:hover:border-purple-600 transition-all duration-300">
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <FileSpreadsheet className="w-4 h-4 text-purple-500" />
                    <span>Total Rows</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {profile.row_count.toLocaleString()}
                  </div>
                </div>

                {/* Column Count */}
                <div className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-xl hover:shadow-fuchsia-500/10 hover:border-fuchsia-300 dark:hover:border-fuchsia-600 transition-all duration-300">
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <BarChart2 className="w-4 h-4 text-fuchsia-500" />
                    <span>Columns</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {profile.column_count}
                  </div>
                </div>

                {/* Quality Score */}
                <div className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-xl hover:shadow-emerald-500/10 hover:border-emerald-300 dark:hover:border-emerald-600 transition-all duration-300">
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <Target className="w-4 h-4 text-emerald-500" />
                    <span>Quality Score</span>
                  </div>
                  <div className="flex items-baseline gap-1">
                    <span className={`text-2xl font-bold ${getQualityColor(profile.quality_score).text}`}>
                      {profile.quality_score}
                    </span>
                    <span className="text-gray-400">%</span>
                  </div>
                  {/* Progress bar */}
                  <div className="mt-2 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getQualityColor(profile.quality_score).bg} rounded-full transition-all duration-1000`}
                      style={{ width: `${profile.quality_score}%` }}
                    />
                  </div>
                </div>

                {/* Profiled At */}
                <div className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-xl hover:shadow-cyan-500/10 hover:border-cyan-300 dark:hover:border-cyan-600 transition-all duration-300">
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <Calendar className="w-4 h-4 text-cyan-500" />
                    <span>Profiled At</span>
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {new Date(profile.profiled_at).toLocaleDateString()}
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    {new Date(profile.profiled_at).toLocaleTimeString()}
                  </div>
                </div>
              </div>

              {/* Data Type Tags */}
              <div className="mb-6 flex flex-wrap gap-3">
                {profile.has_temporal && (
                  <span className="flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl text-sm font-medium text-blue-600 dark:text-blue-400">
                    <Calendar className="w-4 h-4" />
                    Temporal Data
                  </span>
                )}
                {profile.has_numeric && (
                  <span className="flex items-center gap-2 px-4 py-2 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 rounded-xl text-sm font-medium text-emerald-600 dark:text-emerald-400">
                    <Hash className="w-4 h-4" />
                    Numeric Data
                  </span>
                )}
                {profile.has_categorical && (
                  <span className="flex items-center gap-2 px-4 py-2 bg-purple-50 dark:bg-purple-900/30 border border-purple-200 dark:border-purple-800 rounded-xl text-sm font-medium text-purple-600 dark:text-purple-400">
                    <Type className="w-4 h-4" />
                    Categorical Data
                  </span>
                )}
              </div>

              {/* Search */}
              <div className="mb-6">
                <div className="relative max-w-md">
                  <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search columns..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                  />
                </div>
              </div>

              {/* Column Profiles */}
              <div className="space-y-4">
                {filteredColumns.map((column) => {
                  const TypeIcon = dataTypeIcons[column.data_type] || Info;
                  const typeColors = dataTypeColors[column.data_type] || dataTypeColors.unknown;
                  const hasNulls = column.null_percent > 0;
                  const isExpanded = expandedColumns.has(column.name);

                  return (
                    <div
                      key={column.name}
                      className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 overflow-hidden hover:shadow-xl hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300"
                    >
                      <div className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-4">
                            <div className={`w-12 h-12 rounded-xl ${typeColors.bg} ${typeColors.border} border flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                              <TypeIcon className={`w-6 h-6 ${typeColors.text}`} />
                            </div>
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                                {column.name}
                                {hasNulls && column.null_percent > 10 && (
                                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                                )}
                              </h3>
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-sm text-gray-500 dark:text-gray-400">{column.sql_type}</span>
                                <span className="text-gray-300 dark:text-gray-600">•</span>
                                <span className={`text-xs px-2 py-0.5 rounded-full ${typeColors.bg} ${typeColors.text} font-medium`}>
                                  {column.data_type}
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-3">
                            {hasNulls && (
                              <span className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-800 text-amber-600 dark:text-amber-400 rounded-lg font-medium">
                                <AlertTriangle className="w-3 h-3" />
                                {column.null_percent.toFixed(1)}% nulls
                              </span>
                            )}
                            <button
                              onClick={() => toggleColumnExpand(column.name)}
                              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-all"
                            >
                              <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} />
                            </button>
                          </div>
                        </div>

                        {/* Stats Grid */}
                        <div className="mt-5 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                          <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600">
                            <span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Unique Values</span>
                            <span className="text-sm font-semibold text-gray-900 dark:text-white">
                              {column.unique_count.toLocaleString()}
                            </span>
                            <span className="text-xs text-indigo-600 dark:text-indigo-400 ml-1">
                              ({column.unique_percent.toFixed(1)}%)
                            </span>
                          </div>
                          <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600">
                            <span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Null Count</span>
                            <span className={`text-sm font-semibold ${hasNulls ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'}`}>
                              {column.null_count.toLocaleString()}
                            </span>
                          </div>
                          {column.min_value && (
                            <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600">
                              <span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Min Value</span>
                              <span className="text-sm font-semibold text-gray-900 dark:text-white truncate block">
                                {column.min_value}
                              </span>
                            </div>
                          )}
                          {column.max_value && (
                            <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600">
                              <span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Max Value</span>
                              <span className="text-sm font-semibold text-gray-900 dark:text-white truncate block">
                                {column.max_value}
                              </span>
                            </div>
                          )}
                          {column.mean !== undefined && column.mean !== null && (
                            <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600">
                              <span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Mean</span>
                              <span className="text-sm font-semibold text-cyan-600 dark:text-cyan-400">
                                {column.mean.toFixed(2)}
                              </span>
                            </div>
                          )}
                          {column.std_dev !== undefined && column.std_dev !== null && (
                            <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600">
                              <span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Std Dev</span>
                              <span className="text-sm font-semibold text-purple-600 dark:text-purple-400">
                                {column.std_dev.toFixed(2)}
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Top Values - Expandable */}
                        {column.top_values && column.top_values.length > 0 && isExpanded && (
                          <div className="mt-5 pt-5 border-t border-gray-200 dark:border-gray-700">
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4 flex items-center gap-2">
                              <TrendingUp className="w-4 h-4 text-indigo-500" />
                              Top Values Distribution
                            </h4>
                            <div className="space-y-3">
                              {column.top_values.slice(0, 5).map((tv, idx) => (
                                <div key={idx} className="flex items-center gap-4">
                                  <div className="flex-1 relative">
                                    <div className="h-8 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
                                      <div
                                        className={`h-full ${typeColors.bg} rounded-lg transition-all duration-500`}
                                        style={{ width: `${Math.min(tv.percent * 1.2, 100)}%` }}
                                      />
                                    </div>
                                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-700 dark:text-gray-300 truncate max-w-[200px]">
                                      {tv.value || '(empty)'}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-3 min-w-[100px] justify-end">
                                    <span className="text-sm text-gray-500 dark:text-gray-400">
                                      {tv.count.toLocaleString()}
                                    </span>
                                    <span className={`text-sm font-semibold ${typeColors.text}`}>
                                      {tv.percent.toFixed(1)}%
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Show expand hint if there are top values */}
                        {column.top_values && column.top_values.length > 0 && !isExpanded && (
                          <button
                            onClick={() => toggleColumnExpand(column.name)}
                            className="mt-4 text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 flex items-center gap-1 font-medium transition-colors"
                          >
                            <TrendingUp className="w-3 h-3" />
                            View distribution ({column.top_values.length} values)
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {/* Empty State */}
          {!profile && !isProfiling && (
            <div className="flex flex-col items-center justify-center h-80 text-center">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mb-6 shadow-lg shadow-purple-500/25">
                <BarChart2 className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Select a Data Source
              </h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mb-8">
                Choose a connection and table above to analyze data quality, statistics, and distributions
              </p>
              <div className="flex items-center justify-center gap-6 text-sm text-gray-500 dark:text-gray-400">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  Quality Analysis
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-purple-500" />
                  Statistical Insights
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-500" />
                  Fast Profiling
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {isProfiling && (
            <div className="flex flex-col items-center justify-center h-80 text-center">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mx-auto mb-4 animate-pulse">
                <Loader2 className="w-8 h-8 animate-spin text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Profiling Your Data
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                Analyzing <span className="text-indigo-600 dark:text-indigo-400 font-medium">{selectedSchema}.{selectedTable}</span>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DataProfiler;
