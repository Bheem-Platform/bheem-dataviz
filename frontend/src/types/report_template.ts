/**
 * Report Templates Types
 *
 * TypeScript types for report template management including
 * layouts, placeholders, styles, themes, and versioning.
 */

// Enums

export enum TemplateType {
  DASHBOARD = 'dashboard',
  CHART = 'chart',
  DATA_TABLE = 'data_table',
  KPI = 'kpi',
  MIXED = 'mixed',
  CUSTOM = 'custom',
}

export enum TemplateStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
  DEPRECATED = 'deprecated',
}

export enum PlaceholderType {
  TEXT = 'text',
  IMAGE = 'image',
  CHART = 'chart',
  TABLE = 'table',
  KPI = 'kpi',
  DATE = 'date',
  PAGE_NUMBER = 'page_number',
  FILTER = 'filter',
  LOGO = 'logo',
  CUSTOM = 'custom',
}

export enum LayoutType {
  SINGLE_COLUMN = 'single_column',
  TWO_COLUMN = 'two_column',
  THREE_COLUMN = 'three_column',
  GRID = 'grid',
  FREEFORM = 'freeform',
  MASTER_DETAIL = 'master_detail',
}

export enum PageBreakBehavior {
  AUTO = 'auto',
  BEFORE = 'before',
  AFTER = 'after',
  AVOID = 'avoid',
}

// Style Interfaces

export interface FontStyle {
  family: string;
  size: number;
  weight: string;
  style: string;
  color: string;
  line_height: number;
}

export interface BorderStyle {
  width: number;
  style: string;
  color: string;
  radius: number;
}

export interface SpacingStyle {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export interface BackgroundStyle {
  color?: string;
  image_url?: string;
  repeat: string;
  position: string;
  size: string;
}

export interface ElementStyle {
  font?: FontStyle;
  border?: BorderStyle;
  padding?: SpacingStyle;
  margin?: SpacingStyle;
  background?: BackgroundStyle;
  width?: string;
  height?: string;
  min_width?: string;
  min_height?: string;
  max_width?: string;
  max_height?: string;
  alignment: string;
  vertical_alignment: string;
}

// Placeholder Interfaces

export interface PlaceholderPosition {
  x: number;
  y: number;
  width: number;
  height: number;
  z_index: number;
  rotation: number;
}

export interface PlaceholderConfig {
  placeholder_type: PlaceholderType;
  source_id?: string;
  default_value?: string;
  format_string?: string;
  filters?: Record<string, unknown>;
  parameters?: Record<string, unknown>;
}

export interface TemplatePlaceholder {
  id: string;
  name: string;
  placeholder_type: PlaceholderType;
  position: PlaceholderPosition;
  config: PlaceholderConfig;
  style?: ElementStyle;
  required: boolean;
  editable: boolean;
  page_break: PageBreakBehavior;
}

// Section Interfaces

export interface TemplateSection {
  id: string;
  name: string;
  title?: string;
  description?: string;
  layout: LayoutType;
  placeholders: TemplatePlaceholder[];
  style?: ElementStyle;
  page_break: PageBreakBehavior;
  repeat_for_data: boolean;
  data_source?: string;
  visible: boolean;
  order: number;
}

// Page Interfaces

export interface PageMargins {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export interface PageConfig {
  size: string;
  orientation: string;
  margins: PageMargins;
  background?: BackgroundStyle;
}

export interface TemplatePage {
  id: string;
  name: string;
  page_number: number;
  config: PageConfig;
  header?: TemplateSection;
  footer?: TemplateSection;
  sections: TemplateSection[];
}

// Theme Interfaces

export interface TemplateColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text_primary: string;
  text_secondary: string;
  border: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface TemplateTypography {
  title: FontStyle;
  subtitle: FontStyle;
  heading: FontStyle;
  body: FontStyle;
  caption: FontStyle;
  label: FontStyle;
}

export interface TemplateTheme {
  name: string;
  colors: TemplateColorPalette;
  typography: TemplateTypography;
  chart_colors: string[];
  border_radius: number;
  shadow: string;
}

// Template Interfaces

export interface ReportTemplate {
  id: string;
  name: string;
  description?: string;
  template_type: TemplateType;
  category?: string;
  tags: string[];
  user_id: string;
  organization_id?: string;
  status: TemplateStatus;
  version: number;
  pages: TemplatePage[];
  theme: TemplateTheme;
  default_filters: Record<string, unknown>;
  default_parameters: Record<string, unknown>;
  is_public: boolean;
  is_system: boolean;
  thumbnail_url?: string;
  preview_url?: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export interface ReportTemplateCreate {
  name: string;
  description?: string;
  template_type: TemplateType;
  category?: string;
  tags?: string[];
  pages?: TemplatePage[];
  theme?: TemplateTheme;
  default_filters?: Record<string, unknown>;
  default_parameters?: Record<string, unknown>;
  is_public?: boolean;
}

export interface ReportTemplateUpdate {
  name?: string;
  description?: string;
  category?: string;
  tags?: string[];
  pages?: TemplatePage[];
  theme?: TemplateTheme;
  default_filters?: Record<string, unknown>;
  default_parameters?: Record<string, unknown>;
  status?: TemplateStatus;
  is_public?: boolean;
}

export interface ReportTemplateListResponse {
  templates: ReportTemplate[];
  total: number;
}

// Version Interfaces

export interface TemplateVersion {
  id: string;
  template_id: string;
  version: number;
  name: string;
  description?: string;
  pages: TemplatePage[];
  theme: TemplateTheme;
  change_summary?: string;
  created_by: string;
  created_at: string;
}

export interface TemplateVersionListResponse {
  versions: TemplateVersion[];
  total: number;
}

// Category Interfaces

export interface TemplateCategory {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  parent_id?: string;
  order: number;
  template_count: number;
}

export interface TemplateCategoryCreate {
  name: string;
  description?: string;
  icon?: string;
  parent_id?: string;
  order?: number;
}

export interface TemplateCategoryListResponse {
  categories: TemplateCategory[];
  total: number;
}

// Instance Interfaces

export interface TemplateInstance {
  id: string;
  template_id: string;
  template_version: number;
  name: string;
  user_id: string;
  organization_id?: string;
  placeholder_values: Record<string, unknown>;
  filters: Record<string, unknown>;
  parameters: Record<string, unknown>;
  generated_at?: string;
  file_url?: string;
  file_format?: string;
  created_at: string;
  updated_at: string;
}

export interface TemplateInstanceCreate {
  template_id: string;
  name: string;
  placeholder_values?: Record<string, unknown>;
  filters?: Record<string, unknown>;
  parameters?: Record<string, unknown>;
}

export interface TemplateInstanceListResponse {
  instances: TemplateInstance[];
  total: number;
}

// Constants

export const TEMPLATE_TYPE_LABELS: Record<TemplateType, string> = {
  [TemplateType.DASHBOARD]: 'Dashboard Report',
  [TemplateType.CHART]: 'Chart Report',
  [TemplateType.DATA_TABLE]: 'Data Table Report',
  [TemplateType.KPI]: 'KPI Report',
  [TemplateType.MIXED]: 'Mixed Report',
  [TemplateType.CUSTOM]: 'Custom Report',
};

export const TEMPLATE_STATUS_LABELS: Record<TemplateStatus, string> = {
  [TemplateStatus.DRAFT]: 'Draft',
  [TemplateStatus.PUBLISHED]: 'Published',
  [TemplateStatus.ARCHIVED]: 'Archived',
  [TemplateStatus.DEPRECATED]: 'Deprecated',
};

export const PLACEHOLDER_TYPE_LABELS: Record<PlaceholderType, string> = {
  [PlaceholderType.TEXT]: 'Text',
  [PlaceholderType.IMAGE]: 'Image',
  [PlaceholderType.CHART]: 'Chart',
  [PlaceholderType.TABLE]: 'Data Table',
  [PlaceholderType.KPI]: 'KPI Card',
  [PlaceholderType.DATE]: 'Date',
  [PlaceholderType.PAGE_NUMBER]: 'Page Number',
  [PlaceholderType.FILTER]: 'Filter Value',
  [PlaceholderType.LOGO]: 'Logo',
  [PlaceholderType.CUSTOM]: 'Custom',
};

export const LAYOUT_TYPE_LABELS: Record<LayoutType, string> = {
  [LayoutType.SINGLE_COLUMN]: 'Single Column',
  [LayoutType.TWO_COLUMN]: 'Two Columns',
  [LayoutType.THREE_COLUMN]: 'Three Columns',
  [LayoutType.GRID]: 'Grid',
  [LayoutType.FREEFORM]: 'Freeform',
  [LayoutType.MASTER_DETAIL]: 'Master-Detail',
};

export const TEMPLATE_STATUS_COLORS: Record<TemplateStatus, string> = {
  [TemplateStatus.DRAFT]: 'gray',
  [TemplateStatus.PUBLISHED]: 'green',
  [TemplateStatus.ARCHIVED]: 'yellow',
  [TemplateStatus.DEPRECATED]: 'red',
};

// Helper Functions

export function getDefaultFontStyle(): FontStyle {
  return {
    family: 'Arial',
    size: 12,
    weight: 'normal',
    style: 'normal',
    color: '#000000',
    line_height: 1.5,
  };
}

export function getDefaultTheme(): TemplateTheme {
  return {
    name: 'default',
    colors: {
      primary: '#3B82F6',
      secondary: '#6B7280',
      accent: '#10B981',
      background: '#FFFFFF',
      surface: '#F9FAFB',
      text_primary: '#111827',
      text_secondary: '#6B7280',
      border: '#E5E7EB',
      success: '#10B981',
      warning: '#F59E0B',
      error: '#EF4444',
      info: '#3B82F6',
    },
    typography: {
      title: { ...getDefaultFontStyle(), size: 24, weight: 'bold' },
      subtitle: { ...getDefaultFontStyle(), size: 18, weight: 'semibold' },
      heading: { ...getDefaultFontStyle(), size: 16, weight: 'semibold' },
      body: getDefaultFontStyle(),
      caption: { ...getDefaultFontStyle(), size: 10, color: '#6B7280' },
      label: { ...getDefaultFontStyle(), size: 11, weight: 'medium' },
    },
    chart_colors: [
      '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
      '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1',
    ],
    border_radius: 4,
    shadow: '0 1px 3px rgba(0,0,0,0.1)',
  };
}

export function getDefaultPageConfig(): PageConfig {
  return {
    size: 'A4',
    orientation: 'portrait',
    margins: { top: 20, right: 20, bottom: 20, left: 20 },
  };
}

export function getDefaultPlaceholderPosition(): PlaceholderPosition {
  return {
    x: 0,
    y: 0,
    width: 100,
    height: 50,
    z_index: 0,
    rotation: 0,
  };
}

export function createTextPlaceholder(
  id: string,
  name: string,
  defaultValue: string = ''
): TemplatePlaceholder {
  return {
    id,
    name,
    placeholder_type: PlaceholderType.TEXT,
    position: getDefaultPlaceholderPosition(),
    config: {
      placeholder_type: PlaceholderType.TEXT,
      default_value: defaultValue,
    },
    required: false,
    editable: true,
    page_break: PageBreakBehavior.AUTO,
  };
}

export function createChartPlaceholder(
  id: string,
  name: string,
  chartId: string
): TemplatePlaceholder {
  return {
    id,
    name,
    placeholder_type: PlaceholderType.CHART,
    position: { ...getDefaultPlaceholderPosition(), width: 400, height: 300 },
    config: {
      placeholder_type: PlaceholderType.CHART,
      source_id: chartId,
    },
    required: false,
    editable: true,
    page_break: PageBreakBehavior.AUTO,
  };
}

export function isTemplateEditable(template: ReportTemplate): boolean {
  return !template.is_system && template.status !== TemplateStatus.ARCHIVED;
}

export function isTemplateDraft(template: ReportTemplate): boolean {
  return template.status === TemplateStatus.DRAFT;
}

export function isTemplatePublished(template: ReportTemplate): boolean {
  return template.status === TemplateStatus.PUBLISHED;
}

export function canPublishTemplate(template: ReportTemplate): boolean {
  return (
    !template.is_system &&
    template.status === TemplateStatus.DRAFT &&
    template.pages.length > 0
  );
}

export function getTemplatePlaceholders(template: ReportTemplate): TemplatePlaceholder[] {
  const placeholders: TemplatePlaceholder[] = [];

  for (const page of template.pages) {
    if (page.header) {
      placeholders.push(...page.header.placeholders);
    }
    for (const section of page.sections) {
      placeholders.push(...section.placeholders);
    }
    if (page.footer) {
      placeholders.push(...page.footer.placeholders);
    }
  }

  return placeholders;
}

export function getRequiredPlaceholders(template: ReportTemplate): TemplatePlaceholder[] {
  return getTemplatePlaceholders(template).filter(p => p.required);
}

export function validatePlaceholderValues(
  template: ReportTemplate,
  values: Record<string, unknown>
): { valid: boolean; missing: string[] } {
  const required = getRequiredPlaceholders(template);
  const missing = required
    .filter(p => !(p.id in values) || values[p.id] === null || values[p.id] === undefined)
    .map(p => p.name);

  return {
    valid: missing.length === 0,
    missing,
  };
}

export function getTemplateStatusIcon(status: TemplateStatus): string {
  const icons: Record<TemplateStatus, string> = {
    [TemplateStatus.DRAFT]: 'edit',
    [TemplateStatus.PUBLISHED]: 'check-circle',
    [TemplateStatus.ARCHIVED]: 'archive',
    [TemplateStatus.DEPRECATED]: 'alert-circle',
  };
  return icons[status] || 'file';
}

export function getPlaceholderTypeIcon(type: PlaceholderType): string {
  const icons: Record<PlaceholderType, string> = {
    [PlaceholderType.TEXT]: 'type',
    [PlaceholderType.IMAGE]: 'image',
    [PlaceholderType.CHART]: 'bar-chart',
    [PlaceholderType.TABLE]: 'table',
    [PlaceholderType.KPI]: 'trending-up',
    [PlaceholderType.DATE]: 'calendar',
    [PlaceholderType.PAGE_NUMBER]: 'hash',
    [PlaceholderType.FILTER]: 'filter',
    [PlaceholderType.LOGO]: 'award',
    [PlaceholderType.CUSTOM]: 'code',
  };
  return icons[type] || 'square';
}
