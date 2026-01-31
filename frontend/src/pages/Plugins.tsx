/**
 * Plugins Page
 *
 * Plugin management and marketplace.
 */

import { useState } from 'react';
import {
  Puzzle,
  Search,
  Download,
  Check,
  Star,
  Settings,
  Trash2,
  ExternalLink,
} from 'lucide-react';

interface Plugin {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  type: string;
  downloads: number;
  rating: number;
  isInstalled: boolean;
  isEnabled: boolean;
}

const mockPlugins: Plugin[] = [
  { id: '1', name: 'Slack Integration', description: 'Send alerts and reports to Slack channels', author: 'Bheem Team', version: '1.2.0', type: 'integration', downloads: 15420, rating: 4.8, isInstalled: true, isEnabled: true },
  { id: '2', name: 'BigQuery Connector', description: 'Connect to Google BigQuery data warehouse', author: 'Bheem Team', version: '2.0.1', type: 'connector', downloads: 12340, rating: 4.9, isInstalled: true, isEnabled: true },
  { id: '3', name: 'Sankey Charts', description: 'Beautiful flow diagrams for your data', author: 'Community', version: '1.0.0', type: 'visualization', downloads: 8560, rating: 4.5, isInstalled: false, isEnabled: false },
  { id: '4', name: 'PDF Export Pro', description: 'Advanced PDF export with custom templates', author: 'Bheem Team', version: '1.5.0', type: 'export', downloads: 9870, rating: 4.7, isInstalled: true, isEnabled: false },
  { id: '5', name: 'LDAP Authentication', description: 'Enterprise LDAP/Active Directory integration', author: 'Enterprise', version: '1.1.0', type: 'auth', downloads: 5430, rating: 4.6, isInstalled: false, isEnabled: false },
];

const categories = ['All', 'Connector', 'Visualization', 'Integration', 'Export', 'Auth'];

export function Plugins() {
  const [plugins] = useState<Plugin[]>(mockPlugins);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [activeTab, setActiveTab] = useState<'installed' | 'marketplace'>('installed');

  const filteredPlugins = plugins.filter(plugin => {
    const matchesSearch = plugin.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || plugin.type.toLowerCase() === selectedCategory.toLowerCase();
    const matchesTab = activeTab === 'marketplace' || (activeTab === 'installed' && plugin.isInstalled);
    return matchesSearch && matchesCategory && matchesTab;
  });

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Plugins
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Extend functionality with plugins
              </p>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 flex gap-4 border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('installed')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'installed'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Installed ({plugins.filter(p => p.isInstalled).length})
            </button>
            <button
              onClick={() => setActiveTab('marketplace')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'marketplace'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Marketplace
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search plugins..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            />
          </div>
          <div className="flex gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-2 rounded-lg text-sm ${
                  selectedCategory === cat
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Plugins Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPlugins.map((plugin) => (
            <div key={plugin.id} className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                      <Puzzle className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">{plugin.name}</h3>
                      <p className="text-xs text-gray-500">by {plugin.author}</p>
                    </div>
                  </div>
                  <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-gray-600 dark:text-gray-400">
                    v{plugin.version}
                  </span>
                </div>

                <p className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                  {plugin.description}
                </p>

                <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <Download className="w-4 h-4" />
                    {(plugin.downloads / 1000).toFixed(1)}k
                  </span>
                  <span className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                    {plugin.rating}
                  </span>
                  <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    {plugin.type}
                  </span>
                </div>

                <div className="mt-4 flex gap-2">
                  {plugin.isInstalled ? (
                    <>
                      <button
                        className={`flex-1 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-1 ${
                          plugin.isEnabled
                            ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                            : 'bg-gray-100 text-gray-600 dark:bg-gray-700'
                        }`}
                      >
                        <Check className="w-4 h-4" />
                        {plugin.isEnabled ? 'Enabled' : 'Disabled'}
                      </button>
                      <button className="p-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-500 hover:text-gray-700">
                        <Settings className="w-4 h-4" />
                      </button>
                      <button className="p-2 border border-gray-300 dark:border-gray-600 rounded-lg text-red-500 hover:text-red-700">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </>
                  ) : (
                    <button className="flex-1 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2 hover:bg-blue-700">
                      <Download className="w-4 h-4" />
                      Install
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredPlugins.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
            <Puzzle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">No plugins found</h3>
            <p className="text-gray-500 mt-1">Try adjusting your search or filters</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Plugins;
