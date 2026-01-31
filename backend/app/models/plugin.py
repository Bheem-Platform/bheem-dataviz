"""
Plugin Models

Database models for plugin management and configuration.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Plugin(Base):
    """
    Plugin model for installed plugins.
    """
    __tablename__ = "plugins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Plugin info
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False)

    # Source
    source = Column(String(50), default="marketplace")  # marketplace, custom, builtin
    package_url = Column(String(500), nullable=True)
    repository_url = Column(String(500), nullable=True)

    # Type
    plugin_type = Column(String(50), nullable=False)  # connector, visualization, transform, auth, export

    # Author
    author = Column(String(255), nullable=True)
    author_email = Column(String(255), nullable=True)

    # Icon/Branding
    icon_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)

    # Configuration schema
    config_schema = Column(JSONB, default={})
    default_config = Column(JSONB, default={})

    # Permissions required
    required_permissions = Column(JSONB, default=[])

    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)

    # Installation
    installed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    installed_by = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace_configs = relationship("PluginWorkspaceConfig", back_populates="plugin", cascade="all, delete-orphan")


class PluginWorkspaceConfig(Base):
    """
    Per-workspace plugin configuration.
    """
    __tablename__ = "plugin_workspace_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    plugin_id = Column(UUID(as_uuid=True), ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)

    # Configuration
    config = Column(JSONB, default={})
    secrets = Column(JSONB, default={})  # Encrypted

    # Status
    is_enabled = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    enabled_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    plugin = relationship("Plugin", back_populates="workspace_configs")

    __table_args__ = (
        Index('ix_plugin_workspace_configs_unique', plugin_id, workspace_id, unique=True),
    )


class PluginMarketplace(Base):
    """
    Plugin marketplace listing.
    """
    __tablename__ = "plugin_marketplace"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Plugin info
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)

    # Versioning
    latest_version = Column(String(50), nullable=False)
    versions = Column(JSONB, default=[])

    # Type
    plugin_type = Column(String(50), nullable=False)
    categories = Column(JSONB, default=[])
    tags = Column(JSONB, default=[])

    # Author
    author = Column(String(255), nullable=True)
    author_url = Column(String(500), nullable=True)

    # Assets
    icon_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    screenshots = Column(JSONB, default=[])

    # Stats
    downloads = Column(Integer, default=0)
    rating = Column(Float, default=0)
    reviews_count = Column(Integer, default=0)

    # Status
    is_verified = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
