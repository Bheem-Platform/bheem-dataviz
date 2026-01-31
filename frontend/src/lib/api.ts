import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_BASE = '/api/v1'

// Token storage key - standardized to 'access_token'
const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Flag to prevent multiple simultaneous refresh attempts
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: any) => void
}> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token!)
    }
  })
  failedQueue = []
}

// Request interceptor for auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling with token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Don't retry for auth endpoints
      if (originalRequest.url?.includes('/auth/')) {
        return Promise.reject(error)
      }

      if (isRefreshing) {
        // Wait for the refresh to complete
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        }).catch((err) => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

      if (!refreshToken) {
        // No refresh token - redirect to login
        isRefreshing = false
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        // Attempt to refresh the token
        const response = await axios.post(`${API_BASE}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token: newRefreshToken } = response.data

        // Store new tokens
        localStorage.setItem(TOKEN_KEY, access_token)
        localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken)

        // Update the authorization header
        originalRequest.headers.Authorization = `Bearer ${access_token}`

        // Process queued requests
        processQueue(null, access_token)
        isRefreshing = false

        // Retry the original request
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed - clear tokens and redirect to login
        processQueue(refreshError, null)
        isRefreshing = false
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Connections API
export const connectionsApi = {
  list: () => api.get('/connections/'),
  get: (id: string) => api.get(`/connections/${id}`),
  create: (data: any) => api.post('/connections/', data),
  update: (id: string, data: any) => api.put(`/connections/${id}`, data),
  delete: (id: string) => api.delete(`/connections/${id}`),
  test: (id: string) => api.post(`/connections/${id}/test`),
  sync: (id: string) => api.post(`/connections/${id}/sync`),
}

// Dashboards API
export const dashboardsApi = {
  list: () => api.get('/dashboards/'),
  get: (id: string) => api.get(`/dashboards/${id}`),
  create: (data: any) => api.post('/dashboards/', data),
  update: (id: string, data: any) => api.put(`/dashboards/${id}`, data),
  delete: (id: string) => api.delete(`/dashboards/${id}`),
  duplicate: (id: string) => api.post(`/dashboards/${id}/duplicate`),
  publish: (id: string) => api.post(`/dashboards/${id}/publish`),
  getTemplates: () => api.get('/dashboards/templates'),
}

// Datasets API
export const datasetsApi = {
  list: () => api.get('/datasets/'),
  get: (id: string) => api.get(`/datasets/${id}`),
  create: (data: any) => api.post('/datasets/', data),
  update: (id: string, data: any) => api.put(`/datasets/${id}`, data),
  delete: (id: string) => api.delete(`/datasets/${id}`),
  preview: (id: string, params?: any) => api.get(`/datasets/${id}/preview`, { params }),
  addMeasure: (id: string, data: any) => api.post(`/datasets/${id}/measures`, data),
  addRelationship: (id: string, data: any) => api.post(`/datasets/${id}/relationships`, data),
}

// Charts API
export const chartsApi = {
  list: () => api.get('/charts'),
  get: (id: string) => api.get(`/charts/${id}`),
  create: (data: any) => api.post('/charts', data),
  update: (id: string, data: any) => api.put(`/charts/${id}`, data),
  delete: (id: string) => api.delete(`/charts/${id}`),
  render: (id: string) => api.get(`/charts/${id}/render`),
  export: (id: string, format: string) =>
    api.get(`/charts/${id}/export`, { params: { format }, responseType: 'blob' }),
}

// Queries API
export const queriesApi = {
  execute: (data: any) => api.post('/queries/execute', data),
  preview: (data: any) => api.post('/queries/preview', data),
  listSaved: () => api.get('/queries/saved'),
  getSaved: (id: string) => api.get(`/queries/saved/${id}`),
  save: (data: any) => api.post('/queries/saved', data),
  deleteSaved: (id: string) => api.delete(`/queries/saved/${id}`),
}

// AI API
export const aiApi = {
  nlQuery: (data: any) => api.post('/ai/nl-query', data),
  getInsights: (datasetId: string) => api.post('/ai/insights', { dataset_id: datasetId }),
  chat: (data: any) => api.post('/ai/chat', data),
  suggest: (chartId: string) => api.post('/ai/suggest', { chart_id: chartId }),
}

// KPI API
export const kpiApi = {
  calculate: (data: any) => api.post('/kpi/calculate', data),
  batch: (requests: any[]) => api.post('/kpi/batch', requests),
}

// Filters API
export const filtersApi = {
  // Get filter options for a single column
  getColumnOptions: (connectionId: string, schema: string, table: string, column: string) =>
    api.get(`/filters/options/${connectionId}/${schema}/${table}/${column}`),

  // Get filter options for multiple columns
  getMultipleColumnOptions: (connectionId: string, schema: string, table: string, columns: string[]) =>
    api.post(`/filters/options/${connectionId}/${schema}/${table}`, columns),

  // Get filter options for a chart's columns
  getChartOptions: (chartId: string, columns?: string[]) =>
    api.get(`/filters/options/chart/${chartId}`, { params: columns ? { columns: columns.join(',') } : {} }),

  // Saved filter presets
  listPresets: (dashboardId: string) =>
    api.get(`/filters/presets/${dashboardId}`),

  getPreset: (presetId: string) =>
    api.get(`/filters/presets/preset/${presetId}`),

  createPreset: (dashboardId: string, data: { name: string; description?: string; filter_state: any }) =>
    api.post(`/filters/presets/${dashboardId}`, data),

  updatePreset: (presetId: string, data: { name?: string; description?: string; filter_state?: any }) =>
    api.put(`/filters/presets/preset/${presetId}`, data),

  deletePreset: (presetId: string) =>
    api.delete(`/filters/presets/preset/${presetId}`),

  // Dashboard filter state
  getFilterState: (dashboardId: string) =>
    api.get(`/filters/state/${dashboardId}`),

  saveFilterState: (dashboardId: string, filterState: any) =>
    api.post(`/filters/state/${dashboardId}`, filterState),

  clearFilterState: (dashboardId: string) =>
    api.delete(`/filters/state/${dashboardId}`),

  // Slicer configuration
  getSlicerConfig: (dashboardId: string) =>
    api.get(`/filters/slicers/${dashboardId}`),

  updateSlicerConfig: (dashboardId: string, slicers: any[]) =>
    api.put(`/filters/slicers/${dashboardId}`, slicers),

  // Get hierarchy values for drill-down slicers
  getHierarchyValues: (connectionId: string, schema: string, table: string, levels: string[], parentValues?: Record<string, string>) =>
    api.post(`/filters/hierarchy/${connectionId}/${schema}/${table}`, { levels, parent_values: parentValues }),
}

// Drill API
export const drillApi = {
  // Execute drill operation
  executeDrill: (data: {
    chart_id: string;
    hierarchy_id: string;
    direction: 'up' | 'down';
    clicked_value?: any;
    current_path?: any;
  }) => api.post('/drill/execute', data),

  // Execute drillthrough
  executeDrillthrough: (data: {
    source_chart_id: string;
    target_id: string;
    clicked_data: Record<string, any>;
    current_filters?: Record<string, any>;
  }) => api.post('/drill/drillthrough', data),

  // Get chart drill config
  getChartConfig: (chartId: string) =>
    api.get(`/drill/config/${chartId}`),

  // Update chart drill config
  updateChartConfig: (chartId: string, config: any) =>
    api.put(`/drill/config/${chartId}`, config),

  // Get hierarchy templates
  getHierarchyTemplates: () =>
    api.get('/drill/hierarchies/templates'),

  // Create custom hierarchy
  createHierarchy: (hierarchyId: string, hierarchyName: string, columns: any[]) =>
    api.post('/drill/hierarchies/create', columns, {
      params: { hierarchy_id: hierarchyId, hierarchy_name: hierarchyName },
    }),

  // Get drill breadcrumbs
  getBreadcrumbs: (chartId: string, hierarchyId: string, drillPath?: string) =>
    api.get(`/drill/breadcrumbs/${chartId}`, {
      params: { hierarchy_id: hierarchyId, drill_path: drillPath },
    }),

  // Get dashboard drill state
  getDashboardState: (dashboardId: string) =>
    api.get(`/drill/state/dashboard/${dashboardId}`),

  // Save dashboard drill state
  saveDashboardState: (dashboardId: string, state: any) =>
    api.put(`/drill/state/dashboard/${dashboardId}`, state),

  // Clear dashboard drill state
  clearDashboardState: (dashboardId: string) =>
    api.delete(`/drill/state/dashboard/${dashboardId}`),
}

// Conditional Format API
export const conditionalFormatApi = {
  // Get chart formats
  getChartFormats: (chartId: string) =>
    api.get(`/conditional-format/chart/${chartId}`),

  // Update all chart formats
  updateChartFormats: (chartId: string, formats: any) =>
    api.put(`/conditional-format/chart/${chartId}`, formats),

  // Add a format
  addFormat: (chartId: string, format: any) =>
    api.post(`/conditional-format/chart/${chartId}/format`, format),

  // Update a format
  updateFormat: (chartId: string, formatId: string, format: any) =>
    api.put(`/conditional-format/chart/${chartId}/format/${formatId}`, format),

  // Delete a format
  deleteFormat: (chartId: string, formatId: string) =>
    api.delete(`/conditional-format/chart/${chartId}/format/${formatId}`),

  // Evaluate formats on data
  evaluate: (data: any[], formats: any[]) =>
    api.post('/conditional-format/evaluate', { data, formats }),

  // Evaluate chart formats
  evaluateChart: (chartId: string, data: any[]) =>
    api.post(`/conditional-format/evaluate/chart/${chartId}`, data),

  // Get format templates
  getTemplates: () =>
    api.get('/conditional-format/templates'),

  // Get icon sets
  getIconSets: () =>
    api.get('/conditional-format/icon-sets'),

  // Preview format
  preview: (sampleData: any[], format: any) =>
    api.post('/conditional-format/preview', { sample_data: sampleData, format }),

  // Reorder formats
  reorderFormats: (chartId: string, formatIds: string[]) =>
    api.put(`/conditional-format/chart/${chartId}/reorder`, formatIds),

  // Toggle format enabled
  toggleFormat: (chartId: string, formatId: string, enabled: boolean) =>
    api.put(`/conditional-format/chart/${chartId}/format/${formatId}/toggle`, null, {
      params: { enabled },
    }),
}

// Time Intelligence API
export const timeIntelligenceApi = {
  // Calculate time intelligence
  calculate: (request: any) =>
    api.post('/time-intelligence/calculate', request),

  // Generate SQL only
  generateSql: (request: any) =>
    api.post('/time-intelligence/generate-sql', request),

  // Get templates
  getTemplates: () =>
    api.get('/time-intelligence/templates'),

  // Generate date table SQL
  generateDateTable: (config: any) =>
    api.post('/time-intelligence/date-table/generate', config),

  // Get date table columns
  getDateTableColumns: (includeFiscal?: boolean) =>
    api.get('/time-intelligence/date-table/columns', {
      params: { include_fiscal: includeFiscal },
    }),

  // Preview function
  preview: (func: any, schemaName: string, tableName: string, referenceDate?: string) =>
    api.post('/time-intelligence/preview', func, {
      params: { schema_name: schemaName, table_name: tableName, reference_date: referenceDate },
    }),

  // Get period types
  getPeriodTypes: () =>
    api.get('/time-intelligence/period-types'),

  // Get aggregation types
  getAggregationTypes: () =>
    api.get('/time-intelligence/aggregation-types'),

  // Get granularities
  getGranularities: () =>
    api.get('/time-intelligence/granularities'),
}

// Row-Level Security API
export const rlsApi = {
  // Roles
  listRoles: () =>
    api.get('/rls/roles'),

  createRole: (role: any) =>
    api.post('/rls/roles', role),

  getRole: (roleId: string) =>
    api.get(`/rls/roles/${roleId}`),

  updateRole: (roleId: string, role: any) =>
    api.put(`/rls/roles/${roleId}`, role),

  deleteRole: (roleId: string) =>
    api.delete(`/rls/roles/${roleId}`),

  // Policies
  listPolicies: (params?: { table_name?: string; schema_name?: string; connection_id?: string }) =>
    api.get('/rls/policies', { params }),

  createPolicy: (policy: any) =>
    api.post('/rls/policies', policy),

  getPolicy: (policyId: string) =>
    api.get(`/rls/policies/${policyId}`),

  updatePolicy: (policyId: string, policy: any) =>
    api.put(`/rls/policies/${policyId}`, policy),

  deletePolicy: (policyId: string) =>
    api.delete(`/rls/policies/${policyId}`),

  togglePolicy: (policyId: string, enabled: boolean) =>
    api.put(`/rls/policies/${policyId}/toggle`, null, { params: { enabled } }),

  // User Role Mappings
  getUserRoles: (userId: string) =>
    api.get(`/rls/user-roles/${userId}`),

  setUserRoles: (userId: string, mapping: any) =>
    api.put(`/rls/user-roles/${userId}`, mapping),

  // Object Permissions
  getObjectPermissions: (objectType: string, objectId: string) =>
    api.get(`/rls/permissions/${objectType}/${objectId}`),

  setObjectPermissions: (objectType: string, objectId: string, permissions: any[]) =>
    api.put(`/rls/permissions/${objectType}/${objectId}`, permissions),

  // Evaluation
  evaluate: (request: any) =>
    api.post('/rls/evaluate', request),

  testPolicy: (policy: any, testUser: any, tableName: string, schemaName?: string) =>
    api.post('/rls/test', { policy, test_user: testUser, table_name: tableName, schema_name: schemaName }),

  // Configuration
  getConfig: () =>
    api.get('/rls/config'),

  updateConfig: (config: any) =>
    api.put('/rls/config', config),

  // Templates
  getTemplates: () =>
    api.get('/rls/templates'),

  applyTemplate: (templateId: string, tableName: string, schemaName?: string, roleIds?: string[]) =>
    api.post(`/rls/templates/${templateId}/apply`, null, {
      params: { table_name: tableName, schema_name: schemaName, role_ids: roleIds },
    }),
}

// Schedule and Alerts API
export const scheduleApi = {
  // Schedules
  listSchedules: (params?: { target_type?: string; target_id?: string; status?: string }) =>
    api.get('/schedule/schedules', { params }),

  createSchedule: (schedule: any) =>
    api.post('/schedule/schedules', schedule),

  getSchedule: (scheduleId: string) =>
    api.get(`/schedule/schedules/${scheduleId}`),

  updateSchedule: (scheduleId: string, schedule: any) =>
    api.put(`/schedule/schedules/${scheduleId}`, schedule),

  deleteSchedule: (scheduleId: string) =>
    api.delete(`/schedule/schedules/${scheduleId}`),

  pauseSchedule: (scheduleId: string) =>
    api.post(`/schedule/schedules/${scheduleId}/pause`),

  resumeSchedule: (scheduleId: string) =>
    api.post(`/schedule/schedules/${scheduleId}/resume`),

  runScheduleNow: (scheduleId: string) =>
    api.post(`/schedule/schedules/${scheduleId}/run`),

  getScheduleHistory: (scheduleId: string, limit?: number) =>
    api.get(`/schedule/schedules/${scheduleId}/history`, { params: { limit } }),

  // Alerts
  listAlerts: (params?: { target_type?: string; target_id?: string; severity?: string }) =>
    api.get('/schedule/alerts', { params }),

  createAlert: (alert: any) =>
    api.post('/schedule/alerts', alert),

  getAlert: (alertId: string) =>
    api.get(`/schedule/alerts/${alertId}`),

  updateAlert: (alertId: string, alert: any) =>
    api.put(`/schedule/alerts/${alertId}`, alert),

  deleteAlert: (alertId: string) =>
    api.delete(`/schedule/alerts/${alertId}`),

  toggleAlert: (alertId: string, enabled: boolean) =>
    api.put(`/schedule/alerts/${alertId}/toggle`, null, { params: { enabled } }),

  snoozeAlert: (alertId: string, hours: number) =>
    api.post(`/schedule/alerts/${alertId}/snooze`, null, { params: { hours } }),

  evaluateAlert: (alertId: string, values: Record<string, number>, previousValues?: Record<string, number>) =>
    api.post(`/schedule/alerts/${alertId}/evaluate`, { values, previous_values: previousValues }),

  getAlertHistory: (alertId: string, triggeredOnly?: boolean, limit?: number) =>
    api.get(`/schedule/alerts/${alertId}/history`, { params: { triggered_only: triggeredOnly, limit } }),

  // Summaries
  getScheduleSummary: () =>
    api.get('/schedule/summary/schedules'),

  getAlertSummary: () =>
    api.get('/schedule/summary/alerts'),

  // Templates
  getScheduleTemplates: () =>
    api.get('/schedule/templates/schedules'),

  getAlertTemplates: () =>
    api.get('/schedule/templates/alerts'),

  // All execution history
  getAllScheduleExecutions: (limit?: number) =>
    api.get('/schedule/history/executions', { params: { limit } }),

  getAllAlertExecutions: (triggeredOnly?: boolean, limit?: number) =>
    api.get('/schedule/history/alerts', { params: { triggered_only: triggeredOnly, limit } }),
}

// Quick Charts API
export const quickChartsApi = {
  getTables: (connectionId: string) => api.get(`/quickcharts/tables/${connectionId}`),
  getSuggestions: (connectionId: string, schema: string, table: string, maxSuggestions?: number) =>
    api.get(`/quickcharts/suggestions/${connectionId}/${schema}/${table}`, {
      params: { max_suggestions: maxSuggestions || 5 }
    }),
  createChart: (data: any) => api.post('/quickcharts/create-chart', data),
  getHomeSuggestions: (limit?: number) => api.get('/quickcharts/home-suggestions', {
    params: { limit: limit || 3 }
  }),
  analyzeConnection: (connectionId: string) => api.get(`/quickcharts/connection/${connectionId}/analyze`),
}

// Workspaces API
export const workspacesApi = {
  // Workspace CRUD
  list: () =>
    api.get('/workspaces/'),

  create: (data: {
    name: string;
    description?: string;
    slug?: string;
    logo_url?: string;
    primary_color?: string;
    settings?: Record<string, unknown>;
  }) => api.post('/workspaces/', data),

  get: (workspaceId: string) =>
    api.get(`/workspaces/${workspaceId}`),

  getPersonal: () =>
    api.get('/workspaces/personal'),

  update: (workspaceId: string, data: {
    name?: string;
    description?: string;
    logo_url?: string;
    primary_color?: string;
    settings?: Record<string, unknown>;
    is_default?: boolean;
  }) => api.put(`/workspaces/${workspaceId}`, data),

  delete: (workspaceId: string) =>
    api.delete(`/workspaces/${workspaceId}`),

  transferOwnership: (workspaceId: string, newOwnerId: string) =>
    api.post(`/workspaces/${workspaceId}/transfer-ownership`, { new_owner_id: newOwnerId }),

  // Members
  listMembers: (workspaceId: string, includeInactive?: boolean) =>
    api.get(`/workspaces/${workspaceId}/members`, {
      params: { include_inactive: includeInactive },
    }),

  addMember: (workspaceId: string, data: { user_id: string; role?: string }) =>
    api.post(`/workspaces/${workspaceId}/members`, data),

  updateMember: (workspaceId: string, userId: string, data: {
    role?: string;
    custom_permissions?: Record<string, boolean>;
    is_active?: boolean;
  }) => api.put(`/workspaces/${workspaceId}/members/${userId}`, data),

  removeMember: (workspaceId: string, userId: string) =>
    api.delete(`/workspaces/${workspaceId}/members/${userId}`),

  // Invitations
  listInvitations: (workspaceId: string, status?: string) =>
    api.get(`/workspaces/${workspaceId}/invitations`, { params: { status } }),

  createInvitation: (workspaceId: string, data: {
    email: string;
    role?: string;
    message?: string;
    expires_in_days?: number;
  }) => api.post(`/workspaces/${workspaceId}/invitations`, data),

  bulkInvite: (workspaceId: string, data: {
    emails: string[];
    role?: string;
    message?: string;
  }) => api.post(`/workspaces/${workspaceId}/invitations/bulk`, data),

  acceptInvitation: (token: string) =>
    api.post('/workspaces/invitations/accept', { token }),

  declineInvitation: (token: string) =>
    api.post('/workspaces/invitations/decline', { token }),

  cancelInvitation: (workspaceId: string, invitationId: string) =>
    api.delete(`/workspaces/${workspaceId}/invitations/${invitationId}`),

  // Permissions
  checkPermission: (workspaceId: string, data: {
    object_type: string;
    object_id: string;
    action: string;
  }) => api.post(`/workspaces/${workspaceId}/check-permission`, data),

  setObjectPermission: (workspaceId: string, data: {
    object_type: string;
    object_id: string;
    user_id?: string;
    role?: string;
    can_view?: boolean;
    can_edit?: boolean;
    can_delete?: boolean;
    can_share?: boolean;
    can_export?: boolean;
  }) => api.post(`/workspaces/${workspaceId}/permissions`, data),

  // Role permissions info
  getRolePermissions: () =>
    api.get('/workspaces/roles/permissions'),
}

// Reports API
export const reportsApi = {
  // Templates
  createTemplate: (data: {
    name: string;
    description?: string;
    page_config?: Record<string, unknown>;
    branding?: Record<string, unknown>;
    sections: Array<Record<string, unknown>>;
    workspace_id?: string;
    is_public?: boolean;
    tags?: string[];
  }) => api.post('/reports/templates', data),

  listTemplates: (params?: {
    workspace_id?: string;
    is_public?: boolean;
    tags?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/reports/templates', { params }),

  getTemplate: (templateId: string) =>
    api.get(`/reports/templates/${templateId}`),

  updateTemplate: (templateId: string, data: Record<string, unknown>) =>
    api.patch(`/reports/templates/${templateId}`, data),

  deleteTemplate: (templateId: string) =>
    api.delete(`/reports/templates/${templateId}`),

  duplicateTemplate: (templateId: string, newName: string) =>
    api.post(`/reports/templates/${templateId}/duplicate`, null, {
      params: { new_name: newName },
    }),

  // Report Generation
  generateReport: (data: {
    template_id?: string;
    dashboard_id?: string;
    title?: string;
    subtitle?: string;
    format?: string;
    page_config?: Record<string, unknown>;
    branding?: Record<string, unknown>;
    sections?: Array<Record<string, unknown>>;
    filters?: Record<string, unknown>;
    parameters?: Record<string, unknown>;
    include_cover_page?: boolean;
    include_toc?: boolean;
  }) => api.post('/reports/generate', data),

  getJobStatus: (jobId: string) =>
    api.get(`/reports/jobs/${jobId}`),

  listJobs: (params?: {
    status?: string;
    limit?: number;
  }) => api.get('/reports/jobs', { params }),

  cancelJob: (jobId: string) =>
    api.post(`/reports/jobs/${jobId}/cancel`),

  downloadReport: (jobId: string) =>
    api.get(`/reports/download/${jobId}`, { responseType: 'blob' }),

  // Dashboard Export
  exportDashboard: (data: {
    dashboard_id: string;
    format?: string;
    title?: string;
    include_filters?: boolean;
    filter_state?: Record<string, unknown>;
  }) => api.post('/reports/export/dashboard', data),

  exportChart: (data: {
    chart_id: string;
    format?: string;
    width?: number;
    height?: number;
    scale?: number;
    include_title?: boolean;
    include_legend?: boolean;
    background_color?: string;
  }) => api.post('/reports/export/chart', data),

  // Scheduled Reports
  createScheduledReport: (params: {
    name: string;
    config: Record<string, unknown>;
    schedule: string;
    recipients: string[];
    workspace_id?: string;
  }) => api.post('/reports/scheduled', null, { params }),

  listScheduledReports: (params?: {
    workspace_id?: string;
    enabled_only?: boolean;
  }) => api.get('/reports/scheduled', { params }),

  deleteScheduledReport: (reportId: string) =>
    api.delete(`/reports/scheduled/${reportId}`),

  // Template Library
  getTemplateCategories: () =>
    api.get('/reports/library/categories'),

  getBuiltInTemplates: () =>
    api.get('/reports/library/built-in'),

  // Format Info
  getAvailableFormats: () =>
    api.get('/reports/formats'),
}

// Subscriptions and Alerts API
export const subscriptionsApi = {
  // Data Alerts
  createAlert: (data: {
    name: string;
    description?: string;
    enabled?: boolean;
    target_type: string;
    target_id: string;
    metric_column?: string;
    thresholds: Array<{
      condition: string;
      value: number;
      secondary_value?: number;
      severity: string;
    }>;
    evaluation_frequency?: string;
    cooldown_minutes?: number;
    notifications: Array<{
      channel: string;
      email?: Record<string, unknown>;
      slack?: Record<string, unknown>;
      webhook?: Record<string, unknown>;
      teams?: Record<string, unknown>;
    }>;
    workspace_id?: string;
    tags?: string[];
    metadata?: Record<string, unknown>;
  }) => api.post('/subscriptions/alerts', data),

  listAlerts: (params?: {
    workspace_id?: string;
    target_type?: string;
    target_id?: string;
    enabled_only?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/subscriptions/alerts', { params }),

  getAlert: (alertId: string) =>
    api.get(`/subscriptions/alerts/${alertId}`),

  updateAlert: (alertId: string, data: Record<string, unknown>) =>
    api.patch(`/subscriptions/alerts/${alertId}`, data),

  deleteAlert: (alertId: string) =>
    api.delete(`/subscriptions/alerts/${alertId}`),

  pauseAlert: (alertId: string) =>
    api.post(`/subscriptions/alerts/${alertId}/pause`),

  resumeAlert: (alertId: string) =>
    api.post(`/subscriptions/alerts/${alertId}/resume`),

  evaluateAlert: (alertId: string, currentValue: number, previousValue?: number) =>
    api.post(`/subscriptions/alerts/${alertId}/evaluate`, null, {
      params: { current_value: currentValue, previous_value: previousValue },
    }),

  acknowledgeAlert: (alertId: string) =>
    api.post(`/subscriptions/alerts/${alertId}/acknowledge`),

  getAlertHistory: (alertId: string, limit?: number) =>
    api.get(`/subscriptions/alerts/${alertId}/history`, { params: { limit } }),

  getAllAlertHistory: (limit?: number) =>
    api.get('/subscriptions/alerts/history/all', { params: { limit } }),

  getAlertSummary: (workspaceId?: string) =>
    api.get('/subscriptions/alerts/summary', { params: { workspace_id: workspaceId } }),

  // Dashboard Subscriptions
  createSubscription: (data: {
    name: string;
    description?: string;
    enabled?: boolean;
    dashboard_id: string;
    schedule: {
      frequency: string;
      time_of_day?: string;
      day_of_week?: number;
      day_of_month?: number;
      timezone?: string;
      cron_expression?: string;
    };
    content: {
      include_dashboard_snapshot?: boolean;
      include_charts?: string[];
      include_data_tables?: boolean;
      include_insights?: boolean;
      include_kpis?: boolean;
      format?: string;
    };
    recipients: string[];
    notification_channel?: string;
    filter_state?: Record<string, unknown>;
    workspace_id?: string;
    metadata?: Record<string, unknown>;
  }) => api.post('/subscriptions/subscriptions', data),

  listSubscriptions: (params?: {
    workspace_id?: string;
    dashboard_id?: string;
    active_only?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/subscriptions/subscriptions', { params }),

  getSubscription: (subscriptionId: string) =>
    api.get(`/subscriptions/subscriptions/${subscriptionId}`),

  updateSubscription: (subscriptionId: string, data: Record<string, unknown>) =>
    api.patch(`/subscriptions/subscriptions/${subscriptionId}`, data),

  deleteSubscription: (subscriptionId: string) =>
    api.delete(`/subscriptions/subscriptions/${subscriptionId}`),

  pauseSubscription: (subscriptionId: string) =>
    api.post(`/subscriptions/subscriptions/${subscriptionId}/pause`),

  resumeSubscription: (subscriptionId: string) =>
    api.post(`/subscriptions/subscriptions/${subscriptionId}/resume`),

  sendSubscriptionNow: (subscriptionId: string) =>
    api.post(`/subscriptions/subscriptions/${subscriptionId}/send`),

  getSubscriptionDeliveries: (subscriptionId: string, limit?: number) =>
    api.get(`/subscriptions/subscriptions/${subscriptionId}/deliveries`, { params: { limit } }),

  getAllSubscriptionDeliveries: (limit?: number) =>
    api.get('/subscriptions/subscriptions/deliveries/all', { params: { limit } }),

  getSubscriptionSummary: (workspaceId?: string) =>
    api.get('/subscriptions/subscriptions/summary', { params: { workspace_id: workspaceId } }),

  // Notification Channels
  listNotificationChannels: () =>
    api.get('/subscriptions/channels'),

  // Test Notifications
  testEmail: (recipients: string[], subject?: string) =>
    api.post('/subscriptions/test/email', null, { params: { recipients, subject } }),

  testSlack: (webhookUrl: string, message?: string) =>
    api.post('/subscriptions/test/slack', null, { params: { webhook_url: webhookUrl, message } }),

  testWebhook: (url: string, method?: string) =>
    api.post('/subscriptions/test/webhook', null, { params: { url, method } }),
}

// Advanced Charts API
export const advancedChartsApi = {
  // Chart Types
  listTypes: () =>
    api.get('/advanced-charts/types'),

  getTypeInfo: (chartType: string) =>
    api.get(`/advanced-charts/types/${chartType}`),

  // Suggestions
  suggestChartTypes: (data: unknown[], params: {
    columns: string[];
    has_time_column?: boolean;
    has_hierarchy?: boolean;
    has_flow_data?: boolean;
    num_categories?: number;
    num_measures?: number;
  }) => api.post('/advanced-charts/suggest', data, { params }),

  // Chart Creation
  createWaterfall: (data: unknown[], request: {
    connection_id: string;
    category_column: string;
    value_column: string;
    type_column?: string;
    auto_total?: boolean;
    starting_value?: number;
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/waterfall', request, {
    params: { data: JSON.stringify(data) },
  }),

  createFunnel: (data: unknown[], request: {
    connection_id: string;
    stage_column: string;
    value_column: string;
    stage_order?: string[];
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/funnel', request, {
    params: { data: JSON.stringify(data) },
  }),

  createGantt: (data: unknown[], request: {
    connection_id: string;
    id_column: string;
    name_column: string;
    start_column: string;
    end_column: string;
    progress_column?: string;
    parent_column?: string;
    dependencies_column?: string;
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/gantt', request, {
    params: { data: JSON.stringify(data) },
  }),

  createTreemap: (data: unknown[], request: {
    connection_id: string;
    id_column: string;
    name_column: string;
    value_column: string;
    parent_column?: string;
    color_column?: string;
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/treemap', request, {
    params: { data: JSON.stringify(data) },
  }),

  createSankey: (data: unknown[], request: {
    connection_id: string;
    source_column: string;
    target_column: string;
    value_column: string;
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/sankey', request, {
    params: { data: JSON.stringify(data) },
  }),

  createRadar: (data: unknown[], request: {
    connection_id: string;
    axis_column: string;
    value_columns: string[];
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/radar', request, {
    params: { data: JSON.stringify(data) },
  }),

  createBullet: (data: unknown[], request: {
    connection_id: string;
    title_column: string;
    actual_column: string;
    target_column?: string;
    range_columns?: string[];
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/bullet', request, {
    params: { data: JSON.stringify(data) },
  }),

  createHeatmap: (data: unknown[], request: {
    connection_id: string;
    x_column: string;
    y_column: string;
    value_column: string;
    aggregation?: string;
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/heatmap', request, {
    params: { data: JSON.stringify(data) },
  }),

  createGauge: (data: unknown[], request: {
    connection_id: string;
    value_column: string;
    min_value?: number;
    max_value?: number;
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/gauge', request, {
    params: { data: JSON.stringify(data) },
  }),

  createBoxplot: (data: unknown[], request: {
    connection_id: string;
    category_column: string;
    value_column: string;
    config?: Record<string, unknown>;
  }) => api.post('/advanced-charts/boxplot', request, {
    params: { data: JSON.stringify(data) },
  }),

  // Generic creation
  create: (chartType: string, data: unknown[], config: Record<string, unknown>) =>
    api.post(`/advanced-charts/create/${chartType}`, { config, data }),

  // Templates
  getTemplate: (chartType: string) =>
    api.get(`/advanced-charts/templates/${chartType}`),
}

// Embed SDK API
export const embedApi = {
  // Token Management
  createToken: (data: {
    name: string;
    description?: string;
    resource_type: string;
    resource_id: string;
    workspace_id?: string;
    allow_interactions?: boolean;
    allow_export?: boolean;
    allow_fullscreen?: boolean;
    allow_comments?: boolean;
    theme?: string;
    show_header?: boolean;
    show_toolbar?: boolean;
    custom_css?: string;
    allowed_domains?: string[];
    expires_at?: string;
    max_views?: number;
    settings?: Record<string, unknown>;
  }) => api.post('/embed/tokens', data),

  listTokens: (params?: {
    workspace_id?: string;
    resource_type?: string;
    resource_id?: string;
    active_only?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/embed/tokens', { params }),

  getToken: (tokenId: string) =>
    api.get(`/embed/tokens/${tokenId}`),

  updateToken: (tokenId: string, data: {
    name?: string;
    description?: string;
    allow_interactions?: boolean;
    allow_export?: boolean;
    allow_fullscreen?: boolean;
    allow_comments?: boolean;
    theme?: string;
    show_header?: boolean;
    show_toolbar?: boolean;
    custom_css?: string;
    allowed_domains?: string[];
    expires_at?: string;
    max_views?: number;
    is_active?: boolean;
    settings?: Record<string, unknown>;
  }) => api.patch(`/embed/tokens/${tokenId}`, data),

  revokeToken: (tokenId: string) =>
    api.post(`/embed/tokens/${tokenId}/revoke`),

  deleteToken: (tokenId: string) =>
    api.delete(`/embed/tokens/${tokenId}`),

  // Token Validation (Public)
  validateToken: (token: string, origin?: string) =>
    api.post('/embed/validate', { token, origin }),

  // Session Management (Public)
  startSession: (data: {
    token: string;
    origin_url?: string;
    referrer?: string;
    user_agent?: string;
  }) => api.post('/embed/session/start', data),

  endSession: (data: {
    session_id: string;
    duration_seconds?: number;
    interaction_count?: number;
    filter_changes?: number;
    exports_count?: number;
  }) => api.post('/embed/session/end', data),

  trackEvent: (data: {
    session_id: string;
    event_type: string;
    event_data?: Record<string, unknown>;
  }) => api.post('/embed/session/track', data),

  // Analytics
  getTokenAnalytics: (tokenId: string, params?: {
    start_date?: string;
    end_date?: string;
  }) => api.get(`/embed/analytics/token/${tokenId}`, { params }),

  getAnalyticsSummary: (params?: {
    workspace_id?: string;
    resource_type?: string;
    resource_id?: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/embed/analytics/summary', { params }),

  // Whitelist Management
  listWhitelist: (workspaceId: string) =>
    api.get('/embed/whitelist', { params: { workspace_id: workspaceId } }),

  addToWhitelist: (workspaceId: string, data: {
    domain: string;
    is_wildcard?: boolean;
    notes?: string;
  }) => api.post('/embed/whitelist', data, {
    params: { workspace_id: workspaceId },
  }),

  removeFromWhitelist: (whitelistId: string) =>
    api.delete(`/embed/whitelist/${whitelistId}`),

  // Code Generation
  generateCode: (data: {
    token_id: string;
    width?: string;
    height?: string;
    include_sdk?: boolean;
    framework?: 'vanilla' | 'react' | 'vue' | 'angular';
  }) => api.post('/embed/code', data),

  // SDK Config
  getSDKConfig: () =>
    api.get('/embed/sdk/config'),

  // Quick Embed
  getQuickEmbed: (resourceType: string, resourceId: string) =>
    api.get(`/embed/quick/${resourceType}/${resourceId}`),
}

// Audit API
export const auditApi = {
  // Audit Logs
  getLogs: (params?: {
    user_id?: string;
    user_email?: string;
    action?: string;
    action_category?: string;
    action_type?: string;
    resource_type?: string;
    resource_id?: string;
    workspace_id?: string;
    ip_address?: string;
    success_only?: boolean;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/audit/logs', { params }),

  getLog: (logId: string) =>
    api.get(`/audit/logs/${logId}`),

  getSummary: (params?: {
    workspace_id?: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/audit/logs/summary', { params }),

  exportLogs: (config: {
    format: 'csv' | 'json' | 'xlsx';
    filters?: Record<string, unknown>;
    include_metadata?: boolean;
    max_records?: number;
  }) => api.post('/audit/logs/export', config),

  // Activity Timeline
  getActivityTimeline: (params?: {
    workspace_id?: string;
    user_id?: string;
    limit?: number;
  }) => api.get('/audit/activity/timeline', { params }),

  getUserActivity: (userId: string, workspaceId?: string) =>
    api.get(`/audit/activity/user/${userId}`, {
      params: { workspace_id: workspaceId },
    }),

  // Security Alerts
  getAlerts: (params?: {
    alert_type?: string;
    severity?: string;
    status?: string;
    user_id?: string;
    workspace_id?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/audit/alerts', { params }),

  getAlert: (alertId: string) =>
    api.get(`/audit/alerts/${alertId}`),

  createAlert: (alert: {
    alert_type: string;
    severity: string;
    title: string;
    description?: string;
    user_id?: string;
    user_email?: string;
    ip_address?: string;
    related_audit_ids?: string[];
    workspace_id?: string;
    metadata?: Record<string, unknown>;
  }) => api.post('/audit/alerts', alert),

  updateAlert: (alertId: string, update: {
    status?: string;
    resolution_notes?: string;
  }) => api.patch(`/audit/alerts/${alertId}`, update),

  resolveAlert: (alertId: string, resolutionNotes: string) =>
    api.post(`/audit/alerts/${alertId}/resolve`, null, {
      params: { resolution_notes: resolutionNotes },
    }),

  dismissAlert: (alertId: string, reason: string) =>
    api.post(`/audit/alerts/${alertId}/dismiss`, null, {
      params: { reason },
    }),

  // Dashboard Stats
  getDashboardStats: (workspaceId?: string) =>
    api.get('/audit/dashboard', { params: { workspace_id: workspaceId } }),

  // Anomaly Detection
  checkAnomalies: (params?: {
    user_id?: string;
    workspace_id?: string;
  }) => api.post('/audit/anomalies/check', null, { params }),

  // Archive Management
  archiveLogs: (daysToKeep?: number) =>
    api.post('/audit/archive', null, {
      params: { days_to_keep: daysToKeep || 90 },
    }),

  getArchivedLogs: (params?: {
    start_date?: string;
    end_date?: string;
    user_id?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/audit/archived', { params }),
}

// Cloud Connectors API (BigQuery & Snowflake)
export const cloudConnectorsApi = {
  // BigQuery
  bigquery: {
    getStatus: () =>
      api.get('/cloud/bigquery/status'),

    test: (data: {
      project_id: string;
      credentials_json?: string;
      credentials_path?: string;
    }) => api.post('/cloud/bigquery/test', data),

    create: (data: {
      name: string;
      project_id: string;
      credentials_json?: string;
      credentials_path?: string;
      default_dataset?: string;
    }) => api.post('/cloud/bigquery/connections', data),

    getDatasets: (connectionId: string) =>
      api.get(`/cloud/bigquery/${connectionId}/datasets`),

    getTables: (connectionId: string, datasetId?: string) =>
      api.get(`/cloud/bigquery/${connectionId}/tables`, { params: { dataset_id: datasetId } }),

    getTableColumns: (connectionId: string, datasetId: string, tableId: string) =>
      api.get(`/cloud/bigquery/${connectionId}/tables/${datasetId}/${tableId}/columns`),

    getTablePreview: (connectionId: string, datasetId: string, tableId: string, limit?: number, offset?: number) =>
      api.get(`/cloud/bigquery/${connectionId}/tables/${datasetId}/${tableId}/preview`, {
        params: { limit, offset },
      }),

    executeQuery: (connectionId: string, sql: string, limit?: number) =>
      api.post(`/cloud/bigquery/${connectionId}/query`, null, {
        params: { sql, limit },
      }),

    estimateCost: (connectionId: string, sql: string) =>
      api.post(`/cloud/bigquery/${connectionId}/estimate-cost`, null, {
        params: { sql },
      }),
  },

  // Snowflake
  snowflake: {
    getStatus: () =>
      api.get('/cloud/snowflake/status'),

    test: (data: {
      account: string;
      user: string;
      password: string;
      warehouse?: string;
      database?: string;
      schema?: string;
      role?: string;
    }) => api.post('/cloud/snowflake/test', data),

    create: (data: {
      name: string;
      account: string;
      user: string;
      password: string;
      warehouse?: string;
      database?: string;
      schema?: string;
      role?: string;
    }) => api.post('/cloud/snowflake/connections', data),

    getDatabases: (connectionId: string) =>
      api.get(`/cloud/snowflake/${connectionId}/databases`),

    getWarehouses: (connectionId: string) =>
      api.get(`/cloud/snowflake/${connectionId}/warehouses`),

    getTables: (connectionId: string, database?: string, schema?: string) =>
      api.get(`/cloud/snowflake/${connectionId}/tables`, {
        params: { database, schema },
      }),

    getTableColumns: (connectionId: string, database: string, schema: string, table: string) =>
      api.get(`/cloud/snowflake/${connectionId}/tables/${database}/${schema}/${table}/columns`),

    getTablePreview: (connectionId: string, database: string, schema: string, table: string, limit?: number, offset?: number) =>
      api.get(`/cloud/snowflake/${connectionId}/tables/${database}/${schema}/${table}/preview`, {
        params: { limit, offset },
      }),

    executeQuery: (connectionId: string, sql: string, options?: {
      database?: string;
      schema?: string;
      limit?: number;
    }) => api.post(`/cloud/snowflake/${connectionId}/query`, null, {
      params: { sql, ...options },
    }),
  },
}

// Quick Insights API
export const insightsApi = {
  // Main analysis
  analyze: (data: {
    data: any[];
    columns?: string[];
    date_column?: string;
    measure_columns?: string[];
    dimension_columns?: string[];
    insight_types?: string[];
  }) => api.post('/insights/analyze', data),

  analyzeChart: (chartId: string) =>
    api.post(`/insights/analyze/chart/${chartId}`),

  analyzeDataset: (datasetId: string, limitRows?: number) =>
    api.post(`/insights/analyze/dataset/${datasetId}`, null, {
      params: { limit_rows: limitRows },
    }),

  // Specific analysis types
  detectTrends: (data: {
    data: any[];
    date_column: string;
    value_columns: string[];
  }) => api.post('/insights/trends', data),

  detectOutliers: (data: {
    data: any[];
    columns: string[];
    method?: 'iqr' | 'zscore';
    threshold?: number;
  }) => api.post('/insights/outliers', data),

  analyzeCorrelations: (data: {
    data: any[];
    columns: string[];
    min_correlation?: number;
  }) => api.post('/insights/correlations', data),

  analyzeDistribution: (data: {
    data: any[];
    columns: string[];
  }) => api.post('/insights/distribution', data),

  // Data profiling
  profileData: (data: any[], columns?: string[]) =>
    api.post('/insights/profile', { data, columns }),

  // Performers
  identifyPerformers: (data: {
    data: any[];
    measure: string;
    dimension: string;
  }) => api.post('/insights/performers', data),

  // Comparison
  compareGroups: (data: {
    data: any[];
    measures: string[];
    dimensions: string[];
  }) => api.post('/insights/compare', data),

  // Templates and configuration
  getTemplates: () =>
    api.get('/insights/templates'),

  getInsightTypes: () =>
    api.get('/insights/types'),

  // Dashboard quick insights
  getDashboardQuickInsights: (dashboardId: string, maxInsights?: number) =>
    api.post(`/insights/dashboard/${dashboardId}/quick`, null, {
      params: { max_insights: maxInsights },
    }),

  // Scheduled analysis
  scheduleAnalysis: (
    targetType: string,
    targetId: string,
    data: {
      frequency: string;
      insight_types?: string[];
      notify_on_high?: boolean;
    }
  ) => api.post(`/insights/schedule/${targetType}/${targetId}`, data),
}

// Kodee NL-to-SQL API
export const kodeeApi = {
  // NL-to-SQL Query
  query: (data: {
    question: string;
    connection_id?: string;
    model_id?: string;
    conversation_id?: string;
    include_explanation?: boolean;
    max_rows?: number;
  }) => api.post('/kodee/query', data),

  // Schema Context
  getSchemaContext: (connectionId: string, modelId?: string) =>
    api.get(`/kodee/context/${connectionId}`, { params: { model_id: modelId } }),

  // Chat Interface
  chat: (data: {
    message: string;
    session_id?: string;
    connection_id?: string;
    model_id?: string;
    execute_query?: boolean;
  }) => api.post('/kodee/chat', data),

  createChatSession: (connectionId?: string, modelId?: string) =>
    api.post('/kodee/chat/session', null, { params: { connection_id: connectionId, model_id: modelId } }),

  getChatSession: (sessionId: string) =>
    api.get(`/kodee/chat/session/${sessionId}`),

  listChatSessions: (connectionId?: string, limit?: number) =>
    api.get('/kodee/chat/sessions', { params: { connection_id: connectionId, limit } }),

  // SQL Validation
  validateSql: (sql: string, connectionId?: string, strict?: boolean) =>
    api.post('/kodee/validate', { sql, connection_id: connectionId, strict }),

  // Query History
  getHistory: (connectionId?: string, page?: number, pageSize?: number) =>
    api.get('/kodee/history', { params: { connection_id: connectionId, page, page_size: pageSize } }),

  deleteHistoryItem: (queryId: string) =>
    api.delete(`/kodee/history/${queryId}`),

  // Feedback
  submitFeedback: (feedback: {
    query_id: string;
    rating: number;
    correct_sql?: string;
    comments?: string;
  }) => api.post('/kodee/feedback', feedback),

  // Examples and Templates
  getExamples: () =>
    api.get('/kodee/examples'),

  // Suggestions
  getSuggestions: (connectionId: string, modelId?: string) =>
    api.get(`/kodee/suggestions/${connectionId}`, { params: { model_id: modelId } }),
}

// Mobile API
export const mobileApi = {
  // Mobile Dashboard Layouts
  getMobileLayout: (dashboardId: string) =>
    api.get(`/mobile/dashboard/${dashboardId}/layout`),

  saveMobileLayout: (dashboardId: string, layout: {
    enabled?: boolean;
    layout_mode?: string;
    charts?: Array<{
      chart_id: string;
      order: number;
      visible?: boolean;
      collapsed?: boolean;
      height?: number;
      simplified?: boolean;
      touch_enabled?: boolean;
      swipe_navigation?: boolean;
    }>;
    stack_charts?: boolean;
    show_chart_titles?: boolean;
    compact_headers?: boolean;
    hide_empty_charts?: boolean;
    filter_position?: string;
    collapsible_filters?: boolean;
    quick_filters_count?: number;
    show_navigation?: boolean;
    bottom_navigation?: boolean;
    swipe_between_charts?: boolean;
    pull_to_refresh?: boolean;
  }) => api.put(`/mobile/dashboard/${dashboardId}/layout`, layout),

  generateMobileLayout: (dashboardId: string, charts: Array<{ id: string; type: string }>) =>
    api.post(`/mobile/dashboard/${dashboardId}/layout/generate`, charts),

  getMobileDashboard: (dashboardId: string, params?: {
    device_width?: number;
    charts?: string;
    filters?: string;
  }) => api.get(`/mobile/dashboard/${dashboardId}`, { params }),

  // User Settings
  getUserSettings: () =>
    api.get('/mobile/settings'),

  saveUserSettings: (settings: {
    layout_mode_preference?: string;
    default_dashboard_id?: string;
    quick_access_dashboards?: string[];
    gesture_config?: Record<string, unknown>;
    offline_config?: Record<string, unknown>;
    notification_preferences?: Record<string, unknown>;
    dark_mode?: string;
    font_size?: string;
    data_saver_mode?: boolean;
    biometric_auth?: boolean;
  }) => api.put('/mobile/settings', settings),

  updateUserSettings: (updates: Record<string, unknown>) =>
    api.patch('/mobile/settings', updates),

  // Gestures
  getDefaultGestures: () =>
    api.get('/mobile/gestures/defaults'),

  updateGestureSettings: (gestureConfig: {
    enabled?: boolean;
    bindings?: Array<{
      gesture: string;
      action: string;
      target?: string;
      params?: Record<string, unknown>;
    }>;
    haptic_feedback?: boolean;
    gesture_hints?: boolean;
  }) => api.put('/mobile/settings/gestures', gestureConfig),

  // Offline / Caching
  cacheDashboard: (dashboardId: string, dashboardName: string, dashboardData?: Record<string, unknown>) =>
    api.post(`/mobile/cache/dashboard/${dashboardId}`, dashboardData, {
      params: { dashboard_name: dashboardName },
    }),

  getCachedDashboard: (dashboardId: string) =>
    api.get(`/mobile/cache/dashboard/${dashboardId}`),

  listCachedDashboards: () =>
    api.get('/mobile/cache/dashboards'),

  removeCachedDashboard: (dashboardId: string) =>
    api.delete(`/mobile/cache/dashboard/${dashboardId}`),

  getSyncStatus: () =>
    api.get('/mobile/sync/status'),

  syncOfflineChanges: (changes: Array<Record<string, unknown>>) =>
    api.post('/mobile/sync', changes),

  // Push Notifications
  registerDevice: (deviceInfo: {
    device_id?: string;
    platform: string;
    os_version?: string;
    app_version?: string;
    screen_width: number;
    screen_height: number;
    pixel_ratio?: number;
    is_tablet?: boolean;
    supports_touch?: boolean;
    push_token?: string;
  }) => api.post('/mobile/device/register', deviceInfo),

  getNotifications: (params?: {
    unread_only?: boolean;
    limit?: number;
  }) => api.get('/mobile/notifications', { params }),

  markNotificationRead: (notificationId: string) =>
    api.post(`/mobile/notifications/${notificationId}/read`),

  markAllNotificationsRead: () =>
    api.post('/mobile/notifications/read-all'),

  updateNotificationSettings: (preferences: {
    enabled?: boolean;
    alert_notifications?: boolean;
    report_notifications?: boolean;
    mention_notifications?: boolean;
    schedule_notifications?: boolean;
    quiet_hours_enabled?: boolean;
    quiet_hours_start?: string;
    quiet_hours_end?: string;
  }) => api.put('/mobile/settings/notifications', preferences),

  // Analytics
  trackAnalyticsEvent: (event: {
    event_type: string;
    user_id?: string;
    device_info: {
      platform: string;
      screen_width: number;
      screen_height: number;
      pixel_ratio?: number;
      is_tablet?: boolean;
      supports_touch?: boolean;
    };
    dashboard_id?: string;
    chart_id?: string;
    gesture?: string;
    duration_ms?: number;
    metadata?: Record<string, unknown>;
    timestamp: string;
  }) => api.post('/mobile/analytics/event', event),

  getUsageStats: (days?: number) =>
    api.get('/mobile/analytics/stats', { params: { days } }),

  // Breakpoints
  getBreakpoints: () =>
    api.get('/mobile/breakpoints'),

  // Device Detection
  detectDevice: (params?: {
    screen_width?: number;
    screen_height?: number;
  }) => api.get('/mobile/detect', { params }),
}

// Collaboration API
export const collaborationApi = {
  // Presence
  joinRoom: (resourceType: string, resourceId: string, deviceType?: string) =>
    api.post('/collaboration/presence/join', null, {
      params: { resource_type: resourceType, resource_id: resourceId, device_type: deviceType },
    }),

  leaveRoom: (resourceType: string, resourceId: string) =>
    api.post('/collaboration/presence/leave', null, {
      params: { resource_type: resourceType, resource_id: resourceId },
    }),

  updatePresence: (resourceType: string, resourceId: string, update: {
    cursor?: { x: number; y: number; element_id?: string; element_type?: string };
    status?: string;
  }) => api.post('/collaboration/presence/update', update, {
    params: { resource_type: resourceType, resource_id: resourceId },
  }),

  getRoomPresence: (resourceType: string, resourceId: string) =>
    api.get(`/collaboration/presence/${resourceType}/${resourceId}`),

  heartbeat: (resourceType: string, resourceId: string) =>
    api.post('/collaboration/presence/heartbeat', null, {
      params: { resource_type: resourceType, resource_id: resourceId },
    }),

  // Comments
  createComment: (comment: {
    content: string;
    resource_type: string;
    resource_id: string;
    parent_id?: string;
    mentions?: string[];
    position?: Record<string, unknown>;
  }) => api.post('/collaboration/comments', comment),

  listComments: (resourceType: string, resourceId: string, params?: {
    include_resolved?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get(`/collaboration/comments/${resourceType}/${resourceId}`, { params }),

  getComment: (commentId: string) =>
    api.get(`/collaboration/comments/single/${commentId}`),

  updateComment: (commentId: string, update: {
    content?: string;
    status?: string;
  }) => api.patch(`/collaboration/comments/${commentId}`, update),

  deleteComment: (commentId: string) =>
    api.delete(`/collaboration/comments/${commentId}`),

  resolveComment: (commentId: string) =>
    api.post(`/collaboration/comments/${commentId}/resolve`),

  addReaction: (commentId: string, reactionType: string) =>
    api.post(`/collaboration/comments/${commentId}/reactions`, null, {
      params: { reaction_type: reactionType },
    }),

  removeReaction: (commentId: string, reactionType: string) =>
    api.delete(`/collaboration/comments/${commentId}/reactions`, {
      params: { reaction_type: reactionType },
    }),

  // Activity Feed
  getActivityFeed: (params?: {
    workspace_id?: string;
    user_id?: string;
    resource_type?: string;
    resource_id?: string;
    activity_types?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/collaboration/activity', { params }),

  logActivity: (data: {
    activity_type: string;
    target_type: string;
    target_id: string;
    target_name: string;
    description: string;
    workspace_id?: string;
    metadata?: Record<string, unknown>;
  }) => api.post('/collaboration/activity/log', null, { params: data }),

  // Edit Locks
  acquireLock: (resourceType: string, resourceId: string, elementId?: string) =>
    api.post('/collaboration/locks/acquire', null, {
      params: { resource_type: resourceType, resource_id: resourceId, element_id: elementId },
    }),

  releaseLock: (resourceType: string, resourceId: string, elementId?: string) =>
    api.post('/collaboration/locks/release', null, {
      params: { resource_type: resourceType, resource_id: resourceId, element_id: elementId },
    }),

  getLocks: (resourceType: string, resourceId: string) =>
    api.get(`/collaboration/locks/${resourceType}/${resourceId}`),

  // Notifications
  getNotifications: (params?: {
    unread_only?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/collaboration/notifications', { params }),

  markNotificationRead: (notificationId: string) =>
    api.post(`/collaboration/notifications/${notificationId}/read`),

  markAllNotificationsRead: () =>
    api.post('/collaboration/notifications/read-all'),

  getNotificationPreferences: () =>
    api.get('/collaboration/notifications/preferences'),

  updateNotificationPreferences: (preferences: Record<string, unknown>) =>
    api.put('/collaboration/notifications/preferences', preferences),

  // Sessions
  getSession: (resourceType: string, resourceId: string) =>
    api.get(`/collaboration/sessions/${resourceType}/${resourceId}`),

  recordChange: (resourceType: string, resourceId: string) =>
    api.post(`/collaboration/sessions/${resourceType}/${resourceId}/change`),
}

// Sharing API
export const sharingApi = {
  // Share Links
  createShareLink: (data: {
    resource_type: string;
    resource_id: string;
    name?: string;
    description?: string;
    access_level?: string;
    visibility?: string;
    password?: string;
    allowed_emails?: string[];
    allowed_domains?: string[];
    expires_at?: string;
    max_views?: number;
    custom_slug?: string;
    hide_branding?: boolean;
    preset_filters?: Record<string, unknown>;
    locked_filters?: boolean;
    show_toolbar?: boolean;
    show_export?: boolean;
    theme?: string;
    workspace_id?: string;
  }, resourceName: string) =>
    api.post('/sharing/links', data, { params: { resource_name: resourceName } }),

  listShareLinks: (params?: {
    workspace_id?: string;
    resource_type?: string;
    resource_id?: string;
    include_revoked?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/sharing/links', { params }),

  getShareLink: (linkId: string) =>
    api.get(`/sharing/links/${linkId}`),

  updateShareLink: (linkId: string, update: {
    name?: string;
    description?: string;
    access_level?: string;
    visibility?: string;
    password?: string;
    allowed_emails?: string[];
    allowed_domains?: string[];
    expires_at?: string;
    max_views?: number;
    is_active?: boolean;
    preset_filters?: Record<string, unknown>;
    locked_filters?: boolean;
    show_toolbar?: boolean;
    show_export?: boolean;
    theme?: string;
  }) => api.patch(`/sharing/links/${linkId}`, update),

  deleteShareLink: (linkId: string) =>
    api.delete(`/sharing/links/${linkId}`),

  revokeShareLink: (linkId: string) =>
    api.post(`/sharing/links/${linkId}/revoke`),

  // Access Validation (Public)
  validateAccess: (data: {
    token: string;
    password?: string;
    viewer_email?: string;
    viewer_name?: string;
  }) => api.post('/sharing/access', data),

  accessByCode: (code: string, params?: {
    password?: string;
    email?: string;
    name?: string;
  }) => api.get(`/sharing/access/${code}`, { params }),

  // Analytics
  getShareAnalytics: (linkId: string, days?: number) =>
    api.get(`/sharing/links/${linkId}/analytics`, { params: { days } }),

  // QR Code
  generateQRCode: (linkId: string, config?: {
    size?: number;
    format?: string;
    foreground_color?: string;
    background_color?: string;
  }) => api.post(`/sharing/links/${linkId}/qr`, config),

  // Email Sharing
  sendShareEmail: (linkId: string, data: {
    recipients: string[];
    subject?: string;
    message?: string;
    include_preview?: boolean;
  }) => api.post(`/sharing/links/${linkId}/email`, data),

  // Templates
  createTemplate: (name: string, settings: Record<string, unknown>, params?: {
    description?: string;
    workspace_id?: string;
  }) => api.post('/sharing/templates', settings, { params: { name, ...params } }),

  listTemplates: (workspaceId?: string) =>
    api.get('/sharing/templates', { params: { workspace_id: workspaceId } }),

  // Quick Share
  quickShare: (resourceType: string, resourceId: string, resourceName: string, params?: {
    access_level?: string;
    expires_in_days?: number;
    require_password?: boolean;
    password?: string;
  }) => api.post(`/sharing/quick/${resourceType}/${resourceId}`, null, {
    params: { resource_name: resourceName, ...params },
  }),

  // Bulk Operations
  bulkCreate: (resourceType: string, resourceIds: string[], accessLevel?: string) =>
    api.post('/sharing/bulk/create', null, {
      params: { resource_type: resourceType, resource_ids: resourceIds, access_level: accessLevel },
    }),

  bulkRevoke: (linkIds: string[]) =>
    api.post('/sharing/bulk/revoke', linkIds),
}

// Shortcuts & Command Palette API
export const shortcutsApi = {
  // Shortcuts
  listShortcuts: (params?: {
    scope?: string;
    category?: string;
  }) => api.get('/shortcuts/shortcuts', { params }),

  getShortcut: (shortcutId: string) =>
    api.get(`/shortcuts/shortcuts/${shortcutId}`),

  createCustomShortcut: (data: {
    name: string;
    key: string;
    modifiers?: string;
    action_type: string;
    action_target: string;
    category?: string;
    scope?: string;
    description?: string;
  }) => api.post('/shortcuts/shortcuts', null, { params: data }),

  overrideShortcut: (shortcutId: string, params?: {
    key?: string;
    modifiers?: string;
    enabled?: boolean;
  }) => api.put(`/shortcuts/shortcuts/${shortcutId}/override`, null, { params }),

  resetShortcut: (shortcutId: string) =>
    api.post(`/shortcuts/shortcuts/${shortcutId}/reset`),

  resetAllShortcuts: () =>
    api.post('/shortcuts/shortcuts/reset-all'),

  getShortcutCategories: () =>
    api.get('/shortcuts/shortcuts/categories'),

  // Commands
  listCommands: (params?: {
    category?: string;
    include_recent?: boolean;
  }) => api.get('/shortcuts/commands', { params }),

  searchCommands: (query: string, params?: {
    category?: string;
    limit?: number;
  }) => api.get('/shortcuts/commands/search', { params: { q: query, ...params } }),

  executeCommand: (commandId: string, context?: Record<string, unknown>) =>
    api.post(`/shortcuts/commands/${commandId}/execute`, context),

  // Preferences
  getPreferences: () =>
    api.get('/shortcuts/preferences'),

  updatePreferences: (updates: Record<string, unknown>) =>
    api.put('/shortcuts/preferences', updates),

  // History
  getCommandHistory: () =>
    api.get('/shortcuts/history'),

  clearCommandHistory: () =>
    api.delete('/shortcuts/history'),

  // Favorites
  addFavorite: (commandId: string) =>
    api.post(`/shortcuts/favorites/${commandId}`),

  removeFavorite: (commandId: string) =>
    api.delete(`/shortcuts/favorites/${commandId}`),
}

// Global Search & Navigation API
export const searchApi = {
  // Search
  search: (query: string, params?: {
    types?: string;
    scope?: string;
    sort_by?: string;
    sort_order?: string;
    skip?: number;
    limit?: number;
    include_content?: boolean;
    tags?: string;
    workspace_id?: string;
    created_by?: string;
    is_favorite?: boolean;
  }) => api.get('/search/search', { params: { q: query, ...params } }),

  advancedSearch: (query: {
    query: string;
    filters?: Record<string, unknown>;
    scope?: string;
    sort_by?: string;
    sort_order?: string;
    skip?: number;
    limit?: number;
    include_content?: boolean;
  }) => api.post('/search/search', query),

  getSuggestions: (query: string, limit?: number) =>
    api.get('/search/suggestions', { params: { q: query, limit } }),

  // Recent Items
  getRecentItems: (params?: {
    types?: string;
    limit?: number;
  }) => api.get('/search/recent', { params }),

  addRecentItem: (data: {
    resource_type: string;
    resource_id: string;
    name: string;
    action?: string;
    description?: string;
  }) => api.post('/search/recent', null, { params: data }),

  clearRecentItems: (resourceType?: string) =>
    api.delete('/search/recent', { params: { resource_type: resourceType } }),

  // Favorites
  getFavorites: (params?: {
    resource_type?: string;
    folder?: string;
  }) => api.get('/search/favorites', { params }),

  addFavorite: (data: {
    resource_type: string;
    resource_id: string;
    name: string;
    description?: string;
    folder?: string;
    notes?: string;
  }) => api.post('/search/favorites', null, { params: data }),

  updateFavorite: (favoriteId: string, params?: {
    folder?: string;
    notes?: string;
    display_order?: number;
  }) => api.put(`/search/favorites/${favoriteId}`, null, { params }),

  removeFavorite: (resourceType: string, resourceId: string) =>
    api.delete('/search/favorites', { params: { resource_type: resourceType, resource_id: resourceId } }),

  reorderFavorites: (favoriteIds: string[]) =>
    api.put('/search/favorites/reorder', favoriteIds),

  // Quick Navigation
  getQuickNav: () =>
    api.get('/search/nav'),

  // Index Management (Admin)
  getIndexStatus: () =>
    api.get('/search/index/status'),

  indexResource: (resourceType: string, resourceId: string, data: Record<string, unknown>) =>
    api.post('/search/index/resource', data, {
      params: { resource_type: resourceType, resource_id: resourceId },
    }),

  removeFromIndex: (resourceType: string, resourceId: string) =>
    api.delete('/search/index/resource', {
      params: { resource_type: resourceType, resource_id: resourceId },
    }),

  reindexAll: () =>
    api.post('/search/index/reindex'),
}

// SDK & API Management
export const sdkApi = {
  // API Keys
  listKeys: (params?: {
    workspace_id?: string;
    key_type?: string;
    status?: string;
  }) => api.get('/sdk/keys', { params }),

  createKey: (data: {
    name: string;
    description?: string;
    key_type?: string;
    workspace_id?: string;
    permissions?: Record<string, unknown>;
    rate_limits?: Record<string, unknown>;
    allowed_ips?: string[];
    allowed_domains?: string[];
    expires_in_days?: number;
    tags?: string[];
  }) => api.post('/sdk/keys', data),

  getKey: (keyId: string) =>
    api.get(`/sdk/keys/${keyId}`),

  updateKey: (keyId: string, data: Record<string, unknown>) =>
    api.patch(`/sdk/keys/${keyId}`, data),

  revokeKey: (keyId: string) =>
    api.post(`/sdk/keys/${keyId}/revoke`),

  deleteKey: (keyId: string) =>
    api.delete(`/sdk/keys/${keyId}`),

  rotateKey: (keyId: string) =>
    api.post(`/sdk/keys/${keyId}/rotate`),

  // Validation
  validateKey: (apiKey: string, params?: {
    endpoint?: string;
    ip_address?: string;
    domain?: string;
  }) => api.post('/sdk/validate', { api_key: apiKey, ...params }),

  // Usage & Rate Limits
  getUsageStats: (keyId: string, days?: number) =>
    api.get(`/sdk/keys/${keyId}/usage`, { params: { days } }),

  getRateLimitStatus: (keyId: string) =>
    api.get(`/sdk/keys/${keyId}/rate-limits`),

  // Code Generation
  generateCode: (params: {
    language: string;
    resource_type: string;
    resource_id: string;
    include_auth?: boolean;
    include_error_handling?: boolean;
  }) => api.post('/sdk/generate-code', null, { params }),

  getSupportedLanguages: () =>
    api.get('/sdk/languages'),

  // Documentation
  getDocumentation: () =>
    api.get('/sdk/docs'),

  getOpenAPISpec: () =>
    api.get('/sdk/docs/openapi'),

  getPostmanCollection: () =>
    api.get('/sdk/docs/postman'),

  // Configuration
  getConfig: () =>
    api.get('/sdk/config'),

  // Embed Info
  getEmbedInfo: (resourceType: string, resourceId: string) =>
    api.get(`/sdk/embed/${resourceType}/${resourceId}`),
}

// Plugin Management API
export const pluginsApi = {
  // Installed Plugins
  listInstalled: (params?: {
    workspace_id?: string;
    plugin_type?: string;
    status?: string;
  }) => api.get('/plugins/installed', { params }),

  getInstalled: (pluginId: string) =>
    api.get(`/plugins/installed/${pluginId}`),

  install: (data: {
    plugin_id: string;
    version?: string;
    config?: Record<string, unknown>;
    workspace_id?: string;
    enable_after_install?: boolean;
  }) => api.post('/plugins/install', data),

  uninstall: (pluginId: string) =>
    api.delete(`/plugins/installed/${pluginId}`),

  enable: (pluginId: string) =>
    api.post(`/plugins/installed/${pluginId}/enable`),

  disable: (pluginId: string) =>
    api.post(`/plugins/installed/${pluginId}/disable`),

  updateConfig: (pluginId: string, data: {
    config?: Record<string, unknown>;
    enabled_workspaces?: string[];
  }) => api.patch(`/plugins/installed/${pluginId}`, data),

  updateVersion: (pluginId: string, version?: string) =>
    api.post(`/plugins/installed/${pluginId}/update-version`, null, {
      params: { version },
    }),

  // Registry
  searchRegistry: (params?: {
    q?: string;
    type?: string;
    keywords?: string;
    verified_only?: boolean;
    sort_by?: string;
    page?: number;
    page_size?: number;
  }) => api.get('/plugins/registry', { params }),

  getRegistryPlugin: (pluginId: string) =>
    api.get(`/plugins/registry/${pluginId}`),

  getFeaturedPlugins: (limit?: number) =>
    api.get('/plugins/registry/featured', { params: { limit } }),

  // Statistics & Updates
  getStats: () =>
    api.get('/plugins/stats'),

  checkUpdates: () =>
    api.get('/plugins/updates'),

  // Events
  getEvents: (pluginId?: string, limit?: number) =>
    api.get('/plugins/events', { params: { plugin_id: pluginId, limit } }),

  // Hooks
  executeHooks: (hookType: string, data?: Record<string, unknown>) =>
    api.post('/plugins/hooks/execute', data, { params: { hook_type: hookType } }),

  listHooks: () =>
    api.get('/plugins/hooks'),

  // Plugin Types
  getPluginTypes: () =>
    api.get('/plugins/types'),

  // Bulk Operations
  bulkEnable: (pluginIds: string[]) =>
    api.post('/plugins/bulk/enable', pluginIds),

  bulkDisable: (pluginIds: string[]) =>
    api.post('/plugins/bulk/disable', pluginIds),
}

// Caching API
export const cachingApi = {
  // Cache Operations
  listKeys: (params?: {
    cache_type?: string;
    pattern?: string;
    workspace_id?: string;
    limit?: number;
    cursor?: string;
  }) => api.get('/cache/keys', { params }),

  getKeyInfo: (key: string) =>
    api.get(`/cache/keys/${encodeURIComponent(key)}`),

  deleteKey: (key: string) =>
    api.delete(`/cache/keys/${encodeURIComponent(key)}`),

  setEntry: (params: {
    cache_type: string;
    identifier: string;
    data: unknown;
    workspace_id?: string;
    ttl_seconds?: number;
    tags?: string;
  }) => api.post('/cache/set', params.data, {
    params: {
      cache_type: params.cache_type,
      identifier: params.identifier,
      workspace_id: params.workspace_id,
      ttl_seconds: params.ttl_seconds,
      tags: params.tags,
    },
  }),

  getEntry: (params: {
    cache_type: string;
    identifier: string;
    workspace_id?: string;
  }) => api.get('/cache/get', { params }),

  checkExists: (params: {
    cache_type: string;
    identifier: string;
    workspace_id?: string;
  }) => api.get('/cache/exists', { params }),

  // TTL Policies
  listPolicies: (cacheType?: string) =>
    api.get('/cache/policies', { params: { cache_type: cacheType } }),

  createPolicy: (data: {
    name: string;
    description?: string;
    cache_type: string;
    default_ttl_seconds?: number;
    max_ttl_seconds?: number;
    min_ttl_seconds?: number;
    stale_while_revalidate_seconds?: number;
    adaptive_ttl?: boolean;
  }) => api.post('/cache/policies', data),

  getPolicy: (policyId: string) =>
    api.get(`/cache/policies/${policyId}`),

  updatePolicy: (policyId: string, data: Record<string, unknown>) =>
    api.patch(`/cache/policies/${policyId}`, data),

  deletePolicy: (policyId: string) =>
    api.delete(`/cache/policies/${policyId}`),

  // Cache Warming
  listWarmingTasks: () =>
    api.get('/cache/warming'),

  createWarmingTask: (data: {
    name: string;
    description?: string;
    cache_type: string;
    target_keys: Array<Record<string, unknown>>;
    schedule?: string;
    priority?: number;
    enabled?: boolean;
  }) => api.post('/cache/warming', data),

  getWarmingTask: (taskId: string) =>
    api.get(`/cache/warming/${taskId}`),

  deleteWarmingTask: (taskId: string) =>
    api.delete(`/cache/warming/${taskId}`),

  executeWarmingTask: (taskId: string) =>
    api.post(`/cache/warming/${taskId}/execute`),

  warmAll: () =>
    api.post('/cache/warm-all'),

  // Invalidation
  listInvalidationRules: () =>
    api.get('/cache/invalidation/rules'),

  createInvalidationRule: (data: {
    name: string;
    description?: string;
    event_type: string;
    target_cache_types: string[];
    key_patterns: string[];
    delay_seconds?: number;
    cascade?: boolean;
  }) => api.post('/cache/invalidation/rules', data),

  getInvalidationRule: (ruleId: string) =>
    api.get(`/cache/invalidation/rules/${ruleId}`),

  deleteInvalidationRule: (ruleId: string) =>
    api.delete(`/cache/invalidation/rules/${ruleId}`),

  invalidate: (data: {
    cache_type?: string;
    key_pattern?: string;
    workspace_id?: string;
    tags?: string[];
    reason?: string;
  }) => api.post('/cache/invalidate', data),

  invalidateByType: (cacheType: string, workspaceId?: string) =>
    api.post(`/cache/invalidate/by-type/${cacheType}`, null, {
      params: { workspace_id: workspaceId },
    }),

  triggerInvalidationEvent: (eventType: string, source?: string) =>
    api.post('/cache/invalidate/event', null, {
      params: { event_type: eventType, source: source || 'api' },
    }),

  listInvalidationEvents: (limit?: number) =>
    api.get('/cache/invalidation/events', { params: { limit } }),

  // Statistics & Health
  getStats: () =>
    api.get('/cache/stats'),

  getHealth: () =>
    api.get('/cache/health'),

  // Management
  clearAll: (confirm: boolean) =>
    api.post('/cache/clear', null, { params: { confirm } }),

  clearType: (cacheType: string) =>
    api.post(`/cache/clear/${cacheType}`),

  getCacheTypes: () =>
    api.get('/cache/types'),

  getDefaults: () =>
    api.get('/cache/defaults'),
}

// External Integrations API
export const integrationsApi = {
  // Webhooks
  listWebhooks: (params?: {
    workspace_id?: string;
    integration_type?: string;
    status?: string;
  }) => api.get('/integrations/webhooks', { params }),

  createWebhook: (data: {
    name: string;
    description?: string;
    integration_type?: string;
    events: string[];
    config: {
      url: string;
      method?: string;
      headers?: Record<string, string>;
      secret?: string;
      timeout_seconds?: number;
      retry_count?: number;
      retry_delay_seconds?: number;
    };
    workspace_id?: string;
  }) => api.post('/integrations/webhooks', data),

  getWebhook: (webhookId: string) =>
    api.get(`/integrations/webhooks/${webhookId}`),

  updateWebhook: (webhookId: string, data: {
    name?: string;
    description?: string;
    events?: string[];
    config?: Record<string, unknown>;
    status?: string;
  }) => api.patch(`/integrations/webhooks/${webhookId}`, data),

  deleteWebhook: (webhookId: string) =>
    api.delete(`/integrations/webhooks/${webhookId}`),

  testWebhook: (webhookId: string, data?: {
    event_type?: string;
    sample_data?: Record<string, unknown>;
  }) => api.post(`/integrations/webhooks/${webhookId}/test`, data || {}),

  getWebhookDeliveries: (webhookId: string, limit?: number) =>
    api.get(`/integrations/webhooks/${webhookId}/deliveries`, {
      params: { limit },
    }),

  getWebhookEventTypes: () =>
    api.get('/integrations/webhooks/events/types'),

  // Notification Channels
  listChannels: (params?: {
    workspace_id?: string;
    integration_type?: string;
  }) => api.get('/integrations/channels', { params }),

  createChannel: (data: {
    name: string;
    integration_type: string;
    config: {
      slack?: Record<string, unknown>;
      teams?: Record<string, unknown>;
      discord?: Record<string, unknown>;
    };
    workspace_id?: string;
  }) => api.post('/integrations/channels', data),

  getChannel: (channelId: string) =>
    api.get(`/integrations/channels/${channelId}`),

  deleteChannel: (channelId: string) =>
    api.delete(`/integrations/channels/${channelId}`),

  sendNotification: (channelId: string, message: {
    title: string;
    message: string;
    url?: string;
    color?: string;
    fields?: Array<{ title: string; value: string }>;
    image_url?: string;
  }) => api.post(`/integrations/channels/${channelId}/send`, message),

  testChannel: (channelId: string) =>
    api.post(`/integrations/channels/${channelId}/test`),

  // Git Integration
  listGitRepositories: (params?: {
    workspace_id?: string;
    provider?: string;
  }) => api.get('/integrations/git/repositories', { params }),

  createGitRepository: (data: {
    name: string;
    description?: string;
    provider: string;
    url: string;
    branch?: string;
    path_prefix?: string;
    access_token?: string;
    ssh_key_id?: string;
    sync_direction?: string;
    auto_sync?: boolean;
    sync_interval_minutes?: number;
    workspace_id?: string;
  }) => api.post('/integrations/git/repositories', data),

  getGitRepository: (repoId: string) =>
    api.get(`/integrations/git/repositories/${repoId}`),

  updateGitRepository: (repoId: string, data: {
    name?: string;
    description?: string;
    branch?: string;
    path_prefix?: string;
    access_token?: string;
    ssh_key_id?: string;
    sync_direction?: string;
    auto_sync?: boolean;
    sync_interval_minutes?: number;
    status?: string;
  }) => api.patch(`/integrations/git/repositories/${repoId}`, data),

  deleteGitRepository: (repoId: string) =>
    api.delete(`/integrations/git/repositories/${repoId}`),

  syncGitRepository: (repoId: string) =>
    api.post(`/integrations/git/repositories/${repoId}/sync`),

  exportToGit: (repoId: string, config: {
    resource_type: string;
    resource_id: string;
    file_path: string;
    format?: string;
    include_data?: boolean;
    commit_message?: string;
  }) => api.post(`/integrations/git/repositories/${repoId}/export`, config),

  importFromGit: (repoId: string, config: {
    file_path: string;
    resource_type: string;
    overwrite_existing?: boolean;
    target_workspace_id?: string;
  }) => api.post(`/integrations/git/repositories/${repoId}/import`, config),

  // dbt Integration
  listDbtProjects: (workspaceId?: string) =>
    api.get('/integrations/dbt/projects', {
      params: { workspace_id: workspaceId },
    }),

  createDbtProject: (data: {
    name: string;
    description?: string;
    project_path: string;
    profile_name: string;
    target_name?: string;
    connection_id?: string;
    git_repository_id?: string;
    workspace_id?: string;
  }) => api.post('/integrations/dbt/projects', data),

  getDbtProject: (projectId: string) =>
    api.get(`/integrations/dbt/projects/${projectId}`),

  deleteDbtProject: (projectId: string) =>
    api.delete(`/integrations/dbt/projects/${projectId}`),

  runDbt: (projectId: string, data: {
    command: string;
    select?: string;
    exclude?: string;
    full_refresh?: boolean;
    vars?: Record<string, unknown>;
  }) => api.post(`/integrations/dbt/projects/${projectId}/run`, data),

  getDbtModels: (projectId: string) =>
    api.get(`/integrations/dbt/projects/${projectId}/models`),

  getDbtRunHistory: (projectId: string, limit?: number) =>
    api.get(`/integrations/dbt/projects/${projectId}/runs`, {
      params: { limit },
    }),

  // Integration Hub
  getIntegrationHub: (workspaceId?: string) =>
    api.get('/integrations/hub', {
      params: { workspace_id: workspaceId },
    }),

  getZapierConfig: () =>
    api.get('/integrations/zapier/config'),

  getIntegrationStats: (workspaceId?: string) =>
    api.get('/integrations/stats', {
      params: { workspace_id: workspaceId },
    }),

  // OAuth
  getOAuthAuthorizeUrl: (integrationType: string, scopes?: string) =>
    api.get('/integrations/oauth/authorize', {
      params: { integration_type: integrationType, scopes },
    }),

  handleOAuthCallback: (code: string, state: string) =>
    api.post('/integrations/oauth/callback', null, {
      params: { code, state },
    }),

  disconnectOAuth: (integrationType: string) =>
    api.delete(`/integrations/oauth/${integrationType}`),
}

// Theming & White-Label API
export const themingApi = {
  // Themes
  listThemes: (params?: {
    workspace_id?: string;
    scope?: string;
    mode?: string;
    include_system?: boolean;
  }) => api.get('/theming/themes', { params }),

  createTheme: (data: {
    name: string;
    description?: string;
    mode?: string;
    scope?: string;
    colors?: Record<string, unknown>;
    dark_colors?: Record<string, unknown>;
    typography?: Record<string, unknown>;
    spacing?: Record<string, unknown>;
    border_radius?: Record<string, unknown>;
    shadows?: Record<string, unknown>;
    components?: Array<Record<string, unknown>>;
    custom_css?: string;
    workspace_id?: string;
  }) => api.post('/theming/themes', data),

  getTheme: (themeId: string) =>
    api.get(`/theming/themes/${themeId}`),

  updateTheme: (themeId: string, data: {
    name?: string;
    description?: string;
    mode?: string;
    colors?: Record<string, unknown>;
    dark_colors?: Record<string, unknown>;
    typography?: Record<string, unknown>;
    spacing?: Record<string, unknown>;
    border_radius?: Record<string, unknown>;
    shadows?: Record<string, unknown>;
    components?: Array<Record<string, unknown>>;
    custom_css?: string;
    is_default?: boolean;
  }) => api.patch(`/theming/themes/${themeId}`, data),

  deleteTheme: (themeId: string) =>
    api.delete(`/theming/themes/${themeId}`),

  duplicateTheme: (themeId: string, name: string) =>
    api.post(`/theming/themes/${themeId}/duplicate`, null, {
      params: { name },
    }),

  // Presets
  getPresets: () =>
    api.get('/theming/presets'),

  applyPreset: (themeId: string, presetId: string) =>
    api.post(`/theming/themes/${themeId}/apply-preset`, null, {
      params: { preset_id: presetId },
    }),

  // CSS Generation
  getThemeCSS: (themeId: string, minify?: boolean) =>
    api.get(`/theming/themes/${themeId}/css`, { params: { minify } }),

  getThemeCSSFile: (themeId: string, minify?: boolean) =>
    api.get(`/theming/themes/${themeId}/css.css`, {
      params: { minify },
      responseType: 'text',
    }),

  // Preview
  getThemePreview: (themeId: string) =>
    api.get(`/theming/themes/${themeId}/preview`),

  // Branding
  getBranding: (workspaceId: string) =>
    api.get(`/theming/branding/${workspaceId}`),

  createBranding: (data: {
    workspace_id: string;
    company_name: string;
    tagline?: string;
    primary_color?: string;
    secondary_color?: string;
    logo?: Record<string, unknown>;
  }) => api.post('/theming/branding', data),

  updateBranding: (workspaceId: string, data: {
    company_name?: string;
    tagline?: string;
    support_email?: string;
    support_url?: string;
    logo?: Record<string, unknown>;
    primary_color?: string;
    secondary_color?: string;
    custom_domain?: string;
    footer_text?: string;
    footer_links?: Array<Record<string, string>>;
    privacy_policy_url?: string;
    terms_of_service_url?: string;
    social_links?: Record<string, string>;
    email_from_name?: string;
    email_from_address?: string;
    hide_powered_by?: boolean;
    theme_id?: string;
  }) => api.patch(`/theming/branding/${workspaceId}`, data),

  deleteBranding: (workspaceId: string) =>
    api.delete(`/theming/branding/${workspaceId}`),

  verifyCustomDomain: (workspaceId: string) =>
    api.post(`/theming/branding/${workspaceId}/verify-domain`),

  // User Preferences
  getUserPreferences: () =>
    api.get('/theming/preferences'),

  updateUserPreferences: (params?: {
    mode?: string;
    theme_id?: string;
    font_size?: string;
    reduce_motion?: boolean;
    high_contrast?: boolean;
  }) => api.put('/theming/preferences', null, { params }),

  // Active Theme
  getActiveTheme: (workspaceId?: string) =>
    api.get('/theming/active', { params: { workspace_id: workspaceId } }),

  getActiveThemeCSS: (params?: {
    workspace_id?: string;
    minify?: boolean;
  }) => api.get('/theming/active/css.css', {
    params,
    responseType: 'text',
  }),
}

// Query Optimization API
export const queryOptimizationApi = {
  // Query Plans
  analyzePlan: (data: {
    sql: string;
    connection_id: string;
    explain_analyze?: boolean;
    explain_buffers?: boolean;
    explain_verbose?: boolean;
  }) => api.post('/query-optimization/plans/analyze', data),

  getPlan: (planId: string) =>
    api.get(`/query-optimization/plans/${planId}`),

  listPlans: (params?: {
    connection_id?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/query-optimization/plans', { params }),

  comparePlans: (params: {
    original_sql: string;
    optimized_sql: string;
    connection_id: string;
  }) => api.post('/query-optimization/plans/compare', null, { params }),

  deletePlan: (planId: string) =>
    api.delete(`/query-optimization/plans/${planId}`),

  // Cost Estimation
  estimateCost: (data: {
    sql: string;
    connection_id: string;
    include_components?: boolean;
  }) => api.post('/query-optimization/cost/estimate', data),

  estimateResources: (data: {
    sql: string;
    connection_id: string;
  }) => api.post('/query-optimization/cost/resources', data),

  // Optimization
  optimizeQuery: (params: {
    sql: string;
    connection_id: string;
    auto_apply?: boolean;
  }) => api.post('/query-optimization/optimize', null, { params }),

  getSuggestions: (queryHash: string) =>
    api.get(`/query-optimization/suggestions/${queryHash}`),

  applySuggestion: (suggestionId: string, queryHash: string) =>
    api.post(`/query-optimization/suggestions/${suggestionId}/apply`, null, {
      params: { query_hash: queryHash },
    }),

  dismissSuggestion: (suggestionId: string, queryHash: string) =>
    api.post(`/query-optimization/suggestions/${suggestionId}/dismiss`, null, {
      params: { query_hash: queryHash },
    }),

  // Index Suggestions
  getIndexSuggestions: (params?: {
    connection_id?: string;
    table_name?: string;
    limit?: number;
  }) => api.get('/query-optimization/indexes/suggestions', { params }),

  analyzeMissingIndexes: (connectionId: string) =>
    api.post('/query-optimization/indexes/analyze', null, {
      params: { connection_id: connectionId },
    }),

  // Query Rewrite
  rewriteQuery: (params: {
    sql: string;
    connection_id: string;
  }) => api.post('/query-optimization/rewrite', null, { params }),

  // Execution Tracking
  recordExecution: (data: {
    sql: string;
    connection_id: string;
    execution_time_ms: number;
    rows_returned: number;
    rows_scanned?: number;
    bytes_processed?: number;
    source_type?: string;
    source_id?: string;
    user_id?: string;
    workspace_id?: string;
    cached?: boolean;
    cache_hit?: boolean;
    status?: string;
    error_message?: string;
  }) => api.post('/query-optimization/executions', null, { params: data }),

  getPerformanceStats: (queryHash: string) =>
    api.get(`/query-optimization/executions/${queryHash}/stats`),

  // Slow Queries
  listSlowQueries: (params?: {
    connection_id?: string;
    source_type?: string;
    status?: string;
    min_execution_time_ms?: number;
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/query-optimization/slow-queries', { params }),

  getSlowQuery: (queryId: string) =>
    api.get(`/query-optimization/slow-queries/${queryId}`),

  optimizeSlowQuery: (queryId: string) =>
    api.post(`/query-optimization/slow-queries/${queryId}/optimize`),

  updateSlowQueryStatus: (queryId: string, status: string) =>
    api.put(`/query-optimization/slow-queries/${queryId}/status`, null, {
      params: { status },
    }),

  // Query History
  getHistory: (params?: {
    connection_id?: string;
    source_type?: string;
    user_id?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/query-optimization/history', { params }),

  getHistoryStats: (params?: {
    connection_id?: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/query-optimization/history/stats', { params }),

  deleteHistoryEntry: (entryId: string) =>
    api.delete(`/query-optimization/history/${entryId}`),

  clearHistory: (params?: {
    connection_id?: string;
    before_date?: string;
  }) => api.delete('/query-optimization/history', { params }),

  // Configuration
  getConfig: () =>
    api.get('/query-optimization/config'),

  updateConfig: (data: {
    slow_query_threshold_ms?: number;
    auto_analyze?: boolean;
    auto_suggest_indexes?: boolean;
    max_suggestions_per_query?: number;
    cache_plans?: boolean;
    plan_cache_ttl_seconds?: number;
    collect_statistics?: boolean;
    statistics_sample_rate?: number;
  }) => api.put('/query-optimization/config', data),

  // Dashboard
  getDashboardSummary: () =>
    api.get('/query-optimization/dashboard/summary'),

  getPerformanceTrends: (params?: {
    connection_id?: string;
    days?: number;
  }) => api.get('/query-optimization/dashboard/trends', { params }),
}

// Background Jobs API
export const backgroundJobsApi = {
  // Jobs
  createJob: (data: {
    name: string;
    job_type: string;
    priority?: string;
    payload?: Record<string, unknown>;
    scheduled_at?: string;
    timeout_seconds?: number;
    retry_policy_id?: string;
    workspace_id?: string;
    user_id?: string;
    tags?: string[];
    metadata?: Record<string, unknown>;
  }) => api.post('/jobs/jobs', data),

  listJobs: (params?: {
    status?: string;
    job_type?: string;
    priority?: string;
    workspace_id?: string;
    user_id?: string;
    tags?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/jobs/jobs', { params }),

  getJob: (jobId: string) =>
    api.get(`/jobs/jobs/${jobId}`),

  updateJob: (jobId: string, data: {
    status?: string;
    priority?: string;
    progress?: number;
    progress_message?: string;
    result?: Record<string, unknown>;
    error_message?: string;
    tags?: string[];
  }) => api.patch(`/jobs/jobs/${jobId}`, data),

  deleteJob: (jobId: string) =>
    api.delete(`/jobs/jobs/${jobId}`),

  cancelJob: (jobId: string) =>
    api.post(`/jobs/jobs/${jobId}/cancel`),

  retryJob: (jobId: string) =>
    api.post(`/jobs/jobs/${jobId}/retry`),

  updateJobProgress: (jobId: string, progress: number, message?: string) =>
    api.post(`/jobs/jobs/${jobId}/progress`, null, {
      params: { progress, message },
    }),

  startJob: (jobId: string, workerId: string) =>
    api.post(`/jobs/jobs/${jobId}/start`, null, {
      params: { worker_id: workerId },
    }),

  completeJob: (jobId: string, result: {
    status: string;
    result?: Record<string, unknown>;
    error_message?: string;
    error_details?: Record<string, unknown>;
    execution_time_ms: number;
    completed_at: string;
  }) => api.post(`/jobs/jobs/${jobId}/complete`, result),

  // Schedules
  createSchedule: (data: {
    name: string;
    description?: string;
    job_type: string;
    schedule_type: string;
    schedule_config: Record<string, unknown>;
    payload?: Record<string, unknown>;
    priority?: string;
    timeout_seconds?: number;
    retry_policy_id?: string;
    enabled?: boolean;
    workspace_id?: string;
    tags?: string[];
  }) => api.post('/jobs/schedules', data),

  listSchedules: (params?: {
    job_type?: string;
    enabled?: boolean;
    workspace_id?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/jobs/schedules', { params }),

  getSchedule: (scheduleId: string) =>
    api.get(`/jobs/schedules/${scheduleId}`),

  updateSchedule: (scheduleId: string, data: {
    name?: string;
    description?: string;
    schedule_type?: string;
    schedule_config?: Record<string, unknown>;
    payload?: Record<string, unknown>;
    priority?: string;
    timeout_seconds?: number;
    retry_policy_id?: string;
    enabled?: boolean;
    tags?: string[];
  }) => api.patch(`/jobs/schedules/${scheduleId}`, data),

  deleteSchedule: (scheduleId: string) =>
    api.delete(`/jobs/schedules/${scheduleId}`),

  runScheduleNow: (scheduleId: string) =>
    api.post(`/jobs/schedules/${scheduleId}/run`),

  enableSchedule: (scheduleId: string) =>
    api.post(`/jobs/schedules/${scheduleId}/enable`),

  disableSchedule: (scheduleId: string) =>
    api.post(`/jobs/schedules/${scheduleId}/disable`),

  getScheduleRuns: (scheduleId: string, limit?: number) =>
    api.get(`/jobs/schedules/${scheduleId}/runs`, { params: { limit } }),

  // Retry Policies
  createRetryPolicy: (data: {
    name: string;
    description?: string;
    strategy: string;
    max_retries?: number;
    initial_delay_seconds?: number;
    max_delay_seconds?: number;
    multiplier?: number;
    retry_on_statuses?: string[];
    retry_on_errors?: string[];
  }) => api.post('/jobs/retry-policies', data),

  listRetryPolicies: () =>
    api.get('/jobs/retry-policies'),

  getRetryPolicy: (policyId: string) =>
    api.get(`/jobs/retry-policies/${policyId}`),

  updateRetryPolicy: (policyId: string, data: {
    name?: string;
    description?: string;
    strategy?: string;
    max_retries?: number;
    initial_delay_seconds?: number;
    max_delay_seconds?: number;
    multiplier?: number;
    retry_on_statuses?: string[];
    retry_on_errors?: string[];
  }) => api.patch(`/jobs/retry-policies/${policyId}`, data),

  deleteRetryPolicy: (policyId: string) =>
    api.delete(`/jobs/retry-policies/${policyId}`),

  // Workers
  registerWorker: (params: {
    name: string;
    hostname: string;
    job_types: string;
    max_concurrent_jobs?: number;
  }) => api.post('/jobs/workers/register', null, { params }),

  listWorkers: (status?: string) =>
    api.get('/jobs/workers', { params: { status } }),

  workerHeartbeat: (workerId: string, data: {
    status: string;
    current_job_id?: string;
    memory_usage_mb?: number;
    cpu_usage_percent?: number;
  }) => api.post(`/jobs/workers/${workerId}/heartbeat`, null, { params: data }),

  unregisterWorker: (workerId: string) =>
    api.delete(`/jobs/workers/${workerId}`),

  getNextJobForWorker: (workerId: string) =>
    api.get(`/jobs/workers/${workerId}/next-job`),

  // History
  getJobHistory: (params?: {
    job_type?: string;
    status?: string;
    workspace_id?: string;
    user_id?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/jobs/history', { params }),

  getJobHistoryStats: (params?: {
    workspace_id?: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/jobs/history/stats', { params }),

  // Queues
  getQueueStats: (queueName: string) =>
    api.get(`/jobs/queues/${queueName}/stats`),

  getAllQueueStats: () =>
    api.get('/jobs/queues/stats'),

  // Dashboard
  getDashboard: () =>
    api.get('/jobs/dashboard'),

  // Configuration
  getConfig: () =>
    api.get('/jobs/config'),

  updateConfig: (data: {
    enabled?: boolean;
    max_workers?: number;
    default_timeout_seconds?: number;
    max_retry_attempts?: number;
    cleanup_completed_after_hours?: number;
    cleanup_failed_after_hours?: number;
    rate_limit_enabled?: boolean;
    rate_limit_per_minute?: number;
  }) => api.put('/jobs/config', data),

  // Cleanup
  cleanup: () =>
    api.post('/jobs/cleanup'),

  // Bulk Operations
  bulkCancelJobs: (jobIds: string[]) =>
    api.post('/jobs/jobs/bulk/cancel', jobIds),

  bulkRetryJobs: (jobIds: string[]) =>
    api.post('/jobs/jobs/bulk/retry', jobIds),

  bulkDeleteJobs: (jobIds: string[]) =>
    api.delete('/jobs/jobs/bulk', { data: jobIds }),
}

// Performance Monitoring API
export const performanceMonitoringApi = {
  // System Metrics
  getSystemMetrics: () =>
    api.get('/monitoring/system'),

  getProcessMetrics: () =>
    api.get('/monitoring/process'),

  // Request Metrics
  getRequestMetrics: () =>
    api.get('/monitoring/requests'),

  getEndpointMetrics: (limit?: number) =>
    api.get('/monitoring/requests/endpoints', { params: { limit } }),

  recordRequest: (data: {
    endpoint: string;
    method: string;
    status_code: number;
    latency_ms: number;
  }) => api.post('/monitoring/requests/record', null, { params: data }),

  // Database Metrics
  getDatabaseMetrics: (connectionId?: string) =>
    api.get('/monitoring/databases', { params: { connection_id: connectionId } }),

  getConnectionPoolMetrics: (connectionId: string) =>
    api.get(`/monitoring/databases/${connectionId}/pool`),

  // Cache Metrics
  getCacheMetrics: () =>
    api.get('/monitoring/cache'),

  // Metric Queries
  queryMetrics: (query: {
    metric_name: string;
    labels?: Record<string, string>;
    aggregation?: string;
    time_window?: string;
    start_time?: string;
    end_time?: string;
    step_seconds?: number;
  }) => api.post('/monitoring/metrics/query', query),

  getMetricStatistics: (metricName: string, timeWindow?: string) =>
    api.get(`/monitoring/metrics/${metricName}/stats`, {
      params: { time_window: timeWindow },
    }),

  recordMetric: (name: string, value: number, labels?: string) =>
    api.post('/monitoring/metrics/record', null, {
      params: { name, value, labels },
    }),

  // Alert Rules
  createAlertRule: (data: {
    name: string;
    description?: string;
    severity: string;
    category: string;
    thresholds: Array<{
      metric_name: string;
      operator: string;
      value: number;
      duration_seconds?: number;
      aggregation?: string;
      labels?: Record<string, string>;
    }>;
    notification_channels?: string[];
    cooldown_seconds?: number;
    enabled?: boolean;
    workspace_id?: string;
    tags?: string[];
  }) => api.post('/monitoring/alerts/rules', data),

  listAlertRules: (params?: {
    category?: string;
    severity?: string;
    enabled?: boolean;
    limit?: number;
    offset?: number;
  }) => api.get('/monitoring/alerts/rules', { params }),

  getAlertRule: (ruleId: string) =>
    api.get(`/monitoring/alerts/rules/${ruleId}`),

  updateAlertRule: (ruleId: string, data: {
    name?: string;
    description?: string;
    severity?: string;
    thresholds?: Array<Record<string, unknown>>;
    notification_channels?: string[];
    cooldown_seconds?: number;
    enabled?: boolean;
    tags?: string[];
  }) => api.patch(`/monitoring/alerts/rules/${ruleId}`, data),

  deleteAlertRule: (ruleId: string) =>
    api.delete(`/monitoring/alerts/rules/${ruleId}`),

  enableAlertRule: (ruleId: string) =>
    api.post(`/monitoring/alerts/rules/${ruleId}/enable`),

  disableAlertRule: (ruleId: string) =>
    api.post(`/monitoring/alerts/rules/${ruleId}/disable`),

  // Alerts
  listAlerts: (params?: {
    status?: string;
    severity?: string;
    rule_id?: string;
    limit?: number;
    offset?: number;
  }) => api.get('/monitoring/alerts', { params }),

  listActiveAlerts: (limit?: number) =>
    api.get('/monitoring/alerts/active', { params: { limit } }),

  getAlert: (alertId: string) =>
    api.get(`/monitoring/alerts/${alertId}`),

  acknowledgeAlert: (alertId: string, data: {
    user_id: string;
    comment?: string;
  }) => api.post(`/monitoring/alerts/${alertId}/acknowledge`, data),

  resolveAlert: (alertId: string) =>
    api.post(`/monitoring/alerts/${alertId}/resolve`),

  silenceAlert: (alertId: string, data: {
    duration_minutes: number;
    reason?: string;
  }) => api.post(`/monitoring/alerts/${alertId}/silence`, data),

  getAlertStatistics: () =>
    api.get('/monitoring/alerts/stats'),

  checkAlerts: () =>
    api.post('/monitoring/alerts/check'),

  // Dashboard
  getDashboard: () =>
    api.get('/monitoring/dashboard'),

  // Health
  getHealthStatus: () =>
    api.get('/monitoring/health'),

  livenessProbe: () =>
    api.get('/monitoring/health/live'),

  readinessProbe: () =>
    api.get('/monitoring/health/ready'),

  // Configuration
  getConfig: () =>
    api.get('/monitoring/config'),

  updateConfig: (data: {
    enabled?: boolean;
    collection_interval_seconds?: number;
    retention_days?: number;
    enable_system_metrics?: boolean;
    enable_application_metrics?: boolean;
    enable_database_metrics?: boolean;
    enable_cache_metrics?: boolean;
    slow_request_threshold_ms?: number;
    alert_cooldown_seconds?: number;
  }) => api.put('/monitoring/config', data),
}

// Workspace Management API
export const workspaceManagementApi = {
  // Workspaces
  createWorkspace: (data: {
    name: string;
    slug: string;
    description?: string;
    logo_url?: string;
    plan?: string;
    settings?: Record<string, unknown>;
    metadata?: Record<string, unknown>;
  }) => api.post('/workspace-mgmt/workspaces', data),

  listWorkspaces: (params?: {
    owner_only?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/workspace-mgmt/workspaces', { params }),

  getWorkspace: (workspaceId: string) =>
    api.get(`/workspace-mgmt/workspaces/${workspaceId}`),

  updateWorkspace: (workspaceId: string, data: {
    name?: string;
    description?: string;
    logo_url?: string;
    settings?: Record<string, unknown>;
    metadata?: Record<string, unknown>;
  }) => api.patch(`/workspace-mgmt/workspaces/${workspaceId}`, data),

  deleteWorkspace: (workspaceId: string) =>
    api.delete(`/workspace-mgmt/workspaces/${workspaceId}`),

  getWorkspaceSummary: (workspaceId: string) =>
    api.get(`/workspace-mgmt/workspaces/${workspaceId}/summary`),

  getUserWorkspaces: () =>
    api.get('/workspace-mgmt/workspaces/user/all'),

  // Workspace Settings
  getWorkspaceSettings: (workspaceId: string) =>
    api.get(`/workspace-mgmt/workspaces/${workspaceId}/settings`),

  updateWorkspaceSettings: (workspaceId: string, data: {
    allow_public_dashboards?: boolean;
    allow_public_links?: boolean;
    require_2fa?: boolean;
    default_member_role?: string;
    allowed_email_domains?: string[];
    ip_whitelist?: string[];
    session_timeout_minutes?: number;
    password_policy?: Record<string, unknown>;
    branding?: Record<string, unknown>;
    notification_settings?: Record<string, unknown>;
    data_retention_days?: number;
  }) => api.put(`/workspace-mgmt/workspaces/${workspaceId}/settings`, data),

  // Members
  addMember: (workspaceId: string, data: {
    user_id: string;
    role?: string;
    permissions?: Record<string, boolean>;
  }) => api.post(`/workspace-mgmt/workspaces/${workspaceId}/members`, data),

  listMembers: (workspaceId: string, params?: {
    role?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }) => api.get(`/workspace-mgmt/workspaces/${workspaceId}/members`, { params }),

  getMember: (workspaceId: string, memberId: string) =>
    api.get(`/workspace-mgmt/workspaces/${workspaceId}/members/${memberId}`),

  updateMember: (workspaceId: string, memberId: string, data: {
    role?: string;
    permissions?: Record<string, boolean>;
    status?: string;
  }) => api.patch(`/workspace-mgmt/workspaces/${workspaceId}/members/${memberId}`, data),

  removeMember: (workspaceId: string, memberId: string) =>
    api.delete(`/workspace-mgmt/workspaces/${workspaceId}/members/${memberId}`),

  // Invitations
  createInvitation: (workspaceId: string, data: {
    email: string;
    role?: string;
    message?: string;
    expires_in_days?: number;
  }) => api.post(`/workspace-mgmt/workspaces/${workspaceId}/invitations`, data),

  listInvitations: (workspaceId: string, params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }) => api.get(`/workspace-mgmt/workspaces/${workspaceId}/invitations`, { params }),

  getInvitation: (invitationId: string) =>
    api.get(`/workspace-mgmt/invitations/${invitationId}`),

  bulkInvite: (workspaceId: string, data: {
    emails: string[];
    role?: string;
    message?: string;
    expires_in_days?: number;
  }) => api.post(`/workspace-mgmt/workspaces/${workspaceId}/invitations/bulk`, data),

  acceptInvitation: (invitationId: string, userId?: string) =>
    api.post(`/workspace-mgmt/invitations/${invitationId}/accept`, { accept: true, user_id: userId }),

  declineInvitation: (invitationId: string) =>
    api.post(`/workspace-mgmt/invitations/${invitationId}/decline`, { accept: false }),

  cancelInvitation: (workspaceId: string, invitationId: string) =>
    api.post(`/workspace-mgmt/workspaces/${workspaceId}/invitations/${invitationId}/cancel`),

  resendInvitation: (workspaceId: string, invitationId: string) =>
    api.post(`/workspace-mgmt/workspaces/${workspaceId}/invitations/${invitationId}/resend`),

  // Quotas
  getQuota: (workspaceId: string) =>
    api.get(`/workspace-mgmt/workspaces/${workspaceId}/quota`),

  getQuotaUsage: (workspaceId: string) =>
    api.get(`/workspace-mgmt/workspaces/${workspaceId}/quota/usage`),

  checkQuota: (workspaceId: string, resourceType: string) =>
    api.get(`/workspace-mgmt/workspaces/${workspaceId}/quota/check`, {
      params: { resource_type: resourceType },
    }),

  // Teams
  createTeam: (workspaceId: string, data: {
    name: string;
    description?: string;
    color?: string;
    member_ids?: string[];
  }) => api.post(`/workspace-mgmt/workspaces/${workspaceId}/teams`, data),

  listTeams: (workspaceId: string, params?: {
    skip?: number;
    limit?: number;
  }) => api.get(`/workspace-mgmt/workspaces/${workspaceId}/teams`, { params }),

  getTeam: (workspaceId: string, teamId: string) =>
    api.get(`/workspace-mgmt/workspaces/${workspaceId}/teams/${teamId}`),

  updateTeam: (workspaceId: string, teamId: string, data: {
    name?: string;
    description?: string;
    color?: string;
    member_ids?: string[];
    permissions?: Record<string, boolean>;
  }) => api.patch(`/workspace-mgmt/workspaces/${workspaceId}/teams/${teamId}`, data),

  deleteTeam: (workspaceId: string, teamId: string) =>
    api.delete(`/workspace-mgmt/workspaces/${workspaceId}/teams/${teamId}`),

  addTeamMember: (workspaceId: string, teamId: string, memberId: string) =>
    api.post(`/workspace-mgmt/workspaces/${workspaceId}/teams/${teamId}/members/${memberId}`),

  removeTeamMember: (workspaceId: string, teamId: string, memberId: string) =>
    api.delete(`/workspace-mgmt/workspaces/${workspaceId}/teams/${teamId}/members/${memberId}`),

  // Activity
  getActivity: (workspaceId: string, params?: {
    user_id?: string;
    action?: string;
    resource_type?: string;
    skip?: number;
    limit?: number;
  }) => api.get(`/workspace-mgmt/workspaces/${workspaceId}/activity`, { params }),

  // Permissions
  checkPermission: (workspaceId: string, memberId: string, permission: string) =>
    api.get(`/workspace-mgmt/workspaces/${workspaceId}/permissions/check`, {
      params: { member_id: memberId, permission },
    }),

  getRolePermissions: (role: string) =>
    api.get(`/workspace-mgmt/permissions/roles/${role}`),

  // Plan Management
  upgradePlan: (workspaceId: string, plan: string) =>
    api.post(`/workspace-mgmt/workspaces/${workspaceId}/upgrade`, null, {
      params: { plan },
    }),

  startTrial: (workspaceId: string, plan: string, trialDays?: number) =>
    api.post(`/workspace-mgmt/workspaces/${workspaceId}/trial`, null, {
      params: { plan, trial_days: trialDays },
    }),

  cancelTrial: (workspaceId: string) =>
    api.post(`/workspace-mgmt/workspaces/${workspaceId}/trial/cancel`),
}

// User Management API
export const userManagementApi = {
  // Users
  createUser: (data: {
    email: string;
    password?: string;
    name: string;
    display_name?: string;
    avatar_url?: string;
    user_type?: string;
    auth_provider?: string;
    auth_provider_id?: string;
    phone?: string;
    timezone?: string;
    locale?: string;
    metadata?: Record<string, unknown>;
  }, createdBy?: string) =>
    api.post('/user-mgmt/users', data, { params: { created_by: createdBy } }),

  listUsers: (params?: {
    status?: string;
    user_type?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/user-mgmt/users', { params }),

  getUser: (userId: string) =>
    api.get(`/user-mgmt/users/${userId}`),

  getUserByEmail: (email: string) =>
    api.get(`/user-mgmt/users/email/${encodeURIComponent(email)}`),

  updateUser: (userId: string, data: {
    name?: string;
    display_name?: string;
    avatar_url?: string;
    phone?: string;
    timezone?: string;
    locale?: string;
    metadata?: Record<string, unknown>;
  }) => api.patch(`/user-mgmt/users/${userId}`, data),

  adminUpdateUser: (userId: string, data: {
    name?: string;
    display_name?: string;
    email?: string;
    user_type?: string;
    status?: string;
    email_verified?: boolean;
    phone_verified?: boolean;
    mfa_enabled?: boolean;
    metadata?: Record<string, unknown>;
  }, adminId: string) =>
    api.put(`/user-mgmt/users/${userId}/admin`, data, { params: { admin_id: adminId } }),

  deleteUser: (userId: string, deletedBy: string) =>
    api.delete(`/user-mgmt/users/${userId}`, { params: { deleted_by: deletedBy } }),

  getUserProfile: (userId: string) =>
    api.get(`/user-mgmt/users/${userId}/profile`),

  // User Preferences
  getUserPreferences: (userId: string) =>
    api.get(`/user-mgmt/users/${userId}/preferences`),

  updateUserPreferences: (userId: string, data: {
    theme?: string;
    language?: string;
    date_format?: string;
    time_format?: string;
    number_format?: string;
    first_day_of_week?: number;
    default_workspace_id?: string;
    notifications?: Record<string, boolean>;
    email_notifications?: Record<string, boolean>;
    dashboard_settings?: Record<string, unknown>;
    chart_defaults?: Record<string, unknown>;
  }) => api.put(`/user-mgmt/users/${userId}/preferences`, data),

  // Password Management
  changePassword: (userId: string, data: {
    current_password: string;
    new_password: string;
  }, ipAddress?: string) =>
    api.post(`/user-mgmt/users/${userId}/password/change`, data, {
      params: { ip_address: ipAddress },
    }),

  getPasswordPolicy: () =>
    api.get('/user-mgmt/password/policy'),

  // MFA
  setupMFA: (userId: string) =>
    api.post(`/user-mgmt/users/${userId}/mfa/setup`),

  enableMFA: (userId: string, code: string) =>
    api.post(`/user-mgmt/users/${userId}/mfa/enable`, { code }),

  disableMFA: (userId: string, code: string) =>
    api.post(`/user-mgmt/users/${userId}/mfa/disable`, { code }),

  verifyMFA: (userId: string, code: string) =>
    api.post(`/user-mgmt/users/${userId}/mfa/verify`, { code }),

  regenerateBackupCodes: (userId: string) =>
    api.post(`/user-mgmt/users/${userId}/mfa/backup-codes`),

  // Roles
  createRole: (data: {
    name: string;
    description?: string;
    scope?: string;
    permissions?: string[];
    is_system?: boolean;
    workspace_id?: string;
    metadata?: Record<string, unknown>;
  }, createdBy: string) =>
    api.post('/user-mgmt/roles', data, { params: { created_by: createdBy } }),

  listRoles: (params?: {
    scope?: string;
    workspace_id?: string;
    include_system?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/user-mgmt/roles', { params }),

  getRole: (roleId: string) =>
    api.get(`/user-mgmt/roles/${roleId}`),

  updateRole: (roleId: string, data: {
    name?: string;
    description?: string;
    permissions?: string[];
    metadata?: Record<string, unknown>;
  }) => api.patch(`/user-mgmt/roles/${roleId}`, data),

  deleteRole: (roleId: string) =>
    api.delete(`/user-mgmt/roles/${roleId}`),

  // Role Assignment
  assignRole: (data: {
    user_id: string;
    role_id: string;
    workspace_id?: string;
    expires_at?: string;
  }, assignedBy: string) =>
    api.post('/user-mgmt/roles/assign', data, { params: { assigned_by: assignedBy } }),

  revokeRole: (assignmentId: string, revokedBy: string) =>
    api.delete(`/user-mgmt/roles/assignments/${assignmentId}`, {
      params: { revoked_by: revokedBy },
    }),

  getUserRoles: (userId: string, workspaceId?: string) =>
    api.get(`/user-mgmt/users/${userId}/roles`, { params: { workspace_id: workspaceId } }),

  // Permissions
  getAllPermissions: () =>
    api.get('/user-mgmt/permissions'),

  getUserPermissions: (userId: string, workspaceId?: string) =>
    api.get(`/user-mgmt/users/${userId}/permissions`, {
      params: { workspace_id: workspaceId },
    }),

  checkUserPermission: (userId: string, permission: string, workspaceId?: string) =>
    api.get(`/user-mgmt/users/${userId}/permissions/check`, {
      params: { permission, workspace_id: workspaceId },
    }),

  // Sessions
  createSession: (data: {
    user_id: string;
    device_info?: Record<string, unknown>;
    ip_address?: string;
    user_agent?: string;
  }, expiresInHours?: number) =>
    api.post('/user-mgmt/sessions', data, { params: { expires_in_hours: expiresInHours } }),

  getSession: (sessionId: string) =>
    api.get(`/user-mgmt/sessions/${sessionId}`),

  updateSessionActivity: (sessionId: string) =>
    api.post(`/user-mgmt/sessions/${sessionId}/activity`),

  revokeSession: (sessionId: string, reason?: string) =>
    api.post(`/user-mgmt/sessions/${sessionId}/revoke`, null, { params: { reason } }),

  getUserSessions: (userId: string, currentSessionId?: string) =>
    api.get(`/user-mgmt/users/${userId}/sessions`, {
      params: { current_session_id: currentSessionId },
    }),

  revokeAllUserSessions: (userId: string, exceptSessionId?: string) =>
    api.post(`/user-mgmt/users/${userId}/sessions/revoke-all`, null, {
      params: { except_session_id: exceptSessionId },
    }),

  // Audit Logs
  getAuditLogs: (params?: {
    user_id?: string;
    action?: string;
    resource_type?: string;
    success?: boolean;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/user-mgmt/audit', { params }),

  getUserAuditLogs: (userId: string, params?: {
    action?: string;
    skip?: number;
    limit?: number;
  }) => api.get(`/user-mgmt/users/${userId}/audit`, { params }),

  // Statistics
  getUserStatistics: () =>
    api.get('/user-mgmt/statistics'),

  // Login Tracking
  logLoginAttempt: (params: {
    email: string;
    success: boolean;
    ip_address?: string;
    user_agent?: string;
    error_message?: string;
  }) => api.post('/user-mgmt/auth/login-attempt', null, { params }),
}

// Billing API
export const billingApi = {
  // Plans
  listPlans: (includePrivate?: boolean) =>
    api.get('/billing/plans', { params: { include_private: includePrivate } }),

  getPlan: (planId: string) =>
    api.get(`/billing/plans/${planId}`),

  getPlanComparison: () =>
    api.get('/billing/plans/compare'),

  // Subscriptions
  createSubscription: (data: {
    workspace_id: string;
    plan_id: string;
    billing_interval?: string;
    payment_method_id?: string;
    coupon_code?: string;
    trial_days?: number;
  }) => api.post('/billing/subscriptions', data),

  getSubscription: (subscriptionId: string) =>
    api.get(`/billing/subscriptions/${subscriptionId}`),

  getWorkspaceSubscription: (workspaceId: string) =>
    api.get(`/billing/workspaces/${workspaceId}/subscription`),

  updateSubscription: (subscriptionId: string, data: {
    plan_id?: string;
    billing_interval?: string;
    payment_method_id?: string;
    quantity?: number;
    coupon_code?: string;
    cancel_at_period_end?: boolean;
  }) => api.patch(`/billing/subscriptions/${subscriptionId}`, data),

  cancelSubscription: (subscriptionId: string, immediate?: boolean) =>
    api.post(`/billing/subscriptions/${subscriptionId}/cancel`, null, {
      params: { immediate },
    }),

  reactivateSubscription: (subscriptionId: string) =>
    api.post(`/billing/subscriptions/${subscriptionId}/reactivate`),

  previewSubscriptionChange: (subscriptionId: string, newPlanId: string) =>
    api.get(`/billing/subscriptions/${subscriptionId}/preview-change`, {
      params: { new_plan_id: newPlanId },
    }),

  getSubscriptionUsage: (subscriptionId: string) =>
    api.get(`/billing/subscriptions/${subscriptionId}/usage`),

  // Invoices
  listInvoices: (workspaceId: string, params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }) => api.get(`/billing/workspaces/${workspaceId}/invoices`, { params }),

  getInvoice: (invoiceId: string) =>
    api.get(`/billing/invoices/${invoiceId}`),

  payInvoice: (invoiceId: string, paymentMethodId?: string) =>
    api.post(`/billing/invoices/${invoiceId}/pay`, null, {
      params: { payment_method_id: paymentMethodId },
    }),

  // Payment Methods
  addPaymentMethod: (workspaceId: string, data: {
    type: string;
    is_default?: boolean;
    card_number?: string;
    card_exp_month?: number;
    card_exp_year?: number;
    card_cvc?: string;
    billing_name?: string;
    billing_email?: string;
    billing_address?: Record<string, string>;
  }) => api.post(`/billing/workspaces/${workspaceId}/payment-methods`, data),

  listPaymentMethods: (workspaceId: string) =>
    api.get(`/billing/workspaces/${workspaceId}/payment-methods`),

  deletePaymentMethod: (paymentMethodId: string) =>
    api.delete(`/billing/payment-methods/${paymentMethodId}`),

  setDefaultPaymentMethod: (workspaceId: string, paymentMethodId: string) =>
    api.post(`/billing/workspaces/${workspaceId}/payment-methods/${paymentMethodId}/default`),

  // Usage
  recordUsage: (workspaceId: string, metricType: string, quantity: number, metadata?: Record<string, unknown>) =>
    api.post(`/billing/workspaces/${workspaceId}/usage`, null, {
      params: { metric_type: metricType, quantity, metadata: metadata ? JSON.stringify(metadata) : undefined },
    }),

  getUsageSummary: (workspaceId: string, params?: {
    start_date?: string;
    end_date?: string;
  }) => api.get(`/billing/workspaces/${workspaceId}/usage`, { params }),

  // Usage Alerts
  createUsageAlert: (workspaceId: string, data: {
    metric_type: string;
    threshold_percent: number;
    notification_channels?: string[];
  }) => api.post(`/billing/workspaces/${workspaceId}/usage-alerts`, data),

  listUsageAlerts: (workspaceId: string) =>
    api.get(`/billing/workspaces/${workspaceId}/usage-alerts`),

  deleteUsageAlert: (alertId: string) =>
    api.delete(`/billing/usage-alerts/${alertId}`),

  // Credits
  addCredit: (workspaceId: string, params: {
    amount: number;
    credit_type: string;
    description?: string;
    expires_at?: string;
  }) => api.post(`/billing/workspaces/${workspaceId}/credits`, null, { params }),

  getCreditBalance: (workspaceId: string) =>
    api.get(`/billing/workspaces/${workspaceId}/credits`),

  // Coupons
  validateCoupon: (code: string, planId?: string) =>
    api.post('/billing/coupons/validate', null, { params: { code, plan_id: planId } }),

  createCoupon: (params: {
    code: string;
    name: string;
    discount_type: string;
    discount_value: number;
    duration?: string;
    duration_months?: number;
    max_redemptions?: number;
    valid_until?: string;
  }) => api.post('/billing/coupons', null, { params }),

  // Billing Settings
  getBillingSettings: (workspaceId: string) =>
    api.get(`/billing/workspaces/${workspaceId}/billing-settings`),

  updateBillingSettings: (workspaceId: string, data: {
    billing_email?: string;
    billing_name?: string;
    billing_address?: Record<string, string>;
    tax_id?: string;
    tax_id_type?: string;
    auto_collection?: boolean;
    invoice_prefix?: string;
    default_payment_method_id?: string;
  }) => api.put(`/billing/workspaces/${workspaceId}/billing-settings`, data),

  // Billing Overview
  getBillingOverview: (workspaceId: string) =>
    api.get(`/billing/workspaces/${workspaceId}/billing`),

  createBillingPortalSession: (workspaceId: string, returnUrl: string) =>
    api.post(`/billing/workspaces/${workspaceId}/billing/portal`, null, {
      params: { return_url: returnUrl },
    }),
}

// Admin Dashboard API
export const adminDashboardApi = {
  // Dashboard Summary
  getDashboardSummary: () =>
    api.get('/admin/dashboard'),

  getDashboardConfig: (adminId: string) =>
    api.get('/admin/dashboard/config', { params: { admin_id: adminId } }),

  updateDashboardConfig: (adminId: string, config: {
    widgets: Array<{
      id: string;
      type: string;
      title: string;
      size: string;
      position: number;
      config?: Record<string, unknown>;
      refresh_interval_seconds?: number;
    }>;
    refresh_interval_seconds?: number;
    theme?: string;
  }) => api.put('/admin/dashboard/config', config, { params: { admin_id: adminId } }),

  // System Health
  getSystemHealth: () =>
    api.get('/admin/health'),

  getResourceUsage: () =>
    api.get('/admin/resources'),

  // Key Metrics
  getKeyMetrics: () =>
    api.get('/admin/metrics'),

  // Statistics
  getUserStats: (timeRange?: string) =>
    api.get('/admin/stats/users', { params: { time_range: timeRange } }),

  getSessionStats: () =>
    api.get('/admin/stats/sessions'),

  getWorkspaceStats: (timeRange?: string) =>
    api.get('/admin/stats/workspaces', { params: { time_range: timeRange } }),

  getRevenueStats: (timeRange?: string) =>
    api.get('/admin/stats/revenue', { params: { time_range: timeRange } }),

  getSubscriptionStats: () =>
    api.get('/admin/stats/subscriptions'),

  getPlatformUsageStats: () =>
    api.get('/admin/stats/usage'),

  // Alerts
  listAlerts: (params?: {
    level?: string;
    acknowledged?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/admin/alerts', { params }),

  getAlertSummary: () =>
    api.get('/admin/alerts/summary'),

  createAlert: (params: {
    level: string;
    title: string;
    message: string;
    source?: string;
  }) => api.post('/admin/alerts', null, { params }),

  acknowledgeAlert: (alertId: string, adminId: string) =>
    api.post(`/admin/alerts/${alertId}/acknowledge`, null, {
      params: { admin_id: adminId },
    }),

  resolveAlert: (alertId: string) =>
    api.post(`/admin/alerts/${alertId}/resolve`),

  // Admin Activity
  listAdminActivities: (params?: {
    admin_id?: string;
    action?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/admin/activity', { params }),

  getRecentActivity: () =>
    api.get('/admin/activity/recent'),

  logAdminActivity: (params: {
    admin_id: string;
    admin_name: string;
    action: string;
    target_type: string;
    target_id?: string;
    target_name?: string;
    ip_address?: string;
  }) => api.post('/admin/activity/log', null, { params }),

  // System Configuration
  getSystemConfig: () =>
    api.get('/admin/config'),

  updateSystemConfig: (data: {
    maintenance_mode?: boolean;
    maintenance_message?: string;
    registration_enabled?: boolean;
    public_signup_enabled?: boolean;
    default_plan_id?: string;
    max_workspaces_per_user?: number;
    trial_days?: number;
    session_timeout_hours?: number;
    password_policy?: Record<string, unknown>;
    email_verification_required?: boolean;
    mfa_required_for_admins?: boolean;
    allowed_email_domains?: string[];
    blocked_email_domains?: string[];
    rate_limits?: Record<string, number>;
    feature_flags?: Record<string, boolean>;
  }, adminId: string) =>
    api.put('/admin/config', data, { params: { admin_id: adminId } }),

  enableMaintenanceMode: (adminId: string, message?: string) =>
    api.post('/admin/config/maintenance/enable', null, {
      params: { admin_id: adminId, message },
    }),

  disableMaintenanceMode: (adminId: string) =>
    api.post('/admin/config/maintenance/disable', null, {
      params: { admin_id: adminId },
    }),

  // Quick Actions
  getQuickActions: () =>
    api.get('/admin/actions'),

  executeQuickAction: (actionId: string, adminId: string, parameters?: Record<string, unknown>) =>
    api.post(`/admin/actions/${actionId}/execute`, null, {
      params: {
        admin_id: adminId,
        parameters: parameters ? JSON.stringify(parameters) : undefined,
      },
    }),

  // Reports
  generateReport: (params: {
    report_type: string;
    name: string;
    format?: string;
    time_range?: string;
    admin_id: string;
    parameters?: Record<string, unknown>;
  }) => api.post('/admin/reports', null, {
    params: {
      ...params,
      parameters: params.parameters ? JSON.stringify(params.parameters) : undefined,
    },
  }),

  listReports: (params?: {
    report_type?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/admin/reports', { params }),

  downloadReport: (reportId: string) =>
    api.get(`/admin/reports/${reportId}/download`, { responseType: 'blob' }),
}

// Two-Factor Authentication API
export const twoFactorAuthApi = {
  // MFA Status
  getMFAStatus: (userId: string) =>
    api.get(`/2fa/users/${userId}/mfa/status`),

  getMFAConfig: (userId: string) =>
    api.get(`/2fa/users/${userId}/mfa/config`),

  updateMFAConfig: (userId: string, data: {
    primary_method?: string;
    recovery_email?: string;
  }) => api.patch(`/2fa/users/${userId}/mfa/config`, data),

  // TOTP (Authenticator App)
  setupTOTP: (userId: string, userEmail: string) =>
    api.post(`/2fa/users/${userId}/mfa/totp/setup`, null, {
      params: { user_email: userEmail },
    }),

  verifyTOTPSetup: (userId: string, data: {
    setup_token: string;
    code: string;
  }, ipAddress?: string) =>
    api.post(`/2fa/users/${userId}/mfa/totp/verify-setup`, data, {
      params: { ip_address: ipAddress },
    }),

  verifyTOTP: (userId: string, code: string) =>
    api.post(`/2fa/users/${userId}/mfa/totp/verify`, null, {
      params: { code },
    }),

  disableTOTP: (userId: string, code: string) =>
    api.post(`/2fa/users/${userId}/mfa/totp/disable`, null, {
      params: { code },
    }),

  // SMS MFA
  setupSMS: (userId: string, phoneNumber: string) =>
    api.post(`/2fa/users/${userId}/mfa/sms/setup`, { phone_number: phoneNumber }),

  verifySMSSetup: (userId: string, data: {
    setup_token: string;
    code: string;
  }, ipAddress?: string) =>
    api.post(`/2fa/users/${userId}/mfa/sms/verify-setup`, data, {
      params: { ip_address: ipAddress },
    }),

  sendSMSCode: (userId: string) =>
    api.post(`/2fa/users/${userId}/mfa/sms/send`),

  verifySMS: (userId: string, token: string, code: string) =>
    api.post(`/2fa/users/${userId}/mfa/sms/verify`, null, {
      params: { token, code },
    }),

  // Email MFA
  setupEmailMFA: (userId: string, email: string) =>
    api.post(`/2fa/users/${userId}/mfa/email/setup`, null, {
      params: { email },
    }),

  verifyEmailMFASetup: (userId: string, data: {
    setup_token: string;
    code: string;
  }, ipAddress?: string) =>
    api.post(`/2fa/users/${userId}/mfa/email/verify-setup`, data, {
      params: { ip_address: ipAddress },
    }),

  sendEmailCode: (userId: string) =>
    api.post(`/2fa/users/${userId}/mfa/email/send`),

  verifyEmailMFA: (userId: string, token: string, code: string) =>
    api.post(`/2fa/users/${userId}/mfa/email/verify`, null, {
      params: { token, code },
    }),

  // Backup Codes
  regenerateBackupCodes: (userId: string) =>
    api.post(`/2fa/users/${userId}/mfa/backup-codes/regenerate`),

  verifyBackupCode: (userId: string, code: string) =>
    api.post(`/2fa/users/${userId}/mfa/backup-codes/verify`, { code }),

  // Trusted Devices
  listTrustedDevices: (userId: string) =>
    api.get(`/2fa/users/${userId}/mfa/devices`),

  trustDevice: (userId: string, data: {
    device_id: string;
    name?: string;
    trust_duration_days?: number;
  }, deviceInfo?: {
    device_type?: string;
    browser?: string;
    os?: string;
    ip_address?: string;
  }) => api.post(`/2fa/users/${userId}/mfa/devices/trust`, data, {
    params: deviceInfo,
  }),

  checkDeviceTrust: (userId: string, deviceId: string) =>
    api.get(`/2fa/users/${userId}/mfa/devices/${deviceId}/check`),

  revokeDeviceTrust: (userId: string, deviceId: string) =>
    api.delete(`/2fa/users/${userId}/mfa/devices/${deviceId}`),

  // MFA Challenge Flow
  createMFAChallenge: (userId: string, deviceInfo?: {
    device_id?: string;
    device_type?: string;
    browser?: string;
    os?: string;
  }) => api.post('/2fa/mfa/challenge', null, {
    params: { user_id: userId, ...deviceInfo },
  }),

  verifyMFAChallenge: (challengeId: string, response: {
    challenge_id: string;
    method: string;
    code?: string;
    webauthn_response?: Record<string, unknown>;
    trust_device?: boolean;
    trust_duration_days?: number;
  }, ipAddress?: string) =>
    api.post(`/2fa/mfa/challenge/${challengeId}/verify`, response, {
      params: { ip_address: ipAddress },
    }),

  // Recovery
  initiateRecovery: (userId: string, method: string, email?: string) =>
    api.post(`/2fa/users/${userId}/mfa/recovery/initiate`, null, {
      params: { method, email },
    }),

  completeRecovery: (token: string) =>
    api.post('/2fa/mfa/recovery/complete', null, {
      params: { token },
    }),

  // MFA Policy (Organization)
  getMFAPolicy: (orgId: string) =>
    api.get(`/2fa/organizations/${orgId}/mfa/policy`),

  updateMFAPolicy: (orgId: string, data: {
    mfa_required?: boolean;
    allowed_methods?: string[];
    require_backup_codes?: boolean;
    max_trusted_devices?: number;
    trust_device_max_days?: number;
    grace_period_days?: number;
    enforce_for_admins?: boolean;
    enforce_for_api_access?: boolean;
    remember_device_option?: boolean;
    bypass_for_internal_ips?: boolean;
    internal_ip_ranges?: string[];
  }) => api.put(`/2fa/organizations/${orgId}/mfa/policy`, data),

  // MFA Events
  getMFAEvents: (userId: string, params?: {
    skip?: number;
    limit?: number;
  }) => api.get(`/2fa/users/${userId}/mfa/events`, { params }),
}

// Security Controls API
export const securityControlsApi = {
  // Rate Limiting
  createRateLimitRule: (data: {
    name: string;
    description?: string;
    scope: string;
    endpoint_pattern?: string;
    requests_per_minute?: number;
    requests_per_hour?: number;
    requests_per_day?: number;
    burst_limit?: number;
    action?: string;
    retry_after_seconds?: number;
    enabled?: boolean;
    priority?: number;
    exemptions?: string[];
  }) => api.post('/security/rate-limits', data),

  listRateLimitRules: (params?: { skip?: number; limit?: number }) =>
    api.get('/security/rate-limits', { params }),

  getRateLimitRule: (ruleId: string) =>
    api.get(`/security/rate-limits/${ruleId}`),

  updateRateLimitRule: (ruleId: string, data: {
    name?: string;
    description?: string;
    endpoint_pattern?: string;
    requests_per_minute?: number;
    requests_per_hour?: number;
    requests_per_day?: number;
    burst_limit?: number;
    action?: string;
    retry_after_seconds?: number;
    enabled?: boolean;
    priority?: number;
    exemptions?: string[];
  }) => api.patch(`/security/rate-limits/${ruleId}`, data),

  deleteRateLimitRule: (ruleId: string) =>
    api.delete(`/security/rate-limits/${ruleId}`),

  checkRateLimit: (params: {
    ip_address: string;
    endpoint: string;
    user_id?: string;
    api_key?: string;
  }) => api.post('/security/rate-limits/check', null, { params }),

  // IP Policies
  createIPRule: (data: {
    list_type: string;
    match_type: string;
    value: string;
    description?: string;
    organization_id?: string;
    expires_at?: string;
    enabled?: boolean;
  }, createdBy: string) =>
    api.post('/security/ip-rules', data, { params: { created_by: createdBy } }),

  listIPRules: (params?: {
    list_type?: string;
    organization_id?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/security/ip-rules', { params }),

  getIPRule: (ruleId: string) =>
    api.get(`/security/ip-rules/${ruleId}`),

  updateIPRule: (ruleId: string, data: {
    description?: string;
    expires_at?: string;
    enabled?: boolean;
  }) => api.patch(`/security/ip-rules/${ruleId}`, data),

  deleteIPRule: (ruleId: string) =>
    api.delete(`/security/ip-rules/${ruleId}`),

  checkIP: (ipAddress: string, organizationId?: string) =>
    api.post('/security/ip-rules/check', null, {
      params: { ip_address: ipAddress, organization_id: organizationId },
    }),

  // Session Security
  getSessionConfig: (orgId: string) =>
    api.get(`/security/organizations/${orgId}/session-config`),

  updateSessionConfig: (orgId: string, data: {
    max_concurrent_sessions?: number;
    session_timeout_minutes?: number;
    idle_timeout_minutes?: number;
    require_reauthentication_minutes?: number;
    bind_to_ip?: boolean;
    bind_to_device?: boolean;
    detect_concurrent_logins?: boolean;
    terminate_other_sessions_on_login?: boolean;
    require_mfa_for_new_device?: boolean;
    high_risk_actions_require_reauth?: boolean;
  }) => api.patch(`/security/organizations/${orgId}/session-config`, data),

  listUserSessions: (userId: string, currentSessionId?: string) =>
    api.get(`/security/users/${userId}/sessions`, {
      params: { current_session_id: currentSessionId },
    }),

  createSession: (params: {
    user_id: string;
    ip_address: string;
    user_agent: string;
    device_type?: string;
    browser?: string;
    os?: string;
  }) => api.post('/security/sessions', null, { params }),

  terminateSession: (sessionId: string) =>
    api.delete(`/security/sessions/${sessionId}`),

  terminateAllSessions: (userId: string, exceptSessionId?: string) =>
    api.post(`/security/users/${userId}/sessions/terminate-all`, null, {
      params: { except_session_id: exceptSessionId },
    }),

  updateSessionActivity: (sessionId: string) =>
    api.post(`/security/sessions/${sessionId}/activity`),

  // Password Policies
  getPasswordPolicy: (orgId: string) =>
    api.get(`/security/organizations/${orgId}/password-policy`),

  updatePasswordPolicy: (orgId: string, data: {
    min_length?: number;
    max_length?: number;
    require_uppercase?: boolean;
    require_lowercase?: boolean;
    require_numbers?: boolean;
    require_special_chars?: boolean;
    special_chars_allowed?: string;
    disallow_common_passwords?: boolean;
    disallow_personal_info?: boolean;
    password_history_count?: number;
    max_age_days?: number;
    min_age_days?: number;
    lockout_threshold?: number;
    lockout_duration_minutes?: number;
    require_password_change_on_first_login?: boolean;
  }) => api.patch(`/security/organizations/${orgId}/password-policy`, data),

  validatePassword: (orgId: string, params: {
    password: string;
    user_id?: string;
    user_email?: string;
    user_name?: string;
  }) => api.post(`/security/organizations/${orgId}/password/validate`, null, { params }),

  checkPasswordStrength: (data: {
    password: string;
    user_email?: string;
    user_name?: string;
  }) => api.post('/security/password/strength', data),

  // API Keys
  createAPIKey: (data: {
    name: string;
    description?: string;
    permissions?: string[];
    rate_limit_override?: number;
    allowed_ips?: string[];
    allowed_origins?: string[];
    expires_at?: string;
  }, userId: string, organizationId?: string) =>
    api.post('/security/api-keys', data, {
      params: { user_id: userId, organization_id: organizationId },
    }),

  listAPIKeys: (params?: {
    user_id?: string;
    organization_id?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/security/api-keys', { params }),

  getAPIKey: (keyId: string) =>
    api.get(`/security/api-keys/${keyId}`),

  updateAPIKey: (keyId: string, data: {
    name?: string;
    description?: string;
    permissions?: string[];
    rate_limit_override?: number;
    allowed_ips?: string[];
    allowed_origins?: string[];
    expires_at?: string;
  }) => api.patch(`/security/api-keys/${keyId}`, data),

  revokeAPIKey: (keyId: string, revokedBy: string) =>
    api.post(`/security/api-keys/${keyId}/revoke`, null, {
      params: { revoked_by: revokedBy },
    }),

  validateAPIKey: (key: string) =>
    api.post('/security/api-keys/validate', null, { params: { key } }),

  getAPIKeyUsage: (keyId: string) =>
    api.get(`/security/api-keys/${keyId}/usage`),

  // Security Events
  listSecurityEvents: (params?: {
    event_type?: string;
    user_id?: string;
    organization_id?: string;
    risk_level?: string;
    success?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/security/events', { params }),

  logSecurityEvent: (params: {
    event_type: string;
    ip_address: string;
    success: boolean;
    user_id?: string;
    organization_id?: string;
    resource_type?: string;
    resource_id?: string;
    action?: string;
    user_agent?: string;
    risk_level?: string;
  }) => api.post('/security/events', null, { params }),

  // CORS & Security Headers
  getCORSConfig: (orgId: string) =>
    api.get(`/security/organizations/${orgId}/cors`),

  updateCORSConfig: (orgId: string, data: {
    allowed_origins?: string[];
    allowed_methods?: string[];
    allowed_headers?: string[];
    exposed_headers?: string[];
    allow_credentials?: boolean;
    max_age_seconds?: number;
    enabled?: boolean;
  }) => api.patch(`/security/organizations/${orgId}/cors`, data),

  getCSPConfig: (orgId: string) =>
    api.get(`/security/organizations/${orgId}/csp`),

  updateCSPConfig: (orgId: string, data: {
    default_src?: string[];
    script_src?: string[];
    style_src?: string[];
    img_src?: string[];
    font_src?: string[];
    connect_src?: string[];
    frame_src?: string[];
    object_src?: string[];
    base_uri?: string[];
    form_action?: string[];
    report_uri?: string;
    report_only?: boolean;
    enabled?: boolean;
  }) => api.patch(`/security/organizations/${orgId}/csp`, data),

  getSecurityHeaders: (orgId: string) =>
    api.get(`/security/organizations/${orgId}/security-headers`),

  updateSecurityHeaders: (orgId: string, data: {
    x_frame_options?: string;
    x_content_type_options?: string;
    x_xss_protection?: string;
    strict_transport_security?: string;
    referrer_policy?: string;
    permissions_policy?: string;
    custom_headers?: Record<string, string>;
    enabled?: boolean;
  }) => api.patch(`/security/organizations/${orgId}/security-headers`, data),

  // Security Overview
  getSecurityOverview: (orgId: string) =>
    api.get(`/security/organizations/${orgId}/overview`),

  getSecurityRecommendations: (orgId: string) =>
    api.get(`/security/organizations/${orgId}/recommendations`),
}

// Compliance API
export const complianceApi = {
  // Consent Management
  getConsentPreferences: (userId: string) =>
    api.get(`/compliance/users/${userId}/consent`),

  updateConsent: (userId: string, data: {
    consent_type: string;
    status: string;
    version: string;
    ip_address?: string;
    user_agent?: string;
    source?: string;
  }, changedBy?: string) =>
    api.post(`/compliance/users/${userId}/consent`, data, {
      params: { changed_by: changedBy },
    }),

  updateConsentBulk: (userId: string, consents: Array<{
    consent_type: string;
    status: string;
    version: string;
    ip_address?: string;
    user_agent?: string;
    source?: string;
  }>) => api.post(`/compliance/users/${userId}/consent/bulk`, { consents }),

  withdrawAllConsent: (userId: string, ipAddress?: string) =>
    api.post(`/compliance/users/${userId}/consent/withdraw-all`, null, {
      params: { ip_address: ipAddress },
    }),

  listConsentRecords: (params?: {
    user_id?: string;
    consent_type?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/compliance/consent/records', { params }),

  getConsentAuditLogs: (params?: {
    user_id?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/compliance/consent/audit', { params }),

  // Data Subject Requests (DSR)
  createDSR: (userId: string, data: {
    request_type: string;
    email: string;
    description?: string;
    data_categories?: string[];
  }) => api.post('/compliance/dsr', data, { params: { user_id: userId } }),

  listDSRs: (params?: {
    user_id?: string;
    status?: string;
    request_type?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/compliance/dsr', { params }),

  getOverdueDSRs: () =>
    api.get('/compliance/dsr/overdue'),

  getDSR: (requestId: string) =>
    api.get(`/compliance/dsr/${requestId}`),

  updateDSR: (requestId: string, data: {
    status?: string;
    identity_verified?: boolean;
    verification_method?: string;
    rejection_reason?: string;
    response_extended?: boolean;
    extension_reason?: string;
  }, updatedBy: string) =>
    api.patch(`/compliance/dsr/${requestId}`, data, {
      params: { updated_by: updatedBy },
    }),

  // Retention Policies
  createRetentionPolicy: (data: {
    name: string;
    description?: string;
    data_category: string;
    classification: string;
    retention_days: number;
    action: string;
    legal_basis: string;
    organization_id?: string;
    applies_to_tables?: string[];
    applies_to_fields?: string[];
    enabled?: boolean;
  }) => api.post('/compliance/retention-policies', data),

  listRetentionPolicies: (params?: {
    organization_id?: string;
    data_category?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/compliance/retention-policies', { params }),

  getRetentionPolicy: (policyId: string) =>
    api.get(`/compliance/retention-policies/${policyId}`),

  updateRetentionPolicy: (policyId: string, data: {
    name?: string;
    description?: string;
    retention_days?: number;
    action?: string;
    legal_basis?: string;
    legal_hold?: boolean;
    applies_to_tables?: string[];
    applies_to_fields?: string[];
    enabled?: boolean;
  }) => api.patch(`/compliance/retention-policies/${policyId}`, data),

  deleteRetentionPolicy: (policyId: string) =>
    api.delete(`/compliance/retention-policies/${policyId}`),

  executeRetentionPolicy: (policyId: string) =>
    api.post(`/compliance/retention-policies/${policyId}/execute`),

  // Processing Activities
  createProcessingActivity: (orgId: string, data: {
    name: string;
    description: string;
    purpose: string;
    legal_basis: string;
    data_categories: string[];
    data_subjects: string[];
    recipients: string[];
    third_country_transfers?: string[];
    transfer_safeguards?: string;
    retention_period: string;
    security_measures?: string[];
    dpia_required?: boolean;
    controller_name: string;
    controller_contact: string;
    processor_name?: string;
    processor_contact?: string;
    dpo_contact?: string;
  }) => api.post(`/compliance/organizations/${orgId}/processing-activities`, data),

  listProcessingActivities: (orgId: string, params?: {
    skip?: number;
    limit?: number;
  }) => api.get(`/compliance/organizations/${orgId}/processing-activities`, { params }),

  getProcessingActivity: (activityId: string) =>
    api.get(`/compliance/processing-activities/${activityId}`),

  // Encryption
  getEncryptionConfig: (orgId: string) =>
    api.get(`/compliance/organizations/${orgId}/encryption`),

  updateEncryptionConfig: (orgId: string, data: {
    encrypt_at_rest?: boolean;
    encrypt_in_transit?: boolean;
    encrypt_pii?: boolean;
    default_algorithm?: string;
    key_rotation_days?: number;
    auto_rotate_keys?: boolean;
    pii_fields?: string[];
  }) => api.patch(`/compliance/organizations/${orgId}/encryption`, data),

  createEncryptionKey: (orgId: string, name: string, purpose: string) =>
    api.post(`/compliance/organizations/${orgId}/encryption/keys`, null, {
      params: { name, purpose },
    }),

  listEncryptionKeys: (orgId: string) =>
    api.get(`/compliance/organizations/${orgId}/encryption/keys`),

  // Privacy Documents
  createPrivacyDocument: (data: {
    document_type: string;
    version: string;
    title: string;
    content: string;
    effective_date: string;
    organization_id?: string;
    locale?: string;
    changelog?: string;
    requires_acceptance?: boolean;
  }) => api.post('/compliance/privacy-documents', data),

  listPrivacyDocuments: (params?: {
    document_type?: string;
    organization_id?: string;
    published_only?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/compliance/privacy-documents', { params }),

  getCurrentPrivacyDocument: (documentType: string, organizationId?: string, locale?: string) =>
    api.get('/compliance/privacy-documents/current', {
      params: { document_type: documentType, organization_id: organizationId, locale },
    }),

  getPrivacyDocument: (docId: string) =>
    api.get(`/compliance/privacy-documents/${docId}`),

  publishPrivacyDocument: (docId: string) =>
    api.post(`/compliance/privacy-documents/${docId}/publish`),

  // Anonymization
  createAnonymizationRule: (data: {
    name: string;
    description?: string;
    field_name: string;
    table_name: string;
    technique: string;
    parameters?: Record<string, unknown>;
    preserve_format?: boolean;
    reversible?: boolean;
    enabled?: boolean;
    organization_id?: string;
  }) => api.post('/compliance/anonymization-rules', data),

  listAnonymizationRules: (params?: {
    organization_id?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/compliance/anonymization-rules', { params }),

  // Data Breaches
  reportDataBreach: (orgId: string, data: {
    title: string;
    description: string;
    severity: string;
    affected_records: number;
    affected_data_types: string[];
    affected_users: number;
    discovery_date: string;
    occurred_date?: string;
  }) => api.post(`/compliance/organizations/${orgId}/breaches`, data),

  listDataBreaches: (orgId: string, params?: {
    resolved?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get(`/compliance/organizations/${orgId}/breaches`, { params }),

  getDataBreach: (breachId: string) =>
    api.get(`/compliance/breaches/${breachId}`),

  updateDataBreach: (breachId: string, data: {
    contained_date?: string;
    resolved_date?: string;
    reported_to_authority?: boolean;
    authority_report_date?: string;
    users_notified?: boolean;
    notification_date?: string;
    root_cause?: string;
    remediation_steps?: string[];
  }) => api.patch(`/compliance/breaches/${breachId}`, data),

  // Compliance Status
  getComplianceStatus: (orgId: string) =>
    api.get(`/compliance/organizations/${orgId}/status`),

  listComplianceAuditLogs: (params?: {
    resource_type?: string;
    user_id?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/compliance/audit-logs', { params }),

  // User Data (GDPR Rights)
  exportUserData: (userId: string) =>
    api.get(`/compliance/users/${userId}/export`),

  deleteUserData: (userId: string) =>
    api.delete(`/compliance/users/${userId}/data`),
}

// Security Audit API
export const securityAuditApi = {
  // Audit Logs
  createAuditLog: (data: {
    category: string;
    severity: string;
    action: string;
    resource_type: string;
    resource_id?: string;
    user_id?: string;
    user_email?: string;
    organization_id?: string;
    ip_address: string;
    user_agent?: string;
    session_id?: string;
    success: boolean;
    error_code?: string;
    error_message?: string;
    old_value?: Record<string, unknown>;
    new_value?: Record<string, unknown>;
    metadata?: Record<string, unknown>;
  }) => api.post('/security-audit/audit-logs', data),

  listAuditLogs: (params?: {
    category?: string;
    severity?: string;
    action?: string;
    resource_type?: string;
    user_id?: string;
    organization_id?: string;
    ip_address?: string;
    success?: boolean;
    start_time?: string;
    end_time?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/security-audit/audit-logs', { params }),

  getAuditLog: (logId: string) =>
    api.get(`/security-audit/audit-logs/${logId}`),

  // Threat Intelligence
  createThreatIndicator: (data: {
    threat_type: string;
    severity: string;
    indicator_type: string;
    indicator_value: string;
    description?: string;
    source?: string;
    confidence?: number;
    tags?: string[];
    expires_at?: string;
  }) => api.post('/security-audit/threat-indicators', data),

  listThreatIndicators: (params?: {
    threat_type?: string;
    active_only?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/security-audit/threat-indicators', { params }),

  getThreatIndicator: (indicatorId: string) =>
    api.get(`/security-audit/threat-indicators/${indicatorId}`),

  checkIndicator: (indicatorType: string, value: string) =>
    api.post('/security-audit/threat-indicators/check', null, {
      params: { indicator_type: indicatorType, value },
    }),

  // Threat Detection
  listThreatDetections: (params?: {
    organization_id?: string;
    status?: string;
    severity?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/security-audit/threats', { params }),

  getThreatDetection: (detectionId: string) =>
    api.get(`/security-audit/threats/${detectionId}`),

  updateThreatDetection: (detectionId: string, params: {
    status?: string;
    assigned_to?: string;
    resolution_notes?: string;
  }) => api.patch(`/security-audit/threats/${detectionId}`, null, { params }),

  // Anomaly Detection
  detectAnomaly: (params: {
    anomaly_type: string;
    description: string;
    actual_value: string;
    deviation_score: number;
    user_id?: string;
    organization_id?: string;
    ip_address?: string;
    expected_value?: string;
  }) => api.post('/security-audit/anomalies', null, { params }),

  listAnomalies: (params?: {
    organization_id?: string;
    user_id?: string;
    anomaly_type?: string;
    investigated?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/security-audit/anomalies', { params }),

  investigateAnomaly: (anomalyId: string, investigatedBy: string, falsePositive?: boolean) =>
    api.post(`/security-audit/anomalies/${anomalyId}/investigate`, null, {
      params: { investigated_by: investigatedBy, false_positive: falsePositive },
    }),

  // Security Incidents
  createIncident: (data: {
    title: string;
    description: string;
    incident_type: string;
    priority: string;
    severity: string;
    organization_id: string;
    affected_systems?: string[];
    affected_users?: string[];
    attack_vectors?: string[];
  }, reportedBy: string) =>
    api.post('/security-audit/incidents', data, { params: { reported_by: reportedBy } }),

  listIncidents: (params?: {
    organization_id?: string;
    status?: string;
    priority?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/security-audit/incidents', { params }),

  getIncident: (incidentId: string) =>
    api.get(`/security-audit/incidents/${incidentId}`),

  updateIncident: (incidentId: string, data: {
    title?: string;
    description?: string;
    status?: string;
    priority?: string;
    assigned_to?: string;
    affected_systems?: string[];
    affected_users?: string[];
    containment_actions?: string[];
    remediation_actions?: string[];
    lessons_learned?: string;
  }, updatedBy: string) =>
    api.patch(`/security-audit/incidents/${incidentId}`, data, {
      params: { updated_by: updatedBy },
    }),

  addIncidentNote: (incidentId: string, note: string, user: string) =>
    api.post(`/security-audit/incidents/${incidentId}/notes`, null, {
      params: { note, user },
    }),

  // Vulnerability Management
  createVulnerability: (data: {
    cve_id?: string;
    title: string;
    description: string;
    severity: string;
    cvss_score?: number;
    affected_component: string;
    affected_versions?: string[];
    organization_id?: string;
    discovered_by: string;
    remediation_steps?: string[];
    references?: string[];
  }) => api.post('/security-audit/vulnerabilities', data),

  listVulnerabilities: (params?: {
    organization_id?: string;
    status?: string;
    severity?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/security-audit/vulnerabilities', { params }),

  getVulnerability: (vulnId: string) =>
    api.get(`/security-audit/vulnerabilities/${vulnId}`),

  updateVulnerability: (vulnId: string, data: {
    status?: string;
    assigned_to?: string;
    due_date?: string;
    remediation_steps?: string[];
    workaround?: string;
    patch_available?: boolean;
    patch_version?: string;
  }) => api.patch(`/security-audit/vulnerabilities/${vulnId}`, data),

  // Security Alerts
  listAlerts: (params?: {
    organization_id?: string;
    severity?: string;
    acknowledged?: boolean;
    resolved?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/security-audit/alerts', { params }),

  acknowledgeAlert: (alertId: string, acknowledgedBy: string) =>
    api.post(`/security-audit/alerts/${alertId}/acknowledge`, null, {
      params: { acknowledged_by: acknowledgedBy },
    }),

  resolveAlert: (alertId: string) =>
    api.post(`/security-audit/alerts/${alertId}/resolve`),

  // Security Metrics
  getSecurityMetrics: (orgId: string) =>
    api.get(`/security-audit/organizations/${orgId}/metrics`),

  getSecurityScorecard: (orgId: string) =>
    api.get(`/security-audit/organizations/${orgId}/scorecard`),
}

// Export API
export const exportApi = {
  // Export Jobs
  createExportJob: (data: {
    export_type: string;
    format: string;
    source_id: string;
    filename?: string;
    pdf_config?: Record<string, unknown>;
    excel_config?: Record<string, unknown>;
    powerpoint_config?: Record<string, unknown>;
    image_config?: Record<string, unknown>;
    csv_config?: Record<string, unknown>;
    json_config?: Record<string, unknown>;
    filters?: Record<string, unknown>;
    parameters?: Record<string, unknown>;
    notify_on_completion?: boolean;
    notification_email?: string;
  }, userId: string, organizationId?: string) =>
    api.post('/export/jobs', data, {
      params: { user_id: userId, organization_id: organizationId },
    }),

  listExportJobs: (params?: {
    user_id?: string;
    organization_id?: string;
    status?: string;
    format?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/export/jobs', { params }),

  getExportJob: (jobId: string) =>
    api.get(`/export/jobs/${jobId}`),

  updateExportJob: (jobId: string, data: {
    status?: string;
    progress?: number;
    file_size?: number;
    file_url?: string;
    error_message?: string;
  }) => api.patch(`/export/jobs/${jobId}`, data),

  cancelExportJob: (jobId: string) =>
    api.post(`/export/jobs/${jobId}/cancel`),

  deleteExportJob: (jobId: string) =>
    api.delete(`/export/jobs/${jobId}`),

  downloadExport: (jobId: string) =>
    api.get(`/export/jobs/${jobId}/download`),

  cleanupExpiredExports: () =>
    api.post('/export/cleanup'),

  // Quick Export
  quickExportPDF: (sourceId: string, exportType: string, userId: string, organizationId?: string) =>
    api.post('/export/quick/pdf', null, {
      params: { source_id: sourceId, export_type: exportType, user_id: userId, organization_id: organizationId },
    }),

  quickExportExcel: (sourceId: string, exportType: string, userId: string, organizationId?: string) =>
    api.post('/export/quick/excel', null, {
      params: { source_id: sourceId, export_type: exportType, user_id: userId, organization_id: organizationId },
    }),

  quickExportImage: (sourceId: string, format: string, exportType: string, userId: string, organizationId?: string) =>
    api.post('/export/quick/image', null, {
      params: { source_id: sourceId, format, export_type: exportType, user_id: userId, organization_id: organizationId },
    }),

  // Export Presets
  createExportPreset: (data: {
    name: string;
    description?: string;
    export_type: string;
    format: string;
    config: Record<string, unknown>;
    is_default?: boolean;
    is_shared?: boolean;
  }, userId: string, organizationId?: string) =>
    api.post('/export/presets', data, {
      params: { user_id: userId, organization_id: organizationId },
    }),

  listExportPresets: (params?: {
    user_id?: string;
    organization_id?: string;
    export_type?: string;
    format?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/export/presets', { params }),

  getDefaultPreset: (userId: string, exportType: string, format: string) =>
    api.get('/export/presets/default', {
      params: { user_id: userId, export_type: exportType, format },
    }),

  getExportPreset: (presetId: string) =>
    api.get(`/export/presets/${presetId}`),

  updateExportPreset: (presetId: string, params: {
    name?: string;
    description?: string;
    is_default?: boolean;
    is_shared?: boolean;
  }) => api.patch(`/export/presets/${presetId}`, null, { params }),

  deleteExportPreset: (presetId: string) =>
    api.delete(`/export/presets/${presetId}`),

  // Export History
  getExportHistory: (params?: {
    user_id?: string;
    organization_id?: string;
    format?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/export/history', { params }),

  // Export Statistics
  getExportStats: (organizationId: string) =>
    api.get(`/export/stats/${organizationId}`),

  // Export Formats Info
  getExportFormats: () =>
    api.get('/export/formats'),
}

// Report Templates API
export const reportTemplatesApi = {
  // Templates CRUD
  createTemplate: (data: {
    name: string;
    description?: string;
    template_type: string;
    category?: string;
    tags?: string[];
    pages?: any[];
    theme?: any;
    default_filters?: Record<string, unknown>;
    default_parameters?: Record<string, unknown>;
    is_public?: boolean;
  }, userId: string, organizationId?: string) =>
    api.post('/report-templates/', data, {
      params: { user_id: userId, organization_id: organizationId },
    }),

  listTemplates: (params?: {
    user_id?: string;
    organization_id?: string;
    template_type?: string;
    status?: string;
    category?: string;
    is_public?: boolean;
    search?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/report-templates/', { params }),

  listSystemTemplates: (templateType?: string, skip?: number, limit?: number) =>
    api.get('/report-templates/system', {
      params: { template_type: templateType, skip, limit },
    }),

  getTemplate: (templateId: string) =>
    api.get(`/report-templates/${templateId}`),

  updateTemplate: (templateId: string, data: {
    name?: string;
    description?: string;
    category?: string;
    tags?: string[];
    pages?: any[];
    theme?: any;
    default_filters?: Record<string, unknown>;
    default_parameters?: Record<string, unknown>;
    status?: string;
    is_public?: boolean;
  }, userId: string) =>
    api.patch(`/report-templates/${templateId}`, data, {
      params: { user_id: userId },
    }),

  deleteTemplate: (templateId: string) =>
    api.delete(`/report-templates/${templateId}`),

  duplicateTemplate: (templateId: string, userId: string, newName?: string, organizationId?: string) =>
    api.post(`/report-templates/${templateId}/duplicate`, null, {
      params: { user_id: userId, new_name: newName, organization_id: organizationId },
    }),

  publishTemplate: (templateId: string, userId: string) =>
    api.post(`/report-templates/${templateId}/publish`, null, {
      params: { user_id: userId },
    }),

  archiveTemplate: (templateId: string, userId: string) =>
    api.post(`/report-templates/${templateId}/archive`, null, {
      params: { user_id: userId },
    }),

  // Template Versions
  listVersions: (templateId: string, skip?: number, limit?: number) =>
    api.get(`/report-templates/${templateId}/versions`, {
      params: { skip, limit },
    }),

  getVersion: (versionId: string) =>
    api.get(`/report-templates/versions/${versionId}`),

  restoreVersion: (templateId: string, versionId: string, userId: string) =>
    api.post(`/report-templates/${templateId}/versions/${versionId}/restore`, null, {
      params: { user_id: userId },
    }),

  // Categories
  listCategories: (parentId?: string) =>
    api.get('/report-templates/categories/', {
      params: { parent_id: parentId },
    }),

  createCategory: (data: {
    name: string;
    description?: string;
    icon?: string;
    parent_id?: string;
    order?: number;
  }) => api.post('/report-templates/categories/', data),

  deleteCategory: (categoryId: string) =>
    api.delete(`/report-templates/categories/${categoryId}`),

  // Template Instances
  createInstance: (data: {
    template_id: string;
    name: string;
    placeholder_values?: Record<string, unknown>;
    filters?: Record<string, unknown>;
    parameters?: Record<string, unknown>;
  }, userId: string, organizationId?: string) =>
    api.post('/report-templates/instances', data, {
      params: { user_id: userId, organization_id: organizationId },
    }),

  listInstances: (params?: {
    user_id?: string;
    organization_id?: string;
    template_id?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/report-templates/instances', { params }),

  getInstance: (instanceId: string) =>
    api.get(`/report-templates/instances/${instanceId}`),

  updateInstance: (instanceId: string, params?: {
    placeholder_values?: Record<string, unknown>;
    filters?: Record<string, unknown>;
    parameters?: Record<string, unknown>;
  }) => api.patch(`/report-templates/instances/${instanceId}`, null, { params }),

  deleteInstance: (instanceId: string) =>
    api.delete(`/report-templates/instances/${instanceId}`),
}

// Scheduled Reports API
export const scheduledReportsApi = {
  // Schedule CRUD
  createSchedule: (data: {
    name: string;
    description?: string;
    source_config: any;
    recurrence: any;
    delivery_configs: any[];
    date_range: any;
    is_active?: boolean;
    notify_on_failure?: boolean;
    failure_notification_emails?: string[];
    tags?: string[];
  }, userId: string, organizationId?: string) =>
    api.post('/scheduled-reports/', data, {
      params: { user_id: userId, organization_id: organizationId },
    }),

  listSchedules: (params?: {
    user_id?: string;
    organization_id?: string;
    status?: string;
    is_active?: boolean;
    source_type?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/scheduled-reports/', { params }),

  getDueSchedules: () =>
    api.get('/scheduled-reports/due'),

  getSchedule: (scheduleId: string) =>
    api.get(`/scheduled-reports/${scheduleId}`),

  updateSchedule: (scheduleId: string, data: {
    name?: string;
    description?: string;
    source_config?: any;
    recurrence?: any;
    delivery_configs?: any[];
    date_range?: any;
    is_active?: boolean;
    status?: string;
    notify_on_failure?: boolean;
    failure_notification_emails?: string[];
    tags?: string[];
  }) => api.patch(`/scheduled-reports/${scheduleId}`, data),

  deleteSchedule: (scheduleId: string) =>
    api.delete(`/scheduled-reports/${scheduleId}`),

  pauseSchedule: (scheduleId: string) =>
    api.post(`/scheduled-reports/${scheduleId}/pause`),

  resumeSchedule: (scheduleId: string) =>
    api.post(`/scheduled-reports/${scheduleId}/resume`),

  triggerExecution: (scheduleId: string) =>
    api.post(`/scheduled-reports/${scheduleId}/trigger`),

  // Executions
  listExecutions: (params?: {
    schedule_id?: string;
    user_id?: string;
    organization_id?: string;
    status?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/scheduled-reports/executions/', { params }),

  getExecution: (executionId: string) =>
    api.get(`/scheduled-reports/executions/${executionId}`),

  cancelExecution: (executionId: string) =>
    api.post(`/scheduled-reports/executions/${executionId}/cancel`),

  retryExecution: (executionId: string) =>
    api.post(`/scheduled-reports/executions/${executionId}/retry`),

  // Processing
  processDueSchedules: () =>
    api.post('/scheduled-reports/process-due'),

  // Statistics
  getScheduleStats: (organizationId: string) =>
    api.get(`/scheduled-reports/stats/${organizationId}`),
}

// Report Subscriptions API
export const reportSubscriptionsApi = {
  // Subscription CRUD
  createSubscription: (data: {
    resource_type: string;
    resource_id: string;
    resource_name?: string;
    subscription_type: string;
    notification_channels: any[];
    schedule?: any;
    digest_config?: any;
    threshold_conditions?: any[];
    filters?: Record<string, unknown>;
    is_active?: boolean;
    expires_at?: string;
  }, userId: string, organizationId?: string) =>
    api.post('/subscriptions/', data, {
      params: { user_id: userId, organization_id: organizationId },
    }),

  listSubscriptions: (params?: {
    user_id?: string;
    organization_id?: string;
    resource_type?: string;
    resource_id?: string;
    subscription_type?: string;
    status?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/subscriptions/', { params }),

  getSubscription: (subscriptionId: string) =>
    api.get(`/subscriptions/${subscriptionId}`),

  updateSubscription: (subscriptionId: string, data: {
    resource_name?: string;
    subscription_type?: string;
    notification_channels?: any[];
    schedule?: any;
    digest_config?: any;
    threshold_conditions?: any[];
    filters?: Record<string, unknown>;
    is_active?: boolean;
    status?: string;
    expires_at?: string;
  }) => api.patch(`/subscriptions/${subscriptionId}`, data),

  deleteSubscription: (subscriptionId: string) =>
    api.delete(`/subscriptions/${subscriptionId}`),

  pauseSubscription: (subscriptionId: string) =>
    api.post(`/subscriptions/${subscriptionId}/pause`),

  resumeSubscription: (subscriptionId: string) =>
    api.post(`/subscriptions/${subscriptionId}/resume`),

  // Notifications
  listNotifications: (params?: {
    user_id?: string;
    subscription_id?: string;
    resource_type?: string;
    unread_only?: boolean;
    skip?: number;
    limit?: number;
  }) => api.get('/subscriptions/notifications/', { params }),

  getNotification: (notificationId: string) =>
    api.get(`/subscriptions/notifications/${notificationId}`),

  markNotificationRead: (notificationId: string) =>
    api.post(`/subscriptions/notifications/${notificationId}/read`),

  markAllNotificationsRead: (userId: string) =>
    api.post('/subscriptions/notifications/mark-all-read', null, {
      params: { user_id: userId },
    }),

  recordNotificationClick: (notificationId: string) =>
    api.post(`/subscriptions/notifications/${notificationId}/click`),

  // Digests
  listDigests: (userId: string, params?: {
    digest_type?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/subscriptions/digests/', {
    params: { user_id: userId, ...params },
  }),

  getDigest: (digestId: string) =>
    api.get(`/subscriptions/digests/${digestId}`),

  sendDigest: (digestId: string) =>
    api.post(`/subscriptions/digests/${digestId}/send`),

  // User Preferences
  getUserPreferences: (userId: string) =>
    api.get(`/subscriptions/preferences/${userId}`),

  updateUserPreferences: (userId: string, params?: {
    global_preferences?: any;
    channel_preferences?: Record<string, boolean>;
    resource_preferences?: Record<string, boolean>;
    muted_resources?: string[];
  }) => api.put(`/subscriptions/preferences/${userId}`, null, { params }),

  muteResource: (userId: string, resourceId: string) =>
    api.post(`/subscriptions/preferences/${userId}/mute/${resourceId}`),

  unmuteResource: (userId: string, resourceId: string) =>
    api.post(`/subscriptions/preferences/${userId}/unmute/${resourceId}`),

  // Statistics
  getSubscriptionStats: (organizationId: string) =>
    api.get(`/subscriptions/stats/${organizationId}`),

  // Threshold Processing
  processThresholds: (resourceType: string, resourceId: string, currentValues: Record<string, number>, previousValues?: Record<string, number>) =>
    api.post('/subscriptions/process-thresholds', null, {
      params: {
        resource_type: resourceType,
        resource_id: resourceId,
        current_values: JSON.stringify(currentValues),
        previous_values: previousValues ? JSON.stringify(previousValues) : undefined,
      },
    }),
}

// BheemFlow API instance for workflow operations
export const bheemFlowApi = axios.create({
  baseURL: import.meta.env.VITE_BHEEMFLOW_API_URL || 'https://platform.bheem.co.uk/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// BheemFlow API interceptors
bheemFlowApi.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

bheemFlowApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('BheemFlow API 401 - user may not have platform access')
    }
    return Promise.reject(error)
  }
)

// Workflows API - BheemFlow integration
const MODULE = 'dataviz'
const getWorkspaceId = () => localStorage.getItem('workspace_id') || 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'

export const workflowsApi = {
  list: () => bheemFlowApi.get(`/workflows?module=${MODULE}&workspace_id=${getWorkspaceId()}`),
  get: (id: string) => bheemFlowApi.get(`/workflows/${id}`),
  create: (data: any) => bheemFlowApi.post('/workflows', { ...data, module: MODULE, workspace_id: getWorkspaceId() }),
  update: (id: string, data: any) => bheemFlowApi.put(`/workflows/${id}`, data),
  delete: (id: string) => bheemFlowApi.delete(`/workflows/${id}`),
  execute: (id: string, variables?: any) => bheemFlowApi.post(`/workflows/${id}/execute`, { variables, triggered_by: 'manual' }),
  getExecution: (id: string) => bheemFlowApi.get(`/executions/${id}`),
  getExecutions: (workflowId: string, limit?: number) => bheemFlowApi.get('/executions', {
    params: { workflow_id: workflowId, module: MODULE, workspace_id: getWorkspaceId(), limit: limit || 10 }
  }),
  cancelExecution: (id: string) => bheemFlowApi.post(`/executions/${id}/cancel`),
  getNodeTypes: () => bheemFlowApi.get(`/node-types?module=${MODULE}`),
  getAnalytics: (days?: number) => bheemFlowApi.get('/analytics/overview', {
    params: { module: MODULE, workspace_id: getWorkspaceId(), days: days || 7 }
  }),
}

// Data Profiler API
export const profilerApi = {
  // Get list of connections that support profiling
  getConnections: () => api.get('/profiler/connections'),

  // Get list of tables for a connection
  getTables: (connectionId: string) => api.get(`/profiler/connections/${connectionId}/tables`),

  // Profile a specific table
  profileTable: (connectionId: string, schema: string, table: string, sampleSize?: number) =>
    api.get(`/profiler/profile/${connectionId}/${schema}/${table}`, {
      params: { sample_size: sampleSize || 10000 }
    }),
}

// Default export for backward compatibility
export default api
