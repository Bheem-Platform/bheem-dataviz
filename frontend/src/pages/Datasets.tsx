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

// Use VITE_API_URL in production, fallback to relative URL for dev proxy
const API_BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1'

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
      const response = await fetch(`${API_BASE_URL}/connections/`)
      if (response.ok) {
        const data = await response.json()
        // Only show connected databases
        setConnections(data.filter((c: Connection) => c.status === 'connected'))
      }
    } catch (error) {
      console.error('Failed to fetch connections:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTables = async (connectionId: string) => {
    try {
      setTablesLoading(true)
      const response = await fetch(`${API_BASE_URL}/connections/${connectionId}/tables`)
      if (response.ok) {
        const data = await response.json()
        setTables(data)
      }
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

      // Fetch columns only on first page, preview always
      const requests: Promise<Response>[] = [
        fetch(`${API_BASE_URL}/connections/${connectionId}/tables/${schema}/${table}/preview?limit=${pageSize}&offset=${offset}`)
      ]

      // Only fetch columns on first page
      if (page === 1) {
        requests.unshift(
          fetch(`${API_BASE_URL}/connections/${connectionId}/tables/${schema}/${table}/columns`)
        )
      }

      const responses = await Promise.all(requests)

      if (page === 1) {
        const [columnsRes, previewRes] = responses
        if (columnsRes.ok) {
          const columnsData = await columnsRes.json()
          setColumns(columnsData)
        }
        if (previewRes.ok) {
          const previewData = await previewRes.json()
          setPreview(previewData)
        }
      } else {
        const [previewRes] = responses
        if (previewRes.ok) {
          const previewData = await previewRes.json()
          setPreview(previewData)
        }
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
      <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <header className="px-8 py-6 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div className="w-10 h-10 rounded-md bg-primary-500 flex items-center justify-center">
                  <Database className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Datasets
                </h1>
              </div>
              <p className="text-gray-500 dark:text-gray-400 ml-13">
                Browse your connected databases and explore data
              </p>
            </div>
            <button
              onClick={fetchConnections}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2.5 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-8">
          <div className="max-w-7xl mx-auto">
            {loading ? (
              <div className="flex items-center justify-center h-80">
                <div className="text-center">
                  <Loader2 className="w-10 h-10 animate-spin text-emerald-500 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">Loading databases...</p>
                </div>
              </div>
            ) : connections.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-80 text-center">
                <div className="w-20 h-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-6">
                  <Database className="w-10 h-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  No databases connected
                </h3>
                <p className="text-gray-500 dark:text-gray-400 max-w-md mb-8">
                  Connect a database first to browse and explore your data
                </p>
                <a
                  href="/connections"
                  className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl font-medium hover:opacity-90 transition-opacity"
                >
                  Connect Database
                </a>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {connections.map((connection) => (
                  <button
                    key={connection.id}
                    onClick={() => selectConnection(connection)}
                    className="group relative bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 text-left hover:shadow-xl hover:shadow-primary-500/10 hover:border-primary-500 dark:hover:border-emerald-600 transition-all duration-300"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-14 rounded-xl bg-primary-500/20 dark:from-emerald-900/30 dark:to-teal-900/30 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                        {connectionTypeIcons[connection.type] ? (
                          (() => {
                            const IconComponent = connectionTypeIcons[connection.type].icon
                            return <IconComponent className="w-8 h-8" style={{ color: connectionTypeIcons[connection.type].color }} />
                          })()
                        ) : (
                          <Database className="w-8 h-8 text-gray-400" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 dark:text-white text-lg mb-1 truncate group-hover:text-primary-500 dark:group-hover:text-primary-500 transition-colors">
                          {connection.name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400 truncate mb-3">
                          {connection.database || connection.host}
                        </p>
                        <div className="flex items-center gap-3">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-primary-500/30 dark:bg-green-900/30 text-white dark:text-green-400 text-xs font-medium rounded-full">
                            <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
                            Connected
                          </span>
                          {connection.tables_count !== undefined && (
                            <span className="text-xs text-gray-400">
                              {connection.tables_count} tables
                            </span>
                          )}
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-300 dark:text-gray-600 group-hover:text-emerald-500 group-hover:translate-x-1 transition-all mt-1" />
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
      <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <header className="px-8 py-5 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-4 max-w-7xl mx-auto">
            <button
              onClick={goBack}
              className="p-2.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-500" />
            </button>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center">
              {selectedConnection && connectionTypeIcons[selectedConnection.type] ? (
                (() => {
                  const IconComponent = connectionTypeIcons[selectedConnection.type].icon
                  return <IconComponent className="w-7 h-7" style={{ color: connectionTypeIcons[selectedConnection.type].color }} />
                })()
              ) : (
                <Database className="w-7 h-7 text-gray-400" />
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
                className="pl-10 pr-4 py-2.5 w-64 bg-gray-100 dark:bg-gray-700 border-0 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-8">
          <div className="max-w-7xl mx-auto">
            {tablesLoading ? (
              <div className="flex items-center justify-center h-80">
                <div className="text-center">
                  <Loader2 className="w-10 h-10 animate-spin text-indigo-500 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">Loading tables...</p>
                </div>
              </div>
            ) : filteredTables.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-80 text-center">
                <div className="w-20 h-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-6">
                  <Table2 className="w-10 h-10 text-gray-400" />
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
                    className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 text-left hover:shadow-lg hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-200"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Table2 className="w-6 h-6 text-blue-500" />
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
    <div className="h-full flex flex-col">
      <header className="flex items-center gap-4 px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <button
          onClick={goBack}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
        >
          <ArrowLeft className="w-5 h-5 text-gray-500" />
        </button>
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center">
            <Table2 className="w-5 h-5 text-blue-500" />
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
          <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-1">
              <Rows className="w-4 h-4" />
              <span>{preview.total.toLocaleString()} rows</span>
            </div>
            <div className="flex items-center gap-1">
              <Columns className="w-4 h-4" />
              <span>{columns.length} columns</span>
            </div>
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>{preview.execution_time}s</span>
            </div>
          </div>
        )}
      </header>

      {previewLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : (
        <div className="flex-1 flex overflow-hidden">
          {/* Columns Sidebar */}
          <div className="w-64 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex flex-col">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                <Columns className="w-4 h-4" />
                Columns ({columns.length})
              </h3>
            </div>
            <div className="flex-1 overflow-auto p-2">
              {columns.map((col) => (
                <div
                  key={col.name}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 group"
                >
                  <span
                    className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      col.type.includes('int') || col.type.includes('numeric') || col.type.includes('decimal')
                        ? 'bg-green-400'
                        : col.type.includes('time') || col.type.includes('date')
                        ? 'bg-yellow-400'
                        : col.type.includes('bool')
                        ? 'bg-purple-400'
                        : 'bg-blue-400'
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
                    className="p-1 opacity-0 group-hover:opacity-100 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                  >
                    <Copy className="w-3 h-3 text-gray-400" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Data Table */}
          <div className="flex-1 overflow-auto">
            {preview && preview.rows.length > 0 ? (
              <table className="w-full text-sm">
                <thead className="bg-gray-100 dark:bg-gray-800 sticky top-0">
                  <tr>
                    {preview.columns.map((col) => (
                      <th
                        key={col}
                        className="px-4 py-3 text-left text-gray-600 dark:text-gray-300 font-medium border-b border-gray-200 dark:border-gray-700 whitespace-nowrap"
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
                      className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                    >
                      {preview.columns.map((col) => (
                        <td
                          key={col}
                          className="px-4 py-2 text-gray-900 dark:text-gray-100 max-w-xs truncate"
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
              <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400">
                <Table2 className="w-12 h-12 mb-4" />
                <p>No data in this table</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer with pagination */}
      {preview && preview.rows.length > 0 && (
        <div className="px-6 py-3 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Showing {((currentPage - 1) * pageSize) + 1} - {Math.min(currentPage * pageSize, preview.total)} of {preview.total.toLocaleString()} rows
          </div>

          {totalPages > 1 && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => goToPage(1)}
                disabled={currentPage === 1 || previewLoading}
                className="p-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                title="First page"
              >
                <ChevronsLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1 || previewLoading}
                className="p-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Previous page"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <span className="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                Page {currentPage} of {totalPages.toLocaleString()}
              </span>

              <button
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages || previewLoading}
                className="p-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Next page"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => goToPage(totalPages)}
                disabled={currentPage === totalPages || previewLoading}
                className="p-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
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
