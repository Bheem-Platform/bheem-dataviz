"""MySQL connection service for managing database connections."""

import aiomysql
from urllib.parse import urlparse, parse_qs, quote_plus, unquote
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MySQLService:
    """Service for handling MySQL database connections."""

    @staticmethod
    def parse_connection_string(conn_str: str) -> Dict[str, Any]:
        """
        Parse a MySQL connection string into its components.

        Format: mysql://[user[:password]@][host][:port][/database][?param=value]

        Returns:
            dict with keys: host, port, database, username, password
        """
        try:
            parsed = urlparse(conn_str)

            # Extract query parameters
            params = parse_qs(parsed.query)

            return {
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 3306,
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
        Build a MySQL connection string from individual components.

        Returns:
            A valid MySQL connection string.
        """
        # Build the user:password part
        auth_part = ""
        if username:
            auth_part = quote_plus(username)
            if password:
                auth_part += f":{quote_plus(password)}"
            auth_part += "@"

        # Build base connection string
        conn_str = f"mysql://{auth_part}{host}:{port}/{database}"

        # Add extra parameters
        if extra:
            params = "&".join(f"{k}={quote_plus(str(v))}" for k, v in extra.items())
            conn_str += f"?{params}"

        return conn_str

    @staticmethod
    async def test_connection(
        host: str,
        port: int,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ssl: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Test a MySQL database connection.

        Returns:
            dict with keys: success, message, tables_count (if successful)
        """
        import ssl as ssl_module
        conn = None
        try:
            # Configure SSL if required
            ssl_ctx = None
            if ssl:
                ssl_ctx = ssl_module.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl_module.CERT_NONE

            # Attempt to connect with a timeout
            conn = await aiomysql.connect(
                host=host,
                port=port,
                user=username or '',
                password=password or '',
                db=database,
                connect_timeout=10,
                ssl=ssl_ctx
            )

            async with conn.cursor() as cursor:
                # Get count of tables in the database
                await cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = %s
                """, (database,))
                result = await cursor.fetchone()
                tables_count = result[0] if result else 0

                # Get MySQL version
                await cursor.execute("SELECT VERSION()")
                version_result = await cursor.fetchone()
                version = version_result[0] if version_result else "Unknown"

            return {
                "success": True,
                "message": "Connection successful",
                "tables_count": tables_count,
                "version": f"MySQL {version}"
            }

        except aiomysql.OperationalError as e:
            error_code = e.args[0] if e.args else 0
            if error_code == 1045:  # Access denied
                return {
                    "success": False,
                    "message": "Invalid username or password"
                }
            elif error_code == 1049:  # Unknown database
                return {
                    "success": False,
                    "message": f"Database '{database}' does not exist"
                }
            elif error_code == 2003:  # Can't connect to server
                return {
                    "success": False,
                    "message": f"Cannot connect to MySQL server at {host}:{port}"
                }
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_tables(
        host: str,
        port: int,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ssl: Optional[bool] = None
    ) -> List[Dict[str, str]]:
        """
        Get list of tables from the database.

        Returns:
            List of dicts with table_schema and table_name
        """
        import ssl as ssl_module
        conn = None
        try:
            ssl_ctx = None
            if ssl:
                ssl_ctx = ssl_module.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl_module.CERT_NONE

            conn = await aiomysql.connect(
                host=host,
                port=port,
                user=username or '',
                password=password or '',
                db=database,
                connect_timeout=10,
                ssl=ssl_ctx
            )

            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT table_schema, table_name, table_type
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    ORDER BY table_name
                """, (database,))
                rows = await cursor.fetchall()

            return [
                {
                    "schema": row[0],
                    "name": row[1],
                    "type": row[2]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_table_relationships(
        host: str,
        port: int,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ssl: Optional[bool] = None
    ) -> Dict[str, int]:
        """
        Get count of tables referencing each table via foreign keys.
        Returns: {table_name: reference_count}
        """
        import ssl as ssl_module
        conn = None
        try:
            ssl_ctx = None
            if ssl:
                ssl_ctx = ssl_module.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl_module.CERT_NONE

            conn = await aiomysql.connect(
                host=host,
                port=port,
                user=username or '',
                password=password or '',
                db=database,
                connect_timeout=10,
                ssl=ssl_ctx
            )

            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT
                        REFERENCED_TABLE_NAME AS referenced_table,
                        COUNT(DISTINCT TABLE_NAME) AS reference_count
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE REFERENCED_TABLE_NAME IS NOT NULL
                    AND TABLE_SCHEMA = %s
                    GROUP BY REFERENCED_TABLE_NAME
                    ORDER BY reference_count DESC
                """, (database,))
                rows = await cursor.fetchall()

            # MySQL returns table names without schema prefix
            return {f"{database}.{row[0]}": row[1] for row in rows}
        except Exception as e:
            logger.error(f"Failed to get table relationships: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_table_columns(
        host: str,
        port: int,
        database: str,
        table: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ssl: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get column information for a specific table.

        Returns:
            List of dicts with column details
        """
        import ssl as ssl_module
        conn = None
        try:
            ssl_ctx = None
            if ssl:
                ssl_ctx = ssl_module.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl_module.CERT_NONE

            conn = await aiomysql.connect(
                host=host,
                port=port,
                user=username or '',
                password=password or '',
                db=database,
                connect_timeout=10,
                ssl=ssl_ctx
            )

            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """, (database, table))
                rows = await cursor.fetchall()

            return [
                {
                    "name": row[0],
                    "type": row[1],
                    "nullable": row[2] == "YES",
                    "default": row[3]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to get columns: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    async def execute_query(
        host: str,
        port: int,
        database: str,
        sql: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        limit: int = 1000,
        ssl: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.

        Returns:
            dict with columns, rows, total count, and execution time
        """
        import time
        import ssl as ssl_module
        conn = None
        try:
            ssl_ctx = None
            if ssl:
                ssl_ctx = ssl_module.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl_module.CERT_NONE

            start_time = time.time()
            conn = await aiomysql.connect(
                host=host,
                port=port,
                user=username or '',
                password=password or '',
                db=database,
                connect_timeout=30,
                ssl=ssl_ctx
            )

            # Add LIMIT if not present (for safety)
            sql_lower = sql.lower().strip()
            if sql_lower.startswith('select') and 'limit' not in sql_lower:
                sql = f"{sql.rstrip(';')} LIMIT {limit}"

            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql)
                rows = await cursor.fetchall()
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

                return {
                    "columns": columns,
                    "rows": list(rows),
                    "total": len(rows),
                    "execution_time": round(execution_time, 3)
                }
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_table_preview(
        host: str,
        port: int,
        database: str,
        table: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        ssl: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get a preview of table data with pagination.

        Returns:
            dict with columns, rows, and total count
        """
        import time
        import ssl as ssl_module
        conn = None
        try:
            ssl_ctx = None
            if ssl:
                ssl_ctx = ssl_module.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl_module.CERT_NONE

            start_time = time.time()
            conn = await aiomysql.connect(
                host=host,
                port=port,
                user=username or '',
                password=password or '',
                db=database,
                connect_timeout=30,
                ssl=ssl_ctx
            )

            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Get total row count
                await cursor.execute(f"SELECT COUNT(*) as cnt FROM `{table}`")
                count_result = await cursor.fetchone()
                total_count = count_result['cnt'] if count_result else 0

                # Get preview rows with pagination
                await cursor.execute(f"SELECT * FROM `{table}` LIMIT {limit} OFFSET {offset}")
                rows = await cursor.fetchall()

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

            return {
                "columns": columns,
                "rows": list(rows),
                "total": total_count,
                "preview_count": len(rows),
                "execution_time": round(execution_time, 3)
            }
        except Exception as e:
            logger.error(f"Table preview failed: {e}")
            raise
        finally:
            if conn:
                conn.close()


# Singleton instance
mysql_service = MySQLService()
