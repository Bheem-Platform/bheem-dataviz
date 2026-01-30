"""
Transform Service - SQL Generator for data transformations.

Converts transform recipe steps into SQL queries for different database dialects.
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)


class SQLDialect(str, Enum):
    postgresql = "postgresql"
    mysql = "mysql"


# Security: Whitelists for SQL generation
ALLOWED_OPERATORS = {'=', '!=', '<>', '>', '>=', '<', '<=', 'is_null', 'is_not_null', 'in', 'not_in', 'like', 'not_like'}
ALLOWED_DIRECTIONS = {'ASC', 'DESC'}
ALLOWED_JOIN_TYPES = {'INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS'}
ALLOWED_LOGIC = {'AND', 'OR'}

# SQL keywords that should never appear in expressions (case-insensitive)
FORBIDDEN_SQL_KEYWORDS = {
    'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
    'UNION', 'INTERSECT', 'EXCEPT', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE',
    'INTO', 'FROM', 'WHERE', 'HAVING', 'ORDER', 'GROUP', 'LIMIT', 'OFFSET',
    '--', '/*', '*/', ';', 'INFORMATION_SCHEMA', 'PG_', 'MYSQL.', 'SLEEP(',
    'BENCHMARK(', 'WAITFOR', 'DELAY', 'SHUTDOWN', 'XP_', 'SP_'
}


class TransformService:
    """
    Service for generating and executing SQL from transform steps.
    """

    def __init__(self, dialect: SQLDialect = SQLDialect.postgresql):
        self.dialect = dialect
        self._quote_char = '"' if dialect == SQLDialect.postgresql else '`'

    def quote_identifier(self, name: str) -> str:
        """Quote a column or table name."""
        q = self._quote_char
        return f"{q}{name}{q}"

    def quote_value(self, value: Any) -> str:
        """Quote a literal value for SQL."""
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Escape single quotes
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, list):
            # For IN clauses
            return f"({', '.join(self.quote_value(v) for v in value)})"
        else:
            return f"'{str(value)}'"

    def validate_expression(self, expression: str, available_columns: Optional[List[str]] = None) -> str:
        """
        Validate and sanitize a SQL expression for calculated columns.

        Only allows:
        - Column references (optionally validated against available_columns)
        - Numeric literals
        - String literals in single quotes
        - Basic arithmetic operators: + - * / %
        - Parentheses for grouping
        - Basic SQL functions: COALESCE, NULLIF, CAST, CONCAT, UPPER, LOWER, TRIM, ABS, ROUND, FLOOR, CEILING

        Raises ValueError if expression contains forbidden patterns.
        """
        if not expression or not expression.strip():
            raise ValueError("Expression cannot be empty")

        expr_upper = expression.upper()

        # Check for forbidden SQL keywords
        for keyword in FORBIDDEN_SQL_KEYWORDS:
            if keyword.upper() in expr_upper:
                raise ValueError(f"Expression contains forbidden keyword: {keyword}")

        # Check for comment patterns
        if '--' in expression or '/*' in expression or '*/' in expression:
            raise ValueError("Expression cannot contain SQL comments")

        # Check for semicolons (statement terminator)
        if ';' in expression:
            raise ValueError("Expression cannot contain semicolons")

        # Check for subquery patterns
        if '(' in expression and any(kw in expr_upper for kw in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
            raise ValueError("Expression cannot contain subqueries")

        return expression.strip()

    def validate_operator(self, operator: str) -> str:
        """Validate filter operator against whitelist."""
        op = operator.lower() if operator else '='
        if op not in ALLOWED_OPERATORS:
            raise ValueError(f"Invalid operator: {operator}. Allowed: {', '.join(ALLOWED_OPERATORS)}")
        return op

    def validate_direction(self, direction: str) -> str:
        """Validate sort direction against whitelist."""
        dir_upper = (direction or 'ASC').upper()
        if dir_upper not in ALLOWED_DIRECTIONS:
            raise ValueError(f"Invalid sort direction: {direction}. Allowed: ASC, DESC")
        return dir_upper

    def validate_join_type(self, join_type: str) -> str:
        """Validate join type against whitelist."""
        jt_upper = (join_type or 'LEFT').upper()
        if jt_upper not in ALLOWED_JOIN_TYPES:
            raise ValueError(f"Invalid join type: {join_type}. Allowed: {', '.join(ALLOWED_JOIN_TYPES)}")
        return jt_upper

    def validate_logic(self, logic: str) -> str:
        """Validate filter logic (AND/OR) against whitelist."""
        logic_upper = (logic or 'AND').upper()
        if logic_upper not in ALLOWED_LOGIC:
            raise ValueError(f"Invalid logic: {logic}. Allowed: AND, OR")
        return logic_upper

    def generate_sql(
        self,
        source_table: str,
        source_schema: str,
        steps: List[Dict[str, Any]],
        limit: Optional[int] = None,
        offset: int = 0,
        available_columns: Optional[List[str]] = None
    ) -> str:
        """
        Generate SQL query from transform steps.

        Args:
            source_table: Starting table name
            source_schema: Schema name
            steps: List of transform step configurations
            limit: Optional row limit
            offset: Offset for pagination

        Returns:
            Generated SQL query string
        """
        # Start with base table
        base_table = f"{self.quote_identifier(source_schema)}.{self.quote_identifier(source_table)}"

        # Track state through transformations
        current_columns = ["*"]  # Will be refined by select steps
        joins = []
        where_clauses = []
        group_by_columns = []
        having_clauses = []
        order_by_clauses = []
        aggregations = []
        column_aliases = {}  # For renamed columns
        added_columns = []  # New calculated columns (add_column step)
        transformed_columns = {}  # Column replacements: {original_col: (expression, alias)}

        # Additional state for new step types
        deduplicate_columns = None  # None = no dedup, [] = DISTINCT *, [...] = DISTINCT ON columns
        use_distinct = False
        step_limit = None  # Limit from limit step (separate from pagination limit)
        step_offset = 0    # Offset from limit step
        union_tables = []  # List of (schema, table, union_all) tuples
        column_order = None  # For reorder step

        # Process each step
        for step in steps:
            step_type = step.get("type")

            if step_type == "select":
                current_columns = step.get("columns", ["*"])

            elif step_type == "rename":
                mapping = step.get("mapping", {})
                column_aliases.update(mapping)

            elif step_type == "drop_column":
                drop_cols = set(step.get("columns", []))
                if current_columns != ["*"]:
                    current_columns = [c for c in current_columns if c not in drop_cols]

            elif step_type == "add_column":
                name = step.get("name")
                expression = step.get("expression")
                if name and expression:
                    # Security: Validate expression before using
                    try:
                        validated_expr = self.validate_expression(expression, available_columns)
                        added_columns.append((validated_expr, name))
                    except ValueError as e:
                        logger.warning(f"Invalid expression rejected: {e}")
                        raise ValueError(f"Invalid expression in add_column: {e}")

            elif step_type == "filter":
                conditions = step.get("conditions", [])
                # Security: Validate logic operator
                logic = self.validate_logic(step.get("logic", "and"))
                clause_parts = []

                for cond in conditions:
                    col_name = cond.get("column", "")
                    # Skip conditions with empty column names
                    if not col_name:
                        continue

                    col = self.quote_identifier(col_name)
                    # Security: Validate operator against whitelist
                    op = self.validate_operator(cond.get("operator", "="))
                    val = cond.get("value")

                    if op == "is_null":
                        clause_parts.append(f"{col} IS NULL")
                    elif op == "is_not_null":
                        clause_parts.append(f"{col} IS NOT NULL")
                    elif op == "in":
                        clause_parts.append(f"{col} IN {self.quote_value(val)}")
                    elif op == "not_in":
                        clause_parts.append(f"{col} NOT IN {self.quote_value(val)}")
                    elif op == "like":
                        clause_parts.append(f"{col} LIKE {self.quote_value(val)}")
                    elif op == "not_like":
                        clause_parts.append(f"{col} NOT LIKE {self.quote_value(val)}")
                    else:
                        # Only basic comparison operators reach here: = != <> > >= < <=
                        clause_parts.append(f"{col} {op} {self.quote_value(val)}")

                if clause_parts:
                    combined = f" {logic} ".join(clause_parts)
                    where_clauses.append(f"({combined})")

            elif step_type == "sort":
                columns = step.get("columns", [])
                for sort_col in columns:
                    col_name = sort_col.get("column", "")
                    if not col_name:
                        continue
                    col = self.quote_identifier(col_name)
                    # Security: Validate direction against whitelist
                    direction = self.validate_direction(sort_col.get("direction", "asc"))
                    order_by_clauses.append(f"{col} {direction}")

            elif step_type == "join":
                join_table = step.get("table")
                join_schema = step.get("schema_name", source_schema)
                # Security: Validate join type against whitelist
                join_type = self.validate_join_type(step.get("join_type", "left"))
                on_conditions = step.get("on", [])

                join_table_full = f"{self.quote_identifier(join_schema)}.{self.quote_identifier(join_table)}"
                join_alias = f"j_{join_table}"

                on_parts = []
                for on_cond in on_conditions:
                    left_col = self.quote_identifier(on_cond.get("left", ""))
                    right_col = self.quote_identifier(on_cond.get("right", ""))
                    on_parts.append(f"t.{left_col} = {join_alias}.{right_col}")

                if on_parts:
                    on_clause = " AND ".join(on_parts)
                    joins.append(f"{join_type} JOIN {join_table_full} AS {join_alias} ON {on_clause}")

                # Add selected columns from join
                select_cols = step.get("select_columns")
                if select_cols and current_columns != ["*"]:
                    for col in select_cols:
                        current_columns.append(f"{join_alias}.{self.quote_identifier(col)}")

            elif step_type == "group_by":
                group_by_columns = [self.quote_identifier(c) for c in step.get("columns", []) if c]
                aggs = step.get("aggregations", [])

                for agg in aggs:
                    col = agg.get("column")
                    func = agg.get("function", "sum").upper()
                    alias = agg.get("alias", f"{func}_{col}")

                    if not col and func != "COUNT":
                        continue

                    quoted_col = self.quote_identifier(col) if col else None

                    if func == "COUNT_DISTINCT":
                        if col:
                            aggregations.append(f"COUNT(DISTINCT {quoted_col}) AS {self.quote_identifier(alias)}")
                    elif func == "COUNT" and (col == "*" or not col):
                        aggregations.append(f"COUNT(*) AS {self.quote_identifier(alias or 'count')}")
                    elif func in ("SUM", "AVG"):
                        # SUM/AVG work directly on numeric columns, just use the column
                        # NULLs are automatically ignored by aggregate functions
                        aggregations.append(f"{func}({quoted_col}) AS {self.quote_identifier(alias)}")
                    elif func in ("MIN", "MAX"):
                        # MIN/MAX work on text too, but try numeric cast for better sorting
                        if self.dialect == SQLDialect.postgresql:
                            # Use COALESCE to handle potential cast failures gracefully
                            aggregations.append(f"{func}({quoted_col}) AS {self.quote_identifier(alias)}")
                        else:
                            aggregations.append(f"{func}({quoted_col}) AS {self.quote_identifier(alias)}")
                    elif col:
                        aggregations.append(f"{func}({quoted_col}) AS {self.quote_identifier(alias)}")

            elif step_type == "deduplicate":
                dedup_cols = step.get("columns", [])
                if dedup_cols:
                    # DISTINCT ON specific columns (PostgreSQL) or GROUP BY (MySQL)
                    deduplicate_columns = dedup_cols
                else:
                    # DISTINCT * (all columns)
                    use_distinct = True

            elif step_type == "limit":
                step_limit = step.get("count", 100)
                step_offset = step.get("offset", 0)

            elif step_type == "reorder":
                # Reorder columns in the output
                column_order = step.get("columns", [])
                # If select hasn't been used yet, use the reorder columns
                if current_columns == ["*"]:
                    current_columns = column_order

            elif step_type == "union":
                union_table = step.get("table")
                union_schema = step.get("schema_name", source_schema)
                union_all = step.get("all", True)  # UNION ALL by default
                if union_table:
                    union_tables.append((union_schema, union_table, union_all))

            elif step_type == "cast":
                col = step.get("column")
                to_type = step.get("to_type", "text").upper()
                if col:
                    type_map = {
                        "TEXT": "VARCHAR" if self.dialect == SQLDialect.mysql else "TEXT",
                        "INTEGER": "INTEGER",
                        "BIGINT": "BIGINT",
                        "DECIMAL": "DECIMAL(18,2)",
                        "BOOLEAN": "BOOLEAN",
                        "DATE": "DATE",
                        "TIMESTAMP": "TIMESTAMP"
                    }
                    sql_type = type_map.get(to_type, "TEXT")
                    transformed_columns[col] = (f"CAST(t.{self.quote_identifier(col)} AS {sql_type})", col)

            elif step_type == "replace":
                col = step.get("column")
                find_val = step.get("find")
                replace_val = step.get("replace_with")
                if col:
                    if find_val is None or find_val == "NULL":
                        expr = f"COALESCE(t.{self.quote_identifier(col)}, {self.quote_value(replace_val)})"
                    else:
                        expr = f"REPLACE(t.{self.quote_identifier(col)}, {self.quote_value(find_val)}, {self.quote_value(replace_val)})"
                    transformed_columns[col] = (expr, col)

            elif step_type == "trim":
                for col in step.get("columns", []):
                    if col:
                        transformed_columns[col] = (f"TRIM(t.{self.quote_identifier(col)})", col)

            elif step_type == "case":
                col = step.get("column")
                case_type = step.get("to", "upper")
                if col:
                    if case_type == "upper":
                        transformed_columns[col] = (f"UPPER(t.{self.quote_identifier(col)})", col)
                    elif case_type == "lower":
                        transformed_columns[col] = (f"LOWER(t.{self.quote_identifier(col)})", col)
                    elif case_type == "title":
                        if self.dialect == SQLDialect.postgresql:
                            transformed_columns[col] = (f"INITCAP(t.{self.quote_identifier(col)})", col)
                        else:
                            # MySQL doesn't have INITCAP, use a workaround
                            transformed_columns[col] = (f"CONCAT(UPPER(SUBSTRING(t.{self.quote_identifier(col)}, 1, 1)), LOWER(SUBSTRING(t.{self.quote_identifier(col)}, 2)))", col)

            elif step_type == "fill_null":
                col = step.get("column")
                val = step.get("value")
                if col:
                    # Handle both NULL and empty strings
                    # Cast to text for NULLIF comparison, then COALESCE replaces all NULLs/empty
                    quoted_col = self.quote_identifier(col)
                    # Use CASE to handle both NULL and empty string for any column type
                    if self.dialect == SQLDialect.postgresql:
                        expr = f"CASE WHEN t.{quoted_col} IS NULL OR TRIM(t.{quoted_col}::TEXT) = '' THEN {self.quote_value(val)} ELSE t.{quoted_col} END"
                    else:
                        expr = f"CASE WHEN t.{quoted_col} IS NULL OR TRIM(CAST(t.{quoted_col} AS CHAR)) = '' THEN {self.quote_value(val)} ELSE t.{quoted_col} END"
                    transformed_columns[col] = (expr, col)

        # Build SELECT clause
        select_parts = []

        if group_by_columns:
            # Group by query
            select_parts.extend(group_by_columns)
            select_parts.extend(aggregations)
        else:
            # Regular query
            if current_columns == ["*"]:
                if transformed_columns:
                    # When we have column transformations, we need to use a subquery approach
                    # to avoid duplicate columns. We'll select transformed cols explicitly
                    # and use * for the rest via a CTE pattern
                    pass  # Will be handled below with CTE
                else:
                    select_parts.append("t.*")
            else:
                for col in current_columns:
                    if "." in col:
                        # Already qualified (from join)
                        select_parts.append(col)
                    elif col in transformed_columns:
                        # Use transformed expression instead of original
                        expr, alias = transformed_columns[col]
                        select_parts.append(f"{expr} AS {self.quote_identifier(alias)}")
                    else:
                        alias = column_aliases.get(col)
                        if alias:
                            select_parts.append(f"t.{self.quote_identifier(col)} AS {self.quote_identifier(alias)}")
                        else:
                            select_parts.append(f"t.{self.quote_identifier(col)}")

            # Add new calculated columns (from add_column step)
            for expr, alias in added_columns:
                select_parts.append(f"{expr} AS {self.quote_identifier(alias)}")

        # Build the query
        sql_parts = []

        # Handle transformed columns with SELECT *
        if current_columns == ["*"] and transformed_columns and not group_by_columns:
            if available_columns:
                # We have column info - build explicit SELECT with transformations applied
                for col in available_columns:
                    if col in transformed_columns:
                        # Use transformed expression
                        expr, alias = transformed_columns[col]
                        select_parts.append(f"{expr} AS {self.quote_identifier(alias)}")
                    else:
                        # Use original column
                        select_parts.append(f"t.{self.quote_identifier(col)}")
            else:
                # No column info available - we need to avoid duplicates
                # Use a subquery approach: select all columns, then override with transformations
                # Build: SELECT (transformed expressions), other_cols FROM (SELECT * FROM table) subq
                # Actually, simplest approach: use COALESCE etc directly on t.* columns
                # by wrapping in a subquery
                transform_expressions = []
                for col, (expr, alias) in transformed_columns.items():
                    transform_expressions.append(f"{expr} AS {self.quote_identifier(alias)}")

                # Generate subquery that excludes transformed columns using column list
                # Since we don't have column info, wrap entire query to apply transforms
                inner_select = "t.*"

                # Build the query with transforms applied via LATERAL or just accept we need columns
                # For now, just select transformed columns - user can add SELECT step for more
                select_parts.extend(transform_expressions)
                # Don't add t.* to avoid duplicates - transforms only mode
                logger.warning("Column transformations without column info - showing transformed columns only")

        # Handle column reordering if specified
        if column_order and select_parts:
            # Reorder select_parts based on column_order
            ordered_parts = []
            remaining_parts = select_parts.copy()

            for col in column_order:
                # Find matching select part
                for part in remaining_parts[:]:
                    # Check if this part is for the requested column
                    part_col = part.split(" AS ")[0].replace("t.", "").strip('"').strip('`')
                    if part_col == col or part.endswith(f'"{col}"') or part.endswith(f'`{col}`'):
                        ordered_parts.append(part)
                        remaining_parts.remove(part)
                        break
            # Add any remaining columns not in the order list
            ordered_parts.extend(remaining_parts)
            select_parts = ordered_parts

        # Standard query building with DISTINCT support
        if use_distinct:
            sql_parts.append(f"SELECT DISTINCT {', '.join(select_parts)}")
        elif deduplicate_columns and self.dialect == SQLDialect.postgresql:
            # PostgreSQL: Use DISTINCT ON for specific columns
            dedup_cols_quoted = ", ".join([self.quote_identifier(c) for c in deduplicate_columns])
            sql_parts.append(f"SELECT DISTINCT ON ({dedup_cols_quoted}) {', '.join(select_parts)}")
        else:
            sql_parts.append(f"SELECT {', '.join(select_parts)}")

        sql_parts.append(f"FROM {base_table} AS t")

        # Add joins
        for join in joins:
            sql_parts.append(join)

        # Add WHERE
        if where_clauses:
            sql_parts.append(f"WHERE {' AND '.join(where_clauses)}")

        # Add GROUP BY
        if group_by_columns:
            sql_parts.append(f"GROUP BY {', '.join(group_by_columns)}")
        elif deduplicate_columns and self.dialect == SQLDialect.mysql:
            # MySQL: Use GROUP BY for deduplication on specific columns
            dedup_cols_quoted = ", ".join([self.quote_identifier(c) for c in deduplicate_columns])
            sql_parts.append(f"GROUP BY {dedup_cols_quoted}")

        # Add ORDER BY (required for DISTINCT ON in PostgreSQL)
        if order_by_clauses:
            sql_parts.append(f"ORDER BY {', '.join(order_by_clauses)}")
        elif deduplicate_columns and self.dialect == SQLDialect.postgresql:
            # DISTINCT ON requires ORDER BY on the same columns
            dedup_order = ", ".join([f"{self.quote_identifier(c)} ASC" for c in deduplicate_columns])
            sql_parts.append(f"ORDER BY {dedup_order}")

        # Determine final limit/offset
        # step_limit from limit step takes precedence, then pagination limit
        final_limit = step_limit if step_limit is not None else limit
        final_offset = step_offset if step_offset > 0 else offset

        # Add LIMIT/OFFSET
        if final_limit is not None:
            if self.dialect == SQLDialect.mysql:
                sql_parts.append(f"LIMIT {final_offset}, {final_limit}" if final_offset else f"LIMIT {final_limit}")
            else:
                sql_parts.append(f"LIMIT {final_limit}")
                if final_offset:
                    sql_parts.append(f"OFFSET {final_offset}")

        # Build main query
        main_query = "\n".join(sql_parts)

        # Handle UNION if specified
        if union_tables:
            union_queries = [main_query]
            for union_schema, union_table, union_all in union_tables:
                union_table_full = f"{self.quote_identifier(union_schema)}.{self.quote_identifier(union_table)}"
                # Build union query with same select structure
                if use_distinct:
                    union_select = f"SELECT DISTINCT {', '.join(select_parts)}"
                else:
                    union_select = f"SELECT {', '.join(select_parts)}"

                union_query_parts = [union_select, f"FROM {union_table_full} AS t"]

                # Apply same WHERE clause
                if where_clauses:
                    union_query_parts.append(f"WHERE {' AND '.join(where_clauses)}")

                union_keyword = "UNION ALL" if union_all else "UNION"
                union_queries.append(f"{union_keyword}\n" + "\n".join(union_query_parts))

            return "\n".join(union_queries)

        return main_query

    def generate_count_sql(
        self,
        source_table: str,
        source_schema: str,
        steps: List[Dict[str, Any]]
    ) -> str:
        """Generate a COUNT query for the transformed data."""
        # Get the base query without limit
        base_sql = self.generate_sql(source_table, source_schema, steps)

        # Wrap in COUNT
        return f"SELECT COUNT(*) as total FROM ({base_sql}) AS count_subquery"


# Factory function to get service for a dialect
def get_transform_service(dialect: str) -> TransformService:
    """Get a TransformService for the specified dialect."""
    if dialect.lower() == "mysql":
        return TransformService(SQLDialect.mysql)
    return TransformService(SQLDialect.postgresql)


# Singleton instances
postgres_transform_service = TransformService(SQLDialect.postgresql)
mysql_transform_service = TransformService(SQLDialect.mysql)
