/**
 * Embed Manager Page
 *
 * Manage embed tokens for dashboards and charts.
 */

import { useState, useEffect } from 'react';
import {
  Code,
  Plus,
  Copy,
  Check,
  Trash2,
  Eye,
  EyeOff,
  ExternalLink,
  Settings,
  Globe,
  Clock,
  BarChart3,
  Layout,
} from 'lucide-react';
import {
  EmbedToken,
  EmbedResourceType,
  EmbedTheme,
} from '../types/embed';
import { embedApi } from '../lib/api';

export function EmbedManager() {
  const [tokens, setTokens] = useState<EmbedToken[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedToken, setSelectedToken] = useState<EmbedToken | null>(null);
  const [showCodeModal, setShowCodeModal] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTokens = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await embedApi.listTokens();
        setTokens(response.data || []);
      } catch (err) {
        console.error('Failed to fetch embed tokens:', err);
        setError('Failed to load embed tokens. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchTokens();
  }, []);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    resource_type: 'dashboard' as EmbedResourceType,
    resource_id: '',
    allow_interactions: true,
    allow_export: false,
    allow_fullscreen: true,
    theme: 'light' as EmbedTheme,
    show_header: true,
    show_toolbar: false,
    allowed_domains: '',
  });

  const filteredTokens = tokens.filter(t =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCopyToken = (tokenId: string) => {
    navigator.clipboard.writeText(`embed_token_${tokenId}_xxx`);
    setCopiedId(tokenId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleCopyCode = (token: EmbedToken) => {
    setSelectedToken(token);
    setShowCodeModal(true);
  };

  const handleToggleActive = (tokenId: string) => {
    setTokens(tokens.map(t =>
      t.id === tokenId ? { ...t, is_active: !t.is_active } : t
    ));
  };

  const handleDelete = (tokenId: string) => {
    setTokens(tokens.filter(t => t.id !== tokenId));
  };

  const handleCreate = () => {
    const newToken: EmbedToken = {
      id: `token_${Date.now()}`,
      name: formData.name,
      description: formData.description,
      created_by: 'user-1',
      resource_type: formData.resource_type,
      resource_id: formData.resource_id,
      allow_interactions: formData.allow_interactions,
      allow_export: formData.allow_export,
      allow_fullscreen: formData.allow_fullscreen,
      allow_comments: false,
      theme: formData.theme,
      show_header: formData.show_header,
      show_toolbar: formData.show_toolbar,
      allowed_domains: formData.allowed_domains.split(',').map(d => d.trim()).filter(Boolean),
      view_count: 0,
      is_active: true,
      created_at: new Date().toISOString(),
      settings: {},
    };
    setTokens([...tokens, newToken]);
    setShowCreateModal(false);
    setFormData({
      name: '',
      description: '',
      resource_type: 'dashboard',
      resource_id: '',
      allow_interactions: true,
      allow_export: false,
      allow_fullscreen: true,
      theme: 'light',
      show_header: true,
      show_toolbar: false,
      allowed_domains: '',
    });
  };

  const getEmbedCode = (token: EmbedToken) => {
    return `<!-- Bheem DataViz Embed -->
<iframe
  src="https://app.bheem.io/embed/${token.resource_type}/${token.resource_id}?token=${token.id}"
  width="100%"
  height="600"
  frameborder="0"
  allowfullscreen="${token.allow_fullscreen}"
  style="border: none; border-radius: 8px;"
></iframe>

<!-- Or use the SDK -->
<script src="https://cdn.bheem.io/embed.js"></script>
<script>
  BheemEmbed.init({
    container: '#dashboard-container',
    token: '${token.id}',
    theme: '${token.theme}',
    onLoad: () => console.log('Loaded'),
    onError: (err) => console.error(err)
  });
</script>`;
  };

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Embed Manager
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Create and manage embed tokens for dashboards and charts
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Embed Token
            </button>
          </div>

          {/* Summary */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm text-gray-500 dark:text-gray-400">Total Tokens</div>
              <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                {tokens.length}
              </div>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <div className="text-sm text-green-600 dark:text-green-400">Active</div>
              <div className="mt-1 text-2xl font-semibold text-green-700 dark:text-green-300">
                {tokens.filter(t => t.is_active).length}
              </div>
            </div>
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <div className="text-sm text-blue-600 dark:text-blue-400">Total Views</div>
              <div className="mt-1 text-2xl font-semibold text-blue-700 dark:text-blue-300">
                {tokens.reduce((sum, t) => sum + t.view_count, 0).toLocaleString()}
              </div>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <div className="text-sm text-purple-600 dark:text-purple-400">Dashboards</div>
              <div className="mt-1 text-2xl font-semibold text-purple-700 dark:text-purple-300">
                {tokens.filter(t => t.resource_type === 'dashboard').length}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search embed tokens..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          />
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-400">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 text-sm text-red-600 dark:text-red-300 hover:underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
            <p className="mt-4 text-gray-500 dark:text-gray-400">Loading embed tokens...</p>
          </div>
        )}

        {/* Tokens Grid */}
        {!loading && !error && <><div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTokens.map((token) => (
            <div
              key={token.id}
              className={`bg-white dark:bg-gray-800 rounded-lg shadow border-l-4 ${
                token.is_active ? 'border-green-500' : 'border-gray-300'
              }`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      token.resource_type === 'dashboard'
                        ? 'bg-blue-100 dark:bg-blue-900/30'
                        : 'bg-purple-100 dark:bg-purple-900/30'
                    }`}>
                      {token.resource_type === 'dashboard' ? (
                        <Layout className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      ) : (
                        <BarChart3 className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {token.name}
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {token.resource_type}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleToggleActive(token.id)}
                    className={`p-1 rounded ${
                      token.is_active
                        ? 'text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20'
                        : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    {token.is_active ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                  </button>
                </div>

                {token.description && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                    {token.description}
                  </p>
                )}

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Views:</span>
                    <span className="ml-2 font-medium text-gray-900 dark:text-white">
                      {token.view_count.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Theme:</span>
                    <span className="ml-2 font-medium text-gray-900 dark:text-white capitalize">
                      {token.theme}
                    </span>
                  </div>
                </div>

                {/* Domains */}
                {token.allowed_domains.length > 0 && (
                  <div className="mb-4">
                    <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-1">
                      <Globe className="w-3 h-3" />
                      Allowed domains:
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {token.allowed_domains.map((domain) => (
                        <span
                          key={domain}
                          className="px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 rounded"
                        >
                          {domain}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Expiry */}
                {token.expires_at && (
                  <div className="flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400 mb-4">
                    <Clock className="w-3 h-3" />
                    Expires: {new Date(token.expires_at).toLocaleDateString()}
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={() => handleCopyToken(token.id)}
                    className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center justify-center gap-2"
                  >
                    {copiedId === token.id ? (
                      <>
                        <Check className="w-4 h-4 text-green-500" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copy Token
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => handleCopyCode(token)}
                    className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                  >
                    <Code className="w-4 h-4" />
                    Get Code
                  </button>
                  <button
                    onClick={() => handleDelete(token.id)}
                    className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredTokens.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
            <Code className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              No embed tokens
            </h3>
            <p className="mt-1 text-gray-500 dark:text-gray-400">
              Create your first embed token to share dashboards externally.
            </p>
          </div>
        )}
        </>}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Create Embed Token
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Sales Dashboard - Public"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Resource Type
                  </label>
                  <select
                    value={formData.resource_type}
                    onChange={(e) => setFormData({ ...formData, resource_type: e.target.value as EmbedResourceType })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="dashboard">Dashboard</option>
                    <option value="chart">Chart</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Theme
                  </label>
                  <select
                    value={formData.theme}
                    onChange={(e) => setFormData({ ...formData, theme: e.target.value as EmbedTheme })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="auto">Auto</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Allowed Domains (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.allowed_domains}
                  onChange={(e) => setFormData({ ...formData, allowed_domains: e.target.value })}
                  placeholder="example.com, www.example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
                <p className="mt-1 text-xs text-gray-500">Leave empty to allow all domains</p>
              </div>
              <div className="space-y-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.allow_interactions}
                    onChange={(e) => setFormData({ ...formData, allow_interactions: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Allow interactions (filters, drill-down)</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.allow_fullscreen}
                    onChange={(e) => setFormData({ ...formData, allow_fullscreen: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Allow fullscreen</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.show_header}
                    onChange={(e) => setFormData({ ...formData, show_header: e.target.checked })}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Show header</span>
                </label>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={!formData.name}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Create Token
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Code Modal */}
      {showCodeModal && selectedToken && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Embed Code
              </h3>
              <button
                onClick={() => setShowCodeModal(false)}
                className="text-gray-400 hover:text-gray-500"
              >
                &times;
              </button>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                {getEmbedCode(selectedToken)}
              </pre>
            </div>
            <div className="flex justify-end gap-3 mt-4">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(getEmbedCode(selectedToken));
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Copy className="w-4 h-4" />
                Copy Code
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default EmbedManager;
