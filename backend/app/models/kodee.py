"""
Kodee NL-to-SQL Models

SQLAlchemy models for Kodee AI chat sessions and query history.
"""

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class QueryIntent(str, enum.Enum):
    """Types of query intent detected by Kodee"""
    SELECT = "select"
    AGGREGATE = "aggregate"
    COMPARE = "compare"
    TREND = "trend"
    TOP_N = "top_n"
    FILTER = "filter"
    JOIN = "join"
    UNKNOWN = "unknown"


class QueryComplexity(str, enum.Enum):
    """Complexity levels of generated queries"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class MessageRole(str, enum.Enum):
    """Role of message in chat"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class FeedbackType(str, enum.Enum):
    """Types of user feedback"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CORRECTION = "correction"


class KodeeChatSession(Base):
    """
    Kodee chat session model.

    Stores conversation sessions between users and Kodee AI.
    """
    __tablename__ = "kodee_chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Context
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.id", ondelete="SET NULL"), nullable=True)
    semantic_model_id = Column(UUID(as_uuid=True), ForeignKey("semantic_models.id", ondelete="SET NULL"), nullable=True)

    # Session info
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Schema context snapshot (for historical accuracy)
    schema_context = Column(JSONB, nullable=True)

    # Statistics
    message_count = Column(Integer, default=0)
    query_count = Column(Integer, default=0)
    successful_queries = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    archived_at = Column(DateTime, nullable=True)

    # Workspace
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)

    # Relationships
    messages = relationship("KodeeChatMessage", back_populates="session", cascade="all, delete-orphan")


class KodeeChatMessage(Base):
    """
    Kodee chat message model.

    Stores individual messages in a chat session.
    """
    __tablename__ = "kodee_chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("kodee_chat_sessions.id", ondelete="CASCADE"), nullable=False)

    # Message content
    role = Column(SQLEnum(MessageRole, name='message_role', create_type=False), nullable=False)
    content = Column(Text, nullable=False)

    # Generated SQL (for assistant messages)
    generated_sql = Column(Text, nullable=True)
    sql_explanation = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)

    # Query analysis
    intent = Column(SQLEnum(QueryIntent, name='query_intent', create_type=False), nullable=True)
    complexity = Column(SQLEnum(QueryComplexity, name='query_complexity', create_type=False), nullable=True)
    tables_used = Column(ARRAY(String), nullable=True)
    columns_used = Column(ARRAY(String), nullable=True)

    # Execution results (if query was executed)
    query_executed = Column(Boolean, default=False)
    execution_successful = Column(Boolean, nullable=True)
    row_count = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    query_result = Column(JSONB, nullable=True)  # Cached result for display

    # Visualization suggestion
    visualization_type = Column(String(50), nullable=True)
    visualization_config = Column(JSONB, nullable=True)

    # Follow-up suggestions
    follow_up_questions = Column(ARRAY(String), nullable=True)
    alternative_queries = Column(ARRAY(String), nullable=True)

    # Error information
    error_message = Column(Text, nullable=True)

    # Extra data (named 'metadata' in database)
    extra_metadata = Column("metadata", JSONB, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("KodeeChatSession", back_populates="messages")
    feedback = relationship("KodeeQueryFeedback", back_populates="message", uselist=False)


class KodeeQueryHistory(Base):
    """
    Kodee query history model.

    Stores all NL-to-SQL queries for analytics and improvement.
    """
    __tablename__ = "kodee_query_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User and context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.id", ondelete="SET NULL"), nullable=True)
    semantic_model_id = Column(UUID(as_uuid=True), ForeignKey("semantic_models.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("kodee_chat_sessions.id", ondelete="SET NULL"), nullable=True)

    # Query details
    natural_language_query = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=False)

    # Analysis
    intent = Column(SQLEnum(QueryIntent, name='query_intent', create_type=False), nullable=True)
    complexity = Column(SQLEnum(QueryComplexity, name='query_complexity', create_type=False), nullable=True)
    confidence = Column(Float, nullable=True)

    # Execution
    executed = Column(Boolean, default=False)
    execution_successful = Column(Boolean, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    row_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    # Feedback tracking
    feedback_received = Column(Boolean, default=False)
    feedback_positive = Column(Boolean, nullable=True)

    # Workspace
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class KodeeQueryFeedback(Base):
    """
    User feedback on Kodee-generated queries.

    Used to improve the NL-to-SQL model over time.
    """
    __tablename__ = "kodee_query_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    message_id = Column(UUID(as_uuid=True), ForeignKey("kodee_chat_messages.id", ondelete="CASCADE"), nullable=True)
    query_history_id = Column(UUID(as_uuid=True), ForeignKey("kodee_query_history.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Feedback type
    feedback_type = Column(SQLEnum(FeedbackType, name='feedback_type', create_type=False), nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 scale

    # Correction (if provided)
    corrected_sql = Column(Text, nullable=True)

    # Comments
    comments = Column(Text, nullable=True)

    # Issue categories
    issue_categories = Column(ARRAY(String), nullable=True)  # e.g., ['wrong_table', 'missing_filter']

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    message = relationship("KodeeChatMessage", back_populates="feedback")


class KodeeQueryTemplate(Base):
    """
    Curated query templates for common questions.

    Used to provide quick answers for frequent queries.
    """
    __tablename__ = "kodee_query_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Template info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    # Pattern matching
    question_patterns = Column(ARRAY(String), nullable=False)  # Regex patterns to match

    # Template SQL (with placeholders)
    sql_template = Column(Text, nullable=False)

    # Required parameters
    parameters = Column(JSONB, default=[])  # [{name, type, default, required}]

    # Context requirements
    required_tables = Column(ARRAY(String), nullable=True)
    required_columns = Column(ARRAY(String), nullable=True)

    # Applicable connections/models
    connection_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    semantic_model_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Built-in vs user-created

    # Usage stats
    use_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)

    # Workspace (null for global templates)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KodeeSchemaCache(Base):
    """
    Cached schema information for faster NL-to-SQL processing.

    Stores processed schema context for connections and models.
    """
    __tablename__ = "kodee_schema_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Source
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.id", ondelete="CASCADE"), nullable=True)
    semantic_model_id = Column(UUID(as_uuid=True), ForeignKey("semantic_models.id", ondelete="CASCADE"), nullable=True)

    # Cache key
    cache_key = Column(String(64), nullable=False, unique=True, index=True)

    # Cached data
    schema_context = Column(JSONB, nullable=False)

    # Embedding vectors for semantic search (stored as arrays)
    table_embeddings = Column(JSONB, nullable=True)  # {table_name: [vector]}
    column_embeddings = Column(JSONB, nullable=True)  # {table.column: [vector]}

    # Statistics
    table_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    relationship_count = Column(Integer, default=0)

    # Validity
    is_valid = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KodeeInsight(Base):
    """
    AI-generated insights from data analysis.

    Stores discovered patterns, anomalies, and recommendations.
    """
    __tablename__ = "kodee_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Source
    connection_id = Column(UUID(as_uuid=True), ForeignKey("connections.id", ondelete="CASCADE"), nullable=True)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=True)
    chart_id = Column(UUID(as_uuid=True), ForeignKey("saved_charts.id", ondelete="CASCADE"), nullable=True)

    # Insight details
    insight_type = Column(String(50), nullable=False)  # trend, anomaly, correlation, recommendation
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Impact/Priority
    impact = Column(String(20), nullable=True)  # high, medium, low
    confidence = Column(Float, nullable=True)

    # Supporting data
    supporting_data = Column(JSONB, nullable=True)  # Charts, numbers, etc.
    sql_query = Column(Text, nullable=True)  # Query used to generate insight

    # Related entities
    related_measures = Column(ARRAY(String), nullable=True)
    related_dimensions = Column(ARRAY(String), nullable=True)
    time_period = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    dismissed_at = Column(DateTime, nullable=True)
    dismissed_by = Column(UUID(as_uuid=True), nullable=True)

    # Visibility
    is_pinned = Column(Boolean, default=False)
    shared_with_workspace = Column(Boolean, default=False)

    # Workspace
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
