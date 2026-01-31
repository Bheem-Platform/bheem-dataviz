from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ConnectionBase(BaseModel):
    name: str
    type: str  # postgresql, mysql, bigquery, etc.
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None  # Maps to database_name in DB
    username: Optional[str] = None
    ssl_enabled: Optional[bool] = False
    additional_config: Optional[Dict[str, Any]] = None


class ConnectionCreate(ConnectionBase):
    password: Optional[str] = None
    connection_string: Optional[str] = None  # Alternative to individual fields

    # BigQuery specific
    project_id: Optional[str] = None
    credentials_json: Optional[str] = None  # Service account JSON
    credentials_path: Optional[str] = None  # Path to credentials file
    dataset_id: Optional[str] = None

    # Snowflake specific
    account: Optional[str] = None  # Snowflake account identifier
    warehouse: Optional[str] = None
    schema: Optional[str] = None
    role: Optional[str] = None
    private_key_path: Optional[str] = None
    private_key_passphrase: Optional[str] = None


class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_enabled: Optional[bool] = None
    additional_config: Optional[Dict[str, Any]] = None


class ConnectionResponse(ConnectionBase):
    id: str
    status: str = "disconnected"
    tables_count: Optional[int] = None
    last_sync: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Keep Connection as alias for backwards compatibility
Connection = ConnectionResponse


class ConnectionTestRequest(BaseModel):
    """Request body for testing a connection without saving it."""
    type: Optional[str] = "postgresql"  # postgresql, mysql, mongodb, bigquery, snowflake
    connection_string: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_enabled: Optional[bool] = False
    additional_config: Optional[Dict[str, Any]] = None

    # BigQuery specific
    project_id: Optional[str] = None
    credentials_json: Optional[str] = None  # Service account JSON
    credentials_path: Optional[str] = None  # Path to credentials file
    dataset_id: Optional[str] = None

    # Snowflake specific
    account: Optional[str] = None  # Snowflake account identifier
    warehouse: Optional[str] = None
    schema: Optional[str] = None
    role: Optional[str] = None
    private_key_path: Optional[str] = None
    private_key_passphrase: Optional[str] = None


class ConnectionTestResponse(BaseModel):
    """Response for connection test."""
    success: bool
    message: str
    tables_count: Optional[int] = None
    version: Optional[str] = None


class TableInfo(BaseModel):
    """Information about a database table."""
    schema_name: str
    name: str
    type: str
    reference_count: int = 0      # How many tables reference this table via FK
    is_important: bool = False    # True if reference_count > 0


class ColumnInfo(BaseModel):
    """Information about a table column."""
    name: str
    type: str
    nullable: bool
    default: Optional[str] = None


class TablePreviewResponse(BaseModel):
    """Response for table data preview."""
    columns: list[str]
    rows: list[Dict[str, Any]]
    total: int
    preview_count: int
    execution_time: float


# File Upload Schemas

class ColumnConfig(BaseModel):
    """Configuration for a column in uploaded file."""
    original_name: str
    name: str
    type: str  # SQL type: TEXT, INTEGER, BIGINT, DOUBLE PRECISION, BOOLEAN, TIMESTAMP
    nullable: bool = True


class FileUploadPreviewResponse(BaseModel):
    """Response for file upload preview."""
    columns: List[ColumnConfig]
    sample_rows: List[Dict[str, Any]]
    row_count: int
    file_id: str  # Temporary file reference for confirmation
    sheets: Optional[List[str]] = None  # For Excel files


class FileUploadConfirmRequest(BaseModel):
    """Request to confirm file upload and create connection."""
    name: str
    file_id: str
    column_config: List[ColumnConfig]


class FileUploadConfirmResponse(BaseModel):
    """Response after file upload confirmation."""
    connection: ConnectionResponse
    table_name: str
    rows_inserted: int
