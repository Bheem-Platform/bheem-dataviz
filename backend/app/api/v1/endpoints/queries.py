from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.query import QueryExecute, QueryResult
from app.services.postgres_service import postgres_service
from app.services.mysql_service import MySQLService
from app.services.encryption_service import encryption_service
from app.models.connection import Connection as ConnectionModel, ConnectionType
from app.models.user import User
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter()

saved_queries = {}


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


@router.post("/execute", response_model=QueryResult)
async def execute_query(
    query: QueryExecute,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a SQL query on a connected database."""
    # Get connection from database
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == query.connection_id)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    if not conn.encrypted_password and not conn.host:
        raise HTTPException(
            status_code=400,
            detail="Connection credentials not found. Please recreate the connection."
        )

    # Decrypt password
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    try:
        if conn.type == ConnectionType.postgresql:
            conn_str = await _get_connection_string(conn)
            result = await postgres_service.execute_query(
                conn_str,
                query.sql,
                query.limit or 1000
            )
        elif conn.type == ConnectionType.mysql:
            result = await MySQLService.execute_query(
                host=conn.host or "localhost",
                port=conn.port or 3306,
                database=conn.database_name or "",
                sql=query.sql,
                username=conn.username,
                password=password,
                limit=query.limit or 1000
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Query execution not implemented for type: {conn.type.value}"
            )

        return QueryResult(
            columns=result["columns"],
            rows=result["rows"],
            total=result["total"],
            execution_time=result["execution_time"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@router.post("/preview", response_model=QueryResult)
async def preview_query(
    query: QueryExecute,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview a SQL query (same as execute but with smaller limit)."""
    query.limit = min(query.limit or 100, 100)
    return await execute_query(query, db)


@router.get("/saved")
async def list_saved_queries(
    current_user: User = Depends(get_current_user)
):
    """List all saved queries."""
    return list(saved_queries.values())


@router.post("/saved")
async def save_query(
    query: QueryExecute,
    current_user: User = Depends(get_current_user)
):
    """Save a query for later use."""
    query_id = str(len(saved_queries) + 1)
    saved_queries[query_id] = {"id": query_id, **query.model_dump()}
    return saved_queries[query_id]
