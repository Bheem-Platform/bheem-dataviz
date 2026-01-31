/**
 * Row-Level Security Management Page
 *
 * Allows users to manage RLS policies, roles, and user assignments.
 */

import React, { useState, useEffect } from 'react';
import {
  Shield,
  Plus,
  Search,
  Edit2,
  Trash2,
  Copy,
  Eye,
  EyeOff,
  Users,
  Key,
  Settings,
  ChevronDown,
  ChevronRight,
  AlertTriangle,
  Check,
  X,
} from 'lucide-react';
import {
  RLSPolicy,
  SecurityRole,
  RLSCondition,
  RLSConditionGroup,
  createDefaultPolicy,
  createDefaultCondition,
  RLS_OPERATOR_OPTIONS,
  USER_ATTRIBUTE_OPTIONS,
} from '../types/rls';
import { RLSConditionEditor } from '../components/rls/RLSConditionEditor';
import api from '../lib/api';
import { cn } from '../lib/utils';

type TabType = 'policies' | 'roles' | 'settings';

const RowLevelSecurity: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('policies');
  const [policies, setPolicies] = useState<RLSPolicy[]>([]);
  const [roles, setRoles] = useState<SecurityRole[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Policy editing state
  const [editingPolicy, setEditingPolicy] = useState<RLSPolicy | null>(null);
  const [isCreatingPolicy, setIsCreatingPolicy] = useState(false);
  const [columns, setColumns] = useState<{ column: string; type: string }[]>([]);

  // Role editing state
  const [editingRole, setEditingRole] = useState<SecurityRole | null>(null);
  const [isCreatingRole, setIsCreatingRole] = useState(false);

  // Configuration state
  const [config, setConfig] = useState({
    enabled: true,
    defaultDeny: false,
    cacheTtlSeconds: 300,
    logAccess: true,
    auditMode: false,
  });

  // Delete confirmation
  const [deleteTarget, setDeleteTarget] = useState<{ type: 'policy' | 'role'; id: string } | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [policiesRes, rolesRes, configRes] = await Promise.all([
        api.get('/api/v1/rls/policies'),
        api.get('/api/v1/rls/roles'),
        api.get('/api/v1/rls/config'),
      ]);
      setPolicies(policiesRes.data || []);
      setRoles(rolesRes.data || []);
      setConfig(configRes.data || config);
    } catch (error) {
      console.error('Failed to fetch RLS data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchColumns = async (tableName: string, schemaName?: string) => {
    try {
      const response = await api.get('/api/v1/queries/columns', {
        params: { table: tableName, schema: schemaName },
      });
      setColumns(response.data.columns || response.data || []);
    } catch (error) {
      console.error('Failed to fetch columns:', error);
      setColumns([]);
    }
  };

  // Policy CRUD
  const handleCreatePolicy = async (policy: RLSPolicy) => {
    try {
      const response = await api.post('/api/v1/rls/policies', policy);
      setPolicies((prev) => [...prev, response.data]);
      setIsCreatingPolicy(false);
      setEditingPolicy(null);
    } catch (error) {
      console.error('Failed to create policy:', error);
    }
  };

  const handleUpdatePolicy = async (policy: RLSPolicy) => {
    try {
      const response = await api.put(`/api/v1/rls/policies/${policy.id}`, policy);
      setPolicies((prev) => prev.map((p) => (p.id === policy.id ? response.data : p)));
      setEditingPolicy(null);
    } catch (error) {
      console.error('Failed to update policy:', error);
    }
  };

  const handleDeletePolicy = async (policyId: string) => {
    try {
      await api.delete(`/api/v1/rls/policies/${policyId}`);
      setPolicies((prev) => prev.filter((p) => p.id !== policyId));
      setDeleteTarget(null);
    } catch (error) {
      console.error('Failed to delete policy:', error);
    }
  };

  const handleTogglePolicy = async (policyId: string, enabled: boolean) => {
    try {
      await api.put(`/api/v1/rls/policies/${policyId}/toggle`, null, {
        params: { enabled },
      });
      setPolicies((prev) =>
        prev.map((p) => (p.id === policyId ? { ...p, enabled } : p))
      );
    } catch (error) {
      console.error('Failed to toggle policy:', error);
    }
  };

  // Role CRUD
  const handleCreateRole = async (role: SecurityRole) => {
    try {
      const response = await api.post('/api/v1/rls/roles', role);
      setRoles((prev) => [...prev, response.data]);
      setIsCreatingRole(false);
      setEditingRole(null);
    } catch (error) {
      console.error('Failed to create role:', error);
    }
  };

  const handleUpdateRole = async (role: SecurityRole) => {
    try {
      const response = await api.put(`/api/v1/rls/roles/${role.id}`, role);
      setRoles((prev) => prev.map((r) => (r.id === role.id ? response.data : r)));
      setEditingRole(null);
    } catch (error) {
      console.error('Failed to update role:', error);
    }
  };

  const handleDeleteRole = async (roleId: string) => {
    try {
      await api.delete(`/api/v1/rls/roles/${roleId}`);
      setRoles((prev) => prev.filter((r) => r.id !== roleId));
      setDeleteTarget(null);
    } catch (error) {
      console.error('Failed to delete role:', error);
    }
  };

  // Config update
  const handleUpdateConfig = async () => {
    try {
      await api.put('/api/v1/rls/config', config);
    } catch (error) {
      console.error('Failed to update config:', error);
    }
  };

  // Filter items
  const filteredPolicies = policies.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredRoles = roles.filter((r) =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <Shield className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900">Row-Level Security</h1>
                <p className="text-sm text-gray-500">
                  Control data access based on user roles and attributes
                </p>
              </div>
            </div>
            {activeTab === 'policies' && (
              <button
                onClick={() => {
                  setEditingPolicy(createDefaultPolicy(''));
                  setIsCreatingPolicy(true);
                }}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                New Policy
              </button>
            )}
            {activeTab === 'roles' && (
              <button
                onClick={() => {
                  setEditingRole({ id: '', name: '', description: '' });
                  setIsCreatingRole(true);
                }}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                New Role
              </button>
            )}
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mt-6">
            <button
              onClick={() => setActiveTab('policies')}
              className={cn(
                'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                activeTab === 'policies'
                  ? 'bg-red-100 text-red-700'
                  : 'text-gray-600 hover:bg-gray-100'
              )}
            >
              <Key className="h-4 w-4" />
              Policies
            </button>
            <button
              onClick={() => setActiveTab('roles')}
              className={cn(
                'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                activeTab === 'roles'
                  ? 'bg-red-100 text-red-700'
                  : 'text-gray-600 hover:bg-gray-100'
              )}
            >
              <Users className="h-4 w-4" />
              Roles
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={cn(
                'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                activeTab === 'settings'
                  ? 'bg-red-100 text-red-700'
                  : 'text-gray-600 hover:bg-gray-100'
              )}
            >
              <Settings className="h-4 w-4" />
              Settings
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Search */}
        {activeTab !== 'settings' && (
          <div className="mb-6">
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={`Search ${activeTab}...`}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>
        )}

        {/* Policies Tab */}
        {activeTab === 'policies' && (
          <div className="space-y-4">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500" />
              </div>
            ) : filteredPolicies.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg border">
                <Shield className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No policies defined</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Create RLS policies to control data access based on user context
                </p>
                <button
                  onClick={() => {
                    setEditingPolicy(createDefaultPolicy(''));
                    setIsCreatingPolicy(true);
                  }}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  <Plus className="h-4 w-4" />
                  Create Policy
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg border overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Policy
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Table
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Conditions
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Roles
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredPolicies.map((policy) => (
                      <tr key={policy.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <div>
                            <div className="font-medium text-gray-900">{policy.name}</div>
                            {policy.description && (
                              <div className="text-xs text-gray-500">{policy.description}</div>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {policy.schemaName && `${policy.schemaName}.`}
                          {policy.tableName || 'All tables'}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {policy.filterGroup.conditions.length} condition(s)
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex gap-1 flex-wrap">
                            {policy.roleIds.length === 0 ? (
                              <span className="text-xs text-gray-400">All roles</span>
                            ) : (
                              policy.roleIds.slice(0, 2).map((roleId) => {
                                const role = roles.find((r) => r.id === roleId);
                                return (
                                  <span
                                    key={roleId}
                                    className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded"
                                  >
                                    {role?.name || roleId}
                                  </span>
                                );
                              })
                            )}
                            {policy.roleIds.length > 2 && (
                              <span className="text-xs text-gray-400">
                                +{policy.roleIds.length - 2} more
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => handleTogglePolicy(policy.id, !policy.enabled)}
                            className={cn(
                              'flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors',
                              policy.enabled
                                ? 'bg-green-100 text-green-700 hover:bg-green-200'
                                : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                            )}
                          >
                            {policy.enabled ? (
                              <>
                                <Eye className="h-3 w-3" />
                                Enabled
                              </>
                            ) : (
                              <>
                                <EyeOff className="h-3 w-3" />
                                Disabled
                              </>
                            )}
                          </button>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-1">
                            <button
                              onClick={() => setEditingPolicy(policy)}
                              className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
                              title="Edit"
                            >
                              <Edit2 className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => setDeleteTarget({ type: 'policy', id: policy.id })}
                              className="p-1.5 text-gray-400 hover:text-red-600 rounded"
                              title="Delete"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Roles Tab */}
        {activeTab === 'roles' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {isLoading ? (
              <div className="col-span-full flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500" />
              </div>
            ) : filteredRoles.length === 0 ? (
              <div className="col-span-full text-center py-12 bg-white rounded-lg border">
                <Users className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No roles defined</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Create security roles to group users for RLS policies
                </p>
              </div>
            ) : (
              filteredRoles.map((role) => (
                <div
                  key={role.id}
                  className="bg-white rounded-lg border p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{role.name}</h3>
                      {role.description && (
                        <p className="text-sm text-gray-500 mt-1">{role.description}</p>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => setEditingRole(role)}
                        className="p-1 text-gray-400 hover:text-gray-600 rounded"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setDeleteTarget({ type: 'role', id: role.id })}
                        className="p-1 text-gray-400 hover:text-red-600 rounded"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  {role.isDefault && (
                    <span className="inline-flex items-center gap-1 mt-2 px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">
                      Default
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="max-w-2xl bg-white rounded-lg border p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">RLS Configuration</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium text-gray-900">Enable RLS</p>
                  <p className="text-sm text-gray-500">
                    Enforce row-level security policies on queries
                  </p>
                </div>
                <button
                  onClick={() => setConfig({ ...config, enabled: !config.enabled })}
                  className={cn(
                    'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                    config.enabled ? 'bg-red-600' : 'bg-gray-200'
                  )}
                >
                  <span
                    className={cn(
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      config.enabled ? 'translate-x-6' : 'translate-x-1'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium text-gray-900">Default Deny</p>
                  <p className="text-sm text-gray-500">
                    Deny access to data without explicit policies
                  </p>
                </div>
                <button
                  onClick={() => setConfig({ ...config, defaultDeny: !config.defaultDeny })}
                  className={cn(
                    'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                    config.defaultDeny ? 'bg-red-600' : 'bg-gray-200'
                  )}
                >
                  <span
                    className={cn(
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      config.defaultDeny ? 'translate-x-6' : 'translate-x-1'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium text-gray-900">Log Access</p>
                  <p className="text-sm text-gray-500">Log all RLS-filtered queries</p>
                </div>
                <button
                  onClick={() => setConfig({ ...config, logAccess: !config.logAccess })}
                  className={cn(
                    'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                    config.logAccess ? 'bg-red-600' : 'bg-gray-200'
                  )}
                >
                  <span
                    className={cn(
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      config.logAccess ? 'translate-x-6' : 'translate-x-1'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium text-gray-900">Audit Mode</p>
                  <p className="text-sm text-gray-500">
                    Log policy violations without enforcing restrictions
                  </p>
                </div>
                <button
                  onClick={() => setConfig({ ...config, auditMode: !config.auditMode })}
                  className={cn(
                    'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                    config.auditMode ? 'bg-red-600' : 'bg-gray-200'
                  )}
                >
                  <span
                    className={cn(
                      'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                      config.auditMode ? 'translate-x-6' : 'translate-x-1'
                    )}
                  />
                </button>
              </div>

              <div className="py-3">
                <label className="block font-medium text-gray-900 mb-1">
                  Cache TTL (seconds)
                </label>
                <p className="text-sm text-gray-500 mb-2">
                  How long to cache policy evaluation results
                </p>
                <input
                  type="number"
                  value={config.cacheTtlSeconds}
                  onChange={(e) =>
                    setConfig({ ...config, cacheTtlSeconds: parseInt(e.target.value) || 0 })
                  }
                  className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                />
              </div>

              <div className="pt-4">
                <button
                  onClick={handleUpdateConfig}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Save Settings
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Policy Editor Modal */}
      {editingPolicy && (
        <PolicyEditorModal
          policy={editingPolicy}
          roles={roles}
          columns={columns}
          isCreating={isCreatingPolicy}
          onSave={isCreatingPolicy ? handleCreatePolicy : handleUpdatePolicy}
          onCancel={() => {
            setEditingPolicy(null);
            setIsCreatingPolicy(false);
          }}
          onFetchColumns={fetchColumns}
        />
      )}

      {/* Role Editor Modal */}
      {editingRole && (
        <RoleEditorModal
          role={editingRole}
          isCreating={isCreatingRole}
          onSave={isCreatingRole ? handleCreateRole : handleUpdateRole}
          onCancel={() => {
            setEditingRole(null);
            setIsCreatingRole(false);
          }}
        />
      )}

      {/* Delete Confirmation Modal */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setDeleteTarget(null)} />
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-sm mx-4 p-6">
            <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mx-auto mb-4">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <h2 className="text-lg font-semibold text-center mb-2">
              Delete {deleteTarget.type === 'policy' ? 'Policy' : 'Role'}
            </h2>
            <p className="text-sm text-gray-500 text-center mb-6">
              Are you sure you want to delete this {deleteTarget.type}? This action cannot be
              undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteTarget(null)}
                className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (deleteTarget.type === 'policy') {
                    handleDeletePolicy(deleteTarget.id);
                  } else {
                    handleDeleteRole(deleteTarget.id);
                  }
                }}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Policy Editor Modal Component
interface PolicyEditorModalProps {
  policy: RLSPolicy;
  roles: SecurityRole[];
  columns: { column: string; type: string }[];
  isCreating: boolean;
  onSave: (policy: RLSPolicy) => void;
  onCancel: () => void;
  onFetchColumns: (table: string, schema?: string) => void;
}

const PolicyEditorModal: React.FC<PolicyEditorModalProps> = ({
  policy,
  roles,
  columns,
  isCreating,
  onSave,
  onCancel,
  onFetchColumns,
}) => {
  const [formData, setFormData] = useState<RLSPolicy>(policy);

  const addCondition = () => {
    const newCondition = createDefaultCondition();
    setFormData({
      ...formData,
      filterGroup: {
        ...formData.filterGroup,
        conditions: [...formData.filterGroup.conditions, newCondition],
      },
    });
  };

  const updateCondition = (index: number, condition: RLSCondition) => {
    const conditions = [...formData.filterGroup.conditions];
    conditions[index] = condition;
    setFormData({
      ...formData,
      filterGroup: { ...formData.filterGroup, conditions },
    });
  };

  const deleteCondition = (index: number) => {
    const conditions = formData.filterGroup.conditions.filter((_, i) => i !== index);
    setFormData({
      ...formData,
      filterGroup: { ...formData.filterGroup, conditions },
    });
  };

  const toggleRole = (roleId: string) => {
    const roleIds = formData.roleIds.includes(roleId)
      ? formData.roleIds.filter((id) => id !== roleId)
      : [...formData.roleIds, roleId];
    setFormData({ ...formData, roleIds });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto">
      <div className="absolute inset-0 bg-black/50" onClick={onCancel} />
      <div className="relative bg-white rounded-lg shadow-xl w-full max-w-3xl mx-4 my-8">
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            {isCreating ? 'Create' : 'Edit'} RLS Policy
          </h2>
          <button onClick={onCancel} className="text-gray-400 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Policy Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <input
                type="text"
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>

          {/* Target Table */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Schema</label>
              <input
                type="text"
                value={formData.schemaName || ''}
                onChange={(e) => setFormData({ ...formData, schemaName: e.target.value })}
                placeholder="public"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Table Name</label>
              <input
                type="text"
                value={formData.tableName || ''}
                onChange={(e) => {
                  setFormData({ ...formData, tableName: e.target.value });
                  if (e.target.value) {
                    onFetchColumns(e.target.value, formData.schemaName);
                  }
                }}
                placeholder="Enter table name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>

          {/* Conditions */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium text-gray-700">Filter Conditions</label>
              <div className="flex items-center gap-2">
                <select
                  value={formData.filterGroup.logic}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      filterGroup: {
                        ...formData.filterGroup,
                        logic: e.target.value as 'AND' | 'OR',
                      },
                    })
                  }
                  className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-red-500"
                >
                  <option value="AND">Match ALL (AND)</option>
                  <option value="OR">Match ANY (OR)</option>
                </select>
                <button
                  onClick={addCondition}
                  className="flex items-center gap-1 px-2 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
                >
                  <Plus className="h-4 w-4" />
                  Add Condition
                </button>
              </div>
            </div>

            {formData.filterGroup.conditions.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                <p className="text-sm text-gray-500">No conditions defined</p>
                <p className="text-xs text-gray-400 mt-1">
                  Add conditions to filter data based on user context
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {formData.filterGroup.conditions.map((condition, index) => (
                  <RLSConditionEditor
                    key={condition.id}
                    condition={condition}
                    columns={columns}
                    onChange={(c) => updateCondition(index, c)}
                    onDelete={() => deleteCondition(index)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Roles */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Apply to Roles
            </label>
            {roles.length === 0 ? (
              <p className="text-sm text-gray-500">No roles defined yet</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {roles.map((role) => (
                  <button
                    key={role.id}
                    onClick={() => toggleRole(role.id)}
                    className={cn(
                      'px-3 py-1.5 text-sm rounded-lg border transition-colors',
                      formData.roleIds.includes(role.id)
                        ? 'bg-red-100 border-red-500 text-red-700'
                        : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                    )}
                  >
                    {role.name}
                  </button>
                ))}
              </div>
            )}
            <p className="text-xs text-gray-500 mt-2">
              Leave empty to apply to all roles
            </p>
          </div>
        </div>

        <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(formData)}
            disabled={!formData.name}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isCreating ? 'Create' : 'Save'} Policy
          </button>
        </div>
      </div>
    </div>
  );
};

// Role Editor Modal Component
interface RoleEditorModalProps {
  role: SecurityRole;
  isCreating: boolean;
  onSave: (role: SecurityRole) => void;
  onCancel: () => void;
}

const RoleEditorModal: React.FC<RoleEditorModalProps> = ({
  role,
  isCreating,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState<SecurityRole>(role);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onCancel} />
      <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">{isCreating ? 'Create' : 'Edit'} Role</h2>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="e.g., Sales Manager"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="Describe the role's purpose..."
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="isDefault"
              checked={formData.isDefault || false}
              onChange={(e) => setFormData({ ...formData, isDefault: e.target.checked })}
              className="rounded border-gray-300 text-red-600 focus:ring-red-500"
            />
            <label htmlFor="isDefault" className="text-sm text-gray-700">
              Set as default role for new users
            </label>
          </div>
        </div>

        <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(formData)}
            disabled={!formData.name}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isCreating ? 'Create' : 'Save'} Role
          </button>
        </div>
      </div>
    </div>
  );
};

export default RowLevelSecurity;
