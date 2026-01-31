/**
 * Performance Monitor Page
 *
 * System performance monitoring and optimization.
 */

import { useState, useEffect } from 'react';
import {
  Activity,
  Clock,
  Database,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Zap,
  RefreshCw,
} from 'lucide-react';
import { performanceMonitoringApi } from '../lib/api';

interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  status: 'good' | 'warning' | 'critical';
}

interface SlowQuery {
  id: string;
  query: string;
  executionTime: number;
  occurrences: number;
  lastSeen: string;
}

export function PerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [slowQueries, setSlowQueries] = useState<SlowQuery[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPerformanceData = async () => {
    try {
      setError(null);
      const [systemResponse, requestResponse, cacheResponse, dbResponse] = await Promise.all([
        performanceMonitoringApi.getSystemMetrics(),
        performanceMonitoringApi.getRequestMetrics(),
        performanceMonitoringApi.getCacheMetrics(),
        performanceMonitoringApi.getDatabaseMetrics(),
      ]);

      // Transform API responses into PerformanceMetric format
      const transformedMetrics: PerformanceMetric[] = [];

      // System metrics
      if (systemResponse.data) {
        const sys = systemResponse.data;
        if (sys.memory_percent !== undefined) {
          transformedMetrics.push({
            name: 'Memory Usage',
            value: Math.round(sys.memory_percent * 10) / 10,
            unit: '%',
            trend: sys.memory_percent > 80 ? 'up' : 'stable',
            status: sys.memory_percent > 90 ? 'critical' : sys.memory_percent > 70 ? 'warning' : 'good',
          });
        }
        if (sys.cpu_percent !== undefined) {
          transformedMetrics.push({
            name: 'CPU Usage',
            value: Math.round(sys.cpu_percent * 10) / 10,
            unit: '%',
            trend: 'stable',
            status: sys.cpu_percent > 90 ? 'critical' : sys.cpu_percent > 70 ? 'warning' : 'good',
          });
        }
      }

      // Request metrics
      if (requestResponse.data) {
        const req = requestResponse.data;
        if (req.avg_latency_ms !== undefined) {
          transformedMetrics.push({
            name: 'Avg Query Time',
            value: Math.round(req.avg_latency_ms),
            unit: 'ms',
            trend: 'stable',
            status: req.avg_latency_ms > 1000 ? 'critical' : req.avg_latency_ms > 500 ? 'warning' : 'good',
          });
        }
        if (req.error_rate !== undefined) {
          transformedMetrics.push({
            name: 'Error Rate',
            value: Math.round(req.error_rate * 100) / 100,
            unit: '%',
            trend: req.error_rate > 1 ? 'up' : 'down',
            status: req.error_rate > 5 ? 'critical' : req.error_rate > 1 ? 'warning' : 'good',
          });
        }
      }

      // Cache metrics
      if (cacheResponse.data) {
        const cache = cacheResponse.data;
        if (cache.hit_rate !== undefined) {
          transformedMetrics.push({
            name: 'Cache Hit Rate',
            value: Math.round(cache.hit_rate * 10) / 10,
            unit: '%',
            trend: cache.hit_rate > 80 ? 'up' : 'down',
            status: cache.hit_rate < 50 ? 'critical' : cache.hit_rate < 70 ? 'warning' : 'good',
          });
        }
      }

      // Database metrics
      if (dbResponse.data) {
        const db = dbResponse.data;
        if (db.active_connections !== undefined) {
          transformedMetrics.push({
            name: 'Active Connections',
            value: db.active_connections,
            unit: '',
            trend: 'stable',
            status: db.active_connections > 100 ? 'warning' : 'good',
          });
        }
        // Extract slow queries if available
        if (db.slow_queries && Array.isArray(db.slow_queries)) {
          const transformedQueries: SlowQuery[] = db.slow_queries.map((q: {
            id?: string;
            query?: string;
            execution_time?: number;
            occurrences?: number;
            last_seen?: string;
          }, index: number) => ({
            id: q.id || String(index + 1),
            query: q.query || 'Unknown query',
            executionTime: q.execution_time || 0,
            occurrences: q.occurrences || 1,
            lastSeen: q.last_seen || 'Unknown',
          }));
          setSlowQueries(transformedQueries);
        }
      }

      setMetrics(transformedMetrics);
    } catch (err) {
      console.error('Failed to fetch performance data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch performance data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPerformanceData();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchPerformanceData();
    setIsRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'text-green-600';
      case 'warning': return 'text-amber-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4" />;
      case 'down': return <TrendingDown className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  if (isLoading) {
    return (
      <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading performance data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 mx-auto text-red-500" />
          <h2 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">Error Loading Data</h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">{error}</p>
          <button
            onClick={handleRefresh}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Performance Monitor
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Real-time system performance metrics
              </p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
          {metrics.map((metric) => (
            <div key={metric.name} className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">{metric.name}</div>
              <div className={`text-2xl font-bold ${getStatusColor(metric.status)}`}>
                {metric.value}{metric.unit}
              </div>
              <div className={`flex items-center gap-1 text-xs mt-1 ${
                metric.trend === 'up' ? 'text-green-600' : metric.trend === 'down' ? 'text-red-600' : 'text-gray-400'
              }`}>
                {getTrendIcon(metric.trend)}
                {metric.trend}
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Response Time Chart Placeholder */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Response Time Trend
            </h3>
            <div className="h-64 flex items-center justify-center border border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
              <div className="text-center text-gray-400">
                <Activity className="w-12 h-12 mx-auto mb-2" />
                <p>Chart visualization area</p>
              </div>
            </div>
          </div>

          {/* Query Distribution */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Query Distribution
            </h3>
            <div className="h-64 flex items-center justify-center border border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
              <div className="text-center text-gray-400">
                <Database className="w-12 h-12 mx-auto mb-2" />
                <p>Chart visualization area</p>
              </div>
            </div>
          </div>
        </div>

        {/* Slow Queries */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Slow Queries
              </h3>
              <span className="text-sm text-gray-500">{slowQueries.length} queries above threshold</span>
            </div>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {slowQueries.map((query) => (
              <div key={query.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <code className="text-sm text-gray-800 dark:text-gray-200 font-mono block truncate max-w-2xl">
                      {query.query}
                    </code>
                    <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {query.executionTime}ms
                      </span>
                      <span className="flex items-center gap-1">
                        <Zap className="w-4 h-4" />
                        {query.occurrences} occurrences
                      </span>
                      <span>Last seen: {query.lastSeen}</span>
                    </div>
                  </div>
                  <button className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded">
                    Optimize
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default PerformanceMonitor;
