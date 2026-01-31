"""
External Integrations API Endpoints

REST API for webhooks, notification channels, Git integration, dbt projects,
and other external integrations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.integrations_service import IntegrationsService
from app.schemas.integrations import (
    IntegrationType,
    IntegrationStatus,
    GitProvider,
    WebhookEventType,
    Webhook,
    WebhookCreate,
    WebhookUpdate,
    WebhookTest,
    WebhookListResponse,
    WebhookDeliveryListResponse,
    NotificationChannel,
    NotificationChannelCreate,
    NotificationChannelListResponse,
    NotificationMessage,
    GitRepository,
    GitRepositoryCreate,
    GitRepositoryUpdate,
    GitRepositoryListResponse,
    GitSyncResult,
    GitExportConfig,
    GitImportConfig,
    DbtProject,
    DbtProjectCreate,
    DbtProjectListResponse,
    DbtModel,
    DbtRunRequest,
    DbtRunResult,
    IntegrationHub,
)

router = APIRouter()


# ==================== WEBHOOKS ====================

@router.get("/webhooks", response_model=WebhookListResponse)
async def list_webhooks(
    workspace_id: Optional[str] = Query(None),
    integration_type: Optional[IntegrationType] = Query(None),
    status: Optional[IntegrationStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List webhooks with optional filters."""
    service = IntegrationsService(db)
    return await service.list_webhooks(workspace_id, integration_type, status)


@router.post("/webhooks", response_model=Webhook)
async def create_webhook(
    data: WebhookCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new webhook."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = IntegrationsService(db)
    return await service.create_webhook(user_id, data)


@router.get("/webhooks/{webhook_id}", response_model=Webhook)
async def get_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get webhook by ID."""
    service = IntegrationsService(db)
    webhook = await service.get_webhook(webhook_id)

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return webhook


@router.patch("/webhooks/{webhook_id}", response_model=Webhook)
async def update_webhook(
    webhook_id: str,
    data: WebhookUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a webhook."""
    service = IntegrationsService(db)
    webhook = await service.update_webhook(webhook_id, data)

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return webhook


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a webhook."""
    service = IntegrationsService(db)
    success = await service.delete_webhook(webhook_id)

    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {"deleted": True}


@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    test: WebhookTest = Body(default_factory=WebhookTest),
    db: AsyncSession = Depends(get_db),
):
    """Test a webhook with sample data."""
    service = IntegrationsService(db)
    try:
        delivery = await service.test_webhook(webhook_id, test)
        return {"success": True, "delivery": delivery}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/webhooks/{webhook_id}/deliveries", response_model=WebhookDeliveryListResponse)
async def get_webhook_deliveries(
    webhook_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get webhook delivery history."""
    service = IntegrationsService(db)
    return await service.get_webhook_deliveries(webhook_id, limit)


@router.get("/webhooks/events/types")
async def get_webhook_event_types(
    db: AsyncSession = Depends(get_db),
):
    """Get available webhook event types."""
    service = IntegrationsService(db)
    return {"event_types": await service.get_webhook_event_types()}


# ==================== NOTIFICATION CHANNELS ====================

@router.get("/channels", response_model=NotificationChannelListResponse)
async def list_notification_channels(
    workspace_id: Optional[str] = Query(None),
    integration_type: Optional[IntegrationType] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List notification channels."""
    service = IntegrationsService(db)
    return await service.list_notification_channels(workspace_id, integration_type)


@router.post("/channels", response_model=NotificationChannel)
async def create_notification_channel(
    data: NotificationChannelCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a notification channel."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = IntegrationsService(db)
    return await service.create_notification_channel(user_id, data)


@router.get("/channels/{channel_id}", response_model=NotificationChannel)
async def get_notification_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get notification channel by ID."""
    service = IntegrationsService(db)
    channel = await service.get_notification_channel(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    return channel


@router.delete("/channels/{channel_id}")
async def delete_notification_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a notification channel."""
    service = IntegrationsService(db)
    success = await service.delete_notification_channel(channel_id)

    if not success:
        raise HTTPException(status_code=404, detail="Channel not found")

    return {"deleted": True}


@router.post("/channels/{channel_id}/send")
async def send_notification(
    channel_id: str,
    message: NotificationMessage,
    db: AsyncSession = Depends(get_db),
):
    """Send a notification through a channel."""
    service = IntegrationsService(db)
    try:
        return await service.send_notification(channel_id, message)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/channels/{channel_id}/test")
async def test_notification_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Test a notification channel."""
    service = IntegrationsService(db)
    try:
        return await service.test_notification_channel(channel_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== GIT INTEGRATION ====================

@router.get("/git/repositories", response_model=GitRepositoryListResponse)
async def list_git_repositories(
    workspace_id: Optional[str] = Query(None),
    provider: Optional[GitProvider] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List Git repositories."""
    service = IntegrationsService(db)
    return await service.list_git_repositories(workspace_id, provider)


@router.post("/git/repositories", response_model=GitRepository)
async def create_git_repository(
    data: GitRepositoryCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a Git repository connection."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = IntegrationsService(db)
    return await service.create_git_repository(user_id, data)


@router.get("/git/repositories/{repo_id}", response_model=GitRepository)
async def get_git_repository(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get Git repository by ID."""
    service = IntegrationsService(db)
    repo = await service.get_git_repository(repo_id)

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return repo


@router.patch("/git/repositories/{repo_id}", response_model=GitRepository)
async def update_git_repository(
    repo_id: str,
    data: GitRepositoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a Git repository."""
    service = IntegrationsService(db)
    repo = await service.update_git_repository(repo_id, data)

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return repo


@router.delete("/git/repositories/{repo_id}")
async def delete_git_repository(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a Git repository."""
    service = IntegrationsService(db)
    success = await service.delete_git_repository(repo_id)

    if not success:
        raise HTTPException(status_code=404, detail="Repository not found")

    return {"deleted": True}


@router.post("/git/repositories/{repo_id}/sync", response_model=GitSyncResult)
async def sync_git_repository(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Sync a Git repository."""
    service = IntegrationsService(db)
    try:
        return await service.sync_git_repository(repo_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/git/repositories/{repo_id}/export")
async def export_to_git(
    repo_id: str,
    config: GitExportConfig,
    db: AsyncSession = Depends(get_db),
):
    """Export a resource to Git."""
    service = IntegrationsService(db)
    try:
        return await service.export_to_git(repo_id, config)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/git/repositories/{repo_id}/import")
async def import_from_git(
    repo_id: str,
    config: GitImportConfig,
    db: AsyncSession = Depends(get_db),
):
    """Import a resource from Git."""
    service = IntegrationsService(db)
    try:
        return await service.import_from_git(repo_id, config)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== DBT INTEGRATION ====================

@router.get("/dbt/projects", response_model=DbtProjectListResponse)
async def list_dbt_projects(
    workspace_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List dbt projects."""
    service = IntegrationsService(db)
    return await service.list_dbt_projects(workspace_id)


@router.post("/dbt/projects", response_model=DbtProject)
async def create_dbt_project(
    data: DbtProjectCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a dbt project."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = IntegrationsService(db)
    return await service.create_dbt_project(user_id, data)


@router.get("/dbt/projects/{project_id}", response_model=DbtProject)
async def get_dbt_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get dbt project by ID."""
    service = IntegrationsService(db)
    project = await service.get_dbt_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.delete("/dbt/projects/{project_id}")
async def delete_dbt_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a dbt project."""
    service = IntegrationsService(db)
    success = await service.delete_dbt_project(project_id)

    if not success:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"deleted": True}


@router.post("/dbt/projects/{project_id}/run", response_model=DbtRunResult)
async def run_dbt(
    project_id: str,
    request_data: DbtRunRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run a dbt command."""
    service = IntegrationsService(db)
    try:
        return await service.run_dbt(project_id, request_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/dbt/projects/{project_id}/models", response_model=list[DbtModel])
async def get_dbt_models(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get dbt models for a project."""
    service = IntegrationsService(db)
    try:
        return await service.get_dbt_models(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/dbt/projects/{project_id}/runs", response_model=list[DbtRunResult])
async def get_dbt_run_history(
    project_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get dbt run history."""
    service = IntegrationsService(db)
    return await service.get_dbt_run_history(project_id, limit)


# ==================== INTEGRATION HUB ====================

@router.get("/hub", response_model=IntegrationHub)
async def get_integration_hub(
    workspace_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get available integrations hub."""
    service = IntegrationsService(db)
    return await service.get_integration_hub(workspace_id)


@router.get("/zapier/config")
async def get_zapier_config(
    db: AsyncSession = Depends(get_db),
):
    """Get Zapier integration configuration."""
    service = IntegrationsService(db)
    return await service.get_zapier_config()


@router.get("/stats")
async def get_integration_stats(
    workspace_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get integration statistics."""
    service = IntegrationsService(db)
    return await service.get_integration_stats(workspace_id)


# ==================== OAUTH ====================

@router.get("/oauth/authorize")
async def oauth_authorize(
    integration_type: IntegrationType = Query(...),
    scopes: str = Query(None, description="Comma-separated scopes"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get OAuth authorization URL.

    Returns the URL to redirect the user to for OAuth authorization.
    """
    # In production, generate state token and build OAuth URL
    return {
        "authorization_url": f"https://oauth.example.com/authorize?client_id=xxx&scope={scopes or ''}",
        "state": "generated_state_token",
        "integration_type": integration_type,
    }


@router.post("/oauth/callback")
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback.

    Exchange authorization code for access token.
    """
    # In production, exchange code for tokens and store
    return {
        "success": True,
        "message": "Integration connected successfully",
    }


@router.delete("/oauth/{integration_type}")
async def disconnect_oauth(
    integration_type: IntegrationType,
    db: AsyncSession = Depends(get_db),
):
    """Disconnect an OAuth integration."""
    # In production, revoke tokens and remove integration
    return {
        "success": True,
        "message": f"{integration_type.value} disconnected successfully",
    }
