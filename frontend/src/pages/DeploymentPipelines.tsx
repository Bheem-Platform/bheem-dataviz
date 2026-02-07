/**
 * Deployment Pipelines Page
 *
 * Manage deployment environments and promotion workflows
 */

import { useState, useEffect } from 'react';
import {
  Rocket,
  Server,
  Plus,
  Search,
  Edit,
  Trash2,
  CheckCircle,
  Clock,
  XCircle,
  ArrowRight,
  Shield,
  Users,
  Settings,
  AlertTriangle,
  ChevronRight,
  Play,
  RotateCcw,
} from 'lucide-react';
import api from '../lib/api';

interface Environment {
  id: string;
  name: string;
  environment_type: 'development' | 'staging' | 'production';
  description: string | null;
  is_default: boolean;
  is_protected: boolean;
  connection_overrides: Record<string, any>;
  allowed_deployers: string[];
  required_approvers: string[];
  min_approvals: number;
  created_at: string;
}

interface Promotion {
  id: string;
  asset_type: string;
  asset_id: string;
  asset_name: string;
  source_environment_id: string;
  target_environment_id: string;
  status: 'pending' | 'approved' | 'rejected' | 'deployed' | 'rolled_back';
  requested_by: string;
  requested_at: string;
  promotion_notes: string | null;
  approvals: Array<{ user_id: string; approved_at: string; comment: string }>;
  rejections: Array<{ user_id: string; rejected_at: string; comment: string }>;
  deployed_at: string | null;
  change_summary: Record<string, any>;
}

const environmentTypeColors: Record<string, string> = {
  development: 'bg-blue-100 text-blue-800 border-blue-200',
  staging: 'bg-amber-100 text-amber-800 border-amber-200',
  production: 'bg-green-100 text-green-800 border-green-200',
};

const environmentTypeIcons: Record<string, string> = {
  development: '🔧',
  staging: '🧪',
  production: '🚀',
};

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-blue-100 text-blue-800',
  rejected: 'bg-red-100 text-red-800',
  deployed: 'bg-green-100 text-green-800',
  rolled_back: 'bg-gray-100 text-gray-800',
};

export default function DeploymentPipelines() {
  const [activeTab, setActiveTab] = useState<'environments' | 'promotions'>('environments');
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateEnvModal, setShowCreateEnvModal] = useState(false);
  const [showPromoteModal, setShowPromoteModal] = useState(false);

  const [newEnvironment, setNewEnvironment] = useState({
    name: '',
    environment_type: 'development' as const,
    description: '',
    is_protected: false,
    min_approvals: 1,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [envRes, promoRes] = await Promise.all([
        api.get('/governance/environments'),
        api.get('/governance/promotions'),
      ]);
      setEnvironments(envRes.data);
      setPromotions(promoRes.data);
    } catch (err) {
      console.error('Error fetching deployment data:', err);
    } finally {
      setLoading(false);
    }
  };

  const createEnvironment = async () => {
    try {
      await api.post('/governance/environments', {
        ...newEnvironment,
        workspace_id: crypto.randomUUID(),
        connection_overrides: {},
        allowed_deployers: [],
        required_approvers: [],
      });
      setShowCreateEnvModal(false);
      setNewEnvironment({
        name: '',
        environment_type: 'development',
        description: '',
        is_protected: false,
        min_approvals: 1,
      });
      fetchData();
    } catch (err) {
      console.error('Error creating environment:', err);
    }
  };

  const approvePromotion = async (promotionId: string) => {
    try {
      await api.post(`/governance/promotions/${promotionId}/approve`, {
        approved: true,
        comment: 'Approved via UI',
      });
      fetchData();
    } catch (err) {
      console.error('Error approving promotion:', err);
    }
  };

  const rejectPromotion = async (promotionId: string) => {
    try {
      await api.post(`/governance/promotions/${promotionId}/approve`, {
        approved: false,
        comment: 'Rejected via UI',
      });
      fetchData();
    } catch (err) {
      console.error('Error rejecting promotion:', err);
    }
  };

  const deployPromotion = async (promotionId: string) => {
    try {
      await api.post(`/governance/promotions/${promotionId}/deploy`);
      fetchData();
    } catch (err) {
      console.error('Error deploying promotion:', err);
    }
  };

  const filteredEnvironments = environments.filter(
    (e) =>
      e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.environment_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredPromotions = promotions.filter(
    (p) =>
      p.asset_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.asset_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getEnvironmentName = (id: string) => {
    return environments.find((e) => e.id === id)?.name || 'Unknown';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Rocket className="h-7 w-7 text-purple-600" />
            Deployment Pipelines
          </h1>
          <p className="text-gray-500 mt-1">
            Manage environments and promote assets through your pipeline
          </p>
        </div>
        <button
          onClick={() => activeTab === 'environments' ? setShowCreateEnvModal(true) : setShowPromoteModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          <Plus className="h-4 w-4" />
          {activeTab === 'environments' ? 'Add Environment' : 'Request Promotion'}
        </button>
      </div>

      {/* Pipeline Visualization */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-sm font-medium text-gray-700 mb-4">Pipeline Overview</h3>
        <div className="flex items-center justify-center gap-4">
          {['development', 'staging', 'production'].map((type, index) => {
            const env = environments.find((e) => e.environment_type === type);
            return (
              <div key={type} className="flex items-center">
                <div className={`p-4 rounded-lg border-2 ${environmentTypeColors[type]} min-w-[140px]`}>
                  <div className="text-2xl text-center mb-2">{environmentTypeIcons[type]}</div>
                  <div className="font-medium text-center capitalize">{type}</div>
                  {env && (
                    <div className="text-xs text-center mt-1 opacity-75">{env.name}</div>
                  )}
                </div>
                {index < 2 && (
                  <ChevronRight className="h-6 w-6 mx-2 text-gray-400" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { key: 'environments', label: 'Environments', icon: Server },
            { key: 'promotions', label: 'Promotions', icon: ArrowRight },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
        />
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
      ) : (
        <>
          {/* Environments Tab */}
          {activeTab === 'environments' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredEnvironments.length === 0 ? (
                <div className="col-span-full text-center py-12 text-gray-500">
                  <Server className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No environments configured</p>
                  <button
                    onClick={() => setShowCreateEnvModal(true)}
                    className="mt-4 text-purple-600 hover:underline"
                  >
                    Create your first environment
                  </button>
                </div>
              ) : (
                filteredEnvironments.map((env) => (
                  <div
                    key={env.id}
                    className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-2xl">{environmentTypeIcons[env.environment_type]}</div>
                        <div>
                          <h3 className="font-medium text-gray-900">{env.name}</h3>
                          <span className={`inline-block mt-1 px-2 py-0.5 text-xs font-medium rounded-full ${environmentTypeColors[env.environment_type]}`}>
                            {env.environment_type}
                          </span>
                        </div>
                      </div>
                      {env.is_protected && (
                        <Shield className="h-4 w-4 text-amber-500" />
                      )}
                    </div>

                    {env.description && (
                      <p className="mt-3 text-sm text-gray-600">{env.description}</p>
                    )}

                    <div className="mt-4 space-y-2">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Users className="h-4 w-4" />
                        <span>{env.required_approvers.length} approvers required</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <CheckCircle className="h-4 w-4" />
                        <span>Min {env.min_approvals} approval(s)</span>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center justify-between">
                      {env.is_default && (
                        <span className="text-xs text-green-600 font-medium">Default</span>
                      )}
                      <div className="flex items-center gap-2 ml-auto">
                        <button className="p-1 text-gray-400 hover:text-purple-600">
                          <Settings className="h-4 w-4" />
                        </button>
                        <button className="p-1 text-gray-400 hover:text-red-600">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Promotions Tab */}
          {activeTab === 'promotions' && (
            <div className="space-y-4">
              {filteredPromotions.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <ArrowRight className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No promotion requests</p>
                  <p className="text-sm mt-2">Promote assets from development to production</p>
                </div>
              ) : (
                filteredPromotions.map((promo) => (
                  <div
                    key={promo.id}
                    className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div>
                          <h3 className="font-medium text-gray-900">{promo.asset_name}</h3>
                          <p className="text-sm text-gray-500">{promo.asset_type}</p>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <span className="px-2 py-1 bg-gray-100 rounded">
                            {getEnvironmentName(promo.source_environment_id)}
                          </span>
                          <ArrowRight className="h-4 w-4" />
                          <span className="px-2 py-1 bg-gray-100 rounded">
                            {getEnvironmentName(promo.target_environment_id)}
                          </span>
                        </div>
                      </div>
                      <span className={`px-3 py-1 text-sm font-medium rounded-full ${statusColors[promo.status]}`}>
                        {promo.status}
                      </span>
                    </div>

                    {promo.promotion_notes && (
                      <p className="mt-3 text-sm text-gray-600">{promo.promotion_notes}</p>
                    )}

                    <div className="mt-4 flex items-center justify-between">
                      <div className="text-sm text-gray-500">
                        <Clock className="h-4 w-4 inline mr-1" />
                        Requested {new Date(promo.requested_at).toLocaleDateString()}
                      </div>
                      {promo.status === 'pending' && (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => approvePromotion(promo.id)}
                            className="flex items-center gap-1 px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
                          >
                            <CheckCircle className="h-4 w-4" />
                            Approve
                          </button>
                          <button
                            onClick={() => rejectPromotion(promo.id)}
                            className="flex items-center gap-1 px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
                          >
                            <XCircle className="h-4 w-4" />
                            Reject
                          </button>
                        </div>
                      )}
                      {promo.status === 'approved' && (
                        <button
                          onClick={() => deployPromotion(promo.id)}
                          className="flex items-center gap-1 px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
                        >
                          <Play className="h-4 w-4" />
                          Deploy
                        </button>
                      )}
                      {promo.status === 'deployed' && (
                        <button className="flex items-center gap-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                          <RotateCcw className="h-4 w-4" />
                          Rollback
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}

      {/* Create Environment Modal */}
      {showCreateEnvModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <h2 className="text-lg font-semibold mb-4">Create Environment</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newEnvironment.name}
                  onChange={(e) => setNewEnvironment({ ...newEnvironment, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  placeholder="Production US-East"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={newEnvironment.environment_type}
                  onChange={(e) => setNewEnvironment({ ...newEnvironment, environment_type: e.target.value as any })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                >
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newEnvironment.description}
                  onChange={(e) => setNewEnvironment({ ...newEnvironment, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="Environment description..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Minimum Approvals</label>
                <input
                  type="number"
                  min={0}
                  value={newEnvironment.min_approvals}
                  onChange={(e) => setNewEnvironment({ ...newEnvironment, min_approvals: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_protected"
                  checked={newEnvironment.is_protected}
                  onChange={(e) => setNewEnvironment({ ...newEnvironment, is_protected: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <label htmlFor="is_protected" className="text-sm text-gray-700">
                  Protected environment (requires approval for all changes)
                </label>
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowCreateEnvModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={createEnvironment}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Create Environment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
