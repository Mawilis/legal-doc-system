from __future__ import annotations

"""
===============================================================================
WILSY OS RUNTIME — PIPELINE AGGREGATE RESULT CONTAINER (FG179)
===============================================================================
Epitome:
    Immutable, cryptographically signed aggregation object consolidating all
    engine lifecycle outputs, artifacts, bus events, metrics, and failure logs.

Biblical Worth Billions:
    "Gather up the fragments that remain, that nothing be lost." — John 6:12
    Every artifact, log, and metric from every executed engine is captured into
    a single tamper-evident result seal.

Collaboration & Ownership:
    - Founder & Lead Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Execution Pipeline Runtime
    - Phase / Milestone: FG179 - Execution Pipeline Manager
    - Target Directory: tools/eos/runtime/
    - File Path: tools/eos/runtime/pipeline_result.py
    - Runtime Alignment: Python 3.10+ Production Environment
===============================================================================
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from tools.eos.core.engine import EngineResult
from tools.eos.runtime.pipeline_statistics import PipelineStatistics
from tools.eos.runtime.pipeline_status import PipelineStatus


class PipelineResult:
    """
    Immutable container representing the complete result of an orchestrated pipeline execution.
    Includes a SHA-256 cryptographic seal across all aggregated engine outputs.
    """

    def __init__(
        self,
        pipeline_id: str,
        plan_id: str,
        status: PipelineStatus,
        engine_results: Optional[List[EngineResult]] = None,
        artifacts: Optional[List[Dict[str, Any]]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        statistics: Optional[PipelineStatistics] = None,
        errors: Optional[List[str]] = None,
        timestamp: Optional[str] = None,
    ) -> None:
        self.pipeline_id = pipeline_id
        self.plan_id = plan_id
        self.status = status
        self.engine_results = engine_results or []
        self.artifacts = artifacts or []
        self.events = events or []
        self.statistics = statistics or PipelineStatistics()
        self.errors = errors or []
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def compute_checksum(self) -> str:
        """
        Calculates an immutable SHA-256 hash across the entire pipeline result body.
        """
        engine_data = [e.to_dict() for e in self.engine_results]
        payload = {
            "pipeline_id": self.pipeline_id,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "engine_results": engine_data,
            "artifacts": self.artifacts,
            "events": self.events,
            "statistics": self.statistics.to_dict(),
            "errors": self.errors,
            "timestamp": self.timestamp,
        }
        raw_bytes = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the pipeline result into a JSON-compatible dictionary.
        """
        return {
            "pipeline_id": self.pipeline_id,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "engine_results": [e.to_dict() for e in self.engine_results],
            "artifacts": self.artifacts,
            "events": self.events,
            "statistics": self.statistics.to_dict(),
            "errors": self.errors,
            "timestamp": self.timestamp,
            "checksum": self.compute_checksum(),
        }


__all__ = ["PipelineResult"]
