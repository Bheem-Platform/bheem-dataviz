"""
Kodee NL-to-SQL API Endpoints

Provides endpoints for natural language to SQL conversion,
chat interactions, and query history.
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient

from app.database import get_db
from app.core.security import get_current_user, CurrentUser
from app.schemas.kodee import (
    NLQueryRequest,
    NLQueryResponse,
    ChatRequest,
    ChatResponse,
    ChatSession,
    SchemaContext,
    QueryHistoryResponse,
    SQLValidationRequest,
    QueryValidation,
    QueryFeedback,
    FEW_SHOT_EXAMPLES,
)
from app.services.kodee_service import get_kodee_service

router = APIRouter()


# NL-to-SQL Query

@router.post("/query", response_model=NLQueryResponse)
async def generate_sql_query(
    request: NLQueryRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Convert a natural language question to SQL.

    Takes a question in plain English and generates the corresponding
    SQL query based on the schema context.
    """
    service = get_kodee_service(db)
    return await service.generate_sql(
        request,
        user_id=current_user.id,
    )


# Schema Context

@router.get("/context/{connection_id}", response_model=SchemaContext)
async def get_schema_context(
    connection_id: str,
    model_id: Optional[str] = Query(None, description="Semantic model ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Get the schema context for a connection.

    Returns table and column metadata used for NL-to-SQL generation.
    """
    service = get_kodee_service(db)
    return await service.build_schema_context(
        connection_id=connection_id,
        model_id=model_id,
    )


# Chat Interface

@router.post("/chat", response_model=ChatResponse)
async def chat_with_kodee(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Chat with Kodee for conversational data exploration.

    Maintains conversation context and can generate SQL from
    natural language questions.
    """
    service = get_kodee_service(db)
    return await service.chat(
        request,
        user_id=current_user.id,
    )


@router.post("/chat/session", response_model=ChatSession)
async def create_chat_session(
    connection_id: Optional[str] = None,
    model_id: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """Create a new chat session"""
    service = get_kodee_service(db)
    return await service.create_session(
        user_id=current_user.id,
        connection_id=connection_id,
        model_id=model_id,
    )


@router.get("/chat/session/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """Get a chat session by ID"""
    service = get_kodee_service(db)
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/chat/sessions", response_model=list[ChatSession])
async def list_chat_sessions(
    connection_id: Optional[str] = None,
    limit: int = Query(20, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """List chat sessions for the current user"""
    service = get_kodee_service(db)

    query = {"user_id": current_user.id}
    if connection_id:
        query["connection_id"] = connection_id

    sessions = []
    async for doc in service.sessions_collection.find(query).sort("updated_at", -1).limit(limit):
        sessions.append(ChatSession(**doc))

    return sessions


# SQL Validation

@router.post("/validate", response_model=QueryValidation)
async def validate_sql(
    request: SQLValidationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Validate a SQL query for security and correctness.

    Checks for blocked operations (DROP, DELETE, etc.) and
    provides warnings for potentially problematic queries.
    """
    service = get_kodee_service(db)
    # Determine dialect from connection if provided
    dialect = "postgresql"
    if request.connection_id:
        connection = await db.dataviz.connections.find_one({"id": request.connection_id})
        if connection:
            dialect = connection.get("type", "postgresql")

    return service._validate_sql(request.sql, dialect)


# Query History

@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    connection_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """Get query history for the current user"""
    service = get_kodee_service(db)
    items, total = await service.get_query_history(
        user_id=current_user.id,
        connection_id=connection_id,
        page=page,
        page_size=page_size,
    )

    return QueryHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/history/{query_id}")
async def delete_query_from_history(
    query_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """Delete a query from history"""
    service = get_kodee_service(db)
    result = await service.history_collection.delete_one({
        "id": query_id,
        "user_id": current_user.id,
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Query not found")

    return {"success": True, "message": "Query deleted from history"}


# Feedback

@router.post("/feedback")
async def submit_query_feedback(
    feedback: QueryFeedback,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Submit feedback on a generated query.

    Helps improve future NL-to-SQL generation.
    """
    feedback_doc = {
        "id": feedback.query_id,
        "user_id": current_user.id,
        "rating": feedback.rating,
        "correct_sql": feedback.correct_sql,
        "comments": feedback.comments,
        "created_at": __import__("datetime").datetime.utcnow(),
    }

    await db.dataviz.kodee_feedback.insert_one(feedback_doc)

    # Update history item with feedback
    await db.dataviz.kodee_history.update_one(
        {"id": feedback.query_id},
        {"$set": {"feedback_rating": feedback.rating}}
    )

    return {"success": True, "message": "Feedback submitted"}


# Examples and Templates

@router.get("/examples")
async def get_query_examples(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get example questions and SQL queries"""
    return {
        "examples": FEW_SHOT_EXAMPLES,
        "categories": [
            {
                "name": "Aggregations",
                "questions": [
                    "What is the total sales amount?",
                    "How many orders were placed this month?",
                    "What is the average order value?",
                ]
            },
            {
                "name": "Rankings",
                "questions": [
                    "What are the top 10 products by revenue?",
                    "Who are the best performing sales reps?",
                    "Which regions have the lowest sales?",
                ]
            },
            {
                "name": "Time Analysis",
                "questions": [
                    "Show me sales trends for the last 12 months",
                    "Compare this quarter to last quarter",
                    "What was our year-over-year growth?",
                ]
            },
            {
                "name": "Filtering",
                "questions": [
                    "Show orders from California",
                    "Which products have sales over $10,000?",
                    "List customers who haven't ordered in 6 months",
                ]
            },
        ]
    }


# Suggestions

@router.get("/suggestions/{connection_id}")
async def get_query_suggestions(
    connection_id: str,
    model_id: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
):
    """
    Get query suggestions based on schema context.

    Returns relevant question suggestions based on available
    tables, measures, and dimensions.
    """
    service = get_kodee_service(db)
    context = await service.build_schema_context(
        connection_id=connection_id,
        model_id=model_id,
    )

    suggestions = []

    # Generate suggestions based on measures
    for measure in context.measures[:5]:
        suggestions.append(f"What is the total {measure.name}?")
        suggestions.append(f"Show {measure.name} by month")

    # Generate suggestions based on dimensions
    for dim in context.dimensions[:3]:
        suggestions.append(f"Break down by {dim.name}")
        suggestions.append(f"Top 10 by {dim.name}")

    # Generate suggestions based on tables
    for table in context.tables[:3]:
        suggestions.append(f"Show recent records from {table.name}")
        suggestions.append(f"How many records are in {table.name}?")

    return {
        "suggestions": suggestions[:15],
        "schema_summary": {
            "tables": len(context.tables),
            "measures": len(context.measures),
            "dimensions": len(context.dimensions),
        }
    }
