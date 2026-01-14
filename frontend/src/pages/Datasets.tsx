import { Plus, Search, Table2, MoreHorizontal } from 'lucide-react'

export function Datasets() {
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Datasets
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Define your data models and semantic layer
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
          <Plus className="w-5 h-5" />
          New Dataset
        </button>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center mb-4">
            <Table2 className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No datasets yet
          </h3>
          <p className="text-gray-500 dark:text-gray-400 max-w-md mb-6">
            Create a dataset to define your data model with tables, columns, measures, and relationships.
          </p>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
            <Plus className="w-5 h-5" />
            Create Dataset
          </button>
        </div>
      </div>
    </div>
  )
}
