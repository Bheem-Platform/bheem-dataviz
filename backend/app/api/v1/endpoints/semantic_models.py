"""API endpoints for Semantic Models - Table Relationships."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import time

from ....models.semantic import SemanticModel, Dimension, Measure, SemanticJoin
from ....models.transform import TransformRecipe
from ....models.connection import Connection as ConnectionModel, ConnectionType
from ....database import get_db
from ....services.postgres_service import postgres_service
from ....services.mysql_service import MySQLService
from ....services.encryption_service import encryption_service
from ....services.transform_service import get_transform_service
from pydantic import BaseModel, Field


router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class TablePosition(BaseModel):
    """Position of a table on the canvas."""
    x: float = 0
    y: float = 0


class TableInfo(BaseModel):
    """Table included in the model."""
    name: str
    schema_name: str = "public"
    alias: Optional[str] = None
    x: float = 0
    y: float = 0


class RelationshipCreate(BaseModel):
    """Create a join/relationship between tables or transforms."""
    name: Optional[str] = None
    from_table: Optional[str] = None  # Not needed for transform-based models
    from_column: str
    to_table: Optional[str] = None  # For table joins
    to_transform_id: Optional[str] = None  # For transform joins
    to_column: str
    join_type: str = "left"  # left, inner, right, full


class RelationshipResponse(BaseModel):
    """Response for a relationship."""
    id: str
    name: Optional[str] = None
    target_schema: str
    target_table: str
    target_alias: Optional[str] = None
    join_type: str
    join_condition: str
    created_at: Optional[datetime] = None


class MeasureCreate(BaseModel):
    """Create a measure."""
    name: str
    description: Optional[str] = None
    column_name: str
    aggregation: str = "sum"  # sum, count, avg, min, max, count_distinct
    display_format: Optional[str] = None


class MeasureResponse(BaseModel):
    """Response for a measure."""
    id: str
    name: str
    description: Optional[str] = None
    column_name: str
    expression: str
    aggregation: str
    display_format: Optional[str] = None
    created_at: Optional[datetime] = None


class DimensionCreate(BaseModel):
    """Create a dimension."""
    name: str
    description: Optional[str] = None
    column_name: str
    display_format: Optional[str] = None


class DimensionResponse(BaseModel):
    """Response for a dimension."""
    id: str
    name: str
    description: Optional[str] = None
    column_name: str
    display_format: Optional[str] = None
    created_at: Optional[datetime] = None


class JoinedTransformSchema(BaseModel):
    """Schema for a joined transform."""
    transform_id: str
    alias: str  # Alias for the transform in SQL
    join_type: str = "left"  # left, inner, right, full
    join_on: List[Dict[str, str]]  # [{"left": "col1", "right": "col2"}]


class SemanticModelCreate(BaseModel):
    """Create a semantic model."""
    name: str
    description: Optional[str] = None
    connection_id: str
    # Primary source: either table or transform (mutually exclusive)
    transform_id: Optional[str] = None  # If set, use transform as primary source
    schema_name: Optional[str] = "public"  # Used when transform_id is None
    table_name: Optional[str] = None  # Used when transform_id is None
    # Additional transforms to join
    joined_transforms: List[JoinedTransformSchema] = []


class SemanticModelUpdate(BaseModel):
    """Update a semantic model."""
    name: Optional[str] = None
    description: Optional[str] = None


class SemanticModelResponse(BaseModel):
    """Full semantic model response."""
    id: str
    name: str
    description: Optional[str] = None
    connection_id: str
    transform_id: Optional[str] = None
    transform_name: Optional[str] = None  # For display purposes
    schema_name: Optional[str] = None
    table_name: Optional[str] = None
    joined_transforms: List[Dict[str, Any]] = []  # Additional transforms to join
    is_active: bool
    dimensions: List[DimensionResponse] = []
    measures: List[MeasureResponse] = []
    joins: List[RelationshipResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SemanticModelSummary(BaseModel):
    """Summary for list view."""
    id: str
    name: str
    description: Optional[str] = None
    connection_id: str
    transform_id: Optional[str] = None
    transform_name: Optional[str] = None
    schema_name: Optional[str] = None
    table_name: Optional[str] = None
    dimensions_count: int = 0
    measures_count: int = 0
    joins_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def model_to_response(model: SemanticModel) -> SemanticModelResponse:
    """Convert SQLAlchemy model to response schema."""
    transform_name = None
    if model.transform:
        transform_name = model.transform.name

    return SemanticModelResponse(
        id=str(model.id),
        name=model.name,
        description=model.description,
        connection_id=model.connection_id,
        transform_id=str(model.transform_id) if model.transform_id else None,
        transform_name=transform_name,
        schema_name=model.schema_name,
        table_name=model.table_name,
        joined_transforms=model.joined_transforms or [],
        is_active=model.is_active,
        dimensions=[
            DimensionResponse(
                id=str(d.id),
                name=d.name,
                description=d.description,
                column_name=d.column_name,
                display_format=d.display_format,
                created_at=d.created_at
            ) for d in model.dimensions
        ],
        measures=[
            MeasureResponse(
                id=str(m.id),
                name=m.name,
                description=m.description,
                column_name=m.column_name,
                expression=m.expression,
                aggregation=m.aggregation,
                display_format=m.display_format,
                created_at=m.created_at
            ) for m in model.measures
        ],
        joins=[
            RelationshipResponse(
                id=str(j.id),
                name=j.target_alias,
                target_schema=j.target_schema,
                target_table=j.target_table,
                target_alias=j.target_alias,
                join_type=j.join_type,
                join_condition=j.join_condition,
                created_at=j.created_at
            ) for j in model.joins
        ],
        created_at=model.created_at,
        updated_at=model.updated_at
    )


# ============================================================================
# MODEL CRUD
# ============================================================================

@router.get("/", response_model=List[SemanticModelSummary])
async def list_models(
    connection_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all semantic models."""
    query = select(SemanticModel).options(
        selectinload(SemanticModel.dimensions),
        selectinload(SemanticModel.measures),
        selectinload(SemanticModel.joins),
        selectinload(SemanticModel.transform)
    )

    if connection_id:
        query = query.where(SemanticModel.connection_id == connection_id)

    query = query.order_by(SemanticModel.updated_at.desc())
    result = await db.execute(query)
    models = result.scalars().all()

    return [
        SemanticModelSummary(
            id=str(m.id),
            name=m.name,
            description=m.description,
            connection_id=m.connection_id,
            transform_id=str(m.transform_id) if m.transform_id else None,
            transform_name=m.transform.name if m.transform else None,
            schema_name=m.schema_name,
            table_name=m.table_name,
            dimensions_count=len(m.dimensions),
            measures_count=len(m.measures),
            joins_count=len(m.joins) + len(m.joined_transforms or []),
            created_at=m.created_at,
            updated_at=m.updated_at
        ) for m in models
    ]


@router.post("/", response_model=SemanticModelResponse)
async def create_model(
    model: SemanticModelCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new semantic model."""
    # Validate: need either transform_id OR table_name
    if not model.transform_id and not model.table_name:
        raise HTTPException(
            status_code=400,
            detail="Either transform_id or table_name is required"
        )

    # Convert joined_transforms to list of dicts for storage
    joined_transforms_data = [
        {
            "transform_id": jt.transform_id,
            "alias": jt.alias,
            "join_type": jt.join_type,
            "join_on": jt.join_on
        }
        for jt in model.joined_transforms
    ] if model.joined_transforms else []

    model_id = uuid.uuid4()
    db_model = SemanticModel(
        id=model_id,
        name=model.name,
        description=model.description,
        connection_id=model.connection_id,
        transform_id=uuid.UUID(model.transform_id) if model.transform_id else None,
        schema_name=model.schema_name if not model.transform_id else None,
        table_name=model.table_name if not model.transform_id else None,
        joined_transforms=joined_transforms_data,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(db_model)
    await db.commit()

    # Fetch the model with relationships loaded
    return await get_model(str(model_id), db)


@router.get("/{model_id}", response_model=SemanticModelResponse)
async def get_model(
    model_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a semantic model by ID."""
    query = select(SemanticModel).options(
        selectinload(SemanticModel.dimensions),
        selectinload(SemanticModel.measures),
        selectinload(SemanticModel.joins),
        selectinload(SemanticModel.transform)
    ).where(SemanticModel.id == uuid.UUID(model_id))

    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model_to_response(model)


@router.put("/{model_id}", response_model=SemanticModelResponse)
async def update_model(
    model_id: str,
    update: SemanticModelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a semantic model."""
    query = select(SemanticModel).where(SemanticModel.id == uuid.UUID(model_id))

    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    if update.name is not None:
        model.name = update.name
    if update.description is not None:
        model.description = update.description

    model.updated_at = datetime.utcnow()

    await db.commit()

    # Return with relationships loaded
    return await get_model(model_id, db)


@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a semantic model."""
    query = select(SemanticModel).where(SemanticModel.id == uuid.UUID(model_id))
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    await db.delete(model)
    await db.commit()

    return {"status": "deleted"}


# ============================================================================
# RELATIONSHIP/JOIN OPERATIONS
# ============================================================================

@router.post("/{model_id}/joins", response_model=SemanticModelResponse)
async def add_join(
    model_id: str,
    join: RelationshipCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a table or transform relationship/join to a semantic model."""
    # Get the model
    query = select(SemanticModel).options(
        selectinload(SemanticModel.dimensions),
        selectinload(SemanticModel.measures),
        selectinload(SemanticModel.joins),
        selectinload(SemanticModel.transform)
    ).where(SemanticModel.id == uuid.UUID(model_id))

    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Determine if this is a transform join or table join
    if join.to_transform_id:
        # Transform join - add to joined_transforms JSONB field
        # Verify the transform exists
        transform_result = await db.execute(
            select(TransformRecipe).where(TransformRecipe.id == uuid.UUID(join.to_transform_id))
        )
        transform = transform_result.scalar_one_or_none()

        if not transform:
            raise HTTPException(status_code=404, detail="Transform not found")

        # Generate a short alias for the transform
        alias = f"t_{join.to_transform_id[:8]}"

        # Create the join entry
        new_join = {
            "transform_id": join.to_transform_id,
            "transform_name": transform.name,  # For display purposes
            "alias": alias,
            "join_type": join.join_type,
            "join_on": [{"left": join.from_column, "right": join.to_column}]
        }

        # Add to joined_transforms
        current_joins = model.joined_transforms or []
        current_joins.append(new_join)
        model.joined_transforms = current_joins

    else:
        # Table join - use SemanticJoin model
        if not join.to_table or not join.from_table:
            raise HTTPException(
                status_code=400,
                detail="from_table and to_table are required for table joins"
            )

        # Build join condition
        join_condition = f"{join.from_table}.{join.from_column} = {join.to_table}.{join.to_column}"

        # Create the join
        db_join = SemanticJoin(
            id=uuid.uuid4(),
            semantic_model_id=model.id,
            target_schema=model.schema_name or "public",
            target_table=join.to_table,
            target_alias=join.name,
            join_type=join.join_type,
            join_condition=join_condition,
            created_at=datetime.utcnow()
        )

        db.add(db_join)

    model.updated_at = datetime.utcnow()

    await db.commit()

    # Return updated model
    return await get_model(model_id, db)


@router.delete("/{model_id}/joins/{join_id}", response_model=SemanticModelResponse)
async def remove_join(
    model_id: str,
    join_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove a join from a semantic model.

    join_id can be either:
    - A UUID for SemanticJoin (table joins)
    - A transform_id for joined_transforms
    """
    # Get the model first
    query = select(SemanticModel).where(SemanticModel.id == uuid.UUID(model_id))
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Check if this is a joined transform (check joined_transforms array)
    if model.joined_transforms:
        # Try to remove from joined_transforms by transform_id
        original_length = len(model.joined_transforms)
        model.joined_transforms = [
            jt for jt in model.joined_transforms
            if jt.get('transform_id') != join_id
        ]

        if len(model.joined_transforms) < original_length:
            # We removed a joined transform
            model.updated_at = datetime.utcnow()
            await db.commit()
            return await get_model(model_id, db)

    # Otherwise, try to delete as SemanticJoin (table join)
    try:
        await db.execute(
            delete(SemanticJoin).where(
                SemanticJoin.id == uuid.UUID(join_id),
                SemanticJoin.semantic_model_id == uuid.UUID(model_id)
            )
        )
        model.updated_at = datetime.utcnow()
        await db.commit()
    except Exception:
        # Invalid UUID format - might already be handled above
        pass

    # Return updated model
    return await get_model(model_id, db)


# ============================================================================
# MEASURE OPERATIONS
# ============================================================================

@router.post("/{model_id}/measures", response_model=SemanticModelResponse)
async def add_measure(
    model_id: str,
    measure: MeasureCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a measure to a semantic model."""
    query = select(SemanticModel).where(SemanticModel.id == uuid.UUID(model_id))
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Build expression
    agg_upper = measure.aggregation.upper()
    if agg_upper == "COUNT_DISTINCT":
        expression = f"COUNT(DISTINCT {measure.column_name})"
    else:
        expression = f"{agg_upper}({measure.column_name})"

    db_measure = Measure(
        id=uuid.uuid4(),
        semantic_model_id=model.id,
        name=measure.name,
        description=measure.description,
        column_name=measure.column_name,
        expression=expression,
        aggregation=measure.aggregation,
        display_format=measure.display_format,
        created_at=datetime.utcnow()
    )

    db.add(db_measure)
    model.updated_at = datetime.utcnow()

    await db.commit()

    return await get_model(model_id, db)


@router.delete("/{model_id}/measures/{measure_id}", response_model=SemanticModelResponse)
async def remove_measure(
    model_id: str,
    measure_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove a measure from a semantic model."""
    await db.execute(
        delete(Measure).where(
            Measure.id == uuid.UUID(measure_id),
            Measure.semantic_model_id == uuid.UUID(model_id)
        )
    )

    query = select(SemanticModel).where(SemanticModel.id == uuid.UUID(model_id))
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if model:
        model.updated_at = datetime.utcnow()

    await db.commit()

    return await get_model(model_id, db)


# ============================================================================
# DIMENSION OPERATIONS
# ============================================================================

@router.post("/{model_id}/dimensions", response_model=SemanticModelResponse)
async def add_dimension(
    model_id: str,
    dimension: DimensionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a dimension to a semantic model."""
    query = select(SemanticModel).where(SemanticModel.id == uuid.UUID(model_id))
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    db_dimension = Dimension(
        id=uuid.uuid4(),
        semantic_model_id=model.id,
        name=dimension.name,
        description=dimension.description,
        column_name=dimension.column_name,
        display_format=dimension.display_format,
        created_at=datetime.utcnow()
    )

    db.add(db_dimension)
    model.updated_at = datetime.utcnow()

    await db.commit()

    return await get_model(model_id, db)


@router.delete("/{model_id}/dimensions/{dimension_id}", response_model=SemanticModelResponse)
async def remove_dimension(
    model_id: str,
    dimension_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove a dimension from a semantic model."""
    await db.execute(
        delete(Dimension).where(
            Dimension.id == uuid.UUID(dimension_id),
            Dimension.semantic_model_id == uuid.UUID(model_id)
        )
    )

    query = select(SemanticModel).where(SemanticModel.id == uuid.UUID(model_id))
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if model:
        model.updated_at = datetime.utcnow()

    await db.commit()

    return await get_model(model_id, db)


# ============================================================================
# PREVIEW / QUERY EXECUTION
# ============================================================================

class ModelPreviewRequest(BaseModel):
    """Request to preview model data."""
    measure_ids: List[str] = []
    dimension_ids: List[str] = []
    limit: int = 100


class ModelPreviewResponse(BaseModel):
    """Response from model preview."""
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    sql_generated: str
    execution_time_ms: float


@router.post("/{model_id}/preview", response_model=ModelPreviewResponse)
async def preview_model(
    model_id: str,
    request: ModelPreviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Preview data from a semantic model.

    Generates and executes a SQL query based on selected measures and dimensions.
    Supports both table-based and transform-based models.
    """
    start_time = time.time()

    # Get the model with all relationships including transform
    query = select(SemanticModel).options(
        selectinload(SemanticModel.dimensions),
        selectinload(SemanticModel.measures),
        selectinload(SemanticModel.joins),
        selectinload(SemanticModel.transform)
    ).where(SemanticModel.id == uuid.UUID(model_id))

    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Get connection
    conn_result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == model.connection_id)
    )
    conn = conn_result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Filter selected measures and dimensions
    selected_measures = [m for m in model.measures if str(m.id) in request.measure_ids]
    selected_dimensions = [d for d in model.dimensions if str(d.id) in request.dimension_ids]

    if not selected_measures and not selected_dimensions:
        raise HTTPException(
            status_code=400,
            detail="Select at least one measure or dimension"
        )

    # Determine SQL dialect
    is_mysql = conn.type == ConnectionType.mysql
    quote = '`' if is_mysql else '"'

    # Build SELECT clause
    select_parts = []

    # Add dimensions
    for dim in selected_dimensions:
        select_parts.append(f'{quote}{dim.column_name}{quote}')

    # Add measures with aggregations
    for measure in selected_measures:
        agg = measure.aggregation.upper()
        col = f'{quote}{measure.column_name}{quote}'
        alias = f'{quote}{measure.name}{quote}'

        if agg == 'COUNT_DISTINCT':
            select_parts.append(f'COUNT(DISTINCT {col}) AS {alias}')
        else:
            select_parts.append(f'{agg}({col}) AS {alias}')

    # Build FROM clause - use transform SQL or table
    cte_parts = []  # CTEs for transforms
    transform_service = get_transform_service(conn.type.value if hasattr(conn.type, 'value') else str(conn.type))

    if model.transform_id and model.transform:
        # Primary transform as source
        primary_sql = transform_service.generate_sql(
            source_table=model.transform.source_table,
            source_schema=model.transform.source_schema,
            steps=model.transform.steps or []
        )
        cte_parts.append(f'primary_data AS ({primary_sql})')
        from_clause = 'primary_data'

        # Handle joined transforms
        if model.joined_transforms:
            for jt in model.joined_transforms:
                # Load the joined transform
                jt_result = await db.execute(
                    select(TransformRecipe).where(TransformRecipe.id == jt['transform_id'])
                )
                joined_transform = jt_result.scalar_one_or_none()

                if joined_transform:
                    # Generate SQL for this transform
                    jt_sql = transform_service.generate_sql(
                        source_table=joined_transform.source_table,
                        source_schema=joined_transform.source_schema,
                        steps=joined_transform.steps or []
                    )
                    alias = jt.get('alias', f'jt_{jt["transform_id"][:8]}')
                    cte_parts.append(f'{alias} AS ({jt_sql})')

                    # Build JOIN clause
                    join_type = jt.get('join_type', 'left').upper()
                    join_conditions = []
                    for join_on in jt.get('join_on', []):
                        left_col = f'primary_data.{quote}{join_on["left"]}{quote}'
                        right_col = f'{alias}.{quote}{join_on["right"]}{quote}'
                        join_conditions.append(f'{left_col} = {right_col}')

                    if join_conditions:
                        from_clause += f' {join_type} JOIN {alias} ON {" AND ".join(join_conditions)}'

    else:
        # Use table directly
        from_clause = f'{quote}{model.schema_name}{quote}.{quote}{model.table_name}{quote}'

        # Add table JOINs (for table-based models)
        for join in model.joins:
            join_type = join.join_type.upper()
            from_clause += f' {join_type} JOIN {quote}{join.target_schema}{quote}.{quote}{join.target_table}{quote}'
            from_clause += f' ON {join.join_condition}'

    # Build GROUP BY (if we have both measures and dimensions)
    group_by = ''
    if selected_dimensions and selected_measures:
        group_cols = [f'{quote}{d.column_name}{quote}' for d in selected_dimensions]
        group_by = f'GROUP BY {", ".join(group_cols)}'

    # Build final SQL with CTEs if needed
    if cte_parts:
        sql = f'WITH {", ".join(cte_parts)} SELECT {", ".join(select_parts)} FROM {from_clause}'
    else:
        sql = f'SELECT {", ".join(select_parts)} FROM {from_clause}'
    if group_by:
        sql += f' {group_by}'
    sql += f' LIMIT {request.limit}'

    # Execute query
    try:
        password = None
        if conn.encrypted_password:
            password = encryption_service.decrypt(conn.encrypted_password)

        if conn.type == ConnectionType.mysql:
            exec_result = await MySQLService.execute_query(
                host=conn.host or "localhost",
                port=conn.port or 3306,
                database=conn.database_name or "",
                sql=sql,
                username=conn.username,
                password=password,
                limit=request.limit
            )
        else:
            # PostgreSQL
            conn_str = postgres_service.build_connection_string(
                host=conn.host or "localhost",
                port=conn.port or 5432,
                database=conn.database_name or "",
                username=conn.username,
                password=password,
                extra=conn.additional_config
            )
            exec_result = await postgres_service.execute_query(conn_str, sql, request.limit)

        execution_time = (time.time() - start_time) * 1000

        return ModelPreviewResponse(
            columns=exec_result.get("columns", []),
            rows=exec_result.get("rows", []),
            total_rows=exec_result.get("total", len(exec_result.get("rows", []))),
            sql_generated=sql,
            execution_time_ms=round(execution_time, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
