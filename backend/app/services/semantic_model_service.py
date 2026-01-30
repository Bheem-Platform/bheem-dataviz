"""
Semantic Model Service - Handles semantic model operations and query generation.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid
import logging

from motor.motor_asyncio import AsyncIOMotorClient
from ..schemas.semantic_model import (
    SemanticModelCreate, SemanticModelUpdate, SemanticModelResponse,
    SemanticModelSummary, ModelTable, ModelTableCreate,
    Relationship, RelationshipCreate,
    Measure, MeasureCreate,
    Dimension, DimensionCreate,
    ColumnAlias, ModelField, ModelFieldsResponse,
    RelationshipType, JoinType
)

logger = logging.getLogger(__name__)


class SemanticModelService:
    """Service for managing semantic models."""

    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.collection = db.dataviz.semantic_models

    async def create_model(self, model: SemanticModelCreate) -> SemanticModelResponse:
        """Create a new semantic model."""
        now = datetime.utcnow()
        model_doc = {
            "id": str(uuid.uuid4()),
            "name": model.name,
            "description": model.description,
            "connection_id": model.connection_id,
            "tables": [t.model_dump() for t in model.tables],
            "relationships": [],
            "measures": [],
            "dimensions": [],
            "column_aliases": [],
            "created_at": now,
            "updated_at": now
        }

        await self.collection.insert_one(model_doc)
        return SemanticModelResponse(**model_doc)

    async def get_model(self, model_id: str) -> Optional[SemanticModelResponse]:
        """Get a semantic model by ID."""
        doc = await self.collection.find_one({"id": model_id})
        if doc:
            return SemanticModelResponse(**doc)
        return None

    async def list_models(self, connection_id: Optional[str] = None) -> List[SemanticModelSummary]:
        """List all semantic models, optionally filtered by connection."""
        query = {}
        if connection_id:
            query["connection_id"] = connection_id

        models = []
        async for doc in self.collection.find(query).sort("updated_at", -1):
            models.append(SemanticModelSummary(
                id=doc["id"],
                name=doc["name"],
                description=doc.get("description"),
                connection_id=doc["connection_id"],
                tables_count=len(doc.get("tables", [])),
                relationships_count=len(doc.get("relationships", [])),
                measures_count=len(doc.get("measures", [])),
                created_at=doc.get("created_at"),
                updated_at=doc.get("updated_at")
            ))
        return models

    async def update_model(self, model_id: str, update: SemanticModelUpdate) -> Optional[SemanticModelResponse]:
        """Update a semantic model's basic info."""
        update_doc = {"updated_at": datetime.utcnow()}
        if update.name is not None:
            update_doc["name"] = update.name
        if update.description is not None:
            update_doc["description"] = update.description

        result = await self.collection.update_one(
            {"id": model_id},
            {"$set": update_doc}
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    async def delete_model(self, model_id: str) -> bool:
        """Delete a semantic model."""
        result = await self.collection.delete_one({"id": model_id})
        return result.deleted_count > 0

    # ========================================================================
    # TABLE OPERATIONS
    # ========================================================================

    async def add_table(self, model_id: str, table: ModelTableCreate) -> Optional[SemanticModelResponse]:
        """Add a table to a semantic model."""
        table_doc = table.model_dump()

        result = await self.collection.update_one(
            {"id": model_id},
            {
                "$push": {"tables": table_doc},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    async def update_table(self, model_id: str, table_name: str, updates: Dict[str, Any]) -> Optional[SemanticModelResponse]:
        """Update a table in a semantic model (e.g., position, alias)."""
        # Build the update query for array element
        set_fields = {f"tables.$.{k}": v for k, v in updates.items()}
        set_fields["updated_at"] = datetime.utcnow()

        result = await self.collection.update_one(
            {"id": model_id, "tables.name": table_name},
            {"$set": set_fields}
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    async def remove_table(self, model_id: str, table_name: str) -> Optional[SemanticModelResponse]:
        """Remove a table from a semantic model (also removes related relationships)."""
        result = await self.collection.update_one(
            {"id": model_id},
            {
                "$pull": {
                    "tables": {"name": table_name},
                    "relationships": {
                        "$or": [
                            {"from_table": table_name},
                            {"to_table": table_name}
                        ]
                    }
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    # ========================================================================
    # RELATIONSHIP OPERATIONS
    # ========================================================================

    async def add_relationship(self, model_id: str, rel: RelationshipCreate) -> Optional[SemanticModelResponse]:
        """Add a relationship between tables."""
        rel_doc = {
            "id": str(uuid.uuid4()),
            "name": rel.name or f"{rel.from_table}.{rel.from_column} -> {rel.to_table}.{rel.to_column}",
            "from_table": rel.from_table,
            "from_column": rel.from_column,
            "to_table": rel.to_table,
            "to_column": rel.to_column,
            "relationship_type": rel.relationship_type.value,
            "join_type": rel.join_type.value
        }

        result = await self.collection.update_one(
            {"id": model_id},
            {
                "$push": {"relationships": rel_doc},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    async def update_relationship(self, model_id: str, rel_id: str, updates: Dict[str, Any]) -> Optional[SemanticModelResponse]:
        """Update a relationship."""
        set_fields = {f"relationships.$.{k}": v for k, v in updates.items()}
        set_fields["updated_at"] = datetime.utcnow()

        result = await self.collection.update_one(
            {"id": model_id, "relationships.id": rel_id},
            {"$set": set_fields}
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    async def remove_relationship(self, model_id: str, rel_id: str) -> Optional[SemanticModelResponse]:
        """Remove a relationship."""
        result = await self.collection.update_one(
            {"id": model_id},
            {
                "$pull": {"relationships": {"id": rel_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    # ========================================================================
    # MEASURE OPERATIONS
    # ========================================================================

    async def add_measure(self, model_id: str, measure: MeasureCreate) -> Optional[SemanticModelResponse]:
        """Add a measure to a semantic model."""
        measure_doc = {
            "id": str(uuid.uuid4()),
            **measure.model_dump()
        }

        result = await self.collection.update_one(
            {"id": model_id},
            {
                "$push": {"measures": measure_doc},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    async def remove_measure(self, model_id: str, measure_id: str) -> Optional[SemanticModelResponse]:
        """Remove a measure."""
        result = await self.collection.update_one(
            {"id": model_id},
            {
                "$pull": {"measures": {"id": measure_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    # ========================================================================
    # DIMENSION OPERATIONS
    # ========================================================================

    async def add_dimension(self, model_id: str, dimension: DimensionCreate) -> Optional[SemanticModelResponse]:
        """Add a dimension to a semantic model."""
        dim_doc = {
            "id": str(uuid.uuid4()),
            **dimension.model_dump()
        }

        result = await self.collection.update_one(
            {"id": model_id},
            {
                "$push": {"dimensions": dim_doc},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    async def remove_dimension(self, model_id: str, dimension_id: str) -> Optional[SemanticModelResponse]:
        """Remove a dimension."""
        result = await self.collection.update_one(
            {"id": model_id},
            {
                "$pull": {"dimensions": {"id": dimension_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            return await self.get_model(model_id)
        return None

    # ========================================================================
    # QUERY GENERATION
    # ========================================================================

    def generate_join_sql(
        self,
        model: SemanticModelResponse,
        tables_needed: List[str],
        dialect: str = "postgresql"
    ) -> Tuple[str, str]:
        """
        Generate JOIN SQL for the tables needed in a query.

        Returns:
            Tuple of (from_clause, list of joined tables)
        """
        if not tables_needed:
            return "", ""

        quote = '"' if dialect == "postgresql" else '`'

        # Find the primary table (first one or one with most relationships)
        primary_table = tables_needed[0]

        # Get table info
        table_map = {t.name: t for t in model.tables}

        # Build FROM clause with primary table
        primary = table_map.get(primary_table)
        primary_schema = primary.schema_name if primary else "public"
        from_clause = f'{quote}{primary_schema}{quote}.{quote}{primary_table}{quote} AS {quote}{primary_table}{quote}'

        # Track joined tables
        joined = {primary_table}
        join_clauses = []

        # Add JOINs for other tables based on relationships
        for table_name in tables_needed:
            if table_name in joined:
                continue

            # Find relationship connecting this table
            for rel in model.relationships:
                join_type = rel.join_type.upper() if hasattr(rel.join_type, 'upper') else rel.join_type.value.upper()

                if rel.from_table == table_name and rel.to_table in joined:
                    # Join from new table to already joined table
                    table_info = table_map.get(table_name)
                    schema = table_info.schema_name if table_info else "public"
                    join_clauses.append(
                        f'{join_type} JOIN {quote}{schema}{quote}.{quote}{table_name}{quote} AS {quote}{table_name}{quote} '
                        f'ON {quote}{table_name}{quote}.{quote}{rel.from_column}{quote} = '
                        f'{quote}{rel.to_table}{quote}.{quote}{rel.to_column}{quote}'
                    )
                    joined.add(table_name)
                    break

                elif rel.to_table == table_name and rel.from_table in joined:
                    # Join from already joined table to new table
                    table_info = table_map.get(table_name)
                    schema = table_info.schema_name if table_info else "public"
                    join_clauses.append(
                        f'{join_type} JOIN {quote}{schema}{quote}.{quote}{table_name}{quote} AS {quote}{table_name}{quote} '
                        f'ON {quote}{rel.from_table}{quote}.{quote}{rel.from_column}{quote} = '
                        f'{quote}{table_name}{quote}.{quote}{rel.to_column}{quote}'
                    )
                    joined.add(table_name)
                    break

        full_from = from_clause
        if join_clauses:
            full_from += '\n' + '\n'.join(join_clauses)

        return full_from, list(joined)

    def generate_model_query(
        self,
        model: SemanticModelResponse,
        select_fields: List[Dict[str, str]],
        group_by_fields: List[Dict[str, str]] = None,
        measures: List[str] = None,
        filters: List[Dict[str, Any]] = None,
        order_by: List[Dict[str, str]] = None,
        limit: int = 100,
        offset: int = 0,
        dialect: str = "postgresql"
    ) -> str:
        """
        Generate a SQL query based on the semantic model.

        Args:
            model: The semantic model
            select_fields: List of {"table": "x", "column": "y"} to select
            group_by_fields: Fields to group by
            measures: List of measure IDs to include
            filters: Filter conditions
            order_by: Order by specifications
            limit: Row limit
            offset: Row offset
            dialect: SQL dialect

        Returns:
            Generated SQL query
        """
        quote = '"' if dialect == "postgresql" else '`'

        # Collect all tables needed
        tables_needed = set()
        for field in select_fields:
            tables_needed.add(field["table"])

        if group_by_fields:
            for field in group_by_fields:
                tables_needed.add(field["table"])

        # Add tables from measures
        measure_map = {m.id: m for m in model.measures}
        if measures:
            for m_id in measures:
                if m_id in measure_map:
                    tables_needed.add(measure_map[m_id].table)

        tables_needed = list(tables_needed)

        # Generate FROM clause with JOINs
        from_clause, _ = self.generate_join_sql(model, tables_needed, dialect)

        # Build SELECT clause
        select_parts = []

        # Add regular fields
        for field in select_fields:
            col_ref = f'{quote}{field["table"]}{quote}.{quote}{field["column"]}{quote}'
            select_parts.append(col_ref)

        # Add measures
        if measures:
            for m_id in measures:
                if m_id in measure_map:
                    m = measure_map[m_id]
                    col_ref = f'{quote}{m.table}{quote}.{quote}{m.column}{quote}'
                    agg = m.aggregate.value.upper()
                    if agg == "COUNT_DISTINCT":
                        select_parts.append(f'COUNT(DISTINCT {col_ref}) AS {quote}{m.name}{quote}')
                    else:
                        select_parts.append(f'{agg}({col_ref}) AS {quote}{m.name}{quote}')

        # Build query
        sql_parts = [f"SELECT {', '.join(select_parts)}"]
        sql_parts.append(f"FROM {from_clause}")

        # Add WHERE clause
        if filters:
            where_parts = []
            for f in filters:
                col_ref = f'{quote}{f["table"]}{quote}.{quote}{f["column"]}{quote}'
                op = f.get("operator", "=")
                val = f.get("value")

                if op == "is_null":
                    where_parts.append(f'{col_ref} IS NULL')
                elif op == "is_not_null":
                    where_parts.append(f'{col_ref} IS NOT NULL')
                elif isinstance(val, str):
                    where_parts.append(f"{col_ref} {op} '{val}'")
                else:
                    where_parts.append(f"{col_ref} {op} {val}")

            if where_parts:
                sql_parts.append(f"WHERE {' AND '.join(where_parts)}")

        # Add GROUP BY
        if group_by_fields:
            group_parts = [f'{quote}{f["table"]}{quote}.{quote}{f["column"]}{quote}' for f in group_by_fields]
            sql_parts.append(f"GROUP BY {', '.join(group_parts)}")

        # Add ORDER BY
        if order_by:
            order_parts = []
            for o in order_by:
                col_ref = f'{quote}{o["table"]}{quote}.{quote}{o["column"]}{quote}'
                direction = o.get("direction", "ASC").upper()
                order_parts.append(f'{col_ref} {direction}')
            sql_parts.append(f"ORDER BY {', '.join(order_parts)}")

        # Add LIMIT/OFFSET
        if dialect == "mysql":
            sql_parts.append(f"LIMIT {offset}, {limit}" if offset else f"LIMIT {limit}")
        else:
            sql_parts.append(f"LIMIT {limit}")
            if offset:
                sql_parts.append(f"OFFSET {offset}")

        return '\n'.join(sql_parts)
