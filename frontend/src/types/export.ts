/**
 * Export & Document Generation Types
 *
 * TypeScript types for PDF, Excel, PowerPoint, and image exports,
 * including export jobs, formats, and configurations.
 */

// Enums

export enum ExportFormat {
  PDF = 'pdf',
  EXCEL = 'excel',
  POWERPOINT = 'powerpoint',
  PNG = 'png',
  SVG = 'svg',
  JPEG = 'jpeg',
  CSV = 'csv',
  JSON = 'json',
}

export enum ExportStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  EXPIRED = 'expired',
}

export enum ExportType {
  DASHBOARD = 'dashboard',
  CHART = 'chart',
  REPORT = 'report',
  QUERY_RESULT = 'query_result',
  DATA_TABLE = 'data_table',
}

export enum PageSize {
  A4 = 'a4',
  A3 = 'a3',
  LETTER = 'letter',
  LEGAL = 'legal',
  TABLOID = 'tabloid',
  CUSTOM = 'custom',
}

export enum PageOrientation {
  PORTRAIT = 'portrait',
  LANDSCAPE = 'landscape',
}

export enum ImageQuality {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  PRINT = 'print',
}

// PDF Export Interfaces

export interface PDFMargins {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

export interface PDFHeader {
  enabled: boolean;
  text?: string;
  logo_url?: string;
  include_date: boolean;
  include_page_number: boolean;
  height: number;
}

export interface PDFFooter {
  enabled: boolean;
  text?: string;
  include_date: boolean;
  include_page_number: boolean;
  include_total_pages: boolean;
  height: number;
}

export interface PDFWatermark {
  enabled: boolean;
  text?: string;
  image_url?: string;
  opacity: number;
  rotation: number;
  position: string;
}

export interface PDFExportConfig {
  page_size: PageSize;
  orientation: PageOrientation;
  custom_width?: number;
  custom_height?: number;
  margins: PDFMargins;
  header: PDFHeader;
  footer: PDFFooter;
  watermark: PDFWatermark;
  include_toc: boolean;
  include_filters: boolean;
  include_timestamp: boolean;
  scale: number;
  print_background: boolean;
  compress: boolean;
  password?: string;
}

// Excel Export Interfaces

export interface ExcelColumnFormat {
  column: string;
  width?: number;
  number_format?: string;
  alignment: string;
  wrap_text: boolean;
  bold: boolean;
  font_color?: string;
  bg_color?: string;
}

export interface ExcelConditionalFormat {
  column: string;
  rule_type: string;
  value: unknown;
  value2?: unknown;
  format: Record<string, unknown>;
}

export interface ExcelChartConfig {
  chart_type: string;
  data_range: string;
  title?: string;
  position: string;
  width: number;
  height: number;
}

export interface ExcelSheetConfig {
  name: string;
  sheet_type: string;
  data_source?: string;
  include_headers: boolean;
  freeze_panes?: string;
  auto_filter: boolean;
  column_formats: ExcelColumnFormat[];
  conditional_formats: ExcelConditionalFormat[];
  charts: ExcelChartConfig[];
  hidden: boolean;
}

export interface ExcelExportConfig {
  sheets: ExcelSheetConfig[];
  include_metadata_sheet: boolean;
  include_summary_sheet: boolean;
  default_column_width: number;
  date_format: string;
  datetime_format: string;
  number_format: string;
  currency_format: string;
  percentage_format: string;
  password?: string;
  protect_structure: boolean;
}

// PowerPoint Export Interfaces

export interface SlideContent {
  type: string;
  source_id?: string;
  content?: string;
  position: Record<string, number>;
  style: Record<string, unknown>;
}

export interface SlideConfig {
  layout: string;
  title?: string;
  subtitle?: string;
  notes?: string;
  contents: SlideContent[];
  background_color?: string;
  background_image?: string;
  transition?: string;
}

export interface PowerPointTheme {
  primary_color: string;
  secondary_color: string;
  background_color: string;
  text_color: string;
  font_family: string;
  title_font_size: number;
  body_font_size: number;
}

export interface PowerPointExportConfig {
  slides: SlideConfig[];
  theme: PowerPointTheme;
  include_title_slide: boolean;
  title?: string;
  subtitle?: string;
  author?: string;
  include_notes: boolean;
  slide_width: number;
  slide_height: number;
}

// Image Export Interfaces

export interface ImageExportConfig {
  format: ExportFormat;
  quality: ImageQuality;
  width?: number;
  height?: number;
  scale: number;
  background_color?: string;
  transparent_background: boolean;
  include_title: boolean;
  include_legend: boolean;
  padding: number;
}

// CSV/JSON Export Interfaces

export interface CSVExportConfig {
  delimiter: string;
  quote_char: string;
  include_headers: boolean;
  encoding: string;
  line_terminator: string;
  date_format: string;
  datetime_format: string;
  null_value: string;
  escape_char?: string;
}

export interface JSONExportConfig {
  pretty_print: boolean;
  indent: number;
  date_format: string;
  include_metadata: boolean;
  array_format: boolean;
}

// Export Job Interfaces

export interface ExportRequest {
  export_type: ExportType;
  format: ExportFormat;
  source_id: string;
  filename?: string;
  pdf_config?: PDFExportConfig;
  excel_config?: ExcelExportConfig;
  powerpoint_config?: PowerPointExportConfig;
  image_config?: ImageExportConfig;
  csv_config?: CSVExportConfig;
  json_config?: JSONExportConfig;
  filters?: Record<string, unknown>;
  parameters?: Record<string, unknown>;
  notify_on_completion?: boolean;
  notification_email?: string;
}

export interface ExportJob {
  id: string;
  user_id: string;
  organization_id?: string;
  export_type: ExportType;
  format: ExportFormat;
  source_id: string;
  source_name?: string;
  filename: string;
  status: ExportStatus;
  progress: number;
  file_size?: number;
  file_url?: string;
  download_count: number;
  error_message?: string;
  config: Record<string, unknown>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  expires_at?: string;
  metadata: Record<string, unknown>;
}

export interface ExportJobUpdate {
  status?: ExportStatus;
  progress?: number;
  file_size?: number;
  file_url?: string;
  error_message?: string;
}

export interface ExportJobListResponse {
  jobs: ExportJob[];
  total: number;
}

// Export Preset Interfaces

export interface ExportPreset {
  id: string;
  name: string;
  description?: string;
  export_type: ExportType;
  format: ExportFormat;
  config: Record<string, unknown>;
  user_id: string;
  organization_id?: string;
  is_default: boolean;
  is_shared: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExportPresetCreate {
  name: string;
  description?: string;
  export_type: ExportType;
  format: ExportFormat;
  config: Record<string, unknown>;
  is_default?: boolean;
  is_shared?: boolean;
}

export interface ExportPresetListResponse {
  presets: ExportPreset[];
  total: number;
}

// Export History Interfaces

export interface ExportHistoryEntry {
  id: string;
  job_id: string;
  user_id: string;
  export_type: ExportType;
  format: ExportFormat;
  source_id: string;
  source_name?: string;
  filename: string;
  file_size?: number;
  status: ExportStatus;
  duration_seconds?: number;
  downloaded: boolean;
  downloaded_at?: string;
  created_at: string;
}

export interface ExportHistoryListResponse {
  entries: ExportHistoryEntry[];
  total: number;
}

// Export Statistics Interfaces

export interface ExportStats {
  organization_id: string;
  total_exports: number;
  exports_today: number;
  exports_this_week: number;
  exports_this_month: number;
  exports_by_format: Record<string, number>;
  exports_by_type: Record<string, number>;
  total_file_size_bytes: number;
  average_duration_seconds: number;
  success_rate: number;
}

// Constants

export const EXPORT_FORMAT_LABELS: Record<ExportFormat, string> = {
  [ExportFormat.PDF]: 'PDF Document',
  [ExportFormat.EXCEL]: 'Excel Spreadsheet',
  [ExportFormat.POWERPOINT]: 'PowerPoint Presentation',
  [ExportFormat.PNG]: 'PNG Image',
  [ExportFormat.SVG]: 'SVG Image',
  [ExportFormat.JPEG]: 'JPEG Image',
  [ExportFormat.CSV]: 'CSV File',
  [ExportFormat.JSON]: 'JSON File',
};

export const EXPORT_STATUS_LABELS: Record<ExportStatus, string> = {
  [ExportStatus.PENDING]: 'Pending',
  [ExportStatus.PROCESSING]: 'Processing',
  [ExportStatus.COMPLETED]: 'Completed',
  [ExportStatus.FAILED]: 'Failed',
  [ExportStatus.CANCELLED]: 'Cancelled',
  [ExportStatus.EXPIRED]: 'Expired',
};

export const EXPORT_TYPE_LABELS: Record<ExportType, string> = {
  [ExportType.DASHBOARD]: 'Dashboard',
  [ExportType.CHART]: 'Chart',
  [ExportType.REPORT]: 'Report',
  [ExportType.QUERY_RESULT]: 'Query Result',
  [ExportType.DATA_TABLE]: 'Data Table',
};

export const PAGE_SIZE_LABELS: Record<PageSize, string> = {
  [PageSize.A4]: 'A4 (210 x 297 mm)',
  [PageSize.A3]: 'A3 (297 x 420 mm)',
  [PageSize.LETTER]: 'Letter (8.5 x 11 in)',
  [PageSize.LEGAL]: 'Legal (8.5 x 14 in)',
  [PageSize.TABLOID]: 'Tabloid (11 x 17 in)',
  [PageSize.CUSTOM]: 'Custom Size',
};

export const IMAGE_QUALITY_LABELS: Record<ImageQuality, string> = {
  [ImageQuality.LOW]: 'Low (72 DPI)',
  [ImageQuality.MEDIUM]: 'Medium (150 DPI)',
  [ImageQuality.HIGH]: 'High (300 DPI)',
  [ImageQuality.PRINT]: 'Print (600 DPI)',
};

export const EXPORT_FILE_EXTENSIONS: Record<ExportFormat, string> = {
  [ExportFormat.PDF]: '.pdf',
  [ExportFormat.EXCEL]: '.xlsx',
  [ExportFormat.POWERPOINT]: '.pptx',
  [ExportFormat.PNG]: '.png',
  [ExportFormat.SVG]: '.svg',
  [ExportFormat.JPEG]: '.jpg',
  [ExportFormat.CSV]: '.csv',
  [ExportFormat.JSON]: '.json',
};

// Helper Functions

export function getExportStatusColor(status: ExportStatus): string {
  const colors: Record<ExportStatus, string> = {
    [ExportStatus.PENDING]: 'yellow',
    [ExportStatus.PROCESSING]: 'blue',
    [ExportStatus.COMPLETED]: 'green',
    [ExportStatus.FAILED]: 'red',
    [ExportStatus.CANCELLED]: 'gray',
    [ExportStatus.EXPIRED]: 'orange',
  };
  return colors[status] || 'gray';
}

export function getExportFormatIcon(format: ExportFormat): string {
  const icons: Record<ExportFormat, string> = {
    [ExportFormat.PDF]: 'file-text',
    [ExportFormat.EXCEL]: 'table',
    [ExportFormat.POWERPOINT]: 'presentation',
    [ExportFormat.PNG]: 'image',
    [ExportFormat.SVG]: 'image',
    [ExportFormat.JPEG]: 'image',
    [ExportFormat.CSV]: 'file-spreadsheet',
    [ExportFormat.JSON]: 'file-code',
  };
  return icons[format] || 'file';
}

export function formatFileSize(bytes?: number): string {
  if (!bytes) return 'Unknown';
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`;
}

export function formatDuration(seconds?: number): string {
  if (!seconds) return '-';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
}

export function isExportComplete(job: ExportJob): boolean {
  return job.status === ExportStatus.COMPLETED;
}

export function isExportInProgress(job: ExportJob): boolean {
  return job.status === ExportStatus.PENDING || job.status === ExportStatus.PROCESSING;
}

export function canDownloadExport(job: ExportJob): boolean {
  return job.status === ExportStatus.COMPLETED && !!job.file_url;
}

export function getExportProgressLabel(job: ExportJob): string {
  if (job.status === ExportStatus.PENDING) return 'Queued...';
  if (job.status === ExportStatus.PROCESSING) return `Processing (${job.progress}%)`;
  if (job.status === ExportStatus.COMPLETED) return 'Ready for download';
  if (job.status === ExportStatus.FAILED) return 'Export failed';
  if (job.status === ExportStatus.CANCELLED) return 'Cancelled';
  if (job.status === ExportStatus.EXPIRED) return 'Expired';
  return 'Unknown';
}

export function getDefaultPDFConfig(): PDFExportConfig {
  return {
    page_size: PageSize.A4,
    orientation: PageOrientation.LANDSCAPE,
    margins: { top: 20, bottom: 20, left: 20, right: 20 },
    header: { enabled: true, include_date: true, include_page_number: false, height: 15 },
    footer: { enabled: true, include_date: false, include_page_number: true, include_total_pages: true, height: 10 },
    watermark: { enabled: false, opacity: 0.1, rotation: -45, position: 'center' },
    include_toc: false,
    include_filters: true,
    include_timestamp: true,
    scale: 1.0,
    print_background: true,
    compress: true,
  };
}

export function getDefaultExcelConfig(): ExcelExportConfig {
  return {
    sheets: [],
    include_metadata_sheet: false,
    include_summary_sheet: false,
    default_column_width: 15,
    date_format: 'YYYY-MM-DD',
    datetime_format: 'YYYY-MM-DD HH:mm:ss',
    number_format: '#,##0.00',
    currency_format: '$#,##0.00',
    percentage_format: '0.00%',
    protect_structure: false,
  };
}

export function getDefaultImageConfig(format: ExportFormat = ExportFormat.PNG): ImageExportConfig {
  return {
    format,
    quality: ImageQuality.HIGH,
    scale: 2.0,
    background_color: '#FFFFFF',
    transparent_background: false,
    include_title: true,
    include_legend: true,
    padding: 20,
  };
}

export function getSupportedFormatsForType(exportType: ExportType): ExportFormat[] {
  const formatMap: Record<ExportType, ExportFormat[]> = {
    [ExportType.DASHBOARD]: [ExportFormat.PDF, ExportFormat.POWERPOINT, ExportFormat.PNG, ExportFormat.JPEG],
    [ExportType.CHART]: [ExportFormat.PNG, ExportFormat.SVG, ExportFormat.JPEG, ExportFormat.PDF],
    [ExportType.REPORT]: [ExportFormat.PDF, ExportFormat.POWERPOINT],
    [ExportType.QUERY_RESULT]: [ExportFormat.EXCEL, ExportFormat.CSV, ExportFormat.JSON],
    [ExportType.DATA_TABLE]: [ExportFormat.EXCEL, ExportFormat.CSV, ExportFormat.JSON],
  };
  return formatMap[exportType] || [];
}
