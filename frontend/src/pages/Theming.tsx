/**
 * Theming Page
 *
 * Customize appearance and branding.
 */

import { useState } from 'react';
import {
  Palette,
  Sun,
  Moon,
  Monitor,
  Type,
  Image,
  Save,
  RotateCcw,
} from 'lucide-react';

interface ThemeSettings {
  colorMode: 'light' | 'dark' | 'auto';
  primaryColor: string;
  accentColor: string;
  fontFamily: string;
  borderRadius: number;
  logoUrl: string;
}

const defaultTheme: ThemeSettings = {
  colorMode: 'auto',
  primaryColor: '#3B82F6',
  accentColor: '#8B5CF6',
  fontFamily: 'Inter',
  borderRadius: 8,
  logoUrl: '',
};

const colorPresets = [
  { name: 'Blue', primary: '#3B82F6', accent: '#6366F1' },
  { name: 'Green', primary: '#10B981', accent: '#14B8A6' },
  { name: 'Purple', primary: '#8B5CF6', accent: '#A855F7' },
  { name: 'Rose', primary: '#F43F5E', accent: '#EC4899' },
  { name: 'Orange', primary: '#F97316', accent: '#EAB308' },
];

const fonts = ['Inter', 'Roboto', 'Open Sans', 'Lato', 'Poppins'];

export function Theming() {
  const [theme, setTheme] = useState<ThemeSettings>(defaultTheme);
  const [hasChanges, setHasChanges] = useState(false);

  const updateTheme = (updates: Partial<ThemeSettings>) => {
    setTheme({ ...theme, ...updates });
    setHasChanges(true);
  };

  const handleSave = () => {
    setHasChanges(false);
    // Save theme settings
  };

  const handleReset = () => {
    setTheme(defaultTheme);
    setHasChanges(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Theming & Appearance
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Customize the look and feel of your workspace
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleReset}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
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
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Color Mode */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Monitor className="w-5 h-5" />
              Color Mode
            </h3>
            <div className="grid grid-cols-3 gap-4">
              {[
                { value: 'light', icon: Sun, label: 'Light' },
                { value: 'dark', icon: Moon, label: 'Dark' },
                { value: 'auto', icon: Monitor, label: 'System' },
              ].map(({ value, icon: Icon, label }) => (
                <button
                  key={value}
                  onClick={() => updateTheme({ colorMode: value as ThemeSettings['colorMode'] })}
                  className={`p-4 border rounded-lg flex flex-col items-center gap-2 ${
                    theme.colorMode === value
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700'
                  }`}
                >
                  <Icon className={`w-6 h-6 ${theme.colorMode === value ? 'text-blue-600' : 'text-gray-400'}`} />
                  <span className={theme.colorMode === value ? 'text-blue-600' : 'text-gray-600 dark:text-gray-400'}>
                    {label}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Color Presets */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Palette className="w-5 h-5" />
              Color Preset
            </h3>
            <div className="grid grid-cols-5 gap-3">
              {colorPresets.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => updateTheme({ primaryColor: preset.primary, accentColor: preset.accent })}
                  className={`p-3 border rounded-lg flex flex-col items-center gap-2 ${
                    theme.primaryColor === preset.primary
                      ? 'border-gray-900 dark:border-white'
                      : 'border-gray-200 dark:border-gray-700'
                  }`}
                >
                  <div className="flex gap-1">
                    <div className="w-4 h-4 rounded-full" style={{ backgroundColor: preset.primary }} />
                    <div className="w-4 h-4 rounded-full" style={{ backgroundColor: preset.accent }} />
                  </div>
                  <span className="text-xs text-gray-600 dark:text-gray-400">{preset.name}</span>
                </button>
              ))}
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Primary Color
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={theme.primaryColor}
                    onChange={(e) => updateTheme({ primaryColor: e.target.value })}
                    className="w-10 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={theme.primaryColor}
                    onChange={(e) => updateTheme({ primaryColor: e.target.value })}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Accent Color
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={theme.accentColor}
                    onChange={(e) => updateTheme({ accentColor: e.target.value })}
                    className="w-10 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={theme.accentColor}
                    onChange={(e) => updateTheme({ accentColor: e.target.value })}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Typography */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Type className="w-5 h-5" />
              Typography
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Font Family
              </label>
              <select
                value={theme.fontFamily}
                onChange={(e) => updateTheme({ fontFamily: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                {fonts.map((font) => (
                  <option key={font} value={font}>{font}</option>
                ))}
              </select>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Border Radius: {theme.borderRadius}px
              </label>
              <input
                type="range"
                min="0"
                max="24"
                value={theme.borderRadius}
                onChange={(e) => updateTheme({ borderRadius: parseInt(e.target.value) })}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>Square</span>
                <span>Rounded</span>
              </div>
            </div>
          </div>

          {/* Branding */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Image className="w-5 h-5" />
              Branding
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Logo URL
              </label>
              <input
                type="text"
                placeholder="https://example.com/logo.png"
                value={theme.logoUrl}
                onChange={(e) => updateTheme({ logoUrl: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div className="mt-4 p-4 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-center">
              <Image className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500">
                Drag and drop your logo here, or click to browse
              </p>
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Preview</h3>
          <div className="p-6 border border-gray-200 dark:border-gray-700 rounded-lg" style={{ fontFamily: theme.fontFamily }}>
            <div className="flex gap-4">
              <button
                className="px-4 py-2 text-white rounded"
                style={{ backgroundColor: theme.primaryColor, borderRadius: theme.borderRadius }}
              >
                Primary Button
              </button>
              <button
                className="px-4 py-2 text-white rounded"
                style={{ backgroundColor: theme.accentColor, borderRadius: theme.borderRadius }}
              >
                Accent Button
              </button>
              <button
                className="px-4 py-2 border border-gray-300 rounded"
                style={{ borderRadius: theme.borderRadius }}
              >
                Secondary Button
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Theming;
