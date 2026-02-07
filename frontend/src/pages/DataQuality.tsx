/**
 * Data Quality Page
 *
 * Manage data quality rules and monitoring
 */

import { useState, useEffect } from 'react';
import {
  Shield,
  Plus,
  Search,
  Edit,
  Trash2,
  Play,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Database,
  Table2,
  Columns,
  TrendingUp,
  BarChart3,
  RefreshCw,
  Eye,
} from 'lucide-react';
import api from '../lib/api';

interface QualityRule {
  id: string;
  name: string;
  description: string | null;
  rule_type: 'not_null' | 'unique' | 'range_check' | 'regex' | 'enum_check' | 'foreign_key' | 'custom_sql' | 'freshness' | 'row_count';
  severity: 'info' | 'warning' | 'error' | 'critical';
  connection_id: string;
  table_name: string;
  column_name: string | null;
  rule_config: Record<string, any>;
  error_threshold: number;
  warning_threshold: number;
  is_active: boolean;
  check_frequency: string;
  last_check_at: string | null;
  created_at: string;
}

interface QualityCheck {
  id: string;
  rule_id: string;
  status: 'pending' | 'running' | 'passed' | 'failed' | 'error';
  total_rows: number;
  passed_rows: number;
  failed_rows: number;
  pass_rate: number;
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  error_message: string | null;
  failed_samples: Array<Record<string, any>>;
}

interface QualityScore {
  id: string;
  asset_type: string;
  connection_id: string;
  table_name: string | null;
  overall_score: number;
  completeness_score: number | null;
  validity_score: number | null;
  freshness_score: number | null;
  rules_passed: number;
  rules_failed: number;
  calculated_at: string;
}

const ruleTypeLabels: Record<string, string> = {
  not_null: 'Not Null',
  unique: 'Unique',
  range_check: 'Range Check',
  regex: 'Regex Pattern',
  enum_check: 'Enum Values',
  foreign_key: 'Foreign Key',
  custom_sql: 'Custom SQL',
  freshness: 'Freshness',
  row_count: 'Row Count',
};

const severityColors: Record<string, string> = {
  info: 'bg-blue-100 text-blue-800',
  warning: 'bg-yellow-100 text-yellow-800',
  error: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
};

const statusColors: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  passed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  error: 'bg-orange-100 text-orange-800',
};

export default function DataQuality() {
  const [activeTab, setActiveTab] = useState<'rules' | 'checks' | 'scores'>('rules');
  const [rules, setRules] = useState<QualityRule[]>([]);
  const [checks, setChecks] = useState<QualityCheck[]>([]);
  const [scores, setScores] = useState<QualityScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateRuleModal, setShowCreateRuleModal] = useState(false);
  const [runningRules, setRunningRules] = useState<Set<string>>(new Set());

  const [newRule, setNewRule] = useState({
    name: '',
    description: '',
    rule_type: 'not_null' as const,
    severity: 'warning' as const,
    connection_id: '',
    table_name: '',
    column_name: '',
    error_threshold: 0,
    warning_threshold: 5,
    check_frequency: 'daily',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [rulesRes, checksRes, scoresRes] = await Promise.all([
        api.get('/governance/quality/rules'),
        api.get('/governance/quality/checks'),
        api.get('/governance/quality/scores'),
      ]);
      setRules(rulesRes.data);
      setChecks(checksRes.data);
      setScores(scoresRes.data);
    } catch (err) {
      console.error('Error fetching quality data:', err);
    } finally {
      setLoading(false);
    }
  };

  const createRule = async () => {
    try {
      await api.post('/governance/quality/rules', {
        ...newRule,
        workspace_id: crypto.randomUUID(),
        rule_config: {},
        is_active: true,
      });
      setShowCreateRuleModal(false);
      setNewRule({
        name: '',
        description: '',
        rule_type: 'not_null',
        severity: 'warning',
        connection_id: '',
        table_name: '',
        column_name: '',
        error_threshold: 0,
        warning_threshold: 5,
        check_frequency: 'daily',
      });
      fetchData();
    } catch (err) {
      console.error('Error creating rule:', err);
    }
  };

  const runQualityCheck = async (ruleId: string) => {
    try {
      setRunningRules((prev) => new Set(prev).add(ruleId));
      await api.post('/governance/quality/run', {
        rule_ids: [ruleId],
      });
      fetchData();
    } catch (err) {
      console.error('Error running quality check:', err);
    } finally {
      setRunningRules((prev) => {
        const next = new Set(prev);
        next.delete(ruleId);
        return next;
      });
    }
  };

  const runAllChecks = async () => {
    try {
      await api.post('/governance/quality/run', {});
      fetchData();
    } catch (err) {
      console.error('Error running all checks:', err);
    }
  };

  const filteredRules = rules.filter(
    (r) =>
      r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.table_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Calculate overall stats
  const totalRules = rules.length;
  const activeRules = rules.filter((r) => r.is_active).length;
  const passedChecks = checks.filter((c) => c.status === 'passed').length;
  const failedChecks = checks.filter((c) => c.status === 'failed').length;
  const avgScore = scores.length > 0
    ? Math.round(scores.reduce((sum, s) => sum + s.overall_score, 0) / scores.length)
    : 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="h-7 w-7 text-emerald-600" />
            Data Quality
          </h1>
          <p className="text-gray-500 mt-1">
            Monitor and enforce data quality rules
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={runAllChecks}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            <Play className="h-4 w-4" />
            Run All Checks
          </button>
          <button
            onClick={() => setShowCreateRuleModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
          >
            <Plus className="h-4 w-4" />
            Add Rule
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{totalRules}</div>
              <div className="text-sm text-gray-500">Total Rules</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-100 text-green-600">
              <CheckCircle className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{activeRules}</div>
              <div className="text-sm text-gray-500">Active Rules</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-100 text-emerald-600">
              <CheckCircle className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{passedChecks}</div>
              <div className="text-sm text-gray-500">Passed Checks</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-100 text-red-600">
              <XCircle className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{failedChecks}</div>
              <div className="text-sm text-gray-500">Failed Checks</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-100 text-purple-600">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{avgScore}%</div>
              <div className="text-sm text-gray-500">Avg Quality Score</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { key: 'rules', label: 'Quality Rules', icon: Shield },
            { key: 'checks', label: 'Check History', icon: Clock },
            { key: 'scores', label: 'Quality Scores', icon: BarChart3 },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-emerald-500 text-emerald-600'
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
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
        />
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
        </div>
      ) : (
        <>
          {/* Rules Tab */}
          {activeTab === 'rules' && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rule</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Frequency</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Check</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredRules.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                        <Shield className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <p>No quality rules defined</p>
                        <button
                          onClick={() => setShowCreateRuleModal(true)}
                          className="mt-4 text-emerald-600 hover:underline"
                        >
                          Create your first rule
                        </button>
                      </td>
                    </tr>
                  ) : (
                    filteredRules.map((rule) => (
                      <tr key={rule.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className={`w-2 h-2 rounded-full ${rule.is_active ? 'bg-green-500' : 'bg-gray-300'}`} />
                              <span className="font-medium text-gray-900">{rule.name}</span>
                            </div>
                            {rule.description && (
                              <div className="text-sm text-gray-500 mt-1">{rule.description}</div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                            {ruleTypeLabels[rule.rule_type]}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm">
                            <div className="flex items-center gap-1 text-gray-700">
                              <Table2 className="h-3 w-3" />
                              {rule.table_name}
                            </div>
                            {rule.column_name && (
                              <div className="flex items-center gap-1 text-gray-500 mt-1">
                                <Columns className="h-3 w-3" />
                                {rule.column_name}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${severityColors[rule.severity]}`}>
                            {rule.severity}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {rule.check_frequency}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {rule.last_check_at
                            ? new Date(rule.last_check_at).toLocaleString()
                            : 'Never'}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => runQualityCheck(rule.id)}
                              disabled={runningRules.has(rule.id)}
                              className="p-1 text-gray-400 hover:text-emerald-600 disabled:opacity-50"
                              title="Run check"
                            >
                              {runningRules.has(rule.id) ? (
                                <RefreshCw className="h-4 w-4 animate-spin" />
                              ) : (
                                <Play className="h-4 w-4" />
                              )}
                            </button>
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

          {/* Checks Tab */}
          {activeTab === 'checks' && (
            <div className="space-y-4">
              {checks.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No quality checks run yet</p>
                </div>
              ) : (
                checks.map((check) => {
                  const rule = rules.find((r) => r.id === check.rule_id);
                  return (
                    <div
                      key={check.id}
                      className="bg-white rounded-lg border border-gray-200 p-4"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`p-2 rounded-full ${
                            check.status === 'passed' ? 'bg-green-100' :
                            check.status === 'failed' ? 'bg-red-100' :
                            check.status === 'running' ? 'bg-blue-100' :
                            'bg-gray-100'
                          }`}>
                            {check.status === 'passed' && <CheckCircle className="h-5 w-5 text-green-600" />}
                            {check.status === 'failed' && <XCircle className="h-5 w-5 text-red-600" />}
                            {check.status === 'running' && <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />}
                            {check.status === 'error' && <AlertTriangle className="h-5 w-5 text-orange-600" />}
                            {check.status === 'pending' && <Clock className="h-5 w-5 text-gray-600" />}
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900">
                              {rule?.name || 'Unknown Rule'}
                            </h3>
                            <p className="text-sm text-gray-500">
                              {new Date(check.started_at).toLocaleString()}
                              {check.duration_ms && ` • ${check.duration_ms}ms`}
                            </p>
                          </div>
                        </div>
                        <span className={`px-3 py-1 text-sm font-medium rounded-full ${statusColors[check.status]}`}>
                          {check.status}
                        </span>
                      </div>

                      {check.status !== 'pending' && check.status !== 'running' && (
                        <div className="mt-4 grid grid-cols-4 gap-4">
                          <div className="text-center p-3 bg-gray-50 rounded">
                            <div className="text-lg font-semibold text-gray-900">{check.total_rows.toLocaleString()}</div>
                            <div className="text-xs text-gray-500">Total Rows</div>
                          </div>
                          <div className="text-center p-3 bg-green-50 rounded">
                            <div className="text-lg font-semibold text-green-700">{check.passed_rows.toLocaleString()}</div>
                            <div className="text-xs text-green-600">Passed</div>
                          </div>
                          <div className="text-center p-3 bg-red-50 rounded">
                            <div className="text-lg font-semibold text-red-700">{check.failed_rows.toLocaleString()}</div>
                            <div className="text-xs text-red-600">Failed</div>
                          </div>
                          <div className="text-center p-3 bg-blue-50 rounded">
                            <div className="text-lg font-semibold text-blue-700">{check.pass_rate.toFixed(1)}%</div>
                            <div className="text-xs text-blue-600">Pass Rate</div>
                          </div>
                        </div>
                      )}

                      {check.error_message && (
                        <div className="mt-4 p-3 bg-red-50 rounded text-sm text-red-700">
                          {check.error_message}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* Scores Tab */}
          {activeTab === 'scores' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {scores.length === 0 ? (
                <div className="col-span-full text-center py-12 text-gray-500">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No quality scores calculated yet</p>
                </div>
              ) : (
                scores.map((score) => (
                  <div
                    key={score.id}
                    className="bg-white rounded-lg border border-gray-200 p-4"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <Database className="h-5 w-5 text-gray-500" />
                        <span className="font-medium text-gray-900">
                          {score.table_name || 'All Tables'}
                        </span>
                      </div>
                      <div className={`text-2xl font-bold ${
                        score.overall_score >= 90 ? 'text-green-600' :
                        score.overall_score >= 70 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {score.overall_score}%
                      </div>
                    </div>

                    <div className="space-y-3">
                      {score.completeness_score !== null && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">Completeness</span>
                            <span className="font-medium">{score.completeness_score}%</span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-500"
                              style={{ width: `${score.completeness_score}%` }}
                            />
                          </div>
                        </div>
                      )}
                      {score.validity_score !== null && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">Validity</span>
                            <span className="font-medium">{score.validity_score}%</span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-purple-500"
                              style={{ width: `${score.validity_score}%` }}
                            />
                          </div>
                        </div>
                      )}
                      {score.freshness_score !== null && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">Freshness</span>
                            <span className="font-medium">{score.freshness_score}%</span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-teal-500"
                              style={{ width: `${score.freshness_score}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between text-sm">
                      <div className="text-gray-500">
                        <span className="text-green-600 font-medium">{score.rules_passed}</span> passed /
                        <span className="text-red-600 font-medium ml-1">{score.rules_failed}</span> failed
                      </div>
                      <span className="text-xs text-gray-400">
                        {new Date(score.calculated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}

      {/* Create Rule Modal */}
      {showCreateRuleModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4">Create Quality Rule</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newRule.name}
                  onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  placeholder="Customer ID Not Null"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newRule.description}
                  onChange={(e) => setNewRule({ ...newRule, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  rows={2}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rule Type</label>
                  <select
                    value={newRule.rule_type}
                    onChange={(e) => setNewRule({ ...newRule, rule_type: e.target.value as any })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  >
                    {Object.entries(ruleTypeLabels).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                  <select
                    value={newRule.severity}
                    onChange={(e) => setNewRule({ ...newRule, severity: e.target.value as any })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Table Name</label>
                <input
                  type="text"
                  value={newRule.table_name}
                  onChange={(e) => setNewRule({ ...newRule, table_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  placeholder="customers"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Column Name (optional)</label>
                <input
                  type="text"
                  value={newRule.column_name}
                  onChange={(e) => setNewRule({ ...newRule, column_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  placeholder="customer_id"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Error Threshold (%)</label>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={newRule.error_threshold}
                    onChange={(e) => setNewRule({ ...newRule, error_threshold: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Warning Threshold (%)</label>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={newRule.warning_threshold}
                    onChange={(e) => setNewRule({ ...newRule, warning_threshold: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Check Frequency</label>
                <select
                  value={newRule.check_frequency}
                  onChange={(e) => setNewRule({ ...newRule, check_frequency: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowCreateRuleModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={createRule}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
              >
                Create Rule
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
