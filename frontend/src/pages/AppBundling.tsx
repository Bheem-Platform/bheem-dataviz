/**
 * App Bundling Page
 *
 * Create and manage app packages (like Power BI Apps)
 */

import { useState, useEffect } from 'react';
import {
  Package,
  Plus,
  Search,
  Edit,
  Trash2,
  Upload,
  Download,
  Eye,
  Globe,
  Lock,
  LayoutDashboard,
  BarChart3,
  FileText,
  Users,
  CheckCircle,
  Clock,
  Star,
  Share2,
} from 'lucide-react';
import api from '../lib/api';

interface App {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  color: string | null;
  dashboards: string[];
  charts: string[];
  reports: string[];
  navigation: Array<{ label: string; type: string; id: string }>;
  landing_dashboard_id: string | null;
  is_public: boolean;
  status: 'draft' | 'published' | 'archived';
  published_at: string | null;
  version: string;
  install_count: number;
  view_count: number;
  created_at: string;
}

interface AppInstallation {
  id: string;
  app_id: string;
  installed_by: string;
  target_workspace_id: string;
  preferences: Record<string, any>;
  is_active: boolean;
  installed_at: string;
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  published: 'bg-green-100 text-green-800',
  archived: 'bg-red-100 text-red-800',
};

const defaultColors = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
  '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1',
];

export default function AppBundling() {
  const [apps, setApps] = useState<App[]>([]);
  const [installations, setInstallations] = useState<AppInstallation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedApp, setSelectedApp] = useState<App | null>(null);

  const [newApp, setNewApp] = useState({
    name: '',
    slug: '',
    description: '',
    icon: '',
    color: defaultColors[0],
    is_public: false,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [appsRes, installsRes] = await Promise.all([
        api.get('/governance/apps'),
        api.get('/governance/apps/installations'),
      ]);
      setApps(appsRes.data);
      setInstallations(installsRes.data);
    } catch (err) {
      console.error('Error fetching apps:', err);
    } finally {
      setLoading(false);
    }
  };

  const createApp = async () => {
    try {
      await api.post('/governance/apps', {
        ...newApp,
        workspace_id: crypto.randomUUID(),
        dashboards: [],
        charts: [],
        reports: [],
        navigation: [],
      });
      setShowCreateModal(false);
      setNewApp({
        name: '',
        slug: '',
        description: '',
        icon: '',
        color: defaultColors[0],
        is_public: false,
      });
      fetchData();
    } catch (err) {
      console.error('Error creating app:', err);
    }
  };

  const publishApp = async (appId: string) => {
    try {
      await api.post(`/governance/apps/${appId}/publish`, {});
      fetchData();
    } catch (err) {
      console.error('Error publishing app:', err);
    }
  };

  const installApp = async (appId: string) => {
    try {
      await api.post(`/governance/apps/${appId}/install`, {
        target_workspace_id: crypto.randomUUID(),
      });
      fetchData();
    } catch (err) {
      console.error('Error installing app:', err);
    }
  };

  const filteredApps = apps.filter(
    (a) =>
      a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Stats
  const totalApps = apps.length;
  const publishedApps = apps.filter((a) => a.status === 'published').length;
  const totalInstalls = apps.reduce((sum, a) => sum + a.install_count, 0);
  const totalViews = apps.reduce((sum, a) => sum + a.view_count, 0);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Package className="h-7 w-7 text-violet-600" />
            App Bundling
          </h1>
          <p className="text-gray-500 mt-1">
            Create and distribute analytics apps
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700"
        >
          <Plus className="h-4 w-4" />
          Create App
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-violet-100 text-violet-600">
              <Package className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{totalApps}</div>
              <div className="text-sm text-gray-500">Total Apps</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-100 text-green-600">
              <CheckCircle className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{publishedApps}</div>
              <div className="text-sm text-gray-500">Published</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
              <Download className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{totalInstalls}</div>
              <div className="text-sm text-gray-500">Installations</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-100 text-amber-600">
              <Eye className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{totalViews}</div>
              <div className="text-sm text-gray-500">Total Views</div>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search apps..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
        />
      </div>

      {/* Apps Grid */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
        </div>
      ) : filteredApps.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <Package className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No apps created yet</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-4 text-violet-600 hover:underline"
          >
            Create your first app
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredApps.map((app) => (
            <div
              key={app.id}
              className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
            >
              {/* App Header */}
              <div
                className="h-24 flex items-center justify-center"
                style={{ backgroundColor: app.color || defaultColors[0] }}
              >
                <div className="text-4xl">
                  {app.icon || '📦'}
                </div>
              </div>

              {/* App Content */}
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{app.name}</h3>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                      {app.description || 'No description'}
                    </p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[app.status]}`}>
                    {app.status}
                  </span>
                </div>

                {/* App Stats */}
                <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <LayoutDashboard className="h-4 w-4" />
                    <span>{app.dashboards.length}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <BarChart3 className="h-4 w-4" />
                    <span>{app.charts.length}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <FileText className="h-4 w-4" />
                    <span>{app.reports.length}</span>
                  </div>
                  <div className="flex items-center gap-1 ml-auto">
                    {app.is_public ? (
                      <Globe className="h-4 w-4 text-green-500" />
                    ) : (
                      <Lock className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                </div>

                {/* Version & Installs */}
                <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                  <span>v{app.version}</span>
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1">
                      <Download className="h-3 w-3" />
                      {app.install_count}
                    </span>
                    <span className="flex items-center gap-1">
                      <Eye className="h-3 w-3" />
                      {app.view_count}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-4 flex items-center gap-2">
                  <button
                    onClick={() => setSelectedApp(app)}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                  >
                    <Eye className="h-4 w-4" />
                    View
                  </button>
                  {app.status === 'draft' && (
                    <button
                      onClick={() => publishApp(app.id)}
                      className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm bg-violet-100 text-violet-700 rounded hover:bg-violet-200"
                    >
                      <Upload className="h-4 w-4" />
                      Publish
                    </button>
                  )}
                  {app.status === 'published' && (
                    <button
                      onClick={() => installApp(app.id)}
                      className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
                    >
                      <Download className="h-4 w-4" />
                      Install
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create App Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Create New App</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">App Name</label>
                <input
                  type="text"
                  value={newApp.name}
                  onChange={(e) => setNewApp({ ...newApp, name: e.target.value, slug: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500"
                  placeholder="Sales Analytics"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL Slug</label>
                <input
                  type="text"
                  value={newApp.slug}
                  onChange={(e) => setNewApp({ ...newApp, slug: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500"
                  placeholder="sales-analytics"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newApp.description}
                  onChange={(e) => setNewApp({ ...newApp, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500"
                  rows={3}
                  placeholder="A comprehensive sales analytics package..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Icon (Emoji)</label>
                <input
                  type="text"
                  value={newApp.icon}
                  onChange={(e) => setNewApp({ ...newApp, icon: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500"
                  placeholder="📊"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Theme Color</label>
                <div className="flex gap-2">
                  {defaultColors.map((color) => (
                    <button
                      key={color}
                      onClick={() => setNewApp({ ...newApp, color })}
                      className={`w-8 h-8 rounded-full ${newApp.color === color ? 'ring-2 ring-offset-2 ring-violet-500' : ''}`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={newApp.is_public}
                  onChange={(e) => setNewApp({ ...newApp, is_public: e.target.checked })}
                  className="rounded border-gray-300 text-violet-600"
                />
                <label htmlFor="is_public" className="text-sm text-gray-700">
                  Make this app publicly available
                </label>
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={createApp}
                className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700"
              >
                Create App
              </button>
            </div>
          </div>
        </div>
      )}

      {/* App Details Modal */}
      {selectedApp && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-start gap-4 mb-6">
              <div
                className="w-16 h-16 rounded-lg flex items-center justify-center text-3xl"
                style={{ backgroundColor: selectedApp.color || defaultColors[0] }}
              >
                {selectedApp.icon || '📦'}
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-gray-900">{selectedApp.name}</h2>
                <p className="text-gray-500 mt-1">{selectedApp.description}</p>
                <div className="flex items-center gap-3 mt-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[selectedApp.status]}`}>
                    {selectedApp.status}
                  </span>
                  <span className="text-sm text-gray-500">v{selectedApp.version}</span>
                </div>
              </div>
            </div>

            {/* Contents */}
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-700 mb-2">Included Content</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center gap-2 text-blue-700">
                      <LayoutDashboard className="h-5 w-5" />
                      <span className="text-lg font-semibold">{selectedApp.dashboards.length}</span>
                    </div>
                    <p className="text-sm text-blue-600 mt-1">Dashboards</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="flex items-center gap-2 text-green-700">
                      <BarChart3 className="h-5 w-5" />
                      <span className="text-lg font-semibold">{selectedApp.charts.length}</span>
                    </div>
                    <p className="text-sm text-green-600 mt-1">Charts</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <div className="flex items-center gap-2 text-purple-700">
                      <FileText className="h-5 w-5" />
                      <span className="text-lg font-semibold">{selectedApp.reports.length}</span>
                    </div>
                    <p className="text-sm text-purple-600 mt-1">Reports</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-medium text-gray-700 mb-2">Analytics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg flex items-center gap-3">
                    <Download className="h-5 w-5 text-gray-500" />
                    <div>
                      <div className="font-semibold text-gray-900">{selectedApp.install_count}</div>
                      <div className="text-sm text-gray-500">Installations</div>
                    </div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg flex items-center gap-3">
                    <Eye className="h-5 w-5 text-gray-500" />
                    <div>
                      <div className="font-semibold text-gray-900">{selectedApp.view_count}</div>
                      <div className="text-sm text-gray-500">Views</div>
                    </div>
                  </div>
                </div>
              </div>

              {selectedApp.published_at && (
                <div className="text-sm text-gray-500">
                  Published on {new Date(selectedApp.published_at).toLocaleDateString()}
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setSelectedApp(null)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
              <button className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 flex items-center gap-2">
                <Edit className="h-4 w-4" />
                Edit App
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
