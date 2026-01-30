import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactECharts from 'echarts-for-react'
import {
  Sparkles,
  Database,
  Table2,
  Plus,
  Pencil,
  Loader2,
  ChevronRight,
  BarChart3,
  LineChart,
  PieChart,
  TrendingUp,
  Hash,
  TableIcon,
  RefreshCw,
  CheckCircle,
  ArrowRight,
  X,
  Palette,
  Type,
  Settings2,
  ChevronDown,
} from 'lucide-react'
import { quickChartsApi, connectionsApi, dashboardsApi } from '@/lib/api'

interface Connection {
  id: string
  name: string
  type: string
  status: string
}

interface TableSummary {
  schema_name: string
  table_name: string
  row_count: number | null
  column_count: number
  has_numeric: boolean
  has_temporal: boolean
}

interface ChartConfig {
  xAxis?: Record<string, unknown>
  yAxis?: Record<string, unknown>
  series?: Record<string, unknown>[]
  [key: string]: unknown
}

interface ChartRecommendation {
  id: string
  chart_type: string
  confidence: number
  reason: string
  title: string
  description: string
  dimensions: Array<{ column: string; alias: string }>
  measures: Array<{ column: string; aggregation: string; alias: string }>
  chart_config: ChartConfig
  query_config: Record<string, unknown>
}

interface QuickChartResponse {
  connection_id: string
  schema_name: string
  table_name: string
  profile: {
    row_count: number
    columns: Array<{
      name: string
      data_type: string
      cardinality: string
    }>
  }
  recommendations: ChartRecommendation[]
}

interface Dashboard {
  id: string
  name: string
}

interface CustomizationState {
  title: string
  colorTheme: string
  aggregation: string
  chartVariant: string
}

const colorThemes = [
  { id: 'default', name: 'Default', colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'] },
  { id: 'ocean', name: 'Ocean', colors: ['#0ea5e9', '#06b6d4', '#14b8a6', '#10b981', '#22c55e'] },
  { id: 'sunset', name: 'Sunset', colors: ['#f97316', '#ef4444', '#ec4899', '#f43f5e', '#fb923c'] },
  { id: 'forest', name: 'Forest', colors: ['#22c55e', '#16a34a', '#15803d', '#166534', '#14532d'] },
  { id: 'purple', name: 'Purple', colors: ['#8b5cf6', '#a855f7', '#d946ef', '#c026d3', '#7c3aed'] },
  { id: 'monochrome', name: 'Monochrome', colors: ['#374151', '#4b5563', '#6b7280', '#9ca3af', '#d1d5db'] },
]

const aggregationOptions = [
  { id: 'sum', name: 'Sum' },
  { id: 'avg', name: 'Average' },
  { id: 'count', name: 'Count' },
  { id: 'min', name: 'Minimum' },
  { id: 'max', name: 'Maximum' },
]

const chartTypeIcons: Record<string, typeof BarChart3> = {
  bar: BarChart3,
  'horizontal-bar': BarChart3,
  line: LineChart,
  area: TrendingUp,
  pie: PieChart,
  donut: PieChart,
  scatter: Hash,
  kpi: TrendingUp,
  table: TableIcon,
}

export function QuickCharts() {
  const navigate = useNavigate()

  // State
  const [connections, setConnections] = useState<Connection[]>([])
  const [selectedConnection, setSelectedConnection] = useState<string>('')
  const [tables, setTables] = useState<TableSummary[]>([])
  const [selectedTable, setSelectedTable] = useState<string>('')
  const [selectedSchema, setSelectedSchema] = useState<string>('public')
  const [suggestions, setSuggestions] = useState<QuickChartResponse | null>(null)
  const [dashboards, setDashboards] = useState<Dashboard[]>([])

  // Loading states
  const [loadingConnections, setLoadingConnections] = useState(true)
  const [loadingTables, setLoadingTables] = useState(false)
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const [creatingChart, setCreatingChart] = useState<string | null>(null)

  // Modal state
  const [showDashboardModal, setShowDashboardModal] = useState(false)
  const [selectedRecommendation, setSelectedRecommendation] = useState<ChartRecommendation | null>(null)
  const [selectedDashboard, setSelectedDashboard] = useState<string>('')
  const [newDashboardName, setNewDashboardName] = useState('')
  const [createNewDashboard, setCreateNewDashboard] = useState(false)

  // Customization state
  const [customizingChart, setCustomizingChart] = useState<string | null>(null)
  const [customizations, setCustomizations] = useState<Record<string, CustomizationState>>({})
  const [expandedSection, setExpandedSection] = useState<string | null>('title')

  // Fetch connections on mount
  useEffect(() => {
    fetchConnections()
    fetchDashboards()
  }, [])

  // Fetch tables when connection changes
  useEffect(() => {
    if (selectedConnection) {
      fetchTables(selectedConnection)
      setSuggestions(null)
      setSelectedTable('')
    }
  }, [selectedConnection])

  // Fetch suggestions when table changes
  useEffect(() => {
    if (selectedConnection && selectedTable) {
      fetchSuggestions()
    }
  }, [selectedConnection, selectedTable, selectedSchema])

  const fetchConnections = async () => {
    try {
      const response = await connectionsApi.list()
      // Filter to supported connection types (PostgreSQL, MySQL, MongoDB, CSV, Excel)
      const supported = response.data.filter(
        (c: Connection) => ['postgresql', 'mysql', 'mongodb', 'csv', 'excel'].includes(c.type) && c.status === 'connected'
      )
      setConnections(supported)
    } catch (error) {
      console.error('Failed to fetch connections:', error)
    } finally {
      setLoadingConnections(false)
    }
  }

  const fetchTables = async (connectionId: string) => {
    setLoadingTables(true)
    try {
      const response = await quickChartsApi.getTables(connectionId)
      setTables(response.data)
    } catch (error) {
      console.error('Failed to fetch tables:', error)
      setTables([])
    } finally {
      setLoadingTables(false)
    }
  }

  const fetchSuggestions = async () => {
    setLoadingSuggestions(true)
    try {
      const response = await quickChartsApi.getSuggestions(
        selectedConnection,
        selectedSchema,
        selectedTable,
        5
      )
      setSuggestions(response.data)
    } catch (error) {
      console.error('Failed to fetch suggestions:', error)
      setSuggestions(null)
    } finally {
      setLoadingSuggestions(false)
    }
  }

  const fetchDashboards = async () => {
    try {
      const response = await dashboardsApi.list()
      setDashboards(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboards:', error)
    }
  }

  const handleAddToDashboard = (recommendation: ChartRecommendation) => {
    setSelectedRecommendation(recommendation)
    setShowDashboardModal(true)
  }

  const handleCreateChart = async () => {
    if (!selectedRecommendation) return

    setCreatingChart(selectedRecommendation.id)

    try {
      let dashboardId = selectedDashboard

      // Create new dashboard if needed
      if (createNewDashboard && newDashboardName) {
        const dashResponse = await dashboardsApi.create({
          name: newDashboardName,
          description: 'Created from Quick Charts',
          icon: '📊',
        })
        dashboardId = dashResponse.data.id
      }

      // Get customized version if available
      const custom = customizations[selectedRecommendation.id]
      const chartConfig = getCustomizedChartConfig(selectedRecommendation)
      const chartTitle = custom?.title || selectedRecommendation.title

      // Update query_config with new aggregation if changed
      let queryConfig = { ...selectedRecommendation.query_config }
      if (custom?.aggregation && selectedRecommendation.measures?.length > 0) {
        queryConfig = {
          ...queryConfig,
          measures: selectedRecommendation.measures.map(m => ({
            ...m,
            aggregation: custom.aggregation,
          })),
        }
      }

      // Create the chart
      await quickChartsApi.createChart({
        recommendation_id: selectedRecommendation.id,
        title: chartTitle,
        dashboard_id: dashboardId || null,
        connection_id: selectedConnection,
        chart_type: selectedRecommendation.chart_type,
        chart_config: chartConfig,
        query_config: queryConfig,
      })

      // Close modal and navigate
      setShowDashboardModal(false)
      setSelectedRecommendation(null)

      if (dashboardId) {
        navigate(`/dashboards/${dashboardId}`)
      } else {
        navigate('/dashboards')
      }
    } catch (error) {
      console.error('Failed to create chart:', error)
      alert('Failed to create chart. Please try again.')
    } finally {
      setCreatingChart(null)
    }
  }

  const handleCustomize = (recommendation: ChartRecommendation) => {
    // Toggle customization panel for this chart
    if (customizingChart === recommendation.id) {
      setCustomizingChart(null)
    } else {
      setCustomizingChart(recommendation.id)
      // Initialize customizations if not set
      if (!customizations[recommendation.id]) {
        const currentAggregation = recommendation.measures?.[0]?.aggregation || 'sum'
        setCustomizations(prev => ({
          ...prev,
          [recommendation.id]: {
            title: recommendation.title,
            colorTheme: 'default',
            aggregation: currentAggregation,
            chartVariant: recommendation.chart_type,
          }
        }))
      }
    }
  }

  const handleAdvancedCustomize = (recommendation: ChartRecommendation) => {
    // Navigate to chart builder with customizations applied
    const custom = customizations[recommendation.id]
    navigate('/charts/new', {
      state: {
        fromQuickChart: {
          ...recommendation,
          title: custom?.title || recommendation.title,
          connection_id: selectedConnection,
          schema: selectedSchema,
          table: selectedTable,
        },
      },
    })
  }

  const updateCustomization = (recId: string, field: keyof CustomizationState, value: string) => {
    setCustomizations(prev => ({
      ...prev,
      [recId]: {
        ...prev[recId],
        [field]: value,
      }
    }))
  }

  const getCustomizedChartConfig = (recommendation: ChartRecommendation) => {
    const custom = customizations[recommendation.id]
    if (!custom) return recommendation.chart_config

    const theme = colorThemes.find(t => t.id === custom.colorTheme)
    const colors = theme?.colors || colorThemes[0].colors

    return {
      ...recommendation.chart_config,
      color: colors,
      series: recommendation.chart_config.series?.map((s: Record<string, unknown>, i: number) => ({
        ...s,
        itemStyle: { color: colors[i % colors.length] },
      })),
    }
  }

  const getCustomizedRecommendation = (recommendation: ChartRecommendation): ChartRecommendation => {
    const custom = customizations[recommendation.id]
    if (!custom) return recommendation

    return {
      ...recommendation,
      title: custom.title,
      chart_config: getCustomizedChartConfig(recommendation),
      measures: recommendation.measures.map(m => ({
        ...m,
        aggregation: custom.aggregation,
      })),
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'bg-green-100 text-green-700'
    if (confidence >= 0.8) return 'bg-blue-100 text-blue-700'
    return 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="h-full overflow-auto">
      <div className="p-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quick Charts</h1>
          <p className="text-gray-500">
            Select a data source and table to automatically generate chart suggestions
          </p>
        </div>
      </div>

      {/* Selection Controls */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Connection Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Database className="w-4 h-4 inline mr-1" />
              Data Connection
            </label>
            <select
              value={selectedConnection}
              onChange={(e) => setSelectedConnection(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loadingConnections}
            >
              <option value="">Select a connection...</option>
              {connections.map((conn) => (
                <option key={conn.id} value={conn.id}>
                  {conn.name} ({conn.type})
                </option>
              ))}
            </select>
          </div>

          {/* Table Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Table2 className="w-4 h-4 inline mr-1" />
              Table
            </label>
            <select
              value={selectedTable}
              onChange={(e) => {
                const [schema, table] = e.target.value.split('.')
                setSelectedSchema(schema)
                setSelectedTable(table)
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={!selectedConnection || loadingTables}
            >
              <option value="">Select a table...</option>
              {tables.map((t) => (
                <option key={`${t.schema_name}.${t.table_name}`} value={`${t.schema_name}.${t.table_name}`}>
                  {t.table_name}
                  {t.row_count !== null && ` (${t.row_count.toLocaleString()} rows)`}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Table Chips */}
        {selectedConnection && tables.length > 0 && !selectedTable && (
          <div className="mt-4">
            <p className="text-sm text-gray-500 mb-2">Or click a table to explore:</p>
            <div className="flex flex-wrap gap-2">
              {tables.slice(0, 8).map((t) => (
                <button
                  key={`${t.schema_name}.${t.table_name}`}
                  onClick={() => {
                    setSelectedSchema(t.schema_name)
                    setSelectedTable(t.table_name)
                  }}
                  className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 flex items-center gap-1.5 transition-colors"
                >
                  <Table2 className="w-3.5 h-3.5" />
                  {t.table_name}
                  {t.has_numeric && t.has_temporal && (
                    <span className="w-2 h-2 bg-green-500 rounded-full" title="Has numeric and temporal data" />
                  )}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loadingSuggestions && (
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="w-10 h-10 animate-spin text-blue-500 mb-4" />
          <p className="text-gray-600 font-medium">Analyzing your data...</p>
          <p className="text-gray-400 text-sm">This may take a few seconds</p>
        </div>
      )}

      {/* No Selection State */}
      {!selectedConnection && !loadingConnections && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
          <Database className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Data Connection</h3>
          <p className="text-gray-500 mb-4">
            Choose a database connection to explore your data and get chart suggestions
          </p>
          <button
            onClick={() => navigate('/connections')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Connection
          </button>
        </div>
      )}

      {/* Chart Suggestions */}
      {suggestions && !loadingSuggestions && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Suggested Charts for "{selectedTable}"
              </h2>
              <p className="text-sm text-gray-500">
                {suggestions.profile.row_count.toLocaleString()} rows, {suggestions.profile.columns.length} columns
              </p>
            </div>
            <button
              onClick={fetchSuggestions}
              className="px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>

          {suggestions.recommendations.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-xl">
              <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Suggestions Available</h3>
              <p className="text-gray-500">
                This table may not have suitable data for automatic chart generation.
              </p>
              <button
                onClick={() => navigate('/charts/new')}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 inline-flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Create Custom Chart
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {suggestions.recommendations.map((rec) => {
                const IconComponent = chartTypeIcons[rec.chart_type] || BarChart3
                const isCustomizing = customizingChart === rec.id
                const custom = customizations[rec.id]
                const displayRec = getCustomizedRecommendation(rec)
                const chartConfig = getCustomizedChartConfig(rec)
                const currentTheme = colorThemes.find(t => t.id === (custom?.colorTheme || 'default')) || colorThemes[0]

                return (
                  <div
                    key={rec.id}
                    className={`bg-white rounded-xl border overflow-hidden transition-all ${
                      isCustomizing ? 'border-blue-300 shadow-lg ring-2 ring-blue-100' : 'border-gray-200 hover:shadow-lg'
                    }`}
                  >
                    {/* Header */}
                    <div className="p-4 border-b border-gray-100">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <div className="p-1.5 bg-blue-100 rounded-lg">
                            <IconComponent className="w-4 h-4 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900 text-sm">{custom?.title || rec.title}</h3>
                            <p className="text-xs text-gray-500 capitalize">{rec.chart_type.replace('-', ' ')} Chart</p>
                          </div>
                        </div>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full font-medium ${getConfidenceColor(rec.confidence)}`}
                        >
                          {Math.round(rec.confidence * 100)}%
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">{rec.reason}</p>
                    </div>

                    {/* Chart Preview */}
                    <div className="h-48 p-2 bg-gray-50">
                      {rec.chart_type === 'kpi' ? (
                        <div className="h-full flex flex-col items-center justify-center">
                          <div className="text-3xl font-bold text-gray-900">--</div>
                          <div className="text-sm text-gray-500">{custom?.title || rec.title}</div>
                          <div className="text-xs text-green-600 mt-1">Preview with real data</div>
                        </div>
                      ) : rec.chart_type === 'table' ? (
                        <div className="h-full flex flex-col items-center justify-center">
                          <TableIcon className="w-12 h-12 text-gray-300 mb-2" />
                          <div className="text-sm text-gray-500">Data Table</div>
                        </div>
                      ) : (
                        <ReactECharts
                          option={{
                            ...chartConfig,
                            title: { show: false },
                            legend: { show: false },
                            grid: { top: 10, right: 10, bottom: 20, left: 40 },
                            color: currentTheme.colors,
                            xAxis: chartConfig.xAxis
                              ? {
                                  ...chartConfig.xAxis,
                                  data: ['A', 'B', 'C', 'D', 'E'],
                                }
                              : undefined,
                            yAxis: chartConfig.yAxis,
                            series: chartConfig.series?.map((s: Record<string, unknown>, i: number) => ({
                              ...s,
                              itemStyle: { color: currentTheme.colors[i % currentTheme.colors.length] },
                              data:
                                rec.chart_type === 'pie' || rec.chart_type === 'donut'
                                  ? [
                                      { value: 40, name: 'A', itemStyle: { color: currentTheme.colors[0] } },
                                      { value: 30, name: 'B', itemStyle: { color: currentTheme.colors[1] } },
                                      { value: 20, name: 'C', itemStyle: { color: currentTheme.colors[2] } },
                                      { value: 10, name: 'D', itemStyle: { color: currentTheme.colors[3] } },
                                    ]
                                  : rec.chart_type === 'scatter'
                                  ? [[10, 20], [20, 40], [30, 35], [40, 50], [50, 45]]
                                  : [40, 65, 45, 80, 55],
                            })),
                          }}
                          style={{ height: '100%', width: '100%' }}
                          opts={{ renderer: 'canvas' }}
                        />
                      )}
                    </div>

                    {/* Customization Panel */}
                    {isCustomizing && custom && (
                      <div className="border-t border-gray-200 bg-gray-50">
                        {/* Title Section */}
                        <div className="border-b border-gray-200">
                          <button
                            onClick={() => setExpandedSection(expandedSection === 'title' ? null : 'title')}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-100"
                          >
                            <div className="flex items-center gap-2">
                              <Type className="w-4 h-4 text-gray-500" />
                              <span className="text-sm font-medium text-gray-700">Title</span>
                            </div>
                            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${expandedSection === 'title' ? 'rotate-180' : ''}`} />
                          </button>
                          {expandedSection === 'title' && (
                            <div className="px-4 pb-3">
                              <input
                                type="text"
                                value={custom.title}
                                onChange={(e) => updateCustomization(rec.id, 'title', e.target.value)}
                                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Chart title"
                              />
                            </div>
                          )}
                        </div>

                        {/* Color Theme Section */}
                        <div className="border-b border-gray-200">
                          <button
                            onClick={() => setExpandedSection(expandedSection === 'colors' ? null : 'colors')}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-100"
                          >
                            <div className="flex items-center gap-2">
                              <Palette className="w-4 h-4 text-gray-500" />
                              <span className="text-sm font-medium text-gray-700">Colors</span>
                              <div className="flex gap-0.5 ml-2">
                                {currentTheme.colors.slice(0, 5).map((color, i) => (
                                  <div key={i} className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                                ))}
                              </div>
                            </div>
                            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${expandedSection === 'colors' ? 'rotate-180' : ''}`} />
                          </button>
                          {expandedSection === 'colors' && (
                            <div className="px-4 pb-3">
                              <div className="grid grid-cols-3 gap-2">
                                {colorThemes.map((theme) => (
                                  <button
                                    key={theme.id}
                                    onClick={() => updateCustomization(rec.id, 'colorTheme', theme.id)}
                                    className={`p-2 rounded-lg border transition-all ${
                                      custom.colorTheme === theme.id
                                        ? 'border-blue-500 bg-blue-50'
                                        : 'border-gray-200 hover:border-gray-300'
                                    }`}
                                  >
                                    <div className="flex gap-0.5 justify-center mb-1">
                                      {theme.colors.slice(0, 5).map((color, i) => (
                                        <div key={i} className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                                      ))}
                                    </div>
                                    <div className="text-xs text-gray-600">{theme.name}</div>
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Aggregation Section */}
                        {rec.measures && rec.measures.length > 0 && (
                          <div className="border-b border-gray-200">
                            <button
                              onClick={() => setExpandedSection(expandedSection === 'aggregation' ? null : 'aggregation')}
                              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-100"
                            >
                              <div className="flex items-center gap-2">
                                <Settings2 className="w-4 h-4 text-gray-500" />
                                <span className="text-sm font-medium text-gray-700">Aggregation</span>
                                <span className="text-xs text-gray-400 bg-gray-200 px-2 py-0.5 rounded capitalize">{custom.aggregation}</span>
                              </div>
                              <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${expandedSection === 'aggregation' ? 'rotate-180' : ''}`} />
                            </button>
                            {expandedSection === 'aggregation' && (
                              <div className="px-4 pb-3">
                                <div className="flex flex-wrap gap-2">
                                  {aggregationOptions.map((agg) => (
                                    <button
                                      key={agg.id}
                                      onClick={() => updateCustomization(rec.id, 'aggregation', agg.id)}
                                      className={`px-3 py-1.5 text-xs rounded-lg border transition-all ${
                                        custom.aggregation === agg.id
                                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                                          : 'border-gray-200 text-gray-600 hover:border-gray-300'
                                      }`}
                                    >
                                      {agg.name}
                                    </button>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Advanced Button */}
                        <div className="px-4 py-3">
                          <button
                            onClick={() => handleAdvancedCustomize(rec)}
                            className="w-full px-3 py-2 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg flex items-center justify-center gap-1.5 transition-colors"
                          >
                            <Settings2 className="w-4 h-4" />
                            Open in Chart Builder
                            <ArrowRight className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="p-3 bg-white border-t border-gray-100 flex gap-2">
                      <button
                        onClick={() => handleAddToDashboard(isCustomizing ? displayRec : rec)}
                        disabled={creatingChart === rec.id}
                        className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-1.5"
                      >
                        {creatingChart === rec.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Plus className="w-4 h-4" />
                        )}
                        Add to Dashboard
                      </button>
                      <button
                        onClick={() => handleCustomize(rec)}
                        className={`px-3 py-2 border text-sm rounded-lg flex items-center gap-1.5 transition-colors ${
                          isCustomizing
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        {isCustomizing ? (
                          <>
                            <X className="w-4 h-4" />
                            Close
                          </>
                        ) : (
                          <>
                            <Pencil className="w-4 h-4" />
                            Customize
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
      </div>

      {/* Dashboard Selection Modal */}
      {showDashboardModal && selectedRecommendation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Chart to Dashboard</h3>

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-4">
                Chart: <span className="font-medium">{selectedRecommendation.title}</span>
              </p>

              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="dashboard-option"
                    checked={!createNewDashboard}
                    onChange={() => setCreateNewDashboard(false)}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Add to existing dashboard</span>
                </label>

                {!createNewDashboard && (
                  <select
                    value={selectedDashboard}
                    onChange={(e) => setSelectedDashboard(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="">Select a dashboard...</option>
                    {dashboards.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                )}

                <label className="flex items-center">
                  <input
                    type="radio"
                    name="dashboard-option"
                    checked={createNewDashboard}
                    onChange={() => setCreateNewDashboard(true)}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Create new dashboard</span>
                </label>

                {createNewDashboard && (
                  <input
                    type="text"
                    value={newDashboardName}
                    onChange={(e) => setNewDashboardName(e.target.value)}
                    placeholder="Dashboard name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                )}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDashboardModal(false)
                  setSelectedRecommendation(null)
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateChart}
                disabled={
                  creatingChart !== null ||
                  (!createNewDashboard && !selectedDashboard) ||
                  (createNewDashboard && !newDashboardName)
                }
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {creatingChart ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <CheckCircle className="w-4 h-4" />
                )}
                Add Chart
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default QuickCharts
