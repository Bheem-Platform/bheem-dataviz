/**
 * Subscriptions Page
 *
 * Report and alert subscriptions management.
 */

import { useState } from 'react';
import {
  Bell,
  Mail,
  Plus,
  Calendar,
  Clock,
  Trash2,
  Edit2,
  Pause,
  Play,
} from 'lucide-react';

interface Subscription {
  id: string;
  name: string;
  type: 'report' | 'alert';
  resource: string;
  frequency: string;
  recipients: string[];
  isActive: boolean;
  lastSent?: string;
  nextSend?: string;
}

const mockSubscriptions: Subscription[] = [
  { id: '1', name: 'Weekly Sales Report', type: 'report', resource: 'Sales Dashboard', frequency: 'Weekly (Mon 9AM)', recipients: ['team@example.com'], isActive: true, lastSent: '2026-01-27', nextSend: '2026-02-03' },
  { id: '2', name: 'Daily Revenue Alert', type: 'alert', resource: 'Revenue KPI', frequency: 'Daily (6PM)', recipients: ['manager@example.com', 'cfo@example.com'], isActive: true, lastSent: '2026-01-30', nextSend: '2026-01-31' },
  { id: '3', name: 'Monthly Executive Summary', type: 'report', resource: 'Executive Dashboard', frequency: 'Monthly (1st day)', recipients: ['executives@example.com'], isActive: false, lastSent: '2026-01-01', nextSend: '2026-02-01' },
];

export function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>(mockSubscriptions);
  const [filter, setFilter] = useState<'all' | 'report' | 'alert'>('all');

  const toggleActive = (id: string) => {
    setSubscriptions(subs =>
      subs.map(s => s.id === id ? { ...s, isActive: !s.isActive } : s)
    );
  };

  const filteredSubs = subscriptions.filter(s =>
    filter === 'all' || s.type === filter
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Subscriptions
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Manage your report and alert subscriptions
              </p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New Subscription
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filters */}
        <div className="flex gap-2 mb-6">
          {['all', 'report', 'alert'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f as typeof filter)}
              className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${
                filter === f
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
              }`}
            >
              {f === 'all' ? 'All' : `${f}s`}
            </button>
          ))}
        </div>

        {/* Subscriptions List */}
        <div className="space-y-4">
          {filteredSubs.map((sub) => (
            <div key={sub.id} className="bg-white dark:bg-gray-800 rounded-lg shadow">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className={`p-2 rounded-lg ${
                      sub.type === 'report'
                        ? 'bg-blue-100 dark:bg-blue-900/30'
                        : 'bg-amber-100 dark:bg-amber-900/30'
                    }`}>
                      {sub.type === 'report'
                        ? <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        : <Bell className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                      }
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">{sub.name}</h3>
                      <p className="text-sm text-gray-500">{sub.resource}</p>
                      <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {sub.frequency}
                        </span>
                        <span className="flex items-center gap-1">
                          <Mail className="w-4 h-4" />
                          {sub.recipients.length} recipient{sub.recipients.length > 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      sub.isActive
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                        : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'
                    }`}>
                      {sub.isActive ? 'Active' : 'Paused'}
                    </span>
                    <button
                      onClick={() => toggleActive(sub.id)}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                    >
                      {sub.isActive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {sub.isActive && (
                  <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 flex gap-6 text-sm">
                    <div>
                      <span className="text-gray-500">Last sent:</span>
                      <span className="ml-2 text-gray-900 dark:text-white">{sub.lastSent}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Next send:</span>
                      <span className="ml-2 text-gray-900 dark:text-white">{sub.nextSend}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredSubs.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
            <Bell className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">No subscriptions found</h3>
            <p className="text-gray-500 mt-1">Create a subscription to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Subscriptions;
