"""
Plugin Service

Business logic for plugin lifecycle management, hooks, and registry.
"""

from typing import Optional, Callable, Any
from datetime import datetime
from collections import defaultdict
import asyncio

from app.schemas.plugins import (
    PluginType,
    PluginStatus,
    HookType,
    PermissionScope,
    PluginManifest,
    PluginInstance,
    PluginInstall,
    PluginUpdate,
    RegistryPlugin,
    RegistrySearchResult,
    RegistrySearchQuery,
    HookContext,
    HookResult,
    HookChainResult,
    PluginEvent,
    PluginListResponse,
    PluginStatsResponse,
    PluginAuthor,
    PLUGIN_TYPE_ICONS,
    compare_versions,
    is_compatible,
)


class PluginService:
    """Service for plugin management."""

    def __init__(self, db=None):
        self.db = db

    # In-memory stores (production would use database)
    _plugins: dict[str, PluginInstance] = {}
    _registry: dict[str, RegistryPlugin] = {}
    _hooks: dict[HookType, list[tuple[str, Callable, int]]] = defaultdict(list)  # type -> [(plugin_id, handler, priority)]
    _events: list[PluginEvent] = []

    # Initialize with sample registry plugins
    @classmethod
    def _init_sample_registry(cls):
        """Initialize sample registry plugins."""
        if cls._registry:
            return

        sample_plugins = [
            {
                "id": "bheem-connector-snowflake",
                "name": "Snowflake Connector",
                "description": "Connect to Snowflake data warehouse",
                "type": PluginType.CONNECTOR,
                "version": "1.2.0",
                "downloads": 5420,
                "rating": 4.8,
                "verified": True,
                "featured": True,
            },
            {
                "id": "bheem-connector-bigquery",
                "name": "BigQuery Connector",
                "description": "Connect to Google BigQuery",
                "type": PluginType.CONNECTOR,
                "version": "1.1.0",
                "downloads": 4230,
                "rating": 4.7,
                "verified": True,
                "featured": True,
            },
            {
                "id": "bheem-viz-sankey",
                "name": "Advanced Sankey Charts",
                "description": "Interactive Sankey diagrams with animations",
                "type": PluginType.VISUALIZATION,
                "version": "2.0.0",
                "downloads": 3100,
                "rating": 4.9,
                "verified": True,
            },
            {
                "id": "bheem-export-powerpoint",
                "name": "PowerPoint Export",
                "description": "Export dashboards to PowerPoint presentations",
                "type": PluginType.EXPORT,
                "version": "1.0.5",
                "downloads": 2890,
                "rating": 4.5,
                "verified": True,
            },
            {
                "id": "bheem-auth-okta",
                "name": "Okta SSO",
                "description": "Single Sign-On with Okta",
                "type": PluginType.AUTH,
                "version": "1.3.0",
                "downloads": 1560,
                "rating": 4.6,
                "verified": True,
            },
            {
                "id": "bheem-theme-dark-pro",
                "name": "Dark Pro Theme",
                "description": "Professional dark theme with custom colors",
                "type": PluginType.THEME,
                "version": "1.1.0",
                "downloads": 8900,
                "rating": 4.9,
                "verified": False,
            },
            {
                "id": "bheem-widget-weather",
                "name": "Weather Widget",
                "description": "Display weather data on dashboards",
                "type": PluginType.WIDGET,
                "version": "1.0.0",
                "downloads": 1200,
                "rating": 4.2,
                "verified": False,
            },
            {
                "id": "bheem-integration-slack",
                "name": "Slack Integration",
                "description": "Send alerts and reports to Slack",
                "type": PluginType.INTEGRATION,
                "version": "2.1.0",
                "downloads": 4500,
                "rating": 4.7,
                "verified": True,
                "featured": True,
            },
            {
                "id": "bheem-ai-forecast",
                "name": "AI Forecasting",
                "description": "Machine learning-based time series forecasting",
                "type": PluginType.AI,
                "version": "1.5.0",
                "downloads": 2100,
                "rating": 4.4,
                "verified": True,
            },
            {
                "id": "bheem-transform-pivot",
                "name": "Advanced Pivot",
                "description": "Advanced pivot table transformations",
                "type": PluginType.TRANSFORM,
                "version": "1.2.0",
                "downloads": 1800,
                "rating": 4.3,
                "verified": False,
            },
        ]

        for p in sample_plugins:
            manifest = PluginManifest(
                id=p["id"],
                name=p["name"],
                version=p["version"],
                description=p["description"],
                type=p["type"],
                author=PluginAuthor(name="Bheem Team", email="plugins@bheem.co.uk"),
                icon=PLUGIN_TYPE_ICONS.get(p["type"]),
                keywords=[p["type"].value],
            )

            cls._registry[p["id"]] = RegistryPlugin(
                id=p["id"],
                manifest=manifest,
                downloads=p["downloads"],
                rating=p["rating"],
                reviews_count=p["downloads"] // 20,
                verified=p.get("verified", False),
                featured=p.get("featured", False),
                versions=[p["version"]],
                latest_version=p["version"],
                published_at=datetime.utcnow(),
            )

    # Plugin Lifecycle

    async def install_plugin(
        self,
        user_id: str,
        data: PluginInstall,
    ) -> PluginInstance:
        """Install a plugin from the registry."""
        self._init_sample_registry()

        # Get from registry
        registry_plugin = self._registry.get(data.plugin_id)
        if not registry_plugin:
            raise ValueError(f"Plugin {data.plugin_id} not found in registry")

        # Check if already installed
        if data.plugin_id in self._plugins:
            existing = self._plugins[data.plugin_id]
            if existing.status != PluginStatus.ERROR:
                raise ValueError(f"Plugin {data.plugin_id} is already installed")

        version = data.version or registry_plugin.latest_version
        now = datetime.utcnow()

        # Create instance
        instance = PluginInstance(
            id=data.plugin_id,
            manifest=registry_plugin.manifest,
            status=PluginStatus.INSTALLED,
            installed_at=now,
            installed_by=user_id,
            version_installed=version,
            config=data.config,
            workspace_id=data.workspace_id,
        )

        # Store
        self._plugins[data.plugin_id] = instance

        # Log event
        await self._log_event(data.plugin_id, "installed", user_id, {"version": version})

        # Auto-enable if requested
        if data.enable_after_install:
            await self.enable_plugin(data.plugin_id, user_id)

        return instance

    async def uninstall_plugin(
        self,
        plugin_id: str,
        user_id: str,
    ) -> bool:
        """Uninstall a plugin."""
        instance = self._plugins.get(plugin_id)
        if not instance:
            return False

        # Disable first if enabled
        if instance.status == PluginStatus.ENABLED:
            await self.disable_plugin(plugin_id, user_id)

        # Run uninstall hook
        await self._run_lifecycle_hook(plugin_id, HookType.ON_UNINSTALL)

        # Remove hooks
        self._remove_plugin_hooks(plugin_id)

        # Remove from store
        del self._plugins[plugin_id]

        # Log event
        await self._log_event(plugin_id, "uninstalled", user_id)

        return True

    async def enable_plugin(
        self,
        plugin_id: str,
        user_id: str,
    ) -> PluginInstance:
        """Enable a plugin."""
        instance = self._plugins.get(plugin_id)
        if not instance:
            raise ValueError(f"Plugin {plugin_id} not found")

        if instance.status == PluginStatus.ENABLED:
            return instance

        try:
            # Run enable hook
            await self._run_lifecycle_hook(plugin_id, HookType.ON_ENABLE)

            # Register hooks
            self._register_plugin_hooks(instance)

            # Update status
            instance.status = PluginStatus.ENABLED
            instance.enabled_at = datetime.utcnow()
            instance.last_error = None

            # Log event
            await self._log_event(plugin_id, "enabled", user_id)

        except Exception as e:
            instance.status = PluginStatus.ERROR
            instance.last_error = str(e)
            instance.error_count += 1
            raise

        return instance

    async def disable_plugin(
        self,
        plugin_id: str,
        user_id: str,
    ) -> PluginInstance:
        """Disable a plugin."""
        instance = self._plugins.get(plugin_id)
        if not instance:
            raise ValueError(f"Plugin {plugin_id} not found")

        if instance.status != PluginStatus.ENABLED:
            return instance

        try:
            # Run disable hook
            await self._run_lifecycle_hook(plugin_id, HookType.ON_DISABLE)

            # Remove hooks
            self._remove_plugin_hooks(plugin_id)

            # Update status
            instance.status = PluginStatus.DISABLED
            instance.disabled_at = datetime.utcnow()

            # Log event
            await self._log_event(plugin_id, "disabled", user_id)

        except Exception as e:
            instance.last_error = str(e)
            raise

        return instance

    async def update_plugin(
        self,
        plugin_id: str,
        user_id: str,
        data: PluginUpdate,
    ) -> PluginInstance:
        """Update plugin configuration."""
        instance = self._plugins.get(plugin_id)
        if not instance:
            raise ValueError(f"Plugin {plugin_id} not found")

        if data.config is not None:
            instance.config.update(data.config)

        if data.enabled_workspaces is not None:
            instance.enabled_workspaces = data.enabled_workspaces

        instance.updated_at = datetime.utcnow()

        # Log event
        await self._log_event(plugin_id, "updated", user_id)

        return instance

    async def update_plugin_version(
        self,
        plugin_id: str,
        user_id: str,
        target_version: Optional[str] = None,
    ) -> PluginInstance:
        """Update plugin to a new version."""
        self._init_sample_registry()

        instance = self._plugins.get(plugin_id)
        if not instance:
            raise ValueError(f"Plugin {plugin_id} not found")

        registry_plugin = self._registry.get(plugin_id)
        if not registry_plugin:
            raise ValueError(f"Plugin {plugin_id} not in registry")

        version = target_version or registry_plugin.latest_version

        if version == instance.version_installed:
            return instance

        was_enabled = instance.status == PluginStatus.ENABLED

        # Disable if enabled
        if was_enabled:
            await self.disable_plugin(plugin_id, user_id)

        # Update version
        instance.status = PluginStatus.UPDATING
        instance.version_installed = version
        instance.manifest = registry_plugin.manifest
        instance.updated_at = datetime.utcnow()

        # Run update hook
        await self._run_lifecycle_hook(plugin_id, HookType.ON_UPDATE)

        instance.status = PluginStatus.INSTALLED

        # Re-enable if was enabled
        if was_enabled:
            await self.enable_plugin(plugin_id, user_id)

        # Log event
        await self._log_event(plugin_id, "version_updated", user_id, {"version": version})

        return instance

    # Plugin Queries

    async def get_plugin(self, plugin_id: str) -> Optional[PluginInstance]:
        """Get a plugin by ID."""
        return self._plugins.get(plugin_id)

    async def list_plugins(
        self,
        workspace_id: Optional[str] = None,
        plugin_type: Optional[PluginType] = None,
        status: Optional[PluginStatus] = None,
    ) -> PluginListResponse:
        """List installed plugins."""
        plugins = list(self._plugins.values())

        if workspace_id:
            plugins = [
                p for p in plugins
                if p.workspace_id is None or p.workspace_id == workspace_id
            ]

        if plugin_type:
            plugins = [p for p in plugins if p.manifest.type == plugin_type]

        if status:
            plugins = [p for p in plugins if p.status == status]

        return PluginListResponse(plugins=plugins, total=len(plugins))

    async def get_plugin_stats(self) -> PluginStatsResponse:
        """Get plugin statistics."""
        plugins = list(self._plugins.values())

        by_type: dict[str, int] = defaultdict(int)
        by_status: dict[str, int] = defaultdict(int)

        for p in plugins:
            by_type[p.manifest.type.value] += 1
            by_status[p.status.value] += 1

        total_hooks = sum(len(hooks) for hooks in self._hooks.values())

        recent_errors = [
            {
                "plugin_id": p.id,
                "error": p.last_error,
                "timestamp": p.updated_at or p.installed_at,
            }
            for p in plugins
            if p.last_error
        ][:10]

        return PluginStatsResponse(
            total_installed=len(plugins),
            total_enabled=len([p for p in plugins if p.status == PluginStatus.ENABLED]),
            by_type=dict(by_type),
            by_status=dict(by_status),
            total_hooks_registered=total_hooks,
            recent_errors=recent_errors,
        )

    # Registry

    async def search_registry(
        self,
        query: RegistrySearchQuery,
    ) -> RegistrySearchResult:
        """Search the plugin registry."""
        self._init_sample_registry()

        plugins = list(self._registry.values())

        # Filter by query
        if query.query:
            q = query.query.lower()
            plugins = [
                p for p in plugins
                if q in p.manifest.name.lower()
                or q in p.manifest.description.lower()
                or any(q in kw.lower() for kw in p.manifest.keywords)
            ]

        # Filter by type
        if query.type:
            plugins = [p for p in plugins if p.manifest.type == query.type]

        # Filter by keywords
        if query.keywords:
            plugins = [
                p for p in plugins
                if any(kw in p.manifest.keywords for kw in query.keywords)
            ]

        # Filter verified only
        if query.verified_only:
            plugins = [p for p in plugins if p.verified]

        # Sort
        if query.sort_by == "downloads":
            plugins.sort(key=lambda p: p.downloads, reverse=True)
        elif query.sort_by == "rating":
            plugins.sort(key=lambda p: p.rating, reverse=True)
        elif query.sort_by == "updated":
            plugins.sort(key=lambda p: p.updated_at or p.published_at, reverse=True)
        elif query.sort_by == "name":
            plugins.sort(key=lambda p: p.manifest.name.lower())

        # Pagination
        total = len(plugins)
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        plugins = plugins[start:end]

        return RegistrySearchResult(
            plugins=plugins,
            total=total,
            page=query.page,
            page_size=query.page_size,
            has_more=end < total,
        )

    async def get_registry_plugin(self, plugin_id: str) -> Optional[RegistryPlugin]:
        """Get a plugin from the registry."""
        self._init_sample_registry()
        return self._registry.get(plugin_id)

    async def get_featured_plugins(self, limit: int = 5) -> list[RegistryPlugin]:
        """Get featured plugins."""
        self._init_sample_registry()
        featured = [p for p in self._registry.values() if p.featured]
        return sorted(featured, key=lambda p: p.downloads, reverse=True)[:limit]

    # Hook Management

    def _register_plugin_hooks(self, instance: PluginInstance) -> None:
        """Register hooks for a plugin."""
        for hook in instance.manifest.hooks:
            # Create placeholder handler (in production, would load actual handler)
            async def handler(ctx: HookContext) -> dict:
                return {"plugin": instance.id, "hook": hook.type.value}

            self._hooks[hook.type].append((instance.id, handler, hook.priority))

        # Sort by priority
        for hook_type in self._hooks:
            self._hooks[hook_type].sort(key=lambda x: x[2])

    def _remove_plugin_hooks(self, plugin_id: str) -> None:
        """Remove all hooks for a plugin."""
        for hook_type in self._hooks:
            self._hooks[hook_type] = [
                h for h in self._hooks[hook_type]
                if h[0] != plugin_id
            ]

    async def execute_hooks(
        self,
        hook_type: HookType,
        context: HookContext,
    ) -> HookChainResult:
        """Execute all hooks of a type in order."""
        results = []
        data = context.data.copy()
        start_time = datetime.utcnow()

        for plugin_id, handler, _ in self._hooks.get(hook_type, []):
            hook_start = datetime.utcnow()
            try:
                ctx = HookContext(
                    hook_type=hook_type,
                    plugin_id=plugin_id,
                    user_id=context.user_id,
                    workspace_id=context.workspace_id,
                    resource_type=context.resource_type,
                    resource_id=context.resource_id,
                    data=data,
                    metadata=context.metadata,
                )

                result_data = await handler(ctx)
                if result_data:
                    data.update(result_data)

                results.append(HookResult(
                    plugin_id=plugin_id,
                    hook_type=hook_type,
                    success=True,
                    data=result_data,
                    execution_time_ms=int((datetime.utcnow() - hook_start).total_seconds() * 1000),
                ))

            except Exception as e:
                results.append(HookResult(
                    plugin_id=plugin_id,
                    hook_type=hook_type,
                    success=False,
                    error=str(e),
                    execution_time_ms=int((datetime.utcnow() - hook_start).total_seconds() * 1000),
                ))

        total_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return HookChainResult(
            hook_type=hook_type,
            results=results,
            final_data=data,
            total_time_ms=total_time,
            any_failed=any(not r.success for r in results),
        )

    async def _run_lifecycle_hook(self, plugin_id: str, hook_type: HookType) -> None:
        """Run a lifecycle hook for a plugin."""
        instance = self._plugins.get(plugin_id)
        if not instance:
            return

        # Find matching hook
        for hook in instance.manifest.hooks:
            if hook.type == hook_type:
                # In production, would execute actual handler
                break

    # Events

    async def _log_event(
        self,
        plugin_id: str,
        event_type: str,
        user_id: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Log a plugin event."""
        import uuid

        event = PluginEvent(
            id=str(uuid.uuid4()),
            plugin_id=plugin_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            details=details or {},
        )

        self._events.append(event)

        # Keep only recent events
        if len(self._events) > 1000:
            self._events = self._events[-500:]

    async def get_plugin_events(
        self,
        plugin_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[PluginEvent]:
        """Get plugin events."""
        events = self._events

        if plugin_id:
            events = [e for e in events if e.plugin_id == plugin_id]

        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]

    # Check Available Updates

    async def check_updates(self) -> list[dict]:
        """Check for available plugin updates."""
        self._init_sample_registry()

        updates = []
        for instance in self._plugins.values():
            registry_plugin = self._registry.get(instance.id)
            if registry_plugin:
                if compare_versions(registry_plugin.latest_version, instance.version_installed) > 0:
                    updates.append({
                        "plugin_id": instance.id,
                        "current_version": instance.version_installed,
                        "latest_version": registry_plugin.latest_version,
                        "plugin_name": instance.manifest.name,
                    })

        return updates
