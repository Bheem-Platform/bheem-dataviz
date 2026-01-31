/**
 * Row-Level Security Types
 *
 * TypeScript types for RLS policies and permissions.
 */

// Enums

export type RLSFilterType = 'static' | 'dynamic' | 'expression';

export type RLSOperator =
  | 'equals'
  | 'not_equals'
  | 'in'
  | 'not_in'
  | 'contains'
  | 'starts_with'
  | 'greater_than'
  | 'less_than'
  | 'between'
  | 'is_null'
  | 'is_not_null';

export type UserAttributeType =
  | 'user_id'
  | 'username'
  | 'email'
  | 'department'
  | 'region'
  | 'role'
  | 'team'
  | 'custom';

export type PermissionLevel = 'none' | 'view' | 'edit' | 'admin';

// Security Role

export interface SecurityRole {
  id: string;
  name: string;
  description?: string;
  isDefault?: boolean;
  priority?: number;
  createdAt?: string;
  updatedAt?: string;
}

// RLS Condition

export interface RLSCondition {
  id: string;
  column: string;
  operator: RLSOperator;
  filterType: RLSFilterType;
  value?: any;
  userAttribute?: UserAttributeType;
  customAttribute?: string;
  expression?: string;
}

export interface RLSConditionGroup {
  id: string;
  logic: 'AND' | 'OR';
  conditions: RLSCondition[];
  groups?: RLSConditionGroup[];
}

// RLS Policy

export interface RLSPolicy {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  priority?: number;
  tableName?: string;
  schemaName?: string;
  connectionId?: string;
  filterGroup: RLSConditionGroup;
  roleIds: string[];
  createdAt?: string;
  updatedAt?: string;
  createdBy?: string;
}

// User Role Mapping

export interface UserRoleMapping {
  userId: string;
  roleIds: string[];
  effectiveFrom?: string;
  effectiveTo?: string;
}

// User Security Context

export interface UserSecurityContext {
  userId: string;
  username: string;
  email?: string;
  roles: string[];
  attributes: Record<string, any>;
}

// Object Permissions

export interface ObjectPermission {
  objectType: string;
  objectId: string;
  roleId?: string;
  userId?: string;
  permissionLevel: PermissionLevel;
  inherited?: boolean;
}

export interface ObjectPermissions {
  objectType: string;
  objectId: string;
  permissions: ObjectPermission[];
  effectivePermission: PermissionLevel;
}

// RLS Filter Request/Response

export interface RLSFilterRequest {
  connectionId: string;
  schemaName: string;
  tableName: string;
  userContext: UserSecurityContext;
}

export interface RLSFilterResponse {
  hasFilters: boolean;
  whereClause?: string;
  policiesApplied: string[];
  accessDenied?: boolean;
  denialReason?: string;
}

// Configuration

export interface RLSConfiguration {
  enabled: boolean;
  defaultDeny: boolean;
  cacheTtlSeconds: number;
  logAccess: boolean;
  auditMode: boolean;
}

// Policy Templates

export interface RLSPolicyTemplate {
  id: string;
  name: string;
  description: string;
  filterGroup: RLSConditionGroup;
}

// Operator Options

export const RLS_OPERATOR_OPTIONS = [
  { value: 'equals', label: 'Equals', description: 'Value equals' },
  { value: 'not_equals', label: 'Not Equals', description: 'Value does not equal' },
  { value: 'in', label: 'In List', description: 'Value is in list' },
  { value: 'not_in', label: 'Not In List', description: 'Value is not in list' },
  { value: 'contains', label: 'Contains', description: 'Value contains text' },
  { value: 'starts_with', label: 'Starts With', description: 'Value starts with text' },
  { value: 'greater_than', label: 'Greater Than', description: 'Value is greater than' },
  { value: 'less_than', label: 'Less Than', description: 'Value is less than' },
  { value: 'between', label: 'Between', description: 'Value is between two values' },
  { value: 'is_null', label: 'Is Null', description: 'Value is null' },
  { value: 'is_not_null', label: 'Is Not Null', description: 'Value is not null' },
];

export const USER_ATTRIBUTE_OPTIONS = [
  { value: 'user_id', label: 'User ID' },
  { value: 'username', label: 'Username' },
  { value: 'email', label: 'Email' },
  { value: 'department', label: 'Department' },
  { value: 'region', label: 'Region' },
  { value: 'role', label: 'Role' },
  { value: 'team', label: 'Team' },
  { value: 'custom', label: 'Custom Attribute' },
];

export const PERMISSION_LEVEL_OPTIONS = [
  { value: 'none', label: 'No Access' },
  { value: 'view', label: 'View Only' },
  { value: 'edit', label: 'Can Edit' },
  { value: 'admin', label: 'Full Admin' },
];

// Helper Functions

export function createDefaultPolicy(tableName: string): RLSPolicy {
  return {
    id: `policy_${Date.now()}`,
    name: `Policy for ${tableName}`,
    enabled: true,
    tableName,
    filterGroup: {
      id: `group_${Date.now()}`,
      logic: 'AND',
      conditions: [],
    },
    roleIds: [],
  };
}

export function createDefaultCondition(): RLSCondition {
  return {
    id: `cond_${Date.now()}`,
    column: '',
    operator: 'equals',
    filterType: 'static',
  };
}

export function hasPermission(
  effectivePermission: PermissionLevel,
  requiredLevel: PermissionLevel
): boolean {
  const levels: PermissionLevel[] = ['none', 'view', 'edit', 'admin'];
  return levels.indexOf(effectivePermission) >= levels.indexOf(requiredLevel);
}
