import { Outlet, NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Database,
  BarChart3,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Wand2,
  GitBranch,
  FolderOpen,
  Gauge,
  Sparkles,
  Filter,
  Clock,
  Shield,
  Calendar,
  Lightbulb,
  Building2,
  FileText,
  Code,
  HardDrive,
  Search,
  FileBarChart,
  Bell,
  Settings,
  CreditCard,
  Users,
  Palette,
  Puzzle,
  Link,
  Activity,
  CheckCircle,
  Lock,
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

interface NavItem {
  name: string
  href: string
  icon: any
}

interface NavSection {
  title: string
  items: NavItem[]
}

const navigationSections: NavSection[] = [
  {
    title: 'Core',
    items: [
      { name: 'Dashboard', href: '/dashboards', icon: LayoutDashboard },
      { name: 'Quick Charts', href: '/quick-charts', icon: Sparkles },
      { name: 'Charts', href: '/charts/new', icon: BarChart3 },
      { name: 'KPIs', href: '/kpis', icon: Gauge },
    ]
  },
  {
    title: 'Data',
    items: [
      { name: 'Connections', href: '/connections', icon: Database },
      { name: 'Datasets', href: '/datasets', icon: FolderOpen },
      { name: 'Transforms', href: '/transforms', icon: Wand2 },
      { name: 'Models', href: '/models', icon: GitBranch },
      { name: 'Profiler', href: '/profiler', icon: Search },
    ]
  },
  {
    title: 'Analytics',
    items: [
      { name: 'Insights', href: '/insights', icon: Lightbulb },
      { name: 'Time Intelligence', href: '/time-intelligence', icon: Clock },
      { name: 'Filters', href: '/filters', icon: Filter },
      { name: 'AI Assistant', href: '/ai', icon: MessageSquare },
    ]
  },
  {
    title: 'Enterprise',
    items: [
      { name: 'Workspaces', href: '/workspaces', icon: Building2 },
      { name: 'Row Level Security', href: '/rls', icon: Shield },
      { name: 'Schedules', href: '/schedules', icon: Calendar },
      { name: 'Embed', href: '/embed', icon: Code },
      { name: 'Cache', href: '/cache', icon: HardDrive },
      { name: 'Audit Logs', href: '/audit', icon: FileText },
    ]
  },
  {
    title: 'Reports',
    items: [
      { name: 'Reports', href: '/reports', icon: FileBarChart },
      { name: 'Subscriptions', href: '/subscriptions', icon: Bell },
    ]
  },
  {
    title: 'Admin',
    items: [
      { name: 'Admin Dashboard', href: '/admin', icon: Settings },
      { name: 'Users', href: '/users', icon: Users },
      { name: 'Billing', href: '/billing', icon: CreditCard },
      { name: 'Theming', href: '/theming', icon: Palette },
      { name: 'Plugins', href: '/plugins', icon: Puzzle },
      { name: 'Integrations', href: '/integrations', icon: Link },
      { name: 'Performance', href: '/performance', icon: Activity },
      { name: 'Compliance', href: '/compliance', icon: CheckCircle },
      { name: 'Security', href: '/security', icon: Lock },
    ]
  },
]

export function Layout() {
  const [collapsed, setCollapsed] = useState(false)
  const [expandedSections, setExpandedSections] = useState<string[]>(['Core', 'Data'])

  const toggleSection = (title: string) => {
    setExpandedSections(prev =>
      prev.includes(title)
        ? prev.filter(t => t !== title)
        : [...prev, title]
    )
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <aside
        className={cn(
          'flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300',
          collapsed ? 'w-16' : 'w-64'
        )}
      >
        {/* Logo */}
        <div className="flex items-center h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            {!collapsed && (
              <span className="font-semibold text-gray-900 dark:text-white">
                Bheem DataViz
              </span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-2 overflow-y-auto">
          {navigationSections.map((section) => (
            <div key={section.title}>
              {!collapsed && (
                <button
                  onClick={() => toggleSection(section.title)}
                  className="flex items-center justify-between w-full px-3 py-1.5 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider hover:text-gray-700 dark:hover:text-gray-300"
                >
                  {section.title}
                  <ChevronDown
                    className={cn(
                      'w-4 h-4 transition-transform',
                      expandedSections.includes(section.title) ? 'rotate-0' : '-rotate-90'
                    )}
                  />
                </button>
              )}
              {(collapsed || expandedSections.includes(section.title)) && (
                <div className="space-y-0.5 mt-1">
                  {section.items.map((item) => (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      className={({ isActive }) =>
                        cn(
                          'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm',
                          isActive
                            ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400'
                            : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
                        )
                      }
                      title={collapsed ? item.name : undefined}
                    >
                      <item.icon className="w-5 h-5 flex-shrink-0" />
                      {!collapsed && <span>{item.name}</span>}
                    </NavLink>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>

        {/* Collapse button */}
        <div className="p-2 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center justify-center w-full px-3 py-2 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <>
                <ChevronLeft className="w-5 h-5 mr-2" />
                <span>Collapse</span>
              </>
            )}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
