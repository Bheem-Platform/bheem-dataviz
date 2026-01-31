/**
 * Kodee NL-to-SQL Types
 *
 * TypeScript types for the Kodee natural language to SQL engine.
 */

// Enums

export type QueryIntent =
  | 'select'
  | 'aggregate'
  | 'compare'
  | 'trend'
  | 'top_n'
  | 'filter'
  | 'join'
  | 'unknown';

export type QueryComplexity = 'simple' | 'moderate' | 'complex';

export type MessageRole = 'user' | 'assistant' | 'system';

export type ValidationStatus = 'valid' | 'warning' | 'invalid' | 'blocked';

// Schema Context Types

export interface ColumnInfo {
  name: string;
  data_type: string;
  nullable: boolean;
  description?: string;
  sample_values: unknown[];
  is_primary_key: boolean;
  is_foreign_key: boolean;
  foreign_key_ref?: string;
}

export interface TableInfo {
  name: string;
  schema_name: string;
  description?: string;
  columns: ColumnInfo[];
  row_count?: number;
  aliases: string[];
}

export interface RelationshipInfo {
  from_table: string;
  from_column: string;
  to_table: string;
  to_column: string;
  relationship_type: string;
}

export interface MeasureInfo {
  id: string;
  name: string;
  description?: string;
  expression: string;
  table: string;
  column: string;
  aggregate: string;
}

export interface DimensionInfo {
  id: string;
  name: string;
  description?: string;
  table: string;
  column: string;
  hierarchy?: string[];
}

export interface SchemaContext {
  connection_id: string;
  model_id?: string;
  model_name?: string;
  tables: TableInfo[];
  relationships: RelationshipInfo[];
  measures: MeasureInfo[];
  dimensions: DimensionInfo[];
  dialect: string;
  additional_context?: string;
}

// Query Types

export interface NLQueryRequest {
  question: string;
  connection_id?: string;
  model_id?: string;
  conversation_id?: string;
  include_explanation?: boolean;
  max_rows?: number;
  timeout_seconds?: number;
}

export interface QueryValidation {
  status: ValidationStatus;
  messages: string[];
  blocked_keywords: string[];
  estimated_complexity?: QueryComplexity;
  estimated_rows?: number;
}

export interface NLQueryResponse {
  sql: string;
  explanation: string;
  confidence: number;
  intent: QueryIntent;
  complexity: QueryComplexity;
  validation: QueryValidation;
  tables_used: string[];
  columns_used: string[];
  alternatives: string[];
  follow_up_questions: string[];
  execution_time_ms?: number;
  conversation_id?: string;
}

export interface QueryExecutionRequest {
  sql: string;
  connection_id: string;
  max_rows?: number;
  timeout_seconds?: number;
}

export interface QueryExecutionResponse {
  columns: string[];
  rows: unknown[][];
  row_count: number;
  execution_time_ms: number;
  truncated: boolean;
}

// Chat Types

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  sql?: string;
  query_result?: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface ChatSession {
  id: string;
  user_id?: string;
  connection_id?: string;
  model_id?: string;
  title?: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
  context?: SchemaContext;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  connection_id?: string;
  model_id?: string;
  execute_query?: boolean;
  include_visualization?: boolean;
}

export interface ChatResponse {
  session_id: string;
  message_id: string;
  response: string;
  sql?: string;
  query_result?: QueryExecutionResponse;
  visualization_suggestion?: Record<string, unknown>;
  suggestions: string[];
  follow_up_questions: string[];
}

// History Types

export interface QueryHistoryItem {
  id: string;
  user_id?: string;
  question: string;
  sql: string;
  connection_id: string;
  model_id?: string;
  executed: boolean;
  execution_successful?: boolean;
  row_count?: number;
  created_at: string;
}

export interface QueryHistoryResponse {
  items: QueryHistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

// Validation Types

export interface SQLValidationRequest {
  sql: string;
  connection_id?: string;
  strict?: boolean;
}

// Feedback Types

export interface QueryFeedback {
  query_id: string;
  rating: number;
  correct_sql?: string;
  comments?: string;
}

// Example Types

export interface QueryExample {
  question: string;
  sql: string;
  explanation: string;
}

export interface QueryCategory {
  name: string;
  questions: string[];
}

export interface QueryExamplesResponse {
  examples: QueryExample[];
  categories: QueryCategory[];
}

// Suggestions Types

export interface QuerySuggestionsResponse {
  suggestions: string[];
  schema_summary: {
    tables: number;
    measures: number;
    dimensions: number;
  };
}

// Constants

export const INTENT_LABELS: Record<QueryIntent, string> = {
  select: 'Data Selection',
  aggregate: 'Aggregation',
  compare: 'Comparison',
  trend: 'Trend Analysis',
  top_n: 'Top N',
  filter: 'Filtering',
  join: 'Join',
  unknown: 'Unknown',
};

export const COMPLEXITY_LABELS: Record<QueryComplexity, string> = {
  simple: 'Simple',
  moderate: 'Moderate',
  complex: 'Complex',
};

export const COMPLEXITY_COLORS: Record<QueryComplexity, string> = {
  simple: 'green',
  moderate: 'yellow',
  complex: 'red',
};

export const VALIDATION_STATUS_COLORS: Record<ValidationStatus, string> = {
  valid: 'green',
  warning: 'yellow',
  invalid: 'red',
  blocked: 'red',
};

// Sample Questions

export const SAMPLE_QUESTIONS = [
  'What are the top 10 products by sales?',
  'Show me total revenue by month',
  'How many orders were placed last quarter?',
  'Compare sales this year vs last year',
  'Which customers have the highest order value?',
  'Show me the trend of new customers over time',
  'What is the average order value by region?',
  'List products with low inventory',
];

// Helper Functions

export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'green';
  if (confidence >= 0.6) return 'yellow';
  return 'red';
}

export function createDefaultQueryRequest(
  question: string,
  connectionId?: string,
  modelId?: string
): NLQueryRequest {
  return {
    question,
    connection_id: connectionId,
    model_id: modelId,
    include_explanation: true,
    max_rows: 1000,
    timeout_seconds: 30,
  };
}

export function createDefaultChatRequest(
  message: string,
  sessionId?: string,
  connectionId?: string
): ChatRequest {
  return {
    message,
    session_id: sessionId,
    connection_id: connectionId,
    execute_query: true,
    include_visualization: false,
  };
}
