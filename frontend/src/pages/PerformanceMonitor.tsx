/**
 * Performance Monitor Page
 *
 * System performance monitoring and optimization.
 */

import { useState } from 'react';
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

const mockMetrics: PerformanceMetric[] = [
  { name: 'Avg Query Time', value: 245, unit: 'ms', trend: 'down', status: 'good' },
  { name: 'Cache Hit Rate', value: 87.3, unit: '%', trend: 'up', status: 'good' },
  { name: 'Active Connections', value: 12, unit: '', trend: 'stable', status: 'good' },
  { name: 'Queue Depth', value: 3, unit: '', trend: 'up', status: 'warning' },
  { name: 'Error Rate', value: 0.2, unit: '%', trend: 'down', status: 'good' },
  { name: 'Memory Usage', value: 68, unit: '%', trend: 'up', status: 'warning' },
];

const mockSlowQueries: SlowQuery[] = [
  { id: '1', query: 'SELECT * FROM orders JOIN customers...', executionTime: 2340, occurrences: 45, lastSeen: '5 min ago' },
  { id: '2', query: 'SELECT COUNT(*) FROM transactions...', executionTime: 1850, occurrences: 23, lastSeen: '12 min ago' },
  { id: '3', query: 'SELECT SUM(amount) FROM payments...', executionTime: 1560, occurrences: 18, lastSeen: '30 min ago' },
];

export function PerformanceMonitor() {
  const [metrics] = useState<PerformanceMetric[]>(mockMetrics);
  const [slowQueries] = useState<SlowQuery[]>(mockSlowQueries);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await new Promise(r => setTimeout(r, 1000));
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

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
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
