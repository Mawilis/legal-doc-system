"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Bus Framework - Immutable Artifact Data Structure (FG150A).
    Represents the fundamental, cryptographically verifiable unit of output
    produced by engines within the Wilsy OS kernel.

Biblical Scale & Architecture:
    Production-ready frozen data structure. Strict immutability ensures zero
    side-effects and absolute historical reproducibility across engine executions.
    Habakkuk 2:2 - "Write the vision and make it plain on tablets, that he may run who reads it."

Collaboration & Maintenance:
    - [Architecture]: Core immutable contract for all engine-generated artifacts.
    - Consumes: Raw payload, engine identifiers, and execution metadata.
    - Produces: Cryptographically hashed, frozen Artifact instance.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Artifact:
    """
    Immutable representation of an engine execution output artifact.

    Attributes:
        artifact_id (str): Unique identifier for the artifact.
        execution_id (str): ID of the execution context/plan that produced this artifact.
        engine_id (str): ID of the engine that generated this artifact.
        artifact_type (str): Domain classification of the payload (e.g., 'repository', 'ai_summary', 'quality_gate').
        created_at (str): ISO-8601 UTC timestamp of creation.
        checksum (str): SHA-256 cryptographic digest of the payload content.
        payload (Any): Primary payload content (dict, list, str, or primitive serializable structure).
        metadata (Dict[str, Any]): Auxiliary operational telemetry or descriptors.
        version (str): Schema/artifact contract version string.
    """

    artifact_id: str
    execution_id: str
    engine_id: str
    artifact_type: str
    created_at: str
    checksum: str
    payload: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    # [FUNCTION EXPLANATION]: Factory builder ensuring auto-generation of cryptographic checksums and IDs.
    @classmethod
    def create(
        cls,
        execution_id: str,
        engine_id: str,
        artifact_type: str,
        payload: Any,
        metadata: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0",
        artifact_id: Optional[str] = None,
    ) -> Artifact:
        """
        Factory method to construct an immutable Artifact with deterministic SHA-256 checksumming.

        Args:
            execution_id (str): ID of the parent execution plan.
            engine_id (str): ID of the producing engine.
            artifact_type (str): Domain classification of the artifact.
            payload (Any): Core data content produced by the engine.
            metadata (Optional[Dict[str, Any]]): Contextual metadata or execution parameters.
            version (str): Contract version string (defaults to "1.0.0").
            artifact_id (Optional[str]): Optional explicit ID; auto-generates UUID4 if omitted.

        Returns:
            Artifact: Fully constructed, frozen Artifact instance.
        """
        generated_id = artifact_id or f"art-{uuid.uuid4().hex[:12]}"
        created_timestamp = datetime.now(timezone.utc).isoformat()
        meta = metadata or {}

        # Compute deterministic SHA-256 checksum over payload
        checksum_hash = cls._compute_payload_checksum(payload)

        return cls(
            artifact_id=generated_id,
            execution_id=execution_id,
            engine_id=engine_id,
            artifact_type=artifact_type,
            created_at=created_timestamp,
            checksum=checksum_hash,
            payload=payload,
            metadata=meta,
            version=version,
        )

    # [FUNCTION EXPLANATION]: Helper method for computing deterministic SHA-256 payload checksums.
    @staticmethod
    def _compute_payload_checksum(payload: Any) -> str:
        """
        Calculates SHA-256 hash of payload data using deterministic JSON serialization.
        """
        try:
            if isinstance(payload, (dict, list)):
                serialized = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
            elif isinstance(payload, bytes):
                serialized = payload
            else:
                serialized = str(payload).encode("utf-8")
            return hashlib.sha256(serialized).hexdigest()
        except Exception as exc:
            # Fallback string coercion for complex unserializable types
            fallback_bytes = str(payload).encode("utf-8")
            return hashlib.sha256(fallback_bytes).hexdigest()

    # [FUNCTION EXPLANATION]: Verifies payload integrity against recorded SHA-256 checksum.
    def verify_integrity(self) -> bool:
        """
        Validates that current payload matches recorded cryptographic checksum.

        Returns:
            bool: True if computed checksum matches recorded checksum, False otherwise.
        """
        computed = self._compute_payload_checksum(self.payload)
        return computed == self.checksum
