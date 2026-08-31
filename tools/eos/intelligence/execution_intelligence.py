# -*- coding: utf-8 -*-
"""TITLE: WILSY OS — FG173 EXECUTION INTELLIGENCE ENGINE.

VERSION: v2.0.0-SOVEREIGN-EVIDENCE-BOUND-INTELLIGENCE
AUTHORITY: Wilsy OS Core Governance
EPITOME:
    Evidence-bound orchestration for execution statistics, diagnostics, decisions,
    predictions, patterns, recommendations, and trends. This engine does not
    manufacture confidence, health, traceability, or execution truth.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/execution_intelligence.py
COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-08-31
CHANGELOG:
    v2.0.0-SOVEREIGN-EVIDENCE-BOUND-INTELLIGENCE:
        Removes static decision confidence and traceability defaults; requires
        explicit cryptographic traceability evidence for packaged decisions;
        derives prediction value from certified execution statistics; derives
        prediction confidence strictly from observed status-evidence coverage;
        derives prediction identifiers from the evidence summary; rejects
        unsupported prediction metrics; and derives diagnostic posture from
        execution evidence instead of reporting unconditional health.
COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned integrity,
    minimization, traceability, and fail-closed posture.
SECURITY / PRIVACY POSTURE:
    This module does not authenticate principals, derive identity, establish
    tenant membership, or widen authorization. It consumes history already scoped
    by its caller and does not persist credentials or sensitive business payloads.
TENANT BOUNDARY:
    The caller owns sovereign tenant authorization and must supply an already
    authorized history store. This engine neither establishes nor merges tenant
    scope.
AUTHORITY BOUNDARY:
    Descriptive and analytical intelligence orchestration only. Statistics,
    diagnostics, confidence coverage, predictions, and packaged decisions are not
    authorization and do not grant business mutation authority.
FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS exclusively owns financial execution. This engine cannot approve,
    release, settle, execute, or infer financial authority.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
from typing import Any, Dict, List, Optional

from .execution_history import ExecutionHistoryStore
from .execution_patterns import ExecutionPatternAnalyzer
from .execution_recommendations import (
    ExecutionRecommendationEngine,
    RecommendationDTO,
)
from .execution_statistics import ExecutionStatisticsEngine
from .execution_trends import ExecutionTrendAnalyzer
from .models import EngineeringDecision, ExecutionPrediction, HistoricalPattern


VERSION = "v2.0.0-SOVEREIGN-EVIDENCE-BOUND-INTELLIGENCE"

_COMPLETE_EVIDENCE = "COMPLETE_STATUS_EVIDENCE"
_NO_EVIDENCE = "NO_EXECUTION_EVIDENCE"
_SUPPORTED_PREDICTION_METRIC = "SUCCESS"
_SHA256_TRACEABILITY_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")

logger = logging.getLogger(__name__)


class ExecutionIntelligenceReport:
    """Container for synthesized descriptive intelligence outputs.

    Authority:
        Read-only report packaging. The report is not authorization or execution
        authority.
    Tenant scope:
        Inherits the already-authorized scope of the supplied history store.
    Financial boundary:
        Kennel EOS remains the exclusive financial execution authority.
    """

    def __init__(
        self,
        statistics: Dict[str, Any],
        patterns: List[Any],
        recommendations: List[Any],
        trends: Dict[str, Any],
    ) -> None:
        self.statistics = statistics
        self.patterns = patterns
        self.recommendations = recommendations
        self.trends = trends


def _require_non_blank_string(value: Any, field_name: str) -> str:
    """Return a trimmed non-blank string or fail closed."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-blank string")
    return value.strip()


def _validate_confidence(value: Any) -> float:
    """Validate explicit decision confidence in the closed interval [0.0, 1.0]."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("confidence_score must be a finite number between 0.0 and 1.0")
    confidence = float(value)
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence_score must be a finite number between 0.0 and 1.0")
    return confidence


def _validate_traceability_checksum(value: Any) -> str:
    """Require an explicit SHA-256 traceability anchor.

    The engine validates format only. Provenance and evidentiary authority remain
    caller-owned and must already be governed outside this module.
    """
    checksum = _require_non_blank_string(value, "traceability_checksum")
    if not _SHA256_TRACEABILITY_RE.fullmatch(checksum):
        raise ValueError(
            "traceability_checksum must use the form sha256:<64 hexadecimal characters>"
        )
    return checksum.lower()


def _require_non_negative_integer(value: Any, field_name: str) -> int:
    """Return a non-negative integer or fail closed."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def _status_evidence_coverage(statistics: Dict[str, Any]) -> float:
    """Return the observed fraction of executions carrying admissible status evidence.

    This value is deliberately used as the legacy prediction ``confidence`` field.
    It is evidence coverage, not a claim of statistical calibration or future
    certainty.
    """
    total = statistics.get("total_executions")
    unknown = statistics.get("unknown_status_executions")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ValueError("total_executions must be a non-negative integer")
    if not isinstance(unknown, int) or isinstance(unknown, bool) or unknown < 0:
        raise ValueError("unknown_status_executions must be a non-negative integer")
    if unknown > total:
        raise ValueError("unknown_status_executions cannot exceed total_executions")
    if total == 0:
        return 0.0
    return (total - unknown) / total


def _prediction_id(target_metric: str, statistics: Dict[str, Any]) -> str:
    """Derive a stable prediction identifier from observed statistics."""
    evidence_summary = {
        "target_metric": target_metric,
        "total_executions": statistics.get("total_executions"),
        "successful_executions": statistics.get("successful_executions"),
        "non_successful_executions": statistics.get("non_successful_executions"),
        "unknown_status_executions": statistics.get("unknown_status_executions"),
        "success_rate": statistics.get("success_rate"),
        "status_distribution": statistics.get("status_distribution"),
        "evidence_status": statistics.get("evidence_status"),
    }
    canonical = json.dumps(
        evidence_summary,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"PRED-EOS-{digest[:16].upper()}"


class ExecutionIntelligenceEngine:
    """Coordinate descriptive intelligence without manufacturing authority or truth.

    Authority:
        Orchestrates execution intelligence only. It does not authenticate,
        authorize, mutate business state, or execute business operations.
    Tenant scope:
        Requires an already-authorized history store supplied by the caller.
    Mutation:
        ``record_execution`` delegates history mutation to the supplied store;
        analytical methods are read-only over that store.
    Fail-closed:
        Missing decision confidence/traceability evidence, malformed statistics,
        and unsupported prediction metrics raise errors instead of receiving
        synthetic defaults.
    Financial boundary:
        Kennel EOS exclusively owns financial execution.
    """

    def __init__(
        self,
        history_store: Optional[ExecutionHistoryStore] = None,
        memory: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        self.history_store = history_store or ExecutionHistoryStore()
        self.memory = memory
        self.config = kwargs.get("config", {})
        logger.info("ExecutionIntelligenceEngine initialized successfully.")

    def record_execution(self, record: Any) -> None:
        """Record caller-supplied execution evidence in the configured history store."""
        self.history_store.add_record(record)

    def analyze_history(self) -> List[HistoricalPattern]:
        """Return pattern analysis over the already-authorized history scope."""
        records = self.history_store.get_all_records()
        return ExecutionPatternAnalyzer.analyze(records)  # type: ignore[no-any-return]

    def compute_statistics(self) -> Dict[str, Any]:
        """Return certified evidence-derived execution statistics."""
        records = self.history_store.get_all_records()
        return ExecutionStatisticsEngine.compute(records)  # type: ignore[arg-type]

    def generate_recommendations(self) -> List[RecommendationDTO]:
        """Generate recommendations from the current authorized execution evidence."""
        records = self.history_store.get_all_records()
        statistics = self.compute_statistics()
        return ExecutionRecommendationEngine.generate(  # type: ignore[no-any-return]
            records,
            statistics,
        )

    def make_decision(
        self,
        decision_id: str,
        title: str,
        rationale: str,
        **kwargs: Any,
    ) -> EngineeringDecision:
        """Package a decision only when explicit confidence and traceability are supplied.

        This method does not derive an autonomous institutional decision. The caller
        must provide governed confidence evidence and a SHA-256 traceability anchor.
        No default confidence or traceability value is permitted.
        """
        normalized_decision_id = _require_non_blank_string(decision_id, "decision_id")
        normalized_title = _require_non_blank_string(title, "title")
        normalized_rationale = _require_non_blank_string(rationale, "rationale")

        if "confidence_score" not in kwargs:
            raise ValueError("confidence_score is required; synthetic confidence is forbidden")
        if "traceability_checksum" not in kwargs:
            raise ValueError(
                "traceability_checksum is required; synthetic traceability is forbidden"
            )

        confidence_score = _validate_confidence(kwargs.pop("confidence_score"))
        traceability_checksum = _validate_traceability_checksum(
            kwargs.pop("traceability_checksum")
        )
        if kwargs:
            unsupported = ", ".join(sorted(kwargs))
            raise TypeError(f"Unsupported decision argument(s): {unsupported}")

        return EngineeringDecision(
            decision_id=normalized_decision_id,
            title=normalized_title,
            rationale=normalized_rationale,
            producing_engine="ExecutionIntelligenceEngine",
            decision_summary=normalized_title,
            confidence_score=confidence_score,
            traceability_checksum=traceability_checksum,
        )

    def predict_execution(self, target_metric: str = "SUCCESS") -> ExecutionPrediction:
        """Return an evidence-bound projection over the supported SUCCESS metric.

        ``predicted_value`` is the observed historical success ratio. The legacy
        confidence fields carry status-evidence coverage only; they are not a claim
        of calibrated predictive certainty. Zero history therefore produces zero
        confidence rather than synthetic certainty.
        """
        normalized_metric = _require_non_blank_string(
            target_metric,
            "target_metric",
        ).upper()
        if normalized_metric != _SUPPORTED_PREDICTION_METRIC:
            raise ValueError(
                f"Unsupported target_metric: {normalized_metric}; "
                f"supported metric is {_SUPPORTED_PREDICTION_METRIC}"
            )

        statistics = self.compute_statistics()
        success_rate = statistics.get("success_rate")
        if isinstance(success_rate, bool) or not isinstance(success_rate, (int, float)):
            raise ValueError("success_rate must be a finite number between 0.0 and 100.0")
        numeric_success_rate = float(success_rate)
        if not math.isfinite(numeric_success_rate) or not 0.0 <= numeric_success_rate <= 100.0:
            raise ValueError("success_rate must be a finite number between 0.0 and 100.0")

        evidence_coverage = _status_evidence_coverage(statistics)

        return ExecutionPrediction(
            prediction_id=_prediction_id(normalized_metric, statistics),
            target_metric=normalized_metric,
            predicted_value=numeric_success_rate / 100.0,
            confidence=evidence_coverage,
            confidence_score=evidence_coverage,
        )

    def run_diagnostics(self) -> Dict[str, Any]:
        """Derive diagnostic posture from execution evidence.

        Posture order is intentionally conservative:
        - ``NO_EVIDENCE`` when no executions exist;
        - ``INCOMPLETE_EVIDENCE`` when status evidence is incomplete;
        - ``DEGRADED`` when any non-success, failure, or warning signal exists;
        - ``HEALTHY`` only when complete observed evidence is entirely successful
          and carries no failure or warning signals.
        """
        statistics = self.compute_statistics()
        total = _require_non_negative_integer(
            statistics.get("total_executions"),
            "total_executions",
        )
        evidence_status = statistics.get("evidence_status")
        non_successful = _require_non_negative_integer(
            statistics.get("non_successful_executions"),
            "non_successful_executions",
        )
        failures = _require_non_negative_integer(
            statistics.get("total_failure_signals"),
            "total_failure_signals",
        )
        warnings = _require_non_negative_integer(
            statistics.get("total_warning_signals"),
            "total_warning_signals",
        )

        if total == 0:
            status = "NO_EVIDENCE"
        elif evidence_status != _COMPLETE_EVIDENCE:
            status = "INCOMPLETE_EVIDENCE"
        elif non_successful > 0 or failures > 0 or warnings > 0:
            status = "DEGRADED"
        else:
            status = "HEALTHY"

        return {
            "status": status,
            "total_records": total,
            "statistics": statistics,
        }

    def synthesize(self) -> ExecutionIntelligenceReport:
        """Synthesize descriptive statistics, patterns, recommendations, and trends."""
        records = self.history_store.get_all_records()
        statistics = self.compute_statistics()
        patterns = self.analyze_history()
        recommendations = self.generate_recommendations()
        trends = ExecutionTrendAnalyzer.analyze(records)  # type: ignore[no-any-return]
        return ExecutionIntelligenceReport(
            statistics,
            patterns,
            recommendations,
            trends,
        )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: FG173 Execution Intelligence Engine
# VERSION: v2.0.0-SOVEREIGN-EVIDENCE-BOUND-INTELLIGENCE
# AUTHORITY BOUNDARY: Descriptive/analytical intelligence orchestration only;
# no authentication, authorization, business mutation, or execution authority.
# TENANT POSTURE: Caller-owned authorized history scope; this artifact neither
# establishes nor widens tenant membership or tenant authority.
# FAIL-CLOSED POSTURE: Missing confidence/traceability evidence, malformed
# statistics, and unsupported prediction metrics fail closed without synthetic truth.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
