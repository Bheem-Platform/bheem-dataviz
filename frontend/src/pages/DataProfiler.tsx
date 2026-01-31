/**
 * Data Profiler Page
 *
 * Analyze and profile datasets for quality and statistics.
 */

import { useState } from 'react';
import {
  BarChart2,
  Database,
  FileSpreadsheet,
  Search,
  RefreshCw,
  Download,
  AlertTriangle,
  CheckCircle,
  Info,
  Hash,
  Type,
  Calendar,
  ToggleLeft,
} from 'lucide-react';

interface ColumnProfile {
  name: string;
  data_type: string;
  null_count: number;
  null_percent: number;
  unique_count: number;
  unique_percent: number;
  min_value?: string;
  max_value?: string;
  mean?: number;
  median?: number;
  std_dev?: number;
  top_values: Array<{ value: string; count: number; percent: number }>;
}

interface DatasetProfile {
  connection_name: string;
  table_name: string;
  row_count: number;
  column_count: number;
  columns: ColumnProfile[];
  profiled_at: string;
  quality_score: number;
}

// Mock data
const mockProfile: DatasetProfile = {
  connection_name: 'Sales Database',
  table_name: 'orders',
  row_count: 125000,
  column_count: 12,
  profiled_at: '2026-01-30T10:00:00Z',
  quality_score: 87,
  columns: [
    {
      name: 'order_id',
      data_type: 'integer',
      null_count: 0,
      null_percent: 0,
      unique_count: 125000,
      unique_percent: 100,
      min_value: '1',
      max_value: '125000',
      top_values: [],
    },
    {
      name: 'customer_name',
      data_type: 'string',
      null_count: 150,
      null_percent: 0.12,
      unique_count: 45000,
      unique_percent: 36,
      top_values: [
        { value: 'John Smith', count: 45, percent: 0.036 },
        { value: 'Jane Doe', count: 38, percent: 0.030 },
        { value: 'Bob Wilson', count: 32, percent: 0.026 },
      ],
    },
    {
      name: 'order_date',
      data_type: 'date',
      null_count: 0,
      null_percent: 0,
      unique_count: 730,
      unique_percent: 0.58,
      min_value: '2024-01-01',
      max_value: '2026-01-30',
      top_values: [],
    },
    {
      name: 'total_amount',
      data_type: 'decimal',
      null_count: 25,
      null_percent: 0.02,
      unique_count: 8500,
      unique_percent: 6.8,
      min_value: '5.00',
      max_value: '15000.00',
      mean: 245.50,
      median: 125.00,
      std_dev: 312.45,
      top_values: [],
    },
    {
      name: 'status',
      data_type: 'string',
      null_count: 0,
      null_percent: 0,
      unique_count: 4,
      unique_percent: 0.003,
      top_values: [
        { value: 'completed', count: 95000, percent: 76 },
        { value: 'pending', count: 20000, percent: 16 },
        { value: 'cancelled', count: 8000, percent: 6.4 },
        { value: 'refunded', count: 2000, percent: 1.6 },
      ],
    },
  ],
};

const dataTypeIcons: Record<string, React.ElementType> = {
  integer: Hash,
  decimal: Hash,
  string: Type,
  date: Calendar,
  boolean: ToggleLeft,
};

export function DataProfiler() {
  const [profile, setProfile] = useState<DatasetProfile | null>(mockProfile);
  const [selectedConnection, setSelectedConnection] = useState<string>('');
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [isProfiling, setIsProfiling] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleRunProfile = async () => {
    setIsProfiling(true);
    await new Promise(r => setTimeout(r, 2000));
    setIsProfiling(false);
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
              disabled={isProfiling}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${isProfiling ? 'animate-spin' : ''}`} />
              {isProfiling ? 'Profiling...' : 'Run Profile'}
            </button>
          </div>

          {/* Source Selection */}
          <div className="mt-6 flex gap-4">
            <select
              value={selectedConnection}
              onChange={(e) => setSelectedConnection(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">Select Connection</option>
              <option value="conn-1">Sales Database</option>
              <option value="conn-2">Marketing Data</option>
            </select>
            <select
              value={selectedTable}
              onChange={(e) => setSelectedTable(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">Select Table</option>
              <option value="orders">orders</option>
              <option value="customers">customers</option>
              <option value="products">products</option>
            </select>
          </div>
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
                            {column.data_type}
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
                      {column.mean !== undefined && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Mean:</span>
                          <span className="ml-2 font-medium text-gray-900 dark:text-white">
                            {column.mean.toFixed(2)}
                          </span>
                        </div>
                      )}
                      {column.std_dev !== undefined && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Std Dev:</span>
                          <span className="ml-2 font-medium text-gray-900 dark:text-white">
                            {column.std_dev.toFixed(2)}
                          </span>
                        </div>
                      )}
                    </div>

                    {column.top_values.length > 0 && (
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

      {!profile && (
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
    </div>
  );
}

export default DataProfiler;
