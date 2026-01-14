import { useState, useRef, useEffect } from 'react'
import {
  Send,
  Sparkles,
  BarChart3,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  Loader2,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Download,
  RefreshCw,
  Zap,
  Brain,
  LineChart,
  PieChart,
  Activity,
} from 'lucide-react'
import ReactECharts from 'echarts-for-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  chart?: any
  insights?: Insight[]
  timestamp: Date
}

interface Insight {
  type: 'trend' | 'anomaly' | 'correlation' | 'recommendation'
  title: string
  description: string
  impact: 'high' | 'medium' | 'low'
}

const sampleInsights: Insight[] = [
  {
    type: 'trend',
    title: 'Revenue Growth',
    description: 'Revenue increased 23% compared to last quarter, primarily driven by the North region.',
    impact: 'high',
  },
  {
    type: 'anomaly',
    title: 'Unusual Drop in West Region',
    description: 'West region sales dropped 15% on Jan 10th, coinciding with a system outage.',
    impact: 'medium',
  },
  {
    type: 'correlation',
    title: 'Marketing Correlation',
    description: 'Strong correlation (0.87) between email campaigns and next-day sales.',
    impact: 'high',
  },
  {
    type: 'recommendation',
    title: 'Inventory Alert',
    description: 'Product SKU-1234 likely to stockout in 5 days based on current velocity.',
    impact: 'high',
  },
]

const quickActions = [
  { icon: TrendingUp, label: 'Sales Trends', query: 'Show me sales trends for the last 6 months' },
  { icon: AlertTriangle, label: 'Anomalies', query: 'Find any anomalies in recent data' },
  { icon: BarChart3, label: 'Top Products', query: 'What are our top 10 products by revenue?' },
  { icon: Lightbulb, label: 'Insights', query: 'Give me key insights about our business performance' },
]

export function KodeeAnalytics() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showInsights, setShowInsights] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const generateChartOption = (type: string) => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    const data = [320, 380, 350, 420, 480, 520]

    if (type === 'trend') {
      return {
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: months },
        yAxis: { type: 'value' },
        series: [
          {
            type: 'line',
            data,
            smooth: true,
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(102, 126, 234, 0.4)' },
                  { offset: 1, color: 'rgba(102, 126, 234, 0.05)' },
                ],
              },
            },
            itemStyle: { color: '#667eea' },
          },
        ],
      }
    }

    return {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: months },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data, itemStyle: { color: '#667eea', borderRadius: [4, 4, 0, 0] } }],
    }
  }

  const handleSend = async (query?: string) => {
    const messageText = query || input
    if (!messageText.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Based on my analysis of your data, here's what I found:\n\n**Key Findings:**\n- Total revenue for the period is **$2.47M**, up 18% from last period\n- The **North region** leads with 34% of total sales\n- **Product A** shows the strongest growth at 45% YoY\n\nI've generated a visualization below to help you understand the trends better.`,
        chart: generateChartOption('trend'),
        insights: sampleInsights.slice(0, 2),
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 2000)
  }

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'trend': return <TrendingUp className="w-4 h-4" />
      case 'anomaly': return <AlertTriangle className="w-4 h-4" />
      case 'correlation': return <Activity className="w-4 h-4" />
      case 'recommendation': return <Lightbulb className="w-4 h-4" />
      default: return <Sparkles className="w-4 h-4" />
    }
  }

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'trend': return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
      case 'anomaly': return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
      case 'correlation': return 'bg-purple-500/10 text-purple-400 border-purple-500/20'
      case 'recommendation': return 'bg-green-500/10 text-green-400 border-green-500/20'
      default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
    }
  }

  return (
    <div className="h-full flex bg-gray-900">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Kodee Analytics</h1>
              <p className="text-sm text-gray-400">AI-powered data insights</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-gray-300 rounded-xl hover:bg-gray-700 transition-colors">
              <RefreshCw className="w-4 h-4" />
              Refresh Data
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-auto p-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-violet-500 via-purple-500 to-pink-500 flex items-center justify-center mb-6 shadow-2xl shadow-purple-500/30">
                <Sparkles className="w-12 h-12 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-3">
                Ask Kodee anything about your data
              </h2>
              <p className="text-gray-400 max-w-lg mb-8">
                I can analyze trends, find anomalies, generate visualizations, and provide actionable insights from your connected data sources.
              </p>

              <div className="grid grid-cols-2 gap-3 max-w-2xl">
                {quickActions.map((action) => (
                  <button
                    key={action.label}
                    onClick={() => handleSend(action.query)}
                    className="flex items-center gap-3 p-4 bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700 hover:border-purple-500/50 hover:bg-gray-800 transition-all group"
                  >
                    <div className="w-10 h-10 rounded-xl bg-gray-700 group-hover:bg-purple-500/20 flex items-center justify-center transition-colors">
                      <action.icon className="w-5 h-5 text-gray-400 group-hover:text-purple-400" />
                    </div>
                    <span className="text-sm text-gray-300 text-left">{action.label}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6 max-w-4xl mx-auto">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-violet-500 to-purple-500 text-white px-6 py-4'
                        : 'bg-gray-800 border border-gray-700'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-700">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center">
                          <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <span className="font-medium text-white">Kodee</span>
                      </div>
                    )}

                    <div className={message.role === 'assistant' ? 'p-6' : ''}>
                      <p className={`whitespace-pre-wrap ${message.role === 'assistant' ? 'text-gray-300' : ''}`}>
                        {message.content}
                      </p>

                      {message.chart && (
                        <div className="mt-4 bg-gray-900/50 rounded-xl p-4">
                          <ReactECharts
                            option={message.chart}
                            style={{ height: '250px', width: '100%' }}
                            opts={{ renderer: 'canvas' }}
                          />
                        </div>
                      )}

                      {message.insights && message.insights.length > 0 && (
                        <div className="mt-4 space-y-2">
                          {message.insights.map((insight, idx) => (
                            <div
                              key={idx}
                              className={`flex items-start gap-3 p-3 rounded-lg border ${getInsightColor(insight.type)}`}
                            >
                              {getInsightIcon(insight.type)}
                              <div>
                                <p className="font-medium text-sm">{insight.title}</p>
                                <p className="text-xs opacity-80 mt-0.5">{insight.description}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {message.role === 'assistant' && (
                        <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-700">
                          <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                            <ThumbsUp className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                            <ThumbsDown className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                            <Copy className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                            <Download className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-800 border border-gray-700 rounded-2xl px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center">
                        <Loader2 className="w-4 h-4 text-white animate-spin" />
                      </div>
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100" />
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-200" />
                      </div>
                      <span className="text-gray-400 text-sm">Analyzing your data...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-800">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-3 p-2 bg-gray-800 border border-gray-700 rounded-2xl focus-within:border-purple-500 transition-colors">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                placeholder="Ask Kodee about your data..."
                className="flex-1 px-4 py-3 bg-transparent text-white placeholder-gray-500 focus:outline-none"
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="p-3 bg-gradient-to-r from-violet-500 to-purple-500 text-white rounded-xl hover:opacity-90 disabled:opacity-50 transition-opacity"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-gray-500 text-center mt-2">
              Kodee AI can analyze your connected data sources and provide insights
            </p>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Auto Insights */}
      {showInsights && (
        <div className="w-80 border-l border-gray-800 bg-gray-800/50 flex flex-col">
          <div className="p-4 border-b border-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                <span className="font-medium text-white">Auto Insights</span>
              </div>
              <button className="p-1 text-gray-400 hover:text-white">
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-4 space-y-3">
            {sampleInsights.map((insight, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl border cursor-pointer hover:scale-[1.02] transition-transform ${getInsightColor(insight.type)}`}
                onClick={() => handleSend(`Tell me more about: ${insight.title}`)}
              >
                <div className="flex items-center gap-2 mb-2">
                  {getInsightIcon(insight.type)}
                  <span className="font-medium text-sm">{insight.title}</span>
                  {insight.impact === 'high' && (
                    <span className="ml-auto px-2 py-0.5 bg-red-500/20 text-red-400 text-xs rounded-full">
                      High
                    </span>
                  )}
                </div>
                <p className="text-xs opacity-80">{insight.description}</p>
              </div>
            ))}
          </div>

          <div className="p-4 border-t border-gray-800">
            <button className="w-full py-3 text-sm text-purple-400 hover:text-purple-300 transition-colors">
              View All Insights →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
