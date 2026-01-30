INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Generating static SQL
INFO  [alembic.runtime.migration] Will assume transactional DDL.
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INFO  [alembic.runtime.migration] Running upgrade  -> 59ff6bfee78a, add_semantic_and_dashboard_models
-- Running upgrade  -> 59ff6bfee78a

CREATE TABLE users (
    id UUID NOT NULL, 
    email VARCHAR NOT NULL, 
    hashed_password VARCHAR, 
    full_name VARCHAR, 
    avatar_url VARCHAR, 
    role VARCHAR DEFAULT 'viewer' NOT NULL, 
    status VARCHAR DEFAULT 'active' NOT NULL, 
    passport_user_id VARCHAR, 
    company_code VARCHAR, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    last_login TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (id), 
    UNIQUE (passport_user_id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE semantic_models (
    id UUID NOT NULL, 
    connection_id VARCHAR NOT NULL, 
    name VARCHAR NOT NULL, 
    description TEXT, 
    schema_name VARCHAR NOT NULL, 
    table_name VARCHAR NOT NULL, 
    is_active BOOLEAN DEFAULT 'true', 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    created_by UUID, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_semantic_models_connection_id ON semantic_models (connection_id);

CREATE TABLE semantic_dimensions (
    id UUID NOT NULL, 
    semantic_model_id UUID NOT NULL, 
    name VARCHAR NOT NULL, 
    description TEXT, 
    column_name VARCHAR NOT NULL, 
    column_expression VARCHAR, 
    display_format VARCHAR, 
    sort_order INTEGER DEFAULT '0', 
    is_hidden BOOLEAN DEFAULT 'false', 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(semantic_model_id) REFERENCES semantic_models (id) ON DELETE CASCADE
);

CREATE TABLE semantic_measures (
    id UUID NOT NULL, 
    semantic_model_id UUID NOT NULL, 
    name VARCHAR NOT NULL, 
    description TEXT, 
    column_name VARCHAR NOT NULL, 
    expression VARCHAR NOT NULL, 
    aggregation VARCHAR DEFAULT 'sum', 
    display_format VARCHAR, 
    format_pattern VARCHAR, 
    sort_order INTEGER DEFAULT '0', 
    is_hidden BOOLEAN DEFAULT 'false', 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(semantic_model_id) REFERENCES semantic_models (id) ON DELETE CASCADE
);

CREATE TABLE semantic_joins (
    id UUID NOT NULL, 
    semantic_model_id UUID NOT NULL, 
    target_schema VARCHAR NOT NULL, 
    target_table VARCHAR NOT NULL, 
    target_alias VARCHAR, 
    join_type VARCHAR DEFAULT 'left', 
    join_condition VARCHAR NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(semantic_model_id) REFERENCES semantic_models (id) ON DELETE CASCADE
);

CREATE TABLE dashboards (
    id UUID NOT NULL, 
    name VARCHAR NOT NULL, 
    description TEXT, 
    icon VARCHAR, 
    created_by UUID, 
    is_public BOOLEAN DEFAULT 'false', 
    is_featured BOOLEAN DEFAULT 'false', 
    layout JSON, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id)
);

CREATE TABLE saved_charts (
    id UUID NOT NULL, 
    dashboard_id UUID, 
    name VARCHAR NOT NULL, 
    description TEXT, 
    connection_id VARCHAR NOT NULL, 
    semantic_model_id UUID, 
    chart_type VARCHAR NOT NULL, 
    chart_config JSON NOT NULL, 
    query_config JSON, 
    width INTEGER DEFAULT '6', 
    height INTEGER DEFAULT '4', 
    position_x INTEGER DEFAULT '0', 
    position_y INTEGER DEFAULT '0', 
    created_by UUID, 
    is_favorite BOOLEAN DEFAULT 'false', 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    last_viewed_at TIMESTAMP WITHOUT TIME ZONE, 
    view_count INTEGER DEFAULT '0', 
    PRIMARY KEY (id), 
    FOREIGN KEY(dashboard_id) REFERENCES dashboards (id) ON DELETE CASCADE
);

CREATE TABLE suggested_questions (
    id UUID NOT NULL, 
    question VARCHAR NOT NULL, 
    description TEXT, 
    icon VARCHAR, 
    connection_id VARCHAR NOT NULL, 
    query_config JSON NOT NULL, 
    chart_type VARCHAR DEFAULT 'bar', 
    category VARCHAR, 
    sort_order INTEGER DEFAULT '0', 
    is_active BOOLEAN DEFAULT 'true', 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id)
);

INSERT INTO alembic_version (version_num) VALUES ('59ff6bfee78a') RETURNING alembic_version.version_num;

COMMIT;

