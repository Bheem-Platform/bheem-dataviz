"""
SDK & API Service

Business logic for API key management, rate limiting, usage tracking, and code generation.
"""

from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
import secrets
import hashlib

from app.schemas.sdk import (
    APIKeyType,
    APIKeyStatus,
    SDKLanguage,
    EndpointCategory,
    RateLimitPeriod,
    APIKeyPermissions,
    RateLimitConfig,
    APIKey,
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyResponse,
    APIKeyListResponse,
    UsageRecord,
    UsageStats,
    UsageStatsResponse,
    RateLimitStatus,
    SDKConfig,
    SDKInitOptions,
    CodeSnippet,
    CodeGenerationRequest,
    CodeGenerationResponse,
    APIParameter,
    APIEndpoint,
    APIEndpointGroup,
    APIDocumentation,
    SDKWebhookConfig,
    SDKWebhookEvent,
    DEFAULT_RATE_LIMITS,
    PUBLIC_KEY_RATE_LIMITS,
    SDK_LANGUAGES_INFO,
    generate_api_key_prefix,
    hash_api_key,
    generate_full_api_key,
    mask_api_key,
)


class SDKService:
    """Service for SDK and API management."""

    def __init__(self, db=None):
        self.db = db

    # In-memory stores (production would use database + Redis)
    _api_keys: dict[str, APIKey] = {}
    _key_lookup: dict[str, str] = {}  # hash -> key_id
    _usage_records: dict[str, list[UsageRecord]] = defaultdict(list)
    _rate_limit_counters: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    _webhooks: dict[str, list[SDKWebhookConfig]] = defaultdict(list)

    # API Key Management

    async def create_api_key(
        self,
        user_id: str,
        data: APIKeyCreate,
    ) -> APIKeyResponse:
        """Create a new API key."""
        import uuid

        # Generate key
        prefix = generate_api_key_prefix()
        full_key = generate_full_api_key(prefix)
        key_hash = hash_api_key(full_key)

        # Set permissions based on key type
        permissions = data.permissions or APIKeyPermissions()
        if data.key_type == APIKeyType.PUBLIC:
            # Public keys have limited permissions
            permissions.can_write_dashboards = False
            permissions.can_write_charts = False
            permissions.can_write_connections = False
            permissions.can_write_datasets = False
            permissions.can_admin = False

        # Set rate limits
        rate_limits = data.rate_limits
        if rate_limits is None:
            if data.key_type == APIKeyType.PUBLIC:
                rate_limits = PUBLIC_KEY_RATE_LIMITS
            else:
                rate_limits = DEFAULT_RATE_LIMITS

        # Calculate expiration
        expires_at = None
        if data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=data.expires_in_days)

        key_id = str(uuid.uuid4())
        now = datetime.utcnow()

        api_key = APIKey(
            id=key_id,
            name=data.name,
            description=data.description,
            key_prefix=prefix,
            key_hash=key_hash,
            key_type=data.key_type,
            status=APIKeyStatus.ACTIVE,
            user_id=user_id,
            workspace_id=data.workspace_id,
            permissions=permissions,
            rate_limits=rate_limits,
            allowed_ips=data.allowed_ips,
            allowed_domains=data.allowed_domains,
            expires_at=expires_at,
            created_at=now,
            created_by=user_id,
            tags=data.tags,
        )

        # Store
        self._api_keys[key_id] = api_key
        self._key_lookup[key_hash] = key_id

        return APIKeyResponse(api_key=api_key, key=full_key)

    async def get_api_key(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID."""
        return self._api_keys.get(key_id)

    async def get_api_key_by_key(self, key: str) -> Optional[APIKey]:
        """Get API key by the actual key value."""
        key_hash = hash_api_key(key)
        key_id = self._key_lookup.get(key_hash)
        if key_id:
            return self._api_keys.get(key_id)
        return None

    async def list_api_keys(
        self,
        user_id: str,
        workspace_id: Optional[str] = None,
        key_type: Optional[APIKeyType] = None,
        status: Optional[APIKeyStatus] = None,
    ) -> APIKeyListResponse:
        """List API keys for a user."""
        keys = []

        for api_key in self._api_keys.values():
            if api_key.user_id != user_id:
                continue

            if workspace_id and api_key.workspace_id != workspace_id:
                continue

            if key_type and api_key.key_type != key_type:
                continue

            if status and api_key.status != status:
                continue

            keys.append(api_key)

        # Sort by created_at descending
        keys.sort(key=lambda k: k.created_at, reverse=True)

        return APIKeyListResponse(keys=keys, total=len(keys))

    async def update_api_key(
        self,
        key_id: str,
        user_id: str,
        data: APIKeyUpdate,
    ) -> Optional[APIKey]:
        """Update an API key."""
        api_key = self._api_keys.get(key_id)
        if not api_key or api_key.user_id != user_id:
            return None

        # Update fields
        if data.name is not None:
            api_key.name = data.name
        if data.description is not None:
            api_key.description = data.description
        if data.permissions is not None:
            api_key.permissions = data.permissions
        if data.rate_limits is not None:
            api_key.rate_limits = data.rate_limits
        if data.allowed_ips is not None:
            api_key.allowed_ips = data.allowed_ips
        if data.allowed_domains is not None:
            api_key.allowed_domains = data.allowed_domains
        if data.status is not None:
            api_key.status = data.status
        if data.tags is not None:
            api_key.tags = data.tags

        api_key.updated_at = datetime.utcnow()

        return api_key

    async def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """Revoke an API key."""
        api_key = self._api_keys.get(key_id)
        if not api_key or api_key.user_id != user_id:
            return False

        api_key.status = APIKeyStatus.REVOKED
        api_key.updated_at = datetime.utcnow()

        return True

    async def delete_api_key(self, key_id: str, user_id: str) -> bool:
        """Delete an API key."""
        api_key = self._api_keys.get(key_id)
        if not api_key or api_key.user_id != user_id:
            return False

        # Remove from lookup
        if api_key.key_hash in self._key_lookup:
            del self._key_lookup[api_key.key_hash]

        del self._api_keys[key_id]

        return True

    async def rotate_api_key(self, key_id: str, user_id: str) -> Optional[APIKeyResponse]:
        """Rotate an API key (generate new key, keep settings)."""
        api_key = self._api_keys.get(key_id)
        if not api_key or api_key.user_id != user_id:
            return None

        # Remove old hash
        if api_key.key_hash in self._key_lookup:
            del self._key_lookup[api_key.key_hash]

        # Generate new key
        prefix = generate_api_key_prefix()
        full_key = generate_full_api_key(prefix)
        key_hash = hash_api_key(full_key)

        # Update
        api_key.key_prefix = prefix
        api_key.key_hash = key_hash
        api_key.updated_at = datetime.utcnow()

        # Store new lookup
        self._key_lookup[key_hash] = key_id

        return APIKeyResponse(api_key=api_key, key=full_key)

    # API Key Validation

    async def validate_api_key(
        self,
        key: str,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        ip_address: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> tuple[bool, Optional[APIKey], Optional[str]]:
        """
        Validate an API key.
        Returns (is_valid, api_key, error_message).
        """
        api_key = await self.get_api_key_by_key(key)

        if not api_key:
            return False, None, "Invalid API key"

        # Check status
        if api_key.status != APIKeyStatus.ACTIVE:
            return False, api_key, f"API key is {api_key.status.value}"

        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            api_key.status = APIKeyStatus.EXPIRED
            return False, api_key, "API key has expired"

        # Check IP whitelist
        if api_key.allowed_ips and ip_address:
            if not self._check_ip_allowed(ip_address, api_key.allowed_ips):
                return False, api_key, "IP address not allowed"

        # Check domain whitelist
        if api_key.allowed_domains and domain:
            if not self._check_domain_allowed(domain, api_key.allowed_domains):
                return False, api_key, "Domain not allowed"

        # Check rate limits
        is_limited, limit_info = await self.check_rate_limit(api_key.id)
        if is_limited:
            return False, api_key, f"Rate limit exceeded. Retry after {limit_info}"

        # Update last used
        api_key.last_used_at = datetime.utcnow()

        return True, api_key, None

    def _check_ip_allowed(self, ip: str, allowed_ips: list[str]) -> bool:
        """Check if IP is in whitelist."""
        # Simple check - production would handle CIDR notation
        return ip in allowed_ips or "*" in allowed_ips

    def _check_domain_allowed(self, domain: str, allowed_domains: list[str]) -> bool:
        """Check if domain is in whitelist."""
        domain = domain.lower()
        for allowed in allowed_domains:
            allowed = allowed.lower()
            if allowed.startswith("*."):
                # Wildcard
                suffix = allowed[2:]
                if domain.endswith(suffix) or domain == suffix:
                    return True
            elif domain == allowed:
                return True
        return False

    # Rate Limiting

    async def check_rate_limit(self, api_key_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if API key is rate limited.
        Returns (is_limited, retry_after_info).
        """
        api_key = self._api_keys.get(api_key_id)
        if not api_key or not api_key.rate_limits.enabled:
            return False, None

        now = datetime.utcnow()
        counters = self._rate_limit_counters[api_key_id]
        limits = api_key.rate_limits

        # Check each period
        checks = [
            (limits.requests_per_second, "second", 1),
            (limits.requests_per_minute, "minute", 60),
            (limits.requests_per_hour, "hour", 3600),
            (limits.requests_per_day, "day", 86400),
        ]

        for limit, period, seconds in checks:
            if limit is None:
                continue

            key = f"{period}:{now.timestamp() // seconds}"
            count = counters.get(key, 0)

            if count >= limit:
                reset_time = (int(now.timestamp() // seconds) + 1) * seconds
                retry_after = reset_time - int(now.timestamp())
                return True, f"{retry_after} seconds"

        return False, None

    async def increment_rate_limit(self, api_key_id: str) -> None:
        """Increment rate limit counters."""
        now = datetime.utcnow()
        counters = self._rate_limit_counters[api_key_id]

        # Increment all period counters
        for period, seconds in [("second", 1), ("minute", 60), ("hour", 3600), ("day", 86400)]:
            key = f"{period}:{now.timestamp() // seconds}"
            counters[key] = counters.get(key, 0) + 1

    async def get_rate_limit_status(self, api_key_id: str) -> list[RateLimitStatus]:
        """Get current rate limit status for all periods."""
        api_key = self._api_keys.get(api_key_id)
        if not api_key:
            return []

        now = datetime.utcnow()
        counters = self._rate_limit_counters[api_key_id]
        limits = api_key.rate_limits
        statuses = []

        checks = [
            (limits.requests_per_minute, RateLimitPeriod.MINUTE, 60),
            (limits.requests_per_hour, RateLimitPeriod.HOUR, 3600),
            (limits.requests_per_day, RateLimitPeriod.DAY, 86400),
        ]

        for limit, period, seconds in checks:
            if limit is None:
                continue

            key = f"{period.value}:{now.timestamp() // seconds}"
            count = counters.get(key, 0)
            reset_time = datetime.fromtimestamp((int(now.timestamp() // seconds) + 1) * seconds)

            statuses.append(RateLimitStatus(
                api_key_id=api_key_id,
                period=period,
                limit=limit,
                remaining=max(0, limit - count),
                reset_at=reset_time,
                is_limited=count >= limit,
            ))

        return statuses

    # Usage Tracking

    async def record_usage(
        self,
        api_key_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
        request_size: int = 0,
        response_size: int = 0,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UsageRecord:
        """Record API usage."""
        import uuid

        record = UsageRecord(
            id=str(uuid.uuid4()),
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            request_size_bytes=request_size,
            response_size_bytes=response_size,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
        )

        self._usage_records[api_key_id].append(record)

        # Also increment rate limit
        await self.increment_rate_limit(api_key_id)

        return record

    async def get_usage_stats(
        self,
        api_key_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> UsageStatsResponse:
        """Get usage statistics for an API key."""
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.utcnow()

        records = self._usage_records.get(api_key_id, [])

        # Filter by date
        records = [r for r in records if start_date <= r.timestamp <= end_date]

        # Calculate stats
        total = len(records)
        successful = len([r for r in records if 200 <= r.status_code < 400])
        failed = len([r for r in records if r.status_code >= 400])
        rate_limited = len([r for r in records if r.status_code == 429])

        # By endpoint
        by_endpoint: dict[str, int] = defaultdict(int)
        by_method: dict[str, int] = defaultdict(int)
        by_status: dict[int, int] = defaultdict(int)

        response_times = []
        total_request_bytes = 0
        total_response_bytes = 0
        unique_ips = set()

        for r in records:
            by_endpoint[r.endpoint] += 1
            by_method[r.method] += 1
            by_status[r.status_code] += 1
            response_times.append(r.response_time_ms)
            total_request_bytes += r.request_size_bytes
            total_response_bytes += r.response_size_bytes
            if r.ip_address:
                unique_ips.add(r.ip_address)

        # Calculate percentiles
        response_times.sort()
        avg_time = sum(response_times) / len(response_times) if response_times else 0
        p50 = response_times[len(response_times) // 2] if response_times else 0
        p95 = response_times[int(len(response_times) * 0.95)] if response_times else 0
        p99 = response_times[int(len(response_times) * 0.99)] if response_times else 0

        stats = UsageStats(
            api_key_id=api_key_id,
            period_start=start_date,
            period_end=end_date,
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            rate_limited_requests=rate_limited,
            requests_by_endpoint=dict(by_endpoint),
            requests_by_method=dict(by_method),
            requests_by_status=dict(by_status),
            avg_response_time_ms=avg_time,
            p50_response_time_ms=p50,
            p95_response_time_ms=p95,
            p99_response_time_ms=p99,
            total_request_bytes=total_request_bytes,
            total_response_bytes=total_response_bytes,
            unique_ips=len(unique_ips),
            unique_endpoints=len(by_endpoint),
        )

        # Daily breakdown
        daily: dict[str, dict] = defaultdict(lambda: {"requests": 0, "errors": 0})
        for r in records:
            day = r.timestamp.strftime("%Y-%m-%d")
            daily[day]["requests"] += 1
            if r.status_code >= 400:
                daily[day]["errors"] += 1

        daily_breakdown = [
            {"date": day, **data}
            for day, data in sorted(daily.items())
        ]

        # Top endpoints
        top_endpoints = sorted(
            [{"endpoint": k, "count": v} for k, v in by_endpoint.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:10]

        return UsageStatsResponse(
            stats=stats,
            daily_breakdown=daily_breakdown,
            top_endpoints=top_endpoints,
        )

    # Code Generation

    async def generate_code(
        self,
        request: CodeGenerationRequest,
        api_key: str,
    ) -> CodeGenerationResponse:
        """Generate code snippets for SDK integration."""
        snippets = []

        if request.language == SDKLanguage.JAVASCRIPT:
            snippets = self._generate_javascript_code(request, api_key)
        elif request.language == SDKLanguage.TYPESCRIPT:
            snippets = self._generate_typescript_code(request, api_key)
        elif request.language == SDKLanguage.PYTHON:
            snippets = self._generate_python_code(request, api_key)
        elif request.language == SDKLanguage.REACT:
            snippets = self._generate_react_code(request, api_key)
        elif request.language == SDKLanguage.VUE:
            snippets = self._generate_vue_code(request, api_key)
        elif request.language == SDKLanguage.CURL:
            snippets = self._generate_curl_code(request, api_key)

        # Setup instructions
        lang_info = SDK_LANGUAGES_INFO.get(request.language, {})
        install_cmd = lang_info.get("install", "")
        setup = f"# Installation\n{install_cmd}\n" if install_cmd else ""

        return CodeGenerationResponse(
            snippets=snippets,
            setup_instructions=setup,
            documentation_url="https://docs.dataviz.bheemkodee.com/sdk",
        )

    def _generate_javascript_code(self, request: CodeGenerationRequest, api_key: str) -> list[CodeSnippet]:
        """Generate JavaScript SDK code."""
        masked_key = mask_api_key(api_key)

        embed_code = f'''import BheemDataViz from '@bheem/dataviz-sdk';

// Initialize SDK
const dataviz = new BheemDataViz({{
  apiKey: '{masked_key}',
  baseUrl: 'https://api.dataviz.bheemkodee.com'
}});

// Embed {request.resource_type}
dataviz.embed({{
  container: '#dataviz-container',
  resourceType: '{request.resource_type}',
  resourceId: '{request.resource_id}',
  width: '100%',
  height: '600px',
  onLoad: () => console.log('{request.resource_type} loaded'),
  onError: (error) => console.error('Error:', error)
}});'''

        fetch_code = f'''// Fetch {request.resource_type} data
const response = await dataviz.get{request.resource_type.title()}('{request.resource_id}');
console.log(response.data);'''

        return [
            CodeSnippet(
                language=SDKLanguage.JAVASCRIPT,
                code=embed_code,
                filename="embed.js",
                description=f"Embed {request.resource_type} in your application",
                dependencies=["@bheem/dataviz-sdk"],
            ),
            CodeSnippet(
                language=SDKLanguage.JAVASCRIPT,
                code=fetch_code,
                filename="fetch.js",
                description=f"Fetch {request.resource_type} data",
                dependencies=["@bheem/dataviz-sdk"],
            ),
        ]

    def _generate_typescript_code(self, request: CodeGenerationRequest, api_key: str) -> list[CodeSnippet]:
        """Generate TypeScript SDK code."""
        masked_key = mask_api_key(api_key)

        code = f'''import BheemDataViz, {{ EmbedOptions, {request.resource_type.title()} }} from '@bheem/dataviz-sdk';

// Initialize SDK
const dataviz = new BheemDataViz({{
  apiKey: '{masked_key}',
  baseUrl: 'https://api.dataviz.bheemkodee.com'
}});

// Embed options
const options: EmbedOptions = {{
  container: '#dataviz-container',
  resourceType: '{request.resource_type}',
  resourceId: '{request.resource_id}',
  width: '100%',
  height: '600px',
  onLoad: (): void => console.log('{request.resource_type} loaded'),
  onError: (error: Error): void => console.error('Error:', error)
}};

// Embed {request.resource_type}
dataviz.embed(options);

// Fetch with types
const data: {request.resource_type.title()} = await dataviz.get{request.resource_type.title()}('{request.resource_id}');'''

        return [
            CodeSnippet(
                language=SDKLanguage.TYPESCRIPT,
                code=code,
                filename="embed.ts",
                description=f"Embed {request.resource_type} with TypeScript types",
                dependencies=["@bheem/dataviz-sdk"],
            ),
        ]

    def _generate_python_code(self, request: CodeGenerationRequest, api_key: str) -> list[CodeSnippet]:
        """Generate Python SDK code."""
        masked_key = mask_api_key(api_key)

        code = f'''from bheem_dataviz import DataVizClient

# Initialize client
client = DataVizClient(
    api_key="{masked_key}",
    base_url="https://api.dataviz.bheemkodee.com"
)

# Get {request.resource_type}
{request.resource_type} = client.{request.resource_type}s.get("{request.resource_id}")
print({request.resource_type}.name)

# Render {request.resource_type} data
data = client.{request.resource_type}s.render("{request.resource_id}")
print(data.to_dataframe())

# Export to various formats
client.{request.resource_type}s.export("{request.resource_id}", format="pdf", path="output.pdf")
client.{request.resource_type}s.export("{request.resource_id}", format="png", path="output.png")'''

        return [
            CodeSnippet(
                language=SDKLanguage.PYTHON,
                code=code,
                filename="example.py",
                description=f"Access {request.resource_type} with Python SDK",
                dependencies=["bheem-dataviz"],
            ),
        ]

    def _generate_react_code(self, request: CodeGenerationRequest, api_key: str) -> list[CodeSnippet]:
        """Generate React component code."""
        masked_key = mask_api_key(api_key)
        component_name = request.resource_type.title()

        code = f'''import React from 'react';
import {{ BheemDataViz{component_name} }} from '@bheem/dataviz-react';

interface Props {{
  filters?: Record<string, unknown>;
}}

export const My{component_name}: React.FC<Props> = ({{ filters }}) => {{
  return (
    <BheemDataViz{component_name}
      apiKey="{masked_key}"
      {request.resource_type}Id="{request.resource_id}"
      width="100%"
      height="600px"
      filters={{filters}}
      onLoad={{() => console.log('Loaded')}}
      onError={{(error) => console.error(error)}}
      onInteraction={{(event) => console.log('Interaction:', event)}}
    />
  );
}};

// Usage
// <My{component_name} filters={{{{ year: 2024 }}}} />'''

        return [
            CodeSnippet(
                language=SDKLanguage.REACT,
                code=code,
                filename=f"My{component_name}.tsx",
                description=f"React component for embedding {request.resource_type}",
                dependencies=["@bheem/dataviz-react", "react"],
            ),
        ]

    def _generate_vue_code(self, request: CodeGenerationRequest, api_key: str) -> list[CodeSnippet]:
        """Generate Vue component code."""
        masked_key = mask_api_key(api_key)

        code = f'''<template>
  <BheemDataViz{request.resource_type.title()}
    api-key="{masked_key}"
    {request.resource_type}-id="{request.resource_id}"
    width="100%"
    height="600px"
    :filters="filters"
    @load="onLoad"
    @error="onError"
    @interaction="onInteraction"
  />
</template>

<script setup lang="ts">
import {{ ref }} from 'vue';
import {{ BheemDataViz{request.resource_type.title()} }} from '@bheem/dataviz-vue';

const filters = ref({{}});

const onLoad = () => console.log('Loaded');
const onError = (error: Error) => console.error(error);
const onInteraction = (event: unknown) => console.log('Interaction:', event);
</script>'''

        return [
            CodeSnippet(
                language=SDKLanguage.VUE,
                code=code,
                filename=f"{request.resource_type.title()}.vue",
                description=f"Vue component for embedding {request.resource_type}",
                dependencies=["@bheem/dataviz-vue", "vue"],
            ),
        ]

    def _generate_curl_code(self, request: CodeGenerationRequest, api_key: str) -> list[CodeSnippet]:
        """Generate cURL examples."""
        masked_key = mask_api_key(api_key)

        get_code = f'''# Get {request.resource_type}
curl -X GET "https://api.dataviz.bheemkodee.com/api/v1/{request.resource_type}s/{request.resource_id}" \\
  -H "Authorization: Bearer {masked_key}" \\
  -H "Content-Type: application/json"'''

        render_code = f'''# Render {request.resource_type} data
curl -X GET "https://api.dataviz.bheemkodee.com/api/v1/{request.resource_type}s/{request.resource_id}/render" \\
  -H "Authorization: Bearer {masked_key}" \\
  -H "Content-Type: application/json"'''

        return [
            CodeSnippet(
                language=SDKLanguage.CURL,
                code=get_code,
                filename=f"get_{request.resource_type}.sh",
                description=f"Get {request.resource_type} details",
            ),
            CodeSnippet(
                language=SDKLanguage.CURL,
                code=render_code,
                filename=f"render_{request.resource_type}.sh",
                description=f"Render {request.resource_type} data",
            ),
        ]

    # API Documentation

    async def get_api_documentation(self) -> APIDocumentation:
        """Get full API documentation."""
        groups = [
            self._get_auth_endpoints(),
            self._get_connections_endpoints(),
            self._get_dashboards_endpoints(),
            self._get_charts_endpoints(),
            self._get_queries_endpoints(),
        ]

        return APIDocumentation(
            title="Bheem DataViz API",
            version="1.0.0",
            description="REST API for Bheem DataViz platform",
            base_url="https://api.dataviz.bheemkodee.com/api/v1",
            auth_description="Use Bearer token authentication with your API key.",
            auth_examples={
                "header": "Authorization: Bearer bv_xxxx_xxxxxxxxx",
            },
            groups=groups,
            sdk_languages=list(SDKLanguage),
            sdk_download_urls={
                "javascript": "https://www.npmjs.com/package/@bheem/dataviz-sdk",
                "python": "https://pypi.org/project/bheem-dataviz/",
            },
        )

    def _get_auth_endpoints(self) -> APIEndpointGroup:
        """Get auth endpoints documentation."""
        return APIEndpointGroup(
            name="Authentication",
            description="Authentication and authorization endpoints",
            category=EndpointCategory.AUTH,
            endpoints=[
                APIEndpoint(
                    path="/auth/login",
                    method="POST",
                    summary="User login",
                    description="Authenticate with email and password",
                    category=EndpointCategory.AUTH,
                    requires_auth=False,
                    rate_limited=True,
                ),
                APIEndpoint(
                    path="/auth/me",
                    method="GET",
                    summary="Get current user",
                    description="Get the authenticated user's profile",
                    category=EndpointCategory.AUTH,
                    requires_auth=True,
                ),
            ],
        )

    def _get_connections_endpoints(self) -> APIEndpointGroup:
        """Get connections endpoints documentation."""
        return APIEndpointGroup(
            name="Data Connections",
            description="Manage database and data source connections",
            category=EndpointCategory.CONNECTIONS,
            endpoints=[
                APIEndpoint(
                    path="/connections",
                    method="GET",
                    summary="List connections",
                    description="Get all data connections for the current user",
                    category=EndpointCategory.CONNECTIONS,
                    required_permissions=["can_read_connections"],
                ),
                APIEndpoint(
                    path="/connections/{id}",
                    method="GET",
                    summary="Get connection",
                    description="Get a specific connection by ID",
                    category=EndpointCategory.CONNECTIONS,
                    path_params=[
                        APIParameter(name="id", type="string", required=True, description="Connection ID"),
                    ],
                    required_permissions=["can_read_connections"],
                ),
            ],
        )

    def _get_dashboards_endpoints(self) -> APIEndpointGroup:
        """Get dashboards endpoints documentation."""
        return APIEndpointGroup(
            name="Dashboards",
            description="Dashboard CRUD and rendering",
            category=EndpointCategory.DASHBOARDS,
            endpoints=[
                APIEndpoint(
                    path="/dashboards",
                    method="GET",
                    summary="List dashboards",
                    category=EndpointCategory.DASHBOARDS,
                    required_permissions=["can_read_dashboards"],
                ),
                APIEndpoint(
                    path="/dashboards/{id}",
                    method="GET",
                    summary="Get dashboard",
                    category=EndpointCategory.DASHBOARDS,
                    path_params=[
                        APIParameter(name="id", type="string", required=True),
                    ],
                    required_permissions=["can_read_dashboards"],
                ),
            ],
        )

    def _get_charts_endpoints(self) -> APIEndpointGroup:
        """Get charts endpoints documentation."""
        return APIEndpointGroup(
            name="Charts",
            description="Chart CRUD and rendering",
            category=EndpointCategory.CHARTS,
            endpoints=[
                APIEndpoint(
                    path="/charts",
                    method="GET",
                    summary="List charts",
                    category=EndpointCategory.CHARTS,
                    required_permissions=["can_read_charts"],
                ),
                APIEndpoint(
                    path="/charts/{id}/render",
                    method="GET",
                    summary="Render chart",
                    description="Execute query and return chart data",
                    category=EndpointCategory.CHARTS,
                    path_params=[
                        APIParameter(name="id", type="string", required=True),
                    ],
                    query_params=[
                        APIParameter(name="filters", type="object", description="Filter parameters"),
                    ],
                    required_permissions=["can_read_charts"],
                ),
            ],
        )

    def _get_queries_endpoints(self) -> APIEndpointGroup:
        """Get queries endpoints documentation."""
        return APIEndpointGroup(
            name="Queries",
            description="SQL query execution",
            category=EndpointCategory.QUERIES,
            endpoints=[
                APIEndpoint(
                    path="/queries/execute",
                    method="POST",
                    summary="Execute SQL query",
                    category=EndpointCategory.QUERIES,
                    required_permissions=["can_execute_queries"],
                ),
            ],
        )
