"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/documentation_contract.py
===============================================================================
Epitome:
    Defines the immutable schemas, data contracts, and structural models for
    the FG210 Institutional Documentation Engine. Enforces a unified, 
    mathematically strict document schema across every subsystem, contract,
    API, event, artifact, governance policy, and execution path in Wilsy OS.

Biblical Worth Billions:
    "Bind up the testimony, seal the law among my disciples." — Isaiah 8:16

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/documentation_contract.py
===============================================================================
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class EntityKind(Enum):
    """Enumeration of all documentable entity types within Wilsy OS."""
    KERNEL = "KERNEL"
    ENGINE = "ENGINE"
    CONTRACT = "CONTRACT"
    API = "API"
    EVENT = "EVENT"
    ARTIFACT = "ARTIFACT"
    GOVERNANCE = "GOVERNANCE"
    COMPATIBILITY = "COMPATIBILITY"
    VERSION = "VERSION"
    GRAPH = "GRAPH"


class VerificationStatus(Enum):
    """Validation lifecycle state for documented entities."""
    VERIFIED = "VERIFIED"
    DEPRECATED = "DEPRECATED"
    EXPERIMENTAL = "EXPERIMENTAL"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class InterfaceSpec:
    """Specification contract for functional functions, methods, or endpoints."""
    name: str
    description: str
    parameters: Dict[str, str] = field(default_factory=dict)
    return_type: str = "void"
    is_async: bool = False


@dataclass(frozen=True)
class EventSpec:
    """Specification contract for published/subscribed sovereign events."""
    event_name: str
    publisher: str
    subscriber: str
    payload_schema: Dict[str, Any] = field(default_factory=dict)
    lifecycle_stage: str = "PRODUCTION"


@dataclass(frozen=True)
class ArtifactSpec:
    """Specification contract for system-generated file or data artifacts."""
    artifact_type: str
    producer: str
    consumer: str
    schema_urn: str
    checksum_algorithm: str = "SHA-256"
    retention_policy: str = "PERMANENT"


@dataclass(frozen=True)
class GovernanceSpec:
    """Specification contract for system policies and enforcement rules."""
    policy_id: str
    title: str
    decision_path: str
    approval_rule: str
    blocking_condition: str
    enforcement_level: str = "STRICT_HALT"


@dataclass(frozen=True)
class DocumentationEntity:
    """
    Immutable documentation contract representing a single documented entity
    within the Wilsy OS self-documenting ecosystem.
    """
    urn: str
    kind: EntityKind
    title: str
    purpose: str
    module_path: str
    version: str
    architecture_summary: str
    lifecycle_stage: str
    dependencies: List[str] = field(default_factory=list)
    interfaces: List[InterfaceSpec] = field(default_factory=list)
    events: List[EventSpec] = field(default_factory=list)
    artifacts: List[ArtifactSpec] = field(default_factory=list)
    governance_rules: List[GovernanceSpec] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    related_modules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> bool:
        """
        Validates structural integrity of the documentation contract.
        
        Raises:
            ValueError: If URN, title, purpose, or module path violates schema rules.
        """
        if not self.urn or not self.urn.startswith("urn:wilsy:doc:"):
            raise ValueError(f"Invalid Documentation URN format: '{self.urn}'. Must start with 'urn:wilsy:doc:'")
        if not self.title or not self.title.strip():
            raise ValueError("Title must be a non-empty string.")
        if not self.purpose or not self.purpose.strip():
            raise ValueError("Purpose must be a non-empty string.")
        if not self.module_path or not self.module_path.strip():
            raise ValueError("Module path is required.")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the contract into a serializable dictionary representation.
        """
        data = asdict(self)
        data["kind"] = self.kind.value
        data["verification_status"] = self.verification_status.value
        return data
