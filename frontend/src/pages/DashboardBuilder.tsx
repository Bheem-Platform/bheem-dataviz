import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Save,
  Share2,
  Plus,
  Undo,
  Redo,
  Eye,
  Loader2,
  Check,
  AlertCircle,
  ChevronDown,
  BarChart3,
  Gauge,
  GitBranch,
  Wand2,
  Table,
  Type,
  X,
  Search,
  Trash2,
  Database,
  Layers,
  Calculator,
  Columns,
  Clock,
  Table2,
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  Target,
  Download,
} from 'lucide-react'
import { KPIConfig, KPIBuilder } from '@/components/dashboard'
import ReactECharts from 'echarts-for-react'

const API_BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1'

// Widget types
interface Widget {
  id: string
  type: 'chart' | 'kpi' | 'model' | 'transform' | 'table' | 'text'
  title: string
  config: Record<string, unknown>
  kpiConfig?: KPIConfig
  chartId?: string
  semanticModelId?: string
  transformId?: string
  chartData?: SavedChart
  modelData?: SemanticModel
  transformData?: Transform
  x?: number
  y?: number
  w?: number
  h?: number
}

interface DashboardData {
  id: string
  name: string
  description?: string
  layout?: {
    widgets: Widget[]
  }
  is_public?: boolean
  is_featured?: boolean
}

interface SavedChart {
  id: string
  name: string
  description?: string
  chart_type: string
  chart_config: Record<string, unknown>
  created_at: string
  is_favorite?: boolean
}

interface SemanticModel {
  id: string
  name: string
  description?: string
  connection_id?: string
  connection_name?: string
  table_name?: string
  transform_name?: string
  transform_id?: string
  measures_count?: number
  dimensions_count?: number
  joins_count?: number
  created_at: string
}

interface Transform {
  id: string
  name: string
  description?: string
  connection_id?: string
  connection_name?: string
  source_table: string
  source_schema?: string
  steps?: any[]
  row_count?: number
  last_executed?: string
  created_at: string
}

interface KPIData {
  current_value: number
  formatted_value: string
  previous_value?: number
  change_percent?: number
  change_direction?: 'up' | 'down' | 'flat'
  comparison_label?: string
  goal_value?: number
  goal_percent?: number
  goal_status?: 'above' | 'below' | 'at'
  trend_data: { period: string; value: number }[]
  reference_date?: string
  current_period?: string
}

// Mini Sparkline Component
function Sparkline({ data, color = '#667eea' }: { data: number[]; color?: string }) {
  if (!data || data.length < 2) return null

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1

  const width = 80
  const height = 24
  const padding = 2

  const points = data.map((value, index) => {
    const x = padding + (index / (data.length - 1)) * (width - padding * 2)
    const y = height - padding - ((value - min) / range) * (height - padding * 2)
    return `${x},${y}`
  }).join(' ')

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle
        cx={width - padding}
        cy={height - padding - ((data[data.length - 1] - min) / range) * (height - padding * 2)}
        r={2}
        fill={color}
      />
    </svg>
  )
}

// Progress Bar Component
function ProgressBar({ percent, status }: { percent: number; status?: string }) {
  const clampedPercent = Math.min(Math.max(percent, 0), 100)
  const getColor = () => {
    switch (status) {
      case 'above': return 'bg-green-500'
      case 'at': return 'bg-yellow-500'
      case 'below': return 'bg-red-500'
      default: return 'bg-purple-500'
    }
  }

  return (
    <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
      <div
        className={`h-full ${getColor()} transition-all duration-500 ease-out rounded-full`}
        style={{ width: `${clampedPercent}%` }}
      />
    </div>
  )
}

// KPI Widget Card - matches KPIs page design
function KPIWidgetCard({ config, onDelete }: { config: KPIConfig; onDelete: () => void }) {
  const [data, setData] = useState<KPIData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/kpi/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          connection_id: config.connectionId,
          semantic_model_id: config.semanticModelId,
          transform_id: config.transformId,
          table_name: config.tableName,
          schema_name: config.schemaName || 'public',
          measure_column: config.measureColumn,
          aggregation: config.aggregation,
          date_column: config.dateColumn,
          comparison_period: config.comparisonPeriod || 'previous_month',
          goal_value: config.goalValue,
          goal_label: config.goalLabel,
          include_trend: true,
          trend_points: 7,
        }),
      })

      if (!response.ok) throw new Error('Failed to load KPI')
      setData(await response.json())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading KPI')
    } finally {
      setLoading(false)
    }
  }, [config])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const getChangeColor = () => {
    if (!data?.change_direction) return 'text-gray-500'
    const isPositive = data.change_direction === 'up'
    const isGood = config.invertColors ? !isPositive : isPositive
    return isGood ? 'text-green-500' : 'text-red-500'
  }

  const getChangeIcon = () => {
    if (!data?.change_direction) return <Minus className="w-3 h-3" />
    if (data.change_direction === 'up') return <TrendingUp className="w-3 h-3" />
    if (data.change_direction === 'down') return <TrendingDown className="w-3 h-3" />
    return <Minus className="w-3 h-3" />
  }

  const getSparklineColor = () => {
    if (!data?.change_direction) return '#667eea'
    const isPositive = data.change_direction === 'up'
    const isGood = config.invertColors ? !isPositive : isPositive
    return isGood ? '#10b981' : '#ef4444'
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 h-48 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-red-200 dark:border-red-800 h-48 flex flex-col items-center justify-center">
        <AlertCircle className="w-6 h-6 text-red-500 mb-2" />
        <span className="text-sm text-red-500">{error}</span>
        <button onClick={fetchData} className="mt-2 text-xs text-blue-500 hover:underline">Retry</button>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 relative group">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{config.title}</h3>
          {data?.reference_date && (
            <p className="text-xs text-gray-400 dark:text-gray-500">Data as of {data.reference_date}</p>
          )}
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button onClick={fetchData} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded" title="Refresh">
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
          <button onClick={onDelete} className="p-1 hover:bg-red-50 dark:hover:bg-red-900/20 rounded" title="Delete">
            <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-500" />
          </button>
        </div>
      </div>

      {/* Main Value */}
      <div className="flex items-end justify-between mb-4">
        <div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{data?.formatted_value || '—'}</p>
          {data?.change_percent !== undefined && data?.comparison_label && (
            <div className={`flex items-center gap-1 mt-1 ${getChangeColor()}`}>
              {getChangeIcon()}
              <span className="text-sm font-medium">{data.change_percent > 0 ? '+' : ''}{data.change_percent}%</span>
              <span className="text-xs text-gray-400 dark:text-gray-500 ml-1">{data.comparison_label}</span>
            </div>
          )}
        </div>
        {data?.trend_data && data.trend_data.length > 1 && (
          <div className="ml-4">
            <Sparkline data={data.trend_data.map(d => d.value)} color={getSparklineColor()} />
          </div>
        )}
      </div>

      {/* Goal Progress */}
      {data?.goal_value !== undefined && data?.goal_percent !== undefined && (
        <div className="pt-4 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Target className="w-3 h-3" />{config.goalLabel || 'Goal'}
            </span>
            <span className={`font-medium ${data.goal_status === 'above' ? 'text-green-500' : data.goal_status === 'at' ? 'text-yellow-500' : 'text-red-500'}`}>
              {data.goal_percent.toFixed(0)}% of {data.goal_value >= 1000 ? `$${(data.goal_value / 1000).toFixed(0)}K` : `$${data.goal_value.toFixed(0)}`}
            </span>
          </div>
          <ProgressBar percent={data.goal_percent} status={data.goal_status} />
        </div>
      )}

      {/* Period Info */}
      {data?.current_period && (
        <div className="mt-3 text-xs text-gray-400 dark:text-gray-500">{data.current_period}</div>
      )}
    </div>
  )
}

// Chart Widget Card - fetches LIVE data from render endpoint
function ChartWidgetCard({ chart, onDelete }: { chart: SavedChart; onDelete: () => void }) {
  const chartRef = useRef<any>(null)
  const [chartData, setChartData] = useState<{ columns: string[]; rows: any[]; chart_type: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(`${API_BASE_URL}/charts/${chart.id}/render`)
        if (!response.ok) {
          const err = await response.json().catch(() => ({}))
          throw new Error(err.detail || 'Failed to load chart data')
        }
        const data = await response.json()
        setChartData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [chart.id])

  const getChartOption = () => {
    const chartType = chartData?.chart_type?.toLowerCase() || chart.chart_type?.toLowerCase() || 'bar'
    const isPie = chartType === 'pie' || chartType === 'donut'

    if (chartData && chartData.rows && chartData.rows.length > 0) {
      const { columns, rows } = chartData
      const dimensionCol = columns[0]
      const measureCols = columns.slice(1)
      const xAxisData = rows.map(row => row[dimensionCol])

      if (isPie) {
        return {
          tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
          series: [{
            type: 'pie',
            radius: chartType === 'donut' ? ['40%', '70%'] : '65%',
            data: rows.map(row => ({
              name: String(row[dimensionCol]),
              value: row[measureCols[0]] || 0
            })),
            label: { show: true, formatter: '{b}: {d}%' },
          }],
        }
      }

      const isHorizontalBar = chartType === 'horizontal-bar'

      return {
        tooltip: { trigger: 'axis', axisPointer: { type: isHorizontalBar ? 'shadow' : 'line' } },
        grid: { left: isHorizontalBar ? 60 : 40, right: 20, top: 20, bottom: 30, containLabel: false },
        xAxis: isHorizontalBar
          ? { type: 'value', axisLabel: { fontSize: 10 } }
          : { type: 'category', data: xAxisData, axisLabel: { fontSize: 10 } },
        yAxis: isHorizontalBar
          ? { type: 'category', data: xAxisData, axisLabel: { fontSize: 10 } }
          : { type: 'value', axisLabel: { fontSize: 10 } },
        series: measureCols.map(col => ({
          name: col,
          type: chartType === 'line' || chartType === 'area' ? 'line' : 'bar',
          data: rows.map(row => row[col] || 0),
          smooth: chartType === 'line' || chartType === 'area',
          areaStyle: chartType === 'area' ? { opacity: 0.3 } : undefined,
          itemStyle: chartType === 'bar' ? { borderRadius: [4, 4, 0, 0] } : isHorizontalBar ? { borderRadius: [0, 4, 4, 0] } : undefined,
        })),
      }
    }

    return {
      xAxis: { type: 'category', show: false, data: ['A', 'B', 'C', 'D', 'E'] },
      yAxis: { type: 'value', show: false },
      series: [{ type: 'bar', data: [30, 50, 40, 60, 45], itemStyle: { color: '#6366f1' } }],
    }
  }

  const chartType = chart.chart_type
  const isTable = chartType === 'table'
  const isKPI = chartType === 'kpi'

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl border overflow-hidden relative group hover:shadow-xl transition-all h-64 border-gray-200 dark:border-gray-700">
      <div className="absolute inset-0">
        {loading ? (
          <div className="h-full flex items-center justify-center bg-gray-50 dark:bg-gray-800">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : error ? (
          <div className="h-full flex flex-col items-center justify-center bg-red-50 dark:bg-red-900/20 p-4">
            <AlertCircle className="w-8 h-8 text-red-500 mb-2" />
            <p className="text-sm text-red-600 dark:text-red-400 text-center">{error}</p>
          </div>
        ) : isKPI && chartData?.rows?.[0] ? (
          <div className="h-full flex items-center justify-center bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20">
            <div className="text-center px-4">
              <p className="text-4xl font-bold text-gray-900 dark:text-white">
                {(() => {
                  const row = chartData.rows[0]
                  const valueCol = chartData.columns[chartData.columns.length - 1]
                  const value = row[valueCol]
                  if (typeof value === 'number') {
                    return value >= 1000000 ? `${(value / 1000000).toFixed(1)}M`
                      : value >= 1000 ? `${(value / 1000).toFixed(1)}K`
                      : value.toLocaleString()
                  }
                  return value
                })()}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {chartData.columns[chartData.columns.length - 1]}
              </p>
            </div>
          </div>
        ) : isTable && chartData?.rows ? (
          <div className="h-full overflow-hidden bg-white dark:bg-gray-800">
            <table className="w-full text-xs">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  {chartData.columns.slice(0, 5).map((col) => (
                    <th key={col} className="px-2 py-1.5 text-left font-medium text-gray-600 dark:text-gray-300 truncate">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {chartData.rows.slice(0, 8).map((row, i) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-750'}>
                    {chartData.columns.slice(0, 5).map((col) => (
                      <td key={col} className="px-2 py-1 text-gray-700 dark:text-gray-300 truncate max-w-[100px]">
                        {row[col] !== null && row[col] !== undefined ? String(row[col]).slice(0, 20) : '—'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : chartData?.rows && chartData.rows.length > 0 ? (
          <ReactECharts
            ref={chartRef}
            option={{ ...getChartOption(), backgroundColor: 'transparent' }}
            style={{ height: '100%', width: '100%' }}
            opts={{ renderer: 'canvas' }}
          />
        ) : (
          <div className="h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-400">No data available</p>
            </div>
          </div>
        )}
      </div>

      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 via-black/50 to-transparent p-3 pt-8">
        <h3 className="text-sm font-semibold text-white truncate">{chart.name}</h3>
      </div>

      <div className="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(); }}
          className="p-1.5 bg-black/50 hover:bg-red-500 backdrop-blur-sm rounded-lg transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5 text-white" />
        </button>
      </div>
    </div>
  )
}

// Model Widget Card
function ModelWidgetCard({ model, onDelete, onNavigate }: { model: SemanticModel; onDelete: () => void; onNavigate: () => void }) {
  return (
    <div onClick={onNavigate} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 relative group hover:shadow-lg hover:border-orange-300 transition-all cursor-pointer">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 flex items-center justify-center">
          <Layers className="w-5 h-5 text-orange-600 dark:text-orange-400" />
        </div>
        <button onClick={(e) => { e.stopPropagation(); onDelete(); }} className="p-1 hover:bg-red-50 dark:hover:bg-red-900/20 rounded opacity-0 group-hover:opacity-100 transition-opacity">
          <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-500" />
        </button>
      </div>
      <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1 truncate">{model.name}</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">{model.description || 'Semantic Model'}</p>
      <div className="flex items-center gap-3 text-xs">
        <span className="flex items-center gap-1 px-2 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full">
          <Calculator className="w-3 h-3" /> {model.measures_count || 0} measures
        </span>
        <span className="flex items-center gap-1 px-2 py-1 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-full">
          <Columns className="w-3 h-3" /> {model.dimensions_count || 0} dims
        </span>
      </div>
      {model.table_name && (
        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center gap-2 text-xs text-gray-500">
          <Table2 className="w-3 h-3" /> {model.table_name}
        </div>
      )}
    </div>
  )
}

// Transform Widget Card
function TransformWidgetCard({ transform, onDelete, onNavigate }: { transform: Transform; onDelete: () => void; onNavigate: () => void }) {
  return (
    <div onClick={onNavigate} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 relative group hover:shadow-lg hover:border-pink-300 transition-all cursor-pointer">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-pink-100 to-rose-100 dark:from-pink-900/30 dark:to-rose-900/30 flex items-center justify-center">
          <Wand2 className="w-5 h-5 text-pink-600 dark:text-pink-400" />
        </div>
        <button onClick={(e) => { e.stopPropagation(); onDelete(); }} className="p-1 hover:bg-red-50 dark:hover:bg-red-900/20 rounded opacity-0 group-hover:opacity-100 transition-opacity">
          <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-500" />
        </button>
      </div>
      <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1 truncate">{transform.name}</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">{transform.description || 'Transform Recipe'}</p>
      <div className="flex items-center gap-3 text-xs">
        <span className="flex items-center gap-1 px-2 py-1 bg-pink-50 dark:bg-pink-900/30 text-pink-600 dark:text-pink-400 rounded-full">
          <Layers className="w-3 h-3" /> {transform.steps?.length || 0} steps
        </span>
        {transform.row_count !== undefined && transform.row_count !== null && (
          <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
            {transform.row_count.toLocaleString()} rows
          </span>
        )}
      </div>
      <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center gap-2 text-xs text-gray-500">
        <Table2 className="w-3 h-3" /> {transform.source_schema ? `${transform.source_schema}.` : ''}{transform.source_table}
      </div>
    </div>
  )
}

// Widget Card Component
function WidgetCard({ widget, onDelete, onNavigate }: { widget: Widget; onDelete: (id: string) => void; onNavigate: (path: string) => void }) {
  if (widget.type === 'kpi' && widget.kpiConfig) {
    return <KPIWidgetCard config={widget.kpiConfig} onDelete={() => onDelete(widget.id)} />
  }

  if (widget.type === 'chart' && widget.chartData) {
    return (
      <div onClick={() => onNavigate(`/charts/${widget.chartData?.id}`)} className="cursor-pointer">
        <ChartWidgetCard chart={widget.chartData} onDelete={() => onDelete(widget.id)} />
      </div>
    )
  }

  if (widget.type === 'model' && widget.modelData) {
    return (
      <ModelWidgetCard
        model={widget.modelData}
        onDelete={() => onDelete(widget.id)}
        onNavigate={() => onNavigate(`/models/${widget.modelData?.id}`)}
      />
    )
  }

  if (widget.type === 'transform' && widget.transformData) {
    return (
      <TransformWidgetCard
        transform={widget.transformData}
        onDelete={() => onDelete(widget.id)}
        onNavigate={() => onNavigate(`/transforms/${widget.transformData?.id}`)}
      />
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 h-48 flex flex-col items-center justify-center text-gray-400">
      <Type className="w-8 h-8 mb-2" />
      <span className="text-sm">{widget.title}</span>
    </div>
  )
}

export function DashboardBuilder() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [widgets, setWidgets] = useState<Widget[]>([])
  const [isPreview, setIsPreview] = useState(false)
  const [dashboardName, setDashboardName] = useState('')
  const [dashboardId, setDashboardId] = useState<string | null>(id || null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle')

  const [showSidePanel, setShowSidePanel] = useState(false)
  const [sidePanelTab, setSidePanelTab] = useState<'charts' | 'kpis' | 'models' | 'transforms'>('charts')
  const [showKPIBuilder, setShowKPIBuilder] = useState(false)

  const [draggedItem, setDraggedItem] = useState<{ type: string; data: any } | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const [charts, setCharts] = useState<SavedChart[]>([])
  const [kpis, setKpis] = useState<{ id: string; name: string; config: KPIConfig }[]>([])
  const [models, setModels] = useState<SemanticModel[]>([])
  const [transforms, setTransforms] = useState<Transform[]>([])
  const [pickerLoading, setPickerLoading] = useState(false)

  const fetchCharts = async () => {
    setPickerLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/dashboards/charts/all`)
      if (response.ok) setCharts(await response.json())
    } finally {
      setPickerLoading(false)
    }
  }

  const fetchKpis = async () => {
    setPickerLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/kpi/saved`)
      if (response.ok) setKpis(await response.json())
    } finally {
      setPickerLoading(false)
    }
  }

  const fetchModels = async () => {
    setPickerLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/models/`)
      if (response.ok) setModels(await response.json())
    } finally {
      setPickerLoading(false)
    }
  }

  const fetchTransforms = async () => {
    setPickerLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/transforms/`)
      if (response.ok) setTransforms(await response.json())
    } finally {
      setPickerLoading(false)
    }
  }

  const loadDashboard = useCallback(async (dashboardId: string) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/dashboards/${dashboardId}`)
      if (response.ok) {
        const data: DashboardData = await response.json()
        setDashboardName(data.name)
        if (data.layout?.widgets) setWidgets(data.layout.widgets)
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (id) loadDashboard(id)
  }, [id, loadDashboard])

  const saveDashboard = async () => {
    setSaving(true)
    setSaveStatus('idle')
    try {
      const body = { name: dashboardName.trim() || 'Untitled Dashboard', layout: { widgets } }
      const response = dashboardId
        ? await fetch(`${API_BASE_URL}/dashboards/${dashboardId}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
        : await fetch(`${API_BASE_URL}/dashboards/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })

      if (response.ok) {
        const saved = await response.json()
        if (!dashboardId) {
          setDashboardId(saved.id)
          navigate(`/dashboards/${saved.id}`, { replace: true })
        }
        setSaveStatus('success')
        setTimeout(() => setSaveStatus('idle'), 2000)
      } else {
        setSaveStatus('error')
      }
    } catch {
      setSaveStatus('error')
    } finally {
      setSaving(false)
    }
  }

  useEffect(() => {
    if (showSidePanel) {
      if (sidePanelTab === 'charts') fetchCharts()
      else if (sidePanelTab === 'kpis') fetchKpis()
      else if (sidePanelTab === 'models') fetchModels()
      else if (sidePanelTab === 'transforms') fetchTransforms()
    }
  }, [showSidePanel, sidePanelTab])

  const addWidget = (type: Widget['type'], data?: any) => {
    const newWidget: Widget = {
      id: `widget-${Date.now()}`,
      type,
      title: data?.name || `New ${type}`,
      config: {},
      kpiConfig: type === 'kpi' ? data : undefined,
      chartId: data?.chartId,
      chartData: data?.chartData,
      modelData: data?.modelData,
      transformData: data?.transformData,
      w: type === 'kpi' ? 3 : 4,
      h: type === 'kpi' ? 2 : 3,
    }
    setWidgets(prev => [...prev, newWidget])
  }

  const deleteWidget = (id: string) => setWidgets(prev => prev.filter(w => w.id !== id))

  const handleChartSelect = (chart: SavedChart) => addWidget('chart', { name: chart.name, chartId: chart.id, chartData: chart })

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent, type: string, data: any) => {
    setDraggedItem({ type, data })
    e.dataTransfer.effectAllowed = 'copy'
  }

  const handleDragEnd = () => {
    setDraggedItem(null)
    setIsDragOver(false)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
    setIsDragOver(true)
  }

  const handleDragLeave = () => {
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    if (!draggedItem) return

    const { type, data } = draggedItem
    if (type === 'chart') {
      addWidget('chart', { name: data.name, chartId: data.id, chartData: data })
    } else if (type === 'kpi') {
      addWidget('kpi', data.config || data)
    } else if (type === 'model') {
      addWidget('model', { name: data.name, modelData: data })
    } else if (type === 'transform') {
      addWidget('transform', { name: data.name, transformData: data })
    }
    setDraggedItem(null)
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100 dark:bg-gray-900">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gray-100 dark:bg-gray-900">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <input
          type="text"
          placeholder="Untitled Dashboard"
          value={dashboardName}
          onChange={(e) => setDashboardName(e.target.value)}
          className="text-lg font-medium bg-transparent border-none focus:outline-none text-gray-900 dark:text-white"
        />
        <div className="flex items-center gap-2">
          <button onClick={() => setIsPreview(!isPreview)} className={`flex items-center gap-2 px-3 py-2 rounded-lg ${isPreview ? 'bg-primary-100 text-primary-600' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}>
            <Eye className="w-5 h-5" /> Preview
          </button>
          <button onClick={saveDashboard} disabled={saving} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-white ${saveStatus === 'success' ? 'bg-green-500' : saveStatus === 'error' ? 'bg-red-500' : 'bg-primary-500 hover:bg-primary-600'}`}>
            {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : saveStatus === 'success' ? <Check className="w-5 h-5" /> : <Save className="w-5 h-5" />}
            {saving ? 'Saving...' : saveStatus === 'success' ? 'Saved!' : 'Save'}
          </button>
        </div>
      </header>

      {/* Toolbar */}
      {!isPreview && (
        <div className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <span className="text-sm text-gray-500">{widgets.length} widget{widgets.length !== 1 ? 's' : ''}</span>
          <button onClick={() => setShowSidePanel(!showSidePanel)} className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium ${showSidePanel ? 'bg-gray-200 dark:bg-gray-700' : 'bg-primary-500 text-white hover:bg-primary-600'}`}>
            <Plus className="w-5 h-5" /> Add Widget
          </button>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        <div
          className={`flex-1 overflow-auto p-6 transition-colors ${isDragOver ? 'bg-primary-50 dark:bg-primary-900/10' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {widgets.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {widgets.map(widget => (
                <WidgetCard key={widget.id} widget={widget} onDelete={deleteWidget} onNavigate={navigate} />
              ))}
            </div>
          ) : (
            <div className={`flex flex-col items-center justify-center h-full border-2 border-dashed rounded-2xl transition-colors ${isDragOver ? 'border-primary-400 bg-primary-50 dark:bg-primary-900/10' : 'border-gray-300 dark:border-gray-700'}`}>
              <Plus className="w-12 h-12 text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {isDragOver ? 'Drop here to add' : 'Start building your dashboard'}
              </h3>
              <p className="text-gray-500 mb-6">
                {isDragOver ? 'Release to add the widget' : 'Drag widgets from the side panel or click "Add Widget"'}
              </p>
              {!showSidePanel && !isDragOver && (
                <button onClick={() => setShowSidePanel(true)} className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
                  <Plus className="w-5 h-5 inline mr-2" /> Add Your First Widget
                </button>
              )}
            </div>
          )}
        </div>

        {/* Side Panel */}
        {showSidePanel && (
          <div className="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white">Add Widgets</h3>
              <button onClick={() => setShowSidePanel(false)} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="flex border-b border-gray-200 dark:border-gray-700">
              {['charts', 'kpis', 'models', 'transforms'].map(tab => (
                <button key={tab} onClick={() => setSidePanelTab(tab as any)}
                  className={`flex-1 py-3 text-xs font-medium ${sidePanelTab === tab ? 'text-primary-600 border-b-2 border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-700/50'}`}>
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-auto p-3 space-y-2">
              {pickerLoading ? (
                <div className="flex items-center justify-center h-32"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
              ) : (
                <>
                  {sidePanelTab === 'charts' && (
                    charts.length > 0 ? charts.map(chart => (
                      <div
                        key={chart.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, 'chart', chart)}
                        onDragEnd={handleDragEnd}
                        onClick={() => handleChartSelect(chart)}
                        className="w-full p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:border-blue-300 cursor-grab active:cursor-grabbing text-left">
                        <div className="flex items-center gap-2">
                          <BarChart3 className="w-4 h-4 text-blue-500" />
                          <span className="text-sm font-medium text-gray-900 dark:text-white truncate">{chart.name}</span>
                        </div>
                        <span className="text-xs text-gray-500 capitalize">{chart.chart_type}</span>
                      </div>
                    )) : <p className="text-center py-8 text-gray-400 text-sm">No charts yet</p>
                  )}
                  {sidePanelTab === 'kpis' && (
                    <>
                      <button onClick={() => setShowKPIBuilder(true)} className="w-full p-3 bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-200 dark:border-purple-700 text-left mb-2">
                        <div className="flex items-center gap-2">
                          <Plus className="w-4 h-4 text-purple-500" />
                          <span className="font-medium text-sm text-purple-700 dark:text-purple-300">Create New KPI</span>
                        </div>
                      </button>
                      {kpis.length > 0 ? kpis.map(kpi => (
                        <div
                          key={kpi.id}
                          draggable
                          onDragStart={(e) => handleDragStart(e, 'kpi', kpi)}
                          onDragEnd={handleDragEnd}
                          onClick={() => addWidget('kpi', kpi.config)}
                          className="w-full p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:border-purple-300 cursor-grab active:cursor-grabbing text-left">
                          <div className="flex items-center gap-2">
                            <Gauge className="w-4 h-4 text-purple-500" />
                            <span className="text-sm font-medium text-gray-900 dark:text-white truncate">{kpi.name}</span>
                          </div>
                          <span className="text-xs text-gray-500">{kpi.config?.aggregation || 'sum'}</span>
                        </div>
                      )) : <p className="text-center py-4 text-gray-400 text-sm">No saved KPIs yet</p>}
                    </>
                  )}
                  {sidePanelTab === 'models' && (
                    models.length > 0 ? models.map(model => (
                      <div
                        key={model.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, 'model', model)}
                        onDragEnd={handleDragEnd}
                        onClick={() => addWidget('model', { name: model.name, modelData: model })}
                        className="w-full p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:border-orange-300 cursor-grab active:cursor-grabbing text-left">
                        <div className="flex items-center gap-2">
                          <Layers className="w-4 h-4 text-orange-500" />
                          <span className="text-sm font-medium text-gray-900 dark:text-white truncate">{model.name}</span>
                        </div>
                        <span className="text-xs text-gray-500">{model.measures_count || 0} measures, {model.dimensions_count || 0} dims</span>
                      </div>
                    )) : <p className="text-center py-8 text-gray-400 text-sm">No models yet</p>
                  )}
                  {sidePanelTab === 'transforms' && (
                    transforms.length > 0 ? transforms.map(transform => (
                      <div
                        key={transform.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, 'transform', transform)}
                        onDragEnd={handleDragEnd}
                        onClick={() => addWidget('transform', { name: transform.name, transformData: transform })}
                        className="w-full p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:border-pink-300 cursor-grab active:cursor-grabbing text-left">
                        <div className="flex items-center gap-2">
                          <Wand2 className="w-4 h-4 text-pink-500" />
                          <span className="text-sm font-medium text-gray-900 dark:text-white truncate">{transform.name}</span>
                        </div>
                        <span className="text-xs text-gray-500">{transform.source_table} • {transform.steps?.length || 0} steps</span>
                      </div>
                    )) : <p className="text-center py-8 text-gray-400 text-sm">No transforms yet</p>
                  )}
                </>
              )}
            </div>

            {/* Footer hint */}
            <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-500 text-center">Drag items to dashboard or click to add</p>
            </div>
          </div>
        )}
      </div>

      <KPIBuilder isOpen={showKPIBuilder} onClose={() => setShowKPIBuilder(false)} onSave={(config) => { addWidget('kpi', config); setShowKPIBuilder(false) }} />
    </div>
  )
}
