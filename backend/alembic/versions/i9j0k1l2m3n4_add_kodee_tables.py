"""Add Kodee NL-to-SQL tables

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-01-30 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'i9j0k1l2m3n4'
down_revision = 'h8i9j0k1l2m3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE query_intent AS ENUM ('select', 'aggregate', 'compare', 'trend', 'top_n', 'filter', 'join', 'unknown')")
    op.execute("CREATE TYPE query_complexity AS ENUM ('simple', 'moderate', 'complex')")
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system')")
    op.execute("CREATE TYPE feedback_type AS ENUM ('positive', 'negative', 'correction')")

    # Create kodee_chat_sessions table
    op.create_table(
        'kodee_chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('schema_context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('message_count', sa.Integer(), default=0),
        sa.Column('query_count', sa.Integer(), default=0),
        sa.Column('successful_queries', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('archived_at', sa.DateTime(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['semantic_model_id'], ['semantic_models.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_kodee_chat_sessions_user_id', 'kodee_chat_sessions', ['user_id'])
    op.create_index('ix_kodee_chat_sessions_workspace_id', 'kodee_chat_sessions', ['workspace_id'])

    # Create kodee_chat_messages table
    op.create_table(
        'kodee_chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'assistant', 'system', name='message_role', create_type=False), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('generated_sql', sa.Text(), nullable=True),
        sa.Column('sql_explanation', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('intent', postgresql.ENUM('select', 'aggregate', 'compare', 'trend', 'top_n', 'filter', 'join', 'unknown', name='query_intent', create_type=False), nullable=True),
        sa.Column('complexity', postgresql.ENUM('simple', 'moderate', 'complex', name='query_complexity', create_type=False), nullable=True),
        sa.Column('tables_used', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('columns_used', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('query_executed', sa.Boolean(), default=False),
        sa.Column('execution_successful', sa.Boolean(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('query_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('visualization_type', sa.String(50), nullable=True),
        sa.Column('visualization_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('follow_up_questions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('alternative_queries', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['kodee_chat_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_kodee_chat_messages_session_id', 'kodee_chat_messages', ['session_id'])

    # Create kodee_query_history table
    op.create_table(
        'kodee_query_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('natural_language_query', sa.Text(), nullable=False),
        sa.Column('generated_sql', sa.Text(), nullable=False),
        sa.Column('intent', postgresql.ENUM('select', 'aggregate', 'compare', 'trend', 'top_n', 'filter', 'join', 'unknown', name='query_intent', create_type=False), nullable=True),
        sa.Column('complexity', postgresql.ENUM('simple', 'moderate', 'complex', name='query_complexity', create_type=False), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('executed', sa.Boolean(), default=False),
        sa.Column('execution_successful', sa.Boolean(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('feedback_received', sa.Boolean(), default=False),
        sa.Column('feedback_positive', sa.Boolean(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['semantic_model_id'], ['semantic_models.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['session_id'], ['kodee_chat_sessions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_kodee_query_history_created_at', 'kodee_query_history', ['created_at'])
    op.create_index('ix_kodee_query_history_user_id', 'kodee_query_history', ['user_id'])

    # Create kodee_query_feedback table
    op.create_table(
        'kodee_query_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('query_history_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('feedback_type', postgresql.ENUM('positive', 'negative', 'correction', name='feedback_type', create_type=False), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('corrected_sql', sa.Text(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('issue_categories', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['kodee_chat_messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['query_history_id'], ['kodee_query_history.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create kodee_query_templates table
    op.create_table(
        'kodee_query_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('question_patterns', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('sql_template', sa.Text(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), default=[]),
        sa.Column('required_tables', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('required_columns', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('connection_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('semantic_model_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_system', sa.Boolean(), default=False),
        sa.Column('use_count', sa.Integer(), default=0),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create kodee_schema_cache table
    op.create_table(
        'kodee_schema_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('cache_key', sa.String(64), nullable=False),
        sa.Column('schema_context', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('table_embeddings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('column_embeddings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('table_count', sa.Integer(), default=0),
        sa.Column('column_count', sa.Integer(), default=0),
        sa.Column('relationship_count', sa.Integer(), default=0),
        sa.Column('is_valid', sa.Boolean(), default=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['semantic_model_id'], ['semantic_models.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_kodee_schema_cache_cache_key', 'kodee_schema_cache', ['cache_key'], unique=True)

    # Create kodee_insights table
    op.create_table(
        'kodee_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('connection_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('chart_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('insight_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('impact', sa.String(20), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('supporting_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sql_query', sa.Text(), nullable=True),
        sa.Column('related_measures', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('related_dimensions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('time_period', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('dismissed_at', sa.DateTime(), nullable=True),
        sa.Column('dismissed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), default=False),
        sa.Column('shared_with_workspace', sa.Boolean(), default=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chart_id'], ['saved_charts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_kodee_insights_workspace_id', 'kodee_insights', ['workspace_id'])
    op.create_index('ix_kodee_insights_insight_type', 'kodee_insights', ['insight_type'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('kodee_insights')
    op.drop_table('kodee_schema_cache')
    op.drop_table('kodee_query_templates')
    op.drop_table('kodee_query_feedback')
    op.drop_table('kodee_query_history')
    op.drop_table('kodee_chat_messages')
    op.drop_table('kodee_chat_sessions')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS feedback_type")
    op.execute("DROP TYPE IF EXISTS message_role")
    op.execute("DROP TYPE IF EXISTS query_complexity")
    op.execute("DROP TYPE IF EXISTS query_intent")
