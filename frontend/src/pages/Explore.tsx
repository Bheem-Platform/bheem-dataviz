import { useState, useEffect } from 'react'
import {
  Play,
  Save,
  Settings,
  Database,
  Columns,
  Filter,
  Palette,
  ChevronRight,
  ChevronDown,
  GripVertical,
  Plus,
  X,
  Sparkles,
} from 'lucide-react'
import ReactECharts from 'echarts-for-react'

// Chart type definitions with ECharts configs
const chartTypes = [
  { id: 'bar', name: 'Bar Chart', icon: '📊', category: 'basic' },
  { id: 'line', name: 'Line Chart', icon: '📈', category: 'basic' },
  { id: 'area', name: 'Area Chart', icon: '📉', category: 'basic' },
  { id: 'pie', name: 'Pie Chart', icon: '🥧', category: 'basic' },
  { id: 'donut', name: 'Donut Chart', icon: '🍩', category: 'basic' },
  { id: 'scatter', name: 'Scatter Plot', icon: '⚬', category: 'basic' },
  { id: 'heatmap', name: 'Heatmap', icon: '🔥', category: 'advanced' },
  { id: 'treemap', name: 'Treemap', icon: '🌳', category: 'advanced' },
  { id: 'sunburst', name: 'Sunburst', icon: '☀️', category: 'advanced' },
  { id: 'radar', name: 'Radar Chart', icon: '🎯', category: 'advanced' },
  { id: 'funnel', name: 'Funnel', icon: '🔻', category: 'advanced' },
  { id: 'gauge', name: 'Gauge', icon: '🎛️', category: 'advanced' },
  { id: 'sankey', name: 'Sankey', icon: '🌊', category: 'advanced' },
  { id: 'boxplot', name: 'Box Plot', icon: '📦', category: 'statistical' },
  { id: 'candlestick', name: 'Candlestick', icon: '🕯️', category: 'financial' },
  { id: 'waterfall', name: 'Waterfall', icon: '💧', category: 'financial' },
  { id: 'table', name: 'Table', icon: '📋', category: 'table' },
  { id: 'pivot', name: 'Pivot Table', icon: '🔄', category: 'table' },
  { id: 'big_number', name: 'Big Number', icon: '🔢', category: 'kpi' },
  { id: 'big_number_trend', name: 'Big Number + Trend', icon: '📊', category: 'kpi' },
]

// Sample columns from dataset
const sampleColumns = [
  { name: 'date', type: 'datetime', icon: '📅' },
  { name: 'region', type: 'string', icon: '🌍' },
  { name: 'product', type: 'string', icon: '📦' },
  { name: 'category', type: 'string', icon: '🏷️' },
  { name: 'sales', type: 'number', icon: '💰' },
  { name: 'quantity', type: 'number', icon: '🔢' },
  { name: 'profit', type: 'number', icon: '📈' },
  { name: 'cost', type: 'number', icon: '💸' },
]

const aggregations = ['SUM', 'AVG', 'COUNT', 'MIN', 'MAX', 'COUNT_DISTINCT']

interface Metric {
  column: string
  aggregation: string
  label: string
}

export function Explore() {
  const [selectedChart, setSelectedChart] = useState('bar')
  const [dimensions, setDimensions] = useState<string[]>(['region'])
  const [metrics, setMetrics] = useState<Metric[]>([
    { column: 'sales', aggregation: 'SUM', label: 'Total Sales' },
  ])
  const [activeTab, setActiveTab] = useState<'data' | 'customize' | 'filters'>('data')
  const [expandedSections, setExpandedSections] = useState({
    columns: true,
    metrics: true,
  })
  const [chartOption, setChartOption] = useState<any>(null)
  const [isAiSuggesting, setIsAiSuggesting] = useState(false)

  // Generate chart based on selections
  useEffect(() => {
    const option = generateChartOption(selectedChart, dimensions, metrics)
    setChartOption(option)
  }, [selectedChart, dimensions, metrics])

  const generateChartOption = (
    type: string,
    dims: string[],
    mets: Metric[]
  ) => {
    const categories = ['North', 'South', 'East', 'West', 'Central']
    const data = [320, 280, 450, 380, 290]

    const baseOption = {
      tooltip: { trigger: 'axis' as const },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    }

    switch (type) {
      case 'bar':
        return {
          ...baseOption,
          xAxis: { type: 'category', data: categories },
          yAxis: { type: 'value' },
          series: [{ type: 'bar', data, itemStyle: { color: '#667eea' } }],
        }
      case 'line':
        return {
          ...baseOption,
          xAxis: { type: 'category', data: categories },
          yAxis: { type: 'value' },
          series: [{ type: 'line', data, smooth: true, itemStyle: { color: '#667eea' } }],
        }
      case 'pie':
        return {
          tooltip: { trigger: 'item' },
          series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            data: categories.map((name, i) => ({ name, value: data[i] })),
          }],
        }
      case 'area':
        return {
          ...baseOption,
          xAxis: { type: 'category', data: categories },
          yAxis: { type: 'value' },
          series: [{ type: 'line', data, areaStyle: {}, smooth: true }],
        }
      case 'radar':
        return {
          radar: {
            indicator: categories.map((name) => ({ name, max: 500 })),
          },
          series: [{ type: 'radar', data: [{ value: data, name: 'Sales' }] }],
        }
      case 'funnel':
        return {
          series: [{
            type: 'funnel',
            data: [
              { value: 100, name: 'Visits' },
              { value: 80, name: 'Cart' },
              { value: 60, name: 'Checkout' },
              { value: 40, name: 'Purchase' },
              { value: 20, name: 'Repeat' },
            ],
          }],
        }
      case 'gauge':
        return {
          series: [{
            type: 'gauge',
            progress: { show: true },
            detail: { formatter: '{value}%' },
            data: [{ value: 72, name: 'Completion' }],
          }],
        }
      default:
        return {
          ...baseOption,
          xAxis: { type: 'category', data: categories },
          yAxis: { type: 'value' },
          series: [{ type: 'bar', data }],
        }
    }
  }

  const handleAiSuggest = async () => {
    setIsAiSuggesting(true)
    // Simulate AI suggestion
    setTimeout(() => {
      setSelectedChart('funnel')
      setIsAiSuggesting(false)
    }, 1500)
  }

  const addDimension = (col: string) => {
    if (!dimensions.includes(col)) {
      setDimensions([...dimensions, col])
    }
  }

  const removeDimension = (col: string) => {
    setDimensions(dimensions.filter((d) => d !== col))
  }

  const addMetric = (col: string) => {
    setMetrics([
      ...metrics,
      { column: col, aggregation: 'SUM', label: `SUM(${col})` },
    ])
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          <select className="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm">
            <option>Sales Dataset</option>
            <option>Marketing Analytics</option>
            <option>User Events</option>
          </select>
          <span className="text-sm text-gray-500">→</span>
          <input
            type="text"
            placeholder="Untitled Chart"
            className="text-lg font-medium bg-transparent border-none focus:outline-none text-gray-900 dark:text-white"
          />
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleAiSuggest}
            disabled={isAiSuggesting}
            className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:opacity-90 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            {isAiSuggesting ? 'Suggesting...' : 'AI Suggest'}
          </button>
          <button className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
            <Play className="w-5 h-5" />
            Run
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
            <Save className="w-5 h-5" />
            Save
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Data Source */}
        <div className="w-64 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col overflow-hidden">
          <div className="p-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              <Database className="w-4 h-4" />
              Data Source
            </div>
          </div>

          <div className="flex-1 overflow-auto p-2">
            {/* Columns Section */}
            <div className="mb-4">
              <button
                onClick={() =>
                  setExpandedSections((s) => ({ ...s, columns: !s.columns }))
                }
                className="flex items-center gap-2 w-full p-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                {expandedSections.columns ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
                <Columns className="w-4 h-4" />
                Columns
              </button>

              {expandedSections.columns && (
                <div className="ml-4 mt-1 space-y-1">
                  {sampleColumns.map((col) => (
                    <div
                      key={col.name}
                      draggable
                      onDragStart={(e) =>
                        e.dataTransfer.setData('column', col.name)
                      }
                      className="flex items-center gap-2 p-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded cursor-grab"
                    >
                      <GripVertical className="w-3 h-3 text-gray-400" />
                      <span>{col.icon}</span>
                      <span>{col.name}</span>
                      <span className="ml-auto text-xs text-gray-400">
                        {col.type}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Saved Metrics */}
            <div>
              <button
                onClick={() =>
                  setExpandedSections((s) => ({ ...s, metrics: !s.metrics }))
                }
                className="flex items-center gap-2 w-full p-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                {expandedSections.metrics ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
                📊 Saved Metrics
              </button>

              {expandedSections.metrics && (
                <div className="ml-4 mt-1 space-y-1">
                  <div className="p-2 text-sm text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded cursor-pointer">
                    + Create metric
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Center - Chart Preview */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Chart Type Selector */}
          <div className="p-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 overflow-x-auto pb-2">
              {chartTypes.slice(0, 10).map((chart) => (
                <button
                  key={chart.id}
                  onClick={() => setSelectedChart(chart.id)}
                  className={`flex flex-col items-center gap-1 p-2 rounded-lg min-w-[60px] transition-colors ${
                    selectedChart === chart.id
                      ? 'bg-primary-100 dark:bg-primary-900/30 border-2 border-primary-500'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-700 border-2 border-transparent'
                  }`}
                >
                  <span className="text-xl">{chart.icon}</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">
                    {chart.name.split(' ')[0]}
                  </span>
                </button>
              ))}
              <button className="flex items-center gap-1 px-3 py-2 text-sm text-primary-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <Plus className="w-4 h-4" />
                More
              </button>
            </div>
          </div>

          {/* Chart Area */}
          <div className="flex-1 p-6 overflow-auto">
            <div className="h-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
              {chartOption && (
                <ReactECharts
                  option={chartOption}
                  style={{ height: '100%', width: '100%' }}
                  opts={{ renderer: 'canvas' }}
                />
              )}
            </div>
          </div>

          {/* Data Preview */}
          <div className="h-48 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <div className="p-2 border-b border-gray-200 dark:border-gray-700 text-sm font-medium text-gray-700 dark:text-gray-300">
              Data Preview (5 rows)
            </div>
            <div className="overflow-auto h-36">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-3 py-2 text-left">region</th>
                    <th className="px-3 py-2 text-left">product</th>
                    <th className="px-3 py-2 text-right">sales</th>
                    <th className="px-3 py-2 text-right">quantity</th>
                  </tr>
                </thead>
                <tbody>
                  {['North', 'South', 'East', 'West', 'Central'].map((r, i) => (
                    <tr key={r} className="border-b border-gray-100 dark:border-gray-700">
                      <td className="px-3 py-2">{r}</td>
                      <td className="px-3 py-2">Product {i + 1}</td>
                      <td className="px-3 py-2 text-right">${(Math.random() * 1000).toFixed(0)}</td>
                      <td className="px-3 py-2 text-right">{Math.floor(Math.random() * 100)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Panel - Configuration */}
        <div className="w-80 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col">
          {/* Tabs */}
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            {(['data', 'customize', 'filters'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 px-4 py-3 text-sm font-medium capitalize ${
                  activeTab === tab
                    ? 'text-primary-500 border-b-2 border-primary-500'
                    : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-auto p-4">
            {activeTab === 'data' && (
              <div className="space-y-6">
                {/* Dimensions */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Dimensions (X-Axis / Group By)
                  </label>
                  <div
                    className="min-h-[60px] p-2 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg"
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={(e) => {
                      const col = e.dataTransfer.getData('column')
                      if (col) addDimension(col)
                    }}
                  >
                    {dimensions.length === 0 ? (
                      <p className="text-sm text-gray-400 text-center py-2">
                        Drag columns here
                      </p>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {dimensions.map((dim) => (
                          <span
                            key={dim}
                            className="flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-sm"
                          >
                            {dim}
                            <X
                              className="w-3 h-3 cursor-pointer"
                              onClick={() => removeDimension(dim)}
                            />
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Metrics */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Metrics (Y-Axis / Values)
                  </label>
                  <div className="space-y-2">
                    {metrics.map((metric, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg"
                      >
                        <select
                          value={metric.aggregation}
                          onChange={(e) => {
                            const newMetrics = [...metrics]
                            newMetrics[idx].aggregation = e.target.value
                            newMetrics[idx].label = `${e.target.value}(${metric.column})`
                            setMetrics(newMetrics)
                          }}
                          className="px-2 py-1 text-sm border border-gray-200 dark:border-gray-600 rounded bg-white dark:bg-gray-600"
                        >
                          {aggregations.map((agg) => (
                            <option key={agg} value={agg}>
                              {agg}
                            </option>
                          ))}
                        </select>
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          ({metric.column})
                        </span>
                        <X
                          className="w-4 h-4 ml-auto cursor-pointer text-gray-400 hover:text-red-500"
                          onClick={() =>
                            setMetrics(metrics.filter((_, i) => i !== idx))
                          }
                        />
                      </div>
                    ))}
                    <button
                      onClick={() => addMetric('profit')}
                      className="w-full p-2 text-sm text-primary-500 border border-dashed border-primary-300 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20"
                    >
                      + Add Metric
                    </button>
                  </div>
                </div>

                {/* Time Column */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Time Column
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm">
                    <option value="">None</option>
                    <option value="date">date</option>
                  </select>
                </div>
              </div>
            )}

            {activeTab === 'customize' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Chart Title
                  </label>
                  <input
                    type="text"
                    placeholder="Enter title"
                    className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Color Scheme
                  </label>
                  <div className="grid grid-cols-5 gap-2">
                    {['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a'].map(
                      (color) => (
                        <button
                          key={color}
                          className="w-8 h-8 rounded-lg border-2 border-gray-200"
                          style={{ backgroundColor: color }}
                        />
                      )
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Show Legend
                  </span>
                  <input type="checkbox" defaultChecked className="rounded" />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Show Labels
                  </span>
                  <input type="checkbox" className="rounded" />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Enable Animation
                  </span>
                  <input type="checkbox" defaultChecked className="rounded" />
                </div>
              </div>
            )}

            {activeTab === 'filters' && (
              <div className="space-y-4">
                <button className="w-full p-3 text-sm text-primary-500 border border-dashed border-primary-300 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20">
                  <Filter className="w-4 h-4 inline mr-2" />
                  Add Filter
                </button>
                <p className="text-sm text-gray-500 text-center">
                  No filters applied
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
