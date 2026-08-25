"""
===============================================================================
WILSY OS — FG225 AUTONOMOUS RECOVERY ENGINE
DOMAIN SUBSYSTEM: RECOVERY INCIDENT
===============================================================================

File Path:
    tools/eos/autonomous_recovery/domain/recovery_incident.py

Version:
    v225.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines the immutable RecoveryIncident data structure, mapping raw runtime 
    failures into institutional incident categories (WORKER_FAILURE, NODE_FAILURE, 
    REPOSITORY_FAILURE, PLUGIN_FAILURE, DOCUMENTATION_FAILURE) with cryptographic 
    checksum integrity.

Biblical Worth Billions:
    "A prudent man foreseeth the evil, and hideth himself; but the simple pass on, 
    and are punished." — Proverbs 22:3

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class IncidentType(str, Enum):
    """Institutional incident classifications for Wilsy OS FG225."""
    WORKER_FAILURE = "WORKER_FAILURE"
    NODE_FAILURE = "NODE_FAILURE"
    REPOSITORY_FAILURE = "REPOSITORY_FAILURE"
    PLUGIN_FAILURE = "PLUGIN_FAILURE"
    DOCUMENTATION_FAILURE = "DOCUMENTATION_FAILURE"
    SYSTEM_FAULT = "SYSTEM_FAULT"


class IncidentSeverity(str, Enum):
    """Severity levels governing recovery escalation and approval matrix."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    """Lifecycle states of an autonomous recovery incident."""
    DETECTED = "DETECTED"
    CLASSIFIED = "CLASSIFIED"
    ANALYZED = "ANALYZED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class RecoveryIncident:
    """
    Represents an institutional failure incident captured within Wilsy OS,
    carrying immutable audit metadata and cryptographic hashing.
    """
    incident_id: str = field(default_factory=lambda: f"INC-{uuid.uuid4().hex[:8].upper()}")
    incident_type: IncidentType = IncidentType.SYSTEM_FAULT
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    source_subsystem: str = "unknown"
    description: str = ""
    status: IncidentStatus = IncidentStatus.DETECTED
    raw_payload: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon initialization."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the incident attributes."""
        raw_data = f"{self.incident_id}:{self.incident_type}:{self.severity}:{self.source_subsystem}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        """Serializes the incident into a dictionary representation."""
        return {
            "incident_id": self.incident_id,
            "incident_type": self.incident_type.value,
            "severity": self.severity.value,
            "source_subsystem": self.source_subsystem,
            "description": self.description,
            "status": self.status.value,
            "raw_payload": self.raw_payload,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
