import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
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
  Rocket,
  History,
  ShieldCheck,
  Table2,
  Package,
  TrendingUp,
  Home,
  User,
  LogOut,
  Moon,
  Sun,
  Menu,
  X,
} from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
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
      { name: 'Home', href: '/', icon: Home },
      { name: 'Dashboards', href: '/dashboards', icon: LayoutDashboard },
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
    title: 'Governance',
    items: [
      { name: 'Data Governance', href: '/governance', icon: Shield },
      { name: 'Deployments', href: '/deployments', icon: Rocket },
      { name: 'Data Lineage', href: '/lineage', icon: GitBranch },
      { name: 'Version Control', href: '/versions', icon: History },
      { name: 'Data Quality', href: '/quality', icon: ShieldCheck },
      { name: 'Schema Tracking', href: '/schema', icon: Table2 },
      { name: 'App Bundling', href: '/apps', icon: Package },
      { name: 'User Analytics', href: '/analytics', icon: TrendingUp },
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
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [collapsed, setCollapsed] = useState(false)
  const [expandedSections, setExpandedSections] = useState<string[]>(['Core', 'Data'])
  const [profileOpen, setProfileOpen] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.documentElement.classList.contains('dark')
    }
    return false
  })
  const profileRef = useRef<HTMLDivElement>(null)

  // Get user display name and initials
  const displayName = user?.name || user?.email?.split('@')[0] || 'User'
  const userEmail = user?.email || ''
  const userInitials = displayName
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  // Close profile dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const toggleSection = (title: string) => {
    setExpandedSections(prev =>
      prev.includes(title)
        ? prev.filter(t => t !== title)
        : [...prev, title]
    )
  }

  const toggleDarkMode = () => {
    const newMode = !darkMode
    setDarkMode(newMode)
    if (newMode) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-900">
      {/* ========== GLOBAL TOP HEADER ========== */}
      <header className="flex-shrink-0 h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 z-50">
        <div className="h-full px-4 flex items-center justify-between">
          {/* Left: Logo & Mobile Menu Toggle */}
          <div className="flex items-center gap-4">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {mobileMenuOpen ? (
                <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              ) : (
                <Menu className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              )}
            </button>

            {/* Logo */}
            <NavLink to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-violet-500/25 group-hover:shadow-violet-500/40 group-hover:scale-105 transition-all">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-bold bg-gradient-to-r from-violet-600 to-fuchsia-600 dark:from-violet-400 dark:to-fuchsia-400 bg-clip-text text-transparent">
                  Bheem DataViz
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400 -mt-0.5">Analytics Platform</p>
              </div>
            </NavLink>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Search (Desktop) */}
            <div className="hidden md:block relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                className="w-48 lg:w-64 pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-800 border-0 rounded-xl text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition-all"
              />
            </div>

            {/* Notifications */}
            <button className="relative p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
              <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {darkMode ? (
                <Sun className="w-5 h-5 text-amber-500" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>

            {/* Profile Dropdown */}
            <div ref={profileRef} className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2 p-1.5 pr-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-xs font-semibold text-white">
                  {userInitials || <User className="w-4 h-4" />}
                </div>
                <span className="hidden sm:block text-sm font-medium text-gray-700 dark:text-gray-300 max-w-[120px] truncate">
                  {displayName}
                </span>
                <ChevronDown className={cn(
                  "w-4 h-4 text-gray-400 transition-transform",
                  profileOpen && "rotate-180"
                )} />
              </button>

              {/* Dropdown Menu */}
              {profileOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50">
                  {/* User Info */}
                  <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{displayName}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{userEmail}</p>
                    {user?.role && (
                      <span className="inline-block mt-1 px-2 py-0.5 text-xs font-medium bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 rounded-full capitalize">
                        {user.role}
                      </span>
                    )}
                  </div>

                  {/* Menu Items */}
                  <div className="py-1">
                    <NavLink
                      to="/profile"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <User className="w-4 h-4" />
                      My Profile
                    </NavLink>
                    <NavLink
                      to="/settings"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <Settings className="w-4 h-4" />
                      Settings
                    </NavLink>
                    <NavLink
                      to="/billing"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <CreditCard className="w-4 h-4" />
                      Billing
                    </NavLink>
                  </div>

                  {/* Logout */}
                  <div className="border-t border-gray-100 dark:border-gray-700 pt-1">
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* ========== MAIN CONTAINER (Sidebar + Content) ========== */}
      <div className="flex flex-1 overflow-hidden">
        {/* Mobile Sidebar Overlay */}
        {mobileMenuOpen && (
          <div
            className="lg:hidden fixed inset-0 bg-black/50 z-40"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}

        {/* Sidebar */}
        <aside
          className={cn(
            'flex flex-col glass-sidebar transition-all duration-300 ease-in-out z-40',
            // Desktop
            'hidden lg:flex',
            collapsed ? 'lg:w-16' : 'lg:w-64',
            // Mobile
            mobileMenuOpen && 'fixed inset-y-16 left-0 flex w-64'
          )}
        >
          {/* Navigation */}
          <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto sidebar-scroll">
            {navigationSections.map((section, sectionIndex) => (
              <div key={section.title}>
                {sectionIndex > 0 && !collapsed && (
                  <div className="section-divider" />
                )}
                {!collapsed && (
                  <button
                    onClick={() => toggleSection(section.title)}
                    className="section-header group"
                  >
                    <span>{section.title}</span>
                    <ChevronDown
                      className={cn(
                        'w-3.5 h-3.5 transition-transform duration-200 opacity-60 group-hover:opacity-100',
                        expandedSections.includes(section.title) ? 'rotate-0' : '-rotate-90'
                      )}
                    />
                  </button>
                )}
                {(collapsed || expandedSections.includes(section.title)) && (
                  <div className="space-y-0.5 mt-1">
                    {section.items.map((item, itemIndex) => (
                      <NavLink
                        key={item.name}
                        to={item.href}
                        onClick={() => setMobileMenuOpen(false)}
                        className={({ isActive }) =>
                          cn(
                            'nav-item',
                            isActive && 'nav-item-active'
                          )
                        }
                        title={collapsed ? item.name : undefined}
                        style={{
                          animationDelay: `${itemIndex * 30}ms`
                        }}
                      >
                        <item.icon className={cn(
                          'w-5 h-5 flex-shrink-0 nav-icon transition-transform duration-200',
                          !collapsed && 'group-hover:scale-110'
                        )} />
                        {!collapsed && (
                          <span className="truncate">{item.name}</span>
                        )}
                      </NavLink>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* Collapse button (Desktop only) */}
          <div className="hidden lg:block p-2 border-t border-white/10 dark:border-white/5">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="flex items-center justify-center w-full px-3 py-2.5 glass-button rounded-xl text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400"
            >
              {collapsed ? (
                <ChevronRight className="w-5 h-5" />
              ) : (
                <>
                  <ChevronLeft className="w-5 h-5 mr-2" />
                  <span className="text-sm font-medium">Collapse</span>
                </>
              )}
            </button>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-hidden main-gradient-bg">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
