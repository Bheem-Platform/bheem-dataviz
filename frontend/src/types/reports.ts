/**
 * Reports Types
 *
 * TypeScript types for report builder and export.
 */

// Enums

export type ReportFormat = 'pdf' | 'html' | 'excel' | 'pptx' | 'image';

export type PageSize = 'a4' | 'letter' | 'legal' | 'a3' | 'tabloid';

export type PageOrientation = 'portrait' | 'landscape';

export type ElementType =
  | 'chart'
  | 'table'
  | 'text'
  | 'image'
  | 'kpi'
  | 'heading'
  | 'divider'
  | 'spacer'
  | 'page_break'
  | 'table_of_contents';

export type TextAlignment = 'left' | 'center' | 'right' | 'justify';

// Configuration Types

export interface BrandingConfig {
  logo_url?: string;
  logo_width?: number;
  logo_position?: 'left' | 'center' | 'right';
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  font_family?: string;
  header_font_family?: string;
  company_name?: string;
  footer_text?: string;
}

export interface PageMargins {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

export interface HeaderFooterConfig {
  show_header?: boolean;
  show_footer?: boolean;
  header_height?: number;
  footer_height?: number;
  include_logo?: boolean;
  include_title?: boolean;
  include_date?: boolean;
  include_page_numbers?: boolean;
  custom_header_html?: string;
  custom_footer_html?: string;
}

export interface PageConfig {
  size?: PageSize;
  orientation?: PageOrientation;
  margins?: PageMargins;
  header_footer?: HeaderFooterConfig;
}

// Element Types

export interface TextStyle {
  font_size?: number;
  font_weight?: 'normal' | 'bold';
  font_style?: 'normal' | 'italic';
  color?: string;
  alignment?: TextAlignment;
  line_height?: number;
}

export interface ChartElement {
  element_type: 'chart';
  chart_id: string;
  title?: string;
  show_title?: boolean;
  width?: string;
  height?: number;
  filters?: Record<string, unknown>;
}

export interface TableElement {
  element_type: 'table';
  data_source: string;
  query?: string;
  columns?: string[];
  title?: string;
  show_title?: boolean;
  max_rows?: number;
  show_row_numbers?: boolean;
  striped?: boolean;
  bordered?: boolean;
  compact?: boolean;
}

export interface TextElement {
  element_type: 'text';
  content: string;
  style?: TextStyle;
  markdown?: boolean;
}

export interface HeadingElement {
  element_type: 'heading';
  text: string;
  level?: number;
  style?: TextStyle;
  include_in_toc?: boolean;
}

export interface ImageElement {
  element_type: 'image';
  url: string;
  alt_text?: string;
  width?: string;
  height?: string;
  alignment?: TextAlignment;
}

export interface KPIElement {
  element_type: 'kpi';
  kpi_id?: string;
  label: string;
  value?: string | number;
  query?: string;
  format?: string;
  comparison_value?: number;
  comparison_label?: string;
  trend_direction?: 'up' | 'down' | 'neutral';
  color?: string;
}

export interface DividerElement {
  element_type: 'divider';
  style?: 'solid' | 'dashed' | 'dotted';
  color?: string;
  thickness?: number;
  margin_top?: number;
  margin_bottom?: number;
}

export interface SpacerElement {
  element_type: 'spacer';
  height?: number;
}

export interface PageBreakElement {
  element_type: 'page_break';
}

export interface TOCElement {
  element_type: 'table_of_contents';
  title?: string;
  max_depth?: number;
  show_page_numbers?: boolean;
}

export type ReportElement =
  | ChartElement
  | TableElement
  | TextElement
  | HeadingElement
  | ImageElement
  | KPIElement
  | DividerElement
  | SpacerElement
  | PageBreakElement
  | TOCElement;

// Report Section

export interface ReportSection {
  id: string;
  title?: string;
  elements: ReportElement[];
  columns?: number;
  background_color?: string;
  padding?: number;
}

// Template Types

export interface ReportTemplate {
  id: string;
  name: string;
  description?: string;
  page_config: PageConfig;
  branding: BrandingConfig;
  sections: ReportSection[];
  workspace_id?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  is_public: boolean;
  usage_count: number;
  tags: string[];
}

export interface ReportTemplateCreate {
  name: string;
  description?: string;
  page_config?: PageConfig;
  branding?: BrandingConfig;
  sections: ReportSection[];
  workspace_id?: string;
  is_public?: boolean;
  tags?: string[];
}

export interface ReportTemplateUpdate {
  name?: string;
  description?: string;
  page_config?: PageConfig;
  branding?: BrandingConfig;
  sections?: ReportSection[];
  is_public?: boolean;
  tags?: string[];
}

// Report Generation

export interface ReportGenerateRequest {
  template_id?: string;
  dashboard_id?: string;
  title?: string;
  subtitle?: string;
  format?: ReportFormat;
  page_config?: PageConfig;
  branding?: BrandingConfig;
  sections?: ReportSection[];
  filters?: Record<string, unknown>;
  parameters?: Record<string, unknown>;
  include_cover_page?: boolean;
  include_toc?: boolean;
  generated_date?: string;
}

export interface ReportGenerateResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  format: ReportFormat;
  message?: string;
  download_url?: string;
  expires_at?: string;
}

export interface ReportJob {
  id: string;
  template_id?: string;
  dashboard_id?: string;
  title: string;
  format: ReportFormat;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  created_by: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  download_url?: string;
  file_size?: number;
  expires_at?: string;
}

// Export Types

export interface DashboardExportRequest {
  dashboard_id: string;
  format?: ReportFormat;
  title?: string;
  include_filters?: boolean;
  filter_state?: Record<string, unknown>;
}

export interface ChartExportRequest {
  chart_id: string;
  format?: 'png' | 'jpeg' | 'svg' | 'pdf';
  width?: number;
  height?: number;
  scale?: number;
  include_title?: boolean;
  include_legend?: boolean;
  background_color?: string;
}

// Scheduled Reports

export interface ScheduledReportConfig {
  template_id: string;
  title: string;
  format?: ReportFormat;
  filters?: Record<string, unknown>;
  parameters?: Record<string, unknown>;
}

export interface ScheduledReport {
  id: string;
  name: string;
  config: ScheduledReportConfig;
  schedule: string;
  recipients: string[];
  enabled: boolean;
  workspace_id?: string;
  created_by: string;
  created_at: string;
  last_generated_at?: string;
  next_generation_at?: string;
}

// Template Library

export interface TemplateCategory {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  template_count: number;
}

export interface TemplatePreview {
  id: string;
  name: string;
  description?: string;
  thumbnail_url?: string;
  category?: string;
  tags: string[];
  usage_count: number;
  is_public: boolean;
}

// Format Info

export interface FormatInfo {
  format: ReportFormat;
  name: string;
  description: string;
  extension: string;
  supports_charts: boolean;
  supports_tables: boolean;
  supports_images: boolean;
}

// Constants

export const FORMAT_LABELS: Record<ReportFormat, string> = {
  pdf: 'PDF',
  html: 'HTML',
  excel: 'Excel',
  pptx: 'PowerPoint',
  image: 'Image',
};

export const FORMAT_ICONS: Record<ReportFormat, string> = {
  pdf: 'file-text',
  html: 'globe',
  excel: 'table',
  pptx: 'presentation',
  image: 'image',
};

export const FORMAT_EXTENSIONS: Record<ReportFormat, string> = {
  pdf: '.pdf',
  html: '.html',
  excel: '.xlsx',
  pptx: '.pptx',
  image: '.png',
};

export const PAGE_SIZE_LABELS: Record<PageSize, string> = {
  a4: 'A4',
  letter: 'Letter',
  legal: 'Legal',
  a3: 'A3',
  tabloid: 'Tabloid',
};

export const ORIENTATION_LABELS: Record<PageOrientation, string> = {
  portrait: 'Portrait',
  landscape: 'Landscape',
};

export const ELEMENT_TYPE_LABELS: Record<ElementType, string> = {
  chart: 'Chart',
  table: 'Table',
  text: 'Text',
  image: 'Image',
  kpi: 'KPI Card',
  heading: 'Heading',
  divider: 'Divider',
  spacer: 'Spacer',
  page_break: 'Page Break',
  table_of_contents: 'Table of Contents',
};

export const ELEMENT_TYPE_ICONS: Record<ElementType, string> = {
  chart: 'bar-chart-2',
  table: 'table',
  text: 'type',
  image: 'image',
  kpi: 'activity',
  heading: 'heading',
  divider: 'minus',
  spacer: 'square',
  page_break: 'file-minus',
  table_of_contents: 'list',
};

// Helper Functions

export function getFormatLabel(format: ReportFormat): string {
  return FORMAT_LABELS[format] || format.toUpperCase();
}

export function getFormatIcon(format: ReportFormat): string {
  return FORMAT_ICONS[format] || 'file';
}

export function getFormatExtension(format: ReportFormat): string {
  return FORMAT_EXTENSIONS[format] || '.pdf';
}

export function getElementTypeLabel(type: ElementType): string {
  return ELEMENT_TYPE_LABELS[type] || type;
}

export function getElementTypeIcon(type: ElementType): string {
  return ELEMENT_TYPE_ICONS[type] || 'square';
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function getJobStatusColor(status: ReportJob['status']): string {
  const colors: Record<ReportJob['status'], string> = {
    pending: 'gray',
    processing: 'blue',
    completed: 'green',
    failed: 'red',
    cancelled: 'gray',
  };
  return colors[status];
}

export function getJobStatusLabel(status: ReportJob['status']): string {
  const labels: Record<ReportJob['status'], string> = {
    pending: 'Pending',
    processing: 'Processing',
    completed: 'Completed',
    failed: 'Failed',
    cancelled: 'Cancelled',
  };
  return labels[status];
}

export function isJobComplete(job: ReportJob): boolean {
  return job.status === 'completed';
}

export function isJobInProgress(job: ReportJob): boolean {
  return job.status === 'pending' || job.status === 'processing';
}

export function createDefaultSection(): ReportSection {
  return {
    id: crypto.randomUUID(),
    title: 'New Section',
    elements: [],
    columns: 1,
    padding: 10,
  };
}

export function createDefaultBranding(): BrandingConfig {
  return {
    primary_color: '#1f2937',
    secondary_color: '#3b82f6',
    accent_color: '#10b981',
    font_family: 'Inter, sans-serif',
  };
}

export function createDefaultPageConfig(): PageConfig {
  return {
    size: 'a4',
    orientation: 'portrait',
    margins: { top: 20, bottom: 20, left: 15, right: 15 },
    header_footer: {
      show_header: true,
      show_footer: true,
      include_page_numbers: true,
      include_date: true,
    },
  };
}
