"""
Data Profiler Service for Quick Charts feature.

Analyzes database tables to understand data characteristics
(column types, cardinality, statistics) for intelligent chart recommendations.
"""

import asyncpg
import logging
from typing import List, Dict, Any, Optional
from app.schemas.quickchart import (
    ColumnDataType,
    Cardinality,
    ColumnProfile,
    TableProfile,
    TopValue,
    TableSummary,
)
from app.services.postgres_service import PostgresService

logger = logging.getLogger(__name__)


class DataProfiler:
    """
    Analyzes database tables to understand data characteristics
    for intelligent chart recommendations.
    """

    # SQL type mappings
    NUMERIC_TYPES = {
        'integer', 'bigint', 'smallint', 'decimal', 'numeric',
        'real', 'double precision', 'float', 'int', 'tinyint',
        'int4', 'int8', 'int2', 'float4', 'float8', 'money'
    }
    TEMPORAL_TYPES = {
        'date', 'timestamp', 'datetime', 'time',
        'timestamp with time zone', 'timestamp without time zone',
        'timestamptz', 'timetz'
    }
    BOOLEAN_TYPES = {'boolean', 'bool', 'bit'}

    async def profile_table(
        self,
        connection_string: str,
        schema: str,
        table: str,
        sample_size: int = 10000
    ) -> TableProfile:
        """
        Profile a table and return column statistics.

        Args:
            connection_string: Database connection string
            schema: Schema name
            table: Table name
            sample_size: Maximum rows to sample for statistics

        Returns:
            TableProfile with column statistics and insights
        """
        conn = None
        try:
            conn_str = PostgresService.normalize_connection_string(connection_string)
            conn = await asyncpg.connect(conn_str, timeout=30)

            # 1. Get row count
            row_count = await self._get_row_count(conn, schema, table)

            # 2. Get column metadata
            columns_meta = await self._get_columns_metadata(conn, schema, table)

            # 3. Profile each column
            column_profiles = []
            for col_meta in columns_meta:
                profile = await self._profile_column(
                    conn, schema, table, col_meta, row_count, sample_size
                )
                column_profiles.append(profile)

            # 4. Derive insights
            has_temporal = any(c.data_type == ColumnDataType.TEMPORAL for c in column_profiles)
            has_numeric = any(c.data_type == ColumnDataType.NUMERIC for c in column_profiles)
            has_categorical = any(c.data_type == ColumnDataType.CATEGORICAL for c in column_profiles)

            suggested_dimensions = self._suggest_dimensions(column_profiles)
            suggested_measures = self._suggest_measures(column_profiles)

            return TableProfile(
                connection_id="",  # Will be set by caller
                schema_name=schema,
                table_name=table,
                row_count=row_count,
                columns=column_profiles,
                has_temporal=has_temporal,
                has_numeric=has_numeric,
                has_categorical=has_categorical,
                suggested_dimensions=suggested_dimensions,
                suggested_measures=suggested_measures
            )

        except Exception as e:
            logger.error(f"Failed to profile table {schema}.{table}: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    async def get_tables_summary(
        self,
        connection_string: str
    ) -> List[TableSummary]:
        """
        Get summary of all tables for quick chart selection.
        """
        conn = None
        try:
            conn_str = PostgresService.normalize_connection_string(connection_string)
            conn = await asyncpg.connect(conn_str, timeout=30)

            # Get tables with column info
            rows = await conn.fetch("""
                SELECT
                    t.table_schema,
                    t.table_name,
                    COUNT(c.column_name) as column_count,
                    BOOL_OR(c.data_type IN ('integer', 'bigint', 'smallint', 'decimal', 'numeric', 'real', 'double precision', 'float', 'money')) as has_numeric,
                    BOOL_OR(c.data_type IN ('date', 'timestamp', 'timestamp with time zone', 'timestamp without time zone', 'time')) as has_temporal
                FROM information_schema.tables t
                JOIN information_schema.columns c
                    ON t.table_schema = c.table_schema
                    AND t.table_name = c.table_name
                WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
                    AND t.table_type = 'BASE TABLE'
                GROUP BY t.table_schema, t.table_name
                ORDER BY t.table_schema, t.table_name
            """)

            summaries = []
            for row in rows:
                # Get row count estimate from pg_stat
                count_row = await conn.fetchrow("""
                    SELECT reltuples::bigint as estimate
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = $1 AND c.relname = $2
                """, row['table_schema'], row['table_name'])

                row_count = count_row['estimate'] if count_row else None
                # If estimate is -1 or 0, try exact count for small tables
                if row_count is not None and row_count <= 0:
                    try:
                        exact = await conn.fetchval(
                            f'SELECT COUNT(*) FROM "{row["table_schema"]}"."{row["table_name"]}" LIMIT 100001'
                        )
                        row_count = exact if exact <= 100000 else None
                    except Exception:
                        row_count = None

                summaries.append(TableSummary(
                    schema_name=row['table_schema'],
                    table_name=row['table_name'],
                    row_count=int(row_count) if row_count else None,
                    column_count=row['column_count'],
                    has_numeric=row['has_numeric'] or False,
                    has_temporal=row['has_temporal'] or False
                ))

            return summaries

        except Exception as e:
            logger.error(f"Failed to get tables summary: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    async def _get_row_count(self, conn, schema: str, table: str) -> int:
        """Get exact row count for a table."""
        try:
            count = await conn.fetchval(f'''
                SELECT COUNT(*) FROM "{schema}"."{table}"
            ''')
            return count
        except Exception as e:
            logger.warning(f"Failed to get row count: {e}")
            return 0

    async def _get_columns_metadata(
        self,
        conn,
        schema: str,
        table: str
    ) -> List[Dict[str, Any]]:
        """Get column metadata from information_schema."""
        rows = await conn.fetch("""
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
        """, schema, table)

        return [
            {
                "name": row["column_name"],
                "type": row["data_type"],
                "nullable": row["is_nullable"] == "YES"
            }
            for row in rows
        ]

    async def _profile_column(
        self,
        conn,
        schema: str,
        table: str,
        col_meta: Dict[str, Any],
        total_rows: int,
        sample_size: int
    ) -> ColumnProfile:
        """Profile a single column with statistics."""
        col_name = col_meta["name"]
        sql_type = col_meta["type"]
        data_type = self._categorize_type(sql_type)

        # Get basic stats (null count, distinct count)
        stats = await self._get_column_stats(
            conn, schema, table, col_name, data_type, sample_size
        )

        # Calculate cardinality
        cardinality = self._calculate_cardinality(stats.get("distinct_count", 0))

        # Refine data type based on cardinality
        # High cardinality text columns are "text", low cardinality are "categorical"
        if data_type == ColumnDataType.CATEGORICAL and cardinality == Cardinality.HIGH:
            data_type = ColumnDataType.TEXT

        return ColumnProfile(
            name=col_name,
            sql_type=sql_type,
            data_type=data_type,
            row_count=total_rows,
            null_count=stats.get("null_count", 0),
            null_percent=round(stats.get("null_count", 0) / total_rows * 100, 2) if total_rows > 0 else 0,
            distinct_count=stats.get("distinct_count", 0),
            cardinality=cardinality,
            min_value=stats.get("min_value"),
            max_value=stats.get("max_value"),
            mean=stats.get("mean"),
            top_values=stats.get("top_values")
        )

    async def _get_column_stats(
        self,
        conn,
        schema: str,
        table: str,
        column: str,
        data_type: ColumnDataType,
        sample_size: int
    ) -> Dict[str, Any]:
        """Get statistics for a column based on its type."""
        stats = {}

        try:
            # Basic stats for all columns
            basic_stats = await conn.fetchrow(f'''
                SELECT
                    COUNT(*) - COUNT("{column}") as null_count,
                    COUNT(DISTINCT "{column}") as distinct_count
                FROM (
                    SELECT "{column}" FROM "{schema}"."{table}" LIMIT {sample_size}
                ) sample
            ''')

            stats["null_count"] = basic_stats["null_count"]
            stats["distinct_count"] = basic_stats["distinct_count"]

            # Numeric-specific stats
            if data_type == ColumnDataType.NUMERIC:
                num_stats = await conn.fetchrow(f'''
                    SELECT
                        MIN("{column}") as min_value,
                        MAX("{column}") as max_value,
                        AVG("{column}")::float as mean
                    FROM (
                        SELECT "{column}" FROM "{schema}"."{table}"
                        WHERE "{column}" IS NOT NULL
                        LIMIT {sample_size}
                    ) sample
                ''')
                stats["min_value"] = num_stats["min_value"]
                stats["max_value"] = num_stats["max_value"]
                stats["mean"] = round(num_stats["mean"], 2) if num_stats["mean"] else None

            # Temporal-specific stats
            elif data_type == ColumnDataType.TEMPORAL:
                time_stats = await conn.fetchrow(f'''
                    SELECT
                        MIN("{column}") as min_value,
                        MAX("{column}") as max_value
                    FROM (
                        SELECT "{column}" FROM "{schema}"."{table}"
                        WHERE "{column}" IS NOT NULL
                        LIMIT {sample_size}
                    ) sample
                ''')
                stats["min_value"] = str(time_stats["min_value"]) if time_stats["min_value"] else None
                stats["max_value"] = str(time_stats["max_value"]) if time_stats["max_value"] else None

            # Categorical-specific stats (top values)
            elif data_type == ColumnDataType.CATEGORICAL and stats["distinct_count"] <= 100:
                top_rows = await conn.fetch(f'''
                    SELECT
                        "{column}"::text as value,
                        COUNT(*) as count
                    FROM (
                        SELECT "{column}" FROM "{schema}"."{table}" LIMIT {sample_size}
                    ) sample
                    WHERE "{column}" IS NOT NULL
                    GROUP BY "{column}"
                    ORDER BY count DESC
                    LIMIT 10
                ''')

                total_for_percent = sum(row["count"] for row in top_rows)
                stats["top_values"] = [
                    TopValue(
                        value=row["value"],
                        count=row["count"],
                        percent=round(row["count"] / total_for_percent * 100, 1) if total_for_percent > 0 else 0
                    )
                    for row in top_rows
                ]

        except Exception as e:
            logger.warning(f"Failed to get stats for column {column}: {e}")

        return stats

    def _categorize_type(self, sql_type: str) -> ColumnDataType:
        """Categorize SQL type into data type for chart selection."""
        sql_type_lower = sql_type.lower()

        # Check for numeric types
        for num_type in self.NUMERIC_TYPES:
            if num_type in sql_type_lower:
                return ColumnDataType.NUMERIC

        # Check for temporal types
        for temp_type in self.TEMPORAL_TYPES:
            if temp_type in sql_type_lower:
                return ColumnDataType.TEMPORAL

        # Check for boolean types
        for bool_type in self.BOOLEAN_TYPES:
            if bool_type in sql_type_lower:
                return ColumnDataType.BOOLEAN

        # Text types default to categorical (will be refined by cardinality)
        if 'char' in sql_type_lower or 'text' in sql_type_lower or 'varchar' in sql_type_lower:
            return ColumnDataType.CATEGORICAL

        # UUID, JSON, etc. are unknown
        return ColumnDataType.UNKNOWN

    def _calculate_cardinality(self, distinct_count: int) -> Cardinality:
        """Calculate cardinality classification."""
        if distinct_count < 10:
            return Cardinality.LOW
        elif distinct_count <= 100:
            return Cardinality.MEDIUM
        else:
            return Cardinality.HIGH

    def _suggest_dimensions(self, columns: List[ColumnProfile]) -> List[str]:
        """Suggest columns suitable for dimensions (GROUP BY)."""
        dimensions = []
        for col in columns:
            # Temporal columns are good dimensions
            if col.data_type == ColumnDataType.TEMPORAL:
                dimensions.append(col.name)
            # Low/medium cardinality categorical columns are good dimensions
            elif col.data_type == ColumnDataType.CATEGORICAL:
                if col.cardinality in [Cardinality.LOW, Cardinality.MEDIUM]:
                    dimensions.append(col.name)
            # Boolean columns can be dimensions
            elif col.data_type == ColumnDataType.BOOLEAN:
                dimensions.append(col.name)
        return dimensions

    def _suggest_measures(self, columns: List[ColumnProfile]) -> List[str]:
        """Suggest columns suitable for measures (aggregation)."""
        measures = []
        for col in columns:
            if col.data_type == ColumnDataType.NUMERIC:
                measures.append(col.name)
        return measures


# Singleton instance
data_profiler = DataProfiler()
