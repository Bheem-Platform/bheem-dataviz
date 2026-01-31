"""
Shortcuts & Command Palette Service

Handles keyboard shortcuts, command palette, and user preferences.
"""

import uuid
from typing import Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.shortcuts import (
    CommandCategory,
    ActionType,
    ShortcutScope,
    KeyBinding,
    ShortcutAction,
    Shortcut,
    ShortcutOverride,
    Command,
    CommandIcon,
    CommandGroup,
    ShortcutPreferences,
    RecentCommand,
    CommandHistory,
    CommandSearchResult,
    CommandSearchResponse,
    DEFAULT_SHORTCUTS,
    format_key_binding,
    fuzzy_match,
)


logger = logging.getLogger(__name__)


class ShortcutsService:
    """Service for keyboard shortcuts and command palette."""

    def __init__(self, db: AsyncSession):
        self.db = db
        # In-memory stores (production would use database)
        self._user_preferences: dict[str, dict] = {}  # user_id -> preferences
        self._command_history: dict[str, dict] = {}  # user_id -> history
        self._shortcuts = {s.id: s for s in DEFAULT_SHORTCUTS}

    # Shortcuts Management

    async def get_shortcuts(
        self,
        user_id: Optional[str] = None,
        scope: Optional[ShortcutScope] = None,
        category: Optional[CommandCategory] = None,
    ) -> list[Shortcut]:
        """Get all shortcuts, optionally filtered and with user overrides applied."""
        shortcuts = list(self._shortcuts.values())

        # Apply user overrides
        if user_id:
            prefs = await self.get_user_preferences(user_id)
            shortcuts = self._apply_overrides(shortcuts, prefs)

        # Filter by scope
        if scope:
            shortcuts = [s for s in shortcuts if s.scope == scope or s.scope == ShortcutScope.GLOBAL]

        # Filter by category
        if category:
            shortcuts = [s for s in shortcuts if s.category == category]

        # Filter out disabled
        shortcuts = [s for s in shortcuts if s.enabled]

        return shortcuts

    async def get_shortcut(self, shortcut_id: str) -> Optional[Shortcut]:
        """Get a single shortcut by ID."""
        return self._shortcuts.get(shortcut_id)

    async def create_custom_shortcut(
        self,
        user_id: str,
        shortcut: Shortcut,
    ) -> Shortcut:
        """Create a custom shortcut for a user."""
        prefs = await self.get_user_preferences(user_id)
        prefs_dict = prefs.model_dump()

        # Add custom shortcut
        shortcut.is_default = False
        shortcut.is_customizable = True
        prefs_dict["custom_shortcuts"].append(shortcut.model_dump())
        prefs_dict["updated_at"] = datetime.utcnow()

        self._user_preferences[user_id] = prefs_dict
        return shortcut

    async def override_shortcut(
        self,
        user_id: str,
        override: ShortcutOverride,
    ) -> Optional[Shortcut]:
        """Override a default shortcut."""
        if override.shortcut_id not in self._shortcuts:
            return None

        prefs = await self.get_user_preferences(user_id)
        prefs_dict = prefs.model_dump()

        # Check if override exists
        existing_idx = next(
            (i for i, o in enumerate(prefs_dict["overrides"]) if o["shortcut_id"] == override.shortcut_id),
            None
        )

        if existing_idx is not None:
            prefs_dict["overrides"][existing_idx] = override.model_dump()
        else:
            prefs_dict["overrides"].append(override.model_dump())

        prefs_dict["updated_at"] = datetime.utcnow()
        self._user_preferences[user_id] = prefs_dict

        # Return the modified shortcut
        shortcut = self._shortcuts[override.shortcut_id].model_copy()
        if override.key_binding:
            shortcut.key_binding = override.key_binding
        if override.enabled is not None:
            shortcut.enabled = override.enabled

        return shortcut

    async def reset_shortcut(
        self,
        user_id: str,
        shortcut_id: str,
    ) -> Optional[Shortcut]:
        """Reset a shortcut to its default."""
        prefs = await self.get_user_preferences(user_id)
        prefs_dict = prefs.model_dump()

        # Remove override
        prefs_dict["overrides"] = [
            o for o in prefs_dict["overrides"]
            if o["shortcut_id"] != shortcut_id
        ]

        # Remove from disabled list
        prefs_dict["disabled_shortcuts"] = [
            s for s in prefs_dict["disabled_shortcuts"]
            if s != shortcut_id
        ]

        prefs_dict["updated_at"] = datetime.utcnow()
        self._user_preferences[user_id] = prefs_dict

        return self._shortcuts.get(shortcut_id)

    async def reset_all_shortcuts(self, user_id: str) -> bool:
        """Reset all shortcuts to defaults."""
        if user_id in self._user_preferences:
            prefs = self._user_preferences[user_id]
            prefs["overrides"] = []
            prefs["disabled_shortcuts"] = []
            prefs["custom_shortcuts"] = []
            prefs["updated_at"] = datetime.utcnow()
        return True

    def _apply_overrides(
        self,
        shortcuts: list[Shortcut],
        prefs: ShortcutPreferences,
    ) -> list[Shortcut]:
        """Apply user overrides to shortcuts."""
        override_map = {o.shortcut_id: o for o in prefs.overrides}
        disabled = set(prefs.disabled_shortcuts)

        result = []
        for shortcut in shortcuts:
            if shortcut.id in disabled:
                continue

            s = shortcut.model_copy()
            if shortcut.id in override_map:
                override = override_map[shortcut.id]
                if override.key_binding:
                    s.key_binding = override.key_binding
                if override.enabled is not None:
                    s.enabled = override.enabled

            result.append(s)

        # Add custom shortcuts
        for custom in prefs.custom_shortcuts:
            result.append(Shortcut(**custom))

        return result

    # User Preferences

    async def get_user_preferences(self, user_id: str) -> ShortcutPreferences:
        """Get user's shortcut preferences."""
        prefs = self._user_preferences.get(user_id)
        if prefs:
            return ShortcutPreferences(**prefs)

        # Return defaults
        return ShortcutPreferences(user_id=user_id)

    async def update_user_preferences(
        self,
        user_id: str,
        updates: dict[str, Any],
    ) -> ShortcutPreferences:
        """Update user's shortcut preferences."""
        prefs = await self.get_user_preferences(user_id)
        prefs_dict = prefs.model_dump()

        for key, value in updates.items():
            if key in prefs_dict and key != "user_id":
                prefs_dict[key] = value

        prefs_dict["updated_at"] = datetime.utcnow()
        self._user_preferences[user_id] = prefs_dict

        return ShortcutPreferences(**prefs_dict)

    # Command Palette

    async def get_commands(
        self,
        user_id: Optional[str] = None,
        category: Optional[CommandCategory] = None,
        include_recent: bool = True,
    ) -> list[CommandGroup]:
        """Get all commands grouped by category."""
        # Get shortcuts and convert to commands
        shortcuts = await self.get_shortcuts(user_id)

        # Get user history for recent/favorites
        history = await self.get_command_history(user_id) if user_id else None

        # Build commands from shortcuts
        commands: list[Command] = []
        for shortcut in shortcuts:
            command = Command(
                id=f"shortcut:{shortcut.id}",
                title=shortcut.name,
                description=shortcut.description,
                category=shortcut.category,
                keywords=[shortcut.name.lower()],
                action=shortcut.action,
                shortcut=shortcut.key_binding,
            )

            # Add recent/favorite info from history
            if history:
                command.use_count = history.command_counts.get(command.id, 0)
                command.is_favorite = command.id in history.favorite_commands
                recent = next(
                    (r for r in history.recent_commands if r.command_id == command.id),
                    None
                )
                if recent:
                    command.is_recent = True
                    command.last_used = recent.used_at

            commands.append(command)

        # Add dynamic commands
        commands.extend(await self._get_dynamic_commands(user_id))

        # Filter by category
        if category:
            commands = [c for c in commands if c.category == category]

        # Group by category
        groups: dict[CommandCategory, list[Command]] = {}
        for cmd in commands:
            if cmd.category not in groups:
                groups[cmd.category] = []
            groups[cmd.category].append(cmd)

        # Build command groups
        category_order = [
            CommandCategory.RECENT,
            CommandCategory.FAVORITE,
            CommandCategory.NAVIGATION,
            CommandCategory.DASHBOARD,
            CommandCategory.CHART,
            CommandCategory.DATA,
            CommandCategory.EDIT,
            CommandCategory.VIEW,
            CommandCategory.HELP,
            CommandCategory.SYSTEM,
        ]

        result = []

        # Add recent commands group
        if include_recent and history and history.recent_commands:
            recent_cmds = [
                c for c in commands
                if c.is_recent
            ][:10]
            if recent_cmds:
                result.append(CommandGroup(
                    id="recent",
                    name="Recent",
                    commands=recent_cmds,
                    priority=100,
                ))

        # Add other groups
        for cat in category_order:
            if cat in groups and cat not in [CommandCategory.RECENT, CommandCategory.FAVORITE]:
                result.append(CommandGroup(
                    id=cat.value,
                    name=cat.value.replace("_", " ").title(),
                    commands=groups[cat],
                    priority=category_order.index(cat),
                ))

        return result

    async def search_commands(
        self,
        query: str,
        user_id: Optional[str] = None,
        category: Optional[CommandCategory] = None,
        limit: int = 20,
    ) -> CommandSearchResponse:
        """Search commands by query."""
        groups = await self.get_commands(user_id, category, include_recent=False)

        # Flatten commands
        all_commands = []
        for group in groups:
            all_commands.extend(group.commands)

        # Search
        results: list[CommandSearchResult] = []
        for cmd in all_commands:
            # Match against title
            matched, score, positions = fuzzy_match(query, cmd.title)
            if matched:
                results.append(CommandSearchResult(
                    command=cmd,
                    match_type="title",
                    match_positions=positions,
                    score=score + cmd.use_count * 0.1,  # Boost by usage
                ))
                continue

            # Match against description
            if cmd.description:
                matched, score, positions = fuzzy_match(query, cmd.description)
                if matched:
                    results.append(CommandSearchResult(
                        command=cmd,
                        match_type="description",
                        match_positions=positions,
                        score=score * 0.8,  # Lower score for description match
                    ))
                    continue

            # Match against keywords
            for keyword in cmd.keywords:
                matched, score, positions = fuzzy_match(query, keyword)
                if matched:
                    results.append(CommandSearchResult(
                        command=cmd,
                        match_type="keyword",
                        match_positions=[],
                        score=score * 0.7,
                    ))
                    break

        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        results = results[:limit]

        # Generate suggestions
        suggestions = []
        if len(results) < 3 and len(query) > 2:
            common_terms = ["dashboard", "chart", "create", "new", "search", "settings"]
            suggestions = [t for t in common_terms if query.lower() in t][:3]

        return CommandSearchResponse(
            results=results,
            total=len(results),
            query=query,
            suggestions=suggestions,
        )

    async def execute_command(
        self,
        command_id: str,
        user_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Record command execution and return the action."""
        # Record in history
        if user_id:
            await self._record_command_use(user_id, command_id, context)

        # Get the command
        groups = await self.get_commands(user_id)
        for group in groups:
            for cmd in group.commands:
                if cmd.id == command_id:
                    return {
                        "action": cmd.action.model_dump(),
                        "command": cmd.model_dump(),
                    }

        return {"error": "Command not found"}

    async def _get_dynamic_commands(self, user_id: Optional[str]) -> list[Command]:
        """Get dynamic commands (recent items, etc.)."""
        # In production, fetch recent dashboards, charts, etc. from database
        return []

    # Command History

    async def get_command_history(self, user_id: str) -> CommandHistory:
        """Get user's command history."""
        history = self._command_history.get(user_id)
        if history:
            return CommandHistory(**history)

        return CommandHistory(user_id=user_id)

    async def _record_command_use(
        self,
        user_id: str,
        command_id: str,
        context: Optional[dict] = None,
    ):
        """Record a command use in history."""
        history = await self.get_command_history(user_id)
        history_dict = history.model_dump()

        # Add to recent
        recent_entry = RecentCommand(
            command_id=command_id,
            used_at=datetime.utcnow(),
            context=context,
        )

        # Remove existing entry for this command
        history_dict["recent_commands"] = [
            r for r in history_dict["recent_commands"]
            if r["command_id"] != command_id
        ]

        # Add to front
        history_dict["recent_commands"].insert(0, recent_entry.model_dump())

        # Trim to max length
        history_dict["recent_commands"] = history_dict["recent_commands"][:50]

        # Update count
        history_dict["command_counts"][command_id] = history_dict["command_counts"].get(command_id, 0) + 1

        self._command_history[user_id] = history_dict

    async def add_favorite(self, user_id: str, command_id: str) -> bool:
        """Add a command to favorites."""
        history = await self.get_command_history(user_id)
        history_dict = history.model_dump()

        if command_id not in history_dict["favorite_commands"]:
            history_dict["favorite_commands"].append(command_id)
            history_dict["favorite_commands"] = history_dict["favorite_commands"][:20]

        self._command_history[user_id] = history_dict
        return True

    async def remove_favorite(self, user_id: str, command_id: str) -> bool:
        """Remove a command from favorites."""
        history = await self.get_command_history(user_id)
        history_dict = history.model_dump()

        history_dict["favorite_commands"] = [
            c for c in history_dict["favorite_commands"]
            if c != command_id
        ]

        self._command_history[user_id] = history_dict
        return True

    async def clear_history(self, user_id: str) -> bool:
        """Clear command history."""
        if user_id in self._command_history:
            history = self._command_history[user_id]
            history["recent_commands"] = []
            history["command_counts"] = {}
        return True

    # Shortcut Categories

    async def get_shortcut_categories(self) -> list[dict[str, Any]]:
        """Get all shortcut categories with counts."""
        categories = {}
        for shortcut in self._shortcuts.values():
            cat = shortcut.category.value
            if cat not in categories:
                categories[cat] = {
                    "id": cat,
                    "name": cat.replace("_", " ").title(),
                    "count": 0,
                }
            categories[cat]["count"] += 1

        return list(categories.values())
