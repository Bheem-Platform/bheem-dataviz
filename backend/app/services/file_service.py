"""Service for handling CSV and Excel file uploads and data table management."""

import pandas as pd
import asyncpg
import uuid
import io
import tempfile
import os
from typing import Dict, Any, List, Optional, BinaryIO
import logging

logger = logging.getLogger(__name__)


# Mapping from pandas dtype to PostgreSQL types
DTYPE_TO_SQL = {
    'int64': 'BIGINT',
    'int32': 'INTEGER',
    'int16': 'SMALLINT',
    'int8': 'SMALLINT',
    'float64': 'DOUBLE PRECISION',
    'float32': 'REAL',
    'bool': 'BOOLEAN',
    'datetime64[ns]': 'TIMESTAMP',
    'datetime64[ns, UTC]': 'TIMESTAMPTZ',
    'object': 'TEXT',
    'string': 'TEXT',
    'category': 'TEXT',
}


class FileService:
    """Service for parsing CSV/Excel files and managing uploaded data tables."""

    # Temporary storage for file previews (in-memory for simplicity)
    # In production, use Redis or file storage
    _temp_files: Dict[str, pd.DataFrame] = {}

    @staticmethod
    def _sanitize_column_name(name: str) -> str:
        """Sanitize column name for PostgreSQL."""
        # Replace spaces and special chars with underscore
        sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in str(name))
        # Ensure it starts with a letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = f'col_{sanitized}'
        # Handle empty names
        if not sanitized:
            sanitized = 'unnamed_column'
        return sanitized.lower()

    @staticmethod
    def _detect_column_type(series: pd.Series) -> str:
        """Detect the best SQL type for a pandas Series."""
        dtype_str = str(series.dtype)

        # Check for specific dtypes
        if dtype_str in DTYPE_TO_SQL:
            return DTYPE_TO_SQL[dtype_str]

        # For object dtype, try to infer better types
        if dtype_str == 'object':
            # Try numeric conversion
            try:
                numeric = pd.to_numeric(series.dropna(), errors='raise')
                if numeric.dtype in ['int64', 'int32']:
                    return 'BIGINT'
                return 'DOUBLE PRECISION'
            except (ValueError, TypeError):
                pass

            # Try datetime conversion
            try:
                pd.to_datetime(series.dropna(), errors='raise')
                return 'TIMESTAMP'
            except (ValueError, TypeError):
                pass

            # Try boolean detection
            unique_vals = set(series.dropna().str.lower().unique()) if hasattr(series, 'str') else set()
            if unique_vals and unique_vals.issubset({'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}):
                return 'BOOLEAN'

        return 'TEXT'

    @staticmethod
    def detect_column_types(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect SQL types for all columns in a DataFrame."""
        columns = []
        for col_name in df.columns:
            sanitized_name = FileService._sanitize_column_name(col_name)
            detected_type = FileService._detect_column_type(df[col_name])
            columns.append({
                'original_name': str(col_name),
                'name': sanitized_name,
                'type': detected_type,
                'nullable': df[col_name].isna().any()
            })
        return columns

    @staticmethod
    def parse_csv(
        file_content: bytes,
        delimiter: str = ',',
        has_header: bool = True,
        encoding: str = 'utf-8'
    ) -> pd.DataFrame:
        """Parse a CSV file into a DataFrame."""
        try:
            # Try specified encoding first, fall back to others
            encodings = [encoding, 'utf-8', 'latin-1', 'cp1252']
            df = None
            last_error = None

            for enc in encodings:
                try:
                    df = pd.read_csv(
                        io.BytesIO(file_content),
                        delimiter=delimiter,
                        header=0 if has_header else None,
                        encoding=enc,
                        on_bad_lines='warn'
                    )
                    break
                except UnicodeDecodeError as e:
                    last_error = e
                    continue

            if df is None:
                raise ValueError(f"Could not decode file with any encoding: {last_error}")

            # If no header, create column names
            if not has_header:
                df.columns = [f'column_{i+1}' for i in range(len(df.columns))]

            return df
        except Exception as e:
            logger.error(f"Failed to parse CSV: {e}")
            raise ValueError(f"Failed to parse CSV file: {e}")

    @staticmethod
    def parse_excel(
        file_content: bytes,
        sheet_name: Optional[str] = None,
        has_header: bool = True
    ) -> pd.DataFrame:
        """Parse an Excel file into a DataFrame."""
        try:
            # Read Excel file
            df = pd.read_excel(
                io.BytesIO(file_content),
                sheet_name=sheet_name or 0,
                header=0 if has_header else None,
                engine='openpyxl'
            )

            # If no header, create column names
            if not has_header:
                df.columns = [f'column_{i+1}' for i in range(len(df.columns))]

            return df
        except Exception as e:
            logger.error(f"Failed to parse Excel: {e}")
            raise ValueError(f"Failed to parse Excel file: {e}")

    @staticmethod
    def get_excel_sheets(file_content: bytes) -> List[str]:
        """Get list of sheet names from an Excel file."""
        try:
            xlsx = pd.ExcelFile(io.BytesIO(file_content), engine='openpyxl')
            return xlsx.sheet_names
        except Exception as e:
            logger.error(f"Failed to get Excel sheets: {e}")
            raise ValueError(f"Failed to read Excel file: {e}")

    @staticmethod
    def store_temp_dataframe(df: pd.DataFrame) -> str:
        """Store a DataFrame temporarily and return a file_id."""
        file_id = str(uuid.uuid4())
        FileService._temp_files[file_id] = df
        return file_id

    @staticmethod
    def get_temp_dataframe(file_id: str) -> Optional[pd.DataFrame]:
        """Retrieve a temporarily stored DataFrame."""
        return FileService._temp_files.get(file_id)

    @staticmethod
    def remove_temp_dataframe(file_id: str) -> None:
        """Remove a temporarily stored DataFrame."""
        FileService._temp_files.pop(file_id, None)

    @staticmethod
    def generate_table_name(connection_id: str) -> str:
        """Generate a unique table name for uploaded data."""
        short_id = str(connection_id).replace('-', '')[:12]
        return f"uploaded_{short_id}"

    @staticmethod
    async def create_data_table(
        connection_string: str,
        table_name: str,
        columns: List[Dict[str, Any]],
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Create a table in the database and insert data from DataFrame."""
        from app.services.postgres_service import postgres_service

        conn = None
        try:
            conn_str = postgres_service.normalize_connection_string(connection_string)
            conn = await asyncpg.connect(conn_str, timeout=30)

            # Build CREATE TABLE statement
            col_defs = []
            for col in columns:
                col_name = col['name']
                col_type = col.get('type', col.get('detected_type', 'TEXT'))
                nullable = 'NULL' if col.get('nullable', True) else 'NOT NULL'
                col_defs.append(f'"{col_name}" {col_type} {nullable}')

            create_sql = f'CREATE TABLE IF NOT EXISTS "public"."{table_name}" (\n  ' + ',\n  '.join(col_defs) + '\n)'
            logger.info(f"Creating table with SQL: {create_sql}")
            await conn.execute(create_sql)

            # Prepare data for insertion
            # Map original column names to sanitized names
            col_mapping = {col['original_name']: col['name'] for col in columns}

            # Rename DataFrame columns
            df_renamed = df.rename(columns=col_mapping)

            # Get column names in order
            col_names = [col['name'] for col in columns]

            # Convert DataFrame to records
            records = df_renamed[col_names].values.tolist()

            # Handle NaN values - convert to None
            def clean_value(val):
                if pd.isna(val):
                    return None
                return val

            records = [[clean_value(v) for v in row] for row in records]

            # Bulk insert using copy_records_to_table for efficiency
            if records:
                # Build INSERT statement with placeholders
                placeholders = ', '.join(f'${i+1}' for i in range(len(col_names)))
                quoted_cols = ', '.join(f'"{c}"' for c in col_names)
                insert_sql = f'INSERT INTO "public"."{table_name}" ({quoted_cols}) VALUES ({placeholders})'

                # Execute in batches
                batch_size = 1000
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    await conn.executemany(insert_sql, batch)

            return {
                'success': True,
                'table_name': table_name,
                'rows_inserted': len(records)
            }

        except Exception as e:
            logger.error(f"Failed to create data table: {e}")
            # Try to drop table if it was partially created
            if conn:
                try:
                    await conn.execute(f'DROP TABLE IF EXISTS "public"."{table_name}"')
                except Exception:
                    pass
            raise ValueError(f"Failed to create data table: {e}")
        finally:
            if conn:
                await conn.close()

    @staticmethod
    async def drop_data_table(connection_string: str, table_name: str) -> bool:
        """Drop an uploaded data table."""
        from app.services.postgres_service import postgres_service

        conn = None
        try:
            conn_str = postgres_service.normalize_connection_string(connection_string)
            conn = await asyncpg.connect(conn_str, timeout=10)

            await conn.execute(f'DROP TABLE IF EXISTS "public"."{table_name}"')
            logger.info(f"Dropped table: {table_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to drop table {table_name}: {e}")
            return False
        finally:
            if conn:
                await conn.close()


# Singleton instance
file_service = FileService()
