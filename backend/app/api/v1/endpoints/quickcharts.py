"""
Quick Charts API endpoints.

Provides intelligent auto-chart generation based on data analysis.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid as uuid_module
import logging

from app.schemas.quickchart import (
    QuickChartResponse,
    TableSummary,
    ChartRecommendation,
    HomeQuickSuggestion,
    QuickChartCreateRequest,
    TableProfile,
    ColumnProfile,
    ColumnDataType,
    Cardinality,
)
from app.schemas.dashboard import SavedChartCreate
from app.models.connection import Connection as ConnectionModel, ConnectionType, ConnectionStatus
from app.models.dashboard import SavedChart, Dashboard
from app.services.data_profiler_service import data_profiler
from app.services.chart_recommendation_service import chart_recommender
from app.services.postgres_service import postgres_service
from app.services.mysql_service import mysql_service
from app.services.mongodb_service import mongodb_service
from app.services.encryption_service import encryption_service
from app.database import get_db
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


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


async def _profile_mysql_table(
    host: str,
    port: int,
    database: str,
    username: Optional[str],
    password: Optional[str],
    table: str,
    connection_id: str
) -> TableProfile:
    """Profile a MySQL table for chart recommendations."""
    import aiomysql

    # Type mappings for MySQL (comprehensive list)
    NUMERIC_TYPES = {
        'int', 'integer', 'bigint', 'smallint', 'tinyint', 'mediumint',
        'decimal', 'numeric', 'float', 'double', 'real', 'dec', 'fixed',
        'bit', 'serial'
    }
    TEMPORAL_TYPES = {'date', 'datetime', 'timestamp', 'time', 'year'}

    conn = None
    try:
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=username or '',
            password=password or '',
            db=database,
            connect_timeout=10
        )

        async with conn.cursor() as cursor:
            # Get row count
            await cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            row_count = (await cursor.fetchone())[0]

            # Get column info
            await cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (database, table))
            columns_meta = await cursor.fetchall()

            column_profiles = []
            suggested_dimensions = []
            suggested_measures = []

            for col_name, data_type, is_nullable in columns_meta:
                data_type_lower = data_type.lower()

                # Determine data type category
                if data_type_lower in NUMERIC_TYPES:
                    col_type = ColumnDataType.NUMERIC
                    suggested_measures.append(col_name)
                elif data_type_lower in TEMPORAL_TYPES:
                    col_type = ColumnDataType.TEMPORAL
                    suggested_dimensions.append(col_name)
                elif data_type_lower in ('bool', 'boolean', 'bit'):
                    col_type = ColumnDataType.BOOLEAN
                else:
                    col_type = ColumnDataType.CATEGORICAL
                    suggested_dimensions.append(col_name)

                # Get distinct count for cardinality
                try:
                    await cursor.execute(f"SELECT COUNT(DISTINCT `{col_name}`) FROM `{table}` LIMIT 10001")
                    distinct_count = (await cursor.fetchone())[0] or 0
                except:
                    distinct_count = 100  # Default to medium cardinality

                # Determine cardinality (LOW < 10, MEDIUM 10-100, HIGH > 100)
                if distinct_count <= 10:
                    cardinality = Cardinality.LOW
                elif distinct_count <= 100:
                    cardinality = Cardinality.MEDIUM
                else:
                    cardinality = Cardinality.HIGH

                column_profiles.append(ColumnProfile(
                    name=col_name,
                    data_type=col_type,
                    sql_type=data_type,
                    row_count=row_count,
                    null_count=0,
                    null_percent=0.0,
                    distinct_count=distinct_count,
                    cardinality=cardinality,
                    min_value=None,
                    max_value=None,
                    mean=None,
                    top_values=[]
                ))

            return TableProfile(
                connection_id=connection_id,
                schema_name=database,
                table_name=table,
                row_count=row_count,
                columns=column_profiles,
                has_temporal=any(c.data_type == ColumnDataType.TEMPORAL for c in column_profiles),
                has_numeric=any(c.data_type == ColumnDataType.NUMERIC for c in column_profiles),
                has_categorical=any(c.data_type == ColumnDataType.CATEGORICAL for c in column_profiles),
                suggested_dimensions=suggested_dimensions[:5],
                suggested_measures=suggested_measures[:5]
            )

    except Exception as e:
        logger.error(f"Failed to profile MySQL table {table}: {e}")
        raise
    finally:
        if conn:
            conn.close()


async def _profile_mongodb_collection(
    host: str,
    port: int,
    database: str,
    collection: str,
    username: Optional[str],
    password: Optional[str],
    auth_source: Optional[str],
    is_srv: bool,
    ssl: bool,
    connection_id: str
) -> TableProfile:
    """Profile a MongoDB collection for chart recommendations."""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
    except ImportError:
        raise HTTPException(status_code=500, detail="MongoDB driver not installed")

    # Type mappings for MongoDB (Python type names from type().__name__)
    NUMERIC_TYPES = {'int', 'float', 'int32', 'int64', 'decimal', 'decimal128', 'long', 'double'}
    TEMPORAL_TYPES = {'datetime', 'date'}

    conn_str = mongodb_service.build_connection_string(
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
        auth_source=auth_source,
        is_srv=is_srv
    )

    client = None
    try:
        use_tls = ssl or is_srv
        client = AsyncIOMotorClient(
            conn_str,
            serverSelectionTimeoutMS=10000,
            tls=use_tls,
        )

        db = client[database] if database else client.get_default_database()
        coll = db[collection]

        # Get document count
        row_count = await coll.count_documents({})

        # Sample documents to infer schema
        cursor = coll.find().limit(100)
        documents = await cursor.to_list(length=100)

        if not documents:
            return TableProfile(
                connection_id=connection_id,
                schema_name=database,
                table_name=collection,
                row_count=0,
                columns=[],
                has_temporal=False,
                has_numeric=False,
                has_categorical=False,
                suggested_dimensions=[],
                suggested_measures=[]
            )

        # Analyze field types
        field_types = {}
        for doc in documents:
            for key, value in doc.items():
                if key == '_id':
                    continue
                if key not in field_types:
                    field_types[key] = set()
                field_types[key].add(type(value).__name__.lower())

        column_profiles = []
        suggested_dimensions = []
        suggested_measures = []

        for field, types in field_types.items():
            # Determine data type category based on Python type names
            is_numeric = any(t in NUMERIC_TYPES for t in types)
            is_temporal = any(t in TEMPORAL_TYPES for t in types)
            is_bool = 'bool' in types

            if is_numeric:
                col_type = ColumnDataType.NUMERIC
                suggested_measures.append(field)
            elif is_temporal:
                col_type = ColumnDataType.TEMPORAL
                suggested_dimensions.append(field)
            elif is_bool:
                col_type = ColumnDataType.BOOLEAN
            else:
                col_type = ColumnDataType.CATEGORICAL
                suggested_dimensions.append(field)

            # Get distinct count for cardinality
            try:
                distinct_values = await coll.distinct(field)
                distinct_count = len(distinct_values) if distinct_values else 0
            except:
                distinct_count = 100  # Default to medium cardinality

            # Determine cardinality (LOW < 10, MEDIUM 10-100, HIGH > 100)
            if distinct_count <= 10:
                cardinality = Cardinality.LOW
            elif distinct_count <= 100:
                cardinality = Cardinality.MEDIUM
            else:
                cardinality = Cardinality.HIGH

            column_profiles.append(ColumnProfile(
                name=field,
                data_type=col_type,
                sql_type=' | '.join(types),
                row_count=row_count,
                null_count=0,
                null_percent=0.0,
                distinct_count=distinct_count,
                cardinality=cardinality,
                min_value=None,
                max_value=None,
                mean=None,
                top_values=[]
            ))

        return TableProfile(
            connection_id=connection_id,
            schema_name=database,
            table_name=collection,
            row_count=row_count,
            columns=column_profiles,
            has_temporal=any(c.data_type == ColumnDataType.TEMPORAL for c in column_profiles),
            has_numeric=any(c.data_type == ColumnDataType.NUMERIC for c in column_profiles),
            has_categorical=any(c.data_type == ColumnDataType.CATEGORICAL for c in column_profiles),
            suggested_dimensions=suggested_dimensions[:5],
            suggested_measures=suggested_measures[:5]
        )

    except Exception as e:
        logger.error(f"Failed to profile MongoDB collection {collection}: {e}")
        raise
    finally:
        if client:
            client.close()


@router.get("/tables/{connection_id}", response_model=List[TableSummary])
async def list_tables_for_quickcharts(
    connection_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    List tables with metadata for quick chart selection.
    Returns table summaries with row counts and data type indicators.
    """
    try:
        conn_uuid = uuid_module.UUID(connection_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid connection ID format")

    # Get connection
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == conn_uuid)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Handle CSV/Excel connections (single table)
    if conn.type in (ConnectionType.csv, ConnectionType.excel):
        table_name = conn.additional_config.get('table_name') if conn.additional_config else None
        if table_name:
            return [TableSummary(
                schema_name="public",
                table_name=table_name,
                row_count=None,  # Could query if needed
                column_count=0,
                has_numeric=True,
                has_temporal=False
            )]
        return []

    # Handle MySQL connections
    if conn.type == ConnectionType.mysql:
        try:
            password = None
            if conn.encrypted_password:
                password = encryption_service.decrypt(conn.encrypted_password)

            tables = await mysql_service.get_tables(
                host=conn.host or "localhost",
                port=conn.port or 3306,
                database=conn.database_name or "",
                username=conn.username,
                password=password,
                ssl=conn.additional_config.get("ssl") if conn.additional_config else None
            )
            return [
                TableSummary(
                    schema_name=t.get("schema", conn.database_name or ""),
                    table_name=t["name"],
                    row_count=None,
                    column_count=0,
                    has_numeric=True,
                    has_temporal=False
                )
                for t in tables
            ]
        except Exception as e:
            logger.error(f"Failed to get MySQL tables for connection {connection_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")

    # Handle MongoDB connections
    if conn.type == ConnectionType.mongodb:
        try:
            password = None
            if conn.encrypted_password:
                password = encryption_service.decrypt(conn.encrypted_password)

            additional = conn.additional_config or {}
            collections = await mongodb_service.get_tables(
                host=conn.host or "localhost",
                port=conn.port or 27017,
                database=conn.database_name or "",
                username=conn.username,
                password=password,
                auth_source=additional.get("auth_source"),
                is_srv=additional.get("is_srv", False),
                ssl=additional.get("ssl", False)
            )
            return [
                TableSummary(
                    schema_name=c.get("schema", conn.database_name or ""),
                    table_name=c["name"],
                    row_count=None,
                    column_count=0,
                    has_numeric=True,
                    has_temporal=False
                )
                for c in collections
            ]
        except Exception as e:
            logger.error(f"Failed to get MongoDB collections for connection {connection_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get collections: {str(e)}")

    # Only PostgreSQL supported for table profiling
    if conn.type not in (ConnectionType.postgresql,):
        raise HTTPException(
            status_code=400,
            detail=f"Quick charts not yet supported for {conn.type.value} connections"
        )

    try:
        conn_str = await _get_connection_string(conn)
        summaries = await data_profiler.get_tables_summary(conn_str)
        return summaries
    except Exception as e:
        logger.error(f"Failed to get tables for connection {connection_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")


@router.get("/suggestions/{connection_id}/{schema}/{table}", response_model=QuickChartResponse)
async def get_quick_chart_suggestions(
    connection_id: str,
    schema: str,
    table: str,
    max_suggestions: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a table and return intelligent chart suggestions.

    This endpoint:
    1. Profiles the table (column types, cardinality, statistics)
    2. Applies recommendation rules to suggest optimal chart types
    3. Returns pre-built chart configurations ready to use
    """
    try:
        conn_uuid = uuid_module.UUID(connection_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid connection ID format")

    # Get connection
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == conn_uuid)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Handle CSV/Excel - use app database
    if conn.type in (ConnectionType.csv, ConnectionType.excel):
        conn_str = settings.DATABASE_URL
        # For CSV/Excel, the table is stored in app's database
        actual_table = conn.additional_config.get('table_name') if conn.additional_config else table
        actual_schema = "public"
    elif conn.type == ConnectionType.postgresql:
        conn_str = await _get_connection_string(conn)
        actual_table = table
        actual_schema = schema
    elif conn.type == ConnectionType.mysql:
        # For MySQL, use a simpler profiling approach
        try:
            password = None
            if conn.encrypted_password:
                password = encryption_service.decrypt(conn.encrypted_password)

            profile = await _profile_mysql_table(
                host=conn.host or "localhost",
                port=conn.port or 3306,
                database=conn.database_name or "",
                username=conn.username,
                password=password,
                table=table,
                connection_id=connection_id
            )

            recommendations = chart_recommender.recommend(
                profile, max_recommendations=max_suggestions
            )

            return QuickChartResponse(
                connection_id=connection_id,
                schema_name=conn.database_name or schema,
                table_name=table,
                profile=profile,
                recommendations=recommendations
            )
        except Exception as e:
            logger.error(f"Failed to generate MySQL suggestions for {schema}.{table}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to analyze MySQL table: {str(e)}")
    elif conn.type == ConnectionType.mongodb:
        # For MongoDB, use collection profiling
        try:
            password = None
            if conn.encrypted_password:
                password = encryption_service.decrypt(conn.encrypted_password)

            additional = conn.additional_config or {}
            profile = await _profile_mongodb_collection(
                host=conn.host or "localhost",
                port=conn.port or 27017,
                database=conn.database_name or "",
                collection=table,
                username=conn.username,
                password=password,
                auth_source=additional.get("auth_source"),
                is_srv=additional.get("is_srv", False),
                ssl=additional.get("ssl", False),
                connection_id=connection_id
            )

            recommendations = chart_recommender.recommend(
                profile, max_recommendations=max_suggestions
            )

            return QuickChartResponse(
                connection_id=connection_id,
                schema_name=conn.database_name or schema,
                table_name=table,
                profile=profile,
                recommendations=recommendations
            )
        except Exception as e:
            logger.error(f"Failed to generate MongoDB suggestions for {table}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to analyze MongoDB collection: {str(e)}")
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Quick charts not yet supported for {conn.type.value} connections"
        )

    try:
        # Profile the table (PostgreSQL path)
        profile = await data_profiler.profile_table(
            conn_str, actual_schema, actual_table
        )
        profile.connection_id = connection_id

        # Generate recommendations
        recommendations = chart_recommender.recommend(
            profile, max_recommendations=max_suggestions
        )

        return QuickChartResponse(
            connection_id=connection_id,
            schema_name=actual_schema,
            table_name=actual_table,
            profile=profile,
            recommendations=recommendations
        )

    except Exception as e:
        logger.error(f"Failed to generate suggestions for {schema}.{table}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze table: {str(e)}")


@router.post("/create-chart")
async def create_chart_from_suggestion(
    request: QuickChartCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a saved chart from a quick chart suggestion.
    Optionally adds the chart to a dashboard.
    """
    try:
        conn_uuid = uuid_module.UUID(request.connection_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid connection ID format")

    # Verify connection exists
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == conn_uuid)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Verify dashboard if provided
    dashboard_uuid = None
    dashboard = None
    if request.dashboard_id:
        try:
            dashboard_uuid = uuid_module.UUID(request.dashboard_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid dashboard ID format")

        dash_result = await db.execute(
            select(Dashboard).where(Dashboard.id == dashboard_uuid)
        )
        dashboard = dash_result.scalar_one_or_none()
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

    # Create the chart
    chart = SavedChart(
        name=request.title or "Quick Chart",
        description="Auto-generated from Quick Charts",
        dashboard_id=dashboard_uuid,
        connection_id=str(conn_uuid),
        chart_type=request.chart_type,
        chart_config=request.chart_config,
        query_config=request.query_config,
        position_x=0,
        position_y=0,
        width=6,
        height=4
    )

    db.add(chart)
    await db.commit()
    await db.refresh(chart)

    # If adding to dashboard, update the dashboard layout to include widget
    if dashboard:
        # Get current layout or initialize empty
        current_layout = dashboard.layout or {"widgets": []}
        widgets = current_layout.get("widgets", [])

        # Create widget entry for the chart
        new_widget = {
            "id": f"widget-{str(chart.id)[:8]}-{int(__import__('time').time() * 1000)}",
            "type": "chart",
            "title": chart.name,
            "config": {},
            "chartId": str(chart.id),
            "chartData": {
                "id": str(chart.id),
                "name": chart.name,
                "description": chart.description,
                "chart_type": chart.chart_type,
                "chart_config": chart.chart_config,
                "is_favorite": False
            },
            "w": 4,
            "h": 3
        }
        widgets.append(new_widget)

        # Update dashboard layout
        dashboard.layout = {"widgets": widgets}
        await db.commit()

    return {
        "id": str(chart.id),
        "name": chart.name,
        "chart_type": chart.chart_type,
        "dashboard_id": str(chart.dashboard_id) if chart.dashboard_id else None,
        "message": "Chart created successfully"
    }


@router.get("/home-suggestions", response_model=List[HomeQuickSuggestion])
async def get_home_quick_suggestions(
    limit: int = 3,
    db: AsyncSession = Depends(get_db)
):
    """
    Get quick chart suggestions for the home page.
    Analyzes recent/popular connections and returns top suggestions.
    """
    suggestions = []

    try:
        # Get recent PostgreSQL connections
        result = await db.execute(
            select(ConnectionModel)
            .where(ConnectionModel.type == ConnectionType.postgresql)
            .where(ConnectionModel.status == ConnectionStatus.connected)
            .order_by(ConnectionModel.last_sync.desc())
            .limit(3)
        )
        connections = result.scalars().all()

        for conn in connections:
            try:
                conn_str = await _get_connection_string(conn)

                # Get table summaries
                tables = await data_profiler.get_tables_summary(conn_str)

                # Pick most promising table (has both numeric and temporal, or most columns)
                best_table = None
                for t in tables:
                    if t.has_numeric and t.has_temporal:
                        best_table = t
                        break
                    elif t.has_numeric and not best_table:
                        best_table = t

                if not best_table and tables:
                    best_table = tables[0]

                if best_table:
                    # Profile and get recommendations
                    profile = await data_profiler.profile_table(
                        conn_str, best_table.schema_name, best_table.table_name
                    )
                    profile.connection_id = str(conn.id)

                    recommendations = chart_recommender.recommend(profile, max_recommendations=1)

                    if recommendations:
                        rec = recommendations[0]
                        suggestions.append(HomeQuickSuggestion(
                            id=rec.id,
                            title=rec.title,
                            chart_type=rec.chart_type,
                            confidence=rec.confidence,
                            table_name=best_table.table_name,
                            connection_id=str(conn.id),
                            connection_name=conn.name,
                            chart_config=rec.chart_config,
                            query_config=rec.query_config
                        ))

                        if len(suggestions) >= limit:
                            break

            except Exception as e:
                logger.warning(f"Failed to get suggestions for connection {conn.id}: {e}")
                continue

    except Exception as e:
        logger.error(f"Failed to get home suggestions: {e}")

    return suggestions[:limit]


@router.get("/connection/{connection_id}/analyze")
async def analyze_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze all tables in a connection and return a summary
    of available quick charts.
    """
    try:
        conn_uuid = uuid_module.UUID(connection_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid connection ID format")

    # Get connection
    result = await db.execute(
        select(ConnectionModel).where(ConnectionModel.id == conn_uuid)
    )
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    if conn.type not in (ConnectionType.postgresql, ConnectionType.csv, ConnectionType.excel):
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not yet supported for {conn.type.value} connections"
        )

    # For CSV/Excel use app database
    if conn.type in (ConnectionType.csv, ConnectionType.excel):
        conn_str = settings.DATABASE_URL
        table_name = conn.additional_config.get('table_name') if conn.additional_config else None
        if not table_name:
            return {"tables": [], "total_suggestions": 0}

        try:
            profile = await data_profiler.profile_table(conn_str, "public", table_name)
            profile.connection_id = connection_id
            recommendations = chart_recommender.recommend(profile, max_recommendations=5)

            return {
                "tables": [{
                    "schema": "public",
                    "table": table_name,
                    "row_count": profile.row_count,
                    "suggestion_count": len(recommendations),
                    "top_suggestion": recommendations[0].chart_type if recommendations else None
                }],
                "total_suggestions": len(recommendations)
            }
        except Exception as e:
            logger.error(f"Failed to analyze table {table_name}: {e}")
            return {"tables": [], "total_suggestions": 0, "error": str(e)}

    # PostgreSQL - analyze multiple tables
    try:
        conn_str = await _get_connection_string(conn)
        tables = await data_profiler.get_tables_summary(conn_str)

        analysis = []
        total_suggestions = 0

        for t in tables[:10]:  # Limit to 10 tables for performance
            try:
                profile = await data_profiler.profile_table(
                    conn_str, t.schema_name, t.table_name
                )
                recommendations = chart_recommender.recommend(profile, max_recommendations=3)

                analysis.append({
                    "schema": t.schema_name,
                    "table": t.table_name,
                    "row_count": t.row_count,
                    "suggestion_count": len(recommendations),
                    "top_suggestion": recommendations[0].chart_type if recommendations else None
                })
                total_suggestions += len(recommendations)

            except Exception as e:
                logger.warning(f"Failed to analyze {t.schema_name}.{t.table_name}: {e}")

        return {
            "tables": analysis,
            "total_suggestions": total_suggestions
        }

    except Exception as e:
        logger.error(f"Failed to analyze connection {connection_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
