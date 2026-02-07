import { forwardRef, HTMLAttributes, InputHTMLAttributes, ButtonHTMLAttributes, SelectHTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { ChevronRight, Search } from 'lucide-react'

// Glass Card Component
interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'hover' | 'interactive' | 'solid'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = 'default', padding = 'md', children, ...props }, ref) => {
    const paddingClasses = {
      none: '',
      sm: 'p-3',
      md: 'p-5',
      lg: 'p-6',
    }

    const variantClasses = {
      default: 'glass-card',
      hover: 'glass-card glass-card-hover',
      interactive: 'glass-card glass-card-interactive',
      solid: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm',
    }

    return (
      <div
        ref={ref}
        className={cn(
          variantClasses[variant],
          paddingClasses[padding],
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)
GlassCard.displayName = 'GlassCard'

// Glass Panel - larger container with subtle glass effect
interface GlassPanelProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated'
}

export const GlassPanel = forwardRef<HTMLDivElement, GlassPanelProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'glass-panel',
          variant === 'elevated' && 'glass-panel-elevated',
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)
GlassPanel.displayName = 'GlassPanel'

// Glass Input Component
interface GlassInputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
}

export const GlassInput = forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          'glass-input',
          error && 'border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      />
    )
  }
)
GlassInput.displayName = 'GlassInput'

// Glass Select Component
interface GlassSelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  error?: boolean
}

export const GlassSelect = forwardRef<HTMLSelectElement, GlassSelectProps>(
  ({ className, error, children, ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={cn(
          'glass-select',
          error && 'border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      >
        {children}
      </select>
    )
  }
)
GlassSelect.displayName = 'GlassSelect'

// Glass Button Component
interface GlassButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'primary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}

export const GlassButton = forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ className, variant = 'default', size = 'md', children, ...props }, ref) => {
    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-sm',
      lg: 'px-6 py-3 text-base',
    }

    const variantClasses = {
      default: 'glass-btn',
      primary: 'glass-btn-primary',
      ghost: 'glass-btn-ghost',
      danger: 'glass-btn-danger',
    }

    return (
      <button
        ref={ref}
        className={cn(
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
)
GlassButton.displayName = 'GlassButton'

// =============================================================================
// MODERN RESPONSIVE PAGE HEADER SYSTEM
// =============================================================================

// Breadcrumb Types
interface BreadcrumbItem {
  label: string
  href?: string
  icon?: ReactNode
}

// Stat Types
interface HeaderStat {
  label: string
  value: string | number
  icon?: ReactNode
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  color?: 'violet' | 'cyan' | 'emerald' | 'amber' | 'rose' | 'indigo'
}

// Tab Types
interface HeaderTab {
  id: string
  label: string
  icon?: ReactNode
  count?: number
}

// Gradient Presets
const gradientPresets = {
  violet: 'from-violet-500 via-fuchsia-500 to-pink-500',
  cyan: 'from-cyan-500 via-blue-500 to-indigo-500',
  emerald: 'from-emerald-500 via-teal-500 to-cyan-500',
  amber: 'from-amber-500 via-orange-500 to-red-500',
  rose: 'from-rose-500 via-pink-500 to-fuchsia-500',
  indigo: 'from-indigo-500 via-purple-500 to-violet-500',
}

const glowPresets = {
  violet: 'shadow-violet-500/30',
  cyan: 'shadow-cyan-500/30',
  emerald: 'shadow-emerald-500/30',
  amber: 'shadow-amber-500/30',
  rose: 'shadow-rose-500/30',
  indigo: 'shadow-indigo-500/30',
}

const bgGradientPresets = {
  violet: 'from-violet-400/20 to-fuchsia-400/20',
  cyan: 'from-cyan-400/20 to-blue-400/20',
  emerald: 'from-emerald-400/20 to-teal-400/20',
  amber: 'from-amber-400/20 to-orange-400/20',
  rose: 'from-rose-400/20 to-pink-400/20',
  indigo: 'from-indigo-400/20 to-purple-400/20',
}

// Modern Page Header Component
interface PageHeaderProps extends HTMLAttributes<HTMLDivElement> {
  // Basic props
  title: string
  subtitle?: string
  icon?: ReactNode
  iconClassName?: string

  // Variant and styling
  variant?: 'default' | 'gradient' | 'minimal' | 'hero'
  gradient?: 'violet' | 'cyan' | 'emerald' | 'amber' | 'rose' | 'indigo'
  size?: 'sm' | 'md' | 'lg'

  // Additional elements
  actions?: ReactNode
  breadcrumbs?: BreadcrumbItem[]
  stats?: HeaderStat[]
  tabs?: HeaderTab[]
  activeTab?: string
  onTabChange?: (tabId: string) => void

  // Search
  searchPlaceholder?: string
  searchValue?: string
  onSearchChange?: (value: string) => void

  // Badge
  badge?: ReactNode

  // Decorations
  showDecorations?: boolean
}

export const PageHeader = forwardRef<HTMLDivElement, PageHeaderProps>(
  ({
    className,
    title,
    subtitle,
    icon,
    iconClassName,
    variant = 'default',
    gradient = 'violet',
    size = 'md',
    actions,
    breadcrumbs,
    stats,
    tabs,
    activeTab,
    onTabChange,
    searchPlaceholder,
    searchValue,
    onSearchChange,
    badge,
    showDecorations = true,
    ...props
  }, ref) => {

    const sizeClasses = {
      sm: { padding: 'px-4 py-3 sm:px-6', title: 'text-lg sm:text-xl', icon: 'w-10 h-10', iconInner: 'w-5 h-5' },
      md: { padding: 'px-4 py-4 sm:px-6 sm:py-5 lg:px-8', title: 'text-xl sm:text-2xl', icon: 'w-12 h-12 sm:w-14 sm:h-14', iconInner: 'w-6 h-6 sm:w-7 sm:h-7' },
      lg: { padding: 'px-4 py-6 sm:px-6 sm:py-8 lg:px-8', title: 'text-2xl sm:text-3xl lg:text-4xl', icon: 'w-14 h-14 sm:w-16 sm:h-16', iconInner: 'w-7 h-7 sm:w-8 sm:h-8' },
    }

    const currentSize = sizeClasses[size]

    // Render Breadcrumbs
    const renderBreadcrumbs = () => {
      if (!breadcrumbs || breadcrumbs.length === 0) return null
      return (
        <nav className="flex items-center gap-1.5 text-sm mb-3 flex-wrap">
          {breadcrumbs.map((crumb, index) => (
            <div key={index} className="flex items-center gap-1.5">
              {index > 0 && <ChevronRight className="w-3.5 h-3.5 text-gray-400" />}
              {crumb.href ? (
                <a
                  href={crumb.href}
                  className="flex items-center gap-1.5 text-gray-500 dark:text-gray-400 hover:text-violet-600 dark:hover:text-violet-400 transition-colors"
                >
                  {crumb.icon}
                  <span>{crumb.label}</span>
                </a>
              ) : (
                <span className="flex items-center gap-1.5 text-gray-700 dark:text-gray-200 font-medium">
                  {crumb.icon}
                  <span>{crumb.label}</span>
                </span>
              )}
            </div>
          ))}
        </nav>
      )
    }

    // Render Stats
    const renderStats = () => {
      if (!stats || stats.length === 0) return null
      return (
        <div className="flex flex-wrap items-center gap-3 mt-4 sm:mt-5">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl border border-white/20 dark:border-gray-700/50"
            >
              {stat.icon && (
                <span className={cn(
                  'flex-shrink-0',
                  stat.color === 'violet' && 'text-violet-500',
                  stat.color === 'cyan' && 'text-cyan-500',
                  stat.color === 'emerald' && 'text-emerald-500',
                  stat.color === 'amber' && 'text-amber-500',
                  stat.color === 'rose' && 'text-rose-500',
                  stat.color === 'indigo' && 'text-indigo-500',
                  !stat.color && 'text-gray-500'
                )}>
                  {stat.icon}
                </span>
              )}
              <span className="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">{stat.value}</span>
              <span className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{stat.label}</span>
              {stat.trend && stat.trendValue && (
                <span className={cn(
                  'text-xs font-medium',
                  stat.trend === 'up' && 'text-emerald-500',
                  stat.trend === 'down' && 'text-red-500',
                  stat.trend === 'neutral' && 'text-gray-400'
                )}>
                  {stat.trend === 'up' && '+'}{stat.trendValue}
                </span>
              )}
            </div>
          ))}
        </div>
      )
    }

    // Render Tabs
    const renderTabs = () => {
      if (!tabs || tabs.length === 0) return null
      return (
        <div className="flex items-center gap-1 mt-4 sm:mt-5 p-1 bg-gray-100/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange?.(tab.id)}
              className={cn(
                'flex items-center gap-2 px-3 py-2 sm:px-4 rounded-lg text-sm font-medium transition-all whitespace-nowrap',
                activeTab === tab.id
                  ? 'bg-white dark:bg-gray-700 text-violet-600 dark:text-violet-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-700/50'
              )}
            >
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
              {tab.count !== undefined && (
                <span className={cn(
                  'px-1.5 py-0.5 text-xs rounded-md',
                  activeTab === tab.id
                    ? 'bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400'
                    : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
                )}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      )
    }

    // Render Search
    const renderSearch = () => {
      if (!onSearchChange) return null
      return (
        <div className="relative mt-4 sm:mt-0 sm:ml-4 w-full sm:w-auto">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder={searchPlaceholder || 'Search...'}
            value={searchValue || ''}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full sm:w-64 lg:w-80 pl-10 pr-4 py-2 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all"
          />
        </div>
      )
    }

    // Variant: Minimal
    if (variant === 'minimal') {
      return (
        <header
          ref={ref}
          className={cn(
            'border-b border-gray-200 dark:border-gray-700/50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm',
            currentSize.padding,
            className
          )}
          {...props}
        >
          {renderBreadcrumbs()}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              {icon && (
                <div className={cn(
                  'rounded-lg p-2 bg-gray-100 dark:bg-gray-800',
                  iconClassName
                )}>
                  {icon}
                </div>
              )}
              <div>
                <div className="flex items-center gap-2">
                  <h1 className={cn('font-bold text-gray-900 dark:text-white', currentSize.title)}>
                    {title}
                  </h1>
                  {badge}
                </div>
                {subtitle && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{subtitle}</p>
                )}
              </div>
            </div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              {renderSearch()}
              {actions && <div className="flex items-center gap-2 sm:gap-3">{actions}</div>}
            </div>
          </div>
          {renderTabs()}
        </header>
      )
    }

    // Variant: Hero (Full width with decorations)
    if (variant === 'hero') {
      return (
        <header
          ref={ref}
          className={cn('relative overflow-hidden', className)}
          {...props}
        >
          {/* Background Decorations */}
          {showDecorations && (
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <div className={cn(
                'absolute -top-24 -right-24 w-64 sm:w-96 h-64 sm:h-96 rounded-full blur-3xl bg-gradient-to-br',
                bgGradientPresets[gradient]
              )} />
              <div className="absolute -bottom-24 -left-24 w-64 sm:w-96 h-64 sm:h-96 rounded-full blur-3xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20" />
              <div className="absolute inset-0 bg-[linear-gradient(rgba(139,92,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(139,92,246,0.03)_1px,transparent_1px)] bg-[size:32px_32px]" />
            </div>
          )}

          <div className={cn('relative', currentSize.padding)}>
            {renderBreadcrumbs()}

            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
              {/* Left Content */}
              <div className="flex items-start gap-4 sm:gap-5">
                {icon && (
                  <div className="relative flex-shrink-0">
                    <div className={cn(
                      'rounded-2xl flex items-center justify-center shadow-xl',
                      currentSize.icon,
                      `bg-gradient-to-br ${gradientPresets[gradient]} ${glowPresets[gradient]}`,
                      iconClassName
                    )}>
                      <span className={cn('text-white', currentSize.iconInner)}>{icon}</span>
                    </div>
                    <div className={cn(
                      'absolute inset-0 rounded-2xl blur-xl opacity-40 -z-10',
                      `bg-gradient-to-br ${gradientPresets[gradient]}`
                    )} />
                  </div>
                )}
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                    <h1 className={cn('font-bold text-gray-900 dark:text-white', currentSize.title)}>
                      {title}
                    </h1>
                    {badge}
                  </div>
                  {subtitle && (
                    <p className="text-gray-500 dark:text-gray-400 mt-1 sm:mt-2 max-w-2xl">
                      {subtitle}
                    </p>
                  )}
                  {renderStats()}
                </div>
              </div>

              {/* Right Content */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                {renderSearch()}
                {actions && <div className="flex flex-wrap items-center gap-2 sm:gap-3">{actions}</div>}
              </div>
            </div>

            {renderTabs()}
          </div>
        </header>
      )
    }

    // Variant: Gradient
    if (variant === 'gradient') {
      return (
        <header
          ref={ref}
          className={cn(
            'relative overflow-hidden bg-gradient-to-r',
            gradientPresets[gradient],
            className
          )}
          {...props}
        >
          {/* Pattern Overlay */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[size:24px_24px]" />

          <div className={cn('relative', currentSize.padding)}>
            {breadcrumbs && (
              <nav className="flex items-center gap-1.5 text-sm mb-3 flex-wrap">
                {breadcrumbs.map((crumb, index) => (
                  <div key={index} className="flex items-center gap-1.5">
                    {index > 0 && <ChevronRight className="w-3.5 h-3.5 text-white/50" />}
                    {crumb.href ? (
                      <a href={crumb.href} className="text-white/70 hover:text-white transition-colors flex items-center gap-1.5">
                        {crumb.icon}
                        <span>{crumb.label}</span>
                      </a>
                    ) : (
                      <span className="text-white font-medium flex items-center gap-1.5">
                        {crumb.icon}
                        <span>{crumb.label}</span>
                      </span>
                    )}
                  </div>
                ))}
              </nav>
            )}

            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex items-center gap-4">
                {icon && (
                  <div className={cn(
                    'rounded-xl flex items-center justify-center bg-white/20 backdrop-blur-sm',
                    currentSize.icon,
                    iconClassName
                  )}>
                    <span className={cn('text-white', currentSize.iconInner)}>{icon}</span>
                  </div>
                )}
                <div>
                  <div className="flex items-center gap-3">
                    <h1 className={cn('font-bold text-white', currentSize.title)}>{title}</h1>
                    {badge}
                  </div>
                  {subtitle && <p className="text-white/80 mt-1">{subtitle}</p>}
                </div>
              </div>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                {onSearchChange && (
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/50" />
                    <input
                      type="text"
                      placeholder={searchPlaceholder || 'Search...'}
                      value={searchValue || ''}
                      onChange={(e) => onSearchChange(e.target.value)}
                      className="w-full sm:w-64 pl-10 pr-4 py-2 bg-white/20 backdrop-blur-sm border border-white/20 rounded-xl text-sm text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30"
                    />
                  </div>
                )}
                {actions}
              </div>
            </div>

            {/* Gradient Stats */}
            {stats && stats.length > 0 && (
              <div className="flex flex-wrap items-center gap-3 mt-5">
                {stats.map((stat, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-xl"
                  >
                    {stat.icon && <span className="text-white/70">{stat.icon}</span>}
                    <span className="text-white font-semibold">{stat.value}</span>
                    <span className="text-white/70 text-sm">{stat.label}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </header>
      )
    }

    // Default Variant
    return (
      <header
        ref={ref}
        className={cn(
          'relative bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200/50 dark:border-gray-700/50',
          currentSize.padding,
          className
        )}
        {...props}
      >
        {/* Subtle gradient line */}
        <div className={cn(
          'absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r',
          gradientPresets[gradient]
        )} />

        {renderBreadcrumbs()}

        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-3 sm:gap-4">
            {icon && (
              <div className={cn(
                'rounded-xl flex items-center justify-center shadow-lg',
                currentSize.icon,
                `bg-gradient-to-br ${gradientPresets[gradient]} ${glowPresets[gradient]}`,
                iconClassName
              )}>
                <span className={cn('text-white', currentSize.iconInner)}>{icon}</span>
              </div>
            )}
            <div>
              <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                <h1 className={cn('font-bold text-gray-900 dark:text-white', currentSize.title)}>
                  {title}
                </h1>
                {badge}
              </div>
              {subtitle && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{subtitle}</p>
              )}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            {renderSearch()}
            {actions && <div className="flex flex-wrap items-center gap-2 sm:gap-3">{actions}</div>}
          </div>
        </div>

        {renderStats()}
        {renderTabs()}
      </header>
    )
  }
)
PageHeader.displayName = 'PageHeader'

// =============================================================================
// OTHER COMPONENTS
// =============================================================================

// Empty State Component
interface EmptyStateProps extends HTMLAttributes<HTMLDivElement> {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
}

export const EmptyState = forwardRef<HTMLDivElement, EmptyStateProps>(
  ({ className, icon, title, description, action, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'flex flex-col items-center justify-center py-16 px-6 text-center',
          className
        )}
        {...props}
      >
        {icon && (
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-100 to-secondary-100 dark:from-primary-900/30 dark:to-secondary-900/30 flex items-center justify-center mb-4 shadow-lg">
            {icon}
          </div>
        )}
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {title}
        </h3>
        {description && (
          <p className="text-gray-500 dark:text-gray-400 max-w-md mb-6">
            {description}
          </p>
        )}
        {action}
      </div>
    )
  }
)
EmptyState.displayName = 'EmptyState'

// Badge Component
interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md'
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', size = 'md', children, ...props }, ref) => {
    const sizeClasses = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-1 text-xs',
    }

    const variantClasses = {
      default: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      primary: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
      success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
      danger: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
      info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    }

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center rounded-full font-medium',
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
        {...props}
      >
        {children}
      </span>
    )
  }
)
Badge.displayName = 'Badge'

// Icon Button Component
interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, variant = 'default', size = 'md', children, ...props }, ref) => {
    const sizeClasses = {
      sm: 'p-1.5',
      md: 'p-2',
      lg: 'p-2.5',
    }

    const variantClasses = {
      default: 'glass-icon-btn',
      ghost: 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300',
      danger: 'hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-500 hover:text-red-600 dark:hover:text-red-400',
    }

    return (
      <button
        ref={ref}
        className={cn(
          'rounded-lg transition-all duration-200',
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
)
IconButton.displayName = 'IconButton'

// Stat Card Component for Headers
interface StatCardProps extends HTMLAttributes<HTMLDivElement> {
  label: string
  value: string | number
  icon?: ReactNode
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  color?: 'violet' | 'cyan' | 'emerald' | 'amber' | 'rose' | 'indigo'
}

export const StatCard = forwardRef<HTMLDivElement, StatCardProps>(
  ({ className, label, value, icon, trend, trendValue, color = 'violet', ...props }, ref) => {
    const colorClasses = {
      violet: 'bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400',
      cyan: 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-400',
      emerald: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400',
      amber: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400',
      rose: 'bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400',
      indigo: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400',
    }

    return (
      <div
        ref={ref}
        className={cn(
          'flex items-center gap-3 p-3 sm:p-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl border border-white/20 dark:border-gray-700/50',
          className
        )}
        {...props}
      >
        {icon && (
          <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', colorClasses[color])}>
            {icon}
          </div>
        )}
        <div>
          <p className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{label}</p>
        </div>
        {trend && trendValue && (
          <span className={cn(
            'ml-auto text-xs sm:text-sm font-medium',
            trend === 'up' && 'text-emerald-500',
            trend === 'down' && 'text-red-500',
            trend === 'neutral' && 'text-gray-400'
          )}>
            {trend === 'up' && '+'}{trendValue}
          </span>
        )}
      </div>
    )
  }
)
StatCard.displayName = 'StatCard'
