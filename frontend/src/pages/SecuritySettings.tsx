/**
 * Security Settings Page
 *
 * Security controls and configuration.
 */

import { useState, useEffect } from 'react';
import {
  Shield,
  Key,
  AlertTriangle,
  CheckCircle,
  Settings,
  Save,
  Loader2,
} from 'lucide-react';
import { securityControlsApi } from '../lib/api';

interface SecuritySetting {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  category: string;
}

interface PasswordPolicy {
  min_length: number;
  max_length: number;
  require_uppercase: boolean;
  require_lowercase: boolean;
  require_numbers: boolean;
  require_special_chars: boolean;
  max_age_days: number;
}

interface SecurityOverview {
  security_score: number;
  recommendations: string[];
}

export function SecuritySettings() {
  const [settings, setSettings] = useState<SecuritySetting[]>([]);
  const [passwordPolicy, setPasswordPolicy] = useState<PasswordPolicy | null>(null);
  const [securityOverview, setSecurityOverview] = useState<SecurityOverview | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Default organization ID - in a real app, this would come from auth context
  const orgId = 'default';

  useEffect(() => {
    const fetchSecurityData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [overviewRes, passwordPolicyRes, rateLimitsRes, ipRulesRes, sessionConfigRes] = await Promise.all([
          securityControlsApi.getSecurityOverview(orgId).catch(() => null),
          securityControlsApi.getPasswordPolicy(orgId).catch(() => null),
          securityControlsApi.listRateLimitRules().catch(() => ({ data: [] })),
          securityControlsApi.listIPRules().catch(() => ({ data: [] })),
          securityControlsApi.getSessionConfig(orgId).catch(() => null),
        ]);

        // Build settings from API responses
        const fetchedSettings: SecuritySetting[] = [];

        // Session settings
        if (sessionConfigRes?.data) {
          const sessionConfig = sessionConfigRes.data;
          fetchedSettings.push({
            id: 'session-timeout',
            name: 'Session Timeout',
            description: `Auto-logout after ${sessionConfig.session_timeout_minutes || 30} minutes of inactivity`,
            enabled: sessionConfig.session_timeout_minutes > 0,
            category: 'authentication',
          });
          fetchedSettings.push({
            id: 'mfa-new-device',
            name: 'Two-Factor Authentication',
            description: 'Require MFA for new device logins',
            enabled: sessionConfig.require_mfa_for_new_device || false,
            category: 'authentication',
          });
          fetchedSettings.push({
            id: 'bind-to-ip',
            name: 'IP Binding',
            description: 'Bind sessions to IP addresses',
            enabled: sessionConfig.bind_to_ip || false,
            category: 'access',
          });
        }

        // Rate limiting
        const rateLimits = rateLimitsRes?.data || [];
        fetchedSettings.push({
          id: 'rate-limiting',
          name: 'API Rate Limiting',
          description: `${rateLimits.length} rate limit rules configured`,
          enabled: rateLimits.some((r: { enabled?: boolean }) => r.enabled),
          category: 'api',
        });

        // IP Rules
        const ipRules = ipRulesRes?.data || [];
        fetchedSettings.push({
          id: 'ip-whitelisting',
          name: 'IP Whitelisting',
          description: `${ipRules.length} IP rules configured`,
          enabled: ipRules.length > 0,
          category: 'access',
        });

        // Password policy settings
        if (passwordPolicyRes?.data) {
          setPasswordPolicy(passwordPolicyRes.data);
          fetchedSettings.push({
            id: 'password-complexity',
            name: 'Password Complexity',
            description: 'Enforce strong password requirements',
            enabled: passwordPolicyRes.data.require_uppercase || passwordPolicyRes.data.require_numbers,
            category: 'authentication',
          });
        }

        // Default settings that are always present
        fetchedSettings.push({
          id: 'audit-logging',
          name: 'Audit Logging',
          description: 'Log all user actions',
          enabled: true,
          category: 'monitoring',
        });
        fetchedSettings.push({
          id: 'data-encryption',
          name: 'Data Encryption at Rest',
          description: 'Encrypt stored data',
          enabled: true,
          category: 'data',
        });
        fetchedSettings.push({
          id: 'sso-saml',
          name: 'SSO/SAML',
          description: 'Single sign-on integration',
          enabled: false,
          category: 'authentication',
        });

        setSettings(fetchedSettings);

        // Security overview
        if (overviewRes?.data) {
          setSecurityOverview(overviewRes.data);
        }
      } catch (err) {
        console.error('Failed to fetch security settings:', err);
        setError('Failed to load security settings. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchSecurityData();
  }, [orgId]);

  const toggleSetting = (id: string) => {
    setSettings(settings.map(s =>
      s.id === id ? { ...s, enabled: !s.enabled } : s
    ));
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      // Save password policy if changed
      if (passwordPolicy) {
        await securityControlsApi.updatePasswordPolicy(orgId, passwordPolicy);
      }
      setHasChanges(false);
    } catch (err) {
      console.error('Failed to save settings:', err);
      setError('Failed to save settings. Please try again.');
    }
  };

  const categories = [...new Set(settings.map(s => s.category))];

  const securityScore = securityOverview?.security_score ?? Math.round((settings.filter(s => s.enabled).length / Math.max(settings.length, 1)) * 100);

  if (loading) {
    return (
      <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading security settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Security Settings
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Configure security controls for your workspace
              </p>
            </div>
            <button
              onClick={handleSave}
              disabled={!hasChanges}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Changes
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" />
            <p className="text-red-700 dark:text-red-300">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Security Score */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <Shield className="w-8 h-8 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Security Score</h3>
                <p className="text-sm text-gray-500">Based on enabled security features</p>
              </div>
            </div>
            <div className="text-right">
              <div className={`text-4xl font-bold ${securityScore >= 70 ? 'text-green-600' : securityScore >= 40 ? 'text-yellow-600' : 'text-red-600'}`}>{securityScore}</div>
              <div className="text-sm text-gray-500">out of 100</div>
            </div>
          </div>
          <div className="mt-4 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div className={`h-2 rounded-full ${securityScore >= 70 ? 'bg-green-500' : securityScore >= 40 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${securityScore}%` }} />
          </div>
        </div>

        {/* Settings by Category */}
        {categories.map((category) => (
          <div key={category} className="bg-white dark:bg-gray-800 rounded-lg shadow mb-6">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white capitalize">
                {category}
              </h3>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {settings.filter(s => s.category === category).map((setting) => (
                <div key={setting.id} className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${
                      setting.enabled
                        ? 'bg-green-100 dark:bg-green-900/30'
                        : 'bg-gray-100 dark:bg-gray-700'
                    }`}>
                      {setting.enabled
                        ? <CheckCircle className="w-5 h-5 text-green-600" />
                        : <AlertTriangle className="w-5 h-5 text-gray-400" />
                      }
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{setting.name}</div>
                      <div className="text-sm text-gray-500">{setting.description}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => toggleSetting(setting.id)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        setting.enabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          setting.enabled ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                    <button className="p-1 text-gray-400 hover:text-gray-600">
                      <Settings className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* Password Policy */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Key className="w-5 h-5" />
            Password Policy
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Minimum Length
              </label>
              <input
                type="number"
                value={passwordPolicy?.min_length ?? 8}
                onChange={(e) => {
                  setPasswordPolicy(prev => prev ? { ...prev, min_length: parseInt(e.target.value) || 8 } : null);
                  setHasChanges(true);
                }}
                min={6}
                max={32}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Password Expiry (days)
              </label>
              <input
                type="number"
                value={passwordPolicy?.max_age_days ?? 90}
                onChange={(e) => {
                  setPasswordPolicy(prev => prev ? { ...prev, max_age_days: parseInt(e.target.value) || 90 } : null);
                  setHasChanges(true);
                }}
                min={0}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
          </div>
          <div className="mt-4 space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={passwordPolicy?.require_uppercase ?? true}
                onChange={(e) => {
                  setPasswordPolicy(prev => prev ? { ...prev, require_uppercase: e.target.checked } : null);
                  setHasChanges(true);
                }}
                className="rounded"
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">Require uppercase letter</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={passwordPolicy?.require_lowercase ?? true}
                onChange={(e) => {
                  setPasswordPolicy(prev => prev ? { ...prev, require_lowercase: e.target.checked } : null);
                  setHasChanges(true);
                }}
                className="rounded"
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">Require lowercase letter</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={passwordPolicy?.require_numbers ?? true}
                onChange={(e) => {
                  setPasswordPolicy(prev => prev ? { ...prev, require_numbers: e.target.checked } : null);
                  setHasChanges(true);
                }}
                className="rounded"
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">Require number</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={passwordPolicy?.require_special_chars ?? false}
                onChange={(e) => {
                  setPasswordPolicy(prev => prev ? { ...prev, require_special_chars: e.target.checked } : null);
                  setHasChanges(true);
                }}
                className="rounded"
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">Require special character</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SecuritySettings;
