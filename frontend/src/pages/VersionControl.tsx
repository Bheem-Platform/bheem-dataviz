/**
 * Version Control Page
 *
 * Manage asset versions and history
 */

import { useState, useEffect } from 'react';
import {
  GitCommit,
  History,
  Search,
  RotateCcw,
  Eye,
  GitCompare,
  Tag,
  Clock,
  User,
  FileText,
  ChevronDown,
  ChevronRight,
  Check,
  AlertCircle,
} from 'lucide-react';
import api from '../lib/api';

interface AssetVersion {
  id: string;
  asset_type: 'dashboard' | 'chart' | 'semantic_model' | 'transform' | 'report' | 'kpi' | 'rls_policy';
  asset_id: string;
  asset_name: string;
  version_number: number;
  version_label: string | null;
  changes_summary: string | null;
  snapshot: Record<string, any>;
  changes_diff: Record<string, any>;
  created_by: string;
  created_at: string;
  environment_id: string | null;
  is_current: boolean;
  is_published: boolean;
}

interface VersionComparison {
  version_a_id: string;
  version_b_id: string;
  additions: Array<{ path: string; value: any }>;
  removals: Array<{ path: string; value: any }>;
  modifications: Array<{ path: string; old_value: any; new_value: any }>;
  total_changes: number;
  breaking_changes: boolean;
}

const assetTypeColors: Record<string, string> = {
  dashboard: 'bg-blue-100 text-blue-800',
  chart: 'bg-green-100 text-green-800',
  semantic_model: 'bg-purple-100 text-purple-800',
  transform: 'bg-orange-100 text-orange-800',
  report: 'bg-pink-100 text-pink-800',
  kpi: 'bg-teal-100 text-teal-800',
  rls_policy: 'bg-red-100 text-red-800',
};

export default function VersionControl() {
  const [versions, setVersions] = useState<AssetVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAssetType, setSelectedAssetType] = useState<string>('all');
  const [selectedVersion, setSelectedVersion] = useState<AssetVersion | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [compareVersions, setCompareVersions] = useState<[string | null, string | null]>([null, null]);
  const [comparison, setComparison] = useState<VersionComparison | null>(null);
  const [showComparisonModal, setShowComparisonModal] = useState(false);
  const [expandedAssets, setExpandedAssets] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchVersions();
  }, []);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      const response = await api.get('/governance/versions');
      setVersions(response.data);
    } catch (err) {
      console.error('Error fetching versions:', err);
    } finally {
      setLoading(false);
    }
  };

  const rollbackToVersion = async (versionId: string) => {
    try {
      await api.post(`/governance/versions/${versionId}/rollback`, {
        version_id: versionId,
        reason: 'Rollback via UI',
      });
      fetchVersions();
    } catch (err) {
      console.error('Error rolling back:', err);
    }
  };

  const compareVersionsHandler = async () => {
    if (!compareVersions[0] || !compareVersions[1]) return;
    try {
      const response = await api.post('/governance/versions/compare', {
        version_a_id: compareVersions[0],
        version_b_id: compareVersions[1],
      });
      setComparison(response.data);
      setShowComparisonModal(true);
    } catch (err) {
      console.error('Error comparing versions:', err);
    }
  };

  // Group versions by asset
  const versionsByAsset = versions.reduce((acc, version) => {
    const key = `${version.asset_type}-${version.asset_id}`;
    if (!acc[key]) {
      acc[key] = {
        asset_name: version.asset_name,
        asset_type: version.asset_type,
        asset_id: version.asset_id,
        versions: [],
      };
    }
    acc[key].versions.push(version);
    return acc;
  }, {} as Record<string, { asset_name: string; asset_type: string; asset_id: string; versions: AssetVersion[] }>);

  // Sort versions within each asset by version number (descending)
  Object.values(versionsByAsset).forEach((asset) => {
    asset.versions.sort((a, b) => b.version_number - a.version_number);
  });

  const filteredAssets = Object.values(versionsByAsset).filter((asset) => {
    const matchesSearch = asset.asset_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = selectedAssetType === 'all' || asset.asset_type === selectedAssetType;
    return matchesSearch && matchesType;
  });

  const toggleAsset = (key: string) => {
    const newExpanded = new Set(expandedAssets);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedAssets(newExpanded);
  };

  const toggleCompareVersion = (versionId: string) => {
    if (compareVersions[0] === versionId) {
      setCompareVersions([null, compareVersions[1]]);
    } else if (compareVersions[1] === versionId) {
      setCompareVersions([compareVersions[0], null]);
    } else if (!compareVersions[0]) {
      setCompareVersions([versionId, compareVersions[1]]);
    } else if (!compareVersions[1]) {
      setCompareVersions([compareVersions[0], versionId]);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <GitCommit className="h-7 w-7 text-indigo-600" />
            Version Control
          </h1>
          <p className="text-gray-500 mt-1">
            Track changes and manage asset versions
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setCompareMode(!compareMode);
              setCompareVersions([null, null]);
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              compareMode
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <GitCompare className="h-4 w-4" />
            Compare Mode
          </button>
          {compareMode && compareVersions[0] && compareVersions[1] && (
            <button
              onClick={compareVersionsHandler}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Compare Selected
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search assets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <select
          value={selectedAssetType}
          onChange={(e) => setSelectedAssetType(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="all">All Types</option>
          <option value="dashboard">Dashboards</option>
          <option value="chart">Charts</option>
          <option value="semantic_model">Semantic Models</option>
          <option value="transform">Transforms</option>
          <option value="report">Reports</option>
          <option value="kpi">KPIs</option>
          <option value="rls_policy">RLS Policies</option>
        </select>
      </div>

      {/* Compare Mode Info */}
      {compareMode && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
          <div className="flex items-center gap-4">
            <GitCompare className="h-5 w-5 text-indigo-600" />
            <div className="flex-1">
              <p className="text-sm text-indigo-800">
                Select two versions to compare. Click on version cards to select them.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 bg-white border border-indigo-200 rounded text-sm">
                {compareVersions[0] ? 'Version A selected' : 'Select Version A'}
              </span>
              <span className="text-indigo-400">vs</span>
              <span className="px-3 py-1 bg-white border border-indigo-200 rounded text-sm">
                {compareVersions[1] ? 'Version B selected' : 'Select Version B'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : filteredAssets.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <History className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No version history found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAssets.map((asset) => {
            const key = `${asset.asset_type}-${asset.asset_id}`;
            const isExpanded = expandedAssets.has(key);
            const currentVersion = asset.versions.find((v) => v.is_current);

            return (
              <div key={key} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                {/* Asset Header */}
                <button
                  onClick={() => toggleAsset(key)}
                  className="w-full p-4 flex items-center justify-between hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    {isExpanded ? (
                      <ChevronDown className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronRight className="h-5 w-5 text-gray-400" />
                    )}
                    <FileText className="h-5 w-5 text-gray-500" />
                    <div className="text-left">
                      <h3 className="font-medium text-gray-900">{asset.asset_name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-2 py-0.5 text-xs font-medium rounded ${assetTypeColors[asset.asset_type]}`}>
                          {asset.asset_type.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-gray-500">
                          {asset.versions.length} version{asset.versions.length !== 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                  </div>
                  {currentVersion && (
                    <div className="flex items-center gap-2">
                      <Tag className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        v{currentVersion.version_number}
                        {currentVersion.version_label && ` (${currentVersion.version_label})`}
                      </span>
                    </div>
                  )}
                </button>

                {/* Version List */}
                {isExpanded && (
                  <div className="border-t border-gray-200">
                    {asset.versions.map((version, index) => (
                      <div
                        key={version.id}
                        className={`p-4 border-b border-gray-100 last:border-b-0 ${
                          compareMode && (compareVersions[0] === version.id || compareVersions[1] === version.id)
                            ? 'bg-indigo-50'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            {compareMode && (
                              <button
                                onClick={() => toggleCompareVersion(version.id)}
                                className={`mt-1 p-1 rounded ${
                                  compareVersions[0] === version.id || compareVersions[1] === version.id
                                    ? 'bg-indigo-600 text-white'
                                    : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                                }`}
                              >
                                <Check className="h-4 w-4" />
                              </button>
                            )}
                            <div className="relative">
                              <div className={`p-2 rounded-full ${version.is_current ? 'bg-green-100' : 'bg-gray-100'}`}>
                                <GitCommit className={`h-4 w-4 ${version.is_current ? 'text-green-600' : 'text-gray-500'}`} />
                              </div>
                              {index < asset.versions.length - 1 && (
                                <div className="absolute top-10 left-1/2 -translate-x-1/2 w-0.5 h-full bg-gray-200" />
                              )}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-gray-900">
                                  Version {version.version_number}
                                </span>
                                {version.version_label && (
                                  <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                                    {version.version_label}
                                  </span>
                                )}
                                {version.is_current && (
                                  <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded">
                                    Current
                                  </span>
                                )}
                                {version.is_published && (
                                  <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">
                                    Published
                                  </span>
                                )}
                              </div>
                              {version.changes_summary && (
                                <p className="text-sm text-gray-600 mt-1">{version.changes_summary}</p>
                              )}
                              <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                <span className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  {new Date(version.created_at).toLocaleString()}
                                </span>
                                <span className="flex items-center gap-1">
                                  <User className="h-3 w-3" />
                                  User
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => setSelectedVersion(version)}
                              className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded"
                              title="View snapshot"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                            {!version.is_current && (
                              <button
                                onClick={() => rollbackToVersion(version.id)}
                                className="p-2 text-gray-400 hover:text-amber-600 hover:bg-amber-50 rounded"
                                title="Rollback to this version"
                              >
                                <RotateCcw className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Version Details Modal */}
      {selectedVersion && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl p-6 max-h-[80vh] overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Eye className="h-5 w-5 text-indigo-600" />
              Version {selectedVersion.version_number} Snapshot
            </h2>
            <div className="bg-gray-50 rounded-lg p-4">
              <pre className="text-sm text-gray-600 overflow-auto">
                {JSON.stringify(selectedVersion.snapshot, null, 2)}
              </pre>
            </div>
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedVersion(null)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Modal */}
      {showComparisonModal && comparison && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl p-6 max-h-[80vh] overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <GitCompare className="h-5 w-5 text-indigo-600" />
              Version Comparison
            </h2>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-700">{comparison.additions.length}</div>
                <div className="text-sm text-green-600">Additions</div>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-red-700">{comparison.removals.length}</div>
                <div className="text-sm text-red-600">Removals</div>
              </div>
              <div className="bg-amber-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-amber-700">{comparison.modifications.length}</div>
                <div className="text-sm text-amber-600">Modifications</div>
              </div>
            </div>

            {comparison.breaking_changes && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="text-red-700 font-medium">This comparison contains breaking changes</span>
              </div>
            )}

            <div className="space-y-4">
              {comparison.additions.length > 0 && (
                <div>
                  <h3 className="font-medium text-green-700 mb-2">Additions</h3>
                  {comparison.additions.map((a: any, i: number) => (
                    <div key={i} className="p-2 bg-green-50 rounded text-sm font-mono">
                      + {a.path}: {JSON.stringify(a.value)}
                    </div>
                  ))}
                </div>
              )}

              {comparison.removals.length > 0 && (
                <div>
                  <h3 className="font-medium text-red-700 mb-2">Removals</h3>
                  {comparison.removals.map((r: any, i: number) => (
                    <div key={i} className="p-2 bg-red-50 rounded text-sm font-mono">
                      - {r.path}: {JSON.stringify(r.value)}
                    </div>
                  ))}
                </div>
              )}

              {comparison.modifications.length > 0 && (
                <div>
                  <h3 className="font-medium text-amber-700 mb-2">Modifications</h3>
                  {comparison.modifications.map((m: any, i: number) => (
                    <div key={i} className="p-2 bg-amber-50 rounded text-sm font-mono">
                      ~ {m.path}: {JSON.stringify(m.old_value)} → {JSON.stringify(m.new_value)}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => {
                  setShowComparisonModal(false);
                  setComparison(null);
                }}
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
