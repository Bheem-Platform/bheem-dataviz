/**
 * Schema Tracking Page
 *
 * Track schema changes and drift detection
 */

import { useState, useEffect } from 'react';
import {
  Table2,
  RefreshCw,
  Search,
  AlertTriangle,
  CheckCircle,
  Clock,
  Database,
  Columns,
  Plus,
  Minus,
  Edit3,
  Eye,
  Check,
  Bell,
} from 'lucide-react';
import api from '../lib/api';

interface SchemaSnapshot {
  id: string;
  connection_id: string;
  tables: Array<{
    name: string;
    schema: string;
    columns: Array<{
      name: string;
      type: string;
      nullable: boolean;
    }>;
  }>;
  snapshot_hash: string;
  tables_count: number;
  columns_count: number;
  captured_at: string;
}

interface SchemaChange {
  id: string;
  connection_id: string;
  change_type: 'column_added' | 'column_removed' | 'column_type_changed' | 'table_added' | 'table_removed';
  table_name: string;
  column_name: string | null;
  old_value: Record<string, any> | null;
  new_value: Record<string, any> | null;
  is_breaking: boolean;
  affected_assets: Array<{ id: string; name: string; type: string }>;
  acknowledged: boolean;
  detected_at: string;
}

const changeTypeLabels: Record<string, { label: string; icon: any; color: string }> = {
  column_added: { label: 'Column Added', icon: Plus, color: 'text-green-600 bg-green-50' },
  column_removed: { label: 'Column Removed', icon: Minus, color: 'text-red-600 bg-red-50' },
  column_type_changed: { label: 'Type Changed', icon: Edit3, color: 'text-amber-600 bg-amber-50' },
  table_added: { label: 'Table Added', icon: Plus, color: 'text-green-600 bg-green-50' },
  table_removed: { label: 'Table Removed', icon: Minus, color: 'text-red-600 bg-red-50' },
};

export default function SchemaTracking() {
  const [activeTab, setActiveTab] = useState<'changes' | 'snapshots'>('changes');
  const [snapshots, setSnapshots] = useState<SchemaSnapshot[]>([]);
  const [changes, setChanges] = useState<SchemaChange[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showBreakingOnly, setShowBreakingOnly] = useState(false);
  const [selectedSnapshot, setSelectedSnapshot] = useState<SchemaSnapshot | null>(null);
  const [capturing, setCapturing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [snapshotsRes, changesRes] = await Promise.all([
        api.get('/governance/schema/snapshots'),
        api.get('/governance/schema/changes'),
      ]);
      setSnapshots(snapshotsRes.data);
      setChanges(changesRes.data);
    } catch (err) {
      console.error('Error fetching schema data:', err);
    } finally {
      setLoading(false);
    }
  };

  const captureSnapshot = async (connectionId: string) => {
    try {
      setCapturing(true);
      await api.post('/governance/schema/capture', {
        connection_id: connectionId,
      });
      fetchData();
    } catch (err) {
      console.error('Error capturing snapshot:', err);
    } finally {
      setCapturing(false);
    }
  };

  const acknowledgeChanges = async (changeIds: string[]) => {
    try {
      await api.post('/governance/schema/acknowledge', {
        change_ids: changeIds,
      });
      fetchData();
    } catch (err) {
      console.error('Error acknowledging changes:', err);
    }
  };

  const filteredChanges = changes.filter((c) => {
    const matchesSearch =
      c.table_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.column_name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesBreaking = !showBreakingOnly || c.is_breaking;
    return matchesSearch && matchesBreaking;
  });

  const unacknowledgedCount = changes.filter((c) => !c.acknowledged).length;
  const breakingCount = changes.filter((c) => c.is_breaking && !c.acknowledged).length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Table2 className="h-7 w-7 text-cyan-600" />
            Schema Tracking
          </h1>
          <p className="text-gray-500 mt-1">
            Monitor schema changes and detect drift
          </p>
        </div>
        <button
          onClick={() => captureSnapshot(crypto.randomUUID())}
          disabled={capturing}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${capturing ? 'animate-spin' : ''}`} />
          Capture Snapshot
        </button>
      </div>

      {/* Alert Banner */}
      {breakingCount > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-4">
          <AlertTriangle className="h-6 w-6 text-red-600" />
          <div className="flex-1">
            <h3 className="font-medium text-red-800">
              {breakingCount} Breaking Change{breakingCount !== 1 ? 's' : ''} Detected
            </h3>
            <p className="text-sm text-red-600 mt-1">
              Review and acknowledge these changes to prevent issues with your dashboards and reports.
            </p>
          </div>
          <button
            onClick={() => acknowledgeChanges(changes.filter((c) => c.is_breaking && !c.acknowledged).map((c) => c.id))}
            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
          >
            Acknowledge All
          </button>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-100 text-cyan-600">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{snapshots.length}</div>
              <div className="text-sm text-gray-500">Snapshots</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-100 text-amber-600">
              <Bell className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{unacknowledgedCount}</div>
              <div className="text-sm text-gray-500">Pending Changes</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-100 text-red-600">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{breakingCount}</div>
              <div className="text-sm text-gray-500">Breaking Changes</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-100 text-green-600">
              <CheckCircle className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {changes.filter((c) => c.acknowledged).length}
              </div>
              <div className="text-sm text-gray-500">Acknowledged</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { key: 'changes', label: 'Schema Changes', icon: Edit3 },
            { key: 'snapshots', label: 'Snapshots', icon: Database },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-cyan-500 text-cyan-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search tables or columns..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
          />
        </div>
        {activeTab === 'changes' && (
          <label className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              checked={showBreakingOnly}
              onChange={(e) => setShowBreakingOnly(e.target.checked)}
              className="rounded border-gray-300 text-cyan-600"
            />
            <span className="text-sm text-gray-700">Breaking only</span>
          </label>
        )}
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
        </div>
      ) : (
        <>
          {/* Changes Tab */}
          {activeTab === 'changes' && (
            <div className="space-y-4">
              {filteredChanges.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Edit3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No schema changes detected</p>
                </div>
              ) : (
                filteredChanges.map((change) => {
                  const typeInfo = changeTypeLabels[change.change_type];
                  const Icon = typeInfo.icon;
                  return (
                    <div
                      key={change.id}
                      className={`bg-white rounded-lg border ${
                        change.is_breaking ? 'border-red-200' : 'border-gray-200'
                      } p-4`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4">
                          <div className={`p-2 rounded-lg ${typeInfo.color}`}>
                            <Icon className="h-5 w-5" />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <h3 className="font-medium text-gray-900">{typeInfo.label}</h3>
                              {change.is_breaking && (
                                <span className="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded-full">
                                  Breaking
                                </span>
                              )}
                              {change.acknowledged && (
                                <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full">
                                  Acknowledged
                                </span>
                              )}
                            </div>
                            <div className="mt-1 text-sm text-gray-600">
                              <span className="font-mono bg-gray-100 px-1 rounded">{change.table_name}</span>
                              {change.column_name && (
                                <>
                                  {' → '}
                                  <span className="font-mono bg-gray-100 px-1 rounded">{change.column_name}</span>
                                </>
                              )}
                            </div>

                            {/* Change Details */}
                            {change.change_type === 'column_type_changed' && (
                              <div className="mt-2 text-sm">
                                <span className="text-red-600 line-through">
                                  {change.old_value?.type}
                                </span>
                                {' → '}
                                <span className="text-green-600">
                                  {change.new_value?.type}
                                </span>
                              </div>
                            )}

                            {/* Affected Assets */}
                            {change.affected_assets.length > 0 && (
                              <div className="mt-3">
                                <p className="text-xs text-gray-500 mb-1">Affected Assets:</p>
                                <div className="flex flex-wrap gap-1">
                                  {change.affected_assets.slice(0, 5).map((asset: any) => (
                                    <span
                                      key={asset.id}
                                      className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                                    >
                                      {asset.name}
                                    </span>
                                  ))}
                                  {change.affected_assets.length > 5 && (
                                    <span className="px-2 py-0.5 text-xs text-gray-400">
                                      +{change.affected_assets.length - 5} more
                                    </span>
                                  )}
                                </div>
                              </div>
                            )}

                            <div className="mt-2 text-xs text-gray-400 flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {new Date(change.detected_at).toLocaleString()}
                            </div>
                          </div>
                        </div>
                        {!change.acknowledged && (
                          <button
                            onClick={() => acknowledgeChanges([change.id])}
                            className="flex items-center gap-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                          >
                            <Check className="h-4 w-4" />
                            Acknowledge
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* Snapshots Tab */}
          {activeTab === 'snapshots' && (
            <div className="space-y-4">
              {snapshots.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Database className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No schema snapshots captured</p>
                  <button
                    onClick={() => captureSnapshot(crypto.randomUUID())}
                    className="mt-4 text-cyan-600 hover:underline"
                  >
                    Capture first snapshot
                  </button>
                </div>
              ) : (
                snapshots.map((snapshot) => (
                  <div
                    key={snapshot.id}
                    className="bg-white rounded-lg border border-gray-200 p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="p-3 rounded-lg bg-cyan-50">
                          <Database className="h-6 w-6 text-cyan-600" />
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">
                            Schema Snapshot
                          </h3>
                          <p className="text-sm text-gray-500">
                            {new Date(snapshot.captured_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => setSelectedSnapshot(snapshot)}
                        className="flex items-center gap-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                      >
                        <Eye className="h-4 w-4" />
                        View Details
                      </button>
                    </div>

                    <div className="mt-4 grid grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-gray-50 rounded">
                        <div className="text-lg font-semibold text-gray-900">{snapshot.tables_count}</div>
                        <div className="text-xs text-gray-500">Tables</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded">
                        <div className="text-lg font-semibold text-gray-900">{snapshot.columns_count}</div>
                        <div className="text-xs text-gray-500">Columns</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded">
                        <div className="text-xs font-mono text-gray-600 truncate" title={snapshot.snapshot_hash}>
                          {snapshot.snapshot_hash.substring(0, 12)}...
                        </div>
                        <div className="text-xs text-gray-500">Hash</div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}

      {/* Snapshot Details Modal */}
      {selectedSnapshot && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl p-6 max-h-[80vh] overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Database className="h-5 w-5 text-cyan-600" />
              Schema Snapshot Details
            </h2>

            <div className="text-sm text-gray-500 mb-4">
              Captured: {new Date(selectedSnapshot.captured_at).toLocaleString()}
            </div>

            <div className="space-y-4">
              {selectedSnapshot.tables.map((table: any, index: number) => (
                <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-4 py-2 font-medium text-gray-900 flex items-center gap-2">
                    <Table2 className="h-4 w-4 text-gray-500" />
                    {table.schema}.{table.name}
                  </div>
                  <div className="divide-y divide-gray-100">
                    {table.columns.map((col: any, colIndex: number) => (
                      <div key={colIndex} className="px-4 py-2 flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <Columns className="h-4 w-4 text-gray-400" />
                          <span className="font-mono">{col.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                            {col.type}
                          </span>
                          {col.nullable && (
                            <span className="text-xs text-gray-400">nullable</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedSnapshot(null)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
