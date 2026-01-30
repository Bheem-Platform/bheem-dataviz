"""add_semantic_and_dashboard_models

Revision ID: 59ff6bfee78a
Revises:
Create Date: 2026-01-17 09:34:15.214013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '59ff6bfee78a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get database connection to check existing tables
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create users table
    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
            sa.Column('hashed_password', sa.String(), nullable=True),
            sa.Column('full_name', sa.String(), nullable=True),
            sa.Column('avatar_url', sa.String(), nullable=True),
            sa.Column('role', sa.String(), nullable=False, server_default='viewer'),
            sa.Column('status', sa.String(), nullable=False, server_default='active'),
            sa.Column('passport_user_id', sa.String(), nullable=True, unique=True),
            sa.Column('company_code', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('last_login', sa.DateTime(), nullable=True),
        )

    # Create semantic_models table
    if 'semantic_models' not in existing_tables:
        op.create_table(
            'semantic_models',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('connection_id', sa.String(), nullable=False, index=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('schema_name', sa.String(), nullable=False),
            sa.Column('table_name', sa.String(), nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        )

    # Create semantic_dimensions table
    if 'semantic_dimensions' not in existing_tables:
        op.create_table(
            'semantic_dimensions',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('semantic_models.id', ondelete='CASCADE'), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('column_name', sa.String(), nullable=False),
            sa.Column('column_expression', sa.String(), nullable=True),
            sa.Column('display_format', sa.String(), nullable=True),
            sa.Column('sort_order', sa.Integer(), server_default='0'),
            sa.Column('is_hidden', sa.Boolean(), server_default='false'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        )

    # Create semantic_measures table
    if 'semantic_measures' not in existing_tables:
        op.create_table(
            'semantic_measures',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('semantic_models.id', ondelete='CASCADE'), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('column_name', sa.String(), nullable=False),
            sa.Column('expression', sa.String(), nullable=False),
            sa.Column('aggregation', sa.String(), server_default='sum'),
            sa.Column('display_format', sa.String(), nullable=True),
            sa.Column('format_pattern', sa.String(), nullable=True),
            sa.Column('sort_order', sa.Integer(), server_default='0'),
            sa.Column('is_hidden', sa.Boolean(), server_default='false'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        )

    # Create semantic_joins table
    if 'semantic_joins' not in existing_tables:
        op.create_table(
            'semantic_joins',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('semantic_models.id', ondelete='CASCADE'), nullable=False),
            sa.Column('target_schema', sa.String(), nullable=False),
            sa.Column('target_table', sa.String(), nullable=False),
            sa.Column('target_alias', sa.String(), nullable=True),
            sa.Column('join_type', sa.String(), server_default='left'),
            sa.Column('join_condition', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        )

    # Create dashboards table - SKIP if exists
    if 'dashboards' not in existing_tables:
        op.create_table(
            'dashboards',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('icon', sa.String(), nullable=True),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('is_public', sa.Boolean(), server_default='false'),
            sa.Column('is_featured', sa.Boolean(), server_default='false'),
            sa.Column('layout', postgresql.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        )

    # Create saved_charts table
    if 'saved_charts' not in existing_tables:
        op.create_table(
            'saved_charts',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dashboards.id', ondelete='CASCADE'), nullable=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('connection_id', sa.String(), nullable=False),
            sa.Column('semantic_model_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('chart_type', sa.String(), nullable=False),
            sa.Column('chart_config', postgresql.JSON(), nullable=False),
            sa.Column('query_config', postgresql.JSON(), nullable=True),
            sa.Column('width', sa.Integer(), server_default='6'),
            sa.Column('height', sa.Integer(), server_default='4'),
            sa.Column('position_x', sa.Integer(), server_default='0'),
            sa.Column('position_y', sa.Integer(), server_default='0'),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('is_favorite', sa.Boolean(), server_default='false'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('last_viewed_at', sa.DateTime(), nullable=True),
            sa.Column('view_count', sa.Integer(), server_default='0'),
        )

    # Create suggested_questions table
    if 'suggested_questions' not in existing_tables:
        op.create_table(
            'suggested_questions',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('question', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('icon', sa.String(), nullable=True),
            sa.Column('connection_id', sa.String(), nullable=False),
            sa.Column('query_config', postgresql.JSON(), nullable=False),
            sa.Column('chart_type', sa.String(), server_default='bar'),
            sa.Column('category', sa.String(), nullable=True),
            sa.Column('sort_order', sa.Integer(), server_default='0'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        )


def downgrade() -> None:
    # Only drop tables that we created (check if they exist)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'suggested_questions' in existing_tables:
        op.drop_table('suggested_questions')
    if 'saved_charts' in existing_tables:
        op.drop_table('saved_charts')
    # Don't drop dashboards as it may have existed before
    if 'semantic_joins' in existing_tables:
        op.drop_table('semantic_joins')
    if 'semantic_measures' in existing_tables:
        op.drop_table('semantic_measures')
    if 'semantic_dimensions' in existing_tables:
        op.drop_table('semantic_dimensions')
    if 'semantic_models' in existing_tables:
        op.drop_table('semantic_models')
    if 'users' in existing_tables:
        op.drop_table('users')
