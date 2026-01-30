import { Link } from 'react-router-dom'
import {
  BarChart3,
  ArrowRight,
  Play,
  Star,
  TrendingUp,
  Users,
  Zap,
  Sparkles,
  PieChart,
  Activity,
} from 'lucide-react'

function AnimatedBars() {
  const bars = [40, 65, 45, 80, 55, 90, 70, 85, 60, 95, 75, 88]
  return (
    <div className="flex items-end justify-between gap-1.5 h-28">
      {bars.map((h, i) => (
        <div
          key={i}
          className="flex-1 rounded-t bg-gradient-to-t from-indigo-600 via-violet-500 to-purple-400 opacity-0 animate-grow"
          style={{
            height: `${h}%`,
            animationDelay: `${i * 80}ms`,
            animationFillMode: 'forwards',
          }}
        />
      ))}
    </div>
  )
}

function FloatingCard({
  icon: Icon,
  value,
  label,
  color,
  className = ''
}: {
  icon: any
  value: string
  label: string
  color: string
  className?: string
}) {
  return (
    <div className={`bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl shadow-gray-900/10 border border-white/50 p-4 flex items-center gap-3 animate-float ${className}`}>
      <div className={`w-11 h-11 rounded-xl ${color} flex items-center justify-center shadow-lg`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <p className="text-xl font-bold text-gray-900">{value}</p>
        <p className="text-xs text-gray-500 font-medium">{label}</p>
      </div>
    </div>
  )
}

function MiniChart({ type }: { type: 'line' | 'pie' }) {
  if (type === 'pie') {
    return (
      <div className="relative w-16 h-16">
        <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
          <circle cx="18" cy="18" r="14" fill="none" stroke="#e5e7eb" strokeWidth="4" />
          <circle
            cx="18" cy="18" r="14" fill="none"
            stroke="url(#pieGradient)" strokeWidth="4"
            strokeDasharray="66 100"
            strokeLinecap="round"
          />
          <defs>
            <linearGradient id="pieGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#6366f1" />
              <stop offset="100%" stopColor="#a855f7" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-bold text-gray-700">66%</span>
        </div>
      </div>
    )
  }

  return (
    <svg viewBox="0 0 80 40" className="w-20 h-10">
      <defs>
        <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#6366f1" />
          <stop offset="100%" stopColor="#a855f7" />
        </linearGradient>
      </defs>
      <path
        d="M0,35 Q10,30 20,25 T40,20 T60,10 T80,5"
        fill="none"
        stroke="url(#lineGradient)"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <circle cx="80" cy="5" r="3" fill="#a855f7" />
    </svg>
  )
}

export function Hero() {
  return (
    <section className="relative pt-24 pb-20 px-6 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-20 left-10 w-72 h-72 bg-indigo-200/30 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-violet-200/30 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-br from-indigo-50/50 via-transparent to-purple-50/50 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto md:mt-20 mt-10 ">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-32 items-center">
          {/* Left Content */}
          <div className="relative z-10">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm border border-indigo-100 rounded-full text-indigo-700 text-sm font-medium mb-8 shadow-lg shadow-indigo-500/10">
              <div className="flex items-center justify-center w-5 h-5 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500">
                <Zap className="w-3 h-3 text-white" />
              </div>
              <span>The #1 Power BI & Tableau Alternative</span>
              <Sparkles className="w-4 h-4 text-amber-500" />
            </div>

            {/* Heading */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl text-gray-900 leading-[1.1] mb-6 tracking-tight">
              Transform data into<span className="text-indigo-700"> insights</span> that speaks
            </h1>

            {/* Description */}
            <p className="text-lg sm:text-xl text-gray-600 mb-10 leading-relaxed max-w-xl">
              Enterprise-grade business intelligence with AI analytics, workflow automation, and semantic layer.
              <span className="font-semibold text-gray-900"> Flat pricing. Unlimited users.</span>
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <Link
                to="/register"
                className="group relative flex items-center justify-center gap-2 px-8 py-4 md:py-2 bg-indigo-700/90 text-white font-semibold rounded-md shadow-xl hover:shadow-2xl hover:shadow-indigo-500/40 hover:-translate-y-0.5 transition-all duration-300"
              >
                <span>Get Started</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                <div className="absolute inset-0 rounded-2xl bg-indigo-800/90 blur-xl opacity-50 group-hover:opacity-70 transition-opacity -z-10" />
              </Link>
              <button className="group flex items-center justify-center gap-2 px-8 py-4 md:py-2 bg-white text-gray-700 font-semibold rounded-md border border-gray-200 hover:border-gray-300 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-50 group-hover:bg-indigo-100 transition-colors">
                  <Play className="w-4 h-4 text-indigo-600 ml-0.5" />
                </div>
                <span>Watch Demo</span>
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 pt-8 border-t border-gray-200/60">
              <div className="flex -space-x-3">
                {['#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#f43f5e'].map((color, i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full border-[3px] border-white shadow-md flex items-center justify-center text-white text-xs font-bold"
                    style={{ backgroundColor: color }}
                  >
                    {['JD', 'AK', 'MR', 'SC', 'EW'][i]}
                  </div>
                ))}
              </div>
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-amber-400 fill-amber-400" />
                  ))}
                  <span className="ml-2 text-sm font-semibold text-gray-900">4.9/5</span>
                </div>
                <p className="text-sm text-gray-500">Trusted by <span className="font-semibold text-gray-700">10,000+</span> data teams</p>
              </div>
            </div>
          </div>

          {/* Right - Dashboard Visual */}
          <div className="relative lg:pl-8">
            {/* Decorative gradient */}
            <div className="absolute -inset-4 bg-gradient-to-br from-indigo-100 via-violet-50 to-purple-100 rounded-[2rem] -rotate-2 -z-10" />
            <div className="absolute -inset-4 bg-gradient-to-tr from-violet-100 via-transparent to-indigo-100 rounded-[2rem] rotate-1 -z-10 opacity-60" />

            {/* Main Dashboard Card */}
            <div className="relative bg-white rounded-2xl shadow-2xl shadow-indigo-500/10 border border-gray-100 overflow-hidden">
              {/* Window Controls */}
              <div className="flex items-center justify-between px-5 py-3 bg-gray-50/80 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-amber-400" />
                  <div className="w-3 h-3 rounded-full bg-emerald-400" />
                </div>
                <div className="flex items-center gap-2 px-3 py-1 bg-white rounded-lg border border-gray-200">
                  <div className="w-4 h-4 rounded bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center">
                    <BarChart3 className="w-2.5 h-2.5 text-white" />
                  </div>
                  <span className="text-xs font-medium text-gray-600">Sales Dashboard</span>
                </div>
                <span className="px-2.5 py-1 bg-emerald-50 text-emerald-600 text-xs font-semibold rounded-full flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  Live
                </span>
              </div>

              {/* Dashboard Content */}
              <div className="p-5 space-y-4">
                {/* KPI Row */}
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: 'Revenue', value: '$2.4M', change: '+23%', up: true, icon: TrendingUp },
                    { label: 'Users', value: '12.5K', change: '+18%', up: true, icon: Users },
                    { label: 'Growth', value: '147%', change: '+12%', up: true, icon: Activity },
                  ].map((kpi, i) => (
                    <div key={i} className="p-3 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-xs text-gray-500 font-medium">{kpi.label}</p>
                        <kpi.icon className="w-3.5 h-3.5 text-gray-400" />
                      </div>
                      <p className="text-lg font-bold text-gray-900">{kpi.value}</p>
                      <div className="flex items-center gap-1 mt-1">
                        <span className={`text-xs font-semibold ${kpi.up ? 'text-emerald-600' : 'text-rose-600'}`}>
                          {kpi.change}
                        </span>
                        <span className="text-xs text-gray-400">vs last month</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-5 gap-3">
                  {/* Main Chart */}
                  <div className="col-span-3 p-4 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-sm font-semibold text-gray-700">Revenue Trend</span>
                      <div className="flex items-center gap-3 text-xs">
                        <div className="flex items-center gap-1.5">
                          <div className="w-2 h-2 rounded-full bg-indigo-500" />
                          <span className="text-gray-500">2024</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <div className="w-2 h-2 rounded-full bg-gray-300" />
                          <span className="text-gray-400">2023</span>
                        </div>
                      </div>
                    </div>
                    <AnimatedBars />
                  </div>

                  {/* Side Charts */}
                  <div className="col-span-2 space-y-3">
                    <div className="p-3 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100 flex items-center justify-between">
                      <div>
                        <p className="text-xs text-gray-500 font-medium mb-1">Conversion</p>
                        <p className="text-sm font-bold text-gray-900">66%</p>
                      </div>
                      <MiniChart type="pie" />
                    </div>
                    <div className="p-3 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-xs text-gray-500 font-medium">Sessions</p>
                        <span className="text-xs font-semibold text-emerald-600">+24%</span>
                      </div>
                      <MiniChart type="line" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Cards */}
            <FloatingCard
              icon={TrendingUp}
              value="+147%"
              label="Growth Rate"
              color="bg-gradient-to-br from-emerald-500 to-teal-500 shadow-emerald-500/30"
              className="absolute -left-6 top-1/4 -translate-y-1/2 hidden lg:flex"
            />
            <FloatingCard
              icon={PieChart}
              value="$48.2K"
              label="Monthly Avg"
              color="bg-gradient-to-br from-violet-500 to-purple-500 shadow-violet-500/30"
              className="absolute -right-4 bottom-20 hidden lg:flex"
            />

            {/* AI Badge */}
            <div className="absolute -right-2 top-16 bg-white/95 backdrop-blur-sm rounded-xl shadow-xl shadow-gray-900/10 border border-white/50 p-3 hidden lg:flex items-center gap-2 animate-float" style={{ animationDelay: '1s' }}>
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-900">AI Powered</p>
                <p className="text-[10px] text-gray-500">Kodee Assistant</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        @keyframes grow {
          from { opacity: 0; transform: scaleY(0); }
          to { opacity: 1; transform: scaleY(1); }
        }
        .animate-float {
          animation: float 4s ease-in-out infinite;
        }
        .animate-grow {
          animation: grow 0.6s ease-out forwards;
          transform-origin: bottom;
        }
      `}</style>
    </section>
  )
}
