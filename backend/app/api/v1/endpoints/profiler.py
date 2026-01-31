"""
Data Profiler API Endpoints

Provides dataset profiling capabilities - analyze table structure,
data quality, statistics, and column distributions.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.models.connection import Connection as ConnectionModel, ConnectionType
from app.services.data_profiler_service import data_profiler
from app.services.postgres_service import postgres_service
from app.services.mysql_service import mysql_service
from app.services.encryption_service import encryption_service
from app.database import get_db
from app.core.security import get_current_user, CurrentUser

router = APIRouter()


class TopValueResponse(BaseModel):
    value: str
    count: int
    percent: float


class ColumnProfileResponse(BaseModel):
    name: str
    data_type: str
    sql_type: str
    null_count: int
    null_percent: float
    unique_count: int
    unique_percent: float
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    std_dev: Optional[float] = None
    top_values: List[TopValueResponse] = []


class DatasetProfileResponse(BaseModel):
    connection_id: str
    connection_name: str
    schema_name: str
    table_name: str
    row_count: int
    column_count: int
    columns: List[ColumnProfileResponse]
    profiled_at: str
    quality_score: float
    has_temporal: bool
    has_numeric: bool
    has_categorical: bool


class TableListResponse(BaseModel):
    schema_name: str
    table_name: str
    row_count: Optional[int]
    column_count: int


async def _get_connection_string(conn: ConnectionModel) -> str:
    """Build connection string from stored connection data."""
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    return postgres_service.build_connection_string(
        host=conn.host or "localhost",
        port=conn.port or 5432,
        database=conn.database_name or "",
        username=conn.username,
        password=password,
        extra=conn.additional_config
    )


@router.get("/connections", response_model=List[dict])
async def list_profilable_connections(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """List connections that support profiling (PostgreSQL, MySQL)."""
    result = await db.execute(
        select(ConnectionModel).where(
            ConnectionModel.type.in_([ConnectionType.postgresql, ConnectionType.mysql, ConnectionType.csv])
        ).order_by(ConnectionModel.name)
    )
    connections = result.scalars().all()

    return [
        {
            "id": str(conn.id),
            "name": conn.name,
            "type": conn.type.value,
            "database": conn.database_name
        }
        for conn in connections
    ]


@router.get("/connections/{connection_id}/tables", response_model=List[TableListResponse])
async def list_tables(
    connection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """List tables for a connection that can be profiled."""
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    if conn.type == ConnectionType.csv:
        # For CSV connections, return the uploaded table
        table_name = conn.additional_config.get('table_name') if conn.additional_config else None
        if table_name:
            return [TableListResponse(
                schema_name="public",
                table_name=table_name,
                row_count=conn.additional_config.get('row_count'),
                column_count=len(conn.additional_config.get('columns', []))
            )]
        return []

    if conn.type != ConnectionType.postgresql:
        raise HTTPException(status_code=400, detail=f"Profiling not supported for {conn.type.value}")

    try:
        conn_str = await _get_connection_string(conn)
        tables = await data_profiler.get_tables_summary(conn_str)
        return [
            TableListResponse(
                schema_name=t.schema_name,
                table_name=t.table_name,
                row_count=t.row_count,
                column_count=t.column_count
            )
            for t in tables
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tables: {str(e)}")


@router.get("/profile/{connection_id}/{schema_name}/{table_name}", response_model=DatasetProfileResponse)
async def profile_table(
    connection_id: str,
    schema_name: str,
    table_name: str,
    sample_size: int = 10000,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Profile a specific table and return detailed statistics."""
    from datetime import datetime

    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    if conn.type not in [ConnectionType.postgresql, ConnectionType.csv]:
        raise HTTPException(status_code=400, detail=f"Profiling not supported for {conn.type.value}")

    try:
        conn_str = await _get_connection_string(conn)
        profile = await data_profiler.profile_table(conn_str, schema_name, table_name, sample_size)

        # Calculate quality score based on null percentages
        total_null_percent = sum(c.null_percent for c in profile.columns)
        avg_null_percent = total_null_percent / len(profile.columns) if profile.columns else 0
        quality_score = max(0, 100 - avg_null_percent * 2)  # Penalize nulls

        # Build response
        columns = []
        for col in profile.columns:
            unique_percent = (col.distinct_count / profile.row_count * 100) if profile.row_count > 0 else 0

            top_values = []
            if col.top_values:
                for tv in col.top_values:
                    top_values.append(TopValueResponse(
                        value=str(tv.value) if tv.value else "",
                        count=tv.count,
                        percent=tv.percent
                    ))

            columns.append(ColumnProfileResponse(
                name=col.name,
                data_type=col.data_type.value if hasattr(col.data_type, 'value') else str(col.data_type),
                sql_type=col.sql_type,
                null_count=col.null_count,
                null_percent=col.null_percent,
                unique_count=col.distinct_count,
                unique_percent=round(unique_percent, 2),
                min_value=str(col.min_value) if col.min_value is not None else None,
                max_value=str(col.max_value) if col.max_value is not None else None,
                mean=col.mean,
                top_values=top_values
            ))

        return DatasetProfileResponse(
            connection_id=connection_id,
            connection_name=conn.name,
            schema_name=schema_name,
            table_name=table_name,
            row_count=profile.row_count,
            column_count=len(profile.columns),
            columns=columns,
            profiled_at=datetime.utcnow().isoformat() + "Z",
            quality_score=round(quality_score, 1),
            has_temporal=profile.has_temporal,
            has_numeric=profile.has_numeric,
            has_categorical=profile.has_categorical
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to profile table: {str(e)}")
