"""
Compliance & Data Protection API Endpoints

REST API for GDPR compliance, consent management, data subject requests,
retention policies, and privacy controls.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.compliance import (
    ConsentType, ConsentStatus, ConsentRecord, ConsentRequest, ConsentBulkRequest,
    ConsentPreferences, ConsentAuditLog, ConsentListResponse,
    DataSubjectRequest, DataSubjectRequestCreate, DataSubjectRequestUpdate,
    DataSubjectRequestType, DataSubjectRequestStatus, DataSubjectRequestListResponse,
    RetentionPolicy, RetentionPolicyCreate, RetentionPolicyUpdate,
    RetentionExecution, RetentionPolicyListResponse,
    ProcessingActivity, ProcessingActivityCreate, ProcessingActivityListResponse,
    EncryptionConfig, EncryptionConfigUpdate, EncryptionKey,
    PrivacyDocument, PrivacyDocumentCreate, PrivacyDocumentUpdate, PrivacyDocumentListResponse,
    AnonymizationRule, AnonymizationRuleCreate,
    DataBreach, DataBreachCreate, DataBreachUpdate, DataBreachListResponse,
    ComplianceStatus, ComplianceAuditListResponse,
)
from app.services.compliance_service import compliance_service

router = APIRouter()


# Consent Management

@router.get("/users/{user_id}/consent", response_model=ConsentPreferences, tags=["consent"])
async def get_consent_preferences(user_id: str):
    """Get user's consent preferences."""
    return compliance_service.get_consent_preferences(user_id)


@router.post("/users/{user_id}/consent", response_model=ConsentRecord, tags=["consent"])
async def update_consent(
    user_id: str,
    data: ConsentRequest,
    changed_by: Optional[str] = Query(None, description="User who made the change"),
):
    """Update user consent."""
    return compliance_service.update_consent(user_id, data, changed_by)


@router.post("/users/{user_id}/consent/bulk", tags=["consent"])
async def update_consent_bulk(user_id: str, data: ConsentBulkRequest):
    """Update multiple consents at once."""
    results = []
    for consent in data.consents:
        record = compliance_service.update_consent(user_id, consent)
        results.append(record)
    return {"records": results, "total": len(results)}


@router.post("/users/{user_id}/consent/withdraw-all", tags=["consent"])
async def withdraw_all_consent(
    user_id: str,
    ip_address: Optional[str] = Query(None),
):
    """Withdraw all non-essential consent for user."""
    count = compliance_service.withdraw_all_consent(user_id, ip_address)
    return {"success": True, "consents_withdrawn": count}


@router.get("/consent/records", response_model=ConsentListResponse, tags=["consent"])
async def list_consent_records(
    user_id: Optional[str] = Query(None),
    consent_type: Optional[ConsentType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List consent records."""
    return compliance_service.list_consent_records(user_id, consent_type, skip, limit)


@router.get("/consent/audit", tags=["consent"])
async def get_consent_audit_logs(
    user_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get consent audit logs."""
    logs = compliance_service.get_consent_audit_logs(user_id, skip, limit)
    return {"logs": logs, "total": len(logs)}


# Data Subject Requests (GDPR)

@router.post("/dsr", response_model=DataSubjectRequest, tags=["dsr"])
async def create_data_subject_request(
    user_id: str = Query(...),
    data: DataSubjectRequestCreate = ...,
):
    """Create a GDPR data subject request."""
    return compliance_service.create_data_subject_request(user_id, data)


@router.get("/dsr", response_model=DataSubjectRequestListResponse, tags=["dsr"])
async def list_data_subject_requests(
    user_id: Optional[str] = Query(None),
    status: Optional[DataSubjectRequestStatus] = Query(None),
    request_type: Optional[DataSubjectRequestType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List data subject requests."""
    return compliance_service.list_data_subject_requests(
        user_id, status, request_type, skip, limit
    )


@router.get("/dsr/overdue", tags=["dsr"])
async def get_overdue_requests():
    """Get all overdue data subject requests."""
    requests = compliance_service.get_overdue_requests()
    return {"requests": requests, "total": len(requests)}


@router.get("/dsr/{request_id}", response_model=DataSubjectRequest, tags=["dsr"])
async def get_data_subject_request(request_id: str):
    """Get data subject request by ID."""
    request = compliance_service.get_data_subject_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.patch("/dsr/{request_id}", response_model=DataSubjectRequest, tags=["dsr"])
async def update_data_subject_request(
    request_id: str,
    data: DataSubjectRequestUpdate,
    updated_by: str = Query(...),
):
    """Update data subject request."""
    request = compliance_service.update_data_subject_request(request_id, data, updated_by)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


# Retention Policies

@router.post("/retention-policies", response_model=RetentionPolicy, tags=["retention"])
async def create_retention_policy(data: RetentionPolicyCreate):
    """Create a retention policy."""
    return compliance_service.create_retention_policy(data)


@router.get("/retention-policies", response_model=RetentionPolicyListResponse, tags=["retention"])
async def list_retention_policies(
    organization_id: Optional[str] = Query(None),
    data_category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List retention policies."""
    return compliance_service.list_retention_policies(
        organization_id, data_category, skip, limit
    )


@router.get("/retention-policies/{policy_id}", response_model=RetentionPolicy, tags=["retention"])
async def get_retention_policy(policy_id: str):
    """Get retention policy by ID."""
    policy = compliance_service.get_retention_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.patch("/retention-policies/{policy_id}", response_model=RetentionPolicy, tags=["retention"])
async def update_retention_policy(policy_id: str, data: RetentionPolicyUpdate):
    """Update retention policy."""
    policy = compliance_service.update_retention_policy(policy_id, data)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.delete("/retention-policies/{policy_id}", tags=["retention"])
async def delete_retention_policy(policy_id: str):
    """Delete retention policy."""
    if compliance_service.delete_retention_policy(policy_id):
        return {"success": True, "message": "Policy deleted"}
    raise HTTPException(status_code=404, detail="Policy not found")


@router.post("/retention-policies/{policy_id}/execute", response_model=RetentionExecution, tags=["retention"])
async def execute_retention_policy(policy_id: str):
    """Execute a retention policy."""
    execution = compliance_service.execute_retention_policy(policy_id)
    if not execution:
        raise HTTPException(status_code=400, detail="Cannot execute policy (disabled, legal hold, or not found)")
    return execution


# Processing Activities (GDPR Article 30)

@router.post("/organizations/{org_id}/processing-activities", response_model=ProcessingActivity, tags=["processing"])
async def create_processing_activity(org_id: str, data: ProcessingActivityCreate):
    """Create processing activity record."""
    return compliance_service.create_processing_activity(org_id, data)


@router.get("/organizations/{org_id}/processing-activities", response_model=ProcessingActivityListResponse, tags=["processing"])
async def list_processing_activities(
    org_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List processing activities."""
    return compliance_service.list_processing_activities(org_id, skip, limit)


@router.get("/processing-activities/{activity_id}", response_model=ProcessingActivity, tags=["processing"])
async def get_processing_activity(activity_id: str):
    """Get processing activity by ID."""
    activity = compliance_service.get_processing_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


# Encryption

@router.get("/organizations/{org_id}/encryption", response_model=EncryptionConfig, tags=["encryption"])
async def get_encryption_config(org_id: str):
    """Get encryption configuration."""
    return compliance_service.get_encryption_config(org_id)


@router.patch("/organizations/{org_id}/encryption", response_model=EncryptionConfig, tags=["encryption"])
async def update_encryption_config(org_id: str, data: EncryptionConfigUpdate):
    """Update encryption configuration."""
    return compliance_service.update_encryption_config(org_id, data)


@router.post("/organizations/{org_id}/encryption/keys", response_model=EncryptionKey, tags=["encryption"])
async def create_encryption_key(
    org_id: str,
    name: str = Query(...),
    purpose: str = Query(...),
):
    """Create a new encryption key."""
    return compliance_service.create_encryption_key(org_id, name, purpose)


@router.get("/organizations/{org_id}/encryption/keys", tags=["encryption"])
async def list_encryption_keys(org_id: str):
    """List encryption keys."""
    keys = compliance_service.list_encryption_keys(org_id)
    return {"keys": keys, "total": len(keys)}


# Privacy Documents

@router.post("/privacy-documents", response_model=PrivacyDocument, tags=["privacy"])
async def create_privacy_document(data: PrivacyDocumentCreate):
    """Create privacy document."""
    return compliance_service.create_privacy_document(data)


@router.get("/privacy-documents", response_model=PrivacyDocumentListResponse, tags=["privacy"])
async def list_privacy_documents(
    document_type: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    published_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List privacy documents."""
    return compliance_service.list_privacy_documents(
        document_type, organization_id, published_only, skip, limit
    )


@router.get("/privacy-documents/current", response_model=PrivacyDocument, tags=["privacy"])
async def get_current_privacy_document(
    document_type: str = Query(...),
    organization_id: Optional[str] = Query(None),
    locale: str = Query("en"),
):
    """Get current published privacy document."""
    document = compliance_service.get_current_privacy_document(
        document_type, organization_id, locale
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/privacy-documents/{doc_id}", response_model=PrivacyDocument, tags=["privacy"])
async def get_privacy_document(doc_id: str):
    """Get privacy document by ID."""
    document = compliance_service.get_privacy_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/privacy-documents/{doc_id}/publish", response_model=PrivacyDocument, tags=["privacy"])
async def publish_privacy_document(doc_id: str):
    """Publish privacy document."""
    document = compliance_service.publish_privacy_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


# Anonymization

@router.post("/anonymization-rules", response_model=AnonymizationRule, tags=["anonymization"])
async def create_anonymization_rule(data: AnonymizationRuleCreate):
    """Create anonymization rule."""
    return compliance_service.create_anonymization_rule(data)


@router.get("/anonymization-rules", tags=["anonymization"])
async def list_anonymization_rules(
    organization_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List anonymization rules."""
    rules = compliance_service.list_anonymization_rules(organization_id, skip, limit)
    return {"rules": rules, "total": len(rules)}


# Data Breaches

@router.post("/organizations/{org_id}/breaches", response_model=DataBreach, tags=["breaches"])
async def report_data_breach(org_id: str, data: DataBreachCreate):
    """Report a data breach."""
    return compliance_service.report_data_breach(org_id, data)


@router.get("/organizations/{org_id}/breaches", response_model=DataBreachListResponse, tags=["breaches"])
async def list_data_breaches(
    org_id: str,
    resolved: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List data breaches."""
    return compliance_service.list_data_breaches(org_id, resolved, skip, limit)


@router.get("/breaches/{breach_id}", response_model=DataBreach, tags=["breaches"])
async def get_data_breach(breach_id: str):
    """Get data breach by ID."""
    breach = compliance_service.get_data_breach(breach_id)
    if not breach:
        raise HTTPException(status_code=404, detail="Breach not found")
    return breach


@router.patch("/breaches/{breach_id}", response_model=DataBreach, tags=["breaches"])
async def update_data_breach(breach_id: str, data: DataBreachUpdate):
    """Update data breach."""
    breach = compliance_service.update_data_breach(breach_id, data)
    if not breach:
        raise HTTPException(status_code=404, detail="Breach not found")
    return breach


# Compliance Status

@router.get("/organizations/{org_id}/status", response_model=ComplianceStatus, tags=["compliance"])
async def get_compliance_status(org_id: str):
    """Get overall compliance status."""
    return compliance_service.get_compliance_status(org_id)


@router.get("/audit-logs", response_model=ComplianceAuditListResponse, tags=["compliance"])
async def list_compliance_audit_logs(
    resource_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List compliance audit logs."""
    return compliance_service.list_compliance_audit_logs(
        resource_type, user_id, skip, limit
    )


# User Data (GDPR Rights)

@router.get("/users/{user_id}/export", tags=["user-data"])
async def export_user_data(user_id: str):
    """Export all user data (GDPR portability)."""
    return compliance_service.export_user_data(user_id)


@router.delete("/users/{user_id}/data", tags=["user-data"])
async def delete_user_data(user_id: str):
    """Delete all user data (GDPR erasure / right to be forgotten)."""
    result = compliance_service.delete_user_data(user_id)
    return {"success": True, "deleted": result}
