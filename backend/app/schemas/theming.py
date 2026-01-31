"""
Theming & White-Label Schemas

Pydantic schemas for themes, branding, custom CSS, and white-label configuration.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# Enums

class ThemeMode(str, Enum):
    """Theme color modes"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Follow system preference


class ThemeScope(str, Enum):
    """Theme scope"""
    GLOBAL = "global"  # System-wide
    WORKSPACE = "workspace"  # Per workspace
    USER = "user"  # Per user
    EMBED = "embed"  # For embedded content


class ComponentType(str, Enum):
    """UI component types for styling"""
    BUTTON = "button"
    INPUT = "input"
    CARD = "card"
    TABLE = "table"
    CHART = "chart"
    SIDEBAR = "sidebar"
    HEADER = "header"
    MODAL = "modal"
    TOOLTIP = "tooltip"
    BADGE = "badge"
    ALERT = "alert"
    DROPDOWN = "dropdown"


class FontWeight(str, Enum):
    """Font weights"""
    THIN = "100"
    LIGHT = "300"
    REGULAR = "400"
    MEDIUM = "500"
    SEMIBOLD = "600"
    BOLD = "700"
    EXTRABOLD = "800"


# Color Models

class ColorPalette(BaseModel):
    """Color palette configuration"""
    # Primary colors
    primary: str = "#3B82F6"  # Blue
    primary_hover: str = "#2563EB"
    primary_foreground: str = "#FFFFFF"

    # Secondary colors
    secondary: str = "#6B7280"  # Gray
    secondary_hover: str = "#4B5563"
    secondary_foreground: str = "#FFFFFF"

    # Accent colors
    accent: str = "#8B5CF6"  # Purple
    accent_hover: str = "#7C3AED"
    accent_foreground: str = "#FFFFFF"

    # Background colors
    background: str = "#FFFFFF"
    background_secondary: str = "#F9FAFB"
    background_tertiary: str = "#F3F4F6"

    # Foreground/text colors
    foreground: str = "#111827"
    foreground_secondary: str = "#6B7280"
    foreground_muted: str = "#9CA3AF"

    # Border colors
    border: str = "#E5E7EB"
    border_focus: str = "#3B82F6"

    # Status colors
    success: str = "#10B981"
    success_foreground: str = "#FFFFFF"
    warning: str = "#F59E0B"
    warning_foreground: str = "#000000"
    error: str = "#EF4444"
    error_foreground: str = "#FFFFFF"
    info: str = "#3B82F6"
    info_foreground: str = "#FFFFFF"

    # Chart colors (for data visualization)
    chart_colors: list[str] = Field(default_factory=lambda: [
        "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
        "#EC4899", "#06B6D4", "#84CC16", "#F97316", "#6366F1"
    ])


class DarkPalette(ColorPalette):
    """Dark mode color palette"""
    primary: str = "#60A5FA"
    primary_hover: str = "#3B82F6"

    background: str = "#111827"
    background_secondary: str = "#1F2937"
    background_tertiary: str = "#374151"

    foreground: str = "#F9FAFB"
    foreground_secondary: str = "#D1D5DB"
    foreground_muted: str = "#9CA3AF"

    border: str = "#374151"


# Typography Models

class FontConfig(BaseModel):
    """Font configuration"""
    family: str = "Inter, system-ui, sans-serif"
    fallback: str = "system-ui, -apple-system, sans-serif"
    weight: FontWeight = FontWeight.REGULAR
    size_base: str = "16px"
    line_height: str = "1.5"


class Typography(BaseModel):
    """Typography configuration"""
    # Font families
    font_sans: str = "Inter, system-ui, sans-serif"
    font_mono: str = "JetBrains Mono, monospace"
    font_heading: Optional[str] = None  # Uses sans by default

    # Font sizes
    size_xs: str = "0.75rem"
    size_sm: str = "0.875rem"
    size_base: str = "1rem"
    size_lg: str = "1.125rem"
    size_xl: str = "1.25rem"
    size_2xl: str = "1.5rem"
    size_3xl: str = "1.875rem"
    size_4xl: str = "2.25rem"

    # Line heights
    line_tight: str = "1.25"
    line_normal: str = "1.5"
    line_relaxed: str = "1.75"

    # Letter spacing
    tracking_tight: str = "-0.025em"
    tracking_normal: str = "0"
    tracking_wide: str = "0.025em"

    # Font weights
    weight_light: str = "300"
    weight_normal: str = "400"
    weight_medium: str = "500"
    weight_semibold: str = "600"
    weight_bold: str = "700"


# Spacing & Layout Models

class Spacing(BaseModel):
    """Spacing configuration"""
    base: str = "4px"
    xs: str = "4px"
    sm: str = "8px"
    md: str = "16px"
    lg: str = "24px"
    xl: str = "32px"
    xxl: str = "48px"


class BorderRadius(BaseModel):
    """Border radius configuration"""
    none: str = "0"
    sm: str = "4px"
    md: str = "8px"
    lg: str = "12px"
    xl: str = "16px"
    full: str = "9999px"


class Shadow(BaseModel):
    """Shadow configuration"""
    sm: str = "0 1px 2px rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px rgba(0, 0, 0, 0.1)"
    lg: str = "0 10px 15px rgba(0, 0, 0, 0.1)"
    xl: str = "0 20px 25px rgba(0, 0, 0, 0.15)"


# Component Styles

class ComponentStyle(BaseModel):
    """Style overrides for a component"""
    component: ComponentType
    styles: dict[str, str] = Field(default_factory=dict)
    variants: dict[str, dict[str, str]] = Field(default_factory=dict)


# Theme Models

class Theme(BaseModel):
    """Complete theme configuration"""
    id: str
    name: str
    description: Optional[str] = None
    mode: ThemeMode = ThemeMode.LIGHT
    scope: ThemeScope = ThemeScope.GLOBAL

    # Colors
    colors: ColorPalette = Field(default_factory=ColorPalette)
    dark_colors: Optional[ColorPalette] = None  # For auto mode

    # Typography
    typography: Typography = Field(default_factory=Typography)

    # Layout
    spacing: Spacing = Field(default_factory=Spacing)
    border_radius: BorderRadius = Field(default_factory=BorderRadius)
    shadows: Shadow = Field(default_factory=Shadow)

    # Component overrides
    components: list[ComponentStyle] = Field(default_factory=list)

    # Custom CSS
    custom_css: Optional[str] = None

    # Metadata
    is_default: bool = False
    is_system: bool = False
    created_by: Optional[str] = None
    workspace_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Preview
    preview_image: Optional[str] = None


class ThemeCreate(BaseModel):
    """Create theme request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    mode: ThemeMode = ThemeMode.LIGHT
    scope: ThemeScope = ThemeScope.WORKSPACE
    colors: Optional[ColorPalette] = None
    dark_colors: Optional[ColorPalette] = None
    typography: Optional[Typography] = None
    spacing: Optional[Spacing] = None
    border_radius: Optional[BorderRadius] = None
    shadows: Optional[Shadow] = None
    components: list[ComponentStyle] = Field(default_factory=list)
    custom_css: Optional[str] = None
    workspace_id: Optional[str] = None


class ThemeUpdate(BaseModel):
    """Update theme request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    mode: Optional[ThemeMode] = None
    colors: Optional[ColorPalette] = None
    dark_colors: Optional[ColorPalette] = None
    typography: Optional[Typography] = None
    spacing: Optional[Spacing] = None
    border_radius: Optional[BorderRadius] = None
    shadows: Optional[Shadow] = None
    components: Optional[list[ComponentStyle]] = None
    custom_css: Optional[str] = None
    is_default: Optional[bool] = None


# Branding Models

class Logo(BaseModel):
    """Logo configuration"""
    light_url: Optional[str] = None  # Logo for light mode
    dark_url: Optional[str] = None  # Logo for dark mode
    favicon_url: Optional[str] = None
    width: int = 120
    height: int = 40


class Branding(BaseModel):
    """White-label branding configuration"""
    id: str
    workspace_id: str

    # Basic info
    company_name: str
    tagline: Optional[str] = None
    support_email: Optional[str] = None
    support_url: Optional[str] = None

    # Logos
    logo: Logo = Field(default_factory=Logo)

    # Colors (quick branding)
    primary_color: str = "#3B82F6"
    secondary_color: str = "#6B7280"

    # Custom domain
    custom_domain: Optional[str] = None
    custom_domain_verified: bool = False

    # Footer
    footer_text: Optional[str] = None
    footer_links: list[dict[str, str]] = Field(default_factory=list)

    # Legal
    privacy_policy_url: Optional[str] = None
    terms_of_service_url: Optional[str] = None

    # Social
    social_links: dict[str, str] = Field(default_factory=dict)

    # Email templates
    email_from_name: Optional[str] = None
    email_from_address: Optional[str] = None

    # Feature flags
    hide_powered_by: bool = False
    custom_login_page: bool = False
    custom_error_pages: bool = False

    # Active theme
    theme_id: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class BrandingCreate(BaseModel):
    """Create branding configuration"""
    workspace_id: str
    company_name: str
    tagline: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo: Optional[Logo] = None


class BrandingUpdate(BaseModel):
    """Update branding configuration"""
    company_name: Optional[str] = None
    tagline: Optional[str] = None
    support_email: Optional[str] = None
    support_url: Optional[str] = None
    logo: Optional[Logo] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    custom_domain: Optional[str] = None
    footer_text: Optional[str] = None
    footer_links: Optional[list[dict[str, str]]] = None
    privacy_policy_url: Optional[str] = None
    terms_of_service_url: Optional[str] = None
    social_links: Optional[dict[str, str]] = None
    email_from_name: Optional[str] = None
    email_from_address: Optional[str] = None
    hide_powered_by: Optional[bool] = None
    theme_id: Optional[str] = None


# User Preferences

class UserThemePreferences(BaseModel):
    """User theme preferences"""
    user_id: str
    theme_mode: ThemeMode = ThemeMode.AUTO
    preferred_theme_id: Optional[str] = None
    font_size: str = "medium"  # small, medium, large
    reduce_motion: bool = False
    high_contrast: bool = False
    custom_overrides: dict[str, str] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# CSS Generation

class CSSVariables(BaseModel):
    """CSS custom properties"""
    variables: dict[str, str]
    scope: str = ":root"


class GeneratedCSS(BaseModel):
    """Generated CSS output"""
    css: str
    variables: CSSVariables
    minified: bool = False
    hash: str  # For cache busting


# Response Models

class ThemeListResponse(BaseModel):
    """List of themes"""
    themes: list[Theme]
    total: int


class ThemePreviewResponse(BaseModel):
    """Theme preview data"""
    theme: Theme
    css: GeneratedCSS
    preview_components: dict[str, str]  # Component previews


# Constants

DEFAULT_LIGHT_THEME = Theme(
    id="system-light",
    name="Light",
    description="Default light theme",
    mode=ThemeMode.LIGHT,
    is_default=True,
    is_system=True,
)

DEFAULT_DARK_THEME = Theme(
    id="system-dark",
    name="Dark",
    description="Default dark theme",
    mode=ThemeMode.DARK,
    colors=DarkPalette(),
    is_system=True,
)

PRESET_THEMES = {
    "ocean": {
        "name": "Ocean",
        "primary": "#0891B2",
        "secondary": "#0E7490",
        "accent": "#06B6D4",
    },
    "forest": {
        "name": "Forest",
        "primary": "#059669",
        "secondary": "#047857",
        "accent": "#10B981",
    },
    "sunset": {
        "name": "Sunset",
        "primary": "#EA580C",
        "secondary": "#C2410C",
        "accent": "#F97316",
    },
    "berry": {
        "name": "Berry",
        "primary": "#BE185D",
        "secondary": "#9D174D",
        "accent": "#EC4899",
    },
    "slate": {
        "name": "Slate",
        "primary": "#475569",
        "secondary": "#334155",
        "accent": "#64748B",
    },
}


# Helper Functions

def generate_css_variables(colors: ColorPalette) -> dict[str, str]:
    """Generate CSS custom properties from color palette."""
    return {
        "--color-primary": colors.primary,
        "--color-primary-hover": colors.primary_hover,
        "--color-primary-foreground": colors.primary_foreground,
        "--color-secondary": colors.secondary,
        "--color-secondary-hover": colors.secondary_hover,
        "--color-secondary-foreground": colors.secondary_foreground,
        "--color-accent": colors.accent,
        "--color-accent-hover": colors.accent_hover,
        "--color-accent-foreground": colors.accent_foreground,
        "--color-background": colors.background,
        "--color-background-secondary": colors.background_secondary,
        "--color-background-tertiary": colors.background_tertiary,
        "--color-foreground": colors.foreground,
        "--color-foreground-secondary": colors.foreground_secondary,
        "--color-foreground-muted": colors.foreground_muted,
        "--color-border": colors.border,
        "--color-border-focus": colors.border_focus,
        "--color-success": colors.success,
        "--color-warning": colors.warning,
        "--color-error": colors.error,
        "--color-info": colors.info,
    }


def generate_typography_variables(typography: Typography) -> dict[str, str]:
    """Generate CSS variables from typography config."""
    return {
        "--font-sans": typography.font_sans,
        "--font-mono": typography.font_mono,
        "--font-heading": typography.font_heading or typography.font_sans,
        "--text-xs": typography.size_xs,
        "--text-sm": typography.size_sm,
        "--text-base": typography.size_base,
        "--text-lg": typography.size_lg,
        "--text-xl": typography.size_xl,
        "--text-2xl": typography.size_2xl,
        "--text-3xl": typography.size_3xl,
        "--text-4xl": typography.size_4xl,
    }


def validate_hex_color(color: str) -> bool:
    """Validate hex color format."""
    import re
    return bool(re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color))


def lighten_color(hex_color: str, percent: float) -> str:
    """Lighten a hex color by a percentage."""
    # Simple implementation - production would be more sophisticated
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    new_rgb = tuple(min(255, int(c + (255 - c) * percent)) for c in rgb)
    return '#{:02x}{:02x}{:02x}'.format(*new_rgb)


def darken_color(hex_color: str, percent: float) -> str:
    """Darken a hex color by a percentage."""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    new_rgb = tuple(max(0, int(c * (1 - percent))) for c in rgb)
    return '#{:02x}{:02x}{:02x}'.format(*new_rgb)
