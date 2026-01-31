/**
 * Time Intelligence Types
 *
 * TypeScript types for time-based calculations.
 */

// Enums

export type TimeGranularity = 'year' | 'quarter' | 'month' | 'week' | 'day' | 'hour';

export type TimePeriodType =
  | 'ytd'
  | 'qtd'
  | 'mtd'
  | 'wtd'
  | 'sply'
  | 'splm'
  | 'splq'
  | 'pp'
  | 'ppy'
  | 'ppq'
  | 'ppm'
  | 'rolling'
  | 'trailing'
  | 'parallel'
  | 'date_range'
  | 'fiscal_ytd'
  | 'fiscal_qtd';

export type AggregationType = 'sum' | 'avg' | 'min' | 'max' | 'count' | 'first' | 'last';

// Configuration

export interface FiscalCalendarConfig {
  fiscalYearStartMonth: number;
  fiscalYearStartDay: number;
  weekStartsOn: number;
}

export interface TimeIntelligenceFunction {
  id: string;
  name: string;
  periodType: TimePeriodType;
  dateColumn: string;
  measureColumn: string;
  aggregation: AggregationType;
  periods?: number;
  offset?: number;
  granularity?: TimeGranularity;
  useFiscalCalendar?: boolean;
  fiscalConfig?: FiscalCalendarConfig;
  startDate?: string;
  endDate?: string;
  outputColumn?: string;
  includeComparison?: boolean;
  includePctChange?: boolean;
}

// Request/Response

export interface TimeIntelligenceRequest {
  connectionId: string;
  schemaName: string;
  tableName: string;
  functions: TimeIntelligenceFunction[];
  filters?: Record<string, any>;
  groupBy?: string[];
  referenceDate?: string;
}

export interface TimeIntelligenceResult {
  functionId: string;
  value?: number;
  comparisonValue?: number;
  pctChange?: number;
  periodStart?: string;
  periodEnd?: string;
  comparisonPeriodStart?: string;
  comparisonPeriodEnd?: string;
}

export interface TimeIntelligenceResponse {
  success: boolean;
  results: TimeIntelligenceResult[];
  query?: string;
  error?: string;
}

// Date Table

export interface DateTableConfig {
  startDate: string;
  endDate: string;
  tableName: string;
  includeFiscal?: boolean;
  fiscalConfig?: FiscalCalendarConfig;
  includeHolidays?: boolean;
  holidayCountry?: string;
}

export interface DateTableColumn {
  name: string;
  type: string;
  description: string;
}

// Templates

export interface TimeIntelligenceTemplate {
  id: string;
  name: string;
  description: string;
  periodType: TimePeriodType;
  aggregation: AggregationType;
  includeComparison?: boolean;
  includePctChange?: boolean;
  periods?: number;
  granularity?: TimeGranularity;
}

// Period Type Options

export interface PeriodTypeOption {
  value: TimePeriodType;
  label: string;
  description: string;
}

export const PERIOD_TYPE_OPTIONS: PeriodTypeOption[] = [
  { value: 'ytd', label: 'Year-to-Date', description: 'From start of year to current date' },
  { value: 'qtd', label: 'Quarter-to-Date', description: 'From start of quarter to current date' },
  { value: 'mtd', label: 'Month-to-Date', description: 'From start of month to current date' },
  { value: 'wtd', label: 'Week-to-Date', description: 'From start of week to current date' },
  { value: 'sply', label: 'Same Period Last Year', description: 'Same dates in the previous year' },
  { value: 'splm', label: 'Same Period Last Month', description: 'Same dates in the previous month' },
  { value: 'splq', label: 'Same Period Last Quarter', description: 'Same dates in the previous quarter' },
  { value: 'ppy', label: 'Previous Year', description: 'Full previous year' },
  { value: 'ppq', label: 'Previous Quarter', description: 'Full previous quarter' },
  { value: 'ppm', label: 'Previous Month', description: 'Full previous month' },
  { value: 'rolling', label: 'Rolling Periods', description: 'Rolling N periods from current date' },
  { value: 'trailing', label: 'Trailing Periods', description: 'N complete periods before current' },
  { value: 'fiscal_ytd', label: 'Fiscal Year-to-Date', description: 'From fiscal year start to current date' },
  { value: 'fiscal_qtd', label: 'Fiscal Quarter-to-Date', description: 'From fiscal quarter start to current date' },
];

export const AGGREGATION_OPTIONS = [
  { value: 'sum', label: 'Sum', description: 'Total of all values' },
  { value: 'avg', label: 'Average', description: 'Mean of all values' },
  { value: 'min', label: 'Minimum', description: 'Smallest value' },
  { value: 'max', label: 'Maximum', description: 'Largest value' },
  { value: 'count', label: 'Count', description: 'Number of values' },
  { value: 'first', label: 'First', description: 'First value in period' },
  { value: 'last', label: 'Last', description: 'Last value in period' },
];

export const GRANULARITY_OPTIONS = [
  { value: 'year', label: 'Year' },
  { value: 'quarter', label: 'Quarter' },
  { value: 'month', label: 'Month' },
  { value: 'week', label: 'Week' },
  { value: 'day', label: 'Day' },
  { value: 'hour', label: 'Hour' },
];

// Helper Functions

export function createDefaultTimeFunction(
  dateColumn: string,
  measureColumn: string,
  periodType: TimePeriodType = 'ytd'
): TimeIntelligenceFunction {
  return {
    id: `ti_${Date.now()}`,
    name: `${periodType.toUpperCase()} ${measureColumn}`,
    periodType,
    dateColumn,
    measureColumn,
    aggregation: 'sum',
    includeComparison: false,
    includePctChange: false,
  };
}

export function getComparisonLabel(periodType: TimePeriodType): string {
  switch (periodType) {
    case 'ytd':
    case 'sply':
    case 'ppy':
      return 'vs. Last Year';
    case 'qtd':
    case 'splq':
    case 'ppq':
      return 'vs. Last Quarter';
    case 'mtd':
    case 'splm':
    case 'ppm':
      return 'vs. Last Month';
    case 'rolling':
    case 'trailing':
      return 'vs. Prior Period';
    default:
      return 'vs. Comparison';
  }
}

export function formatPctChange(pctChange: number | undefined): string {
  if (pctChange === undefined || pctChange === null) return '-';
  const sign = pctChange >= 0 ? '+' : '';
  return `${sign}${pctChange.toFixed(1)}%`;
}
