/**
 * Data Governance Page
 *
 * Manage data stewards, ownership, and data catalog
 */

import { useState, useEffect } from 'react';
import {
  Users,
  Database,
  Shield,
  Plus,
  Search,
  Edit,
  Trash2,
  User,
  Building2,
  Tag,
  AlertTriangle,
  CheckCircle,
  Clock,
  Mail,
  Phone,
} from 'lucide-react';
import api from '../lib/api';

interface DataSteward {
  id: string;
  user_id: string;
  user_email: string;
  user_name: string;
  owner_type: 'primary' | 'steward' | 'custodian' | 'consumer';
  department: string | null;
  domain: string | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
}

interface DataOwnership {
  id: string;
  asset_type: string;
  asset_id: string;
  asset_name: string;
  connection_id: string | null;
  table_name: string | null;
  steward_id: string;
  owner_type: string;
  sla_freshness_hours: number | null;
  quality_threshold: number;
  pii_flag: boolean;
  business_glossary: string | null;
  created_at: string;
}

const ownerTypeColors: Record<string, string> = {
  primary: 'bg-blue-100 text-blue-800',
  steward: 'bg-green-100 text-green-800',
  custodian: 'bg-purple-100 text-purple-800',
  consumer: 'bg-gray-100 text-gray-800',
};

export default function DataGovernance() {
  const [activeTab, setActiveTab] = useState<'stewards' | 'ownership' | 'catalog'>('stewards');
  const [stewards, setStewards] = useState<DataSteward[]>([]);
  const [ownership, setOwnership] = useState<DataOwnership[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateStewardModal, setShowCreateStewardModal] = useState(false);
  const [showCreateOwnershipModal, setShowCreateOwnershipModal] = useState(false);

  // Form state for creating steward
  const [newSteward, setNewSteward] = useState({
    user_email: '',
    user_name: '',
    owner_type: 'steward' as const,
    department: '',
    domain: '',
    description: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [stewardsRes, ownershipRes] = await Promise.all([
        api.get('/governance/stewards'),
        api.get('/governance/ownership'),
      ]);
      setStewards(stewardsRes.data);
      setOwnership(ownershipRes.data);
    } catch (err) {
      console.error('Error fetching governance data:', err);
    } finally {
      setLoading(false);
    }
  };

  const createSteward = async () => {
    try {
      await api.post('/governance/stewards', {
        ...newSteward,
        user_id: crypto.randomUUID(),
      });
      setShowCreateStewardModal(false);
      setNewSteward({
        user_email: '',
        user_name: '',
        owner_type: 'steward',
        department: '',
        domain: '',
        description: '',
      });
      fetchData();
    } catch (err) {
      console.error('Error creating steward:', err);
    }
  };

  const filteredStewards = stewards.filter(
    (s) =>
      s.user_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.user_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.domain?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredOwnership = ownership.filter(
    (o) =>
      o.asset_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      o.table_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="h-7 w-7 text-blue-600" />
            Data Governance
          </h1>
          <p className="text-gray-500 mt-1">
            Manage data stewards, ownership, and data catalog
          </p>
        </div>
        <button
          onClick={() => activeTab === 'stewards' ? setShowCreateStewardModal(true) : setShowCreateOwnershipModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          {activeTab === 'stewards' ? 'Add Steward' : 'Assign Ownership'}
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { key: 'stewards', label: 'Data Stewards', icon: Users },
            { key: 'ownership', label: 'Data Ownership', icon: Database },
            { key: 'catalog', label: 'Data Catalog', icon: Tag },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
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
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {/* Stewards Tab */}
          {activeTab === 'stewards' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredStewards.length === 0 ? (
                <div className="col-span-full text-center py-12 text-gray-500">
                  <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No data stewards found</p>
                  <button
                    onClick={() => setShowCreateStewardModal(true)}
                    className="mt-4 text-blue-600 hover:underline"
                  >
                    Add your first steward
                  </button>
                </div>
              ) : (
                filteredStewards.map((steward) => (
                  <div
                    key={steward.id}
                    className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <User className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="font-medium text-gray-900">{steward.user_name}</h3>
                          <p className="text-sm text-gray-500">{steward.user_email}</p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${ownerTypeColors[steward.owner_type]}`}>
                        {steward.owner_type}
                      </span>
                    </div>

                    <div className="mt-4 space-y-2">
                      {steward.domain && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Building2 className="h-4 w-4" />
                          <span>{steward.domain}</span>
                        </div>
                      )}
                      {steward.department && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Tag className="h-4 w-4" />
                          <span>{steward.department}</span>
                        </div>
                      )}
                    </div>

                    <div className="mt-4 flex items-center justify-between">
                      <span className={`flex items-center gap-1 text-xs ${steward.is_active ? 'text-green-600' : 'text-gray-400'}`}>
                        {steward.is_active ? <CheckCircle className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                        {steward.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <div className="flex items-center gap-2">
                        <button className="p-1 text-gray-400 hover:text-blue-600">
                          <Edit className="h-4 w-4" />
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

          {/* Ownership Tab */}
          {activeTab === 'ownership' && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Owner Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SLA</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quality</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">PII</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredOwnership.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                        No ownership records found
                      </td>
                    </tr>
                  ) : (
                    filteredOwnership.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-gray-900">{item.asset_name}</div>
                            {item.table_name && (
                              <div className="text-sm text-gray-500">{item.table_name}</div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                            {item.asset_type}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${ownerTypeColors[item.owner_type]}`}>
                            {item.owner_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {item.sla_freshness_hours ? `${item.sla_freshness_hours}h` : '-'}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${item.quality_threshold >= 90 ? 'bg-green-500' : item.quality_threshold >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                style={{ width: `${item.quality_threshold}%` }}
                              />
                            </div>
                            <span className="text-sm text-gray-600">{item.quality_threshold}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {item.pii_flag ? (
                            <span className="flex items-center gap-1 text-amber-600">
                              <AlertTriangle className="h-4 w-4" />
                              Yes
                            </span>
                          ) : (
                            <span className="text-gray-400">No</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <button className="p-1 text-gray-400 hover:text-blue-600">
                              <Edit className="h-4 w-4" />
                            </button>
                            <button className="p-1 text-gray-400 hover:text-red-600">
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Catalog Tab */}
          {activeTab === 'catalog' && (
            <div className="text-center py-12 text-gray-500">
              <Tag className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Data Catalog coming soon</p>
              <p className="text-sm mt-2">Browse and search your data assets with business context</p>
            </div>
          )}
        </>
      )}

      {/* Create Steward Modal */}
      {showCreateStewardModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <h2 className="text-lg font-semibold mb-4">Add Data Steward</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newSteward.user_name}
                  onChange={(e) => setNewSteward({ ...newSteward, user_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="John Doe"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={newSteward.user_email}
                  onChange={(e) => setNewSteward({ ...newSteward, user_email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="john@company.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  value={newSteward.owner_type}
                  onChange={(e) => setNewSteward({ ...newSteward, owner_type: e.target.value as any })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="primary">Primary Owner</option>
                  <option value="steward">Data Steward</option>
                  <option value="custodian">Data Custodian</option>
                  <option value="consumer">Consumer</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Domain</label>
                <input
                  type="text"
                  value={newSteward.domain}
                  onChange={(e) => setNewSteward({ ...newSteward, domain: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Sales, HR, Finance..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <input
                  type="text"
                  value={newSteward.department}
                  onChange={(e) => setNewSteward({ ...newSteward, department: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Analytics Team"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowCreateStewardModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={createSteward}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add Steward
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
