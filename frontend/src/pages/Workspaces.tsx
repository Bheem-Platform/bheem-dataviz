/**
 * Workspaces Management Page
 *
 * Team workspaces and collaboration management interface.
 */

import { useState, useEffect } from 'react';
import {
  Building2,
  Users,
  Plus,
  Settings,
  Mail,
  Trash2,
  MoreVertical,
  Crown,
  Shield,
  User,
  Eye,
  Search,
  Copy,
  Check,
  X,
  UserPlus,
  Clock,
} from 'lucide-react';
import {
  Workspace,
  WorkspaceMember,
  WorkspaceInvitation,
  WorkspaceRole,
  ROLE_LABELS,
  ROLE_COLORS,
  INVITE_STATUS_LABELS,
  getAvailableRolesForAssignment,
  formatMemberJoinDate,
  formatLastAccessed,
} from '../types/workspace';
import { workspacesApi } from '../lib/api';

const roleIcons: Record<WorkspaceRole, React.ElementType> = {
  owner: Crown,
  admin: Shield,
  member: User,
  viewer: Eye,
};

export function Workspaces() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState<Workspace | null>(null);
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [invitations, setInvitations] = useState<WorkspaceInvitation[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'members' | 'settings'>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState('');
  const [newWorkspaceDesc, setNewWorkspaceDesc] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<WorkspaceRole>('member');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentUserRole = 'owner' as WorkspaceRole; // Mock: current user's role

  // Fetch workspaces from API
  useEffect(() => {
    const fetchWorkspaces = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await workspacesApi.list();
        setWorkspaces(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch workspaces');
        console.error('Error fetching workspaces:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchWorkspaces();
  }, []);

  // Fetch members and invitations when a workspace is selected
  useEffect(() => {
    if (!selectedWorkspace) {
      setMembers([]);
      setInvitations([]);
      return;
    }

    const fetchWorkspaceDetails = async () => {
      try {
        const [membersResponse, invitationsResponse] = await Promise.all([
          workspacesApi.listMembers(selectedWorkspace.id),
          workspacesApi.listInvitations(selectedWorkspace.id),
        ]);
        setMembers(membersResponse.data);
        setInvitations(invitationsResponse.data);
      } catch (err) {
        console.error('Error fetching workspace details:', err);
      }
    };
    fetchWorkspaceDetails();
  }, [selectedWorkspace]);

  const filteredWorkspaces = workspaces.filter(w =>
    w.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateWorkspace = () => {
    const newWorkspace: Workspace = {
      id: `ws_${Date.now()}`,
      name: newWorkspaceName,
      slug: newWorkspaceName.toLowerCase().replace(/\s+/g, '-'),
      description: newWorkspaceDesc,
      owner_id: 'user-1',
      is_personal: false,
      is_default: false,
      settings: {},
      is_active: true,
      member_count: 1,
      dashboard_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setWorkspaces([...workspaces, newWorkspace]);
    setShowCreateModal(false);
    setNewWorkspaceName('');
    setNewWorkspaceDesc('');
  };

  const handleInviteMember = () => {
    const newInvitation: WorkspaceInvitation = {
      id: `inv_${Date.now()}`,
      workspace_id: selectedWorkspace?.id || '',
      email: inviteEmail,
      role: inviteRole,
      status: 'pending',
      invited_by: 'user-1',
      inviter_name: 'John Admin',
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      created_at: new Date().toISOString(),
    };
    setInvitations([...invitations, newInvitation]);
    setShowInviteModal(false);
    setInviteEmail('');
    setInviteRole('member');
  };

  const handleCopyInviteLink = (id: string) => {
    navigator.clipboard.writeText(`https://app.example.com/invite/${id}`);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleRevokeInvitation = (id: string) => {
    setInvitations(invitations.filter(i => i.id !== id));
  };

  const handleChangeMemberRole = (memberId: string, newRole: WorkspaceRole) => {
    setMembers(members.map(m =>
      m.id === memberId ? { ...m, role: newRole } : m
    ));
  };

  const handleRemoveMember = (memberId: string) => {
    setMembers(members.filter(m => m.id !== memberId));
  };

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Workspaces
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Manage team workspaces and collaboration
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Workspace
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Error State */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-300">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 text-sm text-red-600 dark:text-red-400 underline hover:no-underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600 dark:text-gray-400">Loading workspaces...</span>
          </div>
        )}

        {!loading && (
        <div className="flex gap-6">
          {/* Sidebar - Workspace List */}
          <div className="w-80 flex-shrink-0">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search workspaces..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </div>
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredWorkspaces.map((workspace) => (
                  <button
                    key={workspace.id}
                    onClick={() => setSelectedWorkspace(workspace)}
                    className={`w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                      selectedWorkspace?.id === workspace.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: workspace.primary_color || '#6B7280' }}
                      >
                        {workspace.is_personal ? (
                          <User className="w-5 h-5 text-white" />
                        ) : (
                          <Building2 className="w-5 h-5 text-white" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900 dark:text-white truncate">
                            {workspace.name}
                          </span>
                          {workspace.is_default && (
                            <span className="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded">
                              Default
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-500 dark:text-gray-400">
                          <span className="flex items-center gap-1">
                            <Users className="w-3 h-3" />
                            {workspace.member_count}
                          </span>
                          <span>{workspace.dashboard_count} dashboards</span>
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {selectedWorkspace ? (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                {/* Workspace Header */}
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div
                        className="w-16 h-16 rounded-xl flex items-center justify-center"
                        style={{ backgroundColor: selectedWorkspace.primary_color || '#6B7280' }}
                      >
                        {selectedWorkspace.is_personal ? (
                          <User className="w-8 h-8 text-white" />
                        ) : (
                          <Building2 className="w-8 h-8 text-white" />
                        )}
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                          {selectedWorkspace.name}
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {selectedWorkspace.description || 'No description'}
                        </p>
                      </div>
                    </div>
                    <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                      <Settings className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Tabs */}
                  <div className="mt-6 flex gap-4">
                    {['overview', 'members', 'settings'].map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab as any)}
                        className={`px-4 py-2 text-sm font-medium rounded-lg ${
                          activeTab === tab
                            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                        }`}
                      >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tab Content */}
                <div className="p-6">
                  {activeTab === 'overview' && (
                    <div className="grid grid-cols-3 gap-6">
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <div className="text-sm text-gray-500 dark:text-gray-400">Members</div>
                        <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                          {selectedWorkspace.member_count}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <div className="text-sm text-gray-500 dark:text-gray-400">Dashboards</div>
                        <div className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">
                          {selectedWorkspace.dashboard_count}
                        </div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <div className="text-sm text-gray-500 dark:text-gray-400">Created</div>
                        <div className="mt-1 text-lg font-medium text-gray-900 dark:text-white">
                          {new Date(selectedWorkspace.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === 'members' && (
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                          Team Members
                        </h3>
                        <button
                          onClick={() => setShowInviteModal(true)}
                          className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 flex items-center gap-2"
                        >
                          <UserPlus className="w-4 h-4" />
                          Invite
                        </button>
                      </div>

                      {/* Members List */}
                      <div className="space-y-3">
                        {members
                          .filter(m => m.workspace_id === selectedWorkspace.id)
                          .map((member) => {
                            const RoleIcon = roleIcons[member.role];
                            return (
                              <div
                                key={member.id}
                                className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                              >
                                <div className="flex items-center gap-3">
                                  <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                      {member.user_name?.charAt(0) || '?'}
                                    </span>
                                  </div>
                                  <div>
                                    <div className="font-medium text-gray-900 dark:text-white">
                                      {member.user_name}
                                    </div>
                                    <div className="text-sm text-gray-500 dark:text-gray-400">
                                      {member.user_email}
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-4">
                                  <div className="flex items-center gap-2">
                                    <RoleIcon className="w-4 h-4 text-gray-400" />
                                    <span className="text-sm text-gray-600 dark:text-gray-300">
                                      {ROLE_LABELS[member.role]}
                                    </span>
                                  </div>
                                  <div className="text-xs text-gray-400">
                                    Active {formatLastAccessed(member.last_accessed_at)}
                                  </div>
                                  {member.role !== 'owner' && currentUserRole !== 'viewer' && currentUserRole !== 'member' && (
                                    <button
                                      onClick={() => handleRemoveMember(member.id)}
                                      className="p-1 text-gray-400 hover:text-red-500"
                                    >
                                      <X className="w-4 h-4" />
                                    </button>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                      </div>

                      {/* Pending Invitations */}
                      {invitations.filter(i => i.workspace_id === selectedWorkspace.id && i.status === 'pending').length > 0 && (
                        <div className="mt-6">
                          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                            Pending Invitations
                          </h4>
                          <div className="space-y-2">
                            {invitations
                              .filter(i => i.workspace_id === selectedWorkspace.id && i.status === 'pending')
                              .map((invitation) => (
                                <div
                                  key={invitation.id}
                                  className="flex items-center justify-between p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg"
                                >
                                  <div className="flex items-center gap-3">
                                    <Mail className="w-5 h-5 text-amber-500" />
                                    <div>
                                      <div className="font-medium text-gray-900 dark:text-white">
                                        {invitation.email}
                                      </div>
                                      <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2">
                                        <Clock className="w-3 h-3" />
                                        Expires {new Date(invitation.expires_at).toLocaleDateString()}
                                      </div>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <button
                                      onClick={() => handleCopyInviteLink(invitation.id)}
                                      className="p-1.5 text-gray-400 hover:text-gray-600"
                                      title="Copy invite link"
                                    >
                                      {copiedId === invitation.id ? (
                                        <Check className="w-4 h-4 text-green-500" />
                                      ) : (
                                        <Copy className="w-4 h-4" />
                                      )}
                                    </button>
                                    <button
                                      onClick={() => handleRevokeInvitation(invitation.id)}
                                      className="p-1.5 text-gray-400 hover:text-red-500"
                                      title="Revoke invitation"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </button>
                                  </div>
                                </div>
                              ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'settings' && (
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Workspace Name
                        </label>
                        <input
                          type="text"
                          defaultValue={selectedWorkspace.name}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Description
                        </label>
                        <textarea
                          defaultValue={selectedWorkspace.description}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        />
                      </div>
                      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h4 className="text-sm font-medium text-red-600 mb-2">Danger Zone</h4>
                        <button className="px-4 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20">
                          Delete Workspace
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
                <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Select a workspace
                </h3>
                <p className="mt-1 text-gray-500 dark:text-gray-400">
                  Choose a workspace from the list to view details and manage members.
                </p>
              </div>
            )}
          </div>
        </div>
        )}
      </div>

      {/* Create Workspace Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Create New Workspace
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Workspace Name
                </label>
                <input
                  type="text"
                  value={newWorkspaceName}
                  onChange={(e) => setNewWorkspaceName(e.target.value)}
                  placeholder="e.g., Marketing Team"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description (optional)
                </label>
                <textarea
                  value={newWorkspaceDesc}
                  onChange={(e) => setNewWorkspaceDesc(e.target.value)}
                  placeholder="What is this workspace for?"
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateWorkspace}
                disabled={!newWorkspaceName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Create Workspace
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Invite Member Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Invite Team Member
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="colleague@company.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Role
                </label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value as WorkspaceRole)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  {getAvailableRolesForAssignment(currentUserRole).map((role) => (
                    <option key={role} value={role}>
                      {ROLE_LABELS[role]}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowInviteModal(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleInviteMember}
                disabled={!inviteEmail.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Send Invitation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Workspaces;
