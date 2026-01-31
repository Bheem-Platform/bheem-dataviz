/**
 * Admin Dashboard Page
 *
 * System administration and monitoring dashboard.
 */

import { useState } from 'react';
import {
  Users,
  Database,
  Activity,
  AlertTriangle,
  TrendingUp,
  Server,
  Shield,
  Clock,
  HardDrive,
  Cpu,
} from 'lucide-react';

interface SystemStats {
  activeUsers: number;
  totalUsers: number;
  totalDashboards: number;
  totalQueries: number;
  avgResponseTime: number;
  uptime: string;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  activeConnections: number;
}

interface RecentActivity {
  id: string;
  user: string;
  action: string;
  resource: string;
  timestamp: string;
}

const mockStats: SystemStats = {
  activeUsers: 45,
  totalUsers: 250,
  totalDashboards: 128,
  totalQueries: 15420,
  avgResponseTime: 245,
  uptime: '99.9%',
  cpuUsage: 34,
  memoryUsage: 68,
  diskUsage: 52,
  activeConnections: 12,
};

const mockActivities: RecentActivity[] = [
  { id: '1', user: 'john@example.com', action: 'Created dashboard', resource: 'Sales Q4 Report', timestamp: '2 minutes ago' },
  { id: '2', user: 'jane@example.com', action: 'Updated connection', resource: 'PostgreSQL Prod', timestamp: '5 minutes ago' },
  { id: '3', user: 'admin@example.com', action: 'Added user', resource: 'new.user@example.com', timestamp: '10 minutes ago' },
  { id: '4', user: 'john@example.com', action: 'Executed query', resource: 'Monthly Revenue', timestamp: '15 minutes ago' },
];

export function AdminDashboard() {
  const [stats] = useState<SystemStats>(mockStats);
  const [activities] = useState<RecentActivity[]>(mockActivities);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Admin Dashboard
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            System monitoring and administration
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <Users className="w-4 h-4" />
              Active Users
            </div>
            <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
              {stats.activeUsers}
            </div>
            <div className="text-xs text-gray-400">of {stats.totalUsers} total</div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <Database className="w-4 h-4" />
              Dashboards
            </div>
            <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
              {stats.totalDashboards}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <Activity className="w-4 h-4" />
              Queries Today
            </div>
            <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
              {stats.totalQueries.toLocaleString()}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <Clock className="w-4 h-4" />
              Avg Response
            </div>
            <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
              {stats.avgResponseTime}ms
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center gap-2 text-sm text-green-600">
              <TrendingUp className="w-4 h-4" />
              Uptime
            </div>
            <div className="mt-1 text-2xl font-bold text-green-600">
              {stats.uptime}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* System Resources */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              System Resources
            </h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                    <Cpu className="w-4 h-4" /> CPU
                  </span>
                  <span className="text-gray-900 dark:text-white">{stats.cpuUsage}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${stats.cpuUsage}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                    <Server className="w-4 h-4" /> Memory
                  </span>
                  <span className="text-gray-900 dark:text-white">{stats.memoryUsage}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${stats.memoryUsage}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                    <HardDrive className="w-4 h-4" /> Disk
                  </span>
                  <span className="text-gray-900 dark:text-white">{stats.diskUsage}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-amber-500 h-2 rounded-full"
                    style={{ width: `${stats.diskUsage}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Recent Activity
            </h3>
            <div className="space-y-3">
              {activities.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {activity.action}
                    </div>
                    <div className="text-xs text-gray-500">
                      {activity.user} - {activity.resource}
                    </div>
                  </div>
                  <div className="text-xs text-gray-400">{activity.timestamp}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:bg-gray-50 dark:hover:bg-gray-700 text-left">
            <Users className="w-6 h-6 text-blue-500 mb-2" />
            <div className="font-medium text-gray-900 dark:text-white">User Management</div>
            <div className="text-sm text-gray-500">Manage users & roles</div>
          </button>
          <button className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:bg-gray-50 dark:hover:bg-gray-700 text-left">
            <Shield className="w-6 h-6 text-green-500 mb-2" />
            <div className="font-medium text-gray-900 dark:text-white">Security</div>
            <div className="text-sm text-gray-500">Configure security settings</div>
          </button>
          <button className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:bg-gray-50 dark:hover:bg-gray-700 text-left">
            <Database className="w-6 h-6 text-purple-500 mb-2" />
            <div className="font-medium text-gray-900 dark:text-white">Connections</div>
            <div className="text-sm text-gray-500">Manage data sources</div>
          </button>
          <button className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:bg-gray-50 dark:hover:bg-gray-700 text-left">
            <AlertTriangle className="w-6 h-6 text-amber-500 mb-2" />
            <div className="font-medium text-gray-900 dark:text-white">Alerts</div>
            <div className="text-sm text-gray-500">View system alerts</div>
          </button>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
