from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid as uuid_module
import logging

from app.schemas.connection import (
    ConnectionResponse,
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionTestRequest,
    ConnectionTestResponse,
    TableInfo,
    ColumnInfo,
    TablePreviewResponse,
    FileUploadPreviewResponse,
    FileUploadConfirmRequest,
    FileUploadConfirmResponse,
    ColumnConfig
)
from app.models.connection import Connection as ConnectionModel, ConnectionType, ConnectionStatus
from app.models.user import User
from app.services.postgres_service import postgres_service
from app.services.mysql_service import mysql_service
from app.services.mongodb_service import mongodb_service
from app.services.encryption_service import encryption_service
from app.services.file_service import file_service
from app.database import get_db
from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()


def _build_connection_string(data: dict, password: str = None) -> str:
    """Build connection string from connection data."""
    if data.get("connection_string"):
        return data["connection_string"]

    conn_type = data.get("type", "postgresql").lower()

    if conn_type == "mysql":
        return mysql_service.build_connection_string(
            host=data.get("host", "localhost"),
            port=data.get("port", 3306),
            database=data.get("database", ""),
            username=data.get("username"),
            password=password,
            extra=data.get("additional_config")
        )

    if conn_type == "mongodb":
        additional = data.get("additional_config") or {}
        return mongodb_service.build_connection_string(
            host=data.get("host", "localhost"),
            port=data.get("port", 27017),
            database=data.get("database", ""),
            username=data.get("username"),
            password=password,
            auth_source=additional.get("auth_source"),
            replica_set=additional.get("replica_set"),
            is_srv=additional.get("is_srv", False)
        )

    # Default to PostgreSQL
    return postgres_service.build_connection_string(
        host=data.get("host", "localhost"),
        port=data.get("port", 5432),
        database=data.get("database", ""),
        username=data.get("username"),
        password=password,
        extra=data.get("additional_config")
    )


def _model_to_response(conn: ConnectionModel) -> ConnectionResponse:
    """Convert database model to response schema."""
    return ConnectionResponse(
        id=str(conn.id),
        name=conn.name,
        type=conn.type.value if conn.type else "postgresql",
        host=conn.host,
        port=conn.port,
        database=conn.database_name,
        username=conn.username,
        ssl_enabled=conn.ssl_enabled,
        additional_config=conn.additional_config,
        status=conn.status.value if conn.status else "disconnected",
        tables_count=conn.tables_count,
        last_sync=conn.last_sync,
        created_at=conn.created_at,
        updated_at=conn.updated_at
    )


@router.get("/", response_model=List[ConnectionResponse])
async def list_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all saved connections."""
    result = await db.execute(select(ConnectionModel).order_by(ConnectionModel.created_at.desc()))
    connections = result.scalars().all()
    return [_model_to_response(conn) for conn in connections]


@router.post("/", response_model=ConnectionResponse)
async def create_connection(
    connection: ConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new database connection."""
    conn_data = connection.model_dump()

    # Map type string to enum first
    try:
        conn_type = ConnectionType(conn_data["type"].lower())
    except ValueError:
        conn_type = ConnectionType.postgresql

    # Determine password and parse connection string
    password = None
    additional_config = conn_data.get("additional_config") or {}

    if connection.connection_string:
        # Use appropriate parser based on connection type
        if conn_type == ConnectionType.mysql:
            parsed = mysql_service.parse_connection_string(connection.connection_string)
            # Check for SSL in extra params
            extra = parsed.get("extra") or {}
            ssl_mode = extra.get("ssl-mode", "").lower()
            if ssl_mode in ("required", "verify_ca", "verify_identity", "true", "1"):
                additional_config["ssl"] = True
        elif conn_type == ConnectionType.mongodb:
            parsed = mongodb_service.parse_connection_string(connection.connection_string)
            # Store MongoDB-specific settings
            if parsed.get("auth_source"):
                additional_config["auth_source"] = parsed["auth_source"]
            if parsed.get("replica_set"):
                additional_config["replica_set"] = parsed["replica_set"]
            if parsed.get("is_srv"):
                additional_config["is_srv"] = parsed["is_srv"]
            if parsed.get("extra"):
                additional_config.update(parsed["extra"])
        else:
            parsed = postgres_service.parse_connection_string(connection.connection_string)

        conn_data.update({
            "host": parsed["host"],
            "port": parsed["port"],
            "database": parsed["database"],
            "username": parsed["username"],
        })
        password = parsed.get("password")
    else:
        password = connection.password

    # Encrypt password
    encrypted_password = encryption_service.encrypt(password) if password else None

    # Create the connection model
    db_connection = ConnectionModel(
        name=conn_data["name"],
        type=conn_type,
        host=conn_data.get("host"),
        port=conn_data.get("port"),
        database_name=conn_data.get("database"),
        username=conn_data.get("username"),
        encrypted_password=encrypted_password,
        ssl_enabled=conn_data.get("ssl_enabled", False),
        additional_config=additional_config,
        status=ConnectionStatus.disconnected
    )

    db.add(db_connection)
    await db.commit()
    await db.refresh(db_connection)

    return _model_to_response(db_connection)


# File upload routes - must be before /{connection_id} routes
@router.post("/upload-preview", response_model=FileUploadPreviewResponse)
async def upload_preview(
    file: UploadFile = File(...),
    file_type: str = Form(...),  # 'csv' or 'excel'
    delimiter: str = Form(','),
    has_header: bool = Form(True),
    sheet_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a CSV or Excel file and get a preview of the data.
    Returns column info, sample rows, and a file_id for confirmation.
    """
    try:
        # Read file content
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        sheets = None

        if file_type == 'csv':
            df = file_service.parse_csv(content, delimiter=delimiter, has_header=has_header)
        elif file_type == 'excel':
            # Get sheet names for Excel files
            sheets = file_service.get_excel_sheets(content)
            df = file_service.parse_excel(content, sheet_name=sheet_name, has_header=has_header)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")

        # Detect column types
        columns = file_service.detect_column_types(df)

        # Get sample rows (first 10)
        sample_df = df.head(10)
        sample_rows = sample_df.to_dict(orient='records')

        # Store DataFrame temporarily
        file_id = file_service.store_temp_dataframe(df)

        return FileUploadPreviewResponse(
            columns=[ColumnConfig(**col) for col in columns],
            sample_rows=sample_rows,
            row_count=len(df),
            file_id=file_id,
            sheets=sheets
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.post("/upload-confirm", response_model=FileUploadConfirmResponse)
async def upload_confirm(
    request: FileUploadConfirmRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Confirm file upload: create connection and data table.
    """
    # Retrieve stored DataFrame
    df = file_service.get_temp_dataframe(request.file_id)
    if df is None:
        raise HTTPException(
            status_code=400,
            detail="File preview expired or not found. Please upload the file again."
        )

    try:
        # Create connection record first to get the ID
        db_connection = ConnectionModel(
            name=request.name,
            type=ConnectionType.csv,  # Use csv for both CSV and Excel uploads
            status=ConnectionStatus.disconnected,
            additional_config={}
        )

        db.add(db_connection)
        await db.commit()
        await db.refresh(db_connection)

        # Generate table name from connection ID
        table_name = file_service.generate_table_name(str(db_connection.id))

        # Use the application's database for storing uploaded data
        app_db_url = settings.DATABASE_URL

        # Create the data table and insert data
        result = await file_service.create_data_table(
            app_db_url,
            table_name,
            [col.model_dump() for col in request.column_config],
            df
        )

        # Update connection with table info
        db_connection.additional_config = {
            'table_name': table_name,
            'original_filename': request.name,
            'row_count': len(df),
            'columns': [col.model_dump() for col in request.column_config]
        }
        db_connection.status = ConnectionStatus.connected
        db_connection.tables_count = 1

        await db.commit()
        await db.refresh(db_connection)

        # Clean up temp storage
        file_service.remove_temp_dataframe(request.file_id)

        return FileUploadConfirmResponse(
            connection=_model_to_response(db_connection),
            table_name=table_name,
            rows_inserted=result['rows_inserted']
        )

    except Exception as e:
        # Rollback connection if table creation failed
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create data table: {str(e)}")


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific connection by ID."""
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    return _model_to_response(conn)


@router.put("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: str,
    update_data: ConnectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a connection."""
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    update_dict = update_data.model_dump(exclude_unset=True)

    # Handle password update
    if "password" in update_dict:
        password = update_dict.pop("password")
        if password:
            conn.encrypted_password = encryption_service.encrypt(password)

    # Handle database field mapping
    if "database" in update_dict:
        conn.database_name = update_dict.pop("database")

    # Update other fields
    for field, value in update_dict.items():
        if hasattr(conn, field):
            setattr(conn, field, value)

    conn.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(conn)

    return _model_to_response(conn)


@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a connection. For CSV/Excel connections, also drops the data table."""
    try:
        conn_uuid = uuid_module.UUID(connection_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid connection ID format")

    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == conn_uuid)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # For CSV/Excel connections, drop the associated data table
    if conn.type in (ConnectionType.csv, ConnectionType.excel):
        table_name = conn.additional_config.get('table_name') if conn.additional_config else None
        if table_name:
            try:
                await file_service.drop_data_table(settings.DATABASE_URL, table_name)
            except Exception as e:
                # Log but don't fail the deletion
                logging.warning(f"Failed to drop data table {table_name}: {e}")

    await db.delete(conn)
    await db.commit()

    return {"status": "deleted"}


async def _get_connection_string(conn: ConnectionModel) -> str:
    """Build connection string from stored connection data."""
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    if conn.type == ConnectionType.mysql:
        return mysql_service.build_connection_string(
            host=conn.host or "localhost",
            port=conn.port or 3306,
            database=conn.database_name or "",
            username=conn.username,
            password=password,
            extra=conn.additional_config
        )

    if conn.type == ConnectionType.mongodb:
        additional = conn.additional_config or {}
        return mongodb_service.build_connection_string(
            host=conn.host or "localhost",
            port=conn.port or 27017,
            database=conn.database_name or "",
            username=conn.username,
            password=password,
            auth_source=additional.get("auth_source"),
            replica_set=additional.get("replica_set"),
            is_srv=additional.get("is_srv", False)
        )

    # Default to PostgreSQL
    return postgres_service.build_connection_string(
        host=conn.host or "localhost",
        port=conn.port or 5432,
        database=conn.database_name or "",
        username=conn.username,
        password=password,
        extra=conn.additional_config
    )


@router.post("/{connection_id}/test", response_model=ConnectionTestResponse)
async def test_saved_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test a saved connection."""
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # For CSV/Excel connections, verify the table exists
    if conn.type in (ConnectionType.csv, ConnectionType.excel):
        table_name = conn.additional_config.get('table_name') if conn.additional_config else None
        if table_name:
            conn.status = ConnectionStatus.connected
            conn.last_sync = datetime.utcnow()
            await db.commit()
            return ConnectionTestResponse(
                success=True,
                message="Data table is available",
                tables_count=1
            )
        else:
            return ConnectionTestResponse(
                success=False,
                message="No data table associated with this connection"
            )

    if conn.type not in (ConnectionType.postgresql, ConnectionType.mysql, ConnectionType.mongodb):
        return ConnectionTestResponse(
            success=False,
            message=f"Connection test not implemented for type: {conn.type.value}"
        )

    # Decrypt password
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    # Test based on connection type
    if conn.type == ConnectionType.mysql:
        use_ssl = conn.additional_config.get("ssl", False) if conn.additional_config else False
        test_result = await mysql_service.test_connection(
            host=conn.host or "localhost",
            port=conn.port or 3306,
            database=conn.database_name or "",
            username=conn.username,
            password=password,
            ssl=use_ssl
        )
    elif conn.type == ConnectionType.mongodb:
        additional = conn.additional_config or {}
        test_result = await mongodb_service.test_connection(
            host=conn.host or "localhost",
            port=conn.port or 27017,
            database=conn.database_name or "",
            username=conn.username,
            password=password,
            auth_source=additional.get("auth_source"),
            is_srv=additional.get("is_srv", False),
            ssl=additional.get("ssl", False)
        )
    else:
        conn_str = await _get_connection_string(conn)
        test_result = await postgres_service.test_connection(conn_str)

    # Update connection status based on test result
    if test_result["success"]:
        conn.status = ConnectionStatus.connected
        conn.tables_count = test_result.get("tables_count")
        conn.last_sync = datetime.utcnow()
    else:
        conn.status = ConnectionStatus.error

    await db.commit()

    return ConnectionTestResponse(
        success=test_result["success"],
        message=test_result["message"],
        tables_count=test_result.get("tables_count"),
        version=test_result.get("version")
    )


@router.post("/test", response_model=ConnectionTestResponse)
async def test_connection(
    request: ConnectionTestRequest,
    current_user: User = Depends(get_current_user)
):
    """Test a connection without saving it (for connection form validation)."""
    try:
        conn_type = request.type.lower() if request.type else "postgresql"

        if conn_type == "mysql":
            # Parse connection string if provided, otherwise use individual fields
            if request.connection_string:
                parsed = mysql_service.parse_connection_string(request.connection_string)
                host = parsed.get("host", "localhost")
                port = parsed.get("port", 3306)
                database = parsed.get("database", "")
                username = parsed.get("username")
                password = parsed.get("password")
                extra = parsed.get("extra") or {}
                # Check for SSL mode in extra params
                ssl_mode = extra.get("ssl-mode", "").lower()
                use_ssl = ssl_mode in ("required", "verify_ca", "verify_identity", "true", "1")
            else:
                host = request.host or "localhost"
                port = request.port or 3306
                database = request.database or ""
                username = request.username
                password = request.password
                use_ssl = False

            result = await mysql_service.test_connection(
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
                ssl=use_ssl
            )
        elif conn_type == "mongodb":
            # Parse connection string if provided, otherwise use individual fields
            if request.connection_string:
                parsed = mongodb_service.parse_connection_string(request.connection_string)
                host = parsed.get("host", "localhost")
                port = parsed.get("port", 27017)
                database = parsed.get("database", "")
                username = parsed.get("username")
                password = parsed.get("password")
                auth_source = parsed.get("auth_source")
                is_srv = parsed.get("is_srv", False)
            else:
                host = request.host or "localhost"
                port = request.port or 27017
                database = request.database or ""
                username = request.username
                password = request.password
                additional = request.additional_config or {}
                auth_source = additional.get("auth_source")
                is_srv = additional.get("is_srv", False)

            result = await mongodb_service.test_connection(
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
                auth_source=auth_source,
                is_srv=is_srv,
                ssl=request.ssl_enabled or False
            )
        else:
            conn_str = _build_connection_string(request.model_dump(), request.password)
            result = await postgres_service.test_connection(conn_str)

        return ConnectionTestResponse(
            success=result["success"],
            message=result["message"],
            tables_count=result.get("tables_count"),
            version=result.get("version")
        )
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"Failed to test connection: {str(e)}"
        )


@router.get("/{connection_id}/tables", response_model=List[TableInfo])
async def get_tables(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of tables for a connection, sorted by importance (FK references)."""
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # For CSV/Excel connections, return the uploaded table
    if conn.type in (ConnectionType.csv, ConnectionType.excel):
        table_name = conn.additional_config.get('table_name') if conn.additional_config else None
        if table_name:
            return [
                TableInfo(
                    schema_name="public",
                    name=table_name,
                    type="BASE TABLE",
                    reference_count=0,
                    is_important=False
                )
            ]
        return []

    if conn.type not in (ConnectionType.postgresql, ConnectionType.mysql, ConnectionType.mongodb):
        raise HTTPException(
            status_code=400,
            detail=f"Table listing not implemented for type: {conn.type.value}"
        )

    try:
        # Decrypt password
        password = None
        if conn.encrypted_password:
            password = encryption_service.decrypt(conn.encrypted_password)

        if conn.type == ConnectionType.mysql:
            use_ssl = conn.additional_config.get("ssl", False) if conn.additional_config else False
            tables = await mysql_service.get_tables(
                host=conn.host or "localhost",
                port=conn.port or 3306,
                database=conn.database_name or "",
                username=conn.username,
                password=password,
                ssl=use_ssl
            )
            # Get FK relationships for MySQL
            relationships = await mysql_service.get_table_relationships(
                host=conn.host or "localhost",
                port=conn.port or 3306,
                database=conn.database_name or "",
                username=conn.username,
                password=password,
                ssl=use_ssl
            )
        elif conn.type == ConnectionType.mongodb:
            additional = conn.additional_config or {}
            tables = await mongodb_service.get_tables(
                host=conn.host or "localhost",
                port=conn.port or 27017,
                database=conn.database_name or "",
                username=conn.username,
                password=password,
                auth_source=additional.get("auth_source"),
                is_srv=additional.get("is_srv", False),
                ssl=additional.get("ssl", False)
            )
            # MongoDB has no FK relationships
            relationships = {}
        else:
            conn_str = await _get_connection_string(conn)
            tables = await postgres_service.get_tables(conn_str)
            # Get FK relationships for PostgreSQL
            relationships = await postgres_service.get_table_relationships(conn_str)

        # Build result with reference counts
        table_infos = []
        for t in tables:
            full_name = f"{t['schema']}.{t['name']}"
            ref_count = relationships.get(full_name, 0)
            table_infos.append(TableInfo(
                schema_name=t["schema"],
                name=t["name"],
                type=t["type"],
                reference_count=ref_count,
                is_important=ref_count > 0
            ))

        # Sort: important tables first (by ref count desc), then alphabetically
        table_infos.sort(key=lambda x: (-x.reference_count, x.name))
        return table_infos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")


@router.get("/{connection_id}/tables/{schema_name}/{table_name}/columns", response_model=List[ColumnInfo])
async def get_table_columns(
    connection_id: str,
    schema_name: str,
    table_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get column information for a specific table."""
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # For CSV/Excel connections, use the app database
    if conn.type in (ConnectionType.csv, ConnectionType.excel):
        try:
            columns = await postgres_service.get_table_columns(settings.DATABASE_URL, schema_name, table_name)
            return [
                ColumnInfo(
                    name=c["name"],
                    type=c["type"],
                    nullable=c["nullable"],
                    default=c["default"]
                )
                for c in columns
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get columns: {str(e)}")

    if conn.type not in (ConnectionType.postgresql, ConnectionType.mysql, ConnectionType.mongodb):
        raise HTTPException(
            status_code=400,
            detail=f"Column listing not implemented for type: {conn.type.value}"
        )

    try:
        # Decrypt password
        password = None
        if conn.encrypted_password:
            password = encryption_service.decrypt(conn.encrypted_password)

        if conn.type == ConnectionType.mysql:
            use_ssl = conn.additional_config.get("ssl", False) if conn.additional_config else False
            columns = await mysql_service.get_table_columns(
                host=conn.host or "localhost",
                port=conn.port or 3306,
                database=conn.database_name or "",
                table=table_name,
                username=conn.username,
                password=password,
                ssl=use_ssl
            )
        elif conn.type == ConnectionType.mongodb:
            additional = conn.additional_config or {}
            columns = await mongodb_service.get_table_columns(
                host=conn.host or "localhost",
                port=conn.port or 27017,
                database=conn.database_name or "",
                collection=table_name,
                username=conn.username,
                password=password,
                auth_source=additional.get("auth_source"),
                is_srv=additional.get("is_srv", False),
                ssl=additional.get("ssl", False)
            )
        else:
            conn_str = await _get_connection_string(conn)
            columns = await postgres_service.get_table_columns(conn_str, schema_name, table_name)

        return [
            ColumnInfo(
                name=c["name"],
                type=c["type"],
                nullable=c["nullable"],
                default=c["default"]
            )
            for c in columns
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get columns: {str(e)}")


@router.get("/{connection_id}/tables/{schema_name}/{table_name}/preview", response_model=TablePreviewResponse)
async def get_table_preview(
    connection_id: str,
    schema_name: str,
    table_name: str,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a preview of table data with pagination support."""
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # For CSV/Excel connections, use the app database
    if conn.type in (ConnectionType.csv, ConnectionType.excel):
        try:
            preview_result = await postgres_service.get_table_preview(
                settings.DATABASE_URL, schema_name, table_name, min(limit, 500), offset
            )
            return TablePreviewResponse(
                columns=preview_result["columns"],
                rows=preview_result["rows"],
                total=preview_result["total"],
                preview_count=preview_result["preview_count"],
                execution_time=preview_result["execution_time"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get table preview: {str(e)}")

    if conn.type not in (ConnectionType.postgresql, ConnectionType.mysql, ConnectionType.mongodb):
        raise HTTPException(
            status_code=400,
            detail=f"Table preview not implemented for type: {conn.type.value}"
        )

    try:
        # Decrypt password
        password = None
        if conn.encrypted_password:
            password = encryption_service.decrypt(conn.encrypted_password)

        if conn.type == ConnectionType.mysql:
            use_ssl = conn.additional_config.get("ssl", False) if conn.additional_config else False
            preview_result = await mysql_service.get_table_preview(
                host=conn.host or "localhost",
                port=conn.port or 3306,
                database=conn.database_name or "",
                table=table_name,
                username=conn.username,
                password=password,
                limit=min(limit, 500),
                offset=offset,
                ssl=use_ssl
            )
        elif conn.type == ConnectionType.mongodb:
            additional = conn.additional_config or {}
            preview_result = await mongodb_service.get_table_preview(
                host=conn.host or "localhost",
                port=conn.port or 27017,
                database=conn.database_name or "",
                collection=table_name,
                username=conn.username,
                password=password,
                auth_source=additional.get("auth_source"),
                is_srv=additional.get("is_srv", False),
                ssl=additional.get("ssl", False),
                limit=min(limit, 500),
                offset=offset
            )
        else:
            conn_str = await _get_connection_string(conn)
            preview_result = await postgres_service.get_table_preview(
                conn_str, schema_name, table_name, min(limit, 500), offset
            )

        return TablePreviewResponse(
            columns=preview_result["columns"],
            rows=preview_result["rows"],
            total=preview_result["total"],
            preview_count=preview_result["preview_count"],
            execution_time=preview_result["execution_time"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get table preview: {str(e)}")
