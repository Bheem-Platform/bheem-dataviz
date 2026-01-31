"""
Cloud Connectors API Endpoints

Provides endpoints for BigQuery and Snowflake cloud database connections.
"""

from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.connection import (
    ConnectionResponse,
    ConnectionTestResponse,
    TableInfo,
    ColumnInfo,
    TablePreviewResponse,
)
from app.models.connection import Connection as ConnectionModel, ConnectionType, ConnectionStatus
from app.services.bigquery_service import bigquery_service, BigQueryService
from app.services.snowflake_service import snowflake_service, SnowflakeService
from app.services.encryption_service import encryption_service

router = APIRouter()


# Request/Response Models

class BigQueryConnectionCreate(BaseModel):
    """Request to create a BigQuery connection."""
    name: str
    project_id: str
    credentials_json: Optional[str] = None  # Service account JSON content
    credentials_path: Optional[str] = None  # Path to credentials file
    default_dataset: Optional[str] = None


class BigQueryTestRequest(BaseModel):
    """Request to test a BigQuery connection."""
    project_id: str
    credentials_json: Optional[str] = None
    credentials_path: Optional[str] = None


class SnowflakeConnectionCreate(BaseModel):
    """Request to create a Snowflake connection."""
    name: str
    account: str
    user: str
    password: str
    warehouse: Optional[str] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    role: Optional[str] = None


class SnowflakeTestRequest(BaseModel):
    """Request to test a Snowflake connection."""
    account: str
    user: str
    password: str
    warehouse: Optional[str] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    role: Optional[str] = None


class DatasetInfo(BaseModel):
    """Information about a BigQuery dataset."""
    id: str
    project: str
    description: Optional[str] = None
    location: Optional[str] = None


class DatabaseInfo(BaseModel):
    """Information about a Snowflake database."""
    name: str
    owner: Optional[str] = None
    comment: Optional[str] = None


class QueryCostEstimate(BaseModel):
    """Query cost estimate result."""
    bytes_processed: int
    bytes_processed_formatted: str
    estimated_cost_usd: float
    estimated_cost_formatted: str


# BigQuery Endpoints

@router.get("/bigquery/status")
async def get_bigquery_status():
    """Check if BigQuery client is available."""
    return {
        "available": BigQueryService.is_available(),
        "message": "BigQuery client is available" if BigQueryService.is_available()
        else "BigQuery client not installed. Run: pip install google-cloud-bigquery"
    }


@router.post("/bigquery/test", response_model=ConnectionTestResponse)
async def test_bigquery_connection(
    request: BigQueryTestRequest,
    current_user: dict = Depends(get_current_user),
):
    """Test a BigQuery connection without saving."""
    result = await bigquery_service.test_connection(
        project_id=request.project_id,
        credentials_json=request.credentials_json,
        credentials_path=request.credentials_path,
    )

    return ConnectionTestResponse(
        success=result["success"],
        message=result["message"],
        tables_count=result.get("datasets_count"),
    )


@router.post("/bigquery/connections", response_model=ConnectionResponse)
async def create_bigquery_connection(
    connection: BigQueryConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new BigQuery connection."""
    # Test connection first
    test_result = await bigquery_service.test_connection(
        project_id=connection.project_id,
        credentials_json=connection.credentials_json,
        credentials_path=connection.credentials_path,
    )

    if not test_result["success"]:
        raise HTTPException(
            status_code=400,
            detail=f"Connection test failed: {test_result['message']}"
        )

    # Encrypt credentials if provided as JSON
    encrypted_creds = None
    if connection.credentials_json:
        encrypted_creds = encryption_service.encrypt(connection.credentials_json)

    # Create connection model
    db_connection = ConnectionModel(
        name=connection.name,
        type=ConnectionType.bigquery,
        host=connection.project_id,  # Store project_id in host field
        database_name=connection.default_dataset,
        additional_config={
            "project_id": connection.project_id,
            "credentials_path": connection.credentials_path,
            "default_dataset": connection.default_dataset,
        },
        encrypted_password=encrypted_creds,  # Store encrypted credentials
        status=ConnectionStatus.connected,
        tables_count=test_result.get("datasets_count"),
    )

    db.add(db_connection)
    await db.commit()
    await db.refresh(db_connection)

    return ConnectionResponse(
        id=str(db_connection.id),
        name=db_connection.name,
        type="bigquery",
        host=connection.project_id,
        database=connection.default_dataset,
        status="connected",
        tables_count=db_connection.tables_count,
        created_at=db_connection.created_at,
    )


@router.get("/bigquery/{connection_id}/datasets", response_model=list[DatasetInfo])
async def get_bigquery_datasets(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get list of datasets for a BigQuery connection."""
    conn = await _get_connection(db, connection_id, ConnectionType.bigquery)
    creds_json = _get_bigquery_credentials(conn)

    datasets = await bigquery_service.get_datasets(
        project_id=conn.additional_config.get("project_id"),
        credentials_json=creds_json,
    )

    return [
        DatasetInfo(
            id=ds["id"],
            project=ds["project"],
            description=ds.get("description"),
            location=ds.get("location"),
        )
        for ds in datasets
    ]


@router.get("/bigquery/{connection_id}/tables", response_model=list[TableInfo])
async def get_bigquery_tables(
    connection_id: str,
    dataset_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get list of tables for a BigQuery connection."""
    conn = await _get_connection(db, connection_id, ConnectionType.bigquery)
    creds_json = _get_bigquery_credentials(conn)

    tables = await bigquery_service.get_tables(
        project_id=conn.additional_config.get("project_id"),
        dataset_id=dataset_id or conn.database_name,
        credentials_json=creds_json,
    )

    return [
        TableInfo(
            schema_name=t["schema"],
            name=t["name"],
            type=t["type"],
            reference_count=0,
            is_important=False,
        )
        for t in tables
    ]


@router.get("/bigquery/{connection_id}/tables/{dataset_id}/{table_id}/columns", response_model=list[ColumnInfo])
async def get_bigquery_table_columns(
    connection_id: str,
    dataset_id: str,
    table_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get column information for a BigQuery table."""
    conn = await _get_connection(db, connection_id, ConnectionType.bigquery)
    creds_json = _get_bigquery_credentials(conn)

    columns = await bigquery_service.get_table_columns(
        project_id=conn.additional_config.get("project_id"),
        dataset_id=dataset_id,
        table_id=table_id,
        credentials_json=creds_json,
    )

    return [
        ColumnInfo(
            name=c["name"],
            type=c["type"],
            nullable=c["nullable"],
            default=None,
        )
        for c in columns
    ]


@router.get("/bigquery/{connection_id}/tables/{dataset_id}/{table_id}/preview", response_model=TablePreviewResponse)
async def get_bigquery_table_preview(
    connection_id: str,
    dataset_id: str,
    table_id: str,
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a preview of BigQuery table data."""
    conn = await _get_connection(db, connection_id, ConnectionType.bigquery)
    creds_json = _get_bigquery_credentials(conn)

    result = await bigquery_service.get_table_preview(
        project_id=conn.additional_config.get("project_id"),
        dataset_id=dataset_id,
        table_id=table_id,
        credentials_json=creds_json,
        limit=limit,
        offset=offset,
    )

    return TablePreviewResponse(
        columns=result["columns"],
        rows=result["rows"],
        total=result["total"],
        preview_count=result["preview_count"],
        execution_time=result["execution_time"],
    )


@router.post("/bigquery/{connection_id}/query")
async def execute_bigquery_query(
    connection_id: str,
    sql: str,
    limit: int = Query(1000, le=10000),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Execute a SQL query against BigQuery."""
    conn = await _get_connection(db, connection_id, ConnectionType.bigquery)
    creds_json = _get_bigquery_credentials(conn)

    result = await bigquery_service.execute_query(
        project_id=conn.additional_config.get("project_id"),
        sql=sql,
        credentials_json=creds_json,
        limit=limit,
    )

    return result


@router.post("/bigquery/{connection_id}/estimate-cost", response_model=QueryCostEstimate)
async def estimate_bigquery_query_cost(
    connection_id: str,
    sql: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Estimate the cost of a BigQuery query."""
    conn = await _get_connection(db, connection_id, ConnectionType.bigquery)
    creds_json = _get_bigquery_credentials(conn)

    result = await bigquery_service.estimate_query_cost(
        project_id=conn.additional_config.get("project_id"),
        sql=sql,
        credentials_json=creds_json,
    )

    return QueryCostEstimate(**result)


# Snowflake Endpoints

@router.get("/snowflake/status")
async def get_snowflake_status():
    """Check if Snowflake client is available."""
    return {
        "available": SnowflakeService.is_available(),
        "message": "Snowflake client is available" if SnowflakeService.is_available()
        else "Snowflake client not installed. Run: pip install snowflake-connector-python"
    }


@router.post("/snowflake/test", response_model=ConnectionTestResponse)
async def test_snowflake_connection(
    request: SnowflakeTestRequest,
    current_user: dict = Depends(get_current_user),
):
    """Test a Snowflake connection without saving."""
    result = await snowflake_service.test_connection(
        account=request.account,
        user=request.user,
        password=request.password,
        warehouse=request.warehouse,
        database=request.database,
        schema=request.schema,
        role=request.role,
    )

    return ConnectionTestResponse(
        success=result["success"],
        message=result["message"],
        tables_count=result.get("databases_count"),
    )


@router.post("/snowflake/connections", response_model=ConnectionResponse)
async def create_snowflake_connection(
    connection: SnowflakeConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new Snowflake connection."""
    # Test connection first
    test_result = await snowflake_service.test_connection(
        account=connection.account,
        user=connection.user,
        password=connection.password,
        warehouse=connection.warehouse,
        database=connection.database,
        schema=connection.schema,
        role=connection.role,
    )

    if not test_result["success"]:
        raise HTTPException(
            status_code=400,
            detail=f"Connection test failed: {test_result['message']}"
        )

    # Encrypt password
    encrypted_password = encryption_service.encrypt(connection.password)

    # Create connection model
    db_connection = ConnectionModel(
        name=connection.name,
        type=ConnectionType.snowflake,
        host=connection.account,  # Store account in host field
        username=connection.user,
        encrypted_password=encrypted_password,
        database_name=connection.database,
        additional_config={
            "account": connection.account,
            "warehouse": connection.warehouse,
            "schema": connection.schema,
            "role": connection.role,
        },
        status=ConnectionStatus.connected,
        tables_count=test_result.get("databases_count"),
    )

    db.add(db_connection)
    await db.commit()
    await db.refresh(db_connection)

    return ConnectionResponse(
        id=str(db_connection.id),
        name=db_connection.name,
        type="snowflake",
        host=connection.account,
        database=connection.database,
        username=connection.user,
        status="connected",
        tables_count=db_connection.tables_count,
        created_at=db_connection.created_at,
    )


@router.get("/snowflake/{connection_id}/databases", response_model=list[DatabaseInfo])
async def get_snowflake_databases(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get list of databases for a Snowflake connection."""
    conn = await _get_connection(db, connection_id, ConnectionType.snowflake)
    password = _get_snowflake_password(conn)

    databases = await snowflake_service.get_databases(
        account=conn.additional_config.get("account"),
        user=conn.username,
        password=password,
        warehouse=conn.additional_config.get("warehouse"),
        role=conn.additional_config.get("role"),
    )

    return [
        DatabaseInfo(
            name=db_info["name"],
            owner=db_info.get("owner"),
            comment=db_info.get("comment"),
        )
        for db_info in databases
    ]


@router.get("/snowflake/{connection_id}/warehouses")
async def get_snowflake_warehouses(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get list of warehouses for a Snowflake connection."""
    conn = await _get_connection(db, connection_id, ConnectionType.snowflake)
    password = _get_snowflake_password(conn)

    warehouses = await snowflake_service.get_warehouses(
        account=conn.additional_config.get("account"),
        user=conn.username,
        password=password,
        role=conn.additional_config.get("role"),
    )

    return warehouses


@router.get("/snowflake/{connection_id}/tables", response_model=list[TableInfo])
async def get_snowflake_tables(
    connection_id: str,
    database: Optional[str] = Query(None),
    schema: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get list of tables for a Snowflake connection."""
    conn = await _get_connection(db, connection_id, ConnectionType.snowflake)
    password = _get_snowflake_password(conn)

    use_database = database or conn.database_name
    if not use_database:
        raise HTTPException(status_code=400, detail="Database must be specified")

    tables = await snowflake_service.get_tables(
        account=conn.additional_config.get("account"),
        user=conn.username,
        password=password,
        database=use_database,
        schema=schema or conn.additional_config.get("schema"),
        warehouse=conn.additional_config.get("warehouse"),
        role=conn.additional_config.get("role"),
    )

    return [
        TableInfo(
            schema_name=t["schema"],
            name=t["name"],
            type=t["type"],
            reference_count=0,
            is_important=False,
        )
        for t in tables
    ]


@router.get("/snowflake/{connection_id}/tables/{database}/{schema}/{table}/columns", response_model=list[ColumnInfo])
async def get_snowflake_table_columns(
    connection_id: str,
    database: str,
    schema: str,
    table: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get column information for a Snowflake table."""
    conn = await _get_connection(db, connection_id, ConnectionType.snowflake)
    password = _get_snowflake_password(conn)

    columns = await snowflake_service.get_table_columns(
        account=conn.additional_config.get("account"),
        user=conn.username,
        password=password,
        database=database,
        schema=schema,
        table=table,
        warehouse=conn.additional_config.get("warehouse"),
        role=conn.additional_config.get("role"),
    )

    return [
        ColumnInfo(
            name=c["name"],
            type=c["type"],
            nullable=c["nullable"],
            default=c.get("default"),
        )
        for c in columns
    ]


@router.get("/snowflake/{connection_id}/tables/{database}/{schema}/{table}/preview", response_model=TablePreviewResponse)
async def get_snowflake_table_preview(
    connection_id: str,
    database: str,
    schema: str,
    table: str,
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a preview of Snowflake table data."""
    conn = await _get_connection(db, connection_id, ConnectionType.snowflake)
    password = _get_snowflake_password(conn)

    result = await snowflake_service.get_table_preview(
        account=conn.additional_config.get("account"),
        user=conn.username,
        password=password,
        database=database,
        schema=schema,
        table=table,
        warehouse=conn.additional_config.get("warehouse"),
        role=conn.additional_config.get("role"),
        limit=limit,
        offset=offset,
    )

    return TablePreviewResponse(
        columns=result["columns"],
        rows=result["rows"],
        total=result["total"],
        preview_count=result["preview_count"],
        execution_time=result["execution_time"],
    )


@router.post("/snowflake/{connection_id}/query")
async def execute_snowflake_query(
    connection_id: str,
    sql: str,
    database: Optional[str] = Query(None),
    schema: Optional[str] = Query(None),
    limit: int = Query(1000, le=10000),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Execute a SQL query against Snowflake."""
    conn = await _get_connection(db, connection_id, ConnectionType.snowflake)
    password = _get_snowflake_password(conn)

    result = await snowflake_service.execute_query(
        account=conn.additional_config.get("account"),
        user=conn.username,
        password=password,
        sql=sql,
        database=database or conn.database_name,
        schema=schema or conn.additional_config.get("schema"),
        warehouse=conn.additional_config.get("warehouse"),
        role=conn.additional_config.get("role"),
        limit=limit,
    )

    return result


# Helper Functions

async def _get_connection(
    db: AsyncSession,
    connection_id: str,
    expected_type: ConnectionType,
) -> ConnectionModel:
    """Get a connection and validate its type."""
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    if conn.type != expected_type:
        raise HTTPException(
            status_code=400,
            detail=f"Connection is not a {expected_type.value} connection"
        )

    return conn


def _get_bigquery_credentials(conn: ConnectionModel) -> Optional[str]:
    """Get decrypted BigQuery credentials."""
    if conn.encrypted_password:
        return encryption_service.decrypt(conn.encrypted_password)
    return None


def _get_snowflake_password(conn: ConnectionModel) -> str:
    """Get decrypted Snowflake password."""
    if conn.encrypted_password:
        return encryption_service.decrypt(conn.encrypted_password)
    raise HTTPException(status_code=500, detail="Connection password not found")
