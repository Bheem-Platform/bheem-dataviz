/**
 * Data Lineage Page
 *
 * Visualize data flow and impact analysis
 */

import { useState, useEffect, useCallback } from 'react';
import {
  GitBranch,
  Search,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Database,
  Table2,
  BarChart3,
  LayoutDashboard,
  Columns,
  Box,
  AlertTriangle,
  ChevronRight,
  Eye,
  RefreshCw,
} from 'lucide-react';
import api from '../lib/api';

interface LineageNode {
  id: string;
  node_type: 'connection' | 'table' | 'column' | 'transform' | 'semantic_model' | 'measure' | 'dimension' | 'chart' | 'dashboard' | 'kpi';
  asset_id: string;
  asset_name: string;
  connection_id: string | null;
  schema_name: string | null;
  table_name: string | null;
  column_name: string | null;
  description: string | null;
  node_metadata: Record<string, any>;
  quality_score: number | null;
}

interface LineageEdge {
  id: string;
  source_node_id: string;
  target_node_id: string;
  edge_type: string;
  transformation_type: string | null;
  transformation_sql: string | null;
  confidence: number;
  is_active: boolean;
}

interface ImpactAnalysis {
  source_node_id: string;
  change_type: string;
  affected_nodes: Array<{ id: string; name: string; type: string }>;
  affected_dashboards: Array<{ id: string; name: string }>;
  affected_charts: Array<{ id: string; name: string }>;
  total_affected: number;
  critical_impacts: number;
}

const nodeTypeIcons: Record<string, any> = {
  connection: Database,
  table: Table2,
  column: Columns,
  transform: RefreshCw,
  semantic_model: Box,
  measure: BarChart3,
  dimension: Box,
  chart: BarChart3,
  dashboard: LayoutDashboard,
  kpi: BarChart3,
};

const nodeTypeColors: Record<string, string> = {
  connection: 'bg-blue-500',
  table: 'bg-green-500',
  column: 'bg-cyan-500',
  transform: 'bg-purple-500',
  semantic_model: 'bg-orange-500',
  measure: 'bg-pink-500',
  dimension: 'bg-indigo-500',
  chart: 'bg-red-500',
  dashboard: 'bg-amber-500',
  kpi: 'bg-teal-500',
};

export default function DataLineage() {
  const [nodes, setNodes] = useState<LineageNode[]>([]);
  const [edges, setEdges] = useState<LineageEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<LineageNode | null>(null);
  const [impactAnalysis, setImpactAnalysis] = useState<ImpactAnalysis | null>(null);
  const [showImpactModal, setShowImpactModal] = useState(false);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    fetchLineage();
  }, []);

  const fetchLineage = async () => {
    try {
      setLoading(true);
      const [nodesRes, edgesRes] = await Promise.all([
        api.get('/governance/lineage/nodes'),
        api.get('/governance/lineage/edges'),
      ]);
      setNodes(nodesRes.data);
      setEdges(edgesRes.data);
    } catch (err) {
      console.error('Error fetching lineage:', err);
    } finally {
      setLoading(false);
    }
  };

  const analyzeImpact = async (nodeId: string, changeType: string) => {
    try {
      const response = await api.post('/governance/lineage/impact', {
        source_node_id: nodeId,
        change_type: changeType,
      });
      setImpactAnalysis(response.data);
      setShowImpactModal(true);
    } catch (err) {
      console.error('Error analyzing impact:', err);
    }
  };

  const filteredNodes = nodes.filter(
    (n) =>
      n.asset_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      n.node_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Group nodes by type for the legend/stats
  const nodesByType = nodes.reduce((acc, node) => {
    acc[node.node_type] = (acc[node.node_type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Get upstream and downstream nodes for selected node
  const getUpstream = (nodeId: string): LineageNode[] => {
    const upstreamEdges = edges.filter((e) => e.target_node_id === nodeId);
    return nodes.filter((n) => upstreamEdges.some((e) => e.source_node_id === n.id));
  };

  const getDownstream = (nodeId: string): LineageNode[] => {
    const downstreamEdges = edges.filter((e) => e.source_node_id === nodeId);
    return nodes.filter((n) => downstreamEdges.some((e) => e.target_node_id === n.id));
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <GitBranch className="h-7 w-7 text-teal-600" />
            Data Lineage
          </h1>
          <p className="text-gray-500 mt-1">
            Track data flow and understand impact of changes
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded"
          >
            <ZoomOut className="h-5 w-5" />
          </button>
          <span className="text-sm text-gray-600">{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => setZoom(Math.min(2, zoom + 0.1))}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded"
          >
            <ZoomIn className="h-5 w-5" />
          </button>
          <button
            onClick={() => setZoom(1)}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded"
          >
            <Maximize2 className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {Object.entries(nodesByType).map(([type, count]) => {
          const Icon = nodeTypeIcons[type] || Box;
          return (
            <div key={type} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${nodeTypeColors[type]} text-white`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                  <div className="text-sm text-gray-500 capitalize">{type.replace('_', ' ')}s</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Node List */}
        <div className="lg:col-span-1 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search nodes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            />
          </div>

          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden max-h-[600px] overflow-y-auto">
            {loading ? (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-teal-600"></div>
              </div>
            ) : filteredNodes.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <GitBranch className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>No lineage nodes found</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {filteredNodes.map((node) => {
                  const Icon = nodeTypeIcons[node.node_type] || Box;
                  return (
                    <button
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      className={`w-full p-3 text-left hover:bg-gray-50 flex items-center gap-3 ${
                        selectedNode?.id === node.id ? 'bg-teal-50 border-l-2 border-teal-500' : ''
                      }`}
                    >
                      <div className={`p-2 rounded ${nodeTypeColors[node.node_type]} text-white`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 truncate">{node.asset_name}</div>
                        <div className="text-xs text-gray-500 capitalize">{node.node_type.replace('_', ' ')}</div>
                      </div>
                      {node.quality_score !== null && (
                        <div className={`text-xs px-2 py-1 rounded ${
                          node.quality_score >= 90 ? 'bg-green-100 text-green-700' :
                          node.quality_score >= 70 ? 'bg-yellow-100 text-yellow-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {node.quality_score}%
                        </div>
                      )}
                      <ChevronRight className="h-4 w-4 text-gray-400" />
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Lineage Graph / Details */}
        <div className="lg:col-span-2">
          {selectedNode ? (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-lg ${nodeTypeColors[selectedNode.node_type]} text-white`}>
                    {(() => {
                      const Icon = nodeTypeIcons[selectedNode.node_type] || Box;
                      return <Icon className="h-6 w-6" />;
                    })()}
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">{selectedNode.asset_name}</h2>
                    <p className="text-sm text-gray-500 capitalize">{selectedNode.node_type.replace('_', ' ')}</p>
                  </div>
                </div>
                <button
                  onClick={() => analyzeImpact(selectedNode.id, 'schema_change')}
                  className="flex items-center gap-2 px-4 py-2 bg-amber-100 text-amber-700 rounded-lg hover:bg-amber-200"
                >
                  <AlertTriangle className="h-4 w-4" />
                  Impact Analysis
                </button>
              </div>

              {selectedNode.description && (
                <p className="text-gray-600 mb-6">{selectedNode.description}</p>
              )}

              <div className="grid grid-cols-2 gap-6">
                {/* Upstream */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Upstream Dependencies</h3>
                  <div className="space-y-2">
                    {getUpstream(selectedNode.id).length === 0 ? (
                      <p className="text-sm text-gray-400">No upstream dependencies</p>
                    ) : (
                      getUpstream(selectedNode.id).map((node) => {
                        const Icon = nodeTypeIcons[node.node_type] || Box;
                        return (
                          <button
                            key={node.id}
                            onClick={() => setSelectedNode(node)}
                            className="w-full p-2 text-left bg-gray-50 rounded-lg hover:bg-gray-100 flex items-center gap-2"
                          >
                            <Icon className="h-4 w-4 text-gray-500" />
                            <span className="text-sm">{node.asset_name}</span>
                          </button>
                        );
                      })
                    )}
                  </div>
                </div>

                {/* Downstream */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Downstream Consumers</h3>
                  <div className="space-y-2">
                    {getDownstream(selectedNode.id).length === 0 ? (
                      <p className="text-sm text-gray-400">No downstream consumers</p>
                    ) : (
                      getDownstream(selectedNode.id).map((node) => {
                        const Icon = nodeTypeIcons[node.node_type] || Box;
                        return (
                          <button
                            key={node.id}
                            onClick={() => setSelectedNode(node)}
                            className="w-full p-2 text-left bg-gray-50 rounded-lg hover:bg-gray-100 flex items-center gap-2"
                          >
                            <Icon className="h-4 w-4 text-gray-500" />
                            <span className="text-sm">{node.asset_name}</span>
                          </button>
                        );
                      })
                    )}
                  </div>
                </div>
              </div>

              {/* Node Metadata */}
              {Object.keys(selectedNode.node_metadata).length > 0 && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Metadata</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <pre className="text-xs text-gray-600 overflow-auto">
                      {JSON.stringify(selectedNode.node_metadata, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <Eye className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500">Select a node to view its lineage details</p>
            </div>
          )}
        </div>
      </div>

      {/* Impact Analysis Modal */}
      {showImpactModal && impactAnalysis && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              Impact Analysis Results
            </h2>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-amber-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-amber-700">{impactAnalysis.total_affected}</div>
                <div className="text-sm text-amber-600">Total Affected Items</div>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-red-700">{impactAnalysis.critical_impacts}</div>
                <div className="text-sm text-red-600">Critical Impacts</div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-700 mb-2">Affected Dashboards ({impactAnalysis.affected_dashboards.length})</h3>
                <div className="space-y-1">
                  {impactAnalysis.affected_dashboards.map((d: any) => (
                    <div key={d.id} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                      <LayoutDashboard className="h-4 w-4 text-gray-500" />
                      <span className="text-sm">{d.name}</span>
                    </div>
                  ))}
                  {impactAnalysis.affected_dashboards.length === 0 && (
                    <p className="text-sm text-gray-400">No dashboards affected</p>
                  )}
                </div>
              </div>

              <div>
                <h3 className="font-medium text-gray-700 mb-2">Affected Charts ({impactAnalysis.affected_charts.length})</h3>
                <div className="space-y-1">
                  {impactAnalysis.affected_charts.map((c: any) => (
                    <div key={c.id} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                      <BarChart3 className="h-4 w-4 text-gray-500" />
                      <span className="text-sm">{c.name}</span>
                    </div>
                  ))}
                  {impactAnalysis.affected_charts.length === 0 && (
                    <p className="text-sm text-gray-400">No charts affected</p>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowImpactModal(false)}
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
