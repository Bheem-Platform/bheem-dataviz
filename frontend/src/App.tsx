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
          <Route path="connections" element={<DataConnections />} />
          <Route path="datasets" element={<Datasets />} />
          <Route path="transforms" element={<TransformBuilder />} />
          <Route path="transforms/:id" element={<TransformBuilder />} />
          <Route path="models" element={<SemanticModels />} />
          <Route path="models/:id" element={<SemanticModels />} />
          <Route path="kpis" element={<KPIs />} />
          <Route path="charts/new" element={<ChartBuilder />} />
          <Route path="charts/:id" element={<ChartBuilder />} />
          <Route path="ai" element={<AIChat />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
