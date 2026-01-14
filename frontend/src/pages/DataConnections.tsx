import { useState } from 'react'
import { Plus, Database, Search, MoreHorizontal, CheckCircle, XCircle } from 'lucide-react'

const connectionTypes = [
  { id: 'postgresql', name: 'PostgreSQL', icon: '🐘' },
  { id: 'mysql', name: 'MySQL', icon: '🐬' },
  { id: 'bigquery', name: 'BigQuery', icon: '🔷' },
  { id: 'snowflake', name: 'Snowflake', icon: '❄️' },
  { id: 'csv', name: 'CSV File', icon: '📄' },
  { id: 'excel', name: 'Excel', icon: '📊' },
  { id: 'api', name: 'REST API', icon: '🔌' },
  { id: 'mongodb', name: 'MongoDB', icon: '🍃' },
]

const mockConnections = [
  {
    id: '1',
    name: 'Production Database',
    type: 'postgresql',
    status: 'connected',
    tables: 24,
    lastUsed: '2024-01-15',
  },
  {
    id: '2',
    name: 'Analytics Warehouse',
    type: 'bigquery',
    status: 'connected',
    tables: 156,
    lastUsed: '2024-01-15',
  },
  {
    id: '3',
    name: 'Sales Data',
    type: 'csv',
    status: 'error',
    tables: 1,
    lastUsed: '2024-01-10',
  },
]

export function DataConnections() {
  const [showNewConnection, setShowNewConnection] = useState(false)
  const [search, setSearch] = useState('')

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Data Connections
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Connect to your databases and data sources
          </p>
        </div>
        <button
          onClick={() => setShowNewConnection(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Plus className="w-5 h-5" />
          New Connection
        </button>
      </header>

      {/* Search */}
      <div className="px-6 py-3 bg-gray-50 dark:bg-gray-800/50">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search connections..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2 w-full border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Connections List */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid gap-4">
          {mockConnections.map((connection) => {
            const typeInfo = connectionTypes.find((t) => t.id === connection.type)
            return (
              <div
                key={connection.id}
                className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-2xl">
                    {typeInfo?.icon || '📊'}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      {connection.name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {typeInfo?.name} • {connection.tables} tables
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    {connection.status === 'connected' ? (
                      <>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-green-600 dark:text-green-400">
                          Connected
                        </span>
                      </>
                    ) : (
                      <>
                        <XCircle className="w-4 h-4 text-red-500" />
                        <span className="text-sm text-red-600 dark:text-red-400">
                          Error
                        </span>
                      </>
                    )}
                  </div>

                  <span className="text-sm text-gray-400">
                    Last used {connection.lastUsed}
                  </span>

                  <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                    <MoreHorizontal className="w-5 h-5 text-gray-400" />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* New Connection Modal */}
      {showNewConnection && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                New Connection
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Select a data source type to connect
              </p>
            </div>

            <div className="p-6 overflow-auto">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {connectionTypes.map((type) => (
                  <button
                    key={type.id}
                    className="flex flex-col items-center gap-2 p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
                  >
                    <span className="text-3xl">{type.icon}</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {type.name}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
              <button
                onClick={() => setShowNewConnection(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
