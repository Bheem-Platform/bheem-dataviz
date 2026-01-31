"""
External Integrations Schemas

Pydantic schemas for Zapier/Make webhooks, dbt integration, Git version control,
and external notification services.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from datetime import datetime


# Enums

class IntegrationType(str, Enum):
    """Types of external integrations"""
    ZAPIER = "zapier"
    MAKE = "make"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    DBT = "dbt"
    GIT = "git"
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    JIRA = "jira"
    NOTION = "notion"
    AIRTABLE = "airtable"


class IntegrationStatus(str, Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    EXPIRED = "expired"


class WebhookEventType(str, Enum):
    """Types of events that can trigger webhooks"""
    DASHBOARD_CREATED = "dashboard.created"
    DASHBOARD_UPDATED = "dashboard.updated"
    DASHBOARD_DELETED = "dashboard.deleted"
    DASHBOARD_PUBLISHED = "dashboard.published"
    CHART_CREATED = "chart.created"
    CHART_UPDATED = "chart.updated"
    CHART_DELETED = "chart.deleted"
    QUERY_EXECUTED = "query.executed"
    DATA_REFRESHED = "data.refreshed"
    ALERT_TRIGGERED = "alert.triggered"
    REPORT_GENERATED = "report.generated"
    USER_INVITED = "user.invited"
    USER_JOINED = "user.joined"
    COMMENT_ADDED = "comment.added"
    SHARE_LINK_CREATED = "share_link.created"


class WebhookMethod(str, Enum):
    """HTTP methods for webhooks"""
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"


class GitProvider(str, Enum):
    """Git providers"""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    AZURE_DEVOPS = "azure_devops"


class GitSyncDirection(str, Enum):
    """Git sync direction"""
    PUSH = "push"
    PULL = "pull"
    BIDIRECTIONAL = "bidirectional"


class DbtResourceType(str, Enum):
    """dbt resource types"""
    MODEL = "model"
    SOURCE = "source"
    SEED = "seed"
    SNAPSHOT = "snapshot"
    TEST = "test"
    MACRO = "macro"


# Webhook Models

class WebhookConfig(BaseModel):
    """Webhook configuration"""
    url: str
    method: WebhookMethod = WebhookMethod.POST
    headers: dict[str, str] = Field(default_factory=dict)
    secret: Optional[str] = None
    timeout_seconds: int = 30
    retry_count: int = 3
    retry_delay_seconds: int = 5


class Webhook(BaseModel):
    """Webhook subscription"""
    id: str
    name: str
    description: Optional[str] = None
    integration_type: IntegrationType
    events: list[WebhookEventType]
    config: WebhookConfig
    status: IntegrationStatus = IntegrationStatus.ACTIVE
    workspace_id: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    failure_count: int = 0
    last_error: Optional[str] = None


class WebhookCreate(BaseModel):
    """Create webhook request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    integration_type: IntegrationType = IntegrationType.WEBHOOK
    events: list[WebhookEventType] = Field(..., min_length=1)
    config: WebhookConfig
    workspace_id: Optional[str] = None


class WebhookUpdate(BaseModel):
    """Update webhook request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    events: Optional[list[WebhookEventType]] = None
    config: Optional[WebhookConfig] = None
    status: Optional[IntegrationStatus] = None


class WebhookDelivery(BaseModel):
    """Webhook delivery record"""
    id: str
    webhook_id: str
    event_type: WebhookEventType
    payload: dict[str, Any]
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    duration_ms: int
    success: bool
    error: Optional[str] = None
    attempt_number: int
    delivered_at: datetime = Field(default_factory=datetime.utcnow)


class WebhookTest(BaseModel):
    """Test webhook request"""
    event_type: WebhookEventType = WebhookEventType.DASHBOARD_UPDATED
    sample_data: Optional[dict[str, Any]] = None


# Zapier/Make Integration

class ZapierTrigger(BaseModel):
    """Zapier trigger configuration"""
    id: str
    name: str
    description: Optional[str] = None
    event_type: WebhookEventType
    sample_data: dict[str, Any]


class ZapierAction(BaseModel):
    """Zapier action configuration"""
    id: str
    name: str
    description: Optional[str] = None
    endpoint: str
    method: WebhookMethod
    input_fields: list[dict[str, Any]]
    output_fields: list[dict[str, Any]]


class ZapierIntegration(BaseModel):
    """Zapier integration configuration"""
    webhook_url: str
    api_key: str
    triggers: list[ZapierTrigger]
    actions: list[ZapierAction]
    connected: bool = False
    last_sync: Optional[datetime] = None


# Slack/Teams Integration

class SlackConfig(BaseModel):
    """Slack integration configuration"""
    webhook_url: str
    channel: Optional[str] = None
    username: str = "Bheem DataViz"
    icon_emoji: str = ":chart_with_upwards_trend:"
    include_preview: bool = True


class TeamsConfig(BaseModel):
    """Microsoft Teams integration configuration"""
    webhook_url: str
    include_preview: bool = True
    theme_color: str = "#3B82F6"


class DiscordConfig(BaseModel):
    """Discord integration configuration"""
    webhook_url: str
    username: str = "Bheem DataViz"
    avatar_url: Optional[str] = None
    include_preview: bool = True


class NotificationChannelConfig(BaseModel):
    """Notification channel configuration"""
    slack: Optional[SlackConfig] = None
    teams: Optional[TeamsConfig] = None
    discord: Optional[DiscordConfig] = None


class NotificationChannel(BaseModel):
    """Notification channel"""
    id: str
    name: str
    integration_type: IntegrationType
    config: NotificationChannelConfig
    status: IntegrationStatus = IntegrationStatus.ACTIVE
    workspace_id: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    message_count: int = 0


class NotificationChannelCreate(BaseModel):
    """Create notification channel request"""
    name: str = Field(..., min_length=1, max_length=100)
    integration_type: IntegrationType
    config: NotificationChannelConfig
    workspace_id: Optional[str] = None


class NotificationMessage(BaseModel):
    """Notification message"""
    title: str
    message: str
    url: Optional[str] = None
    color: Optional[str] = None
    fields: list[dict[str, str]] = Field(default_factory=list)
    image_url: Optional[str] = None


# Git Integration

class GitRepository(BaseModel):
    """Git repository configuration"""
    id: str
    name: str
    description: Optional[str] = None
    provider: GitProvider
    url: str
    branch: str = "main"
    path_prefix: str = ""
    access_token: Optional[str] = None
    ssh_key_id: Optional[str] = None
    sync_direction: GitSyncDirection = GitSyncDirection.BIDIRECTIONAL
    auto_sync: bool = False
    sync_interval_minutes: int = 60
    status: IntegrationStatus = IntegrationStatus.ACTIVE
    workspace_id: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    last_sync_commit: Optional[str] = None
    last_sync_error: Optional[str] = None


class GitRepositoryCreate(BaseModel):
    """Create git repository request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    provider: GitProvider
    url: str
    branch: str = "main"
    path_prefix: str = ""
    access_token: Optional[str] = None
    ssh_key_id: Optional[str] = None
    sync_direction: GitSyncDirection = GitSyncDirection.BIDIRECTIONAL
    auto_sync: bool = False
    sync_interval_minutes: int = 60
    workspace_id: Optional[str] = None


class GitRepositoryUpdate(BaseModel):
    """Update git repository request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    branch: Optional[str] = None
    path_prefix: Optional[str] = None
    access_token: Optional[str] = None
    ssh_key_id: Optional[str] = None
    sync_direction: Optional[GitSyncDirection] = None
    auto_sync: Optional[bool] = None
    sync_interval_minutes: Optional[int] = None
    status: Optional[IntegrationStatus] = None


class GitCommit(BaseModel):
    """Git commit information"""
    sha: str
    message: str
    author_name: str
    author_email: str
    timestamp: datetime
    files_changed: int
    additions: int
    deletions: int


class GitSyncResult(BaseModel):
    """Git sync result"""
    repository_id: str
    direction: GitSyncDirection
    success: bool
    commits: list[GitCommit]
    files_synced: int
    conflicts: list[str]
    error: Optional[str] = None
    started_at: datetime
    completed_at: datetime


class GitExportConfig(BaseModel):
    """Configuration for exporting to Git"""
    resource_type: str  # dashboard, chart, query, etc.
    resource_id: str
    file_path: str
    format: str = "json"  # json, yaml
    include_data: bool = False
    commit_message: Optional[str] = None


class GitImportConfig(BaseModel):
    """Configuration for importing from Git"""
    file_path: str
    resource_type: str
    overwrite_existing: bool = False
    target_workspace_id: Optional[str] = None


# dbt Integration

class DbtProject(BaseModel):
    """dbt project configuration"""
    id: str
    name: str
    description: Optional[str] = None
    project_path: str
    profile_name: str
    target_name: str = "dev"
    version: str = "1.0.0"
    connection_id: Optional[str] = None
    git_repository_id: Optional[str] = None
    status: IntegrationStatus = IntegrationStatus.ACTIVE
    workspace_id: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[str] = None


class DbtProjectCreate(BaseModel):
    """Create dbt project request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    project_path: str
    profile_name: str
    target_name: str = "dev"
    connection_id: Optional[str] = None
    git_repository_id: Optional[str] = None
    workspace_id: Optional[str] = None


class DbtModel(BaseModel):
    """dbt model information"""
    name: str
    description: Optional[str] = None
    resource_type: DbtResourceType
    schema_name: str
    database: Optional[str] = None
    columns: list[dict[str, Any]]
    depends_on: list[str]
    tags: list[str]
    config: dict[str, Any]


class DbtRunCommand(str, Enum):
    """dbt run commands"""
    RUN = "run"
    TEST = "test"
    BUILD = "build"
    COMPILE = "compile"
    SEED = "seed"
    SNAPSHOT = "snapshot"
    SOURCE_FRESHNESS = "source freshness"
    DOCS_GENERATE = "docs generate"


class DbtRunRequest(BaseModel):
    """dbt run request"""
    command: DbtRunCommand
    select: Optional[str] = None  # model selector
    exclude: Optional[str] = None
    full_refresh: bool = False
    vars: dict[str, Any] = Field(default_factory=dict)


class DbtRunResult(BaseModel):
    """dbt run result"""
    id: str
    project_id: str
    command: DbtRunCommand
    status: str  # success, error, running
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    models_run: int = 0
    models_success: int = 0
    models_error: int = 0
    models_skipped: int = 0
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_warned: int = 0
    logs: list[str]
    artifacts: dict[str, Any]


# OAuth Configuration

class OAuthConfig(BaseModel):
    """OAuth configuration for integrations"""
    id: str
    integration_type: IntegrationType
    client_id: str
    client_secret_encrypted: str
    redirect_uri: str
    scopes: list[str]
    authorize_url: str
    token_url: str
    workspace_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OAuthToken(BaseModel):
    """OAuth token"""
    integration_type: IntegrationType
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    scopes: list[str]


class OAuthAuthorizeRequest(BaseModel):
    """OAuth authorization request"""
    integration_type: IntegrationType
    scopes: list[str] = Field(default_factory=list)
    state: Optional[str] = None


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request"""
    code: str
    state: Optional[str] = None


# Integration Hub

class IntegrationInfo(BaseModel):
    """Integration information"""
    type: IntegrationType
    name: str
    description: str
    icon: str
    category: str  # automation, notification, version_control, data
    available: bool
    connected: bool = False
    requires_oauth: bool = False
    config_schema: list[dict[str, Any]]


class IntegrationHub(BaseModel):
    """Integration hub listing"""
    integrations: list[IntegrationInfo]
    categories: list[str]
    total: int


# Response Models

class WebhookListResponse(BaseModel):
    """List webhooks response"""
    webhooks: list[Webhook]
    total: int


class WebhookDeliveryListResponse(BaseModel):
    """List webhook deliveries response"""
    deliveries: list[WebhookDelivery]
    total: int


class NotificationChannelListResponse(BaseModel):
    """List notification channels response"""
    channels: list[NotificationChannel]
    total: int


class GitRepositoryListResponse(BaseModel):
    """List git repositories response"""
    repositories: list[GitRepository]
    total: int


class DbtProjectListResponse(BaseModel):
    """List dbt projects response"""
    projects: list[DbtProject]
    total: int


# Constants

ZAPIER_TRIGGERS: list[ZapierTrigger] = [
    ZapierTrigger(
        id="new_dashboard",
        name="New Dashboard",
        description="Triggers when a new dashboard is created",
        event_type=WebhookEventType.DASHBOARD_CREATED,
        sample_data={"dashboard_id": "123", "name": "Sales Dashboard", "created_by": "user@example.com"},
    ),
    ZapierTrigger(
        id="alert_triggered",
        name="Alert Triggered",
        description="Triggers when a data alert is triggered",
        event_type=WebhookEventType.ALERT_TRIGGERED,
        sample_data={"alert_id": "456", "name": "High Revenue Alert", "value": 1000000, "threshold": 900000},
    ),
    ZapierTrigger(
        id="report_generated",
        name="Report Generated",
        description="Triggers when a scheduled report is generated",
        event_type=WebhookEventType.REPORT_GENERATED,
        sample_data={"report_id": "789", "name": "Weekly Sales Report", "format": "pdf", "url": "https://..."},
    ),
]

AVAILABLE_INTEGRATIONS: list[IntegrationInfo] = [
    IntegrationInfo(
        type=IntegrationType.ZAPIER,
        name="Zapier",
        description="Connect to 5000+ apps with Zapier automation",
        icon="zap",
        category="automation",
        available=True,
        requires_oauth=False,
        config_schema=[{"key": "webhook_url", "type": "string", "label": "Webhook URL", "required": True}],
    ),
    IntegrationInfo(
        type=IntegrationType.MAKE,
        name="Make (Integromat)",
        description="Advanced automation scenarios with Make",
        icon="layers",
        category="automation",
        available=True,
        requires_oauth=False,
        config_schema=[{"key": "webhook_url", "type": "string", "label": "Webhook URL", "required": True}],
    ),
    IntegrationInfo(
        type=IntegrationType.SLACK,
        name="Slack",
        description="Send notifications to Slack channels",
        icon="slack",
        category="notification",
        available=True,
        requires_oauth=False,
        config_schema=[
            {"key": "webhook_url", "type": "string", "label": "Webhook URL", "required": True},
            {"key": "channel", "type": "string", "label": "Channel", "required": False},
        ],
    ),
    IntegrationInfo(
        type=IntegrationType.TEAMS,
        name="Microsoft Teams",
        description="Send notifications to Teams channels",
        icon="users",
        category="notification",
        available=True,
        requires_oauth=False,
        config_schema=[{"key": "webhook_url", "type": "string", "label": "Webhook URL", "required": True}],
    ),
    IntegrationInfo(
        type=IntegrationType.DISCORD,
        name="Discord",
        description="Send notifications to Discord servers",
        icon="message-circle",
        category="notification",
        available=True,
        requires_oauth=False,
        config_schema=[{"key": "webhook_url", "type": "string", "label": "Webhook URL", "required": True}],
    ),
    IntegrationInfo(
        type=IntegrationType.GITHUB,
        name="GitHub",
        description="Version control with GitHub repositories",
        icon="github",
        category="version_control",
        available=True,
        requires_oauth=True,
        config_schema=[
            {"key": "repository", "type": "string", "label": "Repository URL", "required": True},
            {"key": "branch", "type": "string", "label": "Branch", "required": False, "default": "main"},
        ],
    ),
    IntegrationInfo(
        type=IntegrationType.GITLAB,
        name="GitLab",
        description="Version control with GitLab repositories",
        icon="gitlab",
        category="version_control",
        available=True,
        requires_oauth=True,
        config_schema=[
            {"key": "repository", "type": "string", "label": "Repository URL", "required": True},
            {"key": "branch", "type": "string", "label": "Branch", "required": False, "default": "main"},
        ],
    ),
    IntegrationInfo(
        type=IntegrationType.DBT,
        name="dbt",
        description="Data transformation with dbt projects",
        icon="database",
        category="data",
        available=True,
        requires_oauth=False,
        config_schema=[
            {"key": "project_path", "type": "string", "label": "Project Path", "required": True},
            {"key": "profile_name", "type": "string", "label": "Profile Name", "required": True},
        ],
    ),
    IntegrationInfo(
        type=IntegrationType.JIRA,
        name="Jira",
        description="Create issues and track projects in Jira",
        icon="trello",
        category="automation",
        available=True,
        requires_oauth=True,
        config_schema=[
            {"key": "site_url", "type": "string", "label": "Jira Site URL", "required": True},
            {"key": "project_key", "type": "string", "label": "Project Key", "required": True},
        ],
    ),
    IntegrationInfo(
        type=IntegrationType.NOTION,
        name="Notion",
        description="Sync dashboards and data with Notion",
        icon="book-open",
        category="automation",
        available=True,
        requires_oauth=True,
        config_schema=[{"key": "workspace_id", "type": "string", "label": "Workspace ID", "required": True}],
    ),
]


# Helper Functions

def get_webhook_sample_payload(event_type: WebhookEventType) -> dict[str, Any]:
    """Get sample payload for webhook event type."""
    samples = {
        WebhookEventType.DASHBOARD_CREATED: {
            "event": "dashboard.created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "dashboard_id": "dash_123",
                "name": "Sales Dashboard",
                "created_by": "user@example.com",
                "workspace_id": "ws_456",
            },
        },
        WebhookEventType.ALERT_TRIGGERED: {
            "event": "alert.triggered",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "alert_id": "alert_789",
                "name": "High Revenue Alert",
                "current_value": 1000000,
                "threshold": 900000,
                "severity": "high",
            },
        },
        WebhookEventType.REPORT_GENERATED: {
            "event": "report.generated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "report_id": "report_abc",
                "name": "Weekly Sales Report",
                "format": "pdf",
                "download_url": "https://dataviz.bheem.co.uk/reports/download/report_abc",
            },
        },
    }
    return samples.get(event_type, {"event": event_type.value, "timestamp": datetime.utcnow().isoformat(), "data": {}})


def validate_webhook_url(url: str) -> bool:
    """Validate webhook URL format."""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def generate_webhook_signature(payload: str, secret: str) -> str:
    """Generate HMAC signature for webhook payload."""
    import hmac
    import hashlib
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
