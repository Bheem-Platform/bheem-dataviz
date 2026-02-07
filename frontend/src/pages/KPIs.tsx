import { useState, useEffect, useCallback } from 'react'
import {
  Plus,
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  Trash2,
  Edit3,
  Target,
  Loader2,
  AlertCircle,
  MoreHorizontal,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  BarChart3,
  Activity,
  Clock,
  ChevronRight,
  Star,
  Grid3X3,
  List,
  Home,
} from 'lucide-react'
import { KPIBuilder, KPIConfig } from '@/components/dashboard'
import { api } from '../lib/api'
import { cn } from '@/lib/utils'
import { PageHeader, Badge } from '@/components/ui/glass'

interface SavedKPI {
  id: string
  name: string
  description?: string
  connection_id?: string
  semantic_model_id?: string
  transform_id?: string
  config: KPIConfig
  is_favorite: boolean
  created_at: string
  updated_at: string
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

// Sparkline SVG Component
function Sparkline({ data, color, height = 40 }: { data: number[]; color: string; height?: number }) {
  if (!data || data.length < 2) return null

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1

  const width = 120
  const padding = 4

  const points = data.map((value, index) => {
    const x = padding + (index / (data.length - 1)) * (width - padding * 2)
    const y = height - padding - ((value - min) / range) * (height - padding * 2)
    return `${x},${y}`
  }).join(' ')

  const areaPoints = `${padding},${height - padding} ${points} ${width - padding},${height - padding}`

  return (
    <svg width={width} height={height} className="overflow-visible">
      <defs>
        <linearGradient id={`gradient-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon
        points={areaPoints}
        fill={`url(#gradient-${color})`}
      />
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle
        cx={width - padding}
        cy={height - padding - ((data[data.length - 1] - min) / range) * (height - padding * 2)}
        r={3}
        fill={color}
      />
    </svg>
  )
}

// Circular Progress Component
function CircularProgress({ percent, size = 80, strokeWidth = 8, color }: {
  percent: number;
  size?: number;
  strokeWidth?: number;
  color: string;
}) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (Math.min(percent, 100) / 100) * circumference

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-gray-100 dark:text-gray-800"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-lg font-bold text-gray-900 dark:text-white">{Math.round(percent)}%</span>
      </div>
    </div>
  )
}

// Modern KPI Card - Large variant
function KPICardLarge({ kpi, onEdit, onDelete }: {
  kpi: SavedKPI
  onEdit: () => void
  onDelete: () => void
}) {
  const [data, setData] = useState<KPIData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/kpi/calculate', {
        connection_id: kpi.config.connectionId,
        semantic_model_id: kpi.config.semanticModelId,
        transform_id: kpi.config.transformId,
        table_name: kpi.config.tableName,
        schema_name: kpi.config.schemaName || 'public',
        measure_column: kpi.config.measureColumn,
        aggregation: kpi.config.aggregation,
        date_column: kpi.config.dateColumn,
        comparison_period: kpi.config.comparisonPeriod || 'previous_month',
        goal_value: kpi.config.goalValue,
        goal_label: kpi.config.goalLabel,
        include_trend: true,
        trend_points: 7,
      })
      setData(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error loading KPI')
    } finally {
      setLoading(false)
    }
  }, [kpi.config])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const isPositive = data?.change_direction === 'up'
  const isGood = kpi.config.invertColors ? !isPositive : isPositive
  const changeColor = isGood ? '#10b981' : '#ef4444'

  if (loading) {
    return (
      <div className="col-span-2 row-span-2 bento-card bento-card-gradient-1 flex items-center justify-center min-h-[280px]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
            <Loader2 className="w-5 h-5 animate-spin text-white/80" />
          </div>
          <span className="text-sm text-white/60">Loading metrics...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="col-span-2 row-span-2 bento-card bg-gradient-to-br from-red-500/10 to-orange-500/10 border-red-200/50 dark:border-red-800/50 flex items-center justify-center min-h-[280px]">
        <div className="flex flex-col items-center gap-3 text-center px-6">
          <div className="w-12 h-12 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <AlertCircle className="w-6 h-6 text-red-500" />
          </div>
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button onClick={fetchData} className="text-sm text-primary-500 hover:underline">
            Try again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="col-span-2 row-span-2 bento-card bento-card-gradient-1 group min-h-[280px] relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

      {/* Header */}
      <div className="flex items-start justify-between mb-6 relative z-10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-8 h-8 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="text-white/60 text-sm font-medium uppercase tracking-wider">Primary KPI</span>
          </div>
          <h3 className="text-lg font-semibold text-white">{kpi.config.title}</h3>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button onClick={onEdit} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
            <Edit3 className="w-4 h-4 text-white/70" />
          </button>
          <button onClick={onDelete} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
            <Trash2 className="w-4 h-4 text-white/70" />
          </button>
        </div>
      </div>

      {/* Main Value */}
      <div className="relative z-10 mb-6">
        <div className="text-5xl font-bold text-white tracking-tight mb-2">
          {data?.formatted_value || '—'}
        </div>
        {data?.change_percent !== undefined && (
          <div className="flex items-center gap-2">
            <span className={cn(
              "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-semibold",
              isGood
                ? "bg-emerald-400/20 text-emerald-300"
                : "bg-red-400/20 text-red-300"
            )}>
              {isGood ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
              {data.change_percent > 0 ? '+' : ''}{data.change_percent}%
            </span>
            <span className="text-white/50 text-sm">{data.comparison_label}</span>
          </div>
        )}
      </div>

      {/* Sparkline */}
      {data?.trend_data && data.trend_data.length > 1 && (
        <div className="relative z-10 mt-auto">
          <Sparkline
            data={data.trend_data.map(d => d.value)}
            color="rgba(255,255,255,0.8)"
            height={60}
          />
        </div>
      )}

      {/* Goal Progress */}
      {data?.goal_percent !== undefined && (
        <div className="absolute bottom-6 right-6 z-10">
          <CircularProgress
            percent={data.goal_percent}
            size={70}
            strokeWidth={6}
            color="rgba(255,255,255,0.9)"
          />
        </div>
      )}
    </div>
  )
}

// Modern KPI Card - Compact variant
function KPICardCompact({ kpi, onEdit, onDelete }: {
  kpi: SavedKPI
  onEdit: () => void
  onDelete: () => void
}) {
  const [data, setData] = useState<KPIData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/kpi/calculate', {
        connection_id: kpi.config.connectionId,
        semantic_model_id: kpi.config.semanticModelId,
        transform_id: kpi.config.transformId,
        table_name: kpi.config.tableName,
        schema_name: kpi.config.schemaName || 'public',
        measure_column: kpi.config.measureColumn,
        aggregation: kpi.config.aggregation,
        date_column: kpi.config.dateColumn,
        comparison_period: kpi.config.comparisonPeriod || 'previous_month',
        goal_value: kpi.config.goalValue,
        goal_label: kpi.config.goalLabel,
        include_trend: true,
        trend_points: 7,
      })
      setData(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error')
    } finally {
      setLoading(false)
    }
  }, [kpi.config])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const isPositive = data?.change_direction === 'up'
  const isGood = kpi.config.invertColors ? !isPositive : isPositive

  if (loading) {
    return (
      <div className="bento-card flex items-center justify-center min-h-[160px]">
        <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bento-card flex items-center justify-center min-h-[160px] bg-red-50/50 dark:bg-red-950/20 border-red-200 dark:border-red-900">
        <div className="text-center">
          <AlertCircle className="w-5 h-5 text-red-500 mx-auto mb-1" />
          <button onClick={fetchData} className="text-xs text-primary-500 hover:underline">Retry</button>
        </div>
      </div>
    )
  }

  return (
    <div className="bento-card group min-h-[160px] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-800 dark:to-gray-700 flex items-center justify-center">
            <BarChart3 className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          </div>
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400 truncate max-w-[120px]">
            {kpi.config.title}
          </span>
        </div>
        <button
          onClick={onEdit}
          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
        >
          <MoreHorizontal className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      {/* Value */}
      <div className="flex-1 flex flex-col justify-center">
        <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
          {data?.formatted_value || '—'}
        </div>
        {data?.change_percent !== undefined && (
          <div className={cn(
            "inline-flex items-center gap-1 text-sm font-medium",
            isGood ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"
          )}>
            {isGood ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
            {data.change_percent > 0 ? '+' : ''}{data.change_percent}%
          </div>
        )}
      </div>

      {/* Mini Sparkline */}
      {data?.trend_data && data.trend_data.length > 1 && (
        <div className="mt-3 -mx-1">
          <Sparkline
            data={data.trend_data.map(d => d.value)}
            color={isGood ? '#10b981' : '#ef4444'}
            height={30}
          />
        </div>
      )}
    </div>
  )
}

// KPI Card with Goal Progress
function KPICardWithGoal({ kpi, onEdit, onDelete }: {
  kpi: SavedKPI
  onEdit: () => void
  onDelete: () => void
}) {
  const [data, setData] = useState<KPIData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/kpi/calculate', {
        connection_id: kpi.config.connectionId,
        semantic_model_id: kpi.config.semanticModelId,
        transform_id: kpi.config.transformId,
        table_name: kpi.config.tableName,
        schema_name: kpi.config.schemaName || 'public',
        measure_column: kpi.config.measureColumn,
        aggregation: kpi.config.aggregation,
        date_column: kpi.config.dateColumn,
        comparison_period: kpi.config.comparisonPeriod || 'previous_month',
        goal_value: kpi.config.goalValue,
        goal_label: kpi.config.goalLabel,
        include_trend: true,
        trend_points: 7,
      })
      setData(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error')
    } finally {
      setLoading(false)
    }
  }, [kpi.config])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const goalColor = data?.goal_status === 'above' ? '#10b981' : data?.goal_status === 'at' ? '#f59e0b' : '#ef4444'

  if (loading) {
    return (
      <div className="bento-card row-span-2 flex items-center justify-center min-h-[320px]">
        <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bento-card row-span-2 flex items-center justify-center min-h-[320px]">
        <div className="text-center">
          <AlertCircle className="w-6 h-6 text-red-500 mx-auto mb-2" />
          <p className="text-sm text-gray-500">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bento-card row-span-2 group min-h-[320px] flex flex-col">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <span className="text-xs font-semibold text-primary-500 uppercase tracking-wider">Goal Tracker</span>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mt-1">{kpi.config.title}</h3>
        </div>
        <button onClick={onEdit} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg opacity-0 group-hover:opacity-100 transition-all">
          <Edit3 className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      {/* Circular Progress */}
      <div className="flex-1 flex items-center justify-center">
        <div className="relative">
          <CircularProgress
            percent={data?.goal_percent || 0}
            size={140}
            strokeWidth={12}
            color={goalColor}
          />
          <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-center">
            <span className="text-2xl font-bold text-gray-900 dark:text-white block">
              {data?.formatted_value}
            </span>
            <span className="text-xs text-gray-500">
              of {data?.goal_value?.toLocaleString()} {kpi.config.goalLabel || 'goal'}
            </span>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="mt-auto pt-4 border-t border-gray-100 dark:border-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">Status</span>
          <span className={cn(
            "px-2.5 py-1 rounded-full text-xs font-semibold",
            data?.goal_status === 'above' && "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
            data?.goal_status === 'at' && "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
            data?.goal_status === 'below' && "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
          )}>
            {data?.goal_status === 'above' ? 'On Track' : data?.goal_status === 'at' ? 'At Risk' : 'Behind'}
          </span>
        </div>
      </div>
    </div>
  )
}

// Quick Stats Card
function QuickStatsCard({ stats }: { stats: { label: string; value: string; icon: any }[] }) {
  return (
    <div className="bento-card col-span-2 p-0 overflow-hidden">
      <div className="grid grid-cols-3 divide-x divide-gray-100 dark:divide-gray-800">
        {stats.map((stat, i) => (
          <div key={i} className="p-5 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 flex items-center justify-center mx-auto mb-3">
              <stat.icon className="w-5 h-5 text-primary-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</div>
            <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// Main KPIs Page
export function KPIs() {
  const [kpis, setKpis] = useState<SavedKPI[]>([])
  const [showBuilder, setShowBuilder] = useState(false)
  const [editingKpi, setEditingKpi] = useState<SavedKPI | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [viewMode, setViewMode] = useState<'bento' | 'grid'>('bento')

  const loadKpis = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get('/kpi/saved')
      setKpis(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error loading KPIs')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadKpis()
  }, [loadKpis])

  const handleSaveKpi = async (config: KPIConfig) => {
    try {
      if (editingKpi) {
        await api.patch(`/kpi/saved/${editingKpi.id}`, {
          name: config.title,
          config,
          connection_id: config.connectionId,
          semantic_model_id: config.semanticModelId,
          transform_id: config.transformId,
        })
        setEditingKpi(null)
      } else {
        await api.post('/kpi/saved', {
          name: config.title,
          config,
          connection_id: config.connectionId,
          semantic_model_id: config.semanticModelId,
          transform_id: config.transformId,
        })
      }
      setShowBuilder(false)
      loadKpis()
    } catch (err: any) {
      console.error('Error saving KPI:', err)
      alert(err.response?.data?.detail || err.message || 'Failed to save KPI')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this KPI?')) return
    try {
      await api.delete(`/kpi/saved/${id}`)
      loadKpis()
    } catch (err: any) {
      alert(err.response?.data?.detail || err.message || 'Failed to delete KPI')
    }
  }

  const handleEdit = (kpi: SavedKPI) => {
    setEditingKpi(kpi)
    setShowBuilder(true)
  }

  const refreshAll = () => setRefreshKey(prev => prev + 1)

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="text-center">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <p className="text-gray-500">Loading your KPIs...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="text-center max-w-md px-6">
          <div className="w-16 h-16 rounded-2xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Failed to load KPIs</h3>
          <p className="text-gray-500 mb-6">{error}</p>
          <button
            onClick={loadKpis}
            className="px-6 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-medium"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-950">
      {/* Modern Responsive Header */}
      <PageHeader
        variant="hero"
        gradient="violet"
        size="md"
        icon={<Activity className="w-7 h-7" />}
        title="KPI Dashboard"
        subtitle="Track your key performance indicators in real-time"
        breadcrumbs={[
          { label: 'Home', href: '/', icon: <Home className="w-3.5 h-3.5" /> },
          { label: 'KPIs' }
        ]}
        badge={
          kpis.length > 0 ? (
            <Badge variant="success" size="sm">{kpis.length} Active</Badge>
          ) : null
        }
        stats={kpis.length > 0 ? [
          { label: 'KPIs', value: kpis.length, icon: <Activity className="w-4 h-4" />, color: 'violet' },
          { label: 'Favorites', value: kpis.filter(k => k.is_favorite).length, icon: <Star className="w-4 h-4" />, color: 'amber' },
        ] : undefined}
        actions={
          <>
            {/* View Toggle */}
            <div className="flex items-center bg-white dark:bg-gray-800 rounded-xl p-1 border border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setViewMode('bento')}
                className={cn(
                  "p-2 rounded-lg transition-all",
                  viewMode === 'bento'
                    ? "bg-violet-500 text-white shadow-sm"
                    : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                )}
              >
                <Grid3X3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  "p-2 rounded-lg transition-all",
                  viewMode === 'grid'
                    ? "bg-violet-500 text-white shadow-sm"
                    : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                )}
              >
                <List className="w-4 h-4" />
              </button>
            </div>

            <button
              onClick={refreshAll}
              className="flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="hidden sm:inline font-medium">Refresh</span>
            </button>

            <button
              onClick={() => { setEditingKpi(null); setShowBuilder(true); }}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white rounded-xl hover:opacity-90 transition-opacity shadow-lg shadow-violet-500/25 font-medium"
            >
              <Plus className="w-5 h-5" />
              <span className="hidden sm:inline">Add KPI</span>
            </button>
          </>
        }
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">

        {/* Empty State */}
        {kpis.length === 0 ? (
          <div className="bento-card col-span-full py-20">
            <div className="text-center max-w-md mx-auto">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary-100 to-secondary-100 dark:from-primary-900/30 dark:to-secondary-900/30 flex items-center justify-center mx-auto mb-6">
                <Sparkles className="w-10 h-10 text-primary-500" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                Create your first KPI
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-8">
                Start tracking key metrics from your data sources. KPIs help you monitor performance and make data-driven decisions.
              </p>
              <button
                onClick={() => setShowBuilder(true)}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl hover:opacity-90 transition-opacity shadow-lg shadow-primary-500/25 font-medium"
              >
                <Plus className="w-5 h-5" />
                Create KPI
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Bento Grid Layout */}
            {viewMode === 'bento' ? (
              <div className="bento-grid">
                {/* Quick Stats */}
                <QuickStatsCard
                  stats={[
                    { label: 'Total KPIs', value: kpis.length.toString(), icon: BarChart3 },
                    { label: 'On Track', value: '—', icon: Target },
                    { label: 'Last Updated', value: 'Now', icon: Clock },
                  ]}
                />

                {/* Featured KPI - Large */}
                {kpis[0] && (
                  <KPICardLarge
                    key={`${kpis[0].id}-${refreshKey}`}
                    kpi={kpis[0]}
                    onEdit={() => handleEdit(kpis[0])}
                    onDelete={() => handleDelete(kpis[0].id)}
                  />
                )}

                {/* Goal KPI */}
                {kpis[1] && kpis[1].config.goalValue && (
                  <KPICardWithGoal
                    key={`${kpis[1].id}-${refreshKey}`}
                    kpi={kpis[1]}
                    onEdit={() => handleEdit(kpis[1])}
                    onDelete={() => handleDelete(kpis[1].id)}
                  />
                )}

                {/* Compact KPIs */}
                {kpis.slice(kpis[1]?.config.goalValue ? 2 : 1).map(kpi => (
                  <KPICardCompact
                    key={`${kpi.id}-${refreshKey}`}
                    kpi={kpi}
                    onEdit={() => handleEdit(kpi)}
                    onDelete={() => handleDelete(kpi.id)}
                  />
                ))}
              </div>
            ) : (
              /* Standard Grid Layout */
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                {kpis.map(kpi => (
                  <KPICardCompact
                    key={`${kpi.id}-${refreshKey}`}
                    kpi={kpi}
                    onEdit={() => handleEdit(kpi)}
                    onDelete={() => handleDelete(kpi.id)}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* KPI Builder Modal */}
      <KPIBuilder
        isOpen={showBuilder}
        onClose={() => { setShowBuilder(false); setEditingKpi(null); }}
        onSave={handleSaveKpi}
        initialConfig={editingKpi?.config}
      />
    </div>
  )
}
