# -*- coding: utf-8 -*-
"""TITLE: WILSY OS — FG173 EXECUTION STATISTICS CONTRACT CERTIFICATE.

TEST VERSION: v1.0.0-WILSY-EXECUTION-STATISTICS-CONTRACT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME:
    Non-skipping, deterministic certification of the FG173 execution-statistics
    truth contract. The suite proves that observed execution evidence, and only
    admissible execution evidence, determines descriptive statistics.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/eos/intelligence/test_execution_statistics_contract.py
PRIMARY ARTIFACT UNDER TEST:
    tools/eos/intelligence/execution_statistics.py
COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-08-31
CONTRACT:
    - no execution evidence is never represented as perfect success;
    - only normalized string status SUCCESS contributes to successful execution;
    - non-successful execution remains distinguishable from successful execution;
    - missing, blank, or non-string status is incomplete evidence;
    - runtime, artifact, failure, and warning aggregates are evidence-derived;
    - malformed telemetry fails closed;
    - canonical ExecutionRecord fields are exercised directly;
    - no conditional skips or dynamic fixture adaptation are permitted.
TENANT BOUNDARY:
    Tests descriptive aggregation only. Tenant authorization remains caller-owned;
    this certificate does not grant, derive, or widen tenant authority.
AUTHORITY BOUNDARY:
    Execution statistics are observations, not authorization, prediction,
    recommendation, business mutation, or execution authority.
FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

import unittest

from tools.eos.intelligence.execution_history import ExecutionRecord
from tools.eos.intelligence.execution_statistics import ExecutionStatisticsEngine


TEST_VERSION = "v1.0.0-WILSY-EXECUTION-STATISTICS-CONTRACT-CERT"


class TestExecutionStatisticsContract(unittest.TestCase):
    """Certify deterministic and fail-closed FG173 statistics semantics."""

    def test_no_execution_evidence_is_explicit_and_never_perfect_success(self) -> None:
        """Zero records must report no evidence rather than successful history."""
        self.assertEqual(
            ExecutionStatisticsEngine.compute([]),
            {
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
                "evidence_status": "NO_EXECUTION_EVIDENCE",
            },
        )

    def test_all_success_history_is_measured_from_canonical_records(self) -> None:
        """Canonical SUCCESS records must produce evidence-derived perfect success."""
        records = [
            ExecutionRecord(
                "EXEC-SUCCESS-001",
                status="SUCCESS",
                duration_ms=100.0,
                artifacts_count=2,
                failure_count=0,
                warning_count=1,
            ),
            ExecutionRecord(
                "EXEC-SUCCESS-002",
                status=" success ",
                duration_ms=300.0,
                artifacts_count=6,
                failure_count=0,
                warning_count=0,
            ),
        ]

        self.assertEqual(
            ExecutionStatisticsEngine.compute(records),
            {
                "total_executions": 2,
                "successful_executions": 2,
                "non_successful_executions": 0,
                "unknown_status_executions": 0,
                "total_failure_signals": 0,
                "total_warning_signals": 1,
                "average_runtime_ms": 200.0,
                "max_runtime_ms": 300.0,
                "min_runtime_ms": 100.0,
                "average_artifact_count": 4.0,
                "success_rate": 100.0,
                "status_distribution": {"SUCCESS": 2},
                "evidence_status": "COMPLETE_STATUS_EVIDENCE",
            },
        )

    def test_explicit_non_success_never_becomes_success(self) -> None:
        """An explicit non-success status must reduce measured success."""
        result = ExecutionStatisticsEngine.compute(
            [
                ExecutionRecord(
                    "EXEC-FAIL-001",
                    status="FAILURE",
                    duration_ms=50.0,
                    artifacts_count=1,
                    failure_count=1,
                    warning_count=0,
                )
            ]
        )

        self.assertEqual(result["total_executions"], 1)
        self.assertEqual(result["successful_executions"], 0)
        self.assertEqual(result["non_successful_executions"], 1)
        self.assertEqual(result["success_rate"], 0.0)
        self.assertEqual(result["status_distribution"], {"FAILURE": 1})
        self.assertEqual(result["evidence_status"], "COMPLETE_STATUS_EVIDENCE")

    def test_mixed_history_computes_exact_evidence_derived_aggregates(self) -> None:
        """Mixed history must produce exact runtime, artifact, signal, and success math."""
        records = [
            ExecutionRecord(
                "EXEC-SUCCESS-001",
                status="SUCCESS",
                duration_ms=100.0,
                artifacts_count=2,
                failure_count=0,
                warning_count=0,
            ),
            ExecutionRecord(
                "EXEC-FAIL-001",
                status="FAILURE",
                duration_ms=300.0,
                artifacts_count=6,
                failure_count=1,
                warning_count=2,
            ),
        ]

        self.assertEqual(
            ExecutionStatisticsEngine.compute(records),
            {
                "total_executions": 2,
                "successful_executions": 1,
                "non_successful_executions": 1,
                "unknown_status_executions": 0,
                "total_failure_signals": 1,
                "total_warning_signals": 2,
                "average_runtime_ms": 200.0,
                "max_runtime_ms": 300.0,
                "min_runtime_ms": 100.0,
                "average_artifact_count": 4.0,
                "success_rate": 50.0,
                "status_distribution": {"FAILURE": 1, "SUCCESS": 1},
                "evidence_status": "COMPLETE_STATUS_EVIDENCE",
            },
        )

    def test_non_string_status_is_unknown_incomplete_evidence(self) -> None:
        """Non-string status must not be promoted to complete status evidence."""
        record = ExecutionRecord("EXEC-BAD-STATUS-001")
        record.status = 123  # type: ignore[assignment]

        result = ExecutionStatisticsEngine.compute([record])

        self.assertEqual(result["successful_executions"], 0)
        self.assertEqual(result["non_successful_executions"], 1)
        self.assertEqual(result["unknown_status_executions"], 1)
        self.assertEqual(result["success_rate"], 0.0)
        self.assertEqual(result["status_distribution"], {"UNKNOWN": 1})
        self.assertEqual(result["evidence_status"], "INCOMPLETE_STATUS_EVIDENCE")

    def test_blank_status_is_unknown_incomplete_evidence(self) -> None:
        """Blank string status must remain incomplete rather than successful."""
        result = ExecutionStatisticsEngine.compute(
            [ExecutionRecord("EXEC-BLANK-STATUS-001", status="   ")]
        )

        self.assertEqual(result["unknown_status_executions"], 1)
        self.assertEqual(result["status_distribution"], {"UNKNOWN": 1})
        self.assertEqual(result["evidence_status"], "INCOMPLETE_STATUS_EVIDENCE")
        self.assertEqual(result["success_rate"], 0.0)

    def test_negative_runtime_fails_closed(self) -> None:
        """Negative runtime telemetry must be rejected."""
        with self.assertRaisesRegex(
            ValueError,
            r"^duration_ms must be a finite non-negative number$",
        ):
            ExecutionStatisticsEngine.compute(
                [ExecutionRecord("EXEC-NEGATIVE-RUNTIME-001", duration_ms=-1.0)]
            )

    def test_non_finite_runtime_fails_closed(self) -> None:
        """Non-finite runtime telemetry must be rejected."""
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    r"^duration_ms must be a finite non-negative number$",
                ):
                    ExecutionStatisticsEngine.compute(
                        [ExecutionRecord("EXEC-NONFINITE-RUNTIME-001", duration_ms=value)]
                    )

    def test_invalid_artifact_count_fails_closed(self) -> None:
        """Canonical artifact-count telemetry must be a non-negative integer."""
        for value in (-1, True):
            with self.subTest(value=value):
                record = ExecutionRecord("EXEC-BAD-ARTIFACTS-001")
                record.artifacts_count = value  # type: ignore[assignment]
                with self.assertRaisesRegex(
                    ValueError,
                    r"^artifacts_count must be a non-negative integer$",
                ):
                    ExecutionStatisticsEngine.compute([record])

    def test_invalid_failure_or_warning_signal_count_fails_closed(self) -> None:
        """Failure and warning signal counts must be non-negative integers."""
        failure_record = ExecutionRecord("EXEC-BAD-FAILURE-COUNT-001")
        failure_record.failure_count = -1

        with self.assertRaisesRegex(
            ValueError,
            r"^failure_count must be a non-negative integer$",
        ):
            ExecutionStatisticsEngine.compute([failure_record])

        warning_record = ExecutionRecord("EXEC-BAD-WARNING-COUNT-001")
        warning_record.warning_count = True  # type: ignore[assignment]

        with self.assertRaisesRegex(
            ValueError,
            r"^warning_count must be a non-negative integer$",
        ):
            ExecutionStatisticsEngine.compute([warning_record])


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# =============================================================================
# ARTIFACT: FG173 Execution Statistics Contract Certificate
# TEST VERSION: v1.0.0-WILSY-EXECUTION-STATISTICS-CONTRACT-CERT
# PRIMARY ARTIFACT: tools/eos/intelligence/execution_statistics.py
# AUTHORITY BOUNDARY: Descriptive execution-statistics certification only.
# TENANT POSTURE: No tenant authority is granted, derived, or widened.
# FAIL-CLOSED POSTURE: Malformed or incomplete evidence cannot become success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS TEST ARTIFACT
