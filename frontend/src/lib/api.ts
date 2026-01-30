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
  list: () => api.get('/datasets'),
  get: (id: string) => api.get(`/datasets/${id}`),
  create: (data: any) => api.post('/datasets', data),
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
