"""Service for processing advanced filters and generating SQL WHERE clauses."""

from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import re

from app.schemas.filter import (
    FilterCondition, FilterOperator, FilterGroup,
    RelativeDateFilter, DateRangeFilter, RelativeDateUnit,
    SlicerConfig, FilterType, FilterOptionsResponse, FilterOptionValue
)


class FilterService:
    """Service for processing filters and generating SQL."""

    def __init__(self, db_type: str = "postgresql"):
        """
        Initialize filter service.

        Args:
            db_type: Database type (postgresql, mysql, mongodb)
        """
        self.db_type = db_type
        self.quote = '`' if db_type == "mysql" else '"'

    def quote_identifier(self, identifier: str) -> str:
        """Quote a column or table identifier."""
        # Handle dotted identifiers (schema.table.column)
        parts = identifier.split('.')
        return '.'.join([f'{self.quote}{part}{self.quote}' for part in parts])

    def escape_value(self, value: Any, data_type: Optional[str] = None) -> str:
        """
        Escape a value for SQL.

        Args:
            value: The value to escape
            data_type: Optional data type hint

        Returns:
            Escaped value string for SQL
        """
        if value is None:
            return "NULL"

        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"

        if isinstance(value, (int, float)):
            return str(value)

        if isinstance(value, (datetime, date)):
            return f"'{value.isoformat()}'"

        if isinstance(value, str):
            # Escape single quotes
            escaped = value.replace("'", "''")
            return f"'{escaped}'"

        if isinstance(value, list):
            return f"({', '.join([self.escape_value(v) for v in value])})"

        return f"'{str(value)}'"

    def build_condition(self, condition: FilterCondition) -> str:
        """
        Build a SQL condition from a FilterCondition.

        Args:
            condition: The filter condition

        Returns:
            SQL WHERE clause fragment
        """
        col = self.quote_identifier(condition.column)
        op = condition.operator
        val = condition.value
        val2 = condition.value2

        if op == FilterOperator.EQUALS:
            if val is None:
                return f"{col} IS NULL"
            return f"{col} = {self.escape_value(val)}"

        elif op == FilterOperator.NOT_EQUALS:
            if val is None:
                return f"{col} IS NOT NULL"
            return f"{col} != {self.escape_value(val)}"

        elif op == FilterOperator.GREATER_THAN:
            return f"{col} > {self.escape_value(val)}"

        elif op == FilterOperator.GREATER_THAN_OR_EQUALS:
            return f"{col} >= {self.escape_value(val)}"

        elif op == FilterOperator.LESS_THAN:
            return f"{col} < {self.escape_value(val)}"

        elif op == FilterOperator.LESS_THAN_OR_EQUALS:
            return f"{col} <= {self.escape_value(val)}"

        elif op == FilterOperator.IN:
            if not isinstance(val, list):
                val = [val]
            if not val:
                return "1=0"  # Empty IN clause - no matches
            values = ', '.join([self.escape_value(v) for v in val])
            return f"{col} IN ({values})"

        elif op == FilterOperator.NOT_IN:
            if not isinstance(val, list):
                val = [val]
            if not val:
                return "1=1"  # Empty NOT IN clause - all matches
            values = ', '.join([self.escape_value(v) for v in val])
            return f"{col} NOT IN ({values})"

        elif op == FilterOperator.BETWEEN:
            return f"{col} BETWEEN {self.escape_value(val)} AND {self.escape_value(val2)}"

        elif op == FilterOperator.LIKE:
            escaped_val = str(val).replace("'", "''")
            return f"{col} LIKE '%{escaped_val}%'"

        elif op == FilterOperator.NOT_LIKE:
            escaped_val = str(val).replace("'", "''")
            return f"{col} NOT LIKE '%{escaped_val}%'"

        elif op == FilterOperator.STARTS_WITH:
            escaped_val = str(val).replace("'", "''")
            return f"{col} LIKE '{escaped_val}%'"

        elif op == FilterOperator.ENDS_WITH:
            escaped_val = str(val).replace("'", "''")
            return f"{col} LIKE '%{escaped_val}'"

        elif op == FilterOperator.CONTAINS:
            escaped_val = str(val).replace("'", "''")
            return f"{col} LIKE '%{escaped_val}%'"

        elif op == FilterOperator.IS_NULL:
            return f"{col} IS NULL"

        elif op == FilterOperator.IS_NOT_NULL:
            return f"{col} IS NOT NULL"

        else:
            # Default to equals
            return f"{col} = {self.escape_value(val)}"

    def build_relative_date_condition(self, filter: RelativeDateFilter) -> str:
        """
        Build a SQL condition for a relative date filter.

        Args:
            filter: The relative date filter

        Returns:
            SQL WHERE clause fragment
        """
        col = self.quote_identifier(filter.column)
        now = datetime.now()

        # Calculate the start date based on unit
        if filter.unit == RelativeDateUnit.DAY:
            start_date = now - timedelta(days=filter.value)
        elif filter.unit == RelativeDateUnit.WEEK:
            start_date = now - timedelta(weeks=filter.value)
        elif filter.unit == RelativeDateUnit.MONTH:
            start_date = now - relativedelta(months=filter.value)
        elif filter.unit == RelativeDateUnit.QUARTER:
            start_date = now - relativedelta(months=filter.value * 3)
        elif filter.unit == RelativeDateUnit.YEAR:
            start_date = now - relativedelta(years=filter.value)
        else:
            start_date = now - timedelta(days=filter.value)

        # Build the condition
        if filter.include_current:
            end_date = now
        else:
            end_date = now - timedelta(days=1)

        if self.db_type == "postgresql":
            return f"{col} >= '{start_date.date()}' AND {col} <= '{end_date.date()}'"
        elif self.db_type == "mysql":
            return f"{col} >= '{start_date.strftime('%Y-%m-%d')}' AND {col} <= '{end_date.strftime('%Y-%m-%d')}'"
        else:
            return f"{col} >= '{start_date.date()}' AND {col} <= '{end_date.date()}'"

    def build_date_range_condition(self, filter: DateRangeFilter) -> str:
        """
        Build a SQL condition for a date range filter.

        Args:
            filter: The date range filter

        Returns:
            SQL WHERE clause fragment
        """
        col = self.quote_identifier(filter.column)
        conditions = []

        if filter.start_date:
            op = ">=" if filter.include_start else ">"
            conditions.append(f"{col} {op} '{filter.start_date}'")

        if filter.end_date:
            op = "<=" if filter.include_end else "<"
            conditions.append(f"{col} {op} '{filter.end_date}'")

        if not conditions:
            return "1=1"

        return " AND ".join(conditions)

    def build_filter_group(self, group: FilterGroup) -> str:
        """
        Build a SQL condition from a filter group (with AND/OR logic).

        Args:
            group: The filter group

        Returns:
            SQL WHERE clause fragment
        """
        if not group.conditions:
            return "1=1"

        parts = []
        for condition in group.conditions:
            if isinstance(condition, FilterCondition):
                parts.append(self.build_condition(condition))
            elif isinstance(condition, FilterGroup):
                nested = self.build_filter_group(condition)
                parts.append(f"({nested})")

        logic = " AND " if group.logic == "and" else " OR "
        return logic.join(parts)

    def build_where_clause(
        self,
        filters: List[FilterCondition] = None,
        date_filters: List[Union[RelativeDateFilter, DateRangeFilter]] = None,
        filter_groups: List[FilterGroup] = None
    ) -> str:
        """
        Build a complete WHERE clause from multiple filter sources.

        Args:
            filters: List of simple filter conditions
            date_filters: List of date filters (relative or range)
            filter_groups: List of filter groups with AND/OR logic

        Returns:
            Complete SQL WHERE clause (without the 'WHERE' keyword)
        """
        all_conditions = []

        # Process simple filters
        if filters:
            for f in filters:
                all_conditions.append(self.build_condition(f))

        # Process date filters
        if date_filters:
            for df in date_filters:
                if isinstance(df, RelativeDateFilter):
                    all_conditions.append(self.build_relative_date_condition(df))
                elif isinstance(df, DateRangeFilter):
                    all_conditions.append(self.build_date_range_condition(df))

        # Process filter groups
        if filter_groups:
            for group in filter_groups:
                all_conditions.append(f"({self.build_filter_group(group)})")

        if not all_conditions:
            return ""

        return " AND ".join(all_conditions)

    def inject_where_clause(self, sql: str, where_clause: str) -> str:
        """
        Inject a WHERE clause into an existing SQL query.

        Args:
            sql: The original SQL query
            where_clause: The WHERE clause to inject (without 'WHERE' keyword)

        Returns:
            Modified SQL query with the WHERE clause
        """
        if not where_clause:
            return sql

        # Normalize whitespace
        sql = re.sub(r'\s+', ' ', sql.strip())

        # Check if query already has WHERE
        where_match = re.search(r'\bWHERE\b', sql, re.IGNORECASE)

        if where_match:
            # Insert additional conditions after existing WHERE
            insert_pos = where_match.end()
            return f"{sql[:insert_pos]} ({where_clause}) AND {sql[insert_pos:]}"
        else:
            # Find the right place to insert WHERE
            # Look for GROUP BY, ORDER BY, LIMIT, or end of query
            patterns = [
                (r'\bGROUP\s+BY\b', 'GROUP BY'),
                (r'\bORDER\s+BY\b', 'ORDER BY'),
                (r'\bLIMIT\b', 'LIMIT'),
                (r'\bHAVING\b', 'HAVING'),
            ]

            insert_pos = len(sql)
            for pattern, _ in patterns:
                match = re.search(pattern, sql, re.IGNORECASE)
                if match and match.start() < insert_pos:
                    insert_pos = match.start()

            return f"{sql[:insert_pos].strip()} WHERE {where_clause} {sql[insert_pos:]}"

    def parse_filter_dict(self, filter_dict: Dict[str, Any]) -> List[FilterCondition]:
        """
        Parse a simple filter dictionary into FilterCondition objects.

        Args:
            filter_dict: Dictionary of column -> value mappings

        Returns:
            List of FilterCondition objects
        """
        conditions = []
        for column, value in filter_dict.items():
            if value is None or value == "" or value == []:
                continue

            if isinstance(value, list):
                conditions.append(FilterCondition(
                    column=column,
                    operator=FilterOperator.IN,
                    value=value
                ))
            else:
                conditions.append(FilterCondition(
                    column=column,
                    operator=FilterOperator.EQUALS,
                    value=value
                ))

        return conditions

    async def get_filter_options(
        self,
        execute_query_fn,
        table: str,
        schema: str,
        column: str,
        search: Optional[str] = None,
        limit: int = 100,
        existing_filters: List[FilterCondition] = None
    ) -> FilterOptionsResponse:
        """
        Get filter options (distinct values) for a column.

        Args:
            execute_query_fn: Async function to execute queries
            table: Table name
            schema: Schema name
            column: Column name
            search: Optional search string to filter values
            limit: Maximum number of values to return
            existing_filters: Existing filters to apply

        Returns:
            FilterOptionsResponse with available values
        """
        col = self.quote_identifier(column)
        table_ref = f'{self.quote_identifier(schema)}.{self.quote_identifier(table)}'

        # Build WHERE clause from existing filters
        where_clause = ""
        if existing_filters:
            # Exclude the current column from filters
            other_filters = [f for f in existing_filters if f.column != column]
            if other_filters:
                where_clause = self.build_where_clause(filters=other_filters)

        # Add search condition
        if search:
            search_condition = f"{col} LIKE '%{search.replace(chr(39), chr(39)+chr(39))}%'"
            if where_clause:
                where_clause = f"({where_clause}) AND {search_condition}"
            else:
                where_clause = search_condition

        where_sql = f"WHERE {where_clause}" if where_clause else ""

        # Query for distinct values with counts
        sql = f"""
            SELECT
                {col} as value,
                COUNT(*) as count
            FROM {table_ref}
            {where_sql}
            GROUP BY {col}
            ORDER BY count DESC, {col}
            LIMIT {limit}
        """

        try:
            result = await execute_query_fn(sql, limit)
            rows = result.get("rows", [])

            values = [
                FilterOptionValue(
                    value=row.get("value"),
                    count=row.get("count", 0)
                )
                for row in rows
                if row.get("value") is not None
            ]

            # Get total and distinct counts
            count_sql = f"""
                SELECT
                    COUNT(*) as total_count,
                    COUNT(DISTINCT {col}) as distinct_count,
                    COUNT(*) - COUNT({col}) as null_count
                FROM {table_ref}
                {where_sql}
            """
            count_result = await execute_query_fn(count_sql, 1)
            count_row = count_result.get("rows", [{}])[0]

            # Get min/max for numeric/date columns
            minmax_sql = f"""
                SELECT MIN({col}) as min_value, MAX({col}) as max_value
                FROM {table_ref}
                {where_sql}
            """
            minmax_result = await execute_query_fn(minmax_sql, 1)
            minmax_row = minmax_result.get("rows", [{}])[0]

            return FilterOptionsResponse(
                column=column,
                total_count=count_row.get("total_count", 0),
                distinct_count=count_row.get("distinct_count", 0),
                null_count=count_row.get("null_count", 0),
                values=values,
                min_value=minmax_row.get("min_value"),
                max_value=minmax_row.get("max_value")
            )

        except Exception as e:
            # Return empty response on error
            return FilterOptionsResponse(
                column=column,
                values=[],
                total_count=0,
                distinct_count=0
            )

    def generate_hierarchy_query(
        self,
        table: str,
        schema: str,
        levels: List[Dict[str, str]],
        parent_values: Dict[str, Any] = None,
        limit: int = 100
    ) -> str:
        """
        Generate a query to get hierarchy values.

        Args:
            table: Table name
            schema: Schema name
            levels: List of hierarchy levels with column info
            parent_values: Selected values from parent levels
            limit: Maximum number of values to return

        Returns:
            SQL query string
        """
        table_ref = f'{self.quote_identifier(schema)}.{self.quote_identifier(table)}'

        # Determine which level to query
        current_level = 0
        if parent_values:
            current_level = len(parent_values)

        if current_level >= len(levels):
            return ""

        level = levels[current_level]
        col = self.quote_identifier(level["column"])

        # Build WHERE clause from parent selections
        where_parts = []
        if parent_values:
            for i, (parent_col, parent_val) in enumerate(parent_values.items()):
                where_parts.append(f'{self.quote_identifier(parent_col)} = {self.escape_value(parent_val)}')

        where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

        sql = f"""
            SELECT DISTINCT {col} as value, COUNT(*) as count
            FROM {table_ref}
            {where_sql}
            GROUP BY {col}
            ORDER BY {col}
            LIMIT {limit}
        """

        return sql


# Factory function to get filter service instance
def get_filter_service(db_type: str = "postgresql") -> FilterService:
    """
    Get a FilterService instance for the specified database type.

    Args:
        db_type: Database type (postgresql, mysql, mongodb)

    Returns:
        FilterService instance
    """
    return FilterService(db_type)
