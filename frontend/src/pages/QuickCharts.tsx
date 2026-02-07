import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import ReactECharts from 'echarts-for-react'
import {
  Sparkles,
  Database,
  Table2,
  Plus,
  Pencil,
  Loader2,
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
  ChevronRight,
  Layers,
  Zap,
  Star,
  ExternalLink,
  Check,
} from 'lucide-react'
import { quickChartsApi, connectionsApi, dashboardsApi } from '@/lib/api'
import { cn } from '@/lib/utils'

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
  { id: 'default', name: 'Default', colors: ['#667eea', '#764ba2', '#f093fb', '#5ee7df', '#b490ca'] },
  { id: 'ocean', name: 'Ocean', colors: ['#0ea5e9', '#06b6d4', '#14b8a6', '#10b981', '#22c55e'] },
  { id: 'sunset', name: 'Sunset', colors: ['#f97316', '#ef4444', '#ec4899', '#f43f5e', '#fb923c'] },
  { id: 'forest', name: 'Forest', colors: ['#22c55e', '#16a34a', '#15803d', '#166534', '#14532d'] },
  { id: 'purple', name: 'Purple', colors: ['#8b5cf6', '#a855f7', '#d946ef', '#c026d3', '#7c3aed'] },
  { id: 'mono', name: 'Mono', colors: ['#374151', '#4b5563', '#6b7280', '#9ca3af', '#d1d5db'] },
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

const chartTypeColors: Record<string, string> = {
  bar: 'from-blue-500 to-indigo-600',
  'horizontal-bar': 'from-blue-500 to-indigo-600',
  line: 'from-emerald-500 to-teal-600',
  area: 'from-purple-500 to-pink-600',
  pie: 'from-amber-500 to-orange-600',
  donut: 'from-rose-500 to-red-600',
  scatter: 'from-cyan-500 to-blue-600',
  kpi: 'from-violet-500 to-purple-600',
  table: 'from-gray-500 to-slate-600',
}

export function QuickCharts() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const initialConnection = searchParams.get('connection') || ''
  const initialSchema = searchParams.get('schema') || 'public'
  const initialTable = searchParams.get('table') || ''

  const [connections, setConnections] = useState<Connection[]>([])
  const [selectedConnection, setSelectedConnection] = useState<string>(initialConnection)
  const [tables, setTables] = useState<TableSummary[]>([])
  const [selectedTable, setSelectedTable] = useState<string>(initialTable)
  const [selectedSchema, setSelectedSchema] = useState<string>(initialSchema)
  const [suggestions, setSuggestions] = useState<QuickChartResponse | null>(null)
  const [dashboards, setDashboards] = useState<Dashboard[]>([])

  const [loadingConnections, setLoadingConnections] = useState(true)
  const [loadingTables, setLoadingTables] = useState(false)
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const [creatingChart, setCreatingChart] = useState<string | null>(null)

  const [showDashboardModal, setShowDashboardModal] = useState(false)
  const [selectedRecommendation, setSelectedRecommendation] = useState<ChartRecommendation | null>(null)
  const [selectedDashboard, setSelectedDashboard] = useState<string>('')
  const [newDashboardName, setNewDashboardName] = useState('')
  const [createNewDashboard, setCreateNewDashboard] = useState(false)

  const [customizingChart, setCustomizingChart] = useState<string | null>(null)
  const [customizations, setCustomizations] = useState<Record<string, CustomizationState>>({})

  const [isInitialLoad, setIsInitialLoad] = useState(!!initialConnection)

  useEffect(() => {
    fetchConnections()
    fetchDashboards()
  }, [])

  useEffect(() => {
    if (selectedConnection) {
      fetchTables(selectedConnection)
      setSuggestions(null)
      if (!isInitialLoad) setSelectedTable('')
    }
  }, [selectedConnection])

  useEffect(() => {
    if (selectedConnection && selectedTable) {
      fetchSuggestions()
      setIsInitialLoad(false)
    }
  }, [selectedConnection, selectedTable, selectedSchema])

  const fetchConnections = async () => {
    try {
      const response = await connectionsApi.list()
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

      if (createNewDashboard && newDashboardName) {
        const dashResponse = await dashboardsApi.create({
          name: newDashboardName,
          description: 'Created from Quick Charts',
          icon: '📊',
        })
        dashboardId = dashResponse.data.id
      }

      const custom = customizations[selectedRecommendation.id]
      const chartConfig = getCustomizedChartConfig(selectedRecommendation)
      const chartTitle = custom?.title || selectedRecommendation.title

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

      await quickChartsApi.createChart({
        recommendation_id: selectedRecommendation.id,
        title: chartTitle,
        dashboard_id: dashboardId || null,
        connection_id: selectedConnection,
        chart_type: selectedRecommendation.chart_type,
        chart_config: chartConfig,
        query_config: queryConfig,
      })

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
    if (customizingChart === recommendation.id) {
      setCustomizingChart(null)
    } else {
      setCustomizingChart(recommendation.id)
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

  const selectedConnectionData = connections.find(c => c.id === selectedConnection)

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-950">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg shadow-orange-500/25">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Quick Charts</h1>
              <p className="text-gray-500 dark:text-gray-400">AI-powered chart recommendations from your data</p>
            </div>
          </div>
        </div>

        {/* Data Source Selection - Bento Style */}
        <div className="bento-grid mb-8">
          {/* Connection Selector Card */}
          <div className="bento-card col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                <Database className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Data Connection</h3>
                <p className="text-sm text-gray-500">Select your data source</p>
              </div>
            </div>

            {loadingConnections ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
              </div>
            ) : connections.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-gray-500 mb-4">No connections available</p>
                <button
                  onClick={() => navigate('/connections')}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors text-sm font-medium"
                >
                  <Plus className="w-4 h-4" />
                  Add Connection
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                {connections.slice(0, 6).map((conn) => (
                  <button
                    key={conn.id}
                    onClick={() => setSelectedConnection(conn.id)}
                    className={cn(
                      "flex items-center gap-3 p-3 rounded-xl border-2 transition-all text-left",
                      selectedConnection === conn.id
                        ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
                        : "border-gray-100 dark:border-gray-800 hover:border-gray-200 dark:hover:border-gray-700"
                    )}
                  >
                    <div className={cn(
                      "w-8 h-8 rounded-lg flex items-center justify-center",
                      selectedConnection === conn.id
                        ? "bg-primary-500 text-white"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-500"
                    )}>
                      <Database className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white truncate">{conn.name}</p>
                      <p className="text-xs text-gray-500 capitalize">{conn.type}</p>
                    </div>
                    {selectedConnection === conn.id && (
                      <Check className="w-5 h-5 text-primary-500 ml-auto flex-shrink-0" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Table Selector Card */}
          <div className="bento-card col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                <Table2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Table</h3>
                <p className="text-sm text-gray-500">Choose a table to analyze</p>
              </div>
            </div>

            {!selectedConnection ? (
              <div className="text-center py-8 text-gray-400">
                <Layers className="w-10 h-10 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Select a connection first</p>
              </div>
            ) : loadingTables ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
              </div>
            ) : tables.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p className="text-sm">No tables found</p>
              </div>
            ) : (
              <div className="flex flex-wrap gap-2 max-h-[200px] overflow-auto">
                {tables.map((t) => (
                  <button
                    key={`${t.schema_name}.${t.table_name}`}
                    onClick={() => {
                      setSelectedSchema(t.schema_name)
                      setSelectedTable(t.table_name)
                    }}
                    className={cn(
                      "inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all",
                      selectedTable === t.table_name && selectedSchema === t.schema_name
                        ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/25"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
                    )}
                  >
                    <Table2 className="w-3.5 h-3.5" />
                    {t.table_name}
                    {t.has_numeric && t.has_temporal && (
                      <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Loading State */}
        {loadingSuggestions && (
          <div className="bento-card col-span-full py-16">
            <div className="text-center">
              <div className="relative inline-block">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center animate-pulse">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <div className="absolute inset-0 rounded-2xl bg-primary-500/20 blur-xl animate-pulse" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mt-6 mb-2">
                Analyzing your data...
              </h3>
              <p className="text-gray-500">Our AI is finding the best chart recommendations</p>
            </div>
          </div>
        )}

        {/* No Selection State */}
        {!selectedConnection && !loadingConnections && !loadingSuggestions && (
          <div className="bento-card col-span-full py-16">
            <div className="text-center max-w-md mx-auto">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-800 dark:to-gray-900 flex items-center justify-center mx-auto mb-6">
                <Database className="w-10 h-10 text-gray-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                Select a data source
              </h3>
              <p className="text-gray-500 mb-8">
                Choose a database connection to get AI-powered chart recommendations based on your data.
              </p>
            </div>
          </div>
        )}

        {/* Chart Recommendations */}
        {suggestions && !loadingSuggestions && (
          <div>
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  Recommended Charts
                </h2>
                <p className="text-gray-500">
                  {suggestions.recommendations.length} suggestions for <span className="font-medium text-gray-900 dark:text-white">{selectedTable}</span>
                  <span className="mx-2">•</span>
                  {suggestions.profile.row_count.toLocaleString()} rows
                </p>
              </div>
              <button
                onClick={fetchSuggestions}
                className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-gray-700 dark:text-gray-300 font-medium"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
            </div>

            {suggestions.recommendations.length === 0 ? (
              <div className="bento-card py-16">
                <div className="text-center">
                  <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    No recommendations available
                  </h3>
                  <p className="text-gray-500 mb-6">
                    This table may not have suitable data for automatic chart generation.
                  </p>
                  <button
                    onClick={() => navigate('/charts/new')}
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-medium"
                  >
                    <Plus className="w-5 h-5" />
                    Create Custom Chart
                  </button>
                </div>
              </div>
            ) : (
              <div className="bento-grid">
                {suggestions.recommendations.map((rec, index) => {
                  const IconComponent = chartTypeIcons[rec.chart_type] || BarChart3
                  const gradientClass = chartTypeColors[rec.chart_type] || 'from-gray-500 to-slate-600'
                  const isCustomizing = customizingChart === rec.id
                  const custom = customizations[rec.id]
                  const currentTheme = colorThemes.find(t => t.id === (custom?.colorTheme || 'default')) || colorThemes[0]
                  const chartConfig = getCustomizedChartConfig(rec)

                  return (
                    <div
                      key={rec.id}
                      className={cn(
                        "bento-card group",
                        index === 0 && "col-span-2 row-span-2",
                        isCustomizing && "ring-2 ring-primary-500"
                      )}
                    >
                      {/* Card Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className={cn(
                            "w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center",
                            gradientClass
                          )}>
                            <IconComponent className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white">
                              {custom?.title || rec.title}
                            </h3>
                            <p className="text-xs text-gray-500 capitalize">{rec.chart_type.replace('-', ' ')} Chart</p>
                          </div>
                        </div>
                        <div className={cn(
                          "px-2.5 py-1 rounded-full text-xs font-semibold",
                          rec.confidence >= 0.9
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                            : rec.confidence >= 0.8
                            ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                            : "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
                        )}>
                          {Math.round(rec.confidence * 100)}% match
                        </div>
                      </div>

                      {/* Reason */}
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                        {rec.reason}
                      </p>

                      {/* Chart Preview */}
                      <div className={cn(
                        "rounded-xl bg-gray-50 dark:bg-gray-800/50 overflow-hidden mb-4",
                        index === 0 ? "h-64" : "h-40"
                      )}>
                        {rec.chart_type === 'kpi' ? (
                          <div className="h-full flex flex-col items-center justify-center">
                            <div className="text-4xl font-bold text-gray-900 dark:text-white">—</div>
                            <div className="text-sm text-gray-500 mt-2">{custom?.title || rec.title}</div>
                          </div>
                        ) : rec.chart_type === 'table' ? (
                          <div className="h-full flex items-center justify-center">
                            <TableIcon className="w-16 h-16 text-gray-300" />
                          </div>
                        ) : (
                          <ReactECharts
                            option={{
                              ...chartConfig,
                              title: { show: false },
                              legend: { show: false },
                              grid: { top: 20, right: 20, bottom: 30, left: 50 },
                              color: currentTheme.colors,
                              xAxis: chartConfig.xAxis
                                ? { ...chartConfig.xAxis, data: ['Jan', 'Feb', 'Mar', 'Apr', 'May'] }
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
                                    : [35, 52, 41, 68, 49],
                              })),
                            }}
                            style={{ height: '100%', width: '100%' }}
                            opts={{ renderer: 'canvas' }}
                          />
                        )}
                      </div>

                      {/* Customization Panel */}
                      {isCustomizing && custom && (
                        <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl space-y-4">
                          {/* Title */}
                          <div>
                            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2 block">Title</label>
                            <input
                              type="text"
                              value={custom.title}
                              onChange={(e) => updateCustomization(rec.id, 'title', e.target.value)}
                              className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            />
                          </div>

                          {/* Color Theme */}
                          <div>
                            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2 block">Color Theme</label>
                            <div className="flex gap-2">
                              {colorThemes.map((theme) => (
                                <button
                                  key={theme.id}
                                  onClick={() => updateCustomization(rec.id, 'colorTheme', theme.id)}
                                  className={cn(
                                    "flex-1 p-2 rounded-lg border-2 transition-all",
                                    custom.colorTheme === theme.id
                                      ? "border-primary-500"
                                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300"
                                  )}
                                >
                                  <div className="flex justify-center gap-1 mb-1">
                                    {theme.colors.slice(0, 4).map((color, i) => (
                                      <div key={i} className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                                    ))}
                                  </div>
                                  <div className="text-xs text-gray-600 dark:text-gray-400">{theme.name}</div>
                                </button>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleAddToDashboard(rec)}
                          disabled={creatingChart === rec.id}
                          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl font-medium hover:opacity-90 transition-opacity disabled:opacity-50 shadow-lg shadow-primary-500/20"
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
                          className={cn(
                            "px-4 py-2.5 border-2 rounded-xl font-medium transition-all",
                            isCustomizing
                              ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-600"
                              : "border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-gray-300"
                          )}
                        >
                          {isCustomizing ? <X className="w-4 h-4" /> : <Palette className="w-4 h-4" />}
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
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
            {/* Modal Header */}
            <div className="p-6 border-b border-gray-100 dark:border-gray-800">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">Add to Dashboard</h3>
              <p className="text-gray-500 mt-1">Choose where to add your chart</p>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-4">
              <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{selectedRecommendation.title}</p>
                  <p className="text-sm text-gray-500 capitalize">{selectedRecommendation.chart_type} chart</p>
                </div>
              </div>

              <div className="space-y-3">
                <label className="flex items-center gap-3 p-4 border-2 border-gray-200 dark:border-gray-700 rounded-xl cursor-pointer hover:border-gray-300 transition-colors">
                  <input
                    type="radio"
                    name="dashboard-option"
                    checked={!createNewDashboard}
                    onChange={() => setCreateNewDashboard(false)}
                    className="w-4 h-4 text-primary-500"
                  />
                  <span className="text-gray-700 dark:text-gray-300">Add to existing dashboard</span>
                </label>

                {!createNewDashboard && (
                  <select
                    value={selectedDashboard}
                    onChange={(e) => setSelectedDashboard(e.target.value)}
                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select a dashboard...</option>
                    {dashboards.map((d) => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                )}

                <label className="flex items-center gap-3 p-4 border-2 border-gray-200 dark:border-gray-700 rounded-xl cursor-pointer hover:border-gray-300 transition-colors">
                  <input
                    type="radio"
                    name="dashboard-option"
                    checked={createNewDashboard}
                    onChange={() => setCreateNewDashboard(true)}
                    className="w-4 h-4 text-primary-500"
                  />
                  <span className="text-gray-700 dark:text-gray-300">Create new dashboard</span>
                </label>

                {createNewDashboard && (
                  <input
                    type="text"
                    value={newDashboardName}
                    onChange={(e) => setNewDashboardName(e.target.value)}
                    placeholder="Dashboard name"
                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
                  />
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-100 dark:border-gray-800 flex gap-3">
              <button
                onClick={() => {
                  setShowDashboardModal(false)
                  setSelectedRecommendation(null)
                }}
                className="flex-1 px-4 py-3 border-2 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
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
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
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
