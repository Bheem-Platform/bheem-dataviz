"""
Kodee NL-to-SQL Schemas

Defines data models for the Kodee natural language to SQL engine,
including schema context, query generation, and chat interfaces.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class QueryIntent(str, Enum):
    """Detected intent from natural language query"""
    SELECT = "select"
    AGGREGATE = "aggregate"
    COMPARE = "compare"
    TREND = "trend"
    TOP_N = "top_n"
    FILTER = "filter"
    JOIN = "join"
    UNKNOWN = "unknown"


class QueryComplexity(str, Enum):
    """Complexity level of the generated query"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class MessageRole(str, Enum):
    """Role in chat conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ValidationStatus(str, Enum):
    """SQL validation status"""
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"
    BLOCKED = "blocked"


# Schema Context Models

class ColumnInfo(BaseModel):
    """Information about a database column"""
    name: str
    data_type: str
    nullable: bool = True
    description: Optional[str] = None
    sample_values: list[Any] = Field(default_factory=list)
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_ref: Optional[str] = None  # "table.column"


class TableInfo(BaseModel):
    """Information about a database table"""
    name: str
    schema_name: str = "public"
    description: Optional[str] = None
    columns: list[ColumnInfo] = Field(default_factory=list)
    row_count: Optional[int] = None
    aliases: list[str] = Field(default_factory=list)


class RelationshipInfo(BaseModel):
    """Information about table relationships"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str  # "one_to_one", "one_to_many", "many_to_many"


class MeasureInfo(BaseModel):
    """Information about semantic model measures"""
    id: str
    name: str
    description: Optional[str] = None
    expression: str  # e.g., "SUM(sales.amount)"
    table: str
    column: str
    aggregate: str


class DimensionInfo(BaseModel):
    """Information about semantic model dimensions"""
    id: str
    name: str
    description: Optional[str] = None
    table: str
    column: str
    hierarchy: Optional[list[str]] = None


class SchemaContext(BaseModel):
    """Complete schema context for NL-to-SQL generation"""
    connection_id: str
    model_id: Optional[str] = None
    model_name: Optional[str] = None
    tables: list[TableInfo] = Field(default_factory=list)
    relationships: list[RelationshipInfo] = Field(default_factory=list)
    measures: list[MeasureInfo] = Field(default_factory=list)
    dimensions: list[DimensionInfo] = Field(default_factory=list)
    dialect: str = "postgresql"  # postgresql, mysql, bigquery, snowflake
    additional_context: Optional[str] = None  # User-provided context


# Query Request/Response Models

class NLQueryRequest(BaseModel):
    """Request for NL-to-SQL conversion"""
    question: str = Field(..., description="Natural language question")
    connection_id: Optional[str] = None
    model_id: Optional[str] = None
    conversation_id: Optional[str] = None
    include_explanation: bool = True
    max_rows: int = Field(default=1000, le=10000)
    timeout_seconds: int = Field(default=30, le=120)


class QueryValidation(BaseModel):
    """SQL validation result"""
    status: ValidationStatus
    messages: list[str] = Field(default_factory=list)
    blocked_keywords: list[str] = Field(default_factory=list)
    estimated_complexity: Optional[QueryComplexity] = None
    estimated_rows: Optional[int] = None


class NLQueryResponse(BaseModel):
    """Response from NL-to-SQL conversion"""
    sql: str
    explanation: str
    confidence: float = Field(..., ge=0, le=1)
    intent: QueryIntent = QueryIntent.UNKNOWN
    complexity: QueryComplexity = QueryComplexity.SIMPLE
    validation: QueryValidation
    tables_used: list[str] = Field(default_factory=list)
    columns_used: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)  # Alternative SQL queries
    follow_up_questions: list[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    conversation_id: Optional[str] = None


class QueryExecutionRequest(BaseModel):
    """Request to execute a generated query"""
    sql: str
    connection_id: str
    max_rows: int = Field(default=1000, le=10000)
    timeout_seconds: int = Field(default=30, le=120)


class QueryExecutionResponse(BaseModel):
    """Response from query execution"""
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    execution_time_ms: float
    truncated: bool = False


# Chat Models

class ChatMessage(BaseModel):
    """A single message in a chat conversation"""
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    sql: Optional[str] = None
    query_result: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatSession(BaseModel):
    """A chat session with Kodee"""
    id: str
    user_id: Optional[str] = None
    connection_id: Optional[str] = None
    model_id: Optional[str] = None
    title: Optional[str] = None
    messages: list[ChatMessage] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    context: Optional[SchemaContext] = None


class ChatRequest(BaseModel):
    """Request for chat interaction"""
    message: str
    session_id: Optional[str] = None
    connection_id: Optional[str] = None
    model_id: Optional[str] = None
    execute_query: bool = True  # Whether to execute generated SQL
    include_visualization: bool = False


class ChatResponse(BaseModel):
    """Response from chat interaction"""
    session_id: str
    message_id: str
    response: str
    sql: Optional[str] = None
    query_result: Optional[QueryExecutionResponse] = None
    visualization_suggestion: Optional[dict[str, Any]] = None
    suggestions: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)


# Query History

class QueryHistoryItem(BaseModel):
    """A record of a previous query"""
    id: str
    user_id: Optional[str] = None
    question: str
    sql: str
    connection_id: str
    model_id: Optional[str] = None
    executed: bool = False
    execution_successful: Optional[bool] = None
    row_count: Optional[int] = None
    created_at: datetime


class QueryHistoryResponse(BaseModel):
    """Response with query history"""
    items: list[QueryHistoryItem]
    total: int
    page: int
    page_size: int


# Validation Request

class SQLValidationRequest(BaseModel):
    """Request to validate SQL"""
    sql: str
    connection_id: Optional[str] = None
    strict: bool = True  # Strict mode blocks more operations


# Feedback Models

class QueryFeedback(BaseModel):
    """User feedback on a generated query"""
    query_id: str
    rating: int = Field(..., ge=1, le=5)
    correct_sql: Optional[str] = None
    comments: Optional[str] = None


# Constants

BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE",
    "GRANT", "REVOKE", "EXEC", "EXECUTE", "xp_", "sp_", "--", "/*", "*/"
]

AGGREGATION_KEYWORDS = [
    "total", "sum", "count", "average", "avg", "mean", "max", "maximum",
    "min", "minimum", "how many", "number of", "percentage", "percent"
]

COMPARISON_KEYWORDS = [
    "compare", "versus", "vs", "against", "difference", "between", "more than",
    "less than", "greater", "higher", "lower", "top", "bottom", "best", "worst"
]

TIME_KEYWORDS = [
    "today", "yesterday", "this week", "last week", "this month", "last month",
    "this year", "last year", "ytd", "mtd", "qtd", "quarter", "year over year",
    "yoy", "mom", "trend", "over time", "by date", "by month", "by year"
]


# Prompt Templates

SYSTEM_PROMPT_TEMPLATE = """You are Kodee, an AI assistant specialized in converting natural language questions into SQL queries.

You have access to the following database schema:

{schema_context}

Guidelines:
1. Generate only SELECT queries - no data modification
2. Use proper table aliases and quote identifiers appropriately for {dialect}
3. Include appropriate JOINs based on the relationships defined
4. Apply reasonable LIMIT clauses to prevent excessive data retrieval
5. Use the semantic model measures and dimensions when available
6. Format SQL for readability with proper indentation
7. Explain your query in plain language

Respond in JSON format with:
- sql: The generated SQL query
- explanation: Plain language explanation of what the query does
- confidence: Your confidence level (0-1) in the query being correct
- tables_used: List of tables referenced
- columns_used: List of columns referenced
"""

FEW_SHOT_EXAMPLES = [
    {
        "question": "What are the top 10 products by sales?",
        "sql": """SELECT p.product_name, SUM(s.amount) as total_sales
FROM products p
JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_name
ORDER BY total_sales DESC
LIMIT 10""",
        "explanation": "This query retrieves the top 10 products ranked by their total sales amount, joining the products and sales tables."
    },
    {
        "question": "How many orders were placed last month?",
        "sql": """SELECT COUNT(*) as order_count
FROM orders
WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND order_date < DATE_TRUNC('month', CURRENT_DATE)""",
        "explanation": "This query counts all orders placed in the previous calendar month."
    },
    {
        "question": "Show me sales by region for this year",
        "sql": """SELECT r.region_name, SUM(s.amount) as total_sales
FROM sales s
JOIN regions r ON s.region_id = r.region_id
WHERE s.sale_date >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY r.region_name
ORDER BY total_sales DESC""",
        "explanation": "This query shows total sales grouped by region for the current year to date."
    }
]
