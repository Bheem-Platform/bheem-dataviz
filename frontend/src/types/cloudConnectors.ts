/**
 * Cloud Connectors Types
 *
 * TypeScript types for BigQuery and Snowflake cloud database connections.
 */

// BigQuery Types

export interface BigQueryConnectionCreate {
  name: string;
  project_id: string;
  credentials_json?: string;
  credentials_path?: string;
  default_dataset?: string;
}

export interface BigQueryTestRequest {
  project_id: string;
  credentials_json?: string;
  credentials_path?: string;
}

export interface BigQueryDataset {
  id: string;
  project: string;
  description?: string;
  location?: string;
  created?: string;
  modified?: string;
}

export interface BigQueryTableInfo {
  schema: string;
  name: string;
  type: string;
  full_id: string;
  num_rows?: number;
  num_bytes?: number;
}

export interface BigQueryQueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
  total: number;
  total_bytes_processed: number;
  total_bytes_billed: number;
  cache_hit: boolean;
  execution_time: number;
}

export interface BigQueryCostEstimate {
  bytes_processed: number;
  bytes_processed_formatted: string;
  estimated_cost_usd: number;
  estimated_cost_formatted: string;
}

// Snowflake Types

export interface SnowflakeConnectionCreate {
  name: string;
  account: string;
  user: string;
  password: string;
  warehouse?: string;
  database?: string;
  schema?: string;
  role?: string;
}

export interface SnowflakeTestRequest {
  account: string;
  user: string;
  password: string;
  warehouse?: string;
  database?: string;
  schema?: string;
  role?: string;
}

export interface SnowflakeDatabase {
  name: string;
  owner?: string;
  comment?: string;
  created_on?: string;
}

export interface SnowflakeSchema {
  name: string;
  database: string;
  owner?: string;
  comment?: string;
}

export interface SnowflakeWarehouse {
  name: string;
  state: string;
  type: string;
  size: string;
  auto_suspend?: number;
  auto_resume?: boolean;
}

export interface SnowflakeTableInfo {
  schema: string;
  name: string;
  type: string;
  database: string;
  rows?: number;
}

// Common Types

export interface CloudConnectionStatus {
  available: boolean;
  message: string;
}

export interface CloudConnectionTestResponse {
  success: boolean;
  message: string;
  tables_count?: number;
  version?: string;
}

export interface CloudTableColumn {
  name: string;
  type: string;
  nullable: boolean;
  default?: string;
  description?: string;
  mode?: string;  // BigQuery specific: NULLABLE, REQUIRED, REPEATED
}

export interface CloudTablePreview {
  columns: string[];
  rows: Record<string, unknown>[];
  total: number;
  preview_count: number;
  execution_time: number;
}

// Connection Form Types

export type CloudProvider = 'bigquery' | 'snowflake';

export interface CloudConnectionFormData {
  provider: CloudProvider;
  name: string;

  // BigQuery fields
  project_id?: string;
  credentials_json?: string;
  credentials_path?: string;
  default_dataset?: string;

  // Snowflake fields
  account?: string;
  user?: string;
  password?: string;
  warehouse?: string;
  database?: string;
  schema?: string;
  role?: string;
}

// Constants

export const CLOUD_PROVIDERS: Record<CloudProvider, { label: string; description: string }> = {
  bigquery: {
    label: 'Google BigQuery',
    description: 'Connect to Google Cloud BigQuery data warehouse',
  },
  snowflake: {
    label: 'Snowflake',
    description: 'Connect to Snowflake cloud data platform',
  },
};

export const BIGQUERY_REGIONS = [
  'us-central1',
  'us-east1',
  'us-west1',
  'europe-west1',
  'europe-west2',
  'asia-east1',
  'asia-southeast1',
  'australia-southeast1',
];

export const SNOWFLAKE_REGIONS = [
  { region: 'us-east-1', cloud: 'aws', label: 'US East (N. Virginia) - AWS' },
  { region: 'us-west-2', cloud: 'aws', label: 'US West (Oregon) - AWS' },
  { region: 'eu-west-1', cloud: 'aws', label: 'EU (Ireland) - AWS' },
  { region: 'eu-central-1', cloud: 'aws', label: 'EU (Frankfurt) - AWS' },
  { region: 'ap-southeast-1', cloud: 'aws', label: 'Asia Pacific (Singapore) - AWS' },
  { region: 'ap-southeast-2', cloud: 'aws', label: 'Asia Pacific (Sydney) - AWS' },
  { region: 'east-us-2', cloud: 'azure', label: 'East US 2 - Azure' },
  { region: 'west-us-2', cloud: 'azure', label: 'West US 2 - Azure' },
  { region: 'west-europe', cloud: 'azure', label: 'West Europe - Azure' },
  { region: 'us-central1', cloud: 'gcp', label: 'US Central 1 - GCP' },
  { region: 'europe-west4', cloud: 'gcp', label: 'Europe West 4 - GCP' },
];

export const SNOWFLAKE_WAREHOUSE_SIZES = [
  'X-Small',
  'Small',
  'Medium',
  'Large',
  'X-Large',
  '2X-Large',
  '3X-Large',
  '4X-Large',
];

// Helper Functions

export function formatBigQueryBytes(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  let unitIndex = 0;
  let size = bytes;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`;
}

export function estimateBigQueryCost(bytesProcessed: number): number {
  // BigQuery pricing: $5 per TB processed
  const costPerTB = 5;
  return (bytesProcessed / Math.pow(1024, 4)) * costPerTB;
}

export function formatSnowflakeAccount(account: string, region: string, cloud: string): string {
  // Format: account.region.cloud (e.g., xy12345.us-east-1.aws)
  return `${account}.${region}.${cloud}`;
}

export function parseSnowflakeAccount(fullAccount: string): {
  account: string;
  region?: string;
  cloud?: string;
} {
  const parts = fullAccount.split('.');
  if (parts.length >= 3) {
    return {
      account: parts[0],
      region: parts[1],
      cloud: parts[2],
    };
  }
  return { account: fullAccount };
}

export function validateBigQueryCredentials(json: string): boolean {
  try {
    const creds = JSON.parse(json);
    return !!(creds.type && creds.project_id && creds.private_key);
  } catch {
    return false;
  }
}

export function createBigQueryConnection(
  name: string,
  projectId: string,
  credentialsJson?: string,
  defaultDataset?: string
): BigQueryConnectionCreate {
  return {
    name,
    project_id: projectId,
    credentials_json: credentialsJson,
    default_dataset: defaultDataset,
  };
}

export function createSnowflakeConnection(
  name: string,
  account: string,
  user: string,
  password: string,
  options?: {
    warehouse?: string;
    database?: string;
    schema?: string;
    role?: string;
  }
): SnowflakeConnectionCreate {
  return {
    name,
    account,
    user,
    password,
    ...options,
  };
}
