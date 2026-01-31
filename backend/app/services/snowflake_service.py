"""
Snowflake Service

Service for handling Snowflake database connections,
schema discovery, and query execution.
"""

import logging
import time
from typing import Any, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Snowflake import with fallback
try:
    import snowflake.connector
    from snowflake.connector import DictCursor
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    logger.warning("snowflake-connector-python not installed. Snowflake connections will be unavailable.")


class SnowflakeService:
    """Service for handling Snowflake connections."""

    @staticmethod
    def is_available() -> bool:
        """Check if Snowflake client is available."""
        return SNOWFLAKE_AVAILABLE

    @staticmethod
    def create_connection(
        account: str,
        user: str,
        password: str,
        warehouse: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        role: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key_passphrase: Optional[str] = None,
    ):
        """
        Create a Snowflake connection.

        Args:
            account: Snowflake account identifier (e.g., "xy12345.us-east-1")
            user: Username
            password: Password (or None if using key-pair auth)
            warehouse: Warehouse to use
            database: Default database
            schema: Default schema
            role: Role to assume
            private_key_path: Path to private key file for key-pair auth
            private_key_passphrase: Passphrase for private key

        Returns:
            Snowflake connection object
        """
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake connector not available. Install snowflake-connector-python.")

        conn_params = {
            "account": account,
            "user": user,
        }

        # Authentication
        if private_key_path:
            # Key-pair authentication
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization

            with open(private_key_path, "rb") as key_file:
                p_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=private_key_passphrase.encode() if private_key_passphrase else None,
                    backend=default_backend()
                )

            pkb = p_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            conn_params["private_key"] = pkb
        else:
            # Password authentication
            conn_params["password"] = password

        # Optional parameters
        if warehouse:
            conn_params["warehouse"] = warehouse
        if database:
            conn_params["database"] = database
        if schema:
            conn_params["schema"] = schema
        if role:
            conn_params["role"] = role

        return snowflake.connector.connect(**conn_params)

    @staticmethod
    def build_connection_string(
        account: str,
        user: str,
        password: str,
        warehouse: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        role: Optional[str] = None,
    ) -> str:
        """
        Build a Snowflake connection string (URL format).

        Returns:
            Connection string in URL format
        """
        # Base URL
        conn_str = f"snowflake://{quote_plus(user)}:{quote_plus(password)}@{account}"

        # Add database/schema
        if database:
            conn_str += f"/{database}"
            if schema:
                conn_str += f"/{schema}"

        # Add query parameters
        params = []
        if warehouse:
            params.append(f"warehouse={quote_plus(warehouse)}")
        if role:
            params.append(f"role={quote_plus(role)}")

        if params:
            conn_str += "?" + "&".join(params)

        return conn_str

    @staticmethod
    def parse_connection_string(conn_str: str) -> dict[str, Any]:
        """
        Parse a Snowflake connection string.

        Returns:
            dict with connection parameters
        """
        from urllib.parse import urlparse, parse_qs, unquote

        parsed = urlparse(conn_str)
        params = parse_qs(parsed.query)

        # Parse path for database/schema
        path_parts = parsed.path.strip("/").split("/")

        return {
            "account": parsed.hostname,
            "user": unquote(parsed.username) if parsed.username else None,
            "password": unquote(parsed.password) if parsed.password else None,
            "database": path_parts[0] if len(path_parts) > 0 and path_parts[0] else None,
            "schema": path_parts[1] if len(path_parts) > 1 else None,
            "warehouse": params.get("warehouse", [None])[0],
            "role": params.get("role", [None])[0],
        }

    @staticmethod
    async def test_connection(
        account: str,
        user: str,
        password: str,
        warehouse: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        role: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Test a Snowflake connection.

        Returns:
            dict with success, message, and additional info
        """
        if not SNOWFLAKE_AVAILABLE:
            return {
                "success": False,
                "message": "Snowflake connector not installed. Run: pip install snowflake-connector-python"
            }

        conn = None
        try:
            conn = SnowflakeService.create_connection(
                account=account,
                user=user,
                password=password,
                warehouse=warehouse,
                database=database,
                schema=schema,
                role=role,
            )

            # Test by getting current context
            cursor = conn.cursor(DictCursor)

            # Get current context
            cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE(), CURRENT_ROLE()")
            context = cursor.fetchone()

            # Get database count
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()

            return {
                "success": True,
                "message": "Connection successful",
                "account": context.get("CURRENT_ACCOUNT()"),
                "user": context.get("CURRENT_USER()"),
                "database": context.get("CURRENT_DATABASE()"),
                "schema": context.get("CURRENT_SCHEMA()"),
                "warehouse": context.get("CURRENT_WAREHOUSE()"),
                "role": context.get("CURRENT_ROLE()"),
                "databases_count": len(databases),
            }

        except Exception as e:
            logger.error(f"Snowflake connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }

        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_databases(
        account: str,
        user: str,
        password: str,
        warehouse: Optional[str] = None,
        role: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get list of databases.

        Returns:
            List of database info dicts
        """
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake connector not available")

        conn = None
        try:
            conn = SnowflakeService.create_connection(
                account=account,
                user=user,
                password=password,
                warehouse=warehouse,
                role=role,
            )

            cursor = conn.cursor(DictCursor)
            cursor.execute("SHOW DATABASES")

            databases = []
            for row in cursor.fetchall():
                databases.append({
                    "name": row.get("name"),
                    "owner": row.get("owner"),
                    "created_on": str(row.get("created_on")) if row.get("created_on") else None,
                    "comment": row.get("comment"),
                    "origin": row.get("origin"),
                })

            return databases

        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_schemas(
        account: str,
        user: str,
        password: str,
        database: str,
        warehouse: Optional[str] = None,
        role: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get list of schemas in a database.

        Returns:
            List of schema info dicts
        """
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake connector not available")

        conn = None
        try:
            conn = SnowflakeService.create_connection(
                account=account,
                user=user,
                password=password,
                warehouse=warehouse,
                database=database,
                role=role,
            )

            cursor = conn.cursor(DictCursor)
            cursor.execute(f"SHOW SCHEMAS IN DATABASE {database}")

            schemas = []
            for row in cursor.fetchall():
                schemas.append({
                    "name": row.get("name"),
                    "database": database,
                    "owner": row.get("owner"),
                    "created_on": str(row.get("created_on")) if row.get("created_on") else None,
                    "comment": row.get("comment"),
                })

            return schemas

        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_tables(
        account: str,
        user: str,
        password: str,
        database: str,
        schema: Optional[str] = None,
        warehouse: Optional[str] = None,
        role: Optional[str] = None,
    ) -> list[dict[str, str]]:
        """
        Get list of tables from Snowflake.

        Returns:
            List of dicts with schema, name, and type
        """
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake connector not available")

        conn = None
        try:
            conn = SnowflakeService.create_connection(
                account=account,
                user=user,
                password=password,
                warehouse=warehouse,
                database=database,
                schema=schema,
                role=role,
            )

            cursor = conn.cursor(DictCursor)

            if schema:
                cursor.execute(f"SHOW TABLES IN SCHEMA {database}.{schema}")
            else:
                cursor.execute(f"SHOW TABLES IN DATABASE {database}")

            tables = []
            for row in cursor.fetchall():
                tables.append({
                    "schema": row.get("schema_name"),
                    "name": row.get("name"),
                    "type": row.get("kind", "TABLE"),
                    "database": row.get("database_name"),
                    "rows": row.get("rows"),
                })

            # Also get views
            if schema:
                cursor.execute(f"SHOW VIEWS IN SCHEMA {database}.{schema}")
            else:
                cursor.execute(f"SHOW VIEWS IN DATABASE {database}")

            for row in cursor.fetchall():
                tables.append({
                    "schema": row.get("schema_name"),
                    "name": row.get("name"),
                    "type": "VIEW",
                    "database": row.get("database_name"),
                })

            return tables

        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_table_columns(
        account: str,
        user: str,
        password: str,
        database: str,
        schema: str,
        table: str,
        warehouse: Optional[str] = None,
        role: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get column information for a specific table.

        Returns:
            List of dicts with column details
        """
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake connector not available")

        conn = None
        try:
            conn = SnowflakeService.create_connection(
                account=account,
                user=user,
                password=password,
                warehouse=warehouse,
                database=database,
                schema=schema,
                role=role,
            )

            cursor = conn.cursor(DictCursor)
            cursor.execute(f"DESCRIBE TABLE {database}.{schema}.{table}")

            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "name": row.get("name"),
                    "type": row.get("type"),
                    "nullable": row.get("null?") == "Y",
                    "default": row.get("default"),
                    "primary_key": row.get("primary key") == "Y",
                    "unique_key": row.get("unique key") == "Y",
                    "comment": row.get("comment"),
                })

            return columns

        finally:
            if conn:
                conn.close()

    @staticmethod
    async def execute_query(
        account: str,
        user: str,
        password: str,
        sql: str,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        warehouse: Optional[str] = None,
        role: Optional[str] = None,
        limit: int = 1000,
        timeout_seconds: int = 60,
    ) -> dict[str, Any]:
        """
        Execute a SQL query against Snowflake.

        Returns:
            dict with columns, rows, total count, and execution time
        """
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake connector not available")

        start_time = time.time()

        conn = None
        try:
            conn = SnowflakeService.create_connection(
                account=account,
                user=user,
                password=password,
                warehouse=warehouse,
                database=database,
                schema=schema,
                role=role,
            )

            # Set query timeout
            cursor = conn.cursor(DictCursor)
            cursor.execute(f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = {timeout_seconds}")

            # Add LIMIT if not present (for safety)
            sql_lower = sql.lower().strip()
            if sql_lower.startswith('select') and 'limit' not in sql_lower:
                sql = f"{sql.rstrip(';')} LIMIT {limit}"

            cursor.execute(sql)
            rows = cursor.fetchall()

            execution_time = time.time() - start_time

            if not rows:
                return {
                    "columns": [],
                    "rows": [],
                    "total": 0,
                    "execution_time": round(execution_time, 3),
                }

            columns = list(rows[0].keys()) if rows else []

            # Convert to list of dicts (already in dict format from DictCursor)
            result_rows = []
            for row in rows:
                row_dict = {}
                for k, v in row.items():
                    # Handle special types
                    if hasattr(v, 'isoformat'):
                        v = v.isoformat()
                    row_dict[k] = v
                result_rows.append(row_dict)

            return {
                "columns": columns,
                "rows": result_rows,
                "total": len(result_rows),
                "execution_time": round(execution_time, 3),
            }

        except Exception as e:
            logger.error(f"Snowflake query execution failed: {e}")
            raise

        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_table_preview(
        account: str,
        user: str,
        password: str,
        database: str,
        schema: str,
        table: str,
        warehouse: Optional[str] = None,
        role: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Get a preview of table data with pagination.

        Returns:
            dict with columns, rows, and total count
        """
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake connector not available")

        start_time = time.time()

        full_table_name = f"{database}.{schema}.{table}"

        # Get preview data
        sql = f'SELECT * FROM {full_table_name} LIMIT {limit} OFFSET {offset}'
        result = await SnowflakeService.execute_query(
            account=account,
            user=user,
            password=password,
            sql=sql,
            database=database,
            schema=schema,
            warehouse=warehouse,
            role=role,
            limit=limit,
        )

        # Get total count
        count_sql = f'SELECT COUNT(*) AS cnt FROM {full_table_name}'
        count_result = await SnowflakeService.execute_query(
            account=account,
            user=user,
            password=password,
            sql=count_sql,
            database=database,
            schema=schema,
            warehouse=warehouse,
            role=role,
            limit=1,
        )

        total = count_result["rows"][0]["CNT"] if count_result["rows"] else 0

        return {
            "columns": result["columns"],
            "rows": result["rows"],
            "total": total,
            "preview_count": len(result["rows"]),
            "execution_time": result["execution_time"],
        }

    @staticmethod
    async def get_warehouses(
        account: str,
        user: str,
        password: str,
        role: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get list of available warehouses.

        Returns:
            List of warehouse info dicts
        """
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake connector not available")

        conn = None
        try:
            conn = SnowflakeService.create_connection(
                account=account,
                user=user,
                password=password,
                role=role,
            )

            cursor = conn.cursor(DictCursor)
            cursor.execute("SHOW WAREHOUSES")

            warehouses = []
            for row in cursor.fetchall():
                warehouses.append({
                    "name": row.get("name"),
                    "state": row.get("state"),
                    "type": row.get("type"),
                    "size": row.get("size"),
                    "auto_suspend": row.get("auto_suspend"),
                    "auto_resume": row.get("auto_resume"),
                })

            return warehouses

        finally:
            if conn:
                conn.close()


# Singleton instance
snowflake_service = SnowflakeService()
