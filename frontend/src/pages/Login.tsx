import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  BarChart3,
  Mail,
  Lock,
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  Zap,
  Shield,
  Globe,
  LineChart,
  Layers,
  Sparkles,
  PieChart,
  TrendingUp,
  Activity,
  BarChart2,
  Database,
  GitBranch,
  Table,
  Gauge,
  Target,
  Boxes
} from 'lucide-react';
import { FaGoogle } from 'react-icons/fa';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, socialLogin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password, rememberMe);
      navigate('/dashboards');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: LineChart,
      title: 'Real-time Analytics',
      description: 'Monitor your data with live updates and instant insights'
    },
    {
      icon: Layers,
      title: 'Semantic Models',
      description: 'Build powerful data models with measures and dimensions'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Optimized queries for blazing fast performance'
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Bank-grade encryption and access controls'
    }
  ];

  // Floating icons configuration
  const floatingIcons = [
    { Icon: BarChart3, size: 'w-8 h-8', position: 'top-[8%] left-[5%]', delay: '0s', duration: '20s', color: 'text-indigo-400/30' },
    { Icon: PieChart, size: 'w-10 h-10', position: 'top-[15%] left-[20%]', delay: '2s', duration: '25s', color: 'text-purple-400/25' },
    { Icon: TrendingUp, size: 'w-7 h-7', position: 'top-[5%] left-[40%]', delay: '1s', duration: '22s', color: 'text-fuchsia-400/30' },
    { Icon: Activity, size: 'w-9 h-9', position: 'top-[20%] left-[60%]', delay: '3s', duration: '18s', color: 'text-indigo-400/25' },
    { Icon: BarChart2, size: 'w-6 h-6', position: 'top-[10%] left-[80%]', delay: '0.5s', duration: '24s', color: 'text-purple-400/30' },
    { Icon: Database, size: 'w-8 h-8', position: 'top-[12%] right-[10%]', delay: '4s', duration: '21s', color: 'text-fuchsia-400/25' },
    { Icon: LineChart, size: 'w-11 h-11', position: 'top-[35%] left-[3%]', delay: '1.5s', duration: '26s', color: 'text-indigo-400/20' },
    { Icon: GitBranch, size: 'w-7 h-7', position: 'top-[45%] left-[15%]', delay: '2.5s', duration: '19s', color: 'text-purple-400/30' },
    { Icon: Table, size: 'w-8 h-8', position: 'top-[40%] right-[5%]', delay: '0s', duration: '23s', color: 'text-fuchsia-400/25' },
    { Icon: Gauge, size: 'w-9 h-9', position: 'top-[55%] right-[15%]', delay: '3.5s', duration: '20s', color: 'text-indigo-400/30' },
    { Icon: PieChart, size: 'w-6 h-6', position: 'top-[60%] left-[8%]', delay: '1s', duration: '27s', color: 'text-purple-400/25' },
    { Icon: Target, size: 'w-8 h-8', position: 'top-[65%] left-[25%]', delay: '4.5s', duration: '17s', color: 'text-fuchsia-400/30' },
    { Icon: BarChart3, size: 'w-10 h-10', position: 'top-[70%] right-[8%]', delay: '2s', duration: '24s', color: 'text-indigo-400/25' },
    { Icon: Boxes, size: 'w-7 h-7', position: 'top-[75%] left-[45%]', delay: '0.5s', duration: '22s', color: 'text-purple-400/30' },
    { Icon: Activity, size: 'w-8 h-8', position: 'top-[80%] left-[10%]', delay: '3s', duration: '19s', color: 'text-fuchsia-400/25' },
    { Icon: TrendingUp, size: 'w-9 h-9', position: 'top-[85%] right-[20%]', delay: '1.5s', duration: '25s', color: 'text-indigo-400/30' },
    { Icon: Database, size: 'w-6 h-6', position: 'top-[88%] left-[30%]', delay: '4s', duration: '21s', color: 'text-purple-400/25' },
    { Icon: LineChart, size: 'w-7 h-7', position: 'top-[92%] right-[40%]', delay: '2.5s', duration: '18s', color: 'text-fuchsia-400/30' },
    { Icon: Gauge, size: 'w-8 h-8', position: 'top-[30%] left-[50%]', delay: '0s', duration: '26s', color: 'text-indigo-400/20' },
    { Icon: BarChart2, size: 'w-10 h-10', position: 'top-[50%] left-[70%]', delay: '3.5s', duration: '23s', color: 'text-purple-400/25' },
  ];

  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-950">
      {/* Full Screen Animated Background */}
      <div className="absolute inset-0">
        {/* Base gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-indigo-950/50 to-slate-950" />

        {/* Aurora waves */}
        <div className="aurora-container">
          <div className="aurora aurora-1" />
          <div className="aurora aurora-2" />
          <div className="aurora aurora-3" />
        </div>

        {/* Mesh gradient */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-purple-600/40 rounded-full blur-[150px] animate-pulse-slow" />
          <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-indigo-600/40 rounded-full blur-[150px] animate-pulse-slow animation-delay-2000" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-fuchsia-600/20 rounded-full blur-[180px] animate-pulse-slow animation-delay-4000" />
        </div>

        {/* Floating Analytics Icons */}
        <div className="absolute inset-0 overflow-hidden">
          {floatingIcons.map((item, index) => (
            <div
              key={index}
              className={`absolute ${item.position} floating-icon`}
              style={{
                animationDelay: item.delay,
                animationDuration: item.duration,
              }}
            >
              <div className="icon-wrapper">
                <item.Icon className={`${item.size} ${item.color}`} />
              </div>
            </div>
          ))}
        </div>

        {/* Grid overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:60px_60px]" />

        {/* Radial gradient overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(2,6,23,0.6)_100%)]" />
      </div>

      {/* Content - Split Layout */}
      <div className="relative z-10 min-h-screen flex">
        {/* Left Side - Branding & Features */}
        <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 xl:p-16">
          {/* Logo */}
          <div>
            <Link to="/" className="inline-flex items-center gap-3 group">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-purple-500/25 group-hover:scale-105 transition-transform">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <span className="text-xl font-bold text-white">Bheem DataViz</span>
                <span className="block text-xs text-white/40">Analytics Platform</span>
              </div>
            </Link>
          </div>

          {/* Main Content */}
          <div className="my-auto max-w-lg">
            <div className="flex items-center gap-2 mb-6">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <span className="text-sm font-medium text-indigo-400 uppercase tracking-wider">
                Data Intelligence
              </span>
            </div>

            <h1 className="text-4xl xl:text-5xl font-bold text-white leading-tight mb-6">
              Transform Raw Data
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-fuchsia-400">
                Into Business Value
              </span>
            </h1>

            <p className="text-lg text-white/60 mb-12 leading-relaxed">
              Connect your data sources, build semantic models, and create stunning visualizations in minutes.
            </p>

            {/* Features Grid */}
            <div className="grid grid-cols-2 gap-4">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="group p-4 rounded-2xl bg-white/[0.03] backdrop-blur-sm border border-white/[0.05] hover:bg-white/[0.08] hover:border-white/[0.1] transition-all duration-300"
                >
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                    <feature.icon className="w-5 h-5 text-indigo-400" />
                  </div>
                  <h3 className="font-semibold text-white text-sm mb-1">{feature.title}</h3>
                  <p className="text-xs text-white/40 leading-relaxed">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center gap-3 text-sm text-white/30">
            <Globe className="w-4 h-4" />
            <span>Trusted by 10,000+ companies worldwide</span>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12">
          <div className="w-full max-w-md">
            {/* Mobile Logo */}
            <div className="lg:hidden text-center mb-8">
              <Link to="/" className="inline-flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-white">Bheem DataViz</span>
              </Link>
            </div>

            {/* Login Card */}
            <div className="relative">
              {/* Card Glow */}
              <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-fuchsia-500 rounded-3xl blur-xl opacity-20" />

              <div className="relative bg-white/[0.05] backdrop-blur-2xl rounded-3xl border border-white/[0.1] p-8 shadow-2xl">
                {/* Header */}
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-white mb-2">Welcome back</h2>
                  <p className="text-white/50 text-sm">Enter your credentials to access your dashboard</p>
                </div>

                {error && (
                  <div className="mb-6 p-4 bg-red-500/10 backdrop-blur-sm border border-red-500/20 rounded-xl text-red-400 text-sm flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center flex-shrink-0">
                      <span>!</span>
                    </div>
                    <span>{error}</span>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                  {/* Email Field */}
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-white/70 mb-2">
                      Email Address
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
                      <input
                        id="email"
                        type="email"
                        placeholder="you@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="w-full pl-12 pr-4 py-3.5 bg-white/[0.05] border border-white/[0.1] rounded-xl text-white placeholder-white/30 focus:outline-none focus:bg-white/[0.08] focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                      />
                    </div>
                  </div>

                  {/* Password Field */}
                  <div>
                    <label htmlFor="password" className="block text-sm font-medium text-white/70 mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
                      <input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="w-full pl-12 pr-12 py-3.5 bg-white/[0.05] border border-white/[0.1] rounded-xl text-white placeholder-white/30 focus:outline-none focus:bg-white/[0.08] focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 transition-all"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-4 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  {/* Remember Me & Forgot Password */}
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-3 cursor-pointer group">
                      <div
                        className={`w-5 h-5 rounded-md border flex items-center justify-center transition-all ${
                          rememberMe
                            ? 'bg-gradient-to-br from-indigo-500 to-purple-600 border-transparent'
                            : 'border-white/20 group-hover:border-white/40'
                        }`}
                        onClick={() => setRememberMe(!rememberMe)}
                      >
                        {rememberMe && <Check className="w-3.5 h-3.5 text-white" />}
                      </div>
                      <span className="text-sm text-white/50 group-hover:text-white/70 transition-colors">
                        Remember me
                      </span>
                    </label>
                    <Link
                      to="/forgot-password"
                      className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
                    >
                      Forgot password?
                    </Link>
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-indigo-600 via-purple-600 to-fuchsia-600 text-white font-semibold rounded-xl shadow-lg shadow-purple-500/25 hover:shadow-xl hover:shadow-purple-500/30 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-300"
                  >
                    {loading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Signing in...
                      </>
                    ) : (
                      <>
                        Sign In
                        <ArrowRight className="w-5 h-5" />
                      </>
                    )}
                  </button>
                </form>

                {/* Divider */}
                <div className="relative my-8">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-white/10" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-transparent text-white/30">or continue with</span>
                  </div>
                </div>

                {/* Social Login */}
                <button
                  onClick={() => socialLogin('google')}
                  className="w-full flex items-center justify-center gap-3 px-6 py-3.5 bg-white/[0.05] border border-white/[0.1] rounded-xl text-white font-medium hover:bg-white/[0.1] hover:border-white/[0.2] transition-all duration-300"
                >
                  <FaGoogle className="w-5 h-5" />
                  Continue with Google
                </button>

                {/* Sign Up Link */}
                <p className="text-center mt-8 text-white/50">
                  Don't have an account?{' '}
                  <Link
                    to="/register"
                    className="text-indigo-400 font-semibold hover:text-indigo-300 transition-colors"
                  >
                    Create account
                  </Link>
                </p>
              </div>
            </div>

            {/* Terms */}
            <p className="text-center mt-8 text-xs text-white/30">
              By signing in, you agree to our{' '}
              <a href="#" className="text-indigo-400/70 hover:text-indigo-400 hover:underline">Terms</a>
              {' '}and{' '}
              <a href="#" className="text-indigo-400/70 hover:text-indigo-400 hover:underline">Privacy Policy</a>
            </p>
          </div>
        </div>
      </div>

      {/* Animation Styles */}
      <style>{`
        .aurora-container {
          position: absolute;
          inset: 0;
          overflow: hidden;
          opacity: 0.4;
        }

        .aurora {
          position: absolute;
          width: 200%;
          height: 200%;
          background: conic-gradient(
            from 0deg at 50% 50%,
            transparent 0deg,
            rgba(99, 102, 241, 0.3) 60deg,
            rgba(139, 92, 246, 0.4) 120deg,
            rgba(217, 70, 239, 0.3) 180deg,
            rgba(139, 92, 246, 0.4) 240deg,
            rgba(99, 102, 241, 0.3) 300deg,
            transparent 360deg
          );
          animation: aurora-rotate 25s linear infinite;
        }

        .aurora-1 {
          top: -50%;
          left: -50%;
          filter: blur(100px);
        }

        .aurora-2 {
          top: -60%;
          left: -30%;
          filter: blur(120px);
          animation-duration: 30s;
          animation-direction: reverse;
          opacity: 0.7;
        }

        .aurora-3 {
          top: -40%;
          left: -70%;
          filter: blur(140px);
          animation-duration: 35s;
          opacity: 0.5;
        }

        @keyframes aurora-rotate {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        .animate-pulse-slow {
          animation: pulse-slow 8s ease-in-out infinite;
        }

        @keyframes pulse-slow {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.1);
          }
        }

        .animation-delay-2000 {
          animation-delay: 2s;
        }

        .animation-delay-4000 {
          animation-delay: 4s;
        }

        /* Floating Icons Animation */
        .floating-icon {
          animation: float-around linear infinite;
        }

        .floating-icon .icon-wrapper {
          animation: rotate-icon 20s linear infinite;
        }

        @keyframes float-around {
          0% {
            transform: translate(0, 0) scale(1);
            opacity: 0;
          }
          5% {
            opacity: 1;
          }
          25% {
            transform: translate(30px, -40px) scale(1.1);
          }
          50% {
            transform: translate(-20px, -80px) scale(0.9);
          }
          75% {
            transform: translate(40px, -120px) scale(1.05);
          }
          95% {
            opacity: 1;
          }
          100% {
            transform: translate(0, -160px) scale(1);
            opacity: 0;
          }
        }

        @keyframes rotate-icon {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }

        /* Glow effect for icons */
        .floating-icon .icon-wrapper {
          filter: drop-shadow(0 0 10px currentColor);
        }
      `}</style>
    </div>
  );
}
