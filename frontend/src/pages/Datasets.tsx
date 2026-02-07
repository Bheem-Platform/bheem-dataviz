import { useState, useEffect } from 'react'
import {
  Database,
  Table2,
  ChevronRight,
  ChevronLeft,
  Loader2,
  RefreshCw,
  Columns,
  Rows,
  Clock,
  ArrowLeft,
  Search,
  Copy,
  ChevronsLeft,
  ChevronsRight,
} from 'lucide-react'
import { SiPostgresql, SiMysql, SiMongodb, SiSnowflake } from 'react-icons/si'
import { BiLogoGoogle } from 'react-icons/bi'
import { FaFileCsv, FaFileExcel } from 'react-icons/fa'
import { IconType } from 'react-icons'
import { api } from '../lib/api'

// API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

interface Connection {
  id: string
  name: string
  type: string
  host?: string
  port?: number
  database?: string
  username?: string
  status: string
  tables_count?: number
}

interface TableInfo {
  schema_name: string
  name: string
  type: string
}

interface ColumnInfo {
  name: string
  type: string
  nullable: boolean
  default: string | null
}

interface TablePreview {
  columns: string[]
  rows: Record<string, any>[]
  total: number
  preview_count: number
  execution_time: number
}

type ViewMode = 'connections' | 'tables' | 'data'

const connectionTypeIcons: Record<string, { icon: IconType; color: string }> = {
  postgresql: { icon: SiPostgresql, color: '#336791' },
  mysql: { icon: SiMysql, color: '#4479A1' },
  bigquery: { icon: BiLogoGoogle, color: '#4285F4' },
  snowflake: { icon: SiSnowflake, color: '#29B5E8' },
  csv: { icon: FaFileCsv, color: '#22C55E' },
  excel: { icon: FaFileExcel, color: '#217346' },
  mongodb: { icon: SiMongodb, color: '#47A248' },
}

export function Datasets() {
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<ViewMode>('connections')

  // Selected connection state
  const [selectedConnection, setSelectedConnection] = useState<Connection | null>(null)
  const [tables, setTables] = useState<TableInfo[]>([])
  const [tablesLoading, setTablesLoading] = useState(false)

  // Selected table state
  const [selectedTable, setSelectedTable] = useState<TableInfo | null>(null)
  const [columns, setColumns] = useState<ColumnInfo[]>([])
  const [preview, setPreview] = useState<TablePreview | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(100)

  // Search
  const [tableSearch, setTableSearch] = useState('')

  // Fetch connections on mount
  useEffect(() => {
    fetchConnections()
  }, [])

  const fetchConnections = async () => {
    try {
      setLoading(true)
      const response = await api.get('/connections/')
      const data = response.data
      // Only show connected databases
      setConnections(data.filter((c: Connection) => c.status === 'connected'))
    } catch (error) {
      console.error('Failed to fetch connections:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTables = async (connectionId: string) => {
    try {
      setTablesLoading(true)
      const response = await api.get(`/connections/${connectionId}/tables`)
      setTables(response.data)
    } catch (error) {
      console.error('Failed to fetch tables:', error)
    } finally {
      setTablesLoading(false)
    }
  }

  const fetchTableDetails = async (connectionId: string, schema: string, table: string, page: number = 1) => {
    try {
      setPreviewLoading(true)
      const offset = (page - 1) * pageSize

      if (page === 1) {
        // Fetch both columns and preview on first page
        const [columnsRes, previewRes] = await Promise.all([
          api.get(`/connections/${connectionId}/tables/${schema}/${table}/columns`),
          api.get(`/connections/${connectionId}/tables/${schema}/${table}/preview?limit=${pageSize}&offset=${offset}`)
        ])
        setColumns(columnsRes.data)
        setPreview(previewRes.data)
      } else {
        // Only fetch preview on subsequent pages
        const previewRes = await api.get(`/connections/${connectionId}/tables/${schema}/${table}/preview?limit=${pageSize}&offset=${offset}`)
        setPreview(previewRes.data)
      }

      setCurrentPage(page)
    } catch (error) {
      console.error('Failed to fetch table details:', error)
    } finally {
      setPreviewLoading(false)
    }
  }

  const selectConnection = (connection: Connection) => {
    setSelectedConnection(connection)
    setViewMode('tables')
    fetchTables(connection.id)
  }

  const selectTable = (table: TableInfo) => {
    if (!selectedConnection) return
    setSelectedTable(table)
    setCurrentPage(1)
    setViewMode('data')
    fetchTableDetails(selectedConnection.id, table.schema_name, table.name)
  }

  const goBack = () => {
    if (viewMode === 'data') {
      setViewMode('tables')
      setSelectedTable(null)
      setPreview(null)
      setColumns([])
      setCurrentPage(1)
    } else if (viewMode === 'tables') {
      setViewMode('connections')
      setSelectedConnection(null)
      setTables([])
    }
  }

  // Pagination helpers
  const totalPages = preview ? Math.ceil(preview.total / pageSize) : 1

  const goToPage = (page: number) => {
    if (!selectedConnection || !selectedTable || page < 1 || page > totalPages) return
    fetchTableDetails(selectedConnection.id, selectedTable.schema_name, selectedTable.name, page)
  }

  const filteredTables = tables.filter(t =>
    t.name.toLowerCase().includes(tableSearch.toLowerCase()) ||
    t.schema_name.toLowerCase().includes(tableSearch.toLowerCase())
  )

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const formatCellValue = (value: any): string => {
    if (value === null) return 'NULL'
    if (value === undefined) return ''
    if (typeof value === 'object') return JSON.stringify(value)
    return String(value)
  }

  // Connections View
  if (viewMode === 'connections') {
    return (
      <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-white to-indigo-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-950/20">
        {/* Header */}
        <div className="px-6 lg:px-8 py-6 border-b border-gray-200/60 dark:border-gray-700/60 bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto">
            {/* Title Row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                  <Database className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Datasets
                  </h1>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Browse your connected databases and explore data
                  </p>
                </div>
              </div>
              <button
                onClick={fetchConnections}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2.5 text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {loading ? (
              <div className="flex items-center justify-center h-80">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mx-auto mb-4 animate-pulse">
                    <Loader2 className="w-8 h-8 animate-spin text-white" />
                  </div>
                  <p className="text-gray-500 dark:text-gray-400">Loading databases...</p>
                </div>
              </div>
            ) : connections.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-80 text-center">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mb-6 shadow-lg shadow-purple-500/25">
                  <Database className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  No databases connected
                </h3>
                <p className="text-gray-500 dark:text-gray-400 max-w-md mb-8">
                  Connect a database first to browse and explore your data
                </p>
                <a
                  href="/connections"
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-all"
                >
                  Connect Database
                </a>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                {connections.map((connection) => (
                  <button
                    key={connection.id}
                    onClick={() => selectConnection(connection)}
                    className="group relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 text-left hover:shadow-2xl hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300 hover:-translate-y-1 flex flex-col h-full"
                  >
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                        {connectionTypeIcons[connection.type] ? (
                          (() => {
                            const IconComponent = connectionTypeIcons[connection.type].icon
                            return <IconComponent className="w-6 h-6 text-white" />
                          })()
                        ) : (
                          <Database className="w-6 h-6 text-white" />
                        )}
                      </div>
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-xs font-medium rounded-full">
                        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                        Connected
                      </span>
                    </div>

                    {/* Content */}
                    <div className="flex-1 mb-4">
                      <h3 className="font-semibold text-gray-900 dark:text-white text-base mb-1 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                        {connection.name}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 truncate mb-3">
                        {connection.database || connection.host}
                      </p>
                      {connection.tables_count !== undefined && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-xs font-medium rounded-md">
                          <Table2 className="w-3 h-3" />
                          {connection.tables_count} tables
                        </span>
                      )}
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700 mt-auto">
                      <span className="text-xs text-gray-400">Click to explore</span>
                      <ChevronRight className="w-5 h-5 text-gray-300 dark:text-gray-600 group-hover:text-indigo-500 group-hover:translate-x-1 transition-all" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Tables View
  if (viewMode === 'tables') {
    return (
      <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-white to-indigo-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-950/20">
        {/* Header */}
        <div className="px-6 lg:px-8 py-5 border-b border-gray-200/60 dark:border-gray-700/60 bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl">
          <div className="flex items-center gap-4 max-w-7xl mx-auto">
            <button
              onClick={goBack}
              className="p-2.5 hover:bg-white dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-500" />
            </button>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              {selectedConnection && connectionTypeIcons[selectedConnection.type] ? (
                (() => {
                  const IconComponent = connectionTypeIcons[selectedConnection.type].icon
                  return <IconComponent className="w-6 h-6 text-white" />
                })()
              ) : (
                <Database className="w-6 h-6 text-white" />
              )}
            </div>
            <div className="flex-1">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                {selectedConnection?.name}
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {tables.length} tables available
              </p>
            </div>
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search tables..."
                value={tableSearch}
                onChange={(e) => setTableSearch(e.target.value)}
                className="pl-10 pr-4 py-2.5 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
              />
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {tablesLoading ? (
              <div className="flex items-center justify-center h-80">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mx-auto mb-4 animate-pulse">
                    <Loader2 className="w-8 h-8 animate-spin text-white" />
                  </div>
                  <p className="text-gray-500 dark:text-gray-400">Loading tables...</p>
                </div>
              </div>
            ) : filteredTables.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-80 text-center">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mb-6 shadow-lg shadow-purple-500/25">
                  <Table2 className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {tableSearch ? 'No tables found' : 'No tables available'}
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  {tableSearch ? 'Try adjusting your search query' : 'This database has no accessible tables'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {filteredTables.map((table) => (
                  <button
                    key={`${table.schema_name}.${table.name}`}
                    onClick={() => selectTable(table)}
                    className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl border border-gray-200/60 dark:border-gray-700/60 p-5 text-left hover:shadow-xl hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-200 hover:-translate-y-0.5"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:scale-110 transition-transform">
                        <Table2 className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 dark:text-white truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                          {table.name}
                        </h3>
                        <p className="text-sm text-gray-400 truncate">
                          {table.schema_name} · {table.type.toLowerCase()}
                        </p>
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-indigo-500 group-hover:translate-x-0.5 transition-all flex-shrink-0" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Data Preview View
  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-white to-indigo-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-950/20">
      <header className="flex items-center gap-4 px-6 py-4 border-b border-gray-200/60 dark:border-gray-700/60 bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl">
        <button
          onClick={goBack}
          className="p-2 hover:bg-white dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-500" />
        </button>
        <div className="flex items-center gap-3 flex-1">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Table2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              {selectedTable?.name}
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {selectedTable?.schema_name} • {selectedConnection?.name}
            </p>
          </div>
        </div>
        {preview && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-sm rounded-lg">
              <Rows className="w-4 h-4" />
              <span>{preview.total.toLocaleString()} rows</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 text-sm rounded-lg">
              <Columns className="w-4 h-4" />
              <span>{columns.length} columns</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-sm rounded-lg">
              <Clock className="w-4 h-4" />
              <span>{preview.execution_time}s</span>
            </div>
          </div>
        )}
      </header>

      {previewLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mx-auto mb-4 animate-pulse">
              <Loader2 className="w-7 h-7 animate-spin text-white" />
            </div>
            <p className="text-gray-500 dark:text-gray-400">Loading data...</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex overflow-hidden">
          {/* Columns Sidebar */}
          <div className="w-64 border-r border-gray-200/60 dark:border-gray-700/60 bg-white/40 dark:bg-gray-800/40 backdrop-blur-sm flex flex-col">
            <div className="p-4 border-b border-gray-200/60 dark:border-gray-700/60 bg-gradient-to-r from-indigo-50/50 to-purple-50/50 dark:from-indigo-900/20 dark:to-purple-900/20">
              <h3 className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                <Columns className="w-4 h-4 text-indigo-500" />
                Columns ({columns.length})
              </h3>
            </div>
            <div className="flex-1 overflow-auto p-2">
              {columns.map((col) => (
                <div
                  key={col.name}
                  className="flex items-center gap-2 p-2.5 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 group transition-colors"
                >
                  <span
                    className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      col.type.includes('int') || col.type.includes('numeric') || col.type.includes('decimal')
                        ? 'bg-emerald-400'
                        : col.type.includes('time') || col.type.includes('date')
                        ? 'bg-amber-400'
                        : col.type.includes('bool')
                        ? 'bg-purple-400'
                        : 'bg-indigo-400'
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {col.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {col.type}
                      {col.nullable && ' • nullable'}
                    </p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(col.name)}
                    className="p-1.5 opacity-0 group-hover:opacity-100 hover:bg-indigo-100 dark:hover:bg-indigo-800/50 rounded-lg transition-all"
                  >
                    <Copy className="w-3 h-3 text-indigo-500" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Data Table */}
          <div className="flex-1 overflow-auto bg-white/60 dark:bg-gray-900/40">
            {preview && preview.rows.length > 0 ? (
              <table className="w-full text-sm">
                <thead className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 sticky top-0">
                  <tr>
                    {preview.columns.map((col) => (
                      <th
                        key={col}
                        className="px-4 py-3 text-left text-gray-700 dark:text-gray-200 font-medium border-b border-gray-200/60 dark:border-gray-700/60 whitespace-nowrap"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.rows.map((row, i) => (
                    <tr
                      key={i}
                      className="border-b border-gray-100 dark:border-gray-800 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/20 transition-colors"
                    >
                      {preview.columns.map((col) => (
                        <td
                          key={col}
                          className="px-4 py-2.5 text-gray-900 dark:text-gray-100 max-w-xs truncate"
                          title={formatCellValue(row[col])}
                        >
                          <span className={row[col] === null ? 'text-gray-400 italic' : ''}>
                            {formatCellValue(row[col])}
                          </span>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="flex flex-col items-center justify-center h-full">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mb-4 shadow-lg shadow-purple-500/25">
                  <Table2 className="w-8 h-8 text-white" />
                </div>
                <p className="text-gray-500 dark:text-gray-400">No data in this table</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer with pagination */}
      {preview && preview.rows.length > 0 && (
        <div className="px-6 py-3 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border-t border-gray-200/60 dark:border-gray-700/60 flex items-center justify-between">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Showing {((currentPage - 1) * pageSize) + 1} - {Math.min(currentPage * pageSize, preview.total)} of {preview.total.toLocaleString()} rows
          </div>

          {totalPages > 1 && (
            <div className="flex items-center gap-1">
              <button
                onClick={() => goToPage(1)}
                disabled={currentPage === 1 || previewLoading}
                className="p-2 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="First page"
              >
                <ChevronsLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1 || previewLoading}
                className="p-2 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Previous page"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <span className="px-4 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg mx-1">
                Page {currentPage} of {totalPages.toLocaleString()}
              </span>

              <button
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages || previewLoading}
                className="p-2 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Next page"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => goToPage(totalPages)}
                disabled={currentPage === totalPages || previewLoading}
                className="p-2 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Last page"
              >
                <ChevronsRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
