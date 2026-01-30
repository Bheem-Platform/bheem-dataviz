import { useState, useEffect } from 'react'
import { GripVertical, Settings, Trash2, Maximize2, MoreHorizontal, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import ReactECharts from 'echarts-for-react'
import { KPICard, KPIConfig } from './KPICard'

// Use relative URL to go through Vite proxy in dev, or direct in production
const API_BASE_URL = '/api/v1'

interface Widget {
  id: string
  type: 'chart' | 'kpi' | 'table' | 'text'
  title: string
  x: number
  y: number
  w: number
  h: number
  config: Record<string, unknown>
  // New: optional saved chart ID for fetching real data
  chartId?: string
  // New: KPI configuration for KPI widgets
  kpiConfig?: KPIConfig
  // Semantic model ID for model-based charts
  semanticModelId?: string
  // Transform ID for transform-based charts
  transformId?: string
}

interface ChartData {
  columns: string[]
  rows: Record<string, any>[]
  total_rows: number
  chart_config: Record<string, any>
  chart_type: string
  sql_generated?: string
  execution_time_ms?: number
}

interface ChartWidgetProps {
  widget: Widget
  isPreview: boolean
  onEdit?: (widget: Widget) => void
  onDelete?: (widgetId: string) => void
}

// Build ECharts option from chart data
const buildChartOption = (data: ChartData, chartType: string) => {
  const { columns, rows } = data

  if (!rows || rows.length === 0) {
    return null
  }

  // Assume first column is dimension (x-axis), rest are measures
  const dimensionCol = columns[0]
  const measureCols = columns.slice(1)

  const xAxisData = rows.map(row => row[dimensionCol])

  const baseOption = {
    tooltip: { trigger: 'axis' as const },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },
    legend: measureCols.length > 1 ? { data: measureCols, top: 0 } : undefined,
  }

  switch (chartType) {
    case 'pie':
    case 'donut':
      return {
        tooltip: { trigger: 'item' as const },
        series: [{
          type: 'pie',
          radius: chartType === 'donut' ? ['40%', '70%'] : '70%',
          data: rows.map(row => ({
            name: row[dimensionCol],
            value: row[measureCols[0]] || 0
          })),
          label: { show: true },
        }],
      }

    case 'line':
      return {
        ...baseOption,
        xAxis: { type: 'category' as const, data: xAxisData },
        yAxis: { type: 'value' as const },
        series: measureCols.map(col => ({
          name: col,
          type: 'line',
          smooth: true,
          data: rows.map(row => row[col] || 0),
        })),
      }

    case 'area':
      return {
        ...baseOption,
        xAxis: { type: 'category' as const, data: xAxisData },
        yAxis: { type: 'value' as const },
        series: measureCols.map(col => ({
          name: col,
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.3 },
          data: rows.map(row => row[col] || 0),
        })),
      }

    case 'bar':
    default:
      return {
        ...baseOption,
        xAxis: { type: 'category' as const, data: xAxisData },
        yAxis: { type: 'value' as const },
        series: measureCols.map(col => ({
          name: col,
          type: 'bar',
          data: rows.map(row => row[col] || 0),
          itemStyle: { borderRadius: [4, 4, 0, 0] },
        })),
      }
  }
}

// Fallback static chart for widgets without chartId
const getStaticChartOption = () => ({
  tooltip: { trigger: 'axis' as const },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true,
  },
  xAxis: {
    type: 'category' as const,
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  },
  yAxis: {
    type: 'value' as const,
  },
  series: [
    {
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'bar',
      itemStyle: { color: '#667eea', borderRadius: [4, 4, 0, 0] },
    },
  ],
})

export function ChartWidget({ widget, isPreview, onEdit, onDelete }: ChartWidgetProps) {
  const [showMenu, setShowMenu] = useState(false)
  const [chartData, setChartData] = useState<ChartData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch data based on widget source
  useEffect(() => {
    if (widget.chartId || widget.semanticModelId || widget.transformId) {
      fetchChartData()
    }
  }, [widget.chartId, widget.semanticModelId, widget.transformId])

  const fetchChartData = async () => {
    setLoading(true)
    setError(null)

    try {
      let response: Response

      if (widget.chartId) {
        // Fetch from saved chart
        response = await fetch(`${API_BASE_URL}/charts/${widget.chartId}/render`)
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.detail || 'Failed to load chart')
        }
        setChartData(await response.json())

      } else if (widget.semanticModelId) {
        // First get the model to find measures and dimensions
        const modelResponse = await fetch(`${API_BASE_URL}/models/${widget.semanticModelId}`)
        if (!modelResponse.ok) {
          throw new Error('Failed to load model')
        }
        const model = await modelResponse.json()

        // Get all measure and dimension IDs
        const measureIds = (model.measures || []).map((m: any) => m.id)
        const dimensionIds = (model.dimensions || []).map((d: any) => d.id)

        if (measureIds.length === 0 && dimensionIds.length === 0) {
          throw new Error('Model has no measures or dimensions')
        }

        // Now call preview with all measures and dimensions
        response = await fetch(`${API_BASE_URL}/models/${widget.semanticModelId}/preview`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            measure_ids: measureIds,
            dimension_ids: dimensionIds,
            limit: 100
          })
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.detail || 'Failed to load model data')
        }

        const data = await response.json()
        const rows = data.rows || []
        const columns = data.columns || (rows.length > 0 ? Object.keys(rows[0]) : [])
        setChartData({
          columns,
          rows,
          total_rows: data.total_rows || rows.length,
          chart_config: {},
          chart_type: 'bar'
        })

      } else if (widget.transformId) {
        // Fetch from transform execute - limit is a query param
        response = await fetch(`${API_BASE_URL}/transforms/${widget.transformId}/execute?limit=100`, {
          method: 'POST',
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.detail || 'Failed to load transform data')
        }

        const data = await response.json()
        // Transform columns array [{name, type}] to string array
        const columns = (data.columns || []).map((c: any) => typeof c === 'string' ? c : c.name)
        const rows = data.data || data.rows || []
        setChartData({
          columns,
          rows,
          total_rows: data.total_rows || rows.length,
          chart_config: {},
          chart_type: 'bar'
        })
      } else {
        return
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const renderContent = () => {
    // Handle loading state
    if (loading) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-gray-500">
          <Loader2 className="w-8 h-8 animate-spin mb-2" />
          <span className="text-sm">Loading chart...</span>
        </div>
      )
    }

    // Handle error state
    if (error) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-red-500 p-4">
          <AlertCircle className="w-8 h-8 mb-2" />
          <span className="text-sm text-center">{error}</span>
          <button
            onClick={fetchChartData}
            className="mt-2 flex items-center gap-1 text-xs text-blue-500 hover:text-blue-600"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </button>
        </div>
      )
    }

    switch (widget.type) {
      case 'chart':
        // Use fetched data if available, otherwise use static
        const chartOption = chartData
          ? buildChartOption(chartData, chartData.chart_type || 'bar')
          : getStaticChartOption()

        if (!chartOption) {
          return (
            <div className="flex items-center justify-center h-full text-gray-400">
              <span className="text-sm">No data available</span>
            </div>
          )
        }

        return (
          <ReactECharts
            option={chartOption}
            style={{ height: '100%', width: '100%' }}
            opts={{ renderer: 'canvas' }}
          />
        )

      case 'kpi':
        // Use KPICard component if kpiConfig is provided
        if (widget.kpiConfig) {
          return (
            <div className="h-full -m-2">
              <KPICard
                config={widget.kpiConfig}
                showMenu={false}
                className="h-full border-0 shadow-none"
              />
            </div>
          )
        }

        // Fallback: Use fetched data for KPI if available
        if (chartData && chartData.rows.length > 0) {
          const row = chartData.rows[0]
          const valueCol = chartData.columns[chartData.columns.length - 1]
          const value = row[valueCol]
          const formattedValue = typeof value === 'number'
            ? value >= 1000000 ? `$${(value / 1000000).toFixed(1)}M`
            : value >= 1000 ? `$${(value / 1000).toFixed(1)}K`
            : `$${value.toFixed(0)}`
            : value

          return (
            <div className="flex flex-col items-center justify-center h-full">
              <span className="text-4xl font-bold text-primary-500">{formattedValue}</span>
              <span className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {valueCol}
              </span>
            </div>
          )
        }

        // Static fallback
        return (
          <div className="flex flex-col items-center justify-center h-full">
            <span className="text-4xl font-bold text-primary-500">$124.5K</span>
            <span className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Total Revenue
            </span>
            <span className="text-xs text-green-500 mt-2">+12.5% vs last month</span>
          </div>
        )

      case 'table':
        // Use fetched data for table if available
        if (chartData && chartData.rows.length > 0) {
          return (
            <div className="overflow-auto h-full">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    {chartData.columns.map(col => (
                      <th key={col} className="text-left p-2 font-medium text-gray-600 dark:text-gray-300">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {chartData.rows.slice(0, 10).map((row, i) => (
                    <tr key={i} className="border-b border-gray-100 dark:border-gray-700/50">
                      {chartData.columns.map(col => (
                        <td key={col} className="p-2 text-gray-900 dark:text-white">
                          {typeof row[col] === 'number' ? row[col].toLocaleString() : row[col]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {chartData.total_rows > 10 && (
                <div className="text-xs text-gray-400 text-center py-2">
                  Showing 10 of {chartData.total_rows} rows
                </div>
              )}
            </div>
          )
        }

        return (
          <div className="overflow-auto h-full">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left p-2 font-medium text-gray-600 dark:text-gray-300">Name</th>
                  <th className="text-right p-2 font-medium text-gray-600 dark:text-gray-300">Value</th>
                  <th className="text-right p-2 font-medium text-gray-600 dark:text-gray-300">Change</th>
                </tr>
              </thead>
              <tbody>
                {['Product A', 'Product B', 'Product C'].map((name, i) => (
                  <tr key={name} className="border-b border-gray-100 dark:border-gray-700/50">
                    <td className="p-2 text-gray-900 dark:text-white">{name}</td>
                    <td className="p-2 text-right text-gray-600 dark:text-gray-300">
                      ${(Math.random() * 1000).toFixed(0)}
                    </td>
                    <td className={`p-2 text-right ${i % 2 === 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {i % 2 === 0 ? '+' : '-'}{(Math.random() * 10).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )

      case 'text':
        return (
          <div className="p-4 h-full">
            <p className="text-gray-700 dark:text-gray-300">
              Add your text content here. You can use this widget for titles,
              descriptions, or any explanatory content in your dashboard.
            </p>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="h-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-2">
          {!isPreview && (
            <div className="widget-drag-handle cursor-move">
              <GripVertical className="w-4 h-4 text-gray-400" />
            </div>
          )}
          <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
            {widget.title}
          </span>
        </div>

        <div className="flex items-center gap-1">
          {/* Refresh button for widgets with data sources */}
          {(widget.chartId || widget.semanticModelId || widget.transformId) && !loading && (
            <button
              onClick={fetchChartData}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              title="Refresh data"
            >
              <RefreshCw className="w-3 h-3 text-gray-400" />
            </button>
          )}

          {!isPreview && (
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <MoreHorizontal className="w-4 h-4 text-gray-400" />
              </button>

              {showMenu && (
                <div className="absolute right-0 top-full mt-1 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10 min-w-[120px]">
                  <button
                    onClick={() => {
                      onEdit?.(widget)
                      setShowMenu(false)
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Settings className="w-4 h-4" />
                    Configure
                  </button>
                  <button
                    onClick={() => setShowMenu(false)}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Maximize2 className="w-4 h-4" />
                    Expand
                  </button>
                  <button
                    onClick={() => {
                      onDelete?.(widget.id)
                      setShowMenu(false)
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-2 overflow-hidden">{renderContent()}</div>
    </div>
  )
}
