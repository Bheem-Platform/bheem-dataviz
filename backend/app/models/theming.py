"""
Theming Models

Database models for themes and appearance customization.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Theme(Base):
    """
    Theme model for visual customization.
    """
    __tablename__ = "themes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Theme info
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Type
    theme_type = Column(String(50), default="custom")  # system, custom

    # Colors
    primary_color = Column(String(20), default="#3B82F6")
    secondary_color = Column(String(20), default="#6366F1")
    accent_color = Column(String(20), default="#8B5CF6")
    background_color = Column(String(20), default="#FFFFFF")
    surface_color = Column(String(20), default="#F3F4F6")
    text_color = Column(String(20), default="#1F2937")

    # Dark mode colors
    dark_primary_color = Column(String(20), default="#60A5FA")
    dark_background_color = Column(String(20), default="#111827")
    dark_surface_color = Column(String(20), default="#1F2937")
    dark_text_color = Column(String(20), default="#F9FAFB")

    # Chart colors
    chart_colors = Column(JSONB, default=[
        "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
        "#EC4899", "#06B6D4", "#84CC16", "#F97316", "#6366F1"
    ])

    # Typography
    font_family = Column(String(100), default="Inter")
    heading_font = Column(String(100), nullable=True)
    font_size_base = Column(Integer, default=14)

    # Borders & Shadows
    border_radius = Column(Integer, default=8)
    shadow_style = Column(String(50), default="soft")  # none, soft, medium, hard

    # Custom CSS
    custom_css = Column(Text, nullable=True)

    # Logo
    logo_light_url = Column(String(500), nullable=True)
    logo_dark_url = Column(String(500), nullable=True)
    favicon_url = Column(String(500), nullable=True)

    # Status
    is_system = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkspaceTheme(Base):
    """
    Workspace theme settings.
    """
    __tablename__ = "workspace_themes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme_id = Column(UUID(as_uuid=True), ForeignKey("themes.id", ondelete="SET NULL"), nullable=True)

    # Mode
    color_mode = Column(String(20), default="auto")  # light, dark, auto

    # Overrides
    custom_overrides = Column(JSONB, default={})

    # Branding
    company_name = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    favicon_url = Column(String(500), nullable=True)

    # White-labeling
    hide_powered_by = Column(Boolean, default=False)
    custom_domain = Column(String(255), nullable=True)

    # Timestamps
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class UserThemePreference(Base):
    """
    User-level theme preferences.
    """
    __tablename__ = "user_theme_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Preferences
    color_mode = Column(String(20), default="auto")  # light, dark, auto
    theme_id = Column(UUID(as_uuid=True), nullable=True)

    # Display
    compact_mode = Column(Boolean, default=False)
    high_contrast = Column(Boolean, default=False)
    reduced_motion = Column(Boolean, default=False)

    # Chart preferences
    preferred_chart_theme = Column(String(50), default="default")
    chart_animation = Column(Boolean, default=True)

    # Timestamps
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
