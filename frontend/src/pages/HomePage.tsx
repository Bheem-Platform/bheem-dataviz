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
  Table2,
  Zap,
  Eye,
  Database,
  Activity,
  Boxes,
  ArrowUpRight,
  Play,
  Bookmark,
  Grid3X3,
  Target,
  Lightbulb,
} from 'lucide-react'
import { QuickChartSuggestions } from '@/components/dashboard/QuickChartSuggestions'
import { api } from '../lib/api'

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

// Mini Chart Preview Components
const MiniBarChart = ({ color = '#8b5cf6' }: { color?: string }) => (
  <svg viewBox="0 0 40 24" className="w-full h-full">
    <rect x="2" y="14" width="5" height="8" fill={color} opacity="0.5" rx="1" />
    <rect x="9" y="10" width="5" height="12" fill={color} opacity="0.7" rx="1" />
    <rect x="16" y="6" width="5" height="16" fill={color} opacity="0.9" rx="1" />
    <rect x="23" y="12" width="5" height="10" fill={color} opacity="0.6" rx="1" />
    <rect x="30" y="4" width="5" height="18" fill={color} rx="1" />
  </svg>
)

const MiniLineChart = ({ color = '#06b6d4' }: { color?: string }) => (
  <svg viewBox="0 0 40 24" className="w-full h-full">
    <defs>
      <linearGradient id={`lineGrad-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor={color} stopOpacity="0.3" />
        <stop offset="100%" stopColor={color} stopOpacity="0" />
      </linearGradient>
    </defs>
    <path d="M2 20 L10 14 L18 16 L26 8 L34 12 L38 6" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" />
    <path d="M2 20 L10 14 L18 16 L26 8 L34 12 L38 6 L38 24 L2 24 Z" fill={`url(#lineGrad-${color})`} />
  </svg>
)

const MiniPieChart = ({ color = '#f59e0b' }: { color?: string }) => (
  <svg viewBox="0 0 24 24" className="w-full h-full">
    <circle cx="12" cy="12" r="10" fill={color} opacity="0.2" />
    <path d="M12 2 A10 10 0 0 1 22 12 L12 12 Z" fill={color} opacity="0.9" />
    <path d="M22 12 A10 10 0 0 1 12 22 L12 12 Z" fill={color} opacity="0.6" />
  </svg>
)

const MiniAreaChart = ({ color = '#10b981' }: { color?: string }) => (
  <svg viewBox="0 0 40 24" className="w-full h-full">
    <defs>
      <linearGradient id={`areaGrad-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor={color} stopOpacity="0.4" />
        <stop offset="100%" stopColor={color} stopOpacity="0.05" />
      </linearGradient>
    </defs>
    <path d="M0 22 L8 16 L16 18 L24 10 L32 14 L40 8 L40 24 L0 24 Z" fill={`url(#areaGrad-${color})`} />
    <path d="M0 22 L8 16 L16 18 L24 10 L32 14 L40 8" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" />
  </svg>
)

const chartTypeConfig: Record<string, { icon: typeof BarChart3; color: string; MiniChart: typeof MiniBarChart }> = {
  bar: { icon: BarChart3, color: '#8b5cf6', MiniChart: MiniBarChart },
  line: { icon: LineChart, color: '#06b6d4', MiniChart: MiniLineChart },
  pie: { icon: PieChart, color: '#f59e0b', MiniChart: MiniPieChart },
  area: { icon: TrendingUp, color: '#10b981', MiniChart: MiniAreaChart },
  donut: { icon: PieChart, color: '#ec4899', MiniChart: MiniPieChart },
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
      const response = await api.get('/dashboards/home')
      setData(response.data)
    } catch (err) {
      console.error('Error fetching home data:', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleQuestionClick = (question: SuggestedQuestion) => {
    navigate('/charts/new', { state: { question } })
  }

  // Stats calculation
  const stats = {
    dashboards: data?.featured_dashboards?.length || 0,
    charts: (data?.recent_charts?.length || 0) + (data?.favorite_charts?.length || 0),
    transforms: data?.recent_transforms?.length || 0,
    favorites: data?.favorite_charts?.length || 0,
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-violet-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-violet-950/20">
        <div className="text-center">
          <div className="relative mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-violet-500/25 mx-auto">
              <Loader2 className="w-8 h-8 text-white animate-spin" />
            </div>
            <div className="absolute inset-0 bg-gradient-to-br from-violet-500 to-fuchsia-500 rounded-2xl blur-xl opacity-30 animate-pulse" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">Loading workspace</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Preparing your analytics dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-red-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-red-950/20">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-red-500 to-rose-500 flex items-center justify-center shadow-lg shadow-red-500/25 mx-auto mb-6">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Connection Error</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">{error}</p>
          <button
            onClick={fetchHomeData}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-violet-500/25 transition-all"
          >
            <Play className="w-4 h-4" />
            Retry Connection
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
    <div className="h-full overflow-auto bg-gradient-to-br from-gray-50 via-white to-violet-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-violet-950/20">
      {/* Hero Header */}
      <div className="relative overflow-hidden">
        {/* Background Decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-24 -right-24 w-96 h-96 bg-gradient-to-br from-violet-400/20 to-fuchsia-400/20 rounded-full blur-3xl" />
          <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-gradient-to-br from-cyan-400/20 to-blue-400/20 rounded-full blur-3xl" />
        </div>

        <div className="relative px-6 py-8 sm:px-8 lg:px-12">
          <div className="max-w-7xl mx-auto">
            {/* Header Content */}
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
              <div className="flex items-center gap-5">
                <div className="relative">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 via-fuchsia-500 to-pink-500 flex items-center justify-center shadow-xl shadow-violet-500/30">
                    <Sparkles className="w-8 h-8 text-white" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-400 flex items-center justify-center shadow-lg">
                    <Zap className="w-3.5 h-3.5 text-white" />
                  </div>
                </div>
                <div>
                  <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">
                    Welcome back
                  </h1>
                  <p className="text-gray-500 dark:text-gray-400 mt-1">
                    Your data analytics workspace is ready
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3">
                <Link
                  to="/charts/new"
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium hover:border-violet-300 dark:hover:border-violet-600 hover:shadow-lg transition-all"
                >
                  <BarChart3 className="w-4 h-4" />
                  New Chart
                </Link>
                <Link
                  to="/dashboards/new"
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-violet-500/25 hover:-translate-y-0.5 transition-all"
                >
                  <Plus className="w-4 h-4" />
                  New Dashboard
                </Link>
              </div>
            </div>

            {/* Stats Grid */}
            {hasData && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8">
                <div className="group relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-4 border border-white/20 dark:border-gray-700/50 hover:shadow-lg hover:shadow-violet-500/10 transition-all">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.dashboards}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Dashboards</p>
                    </div>
                    <div className="w-10 h-10 rounded-xl bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <LayoutDashboard className="w-5 h-5 text-violet-600 dark:text-violet-400" />
                    </div>
                  </div>
                </div>
                <div className="group relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-4 border border-white/20 dark:border-gray-700/50 hover:shadow-lg hover:shadow-cyan-500/10 transition-all">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.charts}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Charts</p>
                    </div>
                    <div className="w-10 h-10 rounded-xl bg-cyan-100 dark:bg-cyan-900/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <BarChart3 className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
                    </div>
                  </div>
                </div>
                <div className="group relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-4 border border-white/20 dark:border-gray-700/50 hover:shadow-lg hover:shadow-indigo-500/10 transition-all">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.transforms}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Transforms</p>
                    </div>
                    <div className="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Wand2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                    </div>
                  </div>
                </div>
                <div className="group relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-4 border border-white/20 dark:border-gray-700/50 hover:shadow-lg hover:shadow-amber-500/10 transition-all">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.favorites}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Favorites</p>
                    </div>
                    <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Star className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6 pb-12 sm:px-8 lg:px-12">
        <div className="max-w-7xl mx-auto">
          {!hasData ? (
            /* Empty State - Getting Started */
            <div className="py-12">
              <div className="text-center mb-12">
                <div className="relative inline-block mb-6">
                  <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-violet-500 via-fuchsia-500 to-pink-500 flex items-center justify-center shadow-2xl shadow-violet-500/30">
                    <Boxes className="w-12 h-12 text-white" />
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-br from-violet-500 to-fuchsia-500 rounded-3xl blur-2xl opacity-30 scale-150" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                  Get started with your analytics
                </h2>
                <p className="text-gray-500 dark:text-gray-400 max-w-lg mx-auto">
                  Connect your data sources, create stunning visualizations, and build interactive dashboards in minutes.
                </p>
              </div>

              {/* Getting Started Cards */}
              <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                <Link
                  to="/connections"
                  className="group relative overflow-hidden bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl hover:shadow-blue-500/10 hover:-translate-y-1 transition-all"
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-400/10 to-cyan-400/10 rounded-full blur-2xl transform translate-x-8 -translate-y-8" />
                  <div className="relative">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-5 shadow-lg shadow-blue-500/25 group-hover:scale-110 transition-transform">
                      <Database className="w-7 h-7 text-white" />
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded-full">Step 1</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      Connect Data
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Link PostgreSQL, MySQL, or other data sources securely.
                    </p>
                    <div className="flex items-center gap-1 mt-4 text-sm text-blue-600 dark:text-blue-400 font-medium">
                      Get started <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Link>

                <Link
                  to="/charts/new"
                  className="group relative overflow-hidden bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl hover:shadow-violet-500/10 hover:-translate-y-1 transition-all"
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-violet-400/10 to-fuchsia-400/10 rounded-full blur-2xl transform translate-x-8 -translate-y-8" />
                  <div className="relative">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center mb-5 shadow-lg shadow-violet-500/25 group-hover:scale-110 transition-transform">
                      <BarChart3 className="w-7 h-7 text-white" />
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-medium text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-900/30 px-2 py-0.5 rounded-full">Step 2</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors">
                      Create Charts
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Visualize your data with beautiful, interactive charts.
                    </p>
                    <div className="flex items-center gap-1 mt-4 text-sm text-violet-600 dark:text-violet-400 font-medium">
                      Create chart <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Link>

                <Link
                  to="/dashboards/new"
                  className="group relative overflow-hidden bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl hover:shadow-emerald-500/10 hover:-translate-y-1 transition-all"
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-emerald-400/10 to-teal-400/10 rounded-full blur-2xl transform translate-x-8 -translate-y-8" />
                  <div className="relative">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mb-5 shadow-lg shadow-emerald-500/25 group-hover:scale-110 transition-transform">
                      <Grid3X3 className="w-7 h-7 text-white" />
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-0.5 rounded-full">Step 3</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                      Build Dashboards
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Combine charts into powerful dashboards and share insights.
                    </p>
                    <div className="flex items-center gap-1 mt-4 text-sm text-emerald-600 dark:text-emerald-400 font-medium">
                      Build now <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Link>
              </div>
            </div>
          ) : (
            /* Dashboard Content */
            <div className="space-y-10">
              {/* Quick Chart Suggestions */}
              <QuickChartSuggestions />

              {/* Suggested Questions */}
              {data.suggested_questions.length > 0 && (
                <section>
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
                        <Lightbulb className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Ask a question
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Get instant answers from your data</p>
                      </div>
                    </div>
                  </div>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {data.suggested_questions.slice(0, 6).map((question) => (
                      <button
                        key={question.id}
                        onClick={() => handleQuestionClick(question)}
                        className="group relative overflow-hidden text-left p-5 bg-gradient-to-br from-amber-50/80 to-orange-50/80 dark:from-amber-900/20 dark:to-orange-900/20 rounded-2xl border border-amber-200/50 dark:border-amber-800/50 hover:shadow-lg hover:shadow-amber-500/10 hover:-translate-y-0.5 transition-all"
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-2xl flex-shrink-0">{question.icon || '💡'}</span>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 dark:text-white group-hover:text-amber-700 dark:group-hover:text-amber-400 transition-colors line-clamp-2">
                              {question.question}
                            </p>
                            {question.description && (
                              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1.5 line-clamp-1">
                                {question.description}
                              </p>
                            )}
                          </div>
                          <ArrowUpRight className="w-5 h-5 text-amber-500 opacity-0 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all flex-shrink-0" />
                        </div>
                      </button>
                    ))}
                  </div>
                </section>
              )}

              {/* Featured Dashboards */}
              {data.featured_dashboards.length > 0 && (
                <section>
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-violet-500/20">
                        <LayoutDashboard className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Featured Dashboards
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Your most important views</p>
                      </div>
                    </div>
                    <Link
                      to="/dashboards"
                      className="flex items-center gap-1 text-sm text-violet-600 dark:text-violet-400 font-medium hover:text-violet-700 dark:hover:text-violet-300 transition-colors"
                    >
                      View all
                      <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
                    {data.featured_dashboards.slice(0, 3).map((dashboard, idx) => (
                      <Link
                        key={dashboard.id}
                        to={`/dashboards/${dashboard.id}`}
                        className="group relative overflow-hidden bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 hover:shadow-xl hover:shadow-violet-500/10 hover:-translate-y-1 transition-all"
                      >
                        {/* Preview Area */}
                        <div className="h-32 bg-gradient-to-br from-violet-100/80 to-fuchsia-100/80 dark:from-violet-900/30 dark:to-fuchsia-900/30 p-4 flex items-center justify-center relative overflow-hidden">
                          <div className="absolute inset-0 bg-[linear-gradient(rgba(139,92,246,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(139,92,246,0.05)_1px,transparent_1px)] bg-[size:20px_20px]" />
                          <div className="grid grid-cols-3 gap-2 w-full max-w-[180px] relative">
                            <div className="bg-white/60 dark:bg-gray-800/60 rounded-lg p-2 h-12"><MiniBarChart color="#8b5cf6" /></div>
                            <div className="bg-white/60 dark:bg-gray-800/60 rounded-lg p-2 h-12 col-span-2"><MiniLineChart color="#06b6d4" /></div>
                            <div className="bg-white/60 dark:bg-gray-800/60 rounded-lg p-2 h-10 col-span-2"><MiniAreaChart color="#10b981" /></div>
                            <div className="bg-white/60 dark:bg-gray-800/60 rounded-lg p-2 h-10 flex items-center justify-center">
                              <MiniPieChart color="#f59e0b" />
                            </div>
                          </div>
                          {/* Hover Overlay */}
                          <div className="absolute inset-0 bg-gradient-to-t from-violet-600/90 to-violet-600/70 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                            <span className="px-4 py-2 bg-white rounded-lg text-violet-600 font-medium text-sm shadow-lg">
                              Open Dashboard
                            </span>
                          </div>
                          {/* Featured Badge */}
                          <div className="absolute top-3 right-3 px-2 py-1 bg-amber-400 text-amber-900 text-xs font-medium rounded-lg flex items-center gap-1">
                            <Star className="w-3 h-3" />
                            Featured
                          </div>
                        </div>

                        {/* Content */}
                        <div className="p-5">
                          <div className="flex items-start gap-3">
                            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-violet-100 to-fuchsia-100 dark:from-violet-900/40 dark:to-fuchsia-900/40 flex items-center justify-center text-xl flex-shrink-0">
                              {dashboard.icon || defaultDashboardIcons[idx % defaultDashboardIcons.length]}
                            </div>
                            <div className="flex-1 min-w-0">
                              <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors truncate">
                                {dashboard.name}
                              </h3>
                              {dashboard.description && (
                                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-1">
                                  {dashboard.description}
                                </p>
                              )}
                              <div className="flex items-center gap-3 mt-2">
                                <span className="flex items-center gap-1 text-xs text-gray-400">
                                  <BarChart3 className="w-3 h-3" />
                                  {dashboard.chart_count} charts
                                </span>
                              </div>
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
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                        <Wand2 className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Transform Recipes
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Your data transformation pipelines</p>
                      </div>
                    </div>
                    <Link
                      to="/transforms"
                      className="flex items-center gap-1 text-sm text-indigo-600 dark:text-indigo-400 font-medium hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
                    >
                      View all
                      <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {data.recent_transforms.slice(0, 3).map((recipe) => (
                      <Link
                        key={recipe.id}
                        to="/transforms"
                        className="group relative overflow-hidden bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-5 hover:shadow-lg hover:border-indigo-300 dark:hover:border-indigo-600 hover:-translate-y-0.5 transition-all"
                      >
                        <div className="flex items-start gap-4">
                          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/40 dark:to-purple-900/40 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <Wand2 className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
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
                            <div className="flex flex-wrap items-center gap-2 mt-3">
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-md">
                                <Table2 className="w-3 h-3" />
                                {recipe.source_table}
                              </span>
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-xs rounded-md">
                                <Layers className="w-3 h-3" />
                                {recipe.steps_count} steps
                              </span>
                              {recipe.row_count !== null && (
                                <span className="text-xs text-gray-400">{recipe.row_count.toLocaleString()} rows</span>
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
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                        <Clock className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Recent Charts
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Pick up where you left off</p>
                      </div>
                    </div>
                    <Link
                      to="/gallery"
                      className="flex items-center gap-1 text-sm text-cyan-600 dark:text-cyan-400 font-medium hover:text-cyan-700 dark:hover:text-cyan-300 transition-colors"
                    >
                      View all
                      <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {data.recent_charts.slice(0, 4).map((chart) => {
                      const config = chartTypeConfig[chart.chart_type] || chartTypeConfig.bar
                      const Icon = config.icon
                      const MiniChart = config.MiniChart

                      return (
                        <Link
                          key={chart.id}
                          to={`/charts/${chart.id}`}
                          className="group relative overflow-hidden bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:-translate-y-0.5 transition-all"
                        >
                          {/* Chart Preview */}
                          <div className="h-24 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 p-4 flex items-center justify-center">
                            <div className="w-full h-full">
                              <MiniChart color={config.color} />
                            </div>
                          </div>

                          {/* Content */}
                          <div className="p-4">
                            <div className="flex items-center gap-3">
                              <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${config.color}15` }}>
                                <Icon className="w-4 h-4" style={{ color: config.color }} />
                              </div>
                              <div className="flex-1 min-w-0">
                                <h3 className="font-medium text-sm text-gray-900 dark:text-white group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors truncate">
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
                            <div className="flex items-center gap-2 mt-3 text-xs text-gray-400">
                              <Eye className="w-3 h-3" />
                              {chart.view_count} views
                            </div>
                          </div>
                        </Link>
                      )
                    })}
                  </div>
                </section>
              )}

              {/* Favorite Charts */}
              {data.favorite_charts.length > 0 && (
                <section>
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-yellow-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
                        <Bookmark className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Favorites
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Your bookmarked charts</p>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {data.favorite_charts.slice(0, 4).map((chart) => {
                      const config = chartTypeConfig[chart.chart_type] || chartTypeConfig.bar
                      const Icon = config.icon
                      const MiniChart = config.MiniChart

                      return (
                        <Link
                          key={chart.id}
                          to={`/charts/${chart.id}`}
                          className="group relative overflow-hidden bg-white dark:bg-gray-800 rounded-2xl border border-amber-200 dark:border-amber-800/50 hover:shadow-lg hover:shadow-amber-500/10 hover:-translate-y-0.5 transition-all"
                        >
                          {/* Chart Preview */}
                          <div className="h-24 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 p-4 flex items-center justify-center relative">
                            <div className="w-full h-full">
                              <MiniChart color={config.color} />
                            </div>
                            <div className="absolute top-2 right-2">
                              <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                            </div>
                          </div>

                          {/* Content */}
                          <div className="p-4">
                            <div className="flex items-center gap-3">
                              <div className="w-9 h-9 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                                <Icon className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <h3 className="font-medium text-sm text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors truncate">
                                  {chart.name}
                                </h3>
                                <p className="text-xs text-gray-400 capitalize">
                                  {chart.chart_type} chart
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2 mt-3 text-xs text-gray-400">
                              <Eye className="w-3 h-3" />
                              {chart.view_count} views
                            </div>
                          </div>
                        </Link>
                      )
                    })}
                  </div>
                </section>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
