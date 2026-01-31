/**
 * Theming & White-Label Types
 *
 * TypeScript types for themes, branding, CSS generation, and white-label configuration.
 */

// Enums

export enum ThemeMode {
  LIGHT = 'light',
  DARK = 'dark',
  AUTO = 'auto',
}

export enum ThemeScope {
  GLOBAL = 'global',
  WORKSPACE = 'workspace',
  USER = 'user',
  EMBED = 'embed',
}

export enum ComponentType {
  BUTTON = 'button',
  INPUT = 'input',
  CARD = 'card',
  TABLE = 'table',
  CHART = 'chart',
  SIDEBAR = 'sidebar',
  HEADER = 'header',
  MODAL = 'modal',
  TOOLTIP = 'tooltip',
  BADGE = 'badge',
  ALERT = 'alert',
  DROPDOWN = 'dropdown',
}

export enum FontWeight {
  THIN = '100',
  LIGHT = '300',
  REGULAR = '400',
  MEDIUM = '500',
  SEMIBOLD = '600',
  BOLD = '700',
  EXTRABOLD = '800',
}

// Color Models

export interface ColorPalette {
  // Primary colors
  primary: string;
  primary_hover: string;
  primary_foreground: string;

  // Secondary colors
  secondary: string;
  secondary_hover: string;
  secondary_foreground: string;

  // Accent colors
  accent: string;
  accent_hover: string;
  accent_foreground: string;

  // Background colors
  background: string;
  background_secondary: string;
  background_tertiary: string;

  // Foreground/text colors
  foreground: string;
  foreground_secondary: string;
  foreground_muted: string;

  // Border colors
  border: string;
  border_focus: string;

  // Status colors
  success: string;
  success_foreground: string;
  warning: string;
  warning_foreground: string;
  error: string;
  error_foreground: string;
  info: string;
  info_foreground: string;

  // Chart colors
  chart_colors: string[];
}

// Typography Models

export interface Typography {
  font_sans: string;
  font_mono: string;
  font_heading?: string | null;

  size_xs: string;
  size_sm: string;
  size_base: string;
  size_lg: string;
  size_xl: string;
  size_2xl: string;
  size_3xl: string;
  size_4xl: string;

  line_tight: string;
  line_normal: string;
  line_relaxed: string;

  tracking_tight: string;
  tracking_normal: string;
  tracking_wide: string;

  weight_light: string;
  weight_normal: string;
  weight_medium: string;
  weight_semibold: string;
  weight_bold: string;
}

// Layout Models

export interface Spacing {
  base: string;
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  xxl: string;
}

export interface BorderRadius {
  none: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  full: string;
}

export interface Shadow {
  sm: string;
  md: string;
  lg: string;
  xl: string;
}

// Component Style

export interface ComponentStyle {
  component: ComponentType;
  styles: Record<string, string>;
  variants: Record<string, Record<string, string>>;
}

// Theme Models

export interface Theme {
  id: string;
  name: string;
  description?: string | null;
  mode: ThemeMode;
  scope: ThemeScope;

  colors: ColorPalette;
  dark_colors?: ColorPalette | null;

  typography: Typography;
  spacing: Spacing;
  border_radius: BorderRadius;
  shadows: Shadow;

  components: ComponentStyle[];
  custom_css?: string | null;

  is_default: boolean;
  is_system: boolean;
  created_by?: string | null;
  workspace_id?: string | null;
  created_at: string;
  updated_at?: string | null;

  preview_image?: string | null;
}

export interface ThemeCreate {
  name: string;
  description?: string | null;
  mode?: ThemeMode;
  scope?: ThemeScope;
  colors?: Partial<ColorPalette>;
  dark_colors?: Partial<ColorPalette>;
  typography?: Partial<Typography>;
  spacing?: Partial<Spacing>;
  border_radius?: Partial<BorderRadius>;
  shadows?: Partial<Shadow>;
  components?: ComponentStyle[];
  custom_css?: string;
  workspace_id?: string;
}

export interface ThemeUpdate {
  name?: string;
  description?: string | null;
  mode?: ThemeMode;
  colors?: Partial<ColorPalette>;
  dark_colors?: Partial<ColorPalette>;
  typography?: Partial<Typography>;
  spacing?: Partial<Spacing>;
  border_radius?: Partial<BorderRadius>;
  shadows?: Partial<Shadow>;
  components?: ComponentStyle[];
  custom_css?: string;
  is_default?: boolean;
}

// Branding Models

export interface Logo {
  light_url?: string | null;
  dark_url?: string | null;
  favicon_url?: string | null;
  width: number;
  height: number;
}

export interface Branding {
  id: string;
  workspace_id: string;

  company_name: string;
  tagline?: string | null;
  support_email?: string | null;
  support_url?: string | null;

  logo: Logo;

  primary_color: string;
  secondary_color: string;

  custom_domain?: string | null;
  custom_domain_verified: boolean;

  footer_text?: string | null;
  footer_links: Array<Record<string, string>>;

  privacy_policy_url?: string | null;
  terms_of_service_url?: string | null;

  social_links: Record<string, string>;

  email_from_name?: string | null;
  email_from_address?: string | null;

  hide_powered_by: boolean;
  custom_login_page: boolean;
  custom_error_pages: boolean;

  theme_id?: string | null;

  created_at: string;
  updated_at?: string | null;
}

export interface BrandingCreate {
  workspace_id: string;
  company_name: string;
  tagline?: string;
  primary_color?: string;
  secondary_color?: string;
  logo?: Logo;
}

export interface BrandingUpdate {
  company_name?: string;
  tagline?: string;
  support_email?: string;
  support_url?: string;
  logo?: Logo;
  primary_color?: string;
  secondary_color?: string;
  custom_domain?: string;
  footer_text?: string;
  footer_links?: Array<Record<string, string>>;
  privacy_policy_url?: string;
  terms_of_service_url?: string;
  social_links?: Record<string, string>;
  email_from_name?: string;
  email_from_address?: string;
  hide_powered_by?: boolean;
  theme_id?: string;
}

// User Preferences

export interface UserThemePreferences {
  user_id: string;
  theme_mode: ThemeMode;
  preferred_theme_id?: string | null;
  font_size: string;
  reduce_motion: boolean;
  high_contrast: boolean;
  custom_overrides: Record<string, string>;
  updated_at: string;
}

// CSS Generation

export interface CSSVariables {
  variables: Record<string, string>;
  scope: string;
}

export interface GeneratedCSS {
  css: string;
  variables: CSSVariables;
  minified: boolean;
  hash: string;
}

// Response Models

export interface ThemeListResponse {
  themes: Theme[];
  total: number;
}

export interface ThemePreviewResponse {
  theme: Theme;
  css: GeneratedCSS;
  preview_components: Record<string, string>;
}

export interface PresetTheme {
  id: string;
  name: string;
  primary: string;
  secondary: string;
  accent: string;
}

// Constants

export const DEFAULT_COLORS: ColorPalette = {
  primary: '#3B82F6',
  primary_hover: '#2563EB',
  primary_foreground: '#FFFFFF',
  secondary: '#6B7280',
  secondary_hover: '#4B5563',
  secondary_foreground: '#FFFFFF',
  accent: '#8B5CF6',
  accent_hover: '#7C3AED',
  accent_foreground: '#FFFFFF',
  background: '#FFFFFF',
  background_secondary: '#F9FAFB',
  background_tertiary: '#F3F4F6',
  foreground: '#111827',
  foreground_secondary: '#6B7280',
  foreground_muted: '#9CA3AF',
  border: '#E5E7EB',
  border_focus: '#3B82F6',
  success: '#10B981',
  success_foreground: '#FFFFFF',
  warning: '#F59E0B',
  warning_foreground: '#000000',
  error: '#EF4444',
  error_foreground: '#FFFFFF',
  info: '#3B82F6',
  info_foreground: '#FFFFFF',
  chart_colors: [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1',
  ],
};

export const DARK_COLORS: ColorPalette = {
  ...DEFAULT_COLORS,
  primary: '#60A5FA',
  primary_hover: '#3B82F6',
  background: '#111827',
  background_secondary: '#1F2937',
  background_tertiary: '#374151',
  foreground: '#F9FAFB',
  foreground_secondary: '#D1D5DB',
  foreground_muted: '#9CA3AF',
  border: '#374151',
};

export const THEME_MODE_LABELS: Record<ThemeMode, string> = {
  [ThemeMode.LIGHT]: 'Light',
  [ThemeMode.DARK]: 'Dark',
  [ThemeMode.AUTO]: 'Auto (System)',
};

export const THEME_SCOPE_LABELS: Record<ThemeScope, string> = {
  [ThemeScope.GLOBAL]: 'Global',
  [ThemeScope.WORKSPACE]: 'Workspace',
  [ThemeScope.USER]: 'User',
  [ThemeScope.EMBED]: 'Embedded',
};

export const COMPONENT_TYPE_LABELS: Record<ComponentType, string> = {
  [ComponentType.BUTTON]: 'Button',
  [ComponentType.INPUT]: 'Input',
  [ComponentType.CARD]: 'Card',
  [ComponentType.TABLE]: 'Table',
  [ComponentType.CHART]: 'Chart',
  [ComponentType.SIDEBAR]: 'Sidebar',
  [ComponentType.HEADER]: 'Header',
  [ComponentType.MODAL]: 'Modal',
  [ComponentType.TOOLTIP]: 'Tooltip',
  [ComponentType.BADGE]: 'Badge',
  [ComponentType.ALERT]: 'Alert',
  [ComponentType.DROPDOWN]: 'Dropdown',
};

export const FONT_SIZE_OPTIONS = [
  { value: 'small', label: 'Small' },
  { value: 'medium', label: 'Medium' },
  { value: 'large', label: 'Large' },
];

export const PRESET_THEMES: Record<string, PresetTheme> = {
  ocean: {
    id: 'ocean',
    name: 'Ocean',
    primary: '#0891B2',
    secondary: '#0E7490',
    accent: '#06B6D4',
  },
  forest: {
    id: 'forest',
    name: 'Forest',
    primary: '#059669',
    secondary: '#047857',
    accent: '#10B981',
  },
  sunset: {
    id: 'sunset',
    name: 'Sunset',
    primary: '#EA580C',
    secondary: '#C2410C',
    accent: '#F97316',
  },
  berry: {
    id: 'berry',
    name: 'Berry',
    primary: '#BE185D',
    secondary: '#9D174D',
    accent: '#EC4899',
  },
  slate: {
    id: 'slate',
    name: 'Slate',
    primary: '#475569',
    secondary: '#334155',
    accent: '#64748B',
  },
};

// Helper Functions

export function isLightMode(mode: ThemeMode): boolean {
  if (mode === ThemeMode.LIGHT) return true;
  if (mode === ThemeMode.DARK) return false;
  // AUTO mode - check system preference
  return !window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

export function getEffectiveColors(theme: Theme): ColorPalette {
  if (theme.mode === ThemeMode.DARK && theme.dark_colors) {
    return theme.dark_colors;
  }
  if (theme.mode === ThemeMode.AUTO) {
    const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
    if (prefersDark && theme.dark_colors) {
      return theme.dark_colors;
    }
  }
  return theme.colors;
}

export function validateHexColor(color: string): boolean {
  return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color);
}

export function lightenColor(hexColor: string, percent: number): string {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);

  const newR = Math.min(255, Math.round(r + (255 - r) * percent));
  const newG = Math.min(255, Math.round(g + (255 - g) * percent));
  const newB = Math.min(255, Math.round(b + (255 - b) * percent));

  return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
}

export function darkenColor(hexColor: string, percent: number): string {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);

  const newR = Math.max(0, Math.round(r * (1 - percent)));
  const newG = Math.max(0, Math.round(g * (1 - percent)));
  const newB = Math.max(0, Math.round(b * (1 - percent)));

  return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
}

export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

export function rgbToHex(r: number, g: number, b: number): string {
  return `#${[r, g, b].map((x) => x.toString(16).padStart(2, '0')).join('')}`;
}

export function getContrastColor(hexColor: string): string {
  const rgb = hexToRgb(hexColor);
  if (!rgb) return '#000000';

  // Calculate relative luminance
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

export function generateColorPalette(primaryColor: string): Partial<ColorPalette> {
  return {
    primary: primaryColor,
    primary_hover: darkenColor(primaryColor, 0.1),
    primary_foreground: getContrastColor(primaryColor),
    accent: lightenColor(primaryColor, 0.2),
    accent_hover: primaryColor,
    accent_foreground: getContrastColor(lightenColor(primaryColor, 0.2)),
    border_focus: primaryColor,
    info: primaryColor,
    info_foreground: getContrastColor(primaryColor),
  };
}

export function cssVariablesToObject(cssText: string): Record<string, string> {
  const variables: Record<string, string> = {};
  const regex = /--([a-zA-Z0-9-]+):\s*([^;]+);/g;
  let match;

  while ((match = regex.exec(cssText)) !== null) {
    variables[`--${match[1]}`] = match[2].trim();
  }

  return variables;
}

export function objectToCSSVariables(
  variables: Record<string, string>,
  scope = ':root'
): string {
  const entries = Object.entries(variables)
    .map(([key, value]) => `  ${key}: ${value};`)
    .join('\n');

  return `${scope} {\n${entries}\n}`;
}

// Theme State Management

export interface ThemingState {
  themes: Theme[];
  activeTheme: Theme | null;
  presets: PresetTheme[];
  branding: Branding | null;
  userPreferences: UserThemePreferences | null;
  isLoading: boolean;
  error: string | null;
  selectedThemeId: string | null;
  previewMode: boolean;
  editingTheme: Theme | null;
}

export function createInitialThemingState(): ThemingState {
  return {
    themes: [],
    activeTheme: null,
    presets: Object.values(PRESET_THEMES),
    branding: null,
    userPreferences: null,
    isLoading: false,
    error: null,
    selectedThemeId: null,
    previewMode: false,
    editingTheme: null,
  };
}

// CSS Application Helpers

export function applyThemeToDocument(theme: Theme): void {
  const colors = getEffectiveColors(theme);
  const root = document.documentElement;

  // Apply color variables
  Object.entries(colors).forEach(([key, value]) => {
    if (key !== 'chart_colors' && typeof value === 'string') {
      root.style.setProperty(`--color-${key.replace(/_/g, '-')}`, value);
    }
  });

  // Apply chart colors
  if (colors.chart_colors) {
    colors.chart_colors.forEach((color, index) => {
      root.style.setProperty(`--chart-color-${index + 1}`, color);
    });
  }

  // Apply typography
  const { typography } = theme;
  root.style.setProperty('--font-sans', typography.font_sans);
  root.style.setProperty('--font-mono', typography.font_mono);
  if (typography.font_heading) {
    root.style.setProperty('--font-heading', typography.font_heading);
  }

  // Apply spacing
  const { spacing } = theme;
  Object.entries(spacing).forEach(([key, value]) => {
    root.style.setProperty(`--spacing-${key}`, value);
  });

  // Apply border radius
  const { border_radius } = theme;
  Object.entries(border_radius).forEach(([key, value]) => {
    root.style.setProperty(`--radius-${key}`, value);
  });

  // Apply shadows
  const { shadows } = theme;
  Object.entries(shadows).forEach(([key, value]) => {
    root.style.setProperty(`--shadow-${key}`, value);
  });

  // Apply custom CSS if present
  if (theme.custom_css) {
    let customStyleEl = document.getElementById('theme-custom-css');
    if (!customStyleEl) {
      customStyleEl = document.createElement('style');
      customStyleEl.id = 'theme-custom-css';
      document.head.appendChild(customStyleEl);
    }
    customStyleEl.textContent = theme.custom_css;
  }

  // Set theme mode attribute
  root.setAttribute('data-theme', theme.mode);
  if (theme.mode === ThemeMode.DARK) {
    root.classList.add('dark');
  } else if (theme.mode === ThemeMode.LIGHT) {
    root.classList.remove('dark');
  } else {
    // AUTO mode
    const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
    root.classList.toggle('dark', prefersDark);
  }
}

export function removeThemeFromDocument(): void {
  const root = document.documentElement;

  // Remove custom style element
  const customStyleEl = document.getElementById('theme-custom-css');
  if (customStyleEl) {
    customStyleEl.remove();
  }

  // Reset theme attribute
  root.removeAttribute('data-theme');
}
