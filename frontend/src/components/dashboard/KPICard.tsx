import { useState, useEffect, useMemo } from 'react'
import {
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  Loader2,
  AlertCircle,
  Target,
  Settings,
  MoreHorizontal
} from 'lucide-react'
import { api } from '../../lib/api'

// Use relative URL to go through Vite proxy in dev
const API_BASE_URL = '/api/v1'

// ============== Types ==============

export interface KPIConfig {
  // Data source
  connectionId: string
  semanticModelId?: string
  transformId?: string
  tableName?: string
  schemaName?: string

  // Measure
  measureColumn: string
  aggregation: 'sum' | 'avg' | 'count' | 'min' | 'max'

  // Time comparison
  dateColumn?: string
  comparisonPeriod?: 'previous_day' | 'previous_week' | 'previous_month' | 'previous_quarter' | 'previous_year'

  // Goal
  goalValue?: number
  goalLabel?: string

  // Display
  title: string
  subtitle?: string
  prefix?: string  // e.g., "$"
  suffix?: string  // e.g., "%"
  decimals?: number
  invertColors?: boolean  // For metrics where down is good (e.g., churn)
}

interface KPIData {
  current_value: number
  formatted_value: string
  previous_value?: number
  change_value?: number
  change_percent?: number
  change_direction?: 'up' | 'down' | 'flat'
  comparison_label?: string
  goal_value?: number
  goal_percent?: number
  goal_status?: 'above' | 'below' | 'at'
  goal_label?: string
  trend_data: { period: string; value: number }[]
  execution_time_ms: number
}

interface KPICardProps {
  config: KPIConfig
  onEdit?: () => void
  onRefresh?: () => void
  className?: string
  showMenu?: boolean
}

// ============== Mini Sparkline Component ==============

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

  // Create area path
  const areaPoints = [
    `${padding},${height - padding}`,
    ...data.map((value, index) => {
      const x = padding + (index / (data.length - 1)) * (width - padding * 2)
      const y = height - padding - ((value - min) / range) * (height - padding * 2)
      return `${x},${y}`
    }),
    `${width - padding},${height - padding}`
  ].join(' ')

  return (
    <svg width={width} height={height} className="overflow-visible">
      {/* Area fill */}
      <polygon
        points={areaPoints}
        fill={color}
        fillOpacity={0.1}
      />
      {/* Line */}
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* End dot */}
      <circle
        cx={width - padding}
        cy={height - padding - ((data[data.length - 1] - min) / range) * (height - padding * 2)}
        r={2}
        fill={color}
      />
    </svg>
  )
}

// ============== Progress Bar Component ==============

function ProgressBar({
  percent,
  status
}: {
  percent: number
  status?: 'above' | 'below' | 'at'
}) {
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
    <div className="w-full">
      <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${getColor()} transition-all duration-500 ease-out rounded-full`}
          style={{ width: `${clampedPercent}%` }}
        />
      </div>
    </div>
  )
}

// ============== Main KPI Card Component ==============

export function KPICard({
  config,
  onEdit,
  onRefresh,
  className = '',
  showMenu = true
}: KPICardProps) {
  const [data, setData] = useState<KPIData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [menuOpen, setMenuOpen] = useState(false)

  // Fetch KPI data
  const fetchData = async () => {
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
        trend_points: 7
      })
      setData(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load KPI')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [config])

  // Determine colors based on change direction
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

  // Format the value
  const formattedValue = useMemo(() => {
    if (!data) return '—'

    const value = data.current_value
    const decimals = config.decimals ?? 0
    const prefix = config.prefix || ''
    const suffix = config.suffix || ''

    // Use formatted_value from backend if no custom formatting
    if (!prefix && !suffix && decimals === 0) {
      return data.formatted_value
    }

    // Custom formatting
    let formatted: string
    if (Math.abs(value) >= 1_000_000) {
      formatted = (value / 1_000_000).toFixed(1) + 'M'
    } else if (Math.abs(value) >= 1_000) {
      formatted = (value / 1_000).toFixed(1) + 'K'
    } else {
      formatted = value.toFixed(decimals)
    }

    return `${prefix}${formatted}${suffix}`
  }, [data, config])

  // Loading state
  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 ${className}`}>
        <div className="flex items-center justify-center h-24">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl p-4 border border-red-200 dark:border-red-800 ${className}`}>
        <div className="flex flex-col items-center justify-center h-24 text-red-500">
          <AlertCircle className="w-6 h-6 mb-2" />
          <span className="text-xs text-center">{error}</span>
          <button
            onClick={fetchData}
            className="mt-2 text-xs text-blue-500 hover:underline flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" /> Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 relative group ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div>
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {config.title}
          </h3>
          {config.subtitle && (
            <p className="text-xs text-gray-400 dark:text-gray-500">{config.subtitle}</p>
          )}
        </div>

        {showMenu && (
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={fetchData}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              title="Refresh"
            >
              <RefreshCw className="w-3 h-3 text-gray-400" />
            </button>
            <div className="relative">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <MoreHorizontal className="w-4 h-4 text-gray-400" />
              </button>
              {menuOpen && (
                <div className="absolute right-0 top-full mt-1 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10 min-w-[100px]">
                  <button
                    onClick={() => {
                      onEdit?.()
                      setMenuOpen(false)
                    }}
                    className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Settings className="w-3 h-3" /> Configure
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Main Value */}
      <div className="flex items-end justify-between">
        <div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {formattedValue}
          </p>

          {/* Change indicator */}
          {data?.change_percent !== undefined && data?.comparison_label && (
            <div className={`flex items-center gap-1 mt-1 ${getChangeColor()}`}>
              {getChangeIcon()}
              <span className="text-sm font-medium">
                {data.change_percent > 0 ? '+' : ''}{data.change_percent}%
              </span>
              <span className="text-xs text-gray-400 dark:text-gray-500 ml-1">
                {data.comparison_label}
              </span>
            </div>
          )}
        </div>

        {/* Sparkline */}
        {data?.trend_data && data.trend_data.length > 1 && (
          <div className="ml-4">
            <Sparkline
              data={data.trend_data.map(d => d.value)}
              color={getSparklineColor()}
            />
          </div>
        )}
      </div>

      {/* Goal Progress */}
      {data?.goal_value !== undefined && data?.goal_percent !== undefined && (
        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Target className="w-3 h-3" />
              {data.goal_label || 'Goal'}
            </span>
            <span className={`font-medium ${
              data.goal_status === 'above' ? 'text-green-500' :
              data.goal_status === 'at' ? 'text-yellow-500' :
              'text-red-500'
            }`}>
              {data.goal_percent.toFixed(0)}% of {
                data.goal_value >= 1000000 ? `$${(data.goal_value / 1000000).toFixed(1)}M` :
                data.goal_value >= 1000 ? `$${(data.goal_value / 1000).toFixed(0)}K` :
                `$${data.goal_value}`
              }
            </span>
          </div>
          <ProgressBar percent={data.goal_percent} status={data.goal_status} />
        </div>
      )}
    </div>
  )
}

// ============== KPI Grid Component ==============

interface KPIGridProps {
  kpis: KPIConfig[]
  columns?: 2 | 3 | 4
  className?: string
}

export function KPIGrid({ kpis, columns = 4, className = '' }: KPIGridProps) {
  const gridCols = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
  }

  return (
    <div className={`grid ${gridCols[columns]} gap-4 ${className}`}>
      {kpis.map((config, index) => (
        <KPICard key={index} config={config} />
      ))}
    </div>
  )
}

// ============== Export Default ==============

export default KPICard
