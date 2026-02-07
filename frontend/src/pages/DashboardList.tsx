import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Plus,
  Search,
  LayoutGrid,
  Rows3,
  Wand2,
  Layers,
  Table2,
  BarChart3,
  Trash2,
  Clock,
  LayoutDashboard,
  TrendingUp,
  PieChart,
  Activity,
  Sparkles,
  Star,
  Eye,
  MoreHorizontal,
  ExternalLink,
  Copy,
  Pencil,
  Users,
  Globe,
  Lock,
  ChevronRight,
  Zap,
  LineChart,
  Gauge,
  ArrowUpRight,
  Play,
  Calendar,
  Home,
} from 'lucide-react'
import { api } from '../lib/api'
import { PageHeader, Badge } from '@/components/ui/glass'

interface Dashboard {
  id: string
  name: string
  description: string | null
  icon: string | null
  is_public: boolean
  is_featured: boolean
  chart_count: number
  created_at: string
  updated_at: string
  layout?: {
    widgets?: Array<{
      type: string
      title?: string
      chartData?: { chart_type?: string }
    }>
  }
}

interface TransformRecipe {
  id: string
  name: string
  description: string | null
  connection_id: string
  source_table: string
  source_schema: string
  steps: any[]
  row_count: number | null
  last_executed: string | null
  created_at: string
  updated_at: string
}

// Mini chart preview components
const MiniBarChart = ({ color = '#8b5cf6' }: { color?: string }) => (
  <svg viewBox="0 0 48 32" className="w-full h-full">
    <rect x="2" y="18" width="6" height="12" fill={color} opacity="0.6" rx="1" />
    <rect x="10" y="12" width="6" height="18" fill={color} opacity="0.8" rx="1" />
    <rect x="18" y="8" width="6" height="22" fill={color} rx="1" />
    <rect x="26" y="14" width="6" height="16" fill={color} opacity="0.7" rx="1" />
    <rect x="34" y="10" width="6" height="20" fill={color} opacity="0.9" rx="1" />
    <rect x="42" y="16" width="4" height="14" fill={color} opacity="0.5" rx="1" />
  </svg>
)

const MiniLineChart = ({ color = '#06b6d4' }: { color?: string }) => (
  <svg viewBox="0 0 48 32" className="w-full h-full">
    <path
      d="M2 28 L10 20 L18 24 L26 12 L34 16 L42 8 L46 10"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M2 28 L10 20 L18 24 L26 12 L34 16 L42 8 L46 10 L46 32 L2 32 Z"
      fill={color}
      opacity="0.1"
    />
  </svg>
)

const MiniPieChart = ({ color = '#f59e0b' }: { color?: string }) => (
  <svg viewBox="0 0 32 32" className="w-full h-full">
    <circle cx="16" cy="16" r="14" fill="none" stroke={color} strokeWidth="4" opacity="0.2" />
    <circle
      cx="16"
      cy="16"
      r="14"
      fill="none"
      stroke={color}
      strokeWidth="4"
      strokeDasharray="50 88"
      transform="rotate(-90 16 16)"
    />
    <circle
      cx="16"
      cy="16"
      r="14"
      fill="none"
      stroke={color}
      strokeWidth="4"
      strokeDasharray="25 88"
      strokeDashoffset="-50"
      opacity="0.6"
      transform="rotate(-90 16 16)"
    />
  </svg>
)

const MiniKPI = ({ color = '#10b981' }: { color?: string }) => (
  <div className="flex flex-col items-center justify-center h-full">
    <div className="text-lg font-bold" style={{ color }}>$24.5K</div>
    <div className="flex items-center gap-0.5 text-[8px]" style={{ color }}>
      <TrendingUp className="w-2 h-2" />
      <span>+12%</span>
    </div>
  </div>
)

const MiniGauge = ({ color = '#ec4899' }: { color?: string }) => (
  <svg viewBox="0 0 32 20" className="w-full h-full">
    <path
      d="M4 18 A12 12 0 0 1 28 18"
      fill="none"
      stroke={color}
      strokeWidth="3"
      opacity="0.2"
      strokeLinecap="round"
    />
    <path
      d="M4 18 A12 12 0 0 1 22 8"
      fill="none"
      stroke={color}
      strokeWidth="3"
      strokeLinecap="round"
    />
  </svg>
)

// Widget preview component
const WidgetPreview = ({ type, index }: { type: string; index: number }) => {
  const colors = ['#8b5cf6', '#06b6d4', '#f59e0b', '#10b981', '#ec4899', '#3b82f6']
  const color = colors[index % colors.length]

  switch (type) {
    case 'chart':
      return index % 2 === 0 ? <MiniBarChart color={color} /> : <MiniLineChart color={color} />
    case 'kpi':
      return <MiniKPI color={color} />
    case 'pie':
    case 'donut':
      return <MiniPieChart color={color} />
    default:
      return <MiniBarChart color={color} />
  }
}

// Dashboard preview card
const DashboardPreviewCard = ({
  dashboard,
  index,
  onDelete,
  featured = false
}: {
  dashboard: Dashboard
  index: number
  onDelete: (id: string) => void
  featured?: boolean
}) => {
  const navigate = useNavigate()
  const [showMenu, setShowMenu] = useState(false)

  const widgets = dashboard.layout?.widgets || []
  const previewWidgets = widgets.slice(0, 6)
  const hasMoreWidgets = widgets.length > 6

  const gradients = [
    'from-violet-500/10 via-purple-500/5 to-fuchsia-500/10',
    'from-blue-500/10 via-cyan-500/5 to-teal-500/10',
    'from-amber-500/10 via-orange-500/5 to-rose-500/10',
    'from-emerald-500/10 via-green-500/5 to-teal-500/10',
    'from-pink-500/10 via-rose-500/5 to-red-500/10',
    'from-indigo-500/10 via-blue-500/5 to-violet-500/10',
  ]

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    if (days === 0) return 'Today'
    if (days === 1) return 'Yesterday'
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <div
      className={`group relative bg-white dark:bg-gray-800/50 rounded-2xl border border-gray-200/60 dark:border-gray-700/60 overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-gray-200/40 dark:hover:shadow-gray-900/40 hover:border-violet-300/60 dark:hover:border-violet-500/40 hover:-translate-y-1 ${
        featured ? 'md:col-span-2 md:row-span-2' : ''
      }`}
    >
      {/* Preview Area */}
      <Link to={`/dashboards/${dashboard.id}`} className="block">
        <div className={`relative ${featured ? 'h-64' : 'h-44'} bg-gradient-to-br ${gradients[index % gradients.length]} p-4 overflow-hidden`}>
          {/* Grid of mini widgets */}
          {previewWidgets.length > 0 ? (
            <div className={`grid ${featured ? 'grid-cols-3 grid-rows-2' : 'grid-cols-3 grid-rows-2'} gap-2 h-full`}>
              {previewWidgets.map((widget, i) => (
                <div
                  key={i}
                  className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg p-2 flex items-center justify-center shadow-sm"
                >
                  <WidgetPreview type={widget.type} index={i} />
                </div>
              ))}
              {hasMoreWidgets && (
                <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg flex items-center justify-center text-xs text-gray-500 dark:text-gray-400 font-medium">
                  +{widgets.length - 6} more
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center">
              <div className="w-16 h-16 rounded-2xl bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm flex items-center justify-center mb-3 shadow-lg">
                <span className="text-3xl">{dashboard.icon || '📊'}</span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Empty dashboard</p>
            </div>
          )}

          {/* Hover overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center pb-6">
            <div className="flex items-center gap-3">
              <button
                onClick={(e) => {
                  e.preventDefault()
                  navigate(`/dashboards/${dashboard.id}`)
                }}
                className="flex items-center gap-2 px-4 py-2 bg-white text-gray-900 rounded-full text-sm font-medium shadow-lg hover:bg-gray-100 transition-colors"
              >
                <Eye className="w-4 h-4" />
                View
              </button>
              <button
                onClick={(e) => {
                  e.preventDefault()
                  navigate(`/dashboards/${dashboard.id}`)
                }}
                className="flex items-center gap-2 px-4 py-2 bg-violet-500 text-white rounded-full text-sm font-medium shadow-lg hover:bg-violet-600 transition-colors"
              >
                <Pencil className="w-4 h-4" />
                Edit
              </button>
            </div>
          </div>

          {/* Featured badge */}
          {dashboard.is_featured && (
            <div className="absolute top-3 left-3 flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full text-white text-xs font-medium shadow-lg">
              <Star className="w-3 h-3 fill-current" />
              Featured
            </div>
          )}

          {/* Visibility badge */}
          <div className="absolute top-3 right-3">
            {dashboard.is_public ? (
              <div className="p-1.5 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg shadow-sm">
                <Globe className="w-3.5 h-3.5 text-green-500" />
              </div>
            ) : (
              <div className="p-1.5 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg shadow-sm">
                <Lock className="w-3.5 h-3.5 text-gray-400" />
              </div>
            )}
          </div>
        </div>
      </Link>

      {/* Content */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <Link to={`/dashboards/${dashboard.id}`} className="flex-1 min-w-0 group/title">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">{dashboard.icon || '📊'}</span>
              <h3 className="font-semibold text-gray-900 dark:text-white truncate group-hover/title:text-violet-600 dark:group-hover/title:text-violet-400 transition-colors">
                {dashboard.name}
              </h3>
            </div>
            {dashboard.description && (
              <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
                {dashboard.description}
              </p>
            )}
          </Link>

          {/* Menu */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
            >
              <MoreHorizontal className="w-4 h-4 text-gray-400" />
            </button>
            {showMenu && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
                <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 py-1 z-20">
                  <Link
                    to={`/dashboards/${dashboard.id}`}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <ExternalLink className="w-4 h-4" />
                    Open Dashboard
                  </Link>
                  <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">
                    <Copy className="w-4 h-4" />
                    Duplicate
                  </button>
                  <hr className="my-1 border-gray-100 dark:border-gray-700" />
                  <button
                    onClick={() => {
                      setShowMenu(false)
                      onDelete(dashboard.id)
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-900/20"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1.5">
            <BarChart3 className="w-3.5 h-3.5" />
            {dashboard.chart_count} widgets
          </span>
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            {formatDate(dashboard.updated_at)}
          </span>
        </div>
      </div>
    </div>
  )
}

// Quick action cards
const QuickActionCard = ({
  icon: Icon,
  title,
  description,
  href,
  gradient
}: {
  icon: any
  title: string
  description: string
  href: string
  gradient: string
}) => (
  <Link
    to={href}
    className="group flex items-center gap-4 p-4 bg-white dark:bg-gray-800/50 rounded-2xl border border-gray-200/60 dark:border-gray-700/60 hover:shadow-lg hover:border-violet-300/60 dark:hover:border-violet-500/40 transition-all"
  >
    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
      <Icon className="w-6 h-6 text-white" />
    </div>
    <div className="flex-1">
      <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors">
        {title}
      </h3>
      <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
    </div>
    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-violet-500 group-hover:translate-x-1 transition-all" />
  </Link>
)

export function DashboardList() {
  const navigate = useNavigate()
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<'all' | 'featured' | 'recent'>('all')

  const [dashboards, setDashboards] = useState<Dashboard[]>([])
  const [loadingDashboards, setLoadingDashboards] = useState(true)

  const [transforms, setTransforms] = useState<TransformRecipe[]>([])
  const [loadingTransforms, setLoadingTransforms] = useState(true)

  useEffect(() => {
    fetchDashboards()
    fetchTransforms()
  }, [])

  const fetchDashboards = async () => {
    try {
      setLoadingDashboards(true)
      const response = await api.get('/dashboards/')
      setDashboards(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboards:', error)
    } finally {
      setLoadingDashboards(false)
    }
  }

  const fetchTransforms = async () => {
    try {
      setLoadingTransforms(true)
      const response = await api.get('/transforms/')
      setTransforms(response.data)
    } catch (error) {
      console.error('Failed to fetch transforms:', error)
    } finally {
      setLoadingTransforms(false)
    }
  }

  const deleteDashboard = async (id: string) => {
    if (!confirm('Are you sure you want to delete this dashboard?')) return

    try {
      await api.delete(`/dashboards/${id}`)
      fetchDashboards()
    } catch (error) {
      console.error('Failed to delete dashboard:', error)
    }
  }

  const filteredDashboards = dashboards.filter((d) => {
    const matchesSearch = d.name.toLowerCase().includes(search.toLowerCase()) ||
      (d.description || '').toLowerCase().includes(search.toLowerCase())

    if (filter === 'featured') return matchesSearch && d.is_featured
    if (filter === 'recent') {
      const daysSinceUpdate = (Date.now() - new Date(d.updated_at).getTime()) / (1000 * 60 * 60 * 24)
      return matchesSearch && daysSinceUpdate < 7
    }
    return matchesSearch
  })

  const featuredDashboards = dashboards.filter(d => d.is_featured)
  const recentDashboards = [...dashboards]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 4)

  const stats = {
    total: dashboards.length,
    widgets: dashboards.reduce((acc, d) => acc + d.chart_count, 0),
    transforms: transforms.length,
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 overflow-hidden">
      {/* Modern Responsive Header */}
      <PageHeader
        variant="default"
        gradient="indigo"
        size="md"
        icon={<LayoutDashboard className="w-7 h-7" />}
        title="Dashboards"
        subtitle="Build and manage your analytics dashboards"
        breadcrumbs={[
          { label: 'Home', href: '/', icon: <Home className="w-3.5 h-3.5" /> },
          { label: 'Dashboards' }
        ]}
        badge={
          dashboards.length > 0 ? (
            <Badge variant="primary" size="sm">{dashboards.length} Total</Badge>
          ) : null
        }
        stats={dashboards.length > 0 ? [
          { label: 'dashboards', value: stats.total, icon: <LayoutGrid className="w-4 h-4" />, color: 'violet' },
          { label: 'widgets', value: stats.widgets, icon: <BarChart3 className="w-4 h-4" />, color: 'cyan' },
          { label: 'transforms', value: stats.transforms, icon: <Wand2 className="w-4 h-4" />, color: 'rose' },
        ] : undefined}
        actions={
          <>
            <Link
              to="/transforms"
              className="flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-xl border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium text-sm shadow-sm"
            >
              <Wand2 className="w-4 h-4" />
              <span className="hidden sm:inline">Transforms</span>
            </Link>
            <Link
              to="/dashboards/new"
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-medium text-sm shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 hover:-translate-y-0.5 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden sm:inline">New Dashboard</span>
            </Link>
          </>
        }
      />

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="px-6 pb-8">
          {loadingDashboards ? (
            <div className="flex items-center justify-center h-64">
              <div className="flex flex-col items-center gap-4">
                <div className="relative">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-violet-500/30 animate-pulse">
                    <LayoutDashboard className="w-8 h-8 text-white" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-white dark:bg-gray-800 flex items-center justify-center shadow-lg">
                    <div className="w-4 h-4 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
                  </div>
                </div>
                <span className="text-sm text-gray-500 dark:text-gray-400">Loading dashboards...</span>
              </div>
            </div>
          ) : dashboards.length === 0 ? (
            /* Empty State */
            <div className="py-16">
              <div className="max-w-2xl mx-auto text-center mb-12">
                <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-violet-100 to-purple-100 dark:from-violet-900/30 dark:to-purple-900/30 flex items-center justify-center mx-auto mb-6 shadow-xl">
                  <LayoutDashboard className="w-12 h-12 text-violet-500" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                  Create your first dashboard
                </h2>
                <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-md mx-auto">
                  Dashboards help you visualize and monitor your data. Start by creating a new dashboard or exploring templates.
                </p>
                <Link
                  to="/dashboards/new"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 hover:scale-105 transition-all"
                >
                  <Plus className="w-5 h-5" />
                  Create Dashboard
                </Link>
              </div>

              {/* Quick Actions */}
              <div className="max-w-3xl mx-auto grid gap-4">
                <QuickActionCard
                  icon={Zap}
                  title="Quick Charts"
                  description="Create instant charts with AI assistance"
                  href="/quick-charts"
                  gradient="from-amber-400 to-orange-500"
                />
                <QuickActionCard
                  icon={Wand2}
                  title="Transform Data"
                  description="Clean and prepare your data for analysis"
                  href="/transforms"
                  gradient="from-pink-400 to-rose-500"
                />
                <QuickActionCard
                  icon={Gauge}
                  title="KPI Dashboard"
                  description="Track key performance indicators"
                  href="/kpis"
                  gradient="from-emerald-400 to-teal-500"
                />
              </div>
            </div>
          ) : (
            <>
              {/* Search & Filter Bar */}
              <div className="flex items-center justify-between mb-6 sticky top-0 bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 py-4 -mx-6 px-6 z-10">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search dashboards..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      className="pl-10 pr-4 py-2.5 w-72 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all shadow-sm"
                    />
                  </div>

                  {/* Filter pills */}
                  <div className="flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-xl">
                    {[
                      { id: 'all', label: 'All' },
                      { id: 'featured', label: 'Featured' },
                      { id: 'recent', label: 'Recent' },
                    ].map((f) => (
                      <button
                        key={f.id}
                        onClick={() => setFilter(f.id as any)}
                        className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-all ${
                          filter === f.id
                            ? 'bg-white dark:bg-gray-700 text-violet-600 dark:text-violet-400 shadow-sm'
                            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                        }`}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <div className="flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`p-2 rounded-md transition-all ${
                        viewMode === 'grid'
                          ? 'bg-white dark:bg-gray-700 shadow-sm text-violet-600 dark:text-violet-400'
                          : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                      }`}
                    >
                      <LayoutGrid className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`p-2 rounded-md transition-all ${
                        viewMode === 'list'
                          ? 'bg-white dark:bg-gray-700 shadow-sm text-violet-600 dark:text-violet-400'
                          : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                      }`}
                    >
                      <Rows3 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Dashboard Grid */}
              {filteredDashboards.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-center">
                  <Search className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    No dashboards found
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    Try adjusting your search or filter
                  </p>
                </div>
              ) : viewMode === 'grid' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 auto-rows-fr">
                  {filteredDashboards.map((dashboard, index) => (
                    <DashboardPreviewCard
                      key={dashboard.id}
                      dashboard={dashboard}
                      index={index}
                      onDelete={deleteDashboard}
                      featured={index === 0 && filter === 'all' && !search && dashboard.is_featured}
                    />
                  ))}
                </div>
              ) : (
                /* List View */
                <div className="space-y-3">
                  {filteredDashboards.map((dashboard, index) => (
                    <div
                      key={dashboard.id}
                      className="group flex items-center gap-4 p-4 bg-white dark:bg-gray-800/50 rounded-2xl border border-gray-200/60 dark:border-gray-700/60 hover:shadow-lg hover:border-violet-300/60 dark:hover:border-violet-500/40 transition-all"
                    >
                      {/* Preview thumbnail */}
                      <Link to={`/dashboards/${dashboard.id}`} className="flex-shrink-0">
                        <div className="w-20 h-14 rounded-xl bg-gradient-to-br from-violet-100 to-purple-100 dark:from-violet-900/30 dark:to-purple-900/30 flex items-center justify-center overflow-hidden">
                          {dashboard.layout?.widgets?.length ? (
                            <div className="grid grid-cols-2 gap-0.5 p-1 w-full h-full">
                              {dashboard.layout.widgets.slice(0, 4).map((w, i) => (
                                <div key={i} className="bg-white/60 dark:bg-gray-700/60 rounded-sm" />
                              ))}
                            </div>
                          ) : (
                            <span className="text-2xl">{dashboard.icon || '📊'}</span>
                          )}
                        </div>
                      </Link>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <Link to={`/dashboards/${dashboard.id}`}>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors truncate">
                              {dashboard.name}
                            </h3>
                            {dashboard.is_featured && (
                              <Star className="w-4 h-4 text-amber-500 fill-amber-500 flex-shrink-0" />
                            )}
                          </div>
                          {dashboard.description && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                              {dashboard.description}
                            </p>
                          )}
                        </Link>
                      </div>

                      {/* Stats */}
                      <div className="flex items-center gap-6 text-sm text-gray-500 dark:text-gray-400">
                        <span className="flex items-center gap-1.5">
                          <BarChart3 className="w-4 h-4" />
                          {dashboard.chart_count}
                        </span>
                        <span className="flex items-center gap-1.5">
                          <Clock className="w-4 h-4" />
                          {new Date(dashboard.updated_at).toLocaleDateString()}
                        </span>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Link
                          to={`/dashboards/${dashboard.id}`}
                          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        >
                          <Eye className="w-4 h-4 text-gray-400" />
                        </Link>
                        <button
                          onClick={() => deleteDashboard(dashboard.id)}
                          className="p-2 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4 text-gray-400 hover:text-rose-500" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Transforms Section */}
              {transforms.length > 0 && !search && filter === 'all' && (
                <section className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-400 to-rose-500 flex items-center justify-center shadow-lg shadow-pink-500/20">
                        <Wand2 className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Transform Recipes</h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{transforms.length} data transformations</p>
                      </div>
                    </div>
                    <Link
                      to="/transforms"
                      className="flex items-center gap-1 text-sm text-violet-600 dark:text-violet-400 hover:underline font-medium"
                    >
                      View all
                      <ArrowUpRight className="w-4 h-4" />
                    </Link>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {transforms.slice(0, 4).map((transform) => (
                      <Link
                        key={transform.id}
                        to="/transforms"
                        className="group p-4 bg-white dark:bg-gray-800/50 rounded-xl border border-gray-200/60 dark:border-gray-700/60 hover:shadow-lg hover:border-pink-300/60 dark:hover:border-pink-500/40 transition-all"
                      >
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-pink-400 to-rose-500 flex items-center justify-center">
                            <Wand2 className="w-4 h-4 text-white" />
                          </div>
                          <h3 className="font-medium text-gray-900 dark:text-white truncate group-hover:text-pink-600 dark:group-hover:text-pink-400 transition-colors">
                            {transform.name}
                          </h3>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                          <span className="flex items-center gap-1 px-2 py-0.5 bg-pink-50 dark:bg-pink-900/30 text-pink-600 dark:text-pink-400 rounded-full">
                            <Layers className="w-3 h-3" />
                            {transform.steps?.length || 0} steps
                          </span>
                          {transform.row_count && (
                            <span>{transform.row_count.toLocaleString()} rows</span>
                          )}
                        </div>
                      </Link>
                    ))}
                  </div>
                </section>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
