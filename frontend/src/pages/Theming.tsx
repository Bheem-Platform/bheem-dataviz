/**
 * Theming Page
 *
 * Customize appearance and branding.
 */

import { useState, useEffect } from 'react';
import {
  Palette,
  Sun,
  Moon,
  Monitor,
  Type,
  Image,
  Save,
  RotateCcw,
  AlertCircle,
} from 'lucide-react';
import { themingApi } from '../lib/api';

interface ThemeSettings {
  colorMode: 'light' | 'dark' | 'auto';
  primaryColor: string;
  accentColor: string;
  fontFamily: string;
  borderRadius: number;
  logoUrl: string;
}

interface ColorPreset {
  name: string;
  primary: string;
  accent: string;
}

const defaultTheme: ThemeSettings = {
  colorMode: 'auto',
  primaryColor: '#3B82F6',
  accentColor: '#8B5CF6',
  fontFamily: 'Inter',
  borderRadius: 8,
  logoUrl: '',
};

export function Theming() {
  const [theme, setTheme] = useState<ThemeSettings>(defaultTheme);
  const [hasChanges, setHasChanges] = useState(false);
  const [colorPresets, setColorPresets] = useState<ColorPreset[]>([]);
  const [fonts, setFonts] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchThemingData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [presetsResponse, themesResponse] = await Promise.all([
          themingApi.getPresets(),
          themingApi.listThemes({ include_system: true }),
        ]);

        // Extract color presets from the API response
        if (presetsResponse.data?.presets) {
          const presets = presetsResponse.data.presets.map((preset: { name: string; colors?: { primary?: string; accent?: string } }) => ({
            name: preset.name,
            primary: preset.colors?.primary || '#3B82F6',
            accent: preset.colors?.accent || '#6366F1',
          }));
          setColorPresets(presets);
        }

        // Extract fonts from themes or use defaults
        if (themesResponse.data?.themes) {
          const extractedFonts = new Set<string>();
          themesResponse.data.themes.forEach((t: { typography?: { fontFamily?: string } }) => {
            if (t.typography?.fontFamily) {
              extractedFonts.add(t.typography.fontFamily);
            }
          });
          if (extractedFonts.size > 0) {
            setFonts(Array.from(extractedFonts));
          }
        }
      } catch (err) {
        console.error('Failed to fetch theming data:', err);
        setError('Failed to load theming data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchThemingData();
  }, []);

  const updateTheme = (updates: Partial<ThemeSettings>) => {
    setTheme({ ...theme, ...updates });
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      setError(null);
      await themingApi.createTheme({
        name: 'Custom Theme',
        mode: theme.colorMode,
        colors: {
          primary: theme.primaryColor,
          accent: theme.accentColor,
        },
        typography: {
          fontFamily: theme.fontFamily,
        },
        border_radius: {
          default: theme.borderRadius,
        },
      });
      setHasChanges(false);
    } catch (err) {
      console.error('Failed to save theme:', err);
      setError('Failed to save theme. Please try again.');
    }
  };

  const handleReset = () => {
    setTheme(defaultTheme);
    setHasChanges(false);
    setError(null);
  };

  if (loading) {
    return (
      <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading theming data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <p className="text-red-700 dark:text-red-400">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

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
