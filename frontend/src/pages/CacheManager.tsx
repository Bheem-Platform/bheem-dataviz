/**
 * Cache Manager Page
 *
 * Query caching management and performance optimization.
 */

import { useState, useEffect } from 'react';
import {
  Database,
  RefreshCw,
  Trash2,
  Settings,
  Activity,
  Clock,
  HardDrive,
  Zap,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { cachingApi } from '../lib/api';

interface CacheEntry {
  key: string;
  type: string;
  size_bytes: number;
  created_at: string;
  expires_at: string;
  access_count: number;
  status: 'valid' | 'stale' | 'expired';
}

interface CacheStats {
  total_entries: number;
  total_size_mb: number;
  hit_rate: number;
  miss_rate: number;
  evictions_today: number;
  avg_ttl_minutes: number;
}

const defaultStats: CacheStats = {
  total_entries: 0,
  total_size_mb: 0,
  hit_rate: 0,
  miss_rate: 0,
  evictions_today: 0,
  avg_ttl_minutes: 0,
};

const statusColors = {
  valid: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400' },
  stale: { bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-400' },
  expired: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400' },
};

export function CacheManager() {
  const [stats, setStats] = useState<CacheStats>(defaultStats);
  const [entries, setEntries] = useState<CacheEntry[]>([]);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    try {
      setError(null);
      const [statsResponse, keysResponse] = await Promise.all([
        cachingApi.getStats(),
        cachingApi.listKeys(),
      ]);
      setStats(statsResponse.data);
      setEntries(keysResponse.data.keys || keysResponse.data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch cache data');
      console.error('Error fetching cache data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleRefreshStats = async () => {
    setIsRefreshing(true);
    await fetchData();
    setIsRefreshing(false);
  };

  const handleClearAll = async () => {
    try {
      setError(null);
      await cachingApi.clearAll(true);
      setEntries([]);
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear cache');
      console.error('Error clearing cache:', err);
    }
  };

  const handleInvalidate = async (key: string) => {
    try {
      setError(null);
      await cachingApi.deleteKey(key);
      setEntries(entries.filter(e => e.key !== key));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to invalidate cache entry');
      console.error('Error invalidating cache entry:', err);
    }
  };

  const filteredEntries = selectedType === 'all'
    ? entries
    : entries.filter(e => e.type === selectedType);

  if (isLoading) {
    return (
      <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">Loading cache data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 border-l-4 border-red-500 p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <p className="text-red-700 dark:text-red-400">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Cache Manager
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Query caching and performance optimization
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleRefreshStats}
                disabled={isRefreshing}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={handleClearAll}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Clear All
              </button>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-6 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Database className="w-4 h-4" />
                Total Entries
              </div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.total_entries.toLocaleString()}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <HardDrive className="w-4 h-4" />
                Cache Size
              </div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.total_size_mb.toFixed(1)} MB
              </div>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                <CheckCircle className="w-4 h-4" />
                Hit Rate
              </div>
              <div className="mt-1 text-2xl font-semibold text-green-700 dark:text-green-300">
                {stats.hit_rate}%
              </div>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
                <AlertCircle className="w-4 h-4" />
                Miss Rate
              </div>
              <div className="mt-1 text-2xl font-semibold text-red-700 dark:text-red-300">
                {stats.miss_rate}%
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Zap className="w-4 h-4" />
                Evictions Today
              </div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.evictions_today}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Clock className="w-4 h-4" />
                Avg TTL
              </div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.avg_ttl_minutes}m
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filter */}
        <div className="mb-6 flex items-center gap-4">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          >
            <option value="all">All Types</option>
            <option value="query_result">Query Results</option>
            <option value="dashboard_data">Dashboard Data</option>
            <option value="connection_schema">Schema Cache</option>
            <option value="chart_data">Chart Data</option>
          </select>
          <span className="text-sm text-gray-500">
            {filteredEntries.length} entries
          </span>
        </div>

        {/* Cache Entries Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Cache Key
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Hits
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Expires
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredEntries.map((entry) => (
                <tr key={entry.key} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4">
                    <code className="text-sm text-gray-900 dark:text-white font-mono">
                      {entry.key.length > 40 ? `${entry.key.slice(0, 40)}...` : entry.key}
                    </code>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {entry.type.replace('_', ' ')}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {formatBytes(entry.size_bytes)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {entry.access_count}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {new Date(entry.expires_at).toLocaleTimeString()}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[entry.status].bg} ${statusColors[entry.status].text}`}>
                      {entry.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleInvalidate(entry.key)}
                      className="text-red-600 hover:text-red-800 dark:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredEntries.length === 0 && (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              No cache entries found
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CacheManager;
