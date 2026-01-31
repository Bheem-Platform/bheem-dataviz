"""
Theming & White-Label Service

Business logic for theme management, branding, and CSS generation.
"""

from typing import Optional
from datetime import datetime
from collections import defaultdict
import hashlib

from app.schemas.theming import (
    ThemeMode,
    ThemeScope,
    ComponentType,
    ColorPalette,
    DarkPalette,
    Typography,
    Spacing,
    BorderRadius,
    Shadow,
    Theme,
    ThemeCreate,
    ThemeUpdate,
    Branding,
    BrandingCreate,
    BrandingUpdate,
    UserThemePreferences,
    CSSVariables,
    GeneratedCSS,
    ThemeListResponse,
    ThemePreviewResponse,
    Logo,
    DEFAULT_LIGHT_THEME,
    DEFAULT_DARK_THEME,
    PRESET_THEMES,
    generate_css_variables,
    generate_typography_variables,
)


class ThemingService:
    """Service for theming and branding management."""

    def __init__(self, db=None):
        self.db = db

    # In-memory stores (production would use database)
    _themes: dict[str, Theme] = {
        DEFAULT_LIGHT_THEME.id: DEFAULT_LIGHT_THEME,
        DEFAULT_DARK_THEME.id: DEFAULT_DARK_THEME,
    }
    _branding: dict[str, Branding] = {}
    _user_preferences: dict[str, UserThemePreferences] = {}
    _css_cache: dict[str, GeneratedCSS] = {}

    # Theme Management

    async def create_theme(
        self,
        user_id: str,
        data: ThemeCreate,
    ) -> Theme:
        """Create a new theme."""
        import uuid

        theme_id = str(uuid.uuid4())
        now = datetime.utcnow()

        theme = Theme(
            id=theme_id,
            name=data.name,
            description=data.description,
            mode=data.mode,
            scope=data.scope,
            colors=data.colors or ColorPalette(),
            dark_colors=data.dark_colors,
            typography=data.typography or Typography(),
            spacing=data.spacing or Spacing(),
            border_radius=data.border_radius or BorderRadius(),
            shadows=data.shadows or Shadow(),
            components=data.components,
            custom_css=data.custom_css,
            workspace_id=data.workspace_id,
            created_by=user_id,
            created_at=now,
        )

        self._themes[theme_id] = theme

        # Invalidate CSS cache
        self._invalidate_css_cache(theme_id)

        return theme

    async def get_theme(self, theme_id: str) -> Optional[Theme]:
        """Get a theme by ID."""
        return self._themes.get(theme_id)

    async def list_themes(
        self,
        workspace_id: Optional[str] = None,
        scope: Optional[ThemeScope] = None,
        mode: Optional[ThemeMode] = None,
        include_system: bool = True,
    ) -> ThemeListResponse:
        """List themes."""
        themes = list(self._themes.values())

        # Filter by workspace
        if workspace_id:
            themes = [
                t for t in themes
                if t.workspace_id is None or t.workspace_id == workspace_id
            ]

        # Filter by scope
        if scope:
            themes = [t for t in themes if t.scope == scope]

        # Filter by mode
        if mode:
            themes = [t for t in themes if t.mode == mode]

        # Filter system themes
        if not include_system:
            themes = [t for t in themes if not t.is_system]

        # Sort: default first, then by name
        themes.sort(key=lambda t: (not t.is_default, t.name.lower()))

        return ThemeListResponse(themes=themes, total=len(themes))

    async def update_theme(
        self,
        theme_id: str,
        user_id: str,
        data: ThemeUpdate,
    ) -> Optional[Theme]:
        """Update a theme."""
        theme = self._themes.get(theme_id)
        if not theme:
            return None

        # Don't allow updating system themes
        if theme.is_system:
            raise ValueError("Cannot modify system themes")

        # Update fields
        if data.name is not None:
            theme.name = data.name
        if data.description is not None:
            theme.description = data.description
        if data.mode is not None:
            theme.mode = data.mode
        if data.colors is not None:
            theme.colors = data.colors
        if data.dark_colors is not None:
            theme.dark_colors = data.dark_colors
        if data.typography is not None:
            theme.typography = data.typography
        if data.spacing is not None:
            theme.spacing = data.spacing
        if data.border_radius is not None:
            theme.border_radius = data.border_radius
        if data.shadows is not None:
            theme.shadows = data.shadows
        if data.components is not None:
            theme.components = data.components
        if data.custom_css is not None:
            theme.custom_css = data.custom_css
        if data.is_default is not None:
            # Unset other defaults
            if data.is_default:
                for t in self._themes.values():
                    if t.id != theme_id and t.workspace_id == theme.workspace_id:
                        t.is_default = False
            theme.is_default = data.is_default

        theme.updated_at = datetime.utcnow()

        # Invalidate CSS cache
        self._invalidate_css_cache(theme_id)

        return theme

    async def delete_theme(self, theme_id: str, user_id: str) -> bool:
        """Delete a theme."""
        theme = self._themes.get(theme_id)
        if not theme:
            return False

        # Don't allow deleting system themes
        if theme.is_system:
            raise ValueError("Cannot delete system themes")

        del self._themes[theme_id]
        self._invalidate_css_cache(theme_id)

        return True

    async def duplicate_theme(
        self,
        theme_id: str,
        user_id: str,
        new_name: str,
    ) -> Optional[Theme]:
        """Duplicate a theme."""
        source = self._themes.get(theme_id)
        if not source:
            return None

        import uuid
        new_id = str(uuid.uuid4())
        now = datetime.utcnow()

        duplicate = Theme(
            id=new_id,
            name=new_name,
            description=f"Copy of {source.name}",
            mode=source.mode,
            scope=source.scope,
            colors=source.colors.model_copy(),
            dark_colors=source.dark_colors.model_copy() if source.dark_colors else None,
            typography=source.typography.model_copy(),
            spacing=source.spacing.model_copy(),
            border_radius=source.border_radius.model_copy(),
            shadows=source.shadows.model_copy(),
            components=source.components.copy(),
            custom_css=source.custom_css,
            workspace_id=source.workspace_id,
            created_by=user_id,
            created_at=now,
        )

        self._themes[new_id] = duplicate
        return duplicate

    # Preset Themes

    async def get_preset_themes(self) -> list[dict]:
        """Get available preset themes."""
        return [
            {"id": k, **v}
            for k, v in PRESET_THEMES.items()
        ]

    async def apply_preset(
        self,
        theme_id: str,
        preset_id: str,
    ) -> Optional[Theme]:
        """Apply a preset to a theme."""
        theme = self._themes.get(theme_id)
        if not theme:
            return None

        preset = PRESET_THEMES.get(preset_id)
        if not preset:
            raise ValueError(f"Preset {preset_id} not found")

        # Update colors from preset
        theme.colors.primary = preset["primary"]
        theme.colors.primary_hover = preset.get("primary_hover", preset["primary"])
        theme.colors.secondary = preset["secondary"]
        theme.colors.accent = preset["accent"]
        theme.updated_at = datetime.utcnow()

        self._invalidate_css_cache(theme_id)

        return theme

    # CSS Generation

    async def generate_css(
        self,
        theme_id: str,
        minify: bool = True,
    ) -> GeneratedCSS:
        """Generate CSS for a theme."""
        cache_key = f"{theme_id}:{minify}"

        # Check cache
        if cache_key in self._css_cache:
            return self._css_cache[cache_key]

        theme = self._themes.get(theme_id)
        if not theme:
            raise ValueError(f"Theme {theme_id} not found")

        # Generate CSS variables
        color_vars = generate_css_variables(theme.colors)
        typography_vars = generate_typography_variables(theme.typography)

        all_vars = {**color_vars, **typography_vars}

        # Add spacing variables
        all_vars.update({
            "--spacing-xs": theme.spacing.xs,
            "--spacing-sm": theme.spacing.sm,
            "--spacing-md": theme.spacing.md,
            "--spacing-lg": theme.spacing.lg,
            "--spacing-xl": theme.spacing.xl,
        })

        # Add border radius
        all_vars.update({
            "--radius-sm": theme.border_radius.sm,
            "--radius-md": theme.border_radius.md,
            "--radius-lg": theme.border_radius.lg,
            "--radius-full": theme.border_radius.full,
        })

        # Add shadows
        all_vars.update({
            "--shadow-sm": theme.shadows.sm,
            "--shadow-md": theme.shadows.md,
            "--shadow-lg": theme.shadows.lg,
            "--shadow-xl": theme.shadows.xl,
        })

        # Generate CSS string
        css_lines = [":root {"]
        for key, value in all_vars.items():
            css_lines.append(f"  {key}: {value};")
        css_lines.append("}")

        # Add dark mode variables if auto mode
        if theme.mode == ThemeMode.AUTO and theme.dark_colors:
            dark_vars = generate_css_variables(theme.dark_colors)
            css_lines.append("")
            css_lines.append("@media (prefers-color-scheme: dark) {")
            css_lines.append("  :root {")
            for key, value in dark_vars.items():
                css_lines.append(f"    {key}: {value};")
            css_lines.append("  }")
            css_lines.append("}")

        # Add custom CSS
        if theme.custom_css:
            css_lines.append("")
            css_lines.append("/* Custom CSS */")
            css_lines.append(theme.custom_css)

        css = "\n".join(css_lines)

        if minify:
            css = self._minify_css(css)

        # Generate hash
        css_hash = hashlib.md5(css.encode()).hexdigest()[:8]

        result = GeneratedCSS(
            css=css,
            variables=CSSVariables(variables=all_vars),
            minified=minify,
            hash=css_hash,
        )

        # Cache
        self._css_cache[cache_key] = result

        return result

    def _minify_css(self, css: str) -> str:
        """Minify CSS."""
        import re
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # Remove whitespace
        css = re.sub(r'\s+', ' ', css)
        # Remove spaces around special chars
        css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
        return css.strip()

    def _invalidate_css_cache(self, theme_id: str) -> None:
        """Invalidate CSS cache for a theme."""
        keys_to_remove = [k for k in self._css_cache if k.startswith(f"{theme_id}:")]
        for key in keys_to_remove:
            del self._css_cache[key]

    # Theme Preview

    async def get_theme_preview(self, theme_id: str) -> ThemePreviewResponse:
        """Get theme preview with CSS and sample components."""
        theme = self._themes.get(theme_id)
        if not theme:
            raise ValueError(f"Theme {theme_id} not found")

        css = await self.generate_css(theme_id, minify=False)

        # Generate preview HTML for components
        previews = {
            "button": f'<button style="background: {theme.colors.primary}; color: {theme.colors.primary_foreground}; padding: 8px 16px; border-radius: {theme.border_radius.md};">Button</button>',
            "card": f'<div style="background: {theme.colors.background}; border: 1px solid {theme.colors.border}; border-radius: {theme.border_radius.lg}; padding: 16px;">Card Content</div>',
            "input": f'<input style="border: 1px solid {theme.colors.border}; border-radius: {theme.border_radius.md}; padding: 8px;" placeholder="Input field" />',
        }

        return ThemePreviewResponse(
            theme=theme,
            css=css,
            preview_components=previews,
        )

    # Branding Management

    async def create_branding(
        self,
        user_id: str,
        data: BrandingCreate,
    ) -> Branding:
        """Create branding configuration for a workspace."""
        import uuid

        # Check if branding already exists for workspace
        if data.workspace_id in self._branding:
            raise ValueError("Branding already exists for this workspace")

        branding_id = str(uuid.uuid4())
        now = datetime.utcnow()

        branding = Branding(
            id=branding_id,
            workspace_id=data.workspace_id,
            company_name=data.company_name,
            tagline=data.tagline,
            primary_color=data.primary_color or "#3B82F6",
            secondary_color=data.secondary_color or "#6B7280",
            logo=data.logo or Logo(),
            created_at=now,
        )

        self._branding[data.workspace_id] = branding
        return branding

    async def get_branding(self, workspace_id: str) -> Optional[Branding]:
        """Get branding for a workspace."""
        return self._branding.get(workspace_id)

    async def update_branding(
        self,
        workspace_id: str,
        data: BrandingUpdate,
    ) -> Optional[Branding]:
        """Update branding configuration."""
        branding = self._branding.get(workspace_id)
        if not branding:
            return None

        # Update fields
        if data.company_name is not None:
            branding.company_name = data.company_name
        if data.tagline is not None:
            branding.tagline = data.tagline
        if data.support_email is not None:
            branding.support_email = data.support_email
        if data.support_url is not None:
            branding.support_url = data.support_url
        if data.logo is not None:
            branding.logo = data.logo
        if data.primary_color is not None:
            branding.primary_color = data.primary_color
        if data.secondary_color is not None:
            branding.secondary_color = data.secondary_color
        if data.custom_domain is not None:
            branding.custom_domain = data.custom_domain
            branding.custom_domain_verified = False
        if data.footer_text is not None:
            branding.footer_text = data.footer_text
        if data.footer_links is not None:
            branding.footer_links = data.footer_links
        if data.privacy_policy_url is not None:
            branding.privacy_policy_url = data.privacy_policy_url
        if data.terms_of_service_url is not None:
            branding.terms_of_service_url = data.terms_of_service_url
        if data.social_links is not None:
            branding.social_links = data.social_links
        if data.email_from_name is not None:
            branding.email_from_name = data.email_from_name
        if data.email_from_address is not None:
            branding.email_from_address = data.email_from_address
        if data.hide_powered_by is not None:
            branding.hide_powered_by = data.hide_powered_by
        if data.theme_id is not None:
            branding.theme_id = data.theme_id

        branding.updated_at = datetime.utcnow()

        return branding

    async def delete_branding(self, workspace_id: str) -> bool:
        """Delete branding configuration."""
        if workspace_id in self._branding:
            del self._branding[workspace_id]
            return True
        return False

    async def verify_custom_domain(self, workspace_id: str) -> dict:
        """Verify custom domain configuration."""
        branding = self._branding.get(workspace_id)
        if not branding or not branding.custom_domain:
            raise ValueError("No custom domain configured")

        # In production, would verify DNS records
        return {
            "domain": branding.custom_domain,
            "verified": False,
            "instructions": [
                f"Add CNAME record pointing to dataviz.bheemkodee.com",
                "Wait for DNS propagation (up to 48 hours)",
                "Run verification again",
            ],
        }

    # User Preferences

    async def get_user_preferences(self, user_id: str) -> UserThemePreferences:
        """Get user theme preferences."""
        if user_id not in self._user_preferences:
            self._user_preferences[user_id] = UserThemePreferences(user_id=user_id)
        return self._user_preferences[user_id]

    async def update_user_preferences(
        self,
        user_id: str,
        mode: Optional[ThemeMode] = None,
        theme_id: Optional[str] = None,
        font_size: Optional[str] = None,
        reduce_motion: Optional[bool] = None,
        high_contrast: Optional[bool] = None,
    ) -> UserThemePreferences:
        """Update user theme preferences."""
        prefs = await self.get_user_preferences(user_id)

        if mode is not None:
            prefs.theme_mode = mode
        if theme_id is not None:
            prefs.preferred_theme_id = theme_id
        if font_size is not None:
            prefs.font_size = font_size
        if reduce_motion is not None:
            prefs.reduce_motion = reduce_motion
        if high_contrast is not None:
            prefs.high_contrast = high_contrast

        prefs.updated_at = datetime.utcnow()

        return prefs

    # Active Theme Resolution

    async def resolve_active_theme(
        self,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Theme:
        """Resolve the active theme based on user and workspace settings."""
        theme_id = None

        # Check user preference
        if user_id:
            prefs = await self.get_user_preferences(user_id)
            theme_id = prefs.preferred_theme_id

        # Check workspace branding
        if not theme_id and workspace_id:
            branding = self._branding.get(workspace_id)
            if branding and branding.theme_id:
                theme_id = branding.theme_id

        # Check workspace default
        if not theme_id and workspace_id:
            for theme in self._themes.values():
                if theme.workspace_id == workspace_id and theme.is_default:
                    theme_id = theme.id
                    break

        # Fall back to system default
        if not theme_id:
            theme_id = DEFAULT_LIGHT_THEME.id

        return self._themes.get(theme_id, DEFAULT_LIGHT_THEME)
