import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Save,
  Plus,
  Undo,
  Redo,
  Eye,
  EyeOff,
  Loader2,
  Check,
  AlertCircle,
  ChevronDown,
  BarChart3,
  Gauge,
  Wand2,
  X,
  Trash2,
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
  GripVertical,
  Maximize2,
  ArrowUp,
  ArrowDown,
  Filter,
  SlidersHorizontal,
  MousePointerClick,
  LayoutGrid,
  PanelRightOpen,
  PanelRightClose,
  Sparkles,
  Settings2,
  ChevronRight,
} from 'lucide-react'
import { KPIConfig, KPIBuilder } from '@/components/dashboard'
import ReactECharts from 'echarts-for-react'
import { api } from '../lib/api'
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'
import ReactGridLayoutComponent from 'react-grid-layout'

const ReactGridLayout: any = ReactGridLayoutComponent

// Layout item interface for react-grid-layout
interface LayoutItem {
  i: string
  x: number
  y: number
  w: number
  h: number
  minW?: number
  minH?: number
  maxW?: number
  maxH?: number
  static?: boolean
}

// Widget types
interface Widget {
  id: string
  type: 'chart' | 'kpi' | 'model' | 'transform' | 'table' | 'text' | 'slicer'
  title: string
  config: Record<string, unknown>
  kpiConfig?: KPIConfig
  chartId?: string
  semanticModelId?: string
  transformId?: string
  chartData?: SavedChart
  modelData?: SemanticModel
  transformData?: Transform
  slicerConfig?: SlicerConfig
  x: number
  y: number
  w: number
  h: number
  zIndex?: number
}

interface SlicerConfig {
  column: string
  connectionId?: string
  tableName?: string
  schemaName?: string
  filterType: 'dropdown' | 'list' | 'range' | 'date'
  multiSelect: boolean
  values?: string[]
  selectedValues?: string[]
}

interface CrossFilterState {
  sourceWidgetId: string | null
  filters: Record<string, any>
}

interface HistoryState {
  widgets: Widget[]
  dashboardName: string
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
      case 'above': return 'bg-emerald-500'
      case 'at': return 'bg-amber-500'
      case 'below': return 'bg-rose-500'
      default: return 'bg-gradient-to-r from-violet-500 to-purple-500'
    }
  }

  return (
    <div className="w-full h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
      <div
        className={`h-full ${getColor()} transition-all duration-500 ease-out rounded-full`}
        style={{ width: `${clampedPercent}%` }}
      />
    </div>
  )
}

// Modern KPI Widget Card
function KPIWidgetCard({ config, onDelete }: { config: KPIConfig; onDelete: () => void }) {
  const [data, setData] = useState<KPIData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/kpi/calculate', {
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
      })
      setData(response.data)
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
    return isGood ? 'text-emerald-500' : 'text-rose-500'
  }

  const getChangeIcon = () => {
    if (!data?.change_direction) return <Minus className="w-3 h-3" />
    if (data.change_direction === 'up') return <TrendingUp className="w-3 h-3" />
    if (data.change_direction === 'down') return <TrendingDown className="w-3 h-3" />
    return <Minus className="w-3 h-3" />
  }

  const getSparklineColor = () => {
    if (!data?.change_direction) return '#8b5cf6'
    const isPositive = data.change_direction === 'up'
    const isGood = config.invertColors ? !isPositive : isPositive
    return isGood ? '#10b981' : '#f43f5e'
  }

  if (loading) {
    return (
      <div className="bento-card h-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 rounded-full border-2 border-violet-200 border-t-violet-500 animate-spin" />
          <span className="text-xs text-gray-400">Loading...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bento-card h-full flex flex-col items-center justify-center border-rose-200 dark:border-rose-800/50 bg-rose-50/50 dark:bg-rose-900/10">
        <AlertCircle className="w-6 h-6 text-rose-500 mb-2" />
        <span className="text-sm text-rose-600 dark:text-rose-400 text-center px-2">{error}</span>
        <button onClick={fetchData} className="mt-2 text-xs text-violet-500 hover:underline">Retry</button>
      </div>
    )
  }

  return (
    <div className="bento-card h-full relative group overflow-hidden">
      {/* Actions */}
      <div className="absolute top-3 right-3 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all z-10">
        <button onClick={fetchData} className="p-1.5 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg border border-gray-200/50 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
          <RefreshCw className="w-3.5 h-3.5 text-gray-500" />
        </button>
        <button onClick={onDelete} className="p-1.5 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg border border-gray-200/50 dark:border-gray-700/50 hover:bg-rose-50 dark:hover:bg-rose-900/30 transition-colors">
          <Trash2 className="w-3.5 h-3.5 text-gray-500 hover:text-rose-500" />
        </button>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">{config.title}</h3>
          {data?.reference_date && (
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Updated {data.reference_date}</p>
          )}
        </div>
      </div>

      {/* Main Value */}
      <div className="flex items-end justify-between mb-4">
        <div className="flex-1">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{data?.formatted_value || '—'}</p>
          {data?.change_percent !== undefined && data?.comparison_label && (
            <div className={`flex items-center gap-1 mt-1 ${getChangeColor()}`}>
              {getChangeIcon()}
              <span className="text-sm font-medium">{data.change_percent > 0 ? '+' : ''}{data.change_percent}%</span>
              <span className="text-xs text-gray-400 dark:text-gray-500 ml-1">{data.comparison_label}</span>
            </div>
          )}
        </div>
        {data?.trend_data && data.trend_data.length > 1 && (
          <div className="ml-3 flex-shrink-0">
            <Sparkline data={data.trend_data.map(d => d.value)} color={getSparklineColor()} />
          </div>
        )}
      </div>

      {/* Goal Progress */}
      {data?.goal_value !== undefined && data?.goal_percent !== undefined && (
        <div className="pt-3 border-t border-gray-100 dark:border-gray-800">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Target className="w-3 h-3" />{config.goalLabel || 'Goal'}
            </span>
            <span className={`font-medium ${data.goal_status === 'above' ? 'text-emerald-500' : data.goal_status === 'at' ? 'text-amber-500' : 'text-rose-500'}`}>
              {data.goal_percent.toFixed(0)}%
            </span>
          </div>
          <ProgressBar percent={data.goal_percent} status={data.goal_status} />
        </div>
      )}
    </div>
  )
}

// Modern Chart Widget Card
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
        const response = await api.get(`/charts/${chart.id}/render`)
        setChartData(response.data)
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Failed to load data')
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
      series: [{ type: 'bar', data: [30, 50, 40, 60, 45], itemStyle: { color: '#8b5cf6' } }],
    }
  }

  const chartType = chart.chart_type
  const isTable = chartType === 'table'
  const isKPI = chartType === 'kpi'

  return (
    <div className="bento-card-hover h-full relative group overflow-hidden p-0">
      <div className="absolute inset-0">
        {loading ? (
          <div className="h-full flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100/50 dark:from-gray-800 dark:to-gray-900/50">
            <div className="flex flex-col items-center gap-2">
              <div className="w-8 h-8 rounded-full border-2 border-violet-200 border-t-violet-500 animate-spin" />
            </div>
          </div>
        ) : error ? (
          <div className="h-full flex flex-col items-center justify-center bg-rose-50/50 dark:bg-rose-900/10 p-4">
            <AlertCircle className="w-8 h-8 text-rose-500 mb-2" />
            <p className="text-sm text-rose-600 dark:text-rose-400 text-center">{error}</p>
          </div>
        ) : isKPI && chartData?.rows?.[0] ? (
          <div className="h-full flex items-center justify-center bg-gradient-to-br from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20">
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
          <div className="h-full overflow-hidden bg-white dark:bg-gray-900">
            <table className="w-full text-xs">
              <thead className="bg-gray-50 dark:bg-gray-800/50">
                <tr>
                  {chartData.columns.slice(0, 5).map((col) => (
                    <th key={col} className="px-2 py-1.5 text-left font-medium text-gray-600 dark:text-gray-300 truncate">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {chartData.rows.slice(0, 8).map((row, i) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50/50 dark:bg-gray-800/30'}>
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
          <div className="h-full flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100/50 dark:from-gray-800/50 dark:to-gray-900/50">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
              <p className="text-sm text-gray-400">No data available</p>
            </div>
          </div>
        )}
      </div>

      {/* Title overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 via-black/40 to-transparent p-3 pt-8">
        <h3 className="text-sm font-semibold text-white truncate">{chart.name}</h3>
        <span className="text-xs text-white/70 capitalize">{chart.chart_type}</span>
      </div>

      {/* Actions */}
      <div className="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(); }}
          className="p-1.5 bg-black/40 hover:bg-rose-500 backdrop-blur-sm rounded-lg transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5 text-white" />
        </button>
      </div>
    </div>
  )
}

// Modern Model Widget Card
function ModelWidgetCard({ model, onDelete, onNavigate }: { model: SemanticModel; onDelete: () => void; onNavigate: () => void }) {
  return (
    <div onClick={onNavigate} className="bento-card h-full cursor-pointer group hover:border-amber-300/50 dark:hover:border-amber-500/30 transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
          <Layers className="w-5 h-5 text-white" />
        </div>
        <button onClick={(e) => { e.stopPropagation(); onDelete(); }} className="p-1.5 hover:bg-rose-50 dark:hover:bg-rose-900/30 rounded-lg opacity-0 group-hover:opacity-100 transition-all">
          <Trash2 className="w-4 h-4 text-gray-400 hover:text-rose-500" />
        </button>
      </div>
      <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1 truncate">{model.name}</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">{model.description || 'Semantic Model'}</p>
      <div className="flex items-center gap-2 flex-wrap text-xs">
        <span className="flex items-center gap-1 px-2 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
          <Calculator className="w-3 h-3" /> {model.measures_count || 0}
        </span>
        <span className="flex items-center gap-1 px-2 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-lg">
          <Columns className="w-3 h-3" /> {model.dimensions_count || 0}
        </span>
      </div>
      {model.table_name && (
        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center gap-2 text-xs text-gray-500">
          <Table2 className="w-3 h-3" /> {model.table_name}
        </div>
      )}
    </div>
  )
}

// Modern Transform Widget Card
function TransformWidgetCard({ transform, onDelete, onNavigate }: { transform: Transform; onDelete: () => void; onNavigate: () => void }) {
  return (
    <div onClick={onNavigate} className="bento-card h-full cursor-pointer group hover:border-pink-300/50 dark:hover:border-pink-500/30 transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-400 to-rose-500 flex items-center justify-center shadow-lg shadow-pink-500/20">
          <Wand2 className="w-5 h-5 text-white" />
        </div>
        <button onClick={(e) => { e.stopPropagation(); onDelete(); }} className="p-1.5 hover:bg-rose-50 dark:hover:bg-rose-900/30 rounded-lg opacity-0 group-hover:opacity-100 transition-all">
          <Trash2 className="w-4 h-4 text-gray-400 hover:text-rose-500" />
        </button>
      </div>
      <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1 truncate">{transform.name}</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">{transform.description || 'Transform Recipe'}</p>
      <div className="flex items-center gap-2 flex-wrap text-xs">
        <span className="flex items-center gap-1 px-2 py-1 bg-pink-50 dark:bg-pink-900/30 text-pink-600 dark:text-pink-400 rounded-lg">
          <Layers className="w-3 h-3" /> {transform.steps?.length || 0} steps
        </span>
        {transform.row_count !== undefined && transform.row_count !== null && (
          <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-lg">
            {transform.row_count.toLocaleString()} rows
          </span>
        )}
      </div>
      <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center gap-2 text-xs text-gray-500">
        <Table2 className="w-3 h-3" /> {transform.source_schema ? `${transform.source_schema}.` : ''}{transform.source_table}
      </div>
    </div>
  )
}

// Modern Slicer Widget Card
function SlicerWidgetCard({ config, onDelete, onFilterChange }: {
  config: SlicerConfig
  onDelete: () => void
  onFilterChange?: (column: string, values: any[]) => void
}) {
  const [selectedValues, setSelectedValues] = useState<string[]>(config.selectedValues || [])
  const [options] = useState<string[]>(config.values || ['Option 1', 'Option 2', 'Option 3'])
  const [isOpen, setIsOpen] = useState(false)

  const handleSelect = (value: string) => {
    let newSelected: string[]
    if (config.multiSelect) {
      newSelected = selectedValues.includes(value)
        ? selectedValues.filter(v => v !== value)
        : [...selectedValues, value]
    } else {
      newSelected = selectedValues.includes(value) ? [] : [value]
    }
    setSelectedValues(newSelected)
    onFilterChange?.(config.column, newSelected)
  }

  const clearSelection = () => {
    setSelectedValues([])
    onFilterChange?.(config.column, [])
  }

  return (
    <div className="bento-card h-full relative group overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <SlidersHorizontal className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {config.column || 'Filter'}
          </span>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {selectedValues.length > 0 && (
            <button onClick={clearSelection} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <X className="w-3 h-3 text-gray-400" />
            </button>
          )}
          <button onClick={onDelete} className="p-1 hover:bg-rose-50 dark:hover:bg-rose-900/30 rounded-lg">
            <Trash2 className="w-3 h-3 text-gray-400 hover:text-rose-500" />
          </button>
        </div>
      </div>

      {/* Filter Content */}
      {config.filterType === 'dropdown' ? (
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="w-full px-3 py-2 text-sm text-left bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl flex items-center justify-between hover:border-cyan-300 dark:hover:border-cyan-600 transition-colors"
          >
            <span className="truncate text-gray-700 dark:text-gray-300">
              {selectedValues.length > 0 ? selectedValues.join(', ') : 'Select...'}
            </span>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>
          {isOpen && (
            <div className="absolute z-20 mt-2 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl max-h-40 overflow-auto">
              {options.map(option => (
                <button
                  key={option}
                  onClick={() => handleSelect(option)}
                  className={`w-full px-3 py-2 text-sm text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors ${
                    selectedValues.includes(option) ? 'bg-cyan-50 dark:bg-cyan-900/20 text-cyan-700 dark:text-cyan-400' : 'text-gray-700 dark:text-gray-300'
                  }`}
                >
                  {config.multiSelect && (
                    <div className={`w-4 h-4 border rounded flex items-center justify-center transition-colors ${
                      selectedValues.includes(option) ? 'bg-cyan-500 border-cyan-500' : 'border-gray-300 dark:border-gray-600'
                    }`}>
                      {selectedValues.includes(option) && <Check className="w-3 h-3 text-white" />}
                    </div>
                  )}
                  {option}
                </button>
              ))}
            </div>
          )}
        </div>
      ) : config.filterType === 'list' ? (
        <div className="space-y-1 max-h-32 overflow-auto">
          {options.map(option => (
            <button
              key={option}
              onClick={() => handleSelect(option)}
              className={`w-full px-2 py-1.5 text-sm text-left rounded-lg flex items-center gap-2 transition-colors ${
                selectedValues.includes(option)
                  ? 'bg-cyan-50 dark:bg-cyan-900/20 text-cyan-700 dark:text-cyan-400'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
              }`}
            >
              <div className={`w-4 h-4 border rounded flex items-center justify-center flex-shrink-0 transition-colors ${
                selectedValues.includes(option) ? 'bg-cyan-500 border-cyan-500' : 'border-gray-300 dark:border-gray-600'
              }`}>
                {selectedValues.includes(option) && <Check className="w-3 h-3 text-white" />}
              </div>
              <span className="truncate">{option}</span>
            </button>
          ))}
        </div>
      ) : config.filterType === 'date' ? (
        <div className="flex gap-2">
          <input type="date" className="flex-1 px-2 py-1.5 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg" placeholder="From" />
          <input type="date" className="flex-1 px-2 py-1.5 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg" placeholder="To" />
        </div>
      ) : (
        <div className="px-2">
          <input type="range" className="w-full accent-cyan-500" min="0" max="100" />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0</span>
            <span>100</span>
          </div>
        </div>
      )}

      {/* Selected count */}
      {selectedValues.length > 0 && (
        <div className="mt-2 text-xs text-cyan-600 dark:text-cyan-400 font-medium">
          {selectedValues.length} selected
        </div>
      )}
    </div>
  )
}

// Widget Card Component
function WidgetCard({ widget, onDelete, onNavigate, onCrossFilter }: {
  widget: Widget
  onDelete: (id: string) => void
  onNavigate: (path: string) => void
  onCrossFilter?: (widgetId: string, column: string, value: any) => void
}) {
  if (widget.type === 'kpi' && widget.kpiConfig) {
    return <KPIWidgetCard config={widget.kpiConfig} onDelete={() => onDelete(widget.id)} />
  }

  if (widget.type === 'chart' && widget.chartData) {
    return (
      <div onClick={() => onNavigate(`/charts/${widget.chartData?.id}`)} className="cursor-pointer h-full">
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

  if (widget.type === 'slicer' && widget.slicerConfig) {
    return (
      <SlicerWidgetCard
        config={widget.slicerConfig}
        onDelete={() => onDelete(widget.id)}
        onFilterChange={(column, values) => onCrossFilter?.(widget.id, column, values)}
      />
    )
  }

  return (
    <div className="bento-card h-full flex flex-col items-center justify-center text-gray-400">
      <LayoutGrid className="w-8 h-8 mb-2" />
      <span className="text-sm">{widget.title}</span>
    </div>
  )
}

// Grid configuration
const GRID_COLS = 12
const GRID_ROW_HEIGHT = 80
const GRID_MARGIN: [number, number] = [16, 16]
const MAX_HISTORY = 50

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
  const [containerWidth, setContainerWidth] = useState(1200)
  const containerRef = useRef<HTMLDivElement>(null)

  const [showSidePanel, setShowSidePanel] = useState(false)
  const [sidePanelTab, setSidePanelTab] = useState<'charts' | 'kpis' | 'models' | 'transforms' | 'slicers'>('charts')
  const [showKPIBuilder, setShowKPIBuilder] = useState(false)

  const [draggedItem, setDraggedItem] = useState<{ type: string; data: any } | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const [charts, setCharts] = useState<SavedChart[]>([])
  const [kpis, setKpis] = useState<{ id: string; name: string; config: KPIConfig }[]>([])
  const [models, setModels] = useState<SemanticModel[]>([])
  const [transforms, setTransforms] = useState<Transform[]>([])
  const [pickerLoading, setPickerLoading] = useState(false)

  // Undo/Redo history
  const [history, setHistory] = useState<HistoryState[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const isUndoRedoAction = useRef(false)

  // Cross-filter state
  const [crossFilter, setCrossFilter] = useState<CrossFilterState>({
    sourceWidgetId: null,
    filters: {},
  })

  // Selected widget for z-order operations
  const [selectedWidgetId, setSelectedWidgetId] = useState<string | null>(null)

  // Save state to history
  const saveToHistory = useCallback((newWidgets: Widget[], name: string) => {
    if (isUndoRedoAction.current) {
      isUndoRedoAction.current = false
      return
    }
    setHistory(prev => {
      const newHistory = prev.slice(0, historyIndex + 1)
      newHistory.push({ widgets: JSON.parse(JSON.stringify(newWidgets)), dashboardName: name })
      if (newHistory.length > MAX_HISTORY) {
        newHistory.shift()
        return newHistory
      }
      return newHistory
    })
    setHistoryIndex(prev => Math.min(prev + 1, MAX_HISTORY - 1))
  }, [historyIndex])

  const handleUndo = useCallback(() => {
    if (historyIndex > 0) {
      isUndoRedoAction.current = true
      const prevState = history[historyIndex - 1]
      setWidgets(JSON.parse(JSON.stringify(prevState.widgets)))
      setDashboardName(prevState.dashboardName)
      setHistoryIndex(prev => prev - 1)
    }
  }, [history, historyIndex])

  const handleRedo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      isUndoRedoAction.current = true
      const nextState = history[historyIndex + 1]
      setWidgets(JSON.parse(JSON.stringify(nextState.widgets)))
      setDashboardName(nextState.dashboardName)
      setHistoryIndex(prev => prev + 1)
    }
  }, [history, historyIndex])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault()
        handleUndo()
      } else if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault()
        handleRedo()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleUndo, handleRedo])

  const bringToFront = useCallback((widgetId: string) => {
    setWidgets(prev => {
      const maxZ = Math.max(...prev.map(w => w.zIndex || 0))
      return prev.map(w => w.id === widgetId ? { ...w, zIndex: maxZ + 1 } : w)
    })
  }, [])

  const sendToBack = useCallback((widgetId: string) => {
    setWidgets(prev => {
      const minZ = Math.min(...prev.map(w => w.zIndex || 0))
      return prev.map(w => w.id === widgetId ? { ...w, zIndex: minZ - 1 } : w)
    })
  }, [])

  const handleCrossFilter = useCallback((widgetId: string, filterColumn: string, filterValue: any) => {
    setCrossFilter(prev => {
      if (prev.sourceWidgetId === widgetId && prev.filters[filterColumn] === filterValue) {
        return { sourceWidgetId: null, filters: {} }
      }
      return {
        sourceWidgetId: widgetId,
        filters: { ...prev.filters, [filterColumn]: filterValue },
      }
    })
  }, [])

  const clearCrossFilter = useCallback(() => {
    setCrossFilter({ sourceWidgetId: null, filters: {} })
  }, [])

  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth)
      }
    }
    updateWidth()
    window.addEventListener('resize', updateWidth)
    return () => window.removeEventListener('resize', updateWidth)
  }, [showSidePanel])

  const generateLayout = (): LayoutItem[] => {
    return widgets.map(widget => ({
      i: widget.id,
      x: widget.x,
      y: widget.y,
      w: widget.w,
      h: widget.h,
      minW: 2,
      minH: 2,
    }))
  }

  const handleLayoutChange = (newLayout: any[]) => {
    setWidgets(prev => {
      const updated = prev.map(widget => {
        const layoutItem = newLayout.find((l: LayoutItem) => l.i === widget.id)
        if (layoutItem) {
          return {
            ...widget,
            x: layoutItem.x,
            y: layoutItem.y,
            w: layoutItem.w,
            h: layoutItem.h,
          }
        }
        return widget
      })
      return updated
    })
  }

  const handleDragStop = () => {
    saveToHistory(widgets, dashboardName)
  }

  const handleResizeStop = () => {
    saveToHistory(widgets, dashboardName)
  }

  const fetchCharts = async () => {
    setPickerLoading(true)
    try {
      const response = await api.get('/dashboards/charts/all')
      setCharts(response.data)
    } catch (e) {
      console.error('Failed to fetch charts:', e)
    } finally {
      setPickerLoading(false)
    }
  }

  const fetchKpis = async () => {
    setPickerLoading(true)
    try {
      const response = await api.get('/kpi/saved')
      setKpis(response.data)
    } catch (e) {
      console.error('Failed to fetch KPIs:', e)
    } finally {
      setPickerLoading(false)
    }
  }

  const fetchModels = async () => {
    setPickerLoading(true)
    try {
      const response = await api.get('/models/')
      setModels(response.data)
    } catch (e) {
      console.error('Failed to fetch models:', e)
    } finally {
      setPickerLoading(false)
    }
  }

  const fetchTransforms = async () => {
    setPickerLoading(true)
    try {
      const response = await api.get('/transforms/')
      setTransforms(response.data)
    } catch (e) {
      console.error('Failed to fetch transforms:', e)
    } finally {
      setPickerLoading(false)
    }
  }

  const loadDashboard = useCallback(async (dashboardId: string) => {
    setLoading(true)
    setHistory([])
    setHistoryIndex(-1)
    setCrossFilter({ sourceWidgetId: null, filters: {} })
    setSelectedWidgetId(null)
    isUndoRedoAction.current = false

    try {
      const response = await api.get(`/dashboards/${dashboardId}`)
      const data: DashboardData = response.data
      setDashboardName(data.name)

      if (data.layout?.widgets && data.layout.widgets.length > 0) {
        let currentY = 0
        let currentX = 0
        const normalizedWidgets = data.layout.widgets.map((widget: any, index: number) => {
          const w = widget.w ?? (widget.type === 'kpi' ? 3 : widget.type === 'slicer' ? 3 : 4)
          const h = widget.h ?? (widget.type === 'kpi' ? 2 : widget.type === 'slicer' ? 2 : 3)

          let x = widget.x
          let y = widget.y

          if (x === undefined || y === undefined) {
            if (currentX + w > GRID_COLS) {
              currentX = 0
              currentY += h
            }
            x = currentX
            y = currentY
            currentX += w
          }

          return {
            ...widget,
            x,
            y,
            w,
            h,
            zIndex: widget.zIndex ?? 0,
          }
        })
        setWidgets(normalizedWidgets)
        setHistory([{ widgets: JSON.parse(JSON.stringify(normalizedWidgets)), dashboardName: data.name }])
        setHistoryIndex(0)
      } else {
        setWidgets([])
        setHistory([{ widgets: [], dashboardName: data.name }])
        setHistoryIndex(0)
      }
    } catch (e) {
      console.error('Failed to load dashboard:', e)
      setWidgets([])
      setDashboardName('')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (id) {
      setDashboardId(id)
      loadDashboard(id)
    } else {
      setWidgets([])
      setDashboardName('')
      setDashboardId(null)
      setHistory([])
      setHistoryIndex(-1)
      setCrossFilter({ sourceWidgetId: null, filters: {} })
      setSelectedWidgetId(null)
      isUndoRedoAction.current = false
    }
  }, [id, loadDashboard])

  const saveDashboard = async () => {
    setSaving(true)
    setSaveStatus('idle')
    try {
      const body = { name: dashboardName.trim() || 'Untitled Dashboard', layout: { widgets } }
      const response = dashboardId
        ? await api.patch(`/dashboards/${dashboardId}`, body)
        : await api.post('/dashboards/', body)

      const saved = response.data
      if (!dashboardId) {
        setDashboardId(saved.id)
        navigate(`/dashboards/${saved.id}`, { replace: true })
      }
      setSaveStatus('success')
      setTimeout(() => setSaveStatus('idle'), 2000)
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

  const getNextPosition = useCallback((width: number, height: number): { x: number; y: number } => {
    if (widgets.length === 0) {
      return { x: 0, y: 0 }
    }

    let maxY = 0
    widgets.forEach(w => {
      const bottom = w.y + w.h
      if (bottom > maxY) maxY = bottom
    })

    const lastRowWidgets = widgets.filter(w => w.y + w.h === maxY)
    let lastRowMaxX = 0
    lastRowWidgets.forEach(w => {
      const right = w.x + w.w
      if (right > lastRowMaxX) lastRowMaxX = right
    })

    if (lastRowMaxX + width <= GRID_COLS) {
      const lastRowY = Math.max(0, maxY - Math.max(...lastRowWidgets.map(w => w.h)))
      return { x: lastRowMaxX, y: lastRowY }
    }

    return { x: 0, y: maxY }
  }, [widgets])

  const addWidget = (type: Widget['type'], data?: any) => {
    const defaultWidth = type === 'kpi' ? 3 : type === 'slicer' ? 3 : 4
    const defaultHeight = type === 'kpi' ? 2 : type === 'slicer' ? 2 : 3
    const position = getNextPosition(defaultWidth, defaultHeight)
    const maxZ = widgets.length > 0 ? Math.max(...widgets.map(w => w.zIndex || 0)) : 0

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
      slicerConfig: type === 'slicer' ? data : undefined,
      x: position.x,
      y: position.y,
      w: defaultWidth,
      h: defaultHeight,
      zIndex: maxZ + 1,
    }
    const newWidgets = [...widgets, newWidget]
    setWidgets(newWidgets)
    saveToHistory(newWidgets, dashboardName)
  }

  const deleteWidget = (id: string) => {
    const newWidgets = widgets.filter(w => w.id !== id)
    setWidgets(newWidgets)
    saveToHistory(newWidgets, dashboardName)
    if (selectedWidgetId === id) setSelectedWidgetId(null)
  }

  const handleChartSelect = (chart: SavedChart) => addWidget('chart', { name: chart.name, chartId: chart.id, chartData: chart })

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
    } else if (type === 'slicer') {
      addWidget('slicer', { name: data.name || `${data.filterType} Filter`, ...data })
    }
    setDraggedItem(null)
  }

  // Tab configuration for side panel
  const tabs = [
    { id: 'charts', label: 'Charts', icon: BarChart3, color: 'text-blue-500' },
    { id: 'kpis', label: 'KPIs', icon: Gauge, color: 'text-violet-500' },
    { id: 'slicers', label: 'Filters', icon: Filter, color: 'text-cyan-500' },
    { id: 'models', label: 'Models', icon: Layers, color: 'text-amber-500' },
    { id: 'transforms', label: 'Transforms', icon: Wand2, color: 'text-pink-500' },
  ]

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-violet-500/30">
              <LayoutGrid className="w-8 h-8 text-white" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-white dark:bg-gray-800 flex items-center justify-center shadow-lg">
              <div className="w-4 h-4 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
            </div>
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Loading Dashboard</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Please wait...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800">
      {/* Modern Header */}
      <header className="flex-shrink-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-800/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/25">
              <LayoutGrid className="w-5 h-5 text-white" />
            </div>
            <div>
              <input
                type="text"
                placeholder="Untitled Dashboard"
                value={dashboardName}
                onChange={(e) => setDashboardName(e.target.value)}
                className="text-xl font-bold bg-transparent border-none focus:outline-none focus:ring-0 text-gray-900 dark:text-white placeholder-gray-400 w-64"
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
                <span className="flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  {widgets.length} widget{widgets.length !== 1 ? 's' : ''}
                </span>
                {historyIndex > 0 && (
                  <span className="text-gray-400">
                    • {historyIndex} change{historyIndex !== 1 ? 's' : ''}
                  </span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Undo/Redo */}
            <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <button
                onClick={handleUndo}
                disabled={historyIndex <= 0}
                className="p-1.5 rounded-md hover:bg-white dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                title="Undo (Ctrl+Z)"
              >
                <Undo className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              </button>
              <button
                onClick={handleRedo}
                disabled={historyIndex >= history.length - 1}
                className="p-1.5 rounded-md hover:bg-white dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                title="Redo (Ctrl+Y)"
              >
                <Redo className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              </button>
            </div>

            {/* Preview Toggle */}
            <button
              onClick={() => setIsPreview(!isPreview)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                isPreview
                  ? 'bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 border border-violet-200 dark:border-violet-700'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-transparent hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              {isPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              {isPreview ? 'Exit Preview' : 'Preview'}
            </button>

            {/* Save Button */}
            <button
              onClick={saveDashboard}
              disabled={saving}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                saveStatus === 'success'
                  ? 'bg-emerald-500 text-white'
                  : saveStatus === 'error'
                  ? 'bg-rose-500 text-white'
                  : 'bg-gradient-to-r from-violet-500 to-purple-600 text-white shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30'
              }`}
            >
              {saving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : saveStatus === 'success' ? (
                <Check className="w-4 h-4" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              {saving ? 'Saving...' : saveStatus === 'success' ? 'Saved!' : 'Save'}
            </button>
          </div>
        </div>

        {/* Toolbar Row */}
        {!isPreview && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
            <div className="flex items-center gap-3">
              {/* Z-order controls */}
              {selectedWidgetId && (
                <div className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <span className="text-xs text-gray-500 mr-2">Layer:</span>
                  <button
                    onClick={() => bringToFront(selectedWidgetId)}
                    className="p-1 hover:bg-white dark:hover:bg-gray-700 rounded transition-colors"
                    title="Bring to Front"
                  >
                    <ArrowUp className="w-3.5 h-3.5 text-gray-600 dark:text-gray-400" />
                  </button>
                  <button
                    onClick={() => sendToBack(selectedWidgetId)}
                    className="p-1 hover:bg-white dark:hover:bg-gray-700 rounded transition-colors"
                    title="Send to Back"
                  >
                    <ArrowDown className="w-3.5 h-3.5 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
              )}

              {/* Cross-filter indicator */}
              {crossFilter.sourceWidgetId && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-violet-50 dark:bg-violet-900/30 border border-violet-200 dark:border-violet-700 rounded-lg">
                  <MousePointerClick className="w-3.5 h-3.5 text-violet-500" />
                  <span className="text-xs text-violet-700 dark:text-violet-300 font-medium">Cross-filter active</span>
                  <button
                    onClick={clearCrossFilter}
                    className="text-xs text-violet-500 hover:text-violet-700 dark:hover:text-violet-300 underline"
                  >
                    Clear
                  </button>
                </div>
              )}
            </div>

            {/* Add Widget Button */}
            <button
              onClick={() => setShowSidePanel(!showSidePanel)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                showSidePanel
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                  : 'bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100'
              }`}
            >
              {showSidePanel ? <PanelRightClose className="w-4 h-4" /> : <PanelRightOpen className="w-4 h-4" />}
              {showSidePanel ? 'Hide Panel' : 'Add Widget'}
            </button>
          </div>
        )}
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Canvas */}
        <div
          ref={containerRef}
          className={`flex-1 overflow-auto p-6 transition-colors ${isDragOver ? 'bg-violet-50/50 dark:bg-violet-900/10' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {widgets.length > 0 ? (
            <ReactGridLayout
              className="layout"
              layout={generateLayout() as any}
              cols={GRID_COLS}
              rowHeight={GRID_ROW_HEIGHT}
              width={containerWidth - 48}
              margin={GRID_MARGIN}
              onLayoutChange={handleLayoutChange as any}
              onDragStop={handleDragStop as any}
              onResizeStop={handleResizeStop as any}
              isDraggable={!isPreview}
              isResizable={!isPreview}
              draggableHandle=".widget-drag-handle"
              resizeHandles={['se', 'sw', 'ne', 'nw', 'e', 'w', 's', 'n'] as any}
              compactType="vertical"
              preventCollision={false}
              allowOverlap={true}
            >
              {widgets.map(widget => (
                <div
                  key={widget.id}
                  className={`relative group ${selectedWidgetId === widget.id ? 'ring-2 ring-violet-500 ring-offset-2 dark:ring-offset-gray-900' : ''}`}
                  style={{ zIndex: widget.zIndex || 0 }}
                  onClick={() => !isPreview && setSelectedWidgetId(widget.id)}
                >
                  {/* Drag Handle */}
                  {!isPreview && (
                    <div className="widget-drag-handle absolute top-0 left-0 right-0 h-8 bg-gradient-to-b from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity cursor-move z-10 flex items-center justify-center rounded-t-xl">
                      <GripVertical className="w-4 h-4 text-white drop-shadow-md" />
                    </div>
                  )}
                  {/* Resize indicator */}
                  {!isPreview && (
                    <div className="absolute bottom-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                      <Maximize2 className="w-3 h-3 text-gray-400" />
                    </div>
                  )}
                  <div className="h-full">
                    <WidgetCard
                      widget={widget}
                      onDelete={deleteWidget}
                      onNavigate={navigate}
                      onCrossFilter={handleCrossFilter}
                    />
                  </div>
                </div>
              ))}
            </ReactGridLayout>
          ) : (
            /* Empty State */
            <div
              className={`h-full flex flex-col items-center justify-center rounded-2xl border-2 border-dashed transition-all ${
                isDragOver
                  ? 'border-violet-400 bg-violet-50/50 dark:bg-violet-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
            >
              <div className={`w-20 h-20 rounded-2xl flex items-center justify-center mb-6 transition-all ${
                isDragOver
                  ? 'bg-gradient-to-br from-violet-500 to-purple-600 shadow-2xl shadow-violet-500/30'
                  : 'bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700'
              }`}>
                {isDragOver ? (
                  <Plus className="w-10 h-10 text-white" />
                ) : (
                  <LayoutGrid className="w-10 h-10 text-gray-400 dark:text-gray-500" />
                )}
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {isDragOver ? 'Drop to add widget' : 'Start building your dashboard'}
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-6 text-center max-w-md">
                {isDragOver ? 'Release to add the widget to your dashboard' : 'Drag widgets from the side panel or click "Add Widget" to get started'}
              </p>
              {!showSidePanel && !isDragOver && (
                <button
                  onClick={() => setShowSidePanel(true)}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all"
                >
                  <Plus className="w-5 h-5" /> Add Your First Widget
                </button>
              )}
            </div>
          )}
        </div>

        {/* Modern Side Panel */}
        {showSidePanel && (
          <div className="w-80 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 flex flex-col">
            {/* Panel Header */}
            <div className="flex items-center justify-between px-4 py-4 border-b border-gray-100 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                  <Plus className="w-4 h-4 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Add Widgets</h3>
              </div>
              <button onClick={() => setShowSidePanel(false)} className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Tabs */}
            <div className="flex flex-wrap gap-1 p-2 border-b border-gray-100 dark:border-gray-800">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setSidePanelTab(tab.id as any)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    sidePanelTab === tab.id
                      ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <tab.icon className={`w-3.5 h-3.5 ${sidePanelTab === tab.id ? '' : tab.color}`} />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto p-3 space-y-2">
              {pickerLoading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="w-6 h-6 rounded-full border-2 border-violet-200 border-t-violet-500 animate-spin" />
                </div>
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
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 cursor-grab active:cursor-grabbing transition-colors group"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                              <BarChart3 className="w-4 h-4 text-blue-500" />
                            </div>
                            <div>
                              <span className="text-sm font-medium text-gray-900 dark:text-white block truncate max-w-[180px]">{chart.name}</span>
                              <span className="text-xs text-gray-500 capitalize">{chart.chart_type}</span>
                            </div>
                          </div>
                          <ChevronRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-8">
                        <BarChart3 className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
                        <p className="text-sm text-gray-400">No charts yet</p>
                      </div>
                    )
                  )}

                  {sidePanelTab === 'kpis' && (
                    <>
                      <button
                        onClick={() => setShowKPIBuilder(true)}
                        className="w-full p-3 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 rounded-xl border border-violet-200 dark:border-violet-700 hover:border-violet-300 dark:hover:border-violet-600 transition-colors text-left"
                      >
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                            <Plus className="w-4 h-4 text-white" />
                          </div>
                          <div>
                            <span className="font-medium text-sm text-violet-700 dark:text-violet-300">Create New KPI</span>
                            <p className="text-xs text-violet-500 dark:text-violet-400">Build a custom metric</p>
                          </div>
                        </div>
                      </button>
                      {kpis.length > 0 ? kpis.map(kpi => (
                        <div
                          key={kpi.id}
                          draggable
                          onDragStart={(e) => handleDragStart(e, 'kpi', kpi)}
                          onDragEnd={handleDragEnd}
                          onClick={() => addWidget('kpi', kpi.config)}
                          className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-violet-300 dark:hover:border-violet-600 cursor-grab active:cursor-grabbing transition-colors group"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="w-8 h-8 rounded-lg bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center">
                                <Gauge className="w-4 h-4 text-violet-500" />
                              </div>
                              <div>
                                <span className="text-sm font-medium text-gray-900 dark:text-white block truncate max-w-[180px]">{kpi.name}</span>
                                <span className="text-xs text-gray-500 capitalize">{kpi.config?.aggregation || 'sum'}</span>
                              </div>
                            </div>
                            <ChevronRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                        </div>
                      )) : (
                        <div className="text-center py-4">
                          <p className="text-sm text-gray-400">No saved KPIs yet</p>
                        </div>
                      )}
                    </>
                  )}

                  {sidePanelTab === 'slicers' && (
                    <div className="space-y-2">
                      <p className="text-xs text-gray-500 mb-3 px-1">Add interactive filters to your dashboard</p>

                      {/* Dropdown Slicer */}
                      <div
                        draggable
                        onDragStart={(e) => handleDragStart(e, 'slicer', { filterType: 'dropdown', multiSelect: true })}
                        onDragEnd={handleDragEnd}
                        onClick={() => addWidget('slicer', { name: 'Dropdown Filter', filterType: 'dropdown', multiSelect: true, column: '' })}
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-cyan-300 dark:hover:border-cyan-600 cursor-grab active:cursor-grabbing transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-lg bg-cyan-100 dark:bg-cyan-900/30 flex items-center justify-center">
                            <SlidersHorizontal className="w-4 h-4 text-cyan-500" />
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">Dropdown Filter</span>
                            <p className="text-xs text-gray-500">Select from a dropdown list</p>
                          </div>
                        </div>
                      </div>

                      {/* List Slicer */}
                      <div
                        draggable
                        onDragStart={(e) => handleDragStart(e, 'slicer', { filterType: 'list', multiSelect: true })}
                        onDragEnd={handleDragEnd}
                        onClick={() => addWidget('slicer', { name: 'List Filter', filterType: 'list', multiSelect: true, column: '' })}
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-cyan-300 dark:hover:border-cyan-600 cursor-grab active:cursor-grabbing transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-lg bg-cyan-100 dark:bg-cyan-900/30 flex items-center justify-center">
                            <Filter className="w-4 h-4 text-cyan-500" />
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">List Filter</span>
                            <p className="text-xs text-gray-500">Visual list with checkboxes</p>
                          </div>
                        </div>
                      </div>

                      {/* Range Slicer */}
                      <div
                        draggable
                        onDragStart={(e) => handleDragStart(e, 'slicer', { filterType: 'range', multiSelect: false })}
                        onDragEnd={handleDragEnd}
                        onClick={() => addWidget('slicer', { name: 'Range Filter', filterType: 'range', multiSelect: false, column: '' })}
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-cyan-300 dark:hover:border-cyan-600 cursor-grab active:cursor-grabbing transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-lg bg-cyan-100 dark:bg-cyan-900/30 flex items-center justify-center">
                            <SlidersHorizontal className="w-4 h-4 text-cyan-500" />
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">Range Slider</span>
                            <p className="text-xs text-gray-500">Numeric range selection</p>
                          </div>
                        </div>
                      </div>

                      {/* Date Slicer */}
                      <div
                        draggable
                        onDragStart={(e) => handleDragStart(e, 'slicer', { filterType: 'date', multiSelect: false })}
                        onDragEnd={handleDragEnd}
                        onClick={() => addWidget('slicer', { name: 'Date Filter', filterType: 'date', multiSelect: false, column: '' })}
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-cyan-300 dark:hover:border-cyan-600 cursor-grab active:cursor-grabbing transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-lg bg-cyan-100 dark:bg-cyan-900/30 flex items-center justify-center">
                            <Clock className="w-4 h-4 text-cyan-500" />
                          </div>
                          <div>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">Date Filter</span>
                            <p className="text-xs text-gray-500">Date range picker</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {sidePanelTab === 'models' && (
                    models.length > 0 ? models.map(model => (
                      <div
                        key={model.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, 'model', model)}
                        onDragEnd={handleDragEnd}
                        onClick={() => addWidget('model', { name: model.name, modelData: model })}
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-amber-300 dark:hover:border-amber-600 cursor-grab active:cursor-grabbing transition-colors group"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                              <Layers className="w-4 h-4 text-amber-500" />
                            </div>
                            <div>
                              <span className="text-sm font-medium text-gray-900 dark:text-white block truncate max-w-[180px]">{model.name}</span>
                              <span className="text-xs text-gray-500">{model.measures_count || 0} measures, {model.dimensions_count || 0} dims</span>
                            </div>
                          </div>
                          <ChevronRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-8">
                        <Layers className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
                        <p className="text-sm text-gray-400">No models yet</p>
                      </div>
                    )
                  )}

                  {sidePanelTab === 'transforms' && (
                    transforms.length > 0 ? transforms.map(transform => (
                      <div
                        key={transform.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, 'transform', transform)}
                        onDragEnd={handleDragEnd}
                        onClick={() => addWidget('transform', { name: transform.name, transformData: transform })}
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-pink-300 dark:hover:border-pink-600 cursor-grab active:cursor-grabbing transition-colors group"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center">
                              <Wand2 className="w-4 h-4 text-pink-500" />
                            </div>
                            <div>
                              <span className="text-sm font-medium text-gray-900 dark:text-white block truncate max-w-[180px]">{transform.name}</span>
                              <span className="text-xs text-gray-500">{transform.source_table} • {transform.steps?.length || 0} steps</span>
                            </div>
                          </div>
                          <ChevronRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-8">
                        <Wand2 className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
                        <p className="text-sm text-gray-400">No transforms yet</p>
                      </div>
                    )
                  )}
                </>
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-100 dark:border-gray-800">
              <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                Drag items to the canvas or click to add
              </p>
            </div>
          </div>
        )}
      </div>

      {/* KPI Builder Modal */}
      <KPIBuilder
        isOpen={showKPIBuilder}
        onClose={() => setShowKPIBuilder(false)}
        onSave={(config) => {
          addWidget('kpi', config)
          setShowKPIBuilder(false)
        }}
      />
    </div>
  )
}
