"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional API Data Transfer Objects (DTOs) & Contracts Engine (FG169).
    Defines strongly-typed, schema-validated, and cryptographically aligned model
    contracts for API request payloads and service responses across Wilsy OS.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional contract engine. Zero child's place.
    Ezekiel 43:11 - "And if they be ashamed of all that they have done, shew them
                    the form of the house, and the fashion thereof..."
    1 Corinthians 14:40 - "Let all things be done decently and in order."

Collaboration & Maintenance:
    - [Architecture]: Strongly-typed Pydantic schemas for platform inter-service communication.
    - [Integrity]: Schema validations prevent malformed payloads from entering the kernel.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class HealthStatusEnum(str, Enum):
    """Subsystem operational status enumeration."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    MAINTENANCE = "MAINTENANCE"


class SubsystemHealthDTO(BaseModel):
    """Detailed operational health contract for individual kernel subsystems."""
    model_config = ConfigDict(frozen=True)

    subsystem_id: str = Field(description="Unique identifier for the subsystem.")
    status: HealthStatusEnum = Field(description="Subsystem operational state.")
    latency_ms: float = Field(ge=0.0, description="Measured response latency in milliseconds.")
    details: Dict[str, Any] = Field(default_factory=dict, description="Granular operational metrics.")


class SystemHealthDTO(BaseModel):
    """Global institutional platform health summary contract."""
    model_config = ConfigDict(frozen=True)

    status: HealthStatusEnum = Field(description="Overall Wilsy OS status.")
    version: str = Field(description="Kernel version string.")
    uptime_seconds: float = Field(ge=0.0, description="Total running uptime in seconds.")
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="UTC time of health evaluation."
    )
    subsystems: List[SubsystemHealthDTO] = Field(default_factory=list, description="Health list per subsystem.")


class KernelSessionDTO(BaseModel):
    """Contract representing an active institutional Wilsy OS Kernel Session."""
    model_config = ConfigDict(frozen=True)

    session_id: str = Field(description="Cryptographic session identifier.")
    tenant_id: str = Field(description="Institutional tenant identifier.")
    operator_id: str = Field(description="Authenticated user or service identity.")
    active_status: bool = Field(default=True, description="Active status indicator.")
    instantiated_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="Session creation UTC timestamp."
    )
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Session configuration parameters.")


class RepositoryMetricsDTO(BaseModel):
    """Contract for document repository and compliance telemetry metrics."""
    model_config = ConfigDict(frozen=True)

    total_artifacts: int = Field(ge=0, description="Total legal document artifacts stored.")
    verified_compliance_rate: float = Field(ge=0.0, le=100.0, description="Percentage of policy-compliant docs.")
    storage_bytes: int = Field(ge=0, description="Total storage consumed in bytes.")
    active_locks: int = Field(ge=0, description="Number of currently immutably locked documents.")
    last_audit_timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="UTC timestamp of the last verification pass."
    )


class ArtifactCatalogDTO(BaseModel):
    """Contract representing a classified legal document artifact record."""
    model_config = ConfigDict(frozen=True)

    catalog_id: str = Field(description="Unique catalog identifier.")
    artifact_name: str = Field(description="Name or title of the legal artifact.")
    classification: str = Field(description="Legal security/compliance classification label.")
    version: str = Field(default="1.0.0", description="Artifact semantic version string.")
    checksum_sha256: str = Field(description="SHA-256 cryptographic hash of the content.")
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="Catalog entry creation UTC timestamp."
    )


class DigitalTwinSnapshotDTO(BaseModel):
    """Contract representing a real-time state mirror of a system process or asset."""
    model_config = ConfigDict(frozen=True)

    twin_id: str = Field(description="Digital twin mirror identifier.")
    physical_entity_id: str = Field(description="Referenced underlying entity ID.")
    snapshot_hash: str = Field(description="State verification hash string.")
    state_data: Dict[str, Any] = Field(description="Structured state snapshot dictionary.")
    telemetry_sync_time: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="UTC timestamp of synchronization."
    )


class ObservabilityDTO(BaseModel):
    """Contract for kernel tracing and runtime metrics telemetry."""
    model_config = ConfigDict(frozen=True)

    trace_id: str = Field(description="OpenTelemetry compliant trace identifier.")
    span_id: str = Field(description="Span segment identifier.")
    log_level: str = Field(default="INFO", description="Current log verbosity level.")
    health_score: float = Field(ge=0.0, le=1.0, description="Calculated engine stability index.")
    active_spans: int = Field(ge=0, description="Count of concurrently executing spans.")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Key-value metric observations.")


class IntelligenceReasoningDTO(BaseModel):
    """Contract capturing AI legal reasoning outputs and confidence scores."""
    model_config = ConfigDict(frozen=True)

    execution_id: str = Field(description="Reasoning run execution ID.")
    query: str = Field(description="Inbound legal query or analysis prompt.")
    reasoning_steps: List[str] = Field(description="Step-by-step analytical reasoning sequence.")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Model output confidence metric.")
    model_version: str = Field(description="Version string of the intelligence model used.")
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="Completion UTC timestamp."
    )
