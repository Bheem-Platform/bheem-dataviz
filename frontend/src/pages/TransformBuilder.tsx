import React, { useState, useEffect, useRef } from 'react'
import {
  Database,
  Table2,
  ChevronRight,
  ChevronLeft,
  ChevronDown,
  ChevronUp,
  Loader2,
  ArrowLeft,
  Plus,
  Trash2,
  Play,
  Save,
  Filter,
  ArrowUpDown,
  Columns,
  Calculator,
  Link2,
  Scissors,
  Type,
  Hash,
  Calendar,
  ToggleLeft,
  GripVertical,
  Eye,
  Code,
  Copy,
  Check,
  X,
  RefreshCw,
  Layers,
  Wand2,
  Clock,
  MoreVertical,
  Edit3,
  Star,
  ChevronsLeft,
  ChevronsRight,
  Eraser,
  ListOrdered,
  Merge,
  MinusSquare,
  PlusSquare,
} from 'lucide-react'
import { SiPostgresql, SiMysql } from 'react-icons/si'
import { FaFileCsv, FaFileExcel } from 'react-icons/fa'
import { IconType } from 'react-icons'

const API_BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1'

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
  reference_count: number
  is_important: boolean
}

interface ColumnInfo {
  name: string
  type: string
  nullable: boolean
}

interface TransformStep {
  id: string
  type: string
  config: Record<string, any>
  expanded: boolean
}

interface PreviewResult {
  columns: { name: string; type: string }[]
  rows: Record<string, any>[]
  total_rows: number
  preview_rows: number
  execution_time_ms: number
  sql_generated?: string
}

interface SavedRecipe {
  id: string
  name: string
  description: string | null
  connection_id: string
  source_table: string
  source_schema: string
  steps: any[]
  row_count: number | null
  last_executed: string | null
  execution_time_ms: number | null
  created_at: string
  updated_at: string
}

type ViewMode = 'list' | 'builder'

// Constants
const connectionTypeIcons: Record<string, { icon: IconType; color: string }> = {
  postgresql: { icon: SiPostgresql, color: '#336791' },
  mysql: { icon: SiMysql, color: '#4479A1' },
  csv: { icon: FaFileCsv, color: '#22C55E' },
  excel: { icon: FaFileExcel, color: '#217346' },
}

const STEP_TYPES = [
  { type: 'select', label: 'Select Columns', icon: Columns, description: 'Choose which columns to include' },
  { type: 'filter', label: 'Filter Rows', icon: Filter, description: 'Filter data based on conditions' },
  { type: 'sort', label: 'Sort', icon: ArrowUpDown, description: 'Order rows by column values' },
  { type: 'group_by', label: 'Group & Aggregate', icon: Calculator, description: 'Group data and calculate aggregates' },
  { type: 'join', label: 'Join Tables', icon: Link2, description: 'Combine with another table' },
  { type: 'union', label: 'Union Tables', icon: Merge, description: 'Stack rows from another table' },
  { type: 'rename', label: 'Rename Columns', icon: Type, description: 'Change column names' },
  { type: 'reorder', label: 'Reorder Columns', icon: ListOrdered, description: 'Change column order' },
  { type: 'cast', label: 'Change Type', icon: Hash, description: 'Convert column data types' },
  { type: 'add_column', label: 'Add Column', icon: PlusSquare, description: 'Create calculated column' },
  { type: 'drop_column', label: 'Drop Columns', icon: MinusSquare, description: 'Remove columns from data' },
  { type: 'deduplicate', label: 'Remove Duplicates', icon: Layers, description: 'Remove duplicate rows' },
  { type: 'limit', label: 'Limit Rows', icon: Scissors, description: 'Take first N rows' },
  { type: 'fill_null', label: 'Fill Nulls', icon: Eraser, description: 'Replace null values' },
  { type: 'replace', label: 'Replace Values', icon: RefreshCw, description: 'Find and replace values' },
  { type: 'trim', label: 'Trim Whitespace', icon: Scissors, description: 'Remove leading/trailing spaces' },
  { type: 'case', label: 'Change Case', icon: Type, description: 'Convert text case' },
]

const FILTER_OPERATORS = [
  { value: '=', label: 'equals' },
  { value: '!=', label: 'not equals' },
  { value: '>', label: 'greater than' },
  { value: '>=', label: 'greater or equal' },
  { value: '<', label: 'less than' },
  { value: '<=', label: 'less or equal' },
  { value: 'like', label: 'contains' },
  { value: 'is_null', label: 'is null' },
  { value: 'is_not_null', label: 'is not null' },
]

const AGG_FUNCTIONS = [
  { value: 'sum', label: 'Sum' },
  { value: 'count', label: 'Count' },
  { value: 'avg', label: 'Average' },
  { value: 'min', label: 'Minimum' },
  { value: 'max', label: 'Maximum' },
  { value: 'count_distinct', label: 'Count Distinct' },
]

const DATA_TYPES = [
  { value: 'text', label: 'Text' },
  { value: 'integer', label: 'Integer' },
  { value: 'decimal', label: 'Decimal' },
  { value: 'boolean', label: 'Boolean' },
  { value: 'date', label: 'Date' },
  { value: 'timestamp', label: 'Timestamp' },
]

function getColumnIcon(type: string) {
  const t = type.toLowerCase()
  if (t.includes('int') || t.includes('numeric') || t.includes('decimal') || t.includes('float')) {
    return <Hash className="w-3.5 h-3.5 text-blue-500" />
  }
  if (t.includes('time') || t.includes('date')) {
    return <Calendar className="w-3.5 h-3.5 text-purple-500" />
  }
  if (t.includes('bool')) {
    return <ToggleLeft className="w-3.5 h-3.5 text-green-500" />
  }
  return <Type className="w-3.5 h-3.5 text-gray-500" />
}

export function TransformBuilder() {
  // View Mode
  const [viewMode, setViewMode] = useState<ViewMode>('list')

  // Saved Recipes State
  const [savedRecipes, setSavedRecipes] = useState<SavedRecipe[]>([])
  const [loadingRecipes, setLoadingRecipes] = useState(true)
  const [editingRecipe, setEditingRecipe] = useState<SavedRecipe | null>(null)

  // Connection & Table State
  const [connections, setConnections] = useState<Connection[]>([])
  const [selectedConnection, setSelectedConnection] = useState<Connection | null>(null)
  const [tables, setTables] = useState<TableInfo[]>([])
  const [selectedTable, setSelectedTable] = useState<TableInfo | null>(null)
  const [columns, setColumns] = useState<ColumnInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingTables, setLoadingTables] = useState(false)
  const [loadingColumns, setLoadingColumns] = useState(false)
  const [showAllTables, setShowAllTables] = useState(false)

  // Transform State
  const [steps, setSteps] = useState<TransformStep[]>([])
  const [showAddStep, setShowAddStep] = useState(false)

  // Preview State
  const [preview, setPreview] = useState<PreviewResult | null>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [showSQL, setShowSQL] = useState(false)
  const [copiedSQL, setCopiedSQL] = useState(false)

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1)
  const [rowsPerPage, setRowsPerPage] = useState(100)

  // Recipe State
  const [recipeName, setRecipeName] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  // Fetch connections and recipes on mount
  useEffect(() => {
    fetchConnections()
    fetchSavedRecipes()
  }, [])

  // Fetch tables when connection changes
  useEffect(() => {
    if (selectedConnection) {
      fetchTables(selectedConnection.id)
    }
  }, [selectedConnection])

  // Fetch columns when table changes
  useEffect(() => {
    if (selectedConnection && selectedTable) {
      fetchColumns(selectedConnection.id, selectedTable.schema_name, selectedTable.name)
      // Reset steps when table changes
      setSteps([])
      setPreview(null)
      setCurrentPage(1)
    }
  }, [selectedTable])

  // Helper to navigate pages and refetch
  const goToPage = (page: number) => {
    if (page < 1) page = 1
    const maxPage = preview ? Math.ceil(preview.total_rows / rowsPerPage) : 1
    if (page > maxPage) page = maxPage
    if (page === currentPage) return
    setCurrentPage(page)
  }

  // Refetch preview when pagination changes (only for actual page navigation, not initial preview)
  const prevPageRef = useRef(currentPage)
  const prevRowsPerPageRef = useRef(rowsPerPage)
  useEffect(() => {
    const pageChanged = prevPageRef.current !== currentPage
    const rowsChanged = prevRowsPerPageRef.current !== rowsPerPage
    prevPageRef.current = currentPage
    prevRowsPerPageRef.current = rowsPerPage

    if ((pageChanged || rowsChanged) && preview && selectedConnection && selectedTable) {
      executePreview()
    }
  }, [currentPage, rowsPerPage])

  const fetchConnections = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/connections/`)
      if (response.ok) {
        const data = await response.json()
        setConnections(data.filter((c: Connection) => c.status === 'connected'))
      }
    } catch (error) {
      console.error('Failed to fetch connections:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSavedRecipes = async () => {
    try {
      setLoadingRecipes(true)
      const response = await fetch(`${API_BASE_URL}/transforms/`)
      if (response.ok) {
        const data = await response.json()
        setSavedRecipes(data)
      }
    } catch (error) {
      console.error('Failed to fetch recipes:', error)
    } finally {
      setLoadingRecipes(false)
    }
  }

  const deleteRecipe = async (recipeId: string) => {
    if (!confirm('Are you sure you want to delete this recipe?')) return

    try {
      const response = await fetch(`${API_BASE_URL}/transforms/${recipeId}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        fetchSavedRecipes()
      }
    } catch (error) {
      console.error('Failed to delete recipe:', error)
    }
  }

  const startNewRecipe = () => {
    setEditingRecipe(null)
    setSelectedConnection(null)
    setSelectedTable(null)
    setSteps([])
    setPreview(null)
    setRecipeName('')
    setShowAllTables(false)
    setViewMode('builder')
  }

  const editRecipe = async (recipe: SavedRecipe) => {
    setEditingRecipe(recipe)
    setRecipeName(recipe.name)

    // Find and set the connection
    const conn = connections.find(c => c.id === recipe.connection_id)
    if (conn) {
      setSelectedConnection(conn)

      // Fetch tables for this connection
      await fetchTables(conn.id)

      // Set the table
      if (recipe.source_table) {
        setSelectedTable({
          schema_name: recipe.source_schema,
          name: recipe.source_table,
          type: 'TABLE',
          reference_count: 0,
          is_important: false,
        })
      }

      // Convert recipe steps to TransformStep format
      const transformSteps: TransformStep[] = recipe.steps.map((step, idx) => ({
        id: `step-${idx}-${Date.now()}`,
        type: step.type,
        config: { ...step },
        expanded: true,
      }))
      // Remove the 'type' from config since it's stored separately
      transformSteps.forEach(s => {
        delete s.config.type
      })
      setSteps(transformSteps)
    }

    setViewMode('builder')
  }

  const fetchTables = async (connectionId: string) => {
    setLoadingTables(true)
    try {
      const response = await fetch(`${API_BASE_URL}/connections/${connectionId}/tables`)
      if (response.ok) {
        setTables(await response.json())
      }
    } catch (error) {
      console.error('Failed to fetch tables:', error)
    } finally {
      setLoadingTables(false)
    }
  }

  const fetchColumns = async (connectionId: string, schema: string, table: string) => {
    setLoadingColumns(true)
    try {
      const response = await fetch(`${API_BASE_URL}/connections/${connectionId}/tables/${schema}/${table}/columns`)
      if (response.ok) {
        setColumns(await response.json())
      }
    } catch (error) {
      console.error('Failed to fetch columns:', error)
    } finally {
      setLoadingColumns(false)
    }
  }

  const addStep = (type: string) => {
    const newStep: TransformStep = {
      id: `step-${Date.now()}`,
      type,
      config: getDefaultConfig(type),
      expanded: true,
    }
    setSteps([...steps, newStep])
    setShowAddStep(false)
  }

  const getDefaultConfig = (type: string): Record<string, any> => {
    switch (type) {
      case 'select':
        return { columns: columns.map(c => c.name) }
      case 'filter':
        return { conditions: [{ column: '', operator: '=', value: '' }], logic: 'and' }
      case 'sort':
        return { columns: [{ column: '', direction: 'asc' }] }
      case 'group_by':
        return { columns: [], aggregations: [{ column: '', function: 'count', alias: '' }] }
      case 'join':
        return { table: '', schema_name: selectedTable?.schema_name || 'public', join_type: 'left', on: [{ left: '', right: '' }], select_columns: [] }
      case 'union':
        return { table: '', schema_name: selectedTable?.schema_name || 'public', all: true }
      case 'rename':
        return { mapping: {}, _renameFrom: '', _renameTo: '' }
      case 'reorder':
        return { columns: columns.map(c => c.name) }
      case 'cast':
        return { column: '', to_type: 'text' }
      case 'add_column':
        return { name: '', expression: '' }
      case 'drop_column':
        return { columns: [] }
      case 'deduplicate':
        return { columns: null }
      case 'limit':
        return { count: 100, offset: 0 }
      case 'fill_null':
        return { column: '', value: '' }
      case 'replace':
        return { column: '', find: '', replace_with: '' }
      case 'trim':
        return { columns: [] }
      case 'case':
        return { column: '', to: 'upper' }
      default:
        return {}
    }
  }

  const updateStep = (stepId: string, config: Record<string, any>) => {
    setSteps(steps.map(s => s.id === stepId ? { ...s, config } : s))
  }

  const removeStep = (stepId: string) => {
    setSteps(steps.filter(s => s.id !== stepId))
  }

  const toggleStepExpanded = (stepId: string) => {
    setSteps(steps.map(s => s.id === stepId ? { ...s, expanded: !s.expanded } : s))
  }

  const executePreview = async () => {
    // Validate based on source type
    if (!selectedConnection || !selectedTable) return

    setLoadingPreview(true)
    try {
      // Clean steps before sending - remove incomplete filter conditions, sort columns, etc.
      const cleanedSteps = steps.map(s => {
        const stepData: any = { type: s.type, ...s.config }

        // Clean filter conditions - remove those without a column selected
        if (s.type === 'filter' && stepData.conditions) {
          stepData.conditions = stepData.conditions.filter(
            (c: any) => c.column && c.column.trim() !== ''
          )
        }

        // Clean sort columns - remove those without a column selected
        if (s.type === 'sort' && stepData.columns) {
          stepData.columns = stepData.columns.filter(
            (c: any) => c.column && c.column.trim() !== ''
          )
        }

        // Clean group_by columns
        if (s.type === 'group_by' && stepData.columns) {
          stepData.columns = stepData.columns.filter((c: string) => c && c.trim() !== '')
        }

        // Clean rename - remove internal fields
        if (s.type === 'rename') {
          delete stepData._renameFrom
          delete stepData._renameTo
        }

        // Clean join - remove empty conditions
        if (s.type === 'join' && stepData.on) {
          stepData.on = stepData.on.filter((c: any) => c.left && c.right)
        }

        return stepData
      })

      const offset = (currentPage - 1) * rowsPerPage

      const body = {
        connection_id: selectedConnection.id,
        source_table: selectedTable.name,
        source_schema: selectedTable.schema_name,
        steps: cleanedSteps,
        preview: true,
        limit: rowsPerPage,
        offset: offset,
      }

      const response = await fetch(`${API_BASE_URL}/transforms/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (response.ok) {
        const data = await response.json()
        setPreview(data)
      } else {
        const error = await response.json()
        alert(`Preview failed: ${error.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Preview failed:', error)
      alert('Preview failed')
    } finally {
      setLoadingPreview(false)
    }
  }

  const saveRecipe = async () => {
    if (!recipeName.trim()) {
      alert('Please enter a recipe name')
      return
    }

    if (!selectedConnection || !selectedTable) {
      alert('Please select a connection and table')
      return
    }

    setSaving(true)
    try {
      // Clean steps before saving - remove incomplete conditions
      const cleanedSteps = steps.map(s => {
        const stepData: any = { type: s.type, ...s.config }

        if (s.type === 'filter' && stepData.conditions) {
          stepData.conditions = stepData.conditions.filter(
            (c: any) => c.column && c.column.trim() !== ''
          )
        }

        if (s.type === 'sort' && stepData.columns) {
          stepData.columns = stepData.columns.filter(
            (c: any) => c.column && c.column.trim() !== ''
          )
        }

        if (s.type === 'group_by' && stepData.columns) {
          stepData.columns = stepData.columns.filter((c: string) => c && c.trim() !== '')
        }

        // Clean rename - remove internal fields
        if (s.type === 'rename') {
          delete stepData._renameFrom
          delete stepData._renameTo
        }

        // Clean join - remove empty conditions
        if (s.type === 'join' && stepData.on) {
          stepData.on = stepData.on.filter((c: any) => c.left && c.right)
        }

        return stepData
      })

      const isUpdate = !!editingRecipe
      const url = isUpdate
        ? `${API_BASE_URL}/transforms/${editingRecipe.id}`
        : `${API_BASE_URL}/transforms/`

      const body = {
        name: recipeName,
        connection_id: selectedConnection.id,
        source_table: selectedTable.name,
        source_schema: selectedTable.schema_name,
        steps: cleanedSteps,
      }

      const response = await fetch(url, {
        method: isUpdate ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (response.ok) {
        setSaveSuccess(true)
        // Refresh the recipes list
        await fetchSavedRecipes()
        // Switch back to list view after a brief delay
        setTimeout(() => {
          setSaveSuccess(false)
          setViewMode('list')
          setEditingRecipe(null)
        }, 1500)
      } else {
        const error = await response.json()
        alert(`Save failed: ${error.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Save failed:', error)
      alert('Save failed: Network error')
    } finally {
      setSaving(false)
    }
  }

  const copySQL = () => {
    if (preview?.sql_generated) {
      navigator.clipboard.writeText(preview.sql_generated)
      setCopiedSQL(true)
      setTimeout(() => setCopiedSQL(false), 2000)
    }
  }

  // Render step editor based on type
  const renderStepEditor = (step: TransformStep) => {
    switch (step.type) {
      case 'select':
        return (
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Select columns to include:</label>
            <div className="flex flex-wrap gap-2">
              {columns.map(col => (
                <label key={col.name} className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600">
                  <input
                    type="checkbox"
                    checked={step.config.columns?.includes(col.name)}
                    onChange={(e) => {
                      const cols = step.config.columns || []
                      if (e.target.checked) {
                        updateStep(step.id, { columns: [...cols, col.name] })
                      } else {
                        updateStep(step.id, { columns: cols.filter((c: string) => c !== col.name) })
                      }
                    }}
                    className="w-3.5 h-3.5 text-primary-500 rounded"
                  />
                  {getColumnIcon(col.type)}
                  <span className="text-sm text-gray-700 dark:text-gray-300">{col.name}</span>
                </label>
              ))}
            </div>
          </div>
        )

      case 'filter':
        return (
          <div className="space-y-3">
            {step.config.conditions?.map((cond: any, idx: number) => (
              <div key={idx} className="flex items-center gap-2">
                {idx > 0 && (
                  <select
                    value={step.config.logic}
                    onChange={(e) => updateStep(step.id, { ...step.config, logic: e.target.value })}
                    className="px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="and">AND</option>
                    <option value="or">OR</option>
                  </select>
                )}
                <select
                  value={cond.column}
                  onChange={(e) => {
                    const newConds = [...step.config.conditions]
                    newConds[idx] = { ...cond, column: e.target.value }
                    updateStep(step.id, { ...step.config, conditions: newConds })
                  }}
                  className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="">Select column...</option>
                  {columns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
                </select>
                <select
                  value={cond.operator}
                  onChange={(e) => {
                    const newConds = [...step.config.conditions]
                    newConds[idx] = { ...cond, operator: e.target.value }
                    updateStep(step.id, { ...step.config, conditions: newConds })
                  }}
                  className="px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {FILTER_OPERATORS.map(op => <option key={op.value} value={op.value}>{op.label}</option>)}
                </select>
                {!['is_null', 'is_not_null'].includes(cond.operator) && (
                  <input
                    type="text"
                    value={cond.value}
                    onChange={(e) => {
                      const newConds = [...step.config.conditions]
                      newConds[idx] = { ...cond, value: e.target.value }
                      updateStep(step.id, { ...step.config, conditions: newConds })
                    }}
                    placeholder="Value..."
                    className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                )}
                <button
                  onClick={() => {
                    const newConds = step.config.conditions.filter((_: any, i: number) => i !== idx)
                    updateStep(step.id, { ...step.config, conditions: newConds })
                  }}
                  className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
            <button
              onClick={() => {
                const newConds = [...(step.config.conditions || []), { column: '', operator: '=', value: '' }]
                updateStep(step.id, { ...step.config, conditions: newConds })
              }}
              className="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add condition
            </button>
          </div>
        )

      case 'sort':
        return (
          <div className="space-y-3">
            {step.config.columns?.map((sort: any, idx: number) => (
              <div key={idx} className="flex items-center gap-2">
                <select
                  value={sort.column}
                  onChange={(e) => {
                    const newCols = [...step.config.columns]
                    newCols[idx] = { ...sort, column: e.target.value }
                    updateStep(step.id, { ...step.config, columns: newCols })
                  }}
                  className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="">Select column...</option>
                  {columns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
                </select>
                <select
                  value={sort.direction}
                  onChange={(e) => {
                    const newCols = [...step.config.columns]
                    newCols[idx] = { ...sort, direction: e.target.value }
                    updateStep(step.id, { ...step.config, columns: newCols })
                  }}
                  className="px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="asc">Ascending</option>
                  <option value="desc">Descending</option>
                </select>
                <button
                  onClick={() => {
                    const newCols = step.config.columns.filter((_: any, i: number) => i !== idx)
                    updateStep(step.id, { ...step.config, columns: newCols })
                  }}
                  className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
            <button
              onClick={() => {
                const newCols = [...(step.config.columns || []), { column: '', direction: 'asc' }]
                updateStep(step.id, { ...step.config, columns: newCols })
              }}
              className="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add sort column
            </button>
          </div>
        )

      case 'group_by':
        return (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Group by columns:</label>
              <div className="flex flex-wrap gap-2">
                {columns.map(col => (
                  <label key={col.name} className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600">
                    <input
                      type="checkbox"
                      checked={step.config.columns?.includes(col.name)}
                      onChange={(e) => {
                        const cols = step.config.columns || []
                        if (e.target.checked) {
                          updateStep(step.id, { ...step.config, columns: [...cols, col.name] })
                        } else {
                          updateStep(step.id, { ...step.config, columns: cols.filter((c: string) => c !== col.name) })
                        }
                      }}
                      className="w-3.5 h-3.5 text-primary-500 rounded"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{col.name}</span>
                  </label>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Aggregations:</label>
              <div className="space-y-2">
                {step.config.aggregations?.map((agg: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-2">
                    <select
                      value={agg.function}
                      onChange={(e) => {
                        const newAggs = [...step.config.aggregations]
                        newAggs[idx] = { ...agg, function: e.target.value }
                        updateStep(step.id, { ...step.config, aggregations: newAggs })
                      }}
                      className="px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      {AGG_FUNCTIONS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
                    </select>
                    <select
                      value={agg.column}
                      onChange={(e) => {
                        const newAggs = [...step.config.aggregations]
                        newAggs[idx] = { ...agg, column: e.target.value, alias: agg.alias || `${agg.function}_${e.target.value}` }
                        updateStep(step.id, { ...step.config, aggregations: newAggs })
                      }}
                      className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Select column...</option>
                      {columns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
                    </select>
                    <span className="text-sm text-gray-500">as</span>
                    <input
                      type="text"
                      value={agg.alias}
                      onChange={(e) => {
                        const newAggs = [...step.config.aggregations]
                        newAggs[idx] = { ...agg, alias: e.target.value }
                        updateStep(step.id, { ...step.config, aggregations: newAggs })
                      }}
                      placeholder="Alias..."
                      className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <button
                      onClick={() => {
                        const newAggs = step.config.aggregations.filter((_: any, i: number) => i !== idx)
                        updateStep(step.id, { ...step.config, aggregations: newAggs })
                      }}
                      className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => {
                    const newAggs = [...(step.config.aggregations || []), { column: '', function: 'sum', alias: '' }]
                    updateStep(step.id, { ...step.config, aggregations: newAggs })
                  }}
                  className="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1"
                >
                  <Plus className="w-3.5 h-3.5" /> Add aggregation
                </button>
              </div>
            </div>
          </div>
        )

      case 'cast':
        return (
          <div className="flex items-center gap-3">
            <select
              value={step.config.column}
              onChange={(e) => updateStep(step.id, { ...step.config, column: e.target.value })}
              className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Select column...</option>
              {columns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
            </select>
            <span className="text-sm text-gray-500">to</span>
            <select
              value={step.config.to_type}
              onChange={(e) => updateStep(step.id, { ...step.config, to_type: e.target.value })}
              className="px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {DATA_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
        )

      case 'fill_null':
        return (
          <div className="flex items-center gap-3">
            <select
              value={step.config.column}
              onChange={(e) => updateStep(step.id, { ...step.config, column: e.target.value })}
              className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Select column...</option>
              {columns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
            </select>
            <span className="text-sm text-gray-500">with</span>
            <input
              type="text"
              value={step.config.value}
              onChange={(e) => updateStep(step.id, { ...step.config, value: e.target.value })}
              placeholder="Replacement value..."
              className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        )

      case 'rename':
        return (
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2 mb-2">
              {Object.entries(step.config.mapping || {}).map(([oldName, newName]) => (
                <div key={oldName} className="flex items-center gap-1 px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 rounded text-sm">
                  <span className="text-gray-700 dark:text-gray-300">{oldName}</span>
                  <span className="text-gray-500">→</span>
                  <span className="font-medium text-indigo-600 dark:text-indigo-400">{newName as string}</span>
                  <button
                    onClick={() => {
                      const newMapping = { ...step.config.mapping }
                      delete newMapping[oldName]
                      updateStep(step.id, { ...step.config, mapping: newMapping })
                    }}
                    className="ml-1 text-red-500 hover:text-red-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <select
                value={step.config._renameFrom || ''}
                onChange={(e) => updateStep(step.id, { ...step.config, _renameFrom: e.target.value })}
                className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Select column...</option>
                {columns.filter(c => !step.config.mapping?.[c.name]).map(c => (
                  <option key={c.name} value={c.name}>{c.name}</option>
                ))}
              </select>
              <span className="text-sm text-gray-500">to</span>
              <input
                type="text"
                value={step.config._renameTo || ''}
                onChange={(e) => updateStep(step.id, { ...step.config, _renameTo: e.target.value })}
                placeholder="New name..."
                className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <button
                onClick={() => {
                  if (step.config._renameFrom && step.config._renameTo) {
                    const newMapping = { ...step.config.mapping, [step.config._renameFrom]: step.config._renameTo }
                    updateStep(step.id, { ...step.config, mapping: newMapping, _renameFrom: '', _renameTo: '' })
                  }
                }}
                disabled={!step.config._renameFrom || !step.config._renameTo}
                className="px-3 py-1.5 text-sm bg-primary-500 text-white rounded hover:bg-primary-600 disabled:opacity-50"
              >
                Add
              </button>
            </div>
          </div>
        )

      case 'reorder':
        return (
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Drag columns to reorder:</label>
            <div className="space-y-1">
              {(step.config.columns || []).map((col: string, idx: number) => (
                <div key={col} className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded">
                  <GripVertical className="w-4 h-4 text-gray-400" />
                  <span className="flex-1 text-sm text-gray-900 dark:text-white">{col}</span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => {
                        if (idx > 0) {
                          const newCols = [...step.config.columns]
                          ;[newCols[idx - 1], newCols[idx]] = [newCols[idx], newCols[idx - 1]]
                          updateStep(step.id, { ...step.config, columns: newCols })
                        }
                      }}
                      disabled={idx === 0}
                      className="p-1 text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-600 rounded disabled:opacity-30"
                    >
                      <ChevronUp className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => {
                        if (idx < step.config.columns.length - 1) {
                          const newCols = [...step.config.columns]
                          ;[newCols[idx], newCols[idx + 1]] = [newCols[idx + 1], newCols[idx]]
                          updateStep(step.id, { ...step.config, columns: newCols })
                        }
                      }}
                      disabled={idx === step.config.columns.length - 1}
                      className="p-1 text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-600 rounded disabled:opacity-30"
                    >
                      <ChevronDown className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )

      case 'add_column':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <input
                type="text"
                value={step.config.name || ''}
                onChange={(e) => updateStep(step.id, { ...step.config, name: e.target.value })}
                placeholder="Column name..."
                className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">Expression:</label>
              <input
                type="text"
                value={step.config.expression || ''}
                onChange={(e) => updateStep(step.id, { ...step.config, expression: e.target.value })}
                placeholder="e.g., quantity * price"
                className="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">Use column names and basic math operators (+, -, *, /)</p>
            </div>
          </div>
        )

      case 'drop_column':
        return (
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Select columns to remove:</label>
            <div className="flex flex-wrap gap-2">
              {columns.map(col => (
                <label key={col.name} className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600">
                  <input
                    type="checkbox"
                    checked={step.config.columns?.includes(col.name)}
                    onChange={(e) => {
                      const cols = step.config.columns || []
                      if (e.target.checked) {
                        updateStep(step.id, { columns: [...cols, col.name] })
                      } else {
                        updateStep(step.id, { columns: cols.filter((c: string) => c !== col.name) })
                      }
                    }}
                    className="w-3.5 h-3.5 text-red-500 rounded"
                  />
                  {getColumnIcon(col.type)}
                  <span className="text-sm text-gray-700 dark:text-gray-300">{col.name}</span>
                </label>
              ))}
            </div>
          </div>
        )

      case 'deduplicate':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="dedupe-all"
                checked={step.config.columns === null}
                onChange={(e) => {
                  if (e.target.checked) {
                    updateStep(step.id, { columns: null })
                  } else {
                    updateStep(step.id, { columns: [] })
                  }
                }}
                className="w-4 h-4 text-primary-500 rounded"
              />
              <label htmlFor="dedupe-all" className="text-sm text-gray-700 dark:text-gray-300">
                Remove duplicates based on all columns
              </label>
            </div>
            {step.config.columns !== null && (
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                  Or select specific columns:
                </label>
                <div className="flex flex-wrap gap-2">
                  {columns.map(col => (
                    <label key={col.name} className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600">
                      <input
                        type="checkbox"
                        checked={step.config.columns?.includes(col.name)}
                        onChange={(e) => {
                          const cols = step.config.columns || []
                          if (e.target.checked) {
                            updateStep(step.id, { columns: [...cols, col.name] })
                          } else {
                            updateStep(step.id, { columns: cols.filter((c: string) => c !== col.name) })
                          }
                        }}
                        className="w-3.5 h-3.5 text-primary-500 rounded"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{col.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      case 'limit':
        return (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-700 dark:text-gray-300">Take first</label>
              <input
                type="number"
                min={1}
                value={step.config.count || 100}
                onChange={(e) => updateStep(step.id, { ...step.config, count: parseInt(e.target.value) || 100 })}
                className="w-24 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <label className="text-sm text-gray-700 dark:text-gray-300">rows</label>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-700 dark:text-gray-300">skip</label>
              <input
                type="number"
                min={0}
                value={step.config.offset || 0}
                onChange={(e) => updateStep(step.id, { ...step.config, offset: parseInt(e.target.value) || 0 })}
                className="w-24 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
        )

      case 'replace':
        return (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">In</span>
            <select
              value={step.config.column || ''}
              onChange={(e) => updateStep(step.id, { ...step.config, column: e.target.value })}
              className="px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Select column...</option>
              {columns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
            </select>
            <span className="text-sm text-gray-500">find</span>
            <input
              type="text"
              value={step.config.find || ''}
              onChange={(e) => updateStep(step.id, { ...step.config, find: e.target.value })}
              placeholder="Find..."
              className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <span className="text-sm text-gray-500">replace with</span>
            <input
              type="text"
              value={step.config.replace_with || ''}
              onChange={(e) => updateStep(step.id, { ...step.config, replace_with: e.target.value })}
              placeholder="Replace..."
              className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        )

      case 'trim':
        return (
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Select columns to trim whitespace:</label>
            <div className="flex flex-wrap gap-2">
              {columns.filter(c => c.type.toLowerCase().includes('char') || c.type.toLowerCase().includes('text') || c.type.toLowerCase().includes('varchar')).map(col => (
                <label key={col.name} className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600">
                  <input
                    type="checkbox"
                    checked={step.config.columns?.includes(col.name)}
                    onChange={(e) => {
                      const cols = step.config.columns || []
                      if (e.target.checked) {
                        updateStep(step.id, { columns: [...cols, col.name] })
                      } else {
                        updateStep(step.id, { columns: cols.filter((c: string) => c !== col.name) })
                      }
                    }}
                    className="w-3.5 h-3.5 text-primary-500 rounded"
                  />
                  <Type className="w-3.5 h-3.5 text-gray-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">{col.name}</span>
                </label>
              ))}
              {columns.filter(c => !c.type.toLowerCase().includes('char') && !c.type.toLowerCase().includes('text') && !c.type.toLowerCase().includes('varchar')).length === columns.length && (
                <span className="text-sm text-gray-500 italic">No text columns found</span>
              )}
            </div>
          </div>
        )

      case 'case':
        return (
          <div className="flex items-center gap-3">
            <select
              value={step.config.column || ''}
              onChange={(e) => updateStep(step.id, { ...step.config, column: e.target.value })}
              className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Select column...</option>
              {columns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
            </select>
            <span className="text-sm text-gray-500">to</span>
            <select
              value={step.config.to || 'upper'}
              onChange={(e) => updateStep(step.id, { ...step.config, to: e.target.value })}
              className="px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="upper">UPPERCASE</option>
              <option value="lower">lowercase</option>
              <option value="title">Title Case</option>
            </select>
          </div>
        )

      case 'join':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <select
                value={step.config.join_type || 'left'}
                onChange={(e) => updateStep(step.id, { ...step.config, join_type: e.target.value })}
                className="px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="inner">Inner Join</option>
                <option value="left">Left Join</option>
                <option value="right">Right Join</option>
                <option value="full">Full Join</option>
              </select>
              <span className="text-sm text-gray-500">with</span>
              <select
                value={step.config.table || ''}
                onChange={(e) => updateStep(step.id, { ...step.config, table: e.target.value })}
                className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Select table...</option>
                {tables.map(t => (
                  <option key={`${t.schema_name}.${t.name}`} value={t.name}>{t.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Join conditions:</label>
              {step.config.on?.map((cond: any, idx: number) => (
                <div key={idx} className="flex items-center gap-2 mb-2">
                  <select
                    value={cond.left || ''}
                    onChange={(e) => {
                      const newOn = [...step.config.on]
                      newOn[idx] = { ...cond, left: e.target.value }
                      updateStep(step.id, { ...step.config, on: newOn })
                    }}
                    className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="">Source column...</option>
                    {columns.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
                  </select>
                  <span className="text-sm text-gray-500">=</span>
                  <input
                    type="text"
                    value={cond.right || ''}
                    onChange={(e) => {
                      const newOn = [...step.config.on]
                      newOn[idx] = { ...cond, right: e.target.value }
                      updateStep(step.id, { ...step.config, on: newOn })
                    }}
                    placeholder="Target column..."
                    className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                  <button
                    onClick={() => {
                      const newOn = step.config.on.filter((_: any, i: number) => i !== idx)
                      updateStep(step.id, { ...step.config, on: newOn })
                    }}
                    className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
              <button
                onClick={() => {
                  const newOn = [...(step.config.on || []), { left: '', right: '' }]
                  updateStep(step.id, { ...step.config, on: newOn })
                }}
                className="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add condition
              </button>
            </div>
          </div>
        )

      case 'union':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500">Union with</span>
              <select
                value={step.config.table || ''}
                onChange={(e) => updateStep(step.id, { ...step.config, table: e.target.value })}
                className="flex-1 px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Select table...</option>
                {tables.map(t => (
                  <option key={`${t.schema_name}.${t.name}`} value={t.name}>{t.name}</option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="union-all"
                checked={step.config.all !== false}
                onChange={(e) => updateStep(step.id, { ...step.config, all: e.target.checked })}
                className="w-4 h-4 text-primary-500 rounded"
              />
              <label htmlFor="union-all" className="text-sm text-gray-700 dark:text-gray-300">
                Keep duplicate rows (UNION ALL)
              </label>
            </div>
          </div>
        )

      default:
        return <div className="text-sm text-gray-500">Editor not implemented for {step.type}</div>
    }
  }

  // ============================================================================
  // LIST VIEW - Show saved recipes
  // ============================================================================
  if (viewMode === 'list') {
    return (
      <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
        {/* Header */}
        <header className="px-8 py-6 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div className="w-10 h-10 rounded-md bg-primary-500 flex items-center justify-center">
                  <Wand2 className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Transform Recipes
                </h1>
              </div>
              <p className="text-gray-500 dark:text-gray-400 ml-13">
                Create and manage data transformation recipes
              </p>
            </div>
            <button
              onClick={startNewRecipe}
              className="flex items-center gap-2 px-4 py-2.5 bg-primary-500 text-white rounded-md font-medium hover:bg-indigo-800 transition-colors"
            >
              <Plus className="w-5 h-5" />
              New Recipe
            </button>
          </div>
        </header>

        {/* Recipe List */}
        <div className="flex-1 overflow-auto p-8">
          <div className="max-w-7xl mx-auto">
            {loadingRecipes ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
              </div>
            ) : savedRecipes.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-center">
                <div className="w-20 h-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-6">
                  <Wand2 className="w-10 h-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  No recipes yet
                </h3>
                <p className="text-gray-500 dark:text-gray-400 max-w-md mb-6">
                  Create your first transform recipe to prepare and shape your data for visualizations
                </p>
                <button
                  onClick={startNewRecipe}
                  className="flex items-center gap-2 px-6 py-3 bg-indigo-700 text-white rounded-md font-medium hover:bg-indigo-800 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                  Create Recipe
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {savedRecipes.map((recipe) => {
                  const conn = connections.find(c => c.id === recipe.connection_id)
                  return (
                    <div
                      key={recipe.id}
                      className="group bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-5 hover:shadow-lg hover:border-indigo-300 dark:hover:border-indigo-600 transition-all"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center">
                          <Wand2 className="w-6 h-6 text-indigo-500" />
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => editRecipe(recipe)}
                            className="p-2 text-gray-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-colors"
                            title="Edit"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deleteRecipe(recipe.id)}
                            className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1 truncate">
                        {recipe.name}
                      </h3>

                      {recipe.description && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">
                          {recipe.description}
                        </p>
                      )}

                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                          <Database className="w-4 h-4" />
                          <span className="truncate">{conn?.name || 'Unknown connection'}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                          <Table2 className="w-4 h-4" />
                          <span className="truncate">{recipe.source_schema}.{recipe.source_table}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="flex items-center gap-1.5 px-2 py-0.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-full text-xs">
                            <Layers className="w-3 h-3" />
                            {recipe.steps.length} steps
                          </span>
                          {recipe.row_count !== null && (
                            <span className="text-gray-400 text-xs">
                              {recipe.row_count.toLocaleString()} rows
                            </span>
                          )}
                        </div>
                      </div>

                      {recipe.last_executed && (
                        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center gap-1.5 text-xs text-gray-400">
                          <Clock className="w-3 h-3" />
                          Last run: {new Date(recipe.last_executed).toLocaleDateString()}
                        </div>
                      )}
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
  // BUILDER VIEW - Create/edit recipe
  // ============================================================================
  return (
    <div className="h-full flex bg-gray-50 dark:bg-gray-900">
      {/* Left Sidebar - Data Source */}
      <div className="w-72 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-primary-500" />
            Data Source
          </h2>
          <button
            onClick={() => setViewMode('list')}
            className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Back to list"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-4 space-y-4">
          {/* Connection Selector */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Connection</label>
            {loading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-5 h-5 animate-spin text-primary-500" />
              </div>
            ) : (
              <select
                value={selectedConnection?.id || ''}
                onChange={(e) => {
                  const conn = connections.find(c => c.id === e.target.value)
                  setSelectedConnection(conn || null)
                  setSelectedTable(null)
                  setTables([])
                  setColumns([])
                  setShowAllTables(false)
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Select connection...</option>
                {connections.map(conn => (
                  <option key={conn.id} value={conn.id}>{conn.name}</option>
                ))}
              </select>
            )}
          </div>

          {/* Table Selector */}
          {selectedConnection && (
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                Select Table
              </label>
              {loadingTables ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="w-5 h-5 animate-spin text-primary-500" />
                </div>
              ) : (
                (() => {
                  const importantTables = tables.filter(t => t.is_important)
                  const otherTables = tables.filter(t => !t.is_important)

                  return (
                    <div className="space-y-1">
                      {/* Important Tables */}
                      {importantTables.map(t => (
                        <button
                          key={`${t.schema_name}.${t.name}`}
                          onClick={() => {
                            setSelectedTable(t)
                            setShowAllTables(false)
                          }}
                          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-colors
                            ${selectedTable?.schema_name === t.schema_name && selectedTable?.name === t.name
                              ? 'bg-indigo-100 dark:bg-indigo-900/30 border border-indigo-500'
                              : 'hover:bg-gray-100 dark:hover:bg-gray-700 border border-transparent'}`}
                        >
                          <span className="text-yellow-500 flex items-center">
                            {Array.from({ length: Math.min(t.reference_count, 3) }).map((_, i) => (
                              <Star key={i} className="w-3 h-3 fill-current" />
                            ))}
                          </span>
                          <span className="flex-1 truncate text-sm text-gray-900 dark:text-white">{t.name}</span>
                          <span className="text-xs text-gray-500">
                            {t.reference_count} ref{t.reference_count !== 1 ? 's' : ''}
                          </span>
                        </button>
                      ))}

                      {/* Divider & Expand Button */}
                      {otherTables.length > 0 && (
                        <>
                          {importantTables.length > 0 && (
                            <div className="border-t border-gray-200 dark:border-gray-700 my-2" />
                          )}
                          <button
                            onClick={() => setShowAllTables(!showAllTables)}
                            className="w-full flex items-center gap-2 px-3 py-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                          >
                            {showAllTables ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                            <span className="text-sm">
                              {showAllTables ? 'Hide tables' : 'View all tables'} ({otherTables.length} more)
                            </span>
                          </button>
                        </>
                      )}

                      {/* Other Tables (collapsed by default) */}
                      {showAllTables && otherTables.map(t => (
                        <button
                          key={`${t.schema_name}.${t.name}`}
                          onClick={() => setSelectedTable(t)}
                          className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-colors
                            ${selectedTable?.schema_name === t.schema_name && selectedTable?.name === t.name
                              ? 'bg-indigo-100 dark:bg-indigo-900/30 border border-indigo-500'
                              : 'hover:bg-gray-100 dark:hover:bg-gray-700 border border-transparent'}`}
                        >
                          <Database className="w-4 h-4 text-gray-400" />
                          <span className="flex-1 truncate text-sm text-gray-900 dark:text-white">{t.name}</span>
                        </button>
                      ))}

                      {/* Show message if no tables at all */}
                      {tables.length === 0 && (
                        <div className="text-sm text-gray-500 text-center py-4">
                          No tables found
                        </div>
                      )}
                    </div>
                  )
                })()
              )}
            </div>
          )}

          {/* Columns List */}
          {columns.length > 0 && (
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                Columns ({columns.length})
              </label>
              <div className="space-y-1 max-h-64 overflow-auto">
                {columns.map(col => (
                  <div
                    key={col.name}
                    className="flex items-center gap-2 px-2 py-1.5 bg-gray-50 dark:bg-gray-700/50 rounded text-sm"
                  >
                    {getColumnIcon(col.type)}
                    <span className="flex-1 text-gray-900 dark:text-white truncate">{col.name}</span>
                    <span className="text-xs text-gray-500">{col.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Middle - Transform Steps */}
      <div className="flex-1 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-primary-500" />
            Transform Steps
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                if (currentPage === 1) {
                  executePreview()
                } else {
                  setCurrentPage(1)
                  // useEffect will trigger executePreview when page changes
                  if (!preview) executePreview()
                }
              }}
              disabled={!selectedTable || loadingPreview}
              className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loadingPreview ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Preview
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-4">
          {!selectedTable ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
              <Table2 className="w-12 h-12 mb-3 text-gray-400" />
              <p>Select a table or transform to start building</p>
            </div>
          ) : (
            <div className="space-y-3">
              {/* Steps List */}
              {steps.map((step, idx) => {
                const stepType = STEP_TYPES.find(s => s.type === step.type)
                const Icon = stepType?.icon || Filter
                return (
                  <div
                    key={step.id}
                    className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
                  >
                    <div
                      className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50"
                      onClick={() => toggleStepExpanded(step.id)}
                    >
                      <GripVertical className="w-4 h-4 text-gray-400" />
                      <span className="w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex items-center justify-center text-sm font-medium">
                        {idx + 1}
                      </span>
                      <Icon className="w-4 h-4 text-gray-500" />
                      <span className="flex-1 font-medium text-gray-900 dark:text-white">{stepType?.label}</span>
                      <button
                        onClick={(e) => { e.stopPropagation(); removeStep(step.id) }}
                        className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      {step.expanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
                    </div>
                    {step.expanded && (
                      <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                        {renderStepEditor(step)}
                      </div>
                    )}
                  </div>
                )
              })}

              {/* Add Step Button */}
              <div className="relative">
                <button
                  onClick={() => setShowAddStep(!showAddStep)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-500 hover:border-primary-500 hover:text-primary-500 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                  Add Transform Step
                </button>

                {showAddStep && (
                  <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-lg z-10">
                    <div className="p-2 grid grid-cols-2 gap-1">
                      {STEP_TYPES.map(st => (
                        <button
                          key={st.type}
                          onClick={() => addStep(st.type)}
                          className="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-left"
                        >
                          <st.icon className="w-4 h-4 text-primary-500" />
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">{st.label}</div>
                            <div className="text-xs text-gray-500">{st.description}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Save Recipe */}
        {selectedTable && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex items-center gap-3">
            <input
              type="text"
              value={recipeName}
              onChange={(e) => setRecipeName(e.target.value)}
              placeholder="Recipe name..."
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <button
              onClick={saveRecipe}
              disabled={saving || !recipeName.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : saveSuccess ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
              {saveSuccess ? 'Saved!' : 'Save Recipe'}
            </button>
          </div>
        )}
      </div>

      {/* Right - Preview */}
      <div className="w-[500px] border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Eye className="w-5 h-5 text-primary-500" />
            Preview
          </h2>
          {preview && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowSQL(!showSQL)}
                className={`p-2 rounded ${showSQL ? 'bg-primary-100 text-primary-600' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500'}`}
              >
                <Code className="w-4 h-4" />
              </button>
              <button
                onClick={() => { setCurrentPage(1); executePreview() }}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 rounded"
                title="Refresh preview"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-auto">
          {loadingPreview ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
            </div>
          ) : !preview ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 p-4">
              <Eye className="w-12 h-12 mb-3 text-gray-400" />
              <p>Click "Preview" to see transformed data</p>
            </div>
          ) : showSQL ? (
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Generated SQL</span>
                <button
                  onClick={copySQL}
                  className="flex items-center gap-1 text-sm text-primary-500 hover:text-primary-600"
                >
                  {copiedSQL ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copiedSQL ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <pre className="p-4 bg-gray-900 text-green-400 rounded-lg text-sm overflow-auto max-h-[calc(100vh-300px)]">
                {preview.sql_generated}
              </pre>
            </div>
          ) : (
            <div className="flex flex-col h-full">
              {/* Stats */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between text-sm">
                <div className="flex items-center gap-4">
                  <span className="text-gray-500">
                    Showing <span className="font-medium text-gray-900 dark:text-white">{((currentPage - 1) * rowsPerPage) + 1}-{Math.min(currentPage * rowsPerPage, preview.total_rows)}</span> of {preview.total_rows} rows
                  </span>
                  <span className="text-gray-500">
                    <span className="font-medium text-gray-900 dark:text-white">{preview.columns.length}</span> columns
                  </span>
                  <span className="text-gray-500">
                    <span className="font-medium text-gray-900 dark:text-white">{preview.execution_time_ms}ms</span>
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 text-xs">Rows per page:</span>
                  <select
                    value={rowsPerPage}
                    onChange={(e) => {
                      setRowsPerPage(Number(e.target.value))
                      setCurrentPage(1)
                    }}
                    className="px-2 py-1 text-xs border rounded dark:bg-gray-700 dark:border-gray-600"
                  >
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                    <option value={250}>250</option>
                    <option value={500}>500</option>
                  </select>
                </div>
              </div>

              {/* Data Table */}
              <div className="overflow-auto flex-1">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-700 sticky top-0">
                    <tr>
                      {preview.columns.map(col => (
                        <th key={col.name} className="px-3 py-2 text-left text-gray-600 dark:text-gray-300 font-medium whitespace-nowrap">
                          {col.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {preview.rows.map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        {preview.columns.map(col => (
                          <td key={col.name} className="px-3 py-2 text-gray-900 dark:text-white whitespace-nowrap">
                            {row[col.name] === null ? (
                              <span className="text-gray-400 italic">null</span>
                            ) : (
                              String(row[col.name])
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination Controls */}
              {preview.total_rows > rowsPerPage && (
                <div className="p-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-center gap-2">
                  <button
                    onClick={() => setCurrentPage(1)}
                    disabled={currentPage === 1 || loadingPreview}
                    className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="First page"
                  >
                    <ChevronsLeft className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1 || loadingPreview}
                    className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Previous page"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="px-3 text-sm">
                    Page <span className="font-medium">{currentPage}</span> of <span className="font-medium">{Math.ceil(preview.total_rows / rowsPerPage)}</span>
                  </span>
                  <button
                    onClick={() => setCurrentPage(p => Math.min(Math.ceil(preview.total_rows / rowsPerPage), p + 1))}
                    disabled={currentPage >= Math.ceil(preview.total_rows / rowsPerPage) || loadingPreview}
                    className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Next page"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setCurrentPage(Math.ceil(preview.total_rows / rowsPerPage))}
                    disabled={currentPage >= Math.ceil(preview.total_rows / rowsPerPage) || loadingPreview}
                    className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Last page"
                  >
                    <ChevronsRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TransformBuilder
