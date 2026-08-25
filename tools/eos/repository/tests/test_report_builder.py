"""
FG143D Native Unit Tests

Repository Intelligence Report Synthesis Boundary.
"""

from __future__ import annotations

import unittest
from datetime import UTC, datetime

from tools.eos.repository.domain.models import (
    RepositoryAssessment,
    RepositoryFinding,
    RepositoryHealth,
    RepositoryIntelligenceReport,
    RepositoryMetrics,
    RepositoryStatus,
)
from tools.eos.repository.reporting.report_builder import (
    RepositoryIntelligenceReportBuilder,
)


class TestRepositoryIntelligenceReportBuilder(unittest.TestCase):
    """
    Native FG143D synthesis contract tests.
    """

    def setUp(self) -> None:
        self.builder = RepositoryIntelligenceReportBuilder()

        self.metrics = RepositoryMetrics(
            file_count=12,
            directory_count=5,
            python_module_count=8,
            package_count=2,
        )

        self.graph = (
            "tools/eos/repository/domain/models.py",
            "tools/eos/repository/graph/repository_graph.py",
        )

        self.assessment = RepositoryAssessment(
            health=RepositoryHealth.HEALTHY,
            status=RepositoryStatus.READY,
            score=100,
            findings=[
                RepositoryFinding(
                    identifier="FG143D:TEST",
                    message="Synthetic synthesis test finding.",
                )
            ],
        )

    def test_build_report_returns_canonical_report(self) -> None:
        """
        The synthesis boundary returns the canonical domain report.
        """
        report = self.builder.build_report(
            self.metrics,
            self.graph,
            self.assessment,
        )

        self.assertIsInstance(report, RepositoryIntelligenceReport)

    def test_build_report_preserves_metrics_graph_and_assessment(self) -> None:
        """
        Synthesis preserves all upstream immutable source structures.
        """
        report = self.builder.build_report(
            self.metrics,
            self.graph,
            self.assessment,
        )

        self.assertIs(report.metrics, self.metrics)
        self.assertIs(report.assessment, self.assessment)
        self.assertEqual(report.graph, self.graph)
        self.assertIsInstance(report.graph, tuple)

    def test_build_report_generates_utc_iso_timestamp(self) -> None:
        """
        Synthesis produces an ISO-8601 UTC generated_at value.
        """
        report = self.builder.build_report(
            self.metrics,
            self.graph,
            self.assessment,
        )

        parsed = datetime.fromisoformat(report.generated_at)

        self.assertIsNotNone(parsed.tzinfo)
        self.assertEqual(parsed.utcoffset(), UTC.utcoffset(parsed))

    def test_build_report_rejects_missing_metrics(self) -> None:
        """
        Missing metrics are rejected at the synthesis boundary.
        """
        with self.assertRaises(ValueError):
            self.builder.build_report(
                None,
                self.graph,
                self.assessment,
            )

    def test_build_report_rejects_missing_graph(self) -> None:
        """
        Missing graph state is rejected at the synthesis boundary.
        """
        with self.assertRaises(ValueError):
            self.builder.build_report(
                self.metrics,
                None,
                self.assessment,
            )

    def test_build_report_rejects_missing_assessment(self) -> None:
        """
        Missing assessment state is rejected at the synthesis boundary.
        """
        with self.assertRaises(ValueError):
            self.builder.build_report(
                self.metrics,
                self.graph,
                None,
            )


if __name__ == "__main__":
    unittest.main()
