import { useState, useEffect } from 'react'
import {
  X,
  Database,
  Table2,
  Wand2,
  Calendar,
  Target,
  TrendingUp,
  ChevronDown,
  Loader2
} from 'lucide-react'
import { KPICard, KPIConfig } from './KPICard'

// Use relative URL to go through Vite proxy in dev, or direct in production
const API_BASE_URL = '/api/v1'

interface Connection {
  id: string
  name: string
  type: string
}

interface Transform {
  id: string
  name: string
  connection_id: string
  source_table: string
}

interface SemanticModelSummary {
  id: string
  name: string
  connection_id: string
  transform_id?: string
  measures_count?: number
  dimensions_count?: number
}

interface SemanticModelFull {
  id: string
  name: string
  connection_id: string
  transform_id?: string
  measures: { id: string; name: string; column_name: string }[]
  dimensions: { id: string; name: string; column_name: string }[]
}

interface TableInfo {
  name: string
  schema: string
}

interface ColumnInfo {
  name: string
  type: string
}

interface KPIBuilderProps {
  isOpen: boolean
  onClose: () => void
  onSave: (config: KPIConfig) => void
  initialConfig?: Partial<KPIConfig>
}

export function KPIBuilder({ isOpen, onClose, onSave, initialConfig }: KPIBuilderProps) {
  // Data sources
  const [connections, setConnections] = useState<Connection[]>([])
  const [transforms, setTransforms] = useState<Transform[]>([])
  const [models, setModels] = useState<SemanticModelSummary[]>([])
  const [selectedModelFull, setSelectedModelFull] = useState<SemanticModelFull | null>(null)
  const [tables, setTables] = useState<TableInfo[]>([])
  const [columns, setColumns] = useState<ColumnInfo[]>([])

  // Selection state
  const [sourceType, setSourceType] = useState<'model' | 'transform' | 'table'>('model')
  const [selectedConnection, setSelectedConnection] = useState<string>('')
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [selectedTransform, setSelectedTransform] = useState<string>('')
  const [selectedTable, setSelectedTable] = useState<string>('')

  // KPI configuration
  const [title, setTitle] = useState(initialConfig?.title || 'New KPI')
  const [measureColumn, setMeasureColumn] = useState(initialConfig?.measureColumn || '')
  const [aggregation, setAggregation] = useState<'sum' | 'avg' | 'count' | 'min' | 'max'>(
    initialConfig?.aggregation || 'sum'
  )
  const [dateColumn, setDateColumn] = useState(initialConfig?.dateColumn || '')
  type ComparisonPeriod = 'previous_day' | 'previous_week' | 'previous_month' | 'previous_quarter' | 'previous_year'
  const [comparisonPeriod, setComparisonPeriod] = useState<ComparisonPeriod>(
    (initialConfig?.comparisonPeriod as ComparisonPeriod) || 'previous_month'
  )
  const [goalValue, setGoalValue] = useState<number | undefined>(initialConfig?.goalValue)
  const [goalLabel, setGoalLabel] = useState(initialConfig?.goalLabel || '')

  // UI state
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(1) // 1: Source, 2: Measure, 3: Comparison, 4: Preview

  // Fetch initial data and reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      // Reset to initial state
      setStep(1)
      setSourceType('model')
      setSelectedModel('')
      setSelectedModelFull(null)
      setSelectedTransform('')
      setSelectedConnection('')
      setSelectedTable('')
      setColumns([])
      setMeasureColumn('')
      setDateColumn('')
      setTitle(initialConfig?.title || 'New KPI')

      // Fetch data sources
      fetchConnections()
      fetchTransforms()
      fetchModels()
    }
  }, [isOpen])

  const fetchConnections = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/connections/`)
      if (res.ok) setConnections(await res.json())
    } catch (e) {
      console.error('Failed to fetch connections:', e)
    }
  }

  const fetchTransforms = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/transforms/`)
      if (res.ok) setTransforms(await res.json())
    } catch (e) {
      console.error('Failed to fetch transforms:', e)
    }
  }

  const fetchModels = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/models/`)
      if (res.ok) setModels(await res.json())
    } catch (e) {
      console.error('Failed to fetch models:', e)
    }
  }

  // Fetch full model details (including measures/dimensions)
  const fetchModelDetails = async (modelId: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/models/${modelId}`)
      if (res.ok) {
        const fullModel = await res.json()
        setSelectedModelFull(fullModel)
        return fullModel
      }
    } catch (e) {
      console.error('Failed to fetch model details:', e)
    }
    return null
  }

  const fetchTables = async (connectionId: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/connections/${connectionId}/tables`)
      if (res.ok) {
        const data = await res.json()
        setTables(data.map((t: any) => ({ name: t.name || t, schema: t.schema || 'public' })))
      }
    } catch (e) {
      console.error('Failed to fetch tables:', e)
    }
  }

  const fetchColumns = async () => {
    setLoading(true)
    try {
      if (sourceType === 'model' && selectedModel) {
        // Use the full model that was fetched when selecting
        if (selectedModelFull) {
          // Get columns from model measures and dimensions
          const cols = [
            ...(selectedModelFull.measures || []).map(m => ({ name: m.column_name, type: 'numeric' })),
            ...(selectedModelFull.dimensions || []).map(d => ({ name: d.column_name, type: 'string' }))
          ]
          setColumns(cols)
        } else {
          // Fetch model details if not already loaded
          const fullModel = await fetchModelDetails(selectedModel)
          if (fullModel) {
            const cols = [
              ...(fullModel.measures || []).map((m: any) => ({ name: m.column_name, type: 'numeric' })),
              ...(fullModel.dimensions || []).map((d: any) => ({ name: d.column_name, type: 'string' }))
            ]
            setColumns(cols)
          }
        }
      } else if (sourceType === 'transform' && selectedTransform) {
        // Execute transform with limit 1 to get columns
        const res = await fetch(`${API_BASE_URL}/transforms/${selectedTransform}/execute?limit=1`, {
          method: 'POST'
        })
        if (res.ok) {
          const data = await res.json()
          setColumns(data.columns?.map((c: any) => ({
            name: typeof c === 'string' ? c : c.name,
            type: typeof c === 'string' ? 'unknown' : c.type
          })) || [])
        }
      } else if (sourceType === 'table' && selectedConnection && selectedTable) {
        const res = await fetch(
          `${API_BASE_URL}/connections/${selectedConnection}/tables/public/${selectedTable}/columns`
        )
        if (res.ok) setColumns(await res.json())
      }
    } catch (e) {
      console.error('Failed to fetch columns:', e)
    } finally {
      setLoading(false)
    }
  }

  // Fetch columns when source selection changes
  useEffect(() => {
    if (sourceType === 'model' && selectedModelFull) {
      fetchColumns()
    } else if (sourceType === 'transform' && selectedTransform) {
      fetchColumns()
    } else if (sourceType === 'table' && selectedTable) {
      fetchColumns()
    }
  }, [selectedModelFull, selectedTransform, selectedTable, sourceType])

  // Get connection ID based on source type
  const getConnectionId = () => {
    if (sourceType === 'model') {
      // Use selectedModelFull first, fallback to summary
      if (selectedModelFull) return selectedModelFull.connection_id
      const model = models.find(m => m.id === selectedModel)
      return model?.connection_id || ''
    } else if (sourceType === 'transform') {
      const transform = transforms.find(t => t.id === selectedTransform)
      return transform?.connection_id || ''
    }
    return selectedConnection
  }

  // Handle model selection
  const handleModelSelect = async (modelId: string) => {
    setSelectedModel(modelId)
    setSelectedModelFull(null) // Reset full model
    setColumns([]) // Clear columns
    if (modelId) {
      await fetchModelDetails(modelId)
    }
  }

  // Build KPI config
  const buildConfig = (): KPIConfig => ({
    connectionId: getConnectionId(),
    semanticModelId: sourceType === 'model' ? selectedModel : undefined,
    transformId: sourceType === 'transform' ? selectedTransform : undefined,
    tableName: sourceType === 'table' ? selectedTable : undefined,
    schemaName: 'public',
    measureColumn,
    aggregation,
    dateColumn: dateColumn || undefined,
    comparisonPeriod: dateColumn ? comparisonPeriod as any : undefined,
    goalValue,
    goalLabel: goalLabel || undefined,
    title
  })

  // Check if step is valid
  const isStepValid = (stepNum: number) => {
    switch (stepNum) {
      case 1:
        return (sourceType === 'model' && selectedModel) ||
               (sourceType === 'transform' && selectedTransform) ||
               (sourceType === 'table' && selectedConnection && selectedTable)
      case 2:
        return measureColumn !== ''
      case 3:
        return true // Optional step
      case 4:
        return true
      default:
        return false
    }
  }

  const handleSave = () => {
    const config = buildConfig()
    onSave(config)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Configure KPI Card
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center px-6 py-3 border-b border-gray-100 dark:border-gray-700/50 bg-gray-50 dark:bg-gray-800/50">
          {['Data Source', 'Measure', 'Comparison', 'Preview'].map((label, i) => (
            <div key={i} className="flex items-center">
              <button
                onClick={() => setStep(i + 1)}
                disabled={!isStepValid(i)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  step === i + 1
                    ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300'
                    : step > i + 1
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-gray-400'
                }`}
              >
                <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                  step === i + 1 ? 'bg-purple-500 text-white' :
                  step > i + 1 ? 'bg-green-500 text-white' :
                  'bg-gray-200 dark:bg-gray-700 text-gray-500'
                }`}>
                  {step > i + 1 ? '✓' : i + 1}
                </span>
                {label}
              </button>
              {i < 3 && <ChevronDown className="w-4 h-4 text-gray-300 rotate-[-90deg] mx-1" />}
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {/* Step 1: Data Source */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Select Data Source
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { type: 'model' as const, icon: Wand2, label: 'Semantic Model', desc: 'Use pre-defined measures' },
                    { type: 'transform' as const, icon: Table2, label: 'Transform', desc: 'Use cleaned data' },
                    { type: 'table' as const, icon: Database, label: 'Raw Table', desc: 'Direct table access' }
                  ].map(({ type, icon: Icon, label, desc }) => (
                    <button
                      key={type}
                      onClick={() => setSourceType(type)}
                      className={`flex flex-col items-center p-4 rounded-xl border-2 transition-all ${
                        sourceType === type
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <Icon className={`w-8 h-8 mb-2 ${sourceType === type ? 'text-purple-500' : 'text-gray-400'}`} />
                      <span className="font-medium text-gray-900 dark:text-white">{label}</span>
                      <span className="text-xs text-gray-500 mt-1">{desc}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Source Selection */}
              <div>
                {sourceType === 'model' && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Select Model</label>
                    {models.length === 0 ? (
                      <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-sm text-yellow-700 dark:text-yellow-300">
                        No semantic models found. Create a model first in the Semantic Models section, or choose a different source type.
                      </div>
                    ) : (
                      <>
                        <select
                          value={selectedModel}
                          onChange={e => handleModelSelect(e.target.value)}
                          className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                        >
                          <option value="">Choose a model...</option>
                          {models.map(m => (
                            <option key={m.id} value={m.id}>{m.name}</option>
                          ))}
                        </select>
                        {selectedModel && !selectedModelFull && (
                          <div className="mt-2 flex items-center text-sm text-gray-500">
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                            Loading model details...
                          </div>
                        )}
                        {selectedModelFull && (
                          <div className="mt-2 text-xs text-gray-500">
                            {selectedModelFull.measures?.length || 0} measures, {selectedModelFull.dimensions?.length || 0} dimensions
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}

                {sourceType === 'transform' && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Select Transform</label>
                    {transforms.length === 0 ? (
                      <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-sm text-yellow-700 dark:text-yellow-300">
                        No transforms found. Create a transform first in the Transforms section, or choose a different source type.
                      </div>
                    ) : (
                      <select
                        value={selectedTransform}
                        onChange={e => setSelectedTransform(e.target.value)}
                        className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                      >
                        <option value="">Choose a transform...</option>
                        {transforms.map(t => (
                          <option key={t.id} value={t.id}>{t.name}</option>
                        ))}
                      </select>
                    )}
                  </div>
                )}

                {sourceType === 'table' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Select Connection</label>
                      {connections.length === 0 ? (
                        <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-sm text-yellow-700 dark:text-yellow-300">
                          No connections found. Create a database connection first in the Data Connections section.
                        </div>
                      ) : (
                        <select
                          value={selectedConnection}
                          onChange={e => {
                            setSelectedConnection(e.target.value)
                            setSelectedTable('')
                            setTables([])
                            if (e.target.value) fetchTables(e.target.value)
                          }}
                          className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                        >
                          <option value="">Choose a connection...</option>
                          {connections.map(c => (
                            <option key={c.id} value={c.id}>{c.name} ({c.type})</option>
                          ))}
                        </select>
                      )}
                    </div>
                    {selectedConnection && (
                      <div>
                        <label className="block text-sm font-medium mb-2">Select Table</label>
                        {tables.length === 0 ? (
                          <div className="flex items-center text-sm text-gray-500">
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                            Loading tables...
                          </div>
                        ) : (
                          <select
                            value={selectedTable}
                            onChange={e => setSelectedTable(e.target.value)}
                            className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                          >
                            <option value="">Choose a table...</option>
                            {tables.map(t => (
                              <option key={t.name} value={t.name}>{t.name}</option>
                            ))}
                          </select>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Measure Configuration */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">KPI Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  placeholder="e.g., Total Revenue"
                  className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                />
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-purple-500" />
                  <span className="ml-2 text-gray-500">Loading columns...</span>
                </div>
              ) : columns.length === 0 ? (
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-sm text-yellow-700 dark:text-yellow-300">
                  No columns available. Please go back and select a valid data source, or ensure your model/transform has measures and dimensions defined.
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Measure Column</label>
                    <select
                      value={measureColumn}
                      onChange={e => setMeasureColumn(e.target.value)}
                      className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                    >
                      <option value="">Select column...</option>
                      {columns.map(c => (
                        <option key={c.name} value={c.name}>{c.name} ({c.type})</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Aggregation</label>
                    <select
                      value={aggregation}
                      onChange={e => setAggregation(e.target.value as any)}
                      className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                    >
                      <option value="sum">Sum</option>
                      <option value="avg">Average</option>
                      <option value="count">Count</option>
                      <option value="min">Minimum</option>
                      <option value="max">Maximum</option>
                    </select>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Comparison & Goal */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="w-5 h-5 text-blue-500" />
                  <span className="font-medium text-blue-700 dark:text-blue-300">Period Comparison</span>
                </div>
                <p className="text-sm text-blue-600 dark:text-blue-400">
                  Enable period comparison by selecting a date column. This will show change vs previous period.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Date Column (Optional)</label>
                  <select
                    value={dateColumn}
                    onChange={e => setDateColumn(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                  >
                    <option value="">No comparison</option>
                    {columns.filter(c =>
                      c.type?.toLowerCase().includes('date') ||
                      c.type?.toLowerCase().includes('time') ||
                      c.name.toLowerCase().includes('date') ||
                      c.name.toLowerCase().includes('created') ||
                      c.name.toLowerCase().includes('updated')
                    ).map(c => (
                      <option key={c.name} value={c.name}>{c.name}</option>
                    ))}
                    {/* Also show all columns as fallback */}
                    <optgroup label="All Columns">
                      {columns.map(c => (
                        <option key={c.name} value={c.name}>{c.name}</option>
                      ))}
                    </optgroup>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Compare To</label>
                  <select
                    value={comparisonPeriod}
                    onChange={e => setComparisonPeriod(e.target.value as ComparisonPeriod)}
                    disabled={!dateColumn}
                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 disabled:opacity-50"
                  >
                    <option value="previous_day">Previous Day</option>
                    <option value="previous_week">Previous Week</option>
                    <option value="previous_month">Previous Month</option>
                    <option value="previous_quarter">Previous Quarter</option>
                    <option value="previous_year">Previous Year</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="w-5 h-5 text-purple-500" />
                  <span className="font-medium text-gray-900 dark:text-white">Goal / Target (Optional)</span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Goal Value</label>
                    <input
                      type="number"
                      value={goalValue || ''}
                      onChange={e => setGoalValue(e.target.value ? Number(e.target.value) : undefined)}
                      placeholder="e.g., 1000000"
                      className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Goal Label</label>
                    <input
                      type="text"
                      value={goalLabel}
                      onChange={e => setGoalLabel(e.target.value)}
                      placeholder="e.g., Q4 Target"
                      className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Preview */}
          {step === 4 && (
            <div className="space-y-6">
              <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">Preview</h3>
                <div className="max-w-sm mx-auto">
                  <KPICard config={buildConfig()} showMenu={false} />
                </div>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Configuration</h3>
                <pre className="text-xs text-gray-600 dark:text-gray-400 overflow-auto">
                  {JSON.stringify(buildConfig(), null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <button
            onClick={() => step > 1 && setStep(step - 1)}
            disabled={step === 1}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
          >
            Back
          </button>

          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              Cancel
            </button>

            {step < 4 ? (
              <button
                onClick={() => setStep(step + 1)}
                disabled={!isStepValid(step)}
                className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
              >
                Add KPI
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default KPIBuilder
