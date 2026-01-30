"""PostgreSQL connection service for managing database connections."""

import asyncpg
from urllib.parse import urlparse, parse_qs, quote_plus, unquote
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class PostgresService:
    """Service for handling PostgreSQL database connections."""

    @staticmethod
    def normalize_connection_string(conn_str: str) -> str:
        """
        Normalize connection string for asyncpg.
        Removes +asyncpg suffix if present since asyncpg expects plain postgresql://
        """
        # asyncpg expects postgresql:// not postgresql+asyncpg://
        return conn_str.replace("postgresql+asyncpg://", "postgresql://")

    @staticmethod
    def parse_connection_string(conn_str: str) -> Dict[str, Any]:
        """
        Parse a PostgreSQL connection string into its components.

        Format: postgresql://[user[:password]@][host][:port][/database][?param=value]

        Returns:
            dict with keys: host, port, database, username, password
        """
        try:
            parsed = urlparse(conn_str)

            # Extract query parameters
            params = parse_qs(parsed.query)

            return {
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 5432,
                "database": parsed.path.lstrip("/") if parsed.path else None,
                "username": unquote(parsed.username) if parsed.username else None,
                "password": unquote(parsed.password) if parsed.password else None,
                "extra": {k: v[0] for k, v in params.items()} if params else None
            }
        except Exception as e:
            logger.error(f"Failed to parse connection string: {e}")
            raise ValueError(f"Invalid connection string format: {e}")

    @staticmethod
    def build_connection_string(
        host: str,
        port: int,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a PostgreSQL connection string from individual components.

        Returns:
            A valid PostgreSQL connection string.
        """
        # Build the user:password part
        auth_part = ""
        if username:
            auth_part = quote_plus(username)
            if password:
                auth_part += f":{quote_plus(password)}"
            auth_part += "@"

        # Build base connection string
        conn_str = f"postgresql://{auth_part}{host}:{port}/{database}"

        # Add extra parameters
        if extra:
            params = "&".join(f"{k}={quote_plus(str(v))}" for k, v in extra.items())
            conn_str += f"?{params}"

        return conn_str

    @staticmethod
    async def test_connection(connection_string: str) -> Dict[str, Any]:
        """
        Test a PostgreSQL database connection.

        Returns:
            dict with keys: success, message, tables_count (if successful)
        """
        conn = None
        try:
            # Normalize connection string for asyncpg
            conn_str = PostgresService.normalize_connection_string(connection_string)
            # Attempt to connect with a timeout
            conn = await asyncpg.connect(conn_str, timeout=10)

            # Get count of tables in the database
            tables_count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            """)

            # Get database version for additional info
            version = await conn.fetchval("SELECT version()")

            return {
                "success": True,
                "message": "Connection successful",
                "tables_count": tables_count,
                "version": version
            }
        except asyncpg.InvalidCatalogNameError as e:
            return {
                "success": False,
                "message": f"Database does not exist: {e}"
            }
        except asyncpg.InvalidPasswordError:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
        except asyncpg.CannotConnectNowError as e:
            return {
                "success": False,
                "message": f"Cannot connect to database: {e}"
            }
        except OSError as e:
            return {
                "success": False,
                "message": f"Connection failed: Unable to reach host ({e})"
            }
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
        finally:
            if conn:
                await conn.close()

    @staticmethod
    async def get_tables(connection_string: str) -> List[Dict[str, str]]:
        """
        Get list of tables from the database.

        Returns:
            List of dicts with table_schema and table_name
        """
        conn = None
        try:
            conn_str = PostgresService.normalize_connection_string(connection_string)
            conn = await asyncpg.connect(conn_str, timeout=10)

            rows = await conn.fetch("""
                SELECT table_schema, table_name, table_type
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name
            """)

            return [
                {
                    "schema": row["table_schema"],
                    "name": row["table_name"],
                    "type": row["table_type"]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    @staticmethod
    async def get_table_relationships(connection_string: str) -> Dict[str, int]:
        """
        Get count of tables referencing each table via foreign keys.
        Returns: {table_name: reference_count} where table_name is schema.table
        """
        conn = None
        try:
            conn_str = PostgresService.normalize_connection_string(connection_string)
            conn = await asyncpg.connect(conn_str, timeout=10)

            rows = await conn.fetch("""
                SELECT
                    ccu.table_schema || '.' || ccu.table_name AS referenced_table,
                    COUNT(DISTINCT tc.table_name) AS reference_count
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                    AND tc.table_schema = ccu.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND ccu.table_schema NOT IN ('pg_catalog', 'information_schema')
                GROUP BY ccu.table_schema, ccu.table_name
                ORDER BY reference_count DESC
            """)

            return {row["referenced_table"]: row["reference_count"] for row in rows}
        except Exception as e:
            logger.error(f"Failed to get table relationships: {e}")
            return {}
        finally:
            if conn:
                await conn.close()

    @staticmethod
    async def get_table_columns(connection_string: str, schema: str, table: str) -> List[Dict[str, Any]]:
        """
        Get column information for a specific table.

        Returns:
            List of dicts with column details
        """
        conn = None
        try:
            conn_str = PostgresService.normalize_connection_string(connection_string)
            conn = await asyncpg.connect(conn_str, timeout=10)

            rows = await conn.fetch("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = $1 AND table_name = $2
                ORDER BY ordinal_position
            """, schema, table)

            return [
                {
                    "name": row["column_name"],
                    "type": row["data_type"],
                    "nullable": row["is_nullable"] == "YES",
                    "default": row["column_default"]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to get columns: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    @staticmethod
    async def execute_query(connection_string: str, sql: str, limit: int = 1000) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.

        Returns:
            dict with columns, rows, total count, and execution time
        """
        import time
        conn = None
        try:
            start_time = time.time()
            conn_str = PostgresService.normalize_connection_string(connection_string)
            conn = await asyncpg.connect(conn_str, timeout=30)

            # Add LIMIT if not present (for safety)
            sql_lower = sql.lower().strip()
            if sql_lower.startswith('select') and 'limit' not in sql_lower:
                sql = f"{sql.rstrip(';')} LIMIT {limit}"

            rows = await conn.fetch(sql)
            execution_time = time.time() - start_time

            if not rows:
                return {
                    "columns": [],
                    "rows": [],
                    "total": 0,
                    "execution_time": round(execution_time, 3)
                }

            # Extract column names from first row
            columns = list(rows[0].keys())

            # Convert rows to list of dicts
            result_rows = [dict(row) for row in rows]

            return {
                "columns": columns,
                "rows": result_rows,
                "total": len(result_rows),
                "execution_time": round(execution_time, 3)
            }
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    @staticmethod
    async def get_table_preview(connection_string: str, schema: str, table: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get a preview of table data with pagination.

        Returns:
            dict with columns, rows, and total count
        """
        import time
        conn = None
        try:
            start_time = time.time()
            conn_str = PostgresService.normalize_connection_string(connection_string)
            conn = await asyncpg.connect(conn_str, timeout=30)

            # Get total row count
            count_result = await conn.fetchval(f"""
                SELECT COUNT(*) FROM "{schema}"."{table}"
            """)

            # Get preview rows with pagination
            rows = await conn.fetch(f"""
                SELECT * FROM "{schema}"."{table}" LIMIT {limit} OFFSET {offset}
            """)

            execution_time = time.time() - start_time

            if not rows:
                return {
                    "columns": [],
                    "rows": [],
                    "total": 0,
                    "preview_count": 0,
                    "execution_time": round(execution_time, 3)
                }

            columns = list(rows[0].keys())
            result_rows = [dict(row) for row in rows]

            return {
                "columns": columns,
                "rows": result_rows,
                "total": count_result,
                "preview_count": len(result_rows),
                "execution_time": round(execution_time, 3)
            }
        except Exception as e:
            logger.error(f"Table preview failed: {e}")
            raise
        finally:
            if conn:
                await conn.close()


# Singleton instance
postgres_service = PostgresService()
