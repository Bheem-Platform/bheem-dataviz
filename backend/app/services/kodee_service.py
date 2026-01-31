"""
Kodee Service - NL-to-SQL Engine

Provides natural language to SQL conversion using OpenAI,
with schema context building, query validation, and conversation management.
"""

import logging
import re
import json
import uuid
from typing import Any, Optional
from datetime import datetime
import time

from openai import AsyncOpenAI
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings
from app.schemas.kodee import (
    QueryIntent,
    QueryComplexity,
    MessageRole,
    ValidationStatus,
    ColumnInfo,
    TableInfo,
    RelationshipInfo,
    MeasureInfo,
    DimensionInfo,
    SchemaContext,
    NLQueryRequest,
    NLQueryResponse,
    QueryValidation,
    ChatMessage,
    ChatSession,
    ChatRequest,
    ChatResponse,
    QueryHistoryItem,
    BLOCKED_KEYWORDS,
    AGGREGATION_KEYWORDS,
    COMPARISON_KEYWORDS,
    TIME_KEYWORDS,
    SYSTEM_PROMPT_TEMPLATE,
    FEW_SHOT_EXAMPLES,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class KodeeService:
    """Service for NL-to-SQL conversion and chat interactions"""

    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.sessions_collection = db.dataviz.kodee_sessions
        self.history_collection = db.dataviz.kodee_history
        self.client: Optional[AsyncOpenAI] = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client"""
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            logger.warning("OpenAI API key not configured - Kodee will use fallback mode")

    # ========================================================================
    # SCHEMA CONTEXT BUILDING
    # ========================================================================

    async def build_schema_context(
        self,
        connection_id: str,
        model_id: Optional[str] = None,
        include_samples: bool = True,
        max_sample_values: int = 5,
    ) -> SchemaContext:
        """
        Build schema context for NL-to-SQL generation.

        Extracts table/column metadata, relationships, and semantic model info.
        """
        tables = []
        relationships = []
        measures = []
        dimensions = []
        dialect = "postgresql"
        model_name = None

        # Get connection info
        connection = await self.db.dataviz.connections.find_one({"id": connection_id})
        if connection:
            dialect = connection.get("type", "postgresql")

        # If we have a semantic model, use it
        if model_id:
            model = await self.db.dataviz.semantic_models.find_one({"id": model_id})
            if model:
                model_name = model.get("name")

                # Extract tables from model
                for t in model.get("tables", []):
                    columns = []
                    for col in t.get("columns", []):
                        columns.append(ColumnInfo(
                            name=col.get("name"),
                            data_type=col.get("data_type", "varchar"),
                            nullable=col.get("nullable", True),
                            description=col.get("description"),
                            is_primary_key=col.get("is_primary_key", False),
                            is_foreign_key=col.get("is_foreign_key", False),
                            foreign_key_ref=col.get("foreign_key_ref"),
                        ))

                    tables.append(TableInfo(
                        name=t.get("name"),
                        schema_name=t.get("schema_name", "public"),
                        description=t.get("description"),
                        columns=columns,
                        aliases=t.get("aliases", []),
                    ))

                # Extract relationships
                for rel in model.get("relationships", []):
                    relationships.append(RelationshipInfo(
                        from_table=rel.get("from_table"),
                        from_column=rel.get("from_column"),
                        to_table=rel.get("to_table"),
                        to_column=rel.get("to_column"),
                        relationship_type=rel.get("relationship_type", "one_to_many"),
                    ))

                # Extract measures
                for m in model.get("measures", []):
                    measures.append(MeasureInfo(
                        id=m.get("id"),
                        name=m.get("name"),
                        description=m.get("description"),
                        expression=f"{m.get('aggregate', 'SUM').upper()}({m.get('table')}.{m.get('column')})",
                        table=m.get("table"),
                        column=m.get("column"),
                        aggregate=m.get("aggregate", "sum"),
                    ))

                # Extract dimensions
                for d in model.get("dimensions", []):
                    dimensions.append(DimensionInfo(
                        id=d.get("id"),
                        name=d.get("name"),
                        description=d.get("description"),
                        table=d.get("table"),
                        column=d.get("column"),
                        hierarchy=d.get("hierarchy"),
                    ))

        return SchemaContext(
            connection_id=connection_id,
            model_id=model_id,
            model_name=model_name,
            tables=tables,
            relationships=relationships,
            measures=measures,
            dimensions=dimensions,
            dialect=dialect,
        )

    def format_schema_for_prompt(self, context: SchemaContext) -> str:
        """Format schema context for inclusion in LLM prompt"""
        lines = []

        # Tables and columns
        lines.append("## Tables\n")
        for table in context.tables:
            table_desc = f" - {table.description}" if table.description else ""
            lines.append(f"### {table.schema_name}.{table.name}{table_desc}")
            lines.append("Columns:")
            for col in table.columns:
                pk = " (PK)" if col.is_primary_key else ""
                fk = f" (FK -> {col.foreign_key_ref})" if col.is_foreign_key else ""
                desc = f" - {col.description}" if col.description else ""
                lines.append(f"  - {col.name}: {col.data_type}{pk}{fk}{desc}")
            lines.append("")

        # Relationships
        if context.relationships:
            lines.append("## Relationships\n")
            for rel in context.relationships:
                lines.append(f"- {rel.from_table}.{rel.from_column} -> {rel.to_table}.{rel.to_column} ({rel.relationship_type})")
            lines.append("")

        # Measures (from semantic model)
        if context.measures:
            lines.append("## Available Measures\n")
            for m in context.measures:
                desc = f" - {m.description}" if m.description else ""
                lines.append(f"- {m.name}: {m.expression}{desc}")
            lines.append("")

        # Dimensions
        if context.dimensions:
            lines.append("## Available Dimensions\n")
            for d in context.dimensions:
                desc = f" - {d.description}" if d.description else ""
                lines.append(f"- {d.name} ({d.table}.{d.column}){desc}")
            lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # QUERY GENERATION
    # ========================================================================

    async def generate_sql(
        self,
        request: NLQueryRequest,
        user_id: Optional[str] = None,
    ) -> NLQueryResponse:
        """
        Generate SQL from natural language question.
        """
        start_time = time.time()

        # Build schema context
        context = await self.build_schema_context(
            connection_id=request.connection_id or "",
            model_id=request.model_id,
        )

        # Detect intent
        intent = self._detect_intent(request.question)

        # Generate SQL using OpenAI or fallback
        if self.client:
            result = await self._generate_sql_openai(request.question, context, intent)
        else:
            result = self._generate_sql_fallback(request.question, context, intent)

        # Validate the generated SQL
        validation = self._validate_sql(result["sql"], context.dialect)

        # Estimate complexity
        complexity = self._estimate_complexity(result["sql"])

        # Generate follow-up questions
        follow_ups = self._generate_follow_up_questions(request.question, intent, context)

        execution_time = (time.time() - start_time) * 1000

        # Store in history
        history_item = QueryHistoryItem(
            id=str(uuid.uuid4()),
            user_id=user_id,
            question=request.question,
            sql=result["sql"],
            connection_id=request.connection_id or "",
            model_id=request.model_id,
            executed=False,
            created_at=datetime.utcnow(),
        )
        await self.history_collection.insert_one(history_item.model_dump())

        return NLQueryResponse(
            sql=result["sql"],
            explanation=result.get("explanation", ""),
            confidence=result.get("confidence", 0.7),
            intent=intent,
            complexity=complexity,
            validation=validation,
            tables_used=result.get("tables_used", []),
            columns_used=result.get("columns_used", []),
            alternatives=result.get("alternatives", []),
            follow_up_questions=follow_ups,
            execution_time_ms=execution_time,
            conversation_id=request.conversation_id,
        )

    async def _generate_sql_openai(
        self,
        question: str,
        context: SchemaContext,
        intent: QueryIntent,
    ) -> dict[str, Any]:
        """Generate SQL using OpenAI API"""
        schema_text = self.format_schema_for_prompt(context)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            schema_context=schema_text,
            dialect=context.dialect,
        )

        # Build messages with few-shot examples
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add few-shot examples
        for example in FEW_SHOT_EXAMPLES[:2]:
            messages.append({"role": "user", "content": example["question"]})
            messages.append({
                "role": "assistant",
                "content": json.dumps({
                    "sql": example["sql"],
                    "explanation": example["explanation"],
                    "confidence": 0.95,
                    "tables_used": [],
                    "columns_used": [],
                })
            })

        # Add user question
        messages.append({"role": "user", "content": question})

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            return {
                "sql": result.get("sql", "SELECT 1"),
                "explanation": result.get("explanation", ""),
                "confidence": result.get("confidence", 0.7),
                "tables_used": result.get("tables_used", []),
                "columns_used": result.get("columns_used", []),
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_sql_fallback(question, context, intent)

    def _generate_sql_fallback(
        self,
        question: str,
        context: SchemaContext,
        intent: QueryIntent,
    ) -> dict[str, Any]:
        """Fallback SQL generation when OpenAI is unavailable"""
        question_lower = question.lower()

        # Get first table as default
        if not context.tables:
            return {
                "sql": "SELECT 1 -- No tables available",
                "explanation": "No schema context available",
                "confidence": 0.1,
            }

        table = context.tables[0]
        table_name = f'"{table.schema_name}"."{table.name}"'

        # Simple pattern matching
        if intent == QueryIntent.AGGREGATE:
            # Look for aggregation
            if any(kw in question_lower for kw in ["count", "how many", "number of"]):
                sql = f"SELECT COUNT(*) as count FROM {table_name}"
                explanation = f"Count of all rows in {table.name}"
            elif any(kw in question_lower for kw in ["total", "sum"]):
                # Find a numeric column
                num_col = next(
                    (c for c in table.columns if c.data_type in ["integer", "numeric", "decimal", "float", "double"]),
                    table.columns[0] if table.columns else None
                )
                if num_col:
                    sql = f'SELECT SUM("{num_col.name}") as total FROM {table_name}'
                    explanation = f"Sum of {num_col.name} from {table.name}"
                else:
                    sql = f"SELECT COUNT(*) as count FROM {table_name}"
                    explanation = f"Count of all rows in {table.name}"
            else:
                sql = f"SELECT * FROM {table_name} LIMIT 100"
                explanation = f"Sample data from {table.name}"

        elif intent == QueryIntent.TOP_N:
            # Extract N if present
            n_match = re.search(r'top\s*(\d+)', question_lower)
            n = int(n_match.group(1)) if n_match else 10
            sql = f"SELECT * FROM {table_name} LIMIT {n}"
            explanation = f"Top {n} rows from {table.name}"

        else:
            # Default: select all with limit
            sql = f"SELECT * FROM {table_name} LIMIT 100"
            explanation = f"Sample data from {table.name}"

        return {
            "sql": sql,
            "explanation": explanation,
            "confidence": 0.5,
            "tables_used": [table.name],
            "columns_used": [],
        }

    def _detect_intent(self, question: str) -> QueryIntent:
        """Detect the intent of a natural language question"""
        question_lower = question.lower()

        # Check for aggregation
        if any(kw in question_lower for kw in AGGREGATION_KEYWORDS):
            return QueryIntent.AGGREGATE

        # Check for comparison
        if any(kw in question_lower for kw in COMPARISON_KEYWORDS):
            return QueryIntent.COMPARE

        # Check for time/trend analysis
        if any(kw in question_lower for kw in TIME_KEYWORDS):
            return QueryIntent.TREND

        # Check for top-N
        if re.search(r'top\s*\d+|bottom\s*\d+|first\s*\d+|last\s*\d+', question_lower):
            return QueryIntent.TOP_N

        # Check for filtering
        if any(kw in question_lower for kw in ["where", "filter", "only", "just", "specific"]):
            return QueryIntent.FILTER

        # Default to select
        return QueryIntent.SELECT

    # ========================================================================
    # QUERY VALIDATION
    # ========================================================================

    def _validate_sql(self, sql: str, dialect: str = "postgresql") -> QueryValidation:
        """Validate generated SQL for security and correctness"""
        messages = []
        blocked = []
        status = ValidationStatus.VALID

        sql_upper = sql.upper()

        # Check for blocked keywords
        for keyword in BLOCKED_KEYWORDS:
            if keyword.upper() in sql_upper:
                blocked.append(keyword)
                status = ValidationStatus.BLOCKED

        if blocked:
            messages.append(f"Blocked operations detected: {', '.join(blocked)}")
            return QueryValidation(
                status=status,
                messages=messages,
                blocked_keywords=blocked,
            )

        # Check for multiple statements
        if sql.count(';') > 1:
            messages.append("Multiple SQL statements detected - only single statements allowed")
            status = ValidationStatus.BLOCKED

        # Warn about missing LIMIT
        if "SELECT" in sql_upper and "LIMIT" not in sql_upper:
            messages.append("Warning: No LIMIT clause - query may return large result set")
            if status == ValidationStatus.VALID:
                status = ValidationStatus.WARNING

        # Warn about SELECT *
        if "SELECT *" in sql_upper:
            messages.append("Warning: SELECT * may return unnecessary columns")
            if status == ValidationStatus.VALID:
                status = ValidationStatus.WARNING

        # Warn about CROSS JOIN
        if "CROSS JOIN" in sql_upper:
            messages.append("Warning: CROSS JOIN may produce very large result set")
            if status == ValidationStatus.VALID:
                status = ValidationStatus.WARNING

        return QueryValidation(
            status=status,
            messages=messages,
            blocked_keywords=blocked,
            estimated_complexity=self._estimate_complexity(sql),
        )

    def _estimate_complexity(self, sql: str) -> QueryComplexity:
        """Estimate the complexity of a SQL query"""
        sql_upper = sql.upper()

        complexity_score = 0

        # Count JOINs
        join_count = sql_upper.count(" JOIN ")
        complexity_score += join_count * 2

        # Count subqueries
        subquery_count = sql_upper.count("(SELECT")
        complexity_score += subquery_count * 3

        # Check for window functions
        if any(fn in sql_upper for fn in ["ROW_NUMBER()", "RANK()", "DENSE_RANK()", "OVER("]):
            complexity_score += 2

        # Check for CTEs
        if "WITH " in sql_upper:
            complexity_score += 2

        # Check for aggregations with GROUP BY
        if "GROUP BY" in sql_upper:
            complexity_score += 1

        # Check for HAVING
        if "HAVING" in sql_upper:
            complexity_score += 1

        # Check for UNION
        if "UNION" in sql_upper:
            complexity_score += 2

        if complexity_score <= 2:
            return QueryComplexity.SIMPLE
        elif complexity_score <= 5:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.COMPLEX

    # ========================================================================
    # CHAT MANAGEMENT
    # ========================================================================

    async def create_session(
        self,
        user_id: Optional[str] = None,
        connection_id: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            connection_id=connection_id,
            model_id=model_id,
            messages=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        await self.sessions_collection.insert_one(session.model_dump())
        return session

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        doc = await self.sessions_collection.find_one({"id": session_id})
        if doc:
            return ChatSession(**doc)
        return None

    async def chat(
        self,
        request: ChatRequest,
        user_id: Optional[str] = None,
    ) -> ChatResponse:
        """Process a chat message and return response"""

        # Get or create session
        session = None
        if request.session_id:
            session = await self.get_session(request.session_id)

        if not session:
            session = await self.create_session(
                user_id=user_id,
                connection_id=request.connection_id,
                model_id=request.model_id,
            )

        # Add user message
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            content=request.message,
            timestamp=datetime.utcnow(),
        )
        session.messages.append(user_message)

        # Generate SQL
        nl_request = NLQueryRequest(
            question=request.message,
            connection_id=session.connection_id,
            model_id=session.model_id,
            conversation_id=session.id,
        )

        query_result = await self.generate_sql(nl_request, user_id)

        # Build assistant response
        response_text = query_result.explanation
        if query_result.validation.status == ValidationStatus.BLOCKED:
            response_text = "I cannot generate that query as it contains blocked operations. " + \
                          "I can only help with SELECT queries that read data."

        # Add assistant message
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.ASSISTANT,
            content=response_text,
            timestamp=datetime.utcnow(),
            sql=query_result.sql if query_result.validation.status != ValidationStatus.BLOCKED else None,
        )
        session.messages.append(assistant_message)

        # Update session
        session.updated_at = datetime.utcnow()
        await self.sessions_collection.update_one(
            {"id": session.id},
            {"$set": session.model_dump()}
        )

        return ChatResponse(
            session_id=session.id,
            message_id=assistant_message.id,
            response=response_text,
            sql=query_result.sql if query_result.validation.status != ValidationStatus.BLOCKED else None,
            suggestions=self._generate_suggestions(request.message, session),
            follow_up_questions=query_result.follow_up_questions,
        )

    def _generate_suggestions(
        self,
        question: str,
        session: ChatSession,
    ) -> list[str]:
        """Generate follow-up suggestions based on conversation"""
        suggestions = []

        # Based on question type, suggest related queries
        question_lower = question.lower()

        if "total" in question_lower or "sum" in question_lower:
            suggestions.append("Break this down by category")
            suggestions.append("Show the trend over time")

        if "by" in question_lower:
            suggestions.append("Show this as a percentage")
            suggestions.append("What's the top performer?")

        if any(kw in question_lower for kw in ["this month", "last month", "this year"]):
            suggestions.append("Compare to previous period")
            suggestions.append("Show year over year growth")

        # Default suggestions
        if not suggestions:
            suggestions = [
                "Show more details",
                "Filter by a specific value",
                "Add another dimension",
            ]

        return suggestions[:4]

    def _generate_follow_up_questions(
        self,
        question: str,
        intent: QueryIntent,
        context: SchemaContext,
    ) -> list[str]:
        """Generate follow-up questions based on the query"""
        follow_ups = []

        if intent == QueryIntent.AGGREGATE:
            follow_ups.append("Would you like to see this broken down by time period?")
            if context.dimensions:
                dim = context.dimensions[0]
                follow_ups.append(f"Would you like to group by {dim.name}?")

        elif intent == QueryIntent.TREND:
            follow_ups.append("Would you like to compare to the same period last year?")
            follow_ups.append("Should I calculate the growth rate?")

        elif intent == QueryIntent.TOP_N:
            follow_ups.append("Would you like to see the bottom performers instead?")
            follow_ups.append("Should I show more details for these items?")

        return follow_ups[:3]

    # ========================================================================
    # HISTORY
    # ========================================================================

    async def get_query_history(
        self,
        user_id: Optional[str] = None,
        connection_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[QueryHistoryItem], int]:
        """Get query history with pagination"""
        query = {}
        if user_id:
            query["user_id"] = user_id
        if connection_id:
            query["connection_id"] = connection_id

        total = await self.history_collection.count_documents(query)

        cursor = self.history_collection.find(query) \
            .sort("created_at", -1) \
            .skip((page - 1) * page_size) \
            .limit(page_size)

        items = []
        async for doc in cursor:
            items.append(QueryHistoryItem(**doc))

        return items, total


def get_kodee_service(db: AsyncIOMotorClient) -> KodeeService:
    """Factory function to get Kodee service instance"""
    return KodeeService(db)
