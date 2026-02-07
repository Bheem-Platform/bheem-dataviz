/**
 * Filter Presets Management Page
 *
 * Allows users to view, create, edit, and delete saved filter presets.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Play,
  ExternalLink,
  X,
  PlusCircle,
} from 'lucide-react';
import { SavedFilterPreset, FilterCondition, SlicerConfig, FilterOperator } from '../types/filters';
import api, { filtersApi } from '../lib/api';
import { cn } from '../lib/utils';

interface FilterPresetFormData {
  name: string;
  description: string;
  dashboardId?: string;
  chartId?: string;
  isDefault: boolean;
  filters: FilterCondition[];
}

const FILTER_OPERATORS: { value: FilterOperator; label: string }[] = [
  { value: '=', label: 'Equals' },
  { value: '!=', label: 'Not Equals' },
  { value: '>', label: 'Greater Than' },
  { value: '>=', label: 'Greater Than or Equal' },
  { value: '<', label: 'Less Than' },
  { value: '<=', label: 'Less Than or Equal' },
  { value: 'contains', label: 'Contains' },
  { value: 'starts_with', label: 'Starts With' },
  { value: 'ends_with', label: 'Ends With' },
  { value: 'in', label: 'In List' },
  { value: 'not_in', label: 'Not In List' },
  { value: 'between', label: 'Between' },
  { value: 'is_null', label: 'Is Empty' },
  { value: 'is_not_null', label: 'Is Not Empty' },
];

const FilterPresets: React.FC = () => {
  const navigate = useNavigate();
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
    filters: [],
  });
  const [dashboards, setDashboards] = useState<{ id: string; name: string }[]>([]);
  const [charts, setCharts] = useState<{ id: string; name: string }[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Fetch presets
  useEffect(() => {
    fetchPresets();
    fetchDashboards();
    fetchCharts();
  }, []);

  const fetchPresets = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get('/filters/presets');
      const data = response.data;
      // API returns array of presets - convert snake_case to camelCase
      const presetsList = Array.isArray(data) ? data : (data.presets || []);
      const convertedPresets = presetsList.map((p: any) => ({
        id: p.id,
        name: p.name,
        description: p.description,
        dashboardId: p.dashboard_id,
        chartId: p.chart_id,
        filters: p.filters || [],
        slicers: p.slicers || [],
        isDefault: p.is_default,
        createdBy: p.created_by,
        createdAt: p.created_at,
        updatedAt: p.updated_at,
      }));
      setPresets(convertedPresets);
    } catch (err) {
      console.error('Failed to fetch presets:', err);
      setError('Failed to load filter presets. Please try again.');
      setPresets([]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDashboards = async () => {
    try {
      const response = await api.get('/dashboards/');
      const data = response.data;
      // API returns array of dashboard summaries
      setDashboards(Array.isArray(data) ? data.map((d: any) => ({ id: d.id, name: d.name })) : []);
    } catch (error) {
      console.error('Failed to fetch dashboards:', error);
      setDashboards([]);
    }
  };

  const fetchCharts = async () => {
    try {
      const response = await api.get('/charts/');
      const data = response.data;
      // API returns array of charts
      setCharts(Array.isArray(data) ? data.map((c: any) => ({ id: c.id, name: c.name || c.title })) : []);
    } catch (error) {
      console.error('Failed to fetch charts:', error);
      setCharts([]);
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
      await api.post('/filters/presets', {
        name: formData.name,
        description: formData.description,
        is_default: formData.isDefault,
        filters: formData.filters.filter(f => f.column), // Only include filters with column set
        slicers: [],
      }, {
        params: {
          dashboard_id: formData.dashboardId || undefined,
          chart_id: formData.chartId || undefined,
        }
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
      await api.put(`/filters/presets/${selectedPreset.id}`, {
        name: formData.name,
        description: formData.description,
        is_default: formData.isDefault,
        filters: formData.filters.filter(f => f.column), // Only include filters with column set
        slicers: selectedPreset.slicers || [],
      });
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
      await api.delete(`/filters/presets/${selectedPreset.id}`);
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
      await api.post('/filters/presets', {
        name: `${preset.name} (Copy)`,
        description: preset.description,
        filters: preset.filters || [],
        slicers: preset.slicers || [],
        is_default: false,
      }, {
        params: {
          dashboard_id: preset.dashboardId || undefined,
          chart_id: preset.chartId || undefined,
        }
      });
      fetchPresets();
    } catch (error) {
      console.error('Failed to duplicate preset:', error);
    }
  };

  // Toggle default
  const handleToggleDefault = async (preset: SavedFilterPreset) => {
    try {
      await api.put(`/filters/presets/${preset.id}`, {
        name: preset.name,
        description: preset.description,
        is_default: !preset.isDefault,
        filters: preset.filters || [],
        slicers: preset.slicers || [],
      });
      fetchPresets();
    } catch (error) {
      console.error('Failed to toggle default:', error);
    }
  };

  // Apply preset - navigate to dashboard with filters
  const handleApplyPreset = (preset: SavedFilterPreset) => {
    if (preset.dashboardId) {
      // Navigate to dashboard with preset filters
      navigate(`/dashboards/${preset.dashboardId}?preset=${preset.id}`);
    } else if (preset.chartId) {
      // Navigate to chart builder with preset filters
      navigate(`/charts/${preset.chartId}?preset=${preset.id}`);
    } else {
      // Show message that preset is not associated with a dashboard/chart
      alert('This preset is not associated with a dashboard or chart. Edit the preset to associate it first.');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      isDefault: false,
      filters: [],
    });
    setSelectedPreset(null);
  };

  // Filter management functions
  const addFilter = () => {
    setFormData({
      ...formData,
      filters: [
        ...formData.filters,
        { column: '', operator: '=' as FilterOperator, value: '' },
      ],
    });
  };

  const updateFilter = (index: number, field: keyof FilterCondition, value: any) => {
    const newFilters = [...formData.filters];
    newFilters[index] = { ...newFilters[index], [field]: value };
    setFormData({ ...formData, filters: newFilters });
  };

  const removeFilter = (index: number) => {
    const newFilters = formData.filters.filter((_, i) => i !== index);
    setFormData({ ...formData, filters: newFilters });
  };

  const openEditModal = (preset: SavedFilterPreset) => {
    setSelectedPreset(preset);
    setFormData({
      name: preset.name,
      description: preset.description || '',
      dashboardId: preset.dashboardId,
      chartId: preset.chartId,
      isDefault: preset.isDefault,
      filters: preset.filters || [],
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
    <div className="h-full overflow-auto bg-gray-50">
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-24">
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

        {/* Error State */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
            <button
              onClick={fetchPresets}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Presets Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          </div>
        ) : error ? null : filteredPresets.length === 0 ? (
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
                    <div className="flex items-center gap-2 mb-3 flex-wrap">
                      {preset.dashboardId && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-50 text-purple-700 text-xs rounded max-w-full">
                          <LayoutDashboard className="h-3 w-3 flex-shrink-0" />
                          <span className="truncate">
                            {dashboards.find(d => d.id === preset.dashboardId)?.name || 'Dashboard'}
                          </span>
                        </span>
                      )}
                      {preset.chartId && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-700 text-xs rounded max-w-full">
                          <BarChart3 className="h-3 w-3 flex-shrink-0" />
                          <span className="truncate">
                            {charts.find(c => c.id === preset.chartId)?.name || 'Chart'}
                          </span>
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
                    {(preset.dashboardId || preset.chartId) && (
                      <button
                        onClick={() => handleApplyPreset(preset)}
                        className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      >
                        <ExternalLink className="h-3 w-3" />
                        Apply
                      </button>
                    )}
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
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] flex flex-col">
            <div className="px-6 py-4 border-b flex-shrink-0">
              <h2 className="text-lg font-semibold">Create Filter Preset</h2>
            </div>
            <div className="p-6 space-y-4 overflow-y-auto flex-1">
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

              {/* Filter Conditions Section */}
              <div className="border-t pt-4">
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Filter Conditions
                  </label>
                  <button
                    type="button"
                    onClick={addFilter}
                    className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                  >
                    <PlusCircle className="h-4 w-4" />
                    Add Filter
                  </button>
                </div>

                {formData.filters.length === 0 ? (
                  <p className="text-sm text-gray-500 italic">No filters configured. Click "Add Filter" to create one.</p>
                ) : (
                  <div className="space-y-3 max-h-48 overflow-y-auto">
                    {formData.filters.map((filter, index) => (
                      <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1 grid grid-cols-3 gap-2">
                          <input
                            type="text"
                            value={filter.column}
                            onChange={(e) => updateFilter(index, 'column', e.target.value)}
                            placeholder="Column"
                            className="px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                          <select
                            value={filter.operator}
                            onChange={(e) => updateFilter(index, 'operator', e.target.value as FilterOperator)}
                            className="px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          >
                            {FILTER_OPERATORS.map((op) => (
                              <option key={op.value} value={op.value}>
                                {op.label}
                              </option>
                            ))}
                          </select>
                          {filter.operator === 'is_null' || filter.operator === 'is_not_null' ? (
                            <span className="px-2 py-1.5 text-sm text-gray-400 italic">No value needed</span>
                          ) : filter.operator === 'between' ? (
                            <div className="flex gap-1">
                              <input
                                type="text"
                                value={filter.value || ''}
                                onChange={(e) => updateFilter(index, 'value', e.target.value)}
                                placeholder="From"
                                className="w-1/2 px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                              />
                              <input
                                type="text"
                                value={filter.value2 || ''}
                                onChange={(e) => updateFilter(index, 'value2', e.target.value)}
                                placeholder="To"
                                className="w-1/2 px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                              />
                            </div>
                          ) : (
                            <input
                              type="text"
                              value={filter.value || ''}
                              onChange={(e) => updateFilter(index, 'value', e.target.value)}
                              placeholder="Value"
                              className="px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            />
                          )}
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFilter(index)}
                          className="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg flex-shrink-0">
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
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] flex flex-col">
            <div className="px-6 py-4 border-b flex-shrink-0">
              <h2 className="text-lg font-semibold">Edit Filter Preset</h2>
            </div>
            <div className="p-6 space-y-4 overflow-y-auto flex-1">
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

              {/* Filter Conditions Section */}
              <div className="border-t pt-4">
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Filter Conditions
                  </label>
                  <button
                    type="button"
                    onClick={addFilter}
                    className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                  >
                    <PlusCircle className="h-4 w-4" />
                    Add Filter
                  </button>
                </div>

                {formData.filters.length === 0 ? (
                  <p className="text-sm text-gray-500 italic">No filters configured. Click "Add Filter" to create one.</p>
                ) : (
                  <div className="space-y-3 max-h-48 overflow-y-auto">
                    {formData.filters.map((filter, index) => (
                      <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1 grid grid-cols-3 gap-2">
                          <input
                            type="text"
                            value={filter.column}
                            onChange={(e) => updateFilter(index, 'column', e.target.value)}
                            placeholder="Column"
                            className="px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                          <select
                            value={filter.operator}
                            onChange={(e) => updateFilter(index, 'operator', e.target.value as FilterOperator)}
                            className="px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          >
                            {FILTER_OPERATORS.map((op) => (
                              <option key={op.value} value={op.value}>
                                {op.label}
                              </option>
                            ))}
                          </select>
                          {filter.operator === 'is_null' || filter.operator === 'is_not_null' ? (
                            <span className="px-2 py-1.5 text-sm text-gray-400 italic">No value needed</span>
                          ) : filter.operator === 'between' ? (
                            <div className="flex gap-1">
                              <input
                                type="text"
                                value={filter.value || ''}
                                onChange={(e) => updateFilter(index, 'value', e.target.value)}
                                placeholder="From"
                                className="w-1/2 px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                              />
                              <input
                                type="text"
                                value={filter.value2 || ''}
                                onChange={(e) => updateFilter(index, 'value2', e.target.value)}
                                placeholder="To"
                                className="w-1/2 px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                              />
                            </div>
                          ) : (
                            <input
                              type="text"
                              value={filter.value || ''}
                              onChange={(e) => updateFilter(index, 'value', e.target.value)}
                              placeholder="Value"
                              className="px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            />
                          )}
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFilter(index)}
                          className="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg flex-shrink-0">
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
