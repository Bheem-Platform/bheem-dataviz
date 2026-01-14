import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/common/Layout'
import { DashboardList } from './pages/DashboardList'
import { DashboardBuilder } from './pages/DashboardBuilder'
import { DataConnections } from './pages/DataConnections'
import { Datasets } from './pages/Datasets'
import { ChartBuilder } from './pages/ChartBuilder'
import { AIChat } from './pages/AIChat'
import { ChartGallery } from './pages/ChartGallery'
import { Explore } from './pages/Explore'
import { SQLLab } from './pages/SQLLab'
import { KodeeAnalytics } from './pages/KodeeAnalytics'
import { Workflows } from './pages/Workflows'
import { LandingPage } from './pages/LandingPage'

function App() {
  return (
    <Routes>
      {/* Landing Page - Public */}
      <Route path="/" element={<LandingPage />} />

      {/* App Routes - with Layout */}
      <Route element={<Layout />}>
        <Route path="dashboards" element={<DashboardList />} />
        <Route path="dashboards/new" element={<DashboardBuilder />} />
        <Route path="dashboards/:id" element={<DashboardBuilder />} />
        <Route path="gallery" element={<ChartGallery />} />
        <Route path="explore" element={<Explore />} />
        <Route path="sql-lab" element={<SQLLab />} />
        <Route path="kodee" element={<KodeeAnalytics />} />
        <Route path="workflows" element={<Workflows />} />
        <Route path="connections" element={<DataConnections />} />
        <Route path="datasets" element={<Datasets />} />
        <Route path="charts/new" element={<ChartBuilder />} />
        <Route path="charts/:id" element={<ChartBuilder />} />
        <Route path="ai" element={<AIChat />} />
      </Route>
    </Routes>
  )
}

export default App
