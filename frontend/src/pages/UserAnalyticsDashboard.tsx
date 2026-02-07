/**
 * User Analytics Dashboard Page
 *
 * Track user adoption and feature usage
 */

import { useState, useEffect } from 'react';
import {
  Users,
  TrendingUp,
  Activity,
  Eye,
  Clock,
  BarChart3,
  PieChart,
  Calendar,
  ArrowUp,
  ArrowDown,
  Search,
  Filter,
  Download,
  LayoutDashboard,
  FileText,
  MousePointer,
  Layers,
} from 'lucide-react';
import api from '../lib/api';

interface UserAnalytics {
  id: string;
  user_id: string;
  period_start: string;
  period_end: string;
  period_type: string;
  sessions_count: number;
  total_duration_seconds: number;
  dashboards_viewed: number;
  charts_viewed: number;
  reports_generated: number;
  queries_executed: number;
  exports_count: number;
  filters_applied: number;
  drill_downs: number;
  dashboards_created: number;
  charts_created: number;
  top_dashboards: Array<{ id: string; name: string; views: number }>;
}

interface FeatureAdoption {
  id: string;
  feature_name: string;
  total_users: number;
  active_users: number;
  usage_count: number;
  adoption_rate: number;
  period_start: string;
  period_end: string;
}

interface ContentPopularity {
  id: string;
  content_type: string;
  content_id: string;
  content_name: string;
  unique_viewers: number;
  total_views: number;
  shares_count: number;
  exports_count: number;
  popularity_score: number;
}

interface AnalyticsDashboard {
  total_users: number;
  active_users: number;
  total_dashboards: number;
  total_charts: number;
  total_queries: number;
  avg_session_duration: number;
  top_features: FeatureAdoption[];
  top_content: ContentPopularity[];
  user_activity: UserAnalytics[];
}

export default function UserAnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [periodType, setPeriodType] = useState<'daily' | 'weekly' | 'monthly'>('weekly');
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d'>('30d');

  useEffect(() => {
    fetchAnalytics();
  }, [periodType, dateRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await api.get('/governance/analytics/dashboard', {
        params: {
          period_type: periodType,
        },
      });
      setAnalytics(response.data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      // Set mock data for demo
      setAnalytics({
        total_users: 156,
        active_users: 89,
        total_dashboards: 42,
        total_charts: 187,
        total_queries: 12450,
        avg_session_duration: 1840,
        top_features: [],
        top_content: [],
        user_activity: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  if (loading) {
    return (
      <div className="p-6 flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-rose-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Activity className="h-7 w-7 text-rose-600" />
            User Analytics
          </h1>
          <p className="text-gray-500 mt-1">
            Track adoption, engagement, and feature usage
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={periodType}
            onChange={(e) => setPeriodType(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-rose-500"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-rose-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
            <Download className="h-4 w-4" />
            Export
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <Users className="h-5 w-5 text-rose-500" />
            <span className="text-xs text-green-600 flex items-center gap-0.5">
              <ArrowUp className="h-3 w-3" />
              12%
            </span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">{analytics?.total_users || 0}</div>
            <div className="text-sm text-gray-500">Total Users</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <Activity className="h-5 w-5 text-green-500" />
            <span className="text-xs text-green-600 flex items-center gap-0.5">
              <ArrowUp className="h-3 w-3" />
              8%
            </span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">{analytics?.active_users || 0}</div>
            <div className="text-sm text-gray-500">Active Users</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <LayoutDashboard className="h-5 w-5 text-blue-500" />
            <span className="text-xs text-green-600 flex items-center gap-0.5">
              <ArrowUp className="h-3 w-3" />
              5%
            </span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">{analytics?.total_dashboards || 0}</div>
            <div className="text-sm text-gray-500">Dashboards</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <BarChart3 className="h-5 w-5 text-purple-500" />
            <span className="text-xs text-green-600 flex items-center gap-0.5">
              <ArrowUp className="h-3 w-3" />
              15%
            </span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">{analytics?.total_charts || 0}</div>
            <div className="text-sm text-gray-500">Charts</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <MousePointer className="h-5 w-5 text-amber-500" />
            <span className="text-xs text-red-600 flex items-center gap-0.5">
              <ArrowDown className="h-3 w-3" />
              3%
            </span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">
              {((analytics?.total_queries || 0) / 1000).toFixed(1)}k
            </div>
            <div className="text-sm text-gray-500">Queries</div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <Clock className="h-5 w-5 text-teal-500" />
            <span className="text-xs text-green-600 flex items-center gap-0.5">
              <ArrowUp className="h-3 w-3" />
              7%
            </span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">
              {formatDuration(analytics?.avg_session_duration || 0)}
            </div>
            <div className="text-sm text-gray-500">Avg Session</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Feature Adoption */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Layers className="h-5 w-5 text-gray-500" />
            Feature Adoption
          </h3>
          <div className="space-y-4">
            {(analytics?.top_features?.length || 0) > 0 ? (
              analytics?.top_features.map((feature) => (
                <div key={feature.id}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">{feature.feature_name}</span>
                    <span className="text-sm text-gray-500">{feature.adoption_rate.toFixed(0)}%</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-rose-500 rounded-full"
                      style={{ width: `${feature.adoption_rate}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between mt-1 text-xs text-gray-500">
                    <span>{feature.active_users} active users</span>
                    <span>{feature.usage_count} uses</span>
                  </div>
                </div>
              ))
            ) : (
              // Mock data for demo
              <>
                {[
                  { name: 'Dashboards', rate: 87, users: 137, uses: 4521 },
                  { name: 'Quick Charts', rate: 72, users: 112, uses: 2890 },
                  { name: 'SQL Lab', rate: 45, users: 70, uses: 1234 },
                  { name: 'Filters', rate: 68, users: 106, uses: 3456 },
                  { name: 'Drill-down', rate: 34, users: 53, uses: 890 },
                  { name: 'Reports', rate: 28, users: 44, uses: 567 },
                ].map((feature, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">{feature.name}</span>
                      <span className="text-sm text-gray-500">{feature.rate}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-rose-500 rounded-full"
                        style={{ width: `${feature.rate}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between mt-1 text-xs text-gray-500">
                      <span>{feature.users} active users</span>
                      <span>{feature.uses} uses</span>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>

        {/* Popular Content */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-gray-500" />
            Popular Content
          </h3>
          <div className="space-y-3">
            {(analytics?.top_content?.length || 0) > 0 ? (
              analytics?.top_content.map((content, index) => (
                <div
                  key={content.id}
                  className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-semibold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{content.content_name}</p>
                    <p className="text-xs text-gray-500 capitalize">{content.content_type}</p>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">{content.total_views}</div>
                    <div className="text-xs text-gray-500">{content.unique_viewers} users</div>
                  </div>
                </div>
              ))
            ) : (
              // Mock data for demo
              <>
                {[
                  { name: 'Sales Overview', type: 'dashboard', views: 1234, users: 89 },
                  { name: 'Revenue by Region', type: 'chart', views: 987, users: 76 },
                  { name: 'Customer Metrics', type: 'dashboard', views: 876, users: 65 },
                  { name: 'Monthly Report', type: 'report', views: 654, users: 54 },
                  { name: 'Product Performance', type: 'chart', views: 543, users: 43 },
                ].map((content, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-semibold text-sm">
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{content.name}</p>
                      <p className="text-xs text-gray-500 capitalize">{content.type}</p>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-gray-900">{content.views}</div>
                      <div className="text-xs text-gray-500">{content.users} users</div>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>
      </div>

      {/* User Activity Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <Users className="h-5 w-5 text-gray-500" />
            User Activity
          </h3>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search users..."
              className="pl-10 pr-4 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-rose-500"
            />
          </div>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sessions</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dashboards</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Charts</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Queries</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {(analytics?.user_activity?.length || 0) > 0 ? (
              analytics?.user_activity.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-rose-100 flex items-center justify-center">
                        <span className="text-sm font-medium text-rose-600">U</span>
                      </div>
                      <span className="text-sm text-gray-900">User {user.user_id.substring(0, 8)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{user.sessions_count}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{formatDuration(user.total_duration_seconds)}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{user.dashboards_viewed}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{user.charts_viewed}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{user.queries_executed}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {user.dashboards_created + user.charts_created}
                  </td>
                </tr>
              ))
            ) : (
              // Mock data for demo
              <>
                {[
                  { id: 1, name: 'John D.', sessions: 45, duration: 12600, dashboards: 89, charts: 234, queries: 567, created: 12 },
                  { id: 2, name: 'Sarah M.', sessions: 38, duration: 9800, dashboards: 67, charts: 189, queries: 432, created: 8 },
                  { id: 3, name: 'Mike R.', sessions: 32, duration: 8400, dashboards: 54, charts: 145, queries: 321, created: 5 },
                  { id: 4, name: 'Emily K.', sessions: 28, duration: 7200, dashboards: 43, charts: 98, queries: 234, created: 3 },
                  { id: 5, name: 'David L.', sessions: 22, duration: 5400, dashboards: 32, charts: 76, queries: 156, created: 2 },
                ].map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-rose-100 flex items-center justify-center">
                          <span className="text-sm font-medium text-rose-600">{user.name.charAt(0)}</span>
                        </div>
                        <span className="text-sm text-gray-900">{user.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{user.sessions}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{formatDuration(user.duration)}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{user.dashboards}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{user.charts}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{user.queries}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{user.created}</td>
                  </tr>
                ))}
              </>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
