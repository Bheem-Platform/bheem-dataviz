import { useState, useEffect, useRef, DragEvent, ChangeEvent } from 'react'
import { Plus, Database, Search, CheckCircle, XCircle, ArrowLeft, Loader2, Eye, EyeOff, Trash2, Upload, FileSpreadsheet, Table } from 'lucide-react'
import { SiPostgresql, SiMysql, SiMongodb, SiSnowflake } from 'react-icons/si'
import { BiLogoGoogle } from 'react-icons/bi'
import { FaFileCsv, FaFileExcel } from 'react-icons/fa'
import { TbApi } from 'react-icons/tb'
import { IconType } from 'react-icons'
import { api } from '../lib/api'

// API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const connectionTypes: { id: string; name: string; icon: IconType; color: string }[] = [
  { id: 'postgresql', name: 'PostgreSQL', icon: SiPostgresql, color: '#336791' },
  { id: 'mysql', name: 'MySQL', icon: SiMysql, color: '#4479A1' },
  { id: 'bigquery', name: 'BigQuery', icon: BiLogoGoogle, color: '#4285F4' },
  { id: 'snowflake', name: 'Snowflake', icon: SiSnowflake, color: '#29B5E8' },
  { id: 'csv', name: 'CSV File', icon: FaFileCsv, color: '#22C55E' },
  { id: 'excel', name: 'Excel', icon: FaFileExcel, color: '#217346' },
  { id: 'api', name: 'REST API', icon: TbApi, color: '#8B5CF6' },
  { id: 'mongodb', name: 'MongoDB', icon: SiMongodb, color: '#47A248' },
]

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
  additional_config?: {
    table_name?: string
    original_filename?: string
    row_count?: number
  }
}

interface TestResult {
  success: boolean
  message: string
  tables_count?: number
  version?: string
}

interface ColumnConfig {
  original_name: string
  name: string
  type: string
  detected_type?: string
  nullable: boolean
}

interface PreviewData {
  columns: ColumnConfig[]
  sample_rows: Record<string, unknown>[]
  row_count: number
  file_id: string
  sheets?: string[]
}

type ModalStep = 'select-type' | 'postgresql-form' | 'mysql-form' | 'mongodb-form' | 'file-upload' | 'file-preview'
type InputMode = 'connection-string' | 'individual-fields'

const SQL_TYPES = ['TEXT', 'INTEGER', 'BIGINT', 'DOUBLE PRECISION', 'BOOLEAN', 'TIMESTAMP']

export function DataConnections() {
  const [showModal, setShowModal] = useState(false)
  const [modalStep, setModalStep] = useState<ModalStep>('select-type')
  const [search, setSearch] = useState('')
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState<string | null>(null)

  // PostgreSQL form state
  const [inputMode, setInputMode] = useState<InputMode>('connection-string')
  const [connectionString, setConnectionString] = useState('')
  const [connectionName, setConnectionName] = useState('')
  const [host, setHost] = useState('localhost')
  const [port, setPort] = useState('5432')
  const [database, setDatabase] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  // MongoDB specific state
  const [authSource, setAuthSource] = useState('')
  const [isSrv, setIsSrv] = useState(false)

  // Test connection state
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<TestResult | null>(null)
  const [saving, setSaving] = useState(false)

  // File upload state
  const [selectedFileType, setSelectedFileType] = useState<'csv' | 'excel'>('csv')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [previewData, setPreviewData] = useState<PreviewData | null>(null)
  const [columnConfig, setColumnConfig] = useState<ColumnConfig[]>([])
  const [selectedSheet, setSelectedSheet] = useState<string>('')
  const [delimiter, setDelimiter] = useState(',')
  const [hasHeader, setHasHeader] = useState(true)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Fetch connections on mount
  useEffect(() => {
    fetchConnections()
  }, [])

  const fetchConnections = async () => {
    try {
      const response = await api.get('/connections/')
      setConnections(response.data)
    } catch (error) {
      console.error('Failed to fetch connections:', error)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setInputMode('connection-string')
    setConnectionString('')
    setConnectionName('')
    setHost('localhost')
    setPort('5432')
    setDatabase('')
    setUsername('')
    setPassword('')
    setTestResult(null)
    // Reset MongoDB state
    setAuthSource('')
    setIsSrv(false)
    // Reset file upload state
    setUploadedFile(null)
    setPreviewData(null)
    setColumnConfig([])
    setSelectedSheet('')
    setDelimiter(',')
    setHasHeader(true)
    setIsDragging(false)
  }

  const openModal = () => {
    resetForm()
    setModalStep('select-type')
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    resetForm()
  }

  const selectConnectionType = (typeId: string) => {
    if (typeId === 'postgresql') {
      setPort('5432')
      setModalStep('postgresql-form')
    } else if (typeId === 'mysql') {
      setPort('3306')
      setModalStep('mysql-form')
    } else if (typeId === 'mongodb') {
      setPort('27017')
      setModalStep('mongodb-form')
    } else if (typeId === 'csv') {
      setSelectedFileType('csv')
      setModalStep('file-upload')
    } else if (typeId === 'excel') {
      setSelectedFileType('excel')
      setModalStep('file-upload')
    } else {
      alert(`${typeId} connector coming soon!`)
    }
  }

  const testConnection = async (dbType: 'postgresql' | 'mysql' | 'mongodb' = 'postgresql') => {
    setTesting(true)
    setTestResult(null)

    try {
      let payload: Record<string, unknown>

      if (inputMode === 'connection-string') {
        payload = { connection_string: connectionString, type: dbType }
      } else if (dbType === 'mongodb') {
        payload = {
          type: dbType,
          host,
          port: parseInt(port),
          database,
          username,
          password,
          additional_config: {
            auth_source: authSource || undefined,
            is_srv: isSrv
          }
        }
      } else {
        payload = {
          type: dbType,
          host,
          port: parseInt(port),
          database,
          username,
          password
        }
      }

      const response = await api.post('/connections/test', payload)
      setTestResult(response.data)
    } catch (error) {
      setTestResult({
        success: false,
        message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      })
    } finally {
      setTesting(false)
    }
  }

  const saveConnection = async (dbType: 'postgresql' | 'mysql' | 'mongodb' = 'postgresql') => {
    if (!connectionName.trim()) {
      alert('Please enter a connection name')
      return
    }

    setSaving(true)

    try {
      let payload: Record<string, unknown>

      if (inputMode === 'connection-string') {
        payload = {
          name: connectionName,
          type: dbType,
          connection_string: connectionString
        }
      } else if (dbType === 'mongodb') {
        payload = {
          name: connectionName,
          type: dbType,
          host,
          port: parseInt(port),
          database,
          username,
          password,
          additional_config: {
            auth_source: authSource || undefined,
            is_srv: isSrv
          }
        }
      } else {
        payload = {
          name: connectionName,
          type: dbType,
          host,
          port: parseInt(port),
          database,
          username,
          password
        }
      }

      const response = await api.post('/connections/', payload)
      const newConnection = response.data
      setConnections([...connections, newConnection])
      closeModal()
      // Auto-test the connection after saving
      testSavedConnection(newConnection.id)
    } catch (error: any) {
      alert(`Failed to save: ${error.response?.data?.detail || error.message || 'Unknown error'}`)
    } finally {
      setSaving(false)
    }
  }

  const deleteConnection = async (id: string) => {
    if (!confirm('Are you sure you want to delete this connection? This action cannot be undone.')) return

    setDeleting(id)
    try {
      await api.delete(`/connections/${id}`)
      setConnections(connections.filter(c => c.id !== id))
    } catch (error: any) {
      console.error('Failed to delete connection:', error)
      alert(`Failed to delete: ${error.response?.data?.detail || error.message || 'Network error'}`)
    } finally {
      setDeleting(null)
    }
  }

  const testSavedConnection = async (id: string) => {
    try {
      await api.post(`/connections/${id}/test`)
      fetchConnections() // Refresh to get updated status
    } catch (error) {
      console.error('Failed to test connection:', error)
    }
  }

  // File upload handlers
  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleFileSelect = (file: File) => {
    // Validate file type
    const extension = file.name.split('.').pop()?.toLowerCase()
    if (selectedFileType === 'csv' && extension !== 'csv') {
      alert('Please select a CSV file')
      return
    }
    if (selectedFileType === 'excel' && !['xlsx', 'xls'].includes(extension || '')) {
      alert('Please select an Excel file (.xlsx or .xls)')
      return
    }

    setUploadedFile(file)
    // Auto-set connection name from filename
    if (!connectionName) {
      setConnectionName(file.name.replace(/\.[^/.]+$/, ''))
    }
  }

  const uploadAndPreview = async () => {
    if (!uploadedFile) return

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', uploadedFile)
      formData.append('file_type', selectedFileType)
      formData.append('delimiter', delimiter)
      formData.append('has_header', String(hasHeader))
      if (selectedSheet) {
        formData.append('sheet_name', selectedSheet)
      }

      const response = await api.post('/connections/upload-preview', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const data: PreviewData = response.data
      setPreviewData(data)
      setColumnConfig(data.columns.map(col => ({
        ...col,
        type: col.type || col.detected_type || 'TEXT'
      })))
      setModalStep('file-preview')
    } catch (error: any) {
      alert(`Failed to upload file: ${error.response?.data?.detail || error.message || 'Unknown error'}`)
    } finally {
      setUploading(false)
    }
  }

  const confirmUpload = async () => {
    if (!previewData || !connectionName.trim()) {
      alert('Please enter a connection name')
      return
    }

    setSaving(true)

    try {
      const response = await api.post('/connections/upload-confirm', {
        name: connectionName,
        file_id: previewData.file_id,
        column_config: columnConfig
      })
      const result = response.data
      setConnections([...connections, result.connection])
      closeModal()
    } catch (error: any) {
      alert(`Failed to import: ${error.response?.data?.detail || error.message || 'Unknown error'}`)
    } finally {
      setSaving(false)
    }
  }

  const updateColumnType = (index: number, newType: string) => {
    setColumnConfig(prev => prev.map((col, i) =>
      i === index ? { ...col, type: newType } : col
    ))
  }

  const filteredConnections = connections.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase())
  )

  const renderFileUploadStep = () => (
    <div className="space-y-6">
      {/* Connection Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Connection Name *
        </label>
        <input
          type="text"
          value={connectionName}
          onChange={(e) => setConnectionName(e.target.value)}
          placeholder={`My ${selectedFileType.toUpperCase()} Data`}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* File Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragging
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : uploadedFile
              ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
          }
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={selectedFileType === 'csv' ? '.csv' : '.xlsx,.xls'}
          onChange={handleFileInputChange}
          className="hidden"
        />

        {uploadedFile ? (
          <div className="space-y-2">
            <FileSpreadsheet className="w-12 h-12 mx-auto text-green-500" />
            <p className="font-medium text-gray-900 dark:text-white">{uploadedFile.name}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {(uploadedFile.size / 1024).toFixed(1)} KB
            </p>
            <button
              onClick={(e) => {
                e.stopPropagation()
                setUploadedFile(null)
              }}
              className="text-sm text-red-500 hover:text-red-600"
            >
              Remove
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <Upload className="w-12 h-12 mx-auto text-gray-400" />
            <p className="text-gray-600 dark:text-gray-300">
              Drag & drop your {selectedFileType.toUpperCase()} file here
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              or click to browse
            </p>
          </div>
        )}
      </div>

      {/* CSV Options */}
      {selectedFileType === 'csv' && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Delimiter
            </label>
            <select
              value={delimiter}
              onChange={(e) => setDelimiter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value=",">Comma (,)</option>
              <option value=";">Semicolon (;)</option>
              <option value="\t">Tab</option>
              <option value="|">Pipe (|)</option>
            </select>
          </div>
          <div className="flex items-center">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={hasHeader}
                onChange={(e) => setHasHeader(e.target.checked)}
                className="w-4 h-4 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                First row is header
              </span>
            </label>
          </div>
        </div>
      )}

      {/* Excel Sheet Selection */}
      {selectedFileType === 'excel' && previewData?.sheets && previewData.sheets.length > 1 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Sheet
          </label>
          <select
            value={selectedSheet}
            onChange={(e) => setSelectedSheet(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {previewData.sheets.map(sheet => (
              <option key={sheet} value={sheet}>{sheet}</option>
            ))}
          </select>
        </div>
      )}
    </div>
  )

  const renderFilePreviewStep = () => (
    <div className="space-y-6">
      {/* Connection Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Connection Name *
        </label>
        <input
          type="text"
          value={connectionName}
          onChange={(e) => setConnectionName(e.target.value)}
          placeholder="My Data"
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* File Info */}
      <div className="flex items-center gap-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <FileSpreadsheet className="w-8 h-8 text-primary-500" />
        <div>
          <p className="font-medium text-gray-900 dark:text-white">{uploadedFile?.name}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {previewData?.row_count.toLocaleString()} rows, {previewData?.columns.length} columns
          </p>
        </div>
      </div>

      {/* Column Configuration */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Column Types
        </h4>
        <div className="max-h-48 overflow-auto border border-gray-200 dark:border-gray-600 rounded-lg">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 dark:bg-gray-700 sticky top-0">
              <tr>
                <th className="px-3 py-2 text-left text-gray-600 dark:text-gray-300">Column</th>
                <th className="px-3 py-2 text-left text-gray-600 dark:text-gray-300">Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
              {columnConfig.map((col, index) => (
                <tr key={col.name} className="bg-white dark:bg-gray-800">
                  <td className="px-3 py-2 text-gray-900 dark:text-white font-mono text-xs">
                    {col.original_name}
                  </td>
                  <td className="px-3 py-2">
                    <select
                      value={col.type}
                      onChange={(e) => updateColumnType(index, e.target.value)}
                      className="w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-primary-500"
                    >
                      {SQL_TYPES.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Data Preview */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Data Preview (first 10 rows)
        </h4>
        <div className="overflow-auto border border-gray-200 dark:border-gray-600 rounded-lg max-h-64">
          <table className="w-full text-xs">
            <thead className="bg-gray-50 dark:bg-gray-700 sticky top-0">
              <tr>
                {previewData?.columns.map(col => (
                  <th
                    key={col.name}
                    className="px-3 py-2 text-left text-gray-600 dark:text-gray-300 whitespace-nowrap"
                  >
                    {col.original_name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
              {previewData?.sample_rows.map((row, rowIndex) => (
                <tr key={rowIndex} className="bg-white dark:bg-gray-800">
                  {previewData.columns.map(col => (
                    <td
                      key={col.name}
                      className="px-3 py-2 text-gray-900 dark:text-white whitespace-nowrap max-w-xs truncate"
                      title={String(row[col.original_name] ?? '')}
                    >
                      {row[col.original_name] === null || row[col.original_name] === undefined
                        ? <span className="text-gray-400 italic">null</span>
                        : String(row[col.original_name])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="px-8 py-6 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div className="w-10 h-10 rounded-md bg-primary-500 flex items-center justify-center">
                <Database className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Data Connections
              </h1>
            </div>
            <p className="text-gray-500 dark:text-gray-400 ml-13">
              Connect to your databases and data sources
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search connections..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 pr-4 py-2.5 w-64 bg-gray-100 dark:bg-gray-700 border-0 rounded-md text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <button
              onClick={openModal}
              className="flex items-center gap-2 px-5 py-2.5 bg-primary-500 text-white rounded-md font-medium hover:bg-primary-600 transition-colors"
            >
              <Plus className="w-5 h-5" />
              New Connection
            </button>
          </div>
        </div>
      </header>

      {/* Connections Grid */}
      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-7xl mx-auto">
          {loading ? (
            <div className="flex items-center justify-center h-80">
              <div className="text-center">
                <Loader2 className="w-10 h-10 animate-spin text-primary-500 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">Loading connections...</p>
              </div>
            </div>
          ) : filteredConnections.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-80 text-center">
              <div className="w-20 h-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-6">
                <Database className="w-10 h-10 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                No connections yet
              </h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mb-8">
                Connect your first database or upload a file to get started
              </p>
              <button
                onClick={openModal}
                className="px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-medium hover:opacity-90 transition-opacity"
              >
                Add Connection
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredConnections.map((connection) => {
                const typeInfo = connectionTypes.find((t) => t.id === connection.type)
                const isFileConnection = ['csv', 'excel'].includes(connection.type)
                return (
                  <div
                    key={connection.id}
                    className="group relative bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl hover:shadow-primary-500/10 hover:border-primary-300 dark:hover:border-primary-600 transition-all duration-300"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-14 rounded-xl bg-primary-500/10 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                        {typeInfo ? (
                          <typeInfo.icon className="w-8 h-8" style={{ color: typeInfo.color }} />
                        ) : (
                          <Database className="w-8 h-8 text-gray-400" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 dark:text-white text-lg mb-1 truncate group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                          {connection.name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400 truncate mb-3">
                          {typeInfo?.name}
                          {connection.host && ` • ${connection.host}`}
                          {connection.database && ` • ${connection.database}`}
                        </p>
                        <div className="flex items-center gap-3 flex-wrap">
                          {connection.status === 'connected' ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-xs font-medium rounded-full">
                              <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                              Connected
                            </span>
                          ) : connection.status === 'error' ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-xs font-medium rounded-full">
                              <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                              Error
                            </span>
                          ) : connection.status === 'syncing' ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs font-medium rounded-full">
                              <Loader2 className="w-3 h-3 animate-spin" />
                              Syncing
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs font-medium rounded-full">
                              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
                              Disconnected
                            </span>
                          )}
                          {isFileConnection && connection.additional_config?.row_count !== undefined && (
                            <span className="text-xs text-gray-400">
                              {connection.additional_config.row_count.toLocaleString()} rows
                            </span>
                          )}
                          {connection.tables_count !== undefined && (
                            <span className="text-xs text-gray-400">
                              {connection.tables_count} table{connection.tables_count !== 1 ? 's' : ''}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                      <button
                        onClick={() => testSavedConnection(connection.id)}
                        className="flex-1 px-3 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
                      >
                        Test Connection
                      </button>
                      <button
                        onClick={() => deleteConnection(connection.id)}
                        disabled={deleting === connection.id}
                        className="p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg text-red-500 transition-colors disabled:opacity-50"
                      >
                        {deleting === connection.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden">
            {/* Modal Header */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-4">
                {(modalStep === 'postgresql-form' || modalStep === 'mysql-form' || modalStep === 'mongodb-form' || modalStep === 'file-upload' || modalStep === 'file-preview') && (
                  <button
                    onClick={() => {
                      if (modalStep === 'file-preview') {
                        setModalStep('file-upload')
                      } else {
                        setModalStep('select-type')
                      }
                    }}
                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                  >
                    <ArrowLeft className="w-5 h-5 text-gray-500" />
                  </button>
                )}
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    {modalStep === 'select-type' && 'New Connection'}
                    {modalStep === 'postgresql-form' && 'PostgreSQL Connection'}
                    {modalStep === 'mysql-form' && 'MySQL Connection'}
                    {modalStep === 'mongodb-form' && 'MongoDB Connection'}
                    {modalStep === 'file-upload' && `Upload ${selectedFileType.toUpperCase()} File`}
                    {modalStep === 'file-preview' && 'Preview & Import'}
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {modalStep === 'select-type' && 'Select a data source type to connect'}
                    {(modalStep === 'postgresql-form' || modalStep === 'mysql-form' || modalStep === 'mongodb-form') && 'Enter your database connection details'}
                    {modalStep === 'file-upload' && 'Upload your file to import data'}
                    {modalStep === 'file-preview' && 'Review and configure your data before importing'}
                  </p>
                </div>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-auto max-h-[calc(80vh-200px)]">
              {modalStep === 'select-type' ? (
                /* Step 1: Type Selection */
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {connectionTypes.map((type) => (
                    <button
                      key={type.id}
                      onClick={() => selectConnectionType(type.id)}
                      className="flex flex-col items-center gap-2 p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
                    >
                      <type.icon className="w-8 h-8" style={{ color: type.color }} />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {type.name}
                      </span>
                    </button>
                  ))}
                </div>
              ) : (modalStep === 'postgresql-form' || modalStep === 'mysql-form' || modalStep === 'mongodb-form') ? (
                /* Step 2: Database Form (PostgreSQL/MySQL/MongoDB) */
                <div className="space-y-6">
                  {/* Connection Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Connection Name *
                    </label>
                    <input
                      type="text"
                      value={connectionName}
                      onChange={(e) => setConnectionName(e.target.value)}
                      placeholder={
                        modalStep === 'mysql-form' ? "My MySQL Database" :
                        modalStep === 'mongodb-form' ? "My MongoDB Database" :
                        "My PostgreSQL Database"
                      }
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  {/* Input Mode Toggle */}
                  <div className="flex gap-2 p-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
                    <button
                      onClick={() => setInputMode('connection-string')}
                      className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                        inputMode === 'connection-string'
                          ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                          : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                      }`}
                    >
                      Connection String
                    </button>
                    <button
                      onClick={() => setInputMode('individual-fields')}
                      className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                        inputMode === 'individual-fields'
                          ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                          : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                      }`}
                    >
                      Individual Fields
                    </button>
                  </div>

                  {inputMode === 'connection-string' ? (
                    /* Connection String Mode */
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Connection String
                      </label>
                      <input
                        type="text"
                        value={connectionString}
                        onChange={(e) => setConnectionString(e.target.value)}
                        placeholder={
                          modalStep === 'mysql-form'
                            ? "mysql://user:password@localhost:3306/database"
                            : modalStep === 'mongodb-form'
                            ? "mongodb://user:password@localhost:27017/database"
                            : "postgresql://user:password@localhost:5432/database"
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
                      />
                      <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        {modalStep === 'mysql-form'
                          ? "Format: mysql://[user[:password]@][host][:port][/database]"
                          : modalStep === 'mongodb-form'
                          ? "Format: mongodb://[user[:password]@][host][:port][/database] or mongodb+srv://..."
                          : "Format: postgresql://[user[:password]@][host][:port][/database]"}
                      </p>
                    </div>
                  ) : (
                    /* Individual Fields Mode */
                    <div className="space-y-4">
                      {/* MongoDB SRV Toggle */}
                      {modalStep === 'mongodb-form' && (
                        <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                          <input
                            type="checkbox"
                            id="srv-toggle"
                            checked={isSrv}
                            onChange={(e) => setIsSrv(e.target.checked)}
                            className="w-4 h-4 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
                          />
                          <label htmlFor="srv-toggle" className="text-sm text-gray-700 dark:text-gray-300">
                            Use SRV record (mongodb+srv://) - for MongoDB Atlas
                          </label>
                        </div>
                      )}

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            {modalStep === 'mongodb-form' && isSrv ? 'Cluster Address' : 'Host'}
                          </label>
                          <input
                            type="text"
                            value={host}
                            onChange={(e) => setHost(e.target.value)}
                            placeholder={modalStep === 'mongodb-form' && isSrv ? "cluster0.xxxxx.mongodb.net" : "localhost"}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                          />
                        </div>
                        {!(modalStep === 'mongodb-form' && isSrv) && (
                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Port
                            </label>
                            <input
                              type="text"
                              value={port}
                              onChange={(e) => setPort(e.target.value)}
                              placeholder={
                                modalStep === 'mysql-form' ? "3306" :
                                modalStep === 'mongodb-form' ? "27017" :
                                "5432"
                              }
                              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                            />
                          </div>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Database
                        </label>
                        <input
                          type="text"
                          value={database}
                          onChange={(e) => setDatabase(e.target.value)}
                          placeholder="mydatabase"
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Username
                          </label>
                          <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder={
                              modalStep === 'mysql-form' ? "root" :
                              modalStep === 'mongodb-form' ? "admin" :
                              "postgres"
                            }
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Password
                          </label>
                          <div className="relative">
                            <input
                              type={showPassword ? 'text' : 'password'}
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              placeholder="********"
                              className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                            >
                              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* MongoDB Auth Source */}
                      {modalStep === 'mongodb-form' && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Auth Database <span className="text-gray-400 font-normal">(optional)</span>
                          </label>
                          <input
                            type="text"
                            value={authSource}
                            onChange={(e) => setAuthSource(e.target.value)}
                            placeholder="admin"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                          />
                          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                            The database where the user is defined (usually "admin")
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Test Result */}
                  {testResult && (
                    <div className={`p-4 rounded-lg ${
                      testResult.success
                        ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                        : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                    }`}>
                      <div className="flex items-center gap-2">
                        {testResult.success ? (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-500" />
                        )}
                        <span className={`font-medium ${
                          testResult.success ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'
                        }`}>
                          {testResult.message}
                        </span>
                      </div>
                      {testResult.success && testResult.tables_count !== undefined && (
                        <p className="mt-2 text-sm text-green-600 dark:text-green-400">
                          Found {testResult.tables_count} {modalStep === 'mongodb-form' ? 'collections' : 'tables'}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ) : modalStep === 'file-upload' ? (
                renderFileUploadStep()
              ) : modalStep === 'file-preview' ? (
                renderFilePreviewStep()
              ) : null}
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-between">
              <button
                onClick={closeModal}
                className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>

              {(modalStep === 'postgresql-form' || modalStep === 'mysql-form' || modalStep === 'mongodb-form') && (
                <div className="flex gap-3">
                  <button
                    onClick={() => testConnection(
                      modalStep === 'mysql-form' ? 'mysql' :
                      modalStep === 'mongodb-form' ? 'mongodb' :
                      'postgresql'
                    )}
                    disabled={testing || (inputMode === 'connection-string' ? !connectionString : !host || !database)}
                    className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {testing && <Loader2 className="w-4 h-4 animate-spin" />}
                    Test Connection
                  </button>
                  <button
                    onClick={() => saveConnection(
                      modalStep === 'mysql-form' ? 'mysql' :
                      modalStep === 'mongodb-form' ? 'mongodb' :
                      'postgresql'
                    )}
                    disabled={saving || !connectionName || (inputMode === 'connection-string' ? !connectionString : !host || !database)}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                    Save Connection
                  </button>
                </div>
              )}

              {modalStep === 'file-upload' && (
                <button
                  onClick={uploadAndPreview}
                  disabled={uploading || !uploadedFile}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading && <Loader2 className="w-4 h-4 animate-spin" />}
                  <Table className="w-4 h-4" />
                  Preview Data
                </button>
              )}

              {modalStep === 'file-preview' && (
                <button
                  onClick={confirmUpload}
                  disabled={saving || !connectionName}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                  <CheckCircle className="w-4 h-4" />
                  Import Data
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
