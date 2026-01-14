import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart3,
  Database,
  Brain,
  Layers,
  Code2,
  Workflow,
  ArrowRight,
  Check,
  X,
  Clock,
  DollarSign,
  Users,
  Shield,
  Zap,
  Globe,
  Play,
  ChevronDown,
  Star,
  TrendingUp,
  PieChart,
  LineChart,
} from 'lucide-react'

// Animated chart bars for hero
function AnimatedBars() {
  return (
    <div className="flex items-end gap-1 h-32">
      {[40, 65, 45, 80, 55, 90, 70, 85, 60, 95, 75, 88].map((h, i) => (
        <div
          key={i}
          className="w-3 rounded-t-sm bg-gradient-to-t from-indigo-600 to-violet-500 animate-pulse"
          style={{
            height: `${h}%`,
            animationDelay: `${i * 100}ms`,
            animationDuration: '2s',
          }}
        />
      ))}
    </div>
  )
}

// Floating stat card
function StatCard({ icon: Icon, value, label, color }: { icon: any; value: string; label: string; color: string }) {
  return (
    <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 p-4 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl ${color} flex items-center justify-center`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  )
}

// Comparison data
const comparisonData = [
  { feature: 'AI-Powered Analytics', bheem: true, powerbi: 'Limited', tableau: 'Limited', looker: false },
  { feature: 'Natural Language Queries', bheem: true, powerbi: true, tableau: false, looker: false },
  { feature: 'Workflow Automation', bheem: true, powerbi: false, tableau: false, looker: false },
  { feature: 'Semantic Layer Built-in', bheem: true, powerbi: false, tableau: false, looker: true },
  { feature: 'Self-Hosted Option', bheem: true, powerbi: false, tableau: true, looker: false },
  { feature: 'Unlimited Users (Flat Rate)', bheem: true, powerbi: false, tableau: false, looker: false },
  { feature: 'White-Label Support', bheem: true, powerbi: false, tableau: false, looker: false },
]

// Features data
const features = [
  {
    icon: Database,
    title: 'Connect Any Data Source',
    description: 'PostgreSQL, MySQL, BigQuery, Snowflake, MongoDB, REST APIs, and 50+ more connectors.',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: BarChart3,
    title: '40+ Visualization Types',
    description: 'Bar charts, line graphs, heatmaps, sankey diagrams, geospatial maps, and more.',
    color: 'from-violet-500 to-purple-500',
  },
  {
    icon: Brain,
    title: 'Kodee AI Assistant',
    description: 'Ask questions in plain English and get instant charts, insights, and anomaly detection.',
    color: 'from-pink-500 to-rose-500',
  },
  {
    icon: Layers,
    title: 'Semantic Layer',
    description: 'Define metrics once with Cube.js. Consistent calculations across all reports.',
    color: 'from-amber-500 to-orange-500',
  },
  {
    icon: Code2,
    title: 'SQL Lab',
    description: 'Full SQL editor with autocomplete, schema browser, and AI-assisted query building.',
    color: 'from-emerald-500 to-teal-500',
  },
  {
    icon: Workflow,
    title: 'BheemFlow Automation',
    description: 'Schedule reports, set alerts, automate refreshes with visual drag-and-drop workflows.',
    color: 'from-indigo-500 to-blue-500',
  },
]

// Pricing tiers
const pricing = [
  {
    name: 'Starter',
    price: '$0',
    period: '/forever',
    description: 'Perfect for individuals and small projects',
    features: ['5 Dashboards', '3 Data Sources', 'Basic Charts', 'Community Support', '1GB Storage'],
    cta: 'Start Free',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$49',
    period: '/month',
    description: 'For growing teams that need more power',
    features: ['Unlimited Dashboards', 'Unlimited Sources', 'All Chart Types', 'Kodee AI', 'SQL Lab', 'BheemFlow', 'Priority Support', '100GB Storage'],
    cta: 'Start 14-Day Trial',
    highlighted: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For organizations requiring security & scale',
    features: ['Everything in Pro', 'Self-Hosted Option', 'White-Label', 'SSO & SAML', 'Row-Level Security', 'Dedicated Support', '99.9% SLA', 'Unlimited Storage'],
    cta: 'Contact Sales',
    highlighted: false,
  },
]

// Testimonials
const testimonials = [
  {
    quote: "Switched from Power BI and saved $15,000 annually. The AI features are incredible.",
    author: "Sarah Chen",
    role: "VP of Analytics, TechScale",
    avatar: "SC",
  },
  {
    quote: "Finally, a BI tool that doesn't nickel and dime us per user. Our whole team has access now.",
    author: "Marcus Rodriguez",
    role: "CTO, DataDriven Inc",
    avatar: "MR",
  },
  {
    quote: "The workflow automation alone replaced three other tools we were paying for.",
    author: "Emily Watson",
    role: "Head of Data, CloudFirst",
    avatar: "EW",
  },
]

export function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  const faqs = [
    {
      q: 'How does pricing compare to Power BI or Tableau?',
      a: 'Power BI charges $10/user/month, Tableau starts at $70/user/month. We charge a flat $49/month for unlimited users - so a team of 50 costs $49 total, not $500-$3,500.',
    },
    {
      q: 'Can I self-host Bheem DataViz?',
      a: 'Yes! Enterprise plans include self-hosted deployment. Run it on your own infrastructure with full data sovereignty while still receiving updates and support.',
    },
    {
      q: 'What is Kodee AI and how does it work?',
      a: 'Kodee is our AI assistant. Ask questions like "Show me sales by region for Q4" in plain English and get instant visualizations. It also proactively detects anomalies and suggests insights.',
    },
    {
      q: 'Do you offer a free trial?',
      a: 'Yes! Start with our free Starter plan forever, or try Pro free for 14 days. No credit card required.',
    },
  ]

  const renderCheck = (val: boolean | string) => {
    if (val === true) return <Check className="w-5 h-5 text-emerald-500" />
    if (val === false) return <X className="w-5 h-5 text-gray-300" />
    return <span className="text-xs text-amber-600 font-medium">{val}</span>
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">Bheem DataViz</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">Features</a>
            <a href="#pricing" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">Pricing</a>
            <a href="#comparison" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">Compare</a>
            <a href="#faq" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">FAQ</a>
          </div>

          <div className="flex items-center gap-4">
            <Link to="/dashboards" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
              Sign In
            </Link>
            <Link
              to="/dashboards"
              className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-sm font-semibold rounded-xl hover:shadow-lg hover:shadow-indigo-500/25 transition-all"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Content */}
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-50 to-violet-50 border border-indigo-100 rounded-full text-indigo-700 text-sm font-medium mb-6">
                <Zap className="w-4 h-4" />
                The #1 Power BI & Tableau Alternative
              </div>

              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
                Transform data into
                <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 bg-clip-text text-transparent"> insights </span>
                that drive growth
              </h1>

              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Enterprise-grade business intelligence with AI analytics, workflow automation, and semantic layer.
                <span className="font-semibold text-gray-900"> Flat pricing. Unlimited users.</span>
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-10">
                <Link
                  to="/dashboards"
                  className="group flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold rounded-xl hover:shadow-xl hover:shadow-indigo-500/25 transition-all"
                >
                  Start Free Trial
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <button className="flex items-center justify-center gap-2 px-8 py-4 bg-gray-50 text-gray-700 font-semibold rounded-xl hover:bg-gray-100 transition-colors border border-gray-200">
                  <Play className="w-5 h-5 text-indigo-600" />
                  Watch Demo
                </button>
              </div>

              {/* Trust Indicators */}
              <div className="flex items-center gap-6 pt-8 border-t border-gray-100">
                <div className="flex -space-x-2">
                  {['#6366f1', '#8b5cf6', '#a855f7', '#ec4899'].map((color, i) => (
                    <div key={i} className="w-10 h-10 rounded-full border-2 border-white" style={{ backgroundColor: color }} />
                  ))}
                </div>
                <div>
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-amber-400 fill-amber-400" />
                    ))}
                  </div>
                  <p className="text-sm text-gray-500">Trusted by 10,000+ data teams</p>
                </div>
              </div>
            </div>

            {/* Right - Visual */}
            <div className="relative">
              {/* Gradient Background */}
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-100 via-violet-50 to-purple-100 rounded-3xl -rotate-3" />

              {/* Main Dashboard Card */}
              <div className="relative bg-white rounded-2xl shadow-2xl shadow-indigo-500/10 border border-gray-200 overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 bg-gray-50 border-b border-gray-100">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center">
                      <BarChart3 className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-semibold text-gray-900">Sales Dashboard</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-full">Live</span>
                  </div>
                </div>

                {/* Dashboard Content */}
                <div className="p-6 space-y-4">
                  {/* KPIs */}
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { label: 'Revenue', value: '$2.4M', change: '+23%', up: true },
                      { label: 'Users', value: '12.5K', change: '+18%', up: true },
                      { label: 'Churn', value: '2.1%', change: '-0.5%', up: false },
                    ].map((kpi, i) => (
                      <div key={i} className="p-4 bg-gray-50 rounded-xl">
                        <p className="text-xs text-gray-500 mb-1">{kpi.label}</p>
                        <p className="text-xl font-bold text-gray-900">{kpi.value}</p>
                        <p className={`text-xs font-medium ${kpi.up ? 'text-emerald-600' : 'text-rose-600'}`}>
                          {kpi.change}
                        </p>
                      </div>
                    ))}
                  </div>

                  {/* Chart */}
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-sm font-medium text-gray-700">Revenue Trend</span>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <div className="w-2 h-2 rounded-full bg-indigo-500" />
                        2024
                      </div>
                    </div>
                    <AnimatedBars />
                  </div>
                </div>
              </div>

              {/* Floating Cards */}
              <div className="absolute -left-8 top-1/4 transform -translate-y-1/2">
                <StatCard icon={TrendingUp} value="+147%" color="bg-gradient-to-br from-emerald-500 to-teal-500" label="Growth" />
              </div>
              <div className="absolute -right-8 bottom-1/4">
                <StatCard icon={Users} value="10K+" color="bg-gradient-to-br from-violet-500 to-purple-500" label="Users" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Logos */}
      <section className="py-12 px-6 bg-gray-50 border-y border-gray-100">
        <div className="max-w-7xl mx-auto">
          <p className="text-center text-sm text-gray-500 mb-8">Trusted by data teams at leading companies</p>
          <div className="flex items-center justify-center gap-12 flex-wrap opacity-60">
            {['Microsoft', 'Google', 'Amazon', 'Stripe', 'Shopify', 'Airbnb'].map((company, i) => (
              <span key={i} className="text-xl font-bold text-gray-400">{company}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Value Props */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: DollarSign, title: 'Save 70-95%', desc: 'vs Power BI & Tableau licensing', color: 'from-emerald-500 to-teal-500' },
              { icon: Users, title: 'Unlimited Users', desc: 'One flat price, whole team access', color: 'from-blue-500 to-indigo-500' },
              { icon: Clock, title: '10+ Hrs Saved', desc: 'Weekly with AI & automation', color: 'from-violet-500 to-purple-500' },
              { icon: Shield, title: '99.9% Uptime', desc: 'Enterprise-grade reliability', color: 'from-rose-500 to-pink-500' },
            ].map((item, i) => (
              <div key={i} className="p-6 bg-white rounded-2xl border border-gray-100 hover:shadow-xl hover:shadow-gray-200/50 transition-all group">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${item.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <item.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-6 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything you need for
              <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent"> data excellence</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              From connecting data sources to sharing insights - one platform for your entire analytics workflow.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, i) => (
              <div key={i} className="bg-white p-8 rounded-2xl border border-gray-100 hover:shadow-xl hover:shadow-gray-200/50 transition-all group">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison */}
      <section id="comparison" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              See how we
              <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent"> compare</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              More features, better AI, fair pricing - compared to legacy BI tools.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xl shadow-gray-200/50">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-200">
                    <th className="text-left py-5 px-6 text-sm font-semibold text-gray-600">Feature</th>
                    <th className="py-5 px-6 text-center bg-gradient-to-r from-indigo-50 to-violet-50">
                      <span className="text-sm font-bold bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">Bheem DataViz</span>
                    </th>
                    <th className="py-5 px-6 text-center text-sm font-semibold text-gray-600">Power BI</th>
                    <th className="py-5 px-6 text-center text-sm font-semibold text-gray-600">Tableau</th>
                    <th className="py-5 px-6 text-center text-sm font-semibold text-gray-600">Looker</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonData.map((row, i) => (
                    <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-6 text-sm text-gray-700 font-medium">{row.feature}</td>
                      <td className="py-4 px-6 text-center bg-gradient-to-r from-indigo-50/50 to-violet-50/50">{renderCheck(row.bheem)}</td>
                      <td className="py-4 px-6 text-center">{renderCheck(row.powerbi)}</td>
                      <td className="py-4 px-6 text-center">{renderCheck(row.tableau)}</td>
                      <td className="py-4 px-6 text-center">{renderCheck(row.looker)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Cost Savings Banner */}
          <div className="mt-12 p-8 bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 rounded-2xl text-white">
            <div className="grid md:grid-cols-3 gap-8 items-center">
              <div className="md:col-span-2">
                <h3 className="text-2xl font-bold mb-2">Save up to 95% vs Power BI</h3>
                <p className="text-indigo-100 mb-4">
                  100 users on Power BI Pro = $12,000/year. Bheem DataViz Pro = $588/year for unlimited users.
                </p>
                <div className="flex items-center gap-6">
                  <div>
                    <p className="text-xs text-indigo-200">Power BI (100 users)</p>
                    <p className="text-xl font-bold line-through opacity-60">$12,000/yr</p>
                  </div>
                  <ArrowRight className="w-6 h-6" />
                  <div>
                    <p className="text-xs text-indigo-200">Bheem DataViz Pro</p>
                    <p className="text-xl font-bold">$588/yr</p>
                  </div>
                </div>
              </div>
              <div className="text-center">
                <p className="text-6xl font-bold">95%</p>
                <p className="text-indigo-200">Savings</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Loved by data teams worldwide</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((t, i) => (
              <div key={i} className="bg-white p-8 rounded-2xl border border-gray-100 shadow-lg shadow-gray-200/50">
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, j) => (
                    <Star key={j} className="w-5 h-5 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-gray-700 mb-6 leading-relaxed">"{t.quote}"</p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-white font-bold">
                    {t.avatar}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{t.author}</p>
                    <p className="text-sm text-gray-500">{t.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Simple,
              <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent"> transparent </span>
              pricing
            </h2>
            <p className="text-xl text-gray-600">No per-user fees. No surprises. No hidden costs.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricing.map((plan, i) => (
              <div
                key={i}
                className={`relative p-8 rounded-2xl ${
                  plan.highlighted
                    ? 'bg-gradient-to-b from-indigo-600 to-violet-600 text-white shadow-xl shadow-indigo-500/25'
                    : 'bg-white border border-gray-200'
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-amber-400 text-amber-900 text-sm font-bold rounded-full">
                    Most Popular
                  </div>
                )}
                <h3 className={`text-xl font-bold mb-2 ${plan.highlighted ? 'text-white' : 'text-gray-900'}`}>{plan.name}</h3>
                <div className="flex items-baseline gap-1 mb-3">
                  <span className={`text-4xl font-bold ${plan.highlighted ? 'text-white' : 'text-gray-900'}`}>{plan.price}</span>
                  <span className={plan.highlighted ? 'text-indigo-200' : 'text-gray-500'}>{plan.period}</span>
                </div>
                <p className={`mb-6 ${plan.highlighted ? 'text-indigo-100' : 'text-gray-600'}`}>{plan.description}</p>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f, j) => (
                    <li key={j} className="flex items-center gap-3">
                      <Check className={`w-5 h-5 ${plan.highlighted ? 'text-indigo-200' : 'text-emerald-500'}`} />
                      <span className={plan.highlighted ? 'text-white' : 'text-gray-700'}>{f}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/dashboards"
                  className={`block w-full py-3 rounded-xl font-semibold text-center transition-all ${
                    plan.highlighted
                      ? 'bg-white text-indigo-600 hover:bg-gray-100'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-20 px-6 bg-gray-50">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Frequently asked questions</h2>
          </div>
          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <div key={i} className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between p-6 text-left"
                >
                  <span className="font-semibold text-gray-900">{faq.q}</span>
                  <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                </button>
                {openFaq === i && (
                  <div className="px-6 pb-6 text-gray-600">{faq.a}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 rounded-3xl p-12 text-center text-white">
            <h2 className="text-4xl font-bold mb-4">Ready to transform your data?</h2>
            <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
              Join 10,000+ data professionals. Start your free trial today - no credit card required.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/dashboards"
                className="flex items-center gap-2 px-8 py-4 bg-white text-indigo-600 font-bold rounded-xl hover:bg-gray-100 transition-colors"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </Link>
              <a href="mailto:sales@bheem.dev" className="px-8 py-4 text-indigo-100 hover:text-white font-semibold transition-colors">
                Talk to Sales
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">Bheem DataViz</span>
            </div>
            <div className="flex items-center gap-8 text-sm text-gray-400">
              <a href="#" className="hover:text-white transition-colors">Documentation</a>
              <a href="#" className="hover:text-white transition-colors">API</a>
              <a href="#" className="hover:text-white transition-colors">Status</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} Bheem Platform. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}
