/**
 * Compliance Page
 *
 * Data governance and compliance management.
 */

import { useState } from 'react';
import {
  Shield,
  FileCheck,
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  Search,
  Filter,
  Plus,
} from 'lucide-react';

interface CompliancePolicy {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'draft' | 'archived';
  violations: number;
  lastChecked: string;
}

interface Violation {
  id: string;
  policy: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  resource: string;
  detectedAt: string;
  status: 'open' | 'resolved' | 'dismissed';
}

const mockPolicies: CompliancePolicy[] = [
  { id: '1', name: 'Data Retention Policy', type: 'retention', status: 'active', violations: 0, lastChecked: '1 hour ago' },
  { id: '2', name: 'PII Access Control', type: 'access_control', status: 'active', violations: 2, lastChecked: '30 min ago' },
  { id: '3', name: 'Export Restrictions', type: 'export', status: 'active', violations: 0, lastChecked: '2 hours ago' },
  { id: '4', name: 'Data Classification', type: 'classification', status: 'draft', violations: 0, lastChecked: 'Never' },
];

const mockViolations: Violation[] = [
  { id: '1', policy: 'PII Access Control', severity: 'high', description: 'Unauthorized access to customer data', resource: 'customers table', detectedAt: '2 hours ago', status: 'open' },
  { id: '2', policy: 'PII Access Control', severity: 'medium', description: 'Missing data masking on SSN field', resource: 'employees table', detectedAt: '1 day ago', status: 'open' },
];

export function Compliance() {
  const [policies] = useState<CompliancePolicy[]>(mockPolicies);
  const [violations] = useState<Violation[]>(mockViolations);
  const [activeTab, setActiveTab] = useState<'policies' | 'violations'>('policies');

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
      case 'high': return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400';
      case 'medium': return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400';
      case 'low': return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400';
      default: return '';
    }
  };

  const openViolations = violations.filter(v => v.status === 'open').length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Compliance & Governance
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Data policies and compliance monitoring
              </p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Create Policy
            </button>
          </div>

          {/* Summary Stats */}
          <div className="mt-6 grid grid-cols-4 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <FileCheck className="w-4 h-4" />
                Active Policies
              </div>
              <div className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
                {policies.filter(p => p.status === 'active').length}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle className="w-4 h-4" />
                Compliant
              </div>
              <div className="mt-1 text-2xl font-bold text-green-600">
                {policies.filter(p => p.violations === 0).length}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-red-600">
                <AlertTriangle className="w-4 h-4" />
                Open Violations
              </div>
              <div className="mt-1 text-2xl font-bold text-red-600">
                {openViolations}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Clock className="w-4 h-4" />
                Last Scan
              </div>
              <div className="mt-1 text-lg font-medium text-gray-900 dark:text-white">
                30 min ago
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 flex gap-4 border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('policies')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'policies'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500'
              }`}
            >
              Policies ({policies.length})
            </button>
            <button
              onClick={() => setActiveTab('violations')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                activeTab === 'violations'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500'
              }`}
            >
              Violations
              {openViolations > 0 && (
                <span className="px-2 py-0.5 bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 rounded-full text-xs">
                  {openViolations}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'policies' ? (
          <div className="space-y-4">
            {policies.map((policy) => (
              <div key={policy.id} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${
                      policy.status === 'active' ? 'bg-green-100 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-gray-700'
                    }`}>
                      <Shield className={`w-5 h-5 ${
                        policy.status === 'active' ? 'text-green-600' : 'text-gray-400'
                      }`} />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">{policy.name}</h3>
                      <p className="text-sm text-gray-500">Type: {policy.type}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <div className={`text-lg font-bold ${policy.violations > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {policy.violations}
                      </div>
                      <div className="text-xs text-gray-500">Violations</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600 dark:text-gray-400">Last checked</div>
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{policy.lastChecked}</div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      policy.status === 'active'
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                        : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'
                    }`}>
                      {policy.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {violations.map((violation) => (
                <div key={violation.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`p-2 rounded-lg ${getSeverityColor(violation.severity)}`}>
                        <AlertTriangle className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900 dark:text-white">{violation.description}</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Policy: {violation.policy} | Resource: {violation.resource}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">Detected: {violation.detectedAt}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(violation.severity)}`}>
                        {violation.severity}
                      </span>
                      <button className="px-3 py-1 text-sm text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded">
                        Resolve
                      </button>
                      <button className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
                        Dismiss
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Compliance;
