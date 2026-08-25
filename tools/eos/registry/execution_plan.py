"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Registry Framework - Immutable Execution Plan (FG148).
    Represents an immutable, integrity-hashed, deterministically ordered execution
    blueprint produced by the DependencyResolver for consumption by schedulers.

Biblical Scale & Architecture:
    Production-ready institutional execution plan contract. Zero child's play.
    Guarantees thread-safe, audit-trailed, SHA-256 hashed engine execution sequences.
    1 Corinthians 14:40 - "But all things should be done decently and in order."

Collaboration & Maintenance:
    - [Architecture]: Immutable data contract isolating discovery from execution.
    - Consumed by: Scheduler (FG149), Kernel Executors, Auditing Dashboard.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from .engine_descriptor import EngineDescriptor

logger = logging.getLogger("WilsyExecutionPlan")


@dataclass(frozen=True)
class ExecutionPlan:
    """
    Immutable dataclass encapsulating a fully resolved engine execution sequence.
    Provides cryptographic checksum validation, timeline auditability, and
    thread-safe execution guarantees across all Wilsy OS dispatch environments.
    """

    execution_id: str
    created_at: str
    ordered_descriptors: Tuple[EngineDescriptor, ...]
    checksum: str

    # [FUNCTION EXPLANATION]: Factory constructor enforcing SHA-256 hash generation and UTC timestamping.
    @classmethod
    def create(
        cls,
        ordered_descriptors: Tuple[EngineDescriptor, ...],
        execution_id: str | None = None,
    ) -> ExecutionPlan:
        """
        Factory method constructing an ExecutionPlan with cryptographic SHA-256 checksums
        and high-precision UTC timestamping.

        Args:
            ordered_descriptors (Tuple[EngineDescriptor, ...]): Topologically sorted descriptors.
            execution_id (str | None): Optional custom execution ID string.

        Returns:
            ExecutionPlan: An immutable, fully integrity-validated execution plan.
        """
        exec_id = execution_id or f"exec-{uuid.uuid4().hex[:12]}"
        now_utc = datetime.now(timezone.utc).isoformat()

        # Compute deterministic SHA-256 checksum across identifiers, versions, enablement, and priorities
        raw_payload = "|".join(
            f"{d.identifier}:{d.version}:{d.enabled}:{d.priority}" for d in ordered_descriptors
        )
        computed_checksum = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        return cls(
            execution_id=exec_id,
            created_at=now_utc,
            ordered_descriptors=ordered_descriptors,
            checksum=computed_checksum,
        )

    # [FUNCTION EXPLANATION]: Returns immutable tuple of engine ID strings in execution order.
    def get_engine_ids(self) -> Tuple[str, ...]:
        """Returns ordered tuple of engine identifier strings."""
        return tuple(desc.identifier for desc in self.ordered_descriptors)

    # [FUNCTION EXPLANATION]: Filters for descriptors marked enabled=True.
    def get_enabled_descriptors(self) -> Tuple[EngineDescriptor, ...]:
        """Returns ordered tuple containing only enabled EngineDescriptors."""
        return tuple(desc for desc in self.ordered_descriptors if desc.enabled)

    # [FUNCTION EXPLANATION]: Returns total count of engines in this execution plan.
    @property
    def total_engines(self) -> int:
        """Returns total number of engines in the plan."""
        return len(self.ordered_descriptors)

    # [FUNCTION EXPLANATION]: Returns count of active enabled engines.
    @property
    def enabled_count(self) -> int:
        """Returns total count of active/enabled engines."""
        return len(self.get_enabled_descriptors())

    # [FUNCTION EXPLANATION]: Verifies execution plan checksum against contained descriptors.
    def verify_integrity(self) -> bool:
        """Re-computes and verifies SHA-256 checksum integrity."""
        raw_payload = "|".join(
            f"{d.identifier}:{d.version}:{d.enabled}:{d.priority}" for d in self.ordered_descriptors
        )
        expected = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
        return self.checksum == expected

    # [FUNCTION EXPLANATION]: Export execution plan for logging, dashboards, and network dispatch.
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the execution plan to a JSON-compatible dictionary."""
        return {
            "execution_id": self.execution_id,
            "created_at": self.created_at,
            "total_engines": self.total_engines,
            "enabled_count": self.enabled_count,
            "checksum": self.checksum,
            "integrity_valid": self.verify_integrity(),
            "ordered_descriptors": [desc.to_dict() for desc in self.ordered_descriptors],
        }
