import { useState } from 'react'
import {
  BarChart3,
  LineChart,
  PieChart,
  Activity,
  TrendingUp,
  Map,
  Gauge,
  ScatterChart,
  AreaChart,
  Grid3X3,
  Boxes,
  GitBranch,
  Network,
  Radar,
  Box,
  Layers,
  Workflow,
  Timer,
  Target,
  Hexagon,
  Circle,
  Search,
  Filter,
  Star,
  Clock,
  Plus,
} from 'lucide-react'
import ReactECharts from 'echarts-for-react'

interface ChartType {
  id: string
  name: string
  category: string
  icon: any
  description: string
  popular?: boolean
  option: any
}

const categories = [
  { id: 'all', name: 'All Charts', count: 42 },
  { id: 'basic', name: 'Basic', count: 8 },
  { id: 'statistical', name: 'Statistical', count: 6 },
  { id: 'time-series', name: 'Time Series', count: 5 },
  { id: 'geo', name: 'Geographic', count: 4 },
  { id: 'part-whole', name: 'Part to Whole', count: 6 },
  { id: 'flow', name: 'Flow & Hierarchy', count: 5 },
  { id: 'correlation', name: 'Correlation', count: 4 },
  { id: 'distribution', name: 'Distribution', count: 4 },
]

const chartTypes: ChartType[] = [
  // Basic Charts
  {
    id: 'bar',
    name: 'Bar Chart',
    category: 'basic',
    icon: BarChart3,
    description: 'Compare values across categories',
    popular: true,
    option: {
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [120, 200, 150, 80, 70], itemStyle: { color: '#667eea', borderRadius: [4, 4, 0, 0] } }],
    },
  },
  {
    id: 'line',
    name: 'Line Chart',
    category: 'basic',
    icon: LineChart,
    description: 'Show trends over time',
    popular: true,
    option: {
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
      yAxis: { type: 'value' },
      series: [{ type: 'line', data: [150, 230, 224, 218, 135], smooth: true, itemStyle: { color: '#667eea' } }],
    },
  },
  {
    id: 'area',
    name: 'Area Chart',
    category: 'basic',
    icon: AreaChart,
    description: 'Emphasize volume below a line',
    popular: true,
    option: {
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
      yAxis: { type: 'value' },
      series: [{ type: 'line', data: [150, 230, 224, 218, 135], areaStyle: { color: 'rgba(102, 126, 234, 0.3)' }, smooth: true, itemStyle: { color: '#667eea' } }],
    },
  },
  {
    id: 'pie',
    name: 'Pie Chart',
    category: 'part-whole',
    icon: PieChart,
    description: 'Show proportions of a whole',
    popular: true,
    option: {
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 1048, name: 'Search' },
          { value: 735, name: 'Direct' },
          { value: 580, name: 'Email' },
          { value: 484, name: 'Social' },
        ],
      }],
    },
  },
  {
    id: 'donut',
    name: 'Donut Chart',
    category: 'part-whole',
    icon: Circle,
    description: 'Pie chart with center cutout',
    option: {
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 1048, name: 'Search' },
          { value: 735, name: 'Direct' },
          { value: 580, name: 'Email' },
        ],
      }],
    },
  },
  {
    id: 'scatter',
    name: 'Scatter Plot',
    category: 'correlation',
    icon: ScatterChart,
    description: 'Show correlation between variables',
    popular: true,
    option: {
      xAxis: { type: 'value' },
      yAxis: { type: 'value' },
      series: [{
        type: 'scatter',
        data: [[10, 8.04], [8, 6.95], [13, 7.58], [9, 8.81], [11, 8.33], [14, 9.96], [6, 7.24], [4, 4.26], [12, 10.84], [7, 4.82]],
        itemStyle: { color: '#667eea' },
      }],
    },
  },
  {
    id: 'bubble',
    name: 'Bubble Chart',
    category: 'correlation',
    icon: Hexagon,
    description: 'Scatter with size dimension',
    option: {
      xAxis: { type: 'value' },
      yAxis: { type: 'value' },
      series: [{
        type: 'scatter',
        symbolSize: (data: number[]) => Math.sqrt(data[2]) * 3,
        data: [[10, 8, 100], [8, 6, 80], [13, 7, 120], [9, 8, 90], [11, 8, 110]],
        itemStyle: { color: '#667eea', opacity: 0.7 },
      }],
    },
  },
  {
    id: 'stacked-bar',
    name: 'Stacked Bar',
    category: 'basic',
    icon: Layers,
    description: 'Compare composition across categories',
    option: {
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
      yAxis: { type: 'value' },
      series: [
        { type: 'bar', stack: 'total', data: [120, 132, 101, 134, 90], itemStyle: { color: '#667eea' } },
        { type: 'bar', stack: 'total', data: [220, 182, 191, 234, 290], itemStyle: { color: '#f687b3' } },
      ],
    },
  },
  {
    id: 'horizontal-bar',
    name: 'Horizontal Bar',
    category: 'basic',
    icon: BarChart3,
    description: 'Bar chart with horizontal orientation',
    option: {
      yAxis: { type: 'category', data: ['Brazil', 'Indonesia', 'USA', 'India', 'China'] },
      xAxis: { type: 'value' },
      series: [{ type: 'bar', data: [18, 23, 29, 104, 131], itemStyle: { color: '#667eea', borderRadius: [0, 4, 4, 0] } }],
    },
  },
  {
    id: 'mixed',
    name: 'Mixed Chart',
    category: 'basic',
    icon: Activity,
    description: 'Combine multiple chart types',
    option: {
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
      yAxis: { type: 'value' },
      series: [
        { type: 'bar', data: [120, 200, 150, 80, 70], itemStyle: { color: '#667eea' } },
        { type: 'line', data: [150, 230, 224, 218, 135], itemStyle: { color: '#f687b3' } },
      ],
    },
  },
  // Time Series
  {
    id: 'time-series',
    name: 'Time Series',
    category: 'time-series',
    icon: Clock,
    description: 'Visualize data over time',
    popular: true,
    option: {
      xAxis: { type: 'time' },
      yAxis: { type: 'value' },
      series: [{
        type: 'line',
        smooth: true,
        data: [
          ['2023-01-01', 150],
          ['2023-02-01', 230],
          ['2023-03-01', 224],
          ['2023-04-01', 218],
          ['2023-05-01', 335],
        ],
        itemStyle: { color: '#667eea' },
      }],
    },
  },
  {
    id: 'candlestick',
    name: 'Candlestick',
    category: 'time-series',
    icon: TrendingUp,
    description: 'Stock price movements',
    option: {
      xAxis: { data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
      yAxis: {},
      series: [{
        type: 'candlestick',
        data: [
          [20, 34, 10, 38],
          [40, 35, 30, 50],
          [31, 38, 33, 44],
          [38, 15, 5, 42],
          [25, 45, 20, 50],
        ],
      }],
    },
  },
  {
    id: 'sparkline',
    name: 'Sparkline',
    category: 'time-series',
    icon: Activity,
    description: 'Compact inline trends',
    option: {
      grid: { left: 0, right: 0, top: 0, bottom: 0 },
      xAxis: { type: 'category', show: false, data: [1, 2, 3, 4, 5, 6, 7] },
      yAxis: { type: 'value', show: false },
      series: [{ type: 'line', data: [5, 8, 6, 9, 7, 10, 8], smooth: true, symbol: 'none', itemStyle: { color: '#667eea' } }],
    },
  },
  // Statistical
  {
    id: 'histogram',
    name: 'Histogram',
    category: 'distribution',
    icon: BarChart3,
    description: 'Show data distribution',
    option: {
      xAxis: { type: 'category', data: ['0-10', '10-20', '20-30', '30-40', '40-50'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [5, 20, 36, 10, 10], barWidth: '99%', itemStyle: { color: '#667eea' } }],
    },
  },
  {
    id: 'boxplot',
    name: 'Box Plot',
    category: 'distribution',
    icon: Box,
    description: 'Statistical distribution summary',
    option: {
      xAxis: { type: 'category', data: ['A', 'B', 'C'] },
      yAxis: { type: 'value' },
      series: [{
        type: 'boxplot',
        data: [
          [655, 850, 940, 980, 1070],
          [760, 800, 845, 885, 960],
          [780, 840, 855, 880, 940],
        ],
      }],
    },
  },
  // Part to Whole
  {
    id: 'treemap',
    name: 'Treemap',
    category: 'part-whole',
    icon: Grid3X3,
    description: 'Hierarchical proportions',
    option: {
      series: [{
        type: 'treemap',
        data: [
          { name: 'A', value: 10, children: [{ name: 'A1', value: 4 }, { name: 'A2', value: 6 }] },
          { name: 'B', value: 20 },
          { name: 'C', value: 15 },
        ],
      }],
    },
  },
  {
    id: 'sunburst',
    name: 'Sunburst',
    category: 'part-whole',
    icon: Target,
    description: 'Hierarchical ring chart',
    option: {
      series: [{
        type: 'sunburst',
        data: [
          { name: 'A', children: [{ name: 'A1', value: 4 }, { name: 'A2', value: 6 }] },
          { name: 'B', value: 20 },
          { name: 'C', value: 15 },
        ],
        radius: ['15%', '80%'],
      }],
    },
  },
  // Flow & Hierarchy
  {
    id: 'sankey',
    name: 'Sankey Diagram',
    category: 'flow',
    icon: Workflow,
    description: 'Flow quantities between nodes',
    option: {
      series: [{
        type: 'sankey',
        data: [{ name: 'a' }, { name: 'b' }, { name: 'c' }, { name: 'd' }],
        links: [
          { source: 'a', target: 'b', value: 5 },
          { source: 'a', target: 'c', value: 3 },
          { source: 'b', target: 'd', value: 8 },
          { source: 'c', target: 'd', value: 3 },
        ],
      }],
    },
  },
  {
    id: 'funnel',
    name: 'Funnel Chart',
    category: 'flow',
    icon: GitBranch,
    description: 'Conversion process stages',
    option: {
      series: [{
        type: 'funnel',
        data: [
          { value: 100, name: 'Visit' },
          { value: 80, name: 'Inquiry' },
          { value: 60, name: 'Order' },
          { value: 40, name: 'Click' },
          { value: 20, name: 'Show' },
        ],
      }],
    },
  },
  {
    id: 'tree',
    name: 'Tree Diagram',
    category: 'flow',
    icon: Network,
    description: 'Hierarchical relationships',
    option: {
      series: [{
        type: 'tree',
        data: [{
          name: 'Root',
          children: [
            { name: 'Child A', children: [{ name: 'A1' }, { name: 'A2' }] },
            { name: 'Child B' },
          ],
        }],
        top: '10%',
        bottom: '10%',
      }],
    },
  },
  // Correlation
  {
    id: 'heatmap',
    name: 'Heatmap',
    category: 'correlation',
    icon: Boxes,
    description: 'Matrix with color intensity',
    option: {
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
      yAxis: { type: 'category', data: ['Morning', 'Afternoon', 'Evening'] },
      visualMap: { min: 0, max: 10, show: false },
      series: [{
        type: 'heatmap',
        data: [[0, 0, 5], [1, 0, 1], [2, 0, 0], [0, 1, 7], [1, 1, 2], [2, 1, 3], [0, 2, 1], [1, 2, 6], [2, 2, 8]],
      }],
    },
  },
  {
    id: 'radar',
    name: 'Radar Chart',
    category: 'correlation',
    icon: Radar,
    description: 'Multi-variable comparison',
    option: {
      radar: {
        indicator: [
          { name: 'Sales', max: 100 },
          { name: 'Admin', max: 100 },
          { name: 'IT', max: 100 },
          { name: 'Support', max: 100 },
          { name: 'Dev', max: 100 },
        ],
      },
      series: [{
        type: 'radar',
        data: [{ value: [80, 50, 60, 70, 90] }],
        areaStyle: { color: 'rgba(102, 126, 234, 0.3)' },
        itemStyle: { color: '#667eea' },
      }],
    },
  },
  // Geographic
  {
    id: 'map',
    name: 'Geographic Map',
    category: 'geo',
    icon: Map,
    description: 'Data on geographic regions',
    option: {
      series: [{
        type: 'pie',
        radius: '60%',
        label: { show: true, formatter: 'Map Viz' },
        data: [{ value: 100, name: 'Geographic visualization' }],
      }],
    },
  },
  // Gauges
  {
    id: 'gauge',
    name: 'Gauge Chart',
    category: 'statistical',
    icon: Gauge,
    description: 'Show progress toward goal',
    popular: true,
    option: {
      series: [{
        type: 'gauge',
        progress: { show: true },
        detail: { valueAnimation: true, formatter: '{value}%' },
        data: [{ value: 70, name: 'Progress' }],
      }],
    },
  },
  {
    id: 'kpi',
    name: 'Big Number / KPI',
    category: 'statistical',
    icon: Target,
    description: 'Single metric highlight',
    popular: true,
    option: {
      title: { text: '$1.2M', left: 'center', top: 'center', textStyle: { fontSize: 48, color: '#667eea' } },
      series: [],
    },
  },
  // Additional charts
  {
    id: 'waterfall',
    name: 'Waterfall Chart',
    category: 'statistical',
    icon: BarChart3,
    description: 'Show cumulative effect',
    option: {
      xAxis: { type: 'category', data: ['Start', 'Q1', 'Q2', 'Q3', 'Q4', 'End'] },
      yAxis: { type: 'value' },
      series: [
        { type: 'bar', stack: 'total', itemStyle: { color: 'transparent' }, data: [0, 100, 150, 130, 180, 0] },
        { type: 'bar', stack: 'total', data: [100, 50, -20, 50, 20, 200], itemStyle: { color: '#667eea' } },
      ],
    },
  },
  {
    id: 'parallel',
    name: 'Parallel Coordinates',
    category: 'correlation',
    icon: Activity,
    description: 'Multi-dimensional comparison',
    option: {
      parallelAxis: [
        { dim: 0, name: 'Price' },
        { dim: 1, name: 'Rating' },
        { dim: 2, name: 'Sales' },
      ],
      series: [{
        type: 'parallel',
        lineStyle: { width: 1, opacity: 0.5 },
        data: [[1, 2, 3], [4, 5, 6], [2, 3, 4]],
      }],
    },
  },
  {
    id: 'polar-bar',
    name: 'Polar Bar',
    category: 'basic',
    icon: Circle,
    description: 'Circular bar chart',
    option: {
      angleAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
      radiusAxis: {},
      polar: {},
      series: [{ type: 'bar', data: [1, 2, 3, 4, 5], coordinateSystem: 'polar', itemStyle: { color: '#667eea' } }],
    },
  },
  {
    id: 'rose',
    name: 'Nightingale Rose',
    category: 'part-whole',
    icon: PieChart,
    description: 'Pie with varying radius',
    option: {
      series: [{
        type: 'pie',
        radius: ['20%', '70%'],
        roseType: 'area',
        data: [
          { value: 40, name: 'A' },
          { value: 38, name: 'B' },
          { value: 32, name: 'C' },
          { value: 30, name: 'D' },
        ],
      }],
    },
  },
  {
    id: 'graph',
    name: 'Network Graph',
    category: 'flow',
    icon: Network,
    description: 'Node-link relationships',
    option: {
      series: [{
        type: 'graph',
        layout: 'force',
        data: [
          { name: 'Node 1', symbolSize: 30 },
          { name: 'Node 2', symbolSize: 20 },
          { name: 'Node 3', symbolSize: 25 },
        ],
        links: [
          { source: 'Node 1', target: 'Node 2' },
          { source: 'Node 2', target: 'Node 3' },
          { source: 'Node 1', target: 'Node 3' },
        ],
        force: { repulsion: 100 },
      }],
    },
  },
  {
    id: 'calendar',
    name: 'Calendar Heatmap',
    category: 'time-series',
    icon: Grid3X3,
    description: 'Activity over calendar',
    option: {
      visualMap: { show: false, min: 0, max: 10 },
      calendar: { range: '2023-01', cellSize: ['auto', 15] },
      series: [{
        type: 'heatmap',
        coordinateSystem: 'calendar',
        data: [['2023-01-01', 5], ['2023-01-02', 8], ['2023-01-03', 3]],
      }],
    },
  },
  {
    id: 'pictorial',
    name: 'Pictorial Bar',
    category: 'basic',
    icon: BarChart3,
    description: 'Bar with custom symbols',
    option: {
      xAxis: { type: 'category', data: ['Water', 'Food', 'Energy'] },
      yAxis: { type: 'value' },
      series: [{
        type: 'pictorialBar',
        symbol: 'roundRect',
        data: [123, 60, 25],
        itemStyle: { color: '#667eea' },
      }],
    },
  },
  {
    id: 'themeriver',
    name: 'Theme River',
    category: 'time-series',
    icon: Activity,
    description: 'Stacked area over time',
    option: {
      singleAxis: { type: 'time', min: '2023-01-01', max: '2023-01-05' },
      series: [{
        type: 'themeRiver',
        data: [
          ['2023-01-01', 10, 'A'],
          ['2023-01-02', 15, 'A'],
          ['2023-01-01', 20, 'B'],
          ['2023-01-02', 25, 'B'],
        ],
      }],
    },
  },
]

export function ChartGallery() {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showPopularOnly, setShowPopularOnly] = useState(false)

  const filteredCharts = chartTypes.filter((chart) => {
    const matchesCategory = selectedCategory === 'all' || chart.category === selectedCategory
    const matchesSearch = chart.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      chart.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesPopular = !showPopularOnly || chart.popular
    return matchesCategory && matchesSearch && matchesPopular
  })

  return (
    <div className="h-full flex bg-gray-900">
      {/* Sidebar - Categories */}
      <div className="w-64 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-lg font-semibold text-white mb-4">Chart Gallery</h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search charts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        <div className="p-4">
          <button
            onClick={() => setShowPopularOnly(!showPopularOnly)}
            className={`flex items-center gap-2 w-full px-3 py-2 rounded-lg transition-colors ${
              showPopularOnly
                ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                : 'text-gray-400 hover:bg-gray-800'
            }`}
          >
            <Star className="w-4 h-4" />
            <span>Popular Only</span>
          </button>
        </div>

        <nav className="flex-1 overflow-auto p-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center justify-between w-full px-3 py-2 rounded-lg transition-colors ${
                selectedCategory === category.id
                  ? 'bg-purple-500/20 text-purple-400'
                  : 'text-gray-400 hover:bg-gray-800'
              }`}
            >
              <span>{category.name}</span>
              <span className="text-xs px-2 py-0.5 bg-gray-700 rounded-full">{category.count}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div>
            <h1 className="text-xl font-bold text-white">
              {selectedCategory === 'all' ? 'All Visualizations' : categories.find(c => c.id === selectedCategory)?.name}
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              {filteredCharts.length} chart types available
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-gray-300 rounded-xl hover:bg-gray-700 transition-colors">
              <Filter className="w-4 h-4" />
              Filters
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-500 text-white rounded-xl hover:opacity-90 transition-opacity">
              <Plus className="w-4 h-4" />
              Create Custom
            </button>
          </div>
        </header>

        {/* Chart Grid */}
        <div className="flex-1 overflow-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredCharts.map((chart) => (
              <div
                key={chart.id}
                className="group bg-gray-800/50 border border-gray-700 rounded-xl overflow-hidden hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10 transition-all cursor-pointer"
              >
                {/* Chart Preview */}
                <div className="h-40 bg-gray-900/50 p-2 relative">
                  <ReactECharts
                    option={chart.option}
                    style={{ height: '100%', width: '100%' }}
                    opts={{ renderer: 'canvas' }}
                  />
                  {chart.popular && (
                    <div className="absolute top-2 right-2">
                      <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                    </div>
                  )}
                </div>

                {/* Chart Info */}
                <div className="p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
                      <chart.icon className="w-4 h-4 text-purple-400" />
                    </div>
                    <h3 className="font-medium text-white group-hover:text-purple-400 transition-colors">
                      {chart.name}
                    </h3>
                  </div>
                  <p className="text-sm text-gray-400">{chart.description}</p>
                  <div className="mt-3">
                    <span className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded-full">
                      {categories.find(c => c.id === chart.category)?.name}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
