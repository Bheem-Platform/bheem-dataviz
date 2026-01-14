import { useState } from 'react'
import { GripVertical, Settings, Trash2, Maximize2, MoreHorizontal } from 'lucide-react'
import ReactECharts from 'echarts-for-react'

interface Widget {
  id: string
  type: 'chart' | 'kpi' | 'table' | 'text'
  title: string
  x: number
  y: number
  w: number
  h: number
  config: Record<string, unknown>
}

interface ChartWidgetProps {
  widget: Widget
  isPreview: boolean
  onEdit?: (widget: Widget) => void
  onDelete?: (widgetId: string) => void
}

// Sample chart options based on widget type
const getChartOption = (widget: Widget) => {
  const baseOption = {
    tooltip: { trigger: 'axis' as const },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
  }

  // Default bar chart
  return {
    ...baseOption,
    xAxis: {
      type: 'category' as const,
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    },
    yAxis: {
      type: 'value' as const,
    },
    series: [
      {
        data: [120, 200, 150, 80, 70, 110, 130],
        type: 'bar',
        itemStyle: {
          color: '#667eea',
        },
      },
    ],
  }
}

export function ChartWidget({ widget, isPreview, onEdit, onDelete }: ChartWidgetProps) {
  const [showMenu, setShowMenu] = useState(false)

  const renderContent = () => {
    switch (widget.type) {
      case 'chart':
        return (
          <ReactECharts
            option={getChartOption(widget)}
            style={{ height: '100%', width: '100%' }}
            opts={{ renderer: 'canvas' }}
          />
        )

      case 'kpi':
        return (
          <div className="flex flex-col items-center justify-center h-full">
            <span className="text-4xl font-bold text-primary-500">$124.5K</span>
            <span className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Total Revenue
            </span>
            <span className="text-xs text-green-500 mt-2">+12.5% vs last month</span>
          </div>
        )

      case 'table':
        return (
          <div className="overflow-auto h-full">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left p-2 font-medium text-gray-600 dark:text-gray-300">
                    Name
                  </th>
                  <th className="text-right p-2 font-medium text-gray-600 dark:text-gray-300">
                    Value
                  </th>
                  <th className="text-right p-2 font-medium text-gray-600 dark:text-gray-300">
                    Change
                  </th>
                </tr>
              </thead>
              <tbody>
                {['Product A', 'Product B', 'Product C'].map((name, i) => (
                  <tr
                    key={name}
                    className="border-b border-gray-100 dark:border-gray-700/50"
                  >
                    <td className="p-2 text-gray-900 dark:text-white">{name}</td>
                    <td className="p-2 text-right text-gray-600 dark:text-gray-300">
                      ${(Math.random() * 1000).toFixed(0)}
                    </td>
                    <td
                      className={`p-2 text-right ${i % 2 === 0 ? 'text-green-500' : 'text-red-500'}`}
                    >
                      {i % 2 === 0 ? '+' : '-'}
                      {(Math.random() * 10).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )

      case 'text':
        return (
          <div className="p-4 h-full">
            <p className="text-gray-700 dark:text-gray-300">
              Add your text content here. You can use this widget for titles,
              descriptions, or any explanatory content in your dashboard.
            </p>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="h-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-2">
          {!isPreview && (
            <div className="widget-drag-handle cursor-move">
              <GripVertical className="w-4 h-4 text-gray-400" />
            </div>
          )}
          <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
            {widget.title}
          </span>
        </div>

        {!isPreview && (
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              <MoreHorizontal className="w-4 h-4 text-gray-400" />
            </button>

            {showMenu && (
              <div className="absolute right-0 top-full mt-1 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10 min-w-[120px]">
                <button
                  onClick={() => {
                    onEdit?.(widget)
                    setShowMenu(false)
                  }}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Settings className="w-4 h-4" />
                  Configure
                </button>
                <button
                  onClick={() => setShowMenu(false)}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Maximize2 className="w-4 h-4" />
                  Expand
                </button>
                <button
                  onClick={() => {
                    onDelete?.(widget.id)
                    setShowMenu(false)
                  }}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 p-2 overflow-hidden">{renderContent()}</div>
    </div>
  )
}
