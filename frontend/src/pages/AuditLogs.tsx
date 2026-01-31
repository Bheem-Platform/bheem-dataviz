/**
 * Audit Logs Page
 *
 * Comprehensive audit logging and security alerts interface.
 */

import { useState, useEffect } from 'react';
import {
  Activity,
  Shield,
  Search,
  Filter,
  Download,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  User,
  Globe,
  Eye,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import {
  AuditLog,
  SecurityAlert,
  AuditLogFilter,
  AlertSeverity,
  AlertStatus,
  ACTION_CATEGORY_LABELS,
  ACTION_TYPE_LABELS,
  ALERT_SEVERITY_LABELS,
  ALERT_STATUS_LABELS,
  formatTimestamp,
  formatRelativeTime,
  formatDuration,
  isHighSeverity,
  isOpenAlert,
} from '../types/audit';

// Mock data
const mockAuditLogs: AuditLog[] = [
  {
    id: '1',
    timestamp: '2026-01-30T10:30:00Z',
    user_id: 'user-1',
    user_email: 'john@example.com',
    user_name: 'John Smith',
    action: 'dashboard.view',
    action_category: 'dashboard',
    action_type: 'view',
    resource_type: 'dashboard',
    resource_id: 'dash-1',
    resource_name: 'Sales Overview',
    ip_address: '192.168.1.100',
    request_method: 'GET',
    request_path: '/api/v1/dashboards/dash-1',
    response_status: 200,
    duration_ms: 145,
    success: 1,
    metadata: {},
  },
  {
    id: '2',
    timestamp: '2026-01-30T10:25:00Z',
    user_id: 'user-2',
    user_email: 'jane@example.com',
    user_name: 'Jane Doe',
    action: 'chart.create',
    action_category: 'chart',
    action_type: 'create',
    resource_type: 'chart',
    resource_id: 'chart-123',
    resource_name: 'Revenue by Region',
    ip_address: '192.168.1.101',
    request_method: 'POST',
    request_path: '/api/v1/charts',
    response_status: 201,
    duration_ms: 320,
    success: 1,
    metadata: {},
  },
  {
    id: '3',
    timestamp: '2026-01-30T10:20:00Z',
    user_id: 'user-3',
    user_email: 'bob@example.com',
    user_name: 'Bob Wilson',
    action: 'auth.login_failed',
    action_category: 'auth',
    action_type: 'login',
    ip_address: '203.0.113.50',
    response_status: 401,
    duration_ms: 50,
    success: 0,
    error_message: 'Invalid credentials',
    metadata: { attempts: 3 },
  },
  {
    id: '4',
    timestamp: '2026-01-30T10:15:00Z',
    user_id: 'user-1',
    user_email: 'john@example.com',
    user_name: 'John Smith',
    action: 'data.export',
    action_category: 'data',
    action_type: 'export',
    resource_type: 'dataset',
    resource_id: 'ds-1',
    resource_name: 'Customer Data',
    ip_address: '192.168.1.100',
    request_method: 'POST',
    request_path: '/api/v1/datasets/ds-1/export',
    response_status: 200,
    duration_ms: 1250,
    success: 1,
    metadata: { format: 'csv', rows: 5000 },
  },
];

const mockAlerts: SecurityAlert[] = [
  {
    id: 'alert-1',
    created_at: '2026-01-30T10:20:00Z',
    alert_type: 'brute_force_attempt',
    severity: 'high',
    title: 'Multiple Failed Login Attempts',
    description: '5 failed login attempts detected from IP 203.0.113.50 within 10 minutes.',
    user_email: 'bob@example.com',
    ip_address: '203.0.113.50',
    related_audit_ids: ['3'],
    status: 'open',
    metadata: { attempts: 5, window_minutes: 10 },
  },
  {
    id: 'alert-2',
    created_at: '2026-01-30T09:00:00Z',
    alert_type: 'unusual_data_access',
    severity: 'medium',
    title: 'Large Data Export',
    description: 'User exported 50,000+ records in a single request.',
    user_id: 'user-5',
    user_email: 'analyst@example.com',
    status: 'investigating',
    metadata: { rows_exported: 52000 },
  },
  {
    id: 'alert-3',
    created_at: '2026-01-29T14:00:00Z',
    alert_type: 'suspicious_login',
    severity: 'low',
    title: 'Login from New Location',
    description: 'First login detected from Germany for user.',
    user_email: 'user@example.com',
    ip_address: '85.214.132.117',
    status: 'resolved',
    resolved_at: '2026-01-29T15:00:00Z',
    resolution_notes: 'Confirmed by user - business travel.',
    metadata: { country: 'Germany' },
  },
];

const severityColors: Record<AlertSeverity, { bg: string; text: string; border: string }> = {
  low: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400', border: 'border-blue-200' },
  medium: { bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-400', border: 'border-amber-200' },
  high: { bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-700 dark:text-orange-400', border: 'border-orange-200' },
  critical: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400', border: 'border-red-200' },
};

const statusColors: Record<AlertStatus, { bg: string; text: string }> = {
  open: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400' },
  investigating: { bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-700 dark:text-amber-400' },
  resolved: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400' },
  dismissed: { bg: 'bg-gray-100 dark:bg-gray-700', text: 'text-gray-700 dark:text-gray-400' },
};

export function AuditLogs() {
  const [activeTab, setActiveTab] = useState<'logs' | 'alerts'>('logs');
  const [logs, setLogs] = useState<AuditLog[]>(mockAuditLogs);
  const [alerts, setAlerts] = useState<SecurityAlert[]>(mockAlerts);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [dateRange, setDateRange] = useState<string>('today');
  const [expandedLog, setExpandedLog] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Summary stats
  const stats = {
    totalEvents: logs.length,
    successfulEvents: logs.filter(l => l.success === 1).length,
    failedEvents: logs.filter(l => l.success === 0).length,
    uniqueUsers: new Set(logs.map(l => l.user_id)).size,
    openAlerts: alerts.filter(a => isOpenAlert(a.status)).length,
    criticalAlerts: alerts.filter(a => a.severity === 'critical' && isOpenAlert(a.status)).length,
  };

  // Filter logs
  const filteredLogs = logs.filter(log => {
    if (searchQuery && !JSON.stringify(log).toLowerCase().includes(searchQuery.toLowerCase())) return false;
    if (selectedCategory !== 'all' && log.action_category !== selectedCategory) return false;
    return true;
  });

  // Filter alerts
  const filteredAlerts = alerts.filter(alert => {
    if (selectedSeverity !== 'all' && alert.severity !== selectedSeverity) return false;
    if (selectedStatus !== 'all' && alert.status !== selectedStatus) return false;
    return true;
  });

  const handleRefresh = async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  const handleExport = () => {
    console.log('Exporting audit logs...');
  };

  const handleResolveAlert = (alertId: string, notes: string) => {
    setAlerts(alerts.map(a =>
      a.id === alertId
        ? { ...a, status: 'resolved' as AlertStatus, resolved_at: new Date().toISOString(), resolution_notes: notes }
        : a
    ));
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Audit Logs
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Security and activity monitoring
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={handleExport}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-6 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm text-gray-500 dark:text-gray-400">Total Events</div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.totalEvents}
              </div>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <div className="text-sm text-green-600 dark:text-green-400">Successful</div>
              <div className="mt-1 text-2xl font-semibold text-green-700 dark:text-green-300">
                {stats.successfulEvents}
              </div>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <div className="text-sm text-red-600 dark:text-red-400">Failed</div>
              <div className="mt-1 text-2xl font-semibold text-red-700 dark:text-red-300">
                {stats.failedEvents}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm text-gray-500 dark:text-gray-400">Active Users</div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.uniqueUsers}
              </div>
            </div>
            <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
              <div className="text-sm text-amber-600 dark:text-amber-400">Open Alerts</div>
              <div className="mt-1 text-2xl font-semibold text-amber-700 dark:text-amber-300">
                {stats.openAlerts}
              </div>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <div className="text-sm text-red-600 dark:text-red-400">Critical</div>
              <div className="mt-1 text-2xl font-semibold text-red-700 dark:text-red-300">
                {stats.criticalAlerts}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('logs')}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeTab === 'logs'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
              >
                <Activity className="w-4 h-4" />
                Activity Logs
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeTab === 'alerts'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
              >
                <Shield className="w-4 h-4" />
                Security Alerts
                {stats.openAlerts > 0 && (
                  <span className="px-2 py-0.5 text-xs bg-red-500 text-white rounded-full">
                    {stats.openAlerts}
                  </span>
                )}
              </button>
            </nav>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder={activeTab === 'logs' ? 'Search logs...' : 'Search alerts...'}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
            </div>
            {activeTab === 'logs' && (
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="all">All Categories</option>
                {Object.entries(ACTION_CATEGORY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            )}
            {activeTab === 'alerts' && (
              <>
                <select
                  value={selectedSeverity}
                  onChange={(e) => setSelectedSeverity(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="all">All Severities</option>
                  {Object.entries(ALERT_SEVERITY_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="all">All Status</option>
                  {Object.entries(ALERT_STATUS_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </>
            )}
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="today">Today</option>
              <option value="week">Last 7 Days</option>
              <option value="month">Last 30 Days</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'logs' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Action
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Resource
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    IP Address
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {filteredLogs.map((log) => (
                  <tr
                    key={log.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                    onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {formatRelativeTime(log.timestamp)}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {formatTimestamp(log.timestamp)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center">
                          <User className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {log.user_name || 'Anonymous'}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {log.user_email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">{log.action}</div>
                      {log.action_category && (
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {ACTION_CATEGORY_LABELS[log.action_category]}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {log.resource_name ? (
                        <div>
                          <div className="text-sm text-gray-900 dark:text-white">{log.resource_name}</div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">{log.resource_type}</div>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {log.success ? (
                        <span className="flex items-center gap-1 text-green-600 dark:text-green-400">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm">Success</span>
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
                          <XCircle className="w-4 h-4" />
                          <span className="text-sm">Failed</span>
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {log.ip_address || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-4">
            {filteredAlerts.map((alert) => {
              const sevColors = severityColors[alert.severity];
              const statColors = statusColors[alert.status];

              return (
                <div
                  key={alert.id}
                  className={`bg-white dark:bg-gray-800 rounded-lg shadow border-l-4 ${sevColors.border} p-6`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`p-2 rounded-lg ${sevColors.bg}`}>
                        <AlertTriangle className={`w-5 h-5 ${sevColors.text}`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${sevColors.bg} ${sevColors.text}`}>
                            {ALERT_SEVERITY_LABELS[alert.severity]}
                          </span>
                          <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${statColors.bg} ${statColors.text}`}>
                            {ALERT_STATUS_LABELS[alert.status]}
                          </span>
                          <span className="text-xs text-gray-400">
                            {formatRelativeTime(alert.created_at)}
                          </span>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                          {alert.title}
                        </h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                          {alert.description}
                        </p>
                        <div className="mt-3 flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                          {alert.user_email && (
                            <span className="flex items-center gap-1">
                              <User className="w-4 h-4" />
                              {alert.user_email}
                            </span>
                          )}
                          {alert.ip_address && (
                            <span className="flex items-center gap-1">
                              <Globe className="w-4 h-4" />
                              {alert.ip_address}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    {isOpenAlert(alert.status) && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleResolveAlert(alert.id, 'Resolved')}
                          className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700"
                        >
                          Resolve
                        </button>
                        <button className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700">
                          Investigate
                        </button>
                      </div>
                    )}
                  </div>
                  {alert.resolution_notes && (
                    <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-xs text-green-600 dark:text-green-400 font-medium mb-1">
                        Resolution Notes
                      </div>
                      <p className="text-sm text-green-700 dark:text-green-300">
                        {alert.resolution_notes}
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
            {filteredAlerts.length === 0 && (
              <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  No alerts found
                </h3>
                <p className="mt-1 text-gray-500 dark:text-gray-400">
                  All clear! No security alerts match your filters.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AuditLogs;
