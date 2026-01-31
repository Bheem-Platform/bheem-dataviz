"""
Row-Level Security Service

Handles RLS policy evaluation and query modification.
"""

import logging
from typing import Any, Optional
from datetime import datetime

from app.schemas.rls import (
    RLSFilterType,
    RLSOperator,
    UserAttributeType,
    PermissionLevel,
    RLSCondition,
    RLSConditionGroup,
    RLSPolicy,
    UserSecurityContext,
    RLSFilterRequest,
    RLSFilterResponse,
    RLSConfiguration,
    RLSAuditEntry,
)

logger = logging.getLogger(__name__)


class RLSService:
    """Service for evaluating and applying row-level security"""

    def __init__(self, config: Optional[RLSConfiguration] = None):
        self.config = config or RLSConfiguration()
        self._policy_cache: dict[str, list[RLSPolicy]] = {}

    def evaluate_access(
        self,
        request: RLSFilterRequest,
        policies: list[RLSPolicy],
    ) -> RLSFilterResponse:
        """
        Evaluate RLS policies for a data access request.

        Returns the filters to apply or access denial.
        """
        if not self.config.enabled:
            return RLSFilterResponse(has_filters=False)

        # Get applicable policies
        applicable_policies = self._get_applicable_policies(
            policies=policies,
            request=request,
        )

        if not applicable_policies:
            if self.config.default_deny:
                return RLSFilterResponse(
                    has_filters=False,
                    access_denied=True,
                    denial_reason="No RLS policy grants access",
                )
            return RLSFilterResponse(has_filters=False)

        # Build combined filter
        where_clauses = []
        applied_policy_ids = []

        for policy in applicable_policies:
            clause = self._build_filter_clause(
                filter_group=policy.filter_group,
                user_context=request.user_context,
            )
            if clause:
                where_clauses.append(f"({clause})")
                applied_policy_ids.append(policy.id)

        if not where_clauses:
            return RLSFilterResponse(has_filters=False)

        # Combine with OR (any matching policy grants access)
        combined_clause = " OR ".join(where_clauses)

        # Log the decision
        if self.config.log_access:
            self._log_access(
                request=request,
                policies_evaluated=[p.id for p in applicable_policies],
                policies_applied=applied_policy_ids,
                decision="allow",
                filters=combined_clause,
            )

        return RLSFilterResponse(
            has_filters=True,
            where_clause=combined_clause,
            policies_applied=applied_policy_ids,
        )

    def _get_applicable_policies(
        self,
        policies: list[RLSPolicy],
        request: RLSFilterRequest,
    ) -> list[RLSPolicy]:
        """Get policies that apply to this request"""
        applicable = []

        user_roles = set(request.user_context.roles)

        for policy in policies:
            if not policy.enabled:
                continue

            # Check table scope
            if policy.table_name and policy.table_name != request.table_name:
                continue
            if policy.schema_name and policy.schema_name != request.schema_name:
                continue
            if policy.connection_id and policy.connection_id != request.connection_id:
                continue

            # Check role assignment
            if policy.role_ids:
                if not user_roles.intersection(set(policy.role_ids)):
                    continue

            applicable.append(policy)

        # Sort by priority
        return sorted(applicable, key=lambda p: p.priority)

    def _build_filter_clause(
        self,
        filter_group: RLSConditionGroup,
        user_context: UserSecurityContext,
    ) -> Optional[str]:
        """Build SQL WHERE clause from filter group"""
        clauses = []

        # Process individual conditions
        for condition in filter_group.conditions:
            clause = self._build_condition_clause(condition, user_context)
            if clause:
                clauses.append(clause)

        # Process nested groups
        for nested_group in filter_group.groups:
            nested_clause = self._build_filter_clause(nested_group, user_context)
            if nested_clause:
                clauses.append(f"({nested_clause})")

        if not clauses:
            return None

        # Combine with AND or OR
        logic = filter_group.logic.upper()
        return f" {logic} ".join(clauses)

    def _build_condition_clause(
        self,
        condition: RLSCondition,
        user_context: UserSecurityContext,
    ) -> Optional[str]:
        """Build SQL clause for a single condition"""
        column = condition.column

        # Get the comparison value(s)
        if condition.filter_type == RLSFilterType.DYNAMIC:
            value = self._get_user_attribute(user_context, condition.user_attribute, condition.custom_attribute)
            if value is None:
                return None
        elif condition.filter_type == RLSFilterType.EXPRESSION:
            # Return the expression directly (with user context substitutions)
            return self._substitute_expression(condition.expression or "", user_context)
        else:
            value = condition.value

        # Build the clause based on operator
        return self._build_operator_clause(column, condition.operator, value)

    def _build_operator_clause(
        self,
        column: str,
        operator: RLSOperator,
        value: Any,
    ) -> Optional[str]:
        """Build clause for an operator"""
        if operator == RLSOperator.EQUALS:
            if isinstance(value, str):
                return f"{column} = '{value}'"
            return f"{column} = {value}"

        elif operator == RLSOperator.NOT_EQUALS:
            if isinstance(value, str):
                return f"{column} != '{value}'"
            return f"{column} != {value}"

        elif operator == RLSOperator.IN:
            if isinstance(value, list):
                if all(isinstance(v, str) for v in value):
                    values_str = ", ".join([f"'{v}'" for v in value])
                else:
                    values_str = ", ".join([str(v) for v in value])
                return f"{column} IN ({values_str})"
            elif isinstance(value, str):
                return f"{column} IN ('{value}')"
            return f"{column} IN ({value})"

        elif operator == RLSOperator.NOT_IN:
            if isinstance(value, list):
                if all(isinstance(v, str) for v in value):
                    values_str = ", ".join([f"'{v}'" for v in value])
                else:
                    values_str = ", ".join([str(v) for v in value])
                return f"{column} NOT IN ({values_str})"
            elif isinstance(value, str):
                return f"{column} NOT IN ('{value}')"
            return f"{column} NOT IN ({value})"

        elif operator == RLSOperator.CONTAINS:
            return f"{column} LIKE '%{value}%'"

        elif operator == RLSOperator.STARTS_WITH:
            return f"{column} LIKE '{value}%'"

        elif operator == RLSOperator.GREATER_THAN:
            return f"{column} > {value}"

        elif operator == RLSOperator.LESS_THAN:
            return f"{column} < {value}"

        elif operator == RLSOperator.BETWEEN:
            if isinstance(value, list) and len(value) >= 2:
                return f"{column} BETWEEN {value[0]} AND {value[1]}"
            return None

        elif operator == RLSOperator.IS_NULL:
            return f"{column} IS NULL"

        elif operator == RLSOperator.IS_NOT_NULL:
            return f"{column} IS NOT NULL"

        return None

    def _get_user_attribute(
        self,
        user_context: UserSecurityContext,
        attribute: Optional[UserAttributeType],
        custom_attribute: Optional[str],
    ) -> Any:
        """Get user attribute value"""
        if attribute == UserAttributeType.USER_ID:
            return user_context.user_id
        elif attribute == UserAttributeType.USERNAME:
            return user_context.username
        elif attribute == UserAttributeType.EMAIL:
            return user_context.email
        elif attribute == UserAttributeType.ROLE:
            return user_context.roles
        elif attribute == UserAttributeType.CUSTOM and custom_attribute:
            return user_context.attributes.get(custom_attribute)
        elif attribute and attribute.value in user_context.attributes:
            return user_context.attributes[attribute.value]
        elif custom_attribute:
            return user_context.attributes.get(custom_attribute)
        return None

    def _substitute_expression(
        self,
        expression: str,
        user_context: UserSecurityContext,
    ) -> str:
        """Substitute user context variables in expression"""
        result = expression

        # Replace placeholders
        result = result.replace("{{user_id}}", f"'{user_context.user_id}'")
        result = result.replace("{{username}}", f"'{user_context.username}'")
        result = result.replace("{{email}}", f"'{user_context.email or ''}'")

        # Replace custom attributes
        for key, value in user_context.attributes.items():
            placeholder = f"{{{{attr.{key}}}}}"
            if isinstance(value, str):
                result = result.replace(placeholder, f"'{value}'")
            elif isinstance(value, list):
                values_str = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in value])
                result = result.replace(placeholder, f"({values_str})")
            else:
                result = result.replace(placeholder, str(value))

        return result

    def _log_access(
        self,
        request: RLSFilterRequest,
        policies_evaluated: list[str],
        policies_applied: list[str],
        decision: str,
        filters: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        """Log an access decision"""
        entry = RLSAuditEntry(
            timestamp=datetime.utcnow().isoformat(),
            user_id=request.user_context.user_id,
            action="data_access",
            object_type="table",
            object_id=f"{request.schema_name}.{request.table_name}",
            policies_evaluated=policies_evaluated,
            policies_applied=policies_applied,
            decision=decision,
            reason=reason,
            filters_applied=filters,
        )
        logger.info(f"RLS Audit: {entry.model_dump_json()}")

    def inject_rls_filter(
        self,
        query: str,
        rls_filter: RLSFilterResponse,
    ) -> str:
        """Inject RLS filter into a query"""
        if not rls_filter.has_filters or not rls_filter.where_clause:
            return query

        # Simple injection - wrap query and add filter
        # In production, use proper SQL parsing
        wrapped = f"""
SELECT * FROM (
    {query}
) AS __rls_filtered
WHERE {rls_filter.where_clause}
"""
        return wrapped.strip()

    def check_object_permission(
        self,
        user_context: UserSecurityContext,
        object_type: str,
        object_id: str,
        required_level: PermissionLevel,
        permissions: list[dict[str, Any]],
    ) -> bool:
        """Check if user has required permission on an object"""
        permission_hierarchy = {
            PermissionLevel.NONE: 0,
            PermissionLevel.VIEW: 1,
            PermissionLevel.EDIT: 2,
            PermissionLevel.ADMIN: 3,
        }

        required_value = permission_hierarchy[required_level]

        for perm in permissions:
            # Check user-specific permission
            if perm.get("user_id") == user_context.user_id:
                level = PermissionLevel(perm.get("permission_level", "none"))
                if permission_hierarchy[level] >= required_value:
                    return True

            # Check role-based permission
            if perm.get("role_id") in user_context.roles:
                level = PermissionLevel(perm.get("permission_level", "none"))
                if permission_hierarchy[level] >= required_value:
                    return True

        return False


def get_rls_service(config: Optional[RLSConfiguration] = None) -> RLSService:
    """Factory function to get service instance"""
    return RLSService(config=config)
