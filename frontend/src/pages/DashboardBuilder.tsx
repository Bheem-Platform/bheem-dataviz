import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { GridStack } from 'gridstack'
import {
  Save,
  Share2,
  Play,
  Plus,
  Settings,
  Undo,
  Redo,
  Eye,
} from 'lucide-react'
import { ChartWidget } from '@/components/dashboard/ChartWidget'

// Widget types
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

export function DashboardBuilder() {
  const { id } = useParams()
  const gridRef = useRef<HTMLDivElement>(null)
  const gridInstance = useRef<GridStack | null>(null)
  const [widgets, setWidgets] = useState<Widget[]>([])
  const [isPreview, setIsPreview] = useState(false)

  const isNew = !id

  // Initialize GridStack
  useEffect(() => {
    if (!gridRef.current) return

    gridInstance.current = GridStack.init(
      {
        column: 12,
        cellHeight: 80,
        margin: 8,
        float: true,
        animate: true,
        draggable: {
          handle: '.widget-drag-handle',
        },
        resizable: {
          handles: 'e,se,s,sw,w',
        },
      },
      gridRef.current
    )

    // Handle widget changes
    gridInstance.current.on('change', (event, items) => {
      if (items) {
        setWidgets((prev) =>
          prev.map((widget) => {
            const item = items.find((i: any) => i.id === widget.id)
            if (item) {
              return {
                ...widget,
                x: item.x ?? widget.x,
                y: item.y ?? widget.y,
                w: item.w ?? widget.w,
                h: item.h ?? widget.h,
              }
            }
            return widget
          })
        )
      }
    })

    return () => {
      gridInstance.current?.destroy(false)
    }
  }, [])

  // Add widget
  const addWidget = (type: Widget['type']) => {
    const newWidget: Widget = {
      id: `widget-${Date.now()}`,
      type,
      title: `New ${type.charAt(0).toUpperCase() + type.slice(1)}`,
      x: 0,
      y: 0,
      w: type === 'kpi' ? 3 : 6,
      h: type === 'kpi' ? 2 : 4,
      config: {},
    }

    setWidgets((prev) => [...prev, newWidget])

    // Add to grid
    gridInstance.current?.addWidget({
      id: newWidget.id,
      x: newWidget.x,
      y: newWidget.y,
      w: newWidget.w,
      h: newWidget.h,
      content: `<div id="${newWidget.id}-content"></div>`,
    })
  }

  return (
    <div className="h-full flex flex-col bg-gray-100 dark:bg-gray-900">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Untitled Dashboard"
            defaultValue={isNew ? '' : 'My Dashboard'}
            className="text-lg font-medium bg-transparent border-none focus:outline-none focus:ring-0 text-gray-900 dark:text-white placeholder-gray-400"
          />
        </div>

        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
            <Undo className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
          <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
            <Redo className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>

          <div className="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-2" />

          <button
            onClick={() => setIsPreview(!isPreview)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
              isPreview
                ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
            }`}
          >
            <Eye className="w-5 h-5" />
            Preview
          </button>

          <button className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-600 dark:text-gray-300">
            <Share2 className="w-5 h-5" />
            Share
          </button>

          <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
            <Save className="w-5 h-5" />
            Save
          </button>
        </div>
      </header>

      {/* Toolbar */}
      {!isPreview && (
        <div className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <span className="text-sm text-gray-500 dark:text-gray-400 mr-2">
            Add Widget:
          </span>
          <button
            onClick={() => addWidget('chart')}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-700 dark:text-gray-200"
          >
            <Plus className="w-4 h-4" />
            Chart
          </button>
          <button
            onClick={() => addWidget('kpi')}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-700 dark:text-gray-200"
          >
            <Plus className="w-4 h-4" />
            KPI
          </button>
          <button
            onClick={() => addWidget('table')}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-700 dark:text-gray-200"
          >
            <Plus className="w-4 h-4" />
            Table
          </button>
          <button
            onClick={() => addWidget('text')}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-700 dark:text-gray-200"
          >
            <Plus className="w-4 h-4" />
            Text
          </button>
        </div>
      )}

      {/* Canvas */}
      <div className="flex-1 overflow-auto p-4">
        <div
          ref={gridRef}
          className="grid-stack"
          style={{ minHeight: '100%' }}
        >
          {widgets.map((widget) => (
            <div
              key={widget.id}
              className="grid-stack-item"
              gs-id={widget.id}
              gs-x={widget.x}
              gs-y={widget.y}
              gs-w={widget.w}
              gs-h={widget.h}
            >
              <div className="grid-stack-item-content">
                <ChartWidget widget={widget} isPreview={isPreview} />
              </div>
            </div>
          ))}
        </div>

        {widgets.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center mb-4">
              <Plus className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Start building your dashboard
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-md">
              Add charts, KPIs, tables, and text widgets to create your
              visualization. Drag and resize widgets to customize the layout.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
