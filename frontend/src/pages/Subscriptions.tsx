/**
 * Subscriptions Page
 *
 * Report and alert subscriptions management.
 */

import { useState, useEffect } from 'react';
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
  AlertCircle,
} from 'lucide-react';
import { subscriptionsApi } from '../lib/api';

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

export function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [filter, setFilter] = useState<'all' | 'report' | 'alert'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSubscriptions = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch both subscriptions and alerts in parallel
        const [subscriptionsRes, alertsRes] = await Promise.all([
          subscriptionsApi.listSubscriptions(),
          subscriptionsApi.listAlerts(),
        ]);

        // Transform subscriptions (reports) to match the Subscription interface
        const reportSubs: Subscription[] = (subscriptionsRes.data || []).map((sub: Record<string, unknown>) => ({
          id: sub.id as string,
          name: sub.name as string,
          type: 'report' as const,
          resource: (sub.dashboard_id as string) || 'Dashboard',
          frequency: ((sub.schedule as Record<string, unknown>)?.frequency as string) || 'Unknown',
          recipients: (sub.recipients as string[]) || [],
          isActive: sub.enabled as boolean,
          lastSent: sub.last_sent_at as string | undefined,
          nextSend: sub.next_run_at as string | undefined,
        }));

        // Transform alerts to match the Subscription interface
        const alertSubs: Subscription[] = (alertsRes.data || []).map((alert: Record<string, unknown>) => ({
          id: alert.id as string,
          name: alert.name as string,
          type: 'alert' as const,
          resource: (alert.target_id as string) || 'Resource',
          frequency: (alert.evaluation_frequency as string) || 'Unknown',
          recipients: ((alert.notifications as Array<Record<string, unknown>>) || []).map((n) => n.channel as string),
          isActive: alert.enabled as boolean,
          lastSent: alert.last_triggered_at as string | undefined,
          nextSend: undefined,
        }));

        setSubscriptions([...reportSubs, ...alertSubs]);
      } catch (err) {
        console.error('Failed to fetch subscriptions:', err);
        setError('Failed to load subscriptions. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchSubscriptions();
  }, []);

  const toggleActive = async (id: string) => {
    const subscription = subscriptions.find(s => s.id === id);
    if (!subscription) return;

    try {
      if (subscription.type === 'report') {
        if (subscription.isActive) {
          await subscriptionsApi.pauseSubscription(id);
        } else {
          await subscriptionsApi.resumeSubscription(id);
        }
      } else {
        if (subscription.isActive) {
          await subscriptionsApi.pauseAlert(id);
        } else {
          await subscriptionsApi.resumeAlert(id);
        }
      }
      setSubscriptions(subs =>
        subs.map(s => s.id === id ? { ...s, isActive: !s.isActive } : s)
      );
    } catch (err) {
      console.error('Failed to toggle subscription status:', err);
      setError('Failed to update subscription status.');
    }
  };

  const filteredSubs = subscriptions.filter(s =>
    filter === 'all' || s.type === filter
  );

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
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

        {/* Error State */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" />
            <p className="text-red-700 dark:text-red-400">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-500 dark:text-gray-400">Loading subscriptions...</p>
          </div>
        )}

        {/* Subscriptions List */}
        {!loading && <div className="space-y-4">
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
        </div>}

        {!loading && filteredSubs.length === 0 && (
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
