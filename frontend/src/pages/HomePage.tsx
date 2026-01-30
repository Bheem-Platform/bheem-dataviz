import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  BarChart3,
  Star,
  MessageCircleQuestion,
  Clock,
  ChevronRight,
  Plus,
  Sparkles,
  TrendingUp,
  PieChart,
  LineChart,
  ArrowRight,
  Loader2,
  Wand2,
  Layers,
  Database,
  Table2,
} from 'lucide-react'
import { QuickChartSuggestions } from '@/components/dashboard/QuickChartSuggestions'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface DashboardSummary {
  id: string
  name: string
  description: string | null
  icon: string | null
  is_public: boolean
  is_featured: boolean
  chart_count: number
  created_at: string
  updated_at: string
}

interface SavedChart {
  id: string
  name: string
  description: string | null
  chart_type: string
  is_favorite: boolean
  dashboard_id: string | null
  updated_at: string
  view_count: number
}

interface SuggestedQuestion {
  id: string
  question: string
  description: string | null
  icon: string | null
  chart_type: string
  category: string | null
}

interface TransformRecipe {
  id: string
  name: string
  description: string | null
  connection_id: string
  source_table: string
  source_schema: string
  steps_count: number
  row_count: number | null
  last_executed: string | null
  created_at: string
  updated_at: string
}

interface HomePageData {
  featured_dashboards: DashboardSummary[]
  recent_charts: SavedChart[]
  favorite_charts: SavedChart[]
  suggested_questions: SuggestedQuestion[]
  recent_transforms: TransformRecipe[]
}

const chartTypeIcons: Record<string, typeof BarChart3> = {
  bar: BarChart3,
  line: LineChart,
  pie: PieChart,
  area: TrendingUp,
  donut: PieChart,
}

const defaultDashboardIcons = ['📊', '📈', '📉', '💹', '🎯', '📋']

export function HomePage() {
  const navigate = useNavigate()
  const [data, setData] = useState<HomePageData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchHomeData()
  }, [])

  const fetchHomeData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/api/v1/dashboards/home`)
      if (!response.ok) {
        throw new Error('Failed to fetch home page data')
      }
      const homeData = await response.json()
      setData(homeData)
    } catch (err) {
      console.error('Error fetching home data:', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleQuestionClick = (question: SuggestedQuestion) => {
    // Navigate to chart builder with pre-filled query
    navigate('/charts/new', { state: { question } })
  }

  const ChartIcon = ({ type }: { type: string }) => {
    const Icon = chartTypeIcons[type] || BarChart3
    return <Icon className="w-5 h-5" />
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500 mx-auto mb-3" />
          <p className="text-gray-500 dark:text-gray-400">Loading your workspace...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button
            onClick={fetchHomeData}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const hasData = data && (
    data.featured_dashboards.length > 0 ||
    data.recent_charts.length > 0 ||
    data.favorite_charts.length > 0 ||
    data.suggested_questions.length > 0 ||
    data.recent_transforms?.length > 0
  )

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Welcome back
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Your data analytics workspace
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/charts/new"
            className="flex items-center gap-2 px-4 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <BarChart3 className="w-5 h-5" />
            New Chart
          </Link>
          <Link
            to="/dashboards/new"
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Dashboard
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        {!hasData ? (
          /* Empty State */
          <div className="max-w-3xl mx-auto py-12">
            <div className="text-center mb-12">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center mx-auto mb-6">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                Get started with your first dashboard
              </h2>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                Connect your data sources, create visualizations, and build interactive dashboards.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <Link
                to="/connections"
                className="p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all group"
              >
                <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <LayoutDashboard className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  1. Connect Data
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Add your PostgreSQL, MySQL, or other data sources.
                </p>
              </Link>

              <Link
                to="/charts/new"
                className="p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all group"
              >
                <div className="w-12 h-12 rounded-xl bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <BarChart3 className="w-6 h-6 text-violet-600 dark:text-violet-400" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  2. Create Charts
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Visualize your data with beautiful, interactive charts.
                </p>
              </Link>

              <Link
                to="/dashboards/new"
                className="p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all group"
              >
                <div className="w-12 h-12 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <TrendingUp className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  3. Build Dashboards
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Combine charts into powerful dashboards and share insights.
                </p>
              </Link>
            </div>
          </div>
        ) : (
          /* Dashboard Grid */
          <div className="space-y-8">
            {/* Quick Chart Suggestions */}
            <QuickChartSuggestions />

            {/* Suggested Questions */}
            {data.suggested_questions.length > 0 && (
              <section>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <MessageCircleQuestion className="w-5 h-5 text-primary-500" />
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Ask a question
                    </h2>
                  </div>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.suggested_questions.map((question) => (
                    <button
                      key={question.id}
                      onClick={() => handleQuestionClick(question)}
                      className="p-4 bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-xl border border-primary-100 dark:border-primary-800 text-left hover:shadow-md transition-all group"
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-xl">{question.icon || '💡'}</span>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                            {question.question}
                          </p>
                          {question.description && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                              {question.description}
                            </p>
                          )}
                        </div>
                        <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
                      </div>
                    </button>
                  ))}
                </div>
              </section>
            )}

            {/* Featured Dashboards */}
            {data.featured_dashboards.length > 0 && (
              <section>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <LayoutDashboard className="w-5 h-5 text-primary-500" />
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Featured Dashboards
                    </h2>
                  </div>
                  <Link
                    to="/dashboards"
                    className="flex items-center gap-1 text-sm text-primary-600 dark:text-primary-400 hover:underline"
                  >
                    View all
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.featured_dashboards.map((dashboard, idx) => (
                    <Link
                      key={dashboard.id}
                      to={`/dashboards/${dashboard.id}`}
                      className="p-5 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all group"
                    >
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-100 to-secondary-100 dark:from-primary-900/30 dark:to-secondary-900/30 flex items-center justify-center text-2xl">
                          {dashboard.icon || defaultDashboardIcons[idx % defaultDashboardIcons.length]}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors truncate">
                            {dashboard.name}
                          </h3>
                          {dashboard.description && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                              {dashboard.description}
                            </p>
                          )}
                          <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                            <span className="flex items-center gap-1">
                              <BarChart3 className="w-3 h-3" />
                              {dashboard.chart_count} charts
                            </span>
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Recent Transforms */}
            {data.recent_transforms?.length > 0 && (
              <section>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Wand2 className="w-5 h-5 text-indigo-500" />
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Transform Recipes
                    </h2>
                  </div>
                  <Link
                    to="/transforms"
                    className="flex items-center gap-1 text-sm text-primary-600 dark:text-primary-400 hover:underline"
                  >
                    View all
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.recent_transforms.map((recipe) => (
                    <Link
                      key={recipe.id}
                      to={`/transforms`}
                      className="p-5 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-indigo-300 dark:hover:border-indigo-600 transition-all group"
                    >
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center">
                          <Wand2 className="w-6 h-6 text-indigo-500" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                            {recipe.name}
                          </h3>
                          {recipe.description && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-1">
                              {recipe.description}
                            </p>
                          )}
                          <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                            <span className="flex items-center gap-1">
                              <Table2 className="w-3 h-3" />
                              {recipe.source_table}
                            </span>
                            <span className="flex items-center gap-1 px-1.5 py-0.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded">
                              <Layers className="w-3 h-3" />
                              {recipe.steps_count} steps
                            </span>
                            {recipe.row_count !== null && (
                              <span>{recipe.row_count.toLocaleString()} rows</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Recent Charts */}
            {data.recent_charts.length > 0 && (
              <section>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-primary-500" />
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Recent Charts
                    </h2>
                  </div>
                  <Link
                    to="/gallery"
                    className="flex items-center gap-1 text-sm text-primary-600 dark:text-primary-400 hover:underline"
                  >
                    View all
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {data.recent_charts.map((chart) => (
                    <Link
                      key={chart.id}
                      to={`/charts/${chart.id}`}
                      className="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all group"
                    >
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                          <ChartIcon type={chart.chart_type} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors truncate">
                            {chart.name}
                          </h3>
                          <p className="text-xs text-gray-400 capitalize">
                            {chart.chart_type} chart
                          </p>
                        </div>
                        {chart.is_favorite && (
                          <Star className="w-4 h-4 text-amber-400 fill-amber-400 flex-shrink-0" />
                        )}
                      </div>
                      <div className="text-xs text-gray-400">
                        {chart.view_count} views
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Favorite Charts */}
            {data.favorite_charts.length > 0 && (
              <section>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Star className="w-5 h-5 text-amber-500" />
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Favorites
                    </h2>
                  </div>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {data.favorite_charts.map((chart) => (
                    <Link
                      key={chart.id}
                      to={`/charts/${chart.id}`}
                      className="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all group"
                    >
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-amber-50 dark:bg-amber-900/30 flex items-center justify-center">
                          <ChartIcon type={chart.chart_type} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors truncate">
                            {chart.name}
                          </h3>
                          <p className="text-xs text-gray-400 capitalize">
                            {chart.chart_type} chart
                          </p>
                        </div>
                        <Star className="w-4 h-4 text-amber-400 fill-amber-400 flex-shrink-0" />
                      </div>
                      <div className="text-xs text-gray-400">
                        {chart.view_count} views
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
