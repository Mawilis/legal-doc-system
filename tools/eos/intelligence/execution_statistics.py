# -*- coding: utf-8 -*-
"""TITLE: WILSY OS — FG173 EXECUTION STATISTICS ENGINE.

VERSION: v2.0.0-SOVEREIGN-EVIDENCE-DERIVED-STATISTICS
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministic, fail-closed execution statistics for the Wilsy OS
Intelligence Layer. Success truth is derived from observed execution status and
never fabricated from missing evidence.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/execution_statistics.py
COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-08-31
CHANGELOG:
    v2.0.0-SOVEREIGN-EVIDENCE-DERIVED-STATISTICS:
        Replaces the hard-coded success-rate constant with evidence-derived status
        statistics; distinguishes zero evidence from successful evidence; adds
        explicit success, non-success, unknown-status, failure-signal, warning-
        signal, status-distribution, and evidence-posture outputs; preserves
        runtime and artifact aggregate compatibility; accepts the established
        ``artifacts_count`` field and the parallel legacy ``artifact_count``
        shape without allowing either form to create success truth.
COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001-aligned
    integrity and minimization posture.
SECURITY / PRIVACY POSTURE:
    This module performs deterministic aggregation over records already supplied
    by a caller. It does not authenticate principals, derive identity, disclose
    credentials, widen record scope, or infer missing execution success.
TENANT BOUNDARY:
    This module does not establish tenant membership or tenant authority. The
    caller must provide an already-authorized, tenant-scoped record set. Records
    from different tenant scopes MUST NOT be combined by this engine.
AUTHORITY BOUNDARY:
    Owns descriptive execution statistics only. Observed statistics are not
    authorization, business mutation authority, recommendation authority,
    prediction truth, or execution authority.
FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS exclusively owns financial execution. This module cannot approve,
    release, execute, settle, or infer any financial state.
"""

from __future__ import annotations

from collections import Counter
import math
from typing import Any, Dict, List, Mapping

from tools.eos.intelligence.execution_history import ExecutionRecordDTO


VERSION = "v2.0.0-SOVEREIGN-EVIDENCE-DERIVED-STATISTICS"

_SUCCESS_STATUS = "SUCCESS"
_NO_EVIDENCE = "NO_EXECUTION_EVIDENCE"
_COMPLETE_EVIDENCE = "COMPLETE_STATUS_EVIDENCE"
_INCOMPLETE_EVIDENCE = "INCOMPLETE_STATUS_EVIDENCE"


def _read_field(record: Any, *names: str) -> Any:
    """Read the first present field without inventing a missing value.

    Authority:
        Reads only fields already present on the supplied record.
    Tenant scope:
        Does not establish, alter, or widen record scope.
    Mutation:
        Read-only.
    Fail-closed:
        Raises ``ValueError`` when none of the accepted field names exists.
    Financial boundary:
        Does not establish or mutate financial truth.
    """
    for name in names:
        if isinstance(record, Mapping) and name in record:
            return record[name]
        if hasattr(record, name):
            return getattr(record, name)
    accepted = ", ".join(names)
    raise ValueError(f"Execution record is missing required field(s): {accepted}")


def _read_optional_field(record: Any, *names: str) -> Any:
    """Read an optional field, returning ``None`` only when it is absent.

    Absence remains explicit and is never converted into successful execution
    truth. This helper is read-only and does not establish tenant or authority
    context.
    """
    for name in names:
        if isinstance(record, Mapping) and name in record:
            return record[name]
        if hasattr(record, name):
            return getattr(record, name)
    return None


def _coerce_non_negative_number(value: Any, field_name: str) -> float:
    """Validate a finite, non-negative numeric execution measurement.

    Invalid telemetry fails closed instead of being replaced with fabricated
    zero-valued execution truth.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a finite non-negative number")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0:
        raise ValueError(f"{field_name} must be a finite non-negative number")
    return numeric


def _coerce_non_negative_count(value: Any, field_name: str) -> int:
    """Validate a non-negative integral execution count.

    Boolean, fractional, negative, and non-numeric values fail closed.
    """
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def _normalize_status(value: Any) -> str:
    """Normalize observed status while preserving missing/invalid status as UNKNOWN.

    Only real, non-blank string status evidence is admissible. The canonical
    ``SUCCESS`` status is the only value that contributes to successful
    execution truth. Missing, non-string, or blank status remains
    non-successful and is reported as incomplete evidence rather than being
    promoted to complete status evidence.
    """
    if not isinstance(value, str):
        return "UNKNOWN"
    status = value.strip().upper()
    return status or "UNKNOWN"


class ExecutionStatisticsEngine:
    """Compute evidence-derived descriptive statistics over execution history.

    Authority:
        Descriptive analytics only. This class does not authorize operations or
        convert observed statistics into business truth.
    Tenant scope:
        Requires the caller to supply an already-authorized, tenant-scoped list.
        It never merges, resolves, or manufactures tenant scope.
    Mutation:
        Read-only; supplied records are not mutated.
    Idempotency:
        Deterministic for an unchanged ordered record set.
    Fail-closed:
        Malformed required runtime/artifact/failure/warning measurements raise
        ``ValueError``. Unknown status is retained as incomplete evidence and
        never counted as success.
    Financial boundary:
        Kennel EOS remains the exclusive financial execution authority.
    """

    @staticmethod
    def compute(records: List[ExecutionRecordDTO]) -> Dict[str, Any]:
        """Return deterministic statistics derived from supplied execution evidence.

        ``SUCCESS`` is the only status counted as successful. Every other
        observed or missing status is non-successful. An empty record set
        returns ``success_rate`` 0.0 together with
        ``evidence_status='NO_EXECUTION_EVIDENCE'`` so zero evidence cannot be
        represented as perfect health.

        Runtime and artifact aggregates preserve the existing public keys.
        ``artifacts_count`` is the canonical history field; ``artifact_count``
        is accepted only as a compatibility input for the parallel legacy model
        and does not create a second output contract.
        """
        total = len(records)
        if total == 0:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "non_successful_executions": 0,
                "unknown_status_executions": 0,
                "total_failure_signals": 0,
                "total_warning_signals": 0,
                "average_runtime_ms": 0.0,
                "max_runtime_ms": 0.0,
                "min_runtime_ms": 0.0,
                "average_artifact_count": 0.0,
                "success_rate": 0.0,
                "status_distribution": {},
                "evidence_status": _NO_EVIDENCE,
            }

        durations: list[float] = []
        artifacts: list[int] = []
        statuses: list[str] = []
        total_failure_signals = 0
        total_warning_signals = 0

        for record in records:
            durations.append(
                _coerce_non_negative_number(
                    _read_field(record, "duration_ms"),
                    "duration_ms",
                )
            )
            artifacts.append(
                _coerce_non_negative_count(
                    _read_field(record, "artifacts_count", "artifact_count"),
                    "artifacts_count",
                )
            )
            total_failure_signals += _coerce_non_negative_count(
                _read_field(record, "failure_count"),
                "failure_count",
            )
            total_warning_signals += _coerce_non_negative_count(
                _read_field(record, "warning_count"),
                "warning_count",
            )
            statuses.append(_normalize_status(_read_optional_field(record, "status")))

        status_distribution = dict(sorted(Counter(statuses).items()))
        successful = status_distribution.get(_SUCCESS_STATUS, 0)
        unknown_statuses = status_distribution.get("UNKNOWN", 0)
        non_successful = total - successful

        return {
            "total_executions": total,
            "successful_executions": successful,
            "non_successful_executions": non_successful,
            "unknown_status_executions": unknown_statuses,
            "total_failure_signals": total_failure_signals,
            "total_warning_signals": total_warning_signals,
            "average_runtime_ms": sum(durations) / total,
            "max_runtime_ms": max(durations),
            "min_runtime_ms": min(durations),
            "average_artifact_count": sum(artifacts) / total,
            "success_rate": (successful / total) * 100.0,
            "status_distribution": status_distribution,
            "evidence_status": (
                _INCOMPLETE_EVIDENCE if unknown_statuses else _COMPLETE_EVIDENCE
            ),
        }


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: FG173 Execution Statistics Engine
# VERSION: v2.0.0-SOVEREIGN-EVIDENCE-DERIVED-STATISTICS
# AUTHORITY BOUNDARY: Descriptive execution statistics only; no authorization,
# business mutation, prediction authority, or execution authority.
# TENANT POSTURE: Caller-owned authorized tenant scope; this artifact neither
# establishes nor widens tenant membership or tenant authority.
# FAIL-CLOSED POSTURE: Missing required telemetry fails closed; unknown status
# remains incomplete evidence and never becomes successful execution truth.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
