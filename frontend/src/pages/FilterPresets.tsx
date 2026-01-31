/**
 * Filter Presets Management Page
 *
 * Allows users to view, create, edit, and delete saved filter presets.
 */

import React, { useState, useEffect } from 'react';
import {
  Filter,
  Plus,
  Search,
  Edit2,
  Trash2,
  Copy,
  Check,
  Star,
  StarOff,
  MoreVertical,
  Calendar,
  LayoutDashboard,
  BarChart3,
} from 'lucide-react';
import { SavedFilterPreset, FilterCondition, SlicerConfig } from '../types/filters';
import api from '../lib/api';
import { cn } from '../lib/utils';

interface FilterPresetFormData {
  name: string;
  description: string;
  dashboardId?: string;
  chartId?: string;
  isDefault: boolean;
}

const FilterPresets: React.FC = () => {
  const [presets, setPresets] = useState<SavedFilterPreset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPreset, setSelectedPreset] = useState<SavedFilterPreset | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [formData, setFormData] = useState<FilterPresetFormData>({
    name: '',
    description: '',
    isDefault: false,
  });
  const [dashboards, setDashboards] = useState<{ id: string; name: string }[]>([]);
  const [charts, setCharts] = useState<{ id: string; name: string }[]>([]);

  // Fetch presets
  useEffect(() => {
    fetchPresets();
    fetchDashboards();
    fetchCharts();
  }, []);

  const fetchPresets = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/api/v1/filters/presets');
      setPresets(response.data.presets || response.data || []);
    } catch (error) {
      console.error('Failed to fetch presets:', error);
      setPresets([]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDashboards = async () => {
    try {
      const response = await api.get('/api/v1/dashboards');
      setDashboards(response.data.dashboards || response.data || []);
    } catch (error) {
      console.error('Failed to fetch dashboards:', error);
    }
  };

  const fetchCharts = async () => {
    try {
      const response = await api.get('/api/v1/charts');
      setCharts(response.data.charts || response.data || []);
    } catch (error) {
      console.error('Failed to fetch charts:', error);
    }
  };

  // Filter presets by search query
  const filteredPresets = presets.filter((preset) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      preset.name.toLowerCase().includes(query) ||
      (preset.description?.toLowerCase().includes(query) ?? false)
    );
  });

  // Create preset
  const handleCreate = async () => {
    try {
      await api.post('/api/v1/filters/presets', {
        ...formData,
        filters: [],
        slicers: [],
      });
      setIsCreateModalOpen(false);
      resetForm();
      fetchPresets();
    } catch (error) {
      console.error('Failed to create preset:', error);
    }
  };

  // Update preset
  const handleUpdate = async () => {
    if (!selectedPreset) return;
    try {
      await api.patch(`/api/v1/filters/presets/${selectedPreset.id}`, formData);
      setIsEditModalOpen(false);
      resetForm();
      fetchPresets();
    } catch (error) {
      console.error('Failed to update preset:', error);
    }
  };

  // Delete preset
  const handleDelete = async () => {
    if (!selectedPreset) return;
    try {
      await api.delete(`/api/v1/filters/presets/${selectedPreset.id}`);
      setIsDeleteModalOpen(false);
      setSelectedPreset(null);
      fetchPresets();
    } catch (error) {
      console.error('Failed to delete preset:', error);
    }
  };

  // Duplicate preset
  const handleDuplicate = async (preset: SavedFilterPreset) => {
    try {
      await api.post('/api/v1/filters/presets', {
        name: `${preset.name} (Copy)`,
        description: preset.description,
        dashboardId: preset.dashboardId,
        chartId: preset.chartId,
        filters: preset.filters,
        slicers: preset.slicers,
        isDefault: false,
      });
      fetchPresets();
    } catch (error) {
      console.error('Failed to duplicate preset:', error);
    }
  };

  // Toggle default
  const handleToggleDefault = async (preset: SavedFilterPreset) => {
    try {
      await api.patch(`/api/v1/filters/presets/${preset.id}`, {
        isDefault: !preset.isDefault,
      });
      fetchPresets();
    } catch (error) {
      console.error('Failed to toggle default:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      isDefault: false,
    });
    setSelectedPreset(null);
  };

  const openEditModal = (preset: SavedFilterPreset) => {
    setSelectedPreset(preset);
    setFormData({
      name: preset.name,
      description: preset.description || '',
      dashboardId: preset.dashboardId,
      chartId: preset.chartId,
      isDefault: preset.isDefault,
    });
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (preset: SavedFilterPreset) => {
    setSelectedPreset(preset);
    setIsDeleteModalOpen(true);
  };

  const formatFilterCount = (filters: FilterCondition[]) => {
    if (!filters || filters.length === 0) return 'No filters';
    return `${filters.length} filter${filters.length > 1 ? 's' : ''}`;
  };

  const formatSlicerCount = (slicers: SlicerConfig[]) => {
    if (!slicers || slicers.length === 0) return 'No slicers';
    return `${slicers.length} slicer${slicers.length > 1 ? 's' : ''}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Filter className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900">Filter Presets</h1>
                <p className="text-sm text-gray-500">
                  Manage saved filter configurations for dashboards and charts
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
              New Preset
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Search */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search presets..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Presets Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          </div>
        ) : filteredPresets.length === 0 ? (
          <div className="text-center py-12">
            <Filter className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">
              {searchQuery ? 'No presets found' : 'No filter presets yet'}
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              {searchQuery
                ? 'Try adjusting your search query'
                : 'Create your first filter preset to get started'}
            </p>
            {!searchQuery && (
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                Create Preset
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPresets.map((preset) => (
              <div
                key={preset.id}
                className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="p-4">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-2">
                      {preset.isDefault && (
                        <Star className="h-4 w-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                      )}
                      <div>
                        <h3 className="font-medium text-gray-900">{preset.name}</h3>
                        {preset.description && (
                          <p className="text-sm text-gray-500 mt-0.5 line-clamp-2">
                            {preset.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="relative group">
                      <button className="p-1 rounded hover:bg-gray-100">
                        <MoreVertical className="h-4 w-4 text-gray-400" />
                      </button>
                      {/* Dropdown Menu */}
                      <div className="absolute right-0 mt-1 w-40 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                        <button
                          onClick={() => openEditModal(preset)}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                          <Edit2 className="h-4 w-4" />
                          Edit
                        </button>
                        <button
                          onClick={() => handleDuplicate(preset)}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                          <Copy className="h-4 w-4" />
                          Duplicate
                        </button>
                        <button
                          onClick={() => handleToggleDefault(preset)}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                          {preset.isDefault ? (
                            <>
                              <StarOff className="h-4 w-4" />
                              Remove Default
                            </>
                          ) : (
                            <>
                              <Star className="h-4 w-4" />
                              Set as Default
                            </>
                          )}
                        </button>
                        <hr className="my-1" />
                        <button
                          onClick={() => openDeleteModal(preset)}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                    <span className="flex items-center gap-1">
                      <Filter className="h-3.5 w-3.5" />
                      {formatFilterCount(preset.filters)}
                    </span>
                    <span>{formatSlicerCount(preset.slicers)}</span>
                  </div>

                  {/* Association */}
                  {(preset.dashboardId || preset.chartId) && (
                    <div className="flex items-center gap-2 mb-3">
                      {preset.dashboardId && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-50 text-purple-700 text-xs rounded">
                          <LayoutDashboard className="h-3 w-3" />
                          Dashboard
                        </span>
                      )}
                      {preset.chartId && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-700 text-xs rounded">
                          <BarChart3 className="h-3 w-3" />
                          Chart
                        </span>
                      )}
                    </div>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-3 border-t text-xs text-gray-400">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3.5 w-3.5" />
                      {formatDate(preset.updatedAt)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => {
              setIsCreateModalOpen(false);
              resetForm();
            }}
          />
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="px-6 py-4 border-b">
              <h2 className="text-lg font-semibold">Create Filter Preset</h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="My Filter Preset"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Optional description..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Associate with Dashboard
                </label>
                <select
                  value={formData.dashboardId || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, dashboardId: e.target.value || undefined })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">None</option>
                  {dashboards.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Associate with Chart
                </label>
                <select
                  value={formData.chartId || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, chartId: e.target.value || undefined })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">None</option>
                  {charts.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="isDefault"
                  checked={formData.isDefault}
                  onChange={(e) => setFormData({ ...formData, isDefault: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="isDefault" className="text-sm text-gray-700">
                  Set as default preset
                </label>
              </div>
            </div>
            <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg">
              <button
                onClick={() => {
                  setIsCreateModalOpen(false);
                  resetForm();
                }}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={!formData.name}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {isEditModalOpen && selectedPreset && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => {
              setIsEditModalOpen(false);
              resetForm();
            }}
          />
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="px-6 py-4 border-b">
              <h2 className="text-lg font-semibold">Edit Filter Preset</h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="editIsDefault"
                  checked={formData.isDefault}
                  onChange={(e) => setFormData({ ...formData, isDefault: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="editIsDefault" className="text-sm text-gray-700">
                  Set as default preset
                </label>
              </div>
            </div>
            <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg">
              <button
                onClick={() => {
                  setIsEditModalOpen(false);
                  resetForm();
                }}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdate}
                disabled={!formData.name}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {isDeleteModalOpen && selectedPreset && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => {
              setIsDeleteModalOpen(false);
              setSelectedPreset(null);
            }}
          />
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-sm mx-4">
            <div className="p-6">
              <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mx-auto mb-4">
                <Trash2 className="h-6 w-6 text-red-600" />
              </div>
              <h2 className="text-lg font-semibold text-center mb-2">Delete Preset</h2>
              <p className="text-sm text-gray-500 text-center mb-6">
                Are you sure you want to delete "{selectedPreset.name}"? This action cannot be
                undone.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setIsDeleteModalOpen(false);
                    setSelectedPreset(null);
                  }}
                  className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterPresets;
