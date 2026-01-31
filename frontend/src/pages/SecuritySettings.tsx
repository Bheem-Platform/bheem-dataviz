/**
 * Security Settings Page
 *
 * Security controls and configuration.
 */

import { useState } from 'react';
import {
  Shield,
  Key,
  Lock,
  Eye,
  EyeOff,
  AlertTriangle,
  CheckCircle,
  Settings,
  Save,
} from 'lucide-react';

interface SecuritySetting {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  category: string;
}

const mockSettings: SecuritySetting[] = [
  { id: '1', name: 'Two-Factor Authentication', description: 'Require 2FA for all users', enabled: true, category: 'authentication' },
  { id: '2', name: 'Session Timeout', description: 'Auto-logout after 30 minutes of inactivity', enabled: true, category: 'authentication' },
  { id: '3', name: 'IP Whitelisting', description: 'Restrict access to specific IP addresses', enabled: false, category: 'access' },
  { id: '4', name: 'API Rate Limiting', description: 'Limit API requests per minute', enabled: true, category: 'api' },
  { id: '5', name: 'Audit Logging', description: 'Log all user actions', enabled: true, category: 'monitoring' },
  { id: '6', name: 'Data Encryption at Rest', description: 'Encrypt stored data', enabled: true, category: 'data' },
  { id: '7', name: 'Password Complexity', description: 'Enforce strong password requirements', enabled: true, category: 'authentication' },
  { id: '8', name: 'SSO/SAML', description: 'Single sign-on integration', enabled: false, category: 'authentication' },
];

export function SecuritySettings() {
  const [settings, setSettings] = useState<SecuritySetting[]>(mockSettings);
  const [hasChanges, setHasChanges] = useState(false);

  const toggleSetting = (id: string) => {
    setSettings(settings.map(s =>
      s.id === id ? { ...s, enabled: !s.enabled } : s
    ));
    setHasChanges(true);
  };

  const handleSave = () => {
    setHasChanges(false);
    // Save settings
  };

  const categories = [...new Set(settings.map(s => s.category))];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
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
              <div className="text-4xl font-bold text-green-600">85</div>
              <div className="text-sm text-gray-500">out of 100</div>
            </div>
          </div>
          <div className="mt-4 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }} />
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
                defaultValue={8}
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
                defaultValue={90}
                min={0}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
          </div>
          <div className="mt-4 space-y-2">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Require uppercase letter</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Require lowercase letter</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Require number</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" className="rounded" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Require special character</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SecuritySettings;
