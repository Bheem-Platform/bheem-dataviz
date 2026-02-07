import React, { useState, useEffect } from 'react'
import {
  Database,
  Plus,
  Trash2,
  Edit3,
  Loader2,
  ArrowLeft,
  Link2,
  Calculator,
  Columns,
  Table2,
  Save,
  X,
  ChevronDown,
  ChevronRight,
  Layers,
  GitBranch,
  Play,
  Eye,
  Code,
  Wand2,
} from 'lucide-react'
import { api } from '../lib/api'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

// Types
interface Connection {
  id: string
  name: string
  type: string
  status: string
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
}

interface TransformRecipe {
  id: string
  name: string
  description?: string
  connection_id: string
  source_table: string
  source_schema: string
  result_columns?: { name: string; type: string }[]
}

interface MeasureResponse {
  id: string
  name: string
  description?: string
  column_name: string
  expression: string
  aggregation: string
  display_format?: string
}

interface DimensionResponse {
  id: string
  name: string
  description?: string
  column_name: string
  display_format?: string
}

interface JoinResponse {
  id: string
  name?: string
  target_schema: string
  target_table: string
  target_alias?: string
  join_type: string
  join_condition: string
}

interface JoinedTransform {
  transform_id: string
  transform_name?: string
  alias: string
  join_type: string
  join_on: { left: string; right: string }[]
}

interface SemanticModel {
  id: string
  name: string
  description?: string
  connection_id: string
  transform_id?: string
  transform_name?: string
  schema_name?: string
  table_name?: string
  joined_transforms?: JoinedTransform[]
  is_active: boolean
  measures: MeasureResponse[]
  dimensions: DimensionResponse[]
  joins: JoinResponse[]
  created_at?: string
  updated_at?: string
}

interface SemanticModelSummary {
  id: string
  name: string
  description?: string
  connection_id: string
  transform_id?: string
  transform_name?: string
  schema_name?: string
  table_name?: string
  measures_count: number
  dimensions_count: number
  joins_count: number
  created_at?: string
}

type SourceType = 'transform' | 'table'

type ViewMode = 'list' | 'editor'

const AGG_OPTIONS = [
  { value: 'sum', label: 'Sum' },
  { value: 'count', label: 'Count' },
  { value: 'count_distinct', label: 'Count Distinct' },
  { value: 'avg', label: 'Average' },
  { value: 'min', label: 'Minimum' },
  { value: 'max', label: 'Maximum' },
]

const JOIN_TYPES = [
  { value: 'left', label: 'Left Join' },
  { value: 'inner', label: 'Inner Join' },
  { value: 'right', label: 'Right Join' },
  { value: 'full', label: 'Full Join' },
]

export function SemanticModels() {
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [models, setModels] = useState<SemanticModelSummary[]>([])
  const [connections, setConnections] = useState<Connection[]>([])
  const [transforms, setTransforms] = useState<TransformRecipe[]>([])
  const [loading, setLoading] = useState(true)

  // Editor state
  const [editingModel, setEditingModel] = useState<SemanticModel | null>(null)
  const [selectedConnection, setSelectedConnection] = useState<Connection | null>(null)
  const [tables, setTables] = useState<TableInfo[]>([])
  const [columns, setColumns] = useState<ColumnInfo[]>([])
  const [loadingTables, setLoadingTables] = useState(false)
  const [loadingColumns, setLoadingColumns] = useState(false)

  // Form state
  const [modelName, setModelName] = useState('')
  const [modelDescription, setModelDescription] = useState('')
  const [sourceType, setSourceType] = useState<SourceType>('transform')
  const [selectedTransform, setSelectedTransform] = useState<TransformRecipe | null>(null)
  const [selectedTable, setSelectedTable] = useState('')
  const [selectedSchema, setSelectedSchema] = useState('public')
  const [saving, setSaving] = useState(false)

  // Expanded sections
  const [expandedSections, setExpandedSections] = useState({
    measures: true,
    dimensions: true,
    joins: false,
  })

  // Add measure modal
  const [showMeasureModal, setShowMeasureModal] = useState(false)
  const [newMeasure, setNewMeasure] = useState({ name: '', column_name: '', aggregation: 'sum', description: '' })

  // Add dimension modal
  const [showDimensionModal, setShowDimensionModal] = useState(false)
  const [newDimension, setNewDimension] = useState({ name: '', column_name: '', description: '' })

  // Add join modal
  const [showJoinModal, setShowJoinModal] = useState(false)
  const [joinSourceType, setJoinSourceType] = useState<'table' | 'transform'>('transform')
  const [newJoin, setNewJoin] = useState({ from_column: '', to_table: '', to_transform_id: '', to_column: '', join_type: 'left' })
  const [joinTableColumns, setJoinTableColumns] = useState<ColumnInfo[]>([])

  // Preview state
  const [previewMeasureIds, setPreviewMeasureIds] = useState<string[]>([])
  const [previewDimensionIds, setPreviewDimensionIds] = useState<string[]>([])
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewData, setPreviewData] = useState<{
    columns: string[]
    rows: Record<string, unknown>[]
    total_rows: number
    sql_generated: string
    execution_time_ms: number
  } | null>(null)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [showPreviewSection, setShowPreviewSection] = useState(true)

  useEffect(() => {
    fetchModels()
    fetchConnections()
    fetchTransforms()
  }, [])

  useEffect(() => {
    if (selectedConnection) {
      fetchTables(selectedConnection.id)
    }
  }, [selectedConnection])

  useEffect(() => {
    if (selectedConnection && selectedTable) {
      fetchColumns(selectedConnection.id, selectedSchema, selectedTable)
    }
  }, [selectedConnection, selectedTable, selectedSchema])

  const fetchModels = async () => {
    try {
      const response = await api.get('/models/')
      setModels(response.data)
    } catch (error) {
      console.error('Failed to fetch models:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchConnections = async () => {
    try {
      const response = await api.get('/connections/')
      const data = response.data
      setConnections(data.filter((c: Connection) => c.status === 'connected'))
    } catch (error) {
      console.error('Failed to fetch connections:', error)
    }
  }

  const fetchTransforms = async () => {
    try {
      const response = await api.get('/transforms/')
      setTransforms(response.data)
    } catch (error) {
      console.error('Failed to fetch transforms:', error)
    }
  }

  const fetchTransformColumns = async (transformId: string) => {
    setLoadingColumns(true)
    try {
      // Execute transform with limit 1 to get column info
      const response = await api.post(`/transforms/${transformId}/execute?limit=1`)
      const data = response.data
      // Convert column objects to ColumnInfo format
      const cols: ColumnInfo[] = (data.columns || []).map((col: any) => ({
        name: typeof col === 'string' ? col : col.name,
        type: typeof col === 'string' ? 'unknown' : (col.type || 'unknown'),
        nullable: true
      }))
      setColumns(cols)
    } catch (error) {
      console.error('Failed to fetch transform columns:', error)
    } finally {
      setLoadingColumns(false)
    }
  }

  const fetchTables = async (connectionId: string) => {
    setLoadingTables(true)
    try {
      const response = await api.get(`/connections/${connectionId}/tables`)
      setTables(response.data)
    } catch (error) {
      console.error('Failed to fetch tables:', error)
    } finally {
      setLoadingTables(false)
    }
  }

  const fetchColumns = async (connectionId: string, schema: string, table: string) => {
    setLoadingColumns(true)
    try {
      const response = await api.get(`/connections/${connectionId}/tables/${schema}/${table}/columns`)
      setColumns(response.data)
    } catch (error) {
      console.error('Failed to fetch columns:', error)
    } finally {
      setLoadingColumns(false)
    }
  }

  const startNewModel = () => {
    setEditingModel(null)
    setModelName('')
    setModelDescription('')
    setSourceType('transform')
    setSelectedTransform(null)
    setSelectedConnection(null)
    setSelectedTable('')
    setSelectedSchema('public')
    setColumns([])
    clearPreview()
    setViewMode('editor')
  }

  const editModel = async (modelId: string) => {
    try {
      const response = await api.get(`/models/${modelId}`)
      const model = response.data
      setEditingModel(model)
      setModelName(model.name)
      setModelDescription(model.description || '')
      clearPreview()

      // Set source type and related fields
      if (model.transform_id) {
        setSourceType('transform')
        const transform = transforms.find(t => t.id === model.transform_id)
        setSelectedTransform(transform || null)
        if (transform) {
          fetchTransformColumns(transform.id)
        }
        setSelectedTable('')
        setSelectedSchema('')
      } else {
        setSourceType('table')
        setSelectedTransform(null)
        setSelectedTable(model.table_name || '')
        setSelectedSchema(model.schema_name || 'public')
      }

      // Set connection
      const conn = connections.find(c => c.id === model.connection_id)
      if (conn) {
        setSelectedConnection(conn)
      }

      setViewMode('editor')
    } catch (error) {
      console.error('Failed to fetch model:', error)
    }
  }

  const deleteModel = async (modelId: string) => {
    if (!confirm('Are you sure you want to delete this model?')) return

    try {
      await api.delete(`/models/${modelId}`)
      fetchModels()
    } catch (error) {
      console.error('Failed to delete model:', error)
    }
  }

  const saveModel = async () => {
    // Validate based on source type
    if (!modelName) {
      alert('Please enter a model name')
      return
    }

    if (sourceType === 'transform' && !selectedTransform) {
      alert('Please select a transform')
      return
    }

    if (sourceType === 'table' && (!selectedConnection || !selectedTable)) {
      alert('Please select a connection and table')
      return
    }

    setSaving(true)
    try {
      if (editingModel) {
        // Update existing model
        await api.put(`/models/${editingModel.id}`, { name: modelName, description: modelDescription })
      } else {
        // Create new model
        const connectionId = sourceType === 'transform'
          ? selectedTransform!.connection_id
          : selectedConnection!.id

        const body = sourceType === 'transform'
          ? {
              name: modelName,
              description: modelDescription,
              connection_id: connectionId,
              transform_id: selectedTransform!.id
            }
          : {
              name: modelName,
              description: modelDescription,
              connection_id: connectionId,
              schema_name: selectedSchema,
              table_name: selectedTable
            }

        const response = await api.post('/models/', body)
        const newModel = response.data
        setEditingModel(newModel)
      }

      fetchModels()
    } catch (error) {
      console.error('Failed to save model:', error)
      alert('Failed to save model')
    } finally {
      setSaving(false)
    }
  }

  const addMeasure = async () => {
    if (!editingModel || !newMeasure.name || !newMeasure.column_name) return

    try {
      const response = await api.post(`/models/${editingModel.id}/measures`, newMeasure)
      const updated = response.data
      setEditingModel(updated)
      setShowMeasureModal(false)
      setNewMeasure({ name: '', column_name: '', aggregation: 'sum', description: '' })
    } catch (error) {
      console.error('Failed to add measure:', error)
    }
  }

  const removeMeasure = async (measureId: string) => {
    if (!editingModel) return

    try {
      const response = await api.delete(`/models/${editingModel.id}/measures/${measureId}`)
      const updated = response.data
      setEditingModel(updated)
    } catch (error) {
      console.error('Failed to remove measure:', error)
    }
  }

  const addDimension = async () => {
    if (!editingModel || !newDimension.name || !newDimension.column_name) return

    try {
      const response = await api.post(`/models/${editingModel.id}/dimensions`, newDimension)
      const updated = response.data
      setEditingModel(updated)
      setShowDimensionModal(false)
      setNewDimension({ name: '', column_name: '', description: '' })
    } catch (error) {
      console.error('Failed to add dimension:', error)
    }
  }

  const removeDimension = async (dimensionId: string) => {
    if (!editingModel) return

    try {
      const response = await api.delete(`/models/${editingModel.id}/dimensions/${dimensionId}`)
      const updated = response.data
      setEditingModel(updated)
    } catch (error) {
      console.error('Failed to remove dimension:', error)
    }
  }

  const fetchJoinTableColumns = async (tableName: string) => {
    if (!selectedConnection) return

    try {
      const response = await api.get(`/connections/${selectedConnection.id}/tables/${selectedSchema}/${tableName}/columns`)
      setJoinTableColumns(response.data)
    } catch (error) {
      console.error('Failed to fetch columns:', error)
    }
  }

  const fetchJoinTransformColumns = async (transformId: string) => {
    try {
      const response = await api.post(`/transforms/${transformId}/execute?limit=1`)
      const data = response.data
      const cols: ColumnInfo[] = (data.columns || []).map((col: any) => ({
        name: typeof col === 'string' ? col : col.name,
        type: typeof col === 'string' ? 'unknown' : (col.type || 'unknown'),
        nullable: true
      }))
      setJoinTableColumns(cols)
    } catch (error) {
      console.error('Failed to fetch transform columns:', error)
    }
  }

  const addJoin = async () => {
    if (!editingModel || !newJoin.from_column || !newJoin.to_column) return

    // Validate based on join source type
    if (joinSourceType === 'table' && !newJoin.to_table) return
    if (joinSourceType === 'transform' && !newJoin.to_transform_id) return

    try {
      const body = joinSourceType === 'transform'
        ? {
            from_column: newJoin.from_column,
            to_transform_id: newJoin.to_transform_id,
            to_column: newJoin.to_column,
            join_type: newJoin.join_type
          }
        : {
            from_table: editingModel.table_name,
            from_column: newJoin.from_column,
            to_table: newJoin.to_table,
            to_column: newJoin.to_column,
            join_type: newJoin.join_type
          }

      const response = await api.post(`/models/${editingModel.id}/joins`, body)
      const updated = response.data
      setEditingModel(updated)
      setShowJoinModal(false)
      setNewJoin({ from_column: '', to_table: '', to_transform_id: '', to_column: '', join_type: 'left' })
      setJoinTableColumns([])
      setJoinSourceType('transform')
    } catch (error) {
      console.error('Failed to add join:', error)
    }
  }

  const removeJoin = async (joinId: string) => {
    if (!editingModel) return

    try {
      const response = await api.delete(`/models/${editingModel.id}/joins/${joinId}`)
      const updated = response.data
      setEditingModel(updated)
    } catch (error) {
      console.error('Failed to remove join:', error)
    }
  }

  const toggleSection = (section: 'measures' | 'dimensions' | 'joins') => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }))
  }

  const togglePreviewMeasure = (measureId: string) => {
    setPreviewMeasureIds(prev =>
      prev.includes(measureId) ? prev.filter(id => id !== measureId) : [...prev, measureId]
    )
  }

  const togglePreviewDimension = (dimensionId: string) => {
    setPreviewDimensionIds(prev =>
      prev.includes(dimensionId) ? prev.filter(id => id !== dimensionId) : [...prev, dimensionId]
    )
  }

  const fetchPreview = async () => {
    if (!editingModel) return
    if (previewMeasureIds.length === 0 && previewDimensionIds.length === 0) {
      setPreviewError('Please select at least one measure or dimension')
      return
    }

    setPreviewLoading(true)
    setPreviewError(null)
    setPreviewData(null)

    try {
      const response = await api.post(`/models/${editingModel.id}/preview`, {
        measure_ids: previewMeasureIds,
        dimension_ids: previewDimensionIds,
        limit: 100
      })
      const data = response.data
      setPreviewData(data)
    } catch (error: any) {
      console.error('Failed to fetch preview:', error)
      setPreviewError(error.response?.data?.detail || 'Failed to fetch preview')
    } finally {
      setPreviewLoading(false)
    }
  }

  const clearPreview = () => {
    setPreviewMeasureIds([])
    setPreviewDimensionIds([])
    setPreviewData(null)
    setPreviewError(null)
  }

  // ============================================================================
  // LIST VIEW
  // ============================================================================
  if (viewMode === 'list') {
    return (
      <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-white to-indigo-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-950/20">
        {/* Header */}
        <div className="px-6 lg:px-8 py-6 border-b border-gray-200/60 dark:border-gray-700/60 bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto">
            {/* Title Row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                  <Layers className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Semantic Models
                  </h1>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Define data models with measures, dimensions, and relationships
                  </p>
                </div>
              </div>
              <button
                onClick={startNewModel}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-all"
              >
                <Plus className="w-5 h-5" />
                New Model
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mx-auto mb-4 animate-pulse">
                    <Loader2 className="w-8 h-8 animate-spin text-white" />
                  </div>
                  <p className="text-gray-500 dark:text-gray-400">Loading models...</p>
                </div>
              </div>
            ) : models.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-center">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mb-6 shadow-lg shadow-purple-500/25">
                  <Layers className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  No semantic models yet
                </h3>
                <p className="text-gray-500 dark:text-gray-400 max-w-md mb-6">
                  Create a semantic model to define measures, dimensions, and table relationships for your data
                </p>
                <button
                  onClick={startNewModel}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 transition-all"
                >
                  <Plus className="w-5 h-5" />
                  Create Model
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                {models.map((model) => {
                  const conn = connections.find(c => c.id === model.connection_id)
                  return (
                    <div
                      key={model.id}
                      className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 p-5 hover:shadow-2xl hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300 hover:-translate-y-1 flex flex-col h-full"
                    >
                      {/* Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:scale-110 transition-transform duration-300">
                          <Layers className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => editModel(model.id)}
                            className="p-2 text-gray-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-colors"
                            title="Edit"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deleteModel(model.id)}
                            className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* Content */}
                      <div className="flex-1 mb-4">
                        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                          {model.name}
                        </h3>

                        {model.description && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">
                            {model.description}
                          </p>
                        )}

                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                            <Database className="w-4 h-4 text-indigo-500" />
                            <span className="truncate">{conn?.name || 'Unknown'}</span>
                          </div>
                          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                            {model.transform_id ? (
                              <>
                                <Wand2 className="w-4 h-4 text-purple-500" />
                                <span className="truncate">{model.transform_name || 'Transform'}</span>
                              </>
                            ) : (
                              <>
                                <Table2 className="w-4 h-4 text-purple-500" />
                                <span className="truncate">{model.schema_name}.{model.table_name}</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Footer */}
                      <div className="flex items-center gap-2 flex-wrap pt-3 border-t border-gray-100 dark:border-gray-700 mt-auto">
                        <span className="flex items-center gap-1.5 px-2 py-0.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-md text-xs font-medium">
                          <Calculator className="w-3 h-3" />
                          {model.measures_count}
                        </span>
                        <span className="flex items-center gap-1.5 px-2 py-0.5 bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-md text-xs font-medium">
                          <Columns className="w-3 h-3" />
                          {model.dimensions_count}
                        </span>
                        {model.joins_count > 0 && (
                          <span className="flex items-center gap-1.5 px-2 py-0.5 bg-fuchsia-50 dark:bg-fuchsia-900/30 text-fuchsia-600 dark:text-fuchsia-400 rounded-md text-xs font-medium">
                            <Link2 className="w-3 h-3" />
                            {model.joins_count}
                          </span>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // ============================================================================
  // EDITOR VIEW
  // ============================================================================
  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-white to-indigo-50/30 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-950/20">
      {/* Header */}
      <header className="px-6 py-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl border-b border-gray-200/60 dark:border-gray-700/60 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setViewMode('list')}
            className="p-2 text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-white dark:hover:bg-gray-700 border border-transparent hover:border-indigo-200 dark:hover:border-indigo-700 rounded-xl transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              {editingModel ? 'Edit Model' : 'New Semantic Model'}
            </h1>
            <p className="text-sm text-gray-500">{editingModel?.name || 'Configure your data model'}</p>
          </div>
        </div>
        <button
          onClick={saveModel}
          disabled={saving || !modelName || (sourceType === 'transform' ? !selectedTransform : (!selectedConnection || !selectedTable))}
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-500/25 disabled:opacity-50 transition-all"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {editingModel ? 'Save Changes' : 'Create Model'}
        </button>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Model Configuration */}
        <div className="w-80 border-r border-gray-200/60 dark:border-gray-700/60 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm overflow-y-auto p-5 space-y-6">
          {/* Basic Info */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Model Name *</label>
            <input
              type="text"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              placeholder="e.g., Sales Analytics"
              className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
            <textarea
              value={modelDescription}
              onChange={(e) => setModelDescription(e.target.value)}
              placeholder="Describe what this model is for..."
              rows={2}
              className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
            />
          </div>

          {/* Source Type Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Data Source *</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => {
                  if (!editingModel) {
                    setSourceType('transform')
                    setSelectedConnection(null)
                    setSelectedTable('')
                    setColumns([])
                  }
                }}
                disabled={!!editingModel}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl border transition-all ${
                  sourceType === 'transform'
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 shadow-sm'
                    : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-indigo-300'
                } ${editingModel ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Wand2 className="w-4 h-4" />
                <span className="text-sm font-medium">Transform</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  if (!editingModel) {
                    setSourceType('table')
                    setSelectedTransform(null)
                    setColumns([])
                  }
                }}
                disabled={!!editingModel}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl border transition-all ${
                  sourceType === 'table'
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 shadow-sm'
                    : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-indigo-300'
                } ${editingModel ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Table2 className="w-4 h-4" />
                <span className="text-sm font-medium">Raw Table</span>
              </button>
            </div>
          </div>

          {/* Transform Selection */}
          {sourceType === 'transform' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Transform *
              </label>
              {transforms.length === 0 ? (
                <div className="text-sm text-gray-500 dark:text-gray-400 p-3 bg-indigo-50/50 dark:bg-indigo-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800/50">
                  No transforms available. Create a transform first.
                </div>
              ) : (
                <select
                  value={selectedTransform?.id || ''}
                  onChange={(e) => {
                    const transform = transforms.find(t => t.id === e.target.value)
                    setSelectedTransform(transform || null)
                    if (transform) {
                      // Set connection from transform
                      const conn = connections.find(c => c.id === transform.connection_id)
                      setSelectedConnection(conn || null)
                      // Fetch columns from transform
                      fetchTransformColumns(transform.id)
                    } else {
                      setColumns([])
                    }
                  }}
                  disabled={!!editingModel}
                  className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                >
                  <option value="">Select transform...</option>
                  {transforms.map(t => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              )}
              {selectedTransform && (
                <div className="mt-2 text-xs text-indigo-600 dark:text-indigo-400 flex items-center gap-1">
                  <Database className="w-3 h-3" />
                  Source: {selectedTransform.source_schema}.{selectedTransform.source_table}
                </div>
              )}
            </div>
          )}

          {/* Raw Table Selection */}
          {sourceType === 'table' && (
            <>
              {/* Connection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Connection *</label>
                <select
                  value={selectedConnection?.id || ''}
                  onChange={(e) => {
                    const conn = connections.find(c => c.id === e.target.value)
                    setSelectedConnection(conn || null)
                    setSelectedTable('')
                    setColumns([])
                  }}
                  disabled={!!editingModel}
                  className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                >
                  <option value="">Select connection...</option>
                  {connections.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              {/* Base Table */}
              {selectedConnection && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Base Table *</label>
                  {loadingTables ? (
                    <div className="flex items-center justify-center py-4">
                      <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
                    </div>
                  ) : (
                    <select
                      value={selectedTable}
                      onChange={(e) => {
                        const table = tables.find(t => t.name === e.target.value)
                        setSelectedTable(e.target.value)
                        if (table) setSelectedSchema(table.schema_name)
                      }}
                      disabled={!!editingModel}
                      className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                    >
                      <option value="">Select table...</option>
                      {tables.map(t => (
                        <option key={`${t.schema_name}.${t.name}`} value={t.name}>
                          {t.schema_name}.{t.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
            </>
          )}

          {/* Available Columns */}
          {columns.length > 0 && (
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Columns className="w-4 h-4 text-indigo-500" />
                Available Columns
                <span className="ml-auto text-xs text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-2 py-0.5 rounded-full">
                  {columns.length}
                </span>
              </label>
              <div className="max-h-48 overflow-y-auto border border-gray-200/60 dark:border-gray-700/60 rounded-xl bg-white/50 dark:bg-gray-800/50">
                {columns.map(col => (
                  <div key={col.name} className="px-3 py-2 text-sm border-b border-gray-100 dark:border-gray-700/50 last:border-0 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/20 transition-colors">
                    <span className="text-gray-900 dark:text-white font-medium">{col.name}</span>
                    <span className="text-indigo-500 dark:text-indigo-400 ml-2 text-xs">{col.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Measures, Dimensions, Joins */}
        <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-br from-gray-50/50 via-white to-indigo-50/30 dark:from-gray-900/50 dark:via-gray-900 dark:to-indigo-950/20">
          {!editingModel ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center mb-6 shadow-lg shadow-purple-500/25">
                <Layers className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Configure Base Model First
              </h3>
              <p className="max-w-md text-gray-500 dark:text-gray-400">
                Fill in the model name, select a connection and base table, then click "Create Model" to add measures and dimensions.
              </p>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6">
              {/* Measures Section */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 overflow-hidden shadow-sm hover:shadow-lg transition-shadow">
                <button
                  onClick={() => toggleSection('measures')}
                  className="w-full px-5 py-4 flex items-center justify-between bg-gradient-to-r from-indigo-50/80 to-purple-50/80 dark:from-indigo-900/30 dark:to-purple-900/30 hover:from-indigo-100 hover:to-purple-100 dark:hover:from-indigo-900/40 dark:hover:to-purple-900/40 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-md shadow-indigo-500/25">
                      <Calculator className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-semibold text-gray-900 dark:text-white">Measures</span>
                    <span className="text-xs bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 px-2 py-0.5 rounded-full font-medium">
                      {editingModel.measures.length}
                    </span>
                  </div>
                  {expandedSections.measures ? <ChevronDown className="w-5 h-5 text-indigo-500" /> : <ChevronRight className="w-5 h-5 text-indigo-500" />}
                </button>

                {expandedSections.measures && (
                  <div className="p-5">
                    {editingModel.measures.length === 0 ? (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 p-3 bg-indigo-50/50 dark:bg-indigo-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800/50">
                        No measures defined. Add measures to enable aggregations.
                      </p>
                    ) : (
                      <div className="space-y-2 mb-4">
                        {editingModel.measures.map(m => (
                          <div key={m.id} className="flex items-center justify-between px-4 py-3 bg-indigo-50/50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/50 rounded-xl hover:bg-indigo-100/50 dark:hover:bg-indigo-900/30 transition-colors">
                            <div>
                              <span className="font-medium text-gray-900 dark:text-white">{m.name}</span>
                              <span className="text-sm text-indigo-600 dark:text-indigo-400 ml-2">{m.expression}</span>
                            </div>
                            <button
                              onClick={() => removeMeasure(m.id)}
                              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    <button
                      onClick={() => setShowMeasureModal(true)}
                      className="flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
                    >
                      <Plus className="w-4 h-4" /> Add Measure
                    </button>
                  </div>
                )}
              </div>

              {/* Dimensions Section */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 overflow-hidden shadow-sm hover:shadow-lg transition-shadow">
                <button
                  onClick={() => toggleSection('dimensions')}
                  className="w-full px-5 py-4 flex items-center justify-between bg-gradient-to-r from-purple-50/80 to-fuchsia-50/80 dark:from-purple-900/30 dark:to-fuchsia-900/30 hover:from-purple-100 hover:to-fuchsia-100 dark:hover:from-purple-900/40 dark:hover:to-fuchsia-900/40 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-500 to-fuchsia-600 flex items-center justify-center shadow-md shadow-purple-500/25">
                      <Columns className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-semibold text-gray-900 dark:text-white">Dimensions</span>
                    <span className="text-xs bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300 px-2 py-0.5 rounded-full font-medium">
                      {editingModel.dimensions.length}
                    </span>
                  </div>
                  {expandedSections.dimensions ? <ChevronDown className="w-5 h-5 text-purple-500" /> : <ChevronRight className="w-5 h-5 text-purple-500" />}
                </button>

                {expandedSections.dimensions && (
                  <div className="p-5">
                    {editingModel.dimensions.length === 0 ? (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 p-3 bg-purple-50/50 dark:bg-purple-900/20 rounded-xl border border-purple-100 dark:border-purple-800/50">
                        No dimensions defined. Add dimensions for grouping and filtering.
                      </p>
                    ) : (
                      <div className="space-y-2 mb-4">
                        {editingModel.dimensions.map(d => (
                          <div key={d.id} className="flex items-center justify-between px-4 py-3 bg-purple-50/50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800/50 rounded-xl hover:bg-purple-100/50 dark:hover:bg-purple-900/30 transition-colors">
                            <div>
                              <span className="font-medium text-gray-900 dark:text-white">{d.name}</span>
                              <span className="text-sm text-purple-600 dark:text-purple-400 ml-2">{d.column_name}</span>
                            </div>
                            <button
                              onClick={() => removeDimension(d.id)}
                              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    <button
                      onClick={() => setShowDimensionModal(true)}
                      className="flex items-center gap-2 text-sm font-medium text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
                    >
                      <Plus className="w-4 h-4" /> Add Dimension
                    </button>
                  </div>
                )}
              </div>

              {/* Joins/Relationships Section */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 overflow-hidden shadow-sm hover:shadow-lg transition-shadow">
                <button
                  onClick={() => toggleSection('joins')}
                  className="w-full px-5 py-4 flex items-center justify-between bg-gradient-to-r from-fuchsia-50/80 to-pink-50/80 dark:from-fuchsia-900/30 dark:to-pink-900/30 hover:from-fuchsia-100 hover:to-pink-100 dark:hover:from-fuchsia-900/40 dark:hover:to-pink-900/40 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-fuchsia-500 to-pink-600 flex items-center justify-center shadow-md shadow-fuchsia-500/25">
                      <GitBranch className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-semibold text-gray-900 dark:text-white">Relationships</span>
                    <span className="text-xs bg-fuchsia-100 dark:bg-fuchsia-900/50 text-fuchsia-700 dark:text-fuchsia-300 px-2 py-0.5 rounded-full font-medium">
                      {editingModel.joins.length}
                    </span>
                  </div>
                  {expandedSections.joins ? <ChevronDown className="w-5 h-5 text-fuchsia-500" /> : <ChevronRight className="w-5 h-5 text-fuchsia-500" />}
                </button>

                {expandedSections.joins && (
                  <div className="p-5">
                    {editingModel.joins.length === 0 && (!editingModel.joined_transforms || editingModel.joined_transforms.length === 0) ? (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 p-3 bg-fuchsia-50/50 dark:bg-fuchsia-900/20 rounded-xl border border-fuchsia-100 dark:border-fuchsia-800/50">
                        No relationships defined. Add joins to connect related tables or transforms.
                      </p>
                    ) : (
                      <div className="space-y-2 mb-4">
                        {/* Table Joins */}
                        {editingModel.joins.map(j => (
                          <div key={j.id} className="flex items-center justify-between px-4 py-3 bg-fuchsia-50/50 dark:bg-fuchsia-900/20 border border-fuchsia-100 dark:border-fuchsia-800/50 rounded-xl hover:bg-fuchsia-100/50 dark:hover:bg-fuchsia-900/30 transition-colors">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-lg bg-fuchsia-100 dark:bg-fuchsia-900/50 flex items-center justify-center">
                                <Table2 className="w-4 h-4 text-fuchsia-600 dark:text-fuchsia-400" />
                              </div>
                              <div>
                                <span className="font-medium text-gray-900 dark:text-white">{j.target_table}</span>
                                <span className="text-sm text-fuchsia-600 dark:text-fuchsia-400 ml-2">({j.join_type})</span>
                                <div className="text-xs text-gray-400 mt-1">{j.join_condition}</div>
                              </div>
                            </div>
                            <button
                              onClick={() => removeJoin(j.id)}
                              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                        {/* Transform Joins */}
                        {editingModel.joined_transforms?.map(jt => (
                          <div key={jt.transform_id} className="flex items-center justify-between px-4 py-3 bg-purple-50/50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800/50 rounded-xl hover:bg-purple-100/50 dark:hover:bg-purple-900/30 transition-colors">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center">
                                <Wand2 className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                              </div>
                              <div>
                                <span className="font-medium text-gray-900 dark:text-white">{jt.transform_name || jt.alias}</span>
                                <span className="text-sm text-purple-600 dark:text-purple-400 ml-2">({jt.join_type} join)</span>
                                <div className="text-xs text-gray-400 mt-1">
                                  ON {jt.join_on?.map(jo => `${jo.left} = ${jo.right}`).join(' AND ')}
                                </div>
                              </div>
                            </div>
                            <button
                              onClick={() => removeJoin(jt.transform_id)}
                              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    <button
                      onClick={() => setShowJoinModal(true)}
                      className="flex items-center gap-2 text-sm font-medium text-fuchsia-600 hover:text-fuchsia-700 dark:text-fuchsia-400 dark:hover:text-fuchsia-300"
                    >
                      <Plus className="w-4 h-4" /> Add Relationship
                    </button>
                  </div>
                )}
              </div>

              {/* Preview Section */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 dark:border-gray-700/60 overflow-hidden shadow-sm hover:shadow-lg transition-shadow">
                <button
                  onClick={() => setShowPreviewSection(!showPreviewSection)}
                  className="w-full px-5 py-4 flex items-center justify-between bg-gradient-to-r from-indigo-50/80 via-purple-50/80 to-fuchsia-50/80 dark:from-indigo-900/30 dark:via-purple-900/30 dark:to-fuchsia-900/30 hover:from-indigo-100 hover:via-purple-100 hover:to-fuchsia-100 dark:hover:from-indigo-900/40 dark:hover:via-purple-900/40 dark:hover:to-fuchsia-900/40 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-md shadow-purple-500/25">
                      <Eye className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-semibold text-gray-900 dark:text-white">Data Preview</span>
                    {previewData && (
                      <span className="text-xs bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 px-2 py-0.5 rounded-full font-medium">
                        {previewData.total_rows} rows
                      </span>
                    )}
                  </div>
                  {showPreviewSection ? <ChevronDown className="w-5 h-5 text-indigo-500" /> : <ChevronRight className="w-5 h-5 text-indigo-500" />}
                </button>

                {showPreviewSection && (
                  <div className="p-5">
                    {/* Selection Area */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      {/* Measures Selection */}
                      <div>
                        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          <Calculator className="w-4 h-4 text-indigo-500" />
                          Select Measures
                        </label>
                        {editingModel.measures.length === 0 ? (
                          <p className="text-xs text-gray-400 p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">No measures available</p>
                        ) : (
                          <div className="space-y-1 max-h-32 overflow-y-auto border border-gray-200/60 dark:border-gray-700/60 rounded-xl p-2 bg-white/50 dark:bg-gray-800/50">
                            {editingModel.measures.map(m => (
                              <label key={m.id} className="flex items-center gap-2 text-sm cursor-pointer hover:bg-indigo-50/50 dark:hover:bg-indigo-900/20 p-1.5 rounded-lg transition-colors">
                                <input
                                  type="checkbox"
                                  checked={previewMeasureIds.includes(m.id)}
                                  onChange={() => togglePreviewMeasure(m.id)}
                                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                                />
                                <span className="text-gray-700 dark:text-gray-300">{m.name}</span>
                                <span className="text-xs text-indigo-500 dark:text-indigo-400">({m.aggregation})</span>
                              </label>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Dimensions Selection */}
                      <div>
                        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          <Columns className="w-4 h-4 text-purple-500" />
                          Select Dimensions
                        </label>
                        {editingModel.dimensions.length === 0 ? (
                          <p className="text-xs text-gray-400 p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">No dimensions available</p>
                        ) : (
                          <div className="space-y-1 max-h-32 overflow-y-auto border border-gray-200/60 dark:border-gray-700/60 rounded-xl p-2 bg-white/50 dark:bg-gray-800/50">
                            {editingModel.dimensions.map(d => (
                              <label key={d.id} className="flex items-center gap-2 text-sm cursor-pointer hover:bg-purple-50/50 dark:hover:bg-purple-900/20 p-1.5 rounded-lg transition-colors">
                                <input
                                  type="checkbox"
                                  checked={previewDimensionIds.includes(d.id)}
                                  onChange={() => togglePreviewDimension(d.id)}
                                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                                />
                                <span className="text-gray-700 dark:text-gray-300">{d.name}</span>
                              </label>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center gap-3 mb-4">
                      <button
                        onClick={fetchPreview}
                        disabled={previewLoading || (previewMeasureIds.length === 0 && previewDimensionIds.length === 0)}
                        className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        {previewLoading ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Play className="w-4 h-4" />
                        )}
                        Run Preview
                      </button>
                      {(previewData || previewError) && (
                        <button
                          onClick={clearPreview}
                          className="px-4 py-2.5 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 rounded-xl transition-colors font-medium"
                        >
                          Clear
                        </button>
                      )}
                    </div>

                    {/* Error Display */}
                    {previewError && (
                      <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
                        {previewError}
                      </div>
                    )}

                    {/* Results */}
                    {previewData && (
                      <div className="space-y-4">
                        {/* Generated SQL */}
                        <div>
                          <div className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            <Code className="w-4 h-4 text-indigo-500" />
                            Generated SQL
                            <span className="text-xs text-indigo-600 dark:text-indigo-400 ml-auto bg-indigo-50 dark:bg-indigo-900/30 px-2 py-0.5 rounded-full">
                              {previewData.execution_time_ms.toFixed(0)}ms
                            </span>
                          </div>
                          <pre className="bg-gray-900 text-gray-100 p-4 rounded-xl text-xs overflow-x-auto max-h-24 scrollbar-thin border border-gray-700">
                            {previewData.sql_generated}
                          </pre>
                        </div>

                        {/* Data Table */}
                        <div>
                          <div className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            <Table2 className="w-4 h-4 text-purple-500" />
                            Results
                            <span className="text-xs text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/30 px-2 py-0.5 rounded-full">
                              {previewData.total_rows} rows, showing {previewData.rows.length}
                            </span>
                          </div>
                          <div className="border border-gray-200/60 dark:border-gray-700/60 rounded-xl overflow-hidden">
                            <div className="overflow-x-auto max-h-64">
                              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                <thead className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 sticky top-0">
                                  <tr>
                                    {previewData.columns.map((col, idx) => (
                                      <th
                                        key={idx}
                                        className="px-4 py-3 text-left text-xs font-semibold text-indigo-700 dark:text-indigo-300 uppercase tracking-wider whitespace-nowrap"
                                      >
                                        {col}
                                      </th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody className="bg-white/80 dark:bg-gray-800/80 divide-y divide-gray-100 dark:divide-gray-700/50">
                                  {previewData.rows.map((row, rowIdx) => (
                                    <tr key={rowIdx} className="hover:bg-indigo-50/50 dark:hover:bg-indigo-900/20 transition-colors">
                                      {previewData.columns.map((col, colIdx) => (
                                        <td
                                          key={colIdx}
                                          className="px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 whitespace-nowrap"
                                        >
                                          {row[col] !== null && row[col] !== undefined
                                            ? typeof row[col] === 'number'
                                              ? row[col].toLocaleString()
                                              : String(row[col])
                                            : <span className="text-gray-400 italic">null</span>
                                          }
                                        </td>
                                      ))}
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add Measure Modal */}
      {showMeasureModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl shadow-indigo-500/20 w-full max-w-md overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-gradient-to-r from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <Calculator className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white">Add Measure</h3>
              </div>
              <button onClick={() => setShowMeasureModal(false)} className="text-white/80 hover:text-white p-1 hover:bg-white/10 rounded-lg transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name *</label>
                <input
                  type="text"
                  value={newMeasure.name}
                  onChange={(e) => setNewMeasure({ ...newMeasure, name: e.target.value })}
                  placeholder="e.g., Total Revenue"
                  className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Column *</label>
                <select
                  value={newMeasure.column_name}
                  onChange={(e) => setNewMeasure({ ...newMeasure, column_name: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                >
                  <option value="">Select column...</option>
                  {columns.map(c => (
                    <option key={c.name} value={c.name}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Aggregation</label>
                <select
                  value={newMeasure.aggregation}
                  onChange={(e) => setNewMeasure({ ...newMeasure, aggregation: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                >
                  {AGG_OPTIONS.map(o => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  onClick={() => setShowMeasureModal(false)}
                  className="px-4 py-2.5 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 rounded-xl font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={addMeasure}
                  disabled={!newMeasure.name || !newMeasure.column_name}
                  className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-500/25 disabled:opacity-50 transition-all"
                >
                  Add Measure
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Dimension Modal */}
      {showDimensionModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl shadow-purple-500/20 w-full max-w-md overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-gradient-to-r from-purple-500 via-fuchsia-500 to-pink-500 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <Columns className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white">Add Dimension</h3>
              </div>
              <button onClick={() => setShowDimensionModal(false)} className="text-white/80 hover:text-white p-1 hover:bg-white/10 rounded-lg transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name *</label>
                <input
                  type="text"
                  value={newDimension.name}
                  onChange={(e) => setNewDimension({ ...newDimension, name: e.target.value })}
                  placeholder="e.g., Product Category"
                  className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Column *</label>
                <select
                  value={newDimension.column_name}
                  onChange={(e) => setNewDimension({ ...newDimension, column_name: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
                >
                  <option value="">Select column...</option>
                  {columns.map(c => (
                    <option key={c.name} value={c.name}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  onClick={() => setShowDimensionModal(false)}
                  className="px-4 py-2.5 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 rounded-xl font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={addDimension}
                  disabled={!newDimension.name || !newDimension.column_name}
                  className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-fuchsia-600 text-white rounded-xl font-medium hover:from-purple-700 hover:to-fuchsia-700 shadow-lg shadow-purple-500/25 disabled:opacity-50 transition-all"
                >
                  Add Dimension
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Join Modal */}
      {showJoinModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl shadow-fuchsia-500/20 w-full max-w-md overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-gradient-to-r from-fuchsia-500 via-pink-500 to-rose-500 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <GitBranch className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white">Add Relationship</h3>
              </div>
              <button onClick={() => setShowJoinModal(false)} className="text-white/80 hover:text-white p-1 hover:bg-white/10 rounded-lg transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              {/* From Column */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  From Column (in {editingModel?.transform_id ? 'transform' : editingModel?.table_name}) *
                </label>
                <select
                  value={newJoin.from_column}
                  onChange={(e) => setNewJoin({ ...newJoin, from_column: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-fuchsia-500/50 focus:border-fuchsia-500 transition-all"
                >
                  <option value="">Select column...</option>
                  {columns.map(c => (
                    <option key={c.name} value={c.name}>{c.name}</option>
                  ))}
                </select>
              </div>

              {/* Join Target Type Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Join To *</label>
                <div className="flex gap-2 mb-3">
                  <button
                    type="button"
                    onClick={() => {
                      setJoinSourceType('transform')
                      setNewJoin({ ...newJoin, to_table: '', to_transform_id: '', to_column: '' })
                      setJoinTableColumns([])
                    }}
                    className={`flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl border transition-all ${
                      joinSourceType === 'transform'
                        ? 'border-fuchsia-500 bg-fuchsia-50 dark:bg-fuchsia-900/30 text-fuchsia-700 dark:text-fuchsia-300 shadow-sm'
                        : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-fuchsia-300'
                    }`}
                  >
                    <Wand2 className="w-4 h-4" />
                    <span className="text-sm font-medium">Transform</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setJoinSourceType('table')
                      setNewJoin({ ...newJoin, to_table: '', to_transform_id: '', to_column: '' })
                      setJoinTableColumns([])
                    }}
                    className={`flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl border transition-all ${
                      joinSourceType === 'table'
                        ? 'border-fuchsia-500 bg-fuchsia-50 dark:bg-fuchsia-900/30 text-fuchsia-700 dark:text-fuchsia-300 shadow-sm'
                        : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-fuchsia-300'
                    }`}
                  >
                    <Table2 className="w-4 h-4" />
                    <span className="text-sm font-medium">Raw Table</span>
                  </button>
                </div>

                {/* Transform Selection */}
                {joinSourceType === 'transform' && (
                  <select
                    value={newJoin.to_transform_id}
                    onChange={(e) => {
                      setNewJoin({ ...newJoin, to_transform_id: e.target.value, to_column: '' })
                      if (e.target.value) fetchJoinTransformColumns(e.target.value)
                    }}
                    className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-fuchsia-500/50 focus:border-fuchsia-500 transition-all"
                  >
                    <option value="">Select transform...</option>
                    {transforms
                      .filter(t => t.id !== editingModel?.transform_id)
                      .map(t => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                  </select>
                )}

                {/* Table Selection */}
                {joinSourceType === 'table' && (
                  <select
                    value={newJoin.to_table}
                    onChange={(e) => {
                      setNewJoin({ ...newJoin, to_table: e.target.value, to_column: '' })
                      if (e.target.value) fetchJoinTableColumns(e.target.value)
                    }}
                    className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-fuchsia-500/50 focus:border-fuchsia-500 transition-all"
                  >
                    <option value="">Select table...</option>
                    {tables.filter(t => t.name !== editingModel?.table_name).map(t => (
                      <option key={t.name} value={t.name}>{t.name}</option>
                    ))}
                  </select>
                )}
              </div>

              {/* To Column - shown when target is selected */}
              {(newJoin.to_table || newJoin.to_transform_id) && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">To Column *</label>
                  <select
                    value={newJoin.to_column}
                    onChange={(e) => setNewJoin({ ...newJoin, to_column: e.target.value })}
                    className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-fuchsia-500/50 focus:border-fuchsia-500 transition-all"
                  >
                    <option value="">Select column...</option>
                    {joinTableColumns.map(c => (
                      <option key={c.name} value={c.name}>{c.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Join Type</label>
                <select
                  value={newJoin.join_type}
                  onChange={(e) => setNewJoin({ ...newJoin, join_type: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-fuchsia-500/50 focus:border-fuchsia-500 transition-all"
                >
                  {JOIN_TYPES.map(j => (
                    <option key={j.value} value={j.value}>{j.label}</option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  onClick={() => {
                    setShowJoinModal(false)
                    setJoinTableColumns([])
                    setJoinSourceType('transform')
                    setNewJoin({ from_column: '', to_table: '', to_transform_id: '', to_column: '', join_type: 'left' })
                  }}
                  className="px-4 py-2.5 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 rounded-xl font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={addJoin}
                  disabled={!newJoin.from_column || !newJoin.to_column || (joinSourceType === 'table' ? !newJoin.to_table : !newJoin.to_transform_id)}
                  className="px-5 py-2.5 bg-gradient-to-r from-fuchsia-600 to-pink-600 text-white rounded-xl font-medium hover:from-fuchsia-700 hover:to-pink-700 shadow-lg shadow-fuchsia-500/25 disabled:opacity-50 transition-all"
                >
                  Add Relationship
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SemanticModels
