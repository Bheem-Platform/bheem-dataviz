"""
Security Audit & Monitoring API Endpoints

REST API for security auditing, threat detection, anomaly detection,
vulnerability management, and security incident management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.schemas.security_audit import (
    AuditLog, AuditLogCreate, AuditLogListResponse,
    AuditCategory, AuditSeverity,
    ThreatIndicator, ThreatIndicatorCreate,
    ThreatDetection, ThreatDetectionListResponse,
    ThreatType, ThreatSeverity, ThreatStatus,
    DetectedAnomaly, AnomalyListResponse, AnomalyType,
    SecurityIncident, SecurityIncidentCreate, SecurityIncidentUpdate,
    SecurityIncidentListResponse, IncidentStatus, IncidentPriority,
    Vulnerability, VulnerabilityCreate, VulnerabilityUpdate,
    VulnerabilityListResponse, VulnerabilitySeverity, VulnerabilityStatus,
    SecurityMetrics, SecurityScorecard,
    SecurityAlert, SecurityAlertListResponse,
)
from app.services.security_audit_service import security_audit_service

router = APIRouter()


# Audit Logs

@router.post("/audit-logs", response_model=AuditLog, tags=["audit-logs"])
async def create_audit_log(data: AuditLogCreate):
    """Create an audit log entry."""
    return security_audit_service.create_audit_log(data)


@router.get("/audit-logs", response_model=AuditLogListResponse, tags=["audit-logs"])
async def list_audit_logs(
    category: Optional[AuditCategory] = Query(None),
    severity: Optional[AuditSeverity] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
    success: Optional[bool] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List audit logs with filtering."""
    from app.schemas.security_audit import AuditLogFilter
    filter = AuditLogFilter(
        category=category,
        severity=severity,
        action=action,
        resource_type=resource_type,
        user_id=user_id,
        organization_id=organization_id,
        ip_address=ip_address,
        success=success,
        start_time=start_time,
        end_time=end_time,
    )
    return security_audit_service.list_audit_logs(filter, skip, limit)


@router.get("/audit-logs/{log_id}", response_model=AuditLog, tags=["audit-logs"])
async def get_audit_log(log_id: str):
    """Get audit log by ID."""
    log = security_audit_service.get_audit_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log


# Threat Intelligence

@router.post("/threat-indicators", response_model=ThreatIndicator, tags=["threat-intelligence"])
async def create_threat_indicator(data: ThreatIndicatorCreate):
    """Create threat indicator."""
    return security_audit_service.create_threat_indicator(data)


@router.get("/threat-indicators", tags=["threat-intelligence"])
async def list_threat_indicators(
    threat_type: Optional[ThreatType] = Query(None),
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List threat indicators."""
    indicators = security_audit_service.list_threat_indicators(
        threat_type, active_only, skip, limit
    )
    return {"indicators": indicators, "total": len(indicators)}


@router.get("/threat-indicators/{indicator_id}", response_model=ThreatIndicator, tags=["threat-intelligence"])
async def get_threat_indicator(indicator_id: str):
    """Get threat indicator by ID."""
    indicator = security_audit_service.get_threat_indicator(indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Threat indicator not found")
    return indicator


@router.post("/threat-indicators/check", tags=["threat-intelligence"])
async def check_indicator(
    indicator_type: str = Query(..., description="Type: ip, domain, hash, email"),
    value: str = Query(...),
):
    """Check if value matches any threat indicator."""
    indicator = security_audit_service.check_indicator(indicator_type, value)
    return {
        "matched": indicator is not None,
        "indicator": indicator,
    }


# Threat Detection

@router.get("/threats", response_model=ThreatDetectionListResponse, tags=["threat-detection"])
async def list_threat_detections(
    organization_id: Optional[str] = Query(None),
    status: Optional[ThreatStatus] = Query(None),
    severity: Optional[ThreatSeverity] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List threat detections."""
    return security_audit_service.list_threat_detections(
        organization_id, status, severity, skip, limit
    )


@router.get("/threats/{detection_id}", response_model=ThreatDetection, tags=["threat-detection"])
async def get_threat_detection(detection_id: str):
    """Get threat detection by ID."""
    detection = security_audit_service.get_threat_detection(detection_id)
    if not detection:
        raise HTTPException(status_code=404, detail="Threat detection not found")
    return detection


@router.patch("/threats/{detection_id}", response_model=ThreatDetection, tags=["threat-detection"])
async def update_threat_detection(
    detection_id: str,
    status: Optional[ThreatStatus] = Query(None),
    assigned_to: Optional[str] = Query(None),
    resolution_notes: Optional[str] = Query(None),
):
    """Update threat detection."""
    detection = security_audit_service.update_threat_detection(
        detection_id, status, assigned_to, resolution_notes
    )
    if not detection:
        raise HTTPException(status_code=404, detail="Threat detection not found")
    return detection


# Anomaly Detection

@router.post("/anomalies", response_model=DetectedAnomaly, tags=["anomaly-detection"])
async def detect_anomaly(
    anomaly_type: AnomalyType = Query(...),
    description: str = Query(...),
    actual_value: str = Query(...),
    deviation_score: float = Query(..., ge=0),
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
    expected_value: Optional[str] = Query(None),
):
    """Record detected anomaly."""
    return security_audit_service.detect_anomaly(
        anomaly_type=anomaly_type,
        description=description,
        actual_value=actual_value,
        deviation_score=deviation_score,
        user_id=user_id,
        organization_id=organization_id,
        ip_address=ip_address,
        expected_value=expected_value,
    )


@router.get("/anomalies", response_model=AnomalyListResponse, tags=["anomaly-detection"])
async def list_anomalies(
    organization_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    anomaly_type: Optional[AnomalyType] = Query(None),
    investigated: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List detected anomalies."""
    return security_audit_service.list_anomalies(
        organization_id, user_id, anomaly_type, investigated, skip, limit
    )


@router.post("/anomalies/{anomaly_id}/investigate", response_model=DetectedAnomaly, tags=["anomaly-detection"])
async def investigate_anomaly(
    anomaly_id: str,
    investigated_by: str = Query(...),
    false_positive: bool = Query(False),
):
    """Mark anomaly as investigated."""
    anomaly = security_audit_service.investigate_anomaly(
        anomaly_id, investigated_by, false_positive
    )
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly


# Security Incidents

@router.post("/incidents", response_model=SecurityIncident, tags=["security-incidents"])
async def create_incident(
    data: SecurityIncidentCreate,
    reported_by: str = Query(...),
):
    """Create security incident."""
    return security_audit_service.create_incident(data, reported_by)


@router.get("/incidents", response_model=SecurityIncidentListResponse, tags=["security-incidents"])
async def list_incidents(
    organization_id: Optional[str] = Query(None),
    status: Optional[IncidentStatus] = Query(None),
    priority: Optional[IncidentPriority] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List security incidents."""
    return security_audit_service.list_incidents(
        organization_id, status, priority, skip, limit
    )


@router.get("/incidents/{incident_id}", response_model=SecurityIncident, tags=["security-incidents"])
async def get_incident(incident_id: str):
    """Get security incident by ID."""
    incident = security_audit_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/incidents/{incident_id}", response_model=SecurityIncident, tags=["security-incidents"])
async def update_incident(
    incident_id: str,
    data: SecurityIncidentUpdate,
    updated_by: str = Query(...),
):
    """Update security incident."""
    incident = security_audit_service.update_incident(incident_id, data, updated_by)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/incidents/{incident_id}/notes", response_model=SecurityIncident, tags=["security-incidents"])
async def add_incident_note(
    incident_id: str,
    note: str = Query(...),
    user: str = Query(...),
):
    """Add note to incident timeline."""
    incident = security_audit_service.add_incident_note(incident_id, note, user)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


# Vulnerability Management

@router.post("/vulnerabilities", response_model=Vulnerability, tags=["vulnerability-management"])
async def create_vulnerability(data: VulnerabilityCreate):
    """Create vulnerability record."""
    return security_audit_service.create_vulnerability(data)


@router.get("/vulnerabilities", response_model=VulnerabilityListResponse, tags=["vulnerability-management"])
async def list_vulnerabilities(
    organization_id: Optional[str] = Query(None),
    status: Optional[VulnerabilityStatus] = Query(None),
    severity: Optional[VulnerabilitySeverity] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List vulnerabilities."""
    return security_audit_service.list_vulnerabilities(
        organization_id, status, severity, skip, limit
    )


@router.get("/vulnerabilities/{vuln_id}", response_model=Vulnerability, tags=["vulnerability-management"])
async def get_vulnerability(vuln_id: str):
    """Get vulnerability by ID."""
    vulnerability = security_audit_service.get_vulnerability(vuln_id)
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vulnerability


@router.patch("/vulnerabilities/{vuln_id}", response_model=Vulnerability, tags=["vulnerability-management"])
async def update_vulnerability(vuln_id: str, data: VulnerabilityUpdate):
    """Update vulnerability."""
    vulnerability = security_audit_service.update_vulnerability(vuln_id, data)
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vulnerability


# Security Alerts

@router.get("/alerts", response_model=SecurityAlertListResponse, tags=["security-alerts"])
async def list_alerts(
    organization_id: Optional[str] = Query(None),
    severity: Optional[ThreatSeverity] = Query(None),
    acknowledged: Optional[bool] = Query(None),
    resolved: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List security alerts."""
    return security_audit_service.list_alerts(
        organization_id, severity, acknowledged, resolved, skip, limit
    )


@router.post("/alerts/{alert_id}/acknowledge", response_model=SecurityAlert, tags=["security-alerts"])
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str = Query(...),
):
    """Acknowledge security alert."""
    alert = security_audit_service.acknowledge_alert(alert_id, acknowledged_by)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/resolve", response_model=SecurityAlert, tags=["security-alerts"])
async def resolve_alert(alert_id: str):
    """Resolve security alert."""
    alert = security_audit_service.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


# Security Metrics

@router.get("/organizations/{org_id}/metrics", response_model=SecurityMetrics, tags=["security-metrics"])
async def get_security_metrics(org_id: str):
    """Get security metrics for organization."""
    return security_audit_service.get_security_metrics(org_id)


@router.get("/organizations/{org_id}/scorecard", response_model=SecurityScorecard, tags=["security-metrics"])
async def get_security_scorecard(org_id: str):
    """Get security scorecard for organization."""
    return security_audit_service.get_security_scorecard(org_id)
