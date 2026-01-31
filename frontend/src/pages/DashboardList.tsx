import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Plus,
  Search,
  LayoutGrid,
  List,
  MoreHorizontal,
  Loader2,
  Wand2,
  Layers,
  Table2,
  BarChart3,
  Trash2,
  Edit3,
  Clock,
  LayoutDashboard,
  TrendingUp,
  PieChart,
  Activity,
} from 'lucide-react'
import { api } from '../lib/api'

// Dashboard cover patterns
const dashboardCovers = [
  // Gradient mesh with chart elements
  (index: number) => (
    <div className="absolute inset-0 bg-gradient-to-br from-violet-500 via-purple-500 to-fuchsia-500">
      <div className="absolute inset-0 opacity-20">
        <svg className="w-full h-full" viewBox="0 0 100 60">
          {/* Mini bar chart */}
          <rect x="10" y="35" width="8" height="20" fill="white" rx="1" />
          <rect x="22" y="25" width="8" height="30" fill="white" rx="1" />
          <rect x="34" y="15" width="8" height="40" fill="white" rx="1" />
          <rect x="46" y="30" width="8" height="25" fill="white" rx="1" />
          <rect x="58" y="20" width="8" height="35" fill="white" rx="1" />
          {/* Trend line */}
          <path d="M10 45 Q30 20, 50 35 T90 15" stroke="white" strokeWidth="2" fill="none" opacity="0.5" />
        </svg>
      </div>
      <div className="absolute bottom-3 right-3 flex gap-1">
        <div className="w-2 h-2 bg-white/40 rounded-full" />
        <div className="w-2 h-2 bg-white/60 rounded-full" />
        <div className="w-2 h-2 bg-white/80 rounded-full" />
      </div>
    </div>
  ),
  // Blue waves with pie
  (index: number) => (
    <div className="absolute inset-0 bg-gradient-to-br from-blue-500 via-cyan-500 to-teal-500">
      <div className="absolute inset-0 opacity-20">
        <svg className="w-full h-full" viewBox="0 0 100 60">
          {/* Pie chart */}
          <circle cx="30" cy="30" r="18" fill="none" stroke="white" strokeWidth="8" strokeDasharray="40 113" transform="rotate(-90 30 30)" />
          <circle cx="30" cy="30" r="18" fill="none" stroke="white" strokeWidth="8" strokeDasharray="30 113" strokeDashoffset="-40" opacity="0.7" transform="rotate(-90 30 30)" />
          <circle cx="30" cy="30" r="18" fill="none" stroke="white" strokeWidth="8" strokeDasharray="43 113" strokeDashoffset="-70" opacity="0.4" transform="rotate(-90 30 30)" />
          {/* KPI boxes */}
          <rect x="60" y="10" width="30" height="15" fill="white" rx="2" opacity="0.3" />
          <rect x="60" y="30" width="30" height="15" fill="white" rx="2" opacity="0.5" />
        </svg>
      </div>
      <div className="absolute top-3 left-3">
        <Activity className="w-5 h-5 text-white/50" />
      </div>
    </div>
  ),
  // Orange/amber with area chart
  (index: number) => (
    <div className="absolute inset-0 bg-gradient-to-br from-orange-500 via-amber-500 to-yellow-500">
      <div className="absolute inset-0 opacity-25">
        <svg className="w-full h-full" viewBox="0 0 100 60" preserveAspectRatio="none">
          {/* Area chart */}
          <path d="M0 60 L0 40 Q25 20, 50 35 T100 25 L100 60 Z" fill="white" />
          <path d="M0 60 L0 50 Q25 35, 50 45 T100 35 L100 60 Z" fill="white" opacity="0.5" />
        </svg>
      </div>
      <div className="absolute top-3 right-3 flex items-center gap-1 bg-white/20 rounded-full px-2 py-1">
        <TrendingUp className="w-3 h-3 text-white" />
        <span className="text-xs text-white font-medium">+24%</span>
      </div>
    </div>
  ),
  // Green with dots pattern
  (index: number) => (
    <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 via-green-500 to-teal-600">
      <div className="absolute inset-0 opacity-20">
        <svg className="w-full h-full" viewBox="0 0 100 60">
          {/* Scatter plot dots */}
          {[
            [15, 40], [25, 25], [35, 35], [45, 20], [55, 30], [65, 15], [75, 25], [85, 10],
            [20, 45], [40, 40], [60, 35], [80, 20]
          ].map(([x, y], i) => (
            <circle key={i} cx={x} cy={y} r={i % 3 === 0 ? 4 : 3} fill="white" opacity={0.5 + (i % 3) * 0.2} />
          ))}
          {/* Trend line */}
          <path d="M10 45 L90 10" stroke="white" strokeWidth="1.5" strokeDasharray="4 2" />
        </svg>
      </div>
      <div className="absolute bottom-3 left-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-1 bg-white/60 rounded" />
          <div className="w-6 h-1 bg-white/40 rounded" />
          <div className="w-4 h-1 bg-white/20 rounded" />
        </div>
      </div>
    </div>
  ),
  // Pink/rose with horizontal bars
  (index: number) => (
    <div className="absolute inset-0 bg-gradient-to-br from-pink-500 via-rose-500 to-red-500">
      <div className="absolute inset-0 opacity-25">
        <svg className="w-full h-full" viewBox="0 0 100 60">
          {/* Horizontal bars */}
          <rect x="20" y="10" width="60" height="8" fill="white" rx="2" />
          <rect x="20" y="22" width="45" height="8" fill="white" rx="2" opacity="0.8" />
          <rect x="20" y="34" width="70" height="8" fill="white" rx="2" opacity="0.6" />
          <rect x="20" y="46" width="35" height="8" fill="white" rx="2" opacity="0.4" />
        </svg>
      </div>
      <div className="absolute top-3 left-3">
        <PieChart className="w-5 h-5 text-white/50" />
      </div>
    </div>
  ),
  // Indigo with grid pattern
  (index: number) => (
    <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-blue-600 to-violet-600">
      <div className="absolute inset-0 opacity-20">
        <svg className="w-full h-full" viewBox="0 0 100 60">
          {/* Grid of mini cards */}
          <rect x="5" y="5" width="28" height="22" fill="white" rx="2" />
          <rect x="37" y="5" width="28" height="22" fill="white" rx="2" opacity="0.7" />
          <rect x="69" y="5" width="28" height="22" fill="white" rx="2" opacity="0.5" />
          <rect x="5" y="32" width="28" height="22" fill="white" rx="2" opacity="0.5" />
          <rect x="37" y="32" width="28" height="22" fill="white" rx="2" opacity="0.7" />
          <rect x="69" y="32" width="28" height="22" fill="white" rx="2" opacity="0.3" />
        </svg>
      </div>
      <div className="absolute bottom-3 right-3">
        <LayoutDashboard className="w-5 h-5 text-white/40" />
      </div>
    </div>
  ),
]

const getDashboardCover = (index: number) => {
  const coverIndex = index % dashboardCovers.length
  return dashboardCovers[coverIndex](index)
}

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

type TabType = 'dashboards' | 'transforms'

export function DashboardList() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboards')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [search, setSearch] = useState('')

  // Dashboard state
  const [dashboards, setDashboards] = useState<Dashboard[]>([])
  const [loadingDashboards, setLoadingDashboards] = useState(true)

  // Transform state
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

  const deleteTransform = async (id: string) => {
    if (!confirm('Are you sure you want to delete this transform recipe?')) return

    try {
      await api.delete(`/transforms/${id}`)
      fetchTransforms()
    } catch (error) {
      console.error('Failed to delete transform:', error)
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

  const filteredDashboards = dashboards.filter(
    (d) =>
      d.name.toLowerCase().includes(search.toLowerCase()) ||
      (d.description || '').toLowerCase().includes(search.toLowerCase())
  )

  const filteredTransforms = transforms.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      (t.description || '').toLowerCase().includes(search.toLowerCase()) ||
      t.source_table.toLowerCase().includes(search.toLowerCase())
  )

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString()
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Dashboards & Transforms
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Manage your dashboards and data transform recipes
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/transforms"
            className="flex items-center gap-2 px-4 py-2 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <Wand2 className="w-5 h-5" />
            New Transform
          </Link>
          <Link
            to="/dashboards/new"
            className="flex items-center gap-2 px-4 py-2 bg-indigo-700 text-white rounded-md hover:bg-indigo-800 transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Dashboard
          </Link>
        </div>
      </header>

      {/* Tabs */}
      <div className="px-6 pt-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab('dashboards')}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg border-b-2 transition-colors ${
              activeTab === 'dashboards'
                ? 'border-indigo-600 text-indigo-600 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboards
            <span className="ml-1 px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 rounded-full">
              {dashboards.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('transforms')}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg border-b-2 transition-colors ${
              activeTab === 'transforms'
                ? 'border-indigo-600 text-indigo-600 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <Wand2 className="w-4 h-4" />
            Transform Recipes
            <span className="ml-1 px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 rounded-full">
              {transforms.length}
            </span>
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex items-center justify-between px-6 py-3 bg-gray-50 dark:bg-gray-800/50">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder={activeTab === 'dashboards' ? 'Search dashboards...' : 'Search transforms...'}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2 w-64 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg ${
              viewMode === 'grid'
                ? 'bg-white dark:bg-gray-700 shadow-sm'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <LayoutGrid className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg ${
              viewMode === 'list'
                ? 'bg-white dark:bg-gray-700 shadow-sm'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <List className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === 'dashboards' ? (
          // Dashboards Tab
          loadingDashboards ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
            </div>
          ) : filteredDashboards.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <LayoutDashboard className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {search ? 'No dashboards found' : 'No dashboards yet'}
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                {search ? 'Try a different search term' : 'Create your first dashboard to get started'}
              </p>
              {!search && (
                <Link
                  to="/dashboards/new"
                  className="flex items-center gap-2 px-4 py-2 bg-indigo-700 text-white rounded-md hover:bg-indigo-800 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                  Create Dashboard
                </Link>
              )}
            </div>
          ) : viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredDashboards.map((dashboard, index) => (
                <div
                  key={dashboard.id}
                  className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-lg hover:border-indigo-300 dark:hover:border-indigo-600 transition-all"
                >
                  <Link to={`/dashboards/${dashboard.id}`}>
                    <div className="aspect-video relative overflow-hidden">
                      {getDashboardCover(index)}
                      {/* Overlay icon */}
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                          <span className="text-2xl">{dashboard.icon || '📊'}</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                  <div className="p-4">
                    <div className="flex items-start justify-between">
                      <Link to={`/dashboards/${dashboard.id}`} className="flex-1">
                        <h3 className="font-medium text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                          {dashboard.name}
                        </h3>
                        {dashboard.description && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                            {dashboard.description}
                          </p>
                        )}
                      </Link>
                      <button
                        onClick={() => deleteDashboard(dashboard.id)}
                        className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <BarChart3 className="w-3 h-3" />
                        {dashboard.chart_count} charts
                      </span>
                      <span>Updated {formatDate(dashboard.updated_at)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Charts
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Updated
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredDashboards.map((dashboard) => (
                    <tr key={dashboard.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <td className="px-6 py-4">
                        <Link
                          to={`/dashboards/${dashboard.id}`}
                          className="font-medium text-gray-900 dark:text-white hover:text-indigo-600"
                        >
                          {dashboard.name}
                        </Link>
                        {dashboard.description && (
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {dashboard.description}
                          </p>
                        )}
                      </td>
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                        {dashboard.chart_count}
                      </td>
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                        {formatDate(dashboard.updated_at)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => deleteDashboard(dashboard.id)}
                          className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : (
          // Transforms Tab
          loadingTransforms ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
            </div>
          ) : filteredTransforms.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <Wand2 className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {search ? 'No transforms found' : 'No transform recipes yet'}
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                {search ? 'Try a different search term' : 'Create a transform recipe to prepare your data'}
              </p>
              {!search && (
                <Link
                  to="/transforms"
                  className="flex items-center gap-2 px-4 py-2 bg-indigo-700 text-white rounded-md hover:bg-indigo-800 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                  Create Transform
                </Link>
              )}
            </div>
          ) : viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredTransforms.map((transform) => (
                <div
                  key={transform.id}
                  className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 hover:shadow-lg hover:border-indigo-300 dark:hover:border-indigo-600 transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center">
                      <Wand2 className="w-6 h-6 text-indigo-500" />
                    </div>
                    <div className="flex items-center gap-1">
                      <Link
                        to="/transforms"
                        className="p-1.5 text-gray-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded transition-colors"
                      >
                        <Edit3 className="w-4 h-4" />
                      </Link>
                      <button
                        onClick={() => deleteTransform(transform.id)}
                        className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1 truncate">
                    {transform.name}
                  </h3>
                  {transform.description && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">
                      {transform.description}
                    </p>
                  )}

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                      <Table2 className="w-4 h-4" />
                      <span className="truncate">{transform.source_schema}.{transform.source_table}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1.5 px-2 py-0.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-full text-xs">
                        <Layers className="w-3 h-3" />
                        {transform.steps?.length || 0} steps
                      </span>
                      {transform.row_count !== null && (
                        <span className="text-gray-400 text-xs">
                          {transform.row_count.toLocaleString()} rows
                        </span>
                      )}
                    </div>
                  </div>

                  {transform.last_executed && (
                    <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center gap-1.5 text-xs text-gray-400">
                      <Clock className="w-3 h-3" />
                      Last run: {formatDate(transform.last_executed)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Source Table
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Steps
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Rows
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Updated
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredTransforms.map((transform) => (
                    <tr key={transform.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900 dark:text-white">
                          {transform.name}
                        </div>
                        {transform.description && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 truncate max-w-xs">
                            {transform.description}
                          </p>
                        )}
                      </td>
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                        {transform.source_table}
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-0.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded text-xs">
                          {transform.steps?.length || 0}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                        {transform.row_count?.toLocaleString() || '-'}
                      </td>
                      <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                        {formatDate(transform.updated_at)}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Link
                            to="/transforms"
                            className="p-1.5 text-gray-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded transition-colors"
                          >
                            <Edit3 className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => deleteTransform(transform.id)}
                            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>
    </div>
  )
}
