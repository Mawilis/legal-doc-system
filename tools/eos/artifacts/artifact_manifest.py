"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Bus Framework - Immutable Execution Manifest (FG150D).
    Provides a cryptographically sealed manifest summarizing all artifacts
    produced during a single execution run.

Biblical Scale & Architecture:
    Production-ready frozen data structure. Seals an entire execution run's
    artifact lineage into a verifiable cryptographic manifest.
    Psalm 40:7 - "Then said I, Behold, I come: in the volume of the book it is written of me."

Collaboration & Maintenance:
    - [Architecture]: Immutable execution summary contract consumed by reporting and audit engines.
    - Consumes: Execution ID and associated Artifact collection.
    - Produces: Cryptographically hashed, frozen ArtifactManifest instance.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Sequence, Tuple


@dataclass(frozen=True)
class ArtifactManifest:
    """
    Immutable summary manifest encapsulating the exact artifact lineage
    produced by a single execution plan run.

    Attributes:
        manifest_id (str): Unique identifier for the manifest.
        execution_id (str): ID of the execution plan run being summarized.
        created_at (str): ISO-8601 UTC timestamp of manifest generation.
        artifact_count (int): Total count of artifacts included in this manifest.
        artifact_ids (Tuple[str, ...]): Immutable tuple of artifact identifiers in deterministic order.
        checksum (str): SHA-256 cryptographic digest of the manifest contents.
        version (str): Manifest schema version string.
    """

    manifest_id: str
    execution_id: str
    created_at: str
    artifact_count: int
    artifact_ids: Tuple[str, ...]
    checksum: str
    version: str = "1.0.0"

    # [FUNCTION EXPLANATION]: Factory builder constructing a cryptographically sealed immutable manifest.
    @classmethod
    def create(
        cls,
        execution_id: str,
        artifact_ids: Sequence[str],
        manifest_id: Optional[str] = None,
        version: str = "1.0.0",
    ) -> ArtifactManifest:
        """
        Factory method to construct an immutable ArtifactManifest with SHA-256 sealing.

        Args:
            execution_id (str): ID of the execution plan.
            artifact_ids (Sequence[str]): Collection of artifact IDs produced during execution.
            manifest_id (Optional[str]): Optional custom manifest ID; auto-generates if omitted.
            version (str): Manifest version (defaults to "1.0.0").

        Returns:
            ArtifactManifest: Sealed, immutable manifest instance.
        """
        gen_manifest_id = manifest_id or f"mnf-{uuid.uuid4().hex[:12]}"
        created_timestamp = datetime.now(timezone.utc).isoformat()
        sorted_artifact_ids = tuple(sorted(artifact_ids))
        count = len(sorted_artifact_ids)

        # Compute SHA-256 checksum over execution context and sorted artifact IDs
        checksum_hash = cls._compute_manifest_checksum(execution_id, sorted_artifact_ids)

        return cls(
            manifest_id=gen_manifest_id,
            execution_id=execution_id,
            created_at=created_timestamp,
            artifact_count=count,
            artifact_ids=sorted_artifact_ids,
            checksum=checksum_hash,
            version=version,
        )

    # [FUNCTION EXPLANATION]: Computes SHA-256 cryptographic hash of manifest execution data.
    @staticmethod
    def _compute_manifest_checksum(execution_id: str, artifact_ids: Tuple[str, ...]) -> str:
        """Calculates SHA-256 cryptographic hash of the execution manifest contents."""
        payload = {
            "execution_id": execution_id,
            "artifact_ids": list(artifact_ids),
        }
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    # [FUNCTION EXPLANATION]: Verifies manifest integrity against stored checksum.
    def verify_integrity(self) -> bool:
        """
        Validates that current manifest contents match the recorded cryptographic checksum.

        Returns:
            bool: True if computed checksum matches recorded checksum, False otherwise.
        """
        computed = self._compute_manifest_checksum(self.execution_id, self.artifact_ids)
        return computed == self.checksum
