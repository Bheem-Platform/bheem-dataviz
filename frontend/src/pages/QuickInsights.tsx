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
  Sparkles,
  Layers,
  Lightbulb,
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

const severityColors: Record<InsightSeverity, { bg: string; text: string; border: string; icon: string }> = {
  high: { bg: 'bg-red-50 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400', border: 'border-red-200 dark:border-red-800', icon: 'text-red-500' },
  medium: { bg: 'bg-amber-50 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-400', border: 'border-amber-200 dark:border-amber-800', icon: 'text-amber-500' },
  low: { bg: 'bg-blue-50 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400', border: 'border-blue-200 dark:border-blue-800', icon: 'text-blue-500' },
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
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-white to-indigo-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-950/20">
      {/* Header */}
      <div className="px-6 lg:px-8 py-6 border-b border-gray-200/60 dark:border-gray-700/60 bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto">
          {/* Title Row */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                <Lightbulb className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Quick Insights
                </h1>
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  AI-powered data analysis and pattern detection
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {/* Connection Dropdown */}
              <div className="relative min-w-[200px]">
                <Database className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <select
                  value={selectedConnection}
                  onChange={(e) => setSelectedConnection(e.target.value)}
                  disabled={connectionsLoading}
                  className="w-full pl-10 pr-10 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all disabled:opacity-50"
                >
                  <option value="">
                    {connectionsLoading ? 'Loading...' : 'Select Connection'}
                  </option>
                  {connections.map((conn) => (
                    <option key={conn.id} value={conn.id}>
                      {conn.name} ({conn.type})
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>

              {/* Table Dropdown */}
              <div className="relative min-w-[220px]">
                <Layers className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <select
                  value={selectedTable}
                  onChange={(e) => setSelectedTable(e.target.value)}
                  disabled={tablesLoading || !selectedConnection}
                  className="w-full pl-10 pr-10 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all disabled:opacity-50"
                >
                  <option value="">
                    {tablesLoading ? 'Loading...' : !selectedConnection ? 'Select connection first' : 'Select Table'}
                  </option>
                  {tables.map((t) => (
                    <option key={`${t.schema_name}.${t.table_name}`} value={`${t.schema_name}.${t.table_name}`}>
                      {t.schema_name}.{t.table_name} {t.row_count ? `(${t.row_count} rows)` : ''}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>

              <button
                onClick={analyzeDataSource}
                disabled={isLoading}
                className="group flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium rounded-xl hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
                Analyze
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 text-sm flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/50 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-4 h-4 text-red-500" />
              </div>
              {error}
            </div>
          )}

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-xl hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                <Sparkles className="w-4 h-4 text-indigo-500" />
                <span>Total Insights</span>
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {summary.total}
              </div>
            </div>
            <div className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-xl hover:shadow-red-500/10 hover:border-red-300 dark:hover:border-red-600 transition-all duration-300">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                <span>High Priority</span>
              </div>
              <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                {summary.high}
              </div>
            </div>
            <div className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-xl hover:shadow-amber-500/10 hover:border-amber-300 dark:hover:border-amber-600 transition-all duration-300">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                <Activity className="w-4 h-4 text-amber-500" />
                <span>Medium Priority</span>
              </div>
              <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                {summary.medium}
              </div>
            </div>
            <div className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-xl hover:shadow-blue-500/10 hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-300">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                <Info className="w-4 h-4 text-blue-500" />
                <span>Low Priority</span>
              </div>
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {summary.low}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex gap-6">
            {/* Sidebar Filters */}
            <div className="w-64 flex-shrink-0">
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 sticky top-6">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <Filter className="w-4 h-4 text-indigo-500" />
                  Filters
                </h3>

                {/* Severity Filter */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Severity
                  </label>
                  <div className="relative">
                    <select
                      value={selectedSeverity}
                      onChange={(e) => setSelectedSeverity(e.target.value as any)}
                      className="w-full px-3 py-2.5 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl text-sm text-gray-900 dark:text-white appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                    >
                      <option value="all">All Severities</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                  </div>
                </div>

                {/* Type Filters */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Insight Types
                  </label>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {(Object.keys(INSIGHT_TYPE_LABELS) as InsightType[]).map((type) => {
                      const Icon = insightIcons[type];
                      const count = insightsByType[type]?.length || 0;
                      const isSelected = selectedTypes.length === 0 || selectedTypes.includes(type);
                      return (
                        <label
                          key={type}
                          className={`flex items-center gap-3 text-sm cursor-pointer p-2 rounded-lg transition-colors ${
                            isSelected ? 'bg-indigo-50 dark:bg-indigo-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleTypeFilter(type)}
                            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                          />
                          <Icon className={`w-4 h-4 ${isSelected ? 'text-indigo-500' : 'text-gray-400'}`} />
                          <span className={`flex-1 ${isSelected ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'}`}>
                            {INSIGHT_TYPE_LABELS[type]}
                          </span>
                          <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                            count > 0 ? 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400' : 'bg-gray-100 dark:bg-gray-700 text-gray-400'
                          }`}>
                            {count}
                          </span>
                        </label>
                      );
                    })}
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button className="w-full px-4 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-xl flex items-center justify-center gap-2 transition-colors">
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
                <button
                  onClick={() => setShowDismissed(!showDismissed)}
                  className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg transition-colors ${
                    showDismissed
                      ? 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  {showDismissed ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                  {showDismissed ? 'Showing Dismissed' : 'Show Dismissed'}
                </button>
              </div>

              {/* Loading State */}
              {isLoading && (
                <div className="flex flex-col items-center justify-center py-16">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mb-4 animate-pulse">
                    <RefreshCw className="w-8 h-8 text-white animate-spin" />
                  </div>
                  <p className="text-gray-500 dark:text-gray-400">Analyzing data...</p>
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
                        className={`bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border ${colors.border} overflow-hidden hover:shadow-xl hover:shadow-indigo-500/5 transition-all duration-300 ${isDismissed ? 'opacity-60' : ''}`}
                      >
                        {/* Insight Header */}
                        <div
                          className="p-5 cursor-pointer"
                          onClick={() => toggleExpand(insight.id)}
                        >
                          <div className="flex items-start gap-4">
                            <div className={`w-12 h-12 rounded-xl ${colors.bg} ${colors.border} border flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}>
                              <Icon className={`w-6 h-6 ${colors.icon}`} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                                {isDismissed && (
                                  <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300">
                                    Dismissed
                                  </span>
                                )}
                                <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full ${colors.bg} ${colors.text} capitalize`}>
                                  {insight.severity}
                                </span>
                                <span className="text-xs text-gray-400 dark:text-gray-500">
                                  {INSIGHT_TYPE_LABELS[insight.type] || insight.type}
                                </span>
                                <span className="text-xs text-gray-400 dark:text-gray-500">
                                  · {Math.round((insight.confidence || 0) * 100)}% confidence
                                </span>
                              </div>
                              <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                                {insight.title}
                              </h3>
                              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                                {insight.description}
                              </p>
                            </div>
                            <button className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-500 dark:text-gray-400 transition-colors">
                              {isExpanded ? (
                                <ChevronDown className="w-4 h-4" />
                              ) : (
                                <ChevronRight className="w-4 h-4" />
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Expanded Details */}
                        {isExpanded && (
                          <div className="px-5 pb-5 border-t border-gray-100 dark:border-gray-700">
                            <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                              <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50">
                                <span className="text-xs text-gray-500 dark:text-gray-400 block mb-2">Affected Columns</span>
                                <div className="flex flex-wrap gap-1.5">
                                  {(insight.affected_columns || []).map((col) => (
                                    <span
                                      key={col}
                                      className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/50 rounded-lg text-indigo-700 dark:text-indigo-300 text-xs font-medium"
                                    >
                                      {col}
                                    </span>
                                  ))}
                                </div>
                              </div>
                              {insight.suggested_chart_type && (
                                <div className="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50">
                                  <span className="text-xs text-gray-500 dark:text-gray-400 block mb-2">Suggested Visualization</span>
                                  <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/50 rounded-lg text-purple-700 dark:text-purple-300 text-xs font-medium capitalize">
                                    {insight.suggested_chart_type} chart
                                  </span>
                                </div>
                              )}
                            </div>

                            {/* Details from insight */}
                            {insight.details && Object.keys(insight.details).length > 0 && (
                              <div className="mt-4 p-4 bg-gradient-to-r from-indigo-50/50 to-purple-50/50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800/50">
                                <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase mb-3 flex items-center gap-2">
                                  <Info className="w-3 h-3" />
                                  Details
                                </h4>
                                <dl className="grid grid-cols-2 gap-3 text-sm">
                                  {Object.entries(insight.details).map(([key, value]) => (
                                    <div key={key} className="flex flex-col">
                                      <dt className="text-xs text-gray-500 dark:text-gray-400 capitalize mb-0.5">
                                        {key.replace(/_/g, ' ')}
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
                                  className="px-4 py-2 text-sm bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 flex items-center gap-2 font-medium shadow-lg shadow-emerald-500/25 transition-all"
                                >
                                  <RefreshCw className="w-4 h-4" />
                                  Restore
                                </button>
                              ) : (
                                <>
                                  <button
                                    onClick={() => handleExploreInCharts(insight)}
                                    className="px-4 py-2 text-sm bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 flex items-center gap-2 font-medium shadow-lg shadow-indigo-500/25 transition-all"
                                  >
                                    <ExternalLink className="w-4 h-4" />
                                    Explore in Charts
                                  </button>
                                  <button
                                    onClick={() => handleCreateAlert(insight)}
                                    className="px-4 py-2 text-sm border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2 font-medium transition-colors"
                                  >
                                    <Bell className="w-4 h-4" />
                                    Create Alert
                                  </button>
                                  <button
                                    onClick={() => handleDismiss(insight.id)}
                                    className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl flex items-center gap-2 transition-colors"
                                  >
                                    <X className="w-4 h-4" />
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
                    <div className="flex flex-col items-center justify-center py-16 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60">
                      <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mb-6 shadow-lg shadow-purple-500/25">
                        <Lightbulb className="w-10 h-10 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                        No insights found
                      </h3>
                      <p className="text-gray-500 dark:text-gray-400 max-w-md text-center">
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
    </div>
  );
}

export default QuickInsights;
