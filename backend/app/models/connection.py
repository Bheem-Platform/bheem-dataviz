from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

from app.database import Base


class ConnectionType(str, enum.Enum):
    postgresql = "postgresql"
    mysql = "mysql"
    bigquery = "bigquery"
    snowflake = "snowflake"
    redshift = "redshift"
    clickhouse = "clickhouse"
    mongodb = "mongodb"
    elasticsearch = "elasticsearch"
    csv = "csv"
    excel = "excel"
    api = "api"
    cube = "cube"


class ConnectionStatus(str, enum.Enum):
    connected = "connected"
    disconnected = "disconnected"
    error = "error"
    syncing = "syncing"


class Connection(Base):
    __tablename__ = "connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(ConnectionType, name='connection_type', create_type=False), nullable=False)
    host = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    database_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    encrypted_password = Column(Text, nullable=True)
    ssl_enabled = Column(Boolean, default=False)
    additional_config = Column(JSONB, default={})
    status = Column(SQLEnum(ConnectionStatus, name='connection_status', create_type=False), default=ConnectionStatus.disconnected)
    tables_count = Column(Integer, default=0)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
