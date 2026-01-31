/**
 * Integrations Page
 *
 * Third-party service integrations management.
 */

import { useState } from 'react';
import {
  Plug,
  Plus,
  Check,
  AlertCircle,
  Settings,
  Trash2,
  RefreshCw,
} from 'lucide-react';

interface Integration {
  id: string;
  name: string;
  type: string;
  icon: string;
  status: 'connected' | 'error' | 'pending';
  lastSync?: string;
  description: string;
}

const availableIntegrations = [
  { type: 'slack', name: 'Slack', icon: '#', description: 'Send alerts and reports to Slack' },
  { type: 'teams', name: 'Microsoft Teams', icon: '#', description: 'Integrate with MS Teams' },
  { type: 'email', name: 'Email (SMTP)', icon: '#', description: 'Configure email delivery' },
  { type: 'webhook', name: 'Webhooks', icon: '#', description: 'Custom webhook endpoints' },
  { type: 'jira', name: 'Jira', icon: '#', description: 'Create tickets from alerts' },
  { type: 'pagerduty', name: 'PagerDuty', icon: '#', description: 'Incident management' },
];

const mockIntegrations: Integration[] = [
  { id: '1', name: 'Production Slack', type: 'slack', icon: '#', status: 'connected', lastSync: '2 minutes ago', description: '#alerts channel' },
  { id: '2', name: 'Email Notifications', type: 'email', icon: '#', status: 'connected', lastSync: '5 minutes ago', description: 'SMTP configured' },
  { id: '3', name: 'Dev Webhooks', type: 'webhook', icon: '#', status: 'error', lastSync: '1 hour ago', description: 'Connection failed' },
];

export function Integrations() {
  const [integrations] = useState<Integration[]>(mockIntegrations);
  const [showAddModal, setShowAddModal] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-600 bg-green-100 dark:bg-green-900/30';
      case 'error': return 'text-red-600 bg-red-100 dark:bg-red-900/30';
      case 'pending': return 'text-amber-600 bg-amber-100 dark:bg-amber-900/30';
      default: return '';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Integrations
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Connect with third-party services
              </p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Integration
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Active Integrations */}
        <div className="mb-8">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Active Integrations
          </h2>
          <div className="space-y-4">
            {integrations.map((integration) => (
              <div key={integration.id} className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                      <Plug className="w-6 h-6 text-gray-500" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{integration.name}</div>
                      <div className="text-sm text-gray-500">{integration.description}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(integration.status)}`}>
                        {integration.status === 'connected' ? <Check className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                        {integration.status}
                      </span>
                      {integration.lastSync && (
                        <div className="text-xs text-gray-400 mt-1">Last sync: {integration.lastSync}</div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                        <RefreshCw className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                        <Settings className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Available Integrations */}
        <div>
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Available Integrations
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableIntegrations.map((integration) => (
              <div key={integration.type} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                    <Plug className="w-5 h-5 text-gray-500" />
                  </div>
                  <h3 className="font-medium text-gray-900 dark:text-white">{integration.name}</h3>
                </div>
                <p className="text-sm text-gray-500 mb-4">{integration.description}</p>
                <button className="w-full py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 text-sm font-medium">
                  Configure
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Integrations;
