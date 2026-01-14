import { useState, useEffect } from 'react'
import {
  Workflow,
  Clock,
  Mail,
  Bell,
  Play,
  Pause,
  Plus,
  MoreVertical,
  Calendar,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Settings,
  Zap,
  FileText,
  Database,
  Send,
  GitBranch,
  Filter,
  Search,
  ChevronRight,
  Timer,
  BarChart3,
  Bot,
  Loader2,
  ExternalLink,
  Activity,
} from 'lucide-react'
import { workflowsApi } from '../lib/api'

interface WorkflowItem {
  id: string
  name: string
  description: string
  type: 'scheduled-report' | 'alert' | 'data-refresh' | 'ai-analysis'
  status: 'active' | 'paused' | 'error'
  schedule?: string
  lastRun?: string
  nextRun?: string
  trigger?: string
  actions: string[]
}

const workflows: WorkflowItem[] = [
  {
    id: '1',
    name: 'Daily Sales Report',
    description: 'Generate and send daily sales summary to stakeholders',
    type: 'scheduled-report',
    status: 'active',
    schedule: 'Daily at 8:00 AM',
    lastRun: '2024-01-15 08:00',
    nextRun: '2024-01-16 08:00',
    actions: ['Generate Report', 'Send Email', 'Archive'],
  },
  {
    id: '2',
    name: 'Revenue Anomaly Alert',
    description: 'Alert when revenue drops more than 20% from average',
    type: 'alert',
    status: 'active',
    trigger: 'Revenue < 80% of rolling avg',
    lastRun: '2024-01-14 15:30',
    actions: ['Check Threshold', 'Send Slack', 'Create Ticket'],
  },
  {
    id: '3',
    name: 'Weekly Data Sync',
    description: 'Sync data from external sources every week',
    type: 'data-refresh',
    status: 'paused',
    schedule: 'Weekly on Monday 6:00 AM',
    lastRun: '2024-01-08 06:00',
    nextRun: 'Paused',
    actions: ['Connect Source', 'Transform Data', 'Load to DB'],
  },
  {
    id: '4',
    name: 'AI Trend Analysis',
    description: 'Run Kodee AI analysis on monthly trends',
    type: 'ai-analysis',
    status: 'active',
    schedule: 'Monthly on 1st at 9:00 AM',
    lastRun: '2024-01-01 09:00',
    nextRun: '2024-02-01 09:00',
    actions: ['Gather Data', 'AI Analysis', 'Generate Insights', 'Notify Team'],
  },
  {
    id: '5',
    name: 'Inventory Low Stock Alert',
    description: 'Alert when inventory falls below reorder point',
    type: 'alert',
    status: 'error',
    trigger: 'Stock < Reorder Point',
    lastRun: '2024-01-15 10:00 (Failed)',
    actions: ['Check Stock', 'Send Alert', 'Create PO'],
  },
]

const workflowTemplates = [
  { icon: FileText, name: 'Scheduled Report', description: 'Send reports on a schedule' },
  { icon: AlertTriangle, name: 'Threshold Alert', description: 'Alert when metrics cross thresholds' },
  { icon: RefreshCw, name: 'Data Refresh', description: 'Sync data from external sources' },
  { icon: Bot, name: 'AI Analysis', description: 'Automated Kodee AI insights' },
  { icon: Database, name: 'ETL Pipeline', description: 'Extract, transform, load data' },
  { icon: Mail, name: 'Email Digest', description: 'Periodic email summaries' },
]

export function Workflows() {
  const [workflowList, setWorkflowList] = useState<WorkflowItem[]>(workflows)
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowItem | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [filterType, setFilterType] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [analytics, setAnalytics] = useState({
    active: 3,
    paused: 1,
    error: 1,
    runsToday: 127
  })

  // Fetch workflows from BheemFlow API
  useEffect(() => {
    const fetchWorkflows = async () => {
      setLoading(true)
      try {
        const response = await workflowsApi.list()
        if (response.data?.workflows && response.data.workflows.length > 0) {
          // Transform BheemFlow workflow format to local format
          const bheemFlowWorkflows = response.data.workflows.map((wf: any) => ({
            id: wf.id,
            name: wf.name,
            description: wf.description || 'BheemFlow workflow',
            type: wf.category === 'refresh' ? 'data-refresh' :
                  wf.category === 'alert' ? 'alert' :
                  wf.category === 'report' ? 'scheduled-report' : 'ai-analysis',
            status: wf.status || 'active',
            schedule: wf.schedule || undefined,
            lastRun: wf.updated_at,
            actions: wf.canvas_state?.nodes?.map((n: any) => n.label || n.type) || ['Process'],
          }))
          setWorkflowList([...bheemFlowWorkflows, ...workflows])
        }
      } catch (error) {
        console.log('Using demo workflows for development')
      } finally {
        setLoading(false)
      }
    }

    const fetchAnalytics = async () => {
      try {
        const response = await workflowsApi.getAnalytics(7)
        if (response.data) {
          setAnalytics({
            active: workflowList.filter(w => w.status === 'active').length,
            paused: workflowList.filter(w => w.status === 'paused').length,
            error: workflowList.filter(w => w.status === 'error').length,
            runsToday: response.data.total_executions || 127
          })
        }
      } catch (error) {
        console.log('Using demo analytics')
      }
    }

    fetchWorkflows()
    fetchAnalytics()
  }, [])

  const executeWorkflow = async (workflowId: string) => {
    try {
      const response = await workflowsApi.execute(workflowId, {})
      console.log('Workflow execution started:', response.data)
      alert('Workflow execution started!')
    } catch (error) {
      console.log('Demo mode: Would execute workflow', workflowId)
      alert('Demo: Workflow execution would start')
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'scheduled-report': return FileText
      case 'alert': return Bell
      case 'data-refresh': return RefreshCw
      case 'ai-analysis': return Bot
      default: return Workflow
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'scheduled-report': return 'bg-blue-500/20 text-blue-400'
      case 'alert': return 'bg-amber-500/20 text-amber-400'
      case 'data-refresh': return 'bg-green-500/20 text-green-400'
      case 'ai-analysis': return 'bg-purple-500/20 text-purple-400'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle2 className="w-4 h-4 text-green-400" />
      case 'paused': return <Pause className="w-4 h-4 text-yellow-400" />
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
      default: return null
    }
  }

  const filteredWorkflows = workflowList.filter((w) => {
    const matchesType = filterType === 'all' || w.type === filterType
    const matchesSearch = w.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      w.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesType && matchesSearch
  })

  return (
    <div className="h-full flex bg-gray-900">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Workflow className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">BheemFlow Workflows</h1>
              <p className="text-sm text-gray-400">Automate reports, alerts, and data pipelines</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search workflows..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 w-64"
              />
            </div>
            <a
              href="https://platform.bheem.co.uk/workflows"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-gray-300 rounded-xl hover:bg-gray-700 transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              BheemFlow Designer
            </a>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl hover:opacity-90 transition-opacity"
            >
              <Plus className="w-4 h-4" />
              Create Workflow
            </button>
          </div>
        </header>

        {/* Stats Bar */}
        <div className="grid grid-cols-4 gap-4 p-6 border-b border-gray-800">
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{workflowList.filter(w => w.status === 'active').length}</p>
                <p className="text-sm text-gray-400">Active</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center">
                <Pause className="w-5 h-5 text-yellow-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{workflowList.filter(w => w.status === 'paused').length}</p>
                <p className="text-sm text-gray-400">Paused</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                <XCircle className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{workflowList.filter(w => w.status === 'error').length}</p>
                <p className="text-sm text-gray-400">Error</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Activity className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{analytics.runsToday}</p>
                <p className="text-sm text-gray-400">Runs Today</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 px-6 py-3 border-b border-gray-800">
          {[
            { id: 'all', label: 'All Workflows' },
            { id: 'scheduled-report', label: 'Reports' },
            { id: 'alert', label: 'Alerts' },
            { id: 'data-refresh', label: 'Data Refresh' },
            { id: 'ai-analysis', label: 'AI Analysis' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterType(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filterType === tab.id
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'text-gray-400 hover:bg-gray-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Workflow List */}
        <div className="flex-1 overflow-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
            </div>
          ) : (
          <div className="space-y-3">
            {filteredWorkflows.map((workflow) => {
              const TypeIcon = getTypeIcon(workflow.type)
              return (
                <div
                  key={workflow.id}
                  onClick={() => setSelectedWorkflow(workflow)}
                  className={`bg-gray-800/50 border rounded-xl p-4 cursor-pointer transition-all hover:shadow-lg ${
                    selectedWorkflow?.id === workflow.id
                      ? 'border-emerald-500/50 shadow-emerald-500/10'
                      : 'border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${getTypeColor(workflow.type)}`}>
                        <TypeIcon className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold text-white">{workflow.name}</h3>
                          {getStatusIcon(workflow.status)}
                        </div>
                        <p className="text-sm text-gray-400 mt-1">{workflow.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        {workflow.schedule && (
                          <div className="flex items-center gap-2 text-sm text-gray-400">
                            <Clock className="w-4 h-4" />
                            {workflow.schedule}
                          </div>
                        )}
                        {workflow.trigger && (
                          <div className="flex items-center gap-2 text-sm text-gray-400">
                            <Zap className="w-4 h-4" />
                            {workflow.trigger}
                          </div>
                        )}
                        {workflow.lastRun && (
                          <p className="text-xs text-gray-500 mt-1">Last run: {workflow.lastRun}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                          {workflow.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        </button>
                        <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                          <Settings className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Actions Pipeline */}
                  <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-700">
                    <span className="text-xs text-gray-500 mr-2">Pipeline:</span>
                    {workflow.actions.map((action, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <span className="px-3 py-1 bg-gray-700/50 text-gray-300 text-xs rounded-lg">
                          {action}
                        </span>
                        {idx < workflow.actions.length - 1 && (
                          <ChevronRight className="w-4 h-4 text-gray-600" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
          )}
        </div>
      </div>

      {/* Right Sidebar - Workflow Details */}
      {selectedWorkflow && (
        <div className="w-96 border-l border-gray-800 bg-gray-800/50 flex flex-col">
          <div className="p-4 border-b border-gray-800">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white">Workflow Details</h3>
              <button
                onClick={() => setSelectedWorkflow(null)}
                className="p-1 text-gray-400 hover:text-white"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-4 space-y-6">
            {/* Basic Info */}
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-3">Configuration</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b border-gray-700">
                  <span className="text-sm text-gray-400">Status</span>
                  <span className={`flex items-center gap-2 text-sm ${
                    selectedWorkflow.status === 'active' ? 'text-green-400' :
                    selectedWorkflow.status === 'paused' ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {getStatusIcon(selectedWorkflow.status)}
                    {selectedWorkflow.status.charAt(0).toUpperCase() + selectedWorkflow.status.slice(1)}
                  </span>
                </div>
                <div className="flex items-center justify-between py-2 border-b border-gray-700">
                  <span className="text-sm text-gray-400">Type</span>
                  <span className="text-sm text-white capitalize">{selectedWorkflow.type.replace('-', ' ')}</span>
                </div>
                {selectedWorkflow.schedule && (
                  <div className="flex items-center justify-between py-2 border-b border-gray-700">
                    <span className="text-sm text-gray-400">Schedule</span>
                    <span className="text-sm text-white">{selectedWorkflow.schedule}</span>
                  </div>
                )}
                {selectedWorkflow.nextRun && (
                  <div className="flex items-center justify-between py-2 border-b border-gray-700">
                    <span className="text-sm text-gray-400">Next Run</span>
                    <span className="text-sm text-white">{selectedWorkflow.nextRun}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Runs */}
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-3">Recent Runs</h4>
              <div className="space-y-2">
                {[
                  { time: '2024-01-15 08:00', status: 'success', duration: '2m 34s' },
                  { time: '2024-01-14 08:00', status: 'success', duration: '2m 12s' },
                  { time: '2024-01-13 08:00', status: 'failed', duration: '1m 05s' },
                ].map((run, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                    <div className="flex items-center gap-3">
                      {run.status === 'success' ? (
                        <CheckCircle2 className="w-4 h-4 text-green-400" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-400" />
                      )}
                      <span className="text-sm text-gray-300">{run.time}</span>
                    </div>
                    <span className="text-xs text-gray-500">{run.duration}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-3">Quick Actions</h4>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => executeWorkflow(selectedWorkflow.id)}
                  className="flex items-center justify-center gap-2 p-3 bg-emerald-500/20 text-emerald-400 rounded-lg hover:bg-emerald-500/30 transition-colors"
                >
                  <Play className="w-4 h-4" />
                  Run Now
                </button>
                <button className="flex items-center justify-center gap-2 p-3 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors">
                  <Settings className="w-4 h-4" />
                  Edit
                </button>
                <button className="flex items-center justify-center gap-2 p-3 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors">
                  <GitBranch className="w-4 h-4" />
                  Clone
                </button>
                <button className="flex items-center justify-center gap-2 p-3 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors">
                  <BarChart3 className="w-4 h-4" />
                  History
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Workflow Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-2xl w-full max-w-2xl border border-gray-700 shadow-2xl">
            <div className="p-6 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">Create New Workflow</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 text-gray-400 hover:text-white"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>
              <p className="text-sm text-gray-400 mt-2">Choose a template or start from scratch</p>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-2 gap-4">
                {workflowTemplates.map((template, idx) => (
                  <button
                    key={idx}
                    className="flex items-start gap-4 p-4 bg-gray-700/50 rounded-xl border border-gray-600 hover:border-emerald-500/50 hover:bg-gray-700 transition-all text-left group"
                  >
                    <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center group-hover:bg-emerald-500/30 transition-colors">
                      <template.icon className="w-6 h-6 text-emerald-400" />
                    </div>
                    <div>
                      <h3 className="font-medium text-white group-hover:text-emerald-400 transition-colors">
                        {template.name}
                      </h3>
                      <p className="text-sm text-gray-400 mt-1">{template.description}</p>
                    </div>
                  </button>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-gray-700">
                <button className="w-full flex items-center justify-center gap-3 p-4 border-2 border-dashed border-gray-600 rounded-xl text-gray-400 hover:border-emerald-500/50 hover:text-emerald-400 transition-colors">
                  <Plus className="w-5 h-5" />
                  Create Blank Workflow
                </button>
              </div>
            </div>

            <div className="p-6 border-t border-gray-700 bg-gray-800/50 rounded-b-2xl">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-400">
                  Need help? <a href="#" className="text-emerald-400 hover:underline">View documentation</a>
                </p>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
