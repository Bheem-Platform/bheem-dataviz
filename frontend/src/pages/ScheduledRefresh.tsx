/**
 * Scheduled Refresh & Alerts Page
 *
 * Management interface for data refresh schedules and alert rules.
 */

import { useState, useEffect } from 'react';
import {
  RefreshSchedule,
  AlertRule,
  ScheduleExecution,
  AlertExecution,
  ScheduleSummary,
  AlertSummary,
  ScheduleFrequency,
  AlertSeverity,
  FREQUENCY_OPTIONS,
  SEVERITY_OPTIONS,
  NOTIFICATION_CHANNEL_OPTIONS,
  createDefaultSchedule,
  createDefaultAlert,
  formatScheduleFrequency,
} from '../types/schedule';

// Mock API functions - replace with actual API calls
const mockSchedules: RefreshSchedule[] = [
  {
    id: '1',
    name: 'Daily Sales Refresh',
    description: 'Refresh sales data every morning',
    enabled: true,
    status: 'active',
    targetType: 'connection',
    targetId: 'conn-1',
    refreshType: 'full',
    schedule: {
      frequency: 'daily',
      time: { hour: 6, minute: 0, timezone: 'UTC' },
      maxRetries: 3,
      retryDelayMinutes: 5,
    },
    notifyOnSuccess: false,
    notifyOnFailure: true,
    notificationRecipients: ['admin@example.com'],
    lastRunAt: '2026-01-30T06:00:00Z',
    lastRunStatus: 'success',
    nextRunAt: '2026-01-31T06:00:00Z',
  },
];

const mockAlerts: AlertRule[] = [
  {
    id: '1',
    name: 'Low Sales Alert',
    description: 'Alert when daily sales fall below threshold',
    enabled: true,
    severity: 'warning',
    targetType: 'dashboard',
    targetId: 'dash-1',
    conditions: [
      {
        id: 'cond-1',
        measure: 'total_sales',
        operator: 'less_than',
        threshold: 10000,
      },
    ],
    conditionLogic: 'AND',
    evaluationSchedule: {
      frequency: 'hourly',
      maxRetries: 3,
      retryDelayMinutes: 5,
    },
    notificationChannels: ['email', 'in_app'],
    notificationRecipients: ['sales@example.com'],
    minIntervalMinutes: 60,
    triggerCount: 3,
    lastTriggeredAt: '2026-01-29T14:00:00Z',
  },
];

export function ScheduledRefresh() {
  const [activeTab, setActiveTab] = useState<'schedules' | 'alerts' | 'history'>('schedules');
  const [schedules, setSchedules] = useState<RefreshSchedule[]>(mockSchedules);
  const [alerts, setAlerts] = useState<AlertRule[]>(mockAlerts);
  const [executions, setExecutions] = useState<ScheduleExecution[]>([]);
  const [alertExecutions, setAlertExecutions] = useState<AlertExecution[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Editor modal state
  const [showScheduleEditor, setShowScheduleEditor] = useState(false);
  const [showAlertEditor, setShowAlertEditor] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<RefreshSchedule | null>(null);
  const [editingAlert, setEditingAlert] = useState<AlertRule | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ type: 'schedule' | 'alert'; id: string } | null>(null);

  // Summary stats
  const scheduleSummary: ScheduleSummary = {
    totalSchedules: schedules.length,
    activeSchedules: schedules.filter(s => s.enabled && s.status === 'active').length,
    pausedSchedules: schedules.filter(s => !s.enabled).length,
    failedSchedules: schedules.filter(s => s.status === 'error').length,
    executionsToday: 12,
    successfulToday: 10,
    failedToday: 2,
  };

  const alertSummary: AlertSummary = {
    totalAlerts: alerts.length,
    activeAlerts: alerts.filter(a => a.enabled).length,
    triggeredToday: 5,
    criticalActive: alerts.filter(a => a.severity === 'critical' && a.enabled).length,
    warningActive: alerts.filter(a => a.severity === 'warning' && a.enabled).length,
  };

  // Filter schedules/alerts
  const filteredSchedules = schedules.filter(s => {
    const matchesSearch = s.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || s.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const filteredAlerts = alerts.filter(a => {
    const matchesSearch = a.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' ||
      (statusFilter === 'active' && a.enabled) ||
      (statusFilter === 'paused' && !a.enabled);
    return matchesSearch && matchesStatus;
  });

  // Handlers
  const handleCreateSchedule = () => {
    setEditingSchedule(createDefaultSchedule('connection', ''));
    setShowScheduleEditor(true);
  };

  const handleEditSchedule = (schedule: RefreshSchedule) => {
    setEditingSchedule({ ...schedule });
    setShowScheduleEditor(true);
  };

  const handleSaveSchedule = (schedule: RefreshSchedule) => {
    if (schedules.find(s => s.id === schedule.id)) {
      setSchedules(schedules.map(s => s.id === schedule.id ? schedule : s));
    } else {
      setSchedules([...schedules, { ...schedule, id: `schedule_${Date.now()}` }]);
    }
    setShowScheduleEditor(false);
    setEditingSchedule(null);
  };

  const handleDeleteSchedule = (id: string) => {
    setDeleteTarget({ type: 'schedule', id });
    setShowDeleteConfirm(true);
  };

  const handleToggleSchedule = (id: string) => {
    setSchedules(schedules.map(s =>
      s.id === id ? { ...s, enabled: !s.enabled } : s
    ));
  };

  const handleRunNow = (id: string) => {
    console.log('Running schedule:', id);
    // API call to trigger immediate execution
  };

  const handleCreateAlert = () => {
    setEditingAlert(createDefaultAlert('dashboard', ''));
    setShowAlertEditor(true);
  };

  const handleEditAlert = (alert: AlertRule) => {
    setEditingAlert({ ...alert });
    setShowAlertEditor(true);
  };

  const handleSaveAlert = (alert: AlertRule) => {
    if (alerts.find(a => a.id === alert.id)) {
      setAlerts(alerts.map(a => a.id === alert.id ? alert : a));
    } else {
      setAlerts([...alerts, { ...alert, id: `alert_${Date.now()}` }]);
    }
    setShowAlertEditor(false);
    setEditingAlert(null);
  };

  const handleDeleteAlert = (id: string) => {
    setDeleteTarget({ type: 'alert', id });
    setShowDeleteConfirm(true);
  };

  const handleToggleAlert = (id: string) => {
    setAlerts(alerts.map(a =>
      a.id === id ? { ...a, enabled: !a.enabled } : a
    ));
  };

  const confirmDelete = () => {
    if (deleteTarget) {
      if (deleteTarget.type === 'schedule') {
        setSchedules(schedules.filter(s => s.id !== deleteTarget.id));
      } else {
        setAlerts(alerts.filter(a => a.id !== deleteTarget.id));
      }
    }
    setShowDeleteConfirm(false);
    setDeleteTarget(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Scheduled Refresh & Alerts
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Manage data refresh schedules and alert notifications
              </p>
            </div>
            <div className="flex gap-3">
              {activeTab === 'schedules' && (
                <button
                  onClick={handleCreateSchedule}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  New Schedule
                </button>
              )}
              {activeTab === 'alerts' && (
                <button
                  onClick={handleCreateAlert}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  New Alert
                </button>
              )}
            </div>
          </div>

          {/* Summary Cards */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Schedules</div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {scheduleSummary.activeSchedules}/{scheduleSummary.totalSchedules}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Executions Today</div>
              <div className="mt-1 text-2xl font-semibold text-green-600">
                {scheduleSummary.successfulToday}
                <span className="text-sm text-gray-500 ml-1">successful</span>
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Alerts</div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {alertSummary.activeAlerts}/{alertSummary.totalAlerts}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Triggered Today</div>
              <div className="mt-1 text-2xl font-semibold text-amber-600">
                {alertSummary.triggeredToday}
                <span className="text-sm text-gray-500 ml-1">alerts</span>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('schedules')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'schedules'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
              >
                Refresh Schedules
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'alerts'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
              >
                Alert Rules
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'history'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
                }`}
              >
                Execution History
              </button>
            </nav>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <input
              type="text"
              placeholder={`Search ${activeTab === 'schedules' ? 'schedules' : activeTab === 'alerts' ? 'alerts' : 'executions'}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="error">Error</option>
          </select>
        </div>

        {/* Schedules Tab */}
        {activeTab === 'schedules' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Schedule
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Frequency
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Last Run
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Next Run
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {filteredSchedules.map((schedule) => (
                  <tr key={schedule.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {schedule.name}
                          </div>
                          {schedule.description && (
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {schedule.description}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatScheduleFrequency(schedule.schedule)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {schedule.lastRunAt ? new Date(schedule.lastRunAt).toLocaleString() : 'Never'}
                      </div>
                      {schedule.lastRunStatus && (
                        <div className={`text-xs ${
                          schedule.lastRunStatus === 'success' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {schedule.lastRunStatus}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {schedule.nextRunAt ? new Date(schedule.nextRunAt).toLocaleString() : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        schedule.enabled && schedule.status === 'active'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                          : schedule.status === 'error'
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {schedule.enabled ? schedule.status : 'paused'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleRunNow(schedule.id)}
                          className="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                          title="Run Now"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleToggleSchedule(schedule.id)}
                          className={`${schedule.enabled ? 'text-amber-600' : 'text-green-600'} hover:opacity-75`}
                          title={schedule.enabled ? 'Pause' : 'Resume'}
                        >
                          {schedule.enabled ? (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          ) : (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          )}
                        </button>
                        <button
                          onClick={() => handleEditSchedule(schedule)}
                          className="text-gray-600 hover:text-gray-900 dark:text-gray-400"
                          title="Edit"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDeleteSchedule(schedule.id)}
                          className="text-red-600 hover:text-red-900 dark:text-red-400"
                          title="Delete"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredSchedules.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                      No schedules found. Create one to get started.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Alert
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Severity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Conditions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Last Triggered
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {filteredAlerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {alert.name}
                          </div>
                          {alert.description && (
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {alert.description}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        alert.severity === 'critical'
                          ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'
                          : alert.severity === 'error'
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                          : alert.severity === 'warning'
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300'
                          : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                      }`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {alert.conditions.length} condition{alert.conditions.length !== 1 ? 's' : ''}
                      <span className="ml-1 text-gray-400">({alert.conditionLogic})</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {alert.lastTriggeredAt ? new Date(alert.lastTriggeredAt).toLocaleString() : 'Never'}
                      </div>
                      {alert.triggerCount > 0 && (
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {alert.triggerCount} total triggers
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        alert.enabled
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {alert.enabled ? 'active' : 'paused'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleToggleAlert(alert.id)}
                          className={`${alert.enabled ? 'text-amber-600' : 'text-green-600'} hover:opacity-75`}
                          title={alert.enabled ? 'Pause' : 'Resume'}
                        >
                          {alert.enabled ? (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          ) : (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          )}
                        </button>
                        <button
                          onClick={() => handleEditAlert(alert)}
                          className="text-gray-600 hover:text-gray-900 dark:text-gray-400"
                          title="Edit"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDeleteAlert(alert.id)}
                          className="text-red-600 hover:text-red-900 dark:text-red-400"
                          title="Delete"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredAlerts.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                      No alerts found. Create one to get started.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="text-center text-gray-500 dark:text-gray-400 py-12">
              Execution history will appear here once schedules and alerts have been run.
            </div>
          </div>
        )}
      </div>

      {/* Schedule Editor Modal */}
      {showScheduleEditor && editingSchedule && (
        <ScheduleEditorModal
          schedule={editingSchedule}
          onSave={handleSaveSchedule}
          onClose={() => {
            setShowScheduleEditor(false);
            setEditingSchedule(null);
          }}
        />
      )}

      {/* Alert Editor Modal */}
      {showAlertEditor && editingAlert && (
        <AlertEditorModal
          alert={editingAlert}
          onSave={handleSaveAlert}
          onClose={() => {
            setShowAlertEditor(false);
            setEditingAlert(null);
          }}
        />
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Confirm Delete
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Are you sure you want to delete this {deleteTarget?.type}? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Schedule Editor Modal Component
interface ScheduleEditorModalProps {
  schedule: RefreshSchedule;
  onSave: (schedule: RefreshSchedule) => void;
  onClose: () => void;
}

function ScheduleEditorModal({ schedule, onSave, onClose }: ScheduleEditorModalProps) {
  const [formData, setFormData] = useState<RefreshSchedule>(schedule);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            {schedule.id.startsWith('schedule_') ? 'Create Schedule' : 'Edit Schedule'}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              rows={2}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Frequency
              </label>
              <select
                value={formData.schedule.frequency}
                onChange={(e) => setFormData({
                  ...formData,
                  schedule: { ...formData.schedule, frequency: e.target.value as ScheduleFrequency }
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                {FREQUENCY_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Refresh Type
              </label>
              <select
                value={formData.refreshType}
                onChange={(e) => setFormData({ ...formData, refreshType: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="full">Full Refresh</option>
                <option value="incremental">Incremental</option>
                <option value="partition">Partition</option>
              </select>
            </div>
          </div>

          {formData.schedule.frequency !== 'once' && formData.schedule.frequency !== 'hourly' && (
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Hour (0-23)
                </label>
                <input
                  type="number"
                  min={0}
                  max={23}
                  value={formData.schedule.time?.hour || 0}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule: {
                      ...formData.schedule,
                      time: { ...formData.schedule.time!, hour: parseInt(e.target.value) }
                    }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Minute (0-59)
                </label>
                <input
                  type="number"
                  min={0}
                  max={59}
                  value={formData.schedule.time?.minute || 0}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule: {
                      ...formData.schedule,
                      time: { ...formData.schedule.time!, minute: parseInt(e.target.value) }
                    }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Timezone
                </label>
                <input
                  type="text"
                  value={formData.schedule.time?.timezone || 'UTC'}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule: {
                      ...formData.schedule,
                      time: { ...formData.schedule.time!, timezone: e.target.value }
                    }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
            </div>
          )}

          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Notifications</h4>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.notifyOnSuccess}
                  onChange={(e) => setFormData({ ...formData, notifyOnSuccess: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Notify on success</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.notifyOnFailure}
                  onChange={(e) => setFormData({ ...formData, notifyOnFailure: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Notify on failure</span>
              </label>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Save Schedule
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Alert Editor Modal Component
interface AlertEditorModalProps {
  alert: AlertRule;
  onSave: (alert: AlertRule) => void;
  onClose: () => void;
}

function AlertEditorModal({ alert, onSave, onClose }: AlertEditorModalProps) {
  const [formData, setFormData] = useState<AlertRule>(alert);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            {alert.id.startsWith('alert_') ? 'Create Alert' : 'Edit Alert'}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              rows={2}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Severity
              </label>
              <select
                value={formData.severity}
                onChange={(e) => setFormData({ ...formData, severity: e.target.value as AlertSeverity })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                {SEVERITY_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Condition Logic
              </label>
              <select
                value={formData.conditionLogic}
                onChange={(e) => setFormData({ ...formData, conditionLogic: e.target.value as 'AND' | 'OR' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="AND">All conditions (AND)</option>
                <option value="OR">Any condition (OR)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Evaluation Frequency
            </label>
            <select
              value={formData.evaluationSchedule.frequency}
              onChange={(e) => setFormData({
                ...formData,
                evaluationSchedule: { ...formData.evaluationSchedule, frequency: e.target.value as ScheduleFrequency }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              {FREQUENCY_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notification Channels
            </label>
            <div className="flex flex-wrap gap-2">
              {NOTIFICATION_CHANNEL_OPTIONS.map(opt => (
                <label key={opt.value} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.notificationChannels.includes(opt.value as any)}
                    onChange={(e) => {
                      const channels = e.target.checked
                        ? [...formData.notificationChannels, opt.value as any]
                        : formData.notificationChannels.filter(c => c !== opt.value);
                      setFormData({ ...formData, notificationChannels: channels });
                    }}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">{opt.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Minimum Interval (minutes)
            </label>
            <input
              type="number"
              min={1}
              value={formData.minIntervalMinutes}
              onChange={(e) => setFormData({ ...formData, minIntervalMinutes: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <p className="mt-1 text-sm text-gray-500">Don't trigger this alert more than once per interval</p>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Save Alert
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ScheduledRefresh;
