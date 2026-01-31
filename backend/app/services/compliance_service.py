"""
Compliance & Data Protection Service

Service for GDPR compliance, data retention, consent management,
data subject requests, and privacy controls.
"""

import secrets
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List, Any

from app.schemas.compliance import (
    ConsentType, ConsentStatus, ConsentRecord, ConsentRequest,
    ConsentPreferences, ConsentAuditLog, ConsentListResponse,
    DataSubjectRequest, DataSubjectRequestCreate, DataSubjectRequestUpdate,
    DataSubjectRequestType, DataSubjectRequestStatus, DataSubjectRequestListResponse,
    RetentionPolicy, RetentionPolicyCreate, RetentionPolicyUpdate,
    RetentionAction, RetentionExecution, RetentionPolicyListResponse,
    ProcessingActivity, ProcessingActivityCreate, ProcessingActivityListResponse,
    EncryptionKey, EncryptionConfig, EncryptionConfigUpdate, EncryptionAlgorithm,
    PrivacyDocument, PrivacyDocumentCreate, PrivacyDocumentUpdate, PrivacyDocumentListResponse,
    AnonymizationRule, AnonymizationRuleCreate, AnonymizationExecution,
    DataBreach, DataBreachCreate, DataBreachUpdate, DataBreachListResponse,
    ComplianceStatus, ComplianceAuditLog, ComplianceAuditListResponse,
    DataClassification, LegalBasis,
    GDPR_RESPONSE_DAYS, GDPR_EXTENSION_DAYS, calculate_dsr_deadline, is_dsr_overdue,
    calculate_compliance_score,
)


class ComplianceService:
    """Service for compliance and data protection."""

    def __init__(self):
        # In-memory stores (use database in production)
        self._consent_records: Dict[str, ConsentRecord] = {}
        self._consent_preferences: Dict[str, ConsentPreferences] = {}
        self._consent_audit_logs: List[ConsentAuditLog] = []
        self._data_subject_requests: Dict[str, DataSubjectRequest] = {}
        self._retention_policies: Dict[str, RetentionPolicy] = {}
        self._retention_executions: List[RetentionExecution] = []
        self._processing_activities: Dict[str, ProcessingActivity] = {}
        self._encryption_configs: Dict[str, EncryptionConfig] = {}
        self._encryption_keys: Dict[str, EncryptionKey] = {}
        self._privacy_documents: Dict[str, PrivacyDocument] = {}
        self._anonymization_rules: Dict[str, AnonymizationRule] = {}
        self._data_breaches: Dict[str, DataBreach] = {}
        self._compliance_audit_logs: List[ComplianceAuditLog] = []

        # Initialize default retention policies
        self._init_default_policies()

    def _init_default_policies(self):
        """Initialize default retention policies."""
        defaults = [
            RetentionPolicy(
                id="default-logs",
                name="Application Logs",
                description="Retention for application and access logs",
                data_category="logs",
                classification=DataClassification.INTERNAL,
                retention_days=90,
                action=RetentionAction.DELETE,
                legal_basis=LegalBasis.LEGITIMATE_INTERESTS,
            ),
            RetentionPolicy(
                id="default-analytics",
                name="Analytics Data",
                description="Retention for analytics and usage data",
                data_category="analytics",
                classification=DataClassification.INTERNAL,
                retention_days=365,
                action=RetentionAction.ANONYMIZE,
                legal_basis=LegalBasis.CONSENT,
            ),
        ]
        for policy in defaults:
            self._retention_policies[policy.id] = policy

    # Consent Management

    def get_consent_preferences(self, user_id: str) -> ConsentPreferences:
        """Get user's consent preferences."""
        if user_id not in self._consent_preferences:
            self._consent_preferences[user_id] = ConsentPreferences(user_id=user_id)
        return self._consent_preferences[user_id]

    def update_consent(
        self,
        user_id: str,
        request: ConsentRequest,
        changed_by: Optional[str] = None,
    ) -> ConsentRecord:
        """Update user consent."""
        record_id = f"consent-{secrets.token_hex(8)}"
        now = datetime.utcnow()

        # Get previous status for audit
        preferences = self.get_consent_preferences(user_id)
        previous_status = getattr(preferences, request.consent_type.value, None)

        # Create consent record
        record = ConsentRecord(
            id=record_id,
            user_id=user_id,
            consent_type=request.consent_type,
            status=request.status,
            version=request.version,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            source=request.source,
            granted_at=now if request.status == ConsentStatus.GRANTED else None,
            withdrawn_at=now if request.status == ConsentStatus.WITHDRAWN else None,
        )

        self._consent_records[record_id] = record

        # Update preferences
        if request.consent_type == ConsentType.MARKETING:
            preferences.marketing = request.status
        elif request.consent_type == ConsentType.ANALYTICS:
            preferences.analytics = request.status
        elif request.consent_type == ConsentType.THIRD_PARTY:
            preferences.third_party = request.status
        elif request.consent_type == ConsentType.PERSONALIZATION:
            preferences.personalization = request.status
        elif request.consent_type == ConsentType.TERMS_OF_SERVICE:
            preferences.terms_accepted = request.status == ConsentStatus.GRANTED
            preferences.terms_version = request.version
        elif request.consent_type == ConsentType.PRIVACY_POLICY:
            preferences.privacy_accepted = request.status == ConsentStatus.GRANTED
            preferences.privacy_version = request.version

        preferences.last_updated = now

        # Create audit log
        audit_log = ConsentAuditLog(
            id=f"audit-{secrets.token_hex(8)}",
            user_id=user_id,
            consent_type=request.consent_type,
            previous_status=previous_status if isinstance(previous_status, ConsentStatus) else None,
            new_status=request.status,
            changed_by=changed_by or user_id,
            ip_address=request.ip_address,
        )
        self._consent_audit_logs.append(audit_log)

        return record

    def withdraw_all_consent(self, user_id: str, ip_address: Optional[str] = None) -> int:
        """Withdraw all non-essential consent for user."""
        count = 0
        consent_types = [
            ConsentType.MARKETING,
            ConsentType.ANALYTICS,
            ConsentType.THIRD_PARTY,
            ConsentType.PERSONALIZATION,
        ]

        for consent_type in consent_types:
            request = ConsentRequest(
                consent_type=consent_type,
                status=ConsentStatus.WITHDRAWN,
                version="withdrawal",
                ip_address=ip_address,
                source="user_request",
            )
            self.update_consent(user_id, request)
            count += 1

        return count

    def list_consent_records(
        self,
        user_id: Optional[str] = None,
        consent_type: Optional[ConsentType] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ConsentListResponse:
        """List consent records."""
        records = list(self._consent_records.values())

        if user_id:
            records = [r for r in records if r.user_id == user_id]
        if consent_type:
            records = [r for r in records if r.consent_type == consent_type]

        records.sort(key=lambda r: r.created_at, reverse=True)
        return ConsentListResponse(
            records=records[skip:skip + limit],
            total=len(records),
        )

    def get_consent_audit_logs(
        self,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ConsentAuditLog]:
        """Get consent audit logs."""
        logs = self._consent_audit_logs

        if user_id:
            logs = [l for l in logs if l.user_id == user_id]

        logs = sorted(logs, key=lambda l: l.created_at, reverse=True)
        return logs[skip:skip + limit]

    # Data Subject Requests

    def create_data_subject_request(
        self,
        user_id: str,
        data: DataSubjectRequestCreate,
    ) -> DataSubjectRequest:
        """Create a GDPR data subject request."""
        request_id = f"dsr-{secrets.token_hex(8)}"
        now = datetime.utcnow()

        request = DataSubjectRequest(
            id=request_id,
            user_id=user_id,
            request_type=data.request_type,
            status=DataSubjectRequestStatus.PENDING,
            email=data.email,
            description=data.description,
            data_categories=data.data_categories,
            response_deadline=calculate_dsr_deadline(now),
        )

        self._data_subject_requests[request_id] = request

        # Log compliance action
        self._log_compliance_action(
            action="dsr_created",
            resource_type="data_subject_request",
            resource_id=request_id,
            user_id=user_id,
            details={"request_type": data.request_type.value},
        )

        return request

    def get_data_subject_request(self, request_id: str) -> Optional[DataSubjectRequest]:
        """Get data subject request by ID."""
        return self._data_subject_requests.get(request_id)

    def update_data_subject_request(
        self,
        request_id: str,
        data: DataSubjectRequestUpdate,
        updated_by: str,
    ) -> Optional[DataSubjectRequest]:
        """Update data subject request."""
        request = self._data_subject_requests.get(request_id)
        if not request:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Handle status changes
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status in [DataSubjectRequestStatus.COMPLETED, DataSubjectRequestStatus.REJECTED]:
                request.completed_at = datetime.utcnow()

        # Handle identity verification
        if update_data.get("identity_verified"):
            request.verified_at = datetime.utcnow()

        # Handle extension
        if update_data.get("response_extended"):
            request.response_deadline = calculate_dsr_deadline(request.created_at, extended=True)

        for key, value in update_data.items():
            setattr(request, key, value)

        request.updated_at = datetime.utcnow()

        # Log compliance action
        self._log_compliance_action(
            action="dsr_updated",
            resource_type="data_subject_request",
            resource_id=request_id,
            user_id=updated_by,
            details=update_data,
        )

        return request

    def list_data_subject_requests(
        self,
        user_id: Optional[str] = None,
        status: Optional[DataSubjectRequestStatus] = None,
        request_type: Optional[DataSubjectRequestType] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> DataSubjectRequestListResponse:
        """List data subject requests."""
        requests = list(self._data_subject_requests.values())

        if user_id:
            requests = [r for r in requests if r.user_id == user_id]
        if status:
            requests = [r for r in requests if r.status == status]
        if request_type:
            requests = [r for r in requests if r.request_type == request_type]

        requests.sort(key=lambda r: r.created_at, reverse=True)
        return DataSubjectRequestListResponse(
            requests=requests[skip:skip + limit],
            total=len(requests),
        )

    def get_overdue_requests(self) -> List[DataSubjectRequest]:
        """Get all overdue DSRs."""
        return [r for r in self._data_subject_requests.values() if is_dsr_overdue(r)]

    # Retention Policies

    def create_retention_policy(self, data: RetentionPolicyCreate) -> RetentionPolicy:
        """Create a retention policy."""
        policy_id = f"retention-{secrets.token_hex(8)}"

        policy = RetentionPolicy(
            id=policy_id,
            **data.model_dump(),
        )

        self._retention_policies[policy_id] = policy
        return policy

    def get_retention_policy(self, policy_id: str) -> Optional[RetentionPolicy]:
        """Get retention policy by ID."""
        return self._retention_policies.get(policy_id)

    def update_retention_policy(self, policy_id: str, data: RetentionPolicyUpdate) -> Optional[RetentionPolicy]:
        """Update retention policy."""
        policy = self._retention_policies.get(policy_id)
        if not policy:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(policy, key, value)
        policy.updated_at = datetime.utcnow()

        return policy

    def delete_retention_policy(self, policy_id: str) -> bool:
        """Delete retention policy."""
        if policy_id in self._retention_policies:
            del self._retention_policies[policy_id]
            return True
        return False

    def list_retention_policies(
        self,
        organization_id: Optional[str] = None,
        data_category: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> RetentionPolicyListResponse:
        """List retention policies."""
        policies = list(self._retention_policies.values())

        if organization_id:
            policies = [p for p in policies if p.organization_id == organization_id or p.organization_id is None]
        if data_category:
            policies = [p for p in policies if p.data_category == data_category]

        policies.sort(key=lambda p: p.name)
        return RetentionPolicyListResponse(
            policies=policies[skip:skip + limit],
            total=len(policies),
        )

    def execute_retention_policy(self, policy_id: str) -> Optional[RetentionExecution]:
        """Execute a retention policy (simulation)."""
        policy = self._retention_policies.get(policy_id)
        if not policy or not policy.enabled or policy.legal_hold:
            return None

        execution = RetentionExecution(
            id=f"exec-{secrets.token_hex(8)}",
            policy_id=policy_id,
            policy_name=policy.name,
            action=policy.action,
            records_affected=0,  # Would be calculated in real execution
            records_processed=100,
            records_failed=0,
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=0.5,
        )

        self._retention_executions.append(execution)
        policy.last_executed_at = datetime.utcnow()
        policy.next_execution_at = datetime.utcnow() + timedelta(days=1)

        return execution

    # Processing Activities

    def create_processing_activity(
        self,
        organization_id: str,
        data: ProcessingActivityCreate,
    ) -> ProcessingActivity:
        """Create processing activity record."""
        activity_id = f"activity-{secrets.token_hex(8)}"

        activity = ProcessingActivity(
            id=activity_id,
            organization_id=organization_id,
            **data.model_dump(),
        )

        self._processing_activities[activity_id] = activity
        return activity

    def get_processing_activity(self, activity_id: str) -> Optional[ProcessingActivity]:
        """Get processing activity by ID."""
        return self._processing_activities.get(activity_id)

    def list_processing_activities(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> ProcessingActivityListResponse:
        """List processing activities."""
        activities = [
            a for a in self._processing_activities.values()
            if a.organization_id == organization_id
        ]
        activities.sort(key=lambda a: a.name)
        return ProcessingActivityListResponse(
            activities=activities[skip:skip + limit],
            total=len(activities),
        )

    # Encryption Configuration

    def get_encryption_config(self, organization_id: str) -> EncryptionConfig:
        """Get encryption configuration."""
        if organization_id not in self._encryption_configs:
            self._encryption_configs[organization_id] = EncryptionConfig(
                organization_id=organization_id
            )
        return self._encryption_configs[organization_id]

    def update_encryption_config(
        self,
        organization_id: str,
        data: EncryptionConfigUpdate,
    ) -> EncryptionConfig:
        """Update encryption configuration."""
        config = self.get_encryption_config(organization_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(config, key, value)
        config.updated_at = datetime.utcnow()
        return config

    def create_encryption_key(
        self,
        organization_id: str,
        name: str,
        purpose: str,
    ) -> EncryptionKey:
        """Create a new encryption key."""
        config = self.get_encryption_config(organization_id)

        key = EncryptionKey(
            id=f"key-{secrets.token_hex(8)}",
            name=name,
            algorithm=config.default_algorithm,
            key_size=256,
            purpose=purpose,
            status="active",
            version=1,
            created_at=datetime.utcnow(),
            organization_id=organization_id,
        )

        self._encryption_keys[key.id] = key
        return key

    def list_encryption_keys(self, organization_id: str) -> List[EncryptionKey]:
        """List encryption keys for organization."""
        return [
            k for k in self._encryption_keys.values()
            if k.organization_id == organization_id
        ]

    # Privacy Documents

    def create_privacy_document(self, data: PrivacyDocumentCreate) -> PrivacyDocument:
        """Create privacy document."""
        doc_id = f"doc-{secrets.token_hex(8)}"

        document = PrivacyDocument(
            id=doc_id,
            **data.model_dump(),
        )

        self._privacy_documents[doc_id] = document
        return document

    def get_privacy_document(self, doc_id: str) -> Optional[PrivacyDocument]:
        """Get privacy document by ID."""
        return self._privacy_documents.get(doc_id)

    def get_current_privacy_document(
        self,
        document_type: str,
        organization_id: Optional[str] = None,
        locale: str = "en",
    ) -> Optional[PrivacyDocument]:
        """Get current published privacy document."""
        documents = [
            d for d in self._privacy_documents.values()
            if d.document_type == document_type and
               d.published and
               (d.organization_id == organization_id or d.organization_id is None) and
               d.locale == locale
        ]

        if not documents:
            return None

        # Return most recent by effective date
        return max(documents, key=lambda d: d.effective_date)

    def publish_privacy_document(self, doc_id: str) -> Optional[PrivacyDocument]:
        """Publish privacy document."""
        document = self._privacy_documents.get(doc_id)
        if not document:
            return None

        document.published = True
        document.published_at = datetime.utcnow()
        return document

    def list_privacy_documents(
        self,
        document_type: Optional[str] = None,
        organization_id: Optional[str] = None,
        published_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> PrivacyDocumentListResponse:
        """List privacy documents."""
        documents = list(self._privacy_documents.values())

        if document_type:
            documents = [d for d in documents if d.document_type == document_type]
        if organization_id:
            documents = [d for d in documents if d.organization_id == organization_id]
        if published_only:
            documents = [d for d in documents if d.published]

        documents.sort(key=lambda d: d.effective_date, reverse=True)
        return PrivacyDocumentListResponse(
            documents=documents[skip:skip + limit],
            total=len(documents),
        )

    # Anonymization

    def create_anonymization_rule(self, data: AnonymizationRuleCreate) -> AnonymizationRule:
        """Create anonymization rule."""
        rule_id = f"anon-{secrets.token_hex(8)}"

        rule = AnonymizationRule(
            id=rule_id,
            **data.model_dump(),
        )

        self._anonymization_rules[rule_id] = rule
        return rule

    def list_anonymization_rules(
        self,
        organization_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[AnonymizationRule]:
        """List anonymization rules."""
        rules = list(self._anonymization_rules.values())

        if organization_id:
            rules = [r for r in rules if r.organization_id == organization_id]

        return rules[skip:skip + limit]

    # Data Breaches

    def report_data_breach(
        self,
        organization_id: str,
        data: DataBreachCreate,
    ) -> DataBreach:
        """Report a data breach."""
        breach_id = f"breach-{secrets.token_hex(8)}"

        breach = DataBreach(
            id=breach_id,
            organization_id=organization_id,
            **data.model_dump(),
        )

        self._data_breaches[breach_id] = breach

        # Log compliance action
        self._log_compliance_action(
            action="breach_reported",
            resource_type="data_breach",
            resource_id=breach_id,
            user_id="system",
            details={"severity": data.severity, "affected_users": data.affected_users},
        )

        return breach

    def get_data_breach(self, breach_id: str) -> Optional[DataBreach]:
        """Get data breach by ID."""
        return self._data_breaches.get(breach_id)

    def update_data_breach(
        self,
        breach_id: str,
        data: DataBreachUpdate,
    ) -> Optional[DataBreach]:
        """Update data breach."""
        breach = self._data_breaches.get(breach_id)
        if not breach:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(breach, key, value)
        breach.updated_at = datetime.utcnow()

        return breach

    def list_data_breaches(
        self,
        organization_id: str,
        resolved: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> DataBreachListResponse:
        """List data breaches."""
        breaches = [
            b for b in self._data_breaches.values()
            if b.organization_id == organization_id
        ]

        if resolved is not None:
            if resolved:
                breaches = [b for b in breaches if b.resolved_date is not None]
            else:
                breaches = [b for b in breaches if b.resolved_date is None]

        breaches.sort(key=lambda b: b.discovery_date, reverse=True)
        return DataBreachListResponse(
            breaches=breaches[skip:skip + limit],
            total=len(breaches),
        )

    # Compliance Status

    def get_compliance_status(self, organization_id: str) -> ComplianceStatus:
        """Get overall compliance status."""
        # Count DSRs
        dsrs = [r for r in self._data_subject_requests.values()]
        pending_dsrs = len([r for r in dsrs if r.status == DataSubjectRequestStatus.PENDING])
        overdue_dsrs = len([r for r in dsrs if is_dsr_overdue(r)])

        # Count policies
        policies = [
            p for p in self._retention_policies.values()
            if p.organization_id == organization_id or p.organization_id is None
        ]
        active_policies = len([p for p in policies if p.enabled])

        # Count processing activities
        activities = len([
            a for a in self._processing_activities.values()
            if a.organization_id == organization_id
        ])

        # Count breaches
        open_breaches = len([
            b for b in self._data_breaches.values()
            if b.organization_id == organization_id and b.resolved_date is None
        ])

        # Check encryption
        encryption_config = self.get_encryption_config(organization_id)

        status = ComplianceStatus(
            organization_id=organization_id,
            gdpr_compliant=True,  # Simplified check
            consent_coverage=0.85,  # Would calculate from user data
            pending_dsr_count=pending_dsrs,
            overdue_dsr_count=overdue_dsrs,
            retention_policies_active=active_policies,
            retention_policies_executed_today=0,
            processing_activities_count=activities,
            data_breaches_open=open_breaches,
            encryption_enabled=encryption_config.encrypt_at_rest,
            compliance_score=0,  # Calculated below
        )

        status.compliance_score = calculate_compliance_score(status)
        return status

    # Compliance Audit Logs

    def _log_compliance_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        ip_address: str = "127.0.0.1",
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log compliance-related action."""
        log = ComplianceAuditLog(
            id=f"log-{secrets.token_hex(8)}",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email="",  # Would be fetched in production
            ip_address=ip_address,
            details=details or {},
        )
        self._compliance_audit_logs.append(log)

        # Keep only last 10000 logs in memory
        if len(self._compliance_audit_logs) > 10000:
            self._compliance_audit_logs = self._compliance_audit_logs[-10000:]

    def list_compliance_audit_logs(
        self,
        resource_type: Optional[str] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ComplianceAuditListResponse:
        """List compliance audit logs."""
        logs = self._compliance_audit_logs

        if resource_type:
            logs = [l for l in logs if l.resource_type == resource_type]
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]

        logs = sorted(logs, key=lambda l: l.created_at, reverse=True)
        return ComplianceAuditListResponse(
            logs=logs[skip:skip + limit],
            total=len(logs),
        )

    # User Data Export (GDPR Portability)

    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR portability."""
        return {
            "user_id": user_id,
            "export_date": datetime.utcnow().isoformat(),
            "consent_preferences": self.get_consent_preferences(user_id).model_dump(),
            "consent_records": [
                r.model_dump() for r in self._consent_records.values()
                if r.user_id == user_id
            ],
            "data_subject_requests": [
                r.model_dump() for r in self._data_subject_requests.values()
                if r.user_id == user_id
            ],
            # Additional data would be gathered from other services
        }

    # User Data Deletion (GDPR Erasure)

    def delete_user_data(self, user_id: str) -> Dict[str, int]:
        """Delete all user data for GDPR erasure."""
        deleted = {
            "consent_records": 0,
            "consent_preferences": 0,
            "audit_logs": 0,
        }

        # Delete consent records
        to_delete = [
            rid for rid, r in self._consent_records.items()
            if r.user_id == user_id
        ]
        for rid in to_delete:
            del self._consent_records[rid]
            deleted["consent_records"] += 1

        # Delete consent preferences
        if user_id in self._consent_preferences:
            del self._consent_preferences[user_id]
            deleted["consent_preferences"] += 1

        # Anonymize audit logs (don't delete for compliance)
        for log in self._consent_audit_logs:
            if log.user_id == user_id:
                log.user_id = "deleted_user"
                deleted["audit_logs"] += 1

        return deleted


# Create singleton instance
compliance_service = ComplianceService()
