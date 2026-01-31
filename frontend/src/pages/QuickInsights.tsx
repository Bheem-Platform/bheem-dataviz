/**
 * Quick Insights Page
 *
 * Automated data insights including trend detection,
 * outlier detection, and correlation analysis.
 */

import { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Link2,
  BarChart2,
  Activity,
  Calendar,
  ArrowUpRight,
  Award,
  ArrowDown,
  Zap,
  RefreshCw,
  Filter,
  Download,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  Info,
} from 'lucide-react';
import {
  Insight,
  InsightType,
  InsightSeverity,
  INSIGHT_TYPE_LABELS,
  SEVERITY_COLORS,
  sortInsightsBySeverity,
  groupInsightsByType,
} from '../types/insights';

// Mock data
const mockInsights: Insight[] = [
  {
    id: '1',
    type: 'trend',
    severity: 'high',
    title: 'Strong upward trend in Revenue',
    description: 'Revenue has increased by 23.5% over the last 30 days with a strong correlation (R²=0.89).',
    details: {
      column: 'revenue',
      direction: 'increasing',
      slope: 1250.5,
      r_squared: 0.89,
      change_percent: 23.5,
    },
    affected_columns: ['revenue'],
    confidence: 0.95,
    generated_at: '2026-01-30T10:00:00Z',
    suggested_chart_type: 'line',
  },
  {
    id: '2',
    type: 'outlier',
    severity: 'medium',
    title: 'Outliers detected in Order Value',
    description: '12 records have order values significantly above the normal range (> 3 standard deviations).',
    details: {
      column: 'order_value',
      outlier_type: 'above',
      count: 12,
      threshold_high: 15000,
      mean: 5200,
      std_dev: 2100,
    },
    affected_columns: ['order_value'],
    confidence: 0.88,
    generated_at: '2026-01-30T10:00:00Z',
    suggested_chart_type: 'scatter',
  },
  {
    id: '3',
    type: 'correlation',
    severity: 'medium',
    title: 'Strong correlation: Marketing Spend ↔ Sales',
    description: 'Marketing spend shows a strong positive correlation (r=0.82) with sales figures.',
    details: {
      column_1: 'marketing_spend',
      column_2: 'sales',
      correlation_type: 'positive',
      coefficient: 0.82,
      p_value: 0.001,
    },
    affected_columns: ['marketing_spend', 'sales'],
    confidence: 0.92,
    generated_at: '2026-01-30T10:00:00Z',
    suggested_chart_type: 'scatter',
  },
  {
    id: '4',
    type: 'seasonality',
    severity: 'low',
    title: 'Weekly seasonality detected',
    description: 'Order volume shows consistent weekly patterns with peaks on Fridays and troughs on Mondays.',
    details: {
      column: 'order_count',
      has_seasonality: true,
      period: 'weekly',
      peak_periods: ['Friday'],
      trough_periods: ['Monday'],
    },
    affected_columns: ['order_count'],
    confidence: 0.78,
    generated_at: '2026-01-30T10:00:00Z',
    suggested_chart_type: 'bar',
  },
  {
    id: '5',
    type: 'significant_change',
    severity: 'high',
    title: 'Significant drop in Customer Retention',
    description: 'Customer retention rate decreased by 15% compared to the previous period. This requires immediate attention.',
    details: {
      column: 'retention_rate',
      change_percent: -15,
      period_1: 'December 2025',
      period_2: 'January 2026',
      is_significant: true,
    },
    affected_columns: ['retention_rate'],
    confidence: 0.94,
    generated_at: '2026-01-30T10:00:00Z',
    suggested_chart_type: 'line',
  },
  {
    id: '6',
    type: 'top_performer',
    severity: 'low',
    title: 'Top performing product category',
    description: 'Electronics category accounts for 45% of total revenue, outperforming other categories by 3x.',
    details: {
      dimension: 'category',
      dimension_value: 'Electronics',
      measure: 'revenue',
      value: 2450000,
      percent_of_total: 45,
    },
    affected_columns: ['category', 'revenue'],
    confidence: 0.99,
    generated_at: '2026-01-30T10:00:00Z',
    suggested_chart_type: 'pie',
  },
];

const insightIcons: Record<InsightType, React.ElementType> = {
  trend: TrendingUp,
  outlier: AlertTriangle,
  correlation: Link2,
  distribution: BarChart2,
  comparison: Activity,
  anomaly: Zap,
  seasonality: Calendar,
  growth: ArrowUpRight,
  top_performer: Award,
  bottom_performer: ArrowDown,
  significant_change: Activity,
};

const severityColors: Record<InsightSeverity, { bg: string; text: string; border: string }> = {
  high: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400', border: 'border-red-200 dark:border-red-800' },
  medium: { bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-400', border: 'border-amber-200 dark:border-amber-800' },
  low: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400', border: 'border-blue-200 dark:border-blue-800' },
};

export function QuickInsights() {
  const [insights, setInsights] = useState<Insight[]>(mockInsights);
  const [selectedTypes, setSelectedTypes] = useState<InsightType[]>([]);
  const [selectedSeverity, setSelectedSeverity] = useState<InsightSeverity | 'all'>('all');
  const [sortBy, setSortBy] = useState<'severity' | 'confidence' | 'date'>('severity');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedInsights, setExpandedInsights] = useState<Set<string>>(new Set());
  const [selectedConnection, setSelectedConnection] = useState<string>('');
  const [showDismissed, setShowDismissed] = useState(false);

  // Filter insights
  const filteredInsights = insights.filter(insight => {
    if (selectedTypes.length > 0 && !selectedTypes.includes(insight.type)) return false;
    if (selectedSeverity !== 'all' && insight.severity !== selectedSeverity) return false;
    return true;
  });

  // Sort insights
  const sortedInsights = sortInsightsBySeverity(filteredInsights);

  // Group by type for summary
  const insightsByType = groupInsightsByType(insights);

  // Summary stats
  const summary = {
    total: insights.length,
    high: insights.filter(i => i.severity === 'high').length,
    medium: insights.filter(i => i.severity === 'medium').length,
    low: insights.filter(i => i.severity === 'low').length,
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsLoading(false);
  };

  const toggleExpand = (id: string) => {
    setExpandedInsights(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const toggleTypeFilter = (type: InsightType) => {
    setSelectedTypes(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Quick Insights
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                AI-powered data analysis and pattern detection
              </p>
            </div>
            <div className="flex items-center gap-3">
              <select
                value={selectedConnection}
                onChange={(e) => setSelectedConnection(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Select Data Source</option>
                <option value="conn-1">Sales Database</option>
                <option value="conn-2">Marketing Data</option>
              </select>
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Analyze
              </button>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Insights</div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {summary.total}
              </div>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <div className="text-sm font-medium text-red-600 dark:text-red-400">High Priority</div>
              <div className="mt-1 text-2xl font-semibold text-red-700 dark:text-red-300">
                {summary.high}
              </div>
            </div>
            <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
              <div className="text-sm font-medium text-amber-600 dark:text-amber-400">Medium Priority</div>
              <div className="mt-1 text-2xl font-semibold text-amber-700 dark:text-amber-300">
                {summary.medium}
              </div>
            </div>
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <div className="text-sm font-medium text-blue-600 dark:text-blue-400">Low Priority</div>
              <div className="mt-1 text-2xl font-semibold text-blue-700 dark:text-blue-300">
                {summary.low}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          {/* Sidebar Filters */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <h3 className="font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Filter className="w-4 h-4" />
                Filters
              </h3>

              {/* Severity Filter */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Severity
                </label>
                <select
                  value={selectedSeverity}
                  onChange={(e) => setSelectedSeverity(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="all">All Severities</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              {/* Type Filters */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Insight Types
                </label>
                <div className="space-y-2">
                  {(Object.keys(INSIGHT_TYPE_LABELS) as InsightType[]).map((type) => {
                    const Icon = insightIcons[type];
                    const count = insightsByType[type]?.length || 0;
                    return (
                      <label
                        key={type}
                        className="flex items-center gap-2 text-sm cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={selectedTypes.length === 0 || selectedTypes.includes(type)}
                          onChange={() => toggleTypeFilter(type)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <Icon className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-700 dark:text-gray-300 flex-1">
                          {INSIGHT_TYPE_LABELS[type]}
                        </span>
                        <span className="text-gray-400 text-xs">{count}</span>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Actions */}
              <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button className="w-full px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Export Insights
                </button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Results header */}
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Showing {sortedInsights.length} of {insights.length} insights
              </span>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  {showDismissed ? (
                    <Eye className="w-4 h-4" />
                  ) : (
                    <EyeOff className="w-4 h-4" />
                  )}
                  <input
                    type="checkbox"
                    checked={showDismissed}
                    onChange={(e) => setShowDismissed(e.target.checked)}
                    className="sr-only"
                  />
                  Show Dismissed
                </label>
              </div>
            </div>

            {/* Insights List */}
            <div className="space-y-4">
              {sortedInsights.map((insight) => {
                const Icon = insightIcons[insight.type];
                const colors = severityColors[insight.severity];
                const isExpanded = expandedInsights.has(insight.id);

                return (
                  <div
                    key={insight.id}
                    className={`bg-white dark:bg-gray-800 rounded-lg shadow border ${colors.border}`}
                  >
                    {/* Insight Header */}
                    <div
                      className="p-4 cursor-pointer"
                      onClick={() => toggleExpand(insight.id)}
                    >
                      <div className="flex items-start gap-4">
                        <div className={`p-2 rounded-lg ${colors.bg}`}>
                          <Icon className={`w-5 h-5 ${colors.text}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${colors.bg} ${colors.text}`}>
                              {insight.severity}
                            </span>
                            <span className="text-xs text-gray-400">
                              {INSIGHT_TYPE_LABELS[insight.type]}
                            </span>
                            <span className="text-xs text-gray-400">
                              · {Math.round(insight.confidence * 100)}% confidence
                            </span>
                          </div>
                          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                            {insight.title}
                          </h3>
                          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            {insight.description}
                          </p>
                        </div>
                        <button className="p-1 text-gray-400 hover:text-gray-600">
                          {isExpanded ? (
                            <ChevronDown className="w-5 h-5" />
                          ) : (
                            <ChevronRight className="w-5 h-5" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {isExpanded && (
                      <div className="px-4 pb-4 border-t border-gray-100 dark:border-gray-700">
                        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Affected Columns:</span>
                            <div className="mt-1 flex flex-wrap gap-1">
                              {insight.affected_columns.map((col) => (
                                <span
                                  key={col}
                                  className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-gray-700 dark:text-gray-300 text-xs"
                                >
                                  {col}
                                </span>
                              ))}
                            </div>
                          </div>
                          {insight.suggested_chart_type && (
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Suggested Visualization:</span>
                              <div className="mt-1 text-gray-700 dark:text-gray-300">
                                {insight.suggested_chart_type} chart
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Details from insight */}
                        {insight.details && (
                          <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                            <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase mb-2">
                              Details
                            </h4>
                            <dl className="grid grid-cols-2 gap-2 text-sm">
                              {Object.entries(insight.details).map(([key, value]) => (
                                <div key={key}>
                                  <dt className="text-gray-500 dark:text-gray-400 capitalize">
                                    {key.replace(/_/g, ' ')}:
                                  </dt>
                                  <dd className="text-gray-900 dark:text-white font-medium">
                                    {typeof value === 'number'
                                      ? value.toLocaleString(undefined, { maximumFractionDigits: 2 })
                                      : String(value)}
                                  </dd>
                                </div>
                              ))}
                            </dl>
                          </div>
                        )}

                        {/* Actions */}
                        <div className="mt-4 flex items-center gap-2">
                          <button className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                            Explore in Charts
                          </button>
                          <button className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700">
                            Create Alert
                          </button>
                          <button className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                            Dismiss
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}

              {sortedInsights.length === 0 && (
                <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
                  <Info className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    No insights found
                  </h3>
                  <p className="mt-1 text-gray-500 dark:text-gray-400">
                    Select a data source and click Analyze to generate insights.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default QuickInsights;
