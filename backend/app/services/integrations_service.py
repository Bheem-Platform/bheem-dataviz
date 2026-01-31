"""
External Integrations Service

Business logic for managing webhooks, notification channels, Git integration,
dbt projects, and other external integrations.
"""

import uuid
import json
import hashlib
import hmac
import httpx
from datetime import datetime, timedelta
from typing import Optional, Any

from app.schemas.integrations import (
    IntegrationType,
    IntegrationStatus,
    WebhookEventType,
    WebhookMethod,
    GitProvider,
    GitSyncDirection,
    DbtRunCommand,
    Webhook,
    WebhookCreate,
    WebhookUpdate,
    WebhookConfig,
    WebhookDelivery,
    WebhookTest,
    NotificationChannel,
    NotificationChannelCreate,
    NotificationChannelConfig,
    SlackConfig,
    TeamsConfig,
    DiscordConfig,
    NotificationMessage,
    GitRepository,
    GitRepositoryCreate,
    GitRepositoryUpdate,
    GitCommit,
    GitSyncResult,
    GitExportConfig,
    GitImportConfig,
    DbtProject,
    DbtProjectCreate,
    DbtModel,
    DbtRunRequest,
    DbtRunResult,
    DbtResourceType,
    OAuthConfig,
    OAuthToken,
    IntegrationInfo,
    IntegrationHub,
    WebhookListResponse,
    WebhookDeliveryListResponse,
    NotificationChannelListResponse,
    GitRepositoryListResponse,
    DbtProjectListResponse,
    AVAILABLE_INTEGRATIONS,
    ZAPIER_TRIGGERS,
    get_webhook_sample_payload,
    generate_webhook_signature,
)


class IntegrationsService:
    """Service for managing external integrations."""

    def __init__(self, db=None):
        self.db = db
        # In-memory stores (production would use database)
        self._webhooks: dict[str, Webhook] = {}
        self._webhook_deliveries: dict[str, list[WebhookDelivery]] = {}
        self._notification_channels: dict[str, NotificationChannel] = {}
        self._git_repositories: dict[str, GitRepository] = {}
        self._dbt_projects: dict[str, DbtProject] = {}
        self._dbt_run_results: dict[str, list[DbtRunResult]] = {}
        self._oauth_configs: dict[str, OAuthConfig] = {}
        self._oauth_tokens: dict[str, OAuthToken] = {}
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize sample integrations."""
        # Sample webhook
        webhook = Webhook(
            id="webhook_sample_001",
            name="Dashboard Update Webhook",
            description="Sends notifications when dashboards are updated",
            integration_type=IntegrationType.WEBHOOK,
            events=[WebhookEventType.DASHBOARD_UPDATED, WebhookEventType.DASHBOARD_PUBLISHED],
            config=WebhookConfig(
                url="https://hooks.example.com/dataviz",
                method=WebhookMethod.POST,
                headers={"X-Custom-Header": "DataViz"},
                timeout_seconds=30,
            ),
            status=IntegrationStatus.ACTIVE,
            created_by="00000000-0000-0000-0000-000000000000",
        )
        self._webhooks[webhook.id] = webhook

        # Sample Slack channel
        slack_channel = NotificationChannel(
            id="channel_slack_001",
            name="Sales Team Alerts",
            integration_type=IntegrationType.SLACK,
            config=NotificationChannelConfig(
                slack=SlackConfig(
                    webhook_url="https://hooks.slack.com/services/xxx/yyy/zzz",
                    channel="#sales-alerts",
                    username="Bheem DataViz",
                )
            ),
            status=IntegrationStatus.ACTIVE,
            created_by="00000000-0000-0000-0000-000000000000",
        )
        self._notification_channels[slack_channel.id] = slack_channel

        # Sample Git repository
        git_repo = GitRepository(
            id="repo_sample_001",
            name="DataViz Dashboards",
            description="Version controlled dashboards and queries",
            provider=GitProvider.GITHUB,
            url="https://github.com/example/dataviz-dashboards",
            branch="main",
            path_prefix="dashboards/",
            sync_direction=GitSyncDirection.BIDIRECTIONAL,
            auto_sync=True,
            sync_interval_minutes=30,
            status=IntegrationStatus.ACTIVE,
            created_by="00000000-0000-0000-0000-000000000000",
        )
        self._git_repositories[git_repo.id] = git_repo

        # Sample dbt project
        dbt_project = DbtProject(
            id="dbt_sample_001",
            name="Analytics Transforms",
            description="dbt project for data transformations",
            project_path="/projects/analytics",
            profile_name="dataviz",
            target_name="dev",
            version="1.0.0",
            status=IntegrationStatus.ACTIVE,
            created_by="00000000-0000-0000-0000-000000000000",
        )
        self._dbt_projects[dbt_project.id] = dbt_project

    # ==================== WEBHOOKS ====================

    async def list_webhooks(
        self,
        workspace_id: Optional[str] = None,
        integration_type: Optional[IntegrationType] = None,
        status: Optional[IntegrationStatus] = None,
    ) -> WebhookListResponse:
        """List webhooks with optional filters."""
        webhooks = list(self._webhooks.values())

        if workspace_id:
            webhooks = [w for w in webhooks if w.workspace_id == workspace_id]
        if integration_type:
            webhooks = [w for w in webhooks if w.integration_type == integration_type]
        if status:
            webhooks = [w for w in webhooks if w.status == status]

        return WebhookListResponse(webhooks=webhooks, total=len(webhooks))

    async def create_webhook(self, user_id: str, data: WebhookCreate) -> Webhook:
        """Create a new webhook."""
        webhook_id = f"webhook_{uuid.uuid4().hex[:12]}"

        webhook = Webhook(
            id=webhook_id,
            name=data.name,
            description=data.description,
            integration_type=data.integration_type,
            events=data.events,
            config=data.config,
            workspace_id=data.workspace_id,
            created_by=user_id,
        )

        self._webhooks[webhook_id] = webhook
        self._webhook_deliveries[webhook_id] = []
        return webhook

    async def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID."""
        return self._webhooks.get(webhook_id)

    async def update_webhook(self, webhook_id: str, data: WebhookUpdate) -> Optional[Webhook]:
        """Update a webhook."""
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            return None

        if data.name is not None:
            webhook.name = data.name
        if data.description is not None:
            webhook.description = data.description
        if data.events is not None:
            webhook.events = data.events
        if data.config is not None:
            webhook.config = data.config
        if data.status is not None:
            webhook.status = data.status

        webhook.updated_at = datetime.utcnow()
        return webhook

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            self._webhook_deliveries.pop(webhook_id, None)
            return True
        return False

    async def test_webhook(self, webhook_id: str, test: WebhookTest) -> WebhookDelivery:
        """Test a webhook with sample data."""
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            raise ValueError("Webhook not found")

        payload = test.sample_data or get_webhook_sample_payload(test.event_type)
        return await self._deliver_webhook(webhook, test.event_type, payload)

    async def trigger_webhook_event(self, event_type: WebhookEventType, data: dict[str, Any]):
        """Trigger webhooks for an event."""
        for webhook in self._webhooks.values():
            if webhook.status == IntegrationStatus.ACTIVE and event_type in webhook.events:
                try:
                    await self._deliver_webhook(webhook, event_type, data)
                except Exception as e:
                    webhook.failure_count += 1
                    webhook.last_error = str(e)

    async def _deliver_webhook(
        self, webhook: Webhook, event_type: WebhookEventType, data: dict[str, Any]
    ) -> WebhookDelivery:
        """Deliver a webhook payload."""
        delivery_id = f"delivery_{uuid.uuid4().hex[:12]}"
        started_at = datetime.utcnow()

        payload = {
            "event": event_type.value,
            "timestamp": started_at.isoformat(),
            "data": data,
        }
        payload_str = json.dumps(payload)

        headers = dict(webhook.config.headers)
        headers["Content-Type"] = "application/json"
        headers["X-DataViz-Event"] = event_type.value
        headers["X-DataViz-Delivery"] = delivery_id

        if webhook.config.secret:
            signature = generate_webhook_signature(payload_str, webhook.config.secret)
            headers["X-DataViz-Signature"] = f"sha256={signature}"

        # Simulate delivery (in production, use httpx)
        delivery = WebhookDelivery(
            id=delivery_id,
            webhook_id=webhook.id,
            event_type=event_type,
            payload=payload,
            response_status=200,
            response_body='{"ok": true}',
            duration_ms=150,
            success=True,
            attempt_number=1,
            delivered_at=datetime.utcnow(),
        )

        # Update webhook stats
        webhook.trigger_count += 1
        webhook.last_triggered_at = datetime.utcnow()

        # Store delivery
        if webhook.id not in self._webhook_deliveries:
            self._webhook_deliveries[webhook.id] = []
        self._webhook_deliveries[webhook.id].append(delivery)

        return delivery

    async def get_webhook_deliveries(
        self, webhook_id: str, limit: int = 50
    ) -> WebhookDeliveryListResponse:
        """Get webhook delivery history."""
        deliveries = self._webhook_deliveries.get(webhook_id, [])
        deliveries = sorted(deliveries, key=lambda d: d.delivered_at, reverse=True)[:limit]
        return WebhookDeliveryListResponse(deliveries=deliveries, total=len(deliveries))

    # ==================== NOTIFICATION CHANNELS ====================

    async def list_notification_channels(
        self,
        workspace_id: Optional[str] = None,
        integration_type: Optional[IntegrationType] = None,
    ) -> NotificationChannelListResponse:
        """List notification channels."""
        channels = list(self._notification_channels.values())

        if workspace_id:
            channels = [c for c in channels if c.workspace_id == workspace_id]
        if integration_type:
            channels = [c for c in channels if c.integration_type == integration_type]

        return NotificationChannelListResponse(channels=channels, total=len(channels))

    async def create_notification_channel(
        self, user_id: str, data: NotificationChannelCreate
    ) -> NotificationChannel:
        """Create a notification channel."""
        channel_id = f"channel_{uuid.uuid4().hex[:12]}"

        channel = NotificationChannel(
            id=channel_id,
            name=data.name,
            integration_type=data.integration_type,
            config=data.config,
            workspace_id=data.workspace_id,
            created_by=user_id,
        )

        self._notification_channels[channel_id] = channel
        return channel

    async def get_notification_channel(self, channel_id: str) -> Optional[NotificationChannel]:
        """Get notification channel by ID."""
        return self._notification_channels.get(channel_id)

    async def delete_notification_channel(self, channel_id: str) -> bool:
        """Delete a notification channel."""
        if channel_id in self._notification_channels:
            del self._notification_channels[channel_id]
            return True
        return False

    async def send_notification(
        self, channel_id: str, message: NotificationMessage
    ) -> dict[str, Any]:
        """Send notification through a channel."""
        channel = self._notification_channels.get(channel_id)
        if not channel:
            raise ValueError("Channel not found")

        result = {"success": False, "channel_id": channel_id}

        if channel.integration_type == IntegrationType.SLACK:
            result = await self._send_slack_notification(channel.config.slack, message)
        elif channel.integration_type == IntegrationType.TEAMS:
            result = await self._send_teams_notification(channel.config.teams, message)
        elif channel.integration_type == IntegrationType.DISCORD:
            result = await self._send_discord_notification(channel.config.discord, message)

        if result.get("success"):
            channel.message_count += 1
            channel.last_used_at = datetime.utcnow()

        return result

    async def _send_slack_notification(
        self, config: SlackConfig, message: NotificationMessage
    ) -> dict[str, Any]:
        """Send Slack notification."""
        # Simulate sending (in production, use httpx)
        payload = {
            "username": config.username,
            "icon_emoji": config.icon_emoji,
            "text": message.title,
            "attachments": [
                {
                    "color": message.color or "#3B82F6",
                    "text": message.message,
                    "fields": [{"title": f["title"], "value": f["value"], "short": True} for f in message.fields],
                }
            ],
        }
        if config.channel:
            payload["channel"] = config.channel

        return {"success": True, "platform": "slack", "payload": payload}

    async def _send_teams_notification(
        self, config: TeamsConfig, message: NotificationMessage
    ) -> dict[str, Any]:
        """Send Microsoft Teams notification."""
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": config.theme_color.replace("#", ""),
            "summary": message.title,
            "sections": [
                {
                    "activityTitle": message.title,
                    "text": message.message,
                    "facts": [{"name": f["title"], "value": f["value"]} for f in message.fields],
                }
            ],
        }
        if message.url:
            payload["potentialAction"] = [{"@type": "OpenUri", "name": "View", "targets": [{"os": "default", "uri": message.url}]}]

        return {"success": True, "platform": "teams", "payload": payload}

    async def _send_discord_notification(
        self, config: DiscordConfig, message: NotificationMessage
    ) -> dict[str, Any]:
        """Send Discord notification."""
        payload = {
            "username": config.username,
            "embeds": [
                {
                    "title": message.title,
                    "description": message.message,
                    "color": int(message.color.replace("#", ""), 16) if message.color else 3447003,
                    "fields": [{"name": f["title"], "value": f["value"], "inline": True} for f in message.fields],
                }
            ],
        }
        if config.avatar_url:
            payload["avatar_url"] = config.avatar_url
        if message.image_url:
            payload["embeds"][0]["image"] = {"url": message.image_url}

        return {"success": True, "platform": "discord", "payload": payload}

    async def test_notification_channel(self, channel_id: str) -> dict[str, Any]:
        """Test a notification channel."""
        message = NotificationMessage(
            title="Test Notification",
            message="This is a test notification from Bheem DataViz.",
            color="#10B981",
            fields=[{"title": "Status", "value": "Success"}, {"title": "Time", "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}],
        )
        return await self.send_notification(channel_id, message)

    # ==================== GIT INTEGRATION ====================

    async def list_git_repositories(
        self,
        workspace_id: Optional[str] = None,
        provider: Optional[GitProvider] = None,
    ) -> GitRepositoryListResponse:
        """List Git repositories."""
        repos = list(self._git_repositories.values())

        if workspace_id:
            repos = [r for r in repos if r.workspace_id == workspace_id]
        if provider:
            repos = [r for r in repos if r.provider == provider]

        return GitRepositoryListResponse(repositories=repos, total=len(repos))

    async def create_git_repository(
        self, user_id: str, data: GitRepositoryCreate
    ) -> GitRepository:
        """Create a Git repository connection."""
        repo_id = f"repo_{uuid.uuid4().hex[:12]}"

        repo = GitRepository(
            id=repo_id,
            name=data.name,
            description=data.description,
            provider=data.provider,
            url=data.url,
            branch=data.branch,
            path_prefix=data.path_prefix,
            access_token=data.access_token,
            ssh_key_id=data.ssh_key_id,
            sync_direction=data.sync_direction,
            auto_sync=data.auto_sync,
            sync_interval_minutes=data.sync_interval_minutes,
            workspace_id=data.workspace_id,
            created_by=user_id,
        )

        self._git_repositories[repo_id] = repo
        return repo

    async def get_git_repository(self, repo_id: str) -> Optional[GitRepository]:
        """Get Git repository by ID."""
        return self._git_repositories.get(repo_id)

    async def update_git_repository(
        self, repo_id: str, data: GitRepositoryUpdate
    ) -> Optional[GitRepository]:
        """Update a Git repository."""
        repo = self._git_repositories.get(repo_id)
        if not repo:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(repo, field, value)

        repo.updated_at = datetime.utcnow()
        return repo

    async def delete_git_repository(self, repo_id: str) -> bool:
        """Delete a Git repository."""
        if repo_id in self._git_repositories:
            del self._git_repositories[repo_id]
            return True
        return False

    async def sync_git_repository(self, repo_id: str) -> GitSyncResult:
        """Sync a Git repository."""
        repo = self._git_repositories.get(repo_id)
        if not repo:
            raise ValueError("Repository not found")

        started_at = datetime.utcnow()

        # Simulate sync (in production, use GitPython or similar)
        result = GitSyncResult(
            repository_id=repo_id,
            direction=repo.sync_direction,
            success=True,
            commits=[
                GitCommit(
                    sha="abc123def456",
                    message="Update dashboard configuration",
                    author_name="DataViz System",
                    author_email="system@dataviz.bheem.co.uk",
                    timestamp=datetime.utcnow(),
                    files_changed=3,
                    additions=45,
                    deletions=12,
                )
            ],
            files_synced=3,
            conflicts=[],
            started_at=started_at,
            completed_at=datetime.utcnow(),
        )

        repo.last_sync_at = datetime.utcnow()
        repo.last_sync_commit = result.commits[0].sha if result.commits else None

        return result

    async def export_to_git(
        self, repo_id: str, config: GitExportConfig
    ) -> dict[str, Any]:
        """Export a resource to Git."""
        repo = self._git_repositories.get(repo_id)
        if not repo:
            raise ValueError("Repository not found")

        # Simulate export (in production, serialize resource and commit)
        return {
            "success": True,
            "repository_id": repo_id,
            "file_path": config.file_path,
            "format": config.format,
            "commit_sha": f"commit_{uuid.uuid4().hex[:8]}",
            "commit_message": config.commit_message or f"Export {config.resource_type} {config.resource_id}",
        }

    async def import_from_git(
        self, repo_id: str, config: GitImportConfig
    ) -> dict[str, Any]:
        """Import a resource from Git."""
        repo = self._git_repositories.get(repo_id)
        if not repo:
            raise ValueError("Repository not found")

        # Simulate import
        return {
            "success": True,
            "repository_id": repo_id,
            "file_path": config.file_path,
            "resource_type": config.resource_type,
            "resource_id": f"{config.resource_type}_{uuid.uuid4().hex[:8]}",
            "imported_at": datetime.utcnow().isoformat(),
        }

    # ==================== DBT INTEGRATION ====================

    async def list_dbt_projects(
        self, workspace_id: Optional[str] = None
    ) -> DbtProjectListResponse:
        """List dbt projects."""
        projects = list(self._dbt_projects.values())

        if workspace_id:
            projects = [p for p in projects if p.workspace_id == workspace_id]

        return DbtProjectListResponse(projects=projects, total=len(projects))

    async def create_dbt_project(
        self, user_id: str, data: DbtProjectCreate
    ) -> DbtProject:
        """Create a dbt project."""
        project_id = f"dbt_{uuid.uuid4().hex[:12]}"

        project = DbtProject(
            id=project_id,
            name=data.name,
            description=data.description,
            project_path=data.project_path,
            profile_name=data.profile_name,
            target_name=data.target_name,
            connection_id=data.connection_id,
            git_repository_id=data.git_repository_id,
            workspace_id=data.workspace_id,
            created_by=user_id,
        )

        self._dbt_projects[project_id] = project
        self._dbt_run_results[project_id] = []
        return project

    async def get_dbt_project(self, project_id: str) -> Optional[DbtProject]:
        """Get dbt project by ID."""
        return self._dbt_projects.get(project_id)

    async def delete_dbt_project(self, project_id: str) -> bool:
        """Delete a dbt project."""
        if project_id in self._dbt_projects:
            del self._dbt_projects[project_id]
            self._dbt_run_results.pop(project_id, None)
            return True
        return False

    async def run_dbt(self, project_id: str, request: DbtRunRequest) -> DbtRunResult:
        """Run dbt command."""
        project = self._dbt_projects.get(project_id)
        if not project:
            raise ValueError("Project not found")

        run_id = f"run_{uuid.uuid4().hex[:12]}"
        started_at = datetime.utcnow()

        # Simulate dbt run (in production, execute dbt CLI)
        result = DbtRunResult(
            id=run_id,
            project_id=project_id,
            command=request.command,
            status="success",
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=12.5,
            models_run=5 if request.command in [DbtRunCommand.RUN, DbtRunCommand.BUILD] else 0,
            models_success=5,
            models_error=0,
            models_skipped=0,
            tests_run=8 if request.command in [DbtRunCommand.TEST, DbtRunCommand.BUILD] else 0,
            tests_passed=7,
            tests_failed=0,
            tests_warned=1,
            logs=[
                f"Running dbt {request.command.value}...",
                "Found 5 models, 8 tests",
                "Completed successfully",
            ],
            artifacts={
                "manifest": {"nodes": 13, "sources": 2},
                "run_results": {"elapsed_time": 12.5},
            },
        )

        project.last_run_at = datetime.utcnow()
        project.last_run_status = result.status

        if project_id not in self._dbt_run_results:
            self._dbt_run_results[project_id] = []
        self._dbt_run_results[project_id].append(result)

        return result

    async def get_dbt_models(self, project_id: str) -> list[DbtModel]:
        """Get dbt models for a project."""
        project = self._dbt_projects.get(project_id)
        if not project:
            raise ValueError("Project not found")

        # Return sample models (in production, parse manifest.json)
        return [
            DbtModel(
                name="stg_orders",
                description="Staging model for orders",
                resource_type=DbtResourceType.MODEL,
                schema_name="staging",
                columns=[
                    {"name": "order_id", "type": "integer", "description": "Primary key"},
                    {"name": "customer_id", "type": "integer", "description": "Foreign key to customers"},
                    {"name": "order_date", "type": "date", "description": "Date of order"},
                ],
                depends_on=["source.raw_orders"],
                tags=["staging", "orders"],
                config={"materialized": "view"},
            ),
            DbtModel(
                name="fct_orders",
                description="Fact table for orders",
                resource_type=DbtResourceType.MODEL,
                schema_name="marts",
                columns=[
                    {"name": "order_id", "type": "integer", "description": "Primary key"},
                    {"name": "customer_id", "type": "integer", "description": "Customer reference"},
                    {"name": "total_amount", "type": "decimal", "description": "Order total"},
                ],
                depends_on=["stg_orders", "stg_customers"],
                tags=["marts", "orders"],
                config={"materialized": "table"},
            ),
        ]

    async def get_dbt_run_history(
        self, project_id: str, limit: int = 20
    ) -> list[DbtRunResult]:
        """Get dbt run history."""
        results = self._dbt_run_results.get(project_id, [])
        return sorted(results, key=lambda r: r.started_at, reverse=True)[:limit]

    # ==================== INTEGRATION HUB ====================

    async def get_integration_hub(
        self, workspace_id: Optional[str] = None
    ) -> IntegrationHub:
        """Get available integrations."""
        integrations = list(AVAILABLE_INTEGRATIONS)

        # Mark connected integrations
        for integration in integrations:
            if integration.type in [IntegrationType.SLACK, IntegrationType.TEAMS, IntegrationType.DISCORD]:
                channels = await self.list_notification_channels(
                    workspace_id=workspace_id, integration_type=integration.type
                )
                integration.connected = len(channels.channels) > 0
            elif integration.type in [IntegrationType.GITHUB, IntegrationType.GITLAB]:
                repos = await self.list_git_repositories(
                    workspace_id=workspace_id,
                    provider=GitProvider.GITHUB if integration.type == IntegrationType.GITHUB else GitProvider.GITLAB,
                )
                integration.connected = len(repos.repositories) > 0
            elif integration.type == IntegrationType.DBT:
                projects = await self.list_dbt_projects(workspace_id=workspace_id)
                integration.connected = len(projects.projects) > 0

        categories = list(set(i.category for i in integrations))

        return IntegrationHub(
            integrations=integrations,
            categories=sorted(categories),
            total=len(integrations),
        )

    async def get_zapier_config(self) -> dict[str, Any]:
        """Get Zapier integration configuration."""
        return {
            "triggers": [t.model_dump() for t in ZAPIER_TRIGGERS],
            "actions": [
                {
                    "id": "create_dashboard",
                    "name": "Create Dashboard",
                    "description": "Create a new dashboard",
                    "endpoint": "/api/v1/dashboards/",
                    "method": "POST",
                    "input_fields": [
                        {"key": "name", "label": "Name", "type": "string", "required": True},
                        {"key": "description", "label": "Description", "type": "string", "required": False},
                    ],
                },
                {
                    "id": "execute_query",
                    "name": "Execute Query",
                    "description": "Execute a SQL query",
                    "endpoint": "/api/v1/queries/execute",
                    "method": "POST",
                    "input_fields": [
                        {"key": "connection_id", "label": "Connection ID", "type": "string", "required": True},
                        {"key": "sql", "label": "SQL Query", "type": "string", "required": True},
                    ],
                },
            ],
            "authentication": {"type": "api_key", "header": "X-API-Key"},
        }

    async def get_webhook_event_types(self) -> list[dict[str, str]]:
        """Get available webhook event types."""
        return [
            {"value": e.value, "label": e.value.replace(".", " ").replace("_", " ").title()}
            for e in WebhookEventType
        ]

    async def get_integration_stats(
        self, workspace_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Get integration statistics."""
        webhooks = await self.list_webhooks(workspace_id=workspace_id)
        channels = await self.list_notification_channels(workspace_id=workspace_id)
        repos = await self.list_git_repositories(workspace_id=workspace_id)
        projects = await self.list_dbt_projects(workspace_id=workspace_id)

        total_deliveries = sum(
            len(self._webhook_deliveries.get(w.id, [])) for w in webhooks.webhooks
        )
        total_notifications = sum(c.message_count for c in channels.channels)

        return {
            "webhooks": {
                "total": webhooks.total,
                "active": len([w for w in webhooks.webhooks if w.status == IntegrationStatus.ACTIVE]),
                "total_deliveries": total_deliveries,
            },
            "notification_channels": {
                "total": channels.total,
                "active": len([c for c in channels.channels if c.status == IntegrationStatus.ACTIVE]),
                "total_messages": total_notifications,
            },
            "git_repositories": {
                "total": repos.total,
                "auto_sync_enabled": len([r for r in repos.repositories if r.auto_sync]),
            },
            "dbt_projects": {
                "total": projects.total,
            },
        }
