import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import {
  Database,
  Table2,
  Loader2,
  ArrowLeft,
  BarChart3,
  LineChart,
  PieChart,
  AreaChart,
  RefreshCw,
  Download,
  Maximize2,
  Settings,
  Search,
  Sparkles,
  Save,
  FolderPlus,
  Check,
  X,
  Wand2,
  Hash,
  TableIcon,
  Plus,
  GitBranch,
  Calculator,
  Columns,
  Play,
  Trash2,
  Star,
  Edit3,
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
  ChevronLeft,
  ChevronRight,
  // New chart type icons
  BarChartHorizontal,
  ScatterChart,
  Gauge,
  Filter,
  Target,
} from 'lucide-react'
import ReactECharts from 'echarts-for-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

interface Connection {
  id: string
  name: string
  type: string
}

interface ColumnInfo {
  name: string
  type: string
  nullable: boolean
}

interface TablePreview {
  columns: string[]
  rows: Record<string, any>[]
  total: number
  preview_count: number
}

interface GeneratedChart {
  id: string
  title: string
  description: string
  type: 'bar' | 'line' | 'pie' | 'area' | 'horizontal-bar' | 'donut' | 'scatter' | 'gauge' | 'funnel' | 'radar' | 'kpi' | 'table'
  option: any
  icon: any
  kpiValue?: string | number
  kpiLabel?: string
  kpiChange?: number
  kpiChangeLabel?: string
  tableColumns?: string[]
  tableRows?: Record<string, any>[]
}

interface DashboardInfo {
  id: string
  name: string
  description: string | null
  chart_count: number
}

interface TransformRecipe {
  id: string
  name: string
  description: string | null
  connection_id: string
  source_table: string
  source_schema: string
  steps: any[]
  result_columns: { name: string; type: string }[]
  row_count: number | null
  last_executed: string | null
  execution_time_ms: number | null
  created_at: string
  updated_at: string
}

interface RecipePreview {
  recipeId: string
  chart: GeneratedChart | null
  loading: boolean
  error: boolean
}

// Semantic Model Types
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

interface SemanticModel {
  id: string
  name: string
  description?: string
  connection_id: string
  transform_id?: string
  transform_name?: string
  schema_name?: string
  table_name?: string
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

type ViewMode = 'recipes' | 'charts'
type DataSourceType = 'transforms' | 'models' | 'saved'

interface SavedChart {
  id: string
  name: string
  description?: string
  chart_type: string
  chart_config: Record<string, any>
  query_config?: Record<string, any>
  connection_id: string
  semantic_model_id?: string
  transform_recipe_id?: string
  is_favorite?: boolean
  created_at: string
  updated_at: string
}

// Professional color palette - inspired by modern BI tools
const chartColors = [
  '#6366f1', // Indigo (primary)
  '#0ea5e9', // Sky blue
  '#10b981', // Emerald
  '#f59e0b', // Amber
  '#ec4899', // Pink
  '#8b5cf6', // Violet
  '#14b8a6', // Teal
  '#f97316', // Orange
  '#64748b', // Slate
  '#84cc16', // Lime
]

// Semantic colors for positive/negative values
const semanticColors = {
  positive: '#10b981', // Green
  negative: '#ef4444', // Red
  neutral: '#6b7280',  // Gray
}

// ============================================================================
// SMART FORMATTING UTILITIES
// ============================================================================

/**
 * Detects if a column likely contains currency/money values
 */
function isCurrencyColumn(colName: string, values: number[]): boolean {
  const currencyKeywords = ['price', 'cost', 'amount', 'revenue', 'sales', 'profit', 'income', 'expense', 'total', 'sum', 'value', 'money', 'fee', 'payment', 'salary', 'wage', 'budget']
  const lowerName = colName.toLowerCase()
  return currencyKeywords.some(kw => lowerName.includes(kw))
}

/**
 * Detects if values are likely percentages (0-100 or 0-1 range)
 */
function isPercentageColumn(colName: string, values: number[]): boolean {
  const percentKeywords = ['percent', 'pct', 'rate', 'ratio', 'share', 'proportion', '%']
  const lowerName = colName.toLowerCase()
  if (percentKeywords.some(kw => lowerName.includes(kw))) return true

  // Check if all values are between 0 and 100
  const allInRange = values.every(v => v >= 0 && v <= 100)
  const avgValue = values.reduce((a, b) => a + b, 0) / values.length
  return allInRange && avgValue <= 100 && avgValue > 0
}

/**
 * Smart number formatter - returns abbreviated numbers like Power BI
 * Examples: 1234567 → "1.2M", 45000 → "45K", 0.156 → "15.6%"
 */
function formatNumber(value: number, options?: {
  isCurrency?: boolean
  isPercent?: boolean
  decimals?: number
  compact?: boolean
}): string {
  if (value === null || value === undefined || isNaN(value)) return '—'

  const { isCurrency = false, isPercent = false, decimals = 1, compact = true } = options || {}

  // Handle percentages
  if (isPercent) {
    // If value is already 0-100, use as-is; if 0-1, multiply by 100
    const pctValue = value <= 1 && value >= 0 ? value * 100 : value
    return `${pctValue.toFixed(decimals)}%`
  }

  const absValue = Math.abs(value)
  let formatted: string

  if (compact && absValue >= 1e9) {
    formatted = `${(value / 1e9).toFixed(decimals)}B`
  } else if (compact && absValue >= 1e6) {
    formatted = `${(value / 1e6).toFixed(decimals)}M`
  } else if (compact && absValue >= 1e3) {
    formatted = `${(value / 1e3).toFixed(decimals)}K`
  } else if (absValue < 1 && absValue > 0) {
    formatted = value.toFixed(2)
  } else {
    formatted = value.toLocaleString(undefined, { maximumFractionDigits: decimals })
  }

  if (isCurrency) {
    return value < 0 ? `-$${formatted.replace('-', '')}` : `$${formatted}`
  }

  return formatted
}

/**
 * Creates an ECharts axis label formatter function
 */
function createAxisFormatter(isCurrency: boolean, isPercent: boolean): (value: number) => string {
  return (value: number) => formatNumber(value, { isCurrency, isPercent, decimals: 0, compact: true })
}

/**
 * Creates a rich tooltip formatter for ECharts
 */
function createTooltipFormatter(categoryCol: string, valueCol: string, total: number, isCurrency: boolean): string {
  // Return HTML template string for ECharts tooltip
  return `<div style="padding: 8px 12px; min-width: 150px;">
    <div style="font-weight: 600; margin-bottom: 6px; color: #374151;">{b}</div>
    <div style="display: flex; justify-content: space-between; align-items: center; gap: 20px;">
      <span style="color: #6b7280;">${valueCol}</span>
      <span style="font-weight: 600; color: #111827;">${isCurrency ? '$' : ''}{c}</span>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center; gap: 20px; margin-top: 4px; padding-top: 4px; border-top: 1px solid #e5e7eb;">
      <span style="color: #9ca3af; font-size: 12px;">% of Total</span>
      <span style="color: #6366f1; font-size: 12px; font-weight: 500;">{d}%</span>
    </div>
  </div>`
}

/**
 * Prettify column name for display
 * Examples: "total_sales_amount" → "Total Sales Amount", "orderQty" → "Order Qty"
 */
function prettifyColumnName(name: string): string {
  return name
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, c => c.toUpperCase())
    .trim()
}

function toSlug(str: string): string {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

/**
 * Creates dataZoom configuration for scrollable charts
 * @param dataLength - Number of data points
 * @param threshold - Minimum data points before enabling scroll (default: 10)
 * @param visibleItems - Number of items to show initially (default: 10)
 * @param orientation - 'horizontal' or 'vertical'
 */
function createDataZoom(
  dataLength: number,
  threshold: number = 10,
  visibleItems: number = 10,
  orientation: 'horizontal' | 'vertical' = 'horizontal'
): any[] {
  if (dataLength <= threshold) return []

  const endPercent = Math.min((visibleItems / dataLength) * 100, 100)

  if (orientation === 'horizontal') {
    return [
      {
        type: 'slider',
        show: true,
        xAxisIndex: 0,
        start: 0,
        end: endPercent,
        height: 20,
        bottom: 10,
        borderColor: '#e5e7eb',
        fillerColor: 'rgba(99, 102, 241, 0.1)',
        handleStyle: { color: '#6366f1', borderColor: '#6366f1' },
        moveHandleSize: 8,
        textStyle: { color: '#6b7280', fontSize: 10 },
        brushSelect: false
      },
      {
        type: 'inside',
        xAxisIndex: 0,
        start: 0,
        end: endPercent,
        zoomOnMouseWheel: false,
        moveOnMouseMove: true,
        moveOnMouseWheel: true
      }
    ]
  } else {
    return [
      {
        type: 'slider',
        show: true,
        yAxisIndex: 0,
        start: 100 - endPercent,
        end: 100,
        width: 20,
        right: 10,
        borderColor: '#e5e7eb',
        fillerColor: 'rgba(99, 102, 241, 0.1)',
        handleStyle: { color: '#6366f1', borderColor: '#6366f1' },
        textStyle: { color: '#6b7280', fontSize: 10 },
        brushSelect: false
      },
      {
        type: 'inside',
        yAxisIndex: 0,
        start: 100 - endPercent,
        end: 100,
        zoomOnMouseWheel: false,
        moveOnMouseMove: true,
        moveOnMouseWheel: true
      }
    ]
  }
}

// ============================================================================
// SIMPLE CHART GENERATOR
// Rule: Column 1 = Category (X-axis), Column 2+ = Value (Y-axis)
// Works for ANY dataset - just uses the data structure directly
// ============================================================================

function generateCharts(
  columns: ColumnInfo[],
  rows: Record<string, any>[],
  tableName: string,
  steps: any[] = []
): GeneratedChart[] {
  const charts: GeneratedChart[] = []
  console.log('=== GENERATING CHARTS ===')
  console.log('Table:', tableName)
  console.log('Columns:', columns)
  console.log('Rows count:', rows.length)

  if (!rows.length || !columns.length) {
    console.log('No data - returning empty charts')
    return charts
  }

  const tableSlug = toSlug(tableName)
  const colNames = columns.map(c => c.name)

  // ========================================
  // DETECT: Which column is category, which is value
  // ========================================

  // Check each column: is it numeric or text?
  const colTypes = columns.map(col => ({
    name: col.name,
    isNumeric: rows.every(r => {
      const v = r[col.name]
      return v === null || v === undefined || v === '' || !isNaN(Number(v))
    }) && rows.some(r => {
      const v = r[col.name]
      return v !== null && v !== undefined && v !== '' && !isNaN(Number(v))
    })
  }))

  const numericCols = colTypes.filter(c => c.isNumeric).map(c => c.name)
  const textCols = colTypes.filter(c => !c.isNumeric).map(c => c.name)

  console.log('Columns:', colNames)
  console.log('Numeric:', numericCols)
  console.log('Text:', textCols)

  // ========================================
  // CASE 1: We have category + value columns
  // Use text column with LOWEST cardinality as category, first numeric col as value
  // ========================================
  if (textCols.length > 0 && numericCols.length > 0) {
    // Find the text column with the lowest cardinality (fewest unique values)
    let categoryCol = textCols[0]
    let bestCardinality = Infinity

    textCols.forEach(colName => {
      const uniqueValues = new Set(rows.map(r => r[colName]))
      if (uniqueValues.size < bestCardinality && uniqueValues.size > 1) {
        bestCardinality = uniqueValues.size
        categoryCol = colName
      }
    })

    const valueCol = numericCols[0]
    console.log(`CASE 1: Selected "${categoryCol}" as category (${bestCardinality} unique values), "${valueCol}" as value`)

    // Aggregate values by category
    const aggregated = new Map<string, number>()
    rows.forEach(row => {
      const key = String(row[categoryCol] || 'Unknown')
      const val = Number(row[valueCol]) || 0
      aggregated.set(key, (aggregated.get(key) || 0) + val)
    })

    const sorted = Array.from(aggregated.entries()).sort((a, b) => b[1] - a[1])
    const labels = sorted.map(e => e[0])
    const values = sorted.map(e => e[1])
    const total = values.reduce((a, b) => a + b, 0)

    // Detect formatting type
    const isCurrency = isCurrencyColumn(valueCol, values)
    const isPercent = isPercentageColumn(valueCol, values)
    const prettyValueCol = prettifyColumnName(valueCol)
    const prettyCategoryCol = prettifyColumnName(categoryCol)

    // Create smart axis formatter
    const axisFormatter = createAxisFormatter(isCurrency, isPercent)

    // Format total for display
    const formattedTotal = formatNumber(total, { isCurrency, isPercent: false, decimals: 1 })

    // Bar Chart - Professional styling
    charts.push({
      id: `${tableSlug}-bar`,
      title: `${prettyValueCol} by ${prettyCategoryCol}`,
      description: `${labels.length} categories · Total: ${formattedTotal}`,
      type: 'bar',
      icon: BarChart3,
      option: {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params: any) => {
            const data = params[0]
            const value = data.value
            const pct = ((value / total) * 100).toFixed(1)
            const formattedValue = formatNumber(value, { isCurrency, isPercent, decimals: 1, compact: false })
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${data.name}</div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">${prettyValueCol}</span>
                <span style="font-weight: 600;">${formattedValue}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 4px; color: #9ca3af; font-size: 12px;">
                <span>% of Total</span>
                <span style="color: #6366f1;">${pct}%</span>
              </div>
            </div>`
          }
        },
        xAxis: {
          type: 'category',
          data: labels,
          axisLabel: {
            rotate: labels.length > 6 ? 45 : 0,
            fontSize: 11,
            color: '#6b7280',
            interval: 0,
            formatter: (val: string) => val.length > 12 ? val.slice(0, 12) + '...' : val
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: axisFormatter, fontSize: 11, color: '#6b7280' },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
        },
        series: [{
          type: 'bar',
          data: values.map((v, i) => ({
            value: v,
            itemStyle: {
              color: chartColors[i % chartColors.length],
              borderRadius: [4, 4, 0, 0]
            }
          })),
          barMaxWidth: 50,
          label: {
            show: labels.length <= 8 && labels.length <= 10,
            position: 'top',
            formatter: (params: any) => formatNumber(params.value, { isCurrency, isPercent, decimals: 0 }),
            fontSize: 11,
            fontWeight: 500,
            color: '#374151'
          }
        }],
        dataZoom: createDataZoom(labels.length, 12, 12, 'horizontal'),
        grid: {
          left: 60,
          right: 20,
          bottom: labels.length > 12 ? 60 : (labels.length > 6 ? 80 : 40),
          top: 40
        }
      }
    })

    // Pie Chart - Professional styling
    const pieLabels = labels.slice(0, 10) // Limit for readability
    const pieValues = values.slice(0, 10)
    const pieTotal = pieValues.reduce((a, b) => a + b, 0)
    charts.push({
      id: `${tableSlug}-pie`,
      title: `${prettyCategoryCol} Distribution`,
      description: pieLabels.length < labels.length ? `Top ${pieLabels.length} of ${labels.length} categories` : `${pieLabels.length} categories`,
      type: 'pie',
      icon: PieChart,
      option: {
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            const formattedValue = formatNumber(params.value, { isCurrency, decimals: 1, compact: false })
            return `<div style="padding: 8px 12px;">
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="width: 10px; height: 10px; border-radius: 2px; background: ${params.color};"></span>
                <span style="font-weight: 600;">${params.name}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">Value</span>
                <span style="font-weight: 600;">${formattedValue}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 2px;">
                <span style="color: #6b7280;">Share</span>
                <span style="font-weight: 600; color: #6366f1;">${params.percent.toFixed(1)}%</span>
              </div>
            </div>`
          }
        },
        legend: {
          type: 'scroll',
          orient: 'vertical',
          right: 10,
          top: 'center',
          textStyle: { fontSize: 11, color: '#6b7280' },
          pageIconSize: 10
        },
        series: [{
          type: 'pie',
          radius: ['0%', '65%'],
          center: ['35%', '50%'],
          data: pieLabels.map((name, i) => ({
            value: pieValues[i],
            name,
            itemStyle: { color: chartColors[i % chartColors.length] }
          })),
          label: {
            show: pieLabels.length <= 6,
            formatter: '{d}%',
            fontSize: 11,
            color: '#374151'
          },
          labelLine: { show: pieLabels.length <= 6, length: 10, length2: 10 },
          emphasis: {
            itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.2)' }
          }
        }]
      }
    })

    // Donut Chart - Professional styling with center metric
    charts.push({
      id: `${tableSlug}-donut`,
      title: `${prettyCategoryCol} Breakdown`,
      description: `Total: ${formattedTotal}`,
      type: 'donut',
      icon: PieChart,
      option: {
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            const formattedValue = formatNumber(params.value, { isCurrency, decimals: 1, compact: false })
            return `<div style="padding: 8px 12px;">
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="width: 10px; height: 10px; border-radius: 2px; background: ${params.color};"></span>
                <span style="font-weight: 600;">${params.name}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">Value</span>
                <span style="font-weight: 600;">${formattedValue}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 2px;">
                <span style="color: #6b7280;">Share</span>
                <span style="font-weight: 600; color: #6366f1;">${params.percent.toFixed(1)}%</span>
              </div>
            </div>`
          }
        },
        graphic: [{
          type: 'text',
          left: 'center',
          top: '45%',
          style: {
            text: formattedTotal,
            textAlign: 'center',
            fontSize: 24,
            fontWeight: 'bold',
            fill: '#111827'
          }
        }, {
          type: 'text',
          left: 'center',
          top: '55%',
          style: {
            text: 'Total',
            textAlign: 'center',
            fontSize: 12,
            fill: '#9ca3af'
          }
        }],
        series: [{
          type: 'pie',
          radius: ['50%', '70%'],
          center: ['50%', '50%'],
          avoidLabelOverlap: true,
          data: pieLabels.map((name, i) => ({
            value: pieValues[i],
            name,
            itemStyle: { color: chartColors[i % chartColors.length] }
          })),
          label: { show: false },
          emphasis: {
            label: { show: true, fontSize: 12, fontWeight: 'bold' },
            itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.2)' }
          }
        }]
      }
    })

    // Line Chart - Professional styling
    charts.push({
      id: `${tableSlug}-line`,
      title: `${prettyValueCol} Trend`,
      description: `Across ${labels.length} ${prettyCategoryCol.toLowerCase()}s`,
      type: 'line',
      icon: LineChart,
      option: {
        tooltip: {
          trigger: 'axis',
          formatter: (params: any) => {
            const data = params[0]
            const formattedValue = formatNumber(data.value, { isCurrency, isPercent, decimals: 1, compact: false })
            const pct = ((data.value / total) * 100).toFixed(1)
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${data.name}</div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="width: 10px; height: 3px; background: ${chartColors[0]}; border-radius: 2px;"></span>
                <span style="color: #6b7280;">${prettyValueCol}</span>
                <span style="font-weight: 600; margin-left: auto;">${formattedValue}</span>
              </div>
            </div>`
          }
        },
        xAxis: {
          type: 'category',
          data: labels,
          axisLabel: {
            rotate: labels.length > 6 ? 45 : 0,
            fontSize: 11,
            color: '#6b7280',
            formatter: (val: string) => val.length > 10 ? val.slice(0, 10) + '...' : val
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: axisFormatter, fontSize: 11, color: '#6b7280' },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
        },
        series: [{
          type: 'line',
          data: values,
          smooth: true,
          symbol: 'circle',
          symbolSize: labels.length > 20 ? 4 : 6,
          itemStyle: { color: chartColors[0] },
          lineStyle: { width: labels.length > 30 ? 2 : 3, color: chartColors[0] },
          emphasis: { scale: 1.5 }
        }],
        dataZoom: createDataZoom(labels.length, 15, 15, 'horizontal'),
        grid: {
          left: 60,
          right: 20,
          bottom: labels.length > 15 ? 60 : (labels.length > 6 ? 80 : 40),
          top: 30
        }
      }
    })

    // Area Chart - Professional gradient
    charts.push({
      id: `${tableSlug}-area`,
      title: `${prettyValueCol} Area`,
      description: 'Filled area visualization',
      type: 'area',
      icon: AreaChart,
      option: {
        tooltip: {
          trigger: 'axis',
          formatter: (params: any) => {
            const data = params[0]
            const formattedValue = formatNumber(data.value, { isCurrency, isPercent, decimals: 1, compact: false })
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${data.name}</div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">${prettyValueCol}</span>
                <span style="font-weight: 600;">${formattedValue}</span>
              </div>
            </div>`
          }
        },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: false,
          axisLabel: {
            rotate: labels.length > 6 ? 45 : 0,
            fontSize: 11,
            color: '#6b7280'
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: axisFormatter, fontSize: 11, color: '#6b7280' },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
        },
        series: [{
          type: 'line',
          data: values,
          smooth: true,
          symbol: 'none',
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: chartColors[0] + 'cc' },
                { offset: 0.7, color: chartColors[0] + '40' },
                { offset: 1, color: chartColors[0] + '05' }
              ]
            }
          },
          itemStyle: { color: chartColors[0] },
          lineStyle: { width: 2, color: chartColors[0] }
        }],
        dataZoom: createDataZoom(labels.length, 15, 15, 'horizontal'),
        grid: {
          left: 60,
          right: 20,
          bottom: labels.length > 15 ? 60 : (labels.length > 6 ? 80 : 40),
          top: 30
        }
      }
    })

    // Horizontal Bar Chart - Professional styling (great for rankings, scrollable vertically)
    const hBarLabels = labels // Use all data, not sliced
    const hBarValues = values
    charts.push({
      id: `${tableSlug}-horizontal-bar`,
      title: `${prettyValueCol} by ${prettyCategoryCol}`,
      description: `${hBarLabels.length} categories ranked`,
      type: 'horizontal-bar',
      icon: BarChartHorizontal,
      option: {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params: any) => {
            const data = params[0]
            const formattedValue = formatNumber(data.value, { isCurrency, isPercent, decimals: 1, compact: false })
            const pct = ((data.value / total) * 100).toFixed(1)
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${data.name}</div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">${prettyValueCol}</span>
                <span style="font-weight: 600;">${formattedValue}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 2px; font-size: 12px; color: #9ca3af;">
                <span>Share</span>
                <span style="color: #6366f1;">${pct}%</span>
              </div>
            </div>`
          }
        },
        xAxis: {
          type: 'value',
          axisLabel: { formatter: axisFormatter, fontSize: 11, color: '#6b7280' },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
        },
        yAxis: {
          type: 'category',
          data: hBarLabels.slice().reverse(),
          axisLabel: {
            fontSize: 11,
            color: '#374151',
            formatter: (val: string) => val.length > 18 ? val.slice(0, 18) + '...' : val
          },
          axisLine: { show: false },
          axisTick: { show: false }
        },
        series: [{
          type: 'bar',
          data: hBarValues.slice().reverse().map((v, i) => ({
            value: v,
            itemStyle: {
              color: chartColors[(hBarValues.length - 1 - i) % chartColors.length],
              borderRadius: [0, 4, 4, 0]
            }
          })),
          barMaxWidth: 20,
          label: {
            show: hBarLabels.length <= 15,
            position: 'right',
            formatter: (params: any) => formatNumber(params.value, { isCurrency, isPercent, decimals: 0 }),
            fontSize: 10,
            color: '#374151'
          }
        }],
        dataZoom: createDataZoom(hBarLabels.length, 12, 12, 'vertical'),
        grid: {
          left: 130,
          right: hBarLabels.length > 12 ? 50 : 70,
          bottom: 20,
          top: 20
        }
      }
    })

    // Gauge Chart - shows the top value as a percentage of total
    const maxValue = Math.max(...values)
    const gaugeValue = Math.round((maxValue / total) * 100)
    charts.push({
      id: `${tableSlug}-gauge`,
      title: `Top ${prettyCategoryCol} Share`,
      description: `${labels[0]}: ${gaugeValue}% of total`,
      type: 'gauge',
      icon: Gauge,
      option: {
        series: [{
          type: 'gauge',
          startAngle: 200,
          endAngle: -20,
          min: 0,
          max: 100,
          splitNumber: 4,
          progress: {
            show: true,
            width: 20,
            itemStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 1, y2: 0,
                colorStops: [
                  { offset: 0, color: chartColors[0] },
                  { offset: 1, color: chartColors[4] }
                ]
              }
            }
          },
          pointer: { show: false },
          axisLine: {
            lineStyle: {
              width: 20,
              color: [[1, '#f3f4f6']]
            }
          },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          anchor: { show: false },
          title: {
            show: true,
            offsetCenter: [0, '70%'],
            fontSize: 13,
            color: '#6b7280',
            fontWeight: 500
          },
          detail: {
            valueAnimation: true,
            offsetCenter: [0, '0%'],
            fontSize: 32,
            fontWeight: 'bold',
            color: '#111827',
            formatter: '{value}%'
          },
          data: [{ value: gaugeValue, name: labels[0] }]
        }]
      }
    })

    // Funnel Chart - Professional styling
    const funnelLabels = labels.slice(0, 6)
    const funnelValues = values.slice(0, 6)
    charts.push({
      id: `${tableSlug}-funnel`,
      title: `${prettyCategoryCol} Funnel`,
      description: 'Conversion funnel view',
      type: 'funnel',
      icon: Filter,
      option: {
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            const formattedValue = formatNumber(params.value, { isCurrency, decimals: 1, compact: false })
            const pct = ((params.value / funnelValues[0]) * 100).toFixed(1)
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${params.name}</div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">Value</span>
                <span style="font-weight: 600;">${formattedValue}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 2px; font-size: 12px;">
                <span style="color: #9ca3af;">vs Top</span>
                <span style="color: #6366f1;">${pct}%</span>
              </div>
            </div>`
          }
        },
        series: [{
          type: 'funnel',
          left: '15%',
          width: '70%',
          top: 30,
          bottom: 30,
          sort: 'descending',
          gap: 4,
          label: {
            show: true,
            position: 'right',
            formatter: (params: any) => `${params.name}\n${formatNumber(params.value, { isCurrency, decimals: 0 })}`,
            fontSize: 11,
            color: '#374151',
            lineHeight: 16
          },
          labelLine: { length: 20, lineStyle: { color: '#d1d5db' } },
          data: funnelLabels.map((name, i) => ({
            value: funnelValues[i],
            name,
            itemStyle: {
              color: chartColors[i % chartColors.length],
              borderColor: '#fff',
              borderWidth: 2
            }
          }))
        }]
      }
    })

    // Radar Chart (if we have enough categories)
    if (labels.length >= 3 && labels.length <= 10) {
      const radarLabels = labels.slice(0, 8)
      const radarValues = values.slice(0, 8)
      const radarMax = Math.max(...radarValues) * 1.2
      charts.push({
        id: `${tableSlug}-radar`,
        title: `${prettyCategoryCol} Radar`,
        description: 'Multi-dimensional comparison',
        type: 'radar',
        icon: Target,
        option: {
          tooltip: {
            trigger: 'item',
            formatter: (params: any) => {
              const data = params.data
              let html = `<div style="padding: 8px 12px;"><div style="font-weight: 600; margin-bottom: 8px;">${prettyValueCol}</div>`
              radarLabels.forEach((label, i) => {
                const formattedValue = formatNumber(data.value[i], { isCurrency, decimals: 0 })
                html += `<div style="display: flex; justify-content: space-between; gap: 16px; margin: 4px 0;">
                  <span style="color: #6b7280;">${label}</span>
                  <span style="font-weight: 500;">${formattedValue}</span>
                </div>`
              })
              html += '</div>'
              return html
            }
          },
          radar: {
            indicator: radarLabels.map((name, i) => ({
              name: name.length > 12 ? name.slice(0, 12) + '...' : name,
              max: radarMax
            })),
            radius: '60%',
            axisName: { color: '#6b7280', fontSize: 11 },
            splitArea: { areaStyle: { color: ['#fff', '#f9fafb'] } },
            axisLine: { lineStyle: { color: '#e5e7eb' } },
            splitLine: { lineStyle: { color: '#e5e7eb' } }
          },
          series: [{
            type: 'radar',
            data: [{
              value: radarValues,
              name: prettyValueCol,
              areaStyle: { color: chartColors[0] + '30' },
              lineStyle: { color: chartColors[0], width: 2 },
              itemStyle: { color: chartColors[0] },
              symbol: 'circle',
              symbolSize: 6
            }]
          }]
        }
      })
    }

    // Scatter Plot (if we have 2+ numeric columns)
    if (numericCols.length >= 2) {
      const xCol = numericCols[0]
      const yCol = numericCols[1]
      const scatterData = rows.map(row => [Number(row[xCol]) || 0, Number(row[yCol]) || 0])
      charts.push({
        id: `${tableSlug}-scatter`,
        title: `${xCol} vs ${yCol}`,
        description: 'Correlation view',
        type: 'scatter',
        icon: ScatterChart,
        option: {
          tooltip: { trigger: 'item', formatter: (params: any) => `${xCol}: ${params.value[0]}<br/>${yCol}: ${params.value[1]}` },
          xAxis: { type: 'value', name: xCol, nameLocation: 'center', nameGap: 30 },
          yAxis: { type: 'value', name: yCol, nameLocation: 'center', nameGap: 40 },
          series: [{
            type: 'scatter',
            data: scatterData,
            symbolSize: 10,
            itemStyle: { color: chartColors[0] }
          }],
          grid: { left: 60, right: 20, bottom: 50, top: 20 }
        }
      })
    }

    // KPI - Total (professional formatting)
    charts.push({
      id: `${tableSlug}-kpi-total`,
      title: `Total ${prettyValueCol}`,
      description: `Sum across ${labels.length} ${prettyCategoryCol.toLowerCase()}s`,
      type: 'kpi',
      icon: Hash,
      option: {},
      kpiValue: formatNumber(total, { isCurrency, isPercent: false, decimals: 1 }),
      kpiLabel: `Total ${prettyValueCol}`,
      kpiChangeLabel: `${labels.length} ${prettyCategoryCol.toLowerCase()}s`
    })
  }

  // ========================================
  // CASE 2: Only text columns (like name, gender)
  // Use the column with LOWEST cardinality (fewest unique values) for grouping
  // e.g., "gender" (2 values) is better than "name" (100+ values)
  // ========================================
  else if (textCols.length > 0 && numericCols.length === 0) {
    // Find the column with the lowest cardinality (fewest unique values)
    let bestCol = textCols[0]
    let bestCardinality = Infinity

    textCols.forEach(colName => {
      const uniqueValues = new Set(rows.map(r => r[colName]))
      if (uniqueValues.size < bestCardinality && uniqueValues.size > 1) {
        bestCardinality = uniqueValues.size
        bestCol = colName
      }
    })

    const categoryCol = bestCol
    const prettyCategoryCol = prettifyColumnName(categoryCol)
    console.log(`CASE 2: Selected "${categoryCol}" as category (${bestCardinality} unique values)`)

    // Count occurrences
    const counts = new Map<string, number>()
    rows.forEach(row => {
      const key = String(row[categoryCol] || 'Unknown')
      counts.set(key, (counts.get(key) || 0) + 1)
    })

    const sorted = Array.from(counts.entries()).sort((a, b) => b[1] - a[1])
    const labels = sorted.map(e => e[0])
    const values = sorted.map(e => e[1])
    const total = values.reduce((a, b) => a + b, 0)
    const formattedTotal = formatNumber(total, { decimals: 0 })

    // Bar Chart - Count (Professional styling)
    charts.push({
      id: `${tableSlug}-bar-count`,
      title: `Count by ${prettyCategoryCol}`,
      description: `${formattedTotal} total records`,
      type: 'bar',
      icon: BarChart3,
      option: {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params: any) => {
            const data = params[0]
            const pct = ((data.value / total) * 100).toFixed(1)
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${data.name}</div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">Count</span>
                <span style="font-weight: 600;">${formatNumber(data.value, { decimals: 0 })}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 4px; color: #9ca3af; font-size: 12px;">
                <span>% of Total</span>
                <span style="color: #6366f1;">${pct}%</span>
              </div>
            </div>`
          }
        },
        xAxis: {
          type: 'category',
          data: labels,
          axisLabel: {
            rotate: labels.length > 6 ? 45 : 0,
            fontSize: 11,
            color: '#6b7280',
            formatter: (val: string) => val.length > 12 ? val.slice(0, 12) + '...' : val
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: (v: number) => formatNumber(v, { decimals: 0 }), fontSize: 11, color: '#6b7280' },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
        },
        series: [{
          type: 'bar',
          data: values.map((v, i) => ({
            value: v,
            itemStyle: { color: chartColors[i % chartColors.length], borderRadius: [4, 4, 0, 0] }
          })),
          barMaxWidth: 50,
          label: {
            show: labels.length <= 8 && labels.length <= 10,
            position: 'top',
            formatter: (params: any) => formatNumber(params.value, { decimals: 0 }),
            fontSize: 11,
            fontWeight: 500,
            color: '#374151'
          }
        }],
        dataZoom: createDataZoom(labels.length, 12, 12, 'horizontal'),
        grid: {
          left: 50,
          right: 20,
          bottom: labels.length > 12 ? 60 : (labels.length > 6 ? 80 : 40),
          top: 40
        }
      }
    })

    // Pie Chart (Professional styling)
    const pieLabels2 = labels.slice(0, 10)
    const pieValues2 = values.slice(0, 10)
    charts.push({
      id: `${tableSlug}-pie-count`,
      title: `${prettyCategoryCol} Distribution`,
      description: pieLabels2.length < labels.length ? `Top ${pieLabels2.length} of ${labels.length} categories` : `${pieLabels2.length} categories`,
      type: 'pie',
      icon: PieChart,
      option: {
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => `<div style="padding: 8px 12px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
              <span style="width: 10px; height: 10px; border-radius: 2px; background: ${params.color};"></span>
              <span style="font-weight: 600;">${params.name}</span>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 24px;">
              <span style="color: #6b7280;">Count</span>
              <span style="font-weight: 600;">${formatNumber(params.value, { decimals: 0 })}</span>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 2px;">
              <span style="color: #6b7280;">Share</span>
              <span style="font-weight: 600; color: #6366f1;">${params.percent.toFixed(1)}%</span>
            </div>
          </div>`
        },
        legend: {
          type: 'scroll',
          orient: 'vertical',
          right: 10,
          top: 'center',
          textStyle: { fontSize: 11, color: '#6b7280' }
        },
        series: [{
          type: 'pie',
          radius: ['0%', '65%'],
          center: ['35%', '50%'],
          data: pieLabels2.map((name, i) => ({
            value: pieValues2[i],
            name,
            itemStyle: { color: chartColors[i % chartColors.length] }
          })),
          label: { show: pieLabels2.length <= 6, formatter: '{d}%', fontSize: 11 },
          emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.2)' } }
        }]
      }
    })

    // Donut (Professional styling)
    charts.push({
      id: `${tableSlug}-donut-count`,
      title: `${prettyCategoryCol} Breakdown`,
      description: `Total: ${formattedTotal} records`,
      type: 'donut',
      icon: PieChart,
      option: {
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => `<div style="padding: 8px 12px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
              <span style="width: 10px; height: 10px; border-radius: 2px; background: ${params.color};"></span>
              <span style="font-weight: 600;">${params.name}</span>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 24px;">
              <span style="color: #6b7280;">Count</span>
              <span style="font-weight: 600;">${formatNumber(params.value, { decimals: 0 })}</span>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 2px;">
              <span style="color: #6b7280;">Share</span>
              <span style="font-weight: 600; color: #6366f1;">${params.percent.toFixed(1)}%</span>
            </div>
          </div>`
        },
        graphic: [{
          type: 'text',
          left: 'center',
          top: '45%',
          style: { text: formattedTotal, textAlign: 'center', fontSize: 24, fontWeight: 'bold', fill: '#111827' }
        }, {
          type: 'text',
          left: 'center',
          top: '55%',
          style: { text: 'Total', textAlign: 'center', fontSize: 12, fill: '#9ca3af' }
        }],
        series: [{
          type: 'pie',
          radius: ['50%', '70%'],
          data: pieLabels2.map((name, i) => ({
            value: pieValues2[i],
            name,
            itemStyle: { color: chartColors[i % chartColors.length] }
          })),
          label: { show: false },
          emphasis: { label: { show: true, fontSize: 12, fontWeight: 'bold' } }
        }]
      }
    })

    // Line Chart (Professional styling)
    charts.push({
      id: `${tableSlug}-line-count`,
      title: `${prettyCategoryCol} Trend`,
      description: 'Count distribution',
      type: 'line',
      icon: LineChart,
      option: {
        tooltip: {
          trigger: 'axis',
          formatter: (params: any) => {
            const data = params[0]
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${data.name}</div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">Count</span>
                <span style="font-weight: 600;">${formatNumber(data.value, { decimals: 0 })}</span>
              </div>
            </div>`
          }
        },
        xAxis: {
          type: 'category',
          data: labels,
          axisLabel: { rotate: labels.length > 6 ? 45 : 0, fontSize: 11, color: '#6b7280' },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: (v: number) => formatNumber(v, { decimals: 0 }), fontSize: 11, color: '#6b7280' },
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
        },
        series: [{
          type: 'line',
          data: values,
          smooth: true,
          symbol: 'circle',
          symbolSize: labels.length > 20 ? 4 : 6,
          itemStyle: { color: chartColors[0] },
          lineStyle: { width: labels.length > 30 ? 2 : 3 }
        }],
        dataZoom: createDataZoom(labels.length, 15, 15, 'horizontal'),
        grid: {
          left: 50,
          right: 20,
          bottom: labels.length > 15 ? 60 : (labels.length > 6 ? 80 : 40),
          top: 30
        }
      }
    })

    // Area Chart (Professional styling)
    charts.push({
      id: `${tableSlug}-area-count`,
      title: `${prettyCategoryCol} Area`,
      description: 'Filled area visualization',
      type: 'area',
      icon: AreaChart,
      option: {
        tooltip: {
          trigger: 'axis',
          formatter: (params: any) => {
            const data = params[0]
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${data.name}</div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">Count</span>
                <span style="font-weight: 600;">${formatNumber(data.value, { decimals: 0 })}</span>
              </div>
            </div>`
          }
        },
        xAxis: {
          type: 'category',
          data: labels,
          boundaryGap: false,
          axisLabel: { rotate: labels.length > 6 ? 45 : 0, fontSize: 11, color: '#6b7280' },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: (v: number) => formatNumber(v, { decimals: 0 }), fontSize: 11, color: '#6b7280' },
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
        },
        series: [{
          type: 'line',
          data: values,
          smooth: true,
          symbol: 'none',
          areaStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: chartColors[0] + 'cc' },
                { offset: 0.7, color: chartColors[0] + '40' },
                { offset: 1, color: chartColors[0] + '05' }
              ]
            }
          },
          itemStyle: { color: chartColors[0] },
          lineStyle: { width: 2 }
        }],
        dataZoom: createDataZoom(labels.length, 15, 15, 'horizontal'),
        grid: {
          left: 50,
          right: 20,
          bottom: labels.length > 15 ? 60 : (labels.length > 6 ? 80 : 40),
          top: 20
        }
      }
    })

    // Horizontal Bar Chart (Professional styling - scrollable for all data)
    const hBarLabels2 = labels // Use all data, not sliced
    const hBarValues2 = values
    charts.push({
      id: `${tableSlug}-horizontal-bar-count`,
      title: `Count by ${prettyCategoryCol}`,
      description: `${hBarLabels2.length} categories ranked`,
      type: 'horizontal-bar',
      icon: BarChartHorizontal,
      option: {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params: any) => {
            const data = params[0]
            const pct = ((data.value / total) * 100).toFixed(1)
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${data.name}</div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">Count</span>
                <span style="font-weight: 600;">${formatNumber(data.value, { decimals: 0 })}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 2px; font-size: 12px; color: #9ca3af;">
                <span>Share</span>
                <span style="color: #6366f1;">${pct}%</span>
              </div>
            </div>`
          }
        },
        xAxis: {
          type: 'value',
          axisLabel: { formatter: (v: number) => formatNumber(v, { decimals: 0 }), fontSize: 11, color: '#6b7280' },
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
        },
        yAxis: {
          type: 'category',
          data: hBarLabels2.slice().reverse(),
          axisLabel: {
            fontSize: 11,
            color: '#374151',
            formatter: (val: string) => val.length > 15 ? val.slice(0, 15) + '...' : val
          },
          axisLine: { show: false },
          axisTick: { show: false }
        },
        series: [{
          type: 'bar',
          data: hBarValues2.slice().reverse().map((v, i) => ({
            value: v,
            itemStyle: { color: chartColors[(hBarValues2.length - 1 - i) % chartColors.length], borderRadius: [0, 4, 4, 0] }
          })),
          barMaxWidth: 20,
          label: {
            show: hBarLabels2.length <= 15,
            position: 'right',
            formatter: (params: any) => formatNumber(params.value, { decimals: 0 }),
            fontSize: 10,
            color: '#374151'
          }
        }],
        dataZoom: createDataZoom(hBarLabels2.length, 12, 12, 'vertical'),
        grid: {
          left: 130,
          right: hBarLabels2.length > 12 ? 50 : 70,
          bottom: 20,
          top: 20
        }
      }
    })

    // Gauge Chart (Professional styling)
    const maxValue2 = Math.max(...values)
    const gaugeValue2 = Math.round((maxValue2 / total) * 100)
    charts.push({
      id: `${tableSlug}-gauge-count`,
      title: `Top ${prettyCategoryCol} Share`,
      description: `${labels[0]}: ${gaugeValue2}% of total`,
      type: 'gauge',
      icon: Gauge,
      option: {
        series: [{
          type: 'gauge',
          startAngle: 200,
          endAngle: -20,
          min: 0,
          max: 100,
          splitNumber: 4,
          progress: {
            show: true,
            width: 20,
            itemStyle: {
              color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: chartColors[0] }, { offset: 1, color: chartColors[4] }] }
            }
          },
          pointer: { show: false },
          axisLine: { lineStyle: { width: 20, color: [[1, '#f3f4f6']] } },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          title: { show: true, offsetCenter: [0, '70%'], fontSize: 13, color: '#6b7280', fontWeight: 500 },
          detail: { valueAnimation: true, offsetCenter: [0, '0%'], fontSize: 32, fontWeight: 'bold', color: '#111827', formatter: '{value}%' },
          data: [{ value: gaugeValue2, name: labels[0] }]
        }]
      }
    })

    // Funnel Chart (Professional styling)
    const funnelLabels2 = labels.slice(0, 6)
    const funnelValues2 = values.slice(0, 6)
    charts.push({
      id: `${tableSlug}-funnel-count`,
      title: `${prettyCategoryCol} Funnel`,
      description: 'Conversion funnel view',
      type: 'funnel',
      icon: Filter,
      option: {
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            const pct = ((params.value / funnelValues2[0]) * 100).toFixed(1)
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 6px;">${params.name}</div>
              <div style="display: flex; justify-content: space-between; gap: 24px;">
                <span style="color: #6b7280;">Count</span>
                <span style="font-weight: 600;">${formatNumber(params.value, { decimals: 0 })}</span>
              </div>
              <div style="display: flex; justify-content: space-between; gap: 24px; margin-top: 2px; font-size: 12px;">
                <span style="color: #9ca3af;">vs Top</span>
                <span style="color: #6366f1;">${pct}%</span>
              </div>
            </div>`
          }
        },
        series: [{
          type: 'funnel',
          left: '15%',
          width: '70%',
          top: 30,
          bottom: 30,
          sort: 'descending',
          gap: 4,
          label: {
            show: true,
            position: 'right',
            formatter: (params: any) => `${params.name}\n${formatNumber(params.value, { decimals: 0 })}`,
            fontSize: 11,
            color: '#374151',
            lineHeight: 16
          },
          labelLine: { length: 20, lineStyle: { color: '#d1d5db' } },
          data: funnelLabels2.map((name, i) => ({
            value: funnelValues2[i],
            name,
            itemStyle: { color: chartColors[i % chartColors.length], borderColor: '#fff', borderWidth: 2 }
          }))
        }]
      }
    })

    // Radar Chart (Professional styling)
    if (labels.length >= 3 && labels.length <= 10) {
      const radarLabels2 = labels.slice(0, 8)
      const radarValues2 = values.slice(0, 8)
      const radarMax2 = Math.max(...radarValues2) * 1.2
      charts.push({
        id: `${tableSlug}-radar-count`,
        title: `${prettyCategoryCol} Radar`,
        description: 'Multi-dimensional comparison',
        type: 'radar',
        icon: Target,
        option: {
          tooltip: {
            trigger: 'item',
            formatter: (params: any) => {
              const data = params.data
              let html = `<div style="padding: 8px 12px;"><div style="font-weight: 600; margin-bottom: 8px;">Count Distribution</div>`
              radarLabels2.forEach((label, i) => {
                html += `<div style="display: flex; justify-content: space-between; gap: 16px; margin: 4px 0;">
                  <span style="color: #6b7280;">${label}</span>
                  <span style="font-weight: 500;">${formatNumber(data.value[i], { decimals: 0 })}</span>
                </div>`
              })
              html += '</div>'
              return html
            }
          },
          radar: {
            indicator: radarLabels2.map(name => ({
              name: name.length > 12 ? name.slice(0, 12) + '...' : name,
              max: radarMax2
            })),
            radius: '60%',
            axisName: { color: '#6b7280', fontSize: 11 },
            splitArea: { areaStyle: { color: ['#fff', '#f9fafb'] } },
            axisLine: { lineStyle: { color: '#e5e7eb' } },
            splitLine: { lineStyle: { color: '#e5e7eb' } }
          },
          series: [{
            type: 'radar',
            data: [{
              value: radarValues2,
              name: 'Count',
              areaStyle: { color: chartColors[0] + '30' },
              lineStyle: { color: chartColors[0], width: 2 },
              itemStyle: { color: chartColors[0] },
              symbol: 'circle',
              symbolSize: 6
            }]
          }]
        }
      })
    }

    // Total KPI (Professional formatting)
    charts.push({
      id: `${tableSlug}-kpi-total`,
      title: 'Total Records',
      description: `Count across ${labels.length} ${prettyCategoryCol.toLowerCase()}s`,
      type: 'kpi',
      icon: Hash,
      option: {},
      kpiValue: formattedTotal,
      kpiLabel: 'Total Records',
      kpiChangeLabel: `${labels.length} ${prettyCategoryCol.toLowerCase()}s`
    })
  }

  // ========================================
  // CASE 3: Only numeric columns
  // Show summary stats
  // ========================================
  else if (numericCols.length > 0) {
    const valueCol = numericCols[0]
    const prettyValueCol = prettifyColumnName(valueCol)
    const values = rows.map(r => Number(r[valueCol]) || 0)
    const total = values.reduce((a, b) => a + b, 0)
    const avg = total / values.length
    const max = Math.max(...values)
    const min = Math.min(...values)

    // Detect formatting
    const isCurrency = isCurrencyColumn(valueCol, values)
    const isPercent = isPercentageColumn(valueCol, values)

    // Summary Bar (Professional styling)
    charts.push({
      id: `${tableSlug}-summary`,
      title: `${prettyValueCol} Summary`,
      description: 'Statistical overview',
      type: 'bar',
      icon: BarChart3,
      option: {
        tooltip: {
          trigger: 'axis',
          formatter: (params: any) => {
            const data = params[0]
            const formattedValue = formatNumber(data.value, { isCurrency, isPercent, decimals: 1, compact: false })
            return `<div style="padding: 8px 12px;">
              <div style="font-weight: 600; margin-bottom: 4px;">${data.name}</div>
              <span style="font-weight: 600;">${formattedValue}</span>
            </div>`
          }
        },
        xAxis: {
          type: 'category',
          data: ['Total', 'Average', 'Maximum', 'Minimum'],
          axisLabel: { fontSize: 11, color: '#6b7280' },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: (v: number) => formatNumber(v, { isCurrency, isPercent, decimals: 0 }), fontSize: 11, color: '#6b7280' },
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
        },
        series: [{
          type: 'bar',
          data: [
            { value: Math.round(total * 100) / 100, itemStyle: { color: chartColors[0], borderRadius: [4, 4, 0, 0] } },
            { value: Math.round(avg * 100) / 100, itemStyle: { color: chartColors[1], borderRadius: [4, 4, 0, 0] } },
            { value: Math.round(max * 100) / 100, itemStyle: { color: chartColors[2], borderRadius: [4, 4, 0, 0] } },
            { value: Math.round(min * 100) / 100, itemStyle: { color: chartColors[3], borderRadius: [4, 4, 0, 0] } }
          ],
          barMaxWidth: 60,
          label: {
            show: true,
            position: 'top',
            formatter: (params: any) => formatNumber(params.value, { isCurrency, isPercent, decimals: 0 }),
            fontWeight: 500,
            fontSize: 11,
            color: '#374151'
          }
        }],
        grid: { left: 60, right: 20, bottom: 40, top: 40 }
      }
    })

    // KPIs (Professional formatting)
    charts.push({
      id: `${tableSlug}-kpi-total`,
      title: `Total ${prettyValueCol}`,
      description: 'Sum of all values',
      type: 'kpi',
      icon: Hash,
      option: {},
      kpiValue: formatNumber(total, { isCurrency, isPercent: false, decimals: 1 }),
      kpiLabel: `Total ${prettyValueCol}`,
      kpiChangeLabel: `${rows.length.toLocaleString()} records`
    })

    charts.push({
      id: `${tableSlug}-kpi-avg`,
      title: `Average ${prettyValueCol}`,
      description: 'Mean value',
      type: 'kpi',
      icon: Hash,
      option: {},
      kpiValue: formatNumber(avg, { isCurrency, isPercent, decimals: 1 }),
      kpiLabel: `Average ${prettyValueCol}`,
      kpiChangeLabel: `${rows.length.toLocaleString()} records`
    })
  }

  // ========================================
  // Always add Data Table
  // ========================================
  charts.push({
    id: `${tableSlug}-table`,
    title: 'Data Table',
    description: `${rows.length} rows × ${columns.length} columns`,
    type: 'table',
    icon: TableIcon,
    option: {},
    tableColumns: colNames.slice(0, 10),
    tableRows: rows
  })

  console.log('=== CHARTS GENERATED ===')
  console.log('Total charts:', charts.length)
  console.log('Chart types:', charts.map(c => c.type))
  charts.forEach(c => console.log(`  - ${c.type}: ${c.title}`))

  return charts
}

export function ChartBuilder() {
  const { id: chartId } = useParams()
  const navigate = useNavigate()

  const [viewMode, setViewMode] = useState<ViewMode>('recipes')
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [dataSourceType, setDataSourceType] = useState<DataSourceType>('transforms')

  // Recipes state
  const [transformRecipes, setTransformRecipes] = useState<TransformRecipe[]>([])
  const [recipePreviews, setRecipePreviews] = useState<Map<string, RecipePreview>>(new Map())
  const [connections, setConnections] = useState<Map<string, Connection>>(new Map())

  // Semantic Models state
  const [semanticModels, setSemanticModels] = useState<SemanticModelSummary[]>([])
  const [selectedModel, setSelectedModel] = useState<SemanticModel | null>(null)
  const [selectedMeasures, setSelectedMeasures] = useState<string[]>([])
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>([])
  const [modelQueryLoading, setModelQueryLoading] = useState(false)

  // Saved Charts state
  const [savedCharts, setSavedCharts] = useState<SavedChart[]>([])
  const [savedChartsLoading, setSavedChartsLoading] = useState(false)

  // Viewing a specific saved chart
  const [viewingChart, setViewingChart] = useState<SavedChart | null>(null)
  const [viewingChartLoading, setViewingChartLoading] = useState(false)
  const [viewingChartData, setViewingChartData] = useState<{ columns: string[]; rows: any[]; chart_type: string } | null>(null)
  const [viewingChartError, setViewingChartError] = useState<string | null>(null)

  // Selected recipe & charts state
  const [selectedRecipe, setSelectedRecipe] = useState<TransformRecipe | null>(null)
  const [generatedCharts, setGeneratedCharts] = useState<GeneratedChart[]>([])
  const [selectedChart, setSelectedChart] = useState<GeneratedChart | null>(null)
  const [chartsLoading, setChartsLoading] = useState(false)
  const [columns, setColumns] = useState<ColumnInfo[]>([])
  const [preview, setPreview] = useState<TablePreview | null>(null)

  // Save to dashboard state
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [dashboards, setDashboards] = useState<DashboardInfo[]>([])
  const [dashboardsLoading, setDashboardsLoading] = useState(false)
  const [selectedDashboardId, setSelectedDashboardId] = useState<string | null>(null)
  const [newDashboardName, setNewDashboardName] = useState('')
  const [createNewDashboard, setCreateNewDashboard] = useState(false)
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [customChartName, setCustomChartName] = useState('')

  // Table state for sorting and pagination
  const [tableSortColumn, setTableSortColumn] = useState<string | null>(null)
  const [tableSortDirection, setTableSortDirection] = useState<'asc' | 'desc'>('asc')
  const [tableCurrentPage, setTableCurrentPage] = useState(1)
  const [tableRowsPerPage, setTableRowsPerPage] = useState(25)

  // Ref for the main chart to enable export
  const mainChartRef = useRef<any>(null)
  const viewingChartRef = useRef<any>(null)

  // Download chart as image
  const downloadChartAsImage = (chartRef: React.RefObject<any>, chartTitle: string) => {
    if (!chartRef.current) {
      console.error('Chart ref not available')
      return
    }

    try {
      const echartInstance = chartRef.current.getEchartsInstance()
      if (!echartInstance) {
        console.error('ECharts instance not available')
        return
      }

      const dataURL = echartInstance.getDataURL({
        type: 'png',
        pixelRatio: 2, // Higher resolution
        backgroundColor: '#fff'
      })

      // Create download link
      const link = document.createElement('a')
      link.download = `${chartTitle.replace(/[^a-z0-9]/gi, '_')}.png`
      link.href = dataURL
      link.click()
    } catch (error) {
      console.error('Failed to export chart:', error)
    }
  }

  // Format cell value based on type
  const formatCellValue = (value: any): string => {
    if (value === null || value === undefined) return ''

    // Check if it's a number
    if (typeof value === 'number' || (!isNaN(Number(value)) && value !== '')) {
      const num = Number(value)
      // Check if it looks like currency (has 2 decimal places)
      if (Number.isFinite(num)) {
        if (Math.abs(num) >= 1000000) {
          return `${(num / 1000000).toFixed(2)}M`
        } else if (Math.abs(num) >= 1000) {
          return num.toLocaleString('en-US', { maximumFractionDigits: 2 })
        }
        return num.toLocaleString('en-US', { maximumFractionDigits: 2 })
      }
    }

    // Check if it's a date
    if (typeof value === 'string') {
      const dateMatch = value.match(/^\d{4}-\d{2}-\d{2}/)
      if (dateMatch) {
        const date = new Date(value)
        if (!isNaN(date.getTime())) {
          return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
        }
      }
    }

    return String(value)
  }

  // Handle table column sort
  const handleTableSort = (column: string) => {
    if (tableSortColumn === column) {
      setTableSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setTableSortColumn(column)
      setTableSortDirection('asc')
    }
    setTableCurrentPage(1) // Reset to first page on sort
  }

  // Get sorted and paginated table data
  const getTableData = (rows: Record<string, any>[] | undefined, columns: string[] | undefined) => {
    if (!rows || !columns) return { sortedRows: [], totalPages: 0, startIndex: 0, endIndex: 0 }

    let sortedRows = [...rows]

    // Sort if column selected
    if (tableSortColumn && columns.includes(tableSortColumn)) {
      sortedRows.sort((a, b) => {
        const aVal = a[tableSortColumn]
        const bVal = b[tableSortColumn]

        // Handle nulls
        if (aVal === null || aVal === undefined) return tableSortDirection === 'asc' ? 1 : -1
        if (bVal === null || bVal === undefined) return tableSortDirection === 'asc' ? -1 : 1

        // Numeric comparison
        const aNum = Number(aVal)
        const bNum = Number(bVal)
        if (!isNaN(aNum) && !isNaN(bNum)) {
          return tableSortDirection === 'asc' ? aNum - bNum : bNum - aNum
        }

        // String comparison
        const aStr = String(aVal).toLowerCase()
        const bStr = String(bVal).toLowerCase()
        if (tableSortDirection === 'asc') {
          return aStr.localeCompare(bStr)
        }
        return bStr.localeCompare(aStr)
      })
    }

    // Pagination
    const totalPages = Math.ceil(sortedRows.length / tableRowsPerPage)
    const startIndex = (tableCurrentPage - 1) * tableRowsPerPage
    const endIndex = Math.min(startIndex + tableRowsPerPage, sortedRows.length)
    const paginatedRows = sortedRows.slice(startIndex, endIndex)

    return { sortedRows: paginatedRows, totalPages, startIndex, endIndex, totalRows: sortedRows.length }
  }

  // Reset table state when chart changes
  useEffect(() => {
    setTableSortColumn(null)
    setTableSortDirection('asc')
    setTableCurrentPage(1)
  }, [selectedChart?.id])

  useEffect(() => {
    fetchAllData()
  }, [])

  // Fetch specific chart if ID is in URL
  useEffect(() => {
    if (chartId) {
      fetchSavedChart(chartId)
    } else {
      setViewingChart(null)
    }
  }, [chartId])

  const fetchSavedChart = async (id: string) => {
    setViewingChartLoading(true)
    setViewingChartError(null)
    setViewingChartData(null)
    try {
      // Fetch chart metadata
      const response = await api.get(`/dashboards/charts/${id}`)
      const chart = response.data
      console.log('Fetched chart:', chart)
      setViewingChart(chart)

      // Fetch live data from render endpoint
      try {
        const renderResponse = await api.get(`/charts/${id}/render`)
        console.log('Rendered chart data:', renderResponse.data)
        setViewingChartData(renderResponse.data)
      } catch (renderError: any) {
        console.error('Failed to render chart:', renderError)
        setViewingChartError(renderError.response?.data?.detail || 'Failed to load chart data')
      }
    } catch (error) {
      console.error('Failed to fetch chart:', error)
      setViewingChart(null)
    } finally {
      setViewingChartLoading(false)
    }
  }

  const deleteChart = async (id: string) => {
    if (!confirm('Are you sure you want to delete this chart?')) return

    try {
      await api.delete(`/dashboards/charts/${id}`)
      navigate('/charts/new')
    } catch (error) {
      console.error('Failed to delete chart:', error)
    }
  }

  const toggleFavorite = async (chart: SavedChart) => {
    try {
      const response = await api.post(`/dashboards/charts/${chart.id}/favorite`)
      setViewingChart(response.data)
    } catch (error) {
      console.error('Failed to toggle favorite:', error)
    }
  }

  const fetchAllData = async () => {
    setLoading(true)
    try {
      // Fetch all connections first
      const connectionsRes = await api.get('/connections/')
      const connectionsData = connectionsRes.data
      const connMap = new Map<string, Connection>()
      connectionsData.forEach((c: Connection) => connMap.set(c.id, c))
      setConnections(connMap)

      // Fetch all transform recipes
      const recipesRes = await api.get('/transforms/')
      const recipesData = recipesRes.data
      setTransformRecipes(recipesData)
      // Fetch previews for each recipe
      recipesData.forEach((recipe: TransformRecipe) => {
        fetchRecipePreview(recipe)
      })

      // Fetch all semantic models
      const modelsRes = await api.get('/models/')
      setSemanticModels(modelsRes.data)

      // Fetch all saved charts
      const chartsRes = await api.get('/dashboards/charts/all')
      setSavedCharts(chartsRes.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRecipePreview = async (recipe: TransformRecipe) => {
    setRecipePreviews(prev => {
      const newMap = new Map(prev)
      newMap.set(recipe.id, { recipeId: recipe.id, chart: null, loading: true, error: false })
      return newMap
    })

    try {
      const response = await api.post(`/transforms/${recipe.id}/execute?preview=true&limit=50`)

      const result = response.data
      const cols: ColumnInfo[] = result.columns.map((c: any) => ({
        name: c.name,
        type: c.type || 'text',
        nullable: true,
      }))
      const rows: Record<string, any>[] = result.rows || []

      let previewChart: GeneratedChart | null = null
      if (cols.length > 0 && rows.length > 0) {
        const charts = generateCharts(cols, rows, recipe.name, recipe.steps || [])
        previewChart = charts.find(c => c.type === 'bar') ||
                       charts.find(c => c.type === 'pie') ||
                       charts.find(c => c.type === 'line') ||
                       charts[0] || null
      }

      setRecipePreviews(prev => {
        const newMap = new Map(prev)
        newMap.set(recipe.id, { recipeId: recipe.id, chart: previewChart, loading: false, error: false })
        return newMap
      })
    } catch (error) {
      console.error(`Failed to fetch preview for recipe ${recipe.id}:`, error)
      setRecipePreviews(prev => {
        const newMap = new Map(prev)
        newMap.set(recipe.id, { recipeId: recipe.id, chart: null, loading: false, error: true })
        return newMap
      })
    }
  }

  const selectRecipe = async (recipe: TransformRecipe) => {
    setSelectedRecipe(recipe)
    setViewMode('charts')
    setChartsLoading(true)
    setGeneratedCharts([])
    setSelectedChart(null)

    try {
      const response = await api.post(`/transforms/${recipe.id}/execute?preview=true&limit=500`)

      const result = response.data
      const cols: ColumnInfo[] = result.columns.map((c: any) => ({
        name: c.name,
        type: c.type || 'text',
        nullable: true,
      }))
      const rows: Record<string, any>[] = result.rows || []

      setColumns(cols)
      setPreview({
        columns: cols.map(c => c.name),
        rows: rows,
        total: result.total_rows || rows.length,
        preview_count: rows.length,
      })

      if (cols.length > 0 && rows.length > 0) {
        const charts = generateCharts(cols, rows, recipe.name, recipe.steps || [])
        setGeneratedCharts(charts)
        if (charts.length > 0) setSelectedChart(charts[0])
      }
    } catch (error) {
      console.error('Failed to generate charts:', error)
    } finally {
      setChartsLoading(false)
    }
  }

  const goBack = () => {
    setViewMode('recipes')
    setSelectedRecipe(null)
    setSelectedModel(null)
    setSelectedMeasures([])
    setSelectedDimensions([])
    setGeneratedCharts([])
    setSelectedChart(null)
    setPreview(null)
    setColumns([])
  }

  // Select a semantic model and load its details
  const selectSemanticModel = async (modelSummary: SemanticModelSummary) => {
    setViewMode('charts')
    setChartsLoading(true)
    setGeneratedCharts([])
    setSelectedChart(null)
    setSelectedMeasures([])
    setSelectedDimensions([])

    try {
      // Fetch full model details
      const response = await api.get(`/models/${modelSummary.id}`)
      const model: SemanticModel = response.data
      setSelectedModel(model)

      // Auto-select first measure and dimension if available
      if (model.measures.length > 0) {
        setSelectedMeasures([model.measures[0].id])
      }
      if (model.dimensions.length > 0) {
        setSelectedDimensions([model.dimensions[0].id])
      }

      // If we have both measure and dimension, run initial query
      if (model.measures.length > 0 && model.dimensions.length > 0) {
        await executeModelQuery(model, [model.measures[0].id], [model.dimensions[0].id])
      } else if (model.measures.length > 0) {
        // Just measures - show totals
        await executeModelQuery(model, [model.measures[0].id], [])
      } else {
        // No measures defined - can't generate charts
        console.log('Model has no measures defined')
        setChartsLoading(false)
      }
    } catch (error) {
      console.error('Failed to select model:', error)
      setChartsLoading(false)
    }
  }

  // Execute query using semantic model
  const executeModelQuery = async (
    model: SemanticModel,
    measureIds: string[],
    dimensionIds: string[]
  ) => {
    setModelQueryLoading(true)
    setChartsLoading(true)

    try {
      // Get selected measures and dimensions
      const measures = model.measures.filter(m => measureIds.includes(m.id))
      const dimensions = model.dimensions.filter(d => dimensionIds.includes(d.id))

      // Use the backend's model preview endpoint - it handles both table and transform-based models
      console.log('Executing model preview:', { modelId: model.id, measureIds, dimensionIds })
      const queryResponse = await api.post(`/models/${model.id}/preview`, {
        measure_ids: measureIds,
        dimension_ids: dimensionIds,
        limit: 500
      })

      const result = queryResponse.data
      console.log('Model preview result:', result)

      // Handle columns - can be array of strings or array of objects
      const cols: ColumnInfo[] = result.columns.map((c: any) => ({
        name: typeof c === 'string' ? c : (c.name || c),
        type: typeof c === 'string' ? 'text' : (c.type || 'text'),
        nullable: true
      }))
      const rows: Record<string, any>[] = result.rows || []

      setColumns(cols)
      setPreview({
        columns: cols.map(c => c.name),
        rows: rows,
        total: result.total_rows || rows.length,
        preview_count: rows.length
      })

      // Generate charts
      console.log('Generating charts with:', { cols, rowCount: rows.length })
      if (cols.length > 0 && rows.length > 0) {
        const modelName = `${model.name} - ${measures.map(m => m.name).join(', ')}`
        const charts = generateCharts(cols, rows, modelName, [])
        console.log('Generated charts:', charts.length)
        setGeneratedCharts(charts)
        if (charts.length > 0) setSelectedChart(charts[0])
      } else {
        console.log('No data to generate charts - cols:', cols.length, 'rows:', rows.length)
        setGeneratedCharts([])
      }
    } catch (error) {
      console.error('Failed to execute model query:', error)
      setGeneratedCharts([])
    } finally {
      setModelQueryLoading(false)
      setChartsLoading(false)
    }
  }

  // Handle measure/dimension selection changes
  const handleMeasureToggle = (measureId: string) => {
    const newSelection = selectedMeasures.includes(measureId)
      ? selectedMeasures.filter(id => id !== measureId)
      : [...selectedMeasures, measureId]

    setSelectedMeasures(newSelection)

    // Re-run query with new selection
    if (selectedModel && newSelection.length > 0) {
      executeModelQuery(selectedModel, newSelection, selectedDimensions)
    }
  }

  const handleDimensionToggle = (dimensionId: string) => {
    const newSelection = selectedDimensions.includes(dimensionId)
      ? selectedDimensions.filter(id => id !== dimensionId)
      : [...selectedDimensions, dimensionId]

    setSelectedDimensions(newSelection)

    // Re-run query with new selection
    if (selectedModel && selectedMeasures.length > 0) {
      executeModelQuery(selectedModel, selectedMeasures, newSelection)
    }
  }

  const fetchDashboards = async () => {
    try {
      setDashboardsLoading(true)
      const response = await api.get('/dashboards/')
      setDashboards(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboards:', error)
    } finally {
      setDashboardsLoading(false)
    }
  }

  const openSaveModal = () => {
    setShowSaveModal(true)
    setSelectedDashboardId(null)
    setNewDashboardName('')
    setCreateNewDashboard(false)
    setSaveSuccess(false)
    // Set default chart name from selected chart title
    setCustomChartName(selectedChart?.title || '')
    fetchDashboards()
  }

  const closeSaveModal = () => {
    setShowSaveModal(false)
    setSaveSuccess(false)
  }

  const saveChartToDashboard = async () => {
    if (!selectedChart || (!selectedRecipe && !selectedModel)) return

    // Debug: Log what we're saving
    console.log('=== SAVING CHART ===')
    console.log('selectedChart:', selectedChart)
    console.log('selectedChart.type:', selectedChart.type)
    console.log('selectedChart.option:', selectedChart.option)
    console.log('selectedChart.option.series:', selectedChart.option?.series)
    console.log('Series type:', selectedChart.option?.series?.[0]?.type)

    try {
      setSaveLoading(true)
      let dashboardId = selectedDashboardId

      if (createNewDashboard && newDashboardName.trim()) {
        const dashboardRes = await api.post('/dashboards/', {
          name: newDashboardName.trim(),
          description: `Created from Chart Builder`,
        })

        dashboardId = dashboardRes.data.id
      }

      let chartPayload: any

      // Use custom name if provided, otherwise fall back to auto-generated title
      const chartName = customChartName.trim() || selectedChart.title

      // Build chart_config based on chart type
      let chartConfig: any
      if (selectedChart.type === 'table') {
        // Validate table data exists
        if (!selectedChart.tableColumns || selectedChart.tableColumns.length === 0) {
          console.error('Table chart is missing tableColumns!')
          alert('Cannot save table chart: missing column data')
          return
        }
        if (!selectedChart.tableRows || selectedChart.tableRows.length === 0) {
          console.error('Table chart is missing tableRows!')
          alert('Cannot save table chart: missing row data')
          return
        }
        chartConfig = {
          tableColumns: selectedChart.tableColumns,
          tableRows: selectedChart.tableRows,
        }
      } else if (selectedChart.type === 'kpi') {
        // KPI charts store value and label
        chartConfig = {
          kpiValue: selectedChart.kpiValue,
          kpiLabel: selectedChart.kpiLabel,
          kpiChange: selectedChart.kpiChange,
          kpiChangeLabel: selectedChart.kpiChangeLabel,
        }
      } else {
        chartConfig = selectedChart.option
      }

      if (selectedModel) {
        // Saving chart from semantic model
        chartPayload = {
          name: chartName,
          description: selectedChart.description,
          connection_id: selectedModel.connection_id,
          chart_type: selectedChart.type,
          chart_config: chartConfig,
          query_config: {
            data_source: 'semantic_model',
            model_id: selectedModel.id,
            model_name: selectedModel.name,
            measures: selectedMeasures,
            dimensions: selectedDimensions,
          },
          dashboard_id: dashboardId || undefined,
        }
      } else if (selectedRecipe) {
        // Saving chart from transform
        chartPayload = {
          name: chartName,
          description: selectedChart.description,
          connection_id: selectedRecipe.connection_id,
          chart_type: selectedChart.type,
          chart_config: chartConfig,
          query_config: {
            data_source: 'transform',
            recipe_id: selectedRecipe.id,
            recipe_name: selectedRecipe.name,
          },
          transform_recipe_id: selectedRecipe.id,
          dashboard_id: dashboardId || undefined,
        }
      }

      // Debug: Log what we're about to save for table charts
      if (selectedChart.type === 'table') {
        console.log('=== SAVING TABLE CHART ===')
        console.log('chartConfig:', chartConfig)
        console.log('tableColumns:', (chartConfig as any)?.tableColumns)
        console.log('tableRows count:', (chartConfig as any)?.tableRows?.length)
      }

      await api.post('/dashboards/charts', chartPayload)

      setSaveSuccess(true)
      setTimeout(() => closeSaveModal(), 1500)
    } catch (error) {
      console.error('Failed to save chart:', error)
      alert('Failed to save chart. Please try again.')
    } finally {
      setSaveLoading(false)
    }
  }

  // Filter recipes by search
  const filteredRecipes = transformRecipes.filter(r =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (r.description || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.source_table.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Filter models by search
  const filteredModels = semanticModels.filter(m =>
    m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (m.description || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (m.table_name || '').toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Filter saved charts by search
  const filteredSavedCharts = savedCharts.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (c.description || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.chart_type.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // === VIEWING SAVED CHART ===
  if (chartId && (viewingChart || viewingChartLoading)) {
    if (viewingChartLoading) {
      return (
        <div className="h-full flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
          <div className="text-center">
            <Loader2 className="w-10 h-10 animate-spin text-indigo-500 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">Loading chart...</p>
          </div>
        </div>
      )
    }

    if (!viewingChart) {
      return (
        <div className="h-full flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
          <div className="text-center">
            <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Chart not found</h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">The chart you're looking for doesn't exist or has been deleted.</p>
            <button
              onClick={() => navigate('/charts/new')}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-500 text-white rounded-xl font-medium hover:bg-indigo-600 transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Charts
            </button>
          </div>
        </div>
      )
    }

    // Build chart option from LIVE rendered data (not the empty template config)
    const chartType = viewingChartData?.chart_type?.toLowerCase() || viewingChart.chart_type?.toLowerCase() || 'bar'
    const isPie = chartType === 'pie' || chartType === 'donut'

    // Build ECharts option from rendered data
    let chartOption: any = {}

    if (viewingChartData && viewingChartData.rows && viewingChartData.rows.length > 0) {
      const { columns, rows } = viewingChartData
      const dimensionCol = columns[0]
      const measureCols = columns.slice(1)
      const xAxisData = rows.map(row => row[dimensionCol])

      if (isPie) {
        chartOption = {
          title: { text: viewingChart.name, left: 'center' },
          tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
          legend: { orient: 'vertical', left: 'left', top: 'middle' },
          series: [{
            type: 'pie',
            radius: chartType === 'donut' ? ['40%', '70%'] : '65%',
            center: ['60%', '50%'],
            data: rows.map(row => ({
              name: String(row[dimensionCol]),
              value: row[measureCols[0]] || 0
            })),
            label: { formatter: '{b}: {d}%' },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }],
          color: chartColors
        }
      } else {
        // Determine if values look like currency
        const firstMeasureValues = rows.map(r => r[measureCols[0]]).filter(v => typeof v === 'number')
        const isCurrency = measureCols.length > 0 && isCurrencyColumn(measureCols[0], firstMeasureValues)

        chartOption = {
          title: { text: viewingChart.name, left: 'center' },
          tooltip: {
            trigger: 'axis',
            axisPointer: { type: chartType === 'bar' || chartType === 'horizontal-bar' ? 'shadow' : 'line' },
            formatter: (params: any) => {
              if (!Array.isArray(params)) params = [params]
              const label = params[0]?.axisValue || params[0]?.name || ''
              let html = `<div style="padding: 8px 12px;"><div style="font-weight: 600; margin-bottom: 6px;">${label}</div>`
              params.forEach((p: any) => {
                const value = isCurrency ? `$${formatNumber(p.value, { compact: true })}` : formatNumber(p.value, { compact: true })
                html += `<div style="display: flex; align-items: center; gap: 8px;"><span style="display: inline-block; width: 10px; height: 10px; background: ${p.color}; border-radius: 2px;"></span><span>${p.seriesName}:</span><span style="font-weight: 600;">${value}</span></div>`
              })
              html += '</div>'
              return html
            }
          },
          grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
          xAxis: chartType === 'horizontal-bar'
            ? { type: 'value', axisLabel: { formatter: createAxisFormatter(isCurrency, false) } }
            : { type: 'category', data: xAxisData, axisLabel: { rotate: xAxisData.length > 10 ? 45 : 0 } },
          yAxis: chartType === 'horizontal-bar'
            ? { type: 'category', data: xAxisData }
            : { type: 'value', axisLabel: { formatter: createAxisFormatter(isCurrency, false) } },
          series: measureCols.map((col, idx) => ({
            name: col,
            type: chartType === 'line' || chartType === 'area' ? 'line' : 'bar',
            data: chartType === 'horizontal-bar' ? rows.map(row => row[col] || 0) : rows.map(row => row[col] || 0),
            smooth: chartType === 'line' || chartType === 'area',
            areaStyle: chartType === 'area' ? { opacity: 0.3 } : undefined,
            itemStyle: chartType === 'bar' ? { borderRadius: [4, 4, 0, 0] } : chartType === 'horizontal-bar' ? { borderRadius: [0, 4, 4, 0] } : undefined,
          })),
          color: chartColors
        }
      }
    } else if (viewingChartError) {
      // Error case - handled in render
    } else {
      // Fallback to template config if no rendered data (though this shouldn't happen)
      chartOption = viewingChart.chart_config || {}
    }

    console.log('=== VIEWING CHART ===')
    console.log('Chart type:', chartType)
    console.log('Rendered data:', viewingChartData)
    console.log('Built chart option:', chartOption)

    return (
      <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        {/* Header */}
        <header className="px-8 py-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Go back"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  {viewingChart.name}
                </h1>
                {viewingChart.description && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {viewingChart.description}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => toggleFavorite(viewingChart)}
                className={`p-2.5 rounded-xl transition-colors ${
                  viewingChart.is_favorite
                    ? 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500'
                }`}
                title={viewingChart.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
              >
                <Star className={`w-5 h-5 ${viewingChart.is_favorite ? 'fill-current' : ''}`} />
              </button>
              <button
                onClick={() => fetchSavedChart(chartId)}
                className="p-2.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-colors text-gray-500"
                title="Refresh"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
              <button
                onClick={() => downloadChartAsImage(viewingChartRef, viewingChart.name)}
                className="p-2.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-colors text-gray-500"
                title="Download as PNG"
              >
                <Download className="w-5 h-5" />
              </button>
              <button
                onClick={() => deleteChart(chartId)}
                className="p-2.5 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors text-gray-500 hover:text-red-500"
                title="Delete chart"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Chart Display */}
        <div className="flex-1 p-8 overflow-auto">
          <div className="max-w-6xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6">
              {/* Chart Type Badge */}
              <div className="flex items-center justify-between mb-6">
                <span className="px-3 py-1.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg text-sm font-medium capitalize">
                  {viewingChart.chart_type} Chart
                </span>
                <span className="text-sm text-gray-400">
                  Created {new Date(viewingChart.created_at).toLocaleDateString()}
                </span>
              </div>

              {/* Chart */}
              <div className="h-[500px]">
                {viewingChartError ? (
                  // Error state
                  <div className="h-full flex flex-col items-center justify-center bg-red-50 dark:bg-red-900/20 rounded-xl">
                    <BarChart3 className="w-16 h-16 text-red-300 mb-4" />
                    <p className="text-lg font-medium text-red-600 dark:text-red-400 mb-2">Failed to load chart data</p>
                    <p className="text-sm text-red-500 dark:text-red-400 mb-4">{viewingChartError}</p>
                    <button
                      onClick={() => fetchSavedChart(chartId!)}
                      className="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
                    >
                      Retry
                    </button>
                  </div>
                ) : !viewingChartData ? (
                  // Loading state
                  <div className="h-full flex items-center justify-center">
                    <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
                  </div>
                ) : viewingChart.chart_type === 'kpi' && viewingChartData?.rows?.[0] ? (
                  // Render KPI card with live data
                  <div className="h-full flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl">
                    <div className="text-center">
                      {(() => {
                        const row = viewingChartData.rows[0]
                        const valueCol = viewingChartData.columns[viewingChartData.columns.length - 1]
                        const value = row[valueCol]
                        const formattedValue = typeof value === 'number'
                          ? value >= 1000000 ? `${(value / 1000000).toFixed(1)}M`
                          : value >= 1000 ? `${(value / 1000).toFixed(1)}K`
                          : value.toLocaleString()
                          : value
                        return (
                          <>
                            <p className="text-7xl font-bold text-gray-900 dark:text-white mb-4">
                              {formattedValue}
                            </p>
                            <p className="text-2xl text-gray-500 dark:text-gray-400">
                              {valueCol}
                            </p>
                          </>
                        )
                      })()}
                    </div>
                  </div>
                ) : viewingChart.chart_type === 'table' && viewingChartData?.rows ? (
                  // Render table with live data
                  <div className="h-full overflow-auto">
                    <table className="w-full border-collapse">
                      <thead className="sticky top-0 bg-gray-50 dark:bg-gray-700 z-10">
                        <tr>
                          {viewingChartData.columns.map((col: string) => (
                            <th
                              key={col}
                              className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider border-b border-gray-200 dark:border-gray-600"
                            >
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {viewingChartData.rows.map((row: Record<string, any>, i: number) => (
                          <tr
                            key={i}
                            className={`${i % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-750'} hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors`}
                          >
                            {viewingChartData.columns.map((col: string) => (
                              <td
                                key={col}
                                className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300 border-b border-gray-100 dark:border-gray-700"
                              >
                                {row[col] !== null && row[col] !== undefined
                                  ? String(row[col])
                                  : <span className="text-gray-400 italic">null</span>}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : Object.keys(chartOption).length > 0 ? (
                  <ReactECharts
                    ref={viewingChartRef}
                    option={chartOption}
                    style={{ height: '100%', width: '100%' }}
                    opts={{ renderer: 'canvas' }}
                  />
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <BarChart3 className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p>No chart configuration available</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // === RECIPES VIEW (Landing) ===
  if (viewMode === 'recipes') {
    return (
      <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-950">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Header */}
          <div className="mb-8">
            {/* Title Row */}
            <div className="flex items-center gap-4 mb-6">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                <BarChart3 className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Chart Builder</h1>
                <p className="text-gray-500 dark:text-gray-400">Create stunning visualizations from your data</p>
              </div>
            </div>

            {/* Controls Row */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              {/* Data Source Toggle */}
              <div className="flex items-center bg-white dark:bg-gray-800 rounded-xl p-1 shadow-sm border border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setDataSourceType('transforms')}
                  className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all flex-1 sm:flex-none ${
                    dataSourceType === 'transforms'
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/25'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <Wand2 className="w-4 h-4" />
                  Transforms
                </button>
                <button
                  onClick={() => setDataSourceType('models')}
                  className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all flex-1 sm:flex-none ${
                    dataSourceType === 'models'
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/25'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <GitBranch className="w-4 h-4" />
                  Models
                </button>
                <button
                  onClick={() => setDataSourceType('saved')}
                  className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all flex-1 sm:flex-none ${
                    dataSourceType === 'saved'
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/25'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <Star className="w-4 h-4" />
                  Saved
                </button>
              </div>

              {/* Spacer */}
              <div className="flex-1 hidden sm:block" />

              {/* Search & Actions */}
              <div className="flex items-center gap-3">
                <div className="relative flex-1 sm:flex-none">
                  <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder={dataSourceType === 'transforms' ? 'Search transforms...' : dataSourceType === 'models' ? 'Search models...' : 'Search saved charts...'}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full sm:w-64 pl-10 pr-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
                  />
                </div>

                <button
                  onClick={fetchAllData}
                  disabled={loading}
                  className="p-2.5 bg-white dark:bg-gray-800 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded-xl transition-colors border border-gray-200 dark:border-gray-700 shadow-sm flex-shrink-0"
                >
                  <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                </button>

                {dataSourceType !== 'saved' && (
                  <a
                    href={dataSourceType === 'transforms' ? '/transforms' : '/models'}
                    className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-600 hover:to-purple-700 transition-all shadow-lg shadow-indigo-500/25 whitespace-nowrap flex-shrink-0"
                  >
                    <Plus className="w-4 h-4" />
                    <span className="hidden sm:inline">New {dataSourceType === 'transforms' ? 'Transform' : 'Model'}</span>
                    <span className="sm:hidden">New</span>
                  </a>
                )}
              </div>
            </div>
          </div>

          {/* Content */}
          {loading ? (
            <div className="bento-card py-16">
              <div className="text-center">
                <div className="relative inline-block">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center animate-pulse">
                    <BarChart3 className="w-8 h-8 text-white" />
                  </div>
                  <div className="absolute inset-0 rounded-2xl bg-indigo-500/20 blur-xl animate-pulse" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mt-6 mb-2">
                  Loading {dataSourceType}...
                </h3>
                <p className="text-gray-500">Fetching your data sources</p>
              </div>
            </div>
          ) : dataSourceType === 'models' ? (
            // === SEMANTIC MODELS VIEW ===
            filteredModels.length === 0 ? (
              <div className="bento-card py-16">
                <div className="text-center max-w-md mx-auto">
                  <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-100 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center mx-auto mb-6">
                    <GitBranch className="w-10 h-10 text-indigo-500" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                    {searchQuery ? 'No matching models' : 'No semantic models yet'}
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400 mb-8">
                    {searchQuery
                      ? 'Try a different search term'
                      : 'Create a semantic model to define measures, dimensions, and relationships for your visualizations'}
                  </p>
                  <a
                    href="/models"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-600 hover:to-purple-700 transition-all shadow-lg shadow-indigo-500/25"
                  >
                    <Sparkles className="w-5 h-5" />
                    Create Your First Model
                  </a>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                {filteredModels.map((model) => {
                  const connection = connections.get(model.connection_id)

                  return (
                    <button
                      key={model.id}
                      onClick={() => selectSemanticModel(model)}
                      className="bento-card group text-left hover:shadow-2xl hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300 hover:-translate-y-1 flex flex-col h-full"
                    >
                      {/* Model Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 flex-shrink-0">
                            <GitBranch className="w-5 h-5 text-white" />
                          </div>
                          <div className="min-w-0">
                            <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                              {model.name}
                            </h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                              {model.description || `${model.table_name}`}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Stats Grid */}
                      <div className="grid grid-cols-3 gap-2 mb-4 flex-1">
                        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center">
                          <div className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                            {model.measures_count}
                          </div>
                          <div className="text-xs text-gray-500">Measures</div>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center">
                          <div className="text-xl font-bold text-purple-600 dark:text-purple-400">
                            {model.dimensions_count}
                          </div>
                          <div className="text-xs text-gray-500">Dimensions</div>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center">
                          <div className="text-xl font-bold text-violet-600 dark:text-violet-400">
                            {model.joins_count}
                          </div>
                          <div className="text-xs text-gray-500">Joins</div>
                        </div>
                      </div>

                      {/* Footer */}
                      <div className="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700 mt-auto">
                        <div className="flex items-center gap-2 min-w-0">
                          {connection && (
                            <span className="text-xs text-gray-400 flex items-center gap-1 truncate">
                              <Database className="w-3 h-3 flex-shrink-0" />
                              <span className="truncate">{connection.name}</span>
                            </span>
                          )}
                        </div>
                        <span className="px-3 py-1.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity shadow-lg shadow-indigo-500/25 flex-shrink-0">
                          Build Charts
                        </span>
                      </div>
                    </button>
                  )
                })}
              </div>
            )
            ) : dataSourceType === 'saved' ? (
              // === SAVED CHARTS VIEW ===
              filteredSavedCharts.length === 0 ? (
                <div className="bento-card py-16">
                  <div className="text-center max-w-md mx-auto">
                    <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-100 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center mx-auto mb-6">
                      <Star className="w-10 h-10 text-indigo-500" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                      {searchQuery ? 'No matching charts' : 'No saved charts yet'}
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-8">
                      {searchQuery
                        ? 'Try a different search term'
                        : 'Build charts from transforms or models and save them for quick access'}
                    </p>
                    <button
                      onClick={() => setDataSourceType('transforms')}
                      className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-600 hover:to-purple-700 transition-all shadow-lg shadow-indigo-500/25"
                    >
                      <Wand2 className="w-5 h-5" />
                      Build from Transforms
                    </button>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                  {filteredSavedCharts.map((chart) => {
                    const connection = connections.get(chart.connection_id)

                    return (
                      <a
                        key={chart.id}
                        href={`/charts/${chart.id}`}
                        className="bento-card group text-left hover:shadow-2xl hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300 hover:-translate-y-1 flex flex-col h-full"
                      >
                        {/* Chart Header */}
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 flex-shrink-0">
                              <BarChart3 className="w-5 h-5 text-white" />
                            </div>
                            <div className="min-w-0">
                              <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                                {chart.name}
                              </h3>
                              <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                                {chart.description || `${chart.chart_type} chart`}
                              </p>
                            </div>
                          </div>
                          {chart.is_favorite && (
                            <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/50 text-yellow-600 dark:text-yellow-400 rounded-lg text-xs font-medium flex-shrink-0">
                              ★
                            </span>
                          )}
                        </div>

                        {/* Chart Preview Area */}
                        <div className="h-32 bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-indigo-900/20 dark:via-purple-900/20 dark:to-pink-900/20 rounded-xl relative overflow-hidden mb-4 flex-1">
                          {chart.chart_type === 'kpi' && chart.chart_config?.kpiValue ? (
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="text-center">
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                  {chart.chart_config.kpiValue as string}
                                </p>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                  {chart.chart_config.kpiLabel as string}
                                </p>
                              </div>
                            </div>
                          ) : chart.chart_config && Object.keys(chart.chart_config).length > 0 ? (
                            <div className="absolute inset-0 p-2">
                              <ReactECharts
                                option={{
                                  ...chart.chart_config,
                                  animation: false,
                                  ...(!['pie', 'donut', 'gauge', 'funnel', 'radar', 'table'].includes(chart.chart_type?.toLowerCase()) ? {
                                    grid: { left: 30, right: 10, bottom: 20, top: 10 }
                                  } : {}),
                                }}
                                style={{ height: '100%', width: '100%' }}
                                opts={{ renderer: 'canvas' }}
                              />
                            </div>
                          ) : (
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="text-center">
                                <BarChart3 className="w-10 h-10 text-indigo-200 dark:text-indigo-700 mx-auto mb-1" />
                                <div className="text-xs font-medium text-indigo-600 dark:text-indigo-400 capitalize">
                                  {chart.chart_type}
                                </div>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700 mt-auto">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="px-2 py-1 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg text-xs font-medium capitalize flex-shrink-0">
                              {chart.chart_type}
                            </span>
                            {connection && (
                              <span className="text-xs text-gray-400 flex items-center gap-1 truncate">
                                <Database className="w-3 h-3 flex-shrink-0" />
                                <span className="truncate">{connection.name}</span>
                              </span>
                            )}
                          </div>
                          <span className="px-3 py-1.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity shadow-lg shadow-indigo-500/25 flex-shrink-0">
                            View
                          </span>
                        </div>
                      </a>
                    )
                  })}
                </div>
              )
            ) : filteredRecipes.length === 0 ? (
              // === TRANSFORMS EMPTY STATE ===
              <div className="bento-card py-16">
                <div className="text-center max-w-md mx-auto">
                  <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-100 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center mx-auto mb-6">
                    <Wand2 className="w-10 h-10 text-indigo-500" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                    {searchQuery ? 'No matching recipes' : 'No transform recipes yet'}
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400 mb-8">
                    {searchQuery
                      ? 'Try a different search term'
                      : 'Create a transform recipe to filter, aggregate, and visualize your data'}
                  </p>
                  <a
                    href="/transforms"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-600 hover:to-purple-700 transition-all shadow-lg shadow-indigo-500/25"
                  >
                    <Sparkles className="w-5 h-5" />
                    Create Your First Transform
                  </a>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                {filteredRecipes.map((recipe) => {
                  const preview = recipePreviews.get(recipe.id)
                  const connection = connections.get(recipe.connection_id)

                  return (
                    <button
                      key={recipe.id}
                      onClick={() => selectRecipe(recipe)}
                      className="bento-card group text-left hover:shadow-2xl hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-300 hover:-translate-y-1 flex flex-col h-full"
                    >
                      {/* Transform Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 flex-shrink-0">
                            <Wand2 className="w-5 h-5 text-white" />
                          </div>
                          <div className="min-w-0">
                            <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                              {recipe.name}
                            </h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                              {recipe.description || `${recipe.source_table}`}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Chart Preview */}
                      <div className="h-32 bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-indigo-900/20 dark:via-purple-900/20 dark:to-pink-900/20 rounded-xl relative overflow-hidden mb-4 flex-1">
                        {preview?.loading ? (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
                          </div>
                        ) : preview?.chart && preview.chart.type !== 'kpi' && preview.chart.type !== 'table' ? (
                          <div className="absolute inset-0 p-2">
                            <ReactECharts
                              option={{
                                ...preview.chart.option,
                                animation: false,
                                grid: { left: 30, right: 10, bottom: 20, top: 10 },
                              }}
                              style={{ height: '100%', width: '100%' }}
                              opts={{ renderer: 'canvas' }}
                            />
                          </div>
                        ) : preview?.chart?.type === 'kpi' ? (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                                {preview.chart.kpiValue}
                              </div>
                              <div className="text-xs text-gray-500 mt-1">
                                {preview.chart.kpiLabel}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-center">
                              <BarChart3 className="w-10 h-10 text-indigo-200 dark:text-indigo-700 mx-auto mb-1" />
                              <p className="text-xs text-indigo-400">
                                {preview?.error ? 'Preview unavailable' : 'Click to visualize'}
                              </p>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Footer */}
                      <div className="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700 mt-auto">
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg text-xs text-gray-600 dark:text-gray-300 truncate">
                            <Table2 className="w-3 h-3 flex-shrink-0" />
                            <span className="truncate">{recipe.source_table}</span>
                          </span>
                          {recipe.steps.length > 0 && (
                            <span className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded-lg text-xs font-medium flex-shrink-0">
                              {recipe.steps.length} steps
                            </span>
                          )}
                        </div>
                        <span className="px-3 py-1.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-xs font-medium rounded-lg opacity-0 group-hover:opacity-100 transition-opacity shadow-lg shadow-indigo-500/25 flex-shrink-0">
                          View Charts
                        </span>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
        </div>
      </div>
    )
  }

  // === CHARTS VIEW ===
  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      <header className="px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          <button
            onClick={goBack}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-500" />
          </button>
          {selectedModel ? (
            // Model Header
            <>
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                <GitBranch className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                    {selectedModel.name}
                  </h1>
                  <span className="px-2 py-0.5 text-xs font-medium bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 rounded-full">
                    Model
                  </span>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {selectedModel.transform_id
                    ? `Transform: ${selectedModel.transform_name || 'Unknown'}`
                    : `${selectedModel.schema_name}.${selectedModel.table_name}`
                  } · {selectedModel.measures.length} measures · {selectedModel.dimensions.length} dimensions · {preview?.total.toLocaleString() || 0} rows
                </p>
              </div>
            </>
          ) : (
            // Transform Header
            <>
              <div className="w-10 h-10 rounded-lg bg-primary-500 flex items-center justify-center">
                <Wand2 className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                    {selectedRecipe?.name}
                  </h1>
                  <span className="px-2 py-0.5 text-xs font-medium bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded-full">
                    Transform
                  </span>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {selectedRecipe?.source_schema}.{selectedRecipe?.source_table} · {selectedRecipe?.steps.length || 0} steps · {preview?.total.toLocaleString() || 0} rows · {generatedCharts.length} charts
                </p>
              </div>
            </>
          )}
          <button className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
            <Download className="w-4 h-4" />
            Export
          </button>
          <button
            onClick={openSaveModal}
            disabled={!selectedChart}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Save className="w-4 h-4" />
            Save Chart
          </button>
        </div>
      </header>

      {chartsLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="relative w-16 h-16 mx-auto mb-6">
              <div className="absolute inset-0 rounded-full border-4 border-indigo-100 dark:border-indigo-900"></div>
              <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-indigo-500 animate-spin"></div>
            </div>
            <p className="text-gray-600 dark:text-gray-400 font-medium">Analyzing data...</p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">Generating smart visualizations</p>
          </div>
        </div>
      ) : generatedCharts.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-20 h-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mx-auto mb-6">
              <BarChart3 className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No charts generated
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-sm">
              {selectedModel && selectedModel.measures.length === 0
                ? 'This model has no measures defined. Add measures (aggregations like SUM, COUNT) to generate charts.'
                : selectedModel && selectedMeasures.length === 0
                ? 'Select at least one measure from the sidebar to generate charts.'
                : 'The data source may not have suitable data for visualizations.'}
            </p>
            {selectedModel && selectedModel.measures.length === 0 && (
              <a
                href={`/models/${selectedModel.id}`}
                className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Measures
              </a>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <div className="w-72 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
            {/* Model Configuration Panel */}
            {selectedModel && (
              <div className="border-b border-gray-200 dark:border-gray-700">
                {/* Measures Section */}
                <div className="p-4 border-b border-gray-100 dark:border-gray-700">
                  <div className="flex items-center gap-2 mb-3">
                    <Calculator className="w-4 h-4 text-emerald-500" />
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                      Measures
                    </h3>
                    <span className="text-xs text-gray-400">({selectedMeasures.length} selected)</span>
                  </div>
                  <div className="space-y-1.5 max-h-32 overflow-auto">
                    {selectedModel.measures.map(measure => (
                      <button
                        key={measure.id}
                        onClick={() => handleMeasureToggle(measure.id)}
                        className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-all text-sm ${
                          selectedMeasures.includes(measure.id)
                            ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 ring-1 ring-emerald-200 dark:ring-emerald-800'
                            : 'bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                          selectedMeasures.includes(measure.id)
                            ? 'border-emerald-500 bg-emerald-500'
                            : 'border-gray-300 dark:border-gray-500'
                        }`}>
                          {selectedMeasures.includes(measure.id) && (
                            <Check className="w-3 h-3 text-white" />
                          )}
                        </div>
                        <span className="truncate flex-1">{measure.name}</span>
                        <span className="text-xs text-gray-400 uppercase">{measure.aggregation}</span>
                      </button>
                    ))}
                    {selectedModel.measures.length === 0 && (
                      <p className="text-xs text-gray-400 italic py-2">No measures defined</p>
                    )}
                  </div>
                </div>

                {/* Dimensions Section */}
                <div className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Columns className="w-4 h-4 text-teal-500" />
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                      Dimensions
                    </h3>
                    <span className="text-xs text-gray-400">({selectedDimensions.length} selected)</span>
                  </div>
                  <div className="space-y-1.5 max-h-32 overflow-auto">
                    {selectedModel.dimensions.map(dimension => (
                      <button
                        key={dimension.id}
                        onClick={() => handleDimensionToggle(dimension.id)}
                        className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-all text-sm ${
                          selectedDimensions.includes(dimension.id)
                            ? 'bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400 ring-1 ring-teal-200 dark:ring-teal-800'
                            : 'bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                          selectedDimensions.includes(dimension.id)
                            ? 'border-teal-500 bg-teal-500'
                            : 'border-gray-300 dark:border-gray-500'
                        }`}>
                          {selectedDimensions.includes(dimension.id) && (
                            <Check className="w-3 h-3 text-white" />
                          )}
                        </div>
                        <span className="truncate flex-1">{dimension.name}</span>
                      </button>
                    ))}
                    {selectedModel.dimensions.length === 0 && (
                      <p className="text-xs text-gray-400 italic py-2">No dimensions defined</p>
                    )}
                  </div>
                </div>

                {/* Query Status */}
                {modelQueryLoading && (
                  <div className="px-4 pb-4">
                    <div className="flex items-center gap-2 text-sm text-indigo-600 dark:text-indigo-400">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Updating chart...
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Charts List */}
            <div className="p-4 border-b border-gray-100 dark:border-gray-700">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                Generated Charts
              </h3>
              <p className="text-xs text-gray-400 mt-0.5">{generatedCharts.length} visualizations</p>
            </div>
            <div className="flex-1 overflow-auto p-3 space-y-2">
              {generatedCharts.map((chart) => (
                <button
                  key={chart.id}
                  onClick={() => {
                    console.log('Selected chart:', chart.type, chart.title)
                    setSelectedChart(chart)
                  }}
                  className={`w-full rounded-xl text-left transition-all duration-200 overflow-hidden ${
                    selectedChart?.id === chart.id
                      ? 'ring-4 ring-indigo-500 bg-indigo-100 dark:bg-indigo-900/50 shadow-lg shadow-indigo-200 dark:shadow-indigo-900/50'
                      : 'bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  {/* Selected Indicator */}
                  {selectedChart?.id === chart.id && (
                    <div className="bg-indigo-500 text-white text-xs font-bold py-1 px-3 text-center">
                      ✓ SELECTED - Will be saved as {chart.type.toUpperCase()}
                    </div>
                  )}
                  <div className="p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <chart.icon className={`w-4 h-4 ${selectedChart?.id === chart.id ? 'text-indigo-600' : 'text-gray-400'}`} />
                      <span className={`text-sm font-medium truncate flex-1 ${selectedChart?.id === chart.id ? 'text-indigo-700 dark:text-indigo-300 font-bold' : 'text-gray-700 dark:text-gray-300'}`}>
                        {chart.title}
                      </span>
                      {/* Chart Type Badge */}
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded uppercase ${
                        selectedChart?.id === chart.id
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                      }`}>
                        {chart.type}
                      </span>
                    </div>
                    <div className="h-24 bg-white dark:bg-gray-800 rounded-lg overflow-hidden flex items-center justify-center">
                      {chart.type === 'kpi' ? (
                        <div className="text-center px-2">
                          <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {chart.kpiValue}
                          </div>
                          <div className="text-xs text-gray-400 truncate">
                            {chart.kpiLabel}
                          </div>
                        </div>
                      ) : chart.type === 'table' ? (
                        <div className="text-center px-2">
                          <TableIcon className="w-8 h-8 text-gray-300 dark:text-gray-600 mx-auto mb-1" />
                          <div className="text-xs text-gray-400">
                            {chart.tableRows?.length || 0} rows
                          </div>
                        </div>
                      ) : (
                        <ReactECharts
                          option={{ ...chart.option, animation: false }}
                          style={{ height: '100%', width: '100%' }}
                          opts={{ renderer: 'canvas' }}
                        />
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Main Chart */}
          <div className="flex-1 p-6 overflow-auto">
            {selectedChart && (
              <div className="h-full bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden">
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-700">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {selectedChart.title}
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                      {selectedChart.description}
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    <button className="p-2.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                      <Settings className="w-5 h-5" />
                    </button>
                    <button className="p-2.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                      <Maximize2 className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => downloadChartAsImage(mainChartRef, selectedChart.title)}
                      className="p-2.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                      title="Download as PNG"
                      disabled={selectedChart.type === 'kpi' || selectedChart.type === 'table'}
                    >
                      <Download className="w-5 h-5" />
                    </button>
                  </div>
                </div>
                <div className="flex-1 p-6 overflow-auto">
                  {selectedChart.type === 'kpi' ? (
                    <div className="h-full flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-6xl font-bold text-gray-900 dark:text-white mb-2">
                          {selectedChart.kpiValue}
                        </div>
                        <div className="text-lg text-gray-500 dark:text-gray-400 mb-4">
                          {selectedChart.kpiLabel}
                        </div>
                        {selectedChart.kpiChangeLabel && (
                          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 rounded-full text-sm text-gray-600 dark:text-gray-300">
                            {selectedChart.kpiChangeLabel}
                          </div>
                        )}
                      </div>
                    </div>
                  ) : selectedChart.type === 'table' ? (
                    <div className="h-full flex flex-col">
                      {/* Table Controls */}
                      <div className="flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-600">
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          {(() => {
                            const { totalRows, startIndex, endIndex } = getTableData(selectedChart.tableRows, selectedChart.tableColumns)
                            return `Showing ${startIndex + 1}-${endIndex} of ${totalRows} rows`
                          })()}
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-500 dark:text-gray-400">Rows:</span>
                            <select
                              value={tableRowsPerPage}
                              onChange={(e) => {
                                setTableRowsPerPage(Number(e.target.value))
                                setTableCurrentPage(1)
                              }}
                              className="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                            >
                              <option value={10}>10</option>
                              <option value={25}>25</option>
                              <option value={50}>50</option>
                              <option value={100}>100</option>
                            </select>
                          </div>
                        </div>
                      </div>

                      {/* Table */}
                      <div className="flex-1 overflow-auto">
                        <table className="w-full border-collapse">
                          <thead className="sticky top-0 bg-gray-50 dark:bg-gray-700 z-10">
                            <tr>
                              {selectedChart.tableColumns?.map((col) => (
                                <th
                                  key={col}
                                  onClick={() => handleTableSort(col)}
                                  className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider border-b border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 select-none transition-colors"
                                >
                                  <div className="flex items-center gap-1">
                                    <span className="truncate">{col}</span>
                                    {tableSortColumn === col ? (
                                      tableSortDirection === 'asc' ? (
                                        <ChevronUp className="w-4 h-4 text-indigo-500 flex-shrink-0" />
                                      ) : (
                                        <ChevronDown className="w-4 h-4 text-indigo-500 flex-shrink-0" />
                                      )
                                    ) : (
                                      <ChevronsUpDown className="w-4 h-4 text-gray-400 flex-shrink-0 opacity-0 group-hover:opacity-100" />
                                    )}
                                  </div>
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {getTableData(selectedChart.tableRows, selectedChart.tableColumns).sortedRows.map((row, i) => (
                              <tr
                                key={i}
                                className={`${i % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-750'} hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors`}
                              >
                                {selectedChart.tableColumns?.map((col) => (
                                  <td
                                    key={col}
                                    className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300 border-b border-gray-100 dark:border-gray-700"
                                  >
                                    {row[col] !== null && row[col] !== undefined
                                      ? <span title={String(row[col])}>{formatCellValue(row[col])}</span>
                                      : <span className="text-gray-400 italic">null</span>}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Pagination */}
                      {(() => {
                        const { totalPages } = getTableData(selectedChart.tableRows, selectedChart.tableColumns)
                        if (totalPages <= 1) return null
                        return (
                          <div className="flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-600">
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              Page {tableCurrentPage} of {totalPages}
                            </div>
                            <div className="flex items-center gap-1">
                              <button
                                onClick={() => setTableCurrentPage(p => Math.max(1, p - 1))}
                                disabled={tableCurrentPage === 1}
                                className="px-3 py-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm text-gray-600 dark:text-gray-400"
                              >
                                Prev
                              </button>
                              <div className="flex items-center gap-1">
                                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                  let pageNum: number
                                  if (totalPages <= 5) {
                                    pageNum = i + 1
                                  } else if (tableCurrentPage <= 3) {
                                    pageNum = i + 1
                                  } else if (tableCurrentPage >= totalPages - 2) {
                                    pageNum = totalPages - 4 + i
                                  } else {
                                    pageNum = tableCurrentPage - 2 + i
                                  }
                                  return (
                                    <button
                                      key={pageNum}
                                      onClick={() => setTableCurrentPage(pageNum)}
                                      className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                                        tableCurrentPage === pageNum
                                          ? 'bg-indigo-500 text-white'
                                          : 'hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-400'
                                      }`}
                                    >
                                      {pageNum}
                                    </button>
                                  )
                                })}
                              </div>
                              <button
                                onClick={() => setTableCurrentPage(p => Math.min(totalPages, p + 1))}
                                disabled={tableCurrentPage === totalPages}
                                className="px-3 py-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm text-gray-600 dark:text-gray-400"
                              >
                                Next
                              </button>
                            </div>
                          </div>
                        )
                      })()}
                    </div>
                  ) : (
                    <ReactECharts
                      ref={mainChartRef}
                      option={selectedChart.option}
                      style={{ height: '100%', width: '100%' }}
                      opts={{ renderer: 'canvas' }}
                    />
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Save to Dashboard Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md mx-4 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Save Chart
              </h3>
              <button
                onClick={closeSaveModal}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            <div className="p-6">
              {saveSuccess ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mx-auto mb-4">
                    <Check className="w-8 h-8 text-green-500" />
                  </div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Chart Saved!
                  </h4>
                  <p className="text-gray-500 dark:text-gray-400">
                    Your chart has been saved successfully.
                  </p>
                </div>
              ) : (
                <>
                  {selectedChart && (
                    <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                      <div className="flex items-center gap-3 mb-3">
                        <selectedChart.icon className="w-5 h-5 text-indigo-500" />
                        <span className="font-medium text-gray-900 dark:text-white flex-1">
                          {selectedChart.title}
                        </span>
                        {/* Chart Type Badge */}
                        <span className="px-2.5 py-1 text-xs font-bold bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full uppercase">
                          {selectedChart.type}
                        </span>
                        {selectedModel ? (
                          <span className="flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 rounded-full">
                            <GitBranch className="w-3 h-3" />
                            Model
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded-full">
                            <Wand2 className="w-3 h-3" />
                            Transform
                          </span>
                        )}
                      </div>
                      <div className="h-32 bg-white dark:bg-gray-800 rounded-lg overflow-hidden flex items-center justify-center">
                        {selectedChart.type === 'kpi' ? (
                          <div className="text-center">
                            <div className="text-3xl font-bold text-gray-900 dark:text-white">
                              {selectedChart.kpiValue}
                            </div>
                            <div className="text-sm text-gray-400">
                              {selectedChart.kpiLabel}
                            </div>
                          </div>
                        ) : selectedChart.type === 'table' ? (
                          <div className="text-center">
                            <TableIcon className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-1" />
                            <div className="text-sm text-gray-400">
                              {selectedChart.tableRows?.length || 0} rows × {selectedChart.tableColumns?.length || 0} cols
                            </div>
                          </div>
                        ) : (
                          <ReactECharts
                            option={{ ...selectedChart.option, animation: false }}
                            style={{ height: '100%', width: '100%' }}
                            opts={{ renderer: 'canvas' }}
                          />
                        )}
                      </div>
                    </div>
                  )}

                  <div className="space-y-4">
                    {/* Chart Name Input */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Chart Name
                      </label>
                      <input
                        type="text"
                        value={customChartName}
                        onChange={(e) => setCustomChartName(e.target.value)}
                        placeholder="Enter a name for your chart..."
                        className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                      <p className="text-xs text-gray-400 mt-1">
                        This name will appear in your saved charts and dashboard
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Save to Dashboard (Optional)
                      </label>

                      {dashboardsLoading ? (
                        <div className="flex items-center justify-center py-4">
                          <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
                        </div>
                      ) : (
                        <div className="space-y-2 max-h-48 overflow-auto">
                          <button
                            onClick={() => {
                              setSelectedDashboardId(null)
                              setCreateNewDashboard(false)
                            }}
                            className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all ${
                              !selectedDashboardId && !createNewDashboard
                                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                                : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                            }`}
                          >
                            <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                              !selectedDashboardId && !createNewDashboard
                                ? 'border-indigo-500'
                                : 'border-gray-300 dark:border-gray-500'
                            }`}>
                              {!selectedDashboardId && !createNewDashboard && (
                                <div className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                              )}
                            </div>
                            <span className="text-gray-900 dark:text-white">
                              Save without dashboard
                            </span>
                          </button>

                          {dashboards.map((dashboard) => (
                            <button
                              key={dashboard.id}
                              onClick={() => {
                                setSelectedDashboardId(dashboard.id)
                                setCreateNewDashboard(false)
                              }}
                              className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all ${
                                selectedDashboardId === dashboard.id
                                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                                  : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                              }`}
                            >
                              <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                                selectedDashboardId === dashboard.id
                                  ? 'border-indigo-500'
                                  : 'border-gray-300 dark:border-gray-500'
                              }`}>
                                {selectedDashboardId === dashboard.id && (
                                  <div className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                                )}
                              </div>
                              <div className="flex-1 text-left">
                                <span className="text-gray-900 dark:text-white block">
                                  {dashboard.name}
                                </span>
                                <span className="text-xs text-gray-400">
                                  {dashboard.chart_count} charts
                                </span>
                              </div>
                            </button>
                          ))}

                          <button
                            onClick={() => {
                              setSelectedDashboardId(null)
                              setCreateNewDashboard(true)
                            }}
                            className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all ${
                              createNewDashboard
                                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                                : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                            }`}
                          >
                            <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                              createNewDashboard
                                ? 'border-indigo-500'
                                : 'border-gray-300 dark:border-gray-500'
                            }`}>
                              {createNewDashboard && (
                                <div className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                              )}
                            </div>
                            <FolderPlus className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-900 dark:text-white">
                              Create new dashboard
                            </span>
                          </button>
                        </div>
                      )}
                    </div>

                    {createNewDashboard && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Dashboard Name
                        </label>
                        <input
                          type="text"
                          value={newDashboardName}
                          onChange={(e) => setNewDashboardName(e.target.value)}
                          placeholder="Enter dashboard name..."
                          className="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            {!saveSuccess && (
              <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                <button
                  onClick={closeSaveModal}
                  className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={saveChartToDashboard}
                  disabled={saveLoading || !customChartName.trim() || (createNewDashboard && !newDashboardName.trim())}
                  className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {saveLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      Save Chart
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
