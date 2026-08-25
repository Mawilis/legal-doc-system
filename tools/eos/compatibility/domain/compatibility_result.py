"""
===============================================================================
WILSY OS — COMPATIBILITY EVALUATION RESULT DOMAIN MODEL (FG208)
===============================================================================
Epitome:
    Defines evaluation result containers, audit logs, and execution decision 
    wrappers for Kernel FG208. Ensures complete traceability and auditability 
    of every version negotiation and capability check prior to scheduler dispatch.

Biblical Worth Billions:
    "Prove all things; hold fast that which is good."
    — 1 Thessalonians 5:21

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/domain/compatibility_result.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from tools.eos.compatibility.domain.compatibility_models import CompatibilityDecision, CompatibilityStatus


@dataclass(frozen=True)
class CompatibilityEvaluationLog:
    """Single assertion trace entry produced during compatibility evaluation."""
    stage: str
    passed: bool
    detail: str
    timestamp: str


@dataclass(frozen=True)
class CompatibilityEvaluationResult:
    """
    Domain aggregate wrapping a compatibility decision alongside evaluation 
    traces and execution readiness status.
    """
    decision: CompatibilityDecision
    evaluation_logs: List[CompatibilityEvaluationLog]
    evaluation_latency_ms: float
    evaluated_at: str

    @classmethod
    def create(
        cls,
        decision: CompatibilityDecision,
        logs: List[CompatibilityEvaluationLog],
        latency_ms: float
    ) -> CompatibilityEvaluationResult:
        """Instantiates an evaluation result with current SAST timestamp."""
        sast_tz = timezone(timedelta(hours=2))
        timestamp_str = datetime.now(sast_tz).strftime("%Y-%m-%d %H:%M:%S SAST")
        return cls(
            decision=decision,
            evaluation_logs=list(logs),
            evaluation_latency_ms=latency_ms,
            evaluated_at=timestamp_str
        )

    def is_dispatchable(self) -> bool:
        """Determines if the workload can proceed to scheduler dispatch."""
        return self.decision.is_executable()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes result aggregate into dictionary format."""
        return {
            "decision": self.decision.to_dict(),
            "evaluation_logs": [
                {
                    "stage": log.stage,
                    "passed": log.passed,
                    "detail": log.detail,
                    "timestamp": log.timestamp
                }
                for log in self.evaluation_logs
            ],
            "evaluation_latency_ms": self.evaluation_latency_ms,
            "evaluated_at": self.evaluated_at
        }
