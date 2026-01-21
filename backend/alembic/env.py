import os
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from sqlalchemy.orm import declarative_base

from alembic import context

# Import the app settings and models
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load .env file directly BEFORE any app imports
load_dotenv(backend_dir / ".env")

# Create a separate Base for alembic to avoid importing async engine
# Import the models directly to get their metadata
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Now import models - they use the same Base from app.database
# We need to import them to register their tables with metadata
from app.models.user import User, UserRole, UserStatus
from app.models.semantic import SemanticModel, Dimension, Measure, SemanticJoin
from app.models.dashboard import Dashboard, SavedChart, SuggestedQuestion
from app.models.connection import Connection, ConnectionType, ConnectionStatus

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Get DATABASE_URL from environment and convert to sync format
database_url = os.getenv("DATABASE_URL", "postgresql://localhost/dataviz")
# Remove +asyncpg if present for sync operations
sync_url = database_url.replace("+asyncpg", "")
# Escape % for configparser (double them)
sync_url_escaped = sync_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", sync_url_escaped)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get target_metadata from the actual models' Base
# Import here to get the metadata after models are loaded
from app.database import Base as AppBase
target_metadata = AppBase.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
