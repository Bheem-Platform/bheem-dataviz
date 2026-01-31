"""
BigQuery Service

Service for handling Google BigQuery database connections,
schema discovery, and query execution.
"""

import logging
import json
import time
from typing import Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# BigQuery import with fallback
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    logger.warning("google-cloud-bigquery not installed. BigQuery connections will be unavailable.")


class BigQueryService:
    """Service for handling Google BigQuery connections."""

    @staticmethod
    def is_available() -> bool:
        """Check if BigQuery client is available."""
        return BIGQUERY_AVAILABLE

    @staticmethod
    def create_client(
        project_id: str,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ) -> "bigquery.Client":
        """
        Create a BigQuery client.

        Args:
            project_id: GCP project ID
            credentials_json: JSON string of service account credentials
            credentials_path: Path to service account JSON file

        Returns:
            BigQuery Client instance
        """
        if not BIGQUERY_AVAILABLE:
            raise RuntimeError("BigQuery client not available. Install google-cloud-bigquery.")

        credentials = None

        if credentials_json:
            # Parse JSON credentials string
            try:
                creds_dict = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(creds_dict)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid credentials JSON: {e}")

        elif credentials_path:
            # Load from file path
            path = Path(credentials_path)
            if not path.exists():
                raise ValueError(f"Credentials file not found: {credentials_path}")
            credentials = service_account.Credentials.from_service_account_file(str(path))

        # Create client
        return bigquery.Client(project=project_id, credentials=credentials)

    @staticmethod
    async def test_connection(
        project_id: str,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Test a BigQuery connection.

        Returns:
            dict with success, message, and additional info
        """
        if not BIGQUERY_AVAILABLE:
            return {
                "success": False,
                "message": "BigQuery client not installed. Run: pip install google-cloud-bigquery"
            }

        try:
            client = BigQueryService.create_client(
                project_id=project_id,
                credentials_json=credentials_json,
                credentials_path=credentials_path,
            )

            # Test by listing datasets
            datasets = list(client.list_datasets(max_results=10))

            return {
                "success": True,
                "message": "Connection successful",
                "datasets_count": len(datasets),
                "project_id": project_id,
                "datasets": [ds.dataset_id for ds in datasets[:5]],
            }

        except Exception as e:
            logger.error(f"BigQuery connection test failed: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }

    @staticmethod
    async def get_datasets(
        project_id: str,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get list of datasets in the project.

        Returns:
            List of dataset info dicts
        """
        if not BIGQUERY_AVAILABLE:
            raise RuntimeError("BigQuery client not available")

        client = BigQueryService.create_client(
            project_id=project_id,
            credentials_json=credentials_json,
            credentials_path=credentials_path,
        )

        datasets = []
        for dataset in client.list_datasets():
            dataset_ref = client.dataset(dataset.dataset_id)
            full_dataset = client.get_dataset(dataset_ref)

            datasets.append({
                "id": dataset.dataset_id,
                "project": dataset.project,
                "description": full_dataset.description,
                "location": full_dataset.location,
                "created": full_dataset.created.isoformat() if full_dataset.created else None,
                "modified": full_dataset.modified.isoformat() if full_dataset.modified else None,
            })

        return datasets

    @staticmethod
    async def get_tables(
        project_id: str,
        dataset_id: Optional[str] = None,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ) -> list[dict[str, str]]:
        """
        Get list of tables from BigQuery.

        Args:
            project_id: GCP project ID
            dataset_id: Specific dataset to list (optional)
            credentials_json: Service account credentials JSON
            credentials_path: Path to credentials file

        Returns:
            List of dicts with schema (dataset), name, and type
        """
        if not BIGQUERY_AVAILABLE:
            raise RuntimeError("BigQuery client not available")

        client = BigQueryService.create_client(
            project_id=project_id,
            credentials_json=credentials_json,
            credentials_path=credentials_path,
        )

        tables = []

        if dataset_id:
            # List tables from specific dataset
            dataset_ref = client.dataset(dataset_id)
            for table in client.list_tables(dataset_ref):
                tables.append({
                    "schema": dataset_id,
                    "name": table.table_id,
                    "type": table.table_type,
                    "full_id": f"{project_id}.{dataset_id}.{table.table_id}",
                })
        else:
            # List tables from all datasets
            for dataset in client.list_datasets():
                dataset_ref = client.dataset(dataset.dataset_id)
                for table in client.list_tables(dataset_ref):
                    tables.append({
                        "schema": dataset.dataset_id,
                        "name": table.table_id,
                        "type": table.table_type,
                        "full_id": f"{project_id}.{dataset.dataset_id}.{table.table_id}",
                    })

        return tables

    @staticmethod
    async def get_table_columns(
        project_id: str,
        dataset_id: str,
        table_id: str,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get column information for a specific table.

        Returns:
            List of dicts with column details
        """
        if not BIGQUERY_AVAILABLE:
            raise RuntimeError("BigQuery client not available")

        client = BigQueryService.create_client(
            project_id=project_id,
            credentials_json=credentials_json,
            credentials_path=credentials_path,
        )

        table_ref = client.dataset(dataset_id).table(table_id)
        table = client.get_table(table_ref)

        columns = []
        for field in table.schema:
            columns.append({
                "name": field.name,
                "type": field.field_type,
                "mode": field.mode,  # NULLABLE, REQUIRED, REPEATED
                "description": field.description,
                "nullable": field.mode != "REQUIRED",
            })

        return columns

    @staticmethod
    async def get_table_info(
        project_id: str,
        dataset_id: str,
        table_id: str,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get detailed table information.

        Returns:
            Dict with table metadata
        """
        if not BIGQUERY_AVAILABLE:
            raise RuntimeError("BigQuery client not available")

        client = BigQueryService.create_client(
            project_id=project_id,
            credentials_json=credentials_json,
            credentials_path=credentials_path,
        )

        table_ref = client.dataset(dataset_id).table(table_id)
        table = client.get_table(table_ref)

        return {
            "project": table.project,
            "dataset": table.dataset_id,
            "table": table.table_id,
            "full_id": f"{table.project}.{table.dataset_id}.{table.table_id}",
            "type": table.table_type,
            "num_rows": table.num_rows,
            "num_bytes": table.num_bytes,
            "created": table.created.isoformat() if table.created else None,
            "modified": table.modified.isoformat() if table.modified else None,
            "description": table.description,
            "partitioning": {
                "type": table.time_partitioning.type_ if table.time_partitioning else None,
                "field": table.time_partitioning.field if table.time_partitioning else None,
            } if table.time_partitioning else None,
            "clustering_fields": table.clustering_fields,
        }

    @staticmethod
    async def execute_query(
        project_id: str,
        sql: str,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
        limit: int = 1000,
        timeout_seconds: int = 60,
    ) -> dict[str, Any]:
        """
        Execute a SQL query against BigQuery.

        Returns:
            dict with columns, rows, total count, and execution time
        """
        if not BIGQUERY_AVAILABLE:
            raise RuntimeError("BigQuery client not available")

        start_time = time.time()

        client = BigQueryService.create_client(
            project_id=project_id,
            credentials_json=credentials_json,
            credentials_path=credentials_path,
        )

        # Add LIMIT if not present (for safety)
        sql_lower = sql.lower().strip()
        if sql_lower.startswith('select') and 'limit' not in sql_lower:
            sql = f"{sql.rstrip(';')} LIMIT {limit}"

        # Configure query job
        job_config = bigquery.QueryJobConfig(
            use_legacy_sql=False,
            timeout_ms=timeout_seconds * 1000,
        )

        try:
            # Run the query
            query_job = client.query(sql, job_config=job_config)

            # Wait for results
            results = query_job.result(timeout=timeout_seconds)

            execution_time = time.time() - start_time

            # Get schema for column names
            columns = [field.name for field in results.schema] if results.schema else []

            # Convert to list of dicts
            rows = []
            for row in results:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Handle BigQuery-specific types
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[col] = value
                rows.append(row_dict)

            return {
                "columns": columns,
                "rows": rows,
                "total": len(rows),
                "total_bytes_processed": query_job.total_bytes_processed,
                "total_bytes_billed": query_job.total_bytes_billed,
                "cache_hit": query_job.cache_hit,
                "execution_time": round(execution_time, 3),
            }

        except Exception as e:
            logger.error(f"BigQuery query execution failed: {e}")
            raise

    @staticmethod
    async def get_table_preview(
        project_id: str,
        dataset_id: str,
        table_id: str,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Get a preview of table data with pagination.

        Returns:
            dict with columns, rows, and total count
        """
        if not BIGQUERY_AVAILABLE:
            raise RuntimeError("BigQuery client not available")

        start_time = time.time()

        # Build preview query
        full_table_id = f"`{project_id}.{dataset_id}.{table_id}`"

        sql = f"""
            SELECT *
            FROM {full_table_id}
            LIMIT {limit}
            OFFSET {offset}
        """

        result = await BigQueryService.execute_query(
            project_id=project_id,
            sql=sql,
            credentials_json=credentials_json,
            credentials_path=credentials_path,
            limit=limit,
        )

        # Get total row count
        count_sql = f"SELECT COUNT(*) as cnt FROM {full_table_id}"
        count_result = await BigQueryService.execute_query(
            project_id=project_id,
            sql=count_sql,
            credentials_json=credentials_json,
            credentials_path=credentials_path,
            limit=1,
        )

        total = count_result["rows"][0]["cnt"] if count_result["rows"] else 0

        return {
            "columns": result["columns"],
            "rows": result["rows"],
            "total": total,
            "preview_count": len(result["rows"]),
            "execution_time": result["execution_time"],
        }

    @staticmethod
    async def estimate_query_cost(
        project_id: str,
        sql: str,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Estimate the cost of running a query (dry run).

        Returns:
            dict with estimated bytes processed and cost
        """
        if not BIGQUERY_AVAILABLE:
            raise RuntimeError("BigQuery client not available")

        client = BigQueryService.create_client(
            project_id=project_id,
            credentials_json=credentials_json,
            credentials_path=credentials_path,
        )

        # Configure dry run
        job_config = bigquery.QueryJobConfig(
            dry_run=True,
            use_legacy_sql=False,
        )

        try:
            query_job = client.query(sql, job_config=job_config)

            # BigQuery pricing: $5 per TB processed
            bytes_processed = query_job.total_bytes_processed
            cost_per_tb = 5.0
            estimated_cost = (bytes_processed / (1024 ** 4)) * cost_per_tb

            return {
                "bytes_processed": bytes_processed,
                "bytes_processed_formatted": BigQueryService._format_bytes(bytes_processed),
                "estimated_cost_usd": round(estimated_cost, 6),
                "estimated_cost_formatted": f"${estimated_cost:.6f}",
            }

        except Exception as e:
            logger.error(f"Query cost estimation failed: {e}")
            raise

    @staticmethod
    def _format_bytes(size: int) -> str:
        """Format bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"


# Singleton instance
bigquery_service = BigQueryService()
