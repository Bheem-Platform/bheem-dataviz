"""
Security Audit & Monitoring Service

Service for security auditing, intrusion detection, anomaly detection,
threat intelligence, and security incident management.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from collections import defaultdict

from app.schemas.security_audit import (
    AuditLog, AuditLogCreate, AuditLogListResponse, AuditLogFilter,
    AuditCategory, AuditSeverity,
    ThreatIndicator, ThreatIndicatorCreate,
    ThreatDetection, ThreatDetectionListResponse,
    ThreatType, ThreatSeverity, ThreatStatus,
    AnomalyBaseline, DetectedAnomaly, AnomalyListResponse, AnomalyType,
    SecurityIncident, SecurityIncidentCreate, SecurityIncidentUpdate,
    SecurityIncidentListResponse, IncidentStatus, IncidentPriority,
    Vulnerability, VulnerabilityCreate, VulnerabilityUpdate,
    VulnerabilityListResponse, VulnerabilitySeverity, VulnerabilityStatus,
    SecurityMetrics, SecurityTrend, SecurityScorecard,
    SecurityAlert, SecurityAlertListResponse,
    calculate_cvss_severity, get_vulnerability_sla_date, calculate_security_score,
)


class SecurityAuditService:
    """Service for security audit and monitoring."""

    def __init__(self):
        # In-memory stores (use database/SIEM in production)
        self._audit_logs: List[AuditLog] = []
        self._threat_indicators: Dict[str, ThreatIndicator] = {}
        self._threat_detections: Dict[str, ThreatDetection] = {}
        self._anomaly_baselines: Dict[str, AnomalyBaseline] = {}
        self._detected_anomalies: Dict[str, DetectedAnomaly] = {}
        self._security_incidents: Dict[str, SecurityIncident] = {}
        self._vulnerabilities: Dict[str, Vulnerability] = {}
        self._security_alerts: Dict[str, SecurityAlert] = {}

        # Detection counters
        self._login_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self._failed_logins: Dict[str, int] = defaultdict(int)

        # Initialize sample threat indicators
        self._init_threat_indicators()

    def _init_threat_indicators(self):
        """Initialize sample threat indicators."""
        indicators = [
            ThreatIndicator(
                id="ind-known-bad-ip-1",
                threat_type=ThreatType.BRUTE_FORCE,
                severity=ThreatSeverity.HIGH,
                indicator_type="ip",
                indicator_value="192.168.1.100",
                description="Known brute force source",
                source="internal",
                confidence=0.9,
                first_seen=datetime.utcnow() - timedelta(days=30),
                last_seen=datetime.utcnow(),
                times_seen=50,
                tags=["brute-force", "automated"],
            ),
        ]
        for ind in indicators:
            self._threat_indicators[ind.id] = ind

    # Audit Logging

    def create_audit_log(self, data: AuditLogCreate) -> AuditLog:
        """Create an audit log entry."""
        log_id = f"audit-{secrets.token_hex(8)}"

        log = AuditLog(
            id=log_id,
            request_id=f"req-{secrets.token_hex(4)}",
            **data.model_dump(),
        )

        self._audit_logs.append(log)

        # Keep only last 100000 logs in memory
        if len(self._audit_logs) > 100000:
            self._audit_logs = self._audit_logs[-100000:]

        # Check for potential threats
        self._analyze_audit_log(log)

        return log

    def _analyze_audit_log(self, log: AuditLog):
        """Analyze audit log for potential threats."""
        # Track failed logins
        if log.category == AuditCategory.AUTHENTICATION and not log.success:
            ip = log.ip_address
            self._failed_logins[ip] += 1

            # Detect brute force
            if self._failed_logins[ip] >= 5:
                self._create_threat_detection(
                    threat_type=ThreatType.BRUTE_FORCE,
                    severity=ThreatSeverity.MEDIUM,
                    title=f"Potential brute force from {ip}",
                    description=f"Detected {self._failed_logins[ip]} failed login attempts from IP {ip}",
                    confidence=min(0.5 + (self._failed_logins[ip] * 0.1), 0.95),
                    ip_addresses=[ip],
                    organization_id=log.organization_id,
                )

        # Check against threat indicators
        if log.ip_address:
            for indicator in self._threat_indicators.values():
                if indicator.indicator_type == "ip" and indicator.indicator_value == log.ip_address:
                    self._create_threat_detection(
                        threat_type=indicator.threat_type,
                        severity=indicator.severity,
                        title=f"Activity from known malicious IP: {log.ip_address}",
                        description=indicator.description or "Activity matched threat indicator",
                        confidence=indicator.confidence,
                        ip_addresses=[log.ip_address],
                        indicators=[indicator.id],
                        organization_id=log.organization_id,
                    )

    def list_audit_logs(
        self,
        filter: Optional[AuditLogFilter] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> AuditLogListResponse:
        """List audit logs with filtering."""
        logs = list(self._audit_logs)

        if filter:
            if filter.category:
                logs = [l for l in logs if l.category == filter.category]
            if filter.severity:
                logs = [l for l in logs if l.severity == filter.severity]
            if filter.action:
                logs = [l for l in logs if filter.action.lower() in l.action.lower()]
            if filter.resource_type:
                logs = [l for l in logs if l.resource_type == filter.resource_type]
            if filter.user_id:
                logs = [l for l in logs if l.user_id == filter.user_id]
            if filter.organization_id:
                logs = [l for l in logs if l.organization_id == filter.organization_id]
            if filter.ip_address:
                logs = [l for l in logs if l.ip_address == filter.ip_address]
            if filter.success is not None:
                logs = [l for l in logs if l.success == filter.success]
            if filter.start_time:
                logs = [l for l in logs if l.timestamp >= filter.start_time]
            if filter.end_time:
                logs = [l for l in logs if l.timestamp <= filter.end_time]

        logs.sort(key=lambda l: l.timestamp, reverse=True)
        return AuditLogListResponse(
            logs=logs[skip:skip + limit],
            total=len(logs),
        )

    def get_audit_log(self, log_id: str) -> Optional[AuditLog]:
        """Get audit log by ID."""
        for log in self._audit_logs:
            if log.id == log_id:
                return log
        return None

    # Threat Intelligence

    def create_threat_indicator(self, data: ThreatIndicatorCreate) -> ThreatIndicator:
        """Create threat indicator."""
        indicator_id = f"ind-{secrets.token_hex(8)}"
        now = datetime.utcnow()

        indicator = ThreatIndicator(
            id=indicator_id,
            first_seen=now,
            last_seen=now,
            **data.model_dump(),
        )

        self._threat_indicators[indicator_id] = indicator
        return indicator

    def get_threat_indicator(self, indicator_id: str) -> Optional[ThreatIndicator]:
        """Get threat indicator by ID."""
        return self._threat_indicators.get(indicator_id)

    def list_threat_indicators(
        self,
        threat_type: Optional[ThreatType] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ThreatIndicator]:
        """List threat indicators."""
        indicators = list(self._threat_indicators.values())

        if threat_type:
            indicators = [i for i in indicators if i.threat_type == threat_type]
        if active_only:
            indicators = [i for i in indicators if i.active]

        indicators.sort(key=lambda i: i.last_seen, reverse=True)
        return indicators[skip:skip + limit]

    def check_indicator(self, indicator_type: str, value: str) -> Optional[ThreatIndicator]:
        """Check if value matches any threat indicator."""
        for indicator in self._threat_indicators.values():
            if indicator.active and indicator.indicator_type == indicator_type and indicator.indicator_value == value:
                indicator.last_seen = datetime.utcnow()
                indicator.times_seen += 1
                return indicator
        return None

    # Threat Detection

    def _create_threat_detection(
        self,
        threat_type: ThreatType,
        severity: ThreatSeverity,
        title: str,
        description: str,
        confidence: float,
        ip_addresses: List[str] = None,
        indicators: List[str] = None,
        organization_id: Optional[str] = None,
    ) -> ThreatDetection:
        """Create internal threat detection."""
        detection_id = f"threat-{secrets.token_hex(8)}"

        detection = ThreatDetection(
            id=detection_id,
            threat_type=threat_type,
            severity=severity,
            status=ThreatStatus.DETECTED,
            title=title,
            description=description,
            source="internal_detection",
            confidence=confidence,
            ip_addresses=ip_addresses or [],
            indicators=indicators or [],
            organization_id=organization_id,
        )

        self._threat_detections[detection_id] = detection

        # Create alert
        self._create_security_alert(
            alert_type="threat_detected",
            severity=severity,
            title=title,
            message=description,
            source="threat_detection",
            organization_id=organization_id,
            related_entity_type="threat",
            related_entity_id=detection_id,
        )

        return detection

    def get_threat_detection(self, detection_id: str) -> Optional[ThreatDetection]:
        """Get threat detection by ID."""
        return self._threat_detections.get(detection_id)

    def update_threat_detection(
        self,
        detection_id: str,
        status: Optional[ThreatStatus] = None,
        assigned_to: Optional[str] = None,
        resolution_notes: Optional[str] = None,
    ) -> Optional[ThreatDetection]:
        """Update threat detection."""
        detection = self._threat_detections.get(detection_id)
        if not detection:
            return None

        if status:
            detection.status = status
            if status == ThreatStatus.RESOLVED:
                detection.resolved_at = datetime.utcnow()
            elif status == ThreatStatus.INVESTIGATING and not detection.acknowledged_at:
                detection.acknowledged_at = datetime.utcnow()

        if assigned_to:
            detection.assigned_to = assigned_to

        if resolution_notes:
            detection.resolution_notes = resolution_notes

        return detection

    def list_threat_detections(
        self,
        organization_id: Optional[str] = None,
        status: Optional[ThreatStatus] = None,
        severity: Optional[ThreatSeverity] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ThreatDetectionListResponse:
        """List threat detections."""
        detections = list(self._threat_detections.values())

        if organization_id:
            detections = [d for d in detections if d.organization_id == organization_id]
        if status:
            detections = [d for d in detections if d.status == status]
        if severity:
            detections = [d for d in detections if d.severity == severity]

        detections.sort(key=lambda d: d.detected_at, reverse=True)
        return ThreatDetectionListResponse(
            detections=detections[skip:skip + limit],
            total=len(detections),
        )

    # Anomaly Detection

    def detect_anomaly(
        self,
        anomaly_type: AnomalyType,
        description: str,
        actual_value: str,
        deviation_score: float,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        expected_value: Optional[str] = None,
    ) -> DetectedAnomaly:
        """Record detected anomaly."""
        anomaly_id = f"anomaly-{secrets.token_hex(8)}"

        # Determine severity based on deviation
        if deviation_score >= 4:
            severity = ThreatSeverity.CRITICAL
        elif deviation_score >= 3:
            severity = ThreatSeverity.HIGH
        elif deviation_score >= 2:
            severity = ThreatSeverity.MEDIUM
        else:
            severity = ThreatSeverity.LOW

        anomaly = DetectedAnomaly(
            id=anomaly_id,
            anomaly_type=anomaly_type,
            severity=severity,
            user_id=user_id,
            organization_id=organization_id,
            description=description,
            expected_value=expected_value,
            actual_value=actual_value,
            deviation_score=deviation_score,
            confidence=min(0.5 + (deviation_score * 0.15), 0.95),
            ip_address=ip_address,
        )

        self._detected_anomalies[anomaly_id] = anomaly

        # Create alert for high severity anomalies
        if severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]:
            self._create_security_alert(
                alert_type="anomaly_detected",
                severity=severity,
                title=f"Anomaly Detected: {anomaly_type.value}",
                message=description,
                source="anomaly_detection",
                organization_id=organization_id,
                related_entity_type="anomaly",
                related_entity_id=anomaly_id,
            )

        return anomaly

    def investigate_anomaly(
        self,
        anomaly_id: str,
        investigated_by: str,
        false_positive: bool = False,
    ) -> Optional[DetectedAnomaly]:
        """Mark anomaly as investigated."""
        anomaly = self._detected_anomalies.get(anomaly_id)
        if not anomaly:
            return None

        anomaly.investigated = True
        anomaly.investigated_at = datetime.utcnow()
        anomaly.investigated_by = investigated_by
        anomaly.false_positive = false_positive

        return anomaly

    def list_anomalies(
        self,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        anomaly_type: Optional[AnomalyType] = None,
        investigated: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> AnomalyListResponse:
        """List detected anomalies."""
        anomalies = list(self._detected_anomalies.values())

        if organization_id:
            anomalies = [a for a in anomalies if a.organization_id == organization_id]
        if user_id:
            anomalies = [a for a in anomalies if a.user_id == user_id]
        if anomaly_type:
            anomalies = [a for a in anomalies if a.anomaly_type == anomaly_type]
        if investigated is not None:
            anomalies = [a for a in anomalies if a.investigated == investigated]

        anomalies.sort(key=lambda a: a.created_at, reverse=True)
        return AnomalyListResponse(
            anomalies=anomalies[skip:skip + limit],
            total=len(anomalies),
        )

    # Security Incidents

    def create_incident(self, data: SecurityIncidentCreate, reported_by: str) -> SecurityIncident:
        """Create security incident."""
        incident_id = f"inc-{secrets.token_hex(8)}"

        incident = SecurityIncident(
            id=incident_id,
            reported_by=reported_by,
            status=IncidentStatus.OPEN,
            **data.model_dump(),
        )

        # Add initial timeline entry
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "Incident created",
            "user": reported_by,
        })

        self._security_incidents[incident_id] = incident

        # Create alert
        self._create_security_alert(
            alert_type="incident_created",
            severity=data.severity,
            title=f"New Security Incident: {data.title}",
            message=data.description,
            source="incident_management",
            organization_id=data.organization_id,
            related_entity_type="incident",
            related_entity_id=incident_id,
        )

        return incident

    def get_incident(self, incident_id: str) -> Optional[SecurityIncident]:
        """Get security incident by ID."""
        return self._security_incidents.get(incident_id)

    def update_incident(
        self,
        incident_id: str,
        data: SecurityIncidentUpdate,
        updated_by: str,
    ) -> Optional[SecurityIncident]:
        """Update security incident."""
        incident = self._security_incidents.get(incident_id)
        if not incident:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Handle status changes
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == IncidentStatus.CONTAINED and not incident.contained_at:
                incident.contained_at = datetime.utcnow()
            elif new_status == IncidentStatus.REMEDIATED and not incident.resolved_at:
                incident.resolved_at = datetime.utcnow()
            elif new_status == IncidentStatus.CLOSED and not incident.closed_at:
                incident.closed_at = datetime.utcnow()

        for key, value in update_data.items():
            setattr(incident, key, value)

        incident.updated_at = datetime.utcnow()

        # Add timeline entry
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": f"Incident updated: {', '.join(update_data.keys())}",
            "user": updated_by,
        })

        return incident

    def add_incident_note(
        self,
        incident_id: str,
        note: str,
        user: str,
    ) -> Optional[SecurityIncident]:
        """Add note to incident timeline."""
        incident = self._security_incidents.get(incident_id)
        if not incident:
            return None

        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": note,
            "user": user,
        })
        incident.updated_at = datetime.utcnow()

        return incident

    def list_incidents(
        self,
        organization_id: Optional[str] = None,
        status: Optional[IncidentStatus] = None,
        priority: Optional[IncidentPriority] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> SecurityIncidentListResponse:
        """List security incidents."""
        incidents = list(self._security_incidents.values())

        if organization_id:
            incidents = [i for i in incidents if i.organization_id == organization_id]
        if status:
            incidents = [i for i in incidents if i.status == status]
        if priority:
            incidents = [i for i in incidents if i.priority == priority]

        incidents.sort(key=lambda i: i.created_at, reverse=True)
        return SecurityIncidentListResponse(
            incidents=incidents[skip:skip + limit],
            total=len(incidents),
        )

    # Vulnerability Management

    def create_vulnerability(self, data: VulnerabilityCreate) -> Vulnerability:
        """Create vulnerability record."""
        vuln_id = f"vuln-{secrets.token_hex(8)}"
        now = datetime.utcnow()

        # Calculate severity from CVSS if provided
        severity = data.severity
        if data.cvss_score:
            severity = calculate_cvss_severity(data.cvss_score)

        vulnerability = Vulnerability(
            id=vuln_id,
            severity=severity,
            status=VulnerabilityStatus.OPEN,
            discovered_at=now,
            due_date=get_vulnerability_sla_date(severity, now),
            **data.model_dump(exclude={"severity"}),
        )

        self._vulnerabilities[vuln_id] = vulnerability

        # Create alert for critical/high vulnerabilities
        if severity in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH]:
            self._create_security_alert(
                alert_type="vulnerability_found",
                severity=ThreatSeverity.HIGH if severity == VulnerabilitySeverity.HIGH else ThreatSeverity.CRITICAL,
                title=f"New Vulnerability: {data.title}",
                message=data.description,
                source="vulnerability_scanner",
                organization_id=data.organization_id,
                related_entity_type="vulnerability",
                related_entity_id=vuln_id,
            )

        return vulnerability

    def get_vulnerability(self, vuln_id: str) -> Optional[Vulnerability]:
        """Get vulnerability by ID."""
        return self._vulnerabilities.get(vuln_id)

    def update_vulnerability(self, vuln_id: str, data: VulnerabilityUpdate) -> Optional[Vulnerability]:
        """Update vulnerability."""
        vulnerability = self._vulnerabilities.get(vuln_id)
        if not vulnerability:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "status" in update_data:
            if update_data["status"] == VulnerabilityStatus.REMEDIATED:
                vulnerability.remediated_at = datetime.utcnow()

        for key, value in update_data.items():
            setattr(vulnerability, key, value)

        vulnerability.updated_at = datetime.utcnow()

        return vulnerability

    def list_vulnerabilities(
        self,
        organization_id: Optional[str] = None,
        status: Optional[VulnerabilityStatus] = None,
        severity: Optional[VulnerabilitySeverity] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> VulnerabilityListResponse:
        """List vulnerabilities."""
        vulnerabilities = list(self._vulnerabilities.values())

        if organization_id:
            vulnerabilities = [v for v in vulnerabilities if v.organization_id == organization_id]
        if status:
            vulnerabilities = [v for v in vulnerabilities if v.status == status]
        if severity:
            vulnerabilities = [v for v in vulnerabilities if v.severity == severity]

        vulnerabilities.sort(key=lambda v: v.discovered_at, reverse=True)
        return VulnerabilityListResponse(
            vulnerabilities=vulnerabilities[skip:skip + limit],
            total=len(vulnerabilities),
        )

    # Security Alerts

    def _create_security_alert(
        self,
        alert_type: str,
        severity: ThreatSeverity,
        title: str,
        message: str,
        source: str,
        organization_id: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
    ) -> SecurityAlert:
        """Create security alert."""
        alert_id = f"alert-{secrets.token_hex(8)}"

        alert = SecurityAlert(
            id=alert_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            source=source,
            organization_id=organization_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )

        self._security_alerts[alert_id] = alert
        return alert

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Optional[SecurityAlert]:
        """Acknowledge security alert."""
        alert = self._security_alerts.get(alert_id)
        if not alert:
            return None

        alert.acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.utcnow()

        return alert

    def resolve_alert(self, alert_id: str) -> Optional[SecurityAlert]:
        """Resolve security alert."""
        alert = self._security_alerts.get(alert_id)
        if not alert:
            return None

        alert.resolved = True
        alert.resolved_at = datetime.utcnow()

        return alert

    def list_alerts(
        self,
        organization_id: Optional[str] = None,
        severity: Optional[ThreatSeverity] = None,
        acknowledged: Optional[bool] = None,
        resolved: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> SecurityAlertListResponse:
        """List security alerts."""
        alerts = list(self._security_alerts.values())

        if organization_id:
            alerts = [a for a in alerts if a.organization_id == organization_id]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]

        alerts.sort(key=lambda a: a.created_at, reverse=True)
        return SecurityAlertListResponse(
            alerts=alerts[skip:skip + limit],
            total=len(alerts),
        )

    # Security Metrics

    def get_security_metrics(self, organization_id: str) -> SecurityMetrics:
        """Get security metrics for organization."""
        now = datetime.utcnow()
        day_ago = now - timedelta(hours=24)

        # Calculate authentication metrics
        auth_logs = [
            l for l in self._audit_logs
            if l.organization_id == organization_id and
               l.category == AuditCategory.AUTHENTICATION and
               l.timestamp >= day_ago
        ]
        total_logins = len(auth_logs)
        failed_logins = len([l for l in auth_logs if not l.success])
        unique_users = len(set(l.user_id for l in auth_logs if l.user_id))

        # Calculate threat metrics
        active_threats = len([
            t for t in self._threat_detections.values()
            if t.organization_id == organization_id and
               t.status not in [ThreatStatus.RESOLVED, ThreatStatus.FALSE_POSITIVE]
        ])
        threats_24h = len([
            t for t in self._threat_detections.values()
            if t.organization_id == organization_id and t.detected_at >= day_ago
        ])

        # Calculate incident metrics
        open_incidents = len([
            i for i in self._security_incidents.values()
            if i.organization_id == organization_id and
               i.status not in [IncidentStatus.CLOSED, IncidentStatus.REMEDIATED]
        ])
        critical_incidents = len([
            i for i in self._security_incidents.values()
            if i.organization_id == organization_id and
               i.status not in [IncidentStatus.CLOSED, IncidentStatus.REMEDIATED] and
               i.priority == IncidentPriority.CRITICAL
        ])

        # Calculate vulnerability metrics
        open_vulns = [
            v for v in self._vulnerabilities.values()
            if v.organization_id == organization_id and
               v.status == VulnerabilityStatus.OPEN
        ]
        critical_vulns = len([v for v in open_vulns if v.severity == VulnerabilitySeverity.CRITICAL])
        overdue_vulns = len([
            v for v in open_vulns
            if v.due_date and v.due_date < now
        ])

        # Calculate anomaly metrics
        anomalies_24h = len([
            a for a in self._detected_anomalies.values()
            if a.organization_id == organization_id and a.created_at >= day_ago
        ])

        return SecurityMetrics(
            organization_id=organization_id,
            total_logins_24h=total_logins,
            failed_logins_24h=failed_logins,
            unique_users_24h=unique_users,
            mfa_usage_percent=75.0,  # Would calculate from auth data
            active_threats=active_threats,
            threats_detected_24h=threats_24h,
            open_incidents=open_incidents,
            critical_incidents=critical_incidents,
            open_vulnerabilities=len(open_vulns),
            critical_vulnerabilities=critical_vulns,
            overdue_vulnerabilities=overdue_vulns,
            anomalies_detected_24h=anomalies_24h,
        )

    def get_security_scorecard(self, organization_id: str) -> SecurityScorecard:
        """Get security scorecard for organization."""
        metrics = self.get_security_metrics(organization_id)
        overall_score = calculate_security_score(metrics)

        # Calculate category scores
        categories = {
            "authentication": 80 if metrics.failed_logins_24h < 10 else 60,
            "threat_management": 90 if metrics.active_threats == 0 else max(50, 90 - metrics.active_threats * 10),
            "incident_response": 85 if metrics.open_incidents == 0 else max(40, 85 - metrics.open_incidents * 15),
            "vulnerability_management": 80 if metrics.critical_vulnerabilities == 0 else max(30, 80 - metrics.critical_vulnerabilities * 20),
        }

        # Determine strengths and weaknesses
        strengths = []
        weaknesses = []
        recommendations = []

        if categories["authentication"] >= 80:
            strengths.append("Strong authentication security")
        else:
            weaknesses.append("High rate of failed login attempts")
            recommendations.append("Review failed login patterns and implement stricter rate limiting")

        if categories["threat_management"] >= 80:
            strengths.append("Effective threat management")
        else:
            weaknesses.append("Active threats require attention")
            recommendations.append("Investigate and resolve active threats")

        if categories["vulnerability_management"] >= 80:
            strengths.append("Good vulnerability management")
        else:
            weaknesses.append("Critical vulnerabilities pending remediation")
            recommendations.append("Prioritize patching critical vulnerabilities")

        return SecurityScorecard(
            organization_id=organization_id,
            overall_score=overall_score,
            categories=categories,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )


# Create singleton instance
security_audit_service = SecurityAuditService()
