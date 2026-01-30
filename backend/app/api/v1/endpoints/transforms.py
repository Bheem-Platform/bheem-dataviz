"""
Transform Recipe API endpoints.

Provides CRUD operations for transform recipes and execution endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime
import time
import logging

from app.schemas.transform import (
    TransformRecipeCreate,
    TransformRecipeUpdate,
    TransformRecipeResponse,
    TransformExecuteRequest,
    TransformPreviewResponse,
)
from app.models.transform import TransformRecipe
from app.models.connection import Connection as ConnectionModel, ConnectionType
from app.services.transform_service import get_transform_service
from app.services.postgres_service import postgres_service
from app.services.mysql_service import mysql_service
from app.services.mongodb_service import mongodb_service
from app.services.mongodb_transform_service import mongodb_transform_service
from app.services.encryption_service import encryption_service
from app.database import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_connection_or_404(connection_id: str, db: AsyncSession) -> ConnectionModel:
    """Get a connection by ID or raise 404."""
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == connection_id)
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return conn


def _model_to_response(recipe: TransformRecipe) -> TransformRecipeResponse:
    """Convert database model to response schema."""
    return TransformRecipeResponse(
        id=str(recipe.id),
        name=recipe.name,
        description=recipe.description,
        connection_id=str(recipe.connection_id),
        source_table=recipe.source_table,
        source_schema=recipe.source_schema,
        steps=recipe.steps or [],
        result_columns=recipe.result_columns or [],
        row_count=recipe.row_count,
        last_executed=recipe.last_executed,
        execution_time_ms=recipe.execution_time_ms,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at
    )


import asyncio
import re

# Security: Query timeout to prevent resource exhaustion
QUERY_TIMEOUT_SECONDS = 30


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to prevent information disclosure.

    Removes sensitive information like connection strings, passwords,
    table names, and internal paths from error messages.
    """
    msg = str(error)

    # Remove connection strings (postgresql://, mysql://, mongodb://)
    msg = re.sub(r'(postgresql|mysql|mongodb)://[^\s]+', '[connection]', msg)

    # Remove file paths
    msg = re.sub(r'/[^\s]+\.py', '[file]', msg)

    # Remove IP addresses
    msg = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[host]', msg)

    # Generic message for common database errors
    msg_lower = msg.lower()
    if 'syntax error' in msg_lower:
        return "SQL syntax error in transform. Please check your configuration."
    if 'permission denied' in msg_lower:
        return "Permission denied. Check database access."
    if 'does not exist' in msg_lower:
        return "Referenced table or column does not exist."
    if 'connection' in msg_lower and ('refused' in msg_lower or 'failed' in msg_lower):
        return "Database connection failed. Please check connection settings."

    # Limit message length
    if len(msg) > 200:
        msg = msg[:200] + "..."

    return msg


async def execute_sql_on_connection(
    conn: ConnectionModel,
    sql: str,
    limit: int = 100,
    timeout: int = QUERY_TIMEOUT_SECONDS
) -> dict:
    """Execute SQL on a connection and return results with timeout protection."""
    # Decrypt password
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    start_time = time.time()

    try:
        if conn.type == ConnectionType.mysql:
            use_ssl = conn.additional_config.get("ssl", False) if conn.additional_config else False
            result = await asyncio.wait_for(
                mysql_service.execute_query(
                    host=conn.host or "localhost",
                    port=conn.port or 3306,
                    database=conn.database_name or "",
                    sql=sql,
                    username=conn.username,
                    password=password,
                    limit=limit,
                    ssl=use_ssl
                ),
                timeout=timeout
            )
        elif conn.type in (ConnectionType.csv, ConnectionType.excel):
            # For CSV/Excel, query the app database
            result = await asyncio.wait_for(
                postgres_service.execute_query(settings.DATABASE_URL, sql, limit),
                timeout=timeout
            )
        else:
            # PostgreSQL and others
            conn_str = postgres_service.build_connection_string(
                host=conn.host or "localhost",
                port=conn.port or 5432,
                database=conn.database_name or "",
                username=conn.username,
                password=password
            )
            result = await asyncio.wait_for(
                postgres_service.execute_query(conn_str, sql, limit),
                timeout=timeout
            )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail=f"Query timed out after {timeout} seconds. Try simplifying your transform or adding filters."
        )

    execution_time = int((time.time() - start_time) * 1000)
    result["execution_time_ms"] = execution_time

    return result


async def _execute_mongodb_transform(
    conn: ConnectionModel,
    request,
    password: str
) -> TransformPreviewResponse:
    """Execute a transform on a MongoDB connection using aggregation pipeline."""
    import json

    additional = conn.additional_config or {}

    # Fetch available columns for the collection
    available_columns = None
    try:
        columns_result = await mongodb_service.get_table_columns(
            host=conn.host or "localhost",
            port=conn.port or 27017,
            database=conn.database_name or "",
            collection=request.source_table,
            username=conn.username,
            password=password,
            auth_source=additional.get("auth_source"),
            is_srv=additional.get("is_srv", False),
            ssl=additional.get("ssl", False)
        )
        if columns_result and isinstance(columns_result, list):
            available_columns = [c["name"] for c in columns_result]
            logger.info(f"MongoDB available columns: {available_columns}")
    except Exception as e:
        logger.warning(f"Could not fetch MongoDB columns: {e}")

    # Generate aggregation pipeline
    pipeline = mongodb_transform_service.generate_pipeline(
        steps=request.steps,
        limit=request.limit if request.preview else None,
        available_columns=available_columns
    )

    logger.info(f"Generated MongoDB pipeline: {json.dumps(pipeline, default=str)}")

    try:
        # Execute aggregation
        result = await mongodb_service.execute_aggregation(
            host=conn.host or "localhost",
            port=conn.port or 27017,
            database=conn.database_name or "",
            collection=request.source_table,
            pipeline=pipeline,
            limit=request.limit,
            username=conn.username,
            password=password,
            auth_source=additional.get("auth_source"),
            is_srv=additional.get("is_srv", False),
            ssl=additional.get("ssl", False)
        )

        if result.get("error"):
            raise HTTPException(status_code=400, detail=f"MongoDB aggregation failed: {result['error']}")

        # Build column info
        columns = []
        for col_name in result.get("columns", []):
            columns.append({"name": col_name, "type": "unknown"})

        # Format pipeline as string for display (similar to SQL)
        pipeline_str = json.dumps(pipeline, indent=2, default=str)

        return TransformPreviewResponse(
            columns=columns,
            rows=result.get("rows", []),
            total_rows=result.get("total", len(result.get("rows", []))),
            preview_rows=len(result.get("rows", [])),
            execution_time_ms=result.get("execution_time_ms", 0),
            sql_generated=f"// MongoDB Aggregation Pipeline\ndb.{request.source_table}.aggregate({pipeline_str})"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MongoDB transform execution failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Transform execution failed: {sanitize_error_message(e)}"
        )


# ============================================================================
# RECIPE CRUD ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[TransformRecipeResponse])
async def list_recipes(
    connection_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all transform recipes, optionally filtered by connection."""
    query = select(TransformRecipe).order_by(TransformRecipe.updated_at.desc())

    if connection_id:
        query = query.where(TransformRecipe.connection_id == connection_id)

    result = await db.execute(query)
    recipes = result.scalars().all()

    return [_model_to_response(r) for r in recipes]


@router.post("/", response_model=TransformRecipeResponse)
async def create_recipe(
    recipe: TransformRecipeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new transform recipe."""
    # Verify connection exists
    await get_connection_or_404(recipe.connection_id, db)

    db_recipe = TransformRecipe(
        name=recipe.name,
        description=recipe.description,
        connection_id=recipe.connection_id,
        source_table=recipe.source_table,
        source_schema=recipe.source_schema,
        steps=recipe.steps
    )

    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)

    return _model_to_response(db_recipe)


@router.get("/{recipe_id}", response_model=TransformRecipeResponse)
async def get_recipe(recipe_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific transform recipe."""
    result = await db.execute(
        select(TransformRecipe).where(TransformRecipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return _model_to_response(recipe)


@router.put("/{recipe_id}", response_model=TransformRecipeResponse)
async def update_recipe(
    recipe_id: str,
    update_data: TransformRecipeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a transform recipe."""
    result = await db.execute(
        select(TransformRecipe).where(TransformRecipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(recipe, field, value)

    recipe.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(recipe)

    return _model_to_response(recipe)


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a transform recipe."""
    result = await db.execute(
        select(TransformRecipe).where(TransformRecipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    await db.delete(recipe)
    await db.commit()

    return {"status": "deleted"}


@router.post("/{recipe_id}/clone", response_model=TransformRecipeResponse)
async def clone_recipe(recipe_id: str, db: AsyncSession = Depends(get_db)):
    """Clone a transform recipe."""
    result = await db.execute(
        select(TransformRecipe).where(TransformRecipe.id == recipe_id)
    )
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Recipe not found")

    cloned = TransformRecipe(
        name=f"{original.name} (Copy)",
        description=original.description,
        connection_id=original.connection_id,
        source_table=original.source_table,
        source_schema=original.source_schema,
        steps=original.steps
    )

    db.add(cloned)
    await db.commit()
    await db.refresh(cloned)

    return _model_to_response(cloned)


# ============================================================================
# EXECUTION ENDPOINTS
# ============================================================================

@router.post("/execute", response_model=TransformPreviewResponse)
async def execute_transform(
    request: TransformExecuteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a transform and return results.

    This can be used for ad-hoc transforms or testing before saving.
    """
    # Get connection
    conn = await get_connection_or_404(request.connection_id, db)

    # Decrypt password
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    # Handle MongoDB connections separately
    if conn.type == ConnectionType.mongodb:
        return await _execute_mongodb_transform(conn, request, password)

    # Determine dialect for SQL databases
    if conn.type == ConnectionType.mysql:
        dialect = "mysql"
    else:
        dialect = "postgresql"

    # Get transform service for dialect
    transform_service = get_transform_service(dialect)

    # Fetch available columns for column transformations
    available_columns = None
    try:
        transform_step_types = {'fill_null', 'cast', 'trim', 'case', 'replace'}
        has_transforms = any(s.get('type') in transform_step_types for s in request.steps)

        if has_transforms:
            if conn.type == ConnectionType.mysql:
                use_ssl = conn.additional_config.get("ssl", False) if conn.additional_config else False
                columns_result = await mysql_service.get_table_columns(
                    host=conn.host or "localhost",
                    port=conn.port or 3306,
                    database=conn.database_name or "",
                    table=request.source_table,
                    username=conn.username,
                    password=password,
                    ssl=use_ssl
                )
            else:
                conn_str = postgres_service.build_connection_string(
                    host=conn.host or "localhost",
                    port=conn.port or 5432,
                    database=conn.database_name or "",
                    username=conn.username,
                    password=password
                )
                columns_result = await postgres_service.get_table_columns(
                    conn_str, request.source_schema, request.source_table
                )

            if columns_result and isinstance(columns_result, list):
                available_columns = [c["name"] for c in columns_result]
    except Exception as e:
        logger.warning(f"Could not fetch columns for transform: {e}")

    # Generate SQL
    sql = transform_service.generate_sql(
        source_table=request.source_table,
        source_schema=request.source_schema,
        steps=request.steps,
        limit=request.limit if request.preview else None,
        offset=request.offset if request.preview else 0,
        available_columns=available_columns
    )

    logger.info(f"Generated SQL: {sql}")

    try:
        # Execute query
        result = await execute_sql_on_connection(conn, sql, request.limit)

        # Get total count if preview
        total_rows = result.get("total", len(result.get("rows", [])))
        if request.preview and request.steps:
            try:
                count_sql = transform_service.generate_count_sql(
                    source_table=request.source_table,
                    source_schema=request.source_schema,
                    steps=request.steps
                )
                count_result = await execute_sql_on_connection(conn, count_sql, 1)
                if count_result.get("rows"):
                    total_rows = count_result["rows"][0].get("total", total_rows)
            except Exception as e:
                logger.warning(f"Failed to get count: {e}")

        # Build column info
        columns = []
        for col_name in result.get("columns", []):
            columns.append({"name": col_name, "type": "unknown"})

        return TransformPreviewResponse(
            columns=columns,
            rows=result.get("rows", []),
            total_rows=total_rows,
            preview_rows=len(result.get("rows", [])),
            execution_time_ms=result.get("execution_time_ms", 0),
            sql_generated=sql
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Transform execution failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Transform execution failed: {sanitize_error_message(e)}"
        )


@router.post("/{recipe_id}/execute", response_model=TransformPreviewResponse)
async def execute_saved_recipe(
    recipe_id: str,
    preview: bool = True,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Execute a saved transform recipe."""
    import json

    # Get recipe
    result = await db.execute(
        select(TransformRecipe).where(TransformRecipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Get connection
    conn = await get_connection_or_404(str(recipe.connection_id), db)

    # Decrypt password
    password = None
    if conn.encrypted_password:
        password = encryption_service.decrypt(conn.encrypted_password)

    steps = recipe.steps or []

    # Handle MongoDB connections
    if conn.type == ConnectionType.mongodb:
        additional = conn.additional_config or {}

        # Fetch available columns
        available_columns = None
        try:
            columns_result = await mongodb_service.get_table_columns(
                host=conn.host or "localhost",
                port=conn.port or 27017,
                database=conn.database_name or "",
                collection=recipe.source_table,
                username=conn.username,
                password=password,
                auth_source=additional.get("auth_source"),
                is_srv=additional.get("is_srv", False),
                ssl=additional.get("ssl", False)
            )
            if columns_result and isinstance(columns_result, list):
                available_columns = [c["name"] for c in columns_result]
        except Exception as e:
            logger.warning(f"Could not fetch MongoDB columns: {e}")

        # Generate pipeline
        pipeline = mongodb_transform_service.generate_pipeline(
            steps=steps,
            limit=limit if preview else None,
            available_columns=available_columns
        )

        try:
            exec_result = await mongodb_service.execute_aggregation(
                host=conn.host or "localhost",
                port=conn.port or 27017,
                database=conn.database_name or "",
                collection=recipe.source_table,
                pipeline=pipeline,
                limit=limit,
                username=conn.username,
                password=password,
                auth_source=additional.get("auth_source"),
                is_srv=additional.get("is_srv", False),
                ssl=additional.get("ssl", False)
            )

            if exec_result.get("error"):
                raise HTTPException(status_code=400, detail=f"MongoDB aggregation failed: {exec_result['error']}")

            # Update recipe stats
            recipe.last_executed = datetime.utcnow()
            recipe.execution_time_ms = exec_result.get("execution_time_ms", 0)
            recipe.row_count = exec_result.get("total", len(exec_result.get("rows", [])))
            recipe.result_columns = [{"name": col, "type": "unknown"} for col in exec_result.get("columns", [])]
            await db.commit()

            pipeline_str = json.dumps(pipeline, indent=2, default=str)

            return TransformPreviewResponse(
                columns=recipe.result_columns,
                rows=exec_result.get("rows", []),
                total_rows=recipe.row_count or 0,
                preview_rows=len(exec_result.get("rows", [])),
                execution_time_ms=exec_result.get("execution_time_ms", 0),
                sql_generated=f"// MongoDB Aggregation Pipeline\ndb.{recipe.source_table}.aggregate({pipeline_str})"
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"MongoDB recipe execution failed: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Recipe execution failed: {sanitize_error_message(e)}")

    # Determine dialect for SQL databases
    if conn.type == ConnectionType.mysql:
        dialect = "mysql"
    else:
        dialect = "postgresql"

    transform_service = get_transform_service(dialect)

    # Fetch available columns for column transformations
    available_columns = None
    try:
        transform_step_types = {'fill_null', 'cast', 'trim', 'case', 'replace'}
        has_transforms = any(s.get('type') in transform_step_types for s in steps)

        if has_transforms:
            if conn.type == ConnectionType.mysql:
                use_ssl = conn.additional_config.get("ssl", False) if conn.additional_config else False
                columns_result = await mysql_service.get_table_columns(
                    host=conn.host or "localhost",
                    port=conn.port or 3306,
                    database=conn.database_name or "",
                    table=recipe.source_table,
                    username=conn.username,
                    password=password,
                    ssl=use_ssl
                )
            else:
                conn_str = postgres_service.build_connection_string(
                    host=conn.host or "localhost",
                    port=conn.port or 5432,
                    database=conn.database_name or "",
                    username=conn.username,
                    password=password
                )
                columns_result = await postgres_service.get_table_columns(
                    conn_str, recipe.source_schema, recipe.source_table
                )

            if columns_result and isinstance(columns_result, list):
                available_columns = [c["name"] for c in columns_result]
    except Exception as e:
        logger.warning(f"Could not fetch columns for recipe execution: {e}")

    # Generate SQL
    sql = transform_service.generate_sql(
        source_table=recipe.source_table,
        source_schema=recipe.source_schema,
        steps=steps,
        limit=limit if preview else None,
        available_columns=available_columns
    )

    try:
        exec_result = await execute_sql_on_connection(conn, sql, limit)

        # Update recipe execution stats
        recipe.last_executed = datetime.utcnow()
        recipe.execution_time_ms = exec_result.get("execution_time_ms", 0)
        recipe.row_count = exec_result.get("total", len(exec_result.get("rows", [])))

        # Store result columns
        recipe.result_columns = [
            {"name": col, "type": "unknown"}
            for col in exec_result.get("columns", [])
        ]

        await db.commit()

        columns = [{"name": col, "type": "unknown"} for col in exec_result.get("columns", [])]

        return TransformPreviewResponse(
            columns=columns,
            rows=exec_result.get("rows", []),
            total_rows=recipe.row_count or 0,
            preview_rows=len(exec_result.get("rows", [])),
            execution_time_ms=exec_result.get("execution_time_ms", 0),
            sql_generated=sql
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Recipe execution failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Recipe execution failed: {sanitize_error_message(e)}"
        )


@router.get("/{recipe_id}/sql")
async def get_recipe_sql(recipe_id: str, db: AsyncSession = Depends(get_db)):
    """Get the generated SQL for a recipe (for debugging/export)."""
    result = await db.execute(
        select(TransformRecipe).where(TransformRecipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Get connection to determine dialect
    conn = await get_connection_or_404(str(recipe.connection_id), db)

    dialect = "mysql" if conn.type == ConnectionType.mysql else "postgresql"
    transform_service = get_transform_service(dialect)

    sql = transform_service.generate_sql(
        source_table=recipe.source_table,
        source_schema=recipe.source_schema,
        steps=recipe.steps or []
    )

    return {"sql": sql, "dialect": dialect}
