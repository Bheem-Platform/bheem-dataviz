import { useState, useEffect, useCallback } from 'react'
import {
  Plus,
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  Trash2,
  Edit,
  Target,
  Loader2,
  AlertCircle,
  MoreHorizontal,
} from 'lucide-react'
import { KPIBuilder, KPIConfig } from '@/components/dashboard'
import { api } from '../lib/api'

const API_BASE_URL = '/api/v1'

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

// KPI Card Component
function KPICard({
  kpi,
  onEdit,
  onDelete,
  onRefresh,
}: {
  kpi: SavedKPI
  onEdit: () => void
  onDelete: () => void
  onRefresh: () => void
}) {
  const [data, setData] = useState<KPIData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [menuOpen, setMenuOpen] = useState(false)

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

  const getChangeColor = () => {
    if (!data?.change_direction) return 'text-gray-500'
    const isPositive = data.change_direction === 'up'
    const isGood = kpi.config.invertColors ? !isPositive : isPositive
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
    const isGood = kpi.config.invertColors ? !isPositive : isPositive
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
        <button onClick={fetchData} className="mt-2 text-xs text-blue-500 hover:underline">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 relative group">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {kpi.config.title}
          </h3>
          {data?.reference_date && (
            <p className="text-xs text-gray-400 dark:text-gray-500">
              Data as of {data.reference_date}
            </p>
          )}
        </div>

        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={fetchData}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4 text-gray-400" />
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
                  onClick={() => { onEdit(); setMenuOpen(false); }}
                  className="flex items-center gap-2 w-full px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Edit className="w-4 h-4" /> Edit
                </button>
                <button
                  onClick={() => { onDelete(); setMenuOpen(false); }}
                  className="flex items-center gap-2 w-full px-3 py-1.5 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Trash2 className="w-4 h-4" /> Delete
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Value */}
      <div className="flex items-end justify-between mb-4">
        <div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {data?.formatted_value || '—'}
          </p>

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
        <div className="pt-4 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Target className="w-3 h-3" />
              {kpi.config.goalLabel || 'Goal'}
            </span>
            <span className={`font-medium ${
              data.goal_status === 'above' ? 'text-green-500' :
              data.goal_status === 'at' ? 'text-yellow-500' :
              'text-red-500'
            }`}>
              {data.goal_percent.toFixed(0)}% of ${data.goal_value >= 1000 ? `${(data.goal_value / 1000).toFixed(0)}K` : data.goal_value.toFixed(0)}
            </span>
          </div>
          <ProgressBar percent={data.goal_percent} status={data.goal_status} />
        </div>
      )}

      {/* Period Info */}
      {data?.current_period && (
        <div className="mt-3 text-xs text-gray-400 dark:text-gray-500">
          {data.current_period}
        </div>
      )}
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

  // Load saved KPIs from API
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

  // Handle save from builder
  const handleSaveKpi = async (config: KPIConfig) => {
    try {
      if (editingKpi) {
        // Update existing KPI
        await api.patch(`/kpi/saved/${editingKpi.id}`, {
          name: config.title,
          config,
          connection_id: config.connectionId,
          semantic_model_id: config.semanticModelId,
          transform_id: config.transformId,
        })
        setEditingKpi(null)
      } else {
        // Create new KPI
        await api.post('/kpi/saved', {
          name: config.title,
          config,
          connection_id: config.connectionId,
          semantic_model_id: config.semanticModelId,
          transform_id: config.transformId,
        })
      }
      setShowBuilder(false)
      loadKpis() // Reload the list
    } catch (err: any) {
      console.error('Error saving KPI:', err)
      alert(err.response?.data?.detail || err.message || 'Failed to save KPI')
    }
  }

  // Delete KPI
  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this KPI?')) {
      return
    }
    try {
      await api.delete(`/kpi/saved/${id}`)
      loadKpis() // Reload the list
    } catch (err: any) {
      console.error('Error deleting KPI:', err)
      alert(err.response?.data?.detail || err.message || 'Failed to delete KPI')
    }
  }

  // Edit KPI
  const handleEdit = (kpi: SavedKPI) => {
    setEditingKpi(kpi)
    setShowBuilder(true)
  }

  // Refresh all KPIs
  const refreshAll = () => {
    setRefreshKey(prev => prev + 1)
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex flex-col items-center justify-center">
        <AlertCircle className="w-8 h-8 text-red-500 mb-2" />
        <p className="text-red-500">{error}</p>
        <button
          onClick={loadKpis}
          className="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              KPI Dashboard
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Track your key performance indicators
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={refreshAll}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh All
            </button>
            <button
              onClick={() => { setEditingKpi(null); setShowBuilder(true); }}
              className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
            >
              <Plus className="w-5 h-5" />
              Add KPI
            </button>
          </div>
        </div>
      </header>

      {/* KPI Grid */}
      <div className="flex-1 overflow-auto p-6">
        {kpis.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mb-4">
              <TrendingUp className="w-8 h-8 text-purple-500" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No KPIs yet
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-md mb-4">
              Create your first KPI to start tracking key metrics from your data.
            </p>
            <button
              onClick={() => setShowBuilder(true)}
              className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
            >
              <Plus className="w-5 h-5" />
              Create KPI
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {kpis.map(kpi => (
              <KPICard
                key={`${kpi.id}-${refreshKey}`}
                kpi={kpi}
                onEdit={() => handleEdit(kpi)}
                onDelete={() => handleDelete(kpi.id)}
                onRefresh={() => {}}
              />
            ))}
          </div>
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
