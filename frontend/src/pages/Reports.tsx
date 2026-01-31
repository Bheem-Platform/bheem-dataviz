/**
 * Reports Page
 *
 * Report management and generation.
 */

import { useState } from 'react';
import {
  FileText,
  Plus,
  Download,
  Calendar,
  Clock,
  Mail,
  MoreVertical,
  Search,
  Filter,
} from 'lucide-react';

interface Report {
  id: string;
  name: string;
  type: string;
  lastGenerated: string;
  schedule?: string;
  format: string;
  status: 'ready' | 'generating' | 'scheduled';
}

const mockReports: Report[] = [
  { id: '1', name: 'Monthly Sales Report', type: 'dashboard', lastGenerated: '2026-01-30', schedule: 'Monthly', format: 'PDF', status: 'ready' },
  { id: '2', name: 'Weekly KPI Summary', type: 'dashboard', lastGenerated: '2026-01-29', schedule: 'Weekly', format: 'PDF', status: 'ready' },
  { id: '3', name: 'Customer Analysis', type: 'query', lastGenerated: '2026-01-28', format: 'XLSX', status: 'ready' },
  { id: '4', name: 'Inventory Status', type: 'dashboard', lastGenerated: '2026-01-27', format: 'PDF', status: 'generating' },
];

export function Reports() {
  const [reports] = useState<Report[]>(mockReports);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredReports = reports.filter(r =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Reports
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Generate and manage reports from your dashboards
              </p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Create Report
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Search & Filter */}
        <div className="flex gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search reports..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            />
          </div>
          <button className="px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>

        {/* Reports Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredReports.map((report) => (
            <div key={report.id} className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                      <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">{report.name}</h3>
                      <p className="text-sm text-gray-500">{report.type}</p>
                    </div>
                  </div>
                  <button className="text-gray-400 hover:text-gray-600">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>

                <div className="mt-4 space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <Calendar className="w-4 h-4" />
                    Last generated: {report.lastGenerated}
                  </div>
                  {report.schedule && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <Clock className="w-4 h-4" />
                      Schedule: {report.schedule}
                    </div>
                  )}
                </div>

                <div className="mt-4 flex items-center justify-between">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    report.status === 'ready'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                      : report.status === 'generating'
                      ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                      : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                  }`}>
                    {report.status}
                  </span>
                  <div className="flex gap-2">
                    <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                      <Mail className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredReports.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">No reports found</h3>
            <p className="text-gray-500 mt-1">Create your first report to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Reports;
