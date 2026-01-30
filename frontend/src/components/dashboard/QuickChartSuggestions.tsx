import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactECharts from 'echarts-for-react'
import {
  Sparkles,
  Plus,
  ArrowRight,
  Loader2,
  BarChart3,
  LineChart,
  PieChart,
  TrendingUp,
  Database,
} from 'lucide-react'
import { quickChartsApi } from '@/lib/api'

interface ChartConfig {
  xAxis?: Record<string, unknown>
  yAxis?: Record<string, unknown>
  series?: Record<string, unknown>[]
  [key: string]: unknown
}

interface HomeQuickSuggestion {
  id: string
  title: string
  chart_type: string
  confidence: number
  table_name: string
  connection_id: string
  connection_name: string
  chart_config: ChartConfig
  query_config: Record<string, unknown>
}

const chartTypeIcons: Record<string, typeof BarChart3> = {
  bar: BarChart3,
  'horizontal-bar': BarChart3,
  line: LineChart,
  area: TrendingUp,
  pie: PieChart,
  donut: PieChart,
}

export function QuickChartSuggestions() {
  const navigate = useNavigate()
  const [suggestions, setSuggestions] = useState<HomeQuickSuggestion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSuggestions()
  }, [])

  const fetchSuggestions = async () => {
    try {
      const response = await quickChartsApi.getHomeSuggestions(3)
      setSuggestions(response.data)
    } catch (err) {
      console.error('Failed to fetch quick chart suggestions:', err)
      setError('Failed to load suggestions')
    } finally {
      setLoading(false)
    }
  }

  // Don't render if loading or no suggestions
  if (loading) {
    return (
      <section className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-yellow-500" />
          <h2 className="text-lg font-semibold text-gray-900">Explore Your Data</h2>
        </div>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      </section>
    )
  }

  if (error || suggestions.length === 0) {
    return null // Don't show section if no suggestions
  }

  return (
    <section className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Explore Your Data</h2>
            <p className="text-sm text-gray-500">AI-suggested charts based on your data</p>
          </div>
        </div>
        <button
          onClick={() => navigate('/quick-charts')}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          See All
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {suggestions.map((suggestion) => {
          const IconComponent = chartTypeIcons[suggestion.chart_type] || BarChart3

          return (
            <div
              key={suggestion.id}
              className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-md transition-shadow group"
            >
              {/* Mini Chart Preview */}
              <div className="h-32 p-2 bg-gray-50">
                {suggestion.chart_type === 'kpi' ? (
                  <div className="h-full flex flex-col items-center justify-center">
                    <div className="text-2xl font-bold text-gray-400">--</div>
                    <div className="text-xs text-gray-400">KPI Card</div>
                  </div>
                ) : (
                  <ReactECharts
                    option={{
                      ...suggestion.chart_config,
                      title: { show: false },
                      legend: { show: false },
                      grid: { top: 5, right: 5, bottom: 15, left: 25 },
                      xAxis: suggestion.chart_config.xAxis
                        ? {
                            ...suggestion.chart_config.xAxis,
                            data: ['A', 'B', 'C', 'D'],
                            axisLabel: { fontSize: 9 },
                          }
                        : undefined,
                      yAxis: suggestion.chart_config.yAxis
                        ? {
                            ...suggestion.chart_config.yAxis,
                            axisLabel: { fontSize: 9 },
                          }
                        : undefined,
                      series: suggestion.chart_config.series?.map((s: Record<string, unknown>) => ({
                        ...s,
                        data:
                          suggestion.chart_type === 'pie' || suggestion.chart_type === 'donut'
                            ? [
                                { value: 40, name: 'A' },
                                { value: 30, name: 'B' },
                                { value: 20, name: 'C' },
                                { value: 10, name: 'D' },
                              ]
                            : [40, 65, 45, 80],
                      })),
                    }}
                    style={{ height: '100%', width: '100%' }}
                    opts={{ renderer: 'canvas' }}
                  />
                )}
              </div>

              {/* Info */}
              <div className="p-3">
                <div className="flex items-start gap-2 mb-2">
                  <div className="p-1 bg-blue-100 rounded">
                    <IconComponent className="w-3.5 h-3.5 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900 truncate">{suggestion.title}</h3>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <Database className="w-3 h-3" />
                      {suggestion.table_name}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => navigate('/quick-charts')}
                  className="w-full px-3 py-1.5 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Explore
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

export default QuickChartSuggestions
