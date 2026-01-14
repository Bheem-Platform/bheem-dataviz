import { useState } from 'react'
import { Save, Play, Settings } from 'lucide-react'
import ReactECharts from 'echarts-for-react'

const chartTypes = [
  { id: 'bar', name: 'Bar', icon: '📊' },
  { id: 'line', name: 'Line', icon: '📈' },
  { id: 'pie', name: 'Pie', icon: '🥧' },
  { id: 'area', name: 'Area', icon: '📉' },
  { id: 'scatter', name: 'Scatter', icon: '⚬' },
  { id: 'heatmap', name: 'Heatmap', icon: '🔥' },
]

// Sample data
const sampleOption = {
  title: {
    text: 'Sales by Region',
    left: 'center',
  },
  tooltip: {
    trigger: 'axis',
  },
  xAxis: {
    type: 'category',
    data: ['North', 'South', 'East', 'West', 'Central'],
  },
  yAxis: {
    type: 'value',
  },
  series: [
    {
      name: 'Sales',
      type: 'bar',
      data: [320, 280, 450, 380, 290],
      itemStyle: {
        color: '#667eea',
      },
    },
  ],
}

export function ChartBuilder() {
  const [selectedType, setSelectedType] = useState('bar')

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Untitled Chart"
            className="text-lg font-medium bg-transparent border-none focus:outline-none focus:ring-0 text-gray-900 dark:text-white placeholder-gray-400"
          />
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-600 dark:text-gray-300">
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
        {/* Left Panel - Data & Config */}
        <div className="w-80 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col">
          {/* Chart Type */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Chart Type
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {chartTypes.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setSelectedType(type.id)}
                  className={`flex flex-col items-center gap-1 p-2 rounded-lg border-2 transition-colors ${
                    selectedType === type.id
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-transparent hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <span className="text-xl">{type.icon}</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">
                    {type.name}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Data Source */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Data Source
            </h3>
            <select className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              <option>Select a dataset...</option>
              <option>Sales Data</option>
              <option>Marketing Analytics</option>
            </select>
          </div>

          {/* Dimensions */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Dimensions (X-Axis)
            </h3>
            <div className="p-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-center text-sm text-gray-500">
              Drag fields here
            </div>
          </div>

          {/* Measures */}
          <div className="p-4">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Measures (Y-Axis)
            </h3>
            <div className="p-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-center text-sm text-gray-500">
              Drag fields here
            </div>
          </div>
        </div>

        {/* Chart Preview */}
        <div className="flex-1 p-6 bg-gray-50 dark:bg-gray-900">
          <div className="h-full bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4">
            <ReactECharts
              option={sampleOption}
              style={{ height: '100%', width: '100%' }}
              opts={{ renderer: 'canvas' }}
            />
          </div>
        </div>

        {/* Right Panel - Style */}
        <div className="w-72 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4 flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Style
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Title
              </label>
              <input
                type="text"
                defaultValue="Sales by Region"
                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                Primary Color
              </label>
              <div className="flex gap-2">
                <input
                  type="color"
                  defaultValue="#667eea"
                  className="w-10 h-10 rounded cursor-pointer"
                />
                <input
                  type="text"
                  defaultValue="#667eea"
                  className="flex-1 px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="text-xs text-gray-500 dark:text-gray-400">
                Show Legend
              </label>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-xs text-gray-500 dark:text-gray-400">
                Show Grid
              </label>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-xs text-gray-500 dark:text-gray-400">
                Show Values
              </label>
              <input type="checkbox" className="rounded" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
