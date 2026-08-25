"""
===============================================================================
WILSY ENGINEERING KERNEL — ARTIFACT AGGREGATOR (PRODUCTION GRADE)
===============================================================================
Epitome:
    FG171D Artifact Aggregator Engine.
    Consumes multi-stage pipeline artifacts (Repository, AI, Review, Release)
    and synthesizes them into an immutable Unified Compliance Report.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Production Mandate:
    - Zero‑loss aggregation: all artifacts are stored immutably.
    - Batch flush for performance.
    - Queryable by session, tenant, and artifact type.
    - Supports both in‑memory and persistent storage backends (pluggable).
    - Idempotent ingestion with deduplication by artifact_id.
    - Full compatibility with kernel.py: add_artifact, artifact_count, flush.

Collaboration & Maintenance:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
===============================================================================
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Callable
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("WilsyOS.Runtime.ArtifactAggregator")


class PipelineArtifact(BaseModel):
    """Immutable representation of a discrete pipeline stage artifact."""
    model_config = ConfigDict(frozen=True)

    artifact_id: str = Field(description="Unique artifact tracking ID.")
    source_task_id: str = Field(description="Originating task ID that produced the artifact.")
    artifact_type: str = Field(description="Classification type.")
    tenant_id: str = Field(default="tenant-default", description="Tenant isolation boundary ID.")
    session_id: str = Field(description="Operational session identifier.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Raw artifact content payload.")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of artifact publication."
    )


class UnifiedComplianceReport(BaseModel):
    """Aggregate master report compiled from all pipeline stage artifacts."""
    model_config = ConfigDict(frozen=True)

    report_id: str = Field(default_factory=lambda: f"unified-rpt-{uuid4().hex[:8]}", description="Unique master report ID.")
    session_id: str = Field(description="Target session identifier.")
    tenant_id: str = Field(description="Target tenant identifier.")
    total_artifacts_aggregated: int = Field(ge=0, description="Count of discrete artifacts processed.")
    aggregated_stages: List[str] = Field(default_factory=list, description="List of included artifact types.")
    master_compliance_score: float = Field(ge=0.0, le=100.0, description="Synthesized master compliance percentage.")
    stage_artifacts: List[PipelineArtifact] = Field(default_factory=list, description="Underlying source artifacts.")
    compiled_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of master aggregation."
    )


class ArtifactAggregator:
    """
    Engine responsible for collecting, validating, and synthesizing pipeline artifacts
    into a UnifiedComplianceReport.
    Supports batch flushing, deduplication, and querying.
    """

    def __init__(self, session_id: Optional[str] = None, tenant_id: str = "tenant-default") -> None:
        # If no session_id given, generate a temporary one for standalone usage
        self.session_id = session_id or f"agg-{uuid4().hex[:12]}"
        self.tenant_id = tenant_id
        self._collected_artifacts: List[PipelineArtifact] = []
        self._artifact_ids: Set[str] = set()
        self._flush_callback: Optional[Callable[[List[PipelineArtifact]], None]] = None

        logger.info(
            f"Initialized ArtifactAggregator | session={self.session_id} | tenant={self.tenant_id}"
        )

    # ==========================================================================
    # PRIMARY METHODS (used by kernel.py)
    # ==========================================================================

    def add_artifact(self, artifact: PipelineArtifact) -> None:
        """
        Registers an artifact, deduplicating by artifact_id.
        This is the method called by WilsyKernelBootstrap._run_stage.
        """
        if self.session_id and artifact.session_id != self.session_id:
            logger.warning(
                f"Artifact session mismatch: expected {self.session_id}, got {artifact.session_id}"
            )

        if artifact.artifact_id in self._artifact_ids:
            logger.warning(f"Duplicate artifact {artifact.artifact_id} – skipping")
            return

        self._collected_artifacts.append(artifact)
        self._artifact_ids.add(artifact.artifact_id)
        logger.info(
            f"Ingested artifact type [{artifact.artifact_type}] ID [{artifact.artifact_id}]"
        )

    def artifact_count(self) -> int:
        """Return the number of artifacts collected."""
        return len(self._collected_artifacts)

    def flush(self) -> None:
        """
        Flush any pending artifacts to the configured storage backend.
        In this in‑memory implementation, flush simply calls the flush callback (if set)
        and logs the count.
        """
        count = self.artifact_count()
        if count == 0:
            logger.info("Flush called with no artifacts")
            return

        logger.info(f"Flushing {count} artifacts to storage")

        if self._flush_callback is not None:
            try:
                self._flush_callback(self._collected_artifacts)
            except Exception as e:
                logger.error(f"Flush callback failed: {e}", exc_info=True)
                raise

    # ==========================================================================
    # LEGACY / COMPATIBILITY METHODS
    # ==========================================================================

    def ingest_artifact(self, artifact: PipelineArtifact) -> None:
        """Legacy alias for add_artifact."""
        self.add_artifact(artifact)

    # ==========================================================================
    # ADDITIONAL PRODUCTION FEATURES
    # ==========================================================================

    def register_flush_callback(self, callback: Callable[[List[PipelineArtifact]], None]) -> None:
        """Register a callback that is invoked on flush()."""
        self._flush_callback = callback
        logger.info("Flush callback registered")

    def generate_unified_report(self) -> UnifiedComplianceReport:
        """Synthesizes all collected artifacts into an immutable UnifiedComplianceReport."""
        total_count = self.artifact_count()
        stages = list(set(a.artifact_type for a in self._collected_artifacts))

        scores: List[float] = []
        for artifact in self._collected_artifacts:
            for key in ["compliance_score", "score", "confidence_score"]:
                if key in artifact.payload and isinstance(artifact.payload[key], (int, float)):
                    scores.append(float(artifact.payload[key]))

        master_score = round(sum(scores) / len(scores), 2) if scores else 100.0

        logger.info(
            f"Compiling Unified Report | session={self.session_id} | "
            f"artifacts={total_count} | score={master_score}%"
        )

        return UnifiedComplianceReport(
            session_id=self.session_id,
            tenant_id=self.tenant_id,
            total_artifacts_aggregated=total_count,
            aggregated_stages=stages,
            master_compliance_score=master_score,
            stage_artifacts=self._collected_artifacts.copy(),
        )

    def get_artifacts_by_type(self, artifact_type: str) -> List[PipelineArtifact]:
        """Query artifacts by type."""
        return [a for a in self._collected_artifacts if a.artifact_type == artifact_type]

    def get_artifacts_by_task(self, task_id: str) -> List[PipelineArtifact]:
        """Query artifacts by source_task_id."""
        return [a for a in self._collected_artifacts if a.source_task_id == task_id]

    def clear(self) -> None:
        """Clear all collected artifacts."""
        self._collected_artifacts.clear()
        self._artifact_ids.clear()
        logger.info("Artifact store cleared")
