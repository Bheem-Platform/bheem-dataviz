/**
 * Quick Insights Page
 *
 * Automated data insights including trend detection,
 * outlier detection, and correlation analysis.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Database,
  ExternalLink,
  Bell,
  X,
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
import { insightsApi, connectionsApi, quickChartsApi } from '../lib/api';

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

interface Connection {
  id: string;
  name: string;
  type: string;
}

interface TableInfo {
  schema_name: string;
  table_name: string;
  row_count?: number | null;
  column_count?: number;
  has_numeric?: boolean;
  has_temporal?: boolean;
}

export function QuickInsights() {
  const navigate = useNavigate();
  const [insights, setInsights] = useState<Insight[]>([]);
  const [dismissedInsights, setDismissedInsights] = useState<Set<string>>(new Set());
  const [connections, setConnections] = useState<Connection[]>([]);
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTypes, setSelectedTypes] = useState<InsightType[]>([]);
  const [selectedSeverity, setSelectedSeverity] = useState<InsightSeverity | 'all'>('all');
  const [sortBy, setSortBy] = useState<'severity' | 'confidence' | 'date'>('severity');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedInsights, setExpandedInsights] = useState<Set<string>>(new Set());
  const [selectedConnection, setSelectedConnection] = useState<string>('');
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [showDismissed, setShowDismissed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionsLoading, setConnectionsLoading] = useState(true);
  const [tablesLoading, setTablesLoading] = useState(false);

  // Handle Explore in Charts - navigate to Quick Charts with insight data
  const handleExploreInCharts = (insight: Insight) => {
    const [schema, table] = selectedTable.split('.');
    const params = new URLSearchParams({
      connection: selectedConnection,
      schema: schema || 'public',
      table: table || '',
    });
    navigate(`/quick-charts?${params.toString()}`);
  };

  // Handle Create Alert - navigate to subscriptions/alerts page
  const handleCreateAlert = (insight: Insight) => {
    const params = new URLSearchParams({
      type: 'insight',
      insightType: insight.type,
      columns: insight.affected_columns.join(','),
      connection: selectedConnection,
      table: selectedTable,
    });
    navigate(`/subscriptions?${params.toString()}`);
  };

  // Handle Dismiss - add to dismissed set
  const handleDismiss = (insightId: string) => {
    setDismissedInsights(prev => new Set([...prev, insightId]));
  };

  // Handle Restore - remove from dismissed set
  const handleRestore = (insightId: string) => {
    setDismissedInsights(prev => {
      const newSet = new Set(prev);
      newSet.delete(insightId);
      return newSet;
    });
  };

  // Fetch connections from API
  const fetchConnections = async () => {
    setConnectionsLoading(true);
    try {
      const response = await connectionsApi.list();
      setConnections(response.data || []);
    } catch (err) {
      console.error('Error fetching connections:', err);
    } finally {
      setConnectionsLoading(false);
    }
  };

  // Fetch tables from connection
  const fetchTables = async (connectionId: string) => {
    if (!connectionId) {
      setTables([]);
      return;
    }
    setTablesLoading(true);
    try {
      const response = await quickChartsApi.getTables(connectionId);
      setTables(response.data?.tables || response.data || []);
    } catch (err) {
      console.error('Error fetching tables:', err);
      setTables([]);
    } finally {
      setTablesLoading(false);
    }
  };

  // Analyze data source
  const analyzeDataSource = async () => {
    if (!selectedTable && !selectedConnection) {
      setError('Please select a connection and table to analyze.');
      return;
    }

    if (!selectedConnection) {
      setError('Please select a connection first.');
      return;
    }

    if (!selectedTable) {
      setError('Please select a table to analyze.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      // Parse the selected table (format: "schema.table")
      const [schema, table] = selectedTable.split('.');

      // Get suggestions/insights for the table
      const response = await quickChartsApi.getSuggestions(
        selectedConnection,
        schema || 'public',
        table
      );

      // The response is QuickChartResponse with recommendations array
      const recommendations = response.data?.recommendations || [];

      // Convert recommendations to insights format
      const insightsData: Insight[] = Array.isArray(recommendations) ? recommendations.map((r: any) => {
        // Get column names from dimensions and measures
        const dimensionCols = (r.dimensions || []).map((d: any) => d.column || d.name);
        const measureCols = (r.measures || []).map((m: any) => m.column || m.name);

        // Map chart type to insight type
        const chartTypeToInsightType: Record<string, InsightType> = {
          line: 'trend',
          bar: 'comparison',
          pie: 'distribution',
          scatter: 'correlation',
          area: 'trend',
          histogram: 'distribution',
        };

        // Build clean details with only simple values
        const details: Record<string, unknown> = {};
        if (r.reason) details.reason = r.reason;

        // Add dimension and measure info
        if (dimensionCols.length > 0) {
          details.dimensions = dimensionCols.join(', ');
        }
        if (measureCols.length > 0) {
          details.measures = measureCols.join(', ');
        }

        // Add confidence score
        details.confidence_score = `${Math.round((r.confidence || 0.7) * 100)}%`;

        return {
          id: r.id || `insight-${Math.random().toString(36).substr(2, 9)}`,
          type: chartTypeToInsightType[r.chart_type] || 'comparison',
          severity: (r.confidence > 0.8 ? 'high' : r.confidence > 0.5 ? 'medium' : 'low') as InsightSeverity,
          title: r.title || `${r.chart_type} chart`,
          description: r.description || r.reason || `Recommended ${r.chart_type} visualization`,
          confidence: r.confidence || 0.7,
          affected_columns: [...dimensionCols, ...measureCols],
          suggested_chart_type: r.chart_type,
          generated_at: new Date().toISOString(),
          details,
        };
      }) : [];

      setInsights(insightsData);
    } catch (err) {
      console.error('Error analyzing data:', err);
      setError('Failed to analyze data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Load connections on mount
  useEffect(() => {
    fetchConnections();
  }, []);

  // Fetch tables when connection changes
  useEffect(() => {
    if (selectedConnection) {
      fetchTables(selectedConnection);
      setSelectedTable(''); // Reset table selection
      setInsights([]); // Clear insights
    }
  }, [selectedConnection]);

  // Filter insights
  const filteredInsights = insights.filter(insight => {
    // Filter by dismissed status
    const isDismissed = dismissedInsights.has(insight.id);
    if (isDismissed && !showDismissed) return false;

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
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
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
              {/* Connection Dropdown */}
              <select
                value={selectedConnection}
                onChange={(e) => setSelectedConnection(e.target.value)}
                disabled={connectionsLoading}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
              >
                <option value="">
                  {connectionsLoading ? 'Loading...' : 'All Connections'}
                </option>
                {connections.map((conn) => (
                  <option key={conn.id} value={conn.id}>
                    {conn.name} ({conn.type})
                  </option>
                ))}
              </select>

              {/* Table Dropdown */}
              <select
                value={selectedTable}
                onChange={(e) => setSelectedTable(e.target.value)}
                disabled={tablesLoading || !selectedConnection}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
              >
                <option value="">
                  {tablesLoading ? 'Loading tables...' : !selectedConnection ? 'Select connection first' : 'Select Table'}
                </option>
                {tables.map((t) => (
                  <option key={`${t.schema_name}.${t.table_name}`} value={`${t.schema_name}.${t.table_name}`}>
                    {t.schema_name}.{t.table_name} {t.row_count ? `(${t.row_count} rows)` : ''}
                  </option>
                ))}
              </select>

              <button
                onClick={analyzeDataSource}
                disabled={isLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Analyze
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-24">
        <div className="flex gap-6">
          {/* Sidebar Filters */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 sticky top-6">
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
                <div className="space-y-2 max-h-64 overflow-y-auto">
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
          <div className="flex-1 min-w-0">
            {/* Results header */}
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Showing {sortedInsights.length} of {insights.length} insights
              </span>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
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

            {/* Loading State */}
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">Analyzing data...</p>
                </div>
              </div>
            )}

            {/* Insights List */}
            {!isLoading && (
              <div className="space-y-4">
                {sortedInsights.map((insight) => {
                  const Icon = insightIcons[insight.type] || Activity;
                  const colors = severityColors[insight.severity] || severityColors.low;
                  const isExpanded = expandedInsights.has(insight.id);
                  const isDismissed = dismissedInsights.has(insight.id);

                  return (
                    <div
                      key={insight.id}
                      className={`bg-white dark:bg-gray-800 rounded-lg shadow border ${colors.border} ${isDismissed ? 'opacity-60' : ''}`}
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
                            <div className="flex items-center gap-2 mb-1 flex-wrap">
                              {isDismissed && (
                                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300">
                                  Dismissed
                                </span>
                              )}
                              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${colors.bg} ${colors.text}`}>
                                {insight.severity}
                              </span>
                              <span className="text-xs text-gray-400">
                                {INSIGHT_TYPE_LABELS[insight.type] || insight.type}
                              </span>
                              <span className="text-xs text-gray-400">
                                · {Math.round((insight.confidence || 0) * 100)}% confidence
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
                                {(insight.affected_columns || []).map((col) => (
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
                          {insight.details && Object.keys(insight.details).length > 0 && (
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
                            {dismissedInsights.has(insight.id) ? (
                              <button
                                onClick={() => handleRestore(insight.id)}
                                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-1"
                              >
                                <RefreshCw className="w-3 h-3" />
                                Restore
                              </button>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleExploreInCharts(insight)}
                                  className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-1"
                                >
                                  <ExternalLink className="w-3 h-3" />
                                  Explore in Charts
                                </button>
                                <button
                                  onClick={() => handleCreateAlert(insight)}
                                  className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-1"
                                >
                                  <Bell className="w-3 h-3" />
                                  Create Alert
                                </button>
                                <button
                                  onClick={() => handleDismiss(insight.id)}
                                  className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1"
                                >
                                  <X className="w-3 h-3" />
                                  Dismiss
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}

                {sortedInsights.length === 0 && !isLoading && (
                  <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
                    <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      No insights found
                    </h3>
                    <p className="mt-1 text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                      {selectedTable
                        ? 'Click Analyze to generate insights for the selected table.'
                        : 'Select a connection and table, then click Analyze to generate insights.'}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default QuickInsights;
