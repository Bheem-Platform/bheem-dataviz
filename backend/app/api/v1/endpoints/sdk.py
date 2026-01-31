"""
SDK & API Management Endpoints

REST API for API keys, usage tracking, rate limits, and code generation.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.sdk_service import SDKService
from app.schemas.sdk import (
    APIKeyType,
    APIKeyStatus,
    SDKLanguage,
    APIKey,
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyResponse,
    APIKeyListResponse,
    UsageStatsResponse,
    RateLimitStatus,
    CodeGenerationRequest,
    CodeGenerationResponse,
    APIDocumentation,
)

router = APIRouter()


# API Key Management

@router.get("/keys", response_model=APIKeyListResponse)
async def list_api_keys(
    workspace_id: Optional[str] = Query(None),
    key_type: Optional[APIKeyType] = Query(None),
    status: Optional[APIKeyStatus] = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all API keys for the current user.

    Optionally filter by workspace, type, or status.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SDKService(db)
    return await service.list_api_keys(user_id, workspace_id, key_type, status)


@router.post("/keys", response_model=APIKeyResponse)
async def create_api_key(
    data: APIKeyCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new API key.

    The full key is only returned once on creation. Store it securely.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SDKService(db)
    return await service.create_api_key(user_id, data)


@router.get("/keys/{key_id}", response_model=APIKey)
async def get_api_key(
    key_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get API key details."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SDKService(db)
    api_key = await service.get_api_key(key_id)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return api_key


@router.patch("/keys/{key_id}", response_model=APIKey)
async def update_api_key(
    key_id: str,
    data: APIKeyUpdate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update an API key."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SDKService(db)
    api_key = await service.update_api_key(key_id, user_id, data)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return api_key


@router.post("/keys/{key_id}/revoke", response_model=APIKey)
async def revoke_api_key(
    key_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Revoke an API key."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SDKService(db)
    success = await service.revoke_api_key(key_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key = await service.get_api_key(key_id)
    return api_key


@router.delete("/keys/{key_id}")
async def delete_api_key(
    key_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete an API key."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SDKService(db)
    success = await service.delete_api_key(key_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="API key not found")

    return {"deleted": True}


@router.post("/keys/{key_id}/rotate", response_model=APIKeyResponse)
async def rotate_api_key(
    key_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Rotate an API key.

    Generates a new key while keeping all settings. The old key becomes invalid.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SDKService(db)
    result = await service.rotate_api_key(key_id, user_id)

    if not result:
        raise HTTPException(status_code=404, detail="API key not found")

    return result


# API Key Validation (Public endpoint for SDK)

@router.post("/validate")
async def validate_api_key(
    api_key: str = Body(..., embed=True),
    endpoint: Optional[str] = Body(None),
    ip_address: Optional[str] = Body(None),
    domain: Optional[str] = Body(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Validate an API key.

    Returns validation result and key permissions.
    """
    service = SDKService(db)
    is_valid, key_obj, error = await service.validate_api_key(
        api_key, endpoint, None, ip_address, domain
    )

    if not is_valid:
        return {
            "valid": False,
            "error": error,
        }

    return {
        "valid": True,
        "key_type": key_obj.key_type.value,
        "permissions": key_obj.permissions.model_dump(),
        "rate_limits": key_obj.rate_limits.model_dump(),
    }


# Usage & Rate Limits

@router.get("/keys/{key_id}/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    key_id: str,
    days: int = Query(30, ge=1, le=90),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get usage statistics for an API key."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SDKService(db)
    api_key = await service.get_api_key(key_id)

    if not api_key or api_key.user_id != user_id:
        raise HTTPException(status_code=404, detail="API key not found")

    from datetime import datetime, timedelta
    start_date = datetime.utcnow() - timedelta(days=days)

    return await service.get_usage_stats(key_id, start_date)


@router.get("/keys/{key_id}/rate-limits", response_model=list[RateLimitStatus])
async def get_rate_limit_status(
    key_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get current rate limit status for an API key."""
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    service = SDKService(db)
    api_key = await service.get_api_key(key_id)

    if not api_key or api_key.user_id != user_id:
        raise HTTPException(status_code=404, detail="API key not found")

    return await service.get_rate_limit_status(key_id)


# Code Generation

@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(
    language: SDKLanguage = Query(...),
    resource_type: str = Query(..., description="dashboard, chart, query"),
    resource_id: str = Query(...),
    include_auth: bool = Query(True),
    include_error_handling: bool = Query(True),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate code snippets for SDK integration.

    Returns code in the requested language for embedding or accessing the resource.
    """
    user_id = getattr(request.state, "user_id", "00000000-0000-0000-0000-000000000000")

    # Get user's first API key for code example
    service = SDKService(db)
    keys = await service.list_api_keys(user_id)

    api_key = "YOUR_API_KEY"
    if keys.keys:
        api_key = keys.keys[0].key_prefix + "_xxxxxxxxxxxxxxxx"

    code_request = CodeGenerationRequest(
        language=language,
        resource_type=resource_type,
        resource_id=resource_id,
        include_auth=include_auth,
        include_error_handling=include_error_handling,
    )

    return await service.generate_code(code_request, api_key)


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported SDK languages."""
    from app.schemas.sdk import SDK_LANGUAGES_INFO

    return {
        "languages": [
            {
                "id": lang.value,
                "name": info["name"],
                "package": info.get("package"),
                "install": info.get("install"),
            }
            for lang, info in SDK_LANGUAGES_INFO.items()
        ]
    }


# API Documentation

@router.get("/docs", response_model=APIDocumentation)
async def get_api_documentation(
    db: AsyncSession = Depends(get_db),
):
    """
    Get full API documentation.

    Returns endpoint documentation, schemas, and SDK information.
    """
    service = SDKService(db)
    return await service.get_api_documentation()


@router.get("/docs/openapi")
async def get_openapi_spec():
    """Get OpenAPI specification."""
    # In production, this would return the actual OpenAPI spec
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Bheem DataViz API",
            "version": "1.0.0",
            "description": "REST API for Bheem DataViz platform",
        },
        "servers": [
            {"url": "https://api.dataviz.bheemkodee.com/api/v1"},
        ],
    }


@router.get("/docs/postman")
async def get_postman_collection():
    """Get Postman collection for API testing."""
    return {
        "info": {
            "name": "Bheem DataViz API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            {
                "name": "Authentication",
                "item": [
                    {
                        "name": "Login",
                        "request": {
                            "method": "POST",
                            "url": "{{baseUrl}}/auth/login",
                        },
                    },
                ],
            },
            {
                "name": "Dashboards",
                "item": [
                    {
                        "name": "List Dashboards",
                        "request": {
                            "method": "GET",
                            "url": "{{baseUrl}}/dashboards",
                        },
                    },
                ],
            },
        ],
        "variable": [
            {"key": "baseUrl", "value": "https://api.dataviz.bheemkodee.com/api/v1"},
        ],
    }


# SDK Configuration

@router.get("/config")
async def get_sdk_config(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get SDK configuration for the current environment."""
    return {
        "version": "1.0.0",
        "base_url": "https://api.dataviz.bheemkodee.com",
        "embed_url": "https://dataviz.bheemkodee.com/embed",
        "cdn_url": "https://cdn.dataviz.bheemkodee.com",
        "supported_languages": [lang.value for lang in SDKLanguage],
        "features": {
            "embed": True,
            "export": True,
            "interactions": True,
            "comments": True,
            "ai": True,
        },
    }


# Quick Embed

@router.get("/embed/{resource_type}/{resource_id}")
async def get_embed_info(
    resource_type: str,
    resource_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get embed information for a resource.

    Returns the embed URL and configuration.
    """
    base_url = "https://dataviz.bheemkodee.com/embed"

    return {
        "embed_url": f"{base_url}/{resource_type}/{resource_id}",
        "iframe_code": f'<iframe src="{base_url}/{resource_type}/{resource_id}" width="100%" height="600" frameborder="0"></iframe>',
        "js_snippet": f'''<div id="dataviz-{resource_id}"></div>
<script src="https://cdn.dataviz.bheemkodee.com/sdk.js"></script>
<script>
  BheemDataViz.embed({{
    container: '#dataviz-{resource_id}',
    resourceType: '{resource_type}',
    resourceId: '{resource_id}'
  }});
</script>''',
    }
