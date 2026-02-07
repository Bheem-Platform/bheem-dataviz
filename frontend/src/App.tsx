import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/common/Layout'
import { PrivateRoute, PublicRoute } from './components/auth/PrivateRoute'
import { HomePage } from './pages/HomePage'
import { DashboardList } from './pages/DashboardList'
import { DashboardBuilder } from './pages/DashboardBuilder'
import { DataConnections } from './pages/DataConnections'
import { Datasets } from './pages/Datasets'
import { ChartBuilder } from './pages/ChartBuilder'
import { TransformBuilder } from './pages/TransformBuilder'
import { SemanticModels } from './pages/SemanticModels'
import { KPIs } from './pages/KPIs'
import { AIChat } from './pages/AIChat'
import { ChartGallery } from './pages/ChartGallery'
import { Explore } from './pages/Explore'
import { SQLLab } from './pages/SQLLab'
import { KodeeAnalytics } from './pages/KodeeAnalytics'
import { Workflows } from './pages/Workflows'
import { QuickCharts } from './pages/QuickCharts'
import { LandingPage } from './pages/LandingPage'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { OAuthCallback } from './pages/OAuthCallback'
import FilterPresets from './pages/FilterPresets'
import TimeIntelligence from './pages/TimeIntelligence'
import RowLevelSecurity from './pages/RowLevelSecurity'
import ScheduledRefresh from './pages/ScheduledRefresh'
import QuickInsights from './pages/QuickInsights'
import Workspaces from './pages/Workspaces'
import AuditLogs from './pages/AuditLogs'
import EmbedManager from './pages/EmbedManager'
import CacheManager from './pages/CacheManager'
import DataProfiler from './pages/DataProfiler'
// New Phase 1-10 pages
import AdminDashboard from './pages/AdminDashboard'
import Billing from './pages/Billing'
import Reports from './pages/Reports'
import UserManagement from './pages/UserManagement'
import Theming from './pages/Theming'
import Plugins from './pages/Plugins'
import Integrations from './pages/Integrations'
import PerformanceMonitor from './pages/PerformanceMonitor'
import Compliance from './pages/Compliance'
import SecuritySettings from './pages/SecuritySettings'
import Subscriptions from './pages/Subscriptions'
// Governance Pages
import DataGovernance from './pages/DataGovernance'
import DeploymentPipelines from './pages/DeploymentPipelines'
import DataLineage from './pages/DataLineage'
import VersionControl from './pages/VersionControl'
import DataQuality from './pages/DataQuality'
import SchemaTracking from './pages/SchemaTracking'
import AppBundling from './pages/AppBundling'
import UserAnalyticsDashboard from './pages/UserAnalyticsDashboard'

function App() {
  return (
    <Routes>
      {/* Landing Page - Public */}
      <Route path="/" element={<LandingPage />} />

      {/* Auth Routes - Public only (redirect if authenticated) */}
      <Route element={<PublicRoute />}>
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
      </Route>

      {/* OAuth Callback - Always accessible */}
      <Route path="auth/callback" element={<OAuthCallback />} />

      {/* Protected App Routes - Require authentication */}
      <Route element={<PrivateRoute />}>
        <Route element={<Layout />}>
          {/* Core Pages */}
          <Route path="home" element={<HomePage />} />
          <Route path="dashboards" element={<DashboardList />} />
          <Route path="dashboards/new" element={<DashboardBuilder />} />
          <Route path="dashboards/:id" element={<DashboardBuilder />} />
          <Route path="quick-charts" element={<QuickCharts />} />
          <Route path="gallery" element={<ChartGallery />} />
          <Route path="explore" element={<Explore />} />
          <Route path="sql-lab" element={<SQLLab />} />
          <Route path="kodee" element={<KodeeAnalytics />} />
          <Route path="workflows" element={<Workflows />} />

          {/* Data Management */}
          <Route path="connections" element={<DataConnections />} />
          <Route path="datasets" element={<Datasets />} />
          <Route path="transforms" element={<TransformBuilder />} />
          <Route path="transforms/:id" element={<TransformBuilder />} />
          <Route path="models" element={<SemanticModels />} />
          <Route path="models/:id" element={<SemanticModels />} />
          <Route path="kpis" element={<KPIs />} />

          {/* Advanced Features */}
          <Route path="filters" element={<FilterPresets />} />
          <Route path="time-intelligence" element={<TimeIntelligence />} />
          <Route path="rls" element={<RowLevelSecurity />} />
          <Route path="schedules" element={<ScheduledRefresh />} />
          <Route path="insights" element={<QuickInsights />} />

          {/* Enterprise Features */}
          <Route path="workspaces" element={<Workspaces />} />
          <Route path="audit" element={<AuditLogs />} />
          <Route path="embed" element={<EmbedManager />} />
          <Route path="cache" element={<CacheManager />} />
          <Route path="profiler" element={<DataProfiler />} />

          {/* Reports & Subscriptions */}
          <Route path="reports" element={<Reports />} />
          <Route path="subscriptions" element={<Subscriptions />} />

          {/* Admin & Settings */}
          <Route path="admin" element={<AdminDashboard />} />
          <Route path="billing" element={<Billing />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="theming" element={<Theming />} />
          <Route path="plugins" element={<Plugins />} />
          <Route path="integrations" element={<Integrations />} />
          <Route path="performance" element={<PerformanceMonitor />} />
          <Route path="compliance" element={<Compliance />} />
          <Route path="security" element={<SecuritySettings />} />

          {/* Governance */}
          <Route path="governance" element={<DataGovernance />} />
          <Route path="governance/stewards" element={<DataGovernance />} />
          <Route path="governance/ownership" element={<DataGovernance />} />
          <Route path="deployments" element={<DeploymentPipelines />} />
          <Route path="lineage" element={<DataLineage />} />
          <Route path="versions" element={<VersionControl />} />
          <Route path="quality" element={<DataQuality />} />
          <Route path="schema" element={<SchemaTracking />} />
          <Route path="apps" element={<AppBundling />} />
          <Route path="analytics" element={<UserAnalyticsDashboard />} />

          {/* Charts */}
          <Route path="charts/new" element={<ChartBuilder />} />
          <Route path="charts/:id" element={<ChartBuilder />} />

          {/* AI */}
          <Route path="ai" element={<AIChat />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
